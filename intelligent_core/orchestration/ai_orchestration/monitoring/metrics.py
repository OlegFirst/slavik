"""
AI Orchestrator Performance Metrics
====================================

Comprehensive Prometheus metrics for orchestrator performance monitoring.

Metrics categories:
- Performance: Latency, throughput, response times
- Efficiency: Resource utilization, token usage, cost
- Quality: Success rate, error rate, retry rate
- Scalability: Queue length, concurrent tasks, agent utilization
- Reliability: Uptime, failures, recovery
- Cognitive: LLM performance, planning depth, tool efficiency
"""

from prometheus_client import Counter, Histogram, Gauge, Summary, Info
import time
from typing import Optional, Dict, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

# Request metrics
orchestrator_requests_total = Counter(
    'orchestrator_requests_total',
    'Total number of requests to orchestrator',
    ['method', 'endpoint', 'status']
)

orchestrator_request_duration = Histogram(
    'orchestrator_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Task metrics
orchestrator_tasks_total = Counter(
    'orchestrator_tasks_total',
    'Total number of tasks processed',
    ['task_type', 'status', 'agent']
)

orchestrator_task_duration = Histogram(
    'orchestrator_task_duration_seconds',
    'Task execution duration',
    ['task_type', 'agent'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# Latency metrics (P50, P95, P99)
orchestrator_latency = Summary(
    'orchestrator_latency_seconds',
    'Request latency summary (P50, P95, P99)',
    ['operation']
)

# ============================================================================
# EFFICIENCY METRICS
# ============================================================================

# Resource utilization
orchestrator_cpu_usage = Gauge(
    'orchestrator_cpu_usage_percent',
    'CPU usage percentage'
)

orchestrator_memory_usage = Gauge(
    'orchestrator_memory_usage_bytes',
    'Memory usage in bytes'
)

# Token efficiency
orchestrator_tokens_used = Counter(
    'orchestrator_tokens_used_total',
    'Total tokens used by LLM',
    ['model', 'operation']
)

orchestrator_tokens_per_task = Histogram(
    'orchestrator_tokens_per_task',
    'Tokens used per task',
    ['task_type'],
    buckets=[100, 500, 1000, 2000, 5000, 10000, 20000]
)

# Cost tracking
orchestrator_cost = Counter(
    'orchestrator_cost_dollars_total',
    'Total cost in dollars',
    ['resource_type']
)

orchestrator_cost_per_task = Gauge(
    'orchestrator_cost_per_task_dollars',
    'Average cost per task in dollars',
    ['task_type']
)

# ============================================================================
# QUALITY METRICS
# ============================================================================

# Success rate
orchestrator_success_rate = Gauge(
    'orchestrator_success_rate_percent',
    'Task success rate percentage',
    ['task_type']
)

# Error tracking
orchestrator_errors_total = Counter(
    'orchestrator_errors_total',
    'Total number of errors',
    ['error_type', 'component']
)

# Retry tracking
orchestrator_retries_total = Counter(
    'orchestrator_retries_total',
    'Total number of task retries',
    ['task_type', 'reason']
)

# ============================================================================
# SCALABILITY METRICS
# ============================================================================

# Queue metrics
orchestrator_queue_length = Gauge(
    'orchestrator_queue_length',
    'Current queue length',
    ['priority']
)

orchestrator_queue_wait_time = Histogram(
    'orchestrator_queue_wait_time_seconds',
    'Time spent waiting in queue',
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)

# Concurrent tasks
orchestrator_active_tasks = Gauge(
    'orchestrator_active_tasks',
    'Number of currently active tasks',
    ['task_type']
)

orchestrator_max_concurrent_tasks = Gauge(
    'orchestrator_max_concurrent_tasks',
    'Maximum concurrent tasks capacity'
)

# Agent utilization
orchestrator_agent_utilization = Gauge(
    'orchestrator_agent_utilization_percent',
    'Agent utilization percentage',
    ['agent_name', 'agent_type']
)

orchestrator_agent_idle_time = Counter(
    'orchestrator_agent_idle_time_seconds_total',
    'Total agent idle time',
    ['agent_name']
)

# ============================================================================
# RELIABILITY METRICS
# ============================================================================

# Uptime
orchestrator_uptime_seconds = Gauge(
    'orchestrator_uptime_seconds',
    'Orchestrator uptime in seconds'
)

# Failures
orchestrator_failures_total = Counter(
    'orchestrator_failures_total',
    'Total system failures',
    ['failure_type', 'severity']
)

# Recovery
orchestrator_recovery_time = Histogram(
    'orchestrator_recovery_time_seconds',
    'Time to recover from failure',
    ['failure_type'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
)

# Circuit breaker
orchestrator_circuit_breaker_state = Gauge(
    'orchestrator_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half-open)',
    ['component']
)

# ============================================================================
# COGNITIVE METRICS (AI-specific)
# ============================================================================

# LLM performance
orchestrator_llm_calls_total = Counter(
    'orchestrator_llm_calls_total',
    'Total LLM API calls',
    ['model', 'provider', 'status']
)

orchestrator_llm_latency = Histogram(
    'orchestrator_llm_latency_seconds',
    'LLM API call latency',
    ['model', 'provider'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Planning & reasoning
orchestrator_planning_depth = Histogram(
    'orchestrator_planning_depth',
    'Planning depth (number of steps)',
    buckets=[1, 2, 3, 5, 10, 15, 20]
)

orchestrator_reasoning_steps = Histogram(
    'orchestrator_reasoning_steps',
    'Number of reasoning steps',
    buckets=[1, 2, 3, 5, 10, 20, 50]
)

# Tool usage
orchestrator_tool_calls_total = Counter(
    'orchestrator_tool_calls_total',
    'Total tool calls',
    ['tool_name', 'status']
)

orchestrator_tool_efficiency = Gauge(
    'orchestrator_tool_efficiency_percent',
    'Tool call success rate',
    ['tool_name']
)

# Memory/context
orchestrator_context_size = Histogram(
    'orchestrator_context_size_bytes',
    'Size of context passed to agents',
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000]
)

orchestrator_memory_retention_rate = Gauge(
    'orchestrator_memory_retention_rate_percent',
    'Memory retention rate across tasks'
)

# Agent selection
orchestrator_agent_selection_accuracy = Gauge(
    'orchestrator_agent_selection_accuracy_percent',
    'Agent selection accuracy',
    ['task_type']
)

# ============================================================================
# BUSINESS METRICS
# ============================================================================

# SLA compliance
orchestrator_sla_compliance = Gauge(
    'orchestrator_sla_compliance_percent',
    'SLA compliance percentage',
    ['sla_type']
)

orchestrator_sla_violations_total = Counter(
    'orchestrator_sla_violations_total',
    'Total SLA violations',
    ['sla_type', 'severity']
)

# User satisfaction
orchestrator_user_satisfaction = Gauge(
    'orchestrator_user_satisfaction_score',
    'User satisfaction score (0-10)',
    ['feedback_type']
)

# Automation rate
orchestrator_automation_rate = Gauge(
    'orchestrator_automation_rate_percent',
    'Percentage of tasks fully automated'
)

# ============================================================================
# INFO METRICS
# ============================================================================

orchestrator_info = Info(
    'orchestrator_info',
    'Orchestrator version and configuration'
)

# ============================================================================
# HELPER CLASS FOR EASY TRACKING
# ============================================================================

class OrchestratorMetrics:
    """Helper class for tracking orchestrator metrics"""

    def __init__(self):
        self.start_time = time.time()
        orchestrator_info.info({
            'version': '1.0.0',
            'environment': 'production'
        })

    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """Track HTTP request"""
        orchestrator_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        orchestrator_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        orchestrator_latency.labels(operation=f"{method}_{endpoint}").observe(duration)

    def track_task(self, task_type: str, agent: str, status: str, duration: float, tokens_used: int = 0):
        """Track task execution"""
        orchestrator_tasks_total.labels(task_type=task_type, status=status, agent=agent).inc()
        orchestrator_task_duration.labels(task_type=task_type, agent=agent).observe(duration)

        if tokens_used > 0:
            orchestrator_tokens_per_task.labels(task_type=task_type).observe(tokens_used)

    def track_error(self, error_type: str, component: str):
        """Track error"""
        orchestrator_errors_total.labels(error_type=error_type, component=component).inc()

    def track_agent_utilization(self, agent_name: str, agent_type: str, utilization: float):
        """Track agent utilization (0-100%)"""
        orchestrator_agent_utilization.labels(agent_name=agent_name, agent_type=agent_type).set(utilization)

    def track_llm_call(self, model: str, provider: str, status: str, latency: float, tokens: int):
        """Track LLM API call"""
        orchestrator_llm_calls_total.labels(model=model, provider=provider, status=status).inc()
        orchestrator_llm_latency.labels(model=model, provider=provider).observe(latency)
        orchestrator_tokens_used.labels(model=model, operation='inference').inc(tokens)

    def update_queue_metrics(self, length: int, priority: str = 'normal'):
        """Update queue metrics"""
        orchestrator_queue_length.labels(priority=priority).set(length)

    def update_active_tasks(self, count: int, task_type: str = 'default'):
        """Update active tasks count"""
        orchestrator_active_tasks.labels(task_type=task_type).set(count)

    def update_uptime(self):
        """Update uptime metric"""
        uptime = time.time() - self.start_time
        orchestrator_uptime_seconds.set(uptime)

    def track_sla_violation(self, sla_type: str, severity: str):
        """Track SLA violation"""
        orchestrator_sla_violations_total.labels(sla_type=sla_type, severity=severity).inc()

    def update_success_rate(self, task_type: str, rate: float):
        """Update success rate (0-100%)"""
        orchestrator_success_rate.labels(task_type=task_type).set(rate)


# Global metrics instance
orchestrator_metrics = OrchestratorMetrics()


# ============================================================================
# DECORATOR FOR AUTOMATIC TRACKING
# ============================================================================

def track_performance(task_type: str = 'default', agent: str = 'unknown'):
    """Decorator to automatically track function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            status = 'success'
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                orchestrator_metrics.track_error(
                    error_type=type(e).__name__,
                    component=func.__name__
                )
                raise
            finally:
                duration = time.time() - start
                orchestrator_metrics.track_task(
                    task_type=task_type,
                    agent=agent,
                    status=status,
                    duration=duration
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            status = 'success'
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                orchestrator_metrics.track_error(
                    error_type=type(e).__name__,
                    component=func.__name__
                )
                raise
            finally:
                duration = time.time() - start
                orchestrator_metrics.track_task(
                    task_type=task_type,
                    agent=agent,
                    status=status,
                    duration=duration
                )

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
