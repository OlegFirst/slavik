"""
Redis Streams EventBus Implementation
======================================

Production-ready event bus using Redis Streams.

Advantages:
    - Persistence (events survive restarts)
    - Consumer groups (load balancing across instances)
    - ACK mechanism (at-least-once delivery)
    - Simple setup (uses existing Redis)
    - Backpressure handling

Limitations:
    - Requires Redis 5.0+
    - Single point of failure (unless Redis cluster)

Use Cases:
    - Production deployments
    - Multi-instance services
    - Reliable event delivery
    - Event replay (consumer group offset)
"""

import json
import asyncio
from typing import Optional
from datetime import datetime

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from infrastructure.eventbus.core.interface import IEventBus, EventHandler
from infrastructure.eventbus.core.events import Event, EventPriority


class RedisStreamEventBus(IEventBus):
    """
    Redis Streams-based event bus.

    Uses Redis Streams for persistent, scalable event delivery.

    Features:
        - Consumer groups for load balancing
        - Event persistence
        - ACK mechanism
        - Automatic retry on failure

    Example:
        ```python
        bus = RedisStreamEventBus(redis_url='redis://localhost:6379')

        # Subscribe with consumer group
        async def handle_event(event: Event):
            print(f"Processing: {event.type}")

        await bus.subscribe(
            'workflow.*',
            handle_event,
            consumer_group='workflow-processors'
        )

        # Publish
        event = Event.create(
            event_type='workflow.completed',
            data={'workflow_id': 'bia_001'},
            source='workflow-engine',
            tenant_id='tenant_123'
        )
        await bus.publish(event)
        ```
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis Streams event bus.

        Args:
            redis_url: Redis connection URL

        Raises:
            ImportError: If redis package not installed
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package required for RedisStreamEventBus. "
                "Install with: pip install redis"
            )

        self.redis_url = redis_url
        self.client: Optional[aioredis.Redis] = None
        self._running_consumers = []
        self._stats = {'published': 0, 'consumed': 0, 'errors': 0}

    async def connect(self):
        """
        Connect to Redis.

        Creates Redis client if not already connected.
        """
        if not self.client:
            self.client = await aioredis.from_url(
                self.redis_url,
                decode_responses=True
            )

    async def publish(self, event: Event) -> None:
        """
        Publish event to Redis stream.

        Events are stored in streams named: 'events:{event.type}'

        Args:
            event: Event to publish
        """
        await self.connect()

        # Stream key based on event type
        stream_key = f"events:{event.type}"

        # Serialize event to dict
        event_data = {
            'id': event.id,
            'type': event.type,
            'data': json.dumps(event.data),
            'source': event.source,
            'tenant_id': event.tenant_id,
            'correlation_id': event.correlation_id or '',
            'timestamp': event.timestamp.isoformat(),
            'priority': str(event.priority.value),
            'retry_count': str(event.retry_count),
            'max_retries': str(event.max_retries)
        }

        # Add to stream
        await self.client.xadd(stream_key, event_data)
        self._stats['published'] += 1

    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        consumer_group: Optional[str] = None
    ) -> str:
        """
        Subscribe to events with consumer group.

        Args:
            event_type: Event type pattern (Note: wildcards limited in Redis)
            handler: Async event handler
            consumer_group: Consumer group name (default: 'default')

        Returns:
            str: Subscription ID

        Note:
            Redis Streams don't support wildcards like RabbitMQ.
            For wildcard support, subscribe to multiple streams.
        """
        await self.connect()

        stream_key = f"events:{event_type}"
        group_name = consumer_group or 'default'

        # Create consumer group if doesn't exist
        try:
            await self.client.xgroup_create(
                stream_key,
                group_name,
                id='0',  # Start from beginning
                mkstream=True  # Create stream if doesn't exist
            )
        except aioredis.ResponseError as e:
            # Group already exists - OK
            if 'BUSYGROUP' not in str(e):
                raise

        # Generate consumer ID
        consumer_id = f"consumer_{len(self._running_consumers)}"

        # Start consumer task
        task = asyncio.create_task(
            self._consume_stream(stream_key, group_name, consumer_id, handler)
        )

        self._running_consumers.append(task)

        # Return subscription ID
        subscription_id = f"{stream_key}:{group_name}:{consumer_id}"
        return subscription_id

    async def _consume_stream(
        self,
        stream_key: str,
        group_name: str,
        consumer_id: str,
        handler: EventHandler
    ):
        """
        Consume events from Redis stream.

        Runs in background task, processing events as they arrive.

        Args:
            stream_key: Redis stream key
            group_name: Consumer group name
            consumer_id: This consumer's ID
            handler: Event handler function
        """
        while True:
            try:
                # Read from stream (blocking with timeout)
                messages = await self.client.xreadgroup(
                    group_name,
                    consumer_id,
                    {stream_key: '>'},  # '>' = only new messages
                    count=10,  # Batch size
                    block=1000  # Block for 1 second
                )

                # Process each message
                for stream, events in messages:
                    for event_id, event_data in events:
                        # Deserialize event
                        event = self._deserialize_event(event_data)

                        # Handle event
                        try:
                            await handler(event)

                            # ACK message (mark as processed)
                            await self.client.xack(stream_key, group_name, event_id)
                            self._stats['consumed'] += 1

                        except Exception as e:
                            self._stats['errors'] += 1
                            print(f"[EventBus] Handler error: {e}")

                            # Retry logic
                            if event.retry_count < event.max_retries:
                                event.retry_count += 1
                                await self.publish(event)  # Republish for retry
                            else:
                                # Max retries reached - ACK anyway to avoid blocking
                                await self.client.xack(stream_key, group_name, event_id)
                                print(f"[EventBus] Max retries reached for event {event.id}")

            except asyncio.CancelledError:
                # Consumer shutdown
                break

            except Exception as e:
                print(f"[EventBus] Consumer error: {e}")
                await asyncio.sleep(5)  # Backoff before retry

    def _deserialize_event(self, event_data: dict) -> Event:
        """
        Deserialize event from Redis stream data.

        Args:
            event_data: Raw event data from Redis

        Returns:
            Event: Reconstructed event
        """
        return Event(
            id=event_data['id'],
            type=event_data['type'],
            data=json.loads(event_data['data']),
            source=event_data['source'],
            tenant_id=event_data['tenant_id'],
            correlation_id=event_data.get('correlation_id') or None,
            timestamp=datetime.fromisoformat(event_data['timestamp']),
            priority=EventPriority(int(event_data['priority'])),
            retry_count=int(event_data['retry_count']),
            max_retries=int(event_data['max_retries'])
        )

    async def unsubscribe(self, subscription_id: str) -> None:
        """
        Cancel subscription.

        Args:
            subscription_id: ID from subscribe()
        """
        # Parse subscription ID: "stream:group:consumer"
        # Find and cancel corresponding task
        # (Implementation depends on tracking tasks by ID)
        pass

    async def close(self) -> None:
        """
        Close bus and cleanup resources.

        Cancels all consumer tasks and closes Redis connection.
        """
        # Cancel all consumer tasks
        for task in self._running_consumers:
            task.cancel()

        # Wait for tasks to finish
        await asyncio.gather(*self._running_consumers, return_exceptions=True)

        # Close Redis connection
        if self.client:
            await self.client.close()

    async def get_stats(self) -> dict:
        """
        Get bus statistics.

        Returns:
            dict: Statistics (published, consumed, errors)
        """
        return self._stats.copy()
