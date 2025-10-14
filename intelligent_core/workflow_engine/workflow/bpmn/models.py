"""
BPMN Data Models

Pydantic models для BPMN процессов, instances и tasks
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProcessStatus(str, Enum):
    """Status of process instance"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"


class TaskStatus(str, Enum):
    """Status of task"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskType(str, Enum):
    """BPMN task types"""
    USER_TASK = "USER_TASK"
    SERVICE_TASK = "SERVICE_TASK"
    SCRIPT_TASK = "SCRIPT_TASK"
    SEND_TASK = "SEND_TASK"
    RECEIVE_TASK = "RECEIVE_TASK"
    MANUAL_TASK = "MANUAL_TASK"
    BUSINESS_RULE_TASK = "BUSINESS_RULE_TASK"


class BPMNProcess(BaseModel):
    """
    BPMN Process Definition

    Хранит BPMN 2.0 XML и metadata процесса
    """
    id: Optional[str] = None
    tenant_id: str = Field(..., min_length=1, max_length=255)
    module: Optional[str] = Field(None, description="BCM module: bia, risk, compliance, etc")

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    bpmn_xml: str = Field(..., description="BPMN 2.0 XML content")

    version: str = Field(default="1.0")
    is_active: bool = Field(default=True)

    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "BIA Process",
                "tenant_id": "acme-corp",
                "module": "bia",
                "bpmn_xml": '<?xml version="1.0"?><definitions>...</definitions>',
                "version": "1.0"
            }
        }


class ProcessInstance(BaseModel):
    """
    BPMN Process Instance

    Запущенный экземпляр процесса с текущим состоянием
    """
    id: Optional[str] = None
    process_id: str = Field(..., description="Reference to BPMNProcess")
    tenant_id: str = Field(..., min_length=1, max_length=255)

    status: ProcessStatus = Field(default=ProcessStatus.ACTIVE)
    variables: Dict[str, Any] = Field(default_factory=dict, description="Process variables")
    current_activities: List[str] = Field(default_factory=list, description="Currently active activity IDs")

    # Gateway state tracking (for parallel/inclusive gateway joins)
    gateway_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Gateway state tracking for joins. Example: {'Gateway_123': {'incoming_completed': ['Flow1', 'Flow2'], 'incoming_total': ['Flow1', 'Flow2', 'Flow3']}}"
    )

    # Workflow Intelligence link
    workflow_intelligence_id: Optional[str] = Field(None, description="Link to WorkflowEngine tracking")

    started_by: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "process_id": "proc-123",
                "tenant_id": "acme-corp",
                "status": "ACTIVE",
                "variables": {"org_id": "org-456"},
                "current_activities": ["identify_processes"],
                "started_by": "user-789"
            }
        }


class Task(BaseModel):
    """
    BPMN Task

    Задача в рамках process instance (userTask, serviceTask, etc)
    """
    id: Optional[str] = None
    instance_id: str = Field(..., description="Process instance ID", alias="process_instance_id")

    activity_id: str = Field(..., description="BPMN activity ID from XML")
    name: str = Field(..., description="Human-readable task name")
    task_type: TaskType = Field(default=TaskType.USER_TASK)

    assignee: Optional[str] = Field(None, description="User assigned to this task")
    status: TaskStatus = Field(default=TaskStatus.ACTIVE)
    variables: Dict[str, Any] = Field(default_factory=dict, description="Task-specific variables")

    # AI enhancements
    ai_recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="AI recommendations for this task")
    ai_predicted_duration_hours: Optional[float] = Field(None, description="AI prediction of task duration")

    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "process_instance_id": "inst-123",
                "activity_id": "identify_processes",
                "name": "Identify Critical Processes",
                "task_type": "USER_TASK",
                "assignee": "user-789",
                "status": "ACTIVE",
                "ai_recommendations": [
                    {"message": "Start with Emergency Department", "confidence": 0.85}
                ]
            }
        }
        populate_by_name = True


# Request/Response Schemas

class ProcessDeployRequest(BaseModel):
    """Request to deploy BPMN process"""
    name: str
    bpmn_xml: str
    module: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0"


class ProcessStartRequest(BaseModel):
    """Request to start process instance"""
    variables: Dict[str, Any] = Field(default_factory=dict)
    started_by: Optional[str] = None


class TaskCompleteRequest(BaseModel):
    """Request to complete task"""
    variables: Dict[str, Any] = Field(default_factory=dict)
    completed_by: Optional[str] = None


class VisualState(BaseModel):
    """
    Visual state for UI

    Содержит данные для отрисовки BPMN diagram в frontend
    """
    type: str = Field(..., description="bpmn or template")

    # BPMN specific
    bpmn_xml: Optional[str] = None
    current_activities: List[str] = Field(default_factory=list)

    # Tasks
    active_tasks: List[Dict[str, Any]] = Field(default_factory=list)

    # Workflow Intelligence context
    workflow_context: Optional[Dict[str, Any]] = None

    # AI predictions
    predictions: Optional[Dict[str, Any]] = None

    # Visualization hints
    visualization_hints: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "bpmn",
                "bpmn_xml": "<?xml version='1.0'?>...",
                "current_activities": ["identify_processes"],
                "active_tasks": [
                    {
                        "id": "task-123",
                        "name": "Identify Processes",
                        "ai_tip": "Start with critical departments"
                    }
                ],
                "predictions": {
                    "success_probability": 0.85,
                    "estimated_duration_days": 14
                },
                "visualization_hints": {
                    "highlight": ["identify_processes"],
                    "show_ai_overlay": True
                }
            }
        }
