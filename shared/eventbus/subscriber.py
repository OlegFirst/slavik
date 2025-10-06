"""
Event Subscriber
================

Helper class for subscribing to events from EventBus.
"""

from typing import Callable, Dict, Any
from shared.eventbus.client import get_eventbus
import asyncio


class EventSubscriber:
    """
    Helper for subscribing to events.

    Simplifies event subscription with consistent patterns.

    Example:
        ```python
        subscriber = EventSubscriber(service_name="validation")

        @subscriber.on("exercise.created")
        async def handle_exercise_created(event_data: dict, tenant_id: str):
            print(f"New exercise: {event_data['exercise_id']}")

        await subscriber.start()
        ```
    """

    def __init__(self, service_name: str):
        """
        Initialize event subscriber.

        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.handlers: Dict[str, Callable] = {}

    def on(self, event_type: str):
        """
        Decorator for registering event handlers.

        Args:
            event_type: Event type to handle (supports wildcards)

        Returns:
            Decorator function

        Example:
            ```python
            @subscriber.on("exercise.created")
            async def handle_exercise_created(event_data: dict, tenant_id: str):
                exercise_id = event_data["exercise_id"]
                await process_exercise(exercise_id)

            @subscriber.on("document.*")
            async def handle_all_document_events(event_data: dict, tenant_id: str):
                print(f"Document event: {event_data}")
            ```
        """
        def decorator(handler: Callable):
            self.handlers[event_type] = handler
            return handler
        return decorator

    async def start(self) -> None:
        """
        Start subscribing to all registered event handlers.

        Call this after registering all handlers.

        Example:
            ```python
            @app.on_event("startup")
            async def startup():
                await subscriber.start()
            ```
        """
        eventbus = get_eventbus()

        # Start subscription for each handler
        tasks = []
        for event_type, handler in self.handlers.items():
            task = asyncio.create_task(
                eventbus.subscribe(
                    event_type,
                    handler,
                    queue_name=f"{self.service_name}_{event_type}"
                )
            )
            tasks.append(task)

        # Wait for all subscriptions
        await asyncio.gather(*tasks)
