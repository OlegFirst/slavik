"""
Gamification Repository
Data access for achievements, points, leaderboard
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import UserAchievement, TrainingEnrollment, EnrollmentStatus


class GamificationRepository:
    """Repository for Gamification"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_achievement(self, achievement: UserAchievement) -> UserAchievement:
        """Create user achievement"""
        self.session.add(achievement)
        await self.session.flush()
        await self.session.refresh(achievement)
        return achievement

    async def get_user_achievements(
        self,
        tenant_id: str,
        person_id: str
    ) -> List[UserAchievement]:
        """Get all achievements for user"""
        result = await self.session.execute(
            select(UserAchievement).where(
                and_(
                    UserAchievement.tenant_id == tenant_id,
                    UserAchievement.person_id == person_id
                )
            ).order_by(UserAchievement.earned_date.desc())
        )
        return list(result.scalars().all())

    async def get_total_points(self, tenant_id: str, person_id: str) -> int:
        """Get total points for user"""
        result = await self.session.execute(
            select(func.sum(UserAchievement.points)).where(
                and_(
                    UserAchievement.tenant_id == tenant_id,
                    UserAchievement.person_id == person_id
                )
            )
        )
        return result.scalar() or 0

    async def get_completed_trainings_count(self, tenant_id: str, person_id: str) -> int:
        """Get count of completed trainings"""
        result = await self.session.execute(
            select(func.count(TrainingEnrollment.id)).where(
                and_(
                    TrainingEnrollment.tenant_id == tenant_id,
                    TrainingEnrollment.person_id == person_id,
                    TrainingEnrollment.status.in_([
                        EnrollmentStatus.COMPLETED,
                        EnrollmentStatus.ASSESSED,
                        EnrollmentStatus.CERTIFIED
                    ])
                )
            )
        )
        return result.scalar() or 0

    async def get_leaderboard(
        self,
        tenant_id: str,
        limit: int = 50
    ) -> List[dict]:
        """Get leaderboard for tenant"""
        # Aggregate points and trainings per person
        query = select(
            UserAchievement.person_id,
            func.sum(UserAchievement.points).label('total_points'),
            func.count(UserAchievement.id).label('achievements_count')
        ).where(
            UserAchievement.tenant_id == tenant_id
        ).group_by(
            UserAchievement.person_id
        ).order_by(
            desc('total_points')
        ).limit(limit)

        result = await self.session.execute(query)
        return [
            {
                "person_id": row.person_id,
                "total_points": row.total_points or 0,
                "achievements_count": row.achievements_count or 0
            }
            for row in result.all()
        ]

    async def get_user_rank(self, tenant_id: str, person_id: str) -> int:
        """Get user's rank in leaderboard"""
        # Get user's points
        user_points = await self.get_total_points(tenant_id, person_id)

        # Count users with more points
        result = await self.session.execute(
            select(func.count(func.distinct(UserAchievement.person_id))).where(
                and_(
                    UserAchievement.tenant_id == tenant_id,
                    UserAchievement.person_id != person_id
                )
            ).group_by(UserAchievement.person_id).having(
                func.sum(UserAchievement.points) > user_points
            )
        )
        higher_ranked = result.scalar() or 0
        return higher_ranked + 1
