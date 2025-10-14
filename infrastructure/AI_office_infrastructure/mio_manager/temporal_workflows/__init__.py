"""
Temporal Workflows for MIO Manager
===================================

Lightweight workflow wrappers following "Temporal as Wrapper" pattern.

Workflows:
- ObservationWorkflow - Continuous platform monitoring
- ReactionWorkflow - Automated problem response
- ReportingWorkflow - Comprehensive reporting
- ControlWorkflow - Task execution monitoring

Pattern Philosophy:
- Temporal provides: durability, retries, long-running support
- Real work done by: integration components (Toolkit, Rules, Actions, etc.)
- Activities are thin wrappers
- Workflows are simple orchestration

Integration Points:
- AutomationToolkitManager (service discovery, metrics)
- ReactionRulesEngine (problem classification)
- ActionExecutor (automated actions)
- EscalationManager (brain escalation)
- workflow_intelligence_client (brain communication)
- coordination_center_client (task coordination)
"""

from .observation_workflow import (
    ObservationWorkflow,
    observation_activities
)

from .reaction_workflow import (
    ReactionWorkflow,
    reaction_activities
)

from .reporting_workflow import (
    ReportingWorkflow,
    reporting_activities
)

from .control_workflow import (
    ControlWorkflow,
    control_activities
)


__all__ = [
    # Workflows
    'ObservationWorkflow',
    'ReactionWorkflow',
    'ReportingWorkflow',
    'ControlWorkflow',

    # Activities (for worker registration)
    'observation_activities',
    'reaction_activities',
    'reporting_activities',
    'control_activities'
]


# Convenience: All workflows list
ALL_WORKFLOWS = [
    ObservationWorkflow,
    ReactionWorkflow,
    ReportingWorkflow,
    ControlWorkflow
]

# Convenience: All activities list
ALL_ACTIVITIES = (
    observation_activities +
    reaction_activities +
    reporting_activities +
    control_activities
)
