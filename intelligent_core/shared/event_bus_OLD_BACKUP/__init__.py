"""
Shared Event Bus Library
========================

Unified event system for the entire platform.

Features:
- Auto-discovery of event handlers
- Redis Streams backend
- Outbox pattern for guaranteed delivery
- Pattern matching (wildcards)
- Consumer groups for load balancing
- Transaction-safe event publishing

Usage:
    # In your service lifespan:
    from shared.event_bus import init_event_bus, get_event_bus

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await init_event_bus(
            service_name="my-service",
            redis_url="redis://localhost:6379"
        )
        yield
        await get_event_bus().close()

    # Publish events:
    from shared.event_bus import publish_event

    await publish_event(
        event_type="workflow.completed",
        data={"workflow_id": "123"},
        source="workflow-service"
    )

    # Subscribe to events:
    from shared.event_bus import subscribe_to

    @subscribe_to("workflow.*")
    async def on_workflow_event(event: Event):
        print(f"Got: {event.type}")
"""

from .core import (
    Event,
    EventBus,
    get_event_bus,
    init_event_bus,
    publish_event,
    subscribe_to,
    EventHandler
)

from .outbox import (
    OutboxPublisher,
    save_to_outbox,
    publish_outbox_events
)

__all__ = [
    "Event",
    "EventBus",
    "get_event_bus",
    "init_event_bus",
    "publish_event",
    "subscribe_to",
    "EventHandler",
    "OutboxPublisher",
    "save_to_outbox",
    "publish_outbox_events",
]

__version__ = "1.0.0"
