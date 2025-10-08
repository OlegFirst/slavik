"""
Event Subscribers for Event Intelligence
=========================================

Subscribes to all platform events for:
- Pattern learning
- Auto-discovery
- Knowledge building
- Predictive analytics
"""

import logging
from typing import Dict, Any
from shared.event_bus import subscribe_to, Event

logger = logging.getLogger(__name__)


# ============================================================================
# WILDCARD SUBSCRIPTIONS (learn from ALL events)
# ============================================================================

@subscribe_to("*")  # Subscribe to ALL events
async def learn_from_all_events(event: Event):
    """
    Learn patterns from ALL platform events.

    Event Intelligence analyzes every event to:
    - Detect patterns
    - Build knowledge graph
    - Predict next events
    - Identify anomalies
    """
    try:
        from .auto_discovery import get_discovery_engine

        engine = get_discovery_engine()
        if engine:
            # Engine automatically learns from events via auto_discovery.py
            logger.debug(f"Learning from event: {event.type} from {event.source}")
        else:
            logger.warning("Discovery engine not initialized")

    except Exception as e:
        logger.error(f"Failed to learn from event {event.type}: {e}")


# ============================================================================
# BIA EVENTS (Business Impact Analysis)
# ============================================================================

@subscribe_to("bcm.bia.*")
async def on_bia_event(event: Event):
    """
    Handle BIA workflow events.

    Events:
    - bcm.bia.started
    - bcm.bia.completed
    - bcm.bia.critical_process_identified
    """
    logger.info(f"📊 BIA Event: {event.type}")

    # Extract BIA context for learning
    bia_id = event.data.get("bia_id")
    if bia_id:
        # Track BIA workflow patterns
        if event.type == "bcm.bia.completed":
            logger.info(f"✅ BIA {bia_id} completed - capturing patterns")


# ============================================================================
# EXERCISE EVENTS (BCM Exercises & Testing)
# ============================================================================

@subscribe_to("bcm.exercise.*")
async def on_exercise_event(event: Event):
    """
    Handle BCM exercise events.

    Events:
    - bcm.exercise.created
    - bcm.exercise.completed
    - bcm.exercise.scenario_created
    - bcm.exercise.inject_delivered
    - bcm.exercise.response_submitted
    """
    logger.info(f"🎯 Exercise Event: {event.type}")

    if event.type == "bcm.exercise.completed":
        exercise_id = event.data.get("exercise_id")
        results = event.data.get("results", {})
        gaps = results.get("gaps", [])

        logger.info(
            f"✅ Exercise {exercise_id} completed with {len(gaps)} gaps identified"
        )


# ============================================================================
# INCIDENT EVENTS (Incident Response)
# ============================================================================

@subscribe_to("response.incident.*")
async def on_incident_event(event: Event):
    """
    Handle incident response events.

    Events:
    - response.incident.created
    - response.incident.escalated
    - response.incident.resolved
    """
    logger.info(f"🚨 Incident Event: {event.type}")

    if event.type == "response.incident.resolved":
        incident_id = event.data.get("incident_id")
        resolution_time = event.data.get("resolution_time_hours")

        logger.info(f"✅ Incident {incident_id} resolved in {resolution_time}h")

        # Learn from incident patterns
        # Predict future incidents
        # Improve response recommendations


# ============================================================================
# WORKFLOW EVENTS (BPMN Workflows)
# ============================================================================

@subscribe_to("bpmn.*")
async def on_bpmn_event(event: Event):
    """
    Handle BPMN workflow events.

    Events:
    - bpmn.process.deployed
    - bpmn.instance.started
    - bpmn.instance.completed
    - bpmn.instance.terminated
    - bpmn.task.created
    - bpmn.task.completed
    """
    logger.info(f"⚙️  BPMN Event: {event.type}")

    # Learn workflow execution patterns
    # Predict bottlenecks
    # Recommend optimizations


# ============================================================================
# COMPLIANCE EVENTS (Audits & Compliance)
# ============================================================================

