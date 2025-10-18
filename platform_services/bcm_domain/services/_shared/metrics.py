"""
Metrics and Observability for Self-Aware Services

Provides Prometheus metrics for all self-aware service components.
"""

import logging
from prometheus_client import Counter, Gauge, Histogram, Info
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


# Event Handling Metrics

events_received_total = Counter(
    'selfaware_events_received_total',
    'Total events received by self-aware services',
    ['service', 'event_type', 'priority']
)

events_handled_total = Counter(
    'selfaware_events_handled_total',
    'Total events handled by self-aware services',
    ['service', 'event_type', 'decision']
)

events_deferred_total = Counter(
    'selfaware_events_deferred_total',
    'Total events deferred due to load',
    ['service', 'event_type', 'reason']
)

events_delegated_total = Counter(
    'selfaware_events_delegated_total',
    'Total events delegated to other services',
    ['service', 'event_type', 'delegate_to']
)

events_rejected_total = Counter(
    'selfaware_events_rejected_total',
    'Total events rejected',
    ['service', 'event_type', 'reason']
)

event_handling_duration_seconds = Histogram(
    'selfaware_event_handling_duration_seconds',
    'Time spent handling events',
    ['service', 'event_type', 'decision'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# Health Metrics

service_health_status = Gauge(
    'selfaware_service_health_status',
    'Service health status (0=down, 1=degraded, 2=healthy)',
    ['service']
)

service_uptime_seconds = Gauge(
    'selfaware_service_uptime_seconds',
    'Service uptime in seconds',
    ['service']
)

health_check_duration_seconds = Histogram(
    'selfaware_health_check_duration_seconds',
    'Health check duration',
    ['service', 'check_name'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

health_check_failures_total = Counter(
    'selfaware_health_check_failures_total',
    'Total health check failures',
    ['service', 'check_name']
)

error_rate = Gauge(
    'selfaware_error_rate',
    'Error rate (percentage)',
    ['service']
)

# Load Management Metrics

current_load_percentage = Gauge(
    'selfaware_current_load_percentage',
    'Current load as percentage of capacity',
    ['service']
)

active_requests = Gauge(
    'selfaware_active_requests',
    'Number of active requests',
    ['service']
)

queued_events = Gauge(
    'selfaware_queued_events',
    'Number of queued events',
    ['service']
)

deferred_events = Gauge(
    'selfaware_deferred_events',
    'Number of deferred events',
    ['service']
)

load_level = Gauge(
    'selfaware_load_level',
    'Load level (0=idle, 1=normal, 2=medium, 3=high, 4=critical)',
    ['service']
)

degradation_events_total = Counter(
    'selfaware_degradation_events_total',
    'Total times service entered degraded mode',
    ['service', 'reason']
)

load_shedding_events_total = Counter(
    'selfaware_load_shedding_events_total',
    'Total load shedding events',
    ['service']
)

request_duration_seconds = Histogram(
    'selfaware_request_duration_seconds',
    'Request processing duration',
    ['service'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Capability Metrics

registered_capabilities = Gauge(
    'selfaware_registered_capabilities',
    'Number of registered capabilities',
    ['service']
)

enabled_capabilities = Gauge(
    'selfaware_enabled_capabilities',
    'Number of enabled capabilities',
    ['service']
)

capability_matches_total = Counter(
    'selfaware_capability_matches_total',
    'Total capability matches',
    ['service', 'capability', 'match_type']
)

# Collaboration Metrics

consensus_requests_total = Counter(
    'selfaware_consensus_requests_total',
    'Total consensus requests initiated',
    ['service']
)

consensus_responses_total = Counter(
    'selfaware_consensus_responses_total',
    'Total consensus responses received',
    ['service', 'vote_type']
)

consensus_duration_seconds = Histogram(
    'selfaware_consensus_duration_seconds',
    'Time to reach consensus',
    ['service', 'strategy', 'result'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

collaboration_success_total = Counter(
    'selfaware_collaboration_success_total',
    'Successful collaborations',
    ['service', 'consensus_type']
)

collaboration_timeout_total = Counter(
    'selfaware_collaboration_timeout_total',
    'Collaboration timeouts',
    ['service', 'consensus_type']
)

votes_cast_total = Counter(
    'selfaware_votes_cast_total',
    'Total votes cast',
    ['service', 'vote_type', 'context_type']
)

# Service Info

service_info = Info(
    'selfaware_service_info',
    'Self-aware service information'
)


class MetricsCollector:
    """
    Metrics collector for self-aware services.

    Aggregates metrics from all components and exposes them
    for Prometheus scraping.
    """

    def __init__(self, service_name: str):
        """
        Initialize metrics collector.

        Args:
            service_name: Service identifier
        """
        self.service_name = service_name

        # Set service info
        service_info.info({
            'service': service_name,
            'version': '1.0.0',
            'type': 'self_aware'
        })

        logger.info(f"MetricsCollector initialized for {service_name}")

    # Event Handling Metrics

    def record_event_received(self, event_type: str, priority: str):
        """Record event received"""
        events_received_total.labels(
            service=self.service_name,
            event_type=event_type,
            priority=priority
        ).inc()

    def record_event_handled(self, event_type: str, decision: str, duration_seconds: float):
        """Record event handled"""
        events_handled_total.labels(
            service=self.service_name,
            event_type=event_type,
            decision=decision
        ).inc()

        event_handling_duration_seconds.labels(
            service=self.service_name,
            event_type=event_type,
            decision=decision
        ).observe(duration_seconds)

    def record_event_deferred(self, event_type: str, reason: str):
        """Record event deferred"""
        events_deferred_total.labels(
            service=self.service_name,
            event_type=event_type,
            reason=reason
        ).inc()

    def record_event_delegated(self, event_type: str, delegate_to: str):
        """Record event delegated"""
        events_delegated_total.labels(
            service=self.service_name,
            event_type=event_type,
            delegate_to=delegate_to
        ).inc()

    def record_event_rejected(self, event_type: str, reason: str):
        """Record event rejected"""
        events_rejected_total.labels(
            service=self.service_name,
            event_type=event_type,
            reason=reason
        ).inc()

    # Health Metrics

    def update_health_status(self, status: str):
        """Update health status"""
        status_map = {
            'healthy': 2,
            'degraded': 1,
            'down': 0,
            'unknown': -1
        }
        service_health_status.labels(
            service=self.service_name
        ).set(status_map.get(status, -1))

    def update_uptime(self, uptime_seconds: float):
        """Update service uptime"""
        service_uptime_seconds.labels(
            service=self.service_name
        ).set(uptime_seconds)

    def record_health_check(self, check_name: str, duration_seconds: float, success: bool):
        """Record health check"""
        health_check_duration_seconds.labels(
            service=self.service_name,
            check_name=check_name
        ).observe(duration_seconds)

        if not success:
            health_check_failures_total.labels(
                service=self.service_name,
                check_name=check_name
            ).inc()

    def update_error_rate(self, rate: float):
        """Update error rate"""
        error_rate.labels(
            service=self.service_name
        ).set(rate)

    # Load Metrics

    def update_load(self, load_percentage: float):
        """Update current load"""
        current_load_percentage.labels(
            service=self.service_name
        ).set(load_percentage * 100)

    def update_active_requests(self, count: int):
        """Update active requests"""
        active_requests.labels(
            service=self.service_name
        ).set(count)

    def update_queued_events(self, count: int):
        """Update queued events"""
        queued_events.labels(
            service=self.service_name
        ).set(count)

    def update_deferred_events(self, count: int):
        """Update deferred events"""
        deferred_events.labels(
            service=self.service_name
        ).set(count)

    def update_load_level(self, level: str):
        """Update load level"""
        level_map = {
            'idle': 0,
            'normal': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        load_level.labels(
            service=self.service_name
        ).set(level_map.get(level, -1))

    def record_degradation(self, reason: str):
        """Record degradation event"""
        degradation_events_total.labels(
            service=self.service_name,
            reason=reason
        ).inc()

    def record_load_shedding(self):
        """Record load shedding"""
        load_shedding_events_total.labels(
            service=self.service_name
        ).inc()

    def record_request_duration(self, duration_seconds: float):
        """Record request duration"""
        request_duration_seconds.labels(
            service=self.service_name
        ).observe(duration_seconds)

    # Capability Metrics

    def update_capabilities(self, registered: int, enabled: int):
        """Update capability counts"""
        registered_capabilities.labels(
            service=self.service_name
        ).set(registered)

        enabled_capabilities.labels(
            service=self.service_name
        ).set(enabled)

    def record_capability_match(self, capability: str, match_type: str):
        """Record capability match"""
        capability_matches_total.labels(
            service=self.service_name,
            capability=capability,
            match_type=match_type
        ).inc()

    # Collaboration Metrics

    def record_consensus_request(self):
        """Record consensus request"""
        consensus_requests_total.labels(
            service=self.service_name
        ).inc()

    def record_consensus_response(self, vote_type: str):
        """Record consensus response"""
        consensus_responses_total.labels(
            service=self.service_name,
            vote_type=vote_type
        ).inc()

    def record_consensus_duration(self, strategy: str, result: str, duration_seconds: float):
        """Record consensus duration"""
        consensus_duration_seconds.labels(
            service=self.service_name,
            strategy=strategy,
            result=result
        ).observe(duration_seconds)

    def record_collaboration_success(self, consensus_type: str):
        """Record successful collaboration"""
        collaboration_success_total.labels(
            service=self.service_name,
            consensus_type=consensus_type
        ).inc()

    def record_collaboration_timeout(self, consensus_type: str):
        """Record collaboration timeout"""
        collaboration_timeout_total.labels(
            service=self.service_name,
            consensus_type=consensus_type
        ).inc()

    def record_vote_cast(self, vote_type: str, context_type: str):
        """Record vote cast"""
        votes_cast_total.labels(
            service=self.service_name,
            vote_type=vote_type,
            context_type=context_type
        ).inc()

    # Aggregate Metrics

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as dictionary"""
        # This would collect current values from all gauges
        # For actual implementation, you'd query the Prometheus registry
        return {
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            # Would include all metric values here
        }


# Global metrics collector (can be initialized per service)
_metrics_collectors: Dict[str, MetricsCollector] = {}


def get_metrics_collector(service_name: str) -> MetricsCollector:
    """
    Get or create metrics collector for service.

    Args:
        service_name: Service identifier

    Returns:
        MetricsCollector instance
    """
    if service_name not in _metrics_collectors:
        _metrics_collectors[service_name] = MetricsCollector(service_name)

    return _metrics_collectors[service_name]
