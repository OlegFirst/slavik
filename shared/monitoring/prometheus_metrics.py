"""
Shared Prometheus Metrics for FastAPI Services
Provides standardized metrics collection for all platform services
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import Response as FastAPIResponse
import time
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Metrics Definitions
# ============================================================================

# HTTP Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'service']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint', 'service']
)

# Database metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation', 'table', 'service']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table', 'service'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Event Bus metrics
eventbus_messages_published = Counter(
    'eventbus_messages_published_total',
    'Total messages published to EventBus',
    ['event_type', 'service']
)

eventbus_messages_consumed = Counter(
    'eventbus_messages_consumed_total',
    'Total messages consumed from EventBus',
    ['event_type', 'service']
)

eventbus_processing_duration_seconds = Histogram(
    'eventbus_processing_duration_seconds',
    'Event processing duration in seconds',
    ['event_type', 'service'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Business metrics
enrollments_total = Counter(
    'enrollments_total',
    'Total enrollments created',
    ['program_type', 'tenant_id', 'service']
)

certifications_issued = Counter(
    'certifications_issued_total',
    'Total certifications issued',
    ['certification_type', 'tenant_id', 'service']
)

policies_created = Counter(
    'policies_created_total',
    'Total policies created',
    ['policy_type', 'tenant_id', 'service']
)

specialists_verified = Counter(
    'specialists_verified_total',
    'Total specialists verified',
    ['verification_source', 'tenant_id', 'service']
)

projects_matched = Counter(
    'projects_matched_total',
    'Total projects matched with specialists',
    ['match_score_range', 'tenant_id', 'service']
)


# ============================================================================
# Middleware
# ============================================================================

class PrometheusMiddleware:
    """
    FastAPI middleware for Prometheus metrics collection

    Usage:
        from shared.monitoring.prometheus_metrics import PrometheusMiddleware

        app = FastAPI()
        app.add_middleware(PrometheusMiddleware, service_name="learning-service")
    """

    def __init__(self, app, service_name: str = "unknown"):
        self.app = app
        self.service_name = service_name

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive)
        method = request.method
        path = request.url.path

        # Skip metrics endpoint itself
        if path == "/metrics":
            return await self.app(scope, receive, send)

        # Track in-progress requests
        http_requests_in_progress.labels(
            method=method,
            endpoint=path,
            service=self.service_name
        ).inc()

        start_time = time.time()

        try:
            # Process request
            await self.app(scope, receive, send)

            # Assume success if no exception
            status = 200

        except Exception as e:
            status = 500
            logger.error(f"Error processing request: {e}")
            raise

        finally:
            # Record metrics
            duration = time.time() - start_time

            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status,
                service=self.service_name
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=path,
                service=self.service_name
            ).observe(duration)

            http_requests_in_progress.labels(
                method=method,
                endpoint=path,
                service=self.service_name
            ).dec()


# ============================================================================
# Metrics Endpoint
# ============================================================================

def get_metrics_endpoint():
    """
    Returns FastAPI endpoint handler for /metrics

    Usage:
        from shared.monitoring.prometheus_metrics import get_metrics_endpoint

        @app.get("/metrics")
        async def metrics():
            return get_metrics_endpoint()
    """
    def metrics_handler():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )

    return metrics_handler


# ============================================================================
# Helper Functions
# ============================================================================

def track_db_query(operation: str, table: str, service: str):
    """
    Context manager for tracking database queries

    Usage:
        with track_db_query("SELECT", "enrollments", "learning-service"):
            result = await db.execute(query)
    """
    class DBQueryTracker:
        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time

            db_queries_total.labels(
                operation=operation,
                table=table,
                service=service
            ).inc()

            db_query_duration_seconds.labels(
                operation=operation,
                table=table,
                service=service
            ).observe(duration)

    return DBQueryTracker()


def track_event_published(event_type: str, service: str):
    """Track EventBus message publication"""
    eventbus_messages_published.labels(
        event_type=event_type,
        service=service
    ).inc()


def track_event_consumed(event_type: str, service: str, duration: float):
    """Track EventBus message consumption"""
    eventbus_messages_consumed.labels(
        event_type=event_type,
        service=service
    ).inc()

    eventbus_processing_duration_seconds.labels(
        event_type=event_type,
        service=service
    ).observe(duration)


def track_business_metric(metric_type: str, service: str, **labels):
    """
    Track business-specific metrics

    Examples:
        track_business_metric("enrollment", "learning-service", program_type="bcm", tenant_id="tenant_1")
        track_business_metric("certification", "learning-service", certification_type="practitioner", tenant_id="tenant_1")
    """
    if metric_type == "enrollment":
        enrollments_total.labels(
            program_type=labels.get("program_type", "unknown"),
            tenant_id=labels.get("tenant_id", "unknown"),
            service=service
        ).inc()

    elif metric_type == "certification":
        certifications_issued.labels(
            certification_type=labels.get("certification_type", "unknown"),
            tenant_id=labels.get("tenant_id", "unknown"),
            service=service
        ).inc()

    elif metric_type == "policy":
        policies_created.labels(
            policy_type=labels.get("policy_type", "unknown"),
            tenant_id=labels.get("tenant_id", "unknown"),
            service=service
        ).inc()

    elif metric_type == "specialist_verified":
        specialists_verified.labels(
            verification_source=labels.get("verification_source", "unknown"),
            tenant_id=labels.get("tenant_id", "unknown"),
            service=service
        ).inc()

    elif metric_type == "project_matched":
        projects_matched.labels(
            match_score_range=labels.get("match_score_range", "unknown"),
            tenant_id=labels.get("tenant_id", "unknown"),
            service=service
        ).inc()
