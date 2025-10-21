"""
RabbitMQ Manager
Асинхронная очередь сообщений для event-driven архитектуры

Features:
- Publish/Subscribe pattern
- Work Queues (task distribution)
- Topic-based routing
- Dead Letter Queue (DLQ)
- Message persistence
- Auto-reconnection
"""

import asyncio
import json
import logging
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue

logger = logging.getLogger(__name__)


class RabbitMQManager:
    """
    RabbitMQ Manager для асинхронной обработки сообщений

    Usage:
        # Publisher
        mq = RabbitMQManager("amqp://user:password@localhost/")
        await mq.connect()
        await mq.publish("events", "user.created", {"user_id": "123"})

        # Consumer
        async def handle_message(message: dict):
            print(f"Received: {message}")

        await mq.subscribe("events", "user.*", handle_message)
    """

    def __init__(
        self,
        url: str = "amqp://guest:guest@localhost/",
        exchange_name: str = "bcm_events",
        exchange_type: ExchangeType = ExchangeType.TOPIC,
        prefetch_count: int = 10
    ):
        self.url = url
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.prefetch_count = prefetch_count

        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.exchange = None
        self.consumers: Dict[str, AbstractQueue] = {}

    async def connect(self):
        """Подключение к RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(
                self.url,
                timeout=30,
                heartbeat=60
            )

            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=self.prefetch_count)

            # Создаем exchange
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                self.exchange_type,
                durable=True
            )

            logger.info(f" Connected to RabbitMQ: {self.url}")

        except Exception as e:
            logger.error(f" Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self):
        """Отключение от RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")

    async def publish(
        self,
        routing_key: str,
        message: Dict[str, Any],
        priority: int = 0,
        ttl: Optional[int] = None
    ):
        """
        Публикация сообщения

        Args:
            routing_key: Ключ маршрутизации (например: "user.created")
            message: Данные сообщения
            priority: Приоритет (0-9, где 9 - высший)
            ttl: Time to live в миллисекундах
        """
        if not self.exchange:
            raise RuntimeError("Not connected to RabbitMQ")

        # Добавляем метаданные
        enriched_message = {
            "data": message,
            "metadata": {
                "routing_key": routing_key,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": priority
            }
        }

        # Создаем сообщение
        msg = Message(
            body=json.dumps(enriched_message).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=priority,
            expiration=ttl
        )

        # Публикуем
        await self.exchange.publish(
            msg,
            routing_key=routing_key
        )

        logger.debug(f" Published message to '{routing_key}': {message}")

    async def subscribe(
        self,
        routing_key: str,
        callback: Callable,
        queue_name: Optional[str] = None,
        durable: bool = True,
        auto_delete: bool = False
    ):
        """
        Подписка на сообщения

        Args:
            routing_key: Паттерн маршрутизации (например: "user.*")
            callback: Async функция для обработки сообщений
            queue_name: Имя очереди (если None, генерируется автоматически)
            durable: Сохранять очередь при перезапуске
            auto_delete: Удалять очередь когда нет подписчиков
        """
        if not self.channel or not self.exchange:
            raise RuntimeError("Not connected to RabbitMQ")

        # Создаем очередь
        queue_name = queue_name or f"{self.exchange_name}.{routing_key}"
        queue = await self.channel.declare_queue(
            queue_name,
            durable=durable,
            auto_delete=auto_delete
        )

        # Привязываем к exchange
        await queue.bind(self.exchange, routing_key=routing_key)

        # Обработчик сообщений
        async def message_handler(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    # Декодируем JSON
                    body = json.loads(message.body.decode())

                    # Вызываем callback
                    await callback(body)

                    logger.debug(f" Processed message from '{routing_key}'")

                except Exception as e:
                    logger.error(f" Error processing message: {e}")
                    # Сообщение будет отправлено в DLQ если настроено
                    raise

        # Запускаем consumer
        await queue.consume(message_handler)

        self.consumers[routing_key] = queue
        logger.info(f" Subscribed to '{routing_key}' on queue '{queue_name}'")

    async def create_work_queue(
        self,
        queue_name: str,
        callback: Callable,
        max_priority: int = 10
    ):
        """
        Создание Work Queue для распределения задач между воркерами

        Args:
            queue_name: Имя очереди задач
            callback: Async функция для обработки задач
            max_priority: Максимальный приоритет (0-255)
        """
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")

        # Создаем очередь с приоритетами
        queue = await self.channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-max-priority": max_priority,
                # Dead Letter Exchange для failed tasks
                "x-dead-letter-exchange": f"{queue_name}.dlx",
                "x-dead-letter-routing-key": "failed"
            }
        )

        # Создаем DLX и DLQ
        dlx = await self.channel.declare_exchange(
            f"{queue_name}.dlx",
            ExchangeType.DIRECT,
            durable=True
        )

        dlq = await self.channel.declare_queue(
            f"{queue_name}.dlq",
            durable=True
        )

        await dlq.bind(dlx, routing_key="failed")

        # Обработчик задач
        async def task_handler(message: aio_pika.IncomingMessage):
            async with message.process(requeue=False):
                try:
                    body = json.loads(message.body.decode())
                    await callback(body)
                    logger.debug(f" Task completed: {queue_name}")
                except Exception as e:
                    logger.error(f" Task failed: {e}")
                    # Сообщение пойдет в DLQ
                    raise

        await queue.consume(task_handler)

        self.consumers[queue_name] = queue
        logger.info(f" Work queue '{queue_name}' created")

    async def publish_task(
        self,
        queue_name: str,
        task: Dict[str, Any],
        priority: int = 0
    ):
        """Публикация задачи в Work Queue"""
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")

        enriched_task = {
            "data": task,
            "metadata": {
                "queue": queue_name,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": priority
            }
        }

        msg = Message(
            body=json.dumps(enriched_task).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=priority
        )

        # Публикуем напрямую в очередь (без exchange)
        await self.channel.default_exchange.publish(
            msg,
            routing_key=queue_name
        )

        logger.debug(f" Task published to '{queue_name}': {task}")

    async def get_queue_stats(self, queue_name: str) -> Dict[str, int]:
        """Получить статистику очереди"""
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")

        queue = await self.channel.declare_queue(queue_name, passive=True)

        return {
            "message_count": queue.declaration_result.message_count,
            "consumer_count": queue.declaration_result.consumer_count
        }