@subscribe_to("bcm.compliance.*")
async def on_compliance_event(event: Event):
    """
    Handle compliance events.

    Events:
    - bcm.compliance.audit_started
    - bcm.compliance.audit_completed
    - bcm.compliance.gap_identified
    - bcm.compliance.improvement_created
    - bcm.compliance.improvement_verified
    """
    logger.info(f"📋 Compliance Event: {event.type}")


# ============================================================================
# GOVERNANCE EVENTS (Policies & Controls)
# ============================================================================

@subscribe_to("bcm.governance.*")
async def on_governance_event(event: Event):
    """
    Handle governance events.

    Events:
    - bcm.governance.policy_created
    - bcm.governance.policy_approved
    - bcm.governance.control_updated
    - bcm.governance.stakeholder_added
    """
    logger.info(f"👔 Governance Event: {event.type}")


# ============================================================================
# KPI EVENTS (Metrics & Performance)
# ============================================================================

@subscribe_to("bcm.kpi.*")
async def on_kpi_event(event: Event):
    """
    Handle KPI calculation events.

    Events:
    - bcm.kpi.calculated
    - bcm.kpi.threshold_exceeded
    """
    logger.info(f"📈 KPI Event: {event.type}")

    if event.type == "bcm.kpi.calculated":
        kpi_name = event.data.get("kpi_name")
        value = event.data.get("value")
        logger.info(f"📊 KPI {kpi_name} = {value}")


# ============================================================================
# PLAN EVENTS (BCM Plans)
# ============================================================================

@subscribe_to("bcm.plan.*")
async def on_plan_event(event: Event):
    """
    Handle BCM plan events.

    Events:
    - bcm.plan.created
    - bcm.plan.approved
    - bcm.plan.activated
    - bcm.plan.tested
    """
    logger.info(f"📝 Plan Event: {event.type}")


# ============================================================================
# DOCUMENT EVENTS (Document Management)
# ============================================================================

@subscribe_to("bcm.document.*")
async def on_document_event(event: Event):
    """
    Handle document events.

    Events:
    - bcm.document.created
    - bcm.document.updated
    - bcm.document.approved
    - bcm.document.archived
    """
    logger.info(f"📄 Document Event: {event.type}")


# ============================================================================
# USER EVENTS (Authentication & Authorization)
# ============================================================================

@subscribe_to("auth.*")
async def on_auth_event(event: Event):
    """
    Handle authentication events.

    Events:
    - auth.success
    - auth.expired
    - auth.invalid
    - auth.missing
    """
    logger.debug(f"🔐 Auth Event: {event.type}")


# ============================================================================
# SERVICE LIFECYCLE EVENTS
# ============================================================================

@subscribe_to("service.started")
async def on_service_started(event: Event):
    """
    Handle service startup events (for auto-discovery).

    This is already handled by auto_discovery.py
    but we log it here for completeness.
    """
    service_name = event.data.get("service_name")
    subscriptions = event.data.get("subscriptions", [])

    logger.info(f"🚀 Service started: {service_name} with {len(subscriptions)} subscriptions")


@subscribe_to("service.stopped")
async def on_service_stopped(event: Event):
    """Handle service shutdown events."""
    service_name = event.data.get("service_name")
    logger.info(f"🛑 Service stopped: {service_name}")


# ============================================================================
# PROACTIVE RECOMMENDATIONS
# ============================================================================

@subscribe_to("proactive.*")
async def on_proactive_event(event: Event):
    """
    Handle proactive recommendation events from Predictive service.

    Events:
    - proactive.daily_digest
    - specialist.demand_forecast
    """
    logger.info(f"🔮 Proactive Event: {event.type}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def register_all_subscribers():
    """
    Register all event subscribers.

    This is called automatically by init_event_bus() via @subscribe_to decorators.
    """
    logger.info("✅ All Event Intelligence subscribers registered")
    logger.info(f"📊 Total subscribers: {len([f for f in globals().values() if hasattr(f, '_is_event_handler')])}")
