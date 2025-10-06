"""
EventBus Client
===============

Async RabbitMQ client for event-driven architecture.

Features:
- Async RabbitMQ connection
- Connection pooling
- Automatic reconnection
- Exchange and queue management
"""

from typing import Optional, Callable, Dict, Any
import asyncio
import json
from datetime import datetime
import aio_pika
from aio_pika import connect_robust, ExchangeType, Message
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractExchange


class EventBusClient:
    """
    Async RabbitMQ event bus client.

    Provides event publishing and subscription capabilities.

    Example:
        ```python
        # Initialize at startup
        eventbus = init_eventbus("amqp://guest:guest@localhost/")

        # Publish event
        await eventbus.publish(
            "exercise.created",
            {"exercise_id": 123, "tenant_id": "tenant456"}
        )

        # Subscribe to events
        async def handle_exercise_event(event_data: dict):
            print(f"Exercise created: {event_data}")

        await eventbus.subscribe("exercise.created", handle_exercise_event)
        ```
    """

    def __init__(self, rabbitmq_url: str, exchange_name: str = "bcm_events"):
        """
        Initialize EventBus client.

        Args:
            rabbitmq_url: RabbitMQ connection URL (e.g., amqp://guest:guest@localhost/)
            exchange_name: Exchange name for events (default: bcm_events)
        """
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.exchange: Optional[AbstractExchange] = None

    async def connect(self) -> None:
        """
        Connect to RabbitMQ.

        Establishes connection, channel, and declares exchange.

        Example:
            ```python
            await eventbus.connect()
            ```
        """
        # Create robust connection (auto-reconnect)
        self.connection = await connect_robust(self.rabbitmq_url)

        # Create channel
        self.channel = await self.connection.channel()

        # Declare exchange
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            ExchangeType.TOPIC,
            durable=True
        )

    async def disconnect(self) -> None:
        """
        Disconnect from RabbitMQ.

        Call this during application shutdown.

        Example:
            ```python
            @app.on_event("shutdown")
            async def shutdown():
                await eventbus.disconnect()
            ```
        """
        if self.connection:
            await self.connection.close()

    async def close(self) -> None:
        """
        Close EventBus connection (alias for disconnect).

        For backwards compatibility with services calling eventbus.close().
        """
        await self.disconnect()

    async def register_subscriptions(self) -> None:
        """
        Register event subscriptions (no-op for compatibility).

        Services should set up their own subscriptions using subscribe() method
        or call their own setup_subscriptions() function.

        This method exists for backwards compatibility.
        """
        pass  # No-op - subscriptions are registered via subscribe() method

    async def publish(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Publish event to EventBus.

        Args:
            event_type: Event type (e.g., "exercise.created", "document.approved")
            event_data: Event payload
            tenant_id: Tenant identifier (optional)

        Returns:
            bool: True if published successfully

        Example:
            ```python
            await eventbus.publish(
                "exercise.created",
                {
                    "exercise_id": 123,
                    "exercise_type": "tabletop",
                    "tenant_id": "tenant456"
                }
            )
            ```
        """
        if not self.exchange:
            await self.connect()

        # Prepare message
        message_body = {
            "event_type": event_type,
            "data": event_data,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        message = Message(
            body=json.dumps(message_body, default=str).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        try:
            # Publish to exchange with routing key = event_type
            await self.exchange.publish(
                message,
                routing_key=event_type
            )
            return True
        except Exception as e:
            print(f"Failed to publish event: {e}")
            return False

    async def subscribe(
        self,
        event_type: str,
        handler: Callable,
        queue_name: Optional[str] = None
    ) -> None:
        """
        Subscribe to events.

        Args:
            event_type: Event type to subscribe to (supports wildcards: *, #)
            handler: Async function to handle events
            queue_name: Custom queue name (optional)

        Example:
            ```python
            async def handle_exercise_event(event_data: dict):
                exercise_id = event_data["exercise_id"]
                print(f"Processing exercise {exercise_id}")

            # Subscribe to specific event
            await eventbus.subscribe("exercise.created", handle_exercise_event)

            # Subscribe to all exercise events
            await eventbus.subscribe("exercise.*", handle_exercise_event)

            # Subscribe to all events
            await eventbus.subscribe("#", handle_all_events)
            ```
        """
        if not self.channel:
            await self.connect()

        # Generate queue name if not provided
        if not queue_name:
            queue_name = f"{event_type.replace('.', '_')}_{id(handler)}"

        # Declare queue
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True
        )

        # Bind queue to exchange with routing key
        await queue.bind(self.exchange, routing_key=event_type)

        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    # Parse message
                    body = json.loads(message.body.decode())
                    event_data = body.get("data", {})
                    tenant_id = body.get("tenant_id")

                    # Call handler
                    try:
                        await handler(event_data, tenant_id)
                    except Exception as e:
                        print(f"Error handling event: {e}")

    def is_connected(self) -> bool:
        """
        Check if connected to RabbitMQ.

        Returns:
            bool: True if connected
        """
        return self.connection is not None and not self.connection.is_closed


# Global EventBus client instance
_eventbus: Optional[EventBusClient] = None


def init_eventbus(
    rabbitmq_url: str,
    exchange_name: str = "bcm_events"
) -> EventBusClient:
    """
    Initialize global EventBus client.

    Call this once during application startup.

    Args:
        rabbitmq_url: RabbitMQ connection URL
        exchange_name: Exchange name (default: bcm_events)

    Returns:
        EventBusClient: Initialized EventBus client

    Example:
        ```python
        @app.on_event("startup")
        async def startup():
            eventbus = init_eventbus(settings.RABBITMQ_URL)
            await eventbus.connect()
        ```
    """
    global _eventbus
    _eventbus = EventBusClient(rabbitmq_url, exchange_name)
    return _eventbus


def get_eventbus() -> EventBusClient:
    """
    Get global EventBus client instance.

    Returns:
        EventBusClient: Global EventBus client

    Raises:
        RuntimeError: If EventBus not initialized
    """
    if _eventbus is None:
        raise RuntimeError(
            "EventBus not initialized. Call init_eventbus() during startup."
        )
    return _eventbus
