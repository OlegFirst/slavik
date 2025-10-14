"""
Risk Service Event Subscriptions Setup
=======================================

Setup event choreography subscriptions for Risk service.
"""

import logging
from event_handlers import get_risk_event_handlers

logger = logging.getLogger(__name__)


async def setup_event_subscriptions(eventbus):
    """
    Setup event subscriptions for Risk service choreography.

    Risk Service SUBSCRIBES TO:
    - bia.assessment.completed: Auto-generate risk suggestions
    - bia.criticality.changed: Re-assess related risks
    - bia.critical.process.identified: Create high-priority risk assessment

    Risk Service PUBLISHES:
    - risk.suggestion.generated
    - risk.assessment.created
    - risk.assessment.completed
    - risk.severity.changed
    """
    try:
        if not eventbus:
            logger.warning("EventBus not available - skipping event subscriptions")
            return

        # Get Risk event handlers
        handlers = get_risk_event_handlers(eventbus)

        # Subscribe to BIA events
        await eventbus.subscribe('bia.assessment.completed', handlers.on_bia_completed)
        logger.info("📥 Subscribed to: bia.assessment.completed")

        await eventbus.subscribe('bia.criticality.changed', handlers.on_criticality_changed)
        logger.info("📥 Subscribed to: bia.criticality.changed")

        await eventbus.subscribe('bia.critical.process.identified', handlers.on_critical_process_identified)
        logger.info("📥 Subscribed to: bia.critical.process.identified")

        logger.info("✅ Risk event choreography configured")
        logger.info("📥 Listening for: BIA events")
        logger.info("📤 Ready to publish: risk.assessment.completed, risk.severity.changed, etc.")

    except Exception as e:
        logger.error(f"Failed to setup event subscriptions: {e}", exc_info=True)
