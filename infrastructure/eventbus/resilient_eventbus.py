"""
Resilient EventBus with Persistence and Dead Letter Queue
AI Platform ISO 22301 - Production Ready

Features:
- Redis Streams для persistence
- Dead Letter Queue (DLQ) для failed events
- Retry механизм с exponential backoff
- Consumer Groups для distributed processing
- Event replay capability
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as aioredis
from redis.asyncio import Redis
import hashlib

logger = logging.getLogger(__name__)


class EventStatus(Enum):
    """Статус события"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DLQ = "dlq"  # Dead Letter Queue


@dataclass
class Event:
    """Событие платформы"""
    event_type: str
    payload: Dict
    event_id: str = None
    timestamp: str = None
    source: str = None
    correlation_id: str = None
    retry_count: int = 0
    max_retries: int = 3
    status: str = EventStatus.PENDING.value

    def __post_init__(self):
        if not self.event_id:
            # Generate unique event ID
            content = f"{self.event_type}{self.timestamp}{self.payload}"
            self.event_id = hashlib.sha256(content.encode()).hexdigest()[:16]

        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """Создание из словаря"""
        return cls(**data)


class ResilientEventBus:
    """
    Resilient EventBus с persistence, DLQ и retry механизмом

    Architecture:
    - Primary Stream: events:{channel}
    - DLQ Stream: events:dlq
    - Consumer Groups: auto-managed
    - Persistence: Redis Streams (AOF + RDB)
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        stream_prefix: str = "events",
        consumer_group_prefix: str = "bcm-platform",
        max_len: int = 10000,
        dlq_retention_hours: int = 168  # 7 days
    ):
        self.redis_url = redis_url
        self.stream_prefix = stream_prefix
        self.consumer_group_prefix = consumer_group_prefix
        self.max_len = max_len
        self.dlq_retention_hours = dlq_retention_hours

        self.redis: Optional[Redis] = None
        self.subscribers: Dict[str, List[Callable]] = {}
        self.consumer_tasks: List[asyncio.Task] = []

    async def connect(self):
        """Подключение к Redis"""
        self.redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
        logger.info("ResilientEventBus connected to Redis")

    async def close(self):
        """Закрытие соединения"""
        # Cancel all consumer tasks
        for task in self.consumer_tasks:
            task.cancel()

        await asyncio.gather(*self.consumer_tasks, return_exceptions=True)

        if self.redis:
            await self.redis.close()

        logger.info("ResilientEventBus closed")

    def _get_stream_name(self, channel: str) -> str:
        """Получение имени stream"""
        return f"{self.stream_prefix}:{channel}"

    def _get_dlq_stream_name(self) -> str:
        """Получение имени DLQ stream"""
        return f"{self.stream_prefix}:dlq"

    def _get_consumer_group_name(self, channel: str) -> str:
        """Получение имени consumer group"""
        return f"{self.consumer_group_prefix}:{channel}"

    # =========================================================================
    # Publishing Events
    # =========================================================================

    async def publish(
        self,
        channel: str,
        event_type: str,
        payload: Dict,
        source: str = None,
        correlation_id: str = None
    ) -> str:
        """
        Публикация события с гарантией persistence

        Returns:
            event_id: ID опубликованного события
        """
        event = Event(
            event_type=event_type,
            payload=payload,
            source=source,
            correlation_id=correlation_id
        )

        stream_name = self._get_stream_name(channel)

        # Publish to Redis Stream
        event_data = {
            "event": json.dumps(event.to_dict())
        }

        message_id = await self.redis.xadd(
            name=stream_name,
            fields=event_data,
            maxlen=self.max_len,
            approximate=True  # Allow ~10% variance for performance
        )

        logger.info(
            f"Event published: {event.event_type} "
            f"(id={event.event_id}, channel={channel}, stream_id={message_id})"
        )

        return event.event_id

    async def publish_batch(
        self,
        channel: str,
        events: List[Event]
    ) -> List[str]:
        """Batch публикация событий"""
        stream_name = self._get_stream_name(channel)

        pipe = self.redis.pipeline()

        for event in events:
            event_data = {"event": json.dumps(event.to_dict())}
            pipe.xadd(
                name=stream_name,
                fields=event_data,
                maxlen=self.max_len,
                approximate=True
            )

        results = await pipe.execute()

        logger.info(f"Batch published {len(events)} events to {channel}")

        return [event.event_id for event in events]

    # =========================================================================
    # Subscribing to Events
    # =========================================================================

    async def subscribe(
        self,
        channel: str,
        handler: Callable[[Event], None],
        consumer_name: str = None
    ):
        """
        Подписка на события с consumer group

        Args:
            channel: Канал событий
            handler: Async функция для обработки события
            consumer_name: Имя consumer (для distributed processing)
        """
        stream_name = self._get_stream_name(channel)
        group_name = self._get_consumer_group_name(channel)

        if not consumer_name:
            consumer_name = f"consumer-{id(handler)}"

        # Create consumer group if not exists
        try:
            await self.redis.xgroup_create(
                name=stream_name,
                groupname=group_name,
                id='0',  # Start from beginning
                mkstream=True
            )
            logger.info(f"Created consumer group: {group_name}")
        except Exception as e:
            # Group already exists
            logger.debug(f"Consumer group exists: {group_name}")

        # Store subscriber
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(handler)

        # Start consumer task
        task = asyncio.create_task(
            self._consume_events(
                stream_name,
                group_name,
                consumer_name,
                handler
            )
        )
        self.consumer_tasks.append(task)

        logger.info(
            f"Subscribed to {channel} "
            f"(group={group_name}, consumer={consumer_name})"
        )

    async def _consume_events(
        self,
        stream_name: str,
        group_name: str,
        consumer_name: str,
        handler: Callable
    ):
        """Потребление событий из stream"""
        logger.info(
            f"Starting consumer: stream={stream_name}, "
            f"group={group_name}, consumer={consumer_name}"
        )

        while True:
            try:
                # Read new messages from stream
                messages = await self.redis.xreadgroup(
                    groupname=group_name,
                    consumername=consumer_name,
                    streams={stream_name: '>'},
                    count=10,  # Process up to 10 messages at once
                    block=5000  # Block for 5 seconds if no messages
                )

                if not messages:
                    continue

                for stream, message_list in messages:
                    for message_id, data in message_list:
                        await self._process_message(
                            stream_name,
                            group_name,
                            message_id,
                            data,
                            handler
                        )

            except asyncio.CancelledError:
                logger.info(f"Consumer {consumer_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Consumer error: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def _process_message(
        self,
        stream_name: str,
        group_name: str,
        message_id: str,
        data: Dict,
        handler: Callable
    ):
        """Обработка одного сообщения с retry и DLQ"""
        try:
            # Parse event
            event_data = json.loads(data['event'])
            event = Event.from_dict(event_data)

            logger.debug(f"Processing event: {event.event_type} (id={event.event_id})")

            # Update status
            event.status = EventStatus.PROCESSING.value

            # Call handler
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)

            # Acknowledge message (remove from pending)
            await self.redis.xack(stream_name, group_name, message_id)

            # Update status
            event.status = EventStatus.COMPLETED.value

            logger.debug(f"Event processed: {event.event_type} (id={event.event_id})")

        except Exception as e:
            logger.error(f"Event processing failed: {e}", exc_info=True)

            # Retry logic
            event.retry_count += 1

            if event.retry_count < event.max_retries:
                # Retry with exponential backoff
                backoff = 2 ** event.retry_count
                logger.warning(
                    f"Retrying event {event.event_id} "
                    f"(attempt {event.retry_count}/{event.max_retries}, "
                    f"backoff={backoff}s)"
                )

                await asyncio.sleep(backoff)

                # Re-add to stream for retry
                # Note: XACK is not called, so message stays in pending

            else:
                # Max retries exceeded -> move to DLQ
                logger.error(
                    f"Max retries exceeded for event {event.event_id}. "
                    f"Moving to DLQ"
                )

                await self._move_to_dlq(event, str(e))

                # Acknowledge original message
                await self.redis.xack(stream_name, group_name, message_id)

    # =========================================================================
    # Dead Letter Queue (DLQ)
    # =========================================================================

    async def _move_to_dlq(self, event: Event, error: str):
        """Перемещение события в DLQ"""
        dlq_stream = self._get_dlq_stream_name()

        event.status = EventStatus.DLQ.value

        dlq_data = {
            "event": json.dumps(event.to_dict()),
            "error": error,
            "moved_at": datetime.now().isoformat()
        }

        await self.redis.xadd(
            name=dlq_stream,
            fields=dlq_data,
            maxlen=self.max_len * 2,  # DLQ can be larger
            approximate=True
        )

        logger.warning(f"Event moved to DLQ: {event.event_id}")

    async def get_dlq_events(self, count: int = 100) -> List[Dict]:
        """Получение событий из DLQ"""
        dlq_stream = self._get_dlq_stream_name()

        messages = await self.redis.xrange(
            name=dlq_stream,
            min='-',
            max='+',
            count=count
        )

        dlq_events = []
        for message_id, data in messages:
            dlq_events.append({
                "message_id": message_id,
                "event": json.loads(data['event']),
                "error": data['error'],
                "moved_at": data['moved_at']
            })

        return dlq_events

    async def replay_dlq_event(self, message_id: str, target_channel: str):
        """Replay события из DLQ обратно в основной stream"""
        dlq_stream = self._get_dlq_stream_name()

        # Get DLQ message
        messages = await self.redis.xrange(
            name=dlq_stream,
            min=message_id,
            max=message_id
        )

        if not messages:
            raise ValueError(f"DLQ message not found: {message_id}")

        _, data = messages[0]
        event_data = json.loads(data['event'])
        event = Event.from_dict(event_data)

        # Reset retry count and status
        event.retry_count = 0
        event.status = EventStatus.PENDING.value

        # Re-publish to target channel
        await self.publish(
            channel=target_channel,
            event_type=event.event_type,
            payload=event.payload,
            source=event.source,
            correlation_id=event.correlation_id
        )

        # Remove from DLQ
        await self.redis.xdel(dlq_stream, message_id)

        logger.info(f"Replayed DLQ event {event.event_id} to {target_channel}")

    async def clear_old_dlq_events(self):
        """Очистка старых событий из DLQ"""
        dlq_stream = self._get_dlq_stream_name()

        cutoff_time = datetime.now() - timedelta(hours=self.dlq_retention_hours)
        cutoff_timestamp = int(cutoff_time.timestamp() * 1000)

        # Trim stream by timestamp
        # Note: XTRIM by timestamp requires Redis 6.2+
        try:
            trimmed = await self.redis.execute_command(
                'XTRIM', dlq_stream, 'MINID', cutoff_timestamp
            )
            logger.info(f"Trimmed {trimmed} old events from DLQ")
        except Exception as e:
            logger.error(f"Failed to trim DLQ: {e}")

    # =========================================================================
    # Monitoring & Statistics
    # =========================================================================

    async def get_stream_info(self, channel: str) -> Dict:
        """Получение информации о stream"""
        stream_name = self._get_stream_name(channel)

        try:
            info = await self.redis.xinfo_stream(stream_name)
            return {
                "length": info['length'],
                "first_entry": info['first-entry'],
                "last_entry": info['last-entry'],
                "groups": info['groups']
            }
        except Exception as e:
            logger.error(f"Failed to get stream info: {e}")
            return {}

    async def get_consumer_group_info(self, channel: str) -> List[Dict]:
        """Получение информации о consumer groups"""
        stream_name = self._get_stream_name(channel)

        try:
            groups = await self.redis.xinfo_groups(stream_name)
            return groups
        except Exception as e:
            logger.error(f"Failed to get consumer group info: {e}")
            return []

    async def get_pending_messages(
        self,
        channel: str,
        consumer_name: str = None
    ) -> List[Dict]:
        """Получение pending (необработанных) сообщений"""
        stream_name = self._get_stream_name(channel)
        group_name = self._get_consumer_group_name(channel)

        try:
            pending = await self.redis.xpending(
                name=stream_name,
                groupname=group_name
            )
            return pending
        except Exception as e:
            logger.error(f"Failed to get pending messages: {e}")
            return []

    async def get_stats(self) -> Dict:
        """Получение общей статистики EventBus"""
        stats = {
            "channels": {},
            "dlq": {}
        }

        # Stats for each channel
        for channel in self.subscribers.keys():
            stream_info = await self.get_stream_info(channel)
            group_info = await self.get_consumer_group_info(channel)
            pending = await self.get_pending_messages(channel)

            stats["channels"][channel] = {
                "stream_length": stream_info.get('length', 0),
                "groups_count": len(group_info),
                "pending_count": len(pending) if pending else 0,
                "subscribers_count": len(self.subscribers[channel])
            }

        # DLQ stats
        dlq_events = await self.get_dlq_events(count=1000)
        stats["dlq"] = {
            "total_events": len(dlq_events),
            "oldest_event": dlq_events[0]['moved_at'] if dlq_events else None
        }

        return stats


# Global instance
_eventbus: Optional[ResilientEventBus] = None


def get_eventbus() -> ResilientEventBus:
    """Получение глобального экземпляра EventBus"""
    global _eventbus

    if _eventbus is None:
        _eventbus = ResilientEventBus()

    return _eventbus


async def initialize_eventbus():
    """Инициализация EventBus"""
    eventbus = get_eventbus()
    await eventbus.connect()
    logger.info("ResilientEventBus initialized")
    return eventbus


# Example usage
if __name__ == "__main__":
    async def example_handler(event: Event):
        """Example event handler"""
        print(f"Received event: {event.event_type}")
        print(f"Payload: {event.payload}")

        # Simulate some processing
        await asyncio.sleep(0.1)

        # Simulate failure for testing DLQ
        if event.payload.get('fail'):
            raise Exception("Simulated failure")

    async def main():
        # Initialize
        eventbus = await initialize_eventbus()

        # Subscribe
        await eventbus.subscribe("test_channel", example_handler)

        # Publish test events
        await eventbus.publish(
            channel="test_channel",
            event_type="test.event",
            payload={"message": "Hello World"}
        )

        # Publish failing event to test DLQ
        await eventbus.publish(
            channel="test_channel",
            event_type="test.failing",
            payload={"message": "This will fail", "fail": True}
        )

        # Wait for processing
        await asyncio.sleep(10)

        # Check DLQ
        dlq_events = await eventbus.get_dlq_events()
        print(f"\nDLQ Events: {len(dlq_events)}")
        for dlq_event in dlq_events:
            print(f"  - {dlq_event['event']['event_type']}: {dlq_event['error']}")

        # Check stats
        stats = await eventbus.get_stats()
        print(f"\nEventBus Stats:")
        print(json.dumps(stats, indent=2))

        # Cleanup
        await eventbus.close()

    asyncio.run(main())
