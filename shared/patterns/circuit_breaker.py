"""
Circuit Breaker Pattern Implementation
Prevents cascade failures across services
"""

import asyncio
import logging
from typing import Callable, Any
from datetime import datetime, timedelta
from enum import Enum
from pybreaker import CircuitBreaker as PyBreakerBase, CircuitBreakerError

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


# Global circuit breakers registry
_circuit_breakers = {}


def get_circuit_breaker(
    service_name: str,
    fail_max: int = 5,
    timeout_duration: int = 60,
    expected_exception: Exception = Exception
) -> PyBreakerBase:
    """Get or create circuit breaker for service"""

    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = PyBreakerBase(
            fail_max=fail_max,
            timeout_duration=timeout_duration,
            expected_exception=expected_exception,
            name=service_name
        )

        logger.info(f"Created circuit breaker for {service_name}")

    return _circuit_breakers[service_name]


async def call_with_circuit_breaker(
    service_name: str,
    func: Callable,
    *args,
    **kwargs
) -> Any:
    """Call function with circuit breaker protection"""

    breaker = get_circuit_breaker(service_name)

    try:
        if asyncio.iscoroutinefunction(func):
            return await breaker.call(func, *args, **kwargs)
        else:
            return breaker.call(func, *args, **kwargs)
    except CircuitBreakerError:
        logger.error(f"Circuit breaker OPEN for {service_name}")
        raise ServiceUnavailableError(
            f"Service {service_name} is temporarily unavailable"
        )


class ServiceUnavailableError(Exception):
    """Service unavailable due to circuit breaker"""
    pass


# Example usage decorator
def with_circuit_breaker(service_name: str):
    """Decorator for circuit breaker protection"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await call_with_circuit_breaker(
                service_name, func, *args, **kwargs
            )
        return wrapper
    return decorator
