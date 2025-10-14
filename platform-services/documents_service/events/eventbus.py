"""
EventBus Client for Documents Service
Connects to RabbitMQ for event-driven architecture

Publishes:
- bcm.document.uploaded
- bcm.document.approved
- bcm.document.published
- bcm.document.archived
- bcm.document.expired
- bcm.document.shared

Subscribes to:
- bcm.plan.created
- bcm.exercise.completed
- bcm.policy.updated
- bcm.audit.started
- bcm.training.scheduled
"""

import json
import asyncio
from typing import Callable, Dict, Any, Optional
from datetime import datetime

try:
    import aio_pika
    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False
    print("⚠️  aio_pika not installed. EventBus will run in mock mode.")
    print("   Install: pip install aio-pika")


class EventBus:
    """
    EventBus client for pub/sub messaging.

    Uses RabbitMQ for production, falls back to mock for development.
    """

    def __init__(
        self,
        rabbitmq_url: str = "amqp://guest:guest@localhost:5672/",
        exchange_name: str = "bcm_events",
        service_name: str = "documents"
    ):
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name
        self.service_name = service_name

        self.connection: Optional[Any] = None
        self.channel: Optional[Any] = None
        self.exchange: Optional[Any] = None
        self.queue: Optional[Any] = None

        self.handlers: Dict[str, Callable] = {}
        self.is_connected = False
        self.mock_mode = not RABBITMQ_AVAILABLE

    async def connect(self):
        """Connect to RabbitMQ"""
        if self.mock_mode:
            print(f"📡 EventBus ({self.service_name}): Running in MOCK mode")
            self.is_connected = True
            return

        try:
            # Connect to RabbitMQ
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()

            # Declare exchange (topic type for routing)
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            # Declare service queue
            self.queue = await self.channel.declare_queue(
                f"{self.service_name}_events",
                durable=True
            )

            self.is_connected = True
            print(f"✅ EventBus ({self.service_name}): Connected to RabbitMQ")

        except Exception as e:
            print(f"⚠️  EventBus ({self.service_name}): Failed to connect - {e}")
            print(f"   Falling back to MOCK mode")
            self.mock_mode = True
            self.is_connected = True

    async def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.mock_mode:
            print(f"📡 EventBus ({self.service_name}): Mock mode - no disconnect needed")
            self.is_connected = False
            return

        if self.connection:
            await self.connection.close()
            self.is_connected = False
            print(f"👋 EventBus ({self.service_name}): Disconnected")

    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        routing_key: Optional[str] = None
    ):
        """
        Publish event to EventBus.

        Args:
            event_type: Event type (e.g., "bcm.document.uploaded")
            data: Event payload
            routing_key: Routing key (defaults to event_type)
        """
        if not self.is_connected:
            print(f"⚠️  EventBus not connected. Event not published: {event_type}")
            return

        # Prepare event message
        event_message = {
            "event_type": event_type,
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        if self.mock_mode:
            # Mock mode - just log
            print(f"📤 EVENT PUBLISHED: {event_type}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            return

        try:
            # Publish to RabbitMQ
            message = aio_pika.Message(
                body=json.dumps(event_message).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await self.exchange.publish(
                message,
                routing_key=routing_key or event_type
            )

            print(f"✅ Event published: {event_type}")

        except Exception as e:
            print(f"❌ Failed to publish event {event_type}: {e}")

    async def subscribe(
        self,
        event_type: str,
        handler: Callable,
        routing_key: Optional[str] = None
    ):
        """
        Subscribe to event type.

        Args:
            event_type: Event type to listen for
            handler: Async function to handle event
            routing_key: Routing pattern (supports wildcards)
        """
        if not self.is_connected:
            print(f"⚠️  EventBus not connected. Cannot subscribe: {event_type}")
            return

        self.handlers[event_type] = handler

        if self.mock_mode:
            print(f"📥 SUBSCRIBED (mock): {event_type}")
            return

        try:
            # Bind queue to exchange with routing key
            await self.queue.bind(
                self.exchange,
                routing_key=routing_key or event_type
            )

            print(f"✅ Subscribed to: {event_type}")

        except Exception as e:
            print(f"❌ Failed to subscribe to {event_type}: {e}")

    async def start_consuming(self):
        """Start consuming messages from queue"""
        if self.mock_mode:
            print(f"📡 EventBus ({self.service_name}): Mock mode - not consuming")
            return

        if not self.queue:
            print(f"⚠️  Queue not initialized")
            return

        try:
            async with self.queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        await self._process_message(message)

        except Exception as e:
            print(f"❌ Error consuming messages: {e}")

    async def _process_message(self, message):
        """Process incoming message"""
        try:
            # Parse message
            body = json.loads(message.body.decode())
            event_type = body.get("event_type")
            data = body.get("data", {})

            print(f"📥 EVENT RECEIVED: {event_type}")

            # Find handler
            handler = self.handlers.get(event_type)

            if handler:
                # Execute handler
                await handler(data)
                print(f"✅ Event handled: {event_type}")
            else:
                print(f"⚠️  No handler for event: {event_type}")

        except Exception as e:
            print(f"❌ Error processing message: {e}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def publish_document_event(
    eventbus: EventBus,
    event_type: str,
    document_id: int,
    document_code: str,
    title: str,
    user_id: str,
    **extra_data
):
    """
    Publish document event with standard fields.

    Args:
        eventbus: EventBus instance
        event_type: Event type
        document_id: Document ID
        document_code: Document code
        title: Document title
        user_id: User who triggered event
        **extra_data: Additional event data
    """
    data = {
        "document_id": document_id,
        "document_code": document_code,
        "title": title,
        "user_id": user_id,
        **extra_data
    }

    await eventbus.publish(event_type, data)


# ============================================================================
# EVENT TYPE CONSTANTS
# ============================================================================

class DocumentEvents:
    """Document event type constants"""

    # Published by Documents service
    UPLOADED = "bcm.document.uploaded"
    APPROVED = "bcm.document.approved"
    REJECTED = "bcm.document.rejected"
    PUBLISHED = "bcm.document.published"
    ARCHIVED = "bcm.document.archived"
    EXPIRED = "bcm.document.expired"
    SHARED = "bcm.document.shared"
    VERSION_CREATED = "bcm.document.version_created"

    # Subscribed from other services
    PLAN_CREATED = "bcm.plan.created"
    PLAN_ACTIVATED = "bcm.plan.activated"
    EXERCISE_COMPLETED = "bcm.exercise.completed"
    POLICY_UPDATED = "bcm.policy.updated"
    AUDIT_STARTED = "bcm.audit.started"
    TRAINING_SCHEDULED = "bcm.training.scheduled"


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Global EventBus instance (initialized in main.py lifespan)
eventbus: Optional[EventBus] = None


def get_eventbus() -> EventBus:
    """Get global EventBus instance"""
    if eventbus is None:
        raise RuntimeError("EventBus not initialized. Call initialize_eventbus() first.")
    return eventbus


def initialize_eventbus(rabbitmq_url: str = "amqp://guest:guest@localhost:5672/") -> EventBus:
    """
    Initialize global EventBus instance.

    Call this in main.py lifespan.
    """
    global eventbus
    eventbus = EventBus(rabbitmq_url=rabbitmq_url)
    return eventbus
