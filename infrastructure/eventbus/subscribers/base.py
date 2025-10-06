"""
Base Event Subscriber
=====================

Base class for all event subscribers.
Provides common functionality and contract for subscribers.
"""

from abc import ABC, abstractmethod
from typing import List
from infrastructure.eventbus.core.interface import IEventBus


class BaseSubscriber(ABC):
    """
    Base class for event subscribers.

    All subscribers should inherit from this class and implement
    the setup_subscriptions() method.

    Features:
        - Automatic subscription management
        - Cleanup on shutdown
        - Subscription tracking

    Example:
        ```python
        class CaseCollectorSubscriber(BaseSubscriber):
            def __init__(self, case_collector):
                super().__init__()
                self.collector = case_collector

            async def setup_subscriptions(self, eventbus):
                await self.subscribe(
                    eventbus,
                    'workflow.state_changed',
                    self.handle_state_changed
                )

            async def handle_state_changed(self, event: Event):
                await self.collector.record_transition(event.data)
        ```
    """

    def __init__(self):
        """Initialize subscriber."""
        self._subscription_ids: List[str] = []

    @abstractmethod
    async def setup_subscriptions(self, eventbus: IEventBus) -> None:
        """
        Setup event subscriptions.

        This method should be implemented by subclasses to register
        all event handlers.

        Args:
            eventbus: EventBus instance to subscribe to

        Example:
            ```python
            async def setup_subscriptions(self, eventbus):
                await self.subscribe(
                    eventbus,
                    'workflow.*',
                    self.handle_workflow_event
                )
            ```
        """
        pass

    async def subscribe(
        self,
        eventbus: IEventBus,
        event_type: str,
        handler,
        consumer_group: str = None
    ) -> str:
        """
        Subscribe to event type and track subscription.

        Args:
            eventbus: EventBus instance
            event_type: Event type pattern
            handler: Event handler function
            consumer_group: Optional consumer group

        Returns:
            str: Subscription ID

        Example:
            ```python
            await self.subscribe(
                eventbus,
                'workflow.completed',
                self.handle_completion
            )
            ```
        """
        sub_id = await eventbus.subscribe(
            event_type,
            handler,
            consumer_group=consumer_group
        )

        # Track subscription for cleanup
        self._subscription_ids.append(sub_id)

        return sub_id

    async def cleanup(self, eventbus: IEventBus) -> None:
        """
        Unsubscribe from all events.

        Call during shutdown to cleanup subscriptions.

        Args:
            eventbus: EventBus instance

        Example:
            ```python
            @app.on_event("shutdown")
            async def shutdown():
                await subscriber.cleanup(bus)
            ```
        """
        for sub_id in self._subscription_ids:
            await eventbus.unsubscribe(sub_id)

        self._subscription_ids.clear()

    def get_subscription_count(self) -> int:
        """
        Get number of active subscriptions.

        Returns:
            int: Number of subscriptions
        """
        return len(self._subscription_ids)
