"""
AI Models - Data models for AI orchestration
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentCategory(str, Enum):
    """Incident category enumeration"""
    OPERATIONAL = "operational"
    SECURITY = "security"
    NATURAL = "natural"
    TECHNOLOGY = "technology"
    HUMAN = "human"
    EXTERNAL = "external"


class ActionType(str, Enum):
    """Types of actions the orchestrator can take"""
    GENERATE_PLAN = "generate_plan"
    SUGGEST_RESPONSE = "suggest_response"
    SCHEDULE_TRAINING = "schedule_training"
    RECOMMEND_SCENARIO = "recommend_scenario"
    ANALYZE_COMPLIANCE = "analyze_compliance"
    CREATE_TASK = "create_task"
    SEND_NOTIFICATION = "send_notification"
    TRIGGER_WORKFLOW = "trigger_workflow"


class BusinessProcess(BaseModel):
    """Business process definition"""
    id: str
    name: str
    description: str
    criticality: RiskLevel
    rto_hours: int = Field(..., description="Recovery Time Objective in hours")
    rpo_hours: int = Field(..., description="Recovery Point Objective in hours")
    dependencies: List[str] = Field(default_factory=list)
    resources_required: List[str] = Field(default_factory=list)


class Incident(BaseModel):
    """Incident definition"""
    id: str
    title: str
    description: str
    category: IncidentCategory
    severity: RiskLevel
    affected_processes: List[str] = Field(default_factory=list)
    estimated_impact: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NaturalLanguageQuery(BaseModel):
    """Natural language query for AI"""
    query: str = Field(..., description="Natural language query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    user_role: Optional[str] = Field(None, description="User role for context")


class AIDecision(BaseModel):
    """AI orchestrator decision"""
    id: str
    type: str
    title: str
    description: str
    recommendation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    status: str = Field(default="pending")  # pending, approved, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tenant_id: str
    data: Dict[str, Any] = Field(default_factory=dict)


class Decision(BaseModel):
    """Detailed AI decision with event context"""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    event_data: Dict[str, Any] = Field(default_factory=dict)
    rules_applied: List[str] = Field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    approved: Optional[bool] = None
    approved_by: Optional[str] = None
    tenant_id: str


class OrchestratorRule(BaseModel):
    """Rule definition for orchestrator"""
    name: str
    event_type: str
    conditions: Dict[str, Any] = Field(default_factory=dict)
    actions: List[ActionType] = Field(default_factory=list)
    priority: int = Field(default=1)
    enabled: bool = Field(default=True)


class RecommendationRequest(BaseModel):
    """Request for AI recommendation"""
    context: str = Field(..., description="Context for recommendation")
    data: Dict[str, Any] = Field(..., description="Data for analysis")
    tenant_id: str = Field(..., description="Tenant identifier")
    user_id: Optional[str] = Field(None, description="User requesting recommendation")


class RecommendationResponse(BaseModel):
    """AI recommendation response"""
    recommendation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)


class AuditSummaryRequest(BaseModel):
    """Request for audit summarization"""
    audit_id: str
    evidence: List[Dict[str, Any]]
    tenant_id: str


class AuditSummaryResponse(BaseModel):
    """Audit summary response"""
    summary: str
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    capa_items: List[Dict[str, Any]] = Field(default_factory=list)


class DecisionApprovalRequest(BaseModel):
    """Request to approve/reject AI decision"""
    decision_id: str
    approved: bool
    approved_by: str
    comments: Optional[str] = None