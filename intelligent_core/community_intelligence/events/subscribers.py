"""
Event Subscribers for Community Intelligence

Listens to events from:
- Workflow Intelligence (workflow completions)
- Internal events (contribution submissions, reviews)
"""

import logging
from typing import Dict, Any
from uuid import UUID

from shared.eventbus import EventBusClient
from shared.database import get_db
from ..services.workflow_integration_service import WorkflowIntegrationService
from ..services.workflow_completion_handler import WorkflowCompletionHandler
from ..services.case_library_bridge import CaseLibraryBridge
from ..services.contribution_service import ContributionService
from ..services.peer_review_service import PeerReviewService
from ..services.reputation_engine import ReputationEngine
from ..services.anonymizer import Anonymizer

logger = logging.getLogger(__name__)


async def setup_event_subscribers(eventbus: EventBusClient):
    """
    Setup all event subscribers

    Subscriptions:
    1. workflow.*.completed → on_workflow_completed
    2. case.contribution.submitted → on_contribution_submitted
    3. case.approved → on_case_approved
    """

    logger.info("Setting up Community Intelligence event subscribers...")

    # Workflow completion events (any module)
    await eventbus.subscribe(
        topics=['workflow.*.completed'],
        handler=on_workflow_completed
    )

    # Contribution submitted
    await eventbus.subscribe(
        topics=['case.contribution.submitted'],
        handler=on_contribution_submitted
    )

    # Case approved
    await eventbus.subscribe(
        topics=['case.approved'],
        handler=on_case_approved
    )

    logger.info("✅ Event subscribers registered")


async def on_workflow_completed(event: Dict[str, Any]):
    """
    Handle workflow completion event

    Event: workflow.{module}.completed
    Example: workflow.bia.completed

    Flow:
    1. Extract workflow data
    2. Check if user opted-in
    3. If yes → auto-submit contribution
    4. If no → send offer to contribute
    """

    try:
        logger.info(f"Received workflow completion event: {event.get('workflow_id')}")

        # Get services
        async for db in get_db():
            eventbus = EventBusClient()
            anonymizer = Anonymizer()

            # Create service instances
            reputation_engine = ReputationEngine(db=db, eventbus=eventbus)

            peer_review_service = PeerReviewService(
                db=db,
                eventbus=eventbus,
                reputation_engine=reputation_engine
            )

            contribution_service = ContributionService(
                db=db,
                anonymizer=anonymizer,
                case_library=None  # Case library bridge handles this
            )

            # Use new WorkflowCompletionHandler (unified handler)
            workflow_handler = WorkflowCompletionHandler(
                db=db,
                eventbus=eventbus,
                anonymizer=anonymizer,
                contribution_service=contribution_service,
                peer_review_service=peer_review_service
            )

            # Handle event
            await workflow_handler.on_workflow_completed(event)

            break  # Only need first iteration

    except Exception as e:
        logger.error(f"Error handling workflow completion: {e}", exc_info=True)


async def on_contribution_submitted(event: Dict[str, Any]):
    """
    Handle contribution submission event

    Event: case.contribution.submitted

    Flow:
    1. Get contribution details
    2. Assign peer reviewers
    3. Send notifications to reviewers
    """

    try:
        contribution_id = UUID(event['contribution_id'])
        module = event['module']

        logger.info(f"Handling contribution submission: {contribution_id}")

        # Get services
        async for db in get_db():
            eventbus = EventBusClient()
            reputation_engine = ReputationEngine(db=db, eventbus=eventbus)

            peer_review_service = PeerReviewService(
                db=db,
                eventbus=eventbus,
                reputation_engine=reputation_engine
            )

            # Get contribution
            from ..models.database import CaseContribution
            contribution = await db.get(CaseContribution, contribution_id)

            if not contribution:
                logger.error(f"Contribution {contribution_id} not found")
                return

            # Assign reviewers
            reviewers = await peer_review_service.assign_reviewers(
                contribution_id=contribution_id,
                module=module,
                contributor_id=contribution.contributor_id,
                contributor_org_id=contribution.org_id
            )

            # Update contribution with assigned reviewers
            contribution.reviewers = [r.user_id for r in reviewers]
            await db.commit()

            logger.info(
                f"Assigned {len(reviewers)} reviewers to contribution {contribution_id}"
            )

            break  # Only need first iteration

    except Exception as e:
        logger.error(f"Error handling contribution submission: {e}", exc_info=True)


async def on_case_approved(event: Dict[str, Any]):
    """
    Handle case approval event

    Event: case.approved

    Flow:
    1. Add case to Workflow Intelligence Case Library (via bridge)
    2. Update contribution record with library_case_id
    3. Notify contributor
    """

    try:
        contribution_id = UUID(event['contribution_id'])
        case_data = event['case_data']
        module = event['module']

        logger.info(f"Handling case approval: {contribution_id}")

        # Get services
        async for db in get_db():
            # Use Case Library Bridge to sync to Workflow Intelligence
            case_bridge = CaseLibraryBridge(db=db)

            # Add to Workflow Intelligence Case Library
            workflow_case_id = await case_bridge.on_case_approved(
                contribution_id=contribution_id,
                case_data=case_data,
                module=module
            )

            # Update contribution record
            from ..models.database import CaseContribution
            contribution = await db.get(CaseContribution, contribution_id)

            if contribution and workflow_case_id:
                contribution.added_to_library = True
                contribution.library_case_id = UUID(workflow_case_id)
                await db.commit()

                logger.info(
                    f"✅ Contribution {contribution_id} synced to workflow library "
                    f"as {workflow_case_id}"
                )
            elif contribution:
                # Failed to sync but mark as approved
                contribution.added_to_library = False
                await db.commit()
                logger.warning(
                    f"⚠️ Contribution {contribution_id} approved but not synced to workflow library"
                )

            break  # Only need first iteration

    except Exception as e:
        logger.error(f"Error handling case approval: {e}", exc_info=True)
