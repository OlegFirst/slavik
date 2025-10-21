"""
Event Bus Core
==============

Core event bus functionality with Redis Streams backend.
"""

import os
import json
import uuid
import logging
import asyncio
from typing import Optional, Callable, Awaitable, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict, field
from functools import wraps

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Type alias for event handler
EventHandler = Callable[["Event"], Awaitable[None]]


@dataclass
class Event:
    """
    Event data structure.

    Attributes:
        id: Unique event ID
        type: Event type (e.g., 'workflow.completed')
        data: Event payload
        source: Service that created the event
        timestamp: When event was created
        tenant_id: Tenant identifier
        correlation_id: For tracking related events
        metadata: Additional metadata
    """
    id: str
    type: str
    data: Dict[str, Any]
    source: str
    timestamp: str
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        event_type: str,
        data: Dict[str, Any],
        source: str,
        tenant_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "Event":
        """Create new event with auto-generated ID and timestamp."""
        return cls(
            id=str(uuid.uuid4()),
            type=event_type,
            data=data,
            source=source,
            timestamp=datetime.utcnow().isoformat(),
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            metadata=metadata or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


class EventBus:
    """
    Redis Streams-based Event Bus.

    Singleton pattern - use get_event_bus() to access.
    """

    def __init__(
        self,
        service_name: str,
        redis_url: str = "redis://localhost:6379",
        consumer_group: Optional[str] = None,
        stream_name: str = "platform:events"
    ):
        """
        Initialize Event Bus.

        Args:
            service_name: Name of this service
            redis_url: Redis connection URL
            consumer_group: Consumer group name (defaults to service_name)
            stream_name: Redis stream name
        """
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - using stub EventBus")

        self.service_name = service_name
        self.redis_url = redis_url
        self.consumer_group = consumer_group or service_name
        self.stream_name = stream_name

        self.client: Optional[aioredis.Redis] = None
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._consumer_tasks: List[asyncio.Task] = []
        self._connected = False
        self._stats = {
            "published": 0,
            "consumed": 0,
            "errors": 0
        }

    async def connect(self):
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - running without event bus")
            return

        try:
            self.client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

            # Test connection
            await self.client.ping()

            # Create stream and consumer group if they don't exist
            try:
                await self.client.xgroup_create(
                    self.stream_name,
                    self.consumer_group,
                    id="0",
                    mkstream=True
                )
                logger.info(f" Created consumer group: {self.consumer_group}")
            except aioredis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
                logger.info(f" Consumer group already exists: {self.consumer_group}")

            self._connected = True
            logger.info(f" EventBus connected to Redis: {self.redis_url}")

        except Exception as e:
            logger.error(f" Failed to connect to Redis: {e}")
            logger.warning("Running without event bus")

    async def publish(self, event: Event) -> None:
        """
        Publish event to stream.

        Args:
            event: Event to publish
        """
        if not self._connected or not self.client:
            logger.debug(f"EventBus not connected - skipping event: {event.type}")
            return

        try:
            # Add to Redis stream
            await self.client.xadd(
                self.stream_name,
                {"event": event.to_json()},
                maxlen=100000  # Keep last 100k events
            )

            self._stats["published"] += 1
            logger.debug(f" Published event: {event.type} (id: {event.id})")

        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f" Failed to publish event {event.type}: {e}")
            raise

    async def subscribe(
        self,
        pattern: str,
        handler: EventHandler,
        consumer_group: Optional[str] = None
    ) -> str:
        """
        Subscribe to events matching pattern.

        Args:
            pattern: Event type pattern (supports wildcards like 'workflow.*')
            handler: Async function to handle events
            consumer_group: Optional consumer group (defaults to service group)

        Returns:
            Subscription ID
        """
        if pattern not in self._subscribers:
            self._subscribers[pattern] = []

        self._subscribers[pattern].append(handler)

        # Start consumer task if connected
        if self._connected:
            task = asyncio.create_task(
                self._consume_events(pattern, consumer_group or self.consumer_group)
            )
            self._consumer_tasks.append(task)

        subscription_id = f"{pattern}:{len(self._subscribers[pattern])}"
        logger.info(f" Subscribed to: {pattern} (id: {subscription_id})")

        return subscription_id

    async def _consume_events(self, pattern: str, consumer_group: str):
        """
        Consume events from stream.

        Args:
            pattern: Event pattern to match
            consumer_group: Consumer group name
        """
        if not self.client:
            return

        consumer_name = f"{self.service_name}:{os.getpid()}"
        logger.info(f" Starting consumer: {consumer_name} for pattern: {pattern}")

        while self._connected:
            try:
                # Read from stream
                events = await self.client.xreadgroup(
                    consumer_group,
                    consumer_name,
                    {self.stream_name: ">"},
                    count=10,
                    block=1000  # Block for 1 second
                )

                if not events:
                    continue

                # Process events
                for stream_name, messages in events:
                    for message_id, message_data in messages:
                        try:
                            # Parse event
                            event_json = message_data.get("event")
                            if not event_json:
                                continue

                            event = Event.from_json(event_json)

                            # Check if pattern matches
                            if self._matches_pattern(event.type, pattern):
                                # Call all handlers for this pattern
                                handlers = self._subscribers.get(pattern, [])
                                for handler in handlers:
                                    try:
                                        await handler(event)
                                        self._stats["consumed"] += 1
                                    except Exception as e:
                                        logger.error(f" Handler error for {event.type}: {e}")
                                        self._stats["errors"] += 1

                            # Acknowledge message
                            await self.client.xack(
                                self.stream_name,
                                consumer_group,
                                message_id
                            )

                        except Exception as e:
                            logger.error(f" Error processing message: {e}")
                            self._stats["errors"] += 1

            except asyncio.CancelledError:
                logger.info(f"Consumer task cancelled: {consumer_name}")
                break
            except Exception as e:
                logger.error(f" Consumer error: {e}")
                await asyncio.sleep(5)  # Wait before retry

    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """
        Check if event type matches pattern.

        Supports wildcards:
        - 'workflow.*' matches 'workflow.started', 'workflow.completed'
        - '*' matches everything
        - 'workflow.*.completed' matches 'workflow.process.completed'

        Args:
            event_type: Event type to check
            pattern: Pattern with wildcards

        Returns:
            True if matches
        """
        if pattern == "*":
            return True

        pattern_parts = pattern.split(".")
        event_parts = event_type.split(".")

        if len(pattern_parts) != len(event_parts):
            return False

        for pattern_part, event_part in zip(pattern_parts, event_parts):
            if pattern_part != "*" and pattern_part != event_part:
                return False

        return True

    async def close(self):
        """Close connections and cleanup."""
        logger.info("Closing EventBus...")
        self._connected = False

        # Cancel consumer tasks
        for task in self._consumer_tasks:
            task.cancel()

        # Wait for tasks to finish
        if self._consumer_tasks:
            await asyncio.gather(*self._consumer_tasks, return_exceptions=True)

        # Close Redis connection
        if self.client:
            await self.client.close()

        logger.info(" EventBus closed")

    def get_stats(self) -> Dict[str, int]:
        """Get bus statistics."""
        return self._stats.copy()


