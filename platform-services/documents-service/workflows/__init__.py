"""
Documents Module Workflows Package

Exports all workflow state machines:
- Document Lifecycle Workflow (DRAFT → PUBLISHED → ARCHIVED)
- Approval Workflow (Multi-stage approval chains)
- Retention Workflow (Archive, destruction, legal hold)
"""

from .lifecycle_workflow import (
    DocumentLifecycleState,
    DocumentLifecycleAction,
    LIFECYCLE_TRANSITIONS,
    can_submit_for_review,
    can_approve,
    can_publish,
    can_archive,
    can_supersede,
    can_mark_obsolete,
    can_restore,
    can_revise,
    can_transition as can_transition_lifecycle,
    get_next_state as get_next_lifecycle_state,
    get_available_actions as get_available_lifecycle_actions,
    execute_transition as execute_lifecycle_transition,
    get_workflow_summary,
)

from .approval_workflow import (
    ApprovalWorkflowState,
    ApprovalWorkflowAction,
    ApprovalPriority,
    ApproverRole,
    APPROVAL_TRANSITIONS,
    get_standard_approval_chain,
    can_request_approval,
    can_approve_request,
    can_reject_request,
    can_recall_request,
    can_escalate_request,
    is_approval_chain_complete,
    get_current_approval_stage,
    get_next_approvers,
    calculate_approval_priority,
    calculate_approval_due_date,
    execute_approval_transition,
    get_approval_workflow_summary,
)

from .retention_workflow import (
    RetentionPhase,
    RetentionAction,
    DestructionStatus,
    ISO_22301_RETENTION_PERIODS,
    HIPAA_RETENTION_PERIODS,
    calculate_retention_period,
    calculate_expiration_date,
    is_retention_expired,
    days_until_expiration,
    should_archive_document,
    can_schedule_destruction,
    calculate_destruction_date,
    can_place_legal_hold,
    can_release_legal_hold,
    execute_retention_action,
    get_retention_status,
    get_documents_pending_retention_action,
)

__all__ = [
    # Lifecycle Workflow
    'DocumentLifecycleState',
    'DocumentLifecycleAction',
    'LIFECYCLE_TRANSITIONS',
    'can_submit_for_review',
    'can_approve',
    'can_publish',
    'can_archive',
    'can_supersede',
    'can_mark_obsolete',
    'can_restore',
    'can_revise',
    'can_transition_lifecycle',
    'get_next_lifecycle_state',
    'get_available_lifecycle_actions',
    'execute_lifecycle_transition',
    'get_workflow_summary',

    # Approval Workflow
    'ApprovalWorkflowState',
    'ApprovalWorkflowAction',
    'ApprovalPriority',
    'ApproverRole',
    'APPROVAL_TRANSITIONS',
    'get_standard_approval_chain',
    'can_request_approval',
    'can_approve_request',
    'can_reject_request',
    'can_recall_request',
    'can_escalate_request',
    'is_approval_chain_complete',
    'get_current_approval_stage',
    'get_next_approvers',
    'calculate_approval_priority',
    'calculate_approval_due_date',
    'execute_approval_transition',
    'get_approval_workflow_summary',

    # Retention Workflow
    'RetentionPhase',
    'RetentionAction',
    'DestructionStatus',
    'ISO_22301_RETENTION_PERIODS',
    'HIPAA_RETENTION_PERIODS',
    'calculate_retention_period',
    'calculate_expiration_date',
    'is_retention_expired',
    'days_until_expiration',
    'should_archive_document',
    'can_schedule_destruction',
    'calculate_destruction_date',
    'can_place_legal_hold',
    'can_release_legal_hold',
    'execute_retention_action',
    'get_retention_status',
    'get_documents_pending_retention_action',
]
