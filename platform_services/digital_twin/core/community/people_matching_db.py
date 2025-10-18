"""
People Matching Service (Database-enabled)

PostgreSQL-backed version of People Matching Service.
Uses CommunityRepository for database operations.

Features:
- Create and manage professional networking profiles
- Match BCM professionals by role, experience, challenges
- Find mentors and mentees
- Discover collaboration opportunities
- Privacy-controlled visibility
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    PeerMatch,
    PeerCriteria,
    UserNetworkingProfile,
    PrivacySettings,
    ProfessionalRole,
    ExperienceLevel,
    MatchingPurpose,
)
from .twin_matching_engine import TwinMatchingEngine
from storage.community_repository import CommunityRepository

logger = logging.getLogger(__name__)


# ============================================
# PEOPLE MATCHING SERVICE (DB)
# ============================================

class PeopleMatchingServiceDB:
    """
    Database-backed People Matching Service

    Connects BCM professionals for mentorship and collaboration
    """

    def __init__(
        self,
        db_session: AsyncSession,
        tenant_id: str,
        matching_engine: Optional[TwinMatchingEngine] = None
    ):
        """
        Initialize People Matching Service

        Args:
            db_session: SQLAlchemy async session
            tenant_id: Tenant ID for multi-tenancy
            matching_engine: Engine for organization similarity
        """
        self.repository = CommunityRepository(db_session)
        self.tenant_id = tenant_id
        self.matching = matching_engine or TwinMatchingEngine()

        logger.info(f"People Matching Service (DB) initialized for tenant: {tenant_id}")

    # ============================================
    # PROFILE MANAGEMENT
    # ============================================

    async def create_profile(
        self,
        profile: UserNetworkingProfile,
        twin_id: str
    ) -> UserNetworkingProfile:
        """
        Create networking profile

        Args:
            profile: User profile data
            twin_id: Organization twin ID

        Returns:
            Created profile
        """
        logger.info(f"Creating networking profile for user: {profile.user_id}")

        profile_data = {
            'user_id': profile.user_id,
            'twin_id': twin_id,
            'tenant_id': self.tenant_id,
            'display_name': profile.display_name,
            'role': profile.role.value,
            'experience_level': profile.experience_level.value,
            'bio': profile.bio,
            'bcm_certifications': profile.bcm_certifications or [],
            'expertise_areas': profile.expertise_areas or [],
            'current_challenges': profile.current_challenges or [],
            'learning_interests': profile.learning_interests or [],
            'languages': profile.languages or [],
            'open_to_mentoring': profile.open_to_mentoring,
            'seeking_mentor': profile.seeking_mentor,
            'open_to_collaboration': profile.open_to_collaboration,
            'visibility_level': profile.visibility_level,
            'show_organization': profile.show_organization,
            'show_real_name': profile.show_real_name,
            'last_active': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }

        db_profile = await self.repository.create_profile(profile_data)

        return self._db_to_pydantic_profile(db_profile)

    async def get_profile(
        self,
        user_id: str
    ) -> Optional[UserNetworkingProfile]:
        """Get user networking profile"""
        db_profile = await self.repository.get_profile(user_id)
        if not db_profile:
            return None

        return self._db_to_pydantic_profile(db_profile)

    async def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[UserNetworkingProfile]:
        """Update networking profile"""
        # Convert enum values to strings if present
        if 'role' in updates and hasattr(updates['role'], 'value'):
            updates['role'] = updates['role'].value
        if 'experience_level' in updates and hasattr(updates['experience_level'], 'value'):
            updates['experience_level'] = updates['experience_level'].value

        db_profile = await self.repository.update_profile(user_id, updates)
        if not db_profile:
            return None

        return self._db_to_pydantic_profile(db_profile)

    async def delete_profile(
        self,
        user_id: str
    ) -> bool:
        """Delete networking profile"""
        return await self.repository.delete_profile(user_id)

    # ============================================
    # PEER MATCHING
    # ============================================

    async def find_peers(
        self,
        user_id: str,
        criteria: PeerCriteria,
        all_twins: List[Any]  # Organization models
    ) -> List[PeerMatch]:
        """
        Find matching peers

        Args:
            user_id: User seeking peers
            criteria: Matching criteria
            all_twins: All organization twins (for similarity)

        Returns:
            List of matching peers
        """
        logger.info(f"Finding peers for user: {user_id}")

        # Get user profile
        user_profile = await self.get_profile(user_id)
        if not user_profile:
            return []

        # Build search filters from criteria
        role = criteria.role.value if criteria.role else None
        experience_level = criteria.experience_level.value if criteria.experience_level else None

        # Search profiles
        candidate_profiles = await self.repository.search_profiles(
            role=role,
            experience_level=experience_level,
            expertise_areas=criteria.expertise_areas,
            languages=criteria.languages,
            open_to_collaboration=criteria.purpose == MatchingPurpose.COLLABORATION,
            visibility_level='public',
            limit=50
        )

        # Score and rank matches
        matches = []
        for candidate_db in candidate_profiles:
            if candidate_db.user_id == user_id:
                continue  # Skip self

            candidate_profile = self._db_to_pydantic_profile(candidate_db)

            # Calculate organization similarity (if available)
            org_similarity = 0.5  # Default
            # TODO: Calculate actual org similarity using matching engine and all_twins

            # Calculate match score
            score = await self._calculate_peer_match_score(
                user_profile,
                candidate_profile,
                org_similarity,
                criteria
            )

            if score >= criteria.min_match_score:
                # Build match
                match = PeerMatch(
                    user_id=candidate_profile.user_id,
                    display_name=candidate_profile.display_name if candidate_profile.show_real_name else "Anonymous BCM Professional",
                    role=candidate_profile.role,
                    experience_level=candidate_profile.experience_level,
                    organization_name=None if not candidate_profile.show_organization else "Organization",  # TODO: Get from twin
                    organization_similarity=org_similarity,
                    common_challenges=self._find_common_items(
                        user_profile.current_challenges or [],
                        candidate_profile.current_challenges or []
                    ),
                    complementary_skills=self._find_complementary_skills(
                        user_profile.expertise_areas or [],
                        candidate_profile.expertise_areas or []
                    ),
                    common_interests=self._find_common_items(
                        user_profile.learning_interests or [],
                        candidate_profile.learning_interests or []
                    ),
                    common_languages=self._find_common_items(
                        user_profile.languages or [],
                        candidate_profile.languages or []
                    ),
                    overall_score=score,
                    match_reason=self._build_match_reason(user_profile, candidate_profile, criteria),
                )

                matches.append(match)

        # Sort by score
        matches.sort(key=lambda m: m.overall_score, reverse=True)

        logger.info(f"Found {len(matches)} peer matches for user {user_id}")

        return matches[:criteria.limit]

    async def find_mentors(
        self,
        user_id: str,
        all_twins: List[Any],
        role: Optional[str] = None,
        max_results: int = 10
    ) -> List[PeerMatch]:
        """Find potential mentors"""
        logger.info(f"Finding mentors for user: {user_id}")

        # Get user profile
        user_profile = await self.get_profile(user_id)
        if not user_profile:
            return []

        # Search for mentors (more experienced, open to mentoring)
        candidate_profiles = await self.repository.search_profiles(
            role=role if role else None,
            open_to_mentoring=True,
            visibility_level='public',
            limit=50
        )

        # Filter by higher experience
        user_exp_level = self._exp_level_to_int(user_profile.experience_level)

        matches = []
        for candidate_db in candidate_profiles:
            if candidate_db.user_id == user_id:
                continue

            candidate_profile = self._db_to_pydantic_profile(candidate_db)
            candidate_exp_level = self._exp_level_to_int(candidate_profile.experience_level)

            # Must be more experienced
            if candidate_exp_level <= user_exp_level:
                continue

            # Calculate score
            org_similarity = 0.5  # TODO: Calculate
            score = await self._calculate_mentor_score(
                user_profile,
                candidate_profile,
                org_similarity
            )

            match = PeerMatch(
                user_id=candidate_profile.user_id,
                display_name=candidate_profile.display_name if candidate_profile.show_real_name else "Anonymous Mentor",
                role=candidate_profile.role,
                experience_level=candidate_profile.experience_level,
                organization_name=None,
                organization_similarity=org_similarity,
                common_challenges=[],
                complementary_skills=candidate_profile.expertise_areas or [],
                common_interests=[],
                common_languages=self._find_common_items(
                    user_profile.languages or [],
                    candidate_profile.languages or []
                ),
                overall_score=score,
                match_reason=f"Experienced {candidate_profile.role.value} available for mentorship",
            )

            matches.append(match)

        matches.sort(key=lambda m: m.overall_score, reverse=True)

        return matches[:max_results]

    async def find_collaboration_opportunities(
        self,
        user_id: str,
        all_twins: List[Any],
        max_results: int = 10
    ) -> List[PeerMatch]:
        """Find collaboration opportunities"""
        criteria = PeerCriteria(
            purpose=MatchingPurpose.COLLABORATION,
            limit=max_results
        )

        return await self.find_peers(user_id, criteria, all_twins)

    # ============================================
    # STATISTICS
    # ============================================

    async def get_network_statistics(self) -> Dict[str, Any]:
        """Get networking statistics"""
        return await self.repository.get_network_statistics()

    # ============================================
    # HELPER METHODS
    # ============================================

    def _db_to_pydantic_profile(self, db_profile) -> UserNetworkingProfile:
        """Convert database model to Pydantic model"""
        return UserNetworkingProfile(
            user_id=db_profile.user_id,
            display_name=db_profile.display_name,
            role=ProfessionalRole(db_profile.role),
            experience_level=ExperienceLevel(db_profile.experience_level),
            bio=db_profile.bio,
            bcm_certifications=db_profile.bcm_certifications or [],
            expertise_areas=db_profile.expertise_areas or [],
            current_challenges=db_profile.current_challenges or [],
            learning_interests=db_profile.learning_interests or [],
            languages=db_profile.languages or [],
            open_to_mentoring=db_profile.open_to_mentoring,
            seeking_mentor=db_profile.seeking_mentor,
            open_to_collaboration=db_profile.open_to_collaboration,
            visibility_level=db_profile.visibility_level,
            show_organization=db_profile.show_organization,
            show_real_name=db_profile.show_real_name,
        )

    async def _calculate_peer_match_score(
        self,
        user_profile: UserNetworkingProfile,
        candidate_profile: UserNetworkingProfile,
        org_similarity: float,
        criteria: PeerCriteria
    ) -> float:
        """Calculate peer match score"""
        score = 0.0

        # Organization similarity (30%)
        score += org_similarity * 0.30

        # Common challenges (25%)
        user_challenges = set(user_profile.current_challenges or [])
        candidate_challenges = set(candidate_profile.current_challenges or [])
        if user_challenges and candidate_challenges:
            challenge_score = len(user_challenges & candidate_challenges) / len(user_challenges | candidate_challenges)
            score += challenge_score * 0.25

        # Complementary skills (20%)
        user_expertise = set(user_profile.expertise_areas or [])
        candidate_expertise = set(candidate_profile.expertise_areas or [])
        if user_expertise and candidate_expertise:
            # Mix of overlap and complementarity
            overlap = len(user_expertise & candidate_expertise) / max(len(user_expertise), len(candidate_expertise))
            score += overlap * 0.20

        # Experience match (15%)
        exp_diff = abs(
            self._exp_level_to_int(user_profile.experience_level) -
            self._exp_level_to_int(candidate_profile.experience_level)
        )
        exp_score = max(0, 1 - (exp_diff / 4.0))
        score += exp_score * 0.15

        # Common languages (10%)
        user_langs = set(user_profile.languages or [])
        candidate_langs = set(candidate_profile.languages or [])
        if user_langs and candidate_langs:
            lang_score = len(user_langs & candidate_langs) / len(user_langs | candidate_langs)
            score += lang_score * 0.10

        return min(max(score, 0.0), 1.0)

    async def _calculate_mentor_score(
        self,
        user_profile: UserNetworkingProfile,
        mentor_profile: UserNetworkingProfile,
        org_similarity: float
    ) -> float:
        """Calculate mentor match score"""
        score = 0.0

        # Experience gap (40%) - prefer 1-2 levels higher
        exp_gap = (
            self._exp_level_to_int(mentor_profile.experience_level) -
            self._exp_level_to_int(user_profile.experience_level)
        )
        if exp_gap == 1:
            score += 0.40
        elif exp_gap == 2:
            score += 0.35
        elif exp_gap >= 3:
            score += 0.25

        # Expertise relevance (30%)
        user_interests = set(user_profile.learning_interests or [])
        mentor_expertise = set(mentor_profile.expertise_areas or [])
        if user_interests and mentor_expertise:
            relevance = len(user_interests & mentor_expertise) / len(user_interests)
            score += relevance * 0.30

        # Organization similarity (20%)
        score += org_similarity * 0.20

        # Language compatibility (10%)
        user_langs = set(user_profile.languages or [])
        mentor_langs = set(mentor_profile.languages or [])
        if user_langs and mentor_langs:
            lang_score = len(user_langs & mentor_langs) / len(user_langs | mentor_langs)
            score += lang_score * 0.10

        return min(max(score, 0.0), 1.0)

    @staticmethod
    def _exp_level_to_int(level: ExperienceLevel) -> int:
        """Convert experience level to integer for comparison"""
        mapping = {
            ExperienceLevel.ENTRY: 1,
            ExperienceLevel.INTERMEDIATE: 2,
            ExperienceLevel.ADVANCED: 3,
            ExperienceLevel.EXPERT: 4,
        }
        return mapping.get(level, 2)

    @staticmethod
    def _find_common_items(list1: List[str], list2: List[str]) -> List[str]:
        """Find common items between two lists"""
        return list(set(list1) & set(list2))

    @staticmethod
    def _find_complementary_skills(
        user_skills: List[str],
        candidate_skills: List[str]
    ) -> List[str]:
        """Find complementary skills (in candidate but not in user)"""
        return list(set(candidate_skills) - set(user_skills))

    @staticmethod
    def _build_match_reason(
        user_profile: UserNetworkingProfile,
        candidate_profile: UserNetworkingProfile,
        criteria: PeerCriteria
    ) -> str:
        """Build human-readable match reason"""
        reasons = []

        common_challenges = set(user_profile.current_challenges or []) & set(candidate_profile.current_challenges or [])
        if common_challenges:
            reasons.append(f"Facing similar challenges: {', '.join(list(common_challenges)[:2])}")

        common_expertise = set(user_profile.expertise_areas or []) & set(candidate_profile.expertise_areas or [])
        if common_expertise:
            reasons.append(f"Shared expertise in {', '.join(list(common_expertise)[:2])}")

        if criteria.purpose == MatchingPurpose.COLLABORATION:
            reasons.append("Open to collaboration")

        return "; ".join(reasons) if reasons else "Potential match based on profile"
