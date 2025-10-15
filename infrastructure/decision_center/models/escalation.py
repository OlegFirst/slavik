"""
Escalation Models
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid

from .decision import DecisionRequest


class EscalationLevel(Enum):
    """Уровни эскалации"""
    L1_OPERATOR = "l1_operator"          # Дежурный оператор
    L2_ENGINEER = "l2_engineer"          # Инженер
    L3_ARCHITECT = "l3_architect"        # Архитектор / Tech Lead
    L4_MANAGEMENT = "l4_management"      # Менеджмент


@dataclass
class EscalationRequest:
    """
    Запрос на эскалацию

    Attributes:
        escalation_id: Unique escalation ID
        original_request: Original decision request
        escalation_level: Level of escalation
        reason: Why escalated
        urgency: Urgency 1-5 (1 = most urgent)
        assigned_to: Who is assigned (name/email)
        created_at: When created
        responded_at: When responded
        resolution: Resolution text
    """
    escalation_id: str
    original_request: DecisionRequest
    escalation_level: EscalationLevel
    reason: str
    urgency: int
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    resolution: Optional[str] = None

    @classmethod
    def create(
        cls,
        original_request: DecisionRequest,
        escalation_level: EscalationLevel,
        reason: str,
        urgency: int = 3,
        assigned_to: Optional[str] = None
    ) -> "EscalationRequest":
        """
        Factory method to create EscalationRequest

        Args:
            original_request: Original decision request
            escalation_level: Level of escalation
            reason: Why escalated
            urgency: Urgency 1-5 (default 3)
            assigned_to: Assigned person

        Returns:
            EscalationRequest instance
        """
        return cls(
            escalation_id=str(uuid.uuid4()),
            original_request=original_request,
            escalation_level=escalation_level,
            reason=reason,
            urgency=urgency,
            assigned_to=assigned_to,
            created_at=datetime.utcnow()
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "escalation_id": self.escalation_id,
            "original_request": self.original_request.to_dict(),
            "escalation_level": self.escalation_level.value,
            "reason": self.reason,
            "urgency": self.urgency,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat(),
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "resolution": self.resolution
        }

    def is_resolved(self) -> bool:
        """Check if escalation is resolved"""
        return self.responded_at is not None

    def response_time_seconds(self) -> Optional[int]:
        """Calculate response time in seconds"""
        if not self.responded_at:
            return None
        delta = self.responded_at - self.created_at
        return int(delta.total_seconds())
