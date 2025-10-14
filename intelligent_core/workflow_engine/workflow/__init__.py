"""
Unified Workflow Engine - Production Version with PostgreSQL + AI

Combines:
- BPMN Orchestration (PostgreSQL) - Visual process modeling
- Workflow Intelligence - AI recommendations and learning
- Event synchronization - Real-time integration

Usage:
    from intelligent_core.unified_workflow import UnifiedWorkflowEngine

    # Initialize with database (async factory)
    workflow = await UnifiedWorkflowEngine.create(
        tenant_id="acme-corp",
        module="bia",
        workflow_intelligence_enabled=True
    )

    # Start from BPMN visual model
    instance_id = await workflow.start_process_from_bpmn(
        bpmn_xml=bpmn_content,
        process_name="BIA Assessment"
    )

    # Get visual state for UI (with AI recommendations)
    state = await workflow.get_visual_state(instance_id)

    # Complete tasks
    await workflow.complete_task(task_id, variables)

    # Close when done
    await workflow.close()

Phase 2 Features:
- PostgreSQL persistence (all data saved to DB)
- AI recommendations injected into tasks
- Event synchronization (BPMN ↔ Workflow Intelligence)
- Progress tracking and predictions
- Case collection for self-learning
"""

from .core.unified_engine import UnifiedWorkflowEngine
from .bpmn.models import (
    BPMNProcess,
    ProcessInstance,
    Task,
    ProcessStatus,
    TaskStatus,
    TaskType,
    VisualState
)
from .persistence.database import DatabaseManager

__version__ = "2.0.0"

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
