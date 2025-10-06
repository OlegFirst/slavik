"""
EventBus Configuration
======================

Configuration utilities for EventBus.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EventBusConfig:
    """
    EventBus configuration.

    Attributes:
        backend: Backend type ('memory', 'redis', 'rabbitmq')
        redis_url: Redis connection URL
        rabbitmq_url: RabbitMQ connection URL (future)
        exchange_name: RabbitMQ exchange name (future)
    """

    backend: str = 'memory'
    redis_url: str = 'redis://localhost:6379'
    rabbitmq_url: Optional[str] = None
    exchange_name: str = 'bcm_events'

    @classmethod
    def from_env(cls) -> 'EventBusConfig':
        """
        Load configuration from environment variables.

        Environment Variables:
            EVENTBUS_BACKEND: Backend type (default: 'memory')
            REDIS_URL: Redis connection URL
            RABBITMQ_URL: RabbitMQ connection URL
            EVENTBUS_EXCHANGE: RabbitMQ exchange name

        Returns:
            EventBusConfig: Configuration instance

        Example:
            ```python
            config = EventBusConfig.from_env()
            bus = create_eventbus(
                backend=config.backend,
                redis_url=config.redis_url
            )
            ```
        """
        return cls(
            backend=os.getenv('EVENTBUS_BACKEND', 'memory'),
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
            rabbitmq_url=os.getenv('RABBITMQ_URL'),
            exchange_name=os.getenv('EVENTBUS_EXCHANGE', 'bcm_events')
        )

    def validate(self) -> None:
        """
        Validate configuration.

        Raises:
            ValueError: If configuration invalid
        """
        valid_backends = ['memory', 'redis', 'rabbitmq']

        if self.backend not in valid_backends:
            raise ValueError(
                f"Invalid backend '{self.backend}'. "
                f"Must be one of: {', '.join(valid_backends)}"
            )

        if self.backend == 'redis' and not self.redis_url:
            raise ValueError("redis_url required for redis backend")

        if self.backend == 'rabbitmq' and not self.rabbitmq_url:
            raise ValueError("rabbitmq_url required for rabbitmq backend")
