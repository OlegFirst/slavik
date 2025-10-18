"""
Governance Service - Event Subscribers
Listens to events from other services and processes them
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from typing import Dict, Any
from datetime import datetime
from shared.eventbus.client import get_eventbus
import logging

logger = logging.getLogger(__name__)


class GovernanceEventSubscriber:
    """
    Event subscriber for Governance Service

    Listens to events from:
    - Learning Service (training completions -> competence updates)
    - Exercise Service (exercise results -> objective progress)
    - Risk Service (risk assessments -> context analysis updates)
    - Incident Service (incidents -> resource allocation)
    - Document Service (document approvals -> policy references)
    """

    def __init__(self):
        self.eventbus = None

    async def init(self):
        """Initialize EventBus connection"""
        try:
            self.eventbus = get_eventbus()
            logger.info("GovernanceEventSubscriber initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GovernanceEventSubscriber: {e}")

    # ========================================================================
    # LEARNING SERVICE EVENTS
    # ========================================================================

    async def handle_training_completed(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle training completion event from Learning Service

        Updates competence records when training is completed
        """
        try:
            logger.info(f"Received training.completed event: {event_data}")

            # Extract data
            enrollment_id = event_data.get("enrollment_id")
            person_id = event_data.get("person_id")
            program_id = event_data.get("program_id")

            # TODO: Update competence record for person
            # Query CompetenceRecord and update current_level if training matches competence_area
            logger.info(f"Training completed event received: person={person_id}, program={program_id}")

        except Exception as e:
            logger.error(f"Error handling training.completed event: {e}")

    async def handle_certification_issued(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle certification issued event from Learning Service

        Updates competence evidence when certification is issued
        """
        try:
            logger.info(f"Received certification.issued event: {event_data}")

            enrollment_id = event_data.get("enrollment_id")
            person_id = event_data.get("person_id")
            certification_number = event_data.get("certification_number")

            # TODO: Update competence evidence_details with certification info
            logger.info(f"Certification issued: person={person_id}, cert={certification_number}")

        except Exception as e:
            logger.error(f"Error handling certification.issued event: {e}")

    # ========================================================================
    # EXERCISE SERVICE EVENTS
    # ========================================================================

    async def handle_exercise_completed(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle exercise completion event from Exercise Service

        Updates BCM objectives based on exercise results
        """
        try:
            logger.info(f"Received exercise.completed event: {event_data}")

            exercise_id = event_data.get("exercise_id")
            effectiveness_score = event_data.get("effectiveness_score", 0)

            # TODO: Update related BCM objectives with exercise results
            # Find objectives related to exercised processes and update progress
            logger.info(f"Exercise completed: exercise={exercise_id}, score={effectiveness_score}")

        except Exception as e:
            logger.error(f"Error handling exercise.completed event: {e}")

    async def handle_gap_identified(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle gap identified event from Exercise Service

        Creates action items in context analysis or objectives
        """
        try:
            logger.info(f"Received exercise.gap_identified event: {event_data}")

            gap_description = event_data.get("gap_description")
            severity = event_data.get("severity")

            # TODO: Create action items or update context analysis
            logger.info(f"Gap identified: description={gap_description}, severity={severity}")

        except Exception as e:
            logger.error(f"Error handling gap.identified event: {e}")

    # ========================================================================
    # RISK SERVICE EVENTS
    # ========================================================================

    async def handle_risk_identified(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle risk identified event from Risk Service

        Links risks to context analysis
        """
        try:
            logger.info(f"Received risk.identified event: {event_data}")

            risk_id = event_data.get("risk_id")
            risk_category = event_data.get("category")

            # TODO: Link risk to relevant context analyses
            # Update ContextAnalysis.identified_risks
            logger.info(f"Risk identified: risk_id={risk_id}, category={risk_category}")

        except Exception as e:
            logger.error(f"Error handling risk.identified event: {e}")

    # ========================================================================
    # INCIDENT SERVICE EVENTS
    # ========================================================================

    async def handle_incident_declared(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle incident declared event from Incident Service

        Updates resource allocation status
        """
        try:
            logger.info(f"Received incident.declared event: {event_data}")

            incident_id = event_data.get("incident_id")
            severity = event_data.get("severity")

            # TODO: Update critical resources to allocated status
            # Mark resources as allocated during incident
            logger.info(f"Incident declared: incident_id={incident_id}, severity={severity}")

        except Exception as e:
            logger.error(f"Error handling incident.declared event: {e}")

    async def handle_incident_resolved(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle incident resolved event from Incident Service

        Releases allocated resources
        """
        try:
            logger.info(f"Received incident.resolved event: {event_data}")

            incident_id = event_data.get("incident_id")

            # TODO: Update resources back to available status
            logger.info(f"Incident resolved: incident_id={incident_id}")

        except Exception as e:
            logger.error(f"Error handling incident.resolved event: {e}")

    # ========================================================================
    # DOCUMENT SERVICE EVENTS
    # ========================================================================

    async def handle_document_approved(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle document approved event from Document Service

        May trigger policy updates or references
        """
        try:
            logger.info(f"Received document.approved event: {event_data}")

            document_id = event_data.get("document_id")
            document_type = event_data.get("document_type")

            # TODO: Link approved documents to policies if relevant
            logger.info(f"Document approved: document_id={document_id}, type={document_type}")

        except Exception as e:
            logger.error(f"Error handling document.approved event: {e}")

    # ========================================================================
    # SUBSCRIPTION SETUP
    # ========================================================================

    async def subscribe_to_events(self):
        """
        Subscribe to all relevant events from other services
        """
        if not self.eventbus:
            await self.init()

        try:
            # Learning Service events
            await self.eventbus.subscribe(
                "learning.training.completed",
                self.handle_training_completed
            )
            await self.eventbus.subscribe(
                "learning.certification.issued",
                self.handle_certification_issued
            )

            # Exercise Service events
            await self.eventbus.subscribe(
                "exercise.completed",
                self.handle_exercise_completed
            )
            await self.eventbus.subscribe(
                "exercise.gap_identified",
                self.handle_gap_identified
            )

            # Risk Service events
            await self.eventbus.subscribe(
                "risk.identified",
                self.handle_risk_identified
            )

            # Incident Service events
            await self.eventbus.subscribe(
                "incident.declared",
                self.handle_incident_declared
            )
            await self.eventbus.subscribe(
                "incident.resolved",
                self.handle_incident_resolved
            )

            # Document Service events
            await self.eventbus.subscribe(
                "document.approved",
                self.handle_document_approved
            )

            logger.info("Successfully subscribed to all governance events")

        except Exception as e:
            logger.error(f"Failed to subscribe to events: {e}")


# Global subscriber instance
_subscriber: GovernanceEventSubscriber = None


def get_subscriber() -> GovernanceEventSubscriber:
    """Get global subscriber instance"""
    global _subscriber
    if _subscriber is None:
        _subscriber = GovernanceEventSubscriber()
    return _subscriber


async def init_subscribers():
    """Initialize and start event subscriptions"""
    subscriber = get_subscriber()
    await subscriber.init()
    await subscriber.subscribe_to_events()
