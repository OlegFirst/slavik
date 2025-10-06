"""
In-Memory EventBus Implementation
==================================

Simple in-memory event bus for MVP, testing, and development.

Advantages:
    - Zero dependencies
    - Instant startup
    - Perfect for unit tests
    - No infrastructure needed

Limitations:
    - Events don't survive process restart
    - Doesn't work across multiple processes
    - No persistence

Use Cases:
    - Unit testing
    - Local development
    - MVP validation
    - Single-process deployments
"""

import asyncio
import re
from typing import Dict, List, Optional
from infrastructure.eventbus.core.interface import IEventBus, EventHandler
from infrastructure.eventbus.core.events import Event


class InMemoryEventBus(IEventBus):
    """
    In-memory event bus implementation.

    Events are stored in memory and delivered via asyncio tasks.
    No external dependencies required.

    Example:
        ```python
        bus = InMemoryEventBus()

        # Subscribe
        async def handle_event(event: Event):
            print(f"Got: {event.type}")

        await bus.subscribe('workflow.*', handle_event)

        # Publish
        event = Event.create(
            event_type='workflow.stage_changed',
            data={'stage': 'analysis'},
            source='workflow-engine',
            tenant_id='tenant_123'
        )
        await bus.publish(event)
        ```
    """

    def __init__(self):
        """Initialize in-memory event bus."""
        # Pattern -> list of handlers
        self._handlers: Dict[str, List[EventHandler]] = {}

        # Subscription ID -> (pattern, handler)
        self._subscriptions: Dict[str, tuple] = {}

        # Statistics
        self._stats = {
            'published': 0,
            'consumed': 0,
            'errors': 0
        }

    async def publish(self, event: Event) -> None:
        """
        Publish event to all matching handlers.

        Args:
            event: Event to publish
        """
        self._stats['published'] += 1

        # Find handlers matching event type
        handlers = self._find_handlers(event.type)

        # Call each handler asynchronously (fire and forget)
        for handler in handlers:
            asyncio.create_task(self._safe_handle(event, handler))

    async def _safe_handle(self, event: Event, handler: EventHandler):
        """
        Handle event with error catching and retry logic.

        Args:
            event: Event to handle
            handler: Event handler function
        """
        try:
            await handler(event)
            self._stats['consumed'] += 1

        except Exception as e:
            self._stats['errors'] += 1
            print(f"[EventBus] Handler error: {e}")

            # Retry logic with exponential backoff
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                backoff_seconds = 2 ** event.retry_count

                print(f"[EventBus] Retrying in {backoff_seconds}s (attempt {event.retry_count}/{event.max_retries})")

                await asyncio.sleep(backoff_seconds)
                await self.publish(event)  # Republish for retry

    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        consumer_group: Optional[str] = None
    ) -> str:
        """
        Subscribe to events matching pattern.

        Args:
            event_type: Event type pattern (supports wildcards: *, #)
            handler: Async function to handle events
            consumer_group: Not used in memory backend (no load balancing)

        Returns:
            str: Subscription ID

        Example:
            ```python
            async def my_handler(event: Event):
                print(event.data)

            # Exact match
            await bus.subscribe('workflow.stage_changed', my_handler)

            # Wildcard - all workflow events
            await bus.subscribe('workflow.*', my_handler)

            # All events
            await bus.subscribe('*', my_handler)
            ```
        """
        import uuid

        # Generate subscription ID
        sub_id = str(uuid.uuid4())

        # Store handler
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)

        # Store subscription for unsubscribe
        self._subscriptions[sub_id] = (event_type, handler)

        return sub_id

    async def unsubscribe(self, subscription_id: str) -> None:
        """
        Cancel subscription.

        Args:
            subscription_id: ID returned from subscribe()
        """
        if subscription_id in self._subscriptions:
            event_type, handler = self._subscriptions[subscription_id]

            # Remove handler
            if event_type in self._handlers:
                try:
                    self._handlers[event_type].remove(handler)
                except ValueError:
                    pass  # Handler already removed

                # Clean up empty handler lists
                if not self._handlers[event_type]:
                    del self._handlers[event_type]

            # Remove subscription
            del self._subscriptions[subscription_id]

    def _find_handlers(self, event_type: str) -> List[EventHandler]:
        """
        Find all handlers matching event type.

        Supports wildcard patterns:
            - 'workflow.*' matches 'workflow.started', 'workflow.completed'
            - '*' or '#' matches everything

        Args:
            event_type: Event type to match

        Returns:
            list: Matching handlers
        """
        handlers = []

        for pattern, handler_list in self._handlers.items():
            if self._match_pattern(pattern, event_type):
                handlers.extend(handler_list)

        return handlers

    def _match_pattern(self, pattern: str, event_type: str) -> bool:
        """
        Check if event type matches pattern.

        Patterns:
            - Exact: 'workflow.stage_changed'
            - Single level wildcard: 'workflow.*'
            - Multi level wildcard: '#' or '*'

        Args:
            pattern: Subscription pattern
            event_type: Event type to test

        Returns:
            bool: True if matches
        """
        # Convert glob pattern to regex
        # '.' -> '\.' (literal dot)
        # '*' -> '.*' (any characters)
        # '#' -> '.*' (any characters)

        regex_pattern = pattern.replace('.', r'\.')
        regex_pattern = regex_pattern.replace('*', '.*')
        regex_pattern = regex_pattern.replace('#', '.*')

        return re.match(f'^{regex_pattern}$', event_type) is not None

    async def close(self) -> None:
        """
        Close bus and cleanup.

        Clears all handlers and subscriptions.
        """
        self._handlers.clear()
        self._subscriptions.clear()

    async def get_stats(self) -> dict:
        """
        Get bus statistics.

        Returns:
            dict: Statistics (published, consumed, errors)
        """
        return self._stats.copy()
