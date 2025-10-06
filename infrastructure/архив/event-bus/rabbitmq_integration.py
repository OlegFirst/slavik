"""
RabbitMQ Integration for EventBus
Объединяет FastAPI EventBus с RabbitMQ для distributed event processing

Features:
- Автоматическая публикация событий в RabbitMQ
- Подписка на события из RabbitMQ
- Fallback на Redis если RabbitMQ недоступен
- Event replay и retry mechanism
"""

import asyncio
import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from message_queue.rabbitmq_manager import RabbitMQManager, get_rabbitmq_manager

logger = logging.getLogger(__name__)


class EventBusRabbitMQBridge:
    """
    Мост между EventBus (FastAPI) и RabbitMQ

    Автоматически:
    - Публикует события из EventBus в RabbitMQ
    - Доставляет события из RabbitMQ в EventBus subscribers
    - Обеспечивает fault tolerance через Redis fallback
    """

    def __init__(
        self,
        rabbitmq_url: Optional[str] = None,
        exchange_name: str = "bcm_events",
        enable_fallback: bool = True
    ):
        self.rabbitmq_url = rabbitmq_url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
        self.exchange_name = exchange_name
        self.enable_fallback = enable_fallback

        self.mq: Optional[RabbitMQManager] = None
        self.is_connected = False
        self.subscribers: Dict[str, list] = {}  # routing_key -> [callbacks]

    async def connect(self):
        """Подключение к RabbitMQ"""
        try:
            self.mq = await get_rabbitmq_manager(self.rabbitmq_url)
            self.is_connected = True
            logger.info("✅ EventBus connected to RabbitMQ")

        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            if not self.enable_fallback:
                raise
            logger.warning("⚠️  Using Redis fallback mode")
            self.is_connected = False

    async def disconnect(self):
        """Отключение от RabbitMQ"""
        if self.mq:
            await self.mq.disconnect()
            self.is_connected = False

    async def publish_event(
        self,
        event_type: str,
        tenant_id: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        priority: int = 0
    ):
        """
        Публикация события в RabbitMQ

        Args:
            event_type: Тип события (например: "bcm.bia.completed")
            tenant_id: Tenant ID
            data: Payload события
            user_id: User ID (optional)
            correlation_id: Correlation ID для tracing
            priority: Приоритет (0-9)
        """
        # Собираем полное событие
        event = {
            "event_type": event_type,
            "tenant_id": tenant_id,
            "data": data,
            "user_id": user_id,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        if not self.is_connected or not self.mq:
            logger.warning(f"⚠️  RabbitMQ not connected, event '{event_type}' not published to queue")
            # Событие уже в Redis через EventBus, просто логируем
            return False

        try:
            # Публикуем в RabbitMQ с routing key = event_type
            await self.mq.publish(
                routing_key=event_type,
                message=event,
                priority=priority
            )

            logger.debug(f"📤 Event '{event_type}' published to RabbitMQ (tenant: {tenant_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to publish event to RabbitMQ: {e}")
            if not self.enable_fallback:
                raise
            return False

    async def subscribe(
        self,
        event_pattern: str,
        callback: Callable,
        queue_name: Optional[str] = None
    ):
        """
        Подписка на события из RabbitMQ

        Args:
            event_pattern: Паттерн событий (например: "bcm.bia.*" или "bcm.#")
            callback: Async функция для обработки события
            queue_name: Имя очереди (опционально)
        """
        if not self.is_connected or not self.mq:
            logger.warning(f"⚠️  RabbitMQ not connected, cannot subscribe to '{event_pattern}'")
            return

        # Сохраняем callback
        if event_pattern not in self.subscribers:
            self.subscribers[event_pattern] = []
        self.subscribers[event_pattern].append(callback)

        # Оборачиваем callback для обработки ошибок
        async def wrapped_callback(message: dict):
            try:
                event = message.get("data", message)
                await callback(event)
            except Exception as e:
                logger.error(f"❌ Error in subscriber callback for '{event_pattern}': {e}")

        # Подписываемся в RabbitMQ
        try:
            await self.mq.subscribe(
                routing_key=event_pattern,
                callback=wrapped_callback,
                queue_name=queue_name or f"eventbus.{event_pattern}"
            )

            logger.info(f"📡 Subscribed to RabbitMQ pattern: '{event_pattern}'")

        except Exception as e:
            logger.error(f"❌ Failed to subscribe to RabbitMQ: {e}")
            raise

    async def create_work_queue_handler(
        self,
        queue_name: str,
        callback: Callable
    ):
        """
        Создать Work Queue для фоновых задач

        Используется для долгих операций (reports, simulations, etc.)
        """
        if not self.is_connected or not self.mq:
            logger.warning(f"⚠️  RabbitMQ not connected, cannot create work queue '{queue_name}'")
            return

        try:
            await self.mq.create_work_queue(
                queue_name=queue_name,
                callback=callback
            )

            logger.info(f"🔧 Work queue created: '{queue_name}'")

        except Exception as e:
            logger.error(f"❌ Failed to create work queue: {e}")
            raise

    async def submit_task(
        self,
        queue_name: str,
        task: Dict[str, Any],
        priority: int = 0
    ):
        """
        Отправить задачу в Work Queue
        """
        if not self.is_connected or not self.mq:
            logger.warning(f"⚠️  RabbitMQ not connected, task for '{queue_name}' not submitted")
            return False

        try:
            await self.mq.publish_task(
                queue_name=queue_name,
                task=task,
                priority=priority
            )

            logger.debug(f"📋 Task submitted to '{queue_name}'")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to submit task: {e}")
            return False


# Singleton instance
_bridge: Optional[EventBusRabbitMQBridge] = None


async def get_eventbus_rabbitmq_bridge() -> EventBusRabbitMQBridge:
    """Получить singleton instance моста"""
    global _bridge

    if _bridge is None:
        _bridge = EventBusRabbitMQBridge()
        await _bridge.connect()

    return _bridge


# Helper functions для использования в EventBus main.py

async def publish_to_rabbitmq(
    event_type: str,
    tenant_id: str,
    data: Dict[str, Any],
    **kwargs
):
    """
    Удобная функция для публикации в RabbitMQ
    Вызывается после публикации в Redis
    """
    try:
        bridge = await get_eventbus_rabbitmq_bridge()
        await bridge.publish_event(
            event_type=event_type,
            tenant_id=tenant_id,
            data=data,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Failed to publish to RabbitMQ: {e}")


async def setup_rabbitmq_subscribers():
    """
    Настройка подписчиков RabbitMQ
    Вызывается при старте EventBus
    """
    try:
        bridge = await get_eventbus_rabbitmq_bridge()

        # Примеры подписок для distributed processing

        # 1. BIA events -> Analytics service
        await bridge.subscribe(
            event_pattern="bcm.bia.*",
            callback=forward_to_analytics
        )

        # 2. Risk events -> Compliance service
        await bridge.subscribe(
            event_pattern="bcm.risk.*",
            callback=forward_to_compliance
        )

        # 3. All critical events -> Monitoring
        await bridge.subscribe(
            event_pattern="*.critical",
            callback=forward_to_monitoring
        )

        logger.info("✅ RabbitMQ subscribers configured")

    except Exception as e:
        logger.error(f"❌ Failed to setup RabbitMQ subscribers: {e}")


async def forward_to_analytics(event: dict):
    """Forward BIA events to analytics service"""
    logger.info(f"📊 Forwarding to analytics: {event.get('event_type')}")
    # Implement forwarding logic


async def forward_to_compliance(event: dict):
    """Forward risk events to compliance service"""
    logger.info(f"📋 Forwarding to compliance: {event.get('event_type')}")
    # Implement forwarding logic


async def forward_to_monitoring(event: dict):
    """Forward critical events to monitoring"""
    logger.warning(f"🚨 Critical event: {event.get('event_type')}")
    # Implement forwarding logic


# Example usage
if __name__ == "__main__":
    async def example():
        # Создать мост
        bridge = EventBusRabbitMQBridge()
        await bridge.connect()

        # Publisher: отправить событие
        await bridge.publish_event(
            event_type="bcm.bia.completed",
            tenant_id="tenant_123",
            data={
                "bia_id": 456,
                "rto": 4,
                "rpo": 2,
                "status": "completed"
            },
            priority=5
        )

        # Consumer: подписаться на события
        async def handle_bia_event(event: dict):
            print(f"BIA Event received: {event}")

        await bridge.subscribe("bcm.bia.*", handle_bia_event)

        # Work Queue: создать очередь для тяжелых задач
        async def process_report(task: dict):
            print(f"Generating report: {task}")
            await asyncio.sleep(2)  # Simulate work

        await bridge.create_work_queue_handler("report_tasks", process_report)

        # Отправить задачу
        await bridge.submit_task(
            "report_tasks",
            {
                "report_type": "compliance",
                "tenant_id": "tenant_123",
                "period": "Q1-2025"
            },
            priority=8
        )

        # Ждем обработки
        await asyncio.sleep(5)

        await bridge.disconnect()

    asyncio.run(example())
