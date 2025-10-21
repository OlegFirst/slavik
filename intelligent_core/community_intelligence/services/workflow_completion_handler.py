"""
Workflow Completion Handler

Handles workflow completion events and integrates with community contribution system.

This is the critical bridge connecting:
- workflow_intelligence (workflow completion)
→ community_intelligence (case contribution offering)

Event Flow:
1. Workflow completes → workflow.{module}.completed event
2. WorkflowCompletionHandler receives event
3. Extract case data from completed workflow
4. Check user opt-in preference
5. Auto-submit OR offer contribution to user
6. Assign peer reviewers
7. Community review process begins
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import httpx

from ..models.database import CaseContribution, ContributionStatus
from ..services.anonymizer import Anonymizer
from ..services.contribution_service import ContributionService
from ..services.peer_review_service import PeerReviewService
from ..config import settings
from shared.eventbus import EventBusClient

logger = logging.getLogger(__name__)


class WorkflowCompletionHandler:
    """
    Main handler for workflow completion → community contribution pipeline

    Subscribes to workflow completion events and manages the flow:
    - Extract workflow data
    - Anonymize for privacy
    - Offer/submit contribution
    - Trigger peer review
    """

    def __init__(
        self,
        db: AsyncSession,
        eventbus: EventBusClient,
        anonymizer: Anonymizer,
        contribution_service: ContributionService,
        peer_review_service: PeerReviewService,
        workflow_api_url: str = None
    ):
        self.db = db
        self.eventbus = eventbus
        self.anonymizer = anonymizer
        self.contribution_service = contribution_service
        self.peer_review_service = peer_review_service
        self.workflow_api_url = workflow_api_url or settings.WORKFLOW_INTELLIGENCE_URL

    async def setup_subscriptions(self):
        """
        Subscribe to workflow completion events

        Events to subscribe:
        - workflow.bia.completed
        - workflow.risk.completed
        - workflow.planning.completed
        - workflow.*.completed (catch-all)
        """

        await self.eventbus.subscribe([
            'workflow.bia.completed',
            'workflow.risk.completed',
            'workflow.planning.completed',
            'workflow.governance.completed',
            'workflow.*.completed'
        ], self.on_workflow_completed)

        logger.info(" Subscribed to workflow completion events")

    async def on_workflow_completed(self, event: Dict[str, Any]):
        """
        Handle workflow completion event

        Event structure:
        {
            'workflow_id': str,
            'module': str,  # 'bia', 'risk', 'planning', etc.
            'org_id': str,
            'user_id': str,
            'completed_at': str (ISO timestamp),
            'completed_successfully': bool,
            'workflow_state': dict,  # Full workflow state
            'metrics': dict,
            'user_preferences': {
                'opt_in_to_share': bool
            }
        }
        """

        workflow_id = event.get('workflow_id')
        module = event.get('module')
        user_id = event.get('user_id')
        org_id = event.get('org_id')
        completed_successfully = event.get('completed_successfully', False)

        logger.info(
            f" Workflow completed: {workflow_id} (module: {module}, "
            f"user: {user_id}, success: {completed_successfully})"
        )

        # Only process successfully completed workflows
        if not completed_successfully:
            logger.debug(f"Workflow {workflow_id} not successful, skipping contribution offer")
            return

        # Check user opt-in preference
        user_prefs = event.get('user_preferences', {})
        opt_in = user_prefs.get('opt_in_to_share', False)

        try:
            # Fetch full workflow case data
            workflow_case = await self._fetch_workflow_case(workflow_id)

            if not workflow_case:
                logger.warning(f"Could not fetch workflow case data for {workflow_id}")
                return

            if opt_in:
                # User opted-in: Auto-submit contribution
                await self._auto_submit_contribution(
                    user_id=UUID(user_id),
                    org_id=UUID(org_id),
                    workflow_case=workflow_case,
                    module=module
                )
            else:
                # Send offer to contribute
                await self._send_contribution_offer(
                    user_id=UUID(user_id),
                    workflow_id=workflow_id,
                    module=module,
                    org_id=UUID(org_id)
                )

        except Exception as e:
            logger.error(
                f"Error processing workflow completion {workflow_id}: {e}",
                exc_info=True
            )

            # Notify user of error
            await self.eventbus.publish('contribution.processing_failed', {
                'workflow_id': workflow_id,
                'user_id': user_id,
                'error': str(e)
            })

    async def _fetch_workflow_case(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch complete workflow case from Workflow Intelligence API

        Endpoint: GET /api/v1/workflows/{workflow_id}/case
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.workflow_api_url}/api/v1/workflows/{workflow_id}/case",
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"Failed to fetch workflow case {workflow_id}: "
                        f"HTTP {response.status_code}"
                    )
                    return None

            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching workflow case: {e}")
                return None
            except Exception as e:
                logger.error(f"Error fetching workflow case: {e}")
                return None

    async def _auto_submit_contribution(
        self,
        user_id: UUID,
        org_id: UUID,
        workflow_case: Dict[str, Any],
        module: str
    ):
        """
        Auto-submit contribution (user opted-in)

        Flow:
        1. Anonymize case data
        2. Submit as contribution
        3. Assign peer reviewers
        4. Notify user
        """

        logger.info(f" Auto-submitting contribution for user {user_id}")

        try:
            # Anonymize case data
            anonymized_result = await self.anonymizer.anonymize_case(workflow_case)

            # Submit contribution
            contribution_id = await self.contribution_service.submit_case(
                contributor_id=str(user_id),
                case_data=anonymized_result.anonymized_data,
                module=module
            )

            logger.info(
                f" Auto-submitted contribution {contribution_id} for workflow "
                f"{workflow_case.get('case_id')} by user {user_id}"
            )

            # Notify user of successful submission
            await self.eventbus.publish('contribution.auto_submitted', {
                'user_id': str(user_id),
                'contribution_id': contribution_id,
                'module': module,
                'message': (
                    "Your workflow has been anonymized and submitted to the community! "
                    "Peer reviewers will evaluate it within 7 days."
                )
            })

        except Exception as e:
            logger.error(f"Failed to auto-submit contribution: {e}", exc_info=True)

            # Fallback: Send offer instead
            await self._send_contribution_offer(
                user_id=user_id,
                workflow_id=workflow_case.get('case_id'),
                module=module,
                org_id=org_id
            )

    async def _send_contribution_offer(
        self,
        user_id: UUID,
        workflow_id: str,
        module: str,
        org_id: UUID
    ):
        """
        Send offer to user to contribute their workflow

        Creates a notification for the user
        """

        logger.info(f" Sending contribution offer to user {user_id}")

        # Publish offer event (notification service will handle)
        await self.eventbus.publish('contribution.offer_sent', {
            'user_id': str(user_id),
            'workflow_id': workflow_id,
            'module': module,
            'org_id': str(org_id),
            'offer_expires_at': (
                datetime.utcnow() + timedelta(days=30)
            ).isoformat(),
            'message': (
                f" Congratulations on completing your {module.upper()} workflow! "
                f"\n\nWould you like to share your success story with the community? "
                f"Your contribution will help other organizations learn from your experience. "
                f"\n\nYour data will be anonymized before sharing."
            ),
            'actions': [
                {
                    'type': 'accept',
                    'label': 'Share My Success',
                    'api_endpoint': f'/api/v1/community/contributions/from-workflow/{workflow_id}'
                },
                {
                    'type': 'preview',
                    'label': 'Preview Anonymized Data',
                    'api_endpoint': f'/api/v1/community/contributions/preview-anonymization'
                },
                {
                    'type': 'decline',
                    'label': 'No Thanks',
                    'api_endpoint': None
                }
            ]
        })

        logger.info(f" Contribution offer sent to user {user_id}")

    async def manually_submit_from_workflow(
        self,
        user_id: UUID,
        workflow_id: str,
        module: str,
        additional_notes: Optional[str] = None
    ) -> str:
        """
        Manually submit contribution from workflow
        (when user accepts the offer)

        Args:
            user_id: User accepting the offer
            workflow_id: Workflow to contribute
            module: BCM module
            additional_notes: Optional user notes

        Returns:
            contribution_id
        """

        logger.info(
            f" Manual contribution submission: workflow {workflow_id} by user {user_id}"
        )

        # Fetch workflow case
        workflow_case = await self._fetch_workflow_case(workflow_id)

        if not workflow_case:
            raise ValueError(f"Workflow {workflow_id} not found or not accessible")

        # Anonymize
        anonymized_result = await self.anonymizer.anonymize_case(workflow_case)

        # Add user notes if provided
        case_data = anonymized_result.anonymized_data
        if additional_notes:
            case_data['contributor_notes'] = additional_notes

        # Submit
        contribution_id = await self.contribution_service.submit_case(
            contributor_id=str(user_id),
            case_data=case_data,
            module=module
        )

        logger.info(
            f" User {user_id} manually submitted contribution {contribution_id} "
            f"from workflow {workflow_id}"
        )

        # Notify user
        await self.eventbus.publish('contribution.submitted', {
            'user_id': str(user_id),
            'contribution_id': contribution_id,
            'workflow_id': workflow_id,
            'module': module
        })

        return contribution_id

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
        workflow_case = await self._fetch_workflow_case(workflow_id)

        if not workflow_case:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Anonymize
        anonymized_result = await self.anonymizer.anonymize_case(workflow_case)

        # Return preview with metadata
        return {
            'workflow_id': workflow_id,
            'anonymized_case': anonymized_result.anonymized_data,
            'anonymization_metadata': {
                'removed_fields': anonymized_result.removed_fields,
                'generalized_fields': anonymized_result.generalized_fields,
                're_identification_risk': anonymized_result.risk_score,
                'k_anonymity': settings.K_ANONYMITY
            },
            'what_was_removed': [
                'Organization name and specific identifiers',
                'Employee names and contact information',
                'Exact dates (generalized to quarters)',
                'Specific locations (generalized to regions)',
                'Proprietary business information'
            ],
            'what_remains': [
                'Organization type and industry',
                'Organization size category',
                'Workflow structure and stages',
                'Success patterns and lessons learned',
                'Anonymized metrics and benchmarks'
            ]
        }
