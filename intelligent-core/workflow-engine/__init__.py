"""
Platform Core - Layer 1 (Domain-Agnostic System Functions)

Core platform services that work independently of business domain:
- Workflow orchestration (BPMN + AI)
- Learning systems
- Coordination
- Community intelligence
- Collective intelligence

These are REUSABLE across ANY domain (not just BCM).

Version: 1.0.0
Created: 2025-10-05
"""

__version__ = "1.0.0"

# Workflow module
from .workflow import (
    UnifiedWorkflowEngine,
    BPMNProcess,
    ProcessInstance,
    Task,
    ProcessStatus,
    TaskStatus,
    TaskType,
    VisualState,
    DatabaseManager
)

__all__ = [
    # Main engine
    "UnifiedWorkflowEngine",

    # Models
    "BPMNProcess",
    "ProcessInstance",
    "Task",
    "ProcessStatus",
    "TaskStatus",
    "TaskType",
    "VisualState",

    # Database
    "DatabaseManager"
]
