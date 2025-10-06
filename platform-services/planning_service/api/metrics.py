"""
Prometheus Metrics for Planning Service
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
    'planning_service_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'planning_service_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

http_request_errors_total = Counter(
    'planning_service_http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

# Business Metrics
strategies_created_total = Counter(
    'planning_service_strategies_created_total',
    'Total strategies created',
    ['strategy_type', 'tenant_id']
)

strategies_approved_total = Counter(
    'planning_service_strategies_approved_total',
    'Total strategies approved',
    ['strategy_type', 'tenant_id']
)

cost_benefit_calculations_total = Counter(
    'planning_service_cost_benefit_calculations_total',
    'Total cost-benefit analyses performed',
    ['recommendation']
)

active_strategies_gauge = Gauge(
    'planning_service_active_strategies',
    'Number of active strategies',
    ['status', 'tenant_id']
)

# Database Metrics
db_query_duration_seconds = Histogram(
    'planning_service_db_query_duration_seconds',
    'Database query latency',
    ['operation']
)

db_connection_pool_size = Gauge(
    'planning_service_db_connection_pool_size',
    'Database connection pool size'
)

# EventBus Metrics
eventbus_events_published_total = Counter(
    'planning_service_eventbus_events_published_total',
    'Total events published to EventBus',
    ['topic', 'success']
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
def track_strategy_created(strategy_type: str, tenant_id: str):
    """Track strategy creation"""
    strategies_created_total.labels(
        strategy_type=strategy_type,
        tenant_id=tenant_id
    ).inc()


def track_strategy_approved(strategy_type: str, tenant_id: str):
    """Track strategy approval"""
    strategies_approved_total.labels(
        strategy_type=strategy_type,
        tenant_id=tenant_id
    ).inc()


def track_cost_benefit_analysis(recommendation: str):
    """Track cost-benefit analysis"""
    cost_benefit_calculations_total.labels(
        recommendation=recommendation
    ).inc()


def track_eventbus_publish(topic: str, success: bool):
    """Track EventBus event publishing"""
    eventbus_events_published_total.labels(
        topic=topic,
        success=str(success).lower()
    ).inc()
