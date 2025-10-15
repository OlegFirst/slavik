"""
Prometheus Metrics for Decision Center
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable

# Decision metrics
decisions_total = Counter(
    'decision_center_decisions_total',
    'Total number of decisions made',
    ['service', 'action', 'decision_type', 'outcome']
)

decision_latency = Histogram(
    'decision_center_decision_latency_seconds',
    'Decision making latency in seconds',
    ['service', 'action']
)

# Escalation metrics
escalations_total = Counter(
    'decision_center_escalations_total',
    'Total number of escalations',
    ['service', 'escalation_level', 'urgency']
)

escalation_response_time = Histogram(
    'decision_center_escalation_response_time_seconds',
    'Escalation response time in seconds',
    ['escalation_level']
)

active_escalations = Gauge(
    'decision_center_active_escalations',
    'Number of active escalations',
    ['escalation_level']
)

# AI consultation metrics
ai_consultations_total = Counter(
    'decision_center_ai_consultations_total',
    'Total number of AI consultations',
    ['tier', 'complexity']
)

ai_consultation_latency = Histogram(
    'decision_center_ai_consultation_latency_seconds',
    'AI consultation latency in seconds',
    ['tier']
)

ai_confidence = Histogram(
    'decision_center_ai_confidence',
    'AI confidence scores',
    ['tier'],
    buckets=[0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
)

# Policy metrics
policy_reloads_total = Counter(
    'decision_center_policy_reloads_total',
    'Total number of policy reloads'
)

policy_validation_errors = Counter(
    'decision_center_policy_validation_errors_total',
    'Total number of policy validation errors'
)

# Audit metrics
audit_logs_written = Counter(
    'decision_center_audit_logs_written_total',
    'Total number of audit logs written',
    ['event_type']
)

audit_log_write_errors = Counter(
    'decision_center_audit_log_write_errors_total',
    'Total number of audit log write errors'
)

# System info
system_info = Info(
    'decision_center_info',
    'Decision Center system information'
)


def track_decision_metrics(func: Callable):
    """
    Decorator to track decision metrics

    Usage:
        @track_decision_metrics
        async def make_decision(self, request):
            ...
    """
    @wraps(func)
    async def wrapper(self, request, *args, **kwargs):
        start_time = time.time()

        try:
            # Make decision
            decision = await func(self, request, *args, **kwargs)

            # Record metrics
            decisions_total.labels(
                service=request.service,
                action=request.action,
                decision_type=decision.decision_type.value,
                outcome=decision.outcome.value
            ).inc()

            decision_latency.labels(
                service=request.service,
                action=request.action
            ).observe(time.time() - start_time)

            return decision

        except Exception as e:
            # Record error metrics
            decisions_total.labels(
                service=request.service,
                action=request.action,
                decision_type='error',
                outcome='error'
            ).inc()
            raise

    return wrapper


def track_escalation_metrics(func: Callable):
    """
    Decorator to track escalation metrics

    Usage:
        @track_escalation_metrics
        async def escalate(self, request, reason, policies):
            ...
    """
    @wraps(func)
    async def wrapper(self, request, reason, policies=None):
        # Call escalation
        decision = await func(self, request, reason, policies)

        # Record metrics
        escalation_level = decision.metadata.get('escalation_level', 'unknown')
        urgency = decision.metadata.get('urgency', 0)

        escalations_total.labels(
            service=request.service,
            escalation_level=escalation_level,
            urgency=str(urgency)
        ).inc()

        # Update active escalations gauge
        active_escalations.labels(
            escalation_level=escalation_level
        ).inc()

        return decision

    return wrapper


def track_ai_consultation_metrics(func: Callable):
    """
    Decorator to track AI consultation metrics

    Usage:
        @track_ai_consultation_metrics
        async def consult(self, problem, context, service, action, complexity):
            ...
    """
    @wraps(func)
    async def wrapper(self, problem, context, service, action, complexity="medium"):
        start_time = time.time()

        # Call AI consultation
        response = await func(self, problem, context, service, action, complexity)

        # Record metrics
        ai_consultations_total.labels(
            tier=response.tier.value,
            complexity=complexity
        ).inc()

        ai_consultation_latency.labels(
            tier=response.tier.value
        ).observe(time.time() - start_time)

        ai_confidence.labels(
            tier=response.tier.value
        ).observe(response.confidence)

        return response

    return wrapper


def record_escalation_response(escalation_level: str, response_time_seconds: int):
    """
    Record escalation response metrics

    Args:
        escalation_level: Escalation level
        response_time_seconds: Response time in seconds
    """
    escalation_response_time.labels(
        escalation_level=escalation_level
    ).observe(response_time_seconds)

    # Decrement active escalations
    active_escalations.labels(
        escalation_level=escalation_level
    ).dec()


def record_policy_reload(success: bool = True):
    """
    Record policy reload metrics

    Args:
        success: Whether reload was successful
    """
    policy_reloads_total.inc()

    if not success:
        policy_validation_errors.inc()


def record_audit_log(event_type: str, success: bool = True):
    """
    Record audit log metrics

    Args:
        event_type: Type of event logged
        success: Whether write was successful
    """
    if success:
        audit_logs_written.labels(
            event_type=event_type
        ).inc()
    else:
        audit_log_write_errors.inc()


def initialize_metrics(version: str, environment: str = "production"):
    """
    Initialize system metrics

    Args:
        version: Decision Center version
        environment: Environment name
    """
    system_info.info({
        'version': version,
        'environment': environment
    })
