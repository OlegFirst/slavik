"""
Reputation Service - Business Logic
Handles user reputation, badges, and gamification
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, update, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    UserReputation, Badge, UserBadge, ReputationEvent,
    ForumTopic, ForumPost, ReputationLevel
)


# Reputation point system
REPUTATION_POINTS = {
    'topic_created': 2,
    'post_created': 1,
    'post_upvoted': 5,
    'post_downvoted': -2,
    'topic_upvoted': 3,
    'topic_downvoted': -1,
    'solution_marked': 15,
    'badge_earned': 10,  # Base value, actual depends on badge
}


class ReputationService:
    """
    Reputation and gamification business logic

    Responsibilities:
    - Reputation tracking
    - Badge management
    - Leaderboards
    - Achievement checking
    """

    async def get_or_create_reputation(
        self,
        db: AsyncSession,
        user_id: str
    ) -> UserReputation:
        """
        Get user reputation, create if doesn't exist

        Args:
            db: Database session
            user_id: User ID

        Returns:
            UserReputation instance
        """
        result = await db.execute(
            select(UserReputation).where(UserReputation.user_id == user_id)
        )
        reputation = result.scalar_one_or_none()

        if not reputation:
            reputation = UserReputation(
                user_id=user_id,
                reputation_score=0,
                reputation_level=ReputationLevel.newbie
            )
            db.add(reputation)
            await db.commit()
            await db.refresh(reputation)

        return reputation

    async def award_points(
        self,
        db: AsyncSession,
        user_id: str,
        event_type: str,
        points: Optional[int] = None,
        topic_id: Optional[int] = None,
        post_id: Optional[int] = None,
        badge_id: Optional[int] = None
    ) -> ReputationEvent:
        """
        Award reputation points to user

        Args:
            db: Database session
            user_id: User ID
            event_type: Type of event
            points: Points to award (if None, use default for event_type)
            topic_id: Related topic ID
            post_id: Related post ID
            badge_id: Related badge ID

        Returns:
            Created ReputationEvent
        """
        # Get reputation
        reputation = await self.get_or_create_reputation(db, user_id)

        # Calculate points
        if points is None:
            points = REPUTATION_POINTS.get(event_type, 0)

        # Create event
        event = ReputationEvent(
            user_id=user_id,
            event_type=event_type,
            points_change=points,
            topic_id=topic_id,
            post_id=post_id,
            badge_id=badge_id
        )
        db.add(event)

        # Update reputation
        reputation.reputation_score += points

        # Update stats based on event type
        if event_type == 'topic_created':
            reputation.topics_created += 1
        elif event_type == 'post_created':
            reputation.posts_created += 1
        elif event_type == 'solution_marked':
            reputation.solutions_marked += 1
        elif event_type == 'post_upvoted':
            reputation.upvotes_received += 1
        elif event_type == 'post_downvoted':
            reputation.downvotes_received += 1
        elif event_type == 'badge_earned':
            reputation.badges_earned += 1

        await db.commit()
        await db.refresh(reputation)
        await db.refresh(event)

        # Check for badge eligibility
        await self._check_and_award_badges(db, user_id, reputation)

        return event

    async def _check_and_award_badges(
        self,
        db: AsyncSession,
        user_id: str,
        reputation: UserReputation
    ):
        """
        Check if user qualifies for any badges

        Args:
            db: Database session
            user_id: User ID
            reputation: User reputation object
        """
        # Get all badges
        result = await db.execute(select(Badge))
        badges = result.scalars().all()

        for badge in badges:
            # Check if user already has this badge
            existing = await db.execute(
                select(UserBadge).where(
                    and_(
                        UserBadge.user_id == user_id,
                        UserBadge.badge_id == badge.id
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue  # Already has badge

            # Check criteria
            if self._check_badge_criteria(badge, reputation):
                await self.award_badge(db, user_id, badge.id, auto_awarded=True)

    def _check_badge_criteria(
        self,
        badge: Badge,
        reputation: UserReputation
    ) -> bool:
        """
        Check if user meets badge criteria

        Args:
            badge: Badge to check
            reputation: User reputation

        Returns:
            True if criteria met
        """
        if not badge.criteria:
            return False

        criteria = badge.criteria

        # Check each criterion
        for key, required_value in criteria.items():
            actual_value = getattr(reputation, key, None)
            if actual_value is None or actual_value < required_value:
                return False

        return True

    async def award_badge(
        self,
        db: AsyncSession,
        user_id: str,
        badge_id: int,
        earned_for: Optional[str] = None,
        auto_awarded: bool = False
    ) -> UserBadge:
        """
        Award a badge to user

        Args:
            db: Database session
            user_id: User ID
            badge_id: Badge ID
            earned_for: Description of achievement
            auto_awarded: Whether badge was auto-awarded

        Returns:
            UserBadge instance
        """
        # Get badge
        result = await db.execute(
            select(Badge).where(Badge.id == badge_id)
        )
        badge = result.scalar_one_or_none()

        if not badge:
            raise ValueError(f"Badge {badge_id} not found")

        # Create user badge
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            earned_for=earned_for or f"Earned {badge.name}"
        )
        db.add(user_badge)

        # Award reputation points
        if auto_awarded:
            await self.award_points(
                db,
                user_id,
                event_type='badge_earned',
                points=badge.points_value,
                badge_id=badge_id
            )

        await db.commit()
        await db.refresh(user_badge)

        return user_badge

    async def get_user_badges(
        self,
        db: AsyncSession,
        user_id: str
    ) -> List[UserBadge]:
        """
        Get badges earned by user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of user badges
        """
        result = await db.execute(
            select(UserBadge)
            .where(UserBadge.user_id == user_id)
            .order_by(UserBadge.earned_at.desc())
        )
        return result.scalars().all()

    async def get_leaderboard(
        self,
        db: AsyncSession,
        period: str = 'all_time',  # all_time, monthly, weekly
        limit: int = 50
    ) -> List[Tuple[int, UserReputation]]:
        """
        Get reputation leaderboard

        Args:
            db: Database session
            period: Time period filter
            limit: Maximum results

        Returns:
            List of (rank, UserReputation) tuples
        """
        stmt = select(UserReputation).order_by(
            UserReputation.reputation_score.desc()
        ).limit(limit)

        # TODO: Add period filtering when we have created_at on events

        result = await db.execute(stmt)
        users = result.scalars().all()

        # Add rank
        leaderboard = [(idx + 1, user) for idx, user in enumerate(users)]

        return leaderboard

    async def get_reputation_history(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> List[ReputationEvent]:
        """
        Get user's reputation history

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum results

        Returns:
            List of reputation events
        """
        result = await db.execute(
            select(ReputationEvent)
            .where(ReputationEvent.user_id == user_id)
            .order_by(ReputationEvent.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_badges(
        self,
        db: AsyncSession,
        badge_type: Optional[str] = None
    ) -> List[Badge]:
        """
        Get all available badges

        Args:
            db: Database session
            badge_type: Filter by type (certification, achievement, special)

        Returns:
            List of badges
        """
        stmt = select(Badge)

        if badge_type:
            stmt = stmt.where(Badge.badge_type == badge_type)

        stmt = stmt.order_by(Badge.badge_type, Badge.tier)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_forum_stats(
        self,
        db: AsyncSession
    ) -> dict:
        """
        Get overall forum statistics

        Args:
            db: Database session

        Returns:
            Dictionary with stats
        """
        # Total topics
        topics_result = await db.execute(
            select(func.count()).select_from(ForumTopic)
        )
        total_topics = topics_result.scalar() or 0

        # Total posts
        posts_result = await db.execute(
            select(func.count()).select_from(ForumPost)
        )
        total_posts = posts_result.scalar() or 0

        # Total users with reputation
        users_result = await db.execute(
            select(func.count()).select_from(UserReputation)
        )
        total_users = users_result.scalar() or 0

        # Recent activity (last 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)

        recent_topics = await db.execute(
            select(func.count())
            .select_from(ForumTopic)
            .where(ForumTopic.created_at >= yesterday)
        )
        recent_topics_count = recent_topics.scalar() or 0

        recent_posts = await db.execute(
            select(func.count())
            .select_from(ForumPost)
            .where(ForumPost.created_at >= yesterday)
        )
        recent_posts_count = recent_posts.scalar() or 0

        return {
            'total_topics': total_topics,
            'total_posts': total_posts,
            'total_users': total_users,
            'recent_topics_count': recent_topics_count,
            'recent_posts_count': recent_posts_count
        }
