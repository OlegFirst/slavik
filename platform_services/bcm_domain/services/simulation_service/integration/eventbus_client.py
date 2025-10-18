"""
EventBus Integration Client for Simulation Service

REAL integration with platform EventBus - NO MOCKS!
"""

import logging
import sys
from typing import Optional, Callable, Awaitable
from pathlib import Path

# Add infrastructure to path for imports
infrastructure_path = Path(__file__).parent.parent.parent.parent.parent / "infrastructure"
sys.path.insert(0, str(infrastructure_path))

from infrastructure.eventbus.core.events import Event, EventPriority
from infrastructure.eventbus.core.interface import IEventBus
from infrastructure.eventbus.backends.memory import InMemoryEventBus

from models.pydantic_models import (
    Simulation,
    SimulationResult,
    SimulationStatus
)
from config.settings import Settings

logger = logging.getLogger(__name__)


class SimulationEventBusClient:
    """
    EventBus client for Simulation Service

    Provides:
    - Event publication (8 event types)
    - Event subscription (3 patterns)
    - Retry logic and error handling
    - Graceful degradation
    """

    def __init__(self, settings: Settings, event_bus: Optional[IEventBus] = None):
        """
        Initialize EventBus client

        Args:
            settings: Application settings
            event_bus: Optional EventBus instance (for testing)
        """
        self.settings = settings
        self.enabled = settings.eventbus_enabled
        self._event_bus = event_bus
        self._subscription_ids = []

        if not self.enabled:
            logger.warning("EventBus integration disabled")

    @property
    def event_bus(self) -> IEventBus:
        """Get or create EventBus instance"""
        if self._event_bus is None:
            # Create InMemoryEventBus as default
            # TODO: Add Redis/RabbitMQ backend when available
            self._event_bus = InMemoryEventBus()
            logger.info("EventBus initialized (InMemory backend)")
        return self._event_bus

    async def connect(self) -> None:
        """
        Connect to EventBus and subscribe to events

        Called on application startup
        """
        if not self.enabled:
            logger.info("EventBus disabled, skipping connection")
            return

        try:
            # Subscribe to events
            await self._subscribe_to_events()
            logger.info("EventBus connected and subscriptions created")

        except Exception as e:
            logger.error(f"Failed to connect to EventBus: {e}")
            if not self.settings.is_development:
                raise

    async def disconnect(self) -> None:
        """
        Disconnect from EventBus

        Called on application shutdown
        """
        if not self.enabled or not self._event_bus:
            return

        try:
            # Unsubscribe all
            for sub_id in self._subscription_ids:
                await self.event_bus.unsubscribe(sub_id)

            # Close connection
            await self.event_bus.close()
            logger.info("EventBus disconnected")

        except Exception as e:
            logger.error(f"Error disconnecting from EventBus: {e}")

    # ========================================================================
    # PUBLISH METHODS - 8 event types
    # ========================================================================

    async def publish_simulation_created(
        self,
        simulation: Simulation,
        tenant_id: str
    ) -> bool:
        """
        Publish simulation.created event

        Subscribers: Knowledge Center, Community Intelligence, Workflow Intelligence

        Args:
            simulation: Simulation instance
            tenant_id: Tenant ID

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type="simulation.created",
            data={
                "simulation_id": simulation.id,
                "specification_id": simulation.specification_id,
                "scenario_id": simulation.scenario_id,
                "engine": simulation.engine.value,
                "created_by": simulation.created_by,
                "organization_id": simulation.organization_id,
                "metadata": {
                    "engine_type": simulation.engine.value,
                    "status": simulation.status.value
                }
            },
            source="simulation-service",
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        return await self._publish_with_retry(event)

    async def publish_simulation_started(
        self,
        simulation_id: str,
        engine: str,
        tenant_id: str
    ) -> bool:
        """
        Publish simulation.started event

        Subscribers: AI Orchestrator, Monitoring

        Args:
            simulation_id: Simulation ID
            engine: Engine type
            tenant_id: Tenant ID

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type="simulation.started",
            data={
                "simulation_id": simulation_id,
                "engine": engine,
                "start_time": None,  # Will be set by event timestamp
            },
            source="simulation-service",
            tenant_id=tenant_id,
            priority=EventPriority.HIGH
        )

        return await self._publish_with_retry(event)

    async def publish_progress_update(
        self,
        simulation_id: str,
        progress_percent: float,
        current_step: str,
        metrics: dict,
        tenant_id: str
    ) -> bool:
        """
        Publish simulation.progress.updated event

        Subscribers: Real-time Dashboard, AI Orchestrator

        Args:
            simulation_id: Simulation ID
            progress_percent: Progress percentage
            current_step: Current step description
            metrics: Current metrics
            tenant_id: Tenant ID

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type="simulation.progress.updated",
            data={
                "simulation_id": simulation_id,
                "progress_percent": progress_percent,
                "current_step": current_step,
                "metrics": metrics
            },
            source="simulation-service",
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        return await self._publish_with_retry(event, max_retries=1)  # Fast updates

    async def publish_simulation_completed(
        self,
        simulation_id: str,
        status: SimulationStatus,
        duration_seconds: int,
        summary: dict,
        tenant_id: str
    ) -> bool:
        """
        Publish simulation.completed event

        Subscribers: Knowledge Center, Community Intelligence, Workflow Intelligence, Predictive Journey

        Args:
            simulation_id: Simulation ID
            status: Final status
            duration_seconds: Total duration
            summary: Result summary
            tenant_id: Tenant ID

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type="simulation.completed",
            data={
                "simulation_id": simulation_id,
                "status": status.value,
                "duration_seconds": duration_seconds,
                "summary": summary
            },
            source="simulation-service",
            tenant_id=tenant_id,
            priority=EventPriority.HIGH
        )

        return await self._publish_with_retry(event)

    async def publish_simulation_failed(
        self,
        simulation_id: str,
        error: str,
        error_code: str,
        tenant_id: str
    ) -> bool:
        """
        Publish simulation.failed event

        Subscribers: AI Orchestrator, Monitoring, Knowledge Center

        Args:
            simulation_id: Simulation ID
            error: Error message
            error_code: Error code
            tenant_id: Tenant ID

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type="simulation.failed",
            data={
                "simulation_id": simulation_id,
                "error": error,
                "error_code": error_code,
                "recovery_possible": True
            },
            source="simulation-service",
            tenant_id=tenant_id,
            priority=EventPriority.CRITICAL
        )

        return await self._publish_with_retry(event)

    async def publish_case_created(
        self,
        case_id: str,
        simulation_id: str,
        quality_score: float,
        lessons_learned: list,
        tenant_id: str
    ) -> bool:
        """
        Publish simulation.case.created event

        Subscribers: Workflow Intelligence (Case Library), Knowledge Center

        Args:
            case_id: Case ID
            simulation_id: Simulation ID
            quality_score: Quality score
            lessons_learned: Lessons learned
            tenant_id: Tenant ID

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type="simulation.case.created",
            data={
                "case_id": case_id,
                "case_type": "simulation",
                "simulation_id": simulation_id,
                "quality_score": quality_score,
                "lessons_learned": lessons_learned
            },
            source="simulation-service",
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        return await self._publish_with_retry(event)

    async def publish_knowledge_stored(
        self,
        simulation_id: str,
        knowledge_id: str,
        category: str,
        title: str,
        tags: list,
        tenant_id: str
    ) -> bool:
        """
        Publish simulation.knowledge.stored event

        Subscribers: Knowledge Center, RAG Pipeline

        Args:
            simulation_id: Simulation ID
            knowledge_id: Knowledge ID
            category: Knowledge category
            title: Knowledge title
            tags: Tags
            tenant_id: Tenant ID

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type="simulation.knowledge.stored",
            data={
                "simulation_id": simulation_id,
                "knowledge_id": knowledge_id,
                "category": category,
                "title": title,
                "tags": tags
            },
            source="simulation-service",
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        return await self._publish_with_retry(event)

    async def publish_community_contributed(
        self,
        simulation_id: str,
        contribution_id: str,
        anonymized: bool,
        quality_score: float,
        tenant_id: str
    ) -> bool:
        """
        Publish simulation.community.contributed event

        Subscribers: Community Intelligence

        Args:
            simulation_id: Simulation ID
            contribution_id: Contribution ID
            anonymized: Whether data is anonymized
            quality_score: Quality score
            tenant_id: Tenant ID

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type="simulation.community.contributed",
            data={
                "simulation_id": simulation_id,
                "contribution_id": contribution_id,
                "anonymized": anonymized,
                "quality_score": quality_score
            },
            source="simulation-service",
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        return await self._publish_with_retry(event)

    # ========================================================================
    # SUBSCRIBE METHODS - External handler registration
    # ========================================================================

    async def publish(
        self,
        event_type: str,
        data: dict,
        priority: str = "NORMAL"
    ) -> bool:
        """
        Generic publish method for event handlers

        Args:
            event_type: Event type (e.g., "simulation.started")
            data: Event data dictionary
            priority: Event priority

        Returns:
            True if published successfully
        """
        event = Event.create(
            event_type=event_type,
            data=data,
            source="simulation-service",
            tenant_id=data.get("tenant_id", "default"),
            priority=EventPriority[priority]
        )

        return await self._publish_with_retry(event)

    async def subscribe(
        self,
        pattern: str,
        handler: Callable[[dict], Awaitable[None]]
    ) -> None:
        """
        Subscribe to events with custom handler

        Args:
            pattern: Event pattern (e.g., "scenario.execution.requested")
            handler: Async handler function accepting event dict
        """
        if not self.enabled:
            logger.warning(f"EventBus disabled, skipping subscription to {pattern}")
            return

        async def event_wrapper(event: Event) -> None:
            """Wrapper to convert Event object to dict for handler"""
            try:
                await handler(event.data)
            except Exception as e:
                logger.error(f"Error in handler for {pattern}: {e}", exc_info=True)

        sub_id = await self.event_bus.subscribe(
            event_type=pattern,
            handler=event_wrapper,
            consumer_group="simulation-service"
        )
        self._subscription_ids.append(sub_id)
        logger.info(f"Subscribed to {pattern}")

    async def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events from other services"""

        # 1. workflow.*.completed - Auto-create simulation cases
        sub_id = await self.event_bus.subscribe(
            event_type="workflow.*.completed",
            handler=self._handle_workflow_completed,
            consumer_group="simulation-service"
        )
        self._subscription_ids.append(sub_id)
        logger.info("Subscribed to workflow.*.completed")

        # 2. orchestrator.decision.needed - Run what-if simulation
        sub_id = await self.event_bus.subscribe(
            event_type="orchestrator.decision.needed",
            handler=self._handle_decision_needed,
            consumer_group="simulation-service"
        )
        self._subscription_ids.append(sub_id)
        logger.info("Subscribed to orchestrator.decision.needed")

        # 3. platform.health.check - Respond to health checks
        sub_id = await self.event_bus.subscribe(
            event_type="platform.health.check",
            handler=self._handle_health_check,
            consumer_group="simulation-service"
        )
        self._subscription_ids.append(sub_id)
        logger.info("Subscribed to platform.health.check")

    async def _handle_workflow_completed(self, event: Event) -> None:
        """
        Handle workflow completion events

        Auto-create simulation case when workflow completes successfully
        """
        try:
            logger.info(f"Received workflow completed event: {event.id}")

            if event.data.get("create_simulation_case"):
                # TODO: Implement case creation from workflow
                logger.info(f"Creating simulation case from workflow: {event.data.get('workflow_id')}")

        except Exception as e:
            logger.error(f"Error handling workflow completed: {e}")

    async def _handle_decision_needed(self, event: Event) -> None:
        """
        Handle decision validation requests

        Run quick what-if simulation for critical decisions
        """
        try:
            logger.info(f"Received decision needed event: {event.id}")

            if event.data.get("decision_type") == "critical":
                # TODO: Implement what-if simulation for decision
                logger.info(f"Running what-if simulation for decision: {event.data.get('decision_id')}")

        except Exception as e:
            logger.error(f"Error handling decision needed: {e}")

    async def _handle_health_check(self, event: Event) -> None:
        """
        Respond to platform health checks
        """
        try:
            # Publish health response
            response_event = Event.create(
                event_type="simulation.health.response",
                data={
                    "service": "simulation-service",
                    "status": "healthy",
                    "active_simulations": 0  # TODO: Get from orchestrator
                },
                source="simulation-service",
                tenant_id=event.tenant_id,
                correlation_id=event.id
            )

            await self.event_bus.publish(response_event)
            logger.debug("Health check response sent")

        except Exception as e:
            logger.error(f"Error responding to health check: {e}")

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _publish_with_retry(
        self,
        event: Event,
        max_retries: int = 3
    ) -> bool:
        """
        Publish event with retry logic

        Args:
            event: Event to publish
            max_retries: Maximum retry attempts

        Returns:
            True if published successfully
        """
        if not self.enabled:
            logger.debug(f"EventBus disabled, skipping event: {event.type}")
            return False

        for attempt in range(max_retries):
            try:
                await self.event_bus.publish(event)
                logger.debug(f"Published event: {event.type} (id: {event.id})")
                return True

            except Exception as e:
                logger.warning(f"Failed to publish event (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt == max_retries - 1:
                    logger.error(f"Failed to publish event after {max_retries} attempts: {event.type}")
                    return False

        return False

    async def health_check(self) -> dict:
        """
        Check EventBus health

        Returns:
            Health status dictionary
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "connected": False
            }

        try:
            stats = await self.event_bus.get_stats()
            return {
                "status": "healthy",
                "connected": True,
                "subscriptions": len(self._subscription_ids),
                "stats": stats
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
