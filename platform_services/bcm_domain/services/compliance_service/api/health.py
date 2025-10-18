"""
Health Check API
Provides service health and readiness endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Dict

from compliance.database.connection import get_db
from compliance.config.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict:
    """
    Basic health check endpoint

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict:
    """
    Readiness check - verifies database connectivity

    Returns:
        Service readiness status with database check
    """
    try:
        # Test database connection
        await db.execute("SELECT 1")

        return {
            "status": "ready",
            "service": settings.service_name,
            "version": settings.service_version,
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "service": settings.service_name,
            "version": settings.service_version,
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/info")
async def service_info() -> Dict:
    """
    Service information endpoint

    Returns:
        Detailed service information
    """
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "description": "ISO 22301:2019 Compliance Management Service",
        "features": [
            "ISO 22301 compliance assessment",
            "Evidence management with workflows",
            "Gap analysis and remediation tracking",
            "Nonconformity management",
            "Internal audit support",
            "AI-powered compliance scanning",
            "EventBus integration",
            "Multi-tenancy support"
        ],
        "endpoints": {
            "health": "/health",
            "ready": "/health/ready",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "config": {
            "ai_enabled": settings.ai_enabled,
            "eventbus_enabled": bool(settings.eventbus_url),
            "multi_tenancy": settings.enable_row_level_security
        }
    }
