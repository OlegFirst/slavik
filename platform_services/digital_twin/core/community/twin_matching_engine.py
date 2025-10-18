"""
Twin Matching Engine

Finds similar organization twins based on multi-dimensional similarity.

Features:
- Multi-dimensional similarity calculation (industry, size, challenges, maturity, etc.)
- Weighted scoring algorithm
- Configurable filters
- Caching for performance
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

from core.models.base import Organization
from .models import (
    TwinMatch,
    SimilarityScore,
    SimilarityBreakdown,
    MatchFilters,
    IndustryType,
    OrganizationSize,
    BCMMaturityLevel,
)

logger = logging.getLogger(__name__)


# ============================================
# SIMILARITY WEIGHTS
# ============================================

DEFAULT_WEIGHTS = {
    'industry': 0.25,       # Same industry is important
    'size': 0.15,           # Similar size helps
    'geography': 0.10,      # Location can matter
    'challenges': 0.25,     # Facing similar challenges is key
    'maturity': 0.15,       # Similar maturity level
    'patterns': 0.10,       # Operational patterns similarity
}


# ============================================
# TWIN MATCHING ENGINE
# ============================================

class TwinMatchingEngine:
    """
    Engine for matching organization twins based on similarity
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        cache_ttl_minutes: int = 30
    ):
        """
        Initialize Twin Matching Engine

        Args:
            weights: Custom similarity weights (default: DEFAULT_WEIGHTS)
            cache_ttl_minutes: Cache TTL in minutes
        """
        self.weights = weights or DEFAULT_WEIGHTS
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._cache: Dict[str, Any] = {}  # Simple in-memory cache

        logger.info(f"Twin Matching Engine initialized with weights: {self.weights}")

    # ============================================
    # PUBLIC API
    # ============================================

    async def find_matches(
        self,
        twin: Organization,
        candidates: List[Organization],
        filters: Optional[MatchFilters] = None,
    ) -> List[TwinMatch]:
        """
        Find matching twins for given organization

        Args:
            twin: Source organization twin
            candidates: List of candidate organizations
            filters: Optional matching filters

        Returns:
            List of TwinMatch sorted by similarity (highest first)
        """
        logger.info(f"Finding matches for twin: {twin.twin_id}")

        filters = filters or MatchFilters()

        # Apply filters
        filtered_candidates = self._apply_filters(candidates, filters)
        logger.info(f"Filtered to {len(filtered_candidates)} candidates")

        # Calculate similarities
        matches = []
        for candidate in filtered_candidates:
            # Skip self
            if candidate.twin_id == twin.twin_id:
                continue

            # Calculate similarity
            similarity = await self.calculate_similarity(twin, candidate)

            # Check minimum threshold
            if similarity.overall >= filters.min_similarity:
                # Create match
                match = self._create_twin_match(
                    candidate=candidate,
                    similarity=similarity
                )
                matches.append(match)

        # Sort by similarity (highest first)
        matches.sort(key=lambda m: m.similarity_score.overall, reverse=True)

        # Limit results
        matches = matches[:filters.max_results]

        logger.info(
            f"Found {len(matches)} matches for {twin.twin_id} "
            f"(avg similarity: {self._avg_similarity(matches):.2f})"
        )

        return matches

    async def calculate_similarity(
        self,
        twin_a: Organization,
        twin_b: Organization
    ) -> SimilarityScore:
        """
        Calculate multi-dimensional similarity between two twins

        Args:
            twin_a: First organization
            twin_b: Second organization

        Returns:
            SimilarityScore with overall score and breakdown
        """
        # Check cache
        cache_key = f"{twin_a.twin_id}:{twin_b.twin_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        # Calculate dimension scores
        breakdown = SimilarityBreakdown(
            industry=self._industry_similarity(twin_a, twin_b),
            size=self._size_similarity(twin_a, twin_b),
            geography=self._geography_similarity(twin_a, twin_b),
            challenges=await self._challenges_similarity(twin_a, twin_b),
            maturity=self._maturity_similarity(twin_a, twin_b),
            patterns=await self._patterns_similarity(twin_a, twin_b),
        )

        # Calculate weighted overall score
        overall = (
            breakdown.industry * self.weights['industry'] +
            breakdown.size * self.weights['size'] +
            breakdown.geography * self.weights['geography'] +
            breakdown.challenges * self.weights['challenges'] +
            breakdown.maturity * self.weights['maturity'] +
            breakdown.patterns * self.weights['patterns']
        )

        # Identify key matching factors
        matching_factors = self._identify_matching_factors(twin_a, twin_b, breakdown)

        similarity = SimilarityScore(
            overall=round(overall, 3),
            breakdown=breakdown,
            matching_factors=matching_factors
        )

        # Cache result
        self._add_to_cache(cache_key, similarity)

        return similarity

    # ============================================
    # DIMENSION SIMILARITY CALCULATORS
    # ============================================

    def _industry_similarity(
        self,
        twin_a: Organization,
        twin_b: Organization
    ) -> float:
        """
        Calculate industry similarity (0-1)

        Rules:
        - Same industry: 1.0
        - Related industries: 0.5-0.7 (future: industry taxonomy)
        - Different industries: 0.0
        """
        if twin_a.industry == twin_b.industry:
            return 1.0

        # Future: implement industry taxonomy for related industries
        # e.g., healthcare & pharmaceuticals = 0.7
        return 0.0

    def _size_similarity(
        self,
        twin_a: Organization,
        twin_b: Organization
    ) -> float:
        """
        Calculate size similarity (0-1)

        Based on employee count difference
        """
        if not twin_a.employee_count or not twin_b.employee_count:
            return 0.5  # Unknown = neutral

        size_a = twin_a.employee_count
        size_b = twin_b.employee_count

        # Calculate ratio
        smaller = min(size_a, size_b)
        larger = max(size_a, size_b)

        if larger == 0:
            return 0.5

        ratio = smaller / larger

        # Convert ratio to similarity (0-1)
        # ratio = 1.0 (same size) → similarity = 1.0
        # ratio = 0.5 (2x difference) → similarity = 0.5
        # ratio = 0.1 (10x difference) → similarity = 0.1
        return ratio

    def _geography_similarity(
        self,
        twin_a: Organization,
        twin_b: Organization
    ) -> float:
        """
        Calculate geographic similarity (0-1)

        Rules:
        - Same country: 1.0
        - Same region: 0.6
        - Different region: 0.3
        - Unknown: 0.5
        """
        if not twin_a.headquarters or not twin_b.headquarters:
            return 0.5  # Unknown

        # Extract country (last part of headquarters string)
        # e.g., "Boston, MA, USA" → "USA"
        country_a = self._extract_country(twin_a.headquarters)
        country_b = self._extract_country(twin_b.headquarters)

        if country_a == country_b:
            return 1.0

        # Future: implement region similarity
        # e.g., USA & Canada = 0.6 (North America)
        return 0.3

    async def _challenges_similarity(
        self,
        twin_a: Organization,
        twin_b: Organization
    ) -> float:
        """
        Calculate challenges similarity (0-1)

        Based on identified challenges/risks
        """
        # Get challenges from metadata
        challenges_a = set(twin_a.metadata.get('challenges', []))
        challenges_b = set(twin_b.metadata.get('challenges', []))

        if not challenges_a or not challenges_b:
            return 0.5  # Unknown

        # Jaccard similarity
        intersection = len(challenges_a & challenges_b)
        union = len(challenges_a | challenges_b)

        if union == 0:
            return 0.5

        return intersection / union

    def _maturity_similarity(
        self,
        twin_a: Organization,
        twin_b: Organization
    ) -> float:
        """
        Calculate BCM maturity similarity (0-1)

        Based on maturity level difference
        """
        # Maturity levels: 1 (beginner) to 5 (optimized)
        level_a = twin_a.maturity_level or 1
        level_b = twin_b.maturity_level or 1

        # Calculate difference
        diff = abs(level_a - level_b)

        # Convert to similarity
        # diff = 0 (same level) → 1.0
        # diff = 1 (one level apart) → 0.75
        # diff = 2 (two levels apart) → 0.5
        # diff = 3 (three levels apart) → 0.25
        # diff = 4 (max difference) → 0.0
        similarity = 1.0 - (diff / 4.0)

        return max(0.0, similarity)

    async def _patterns_similarity(
        self,
        twin_a: Organization,
        twin_b: Organization
    ) -> float:
        """
        Calculate operational patterns similarity (0-1)

        Based on operational patterns from metadata
        Future: enhance with behavioral patterns from interactions
        """
        # Get patterns from metadata
        patterns_a = set(twin_a.metadata.get('patterns', []))
        patterns_b = set(twin_b.metadata.get('patterns', []))

        if not patterns_a or not patterns_b:
            return 0.5  # Unknown

        # Jaccard similarity
        intersection = len(patterns_a & patterns_b)
        union = len(patterns_a | patterns_b)

        if union == 0:
            return 0.5

        return intersection / union

    # ============================================
    # HELPER METHODS
    # ============================================

    def _apply_filters(
        self,
        candidates: List[Organization],
        filters: MatchFilters
    ) -> List[Organization]:
        """Apply filters to candidate list"""
        filtered = candidates

        # Filter by industry
        if filters.industries:
            filtered = [
                c for c in filtered
                if c.industry in filters.industries
            ]

        # Filter by size
        if filters.size_categories:
            filtered = [
                c for c in filtered
                if self._categorize_size(c.employee_count) in filters.size_categories
            ]

        # Filter by country
        if filters.countries:
            filtered = [
                c for c in filtered
                if self._extract_country(c.headquarters) in filters.countries
            ]

        # Filter by maturity
        if filters.min_maturity:
            min_level = self._maturity_to_level(filters.min_maturity)
            filtered = [
                c for c in filtered
                if (c.maturity_level or 1) >= min_level
            ]

        if filters.max_maturity:
            max_level = self._maturity_to_level(filters.max_maturity)
            filtered = [
                c for c in filtered
                if (c.maturity_level or 1) <= max_level
            ]

        # Filter by challenges
        if filters.challenges:
            filtered = [
                c for c in filtered
                if any(
                    challenge in c.metadata.get('challenges', [])
                    for challenge in filters.challenges
                )
            ]

        return filtered

    def _create_twin_match(
        self,
        candidate: Organization,
        similarity: SimilarityScore
    ) -> TwinMatch:
        """Create TwinMatch from candidate and similarity"""

        # Determine what to show based on privacy settings
        # Future: check actual privacy settings from database
        show_name = candidate.metadata.get('community_show_name', False)

        # Extract common challenges
        # Future: compare with source twin
        common_challenges = candidate.metadata.get('challenges', [])[:5]

        # Extract topics
        shared_topics = candidate.metadata.get('topics', [])[:5]

        return TwinMatch(
            twin_id=candidate.twin_id,
            organization_name=candidate.name if show_name else None,
            industry=IndustryType(candidate.industry),
            size=self._categorize_size(candidate.employee_count),
            location=self._generalize_location(candidate.headquarters),
            similarity_score=similarity,
            bcm_maturity_level=self._level_to_maturity(candidate.maturity_level),
            common_challenges=common_challenges,
            shared_topics=shared_topics,
        )

    def _identify_matching_factors(
        self,
        twin_a: Organization,
        twin_b: Organization,
        breakdown: SimilarityBreakdown
    ) -> List[str]:
        """Identify key factors that make these twins similar"""
        factors = []

        # Industry
        if breakdown.industry >= 0.9:
            factors.append(f"Same industry ({twin_a.industry})")

        # Size
        if breakdown.size >= 0.8:
            size_cat = self._categorize_size(twin_a.employee_count)
            factors.append(f"Similar size ({size_cat.value} employees)")

        # Geography
        if breakdown.geography >= 0.9:
            country = self._extract_country(twin_a.headquarters)
            factors.append(f"Same country ({country})")

        # Challenges
        if breakdown.challenges >= 0.7:
            factors.append("Facing similar BCM challenges")

        # Maturity
        if breakdown.maturity >= 0.8:
            maturity = self._level_to_maturity(twin_a.maturity_level)
            factors.append(f"Similar BCM maturity ({maturity.value})")

        # Patterns
        if breakdown.patterns >= 0.7:
            factors.append("Similar operational patterns")

        return factors

    # ============================================
    # UTILITY METHODS
    # ============================================

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
    def _extract_country(headquarters: Optional[str]) -> str:
        """Extract country from headquarters string"""
        if not headquarters:
            return "Unknown"

        # Simple extraction: last part after comma
        # e.g., "Boston, MA, USA" → "USA"
        parts = [p.strip() for p in headquarters.split(',')]
        return parts[-1] if parts else "Unknown"

    @staticmethod
    def _generalize_location(headquarters: Optional[str]) -> str:
        """Generalize location for privacy"""
        if not headquarters:
            return "Unknown"

        # Keep city and country, remove specific address
        # e.g., "123 Main St, Boston, MA, USA" → "Boston, USA"
        parts = [p.strip() for p in headquarters.split(',')]

        if len(parts) >= 3:
            # Assume: [street], [city], [state], [country]
            city = parts[-3] if len(parts) >= 3 else parts[0]
            country = parts[-1]
            return f"{city}, {country}"
        elif len(parts) == 2:
            return f"{parts[0]}, {parts[1]}"
        else:
            return parts[0]

    @staticmethod
    def _maturity_to_level(maturity: BCMMaturityLevel) -> int:
        """Convert maturity enum to level (1-5)"""
        mapping = {
            BCMMaturityLevel.BEGINNER: 1,
            BCMMaturityLevel.DEVELOPING: 2,
            BCMMaturityLevel.ESTABLISHED: 3,
            BCMMaturityLevel.ADVANCED: 4,
            BCMMaturityLevel.OPTIMIZED: 5,
        }
        return mapping.get(maturity, 1)

    @staticmethod
    def _level_to_maturity(level: Optional[int]) -> BCMMaturityLevel:
        """Convert level (1-5) to maturity enum"""
        mapping = {
            1: BCMMaturityLevel.BEGINNER,
            2: BCMMaturityLevel.DEVELOPING,
            3: BCMMaturityLevel.ESTABLISHED,
            4: BCMMaturityLevel.ADVANCED,
            5: BCMMaturityLevel.OPTIMIZED,
        }
        return mapping.get(level or 1, BCMMaturityLevel.BEGINNER)

    @staticmethod
    def _avg_similarity(matches: List[TwinMatch]) -> float:
        """Calculate average similarity score"""
        if not matches:
            return 0.0

        total = sum(m.similarity_score.overall for m in matches)
        return total / len(matches)

    # ============================================
    # CACHE MANAGEMENT
    # ============================================

    def _get_from_cache(self, key: str) -> Optional[SimilarityScore]:
        """Get value from cache if not expired"""
        if key in self._cache:
            cached_value, timestamp = self._cache[key]
            if datetime.utcnow() - timestamp < self.cache_ttl:
                return cached_value
            else:
                # Expired, remove
                del self._cache[key]
        return None

    def _add_to_cache(self, key: str, value: SimilarityScore) -> None:
        """Add value to cache"""
        self._cache[key] = (value, datetime.utcnow())

    def clear_cache(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        logger.info("Twin matching cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self._cache),
            'cache_ttl_minutes': self.cache_ttl.total_seconds() / 60,
        }
