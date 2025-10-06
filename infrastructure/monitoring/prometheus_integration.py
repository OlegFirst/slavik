"""
Prometheus Integration for Monitoring Service
Экспорт метрик в Prometheus и визуализация в Grafana

Features:
- Custom metrics для BCM платформы
- Service health metrics
- Business metrics (BIA, Risk, etc.)
- Auto-discovery новых сервисов
- Grafana dashboards
"""

from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    CollectorRegistry, generate_latest,
    CONTENT_TYPE_LATEST
)
from fastapi import Response
from typing import Dict, Any, List
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class BCMPrometheusMetrics:
    """
    Prometheus metrics для BCM Platform

    Собирает метрики:
    - Service health (up/down, response time)
    - Business metrics (BIA count, Risk count, etc.)
    - User activity
    - Performance metrics
    """

    def __init__(self):
        # Создаем отдельный registry
        self.registry = CollectorRegistry()

        # ============================================
        # INFRASTRUCTURE METRICS
        # ============================================

        # Service Health
        self.service_up = Gauge(
            'bcm_service_up',
            'Service health status (1 = up, 0 = down)',
            ['service_name', 'service_type'],
            registry=self.registry
        )

        self.service_response_time = Histogram(
            'bcm_service_response_time_seconds',
            'Service response time',
            ['service_name'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )

        # HTTP Requests
        self.http_requests_total = Counter(
            'bcm_http_requests_total',
            'Total HTTP requests',
            ['service', 'method', 'endpoint', 'status_code'],
            registry=self.registry
        )

        self.http_request_duration = Histogram(
            'bcm_http_request_duration_seconds',
            'HTTP request duration',
            ['service', 'method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )

        # ============================================
        # EVENT BUS METRICS
        # ============================================

        self.events_published_total = Counter(
            'bcm_events_published_total',
            'Total events published to EventBus',
            ['event_type', 'tenant_id'],
            registry=self.registry
        )

        self.events_consumed_total = Counter(
            'bcm_events_consumed_total',
            'Total events consumed from EventBus',
            ['event_type', 'consumer'],
            registry=self.registry
        )

        self.event_processing_duration = Histogram(
            'bcm_event_processing_duration_seconds',
            'Event processing duration',
            ['event_type'],
            buckets=[0.01, 0.1, 0.5, 1.0, 5.0, 10.0],
            registry=self.registry
        )

        # ============================================
        # BUSINESS METRICS
        # ============================================

        # BIA (Business Impact Analysis)
        self.bia_total = Gauge(
            'bcm_bia_total',
            'Total BIA analyses',
            ['tenant_id', 'status'],
            registry=self.registry
        )

        self.bia_rto_average = Gauge(
            'bcm_bia_rto_average_hours',
            'Average RTO (Recovery Time Objective)',
            ['tenant_id'],
            registry=self.registry
        )

        self.bia_rpo_average = Gauge(
            'bcm_bia_rpo_average_hours',
            'Average RPO (Recovery Point Objective)',
            ['tenant_id'],
            registry=self.registry
        )

        # Risk Management
        self.risks_total = Gauge(
            'bcm_risks_total',
            'Total risks',
            ['tenant_id', 'severity', 'status'],
            registry=self.registry
        )

        self.risk_score_average = Gauge(
            'bcm_risk_score_average',
            'Average risk score',
            ['tenant_id'],
            registry=self.registry
        )

        # Compliance
        self.compliance_score = Gauge(
            'bcm_compliance_score',
            'Compliance score (0-100)',
            ['tenant_id', 'framework'],
            registry=self.registry
        )

        # Incident Response
        self.incidents_total = Counter(
            'bcm_incidents_total',
            'Total incidents',
            ['tenant_id', 'severity', 'status'],
            registry=self.registry
        )

        self.incident_response_time = Histogram(
            'bcm_incident_response_time_minutes',
            'Incident response time',
            ['tenant_id', 'severity'],
            buckets=[5, 15, 30, 60, 120, 240],
            registry=self.registry
        )

        # ============================================
        # USER METRICS
        # ============================================

        self.active_users = Gauge(
            'bcm_active_users',
            'Active users in the system',
            ['tenant_id', 'role'],
            registry=self.registry
        )

        self.user_sessions = Gauge(
            'bcm_user_sessions',
            'Active user sessions',
            ['tenant_id'],
            registry=self.registry
        )

        # ============================================
        # AI METRICS
        # ============================================

        self.ai_requests_total = Counter(
            'bcm_ai_requests_total',
            'Total AI requests',
            ['ai_service', 'model', 'tenant_id'],
            registry=self.registry
        )

        self.ai_request_duration = Histogram(
            'bcm_ai_request_duration_seconds',
            'AI request duration',
            ['ai_service', 'model'],
            buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
            registry=self.registry
        )

        self.ai_tokens_used = Counter(
            'bcm_ai_tokens_used_total',
            'Total AI tokens used',
            ['ai_service', 'model', 'tenant_id'],
            registry=self.registry
        )

        # ============================================
        # DATABASE METRICS
        # ============================================

        self.db_queries_total = Counter(
            'bcm_db_queries_total',
            'Total database queries',
            ['database', 'operation'],
            registry=self.registry
        )

        self.db_query_duration = Histogram(
            'bcm_db_query_duration_seconds',
            'Database query duration',
            ['database', 'operation'],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry
        )

        self.db_connections = Gauge(
            'bcm_db_connections',
            'Active database connections',
            ['database', 'state'],
            registry=self.registry
        )

        # ============================================
        # CACHE METRICS
        # ============================================

        self.cache_hits_total = Counter(
            'bcm_cache_hits_total',
            'Total cache hits',
            ['cache_name'],
            registry=self.registry
        )

        self.cache_misses_total = Counter(
            'bcm_cache_misses_total',
            'Total cache misses',
            ['cache_name'],
            registry=self.registry
        )

        self.cache_size_bytes = Gauge(
            'bcm_cache_size_bytes',
            'Cache size in bytes',
            ['cache_name'],
            registry=self.registry
        )

        logger.info("✅ Prometheus metrics initialized")

    # ============================================
    # HELPER METHODS
    # ============================================

    def record_service_health(self, service_name: str, service_type: str, is_up: bool):
        """Записать статус сервиса"""
        self.service_up.labels(
            service_name=service_name,
            service_type=service_type
        ).set(1 if is_up else 0)

    def record_service_response_time(self, service_name: str, duration: float):
        """Записать время ответа сервиса"""
        self.service_response_time.labels(
            service_name=service_name
        ).observe(duration)

    def record_http_request(
        self,
        service: str,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """Записать HTTP request"""
        self.http_requests_total.labels(
            service=service,
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        self.http_request_duration.labels(
            service=service,
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def record_event_published(self, event_type: str, tenant_id: str):
        """Записать опубликованное событие"""
        self.events_published_total.labels(
            event_type=event_type,
            tenant_id=tenant_id
        ).inc()

    def record_event_consumed(self, event_type: str, consumer: str, duration: float):
        """Записать обработанное событие"""
        self.events_consumed_total.labels(
            event_type=event_type,
            consumer=consumer
        ).inc()

        self.event_processing_duration.labels(
            event_type=event_type
        ).observe(duration)

    def update_bia_metrics(self, tenant_id: str, total: int, status: str, avg_rto: float, avg_rpo: float):
        """Обновить BIA метрики"""
        self.bia_total.labels(
            tenant_id=tenant_id,
            status=status
        ).set(total)

        self.bia_rto_average.labels(tenant_id=tenant_id).set(avg_rto)
        self.bia_rpo_average.labels(tenant_id=tenant_id).set(avg_rpo)

    def update_risk_metrics(self, tenant_id: str, total: int, severity: str, status: str, avg_score: float):
        """Обновить Risk метрики"""
        self.risks_total.labels(
            tenant_id=tenant_id,
            severity=severity,
            status=status
        ).set(total)

        self.risk_score_average.labels(tenant_id=tenant_id).set(avg_score)

    def record_ai_request(self, ai_service: str, model: str, tenant_id: str, duration: float, tokens: int):
        """Записать AI request"""
        self.ai_requests_total.labels(
            ai_service=ai_service,
            model=model,
            tenant_id=tenant_id
        ).inc()

        self.ai_request_duration.labels(
            ai_service=ai_service,
            model=model
        ).observe(duration)

        self.ai_tokens_used.labels(
            ai_service=ai_service,
            model=model,
            tenant_id=tenant_id
        ).inc(tokens)

    def get_metrics(self) -> bytes:
        """Получить метрики в Prometheus format"""
        return generate_latest(self.registry)

    def get_metrics_response(self) -> Response:
        """Получить FastAPI Response с метриками"""
        return Response(
            content=self.get_metrics(),
            media_type=CONTENT_TYPE_LATEST
        )


# Singleton instance
_metrics: BCMPrometheusMetrics = None


def get_metrics() -> BCMPrometheusMetrics:
    """Получить singleton instance метрик"""
    global _metrics
    if _metrics is None:
        _metrics = BCMPrometheusMetrics()
    return _metrics


# Decorator для автоматического измерения времени выполнения
def track_time(metric_func):
    """
    Decorator для отслеживания времени выполнения

    Usage:
        @track_time(lambda duration: metrics.record_service_response_time("my-service", duration))
        async def my_function():
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                metric_func(duration)
                return result
            except Exception as e:
                duration = time.time() - start
                metric_func(duration)
                raise
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    metrics = get_metrics()

    # Record service health
    metrics.record_service_health("eventbus", "platform", True)
    metrics.record_service_health("ai_intelligence", "intelligence", True)

    # Record HTTP request
    metrics.record_http_request(
        service="api_gateway",
        method="POST",
        endpoint="/api/bia",
        status_code=201,
        duration=0.125
    )

    # Record event
    metrics.record_event_published("bcm.bia.created", "tenant_123")
    metrics.record_event_consumed("bcm.bia.created", "analytics_service", 0.05)

    # Update business metrics
    metrics.update_bia_metrics(
        tenant_id="tenant_123",
        total=42,
        status="completed",
        avg_rto=4.5,
        avg_rpo=2.0
    )

    # Record AI request
    metrics.record_ai_request(
        ai_service="claude",
        model="claude-3-5-sonnet",
        tenant_id="tenant_123",
        duration=2.5,
        tokens=1500
    )

    # Print metrics
    print(metrics.get_metrics().decode())
