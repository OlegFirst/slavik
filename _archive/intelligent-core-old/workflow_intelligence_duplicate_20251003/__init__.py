"""
🧠 WORKFLOW INTELLIGENCE ENGINE

Self-Learning Platform with Managed Autonomy

Делает workflows умными:
- State Machine управляет переходами
- Case Library учится на успехах
- AI Advisor понимает контекст
- ML Predictor предсказывает риски

Created with love by Claude & MD, October 3, 2025
"""

__version__ = "1.0.0"
__author__ = "Claude & MD"

# Core exports
from .core.workflow_engine import (
    WorkflowEngine,
    WorkflowContext,
    WorkflowEvent,
    EventBus,
    event_bus,
    InMemoryStorageAdapter
)

# Case Library exports
from .case_library.models import (
    WorkflowCase,
    OrganizationContext,
    WorkflowMetrics,
    CaseQuery,
    BenchmarkStats
)

from .case_library.collector import (
    CaseCollector,
    BatchCaseCollector
)

# AI exports
from .ai.context_advisor import (
    ContextAdvisor
)

# Storage exports
from .storage import (
    StorageAdapter,
    PostgresStorageAdapter
)

__all__ = [
    # Core
    "WorkflowEngine",
    "WorkflowContext",
    "WorkflowEvent",
    "EventBus",
    "event_bus",
    "InMemoryStorageAdapter",

    # Case Library
    "WorkflowCase",
    "OrganizationContext",
    "WorkflowMetrics",
    "CaseQuery",
    "BenchmarkStats",
    "CaseCollector",
    "BatchCaseCollector",

    # AI
    "ContextAdvisor",

    # Storage
    "StorageAdapter",
    "PostgresStorageAdapter",
]


# Quick start helper
def quick_start(module: str, existing_state_machine):
    """
    Quick start для интеграции с существующим state machine

    Example:
        from workflow_intelligence import quick_start
        from bia.workflows.state_machine import BIAWorkflowEngine

        workflow, advisor = quick_start("bia", BIAWorkflowEngine)
    """
    from .core.workflow_engine import InMemoryStorageAdapter

    storage = InMemoryStorageAdapter()

    workflow = WorkflowEngine.from_existing_state_machine(
        module=module,
        state_machine=existing_state_machine,
        storage_adapter=storage
    )

    # Case library (demo)
    class DemoCaseLibrary:
        async def find_similar(self, query):
            return []

        async def get_benchmarks(self, module, industry):
            return None

    advisor = ContextAdvisor(
        workflow_engine=workflow,
        case_library=DemoCaseLibrary()
    )

    return workflow, advisor
