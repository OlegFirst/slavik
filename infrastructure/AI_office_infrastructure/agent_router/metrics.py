"""
Prometheus Metrics для AI Agent Router

Экспортирует метрики для мониторинга производительности роутера и агентов.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict

# ============================================================================
# Request Metrics
# ============================================================================

requests_total = Counter(
    'ai_router_requests_total',
    'Total number of routing requests',
    ['capability', 'agent', 'status']
)

requests_duration = Histogram(
    'ai_router_request_duration_seconds',
    'Request duration in seconds',
    ['capability', 'agent'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

# ============================================================================
# Agent Health Metrics
# ============================================================================

agent_health = Gauge(
    'ai_router_agent_health',
    'Agent health status (1=healthy, 0=unhealthy)',
    ['agent', 'role']
)

agent_response_time = Histogram(
    'ai_router_agent_response_time_seconds',
    'Agent response time in seconds',
    ['agent'],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

agent_last_health_check = Gauge(
    'ai_router_agent_last_health_check_timestamp',
    'Unix timestamp of last health check',
    ['agent']
)

# ============================================================================
# Load Balancing Metrics
# ============================================================================

agent_load = Gauge(
    'ai_router_agent_load',
    'Current load on agent (active requests)',
    ['agent']
)

agent_requests_total = Counter(
    'ai_router_agent_requests_total',
    'Total requests routed to agent',
    ['agent', 'status']
)

# ============================================================================
# Routing Metrics
# ============================================================================

routing_fallback_total = Counter(
    'ai_router_fallback_total',
    'Total number of fallback routing attempts',
    ['capability', 'primary_agent', 'fallback_agent']
)

routing_errors_total = Counter(
    'ai_router_errors_total',
    'Total routing errors',
    ['capability', 'agent', 'error_type']
)

no_agents_available = Counter(
    'ai_router_no_agents_available_total',
    'Total number of times no agents were available',
    ['capability']
)

# ============================================================================
# Capability Metrics
# ============================================================================

capability_requests = Counter(
    'ai_router_capability_requests_total',
    'Total requests by capability',
    ['capability']
)

capability_success_rate = Gauge(
    'ai_router_capability_success_rate',
    'Success rate by capability (0.0-1.0)',
    ['capability']
)

# ============================================================================
# Router Info
# ============================================================================

router_info = Info(
    'ai_router_info',
    'AI Router information'
)

router_agents_registered = Gauge(
    'ai_router_agents_registered',
    'Number of registered agents'
)

# ============================================================================
# Circuit Breaker Metrics (для будущего использования)
# ============================================================================

circuit_breaker_state = Gauge(
    'ai_router_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['agent']
)

circuit_breaker_failures = Counter(
    'ai_router_circuit_breaker_failures_total',
    'Total circuit breaker failures',
    ['agent']
)

# ============================================================================
# Redis Metrics
# ============================================================================

redis_operations_total = Counter(
    'ai_router_redis_operations_total',
    'Total Redis operations',
    ['operation', 'status']
)

redis_connection_errors = Counter(
    'ai_router_redis_connection_errors_total',
    'Total Redis connection errors'
)

# ============================================================================
# Helper Functions
# ============================================================================

def record_request(capability: str, agent: str, status: str, duration: float):
    """Record a routing request"""
    requests_total.labels(capability=capability, agent=agent, status=status).inc()
    requests_duration.labels(capability=capability, agent=agent).observe(duration)
    capability_requests.labels(capability=capability).inc()
    agent_requests_total.labels(agent=agent, status=status).inc()


def record_agent_health(agent: str, role: str, is_healthy: bool, response_time: float = 0):
    """Record agent health check"""
    agent_health.labels(agent=agent, role=role).set(1 if is_healthy else 0)
    if is_healthy and response_time > 0:
        agent_response_time.labels(agent=agent).observe(response_time)


def record_fallback(capability: str, primary_agent: str, fallback_agent: str):
    """Record a fallback routing"""
    routing_fallback_total.labels(
        capability=capability,
        primary_agent=primary_agent,
        fallback_agent=fallback_agent
    ).inc()


def record_error(capability: str, agent: str, error_type: str):
    """Record a routing error"""
    routing_errors_total.labels(
        capability=capability,
        agent=agent,
        error_type=error_type
    ).inc()


def record_no_agents(capability: str):
    """Record when no agents are available"""
    no_agents_available.labels(capability=capability).inc()


def update_agent_load(agent: str, load: float):
    """Update agent load"""
    agent_load.labels(agent=agent).set(load)


def record_redis_operation(operation: str, status: str):
    """Record Redis operation"""
    redis_operations_total.labels(operation=operation, status=status).inc()


def set_router_info(version: str, agents_count: int):
    """Set router info"""
    router_info.info({'version': version})
    router_agents_registered.set(agents_count)


def update_capability_success_rate(capability: str, success_rate: float):
    """Update capability success rate"""
    capability_success_rate.labels(capability=capability).set(success_rate)
