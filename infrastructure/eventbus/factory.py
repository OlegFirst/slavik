"""
EventBus Factory
================

Factory for creating EventBus instances with pluggable backends.

Supports:
    - memory: In-memory (testing, MVP)
    - redis: Redis Streams (production)

Future:
    - rabbitmq: RabbitMQ (advanced routing)
"""

from typing import Optional
from infrastructure.eventbus.core.interface import IEventBus
from infrastructure.eventbus.backends.memory import InMemoryEventBus
from infrastructure.eventbus.backends.redis_streams import RedisStreamEventBus


def create_eventbus(
    backend: str = 'memory',
    **config
) -> IEventBus:
    """
    Factory for creating EventBus instances.

    Args:
        backend: Backend type ('memory' or 'redis')
        **config: Backend-specific configuration

    Returns:
        IEventBus: EventBus instance

    Raises:
        ValueError: If backend type unknown

    Examples:
        ```python
        # In-memory (testing, MVP)
        bus = create_eventbus('memory')

        # Redis Streams (production)
        bus = create_eventbus('redis', redis_url='redis://localhost:6379')

        # From environment
        import os
        bus = create_eventbus(
            backend=os.getenv('EVENTBUS_BACKEND', 'memory'),
            redis_url=os.getenv('REDIS_URL')
        )
        ```

    Configuration Options:

        Memory Backend:
            No configuration needed

        Redis Backend:
            - redis_url: Redis connection URL (default: 'redis://localhost:6379')
    """

    if backend == 'memory':
        return InMemoryEventBus()

    elif backend == 'redis':
        redis_url = config.get('redis_url', 'redis://localhost:6379')
        return RedisStreamEventBus(redis_url)

    else:
        raise ValueError(
            f"Unknown EventBus backend: '{backend}'. "
            f"Supported: 'memory', 'redis'"
        )


def create_eventbus_from_env() -> IEventBus:
    """
    Create EventBus from environment variables.

    Environment Variables:
        EVENTBUS_BACKEND: Backend type ('memory' or 'redis')
        REDIS_URL: Redis connection URL (for redis backend)

    Returns:
        IEventBus: EventBus instance

    Example:
        ```bash
        # .env file
        EVENTBUS_BACKEND=redis
        REDIS_URL=redis://localhost:6379
        ```

        ```python
        # In your app
        bus = create_eventbus_from_env()
        ```
    """
    import os

    backend = os.getenv('EVENTBUS_BACKEND', 'memory')
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

    return create_eventbus(
        backend=backend,
        redis_url=redis_url
    )
