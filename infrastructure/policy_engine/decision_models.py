"""
Decision Center Models (Phase 1.1)
===================================

Data models for decision management, policy compliance, and audit logging.

Models:
- Decision: Core decision record with reasoning
- PolicyRule: Policy configuration
- EscalationRequest: Escalation to human operators
- ApprovalRequest: Manual approval workflow
- DecisionAuditLog: Full audit trail for ISO 22301
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import uuid4


class DecisionType(Enum):
    """Type of decision being made"""
    RECOVERY = "recovery"
    OPTIMIZATION = "optimization"
    SCALING = "scaling"
    EMERGENCY = "emergency"


class DecisionOutcome(Enum):
    """Outcome of a decision"""
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    PENDING = "pending"


class EscalationStatus(Enum):
    """Status of an escalation request"""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class ApprovalStatus(Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class Decision:
    """
    Core decision record

    Captures all information about a decision made by the system,
    including reasoning, policy reference, and outcome.
    """
    decision_id: str = field(default_factory=lambda: str(uuid4()))
    decision_type: DecisionType = DecisionType.RECOVERY
    service_name: str = ""
    outcome: DecisionOutcome = DecisionOutcome.PENDING

    # Decision context
    trigger_event_id: Optional[str] = None
    trigger_data: Dict[str, Any] = field(default_factory=dict)

    # Decision reasoning
    reasoning: str = ""
    policy_reference: Optional[str] = None
    confidence_score: float = 1.0  # 0.0 to 1.0

    # Decision parameters
    action_type: Optional[str] = None  # restart, scale_up, optimize, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None

    # Human involvement
    requires_approval: bool = False
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None

    # Results
    success: Optional[bool] = None
    result_message: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    tenant_id: str = "system"
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'decision_id': self.decision_id,
            'decision_type': self.decision_type.value,
            'service_name': self.service_name,
            'outcome': self.outcome.value,
            'trigger_event_id': self.trigger_event_id,
            'trigger_data': self.trigger_data,
            'reasoning': self.reasoning,
            'policy_reference': self.policy_reference,
            'confidence_score': self.confidence_score,
            'action_type': self.action_type,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat(),
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'requires_approval': self.requires_approval,
            'approved_by': self.approved_by,
            'approval_timestamp': self.approval_timestamp.isoformat() if self.approval_timestamp else None,
            'success': self.success,
            'result_message': self.result_message,
            'result_data': self.result_data,
            'tenant_id': self.tenant_id,
            'correlation_id': self.correlation_id,
            'metadata': self.metadata
        }


@dataclass
class PolicyRule:
    """
    Policy rule configuration

    Defines constraints and requirements for automated decisions.
    """
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    rule_name: str = ""
    service_name: str = ""
    rule_type: str = ""  # recovery, optimization, scaling

    # Constraints
    max_auto_attempts: int = 3
    require_approval: bool = False
    escalate_immediately: bool = False

    # Timing constraints
    rto_seconds: Optional[int] = None  # Recovery Time Objective
    rpo_seconds: Optional[int] = None  # Recovery Point Objective
    escalation_timeout_seconds: int = 300  # 5 minutes default

    # Notification
    notify_channels: List[str] = field(default_factory=list)
    notify_teams: List[str] = field(default_factory=list)

    # Priority
    priority: int = 5  # 1 (highest) to 10 (lowest)
    critical_service: bool = False

    # Business context
    business_hours_only: bool = False
    requires_change_approval: bool = False

    # Metadata
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EscalationRequest:
    """
    Escalation request to human operators

    Tracks escalations when automated decisions cannot proceed.
    """
    escalation_id: str = field(default_factory=lambda: str(uuid4()))
    decision_id: str = ""
    service_name: str = ""
    escalation_type: str = ""  # policy_exceeded, manual_required, emergency

    # Context
    reason: str = ""
    severity: str = "medium"  # low, medium, high, critical
    context_data: Dict[str, Any] = field(default_factory=dict)

    # Assignment
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None

    # Status
    status: EscalationStatus = EscalationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Resolution
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    action_taken: Optional[str] = None

    # Notifications
    notifications_sent: List[str] = field(default_factory=list)

    # Metadata
    tenant_id: str = "system"
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'escalation_id': self.escalation_id,
            'decision_id': self.decision_id,
            'service_name': self.service_name,
            'escalation_type': self.escalation_type,
            'reason': self.reason,
            'severity': self.severity,
            'context_data': self.context_data,
            'assigned_to': self.assigned_to,
            'assigned_team': self.assigned_team,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution': self.resolution,
            'resolved_by': self.resolved_by,
            'action_taken': self.action_taken,
            'notifications_sent': self.notifications_sent,
            'tenant_id': self.tenant_id,
            'correlation_id': self.correlation_id,
            'metadata': self.metadata
        }


@dataclass
class ApprovalRequest:
    """
    Manual approval request workflow

    Manages approval workflow for sensitive actions.
    """
    approval_id: str = field(default_factory=lambda: str(uuid4()))
    decision_id: str = ""
    service_name: str = ""
    action_type: str = ""

    # Request details
    requested_action: str = ""
    justification: str = ""
    impact_assessment: str = ""
    rollback_plan: str = ""

    # Approval workflow
    required_approvers: List[str] = field(default_factory=list)
    approvers: List[Dict[str, Any]] = field(default_factory=list)  # [{user, timestamp, decision, comment}]

    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None

    # Decision
    final_decision: Optional[str] = None
    decision_by: Optional[str] = None
    decision_comment: Optional[str] = None

    # Metadata
    tenant_id: str = "system"
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_approver_decision(self, user: str, approved: bool, comment: Optional[str] = None):
        """Add an approver's decision"""
        self.approvers.append({
            'user': user,
            'timestamp': datetime.utcnow().isoformat(),
            'approved': approved,
            'comment': comment
        })

    def is_approved(self) -> bool:
        """Check if request has sufficient approvals"""
        if not self.required_approvers:
            return len(self.approvers) > 0 and all(a['approved'] for a in self.approvers)

        # Check if all required approvers have approved
        approved_users = {a['user'] for a in self.approvers if a['approved']}
        return all(req in approved_users for req in self.required_approvers)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'approval_id': self.approval_id,
            'decision_id': self.decision_id,
            'service_name': self.service_name,
            'action_type': self.action_type,
            'requested_action': self.requested_action,
            'justification': self.justification,
            'impact_assessment': self.impact_assessment,
            'rollback_plan': self.rollback_plan,
            'required_approvers': self.required_approvers,
            'approvers': self.approvers,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'final_decision': self.final_decision,
            'decision_by': self.decision_by,
            'decision_comment': self.decision_comment,
            'tenant_id': self.tenant_id,
            'correlation_id': self.correlation_id,
            'metadata': self.metadata
        }


