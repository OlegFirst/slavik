"""
Prometheus Metrics for Plans Service
Tracks requests, errors, latency, and business metrics
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["metrics"])

# HTTP Request Metrics
http_requests_total = Counter(
    'plans_service_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'plans_service_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

http_request_errors_total = Counter(
    'plans_service_http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

# Business Metrics
plans_created_total = Counter(
    'plans_service_plans_created_total',
    'Total plans created',
    ['plan_type', 'tenant_id']
)

plans_approved_total = Counter(
    'plans_service_plans_approved_total',
    'Total plans approved',
    ['plan_type', 'tenant_id']
)

plans_activated_total = Counter(
    'plans_service_plans_activated_total',
    'Total plans activated',
    ['activation_type', 'tenant_id']
)

procedures_created_total = Counter(
    'plans_service_procedures_created_total',
    'Total procedures created',
    ['procedure_type']
)

active_plans_gauge = Gauge(
    'plans_service_active_plans',
    'Number of active plans',
    ['status', 'tenant_id']
)

# Database Metrics
db_query_duration_seconds = Histogram(
    'plans_service_db_query_duration_seconds',
    'Database query latency',
    ['operation']
)

# EventBus Metrics
eventbus_events_published_total = Counter(
    'plans_service_eventbus_events_published_total',
    'Total events published to EventBus',
    ['topic', 'success']
)

# Validation Metrics
circular_dependency_detections_total = Counter(
    'plans_service_circular_dependency_detections_total',
    'Total circular dependency detections'
)


def track_request(method: str, endpoint: str):
    """Decorator to track HTTP requests"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "200"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "500"
                http_request_errors_total.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

        return wrapper
    return decorator


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus format
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Helper functions to track business metrics
def track_plan_created(plan_type: str, tenant_id: str):
    """Track plan creation"""
    plans_created_total.labels(
        plan_type=plan_type,
        tenant_id=tenant_id
    ).inc()


def track_plan_approved(plan_type: str, tenant_id: str):
    """Track plan approval"""
    plans_approved_total.labels(
        plan_type=plan_type,
        tenant_id=tenant_id
    ).inc()


def track_plan_activated(activation_type: str, tenant_id: str):
    """Track plan activation"""
    plans_activated_total.labels(
        activation_type=activation_type,
        tenant_id=tenant_id
    ).inc()


def track_procedure_created(procedure_type: str):
    """Track procedure creation"""
    procedures_created_total.labels(
        procedure_type=procedure_type
    ).inc()


def track_circular_dependency_detected():
    """Track circular dependency detection"""
    circular_dependency_detections_total.inc()


def track_eventbus_publish(topic: str, success: bool):
    """Track EventBus event publishing"""
    eventbus_events_published_total.labels(
        topic=topic,
        success=str(success).lower()
    ).inc()
