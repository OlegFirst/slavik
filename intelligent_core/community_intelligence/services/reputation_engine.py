"""
Reputation Engine

Manages community reputation system:
- Point calculations
- Level progression
- Expertise tracking
- Marketplace priority
"""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from ..models.database import (
    UserReputation,
    ReputationTransaction,
    ContributionStatus
)
from ..config import settings
from shared.eventbus import EventBusClient

logger = logging.getLogger(__name__)


class ReputationEngine:
    """
    Service for reputation management

    Features:
    - Point awards for contributions and reviews
    - Automatic level progression
    - Module-specific expertise tracking
    - Marketplace priority calculation
    """

    def __init__(self, db: AsyncSession, eventbus: EventBusClient):
        self.db = db
        self.eventbus = eventbus

    async def award_points(
        self,
        user_id: UUID,
        points: int,
        reason: str,
        module: Optional[str] = None,
        related_contribution_id: Optional[UUID] = None
    ):
        """
        Award reputation points to user

        Args:
            user_id: User receiving points
            points: Number of points to award
            reason: Reason for award ('case_approved', 'peer_review', etc.)
            module: BCM module ('bia', 'risk', etc.) for expertise tracking
            related_contribution_id: Related contribution if applicable

        Side effects:
            - Updates total_points
            - Updates module expertise
            - Updates level if threshold crossed
            - Creates transaction record
            - Publishes reputation events
        """

        # Get or create reputation
        reputation = await self._get_or_create_reputation(user_id)

        old_level = reputation.level
        old_points = reputation.total_points

        # Update points
        reputation.total_points += points

        # Update type-specific counters
        if reason == 'case_approved':
            reputation.contribution_points += points
            reputation.contributions_count += 1
            reputation.cases_approved += 1

            if reputation.first_contribution is None:
                reputation.first_contribution = datetime.utcnow()

            # Update avg case quality
            if related_contribution_id:
                await self._update_avg_case_quality(reputation, related_contribution_id)

        elif reason == 'peer_review_completed':
            reputation.review_points += points
            reputation.reviews_count += 1

        elif reason == 'helpful_review':
            reputation.review_points += points
            reputation.helpful_reviews_count += 1

        # Update module expertise
        if module:
            current_expertise = reputation.expertise.get(module, 0)
            reputation.expertise[module] = current_expertise + points

        # Update level
        new_level = self._calculate_level(reputation.total_points)
        if new_level != old_level:
            reputation.level = new_level
            level_changed = True
        else:
            level_changed = False

        # Update marketplace priority
        reputation.marketplace_priority = self._calculate_marketplace_priority(reputation)

        reputation.updated_at = datetime.utcnow()

        # Create transaction record
        transaction = ReputationTransaction(
            id=uuid4(),
            user_id=user_id,
            points=points,
            reason=reason,
            related_contribution_id=related_contribution_id,
            created_at=datetime.utcnow()
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(reputation)

        logger.info(
            f"Awarded {points} points to user {user_id} for '{reason}'. "
            f"Total: {reputation.total_points} (was {old_points})"
        )

        # Publish event
        await self.eventbus.publish('reputation.points_awarded', {
            'user_id': str(user_id),
            'points': points,
            'reason': reason,
            'total_points': reputation.total_points,
            'level': reputation.level,
            'module': module
        })

        # Level up event
        if level_changed:
            await self.eventbus.publish('reputation.level_up', {
                'user_id': str(user_id),
                'old_level': old_level,
                'new_level': new_level,
                'total_points': reputation.total_points
            })

            logger.info(
                f"🎉 User {user_id} leveled up: {old_level} → {new_level}"
            )

    async def _get_or_create_reputation(self, user_id: UUID) -> UserReputation:
        """Get existing reputation or create new"""

        reputation = await self.db.get(UserReputation, user_id)

        if not reputation:
            # Get user's org_id (would need to join with users table)
            # For now, will be set when creating
            reputation = UserReputation(
                user_id=user_id,
                org_id=UUID('00000000-0000-0000-0000-000000000000'),  # Placeholder
                total_points=0,
                level='newcomer',
                expertise={},
                contribution_points=0,
                contributions_count=0,
                cases_approved=0,
                cases_rejected=0,
                avg_case_quality=0.0,
                review_points=0,
                reviews_count=0,
                helpful_reviews_count=0,
                marketplace_priority=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(reputation)
            await self.db.commit()
            await self.db.refresh(reputation)

            logger.info(f"Created new reputation profile for user {user_id}")

        return reputation

    def _calculate_level(self, total_points: int) -> str:
        """
        Calculate user level from total points

        Levels:
        - newcomer: 0-99
        - contributor: 100-499
        - expert: 500-1999
        - master: 2000+
        """

        if total_points >= settings.LEVEL_THRESHOLDS['master']:
            return 'master'
        elif total_points >= settings.LEVEL_THRESHOLDS['expert']:
            return 'expert'
        elif total_points >= settings.LEVEL_THRESHOLDS['contributor']:
            return 'contributor'
        else:
            return 'newcomer'

    def _calculate_marketplace_priority(self, reputation: UserReputation) -> int:
        """
        Calculate marketplace priority score

        Factors:
        - Total points (50%)
        - Case quality (25%)
        - Review quality (25%)

        Returns:
            Priority score (0-1000)
        """

        # Points component (0-500)
        points_score = min(reputation.total_points / 4, 500)

        # Case quality component (0-250)
        case_quality_score = reputation.avg_case_quality * 25

        # Review quality component (0-250)
        if reputation.reviews_count > 0:
            review_quality = reputation.helpful_reviews_count / reputation.reviews_count
            review_quality_score = review_quality * 250
        else:
            review_quality_score = 0

        priority = int(points_score + case_quality_score + review_quality_score)

        return min(priority, 1000)  # Cap at 1000

    async def _update_avg_case_quality(
        self,
        reputation: UserReputation,
        contribution_id: UUID
    ):
        """Update average case quality from peer reviews"""

        from ..models.database import CaseContribution, PeerReview

        # Get contribution
        contribution = await self.db.get(CaseContribution, contribution_id)
        if not contribution:
            return

        # Get reviews
        result = await self.db.execute(
            select(PeerReview).where(PeerReview.contribution_id == contribution_id)
        )
        reviews = result.scalars().all()

        if not reviews:
            return

        # Calculate average quality from approved reviews
        approved_reviews = [r for r in reviews if r.approved]
        if approved_reviews:
            avg_quality = sum(r.quality_score for r in approved_reviews) / len(approved_reviews)

            # Update running average
            current_avg = reputation.avg_case_quality
            approved_count = reputation.cases_approved

            if approved_count == 1:
                # First case
                reputation.avg_case_quality = avg_quality / 10
            else:
                # Weighted average
                total = (current_avg * (approved_count - 1)) + (avg_quality / 10)
                reputation.avg_case_quality = total / approved_count

    async def get_reputation(self, user_id: UUID) -> Optional[UserReputation]:
        """Get user reputation profile"""
        return await self.db.get(UserReputation, user_id)

    async def get_leaderboard(
        self,
        module: Optional[str] = None,
        limit: int = 10
    ) -> list[UserReputation]:
        """
        Get top contributors leaderboard

        Args:
            module: Filter by module expertise (optional)
            limit: Number of results

        Returns:
            List of top reputation profiles
        """

        query = select(UserReputation)

        if module:
            # Order by module expertise
            query = query.order_by(
                UserReputation.expertise[module].desc()
            )
        else:
            # Order by total points
            query = query.order_by(UserReputation.total_points.desc())

        query = query.limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_transactions(
        self,
        user_id: UUID,
        limit: int = 20
    ) -> list[ReputationTransaction]:
        """Get reputation transaction history for user"""

        result = await self.db.execute(
            select(ReputationTransaction)
            .where(ReputationTransaction.user_id == user_id)
            .order_by(ReputationTransaction.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()

    async def get_expertise_level(
        self,
        user_id: UUID,
        module: str
    ) -> str:
        """
        Get user's expertise level in specific module

        Levels:
        - novice: 0-49
        - intermediate: 50-149
        - advanced: 150-499
        - expert: 500+
        """

        reputation = await self.get_reputation(user_id)
        if not reputation:
            return 'novice'

        points = reputation.expertise.get(module, 0)

        if points >= 500:
            return 'expert'
        elif points >= 150:
            return 'advanced'
        elif points >= 50:
            return 'intermediate'
        else:
            return 'novice'
