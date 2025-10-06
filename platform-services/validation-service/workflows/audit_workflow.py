"""
Audit Workflow
State machine for audit lifecycle: planned → in_progress → fieldwork_complete → report_draft → reported → closed
"""

from enum import Enum
from typing import Dict, Tuple, Optional
from datetime import datetime

class AuditWorkflowState(str, Enum):
    """Audit workflow states"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    FIELDWORK_COMPLETE = "fieldwork_complete"
    REPORT_DRAFT = "report_draft"
    REPORTED = "reported"
    CLOSED = "closed"

class AuditWorkflowAction(str, Enum):
    """Audit workflow actions"""
    START = "start"
    COMPLETE_FIELDWORK = "complete_fieldwork"
    DRAFT_REPORT = "draft_report"
    ISSUE_REPORT = "issue_report"
    CLOSE = "close"
    REOPEN = "reopen"

# State transitions
AUDIT_TRANSITIONS: Dict[Tuple[AuditWorkflowState, AuditWorkflowAction], AuditWorkflowState] = {
    # From PLANNED
    (AuditWorkflowState.PLANNED, AuditWorkflowAction.START): AuditWorkflowState.IN_PROGRESS,

    # From IN_PROGRESS
    (AuditWorkflowState.IN_PROGRESS, AuditWorkflowAction.COMPLETE_FIELDWORK): AuditWorkflowState.FIELDWORK_COMPLETE,

    # From FIELDWORK_COMPLETE
    (AuditWorkflowState.FIELDWORK_COMPLETE, AuditWorkflowAction.DRAFT_REPORT): AuditWorkflowState.REPORT_DRAFT,

    # From REPORT_DRAFT
    (AuditWorkflowState.REPORT_DRAFT, AuditWorkflowAction.ISSUE_REPORT): AuditWorkflowState.REPORTED,
    (AuditWorkflowState.REPORT_DRAFT, AuditWorkflowAction.REOPEN): AuditWorkflowState.FIELDWORK_COMPLETE,

    # From REPORTED
    (AuditWorkflowState.REPORTED, AuditWorkflowAction.CLOSE): AuditWorkflowState.CLOSED,

    # From CLOSED
    (AuditWorkflowState.CLOSED, AuditWorkflowAction.REOPEN): AuditWorkflowState.REPORTED,
}

def can_transition_audit(current_state: AuditWorkflowState, action: AuditWorkflowAction) -> bool:
    """Check if transition is valid"""
    return (current_state, action) in AUDIT_TRANSITIONS

def get_next_audit_state(current_state: AuditWorkflowState, action: AuditWorkflowAction) -> Optional[AuditWorkflowState]:
    """Get next state for action"""
    return AUDIT_TRANSITIONS.get((current_state, action))

def validate_audit_transition(current_state: AuditWorkflowState, action: AuditWorkflowAction) -> Tuple[bool, Optional[str]]:
    """
    Validate state transition
    Returns: (is_valid, error_message)
    """
    if not can_transition_audit(current_state, action):
        return False, f"Invalid transition: {current_state.value} + {action.value}"
    return True, None

# State-specific validations

def can_start_audit(audit) -> Tuple[bool, Optional[str]]:
    """Check if audit can be started"""
    if audit.status != AuditWorkflowState.PLANNED.value:
        return False, f"Cannot start audit from state: {audit.status}"

    if not audit.lead_auditor:
        return False, "Lead auditor must be assigned before starting"

    if not audit.audit_scope:
        return False, "Audit scope must be defined"

    if not audit.audit_criteria or len(audit.audit_criteria) == 0:
        return False, "Audit criteria must be defined"

    return True, None

def can_complete_fieldwork(audit) -> Tuple[bool, Optional[str]]:
    """Check if fieldwork can be completed"""
    if audit.status != AuditWorkflowState.IN_PROGRESS.value:
        return False, f"Audit must be in progress, current: {audit.status}"

    if not audit.actual_start_date:
        return False, "Audit must have an actual start date"

    # Should have at least some findings or observations
    if audit.findings_count == 0:
        return False, "Audit should have at least one finding or observation before completing fieldwork"

    return True, None

def can_issue_report(audit) -> Tuple[bool, Optional[str]]:
    """Check if report can be issued"""
    if audit.status != AuditWorkflowState.REPORT_DRAFT.value:
        return False, f"Report must be in draft state, current: {audit.status}"

    if not audit.audit_report:
        return False, "Audit report must be written before issuing"

    # All major findings should have corrective actions assigned
    if audit.major_findings > 0 and audit.corrective_actions_required == 0:
        return False, "Major findings require corrective actions to be assigned"

    return True, None

# State entry actions
AUDIT_STATE_ENTRY_ACTIONS = {
    AuditWorkflowState.IN_PROGRESS: {
        'set_start_date': True,
        'notify_auditees': True,
        'send_checklist': True,
    },
    AuditWorkflowState.FIELDWORK_COMPLETE: {
        'set_fieldwork_end_date': True,
        'summarize_findings': True,
        'prepare_report_template': True,
    },
    AuditWorkflowState.REPORTED: {
        'set_report_date': True,
        'distribute_report': True,
        'create_capa_items': True,
        'notify_management': True,
    },
    AuditWorkflowState.CLOSED: {
        'verify_all_capa_closed': True,
        'archive_audit': True,
        'update_audit_programme': True,
    },
}

def get_audit_state_entry_actions(state: AuditWorkflowState) -> dict:
    """Get actions to execute when entering a state"""
    return AUDIT_STATE_ENTRY_ACTIONS.get(state, {})
