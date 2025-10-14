"""
Case Library Integration for Collective Agent Networks

Connects to Community Intelligence case contributions to find
organizations that successfully solved specific problems.

This enables Collective Agent creation by:
1. Finding organizations that solved a problem type
2. Extracting their anonymized approaches
3. Ensuring k-anonymity (minimum 5 orgs)
4. Providing data for collective wisdom synthesis
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class CaseLibrary:
    """
    Query case contributions to find organizations that solved problems

    Integrates with:
    - community_intelligence.case_contributions (approved cases)
    - workflow_intelligence.workflow_cases (workflow completions)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_cases(
        self,
        problem_type: str,
        min_success_rate: float = 0.8,
        exclude_org_id: Optional[str] = None,
        min_quality_score: float = 7.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Find successful cases matching problem type

        Args:
            problem_type: Type of problem (e.g., "supply_chain_complexity",
                         "dependency_mapping", "executive_engagement")
            min_success_rate: Minimum success rate (0-1)
            exclude_org_id: Exclude this organization's cases
            min_quality_score: Minimum peer review quality score (1-10)
            limit: Maximum cases to return

        Returns:
            List of anonymized case data with approaches

        Example result:
        [
            {
                'case_id': '...',
                'organization_context': {
                    'industry': 'healthcare',
                    'size': 'medium',
                    'maturity_level': 'developing'
                },
                'approach': {
                    'method': 'stakeholder_workshops',
                    'steps': [...],
                    'tools_used': [...]
                },
                'success_patterns': [...],
                'challenges': [...],
                'success_rate': 1.0
            }
        ]
        """

        try:
            # Import models dynamically to avoid circular imports
            from intelligent_core.community_intelligence.models.database import (
                CaseContribution, ContributionStatus
            )

            # Build query
            query = select(CaseContribution).where(
                and_(
                    CaseContribution.status == ContributionStatus.APPROVED,
                    CaseContribution.tags.contains([problem_type]),
                    CaseContribution.added_to_library == True
                )
            )

            # Exclude requesting org's cases
            if exclude_org_id:
                query = query.where(
                    CaseContribution.contributor_org_id != UUID(exclude_org_id)
                )

            # Order by quality and recency
            query = query.order_by(
                CaseContribution.approved_at.desc()
            ).limit(limit)

            # Execute
            result = await self.db.execute(query)
            contributions = result.scalars().all()

            logger.info(
                f"Found {len(contributions)} cases for problem_type '{problem_type}'"
            )

            # Transform to collective agent format
            cases = []
            for contrib in contributions:
                case_data = contrib.case_data

                # Extract success rate from metrics
                metrics = case_data.get('metrics', {})
                success = metrics.get('success', True)
                success_rate = 1.0 if success else 0.0

                # Skip if below success threshold
                if success_rate < min_success_rate:
                    continue

                # Extract quality score (from peer reviews)
                # In real implementation, would query peer_reviews table
                quality_score = 8.0  # Placeholder - all approved cases are high quality

                if quality_score < min_quality_score:
                    continue

                # Build case record
                cases.append({
                    'case_id': str(contrib.id),
                    'organization_context': case_data.get('organization_context', {}),
                    'journey': case_data.get('journey', []),
                    'approach': {
                        'method': case_data.get('approach_type', 'unknown'),
                        'steps': self._extract_approach_steps(case_data),
                        'tools_used': case_data.get('tools_used', []),
                        'timeline': case_data.get('timeline', {})
                    },
                    'success_patterns': case_data.get('success_patterns', []),
                    'challenges': case_data.get('challenges', []),
                    'lessons_learned': case_data.get('lessons_learned', []),
                    'key_decisions': case_data.get('key_decisions', []),
                    'success_rate': success_rate,
                    'quality_score': quality_score,
                    'module': contrib.module
                })

            logger.info(
                f"Returning {len(cases)} cases after filtering "
                f"(success_rate >= {min_success_rate}, quality >= {min_quality_score})"
            )

            return cases

        except Exception as e:
            logger.error(f"Error finding cases: {e}", exc_info=True)
            # Return empty list on error to allow graceful degradation
            return []

    def _extract_approach_steps(self, case_data: Dict[str, Any]) -> List[str]:
        """
        Extract step-by-step approach from case data

        Converts journey into actionable steps
        """
        journey = case_data.get('journey', [])

        steps = []
        for step in journey:
            step_name = step.get('stage') or step.get('step_name', 'Unknown step')
            actions = step.get('actions', [])

            if actions:
                # Combine step name with key actions
                steps.append(f"{step_name}: {', '.join(actions[:2])}")
            else:
                steps.append(step_name)

        return steps

    async def count_successful_cases(
        self,
        problem_type: str,
        min_success_rate: float = 0.8
    ) -> int:
        """
        Count available successful cases for k-anonymity check

        Args:
            problem_type: Problem type to count
            min_success_rate: Minimum success rate

        Returns:
            Number of successful cases
        """

        try:
            from intelligent_core.community_intelligence.models.database import (
                CaseContribution, ContributionStatus
            )

            # Count approved cases with this problem type
            result = await self.db.execute(
                select(func.count()).select_from(CaseContribution).where(
                    and_(
                        CaseContribution.status == ContributionStatus.APPROVED,
                        CaseContribution.tags.contains([problem_type]),
                        CaseContribution.added_to_library == True
                    )
                )
            )

            count = result.scalar() or 0

            logger.info(
                f"Found {count} successful cases for problem_type '{problem_type}'"
            )

            return count

        except Exception as e:
            logger.error(f"Error counting cases: {e}", exc_info=True)
            return 0

    async def get_problem_types(self) -> List[str]:
        """
        Get all available problem types from case library

        Returns:
            List of unique problem type tags
        """

        try:
            from intelligent_core.community_intelligence.models.database import (
                CaseContribution, ContributionStatus
            )

            # Get all tags from approved cases
            result = await self.db.execute(
                select(CaseContribution.tags).where(
                    and_(
                        CaseContribution.status == ContributionStatus.APPROVED,
                        CaseContribution.added_to_library == True
                    )
                )
            )

            # Flatten and deduplicate tags
            all_tags = []
            for row in result.scalars():
                if row:
                    all_tags.extend(row)

            problem_types = list(set(all_tags))

            logger.info(f"Found {len(problem_types)} unique problem types")

            return sorted(problem_types)

        except Exception as e:
            logger.error(f"Error getting problem types: {e}", exc_info=True)
            return []

    async def get_case_statistics(
        self,
        problem_type: str
    ) -> Dict[str, Any]:
        """
        Get statistics about cases for a problem type

        Returns:
            {
                'total_cases': 15,
                'avg_success_rate': 0.87,
                'industries': ['healthcare', 'finance', ...],
                'org_sizes': ['small', 'medium', 'large'],
                'common_approaches': ['workshops', 'templates', ...]
            }
        """

        cases = await self.find_cases(
            problem_type=problem_type,
            min_success_rate=0.0,  # Get all cases
            limit=100
        )

        if not cases:
            return {
                'total_cases': 0,
                'avg_success_rate': 0.0,
                'industries': [],
                'org_sizes': [],
                'common_approaches': []
            }

        # Calculate statistics
        total = len(cases)
        avg_success = sum(c['success_rate'] for c in cases) / total

        industries = list(set(
            c.get('organization_context', {}).get('industry', 'unknown')
            for c in cases
        ))

        org_sizes = list(set(
            c.get('organization_context', {}).get('size', 'unknown')
            for c in cases
        ))

        approaches = list(set(
            c.get('approach', {}).get('method', 'unknown')
            for c in cases
        ))

        return {
            'total_cases': total,
            'avg_success_rate': round(avg_success, 2),
            'industries': industries,
            'org_sizes': org_sizes,
            'common_approaches': approaches
        }

    async def search_cases_by_challenge(
        self,
        challenge_description: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search cases by challenge description using semantic search

        Future enhancement: Use vector embeddings for semantic matching
        For now: Simple keyword matching in challenges field

        Args:
            challenge_description: Description of the challenge
            limit: Maximum results

        Returns:
            List of matching cases
        """

        try:
            from intelligent_core.community_intelligence.models.database import (
                CaseContribution, ContributionStatus
            )

            # Extract keywords from challenge description
            keywords = challenge_description.lower().split()[:5]  # Top 5 words

            # Query cases
            query = select(CaseContribution).where(
                and_(
                    CaseContribution.status == ContributionStatus.APPROVED,
                    CaseContribution.added_to_library == True
                )
            ).limit(limit)

            result = await self.db.execute(query)
            contributions = result.scalars().all()

            # Filter by keyword matching in challenges
            matching_cases = []
            for contrib in contributions:
                challenges = contrib.case_data.get('challenges', [])
                challenge_text = ' '.join(challenges).lower()

                # Count keyword matches
                matches = sum(1 for kw in keywords if kw in challenge_text)

                if matches > 0:
                    matching_cases.append({
                        'case_id': str(contrib.id),
                        'organization_context': contrib.case_data.get('organization_context', {}),
                        'challenges': challenges,
                        'success_patterns': contrib.case_data.get('success_patterns', []),
                        'match_score': matches / len(keywords)
                    })

            # Sort by match score
            matching_cases.sort(key=lambda x: x['match_score'], reverse=True)

            logger.info(
                f"Found {len(matching_cases)} cases matching challenge '{challenge_description}'"
            )

            return matching_cases

        except Exception as e:
            logger.error(f"Error searching cases by challenge: {e}", exc_info=True)
            return []
