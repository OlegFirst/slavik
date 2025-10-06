"""
Peer Review Service

Manages peer review process for case contributions:
- Smart reviewer assignment
- Review validation
- Approval/rejection workflow
- Quality assurance
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
import logging

from ..models.database import (
    CaseContribution,
    PeerReview,
    UserReputation,
    ContributionStatus
)
from ..config import settings
from shared.eventbus import EventBusClient

logger = logging.getLogger(__name__)


class PeerReviewService:
    """
    Service for peer review management

    Key features:
    - Smart reviewer assignment (expertise + availability)
    - Review quality validation
    - Automatic approval/rejection
    - Reputation updates
    """

    def __init__(
        self,
        db: AsyncSession,
        eventbus: EventBusClient,
        reputation_engine
    ):
        self.db = db
        self.eventbus = eventbus
        self.reputation_engine = reputation_engine

    async def assign_reviewers(
        self,
        contribution_id: UUID,
        module: str,
        contributor_id: UUID,
        contributor_org_id: UUID,
        count: int = None
    ) -> List[UserReputation]:
        """
        Smart reviewer assignment

        Criteria:
        1. Expertise: has experience in module (expertise[module] >= 50)
        2. Diversity: different organization
        3. Availability: < 5 pending reviews
        4. Quality: high helpful_reviews_count preferred
        5. Activity: recent activity preferred

        Returns:
            List of assigned reviewers
        """

        if count is None:
            count = settings.REVIEWERS_PER_CONTRIBUTION

        # Get qualified candidates
        result = await self.db.execute(
            select(UserReputation)
            .where(
                and_(
                    UserReputation.user_id != contributor_id,
                    UserReputation.org_id != contributor_org_id,
                    UserReputation.total_points >= settings.MIN_REPUTATION_TO_REVIEW
                )
            )
            .order_by(UserReputation.total_points.desc())
            .limit(count * 3)  # Get 3x candidates for filtering
        )

        candidates = result.scalars().all()

        # Filter for module expertise
        qualified = []
        for candidate in candidates:
            module_expertise = candidate.expertise.get(module, 0)
            if module_expertise >= settings.MIN_EXPERTISE_TO_REVIEW:
                qualified.append(candidate)

        # Check availability
        available = []
        for candidate in qualified:
            pending_count = await self._get_pending_reviews_count(candidate.user_id)
            if pending_count < settings.MAX_REVIEWS_PENDING:
                available.append(candidate)

        # Select top reviewers
        selected = available[:count]

        if len(selected) < count:
            logger.warning(
                f"Could only assign {len(selected)} reviewers for contribution "
                f"{contribution_id} (needed {count})"
            )

        # Create assignments
        for reviewer in selected:
            await self.eventbus.publish('case.review.assigned', {
                'contribution_id': str(contribution_id),
                'reviewer_id': str(reviewer.user_id),
                'module': module,
                'deadline': (datetime.utcnow() + timedelta(
                    days=settings.REVIEW_DEADLINE_DAYS
                )).isoformat()
            })

        logger.info(
            f"Assigned {len(selected)} reviewers to contribution {contribution_id}"
        )

        return selected

    async def _get_pending_reviews_count(self, user_id: UUID) -> int:
        """Get count of pending reviews for user"""

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
        reviewer_id: UUID,
        contribution_id: UUID,
        review_data: Dict[str, Any]
    ) -> PeerReview:
        """
        Submit peer review

        Args:
            reviewer_id: User submitting review
            contribution_id: Contribution being reviewed
            review_data: {
                'approved': bool,
                'quality_score': int (1-10),
                'feedback': str,
                'suggested_improvements': str,
                'anonymization_ok': bool,
                'relevance_ok': bool,
                'completeness_ok': bool,
                'lessons_clear': bool
            }

        Returns:
            Created peer review
        """

        # Validate reviewer is assigned
        contribution = await self.db.get(CaseContribution, contribution_id)
        if not contribution:
            raise ValueError(f"Contribution {contribution_id} not found")

        if reviewer_id not in contribution.reviewers:
            raise ValueError(f"User {reviewer_id} not assigned as reviewer")

        # Check if already reviewed
        existing = await self.db.execute(
            select(PeerReview).where(
                and_(
                    PeerReview.contribution_id == contribution_id,
                    PeerReview.reviewer_id == reviewer_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Review already submitted")

        # Validate review data
        self._validate_review_data(review_data)

        # Create review
        peer_review = PeerReview(
            id=uuid4(),
            contribution_id=contribution_id,
            reviewer_id=reviewer_id,
            approved=review_data['approved'],
            quality_score=review_data['quality_score'],
            feedback=review_data.get('feedback'),
            suggested_improvements=review_data.get('suggested_improvements'),
            anonymization_ok=review_data.get('anonymization_ok', True),
            relevance_ok=review_data.get('relevance_ok', True),
            completeness_ok=review_data.get('completeness_ok', True),
            lessons_clear=review_data.get('lessons_clear', True),
            reviewed_at=datetime.utcnow()
        )

        self.db.add(peer_review)

        # Update contribution status
        if contribution.status == ContributionStatus.PENDING_REVIEW:
            contribution.status = ContributionStatus.IN_REVIEW

        await self.db.commit()
        await self.db.refresh(peer_review)

        # Award reputation to reviewer
        await self.reputation_engine.award_points(
            user_id=reviewer_id,
            points=settings.POINTS_PEER_REVIEW,
            reason='peer_review_completed',
            related_contribution_id=contribution_id
        )

        # Publish event
        await self.eventbus.publish('review.submitted', {
            'review_id': str(peer_review.id),
            'contribution_id': str(contribution_id),
            'reviewer_id': str(reviewer_id),
            'approved': peer_review.approved,
            'quality_score': peer_review.quality_score
        })

        # Check if all reviews done
        await self.check_review_completion(contribution_id)

        logger.info(
            f"Review submitted by {reviewer_id} for contribution {contribution_id}: "
            f"{'APPROVED' if peer_review.approved else 'REJECTED'} "
            f"(quality: {peer_review.quality_score}/10)"
        )

        return peer_review

    def _validate_review_data(self, review_data: Dict[str, Any]):
        """Validate review data structure"""

        required = ['approved', 'quality_score']
        for field in required:
            if field not in review_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate quality score
        score = review_data['quality_score']
        if not isinstance(score, int) or not (1 <= score <= 10):
            raise ValueError("Quality score must be integer between 1 and 10")

        # Feedback required if rejected
        if not review_data['approved'] and not review_data.get('feedback'):
            raise ValueError("Feedback required when rejecting contribution")

    async def check_review_completion(self, contribution_id: UUID):
        """
        Check if all reviews completed and process result

        Approval logic:
        - Need all 3 reviews (REVIEWERS_PER_CONTRIBUTION)
        - If 2+ approve → APPROVED
        - Otherwise → REJECTED
        """

        contribution = await self.db.get(CaseContribution, contribution_id)

        # Get all reviews
        result = await self.db.execute(
            select(PeerReview).where(PeerReview.contribution_id == contribution_id)
        )
        reviews = result.scalars().all()

        # Need all reviews
        expected_count = len(contribution.reviewers)
        if len(reviews) < expected_count:
            logger.debug(
                f"Contribution {contribution_id}: {len(reviews)}/{expected_count} "
                f"reviews completed"
            )
            return

        # Count approvals
        approvals = [r for r in reviews if r.approved]
        approval_count = len(approvals)

        logger.info(
            f"Contribution {contribution_id}: All {len(reviews)} reviews completed. "
            f"Approvals: {approval_count}/{len(reviews)}"
        )

        # Majority approve?
        if approval_count >= settings.APPROVAL_THRESHOLD:
            await self._approve_contribution(contribution, reviews)
        else:
            await self._reject_contribution(contribution, reviews)

    async def _approve_contribution(
        self,
        contribution: CaseContribution,
        reviews: List[PeerReview]
    ):
        """Approve contribution and add to Case Library"""

        logger.info(f"✅ Approving contribution {contribution.id}")

        contribution.status = ContributionStatus.APPROVED
        contribution.approved_at = datetime.utcnow()

        # Calculate reputation reward
        avg_quality = sum(r.quality_score for r in reviews) / len(reviews)
        points = int(settings.POINTS_CASE_APPROVED_BASE * (avg_quality / 10))

        await self.db.commit()

        # Award reputation to contributor
        await self.reputation_engine.award_points(
            user_id=contribution.contributor_id,
            points=points,
            reason='case_approved',
            module=contribution.module,
            related_contribution_id=contribution.id
        )

        # Publish approval event (Case Library will handle adding)
        await self.eventbus.publish('case.approved', {
            'contribution_id': str(contribution.id),
            'contributor_id': str(contribution.contributor_id),
            'module': contribution.module,
            'case_data': contribution.case_data,
            'avg_quality_score': avg_quality,
            'reputation_earned': points
        })

        logger.info(
            f"✅ Contribution {contribution.id} approved! "
            f"Contributor earned {points} reputation points"
        )

    async def _reject_contribution(
        self,
        contribution: CaseContribution,
        reviews: List[PeerReview]
    ):
        """Reject contribution"""

        logger.info(f"❌ Rejecting contribution {contribution.id}")

        contribution.status = ContributionStatus.REJECTED
        await self.db.commit()

        # Publish rejection event
        await self.eventbus.publish('case.rejected', {
            'contribution_id': str(contribution.id),
            'contributor_id': str(contribution.contributor_id),
            'module': contribution.module,
            'feedback': [
                {
                    'reviewer_id': str(r.reviewer_id),
                    'feedback': r.feedback,
                    'suggested_improvements': r.suggested_improvements
                }
                for r in reviews if not r.approved
            ]
        })

        logger.info(f"❌ Contribution {contribution.id} rejected")

    async def get_pending_reviews(self, user_id: UUID) -> List[CaseContribution]:
        """Get contributions pending review by user"""

        result = await self.db.execute(
            select(CaseContribution)
            .where(
                and_(
                    CaseContribution.reviewers.contains([user_id]),
                    CaseContribution.status.in_([
                        ContributionStatus.PENDING_REVIEW,
                        ContributionStatus.IN_REVIEW
                    ])
                )
            )
            .order_by(CaseContribution.review_deadline.asc())
        )

        return result.scalars().all()

    async def get_user_reviews(
        self,
        user_id: UUID,
        limit: int = 20
    ) -> List[PeerReview]:
        """Get reviews submitted by user"""

        result = await self.db.execute(
            select(PeerReview)
            .where(PeerReview.reviewer_id == user_id)
            .order_by(PeerReview.reviewed_at.desc())
            .limit(limit)
        )

        return result.scalars().all()
