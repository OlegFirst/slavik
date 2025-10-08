"""
High-Level API Wrappers
========================

Convenient wrappers over infrastructure/eventbus for intelligent-core services.
"""

import os
import logging
from typing import Optional, Dict, Any, Callable, Awaitable
from functools import wraps
from datetime import datetime

# Import from infrastructure
from infrastructure.eventbus.factory import create_eventbus
from infrastructure.eventbus.core.events import Event
from infrastructure.eventbus.core.interface import IEventBus, EventHandler

logger = logging.getLogger(__name__)

# Global event bus instance
_event_bus: Optional[IEventBus] = None
_service_name: Optional[str] = None
_event_handlers: list = []  # Store (pattern, handler) for lazy registration


async def init_event_bus(
    service_name: str,
    redis_url: Optional[str] = None,
    backend: Optional[str] = None
) -> IEventBus:
    """
    Initialize global event bus for this service.

    This is a high-level wrapper that:
    1. Creates EventBus from infrastructure/eventbus
    2. Connects to Redis (or uses memory for testing)
    3. Auto-registers this service with Event Intelligence
    4. Registers all @subscribe_to handlers

    Args:
        service_name: Name of this service (for auto-discovery)
        redis_url: Redis URL (default: from REDIS_URL env var)
        backend: Backend type ('redis' or 'memory', default: auto-detect)

    Returns:
        IEventBus instance

    Example:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await init_event_bus(service_name="workflow-service")
            yield
            await shutdown_event_bus()
    """
    global _event_bus, _service_name

    _service_name = service_name

    # Auto-detect backend
    if backend is None:
        redis_url = redis_url or os.getenv("REDIS_URL")
        backend = "redis" if redis_url else "memory"

    # Create EventBus using infrastructure factory
    logger.info(f"Creating EventBus with backend: {backend}")

    if backend == "redis":
        redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        _event_bus = create_eventbus(backend="redis", redis_url=redis_url)
    else:
        logger.warning("Using in-memory EventBus (for testing only!)")
        _event_bus = create_eventbus(backend="memory")

    # Connect (if applicable)
    if hasattr(_event_bus, 'connect'):
        try:
            await _event_bus.connect()
            logger.info(f"✅ EventBus connected ({backend})")
        except Exception as e:
            logger.error(f"❌ Failed to connect EventBus: {e}")
            raise

    # Register all @subscribe_to handlers
    for pattern, handler in _event_handlers:
        try:
            await _event_bus.subscribe(pattern, handler)
            logger.info(f"✅ Registered handler for pattern: {pattern}")
        except Exception as e:
            logger.error(f"❌ Failed to register handler for {pattern}: {e}")

    # Auto-register service with Event Intelligence
    try:
        patterns = [p for p, _ in _event_handlers]
        await publish_event(
            event_type="service.started",
            data={
                "service_name": service_name,
                "subscriptions": patterns,
                "started_at": datetime.utcnow().isoformat(),
                "backend": backend
            },
            source=service_name
        )
        logger.info(f"✅ Service registered with Event Intelligence: {service_name}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to register with Event Intelligence: {e}")

    logger.info(f"✅ EventBus initialized for service: {service_name}")
    return _event_bus


def get_event_bus() -> Optional[IEventBus]:
    """
    Get the global event bus instance.

    Returns:
        IEventBus instance or None if not initialized

    Example:
        bus = get_event_bus()
        if bus:
            await bus.publish(event)
    """
    return _event_bus


async def publish_event(
    event_type: str,
    data: Dict[str, Any],
    source: Optional[str] = None,
    tenant_id: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> None:
    """
    Publish event to the bus.

    High-level wrapper - automatically creates Event and publishes.

    Args:
        event_type: Event type (e.g., 'workflow.completed')
        data: Event payload
        source: Service name (auto-detected if not provided)
        tenant_id: Tenant identifier
        correlation_id: Correlation ID for tracing

    Example:
        await publish_event(
            event_type="workflow.completed",
            data={"workflow_id": "123"},
            tenant_id="tenant_456"
        )
    """
    bus = get_event_bus()
    if not bus:
        logger.warning(f"EventBus not initialized - cannot publish: {event_type}")
        return

    source = source or _service_name or "unknown"

    event = Event.create(
        event_type=event_type,
        data=data,
        source=source,
        tenant_id=tenant_id,
        correlation_id=correlation_id
    )

    try:
        await bus.publish(event)
        logger.debug(f"📤 Published: {event_type} from {source}")
    except Exception as e:
        logger.error(f"❌ Failed to publish {event_type}: {e}")
        raise


def subscribe_to(
    pattern: str,
    consumer_group: Optional[str] = None
):
    """
    Decorator for subscribing to events.

    Handlers are automatically registered when init_event_bus() is called.

    Args:
        pattern: Event type pattern (supports wildcards like 'workflow.*')
        consumer_group: Optional consumer group name

    Example:
        @subscribe_to("workflow.*")
        async def on_workflow(event: Event):
            print(f"Workflow event: {event.type}")

        @subscribe_to("incident.detected", consumer_group="responders")
        async def on_incident(event: Event):
            # Load-balanced across consumer group
            pass
    """
    def decorator(func: EventHandler) -> EventHandler:
        # Store for later registration
        _event_handlers.append((pattern, func))

        @wraps(func)
        async def wrapper(event: Event):
            return await func(event)

        # Mark as event handler
        wrapper._is_event_handler = True
        wrapper._event_pattern = pattern
        wrapper._consumer_group = consumer_group

        return wrapper

    return decorator


async def shutdown_event_bus():
    """
    Shutdown the event bus.

    Call this during app shutdown.

    Example:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await init_event_bus("my-service")
            yield
            await shutdown_event_bus()
    """
    global _event_bus

    bus = get_event_bus()
    if bus:
        try:
            # Publish shutdown event
            if _service_name:
                await publish_event(
                    event_type="service.stopped",
                    data={
                        "service_name": _service_name,
                        "stopped_at": datetime.utcnow().isoformat()
                    },
                    source=_service_name
                )
        except Exception as e:
            logger.warning(f"Failed to publish shutdown event: {e}")

        # Close bus
        try:
            await bus.close()
            logger.info("✅ EventBus closed")
        except Exception as e:
            logger.error(f"Error closing EventBus: {e}")

        _event_bus = None


async def get_bus_stats() -> Dict[str, Any]:
    """
    Get EventBus statistics.

    Returns:
        Statistics dict or empty dict if bus not initialized
    """
    bus = get_event_bus()
    if bus:
        return await bus.get_stats()
    return {}
