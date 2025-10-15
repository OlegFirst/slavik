"""
Decision Models
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class DecisionType(Enum):
    """Типы решений"""
    AUTO_APPROVED = "auto_approved"          # Автоматически одобрено по политикам
    REQUIRES_APPROVAL = "requires_approval"   # Требует human approval
    ESCALATED = "escalated"                  # Эскалировано к оператору
    AI_CONSULTED = "ai_consulted"            # Консультация с AI
    REJECTED = "rejected"                    # Отклонено по политикам


class DecisionOutcome(Enum):
    """Результаты решений"""
    APPROVED = "approved"      # Одобрено (выполнить действие)
    REJECTED = "rejected"      # Отклонено (не выполнять)
    PENDING = "pending"        # Ожидает approval
    ESCALATED = "escalated"    # Эскалировано выше


@dataclass
class DecisionRequest:
    """
    Запрос на принятие решения

    Attributes:
        request_id: Unique request ID
        service: Service name (e.g., "database", "redis")
        action: Action to perform (e.g., "restart", "scale_up")
        reason: Why this action is needed
        priority: Priority 1-5 (1 = critical)
        context: System state, metrics, history
        requester: Who requested (e.g., "infrastructure_coordinator")
        timestamp: When requested
    """
    request_id: str
    service: str
    action: str
    reason: str
    priority: int
    context: Dict[str, Any]
    requester: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        service: str,
        action: str,
        reason: str,
        priority: int = 3,
        context: Optional[Dict[str, Any]] = None,
        requester: str = "system"
    ) -> "DecisionRequest":
        """
        Factory method to create DecisionRequest

        Args:
            service: Service name
            action: Action to perform
            reason: Reason for action
            priority: Priority 1-5 (default 3)
            context: Additional context
            requester: Requester name

        Returns:
            DecisionRequest instance
        """
        return cls(
            request_id=str(uuid.uuid4()),
            service=service,
            action=action,
            reason=reason,
            priority=priority,
            context=context or {},
            requester=requester,
            timestamp=datetime.utcnow()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "service": self.service,
            "action": self.action,
            "reason": self.reason,
            "priority": self.priority,
            "context": self.context,
            "requester": self.requester,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Decision:
    """
    Принятое решение

    Attributes:
        decision_id: Unique decision ID
        request_id: Original request ID
        decision_type: Type of decision
        outcome: Decision outcome
        action: Action to perform (or not)
        justification: Why this decision was made
        decided_by: Who/what made decision (system/human/ai)
        decided_at: When decision was made
        expires_at: When decision expires (TTL)
        metadata: Additional metadata
    """
    decision_id: str
    request_id: str
    decision_type: DecisionType
    outcome: DecisionOutcome
    action: str
    justification: str
    decided_by: str
    decided_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        request: DecisionRequest,
        decision_type: DecisionType,
        outcome: DecisionOutcome,
        justification: str,
        decided_by: str = "system",
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "Decision":
        """
        Factory method to create Decision

        Args:
            request: Original request
            decision_type: Type of decision
            outcome: Decision outcome
            justification: Justification text
            decided_by: Who decided
            expires_at: Expiration time
            metadata: Additional metadata

        Returns:
            Decision instance
        """
        return cls(
            decision_id=str(uuid.uuid4()),
            request_id=request.request_id,
            decision_type=decision_type,
            outcome=outcome,
            action=request.action,
            justification=justification,
            decided_by=decided_by,
            decided_at=datetime.utcnow(),
            expires_at=expires_at,
            metadata=metadata or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "decision_type": self.decision_type.value,
            "outcome": self.outcome.value,
            "action": self.action,
            "justification": self.justification,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata
        }

    def is_expired(self) -> bool:
        """Check if decision expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_approved(self) -> bool:
        """Check if decision approved"""
        return self.outcome == DecisionOutcome.APPROVED

    def is_rejected(self) -> bool:
        """Check if decision rejected"""
        return self.outcome == DecisionOutcome.REJECTED

    def is_pending(self) -> bool:
        """Check if decision pending"""
        return self.outcome == DecisionOutcome.PENDING

    def is_escalated(self) -> bool:
        """Check if decision escalated"""
        return self.outcome == DecisionOutcome.ESCALATED
