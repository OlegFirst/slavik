"""
Case Library Bridge Service

Connects workflow_intelligence cases with community_intelligence contributions.

Responsibilities:
- Sync approved community contributions to workflow case library
- Enable workflow case library to use community-contributed cases
- Maintain bidirectional case visibility
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging
import httpx

from ..models.database import CaseContribution, ContributionStatus
from ..config import settings

logger = logging.getLogger(__name__)


class CaseLibraryBridge:
    """
    Bridge between two case libraries:
    - workflow_intelligence.cases (WorkflowCaseDB)
    - community_intelligence.case_contributions (CaseContribution)

    Ensures approved community cases are available in workflow case library
    """

    def __init__(self, db: AsyncSession, workflow_intelligence_api_url: str = None):
        self.db = db
        self.workflow_api_url = workflow_intelligence_api_url or settings.WORKFLOW_INTELLIGENCE_URL

    async def on_case_approved(
        self,
        contribution_id: UUID,
        case_data: Dict[str, Any],
        module: str
    ) -> Optional[str]:
        """
        When community case approved, add to workflow case library

        Args:
            contribution_id: Community contribution ID
            case_data: Anonymized case data
            module: BCM module (bia, risk, etc.)

        Returns:
            workflow_case_id if successfully added to workflow library
        """

        try:
            # Transform community case format to workflow case format
            workflow_case = self._transform_to_workflow_format(
                case_data=case_data,
                module=module,
                source='community',
                contribution_id=str(contribution_id)
            )

            # Add to workflow intelligence case library via API
            workflow_case_id = await self._add_to_workflow_library(workflow_case)

            logger.info(
                f"✅ Community case {contribution_id} added to workflow library "
                f"as {workflow_case_id}"
            )

            return workflow_case_id

        except Exception as e:
            logger.error(
                f"Failed to add community case {contribution_id} to workflow library: {e}",
                exc_info=True
            )
            return None

    def _transform_to_workflow_format(
        self,
        case_data: Dict[str, Any],
        module: str,
        source: str,
        contribution_id: str
    ) -> Dict[str, Any]:
        """
        Transform community contribution format to workflow case format

        Community format:
        {
            'organization_context': {...},
            'journey': [...],
            'metrics': {...},
            'success_patterns': [...],
            'lessons_learned': [...]
        }

        Workflow format (WorkflowCase):
        {
            'case_id': str,
            'module': str,
            'workflow_name': str,
            'organization_context': OrganizationContext,
            'journey': List[WorkflowStep],
            'metrics': WorkflowMetrics,
            'success_patterns': List[str],
            'lessons_learned': List[str],
            'status': 'completed',
            'source': 'community',
            'metadata': {...}
        }
        """

        org_ctx = case_data.get('organization_context', {})

        return {
            'case_id': str(uuid4()),
            'module': module,
            'workflow_name': f"{module}_workflow",

            # Organization context (already anonymized)
            'organization_context': {
                'industry': org_ctx.get('industry', 'unknown'),
                'size': org_ctx.get('size', 'medium'),
                'maturity_level': org_ctx.get('maturity_level', 'developing'),
                'region': org_ctx.get('region'),
                'regulatory_context': org_ctx.get('regulatory_context', [])
            },

            # Journey (may need transformation)
            'journey': self._transform_journey(case_data.get('journey', [])),

            # Metrics
            'metrics': {
                'total_duration_days': case_data.get('metrics', {}).get('duration_days', 0),
                'processes_count': case_data.get('metrics', {}).get('processes_count', 0),
                'ai_usage_count': case_data.get('metrics', {}).get('ai_usage_count', 0),
                'challenges_encountered': case_data.get('metrics', {}).get('challenges_count', 0),
                'challenges_resolved': case_data.get('metrics', {}).get('challenges_resolved', 0),
                'completed_successfully': case_data.get('metrics', {}).get('success', True),
                'user_satisfaction': case_data.get('metrics', {}).get('satisfaction_score')
            },

            # Patterns and lessons
            'success_patterns': case_data.get('success_patterns', []),
            'lessons_learned': case_data.get('lessons_learned', []),

            # Status
            'status': 'completed',

            # Source metadata
            'source': source,
            'metadata': {
                'community_contribution_id': contribution_id,
                'submitted_at': datetime.utcnow().isoformat(),
                'quality_reviewed': True
            }
        }

    def _transform_journey(self, journey: List[Dict]) -> List[Dict]:
        """
        Transform journey to workflow step format if needed

        Community may have different format than workflow
        """

        transformed = []

        for step in journey:
            transformed.append({
                'stage': step.get('stage') or step.get('step_name', 'unknown'),
                'started_at': step.get('started_at'),
                'completed_at': step.get('completed_at'),
                'duration_hours': step.get('duration_hours', 0),
                'actions': step.get('actions', []),
                'challenges': step.get('challenges', []),
                'ai_interventions': step.get('ai_interventions', [])
            })

        return transformed

    async def _add_to_workflow_library(self, workflow_case: Dict[str, Any]) -> str:
        """
        Add case to workflow intelligence case library via API

        Returns:
            case_id from workflow library
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.workflow_api_url}/api/v1/cases",
                    json=workflow_case,
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()

                return result['case_id']

            except httpx.HTTPError as e:
                logger.error(f"HTTP error adding case to workflow library: {e}")
                raise
            except Exception as e:
                logger.error(f"Error adding case to workflow library: {e}")
                raise

    async def get_community_cases_for_workflow(
        self,
        module: str,
        industry: Optional[str] = None,
        org_size: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get approved community cases for use in workflow context

        Used by workflow intelligence to show community success stories
        """

        # Build query
        query = select(CaseContribution).where(
            and_(
                CaseContribution.status == ContributionStatus.APPROVED,
                CaseContribution.module == module,
                CaseContribution.added_to_library == True
            )
        )

        # Add filters
        if industry:
            query = query.where(CaseContribution.tags.contains([industry]))
        if org_size:
            query = query.where(CaseContribution.tags.contains([org_size]))

        # Order by quality
        query = query.order_by(CaseContribution.approved_at.desc()).limit(limit)

        # Execute
        result = await self.db.execute(query)
        contributions = result.scalars().all()

        # Transform to workflow format
        cases = []
        for contrib in contributions:
            cases.append({
                'case_id': str(contrib.library_case_id or contrib.id),
                'module': contrib.module,
                'case_data': contrib.case_data,
                'org_type': contrib.original_org_type,
                'tags': contrib.tags,
                'approved_at': contrib.approved_at.isoformat() if contrib.approved_at else None,
                'source': 'community'
            })

        return cases

    async def sync_approved_cases(self):
        """
        One-time sync of all approved community cases to workflow library

        Useful for initial migration or periodic sync
        """

        # Get all approved cases not yet synced
        result = await self.db.execute(
            select(CaseContribution).where(
                and_(
                    CaseContribution.status == ContributionStatus.APPROVED,
                    CaseContribution.added_to_library == False
                )
            )
        )

        contributions = result.scalars().all()

        logger.info(f"Syncing {len(contributions)} approved cases to workflow library...")

        synced_count = 0
        failed_count = 0

        for contrib in contributions:
            try:
                workflow_case_id = await self.on_case_approved(
                    contribution_id=contrib.id,
                    case_data=contrib.case_data,
                    module=contrib.module
                )

                if workflow_case_id:
                    # Update contribution record
                    contrib.library_case_id = UUID(workflow_case_id)
                    contrib.added_to_library = True
                    synced_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                logger.error(f"Failed to sync contribution {contrib.id}: {e}")
                failed_count += 1

        await self.db.commit()

        logger.info(
            f"✅ Sync complete: {synced_count} synced, {failed_count} failed"
        )

        return {
            'synced': synced_count,
            'failed': failed_count,
            'total': len(contributions)
        }
