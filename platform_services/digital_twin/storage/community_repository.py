"""
Community Level Database Repository

Repository для работы с данными Community Level:
- Community Learnings (Knowledge Exchange)
- Learning Feedback
- User Networking Profiles
- Privacy Settings
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    CommunityLearningModel,
    LearningFeedbackModel,
    UserNetworkingProfileModel,
    CommunityPrivacySettingsModel
)

logger = logging.getLogger(__name__)


class CommunityRepository:
    """
    Repository for Community Level database operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    # ============================================
    # COMMUNITY LEARNINGS (KNOWLEDGE EXCHANGE)
    # ============================================

    async def create_learning(
        self,
        learning_data: Dict[str, Any]
    ) -> CommunityLearningModel:
        """
        Create community learning

        Args:
            learning_data: Learning data

        Returns:
            Created learning model
        """
        learning = CommunityLearningModel(**learning_data)
        self.session.add(learning)
        await self.session.flush()

        logger.info(f"Created community learning: {learning.learning_id}")

        return learning

    async def get_learning(
        self,
        learning_id: str
    ) -> Optional[CommunityLearningModel]:
        """Get learning by ID"""
        stmt = select(CommunityLearningModel).where(
            CommunityLearningModel.learning_id == learning_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def query_learnings(
        self,
        industry: Optional[str] = None,
        size_category: Optional[str] = None,
        maturity_level: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_effectiveness: float = 0.0,
        min_success_rate: float = 0.0,
        limit: int = 50
    ) -> List[CommunityLearningModel]:
        """
        Query learnings with filters

        Args:
            industry: Filter by industry
            size_category: Filter by organization size
            maturity_level: Filter by BCM maturity
            tags: Filter by tags (ANY)
            min_effectiveness: Minimum effectiveness score
            min_success_rate: Minimum success rate
            limit: Max results

        Returns:
            List of matching learnings
        """
        stmt = select(CommunityLearningModel)

        conditions = []

        # Industry filter
        if industry:
            conditions.append(CommunityLearningModel.industry == industry)

        # Size filter
        if size_category:
            conditions.append(CommunityLearningModel.size_category == size_category)

        # Maturity filter
        if maturity_level:
            conditions.append(CommunityLearningModel.maturity_level == maturity_level)

        # Tags filter (contains ANY of the specified tags)
        if tags:
            # PostgreSQL ARRAY contains ANY
            conditions.append(
                CommunityLearningModel.tags.overlap(tags)
            )

        # Effectiveness filter
        if min_effectiveness > 0:
            conditions.append(
                CommunityLearningModel.effectiveness_score >= min_effectiveness
            )

        # Success rate filter
        if min_success_rate > 0:
            conditions.append(
                CommunityLearningModel.success_rate >= min_success_rate
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Order by relevance (effectiveness * usage)
        stmt = stmt.order_by(
            (CommunityLearningModel.effectiveness_score *
             CommunityLearningModel.times_used).desc()
        )

        stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_top_learnings(
        self,
        industry: Optional[str] = None,
        limit: int = 20
    ) -> List[CommunityLearningModel]:
        """Get top learnings by usage and effectiveness"""
        stmt = select(CommunityLearningModel)

        if industry:
            stmt = stmt.where(CommunityLearningModel.industry == industry)

        # Order by combined score
        stmt = stmt.order_by(
            (CommunityLearningModel.success_rate *
             CommunityLearningModel.times_used).desc()
        )

        stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_learning_metrics(
        self,
        learning_id: str,
        times_used: Optional[int] = None,
        success_rate: Optional[float] = None,
        average_rating: Optional[float] = None
    ) -> Optional[CommunityLearningModel]:
        """Update learning metrics"""
        updates = {}

        if times_used is not None:
            updates['times_used'] = times_used
        if success_rate is not None:
            updates['success_rate'] = success_rate
        if average_rating is not None:
            updates['average_rating'] = average_rating

        if not updates:
            return None

        updates['updated_at'] = datetime.utcnow()

        stmt = (
            update(CommunityLearningModel)
            .where(CommunityLearningModel.learning_id == learning_id)
            .values(**updates)
            .returning(CommunityLearningModel)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_community_statistics(self) -> Dict[str, Any]:
        """Get knowledge exchange statistics"""
        # Total learnings
        total_stmt = select(func.count(CommunityLearningModel.learning_id))
        total = await self.session.scalar(total_stmt)

        # Learnings by industry
        industry_stmt = select(
            CommunityLearningModel.industry,
            func.count(CommunityLearningModel.learning_id)
        ).group_by(CommunityLearningModel.industry)

        industry_result = await self.session.execute(industry_stmt)
        by_industry = {row[0]: row[1] for row in industry_result}

        # Average effectiveness
        avg_effectiveness_stmt = select(
            func.avg(CommunityLearningModel.effectiveness_score)
        )
        avg_effectiveness = await self.session.scalar(avg_effectiveness_stmt) or 0.0

        # Total applications
        total_used_stmt = select(
            func.sum(CommunityLearningModel.times_used)
        )
        total_used = await self.session.scalar(total_used_stmt) or 0

        return {
            'total_learnings': total or 0,
            'learnings_by_industry': by_industry,
            'avg_effectiveness_score': float(avg_effectiveness),
            'total_applications': total_used
        }

    # ============================================
    # LEARNING FEEDBACK
    # ============================================

    async def submit_feedback(
        self,
        feedback_data: Dict[str, Any]
    ) -> LearningFeedbackModel:
        """Submit learning feedback"""
        feedback = LearningFeedbackModel(**feedback_data)
        self.session.add(feedback)
        await self.session.flush()

        logger.info(f"Submitted feedback for learning: {feedback.learning_id}")

        return feedback

    async def get_learning_feedback(
        self,
        learning_id: str,
        limit: int = 100
    ) -> List[LearningFeedbackModel]:
        """Get feedback for learning"""
        stmt = (
            select(LearningFeedbackModel)
            .where(LearningFeedbackModel.learning_id == learning_id)
            .order_by(LearningFeedbackModel.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ============================================
    # USER NETWORKING PROFILES (PEOPLE MATCHING)
    # ============================================

    async def create_profile(
        self,
        profile_data: Dict[str, Any]
    ) -> UserNetworkingProfileModel:
        """Create user networking profile"""
        profile = UserNetworkingProfileModel(**profile_data)
        self.session.add(profile)
        await self.session.flush()

        logger.info(f"Created networking profile for user: {profile.user_id}")

        return profile

    async def get_profile(
        self,
        user_id: str
    ) -> Optional[UserNetworkingProfileModel]:
        """Get user networking profile"""
        stmt = select(UserNetworkingProfileModel).where(
            UserNetworkingProfileModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[UserNetworkingProfileModel]:
        """Update networking profile"""
        updates['updated_at'] = datetime.utcnow()

        stmt = (
            update(UserNetworkingProfileModel)
            .where(UserNetworkingProfileModel.user_id == user_id)
            .values(**updates)
            .returning(UserNetworkingProfileModel)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_profile(
        self,
        user_id: str
    ) -> bool:
        """Delete networking profile"""
        stmt = delete(UserNetworkingProfileModel).where(
            UserNetworkingProfileModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def search_profiles(
        self,
        role: Optional[str] = None,
        experience_level: Optional[str] = None,
        expertise_areas: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        open_to_mentoring: Optional[bool] = None,
        seeking_mentor: Optional[bool] = None,
        open_to_collaboration: Optional[bool] = None,
        visibility_level: str = 'public',
        limit: int = 50
    ) -> List[UserNetworkingProfileModel]:
        """
        Search networking profiles

        Args:
            role: Filter by professional role
            experience_level: Filter by experience level
            expertise_areas: Filter by expertise (ANY)
            languages: Filter by languages (ANY)
            open_to_mentoring: Filter mentors
            seeking_mentor: Filter mentees
            open_to_collaboration: Filter collaborators
            visibility_level: Minimum visibility level
            limit: Max results

        Returns:
            List of matching profiles
        """
        stmt = select(UserNetworkingProfileModel)

        conditions = []

        # Role filter
        if role:
            conditions.append(UserNetworkingProfileModel.role == role)

        # Experience filter
        if experience_level:
            conditions.append(
                UserNetworkingProfileModel.experience_level == experience_level
            )

        # Expertise filter
        if expertise_areas:
            conditions.append(
                UserNetworkingProfileModel.expertise_areas.overlap(expertise_areas)
            )

        # Language filter
        if languages:
            conditions.append(
                UserNetworkingProfileModel.languages.overlap(languages)
            )

        # Mentoring filters
        if open_to_mentoring is not None:
            conditions.append(
                UserNetworkingProfileModel.open_to_mentoring == open_to_mentoring
            )

        if seeking_mentor is not None:
            conditions.append(
                UserNetworkingProfileModel.seeking_mentor == seeking_mentor
            )

        if open_to_collaboration is not None:
            conditions.append(
                UserNetworkingProfileModel.open_to_collaboration == open_to_collaboration
            )

        # Visibility filter
        if visibility_level == 'public':
            conditions.append(
                UserNetworkingProfileModel.visibility_level == 'public'
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(
            UserNetworkingProfileModel.last_active.desc()
        ).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_network_statistics(self) -> Dict[str, Any]:
        """Get networking statistics"""
        # Total profiles
        total_stmt = select(func.count(UserNetworkingProfileModel.user_id))
        total = await self.session.scalar(total_stmt)

        # Profiles by role
        role_stmt = select(
            UserNetworkingProfileModel.role,
            func.count(UserNetworkingProfileModel.user_id)
        ).group_by(UserNetworkingProfileModel.role)

        role_result = await self.session.execute(role_stmt)
        by_role = {row[0]: row[1] for row in role_result}

        # Mentors available
        mentors_stmt = select(
            func.count(UserNetworkingProfileModel.user_id)
        ).where(UserNetworkingProfileModel.open_to_mentoring == True)
        mentors = await self.session.scalar(mentors_stmt) or 0

        # Seeking mentorship
        mentees_stmt = select(
            func.count(UserNetworkingProfileModel.user_id)
        ).where(UserNetworkingProfileModel.seeking_mentor == True)
        mentees = await self.session.scalar(mentees_stmt) or 0

        return {
            'total_professionals': total or 0,
            'professionals_by_role': by_role,
            'mentors_available': mentors,
            'seeking_mentorship': mentees
        }

    # ============================================
    # PRIVACY SETTINGS
    # ============================================

    async def create_privacy_settings(
        self,
        settings_data: Dict[str, Any]
    ) -> CommunityPrivacySettingsModel:
        """Create privacy settings"""
        settings = CommunityPrivacySettingsModel(**settings_data)
        self.session.add(settings)
        await self.session.flush()

        logger.info(f"Created privacy settings for user: {settings.user_id}")

        return settings

    async def get_privacy_settings(
        self,
        user_id: str
    ) -> Optional[CommunityPrivacySettingsModel]:
        """Get privacy settings"""
        stmt = select(CommunityPrivacySettingsModel).where(
            CommunityPrivacySettingsModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_privacy_settings(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[CommunityPrivacySettingsModel]:
        """Update privacy settings"""
        updates['updated_at'] = datetime.utcnow()

        stmt = (
            update(CommunityPrivacySettingsModel)
            .where(CommunityPrivacySettingsModel.user_id == user_id)
            .values(**updates)
            .returning(CommunityPrivacySettingsModel)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
