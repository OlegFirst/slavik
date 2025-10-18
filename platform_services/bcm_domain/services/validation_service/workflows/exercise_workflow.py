"""
Exercise Workflow
State machine for exercise lifecycle: planned → scheduled → in_progress → completed → reviewed

Based on: bcm_exercise/models/models.py (lines 56-62)
Reference: /services/SERVICES/BCM/governance/workflows/policy_workflow.py
"""

from enum import Enum
from typing import Dict, Tuple, Optional
from datetime import datetime

class ExerciseWorkflowState(str, Enum):
    """Exercise workflow states"""
    PLANNED = "planned"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    CANCELLED = "cancelled"

class ExerciseWorkflowAction(str, Enum):
    """Exercise workflow actions"""
    SCHEDULE = "schedule"
    START = "start"
    COMPLETE = "complete"
    REVIEW = "review"
    CANCEL = "cancel"
    REOPEN = "reopen"

# State transitions: (current_state, action) -> next_state
EXERCISE_TRANSITIONS: Dict[Tuple[ExerciseWorkflowState, ExerciseWorkflowAction], ExerciseWorkflowState] = {
    # From PLANNED
    (ExerciseWorkflowState.PLANNED, ExerciseWorkflowAction.SCHEDULE): ExerciseWorkflowState.SCHEDULED,
    (ExerciseWorkflowState.PLANNED, ExerciseWorkflowAction.CANCEL): ExerciseWorkflowState.CANCELLED,

    # From SCHEDULED
    (ExerciseWorkflowState.SCHEDULED, ExerciseWorkflowAction.START): ExerciseWorkflowState.IN_PROGRESS,
    (ExerciseWorkflowState.SCHEDULED, ExerciseWorkflowAction.CANCEL): ExerciseWorkflowState.CANCELLED,

    # From IN_PROGRESS
    (ExerciseWorkflowState.IN_PROGRESS, ExerciseWorkflowAction.COMPLETE): ExerciseWorkflowState.COMPLETED,

    # From COMPLETED
    (ExerciseWorkflowState.COMPLETED, ExerciseWorkflowAction.REVIEW): ExerciseWorkflowState.REVIEWED,
    (ExerciseWorkflowState.COMPLETED, ExerciseWorkflowAction.REOPEN): ExerciseWorkflowState.IN_PROGRESS,

    # From CANCELLED
    (ExerciseWorkflowState.CANCELLED, ExerciseWorkflowAction.REOPEN): ExerciseWorkflowState.PLANNED,
}

def can_transition_exercise(current_state: ExerciseWorkflowState, action: ExerciseWorkflowAction) -> bool:
    """Check if transition is valid"""
    return (current_state, action) in EXERCISE_TRANSITIONS

def get_next_exercise_state(current_state: ExerciseWorkflowState, action: ExerciseWorkflowAction) -> Optional[ExerciseWorkflowState]:
    """Get next state for action"""
    return EXERCISE_TRANSITIONS.get((current_state, action))

def validate_exercise_transition(current_state: ExerciseWorkflowState, action: ExerciseWorkflowAction) -> Tuple[bool, Optional[str]]:
    """
    Validate state transition
    Returns: (is_valid, error_message)
    """
    if not can_transition_exercise(current_state, action):
        return False, f"Invalid transition: {current_state.value} + {action.value}"
    return True, None

# State-specific validations

def can_start_exercise(exercise) -> Tuple[bool, Optional[str]]:
    """Check if exercise can be started"""
    if exercise.status != ExerciseWorkflowState.SCHEDULED.value:
        return False, f"Cannot start exercise from state: {exercise.status}"

    if not exercise.facilitator:
        return False, "Facilitator must be assigned before starting"

    if not exercise.participants or len(exercise.participants) == 0:
        return False, "At least one participant must be assigned"

    return True, None

def can_complete_exercise(exercise) -> Tuple[bool, Optional[str]]:
    """Check if exercise can be completed"""
    if exercise.status != ExerciseWorkflowState.IN_PROGRESS.value:
        return False, f"Exercise must be in progress to complete, current: {exercise.status}"

    if not exercise.actual_start_date:
        return False, "Exercise must have an actual start date"

    return True, None

def can_review_exercise(exercise) -> Tuple[bool, Optional[str]]:
    """Check if exercise can be reviewed"""
    if exercise.status != ExerciseWorkflowState.COMPLETED.value:
        return False, f"Exercise must be completed to review, current: {exercise.status}"

    # Check if debrief happened (lessons learned captured)
    if not exercise.lessons_learned:
        return False, "Lessons learned must be captured before review"

    return True, None

# State entry actions (what happens when entering a state)
EXERCISE_STATE_ENTRY_ACTIONS = {
    ExerciseWorkflowState.SCHEDULED: {
        'notify_participants': True,
        'send_materials': True,
        'create_calendar_event': True,
    },
    ExerciseWorkflowState.IN_PROGRESS: {
        'set_start_time': True,
        'activate_scenario': True,
        'start_timer': True,
        'notify_observers': True,
    },
    ExerciseWorkflowState.COMPLETED: {
        'set_end_time': True,
        'calculate_duration': True,
        'collect_feedback': True,
        'generate_initial_report': True,
    },
    ExerciseWorkflowState.REVIEWED: {
        'create_corrective_actions': True,
        'update_scenario_library': True,
        'distribute_report': True,
        'notify_stakeholders': True,
    },
}

def get_exercise_state_entry_actions(state: ExerciseWorkflowState) -> dict:
    """Get actions to execute when entering a state"""
    return EXERCISE_STATE_ENTRY_ACTIONS.get(state, {})
