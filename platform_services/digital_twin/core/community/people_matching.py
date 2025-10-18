"""
People Matching Service

Connects BCM professionals for mentorship, collaboration, and knowledge exchange.

Features:
- Match professionals by role, experience, challenges
- Mentorship matching (senior ↔ junior)
- Collaboration opportunities
- Privacy-first (opt-in visibility)
- Geographic and timezone awareness
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import (
    PeerMatch,
    PeerCriteria,
    UserNetworkingProfile,
    ProfessionalRole,
    ExperienceLevel,
    MatchingPurpose,
    IndustryType,
    OrganizationSize,
)
from .twin_matching_engine import TwinMatchingEngine
from core.models.base import Organization

logger = logging.getLogger(__name__)


# ============================================
# PEOPLE MATCHING SERVICE
# ============================================

class PeopleMatchingService:
    """
    Service for matching BCM professionals
    """

    def __init__(
        self,
        twin_matching_engine: Optional[TwinMatchingEngine] = None
    ):
        """
        Initialize People Matching Service

        Args:
            twin_matching_engine: Engine for organization twin matching
        """
        self.twin_matching = twin_matching_engine or TwinMatchingEngine()

        # In-memory storage (TODO: replace with database)
        self._profiles: Dict[str, UserNetworkingProfile] = {}
        self._user_to_twin: Dict[str, str] = {}  # user_id → twin_id

        logger.info("People Matching Service initialized")

    # ============================================
    # PUBLIC API - PROFILE MANAGEMENT
    # ============================================

    async def create_profile(
        self,
        profile: UserNetworkingProfile,
        twin_id: str
    ) -> UserNetworkingProfile:
        """
        Create or update user networking profile

        Args:
            profile: User networking profile
            twin_id: Associated organization twin ID

        Returns:
            Created/updated profile
        """
        logger.info(f"Creating networking profile for user: {profile.user_id}")

        # Store profile
        self._profiles[profile.user_id] = profile
        self._user_to_twin[profile.user_id] = twin_id

        logger.info(
            f"Profile created: {profile.user_id} "
            f"(role: {profile.role.value}, experience: {profile.experience_level.value})"
        )

        return profile

    async def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[UserNetworkingProfile]:
        """
        Update user profile

        Args:
            user_id: User ID
            updates: Fields to update

        Returns:
            Updated profile or None if not found
        """
        profile = self._profiles.get(user_id)
        if not profile:
            return None

        # Update fields
        for field, value in updates.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        profile.updated_at = datetime.utcnow()

        logger.info(f"Profile updated: {user_id}")

        return profile

    async def get_profile(self, user_id: str) -> Optional[UserNetworkingProfile]:
        """Get user profile"""
        return self._profiles.get(user_id)

    async def delete_profile(self, user_id: str) -> bool:
        """Delete user profile"""
        if user_id in self._profiles:
            del self._profiles[user_id]
            if user_id in self._user_to_twin:
                del self._user_to_twin[user_id]
            logger.info(f"Profile deleted: {user_id}")
            return True
        return False

    # ============================================
    # PUBLIC API - PEER MATCHING
    # ============================================

    async def find_peers(
        self,
        user_id: str,
        criteria: PeerCriteria,
        all_twins: List[Organization]
    ) -> List[PeerMatch]:
        """
        Find matching peers for user

        Args:
            user_id: Source user ID
            criteria: Matching criteria
            all_twins: List of all organization twins (for org matching)

        Returns:
            List of PeerMatch sorted by match score
        """
        logger.info(f"Finding peers for user: {user_id}")

        # Get user profile
        user_profile = self._profiles.get(user_id)
        if not user_profile:
            logger.warning(f"User profile not found: {user_id}")
            return []

        # Get user's organization twin
        user_twin_id = self._user_to_twin.get(user_id)
        user_twin = next((t for t in all_twins if t.twin_id == user_twin_id), None)

        if not user_twin:
            logger.warning(f"Organization twin not found for user: {user_id}")
            return []

        # Get candidate profiles
        candidates = await self._get_candidate_profiles(user_profile, criteria)
        logger.info(f"Found {len(candidates)} candidate profiles")

        # Calculate matches
        matches = []
        for candidate_profile in candidates:
            # Skip self
            if candidate_profile.user_id == user_id:
                continue

            # Get candidate's organization
            candidate_twin_id = self._user_to_twin.get(candidate_profile.user_id)
            candidate_twin = next((t for t in all_twins if t.twin_id == candidate_twin_id), None)

            if not candidate_twin:
                continue

            # Calculate organization similarity
            org_similarity = await self.twin_matching.calculate_similarity(
                user_twin,
                candidate_twin
            )

            # Calculate peer match score
            match_score = await self._calculate_peer_match_score(
                user_profile,
                candidate_profile,
                org_similarity.overall,
                criteria
            )

            # Check minimum threshold
            if match_score >= criteria.min_match_score:
                # Create peer match
                peer_match = await self._create_peer_match(
                    candidate_profile,
                    candidate_twin,
                    org_similarity.overall,
                    match_score,
                    user_profile
                )
                matches.append(peer_match)

        # Sort by match score
        matches.sort(key=lambda m: m.overall_score, reverse=True)

        # Limit results
        matches = matches[:criteria.max_results]

        logger.info(
            f"Found {len(matches)} peer matches for {user_id} "
            f"(avg score: {self._avg_score(matches):.2f})"
        )

        return matches

    async def find_mentors(
        self,
        user_id: str,
        all_twins: List[Organization],
        role: Optional[ProfessionalRole] = None,
        max_results: int = 10
    ) -> List[PeerMatch]:
        """
        Find potential mentors for user

        Args:
            user_id: User seeking mentor
            all_twins: All organization twins
            role: Optional specific role filter
            max_results: Maximum results

        Returns:
            List of potential mentors
        """
        user_profile = self._profiles.get(user_id)
        if not user_profile:
            return []

        # Criteria for mentor matching
        criteria = PeerCriteria(
            role=role or user_profile.role,
            purpose=MatchingPurpose.MENTORSHIP,
            experience_level=ExperienceLevel.SENIOR,  # Look for senior professionals
            min_match_score=0.6,
            max_results=max_results
        )

        # Find peers
        peers = await self.find_peers(user_id, criteria, all_twins)

        # Filter for those available for mentorship
        mentors = [p for p in peers if p.available_for_mentorship]

        logger.info(f"Found {len(mentors)} potential mentors for {user_id}")

        return mentors

    async def find_collaboration_opportunities(
        self,
        user_id: str,
        all_twins: List[Organization],
        max_results: int = 10
    ) -> List[PeerMatch]:
        """
        Find collaboration opportunities

        Args:
            user_id: User ID
            all_twins: All organization twins
            max_results: Maximum results

        Returns:
            List of collaboration opportunities
        """
        user_profile = self._profiles.get(user_id)
        if not user_profile:
            return []

        criteria = PeerCriteria(
            purpose=MatchingPurpose.COLLABORATION,
            min_match_score=0.6,
            max_results=max_results
        )

        peers = await self.find_peers(user_id, criteria, all_twins)

        # Filter for those available for collaboration
        collaborators = [p for p in peers if p.available_for_collaboration]

        logger.info(f"Found {len(collaborators)} collaboration opportunities for {user_id}")

        return collaborators

    # ============================================
    # PRIVATE METHODS - MATCHING
    # ============================================

    async def _get_candidate_profiles(
        self,
        user_profile: UserNetworkingProfile,
        criteria: PeerCriteria
    ) -> List[UserNetworkingProfile]:
        """Get candidate profiles matching criteria"""
        candidates = list(self._profiles.values())

        # Filter by role
        if criteria.role:
            candidates = [p for p in candidates if p.role == criteria.role]

        # Filter by experience level
        if criteria.experience_level:
            candidates = [p for p in candidates if p.experience_level == criteria.experience_level]

        # Filter by purpose (availability)
        if criteria.purpose == MatchingPurpose.MENTORSHIP:
            # If seeking mentor, find those available for mentorship
            # If offering mentorship, find those seeking mentors
            candidates = [
                p for p in candidates
                if p.available_for_mentorship or p.seeking_mentor
            ]
        elif criteria.purpose == MatchingPurpose.COLLABORATION:
            candidates = [p for p in candidates if p.available_for_collaboration]

        # Geographic filters
        if criteria.same_country_only:
            # TODO: implement country-based filtering
            pass

        return candidates

    async def _calculate_peer_match_score(
        self,
        user_profile: UserNetworkingProfile,
        candidate_profile: UserNetworkingProfile,
        org_similarity: float,
        criteria: PeerCriteria
    ) -> float:
        """
        Calculate peer match score (0-1)

        Considers:
        - Organization similarity
        - Common challenges
        - Complementary skills
        - Experience match (for mentorship)
        - Geographic proximity
        """
        score = 0.0

        # Organization similarity (30%)
        score += org_similarity * 0.30

        # Common challenges (25%)
        user_challenges = set(user_profile.current_challenges)
        candidate_challenges = set(candidate_profile.current_challenges)

        if user_challenges and candidate_challenges:
            common_challenges = len(user_challenges & candidate_challenges)
            total_challenges = len(user_challenges | candidate_challenges)
            challenge_score = common_challenges / total_challenges if total_challenges > 0 else 0
            score += challenge_score * 0.25
        else:
            score += 0.125  # Neutral if no challenges listed

        # Complementary skills (20%)
        user_skills = set(user_profile.skills)
        candidate_skills = set(candidate_profile.skills)
        user_interests = set(user_profile.learning_interests)

        # Skills the candidate has that the user wants to learn
        complementary = len(candidate_skills & user_interests)
        if user_interests:
            complementary_score = complementary / len(user_interests)
            score += complementary_score * 0.20
        else:
            score += 0.10  # Neutral

        # Experience match (15%)
        # For mentorship: prefer higher experience
        # For collaboration: prefer similar experience
        if criteria.purpose == MatchingPurpose.MENTORSHIP:
            user_exp = self._experience_to_level(user_profile.experience_level)
            candidate_exp = self._experience_to_level(candidate_profile.experience_level)

            if candidate_exp > user_exp:
                # Good match: candidate has more experience
                exp_diff = candidate_exp - user_exp
                experience_score = min(exp_diff / 2.0, 1.0)  # Max score for 2+ levels difference
                score += experience_score * 0.15
            else:
                # Not ideal for mentorship
                score += 0.0
        else:
            # For collaboration: similar experience is better
            user_exp = self._experience_to_level(user_profile.experience_level)
            candidate_exp = self._experience_to_level(candidate_profile.experience_level)
            exp_diff = abs(user_exp - candidate_exp)
            experience_score = 1.0 - (exp_diff / 3.0)  # Max diff is 3 levels
            score += max(0, experience_score) * 0.15

        # Language match (10%)
        common_languages = set(user_profile.languages) & set(candidate_profile.languages)
        if common_languages:
            score += 0.10
        else:
            score += 0.0

        # Normalize to 0-1
        score = min(max(score, 0.0), 1.0)

        return score

    async def _create_peer_match(
        self,
        candidate_profile: UserNetworkingProfile,
        candidate_twin: Organization,
        org_similarity: float,
        match_score: float,
        user_profile: UserNetworkingProfile
    ) -> PeerMatch:
        """Create PeerMatch from candidate"""

        # Determine what to show based on privacy settings
        show_name = candidate_profile.show_name
        show_org = candidate_profile.show_organization

        # Common challenges
        user_challenges = set(user_profile.current_challenges)
        candidate_challenges = set(candidate_profile.current_challenges)
        common_challenges = list(user_challenges & candidate_challenges)[:5]

        # Complementary skills
        user_interests = set(user_profile.learning_interests)
        candidate_skills = set(candidate_profile.skills)
        complementary_skills = list(candidate_skills & user_interests)[:5]

        # Geographic proximity
        # TODO: implement proper geo calculation
        geo_proximity = "same_country"  # Placeholder

        return PeerMatch(
            user_id=candidate_profile.user_id,
            name=candidate_profile.user_id if show_name else None,  # TODO: get actual name
            role=candidate_profile.role,
            experience_level=candidate_profile.experience_level,
            organization_industry=IndustryType(candidate_twin.industry),
            organization_size=self._categorize_size(candidate_twin.employee_count),
            organization_similarity=org_similarity,
            common_challenges=common_challenges,
            complementary_skills=complementary_skills,
            geographic_proximity=geo_proximity,
            overall_score=match_score,
            available_for_mentorship=candidate_profile.available_for_mentorship,
            available_for_collaboration=candidate_profile.available_for_collaboration,
            languages=candidate_profile.languages,
            timezone=candidate_profile.timezone,
        )

    # ============================================
    # STATISTICS & ANALYTICS
    # ============================================

    async def get_network_statistics(self) -> Dict[str, Any]:
        """Get networking statistics"""
        all_profiles = list(self._profiles.values())

        # Group by role
        by_role: Dict[str, int] = {}
        for profile in all_profiles:
            role = profile.role.value
            by_role[role] = by_role.get(role, 0) + 1

        # Group by experience
        by_experience: Dict[str, int] = {}
        for profile in all_profiles:
            exp = profile.experience_level.value
            by_experience[exp] = by_experience.get(exp, 0) + 1

        # Availability stats
        available_mentors = sum(1 for p in all_profiles if p.available_for_mentorship)
        seeking_mentors = sum(1 for p in all_profiles if p.seeking_mentor)
        available_collaborators = sum(1 for p in all_profiles if p.available_for_collaboration)

        return {
            'total_professionals': len(all_profiles),
            'professionals_by_role': by_role,
            'professionals_by_experience': by_experience,
            'available_mentors': available_mentors,
            'seeking_mentors': seeking_mentors,
            'available_collaborators': available_collaborators,
            'generated_at': datetime.utcnow().isoformat(),
        }

    # ============================================
    # UTILITY METHODS
    # ============================================

    @staticmethod
    def _experience_to_level(experience: ExperienceLevel) -> int:
        """Convert experience enum to level (0-3)"""
        mapping = {
            ExperienceLevel.JUNIOR: 0,
            ExperienceLevel.INTERMEDIATE: 1,
            ExperienceLevel.SENIOR: 2,
            ExperienceLevel.EXPERT: 3,
        }
        return mapping.get(experience, 0)

    @staticmethod
    def _categorize_size(employee_count: Optional[int]) -> OrganizationSize:
        """Categorize organization size"""
        if not employee_count:
            return OrganizationSize.SMALL

        if employee_count <= 10:
            return OrganizationSize.MICRO
        elif employee_count <= 50:
            return OrganizationSize.SMALL
        elif employee_count <= 200:
            return OrganizationSize.MEDIUM
        elif employee_count <= 1000:
            return OrganizationSize.LARGE
        else:
            return OrganizationSize.ENTERPRISE

    @staticmethod
    def _avg_score(matches: List[PeerMatch]) -> float:
        """Calculate average match score"""
        if not matches:
            return 0.0

        total = sum(m.overall_score for m in matches)
        return total / len(matches)

    def get_profile_count(self) -> int:
        """Get total profile count"""
        return len(self._profiles)

    def get_all_profiles(self) -> List[UserNetworkingProfile]:
        """Get all profiles (admin only)"""
        return list(self._profiles.values())
