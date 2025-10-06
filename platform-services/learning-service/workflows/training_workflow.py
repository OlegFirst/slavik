"""
Training Enrollment Workflow
State machine for training lifecycle: enrolled → in_progress → completed → certified

Reference: /services/SERVICES/BCM/governance/workflows/policy_workflow.py
"""

from enum import Enum
from typing import Dict, Tuple, Optional
from datetime import datetime

# Import EnrollmentStatus from database models to use as EnrollmentState
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.database import EnrollmentStatus as EnrollmentState

class EnrollmentAction(str, Enum):
    """Training enrollment actions"""
    SUBMIT = "submit"
    APPROVE = "approve"
    START = "start"
    START_TRAINING = "start_training"
    UPDATE_PROGRESS = "update_progress"
    COMPLETE = "complete"
    COMPLETE_TRAINING = "complete_training"
    PASS_ASSESSMENT = "pass_assessment"
    FAIL_ASSESSMENT = "fail_assessment"
    CERTIFY = "certify"
    ISSUE_CERTIFICATION = "issue_certification"
    WITHDRAW = "withdraw"
    REENROLL = "reenroll"

# State transitions: (current_state, action) -> next_state
TRANSITIONS: Dict[Tuple[EnrollmentState, EnrollmentAction], EnrollmentState] = {
    # From DRAFT
    (EnrollmentState.DRAFT, EnrollmentAction.SUBMIT): EnrollmentState.SUBMITTED,
    (EnrollmentState.DRAFT, EnrollmentAction.WITHDRAW): EnrollmentState.WITHDRAWN,

    # From SUBMITTED
    (EnrollmentState.SUBMITTED, EnrollmentAction.APPROVE): EnrollmentState.APPROVED,
    (EnrollmentState.SUBMITTED, EnrollmentAction.WITHDRAW): EnrollmentState.WITHDRAWN,

    # From APPROVED
    (EnrollmentState.APPROVED, EnrollmentAction.START): EnrollmentState.IN_PROGRESS,
    (EnrollmentState.APPROVED, EnrollmentAction.START_TRAINING): EnrollmentState.IN_PROGRESS,
    (EnrollmentState.APPROVED, EnrollmentAction.WITHDRAW): EnrollmentState.WITHDRAWN,

    # From ENROLLED
    (EnrollmentState.ENROLLED, EnrollmentAction.START_TRAINING): EnrollmentState.IN_PROGRESS,
    (EnrollmentState.ENROLLED, EnrollmentAction.START): EnrollmentState.IN_PROGRESS,
    (EnrollmentState.ENROLLED, EnrollmentAction.WITHDRAW): EnrollmentState.WITHDRAWN,

    # From IN_PROGRESS
    (EnrollmentState.IN_PROGRESS, EnrollmentAction.UPDATE_PROGRESS): EnrollmentState.IN_PROGRESS,
    (EnrollmentState.IN_PROGRESS, EnrollmentAction.COMPLETE_TRAINING): EnrollmentState.COMPLETED,
    (EnrollmentState.IN_PROGRESS, EnrollmentAction.COMPLETE): EnrollmentState.COMPLETED,
    (EnrollmentState.IN_PROGRESS, EnrollmentAction.WITHDRAW): EnrollmentState.WITHDRAWN,

    # From COMPLETED
    (EnrollmentState.COMPLETED, EnrollmentAction.PASS_ASSESSMENT): EnrollmentState.ASSESSED,
    (EnrollmentState.COMPLETED, EnrollmentAction.FAIL_ASSESSMENT): EnrollmentState.FAILED,
    (EnrollmentState.COMPLETED, EnrollmentAction.ISSUE_CERTIFICATION): EnrollmentState.CERTIFIED,

    # From ASSESSED
    (EnrollmentState.ASSESSED, EnrollmentAction.PASS_ASSESSMENT): EnrollmentState.ASSESSED,
    (EnrollmentState.ASSESSED, EnrollmentAction.FAIL_ASSESSMENT): EnrollmentState.FAILED,
    (EnrollmentState.ASSESSED, EnrollmentAction.CERTIFY): EnrollmentState.CERTIFIED,
    (EnrollmentState.ASSESSED, EnrollmentAction.ISSUE_CERTIFICATION): EnrollmentState.CERTIFIED,

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

def validate_progress_update(progress_data: dict) -> Tuple[bool, Optional[str]]:
    """Validate progress percentage update"""
    progress = progress_data.get("progress_percentage", 0)
    current = progress_data.get("current_progress", 0)

    if not 0 <= progress <= 100:
        return False, f"Progress must be between 0 and 100, got {progress}"

    # Progress should not decrease (unless explicitly allowed)
    if progress < current:
        return False, f"Progress cannot decrease from {current}% to {progress}%"

    return True, None

def validate_assessment_score(score: float, passing_score: int = 70) -> Tuple[bool, Optional[str]]:
    """Validate assessment score"""
    if not 0 <= score <= 100:
        return False, f"Score must be between 0 and 100, got {score}"
    return True, None

def validate_assessment_attempts(current_attempts: int, max_attempts: int = 3) -> Tuple[bool, Optional[str]]:
    """
    Validate assessment attempts

    Args:
        current_attempts: Current number of attempts
        max_attempts: Maximum allowed attempts (default: 3)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if current_attempts >= max_attempts:
        return False, f"Maximum assessment attempts ({max_attempts}) exceeded"
    return True, None

def determine_assessment_result(score: float, passing_score: int) -> EnrollmentAction:
    """Determine if assessment passed or failed"""
    return EnrollmentAction.PASS_ASSESSMENT if score >= passing_score else EnrollmentAction.FAIL_ASSESSMENT

# Workflow helper functions
def can_start_training(status: str, approved_date: Optional[datetime] = None) -> Tuple[bool, Optional[str]]:
    """
    Check if training can be started

    Args:
        status: Current enrollment status
        approved_date: Date when enrollment was approved (optional)

    Returns:
        Tuple of (can_start, error_message)
    """
    # For now, we're using DRAFT/SUBMITTED/APPROVED workflow states
    # Training can start from APPROVED state
    if status not in [EnrollmentState.IN_PROGRESS.value, "approved", "draft", "submitted"]:
        return False, f"Cannot start training from state: {status}"
    return True, None

def can_complete_training(
    status: str,
    progress_percentage: int,
    time_spent_minutes: Optional[int] = None,
    required_progress: int = 100
) -> Tuple[bool, Optional[str]]:
    """
    Check if training can be completed

    Args:
        status: Current enrollment status
        progress_percentage: Current progress percentage
        time_spent_minutes: Time spent in minutes (optional)
        required_progress: Required progress percentage (default: 100)

    Returns:
        Tuple of (can_complete, error_message)
    """
    if status != EnrollmentState.IN_PROGRESS.value:
        return False, f"Training must be in progress to complete, current: {status}"
    if progress_percentage < required_progress:
        return False, f"Progress must be {required_progress}%, current: {progress_percentage}%"
    return True, None

def can_issue_certification(
    status: str,
    assessment_passed: bool,
    certification_awarded: bool
) -> Tuple[bool, Optional[str]]:
    """
    Check if certification can be issued

    Args:
        status: Current enrollment status
        assessment_passed: Whether assessment was passed
        certification_awarded: Whether program awards certification

    Returns:
        Tuple of (can_issue, error_message)
    """
    if not certification_awarded:
        return False, "Program does not award certification"
    if status != EnrollmentState.ASSESSED.value:
        return False, f"Training must be assessed to certify, current: {status}"
    if not assessment_passed:
        return False, "Assessment must be passed before certification"
    return True, None

def auto_progress_calculation(modules_completed: list, total_modules: int) -> int:
    """Calculate progress based on completed modules"""
    if total_modules == 0:
        return 0
    return int((len(modules_completed) / total_modules) * 100)

def validate_enrollment_deadline(
    target_completion_date: Optional[datetime],
    program_duration_hours: Optional[int],
    enrolled_date: datetime = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate enrollment deadline against program duration

    Args:
        target_completion_date: Target completion date
        program_duration_hours: Program duration in hours
        enrolled_date: Enrollment date (defaults to now)

    Returns:
        Tuple of (is_valid, warning_message)
    """
    if not target_completion_date or not program_duration_hours:
        return True, None

    if enrolled_date is None:
        enrolled_date = datetime.utcnow()

    # Calculate time available
    time_available = (target_completion_date - enrolled_date).total_seconds() / 3600  # hours

    # Minimum realistic time is 1.5x program duration (for pacing)
    minimum_time_needed = program_duration_hours * 1.5

    if time_available < minimum_time_needed:
        warning = (
            f"Target completion date may be too aggressive. "
            f"Program requires {program_duration_hours}h, "
            f"recommended time: {minimum_time_needed}h, "
            f"available time: {time_available:.1f}h"
        )
        return True, warning  # Warning, not error

    return True, None

def should_auto_complete(
    progress_percentage: int,
    time_spent_minutes: Optional[int],
    program_duration_hours: Optional[int],
    current_status: str
) -> Tuple[bool, Optional[str]]:
    """
    Determine if enrollment should auto-complete

    Args:
        progress_percentage: Current progress
        time_spent_minutes: Time spent in minutes
        program_duration_hours: Program duration in hours
        current_status: Current enrollment status

    Returns:
        Tuple of (should_auto_complete, reason)
    """
    if current_status != EnrollmentState.IN_PROGRESS.value:
        return False, None

    if progress_percentage < 100:
        return False, None

    # Check time requirements if duration is specified
    if program_duration_hours and time_spent_minutes:
        time_spent_hours = time_spent_minutes / 60
        minimum_time_required = program_duration_hours * 0.8  # 80% minimum

        if time_spent_hours < minimum_time_required:
            return False, f"Minimum time requirement not met ({time_spent_hours:.1f}h / {minimum_time_required:.1f}h)"

    return True, "Progress 100% and time requirements met"

def calculate_certification_expiry(
    certification_date: datetime,
    validity_months: Optional[int]
) -> Optional[datetime]:
    """
    Calculate certification expiry date

    Args:
        certification_date: Date of certification
        validity_months: Validity period in months

    Returns:
        Expiry date or None if no validity period
    """
    if not validity_months:
        return None

    from dateutil.relativedelta import relativedelta
    return certification_date + relativedelta(months=validity_months)

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
