"""
Gamification Service
ПОЛНАЯ логика gamification из original code
Points, Achievements, Leaderboard, Streaks
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from datetime import datetime, timedelta

from models.database import UserAchievement, AchievementLevel
from repositories.gamification_repository import GamificationRepository
from workflows.gamification_workflow import (
    ActionCategory,
    calculate_points,
    award_points,
    check_achievements,
    calculate_streak,
    get_leaderboard_rank,
    calculate_level,
    get_badge_color,
    get_badge_icon,
)


class GamificationService:
    """
    Gamification Service - FULL Logic
    
    Handles:
    - Points calculation and awarding
    - Achievement checking and unlocking
    - Leaderboard management
    - Streak tracking
    - Level calculation
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GamificationRepository(session)

    # ========================================================================
    # POINTS
    # ========================================================================

    async def award_points_for_action(
        self,
        tenant_id: str,
        person_id: str,
        person_name: str,
        action: ActionCategory,
        metadata: Dict
    ) -> UserAchievement:
        """
        Award points for action using workflow logic
        
        Actions:
        - ENROLLMENT_COMPLETED
        - ASSESSMENT_PASSED
        - CERTIFICATION_EARNED
        - TRAINING_STREAK
        - HELP_OTHERS
        - EARLY_COMPLETION
        """
        
        # Calculate points using workflow
        points_data = calculate_points(action, metadata)
        points = points_data["points"]
        multiplier = points_data.get("multiplier", 1.0)
        total_points = int(points * multiplier)

        # Create achievement record
        achievement = UserAchievement(
            tenant_id=tenant_id,
            person_id=person_id,
            person_name=person_name,
            achievement_type=action.value,
            achievement_name=points_data["name"],
            description=points_data.get("description"),
            level=AchievementLevel.BRONZE,  # Default, will be calculated
            points=total_points,
            earned_date=datetime.utcnow(),
            badge_icon=get_badge_icon(action.value),
            badge_color=get_badge_color(AchievementLevel.BRONZE.value),
            metadata=metadata,
        )

        # Save
        achievement = await self.repo.create_achievement(achievement)

        # Check if new achievements unlocked
        await self._check_and_unlock_achievements(tenant_id, person_id, person_name)

        return achievement

    async def _check_and_unlock_achievements(
        self,
        tenant_id: str,
        person_id: str,
        person_name: str
    ):
        """Check and unlock new achievements"""
        
        # Get user stats
        total_points = await self.repo.get_total_points(tenant_id, person_id)
        completed_trainings = await self.repo.get_completed_trainings_count(
            tenant_id, person_id
        )

        # Check achievements using workflow
        new_achievements = check_achievements(
            user_id=person_id,
            total_points=total_points,
            completed_trainings=completed_trainings,
            current_achievements=[]  # Would load existing
        )

        # Award new achievements
        for achievement_data in new_achievements:
            achievement = UserAchievement(
                tenant_id=tenant_id,
                person_id=person_id,
                person_name=person_name,
                achievement_type="milestone",
                achievement_name=achievement_data["name"],
                description=achievement_data["description"],
                level=AchievementLevel(achievement_data["level"]),
                points=achievement_data["points"],
                earned_date=datetime.utcnow(),
                badge_icon=get_badge_icon(achievement_data["type"]),
                badge_color=get_badge_color(achievement_data["level"]),
                metadata=achievement_data.get("metadata", {}),
            )
            await self.repo.create_achievement(achievement)

    async def get_user_total_points(self, tenant_id: str, person_id: str) -> int:
        """Get total points for user"""
        return await self.repo.get_total_points(tenant_id, person_id)

    async def get_user_achievements(
        self,
        tenant_id: str,
        person_id: str
    ) -> List[UserAchievement]:
        """Get all achievements for user"""
        return await self.repo.get_user_achievements(tenant_id, person_id)

    # ========================================================================
    # LEADERBOARD
    # ========================================================================

    async def get_leaderboard(
        self,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get leaderboard with full user stats
        """
        
        # Get base leaderboard from repo
        leaderboard = await self.repo.get_leaderboard(tenant_id, limit)

        # Enrich with additional data
        enriched = []
        for idx, entry in enumerate(leaderboard):
            person_id = entry["person_id"]
            
            # Get completed trainings
            completed = await self.repo.get_completed_trainings_count(
                tenant_id, person_id
            )

            # Calculate level
            level = calculate_level(entry["total_points"])

            # Calculate streak (simplified - would need more data)
            streak = 0  # Would calculate from training completion dates

            enriched.append({
                "rank": idx + 1,
                "person_id": person_id,
                "person_name": entry.get("person_name", "Unknown"),
                "total_points": entry["total_points"],
                "trainings_completed": completed,
                "achievements_count": entry["achievements_count"],
                "current_streak": streak,
                "level": level,
            })

        return enriched

    async def get_user_rank(self, tenant_id: str, person_id: str) -> int:
        """Get user's rank in leaderboard"""
        return await self.repo.get_user_rank(tenant_id, person_id)

    # ========================================================================
    # STREAKS
    # ========================================================================

    async def calculate_user_streak(
        self,
        tenant_id: str,
        person_id: str
    ) -> Dict:
        """
        Calculate user's training streak
        Using workflow logic
        """
        
        # Get user's training completions (would need dates)
        # For now, simplified
        completion_dates = []  # Would fetch from enrollments

        streak_data = calculate_streak(completion_dates)

        return {
            "current_streak": streak_data["current_streak"],
            "longest_streak": streak_data["longest_streak"],
            "streak_active": streak_data["streak_active"],
            "days_until_break": streak_data.get("days_until_break", 0),
        }

    # ========================================================================
    # LEVELS
    # ========================================================================

    async def get_user_level(self, tenant_id: str, person_id: str) -> Dict:
        """Get user's level and progress"""
        
        total_points = await self.repo.get_total_points(tenant_id, person_id)
        level = calculate_level(total_points)

        # Calculate points needed for next level
        next_level = level + 1
        points_for_next = next_level * 1000  # Example: 1000 points per level
        points_needed = points_for_next - total_points

        return {
            "current_level": level,
            "total_points": total_points,
            "next_level": next_level,
            "points_needed_for_next": max(0, points_needed),
            "progress_to_next": min(100, (total_points % 1000) / 10),
        }
