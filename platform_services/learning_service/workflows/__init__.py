"""
Learning Module Workflows
"""

from .training_workflow import (
    EnrollmentState,
    EnrollmentAction,
    can_transition,
    get_next_state,
    validate_transition,
    validate_enrollment_data,
    validate_progress_update,
    validate_assessment_score,
    determine_assessment_result,
    can_start_training,
    can_complete_training,
    can_issue_certification,
    auto_progress_calculation,
    get_state_entry_actions,
)

from .gamification_workflow import (
    ActionCategory,
    calculate_points,
    award_points,
    check_achievements,
    calculate_streak,
    get_leaderboard_rank,
    calculate_level,
    get_badge_color,
    get_badge_icon,
)

__all__ = [
    # Training workflow
    'EnrollmentState',
    'EnrollmentAction',
    'can_transition',
    'get_next_state',
    'validate_transition',
    'validate_enrollment_data',
    'validate_progress_update',
    'validate_assessment_score',
    'determine_assessment_result',
    'can_start_training',
    'can_complete_training',
    'can_issue_certification',
    'auto_progress_calculation',
    'get_state_entry_actions',
    # Gamification workflow
    'ActionCategory',
    'calculate_points',
    'award_points',
    'check_achievements',
    'calculate_streak',
    'get_leaderboard_rank',
    'calculate_level',
    'get_badge_color',
    'get_badge_icon',
]
