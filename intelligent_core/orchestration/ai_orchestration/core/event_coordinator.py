"""
Event Coordinator - EventBus coordination and routing
Handles event publishing, subscription, and routing to handlers
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
import asyncio
import json
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Event structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    tenant_id: Optional[str] = None
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'data': self.data,
            'tenant_id': self.tenant_id,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'metadata': self.metadata
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Event':
        """Create Event from dictionary"""
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.utcnow()

        return Event(
            id=data.get('id', str(uuid.uuid4())),
            type=data['type'],
            data=data.get('data', {}),
            tenant_id=data.get('tenant_id'),
            source=data.get('source'),
            timestamp=timestamp,
            correlation_id=data.get('correlation_id'),
            metadata=data.get('metadata', {})
        )


class EventCoordinator:
    """
    EventBus coordination and routing

    Manages:
    - Event publishing to EventBus
    - Event subscription from EventBus
    - Event routing to registered handlers
    - Pattern matching for subscriptions
    """

    def __init__(self):
        self.redis_client = None
        self.http_client = None
        self.eventbus_url = None
        self.handlers: Dict[str, List[Callable]] = {}  # pattern -> [handlers]
        self.subscriptions_active = False
        logger.info("EventCoordinator initialized")

    async def connect(self, redis_client=None, eventbus_url: str = None,
                     http_client=None) -> None:
        """
        Connect to EventBus

        Args:
            redis_client: Redis client for pub/sub
            eventbus_url: EventBus HTTP URL
            http_client: HTTP client instance
        """
        self.redis_client = redis_client
        self.eventbus_url = eventbus_url
        self.http_client = http_client

        if redis_client:
            logger.info("EventCoordinator connected to Redis")
        if eventbus_url:
            logger.info(f"EventCoordinator connected to EventBus at {eventbus_url}")

    async def subscribe(self, event_pattern: str, handler: Callable) -> None:
        """
        Subscribe to event pattern

        Args:
            event_pattern: Event pattern (e.g., "bcm.*", "platform.ready")
            handler: Handler function (async)
        """
        if event_pattern not in self.handlers:
            self.handlers[event_pattern] = []

        self.handlers[event_pattern].append(handler)
        logger.info(f"Subscribed to pattern: {event_pattern}")

        # Start subscription listener if not already running
        if not self.subscriptions_active and self.redis_client:
            asyncio.create_task(self._subscription_listener())

    async def unsubscribe(self, event_pattern: str, handler: Optional[Callable] = None) -> None:
        """
        Unsubscribe from event pattern

        Args:
            event_pattern: Event pattern
            handler: Specific handler to remove (None = remove all)
        """
        if event_pattern in self.handlers:
            if handler:
                # Remove specific handler
                if handler in self.handlers[event_pattern]:
                    self.handlers[event_pattern].remove(handler)
                    logger.info(f"Unsubscribed handler from {event_pattern}")
            else:
                # Remove all handlers for pattern
                del self.handlers[event_pattern]
                logger.info(f"Unsubscribed all handlers from {event_pattern}")

    async def publish(self, event: Dict[str, Any]) -> None:
        """
        Publish event to EventBus

        Args:
            event: Event data (dict or Event object)
        """
        if isinstance(event, Event):
            event_obj = event
        elif isinstance(event, dict):
            event_obj = Event.from_dict(event)
        else:
            raise ValueError("Event must be Event object or dict")

        # Publish via HTTP if EventBus URL available
        if self.http_client and self.eventbus_url:
            try:
                await self.http_client.post(
                    f"{self.eventbus_url}/api/events/publish",
                    json=event_obj.to_dict()
                )
                logger.debug(f"Published event via HTTP: {event_obj.type}")
            except Exception as e:
                logger.error(f"Failed to publish event via HTTP: {e}")

        # Publish via Redis if available
        if self.redis_client:
            try:
                channel = f"bcm.events.{event_obj.type}"
                await self.redis_client.publish(
                    channel,
                    json.dumps(event_obj.to_dict())
                )
                logger.debug(f"Published event via Redis: {event_obj.type}")
            except Exception as e:
                logger.error(f"Failed to publish event via Redis: {e}")

    async def _subscription_listener(self) -> None:
        """
        Listen for events from Redis pub/sub

        Runs in background task
        """
        if not self.redis_client:
            logger.warning("Cannot start subscription listener - Redis not connected")
            return

        self.subscriptions_active = True
        logger.info("Starting event subscription listener")

        try:
            # Subscribe to all BCM events
            pubsub = self.redis_client.pubsub()
            await pubsub.psubscribe("bcm.events.*")

            async for message in pubsub.listen():
                if message['type'] == 'pmessage':
                    try:
                        # Parse event
                        event_data = message['data']
                        if isinstance(event_data, bytes):
                            event_data = event_data.decode('utf-8')

                        event_dict = json.loads(event_data)
                        event = Event.from_dict(event_dict)

                        # Route to handlers
                        await self._route_event(event)

                    except Exception as e:
                        logger.error(f"Error processing event: {e}")

        except Exception as e:
            logger.error(f"Subscription listener error: {e}")
        finally:
            self.subscriptions_active = False
            logger.info("Stopped event subscription listener")

    async def _route_event(self, event: Event) -> None:
        """
        Route event to matching handlers

        Args:
            event: Event to route
        """
        matched_handlers = []

        # Find matching patterns
        for pattern, handlers in self.handlers.items():
            if self._pattern_matches(pattern, event.type):
                matched_handlers.extend(handlers)

        if not matched_handlers:
            logger.debug(f"No handlers for event: {event.type}")
            return

        logger.debug(f"Routing event {event.type} to {len(matched_handlers)} handlers")

        # Execute handlers concurrently
        tasks = []
        for handler in matched_handlers:
            tasks.append(self._safe_execute_handler(handler, event))

        await asyncio.gather(*tasks)

    async def _safe_execute_handler(self, handler: Callable, event: Event) -> None:
        """
        Safely execute handler with error handling

        Args:
            handler: Handler function
            event: Event to pass
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                # Run sync handler in executor
                await asyncio.get_event_loop().run_in_executor(None, handler, event)
        except Exception as e:
            logger.error(f"Handler execution error for {event.type}: {e}")

    def _pattern_matches(self, pattern: str, event_type: str) -> bool:
        """
        Check if pattern matches event type

        Supports:
        - Exact match: "platform.ready"
        - Wildcard: "platform.*", "bcm.*", "*"

        Args:
            pattern: Pattern string
            event_type: Event type

        Returns:
            True if matches
        """
        if pattern == "*":
            return True

        if pattern == event_type:
            return True

        # Wildcard matching
        if "*" in pattern:
            pattern_parts = pattern.split(".")
            event_parts = event_type.split(".")

            if len(pattern_parts) != len(event_parts):
                return False

            for p_part, e_part in zip(pattern_parts, event_parts):
                if p_part != "*" and p_part != e_part:
                    return False

            return True

        return False

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get event coordinator statistics

        Returns:
            Dictionary with stats
        """
        return {
            'subscriptions_active': self.subscriptions_active,
            'total_patterns': len(self.handlers),
            'total_handlers': sum(len(handlers) for handlers in self.handlers.values()),
            'patterns': list(self.handlers.keys()),
            'redis_connected': self.redis_client is not None,
            'eventbus_url': self.eventbus_url
        }

    async def close(self) -> None:
        """Close connections"""
        self.subscriptions_active = False
        logger.info("EventCoordinator closed")