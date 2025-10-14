"""
Validation Module Workflows
"""

from .exercise_workflow import (
    ExerciseWorkflowState,
    ExerciseWorkflowAction,
    can_transition_exercise,
    get_next_exercise_state,
    validate_exercise_transition,
    can_start_exercise,
    can_complete_exercise,
    can_review_exercise,
    get_exercise_state_entry_actions,
)

from .audit_workflow import (
    AuditWorkflowState,
    AuditWorkflowAction,
    can_transition_audit,
    get_next_audit_state,
    validate_audit_transition,
    can_start_audit,
    can_complete_fieldwork,
    can_issue_report,
    get_audit_state_entry_actions,
)

from .capa_workflow import (
    CAPAWorkflowState,
    CAPAWorkflowAction,
    can_transition_capa,
    get_next_capa_state,
    validate_capa_transition,
    can_implement_capa,
    can_verify_capa,
    can_close_capa,
    get_capa_state_entry_actions,
)

from .kpi_calculations import (
    calculate_kpi_status,
    calculate_kpi_trend,
    calculate_performance_threshold,
    aggregate_measurements,
    get_kpi_summary,
)

__all__ = [
    # Exercise workflow
    'ExerciseWorkflowState',
    'ExerciseWorkflowAction',
    'can_transition_exercise',
    'get_next_exercise_state',
    'validate_exercise_transition',
    'can_start_exercise',
    'can_complete_exercise',
    'can_review_exercise',
    'get_exercise_state_entry_actions',
    # Audit workflow
    'AuditWorkflowState',
    'AuditWorkflowAction',
    'can_transition_audit',
    'get_next_audit_state',
    'validate_audit_transition',
    'can_start_audit',
    'can_complete_fieldwork',
    'can_issue_report',
    'get_audit_state_entry_actions',
    # CAPA workflow
    'CAPAWorkflowState',
    'CAPAWorkflowAction',
    'can_transition_capa',
    'get_next_capa_state',
    'validate_capa_transition',
    'can_implement_capa',
    'can_verify_capa',
    'can_close_capa',
    'get_capa_state_entry_actions',
    # KPI calculations
    'calculate_kpi_status',
    'calculate_kpi_trend',
    'calculate_performance_threshold',
    'aggregate_measurements',
    'get_kpi_summary',
]
