"""
EventBus Client for Scenario Intelligence

Provides EventBus integration for:
- Publishing scenario generation/execution events
- Subscribing to service catalog updates
- Triggering auto-regeneration
- Enabling monitoring through MIO Manager
"""

import logging
import sys
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
import asyncio

# Add infrastructure to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from infrastructure.eventbus import create_eventbus, Event, EventPriority, IEventBus

# Import our event definitions
from events.scenario_events import (
    ScenarioGeneratedEvent,
    ScenarioUpdatedEvent,
    ScenarioExecutedEvent,
    ScenarioRegenerationTriggeredEvent,
    ScenarioRegenerationCompletedEvent,
    ScenarioDeprecatedEvent,
    ScenarioPatternDetectedEvent,
    ScenarioEventTypes,
)

logger = logging.getLogger(__name__)


class ScenarioEventBusClient:
    """
    EventBus Client for Scenario Intelligence

    Handles:
    - Publishing scenario lifecycle events
    - Subscribing to service catalog changes
    - Auto-regeneration coordination
    - MIO Manager integration
    """

    def __init__(
        self,
        backend: str = 'memory',
        eventbus_url: Optional[str] = None,
        redis_url: Optional[str] = None
    ):
        """
        Initialize EventBus client

        Args:
            backend: EventBus backend ('memory', 'redis', 'rabbitmq')
            eventbus_url: URL for HTTP EventBus (optional)
            redis_url: Redis URL for redis backend (optional)
        """
        self.backend = backend
        self.eventbus_url = eventbus_url or "http://localhost:8070"
        self.redis_url = redis_url or "redis://localhost:6379"
        self.eventbus: Optional[IEventBus] = None
        self._subscriptions: List[str] = []
        self._running = False

    async def initialize(self):
        """Initialize EventBus connection"""
        if not self.eventbus:
            self.eventbus = create_eventbus(self.backend)
            logger.info(f" ScenarioEventBusClient initialized with {self.backend} backend")
            self._running = True

    async def close(self):
        """Close EventBus connection"""
        self._running = False
        if self.eventbus:
            # EventBus cleanup if needed
            logger.info(" ScenarioEventBusClient closed")

    # =========================================================================
    # PUBLISH: Scenario Generation Events
    # =========================================================================

    async def publish_scenario_generated(
        self,
        event_data: ScenarioGeneratedEvent
    ):
        """
        Publish scenario.generated event

        Args:
            event_data: ScenarioGeneratedEvent instance
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type=ScenarioEventTypes.SCENARIO_GENERATED,
            data=event_data.to_dict(),
            source='scenario-intelligence',
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(
            f" Published: scenario.generated "
            f"(level={event_data.level}, count={event_data.count}, trigger={event_data.trigger})"
        )

    async def publish_scenario_updated(
        self,
        event_data: ScenarioUpdatedEvent
    ):
        """
        Publish scenario.updated event

        Args:
            event_data: ScenarioUpdatedEvent instance
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type=ScenarioEventTypes.SCENARIO_UPDATED,
            data=event_data.to_dict(),
            source='scenario-intelligence',
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(
            f" Published: scenario.updated "
            f"(id={event_data.scenario_id}, reason={event_data.reason})"
        )

    async def publish_scenario_executed(
        self,
        event_data: ScenarioExecutedEvent
    ):
        """
        Publish scenario.executed event

        Args:
            event_data: ScenarioExecutedEvent instance
        """
        if not self.eventbus:
            await self.initialize()

        # Use HIGH priority for failed executions
        priority = EventPriority.HIGH if event_data.status == 'failed' else EventPriority.NORMAL

        event = Event.create(
            event_type=ScenarioEventTypes.SCENARIO_EXECUTED,
            data=event_data.to_dict(),
            source='scenario-intelligence',
            priority=priority
        )

        await self.eventbus.publish(event)
        logger.info(
            f" Published: scenario.executed "
            f"(id={event_data.scenario_id}, status={event_data.status}, "
            f"duration={event_data.duration_ms}ms)"
        )

    async def publish_regeneration_triggered(
        self,
        event_data: ScenarioRegenerationTriggeredEvent
    ):
        """
        Publish scenario.regeneration.triggered event

        Args:
            event_data: ScenarioRegenerationTriggeredEvent instance
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type=ScenarioEventTypes.REGENERATION_TRIGGERED,
            data=event_data.to_dict(),
            source='scenario-intelligence',
            priority=EventPriority.HIGH
        )

        await self.eventbus.publish(event)
        logger.info(
            f" Published: scenario.regeneration.triggered "
            f"(id={event_data.regeneration_id}, services={len(event_data.affected_services)})"
        )

    async def publish_regeneration_completed(
        self,
        event_data: ScenarioRegenerationCompletedEvent
    ):
        """
        Publish scenario.regeneration.completed event

        Args:
            event_data: ScenarioRegenerationCompletedEvent instance
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type=ScenarioEventTypes.REGENERATION_COMPLETED,
            data=event_data.to_dict(),
            source='scenario-intelligence',
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(
            f" Published: scenario.regeneration.completed "
            f"(id={event_data.regeneration_id}, status={event_data.status}, "
            f"generated={event_data.scenarios_generated}, updated={event_data.scenarios_updated})"
        )

    async def publish_scenario_deprecated(
        self,
        event_data: ScenarioDeprecatedEvent
    ):
        """
        Publish scenario.deprecated event

        Args:
            event_data: ScenarioDeprecatedEvent instance
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type=ScenarioEventTypes.SCENARIO_DEPRECATED,
            data=event_data.to_dict(),
            source='scenario-intelligence',
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(
            f" Published: scenario.deprecated "
            f"(id={event_data.scenario_id}, reason={event_data.reason})"
        )

    async def publish_pattern_detected(
        self,
        event_data: ScenarioPatternDetectedEvent
    ):
        """
        Publish scenario.pattern.detected event

        Args:
            event_data: ScenarioPatternDetectedEvent instance
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type=ScenarioEventTypes.PATTERN_DETECTED,
            data=event_data.to_dict(),
            source='scenario-intelligence',
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(
            f" Published: scenario.pattern.detected "
            f"(type={event_data.pattern_type}, scenarios={len(event_data.scenario_ids)}, "
            f"confidence={event_data.confidence:.2f})"
        )

    # =========================================================================
    # SUBSCRIBE: Service Catalog Events
    # =========================================================================

    async def subscribe_to_catalog_updates(
        self,
        callback: Callable[[Event], Any]
    ):
        """
        Subscribe to service catalog update events

        Subscribes to:
        - service.catalog.updated
        - service.added
        - service.removed
        - service.updated

        Args:
            callback: Async function to handle events
        """
        if not self.eventbus:
            await self.initialize()

        # Subscribe to all service catalog events
        event_types = [
            ScenarioEventTypes.SERVICE_CATALOG_UPDATED,
            ScenarioEventTypes.SERVICE_ADDED,
            ScenarioEventTypes.SERVICE_REMOVED,
            ScenarioEventTypes.SERVICE_UPDATED,
        ]

        for event_type in event_types:
            await self.eventbus.subscribe(event_type, callback)
            self._subscriptions.append(event_type)
            logger.info(f" Subscribed to: {event_type}")

    async def subscribe_to_service_health(
        self,
        callback: Callable[[Event], Any]
    ):
        """
        Subscribe to service health change events

        Args:
            callback: Async function to handle events
        """
        if not self.eventbus:
            await self.initialize()

        event_type = ScenarioEventTypes.SERVICE_HEALTH_CHANGED
        await self.eventbus.subscribe(event_type, callback)
        self._subscriptions.append(event_type)
        logger.info(f" Subscribed to: {event_type}")

    async def subscribe_to_pattern(
        self,
        pattern: str,
        callback: Callable[[Event], Any]
    ):
        """
        Subscribe to events matching a pattern

        Args:
            pattern: Event type pattern (e.g., "service.*", "scenario.*")
            callback: Async function to handle events
        """
        if not self.eventbus:
            await self.initialize()

        await self.eventbus.subscribe(pattern, callback)
        self._subscriptions.append(pattern)
        logger.info(f" Subscribed to pattern: {pattern}")

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def is_connected(self) -> bool:
        """Check if EventBus is connected"""
        return self.eventbus is not None and self._running

    def get_subscriptions(self) -> List[str]:
        """Get list of active subscriptions"""
        return self._subscriptions.copy()

    async def health_check(self) -> Dict[str, Any]:
        """Health check for EventBus connection"""
        return {
            "connected": self.is_connected(),
            "backend": self.backend,
            "subscriptions": len(self._subscriptions),
            "subscription_list": self._subscriptions
        }


# =========================================================================
# Global Instance (Singleton Pattern)
# =========================================================================

_global_client: Optional[ScenarioEventBusClient] = None


def get_eventbus_client() -> ScenarioEventBusClient:
    """Get or create global EventBus client instance"""
    global _global_client
    if _global_client is None:
        _global_client = ScenarioEventBusClient()
    return _global_client


async def initialize_global_eventbus(
    backend: str = 'memory',
    eventbus_url: Optional[str] = None,
    redis_url: Optional[str] = None
) -> ScenarioEventBusClient:
    """
    Initialize global EventBus client

    Args:
        backend: EventBus backend ('memory', 'redis', 'rabbitmq')
        eventbus_url: URL for HTTP EventBus
        redis_url: Redis URL for redis backend

    Returns:
        Initialized ScenarioEventBusClient
    """
    global _global_client
    _global_client = ScenarioEventBusClient(
        backend=backend,
        eventbus_url=eventbus_url,
        redis_url=redis_url
    )
    await _global_client.initialize()
    logger.info(" Global ScenarioEventBusClient initialized")
    return _global_client
