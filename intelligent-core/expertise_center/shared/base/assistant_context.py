"""Assistant Context for Tactical Assistants"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AssistantContext:
    """
    Context for AI Assistant operations

    Provides:
    - Organization context
    - User context
    - Task context
    - Historical context
    """

    value: Dict[str, Any]
    organization_id: str = "default"
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context"""
        return self.value.get(key, default)

    def set(self, key: str, value: Any):
        """Set value in context"""
        self.value[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "value": self.value,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "session_id": self.session_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssistantContext":
        """Create from dictionary"""
        return cls(
            value=data.get("value", {}),
            organization_id=data.get("organization_id", "default"),
            user_id=data.get("user_id"),
            session_id=data.get("session_id")
        )
