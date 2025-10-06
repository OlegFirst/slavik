"""
EventBus Interface
==================

Abstract interface for EventBus implementations.
All backends must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Callable, Awaitable, Optional
from infrastructure.eventbus.core.events import Event


# Type alias for event handler
EventHandler = Callable[[Event], Awaitable[None]]


class IEventBus(ABC):
    """
    EventBus interface - backend-agnostic.

    Any transport (in-memory, Redis, RabbitMQ) must implement this interface.
    This ensures code using EventBus doesn't depend on specific backend.

    Guarantees:
        - At-least-once delivery (may have duplicates)
        - Async operations (non-blocking)
        - Wildcard pattern support (e.g., 'workflow.*')
        - Consumer groups (for load balancing)

    Example:
        ```python
        # Implementation can be anything
        bus: IEventBus = InMemoryEventBus()
        # or
        bus: IEventBus = RedisStreamEventBus()
        # or
        bus: IEventBus = RabbitMQEventBus()

        # But usage is always the same
        await bus.publish(event)
        await bus.subscribe('workflow.*', handler)
        ```
    """

    @abstractmethod
    async def publish(self, event: Event) -> None:
        """
        Publish event to bus.

        Guarantees:
            - At-least-once delivery
            - Async (returns immediately)
            - Event may be delivered multiple times (idempotent handlers recommended)

        Args:
            event: Event to publish

        Raises:
            Exception: If publish fails (backend-specific)

        Example:
            ```python
            event = Event.create(
                event_type='bia.process_created',
                data={'process_id': 123},
                source='bia-service',
                tenant_id='tenant_456'
            )
            await bus.publish(event)
            ```
        """
        pass

    @abstractmethod
    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        consumer_group: Optional[str] = None
    ) -> str:
        """
        Subscribe to events matching pattern.

        Args:
            event_type: Event type pattern (supports wildcards)
                Examples:
                    'workflow.stage_changed' - exact match
                    'workflow.*' - all workflow events
                    '*' or '#' - all events
            handler: Async function to handle events
                Signature: async def handler(event: Event) -> None
            consumer_group: Optional consumer group name
                If specified, multiple instances share load
                If not specified, all instances get all events

        Returns:
            str: Subscription ID (for unsubscribe)

        Example:
            ```python
            async def handle_workflow_event(event: Event):
                print(f"Workflow event: {event.data}")

            # Subscribe to all workflow events
            sub_id = await bus.subscribe(
                'workflow.*',
                handle_workflow_event,
                consumer_group='workflow-processors'
            )
            ```
        """
        pass

    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """
        Cancel subscription.

        Args:
            subscription_id: ID returned from subscribe()

        Example:
            ```python
            sub_id = await bus.subscribe('workflow.*', handler)
            # ... later
            await bus.unsubscribe(sub_id)
            ```
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close bus and cleanup resources.

        Call during application shutdown.

        Example:
            ```python
            @app.on_event("shutdown")
            async def shutdown():
                await bus.close()
            ```
        """
        pass

    async def get_stats(self) -> dict:
        """
        Get bus statistics (optional).

        Returns:
            dict: Statistics (backend-specific)

        Default implementation returns empty stats.
        Backends may override to provide metrics.
        """
        return {
            'published': 0,
            'consumed': 0,
            'errors': 0
        }
