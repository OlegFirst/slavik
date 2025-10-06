"""
Health & Status Endpoints

System health checks and status monitoring
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Request
from pydantic import BaseModel

from storage import PostgreSQLStorage, RedisCache

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# RESPONSE MODELS
# ============================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    services: dict


class StatisticsResponse(BaseModel):
    """Statistics response"""
    database: dict
    cache: dict
    timestamp: str


# ============================================
# ENDPOINTS
# ============================================

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(request: Request):
    """
    Health check endpoint

    Returns health status of all services
    """
    storage: PostgreSQLStorage = request.app.state.app_state.storage
    cache: RedisCache = request.app.state.app_state.cache

    try:
        # Check PostgreSQL
        pg_healthy = await storage.health_check()

        # Check Redis
        redis_healthy = await cache.health_check()

        # Overall status
        overall_status = "healthy" if (pg_healthy and redis_healthy) else "degraded"

        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            services={
                "database": {
                    "status": "healthy" if pg_healthy else "unhealthy",
                    "type": "PostgreSQL"
                },
                "cache": {
                    "status": "healthy" if redis_healthy else "unhealthy",
                    "type": "Redis"
                }
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            services={
                "database": {"status": "unknown", "type": "PostgreSQL"},
                "cache": {"status": "unknown", "type": "Redis"},
                "error": str(e)
            }
        )


@router.get("/status")
async def get_status(request: Request):
    """
    Get service status

    Returns detailed service information
    """
    return {
        "service": "Digital Twin Universal Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": request.app.state.app_state.config.get('environment', 'development'),
        "features": {
            "organizations": "enabled",
            "simulations": "enabled",
            "metrics": "enabled",
            "predictions": "enabled",
            "theory_of_change": "enabled",
            "impact_passport": "enabled"
        }
    }


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(request: Request):
    """
    Get service statistics

    Returns usage statistics from database and cache
    """
    storage: PostgreSQLStorage = request.app.state.app_state.storage
    cache: RedisCache = request.app.state.app_state.cache

    try:
        # Get database statistics
        db_stats = await storage.get_statistics()

        # Get cache statistics
        cache_stats = await cache.get_statistics()

        return StatisticsResponse(
            database=db_stats,
            cache=cache_stats,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}", exc_info=True)
        return StatisticsResponse(
            database={"error": str(e)},
            cache={"error": str(e)},
            timestamp=datetime.utcnow().isoformat()
        )


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint

    Returns pong for basic connectivity check
    """
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/readiness")
async def readiness_check(request: Request):
    """
    Readiness check

    Returns whether service is ready to accept requests
    """
    storage: PostgreSQLStorage = request.app.state.app_state.storage
    cache: RedisCache = request.app.state.app_state.cache

    try:
        # Check if connections are established
        pg_ready = await storage.health_check()
        redis_ready = await cache.health_check()

        is_ready = pg_ready and redis_ready

        return {
            "ready": is_ready,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": pg_ready,
                "cache": redis_ready
            }
        }

    except Exception as e:
        logger.error(f"Readiness check failed: {e}", exc_info=True)
        return {
            "ready": False,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/liveness")
async def liveness_check():
    """
    Liveness check

    Returns whether service is alive (for Kubernetes)
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
