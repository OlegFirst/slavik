"""
Shared Event Bus - High-Level API
==================================

Wrapper over infrastructure/eventbus with intelligent-core specific features:
- High-level API (init_event_bus, publish_event, etc)
- Decorators (@subscribe_to)
- Auto-discovery for Event Intelligence
- Outbox pattern for guaranteed delivery

Architecture:
    infrastructure/eventbus/  ← Low-level event bus engine (Redis, Memory backends)
    intelligent-core/shared/event_bus/  ← High-level API + intelligent-core features

Usage:
    from shared.event_bus import init_event_bus, publish_event, subscribe_to

    # Initialize
    await init_event_bus(service_name="my-service")

    # Publish
    await publish_event(event_type="workflow.completed", data={...})

    # Subscribe
    @subscribe_to("workflow.*")
    async def handler(event):
        pass
"""

import sys
from pathlib import Path

# Add infrastructure to Python path
infrastructure_path = Path(__file__).parent.parent.parent.parent / "infrastructure"
if str(infrastructure_path) not in sys.path:
    sys.path.insert(0, str(infrastructure_path))

# Import from infrastructure/eventbus (the real event bus engine)
from infrastructure.eventbus.factory import create_eventbus, create_eventbus_from_env
from infrastructure.eventbus.core.events import Event
from infrastructure.eventbus.core.interface import IEventBus

# Import intelligent-core specific features
from .wrappers import (
    init_event_bus,
    get_event_bus,
    publish_event,
    subscribe_to,
    shutdown_event_bus
)

from .outbox import (
    OutboxEvent,
    OutboxPublisher,
    save_to_outbox,
    publish_outbox_events
)

__all__ = [
    # From infrastructure/eventbus
    "Event",
    "IEventBus",
    "create_eventbus",
    "create_eventbus_from_env",

    # High-level API
    "init_event_bus",
    "get_event_bus",
    "publish_event",
    "subscribe_to",
    "shutdown_event_bus",

    # Outbox pattern
    "OutboxEvent",
    "OutboxPublisher",
    "save_to_outbox",
    "publish_outbox_events",
]

__version__ = "2.0.0"  # v2 = uses infrastructure/eventbus
