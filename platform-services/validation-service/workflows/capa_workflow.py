"""
CAPA Workflow
State machine for CAPA lifecycle: open → in_progress → implemented → verified → closed
"""

from enum import Enum
from typing import Dict, Tuple, Optional
from datetime import datetime

class CAPAWorkflowState(str, Enum):
    """CAPA workflow states"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    CLOSED = "closed"
    REJECTED = "rejected"

class CAPAWorkflowAction(str, Enum):
    """CAPA workflow actions"""
    START = "start"
    IMPLEMENT = "implement"
    VERIFY = "verify"
    CLOSE = "close"
    REJECT = "reject"
    REOPEN = "reopen"

# State transitions
CAPA_TRANSITIONS: Dict[Tuple[CAPAWorkflowState, CAPAWorkflowAction], CAPAWorkflowState] = {
    # From OPEN
    (CAPAWorkflowState.OPEN, CAPAWorkflowAction.START): CAPAWorkflowState.IN_PROGRESS,
    (CAPAWorkflowState.OPEN, CAPAWorkflowAction.REJECT): CAPAWorkflowState.REJECTED,

    # From IN_PROGRESS
    (CAPAWorkflowState.IN_PROGRESS, CAPAWorkflowAction.IMPLEMENT): CAPAWorkflowState.IMPLEMENTED,

    # From IMPLEMENTED
    (CAPAWorkflowState.IMPLEMENTED, CAPAWorkflowAction.VERIFY): CAPAWorkflowState.VERIFIED,
    (CAPAWorkflowState.IMPLEMENTED, CAPAWorkflowAction.REOPEN): CAPAWorkflowState.IN_PROGRESS,

    # From VERIFIED
    (CAPAWorkflowState.VERIFIED, CAPAWorkflowAction.CLOSE): CAPAWorkflowState.CLOSED,
    (CAPAWorkflowState.VERIFIED, CAPAWorkflowAction.REOPEN): CAPAWorkflowState.IN_PROGRESS,

    # From CLOSED
    (CAPAWorkflowState.CLOSED, CAPAWorkflowAction.REOPEN): CAPAWorkflowState.IN_PROGRESS,

    # From REJECTED
    (CAPAWorkflowState.REJECTED, CAPAWorkflowAction.REOPEN): CAPAWorkflowState.OPEN,
}

def can_transition_capa(current_state: CAPAWorkflowState, action: CAPAWorkflowAction) -> bool:
    """Check if transition is valid"""
    return (current_state, action) in CAPA_TRANSITIONS

def get_next_capa_state(current_state: CAPAWorkflowState, action: CAPAWorkflowAction) -> Optional[CAPAWorkflowState]:
    """Get next state for action"""
    return CAPA_TRANSITIONS.get((current_state, action))

def validate_capa_transition(current_state: CAPAWorkflowState, action: CAPAWorkflowAction) -> Tuple[bool, Optional[str]]:
    """
    Validate state transition
    Returns: (is_valid, error_message)
    """
    if not can_transition_capa(current_state, action):
        return False, f"Invalid transition: {current_state.value} + {action.value}"
    return True, None

# State-specific validations

def can_implement_capa(capa) -> Tuple[bool, Optional[str]]:
    """Check if CAPA can be marked as implemented"""
    if capa.status != CAPAWorkflowState.IN_PROGRESS.value:
        return False, f"CAPA must be in progress, current: {capa.status}"

    if not capa.action_plan:
        return False, "Action plan must be defined before implementing"

    if not capa.implementation_evidence or len(capa.implementation_evidence) == 0:
        return False, "Implementation evidence is required"

    return True, None

def can_verify_capa(capa) -> Tuple[bool, Optional[str]]:
    """Check if CAPA can be verified"""
    if capa.status != CAPAWorkflowState.IMPLEMENTED.value:
        return False, f"CAPA must be implemented to verify, current: {capa.status}"

    if not capa.implementation_date:
        return False, "Implementation date must be set"

    if capa.verification_required and not capa.verification_date:
        return False, "Verification date must be set for CAPAs requiring verification"

    return True, None

def can_close_capa(capa) -> Tuple[bool, Optional[str]]:
    """Check if CAPA can be closed"""
    if capa.status != CAPAWorkflowState.VERIFIED.value:
        return False, f"CAPA must be verified before closing, current: {capa.status}"

    if capa.verification_required and not capa.effectiveness_verified:
        return False, "Effectiveness must be verified before closing"

    return True, None

# Root cause analysis helper
def validate_root_cause_analysis(capa) -> Tuple[bool, Optional[str]]:
    """Validate that root cause analysis is sufficient"""
    if not capa.root_cause_analysis or len(capa.root_cause_analysis) < 50:
        return False, "Root cause analysis must be detailed (minimum 50 characters)"

    # For corrective actions, RCA is mandatory
    if capa.capa_type == 'corrective' and not capa.root_cause_category:
        return False, "Root cause category must be specified for corrective actions"

    return True, None

# State entry actions
CAPA_STATE_ENTRY_ACTIONS = {
    CAPAWorkflowState.IN_PROGRESS: {
        'notify_assigned_person': True,
        'set_start_date': True,
        'create_task_reminders': True,
    },
    CAPAWorkflowState.IMPLEMENTED: {
        'set_implementation_date': True,
        'notify_verifier': True,
        'request_verification': True,
    },
    CAPAWorkflowState.VERIFIED: {
        'set_verification_date': True,
        'prepare_closure_report': True,
        'notify_stakeholders': True,
    },
    CAPAWorkflowState.CLOSED: {
        'set_closure_date': True,
        'update_source_record': True,  # Update audit/exercise/incident
        'archive_capa': True,
        'calculate_metrics': True,
    },
}

def get_capa_state_entry_actions(state: CAPAWorkflowState) -> dict:
    """Get actions to execute when entering a state"""
    return CAPA_STATE_ENTRY_ACTIONS.get(state, {})

# Priority-based SLA (Service Level Agreement)
def get_capa_due_date_days(priority: str) -> int:
    """Get default due date in days based on priority"""
    priority_sla = {
        'critical': 7,    # 1 week
        'high': 30,       # 1 month
        'medium': 90,     # 3 months
        'low': 180,       # 6 months
    }
    return priority_sla.get(priority, 90)
