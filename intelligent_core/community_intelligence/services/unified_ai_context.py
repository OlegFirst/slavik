"""
Unified AI Context Builder

Combines context from multiple sources for AI Advisor:
- Workflow Intelligence (workflow state, progress, validation)
- Community Intelligence (reputation, similar cases, patterns)
- Organization Context
- Case Library (benchmarks, best practices)

Provides comprehensive context to AI for intelligent recommendations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging
import httpx

from ..models.database import UserReputation, CaseContribution, ContributionStatus
from ..config import settings

logger = logging.getLogger(__name__)


class UnifiedAIContextBuilder:
    """
    Build comprehensive AI context from all available sources

    Context Structure:
    {
        'workflow': {...},           # From workflow_intelligence
        'user': {...},                # From community_intelligence
        'organization': {...},        # Org profile
        'community': {...},           # Community insights
        'benchmarks': {...},          # Performance benchmarks
        'recommendations': {...}      # Contextual recommendations
    }
    """

    def __init__(
        self,
        db: AsyncSession,
        workflow_api_url: str = None
    ):
        self.db = db
        self.workflow_api_url = workflow_api_url or settings.WORKFLOW_INTELLIGENCE_URL

    async def build_full_context(
        self,
        user_id: UUID,
        workflow_id: Optional[str] = None,
        module: Optional[str] = None,
        org_id: Optional[UUID] = None,
        include_similar_cases: bool = True,
        include_benchmarks: bool = True
    ) -> Dict[str, Any]:
        """
        Build complete AI context from all sources

        Args:
            user_id: User making request
            workflow_id: Active workflow (if any)
            module: BCM module ('bia', 'risk', etc.)
            org_id: Organization ID
            include_similar_cases: Include similar community cases
            include_benchmarks: Include industry benchmarks

        Returns:
            Comprehensive context dict
        """

        logger.debug(
            f"Building unified AI context for user {user_id}, "
            f"workflow {workflow_id}, module {module}"
        )

        context = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': str(user_id),
            'workflow_id': workflow_id,
            'module': module
        }

        # 1. Workflow context (from workflow_intelligence)
        if workflow_id:
            workflow_ctx = await self._get_workflow_context(workflow_id)
            context['workflow'] = workflow_ctx
        else:
            context['workflow'] = None

        # 2. User reputation and expertise
        user_ctx = await self._get_user_context(user_id, module)
        context['user'] = user_ctx

        # 3. Organization profile
        if org_id:
            org_ctx = await self._get_organization_context(org_id)
            context['organization'] = org_ctx
        else:
            context['organization'] = None

        # 4. Community insights
        if module:
            community_ctx = await self._get_community_context(module, org_id)
            context['community'] = community_ctx

        # 5. Similar cases (if requested)
        if include_similar_cases and org_id and module:
            similar_cases = await self._get_similar_cases(
                module=module,
                org_id=org_id,
                limit=5
            )
            context['similar_cases'] = similar_cases
        else:
            context['similar_cases'] = []

        # 6. Benchmarks (if requested)
        if include_benchmarks and module and org_id:
            benchmarks = await self._get_benchmarks(module, org_id)
            context['benchmarks'] = benchmarks
        else:
            context['benchmarks'] = None

        # 7. Contextual recommendations
        context['recommendations'] = self._generate_recommendations(context)

        logger.debug(f" Unified context built with {len(context)} components")

        return context

    async def _get_workflow_context(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow context from Workflow Intelligence API

        Endpoint: GET /api/v1/workflows/{workflow_id}/context
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.workflow_api_url}/api/v1/workflows/{workflow_id}/context",
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"Could not fetch workflow context for {workflow_id}: "
                        f"HTTP {response.status_code}"
                    )
                    return None

            except Exception as e:
                logger.error(f"Error fetching workflow context: {e}")
                return None

    async def _get_user_context(
        self,
        user_id: UUID,
        module: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user reputation and community standing

        Returns:
            User context with reputation, expertise, contributions
        """

        # Get reputation
        reputation = await self.db.get(UserReputation, user_id)

        if not reputation:
            return {
                'has_reputation': False,
                'level': 'newcomer',
                'total_points': 0,
                'expertise': {},
                'contributions_count': 0
            }

        # Module-specific expertise
        module_expertise = None
        if module:
            module_expertise = {
                'module': module,
                'points': reputation.expertise.get(module, 0),
                'level': self._calculate_expertise_level(
                    reputation.expertise.get(module, 0)
                )
            }

        return {
            'has_reputation': True,
            'level': reputation.level,
            'total_points': reputation.total_points,
            'expertise': reputation.expertise,
            'module_expertise': module_expertise,
            'contributions_count': reputation.contributions_count,
            'cases_approved': reputation.cases_approved,
            'avg_case_quality': float(reputation.avg_case_quality) if reputation.avg_case_quality else 0,
            'reviews_count': reputation.reviews_count,
            'marketplace_priority': reputation.marketplace_priority,
            'first_contribution': reputation.first_contribution.isoformat() if reputation.first_contribution else None
        }

    def _calculate_expertise_level(self, points: int) -> str:
        """Calculate expertise level from points"""
        if points >= 500:
            return 'expert'
        elif points >= 150:
            return 'advanced'
        elif points >= 50:
            return 'intermediate'
        else:
            return 'novice'

    async def _get_organization_context(self, org_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get organization profile

        TODO: Fetch from organization service
        For now, returns placeholder
        """

        # Would fetch from organization/governance service
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(f"http://governance:8010/organizations/{org_id}")
        #     return response.json()

        return {
            'org_id': str(org_id),
            'industry': 'healthcare',  # Placeholder
            'size': 'medium',
            'bcm_maturity': 'developing',
            'region': 'EU'
        }

    async def _get_community_context(
        self,
        module: str,
        org_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get community insights for module

        Returns:
            Community patterns, trending topics, participation stats
        """

        # Get approved case count
        approved_count_query = select(CaseContribution).where(
            and_(
                CaseContribution.module == module,
                CaseContribution.status == ContributionStatus.APPROVED
            )
        )

        result = await self.db.execute(approved_count_query)
        approved_cases = result.scalars().all()

        # Extract trending patterns
        trending_patterns = self._extract_trending_patterns(approved_cases)

        # Get participation stats
        total_contributors = len(set(c.contributor_id for c in approved_cases))

        return {
            'module': module,
            'approved_cases_count': len(approved_cases),
            'unique_contributors': total_contributors,
            'trending_patterns': trending_patterns,
            'avg_quality_score': self._calculate_avg_quality(approved_cases),
            'community_activity': 'active' if len(approved_cases) > 10 else 'growing'
        }

    def _extract_trending_patterns(
        self,
        cases: List[CaseContribution]
    ) -> List[Dict[str, Any]]:
        """Extract trending success patterns from cases"""

        # Collect all success patterns
        all_patterns = []
        for case in cases:
            patterns = case.case_data.get('success_patterns', [])
            all_patterns.extend(patterns)

        # Count frequencies
        from collections import Counter
        pattern_counts = Counter(all_patterns)

        # Return top 5
        trending = []
        for pattern, count in pattern_counts.most_common(5):
            trending.append({
                'pattern': pattern,
                'frequency': count,
                'percentage': round(count / len(cases) * 100, 1) if cases else 0
            })

        return trending

    def _calculate_avg_quality(self, cases: List[CaseContribution]) -> float:
        """Calculate average quality score from peer reviews"""

        # Would aggregate from peer_reviews table
        # For now, placeholder
        return 7.8

    async def _get_similar_cases(
        self,
        module: str,
        org_id: UUID,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get similar approved cases

        Matches on:
        - Same module
        - Similar industry/size
        - High quality scores
        """

        # Get org context for matching
        org_ctx = await self._get_organization_context(org_id)
        industry = org_ctx.get('industry')
        size = org_ctx.get('size')

        # Query approved cases
        query = select(CaseContribution).where(
            and_(
                CaseContribution.module == module,
                CaseContribution.status == ContributionStatus.APPROVED
            )
        )

        # Filter by tags (industry, size)
        if industry:
            query = query.where(CaseContribution.tags.contains([industry]))
        if size:
            query = query.where(CaseContribution.tags.contains([size]))

        query = query.order_by(CaseContribution.approved_at.desc()).limit(limit)

        result = await self.db.execute(query)
        cases = result.scalars().all()

        # Transform for AI context
        similar = []
        for case in cases:
            similar.append({
                'case_id': str(case.id),
                'module': case.module,
                'org_type': case.original_org_type,
                'success_patterns': case.case_data.get('success_patterns', [])[:3],  # Top 3
                'lessons_learned': case.case_data.get('lessons_learned', [])[:2],   # Top 2
                'metrics': case.case_data.get('metrics', {}),
                'approved_at': case.approved_at.isoformat() if case.approved_at else None
            })

        return similar

    async def _get_benchmarks(
        self,
        module: str,
        org_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get industry benchmarks from workflow intelligence

        Endpoint: GET /api/v1/benchmarks/{module}
        """

        org_ctx = await self._get_organization_context(org_id)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.workflow_api_url}/api/v1/benchmarks/{module}",
                    params={
                        'industry': org_ctx.get('industry'),
                        'size': org_ctx.get('size')
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return None

            except Exception as e:
                logger.error(f"Error fetching benchmarks: {e}")
                return None

    def _generate_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Generate contextual recommendations based on full context

        Uses heuristics to provide helpful suggestions
        """

        recommendations = []

        # User-specific recommendations
        user = context.get('user', {})
        if user.get('level') == 'newcomer':
            recommendations.append(
                " Build your reputation by contributing case studies from completed workflows"
            )

        if user.get('contributions_count', 0) == 0:
            recommendations.append(
                " Complete a workflow and share your experience to earn your first reputation points"
            )

        # Workflow-specific recommendations
        workflow = context.get('workflow')
        if workflow:
            if not workflow.get('is_valid'):
                recommendations.append(
                    "️ Complete all validation requirements before proceeding to next stage"
                )

            time_in_stage = workflow.get('time_in_stage_hours', 0)
            if time_in_stage > 48:
                recommendations.append(
                    "⏰ You've been in this stage for over 48 hours - check similar cases for guidance"
                )

        # Community recommendations
        similar_cases = context.get('similar_cases', [])
        if len(similar_cases) > 0:
            recommendations.append(
                f" Found {len(similar_cases)} similar cases from organizations like yours"
            )

        return recommendations

    def format_for_llm_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format unified context into LLM prompt

        Creates comprehensive prompt with all context
        """

        sections = []

        # Header
        sections.append("=" * 60)
        sections.append("AI ADVISOR CONTEXT")
        sections.append("=" * 60)

        # User context
        user = context.get('user', {})
        sections.append("\n USER PROFILE:")
        sections.append(f"  Level: {user.get('level', 'newcomer').upper()}")
        sections.append(f"  Total Points: {user.get('total_points', 0)}")
        if user.get('module_expertise'):
            me = user['module_expertise']
            sections.append(f"  Expertise in {me['module'].upper()}: {me['level'].upper()} ({me['points']} points)")

        # Workflow context
        workflow = context.get('workflow')
        if workflow:
            sections.append("\n CURRENT WORKFLOW:")
            sections.append(f"  State: {workflow.get('current_state', 'unknown')}")
            sections.append(f"  Progress: {workflow.get('progress', 0)}%")
            sections.append(f"  Valid: {' Yes' if workflow.get('is_valid') else ' No'}")

            if not workflow.get('is_valid'):
                errors = workflow.get('validation_errors', [])
                sections.append(f"  Validation Errors: {', '.join(errors)}")

        # Organization context
        org = context.get('organization')
        if org:
            sections.append("\n ORGANIZATION:")
            sections.append(f"  Industry: {org.get('industry', 'N/A')}")
            sections.append(f"  Size: {org.get('size', 'N/A')}")
            sections.append(f"  BCM Maturity: {org.get('bcm_maturity', 'N/A')}")

        # Similar cases
        similar = context.get('similar_cases', [])
        if similar:
            sections.append(f"\n SIMILAR SUCCESS CASES ({len(similar)}):")
            for i, case in enumerate(similar[:3], 1):  # Top 3
                sections.append(f"\n  Case {i}:")
                patterns = case.get('success_patterns', [])
                for pattern in patterns[:2]:
                    sections.append(f"     {pattern}")

        # Trending patterns
        community = context.get('community', {})
        trending = community.get('trending_patterns', [])
        if trending:
            sections.append("\n TRENDING COMMUNITY PATTERNS:")
            for pattern in trending[:3]:
                sections.append(f"  • {pattern['pattern']} ({pattern['percentage']}% of cases)")

        # Benchmarks
        benchmarks = context.get('benchmarks')
        if benchmarks:
            sections.append("\n INDUSTRY BENCHMARKS:")
            sections.append(f"  Avg Duration: {benchmarks.get('avg_duration_days', 'N/A')} days")
            sections.append(f"  Success Rate: {benchmarks.get('success_rate', 'N/A')}%")

        # Recommendations
        recs = context.get('recommendations', [])
        if recs:
            sections.append("\n CONTEXTUAL RECOMMENDATIONS:")
            for rec in recs:
                sections.append(f"  {rec}")

        sections.append("\n" + "=" * 60)

        return "\n".join(sections)
