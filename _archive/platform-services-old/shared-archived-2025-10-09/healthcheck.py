"""
Комплексная проверка здоровья сервисов платформы
"""
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Awaitable
import asyncio
import logging

logger = logging.getLogger(__name__)


async def comprehensive_healthcheck(
    db_check: Optional[Callable[[], Awaitable[None]]] = None,
    redis_check: Optional[Callable[[], Awaitable[None]]] = None,
    qdrant_check: Optional[Callable[[], Awaitable[None]]] = None,
    service_name: str = "unknown",
) -> Dict[str, Any]:
    """
    Комплексная проверка здоровья сервиса

    Args:
        db_check: async функция для проверки БД (должна вызывать исключение при ошибке)
        redis_check: async функция для проверки Redis (должна вызывать исключение при ошибке)
        qdrant_check: async функция для проверки Qdrant (должна вызывать исключение при ошибке)
        service_name: Название сервиса для логирования

    Returns:
        Dict с результатами проверки здоровья:
        - status: "healthy", "degraded", "unhealthy"
        - timestamp: ISO timestamp проверки
        - checks: Dict с результатами каждой проверки
        - service: Название сервиса

    Example:
        >>> async def check_db():
        ...     await db.execute("SELECT 1")
        ...
        >>> health = await comprehensive_healthcheck(db_check=check_db, service_name="bia-service")
        >>> print(health["status"])
        "healthy"
    """

    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": service_name,
        "checks": {}
    }

    # Database check - критичная зависимость
    if db_check:
        try:
            await db_check()
            health["checks"]["database"] = {
                "status": "ok",
                "critical": True
            }
            logger.debug(f"{service_name}: Database check passed")
        except Exception as e:
            health["checks"]["database"] = {
                "status": "error",
                "error": str(e),
                "critical": True
            }
            health["status"] = "unhealthy"
            logger.error(f"{service_name}: Database check failed: {str(e)}")

    # Redis check - важная, но не критичная зависимость
    if redis_check:
        try:
            await redis_check()
            health["checks"]["redis"] = {
                "status": "ok",
                "critical": False
            }
            logger.debug(f"{service_name}: Redis check passed")
        except Exception as e:
            health["checks"]["redis"] = {
                "status": "error",
                "error": str(e),
                "critical": False
            }
            # Redis падение приводит к degraded статусу, но не unhealthy
            if health["status"] == "healthy":
                health["status"] = "degraded"
            logger.warning(f"{service_name}: Redis check failed: {str(e)}")

    # Qdrant check - опциональная зависимость
    if qdrant_check:
        try:
            await qdrant_check()
            health["checks"]["qdrant"] = {
                "status": "ok",
                "critical": False
            }
            logger.debug(f"{service_name}: Qdrant check passed")
        except Exception as e:
            health["checks"]["qdrant"] = {
                "status": "warning",
                "error": str(e),
                "critical": False
            }
            # Qdrant падение не меняет статус сервиса
            logger.warning(f"{service_name}: Qdrant check failed: {str(e)}")

    return health


async def simple_healthcheck(service_name: str = "unknown") -> Dict[str, Any]:
    """
    Простая проверка здоровья без зависимостей

    Args:
        service_name: Название сервиса

    Returns:
        Dict с базовым статусом здоровья
    """

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": service_name,
        "checks": {}
    }


async def check_dependency(
    check_func: Callable[[], Awaitable[None]],
    dependency_name: str,
    timeout: float = 5.0
) -> Dict[str, Any]:
    """
    Проверка одной зависимости с таймаутом

    Args:
        check_func: Async функция проверки
        dependency_name: Название зависимости
        timeout: Таймаут в секундах

    Returns:
        Dict с результатом проверки
    """

    try:
        await asyncio.wait_for(check_func(), timeout=timeout)
        return {
            "status": "ok",
            "dependency": dependency_name
        }
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "dependency": dependency_name,
            "error": f"Check timed out after {timeout}s"
        }
    except Exception as e:
        return {
            "status": "error",
            "dependency": dependency_name,
            "error": str(e)
        }
