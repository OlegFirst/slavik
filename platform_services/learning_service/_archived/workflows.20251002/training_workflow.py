"""
Training Enrollment Workflow
State machine for training lifecycle: enrolled → in_progress → completed → certified

Reference: /services/SERVICES/BCM/governance/workflows/policy_workflow.py
"""

from enum import Enum
from typing import Dict, Tuple, Optional
from datetime import datetime

class EnrollmentState(str, Enum):
    """Training enrollment states"""
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CERTIFIED = "certified"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"

class EnrollmentAction(str, Enum):
    """Training enrollment actions"""
    START_TRAINING = "start_training"
    UPDATE_PROGRESS = "update_progress"
    COMPLETE_TRAINING = "complete_training"
    PASS_ASSESSMENT = "pass_assessment"
    FAIL_ASSESSMENT = "fail_assessment"
    ISSUE_CERTIFICATION = "issue_certification"
    WITHDRAW = "withdraw"
    REENROLL = "reenroll"

# State transitions: (current_state, action) -> next_state
TRANSITIONS: Dict[Tuple[EnrollmentState, EnrollmentAction], EnrollmentState] = {
    # From ENROLLED
    (EnrollmentState.ENROLLED, EnrollmentAction.START_TRAINING): EnrollmentState.IN_PROGRESS,
    (EnrollmentState.ENROLLED, EnrollmentAction.WITHDRAW): EnrollmentState.WITHDRAWN,

    # From IN_PROGRESS
    (EnrollmentState.IN_PROGRESS, EnrollmentAction.UPDATE_PROGRESS): EnrollmentState.IN_PROGRESS,
    (EnrollmentState.IN_PROGRESS, EnrollmentAction.COMPLETE_TRAINING): EnrollmentState.COMPLETED,
    (EnrollmentState.IN_PROGRESS, EnrollmentAction.WITHDRAW): EnrollmentState.WITHDRAWN,

    # From COMPLETED
    (EnrollmentState.COMPLETED, EnrollmentAction.PASS_ASSESSMENT): EnrollmentState.COMPLETED,
    (EnrollmentState.COMPLETED, EnrollmentAction.FAIL_ASSESSMENT): EnrollmentState.FAILED,
    (EnrollmentState.COMPLETED, EnrollmentAction.ISSUE_CERTIFICATION): EnrollmentState.CERTIFIED,

    # From FAILED
    (EnrollmentState.FAILED, EnrollmentAction.REENROLL): EnrollmentState.IN_PROGRESS,

    # From WITHDRAWN
    (EnrollmentState.WITHDRAWN, EnrollmentAction.REENROLL): EnrollmentState.ENROLLED,
}

def can_transition(current_state: EnrollmentState, action: EnrollmentAction) -> bool:
    """Check if transition is valid"""
    return (current_state, action) in TRANSITIONS

def get_next_state(current_state: EnrollmentState, action: EnrollmentAction) -> Optional[EnrollmentState]:
    """Get next state for action"""
    return TRANSITIONS.get((current_state, action))

def validate_transition(current_state: EnrollmentState, action: EnrollmentAction) -> Tuple[bool, Optional[str]]:
    """
    Validate state transition
    Returns: (is_valid, error_message)
    """
    if not can_transition(current_state, action):
        return False, f"Invalid transition: {current_state.value} + {action.value}"
    return True, None

# State-specific validations
def validate_enrollment_data(enrollment_data: dict) -> Tuple[bool, Optional[str]]:
    """Validate enrollment data"""
    required_fields = ['person_id', 'person_name', 'program_id']
    for field in required_fields:
        if field not in enrollment_data or not enrollment_data[field]:
            return False, f"Missing required field: {field}"
    return True, None

def validate_progress_update(progress: int) -> Tuple[bool, Optional[str]]:
    """Validate progress percentage"""
    if not 0 <= progress <= 100:
        return False, f"Progress must be between 0 and 100, got {progress}"
    return True, None

def validate_assessment_score(score: float, passing_score: int = 70) -> Tuple[bool, Optional[str]]:
    """Validate assessment score"""
    if not 0 <= score <= 100:
        return False, f"Score must be between 0 and 100, got {score}"
    return True, None

def determine_assessment_result(score: float, passing_score: int) -> EnrollmentAction:
    """Determine if assessment passed or failed"""
    return EnrollmentAction.PASS_ASSESSMENT if score >= passing_score else EnrollmentAction.FAIL_ASSESSMENT

# Workflow helper functions
def can_start_training(enrollment) -> Tuple[bool, Optional[str]]:
    """Check if training can be started"""
    if enrollment.status != EnrollmentState.ENROLLED.value:
        return False, f"Cannot start training from state: {enrollment.status}"
    return True, None

def can_complete_training(enrollment, required_progress: int = 100) -> Tuple[bool, Optional[str]]:
    """Check if training can be completed"""
    if enrollment.status != EnrollmentState.IN_PROGRESS.value:
        return False, f"Training must be in progress to complete, current: {enrollment.status}"
    if enrollment.progress_percentage < required_progress:
        return False, f"Progress must be {required_progress}%, current: {enrollment.progress_percentage}%"
    return True, None

def can_issue_certification(enrollment) -> Tuple[bool, Optional[str]]:
    """Check if certification can be issued"""
    if enrollment.status != EnrollmentState.COMPLETED.value:
        return False, f"Training must be completed to certify, current: {enrollment.status}"
    if not enrollment.assessment_passed:
        return False, "Assessment must be passed before certification"
    return True, None

def auto_progress_calculation(modules_completed: list, total_modules: int) -> int:
    """Calculate progress based on completed modules"""
    if total_modules == 0:
        return 0
    return int((len(modules_completed) / total_modules) * 100)

# State entry actions (what happens when entering a state)
STATE_ENTRY_ACTIONS = {
    EnrollmentState.IN_PROGRESS: {
        'set_started_date': True,
        'notify_learner': True,
    },
    EnrollmentState.COMPLETED: {
        'set_completed_date': True,
        'notify_learner': True,
        'award_completion_points': True,
    },
    EnrollmentState.CERTIFIED: {
        'set_certification_date': True,
        'generate_certificate_number': True,
        'calculate_expiry_date': True,
        'notify_learner': True,
        'award_certification_points': True,
    },
    EnrollmentState.FAILED: {
        'notify_learner': True,
        'suggest_remedial_training': True,
    },
}

def get_state_entry_actions(state: EnrollmentState) -> dict:
    """Get actions to execute when entering a state"""
    return STATE_ENTRY_ACTIONS.get(state, {})