# Singleton instance
_rabbitmq_manager: Optional[RabbitMQManager] = None


async def get_rabbitmq_manager(url: str = None) -> RabbitMQManager:
    """Получить singleton instance RabbitMQ Manager"""
    global _rabbitmq_manager

    if _rabbitmq_manager is None:
        import os
        url = url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
        _rabbitmq_manager = RabbitMQManager(url)
        await _rabbitmq_manager.connect()

    return _rabbitmq_manager


# Example usage
if __name__ == "__main__":
    async def example():
        # Создаем менеджер
        mq = RabbitMQManager()
        await mq.connect()

        # Publisher: отправка событий
        await mq.publish(
            routing_key="user.created",
            message={"user_id": "123", "email": "test@example.com"}
        )

        await mq.publish(
            routing_key="user.updated",
            message={"user_id": "123", "name": "John Doe"}
        )

        # Consumer: обработка событий
        async def handle_user_events(message: dict):
            print(f"User event: {message}")

        await mq.subscribe("user.*", handle_user_events)

        # Work Queue: распределение задач
        async def process_task(task: dict):
            print(f"Processing task: {task}")
            await asyncio.sleep(1)

        await mq.create_work_queue("email_tasks", process_task)

        await mq.publish_task(
            "email_tasks",
            {"to": "user@example.com", "subject": "Welcome!"},
            priority=5
        )

        # Ждем сообщения
        await asyncio.sleep(5)

        # Статистика
        stats = await mq.get_queue_stats("email_tasks")
        print(f"Queue stats: {stats}")

        await mq.disconnect()

    asyncio.run(example())
