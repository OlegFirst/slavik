"""
Planning Service Event Subscriptions Setup
===========================================

Setup event choreography subscriptions for Planning service.
"""

import logging
from event_handlers import get_planning_event_handlers

logger = logging.getLogger(__name__)


async def setup_event_subscriptions(eventbus):
    """
    Setup event subscriptions for Planning service choreography.

    Planning Service SUBSCRIBES TO:
    - bia.assessment.completed: Analyze recovery requirements
    - bia.critical.process.identified: Create priority BC plan
    - risk.assessment.completed: Auto-create BC plans for high risks
    - risk.severity.changed: Update plan priority
    - risk.mitigation.proposed: Integrate into BC plans

    Planning Service PUBLISHES:
    - plan.created
    - plan.updated
    - plan.approved
    - plan.activated
    - plan.tested
    """
    try:
        if not eventbus:
            logger.warning("EventBus not available - skipping event subscriptions")
            return

        # Get Planning event handlers
        handlers = get_planning_event_handlers(eventbus)

        # Subscribe to BIA events
        await eventbus.subscribe('bia.assessment.completed', handlers.on_bia_completed)
        logger.info(" Subscribed to: bia.assessment.completed")

        await eventbus.subscribe('bia.critical.process.identified', handlers.on_critical_process_identified)
        logger.info(" Subscribed to: bia.critical.process.identified")

        # Subscribe to Risk events
        await eventbus.subscribe('risk.assessment.completed', handlers.on_risk_assessment_completed)
        logger.info(" Subscribed to: risk.assessment.completed")

        await eventbus.subscribe('risk.severity.changed', handlers.on_risk_severity_changed)
        logger.info(" Subscribed to: risk.severity.changed")

        await eventbus.subscribe('risk.mitigation.proposed', handlers.on_risk_mitigation_proposed)
        logger.info(" Subscribed to: risk.mitigation.proposed")

        logger.info(" Planning event choreography configured")
        logger.info(" Listening for: BIA & Risk events")
        logger.info(" Ready to publish: plan.created, plan.activated, etc.")

    except Exception as e:
        logger.error(f"Failed to setup event subscriptions: {e}", exc_info=True)
