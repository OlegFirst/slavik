"""
Role Assignment Workflow
Manages organizational roles and responsibilities (ISO 22301 Clause 5.3)
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

class RoleState(str, Enum):
    """Role Assignment States"""
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

class RoleAction(str, Enum):
    """Role Actions"""
    CREATE = "create"
    ASSIGN = "assign"
    REASSIGN = "reassign"
    DEACTIVATE = "deactivate"
    REACTIVATE = "reactivate"

# State Machine Transitions
TRANSITIONS = {
    (RoleState.PENDING, RoleAction.ASSIGN): RoleState.ACTIVE,
    (RoleState.ACTIVE, RoleAction.REASSIGN): RoleState.ACTIVE,
    (RoleState.ACTIVE, RoleAction.DEACTIVATE): RoleState.INACTIVE,
    (RoleState.INACTIVE, RoleAction.REACTIVATE): RoleState.ACTIVE,
    (RoleState.INACTIVE, RoleAction.REASSIGN): RoleState.ACTIVE,
}

class RoleWorkflowEngine:
    """Role Assignment Workflow Engine"""

    @staticmethod
    def can_transition(from_state: str, action: str) -> bool:
        """Check if transition is allowed"""
        try:
            from_state_enum = RoleState(from_state)
            action_enum = RoleAction(action)
            return (from_state_enum, action_enum) in TRANSITIONS
        except (ValueError, KeyError):
            return False

    @staticmethod
    def get_next_state(from_state: str, action: str) -> Optional[str]:
        """Get next state after action"""
        try:
            from_state_enum = RoleState(from_state)
            action_enum = RoleAction(action)
            next_state = TRANSITIONS.get((from_state_enum, action_enum))
            return next_state.value if next_state else None
        except (ValueError, KeyError):
            return None

    @staticmethod
    def get_allowed_actions(state: str) -> List[str]:
        """Get allowed actions for current state"""
        try:
            state_enum = RoleState(state)
            actions = []
            for (from_st, action), _ in TRANSITIONS.items():
                if from_st == state_enum:
                    actions.append(action.value)
            return actions
        except ValueError:
            return []

    @staticmethod
    def validate_transition(role: Dict, action: str) -> tuple[bool, Optional[str]]:
        """Validate if role can perform action"""
        current_state = role.get("status", RoleState.PENDING.value)

        if not RoleWorkflowEngine.can_transition(current_state, action):
            return False, f"Action '{action}' not allowed in state '{current_state}'"

        # Validate required fields based on action
        if action == RoleAction.ASSIGN.value or action == RoleAction.REASSIGN.value:
            if not role.get("assigned_to"):
                return False, "Person assignment is required"

        return True, None

# Role Validators
class RoleValidator:
    """Validate role data"""

    @staticmethod
    def validate_responsibilities(responsibilities: List[Dict]) -> tuple[bool, Optional[str]]:
        """Validate responsibilities structure"""
        if not responsibilities:
            return False, "At least one responsibility is required"

        required_fields = {"description", "priority"}
        for resp in responsibilities:
            missing = required_fields - set(resp.keys())
            if missing:
                return False, f"Responsibility missing fields: {missing}"

            if resp.get("priority") not in ["high", "medium", "low"]:
                return False, "Priority must be: high, medium, or low"

        return True, None

    @staticmethod
    def validate_authorities(authorities: List[Dict]) -> tuple[bool, Optional[str]]:
        """Validate authorities structure"""
        if not authorities:
            return True, None  # Authorities are optional

        required_fields = {"authority", "scope"}
        for auth in authorities:
            missing = required_fields - set(auth.keys())
            if missing:
                return False, f"Authority missing fields: {missing}"

        return True, None

    @staticmethod
    def validate_competence_requirements(requirements: List[Dict]) -> tuple[bool, Optional[str]]:
        """Validate competence requirements"""
        if not requirements:
            return True, None  # Optional

        required_fields = {"competence", "level", "mandatory"}
        valid_levels = ["basic", "intermediate", "advanced", "expert"]

        for req in requirements:
            missing = required_fields - set(req.keys())
            if missing:
                return False, f"Competence requirement missing fields: {missing}"

            if req.get("level") not in valid_levels:
                return False, f"Competence level must be one of: {valid_levels}"

            if not isinstance(req.get("mandatory"), bool):
                return False, "Mandatory field must be boolean"

        return True, None

    @staticmethod
    def validate_assignment(
        assigned_to: str,
        assigned_to_name: str,
        backup_person: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """Validate role assignment"""
        if not assigned_to:
            return False, "Person assignment is required"

        if not assigned_to_name:
            return False, "Person name is required"

        if backup_person and backup_person == assigned_to:
            return False, "Backup person cannot be the same as primary assignee"

        return True, None