# Global event bus instance
_event_bus: Optional[EventBus] = None
_event_handlers: List[tuple] = []  # Store (pattern, handler, consumer_group) for registration


async def init_event_bus(
    service_name: str,
    redis_url: Optional[str] = None,
    consumer_group: Optional[str] = None
) -> EventBus:
    """
    Initialize global event bus.

    Args:
        service_name: Name of this service
        redis_url: Redis connection URL (defaults to env REDIS_URL)
        consumer_group: Consumer group name (defaults to service_name)

    Returns:
        EventBus instance
    """
    global _event_bus

    redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")

    _event_bus = EventBus(
        service_name=service_name,
        redis_url=redis_url,
        consumer_group=consumer_group
    )

    await _event_bus.connect()

    # Register all collected handlers from @subscribe_to decorators
    for pattern, handler, cgroup in _event_handlers:
        await _event_bus.subscribe(pattern, handler, cgroup)

    # Publish service.started event
    await publish_event(
        event_type="service.started",
        data={
            "service_name": service_name,
            "subscriptions": list(set(p for p, _, _ in _event_handlers)),
            "timestamp": datetime.utcnow().isoformat()
        },
        source=service_name
    )

    logger.info(f" EventBus initialized for service: {service_name}")
    return _event_bus


def get_event_bus() -> Optional[EventBus]:
    """
    Get global event bus instance.

    Returns:
        EventBus instance or None if not initialized
    """
    return _event_bus


async def publish_event(
    event_type: str,
    data: Dict[str, Any],
    source: Optional[str] = None,
    tenant_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Publish event to bus.

    High-level API - automatically uses global event bus.

    Args:
        event_type: Event type (e.g., 'workflow.completed')
        data: Event payload
        source: Service name (auto-detected if not provided)
        tenant_id: Tenant identifier
        correlation_id: Correlation ID
        metadata: Additional metadata
    """
    bus = get_event_bus()
    if not bus:
        logger.warning(f"EventBus not initialized - cannot publish: {event_type}")
        return

    source = source or bus.service_name

    event = Event.create(
        event_type=event_type,
        data=data,
        source=source,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        metadata=metadata
    )

    await bus.publish(event)


def subscribe_to(
    pattern: str,
    consumer_group: Optional[str] = None
):
    """
    Decorator for subscribing to events.

    Usage:
        @subscribe_to("workflow.*")
        async def on_workflow_event(event: Event):
            print(f"Got: {event.type}")

    Args:
        pattern: Event type pattern (supports wildcards)
        consumer_group: Optional consumer group name

    Returns:
        Decorator function
    """
    def decorator(func: EventHandler) -> EventHandler:
        # Store handler for later registration
        _event_handlers.append((pattern, func, consumer_group))

        @wraps(func)
        async def wrapper(event: Event):
            return await func(event)

        return wrapper

    return decorator
