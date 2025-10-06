"""
Deployment Service Prometheus Metrics
=====================================

Prometheus metrics for monitoring deployment service performance.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from config import config

# Service Info
deployment_info = Info(
    'deployment_service',
    'Deployment Service Information'
)
deployment_info.info({
    'version': config.SERVICE_VERSION,
    'service_name': config.SERVICE_NAME
})

# Deployment Metrics
deployments_total = Counter(
    'deployments_total',
    'Total number of deployments',
    ['status', 'strategy', 'tenant_id']
)

deployment_duration_seconds = Histogram(
    'deployment_duration_seconds',
    'Deployment duration in seconds',
    ['strategy', 'status'],
    buckets=[30, 60, 120, 300, 600, 1200, 1800, 3600]
)

services_deployed_total = Counter(
    'services_deployed_total',
    'Total number of services deployed',
    ['service_name', 'status', 'tenant_id']
)

# Service Health Metrics
service_health_status = Gauge(
    'service_health_status',
    'Current health status of services (1=healthy, 0=unhealthy)',
    ['service_name']
)

service_restart_total = Counter(
    'service_restart_total',
    'Total number of service restarts',
    ['service_name', 'success']
)

# Active Deployments
active_deployments = Gauge(
    'active_deployments',
    'Number of currently active deployments',
    ['tenant_id']
)

# Rollback Metrics
rollbacks_total = Counter(
    'rollbacks_total',
    'Total number of rollbacks executed',
    ['reason', 'success']
)

# AI Integration Metrics
ai_strategy_requests_total = Counter(
    'ai_strategy_requests_total',
    'Total AI strategy requests',
    ['success']
)

ai_strategy_duration_seconds = Histogram(
    'ai_strategy_duration_seconds',
    'AI strategy generation duration',
    buckets=[1, 2, 5, 10, 20, 30]
)

# EventBus Metrics
events_published_total = Counter(
    'events_published_total',
    'Total events published to EventBus',
    ['event_type', 'status']
)

# Error Metrics
deployment_errors_total = Counter(
    'deployment_errors_total',
    'Total deployment errors',
    ['error_type', 'service_name']
)


class MetricsCollector:
    """Helper class for collecting metrics"""

    @staticmethod
    def record_deployment_started(tenant_id: str, strategy: str):
        """Record deployment started"""
        active_deployments.labels(tenant_id=tenant_id).inc()

    @staticmethod
    def record_deployment_completed(
        tenant_id: str,
        strategy: str,
        status: str,
        duration: int
    ):
        """Record deployment completion"""
        deployments_total.labels(
            status=status,
            strategy=strategy,
            tenant_id=tenant_id
        ).inc()

        deployment_duration_seconds.labels(
            strategy=strategy,
            status=status
        ).observe(duration)

        active_deployments.labels(tenant_id=tenant_id).dec()

    @staticmethod
    def record_service_deployed(
        service_name: str,
        status: str,
        tenant_id: str
    ):
        """Record service deployment"""
        services_deployed_total.labels(
            service_name=service_name,
            status=status,
            tenant_id=tenant_id
        ).inc()

    @staticmethod
    def record_service_health(service_name: str, healthy: bool):
        """Record service health status"""
        service_health_status.labels(
            service_name=service_name
        ).set(1 if healthy else 0)

    @staticmethod
    def record_service_restart(service_name: str, success: bool):
        """Record service restart"""
        service_restart_total.labels(
            service_name=service_name,
            success=str(success)
        ).inc()

    @staticmethod
    def record_rollback(reason: str, success: bool):
        """Record rollback"""
        rollbacks_total.labels(
            reason=reason,
            success=str(success)
        ).inc()

    @staticmethod
    def record_ai_strategy_request(success: bool, duration: float):
        """Record AI strategy request"""
        ai_strategy_requests_total.labels(
            success=str(success)
        ).inc()

        if success:
            ai_strategy_duration_seconds.observe(duration)

    @staticmethod
    def record_event_published(event_type: str, success: bool):
        """Record event publication"""
        events_published_total.labels(
            event_type=event_type,
            status="success" if success else "failed"
        ).inc()

    @staticmethod
    def record_error(error_type: str, service_name: str = "unknown"):
        """Record deployment error"""
        deployment_errors_total.labels(
            error_type=error_type,
            service_name=service_name
        ).inc()
