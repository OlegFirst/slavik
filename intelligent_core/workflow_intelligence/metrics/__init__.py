"""
Metrics for Workflow Intelligence

Prometheus metrics exporters
"""

from .pdca_metrics import (
    pdca_cycles_total,
    pdca_phase_duration_seconds,
    pdca_quality_score,
    pdca_lessons_learned_total,
    pdca_patterns_detected_total,
    pdca_deviations_total,
    track_pdca_phase,
    track_pdca_metrics,
    initialize_pdca_metrics
)

from .process_metrics import (
    # Counters
    process_framework_process_started_total,
    process_framework_process_completed_total,
    process_framework_step_executed_total,
    process_framework_validation_errors_total,
    process_framework_documents_generated_total,
    # Histograms
    process_framework_step_execution_duration_seconds,
    process_framework_process_duration_seconds,
    # Gauges
    process_framework_active_instances,
    process_framework_pending_approvals,
    # Class and decorators
    ProcessMetrics,
    process_metrics,
    track_process_execution,
    track_step_execution,
    track_validation
)

__all__ = [
    # PDCA Metrics
    'pdca_cycles_total',
    'pdca_phase_duration_seconds',
    'pdca_quality_score',
    'pdca_lessons_learned_total',
    'pdca_patterns_detected_total',
    'pdca_deviations_total',
    'track_pdca_phase',
    'track_pdca_metrics',
    'initialize_pdca_metrics',
    # Process Framework Metrics - Counters
    'process_framework_process_started_total',
    'process_framework_process_completed_total',
    'process_framework_step_executed_total',
    'process_framework_validation_errors_total',
    'process_framework_documents_generated_total',
    # Process Framework Metrics - Histograms
    'process_framework_step_execution_duration_seconds',
    'process_framework_process_duration_seconds',
    # Process Framework Metrics - Gauges
    'process_framework_active_instances',
    'process_framework_pending_approvals',
    # Process Framework - Class and decorators
    'ProcessMetrics',
    'process_metrics',
    'track_process_execution',
    'track_step_execution',
    'track_validation'
]
