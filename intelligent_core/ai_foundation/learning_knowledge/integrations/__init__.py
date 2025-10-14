"""Integrations with other platform components"""

from .workflow_intelligence_adapter import (
    WorkflowIntelligenceAdapter,
    integrate_with_workflow_engine
)

__all__ = [
    "WorkflowIntelligenceAdapter",
    "integrate_with_workflow_engine"
]