@dataclass
class DecisionAuditLog:
    """
    Audit log entry for ISO 22301 compliance

    Comprehensive audit trail for all decisions and actions.
    """
    log_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Decision reference
    decision_id: str = ""
    decision_type: str = ""
    service_name: str = ""

    # Action
    action: str = ""  # decision_made, approval_requested, escalation_created, action_executed
    action_details: str = ""

    # Context
    trigger_event: Optional[str] = None
    policy_applied: Optional[str] = None

    # Decision reasoning
    reasoning: str = ""
    confidence_score: float = 1.0

    # Actors
    automated: bool = True
    actor: Optional[str] = None  # system or user ID

    # Outcome
    outcome: str = ""
    success: Optional[bool] = None

    # Compliance metadata
    compliance_standard: str = "ISO 22301:2019"
    compliance_clause: Optional[str] = None

    # Data
    before_state: Dict[str, Any] = field(default_factory=dict)
    after_state: Dict[str, Any] = field(default_factory=dict)
    event_data: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    tenant_id: str = "system"
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'log_id': self.log_id,
            'timestamp': self.timestamp.isoformat(),
            'decision_id': self.decision_id,
            'decision_type': self.decision_type,
            'service_name': self.service_name,
            'action': self.action,
            'action_details': self.action_details,
            'trigger_event': self.trigger_event,
            'policy_applied': self.policy_applied,
            'reasoning': self.reasoning,
            'confidence_score': self.confidence_score,
            'automated': self.automated,
            'actor': self.actor,
            'outcome': self.outcome,
            'success': self.success,
            'compliance_standard': self.compliance_standard,
            'compliance_clause': self.compliance_clause,
            'before_state': self.before_state,
            'after_state': self.after_state,
            'event_data': self.event_data,
            'tenant_id': self.tenant_id,
            'correlation_id': self.correlation_id,
            'metadata': self.metadata
        }
