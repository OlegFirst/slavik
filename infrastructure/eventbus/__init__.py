"""
EventBus - Pluggable Event System for BCM Platform
====================================================

Clean architecture event bus with multiple backend support.

Features:
- Clean interface (IEventBus)
- Multiple backends: memory, redis, rabbitmq
- Type-safe events
- Wildcard subscriptions
- Consumer groups
- Retry logic
- Event subscribers (event-driven architecture)
- Zero vendor lock-in

Quick Start:
    ```python
    from infrastructure.eventbus import create_eventbus, Event, EventPriority
    from infrastructure.eventbus.subscribers import BaseSubscriber

    # Create bus (pluggable backend)
    bus = create_eventbus('memory')  # or 'redis'

    # Publish event
    event = Event.create(
        event_type='workflow.stage_changed',
        data={'workflow_id': 'bia_001'},
        source='workflow-engine',
        tenant_id='tenant_123'
    )
    await bus.publish(event)

    # Subscribe (simple)
    async def handle_event(event: Event):
        print(f"Got event: {event.type}")

    await bus.subscribe('workflow.*', handle_event)

    # Subscribe (using BaseSubscriber)
    class MySubscriber(BaseSubscriber):
        async def setup_subscriptions(self, eventbus):
            await self.subscribe(eventbus, 'workflow.*', self.handle_event)

        async def handle_event(self, event: Event):
            print(f"Got: {event.type}")

    subscriber = MySubscriber()
    await subscriber.setup_subscriptions(bus)
    ```
"""

from infrastructure.eventbus.core.events import Event, EventPriority
from infrastructure.eventbus.core.interface import IEventBus, EventHandler
from infrastructure.eventbus.factory import create_eventbus

# Import Intelligent Router (graceful choreography)
try:
    from infrastructure.eventbus.intelligent_router import IntelligentEventRouter
    INTELLIGENT_ROUTER_AVAILABLE = True
except ImportError:
    IntelligentEventRouter = None
    INTELLIGENT_ROUTER_AVAILABLE = False

__all__ = [
    'Event',
    'EventPriority',
    'IEventBus',
    'EventHandler',
    'create_eventbus',
    'IntelligentEventRouter',
    'INTELLIGENT_ROUTER_AVAILABLE'
]

__version__ = '0.3.0'  # Updated with Intelligent Router support
