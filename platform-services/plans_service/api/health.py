"""
Advanced Health Checks for Plans Service
Monitors all dependencies and system resources
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import asyncio
from typing import Dict, Any
from datetime import datetime
import logging

from ..database import AsyncSessionLocal
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


async def check_database() -> Dict[str, Any]:
    """Check PostgreSQL database connectivity and health"""
    try:
        start_time = asyncio.get_event_loop().time()

        async with AsyncSessionLocal() as session:
            # Simple query to verify connection
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

            # Check if we can write
            await session.execute(text("SELECT NOW()"))

        response_time = (asyncio.get_event_loop().time() - start_time) * 1000

        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "details": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "Database connection failed"
        }


async def check_eventbus() -> Dict[str, Any]:
    """Check EventBus connectivity"""
    try:
        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.EVENTBUS_URL}/health")

        response_time = (asyncio.get_event_loop().time() - start_time) * 1000

        if response.status_code == 200:
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "details": "EventBus is reachable"
            }
        else:
            return {
                "status": "degraded",
                "status_code": response.status_code,
                "details": f"EventBus returned {response.status_code}"
            }
    except httpx.TimeoutException:
        return {
            "status": "unhealthy",
            "error": "timeout",
            "details": "EventBus connection timeout"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "EventBus unreachable"
        }


async def check_planning_service() -> Dict[str, Any]:
    """Check Planning Service connectivity (dependency)"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.PLANNING_SERVICE_URL}/health")

        if response.status_code == 200:
            return {"status": "healthy", "details": "Planning Service reachable"}
        else:
            return {"status": "degraded", "status_code": response.status_code}
    except Exception as e:
        return {
            "status": "degraded",
            "details": "Planning Service unavailable (soft dependency)"
        }


@router.get("/health", status_code=200)
async def health_check():
    """
    Basic health check
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed", status_code=200)
async def detailed_health_check():
    """
    Detailed health check with all dependencies
    Returns status of database, EventBus, and other services
    """
    checks = {}
    overall_status = "healthy"

    # Run all health checks in parallel
    database_task = asyncio.create_task(check_database())
    eventbus_task = asyncio.create_task(check_eventbus())
    planning_task = asyncio.create_task(check_planning_service())

    # Wait for all checks
    checks["database"] = await database_task
    checks["eventbus"] = await eventbus_task
    checks["planning_service"] = await planning_task

    # Determine overall status
    if any(c["status"] == "unhealthy" for c in checks.values()):
        overall_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    elif any(c["status"] == "degraded" for c in checks.values()):
        overall_status = "degraded"
        http_status = status.HTTP_200_OK
    else:
        overall_status = "healthy"
        http_status = status.HTTP_200_OK

    response = {
        "status": overall_status,
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }

    return JSONResponse(content=response, status_code=http_status)


@router.get("/health/ready", status_code=200)
async def readiness_check():
    """
    Kubernetes readiness probe
    Returns 200 only if service can handle requests
    """
    # Check critical dependencies
    db_check = await check_database()

    if db_check["status"] == "healthy":
        return {
            "status": "ready",
            "service": settings.SERVICE_NAME,
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        return JSONResponse(
            content={
                "status": "not_ready",
                "reason": "Database unavailable",
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get("/health/live", status_code=200)
async def liveness_check():
    """
    Kubernetes liveness probe
    Returns 200 if process is alive (no dependency checks)
    """
    return {
        "status": "alive",
        "service": settings.SERVICE_NAME,
        "timestamp": datetime.utcnow().isoformat()
    }
