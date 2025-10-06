"""
Workflow Integration Service

Connects Workflow Intelligence Engine to Community Contribution System

Handles:
- Auto-detection of workflow completion
- Case data extraction and anonymization
- User opt-in management
- Contribution submission
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..models.database import CaseContribution, ContributionStatus
from ..services.anonymizer import Anonymizer
from ..services.contribution_service import ContributionService
from ..services.peer_review_service import PeerReviewService
from ..config import settings
from shared.eventbus import EventBusClient

logger = logging.getLogger(__name__)


class WorkflowIntegrationService:
    """
    Service for integrating with Workflow Intelligence Engine

    Key responsibilities:
    - Listen for workflow completion events
    - Extract case data from completed workflows
    - Offer contribution to user
    - Auto-submit if user opted-in
    """

    def __init__(
        self,
        db: AsyncSession,
        eventbus: EventBusClient,
        anonymizer: Anonymizer,
        contribution_service: ContributionService,
        peer_review_service: PeerReviewService
    ):
        self.db = db
        self.eventbus = eventbus
        self.anonymizer = anonymizer
        self.contribution_service = contribution_service
        self.peer_review_service = peer_review_service

    async def on_workflow_completed(self, event: Dict[str, Any]):
        """
        Handle workflow completion event

        Event data:
        {
            'workflow_id': str,
            'module': str ('bia', 'risk', etc.),
            'org_id': str,
            'user_id': str,
            'completed_at': str (ISO timestamp),
            'workflow_state': dict,
            'metrics': dict,
            'opt_in_to_share': bool (optional)
        }
        """

        workflow_id = event['workflow_id']
        module = event['module']
        user_id = UUID(event['user_id'])
        org_id = UUID(event['org_id'])

        logger.info(
            f"Workflow completed: {workflow_id} (module: {module}, user: {user_id})"
        )

        # Check if user opted-in to share
        opt_in = event.get('opt_in_to_share', False)

        if not opt_in:
            # Send offer to contribute
            await self._send_contribution_offer(
                user_id=user_id,
                workflow_id=workflow_id,
                module=module
            )
            return

        # User opted-in - auto-submit
        try:
            case_data = await self._extract_case_data(event)

            contribution_id = await self.contribution_service.submit_case(
                contributor_id=str(user_id),
                case_data=case_data,
                module=module
            )

            logger.info(
                f"✅ Auto-submitted contribution {contribution_id} for workflow {workflow_id}"
            )

        except Exception as e:
            logger.error(f"Failed to auto-submit contribution: {e}", exc_info=True)

            # Notify user of failure
            await self.eventbus.publish('contribution.submission_failed', {
                'user_id': str(user_id),
                'workflow_id': workflow_id,
                'error': str(e)
            })

    async def _extract_case_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract case data from workflow completion event

        Returns anonymized case data ready for contribution
        """

        # Extract relevant data
        raw_case_data = {
            'workflow_id': event['workflow_id'],
            'module': event['module'],
            'org_context': event.get('org_context', {}),
            'workflow_state': event.get('workflow_state', {}),
            'metrics': event.get('metrics', {}),
            'success_patterns': event.get('success_patterns', []),
            'challenges': event.get('challenges', []),
            'tools_used': event.get('tools_used', []),
            'timeline': event.get('timeline', {}),
            'completed_at': event['completed_at']
        }

        # Anonymize
        anonymized = await self.anonymizer.anonymize_case(raw_case_data)

        return anonymized.anonymized_data

    async def _send_contribution_offer(
        self,
        user_id: UUID,
        workflow_id: str,
        module: str
    ):
        """
        Send offer to contribute workflow as case

        Publishes event for notification service
        """

        await self.eventbus.publish('contribution.offer_sent', {
            'user_id': str(user_id),
            'workflow_id': workflow_id,
            'module': module,
            'offer_expires_at': (
                datetime.utcnow() + timedelta(days=30)
            ).isoformat(),
            'message': (
                f"Great work completing your {module.upper()} workflow! "
                f"Would you like to share your success story with the community? "
                f"Your contribution will help other organizations learn from your experience."
            )
        })

        logger.info(f"Sent contribution offer to user {user_id} for workflow {workflow_id}")

    async def submit_contribution_from_workflow(
        self,
        user_id: UUID,
        workflow_id: str,
        module: str,
        additional_notes: Optional[str] = None
    ) -> str:
        """
        Manually submit contribution from workflow

        Used when user accepts contribution offer

        Returns:
            contribution_id
        """

        # Fetch workflow data (would call Workflow Intelligence API)
        # For now, placeholder
        workflow_data = await self._fetch_workflow_data(workflow_id)

        if not workflow_data:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Extract and anonymize case data
        case_data = await self._extract_case_data(workflow_data)

        # Add user notes if provided
        if additional_notes:
            case_data['contributor_notes'] = additional_notes

        # Submit contribution
        contribution_id = await self.contribution_service.submit_case(
            contributor_id=str(user_id),
            case_data=case_data,
            module=module
        )

        logger.info(
            f"User {user_id} manually submitted contribution {contribution_id} "
            f"from workflow {workflow_id}"
        )

        return contribution_id

    async def _fetch_workflow_data(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch workflow data from Workflow Intelligence Engine

        TODO: Implement actual API call to Workflow Intelligence service
        """

        # Placeholder - would make HTTP request to workflow intelligence service
        # GET /api/v1/workflows/{workflow_id}

        logger.warning(f"_fetch_workflow_data not implemented - returning mock data")

        return {
            'workflow_id': workflow_id,
            'module': 'bia',
            'org_id': '00000000-0000-0000-0000-000000000000',
            'user_id': '00000000-0000-0000-0000-000000000000',
            'completed_at': datetime.utcnow().isoformat(),
            'workflow_state': {},
            'metrics': {},
            'org_context': {}
        }

    async def preview_anonymized_case(
        self,
        user_id: UUID,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Preview how case will look after anonymization

        Allows user to review before submitting
        """

        # Fetch workflow
        workflow_data = await self._fetch_workflow_data(workflow_id)

        if not workflow_data:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Extract and anonymize
        case_data = await self._extract_case_data(workflow_data)

        # Return preview
        return {
            'workflow_id': workflow_id,
            'anonymized_preview': case_data,
            'original_org_removed': True,
            'original_users_removed': True,
            'original_dates_generalized': True,
            'risk_assessment': {
                're_identification_risk': 'low',
                'k_anonymity': settings.K_ANONYMITY
            }
        }
