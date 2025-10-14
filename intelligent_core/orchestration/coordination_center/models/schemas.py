"""Pydantic schemas for Coordination Center."""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK_PENDING = "rollback_pending"
    ROLLBACK_COMPLETED = "rollback_completed"
    REQUIRES_APPROVAL = "requires_approval"


class ToolCategory(str, Enum):
    """Tool category enum."""
    BCM = "bcm"
    INTELLIGENCE = "intelligence"
    PLATFORM = "platform"
    AI_COLLEAGUE = "ai_colleague"


class ActionType(str, Enum):
    """Action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SIMULATE = "simulate"
    ANALYZE = "analyze"


# Intent Schemas

class IntentContext(BaseModel):
    """Context for intent execution."""
    tenant_id: str = Field(..., description="Tenant ID")
    user_id: str = Field(default="ai_agent", description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class Intent(BaseModel):
    """AI Intent schema."""
    action: str = Field(..., description="Action to perform (e.g., create_bia, run_simulation)")
    entity: Optional[str] = Field(None, description="Entity type (e.g., process, risk, plan)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action")
    context: IntentContext = Field(..., description="Execution context")
    require_approval: bool = Field(default=False, description="Whether human approval is required")


# Tool Schemas

class ToolParameter(BaseModel):
    """Tool parameter definition."""
    name: str
    type: str  # string, integer, boolean, object, array
    required: bool = True
    description: Optional[str] = None
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


class ToolDefinition(BaseModel):
    """Tool definition schema."""
    tool_id: str = Field(..., description="Unique tool identifier (e.g., bia_tool, digital_twin)")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Tool description")
    category: ToolCategory = Field(..., description="Tool category")
    base_url: str = Field(..., description="Base URL for API calls")
    version: str = Field(default="v1", description="Tool version")

    # Actions supported by this tool
    supported_actions: List[str] = Field(..., description="List of supported actions")

    # API endpoint mapping
    endpoints: Dict[str, str] = Field(
        ...,
        description="Mapping of actions to API endpoints"
    )

    # Parameters for each action
    parameters: Dict[str, List[ToolParameter]] = Field(
        default_factory=dict,
        description="Parameters for each action"
    )

    # Authentication
    requires_auth: bool = Field(default=True, description="Whether tool requires authentication")

    # Rate limiting
    rate_limit: Optional[int] = Field(None, description="Max requests per minute")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# Execution Schemas

class ExecutionStep(BaseModel):
    """Execution step."""
    step: int
    action: str
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ExecutionCreate(BaseModel):
    """Create execution request."""
    intent: Intent


class ExecutionResponse(BaseModel):
    """Execution response."""
    execution_id: str
    status: ExecutionStatus
    steps: List[ExecutionStep] = Field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ExecutionListResponse(BaseModel):
    """List of executions."""
    executions: List[ExecutionResponse]
    total: int


# Approval Schemas

class ApprovalRequest(BaseModel):
    """Human approval request."""
    approved: bool
    reason: Optional[str] = None
    approved_by: str


# Rollback Schemas

class RollbackRequest(BaseModel):
    """Rollback request."""
    reason: str
    initiated_by: str


# Audit Schemas

class AuditLogEntry(BaseModel):
    """Audit log entry."""
    execution_id: str
    action: str
    details: Dict[str, Any]
    timestamp: datetime
    user_id: str
    tenant_id: str


# Tool Registry Schemas

class ToolListResponse(BaseModel):
    """List of available tools."""
    tools: List[ToolDefinition]
    total: int


# Health Check

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    services: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status of external services"
    )
