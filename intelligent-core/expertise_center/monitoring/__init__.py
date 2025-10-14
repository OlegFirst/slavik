"""
Monitoring module for expertise-center

Provides Prometheus metrics for all analyzers, specialists, and assistants.
"""

from .metrics import (
    # Metrics
    analyzer_calls_total,
    analyzer_duration_seconds,
    analyzer_http_calls_total,
    analyzer_errors_total,
    specialist_calls_total,
    specialist_duration_seconds,
    circuit_breaker_state,

    # Decorators
    track_analyzer_call,
    track_specialist_call,
    track_http_call,
    update_circuit_breaker_state,

    # Utilities
    set_analyzer_health,
    init_expertise_metrics
)

__all__ = [
    'analyzer_calls_total',
    'analyzer_duration_seconds',
    'analyzer_http_calls_total',
    'analyzer_errors_total',
    'specialist_calls_total',
    'specialist_duration_seconds',
    'circuit_breaker_state',
    'track_analyzer_call',
    'track_specialist_call',
    'track_http_call',
    'update_circuit_breaker_state',
    'set_analyzer_health',
    'init_expertise_metrics'
]
