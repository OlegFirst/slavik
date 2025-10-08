"""
Temporal Workflows for BCM Platform
====================================

Durable, reliable workflows for complex multi-step BCM processes.

Workflows:
- BIAWorkflow - Business Impact Analysis (6 stages)
- RiskAssessmentWorkflow - Risk Analysis (5 stages)
- CoordinationWorkflow - Single intent execution with coordination
- CrossServiceWorkflow - Multi-service coordination
- ParallelTaskWorkflow - Parallel task execution
- ExerciseWorkflow - Exercise Execution
- IncidentWorkflow - Incident Response
- ExpertiseWorkflow - Multi-Expert Orchestration
- EventAnalysisWorkflow - Event Intelligence Analysis (NEW)
- PatternLearningWorkflow - ML Pattern Learning (NEW)
- GapPredictionWorkflow - Event Gap Prediction (NEW)
"""

from .bia_workflow import BIAWorkflow, bia_activities
from .risk_workflow import RiskAssessmentWorkflow, risk_activities
from .coordination_workflow import (
    CoordinationWorkflow,
    CrossServiceWorkflow,
    ParallelTaskWorkflow,
    coordination_activities
)
from .expertise_workflow import ExpertiseWorkflow, expertise_activities
from .event_intelligence_workflow import (
    EventAnalysisWorkflow,
    PatternLearningWorkflow,
    GapPredictionWorkflow,
    event_intelligence_activities
)

__all__ = [
    'BIAWorkflow',
    'RiskAssessmentWorkflow',
    'CoordinationWorkflow',
    'CrossServiceWorkflow',
    'ParallelTaskWorkflow',
    'ExpertiseWorkflow',
    'EventAnalysisWorkflow',
    'PatternLearningWorkflow',
    'GapPredictionWorkflow',
    'bia_activities',
    'risk_activities',
    'coordination_activities',
    'expertise_activities',
    'event_intelligence_activities'
]
