"""
Prometheus Metrics for AI Orchestrator
=======================================

Exports metrics for monitoring orchestrator performance and efficiency.

Metrics Categories:
1. Decision Performance - latency, throughput, context aggregation
2. Execution Performance - success rate, service calls, retries
3. Efficiency Metrics - human intervention, auto-resolution rate
4. Quality Metrics - safety approval, strategy accuracy
5. Resource Efficiency - CPU, memory, cache hit rate
6. Business Impact - MTTR, incident prevention

Integration with Grafana dashboards.
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from typing import Dict, Any
import time


class OrchestratorMetrics:
    """
    Prometheus metrics for AI Orchestrator.

    Exposes /metrics endpoint compatible with Prometheus.
    """

    def __init__(self, registry: CollectorRegistry = None):
        """
        Initialize metrics.

        Args:
            registry: Prometheus registry (creates new if None)
        """
        self.registry = registry or CollectorRegistry()

        # ====================================================================
        # DECISION PERFORMANCE
        # ====================================================================

        # Decision latency (histogram with P50/P95/P99)
        self.decision_latency = Histogram(
            'orchestrator_decision_latency_seconds',
            'Decision-making latency in seconds',
            buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0],
            registry=self.registry
        )

        # Decision throughput
        self.decisions_total = Counter(
            'orchestrator_decisions_total',
            'Total number of decisions made',
            ['action_type', 'priority'],
            registry=self.registry
        )

        # Context aggregation time
        self.context_aggregation_time = Histogram(
            'orchestrator_context_aggregation_seconds',
            'Time to aggregate full context',
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
            registry=self.registry
        )

        # Strategy selection time
        self.strategy_selection_time = Histogram(
            'orchestrator_strategy_selection_seconds',
            'Time to select strategy',
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
            registry=self.registry
        )

        # ====================================================================
        # EXECUTION PERFORMANCE
        # ====================================================================

        # Execution success rate
        self.executions_total = Counter(
            'orchestrator_executions_total',
            'Total number of executions',
            ['action_type', 'status'],
            registry=self.registry
        )

        # Service call latency
        self.service_call_latency = Histogram(
            'orchestrator_service_call_latency_seconds',
            'Service call latency via ServiceRegistry',
            ['service_name'],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
            registry=self.registry
        )

        # Retry overhead
        self.retries_total = Counter(
            'orchestrator_retries_total',
            'Total number of service call retries',
            ['service_name', 'success'],
            registry=self.registry
        )

        # Circuit breaker trips
        self.circuit_breaker_trips = Counter(
            'orchestrator_circuit_breaker_trips_total',
            'Circuit breaker trips',
            ['service_name'],
            registry=self.registry
        )

        # ====================================================================
        # EFFICIENCY METRICS
        # ====================================================================

        # Human intervention rate
        self.escalations_total = Counter(
            'orchestrator_escalations_total',
            'Total escalations to human',
            ['reason'],
            registry=self.registry
        )

        # Auto-resolution rate
        self.auto_resolutions_total = Counter(
            'orchestrator_auto_resolutions_total',
            'Total auto-resolved decisions',
            ['service_name'],
            registry=self.registry
        )

        # Delegation to AI Experts
        self.delegations_total = Counter(
            'orchestrator_delegations_total',
            'Total delegations to specialists',
            ['specialist_type'],
            registry=self.registry
        )

        # ====================================================================
        # QUALITY METRICS
        # ====================================================================

        # Safety approval rate
        self.safety_checks_total = Counter(
            'orchestrator_safety_checks_total',
            'Safety checks performed',
            ['approved'],
            registry=self.registry
        )

        # Strategy confidence
        self.strategy_confidence = Histogram(
            'orchestrator_strategy_confidence',
            'Strategy confidence scores',
            buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry
        )

        # Learning effectiveness (strategies learned from memory)
        self.strategies_from_memory = Counter(
            'orchestrator_strategies_from_memory_total',
            'Strategies retrieved from memory',
            registry=self.registry
        )

        # ====================================================================
        # RESOURCE EFFICIENCY
        # ====================================================================

        # Memory usage
        self.memory_usage_bytes = Gauge(
            'orchestrator_memory_usage_bytes',
            'Memory usage in bytes',
            ['memory_layer'],
            registry=self.registry
        )

        # Cache hit rate
        self.cache_hits_total = Counter(
            'orchestrator_cache_hits_total',
            'Cache hits',
            ['cache_type'],
            registry=self.registry
        )

        self.cache_misses_total = Counter(
            'orchestrator_cache_misses_total',
            'Cache misses',
            ['cache_type'],
            registry=self.registry
        )

        # Active crises
        self.active_crises = Gauge(
            'orchestrator_active_crises',
            'Number of active crisis situations',
            registry=self.registry
        )

        # ====================================================================
        # BUSINESS IMPACT
        # ====================================================================

        # Mean Time To Resolution (MTTR)
        self.resolution_time = Histogram(
            'orchestrator_resolution_time_seconds',
            'Time to resolve incidents',
            buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600],
            registry=self.registry
        )

        # Incidents prevented
        self.incidents_prevented = Counter(
            'orchestrator_incidents_prevented_total',
            'Incidents prevented by proactive actions',
            registry=self.registry
        )

        # PDCA cycles completed
        self.pdca_cycles_total = Counter(
            'orchestrator_pdca_cycles_total',
            'PDCA cycles completed',
            ['phase'],
            registry=self.registry
        )

        # ====================================================================
        # SYSTEM INFO
        # ====================================================================

        self.info = Info(
            'orchestrator_info',
            'Orchestrator version and configuration',
            registry=self.registry
        )

    def record_decision(
        self,
        latency_seconds: float,
        action_type: str,
        priority: str,
        confidence: float,
        safety_approved: bool
    ):
        """Record decision metrics."""
        self.decision_latency.observe(latency_seconds)
        self.decisions_total.labels(action_type=action_type, priority=priority).inc()
        self.strategy_confidence.observe(confidence)
        self.safety_checks_total.labels(approved=str(safety_approved)).inc()

    def record_context_aggregation(self, duration_seconds: float):
        """Record context aggregation time."""
        self.context_aggregation_time.observe(duration_seconds)

    def record_strategy_selection(self, duration_seconds: float):
        """Record strategy selection time."""
        self.strategy_selection_time.observe(duration_seconds)

    def record_execution(self, action_type: str, success: bool):
        """Record execution result."""
        status = 'success' if success else 'failure'
        self.executions_total.labels(action_type=action_type, status=status).inc()

    def record_service_call(
        self,
        service_name: str,
        latency_seconds: float,
        success: bool,
        retries: int = 0
    ):
        """Record service call metrics."""
        self.service_call_latency.labels(service_name=service_name).observe(latency_seconds)

        if retries > 0:
            self.retries_total.labels(
                service_name=service_name,
                success=str(success)
            ).inc(retries)

    def record_circuit_breaker_trip(self, service_name: str):
        """Record circuit breaker trip."""
        self.circuit_breaker_trips.labels(service_name=service_name).inc()

    def record_escalation(self, reason: str):
        """Record human escalation."""
        self.escalations_total.labels(reason=reason).inc()

    def record_auto_resolution(self, service_name: str):
        """Record auto-resolution."""
        self.auto_resolutions_total.labels(service_name=service_name).inc()

    def record_delegation(self, specialist_type: str):
        """Record delegation to specialist."""
        self.delegations_total.labels(specialist_type=specialist_type).inc()

    def record_strategy_from_memory(self):
        """Record strategy retrieved from memory."""
        self.strategies_from_memory.inc()

    def record_cache_hit(self, cache_type: str):
        """Record cache hit."""
        self.cache_hits_total.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str):
        """Record cache miss."""
        self.cache_misses_total.labels(cache_type=cache_type).inc()

    def update_memory_usage(self, memory_layer: str, bytes_used: int):
        """Update memory usage gauge."""
        self.memory_usage_bytes.labels(memory_layer=memory_layer).set(bytes_used)

    def update_active_crises(self, count: int):
        """Update active crises count."""
        self.active_crises.set(count)

    def record_resolution(self, duration_seconds: float):
        """Record incident resolution time."""
        self.resolution_time.observe(duration_seconds)

    def record_incident_prevented(self):
        """Record prevented incident."""
        self.incidents_prevented.inc()

    def record_pdca_cycle(self, phase: str):
        """Record PDCA cycle phase completion."""
        self.pdca_cycles_total.labels(phase=phase).inc()

    def set_info(self, version: str, **kwargs):
        """Set orchestrator info."""
        info_dict = {'version': version, **kwargs}
        self.info.info(info_dict)

    def get_latest_metrics(self) -> bytes:
        """
        Get metrics in Prometheus format.

        Returns:
            Metrics in Prometheus text format
        """
        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """Get Prometheus content type."""
        return CONTENT_TYPE_LATEST


# Global metrics instance
_metrics: OrchestratorMetrics = None


def get_metrics() -> OrchestratorMetrics:
    """Get global metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = OrchestratorMetrics()
        _metrics.set_info(version='1.0.0', component='ai-orchestrator')
    return _metrics


def initialize_metrics() -> OrchestratorMetrics:
    """Initialize metrics."""
    global _metrics
    _metrics = OrchestratorMetrics()
    _metrics.set_info(version='1.0.0', component='ai-orchestrator')
    return _metrics
