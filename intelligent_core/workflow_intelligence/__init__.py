"""
 WORKFLOW INTELLIGENCE ENGINE

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

# Infrastructure exports
from .infrastructure.process_framework import (
    ProcessDefinition,
    ProcessStep,
    ProcessInstance,
    ProcessFramework,
    get_process_framework
)

from .infrastructure.templates import (
    DocumentTemplate,
    DocumentTemplateLibrary,
    get_document_library
)

from .infrastructure.orchestration import (
    ProcessOrchestrator,
    get_process_orchestrator
)

from .workflows import (
    create_bia_process,
    create_risk_assessment_process,
    create_bc_plan_process,
    register_all_bcm_processes
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

    # Infrastructure - Process Framework
    "ProcessDefinition",
    "ProcessStep",
    "ProcessInstance",
    "ProcessFramework",
    "get_process_framework",

    # Infrastructure - Templates
    "DocumentTemplate",
    "DocumentTemplateLibrary",
    "get_document_library",

    # Infrastructure - Orchestration
    "ProcessOrchestrator",
    "get_process_orchestrator",

    # Workflows - BCM Processes
    "create_bia_process",
    "create_risk_assessment_process",
    "create_bc_plan_process",
    "register_all_bcm_processes",

    # Initialization
    "initialize",
    "quick_start",
]


# Production initialization helper
async def initialize(
    module: str,
    existing_state_machine,
    db_manager,
    vector_db_client=None
):
    """
    Production initialization для workflow intelligence

    Args:
        module: Module name (bia, risk, planning, etc)
        existing_state_machine: Existing state machine instance
        db_manager: DatabaseManager from shared.database
        vector_db_client: Optional Qdrant client for semantic search

    Example:
        from intelligent_core.workflow_intelligence import initialize
        from shared.database import get_db_manager
        from bia.workflows.state_machine import BIAWorkflowEngine

        db_manager = get_db_manager()
        workflow, advisor = await initialize("bia", BIAWorkflowEngine, db_manager)

    Returns:
        tuple: (WorkflowEngine, ContextAdvisor)
    """
    from .storage.postgres_adapter import PostgresStorageAdapter
    from .case_library.repository import CaseRepository

    # Real PostgreSQL storage
    storage = PostgresStorageAdapter(db_manager)
    await storage.connect()

    # Create workflow engine
    workflow = WorkflowEngine(
        module=module,
        state_machine=existing_state_machine,
        storage_adapter=storage
    )

    # Real case repository with optional vector search
    async for session in db_manager.get_session():
        case_repository = CaseRepository(
            db_session=session,
            vector_db_client=vector_db_client
        )
        break

    # Real context advisor
    advisor = ContextAdvisor(
        workflow_engine=workflow,
        case_library=case_repository
    )

    return workflow, advisor


# Quick start helper (DEPRECATED - for development/testing only)
def quick_start(module: str, existing_state_machine):
    """
    Quick start для интеграции с существующим state machine

    ️ DEPRECATED: Use `initialize()` for production!
    This uses in-memory storage and demo case library.

    Example:
        from intelligent_core.workflow_intelligence import quick_start
        from bia.workflows.state_machine import BIAWorkflowEngine

        workflow, advisor = quick_start("bia", BIAWorkflowEngine)
    """
    import warnings
    warnings.warn(
        "quick_start() is deprecated. Use initialize() with DatabaseManager for production.",
        DeprecationWarning,
        stacklevel=2
    )

    from .core.workflow_engine import InMemoryStorageAdapter

    storage = InMemoryStorageAdapter()

    workflow = WorkflowEngine(
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
