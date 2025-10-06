"""
Event Subscribers
=================

Base classes and utilities for building event subscribers.

Event subscribers listen to specific event patterns and react to them.
They enable event-driven architecture with loose coupling between services.

Architecture:
    State Machine (Publisher)
        │
        └─→ EventBus
            ├─→ Case Collector (records history)
            ├─→ AI Advisor (prepares context)
            ├─→ Analytics Service (metrics)
            ├─→ Notification Service (alerts)
            └─→ Audit Logger (compliance)

Example:
    ```python
    from infrastructure.eventbus import Event
    from infrastructure.eventbus.subscribers import BaseSubscriber

    class MySubscriber(BaseSubscriber):
        async def setup_subscriptions(self, eventbus):
            await eventbus.subscribe('workflow.*', self.handle_workflow_event)

        async def handle_workflow_event(self, event: Event):
            print(f"Got: {event.type}")

    # Usage
    subscriber = MySubscriber()
    await subscriber.setup_subscriptions(bus)
    ```
"""

from .base import BaseSubscriber

__all__ = [
    'BaseSubscriber',
]
