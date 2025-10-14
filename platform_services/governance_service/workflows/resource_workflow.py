"""
Resource Allocation Workflow
Manages BCM resources allocation (ISO 22301 Clause 7.1)
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

class ResourceAvailability(str, Enum):
    """Resource Availability States"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"

class ResourceAction(str, Enum):
    """Resource Actions"""
    CREATE = "create"
    ALLOCATE = "allocate"
    DEALLOCATE = "deallocate"
    MARK_UNAVAILABLE = "mark_unavailable"
    SCHEDULE_MAINTENANCE = "schedule_maintenance"
    COMPLETE_MAINTENANCE = "complete_maintenance"
    MARK_AVAILABLE = "mark_available"

# State Machine Transitions
TRANSITIONS = {
    (ResourceAvailability.AVAILABLE, ResourceAction.ALLOCATE): ResourceAvailability.ALLOCATED,
    (ResourceAvailability.AVAILABLE, ResourceAction.SCHEDULE_MAINTENANCE): ResourceAvailability.MAINTENANCE,
    (ResourceAvailability.AVAILABLE, ResourceAction.MARK_UNAVAILABLE): ResourceAvailability.UNAVAILABLE,

    (ResourceAvailability.ALLOCATED, ResourceAction.DEALLOCATE): ResourceAvailability.AVAILABLE,
    (ResourceAvailability.ALLOCATED, ResourceAction.MARK_UNAVAILABLE): ResourceAvailability.UNAVAILABLE,

    (ResourceAvailability.UNAVAILABLE, ResourceAction.MARK_AVAILABLE): ResourceAvailability.AVAILABLE,

    (ResourceAvailability.MAINTENANCE, ResourceAction.COMPLETE_MAINTENANCE): ResourceAvailability.AVAILABLE,
}

class ResourceWorkflowEngine:
    """Resource Allocation Workflow Engine"""

    @staticmethod
    def can_transition(from_state: str, action: str) -> bool:
        """Check if transition is allowed"""
        try:
            from_state_enum = ResourceAvailability(from_state)
            action_enum = ResourceAction(action)
            return (from_state_enum, action_enum) in TRANSITIONS
        except (ValueError, KeyError):
            return False

    @staticmethod
    def get_next_state(from_state: str, action: str) -> Optional[str]:
        """Get next state after action"""
        try:
            from_state_enum = ResourceAvailability(from_state)
            action_enum = ResourceAction(action)
            next_state = TRANSITIONS.get((from_state_enum, action_enum))
            return next_state.value if next_state else None
        except (ValueError, KeyError):
            return None

    @staticmethod
    def get_allowed_actions(state: str) -> List[str]:
        """Get allowed actions for current state"""
        try:
            state_enum = ResourceAvailability(state)
            actions = []
            for (from_st, action), _ in TRANSITIONS.items():
                if from_st == state_enum:
                    actions.append(action.value)
            return actions
        except ValueError:
            return []

    @staticmethod
    def validate_transition(resource: Dict, action: str) -> tuple[bool, Optional[str]]:
        """Validate if resource can perform action"""
        current_state = resource.get("availability", ResourceAvailability.AVAILABLE.value)

        if not ResourceWorkflowEngine.can_transition(current_state, action):
            return False, f"Action '{action}' not allowed in state '{current_state}'"

        # Validate required fields based on action
        if action == ResourceAction.ALLOCATE.value:
            if not resource.get("allocated_to"):
                return False, "Allocation target is required"
            if not resource.get("quantity") or resource.get("quantity") <= 0:
                return False, "Valid quantity is required for allocation"

        if action == ResourceAction.SCHEDULE_MAINTENANCE.value:
            if not resource.get("available_from") or not resource.get("available_until"):
                return False, "Maintenance schedule dates are required"

        return True, None

# Resource Validators
class ResourceValidator:
    """Validate resource data"""

    @staticmethod
    def validate_allocation(
        allocated_to: str,
        allocated_to_type: str,
        quantity: float,
        unit: str
    ) -> tuple[bool, Optional[str]]:
        """Validate resource allocation"""
        if not allocated_to:
            return False, "Allocation target is required"

        valid_types = ["process", "activity", "department", "team", "person"]
        if allocated_to_type not in valid_types:
            return False, f"Allocation type must be one of: {valid_types}"

        if quantity <= 0:
            return False, "Quantity must be positive"

        if not unit:
            return False, "Unit of measure is required"

        return True, None

    @staticmethod
    def validate_cost(
        cost_per_unit: Optional[float],
        total_cost: Optional[float],
        quantity: Optional[float]
    ) -> tuple[bool, Optional[str]]:
        """Validate cost calculation"""
        if cost_per_unit is not None and cost_per_unit < 0:
            return False, "Cost per unit cannot be negative"

        if total_cost is not None and total_cost < 0:
            return False, "Total cost cannot be negative"

        # Validate cost calculation if all values present
        if all(v is not None for v in [cost_per_unit, total_cost, quantity]):
            expected_total = cost_per_unit * quantity
            if abs(total_cost - expected_total) > 0.01:  # Allow small floating point errors
                return False, "Total cost does not match cost_per_unit * quantity"

        return True, None

    @staticmethod
    def validate_criticality(criticality: int, is_critical: bool) -> tuple[bool, Optional[str]]:
        """Validate criticality rating"""
        if criticality < 1 or criticality > 5:
            return False, "Criticality must be between 1 and 5"

        # If marked as critical, criticality should be 4 or 5
        if is_critical and criticality < 4:
            return False, "Critical resources should have criticality >= 4"

        return True, None

    @staticmethod
    def validate_availability_period(
        available_from: Optional[datetime],
        available_until: Optional[datetime]
    ) -> tuple[bool, Optional[str]]:
        """Validate availability period"""
        if available_from and available_until:
            if available_until <= available_from:
                return False, "Available until must be after available from"

        return True, None

    @staticmethod
    def validate_recovery_info(
        alternative_resource: Optional[str],
        recovery_time_hours: Optional[int],
        is_critical: bool
    ) -> tuple[bool, Optional[str]]:
        """Validate recovery information"""
        # Critical resources should have recovery plan
        if is_critical:
            if not alternative_resource:
                return False, "Critical resources must have alternative resource defined"
            if not recovery_time_hours or recovery_time_hours <= 0:
                return False, "Critical resources must have valid recovery time"

        if recovery_time_hours is not None and recovery_time_hours < 0:
            return False, "Recovery time cannot be negative"

        return True, None
