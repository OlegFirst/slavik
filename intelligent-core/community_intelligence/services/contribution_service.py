"""
Case Contribution Service

Manages community workflow contributions through peer review process.

Workflow:
1. User submits case (auto-anonymized)
2. System assigns peer reviewers
3. Reviews collected
4. If approved → Case Library
5. Contributor gets reputation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from ..models.database import CaseContribution, PeerReview, UserReputation, ContributionStatus, ReputationTransaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

class ContributionService:
    """
    Service for community contributions

    Example:
    >>> service = ContributionService(db, anonymizer, case_library)
    >>> contribution_id = await service.submit_case(user_id, case_data, "bia")
    """

    def __init__(self, db: AsyncSession, anonymizer, case_library):
        self.db = db
        self.anonymizer = anonymizer
        self.case_library = case_library

    async def submit_case(
        self,
        contributor_id: str,
        case_data: Dict[str, Any],
        module: str
    ) -> str:
        """
        Submit case for community review

        Returns contribution_id
        """

        # 1. Anonymize case data
        anonymized = await self.anonymizer.anonymize_case(case_data)

        # 2. Extract metadata
        org_type = self._extract_org_type(case_data)
        tags = self._extract_tags(case_data, module)

        # 3. Create contribution
        contribution = CaseContribution(
            id=uuid.uuid4(),
            contributor_id=uuid.UUID(contributor_id),
            case_data=anonymized.anonymized_data,
            original_org_type=org_type,
            status=ContributionStatus.PENDING_REVIEW,
            module=module,
            tags=tags,
            submitted_at=datetime.utcnow()
        )

        self.db.add(contribution)
        await self.db.flush()

        # 4. Assign peer reviewers
        reviewers = await self._assign_reviewers(
            contribution_id=contribution.id,
            module=module,
            exclude_user=contributor_id
        )

        contribution.reviewers = [r.user_id for r in reviewers]
        contribution.review_deadline = datetime.utcnow() + timedelta(days=7)

        await self.db.commit()

        # 5. Notify reviewers
        for reviewer in reviewers:
            await self._notify_reviewer(reviewer, contribution)

        return str(contribution.id)

    async def _assign_reviewers(
        self,
        contribution_id: uuid.UUID,
        module: str,
        exclude_user: str,
        count: int = 3
    ) -> List[UserReputation]:
        """
        Smart reviewer assignment

        Criteria:
        - High reputation in module
        - Different organization
        - Available (< 5 pending reviews)
        """

        # Get qualified reviewers
        result = await self.db.execute(
            select(UserReputation)
            .where(
                and_(
                    UserReputation.user_id != uuid.UUID(exclude_user),
                    UserReputation.total_points >= 100  # Minimum reputation
                )
            )
            .order_by(UserReputation.total_points.desc())
            .limit(count * 3)
        )

        candidates = result.scalars().all()

        # Filter for module expertise
        qualified = [
            c for c in candidates
            if c.expertise.get(module, 0) >= 50
        ]

        # Check availability
        available = []
        for candidate in qualified:
            pending = await self._get_pending_reviews_count(candidate.user_id)
            if pending < 5:
                available.append(candidate)

        return available[:count]

    async def _get_pending_reviews_count(self, user_id: uuid.UUID) -> int:
        """Get count of pending reviews for user"""

        # Get contributions assigned to user
        result = await self.db.execute(
            select(func.count(CaseContribution.id))
            .where(
                and_(
                    CaseContribution.reviewers.contains([user_id]),
                    CaseContribution.status.in_([
                        ContributionStatus.PENDING_REVIEW,
                        ContributionStatus.IN_REVIEW
                    ])
                )
            )
        )
        return result.scalar() or 0

    async def submit_review(
        self,
        reviewer_id: str,
        contribution_id: str,
        review: Dict[str, Any]
    ) -> str:
        """Submit peer review"""

        peer_review = PeerReview(
            id=uuid.uuid4(),
            contribution_id=uuid.UUID(contribution_id),
            reviewer_id=uuid.UUID(reviewer_id),
            approved=review['approved'],
            quality_score=review['quality_score'],
            feedback=review.get('feedback'),
            suggested_improvements=review.get('improvements'),
            anonymization_ok=review.get('anonymization_ok', True),
            relevance_ok=review.get('relevance_ok', True),
            completeness_ok=review.get('completeness_ok', True),
            lessons_clear=review.get('lessons_clear', True)
        )

        self.db.add(peer_review)
        await self.db.commit()

        # Award reputation to reviewer
        await self._award_reputation(
            reviewer_id,
            points=5,
            reason='peer_review_completed'
        )

        # Check if all reviews done
        await self._check_review_completion(contribution_id)

        return str(peer_review.id)

    async def _check_review_completion(self, contribution_id: str):
        """Check if all reviews done and process result"""

        contribution = await self.db.get(CaseContribution, uuid.UUID(contribution_id))

        # Get all reviews
        result = await self.db.execute(
            select(PeerReview).where(PeerReview.contribution_id == contribution.id)
        )
        reviews = result.scalars().all()

        # Need 3 reviews
        if len(reviews) < 3:
            return

        # Count approvals
        approvals = [r for r in reviews if r.approved]

        # Majority approve?
        if len(approvals) >= 2:
            await self._approve_contribution(contribution, reviews)
        else:
            await self._reject_contribution(contribution, reviews)

    async def _approve_contribution(
        self,
        contribution: CaseContribution,
        reviews: List[PeerReview]
    ):
        """Approve and add to Case Library"""

        contribution.status = ContributionStatus.APPROVED
        contribution.approved_at = datetime.utcnow()

        # Add to Case Library
        case_id = await self.case_library.add_community_case(
            contribution.case_data,
            metadata={
                'contributed_by': str(contribution.contributor_id),
                'contribution_id': str(contribution.id),
                'review_scores': [r.quality_score for r in reviews],
                'community_source': True
            }
        )

        contribution.added_to_library = True
        contribution.library_case_id = case_id

        await self.db.commit()

        # Award reputation to contributor
        avg_quality = sum(r.quality_score for r in reviews) / len(reviews)
        points = int(50 * (avg_quality / 10))

        await self._award_reputation(
            str(contribution.contributor_id),
            points=points,
            reason='case_approved',
            related_contribution_id=contribution.id
        )

        # Notify contributor
        await self._notify_contributor_approved(contribution, points)

    async def _reject_contribution(
        self,
        contribution: CaseContribution,
        reviews: List[PeerReview]
    ):
        """Reject contribution"""
        contribution.status = ContributionStatus.REJECTED
        await self.db.commit()

        # Notify contributor with feedback
        await self._notify_contributor_rejected(contribution, reviews)

    async def _award_reputation(
        self,
        user_id: str,
        points: int,
        reason: str,
        related_contribution_id: Optional[uuid.UUID] = None
    ):
        """Award reputation points"""

        # Get or create reputation
        reputation = await self.db.get(UserReputation, uuid.UUID(user_id))
        if not reputation:
            reputation = UserReputation(user_id=uuid.UUID(user_id))
            self.db.add(reputation)

        # Update points
        reputation.total_points += points

        if reason == 'case_approved':
            reputation.contribution_points += points
            reputation.contributions_count += 1
            if reputation.first_contribution is None:
                reputation.first_contribution = datetime.utcnow()
        elif reason == 'peer_review_completed':
            reputation.review_points += points
            reputation.reviews_count += 1

        # Update level
        reputation.level = self._calculate_level(reputation.total_points)

        # Create transaction
        transaction = ReputationTransaction(
            user_id=uuid.UUID(user_id),
            points=points,
            reason=reason,
            related_contribution_id=related_contribution_id
        )

        self.db.add(transaction)
        await self.db.commit()

    def _calculate_level(self, points: int) -> str:
        """Calculate user level from points"""
        if points < 100:
            return 'newcomer'
        elif points < 500:
            return 'contributor'
        elif points < 2000:
            return 'expert'
        else:
            return 'master'

    def _extract_org_type(self, case_data: Dict) -> str:
        """Extract organization type for matching"""
        context = case_data.get('organization_context', {})
        return f"{context.get('industry', 'unknown')}_{context.get('size', 'medium')}"

    def _extract_tags(self, case_data: Dict, module: str) -> List[str]:
        """Extract searchable tags"""
        tags = [module]

        context = case_data.get('organization_context', {})
        if context.get('industry'):
            tags.append(context['industry'])
        if context.get('size'):
            tags.append(context['size'])

        # Extract from success patterns
        patterns = case_data.get('success_patterns', [])
        for pattern in patterns:
            words = pattern.lower().split()
            tags.extend([w for w in words if len(w) > 5])

        return list(set(tags))[:10]

    async def get_contribution(self, contribution_id: str) -> Optional[CaseContribution]:
        """Get contribution by ID"""
        return await self.db.get(CaseContribution, uuid.UUID(contribution_id))

    async def get_pending_reviews(self, user_id: str) -> List[CaseContribution]:
        """Get contributions pending review by user"""

        result = await self.db.execute(
            select(CaseContribution)
            .where(
                and_(
                    CaseContribution.reviewers.contains([uuid.UUID(user_id)]),
                    CaseContribution.status.in_([
                        ContributionStatus.PENDING_REVIEW,
                        ContributionStatus.IN_REVIEW
                    ])
                )
            )
        )
        return result.scalars().all()

    async def _notify_reviewer(self, reviewer: UserReputation, contribution: CaseContribution):
        """Notify reviewer of assignment (placeholder)"""
        pass

    async def _notify_contributor_approved(self, contribution: CaseContribution, points: int):
        """Notify contributor of approval (placeholder)"""
        pass

    async def _notify_contributor_rejected(self, contribution: CaseContribution, reviews: List[PeerReview]):
        """Notify contributor of rejection (placeholder)"""
        pass

    async def validate_first_submission(self, case_data: Dict[str, Any]) -> bool:
        """Validate first-time submission has all required fields"""
        required = ['organization_context', 'journey', 'metrics', 'success_patterns']
        return all(field in case_data for field in required)
