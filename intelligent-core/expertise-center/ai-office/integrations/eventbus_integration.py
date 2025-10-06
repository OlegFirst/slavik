"""
EventBus Integration for AI Intelligence Layer

Subscribes to BCM events and publishes AI insights
"""

import logging
import httpx
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class AIEventBusIntegration:
    """
    EventBus integration for AI Intelligence Layer

    Features:
    - Subscribe to BCM module events (risk.*, bia.*, plan.*, incident.*, etc.)
    - Publish AI colleague responses and insights
    - Trigger cross-colleague workflows based on events
    - Learn from all BCM activities
    """

    def __init__(
        self,
        eventbus_url: str = "http://localhost:8001",
        colleague_coordinator=None
    ):
        """
        Initialize EventBus integration

        Args:
            eventbus_url: URL of EventBus service
            colleague_coordinator: ColleagueCoordinator instance for handling events
        """
        self.eventbus_url = eventbus_url
        self.coordinator = colleague_coordinator
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.subscriptions: Dict[str, Callable] = {}
        self.event_stats = {
            "total_received": 0,
            "total_published": 0,
            "by_type": {},
            "ai_responses": 0,
            "workflows_triggered": 0
        }

        logger.info(f"AIEventBusIntegration initialized (EventBus: {eventbus_url})")

    async def connect(self):
        """Connect to EventBus and register subscriptions"""
        try:
            # Test EventBus connection
            response = await self.http_client.get(f"{self.eventbus_url}/health")
            if response.status_code == 200:
                logger.info(f"✅ Connected to EventBus at {self.eventbus_url}")
            else:
                logger.warning(f"⚠️  EventBus responded with status {response.status_code}")

            # Subscribe to BCM events
            await self._register_subscriptions()

        except Exception as e:
            logger.error(f"Failed to connect to EventBus: {e}")

    async def _register_subscriptions(self):
        """Register event subscriptions for BCM modules"""

        # Define event patterns we're interested in
        event_patterns = {
            "risk.created": self._handle_risk_event,
            "risk.updated": self._handle_risk_event,
            "bia.analysis_complete": self._handle_bia_event,
            "plan.created": self._handle_plan_event,
            "incident.declared": self._handle_incident_event,
            "exercise.scheduled": self._handle_exercise_event,
            "project.health_critical": self._handle_project_event,
            "compliance.gap_identified": self._handle_compliance_event
        }

        for event_pattern, handler in event_patterns.items():
            self.subscriptions[event_pattern] = handler
            logger.info(f"Registered subscription: {event_pattern}")

        logger.info(f"✅ Registered {len(self.subscriptions)} event subscriptions")

    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        tenant_id: str = "demo",
        source: str = "ai-intelligence"
    ) -> bool:
        """
        Publish event to EventBus

        Args:
            event_type: Type of event (e.g., "ai.insight", "ai.colleague.response")
            data: Event data
            tenant_id: Tenant identifier
            source: Source of event

        Returns:
            True if published successfully
        """
        try:
            event_payload = {
                "type": event_type,
                "data": data,
                "tenant_id": tenant_id,
                "source": source,
                "timestamp": datetime.utcnow().isoformat()
            }

            response = await self.http_client.post(
                f"{self.eventbus_url}/api/events/publish",
                json=event_payload
            )

            if response.status_code in [200, 201]:
                self.event_stats["total_published"] += 1
                logger.debug(f"Published event: {event_type}")
                return True
            else:
                logger.warning(f"Failed to publish event: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False

    async def _handle_risk_event(self, event: Dict[str, Any]):
        """
        Handle risk-related events

        Triggers Risk Analyst AI for analysis
        """
        self.event_stats["total_received"] += 1
        self._update_event_type_stats(event.get("type"))

        logger.info(f"Handling risk event: {event.get('type')}")

        if not self.coordinator:
            return

        try:
            # Extract risk data
            risk_data = event.get("data", {})
            risk_description = risk_data.get("description", "Unknown risk")
            tenant_id = event.get("tenant_id", "demo")

            # Auto-route to Risk Analyst AI
            query = f"Analyze this risk event: {risk_description}. Provide FAIR assessment and treatment recommendations."

            from coordinator import ColleagueType
            result = await self.coordinator.route_query(
                query=query,
                tenant_id=tenant_id,
                colleague_type=ColleagueType.RISK_ANALYST
            )

            # Publish AI response as event
            await self.publish_event(
                event_type="ai.risk_analysis_complete",
                data={
                    "original_event": event.get("type"),
                    "risk_id": risk_data.get("id"),
                    "ai_analysis": result.get("answer"),
                    "confidence": result.get("confidence"),
                    "suggested_actions": result.get("actions", [])
                },
                tenant_id=tenant_id
            )

            self.event_stats["ai_responses"] += 1

        except Exception as e:
            logger.error(f"Error handling risk event: {e}")

    async def _handle_bia_event(self, event: Dict[str, Any]):
        """Handle BIA-related events"""
        self.event_stats["total_received"] += 1
        self._update_event_type_stats(event.get("type"))

        logger.info(f"Handling BIA event: {event.get('type')}")

        if not self.coordinator:
            return

        try:
            bia_data = event.get("data", {})
            tenant_id = event.get("tenant_id", "demo")

            # Suggest next workflow: BIA → Plans
            await self.publish_event(
                event_type="ai.workflow_suggestion",
                data={
                    "suggested_workflow": "bia_to_plans",
                    "reason": "BIA analysis complete, recommend generating recovery plans",
                    "next_colleague": "plan_generator",
                    "bia_data": bia_data
                },
                tenant_id=tenant_id
            )

            self.event_stats["workflows_triggered"] += 1

        except Exception as e:
            logger.error(f"Error handling BIA event: {e}")

    async def _handle_plan_event(self, event: Dict[str, Any]):
        """Handle plan-related events"""
        self.event_stats["total_received"] += 1
        self._update_event_type_stats(event.get("type"))
        logger.info(f"Handling plan event: {event.get('type')}")

    async def _handle_incident_event(self, event: Dict[str, Any]):
        """Handle incident-related events - route to Incident Advisor AI"""
        self.event_stats["total_received"] += 1
        self._update_event_type_stats(event.get("type"))

        logger.info(f"Handling incident event: {event.get('type')}")

        if not self.coordinator:
            return

        try:
            incident_data = event.get("data", {})
            tenant_id = event.get("tenant_id", "demo")

            # Auto-route to Incident Advisor AI for immediate guidance
            from coordinator import ColleagueType
            query = f"Incident declared: {incident_data.get('description', 'Unknown incident')}. Provide immediate response guidance."

            result = await self.coordinator.route_query(
                query=query,
                tenant_id=tenant_id,
                colleague_type=ColleagueType.INCIDENT_ADVISOR
            )

            await self.publish_event(
                event_type="ai.incident_guidance",
                data={
                    "incident_id": incident_data.get("id"),
                    "ai_guidance": result.get("answer"),
                    "priority_actions": result.get("actions", [])
                },
                tenant_id=tenant_id
            )

            self.event_stats["ai_responses"] += 1

        except Exception as e:
            logger.error(f"Error handling incident event: {e}")

    async def _handle_exercise_event(self, event: Dict[str, Any]):
        """Handle exercise-related events"""
        self.event_stats["total_received"] += 1
        self._update_event_type_stats(event.get("type"))
        logger.info(f"Handling exercise event: {event.get('type')}")

    async def _handle_project_event(self, event: Dict[str, Any]):
        """Handle project-related events - route to Project Manager AI"""
        self.event_stats["total_received"] += 1
        self._update_event_type_stats(event.get("type"))
        logger.info(f"Handling project event: {event.get('type')}")

    async def _handle_compliance_event(self, event: Dict[str, Any]):
        """Handle compliance-related events - route to Compliance Copilot"""
        self.event_stats["total_received"] += 1
        self._update_event_type_stats(event.get("type"))
        logger.info(f"Handling compliance event: {event.get('type')}")

    def _update_event_type_stats(self, event_type: str):
        """Update statistics for event type"""
        if event_type not in self.event_stats["by_type"]:
            self.event_stats["by_type"][event_type] = 0
        self.event_stats["by_type"][event_type] += 1

    async def start_listening(self):
        """
        Start listening for events from EventBus

        Note: This would typically use WebSocket or SSE for real-time events
        For now, this is a placeholder for polling-based approach
        """
        logger.info("EventBus listener started (placeholder - implement WebSocket/SSE for real-time)")
        # TODO: Implement WebSocket or Server-Sent Events (SSE) subscription
        # Example: await self._subscribe_websocket()

    def get_stats(self) -> Dict[str, Any]:
        """Get EventBus integration statistics"""
        return {
            "eventbus_url": self.eventbus_url,
            "subscriptions": list(self.subscriptions.keys()),
            "stats": self.event_stats,
            "coordinator_available": self.coordinator is not None
        }

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
        logger.info("EventBus integration closed")
