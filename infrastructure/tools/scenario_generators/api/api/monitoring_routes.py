"""
API routes for health monitoring and metrics
"""

from fastapi import APIRouter
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import logging
import time
from datetime import datetime

from models.requests import HealthResponse, StatisticsResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["monitoring"])

# Service start time
START_TIME = time.time()

# Prometheus metrics
generation_requests = Counter(
    'scenario_generation_requests_total',
    'Total scenario generation requests',
    ['level', 'status']
)

generation_duration = Histogram(
    'scenario_generation_duration_seconds',
    'Scenario generation duration',
    ['level']
)

scenarios_generated = Counter(
    'scenarios_generated_total',
    'Total scenarios generated',
    ['level']
)

generation_errors = Counter(
    'generation_errors_total',
    'Total generation errors',
    ['level', 'error_type']
)

service_health = Gauge(
    'scenario_orchestrator_health',
    'Service health status (1=healthy, 0=unhealthy)'
)

# Set initial health to healthy
service_health.set(1)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service health status and component availability.
    """
    uptime = time.time() - START_TIME

    # Check components
    components = {
        "api": "healthy",
        "generation_manager": "healthy",  # TODO: Real check
        "registry": "healthy",  # TODO: Real check
        "template_loader": "healthy"  # TODO: Real check
    }

    # Determine overall status
    unhealthy_components = [k for k, v in components.items() if v != "healthy"]
    if unhealthy_components:
        status = "degraded"
        service_health.set(0.5)
    else:
        status = "healthy"
        service_health.set(1)

    return HealthResponse(
        status=status,
        version="1.0.0",
        uptime_seconds=uptime,
        components=components,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Exposes metrics in Prometheus format for scraping.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/api/v1/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """
    Get scenario generation statistics.

    Returns counts by level, type, and category.
    """
    # TODO: Get real statistics from registry
    return StatisticsResponse(
        total_scenarios=46,  # Placeholder
        by_level={
            "1": 46,
            "2": 0,
            "3": 0,
            "4": 0
        },
        by_type={
            "service": 46,
            "subsystem": 0,
            "system": 0,
            "workflow": 0
        },
        by_category={
            "infrastructure": 11,
            "security": 3,
            "ai": 8,
            "intelligence": 10,
            "integration": 5,
            "business": 9
        },
        last_generation=None
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.

    Returns 200 if service is ready to accept requests.
    """
    # TODO: Check if all dependencies are available
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint.

    Returns 200 if service is alive (for Kubernetes probes).
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
