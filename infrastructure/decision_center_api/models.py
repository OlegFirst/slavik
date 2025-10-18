"""
API Models for Decision Center REST API
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class DecisionRequest(BaseModel):
    """Request for decision"""
    service: str = Field(..., description="Service name")
    action: str = Field(..., description="Action type (restart, failover, scale_up, etc.)")
    reason: str = Field(..., description="Reason for the action")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    priority: str = Field(default="medium", description="Priority level (low, medium, high, critical)")
    current_attempt: int = Field(default=1, description="Current recovery attempt number")


class DecisionResponse(BaseModel):
    """Response with decision"""
    decision_id: str
    outcome: str  # approved, rejected, pending
    can_proceed: bool
    reasoning: str
    confidence_score: float
    policy_reference: Optional[str] = None
    requires_approval: bool = False
    ai_enhanced: bool = False
    ai_confidence: Optional[float] = None
    ai_model: Optional[str] = None
    decided_at: datetime


class EscalationRequest(BaseModel):
    """Request to create escalation"""
    service: str = Field(..., description="Service name")
    reason: str = Field(..., description="Reason for escalation")
    severity: str = Field(default="medium", description="Severity level (low, medium, high, critical)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    decision_id: Optional[str] = None


class EscalationResponse(BaseModel):
    """Response with escalation details"""
    escalation_id: str
    service: str
    severity: str
    reason: str
    status: str
    assigned_team: str
    created_at: datetime


class ApprovalRequest(BaseModel):
    """Request to approve/reject decision"""
    approval_id: str = Field(..., description="Approval request ID")
    approved_by: str = Field(..., description="User who is approving")
    approved: bool = Field(..., description="True to approve, False to reject")
    comment: Optional[str] = Field(None, description="Optional comment")


class ApprovalResponse(BaseModel):
    """Response from approval"""
    approval_id: str
    status: str  # approved, rejected, pending
    can_proceed: bool
    decision_by: str
    decided_at: datetime


class StatsResponse(BaseModel):
    """Decision Center statistics"""
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    escalated_decisions: int
    auto_approved: int
    manual_approved: int
    ai_consultations: int = 0
    ai_enhanced_decisions: int = 0
    pending_approvals: int
    active_escalations: int
    approval_rate: float
    automation_rate: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    decision_center: str
    ai_hub_available: bool
    metrics_enabled: bool
    eventbus_connected: bool
