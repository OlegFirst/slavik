"""
Workflow Validation Utilities
Edge case handling for state transitions

Provides comprehensive validation for:
- Invalid state transitions
- Data validation before state changes
- Circular dependency detection
- Orphaned record prevention
- Date sequence validation
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class WorkflowValidationError(Exception):
    """Raised when workflow validation fails"""
    pass


class WorkflowValidator:
    """Common workflow validation logic"""

    @staticmethod
    def validate_date_sequence(
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        field_names: tuple = ("start_date", "end_date")
    ):
        """
        Validate start date is before end date

        Args:
            start_date: The start datetime
            end_date: The end datetime
            field_names: Tuple of field names for error message

        Raises:
            WorkflowValidationError: If start_date >= end_date
        """
        if start_date and end_date and start_date >= end_date:
            raise WorkflowValidationError(
                f"{field_names[0]} must be before {field_names[1]}. "
                f"Got: {start_date} >= {end_date}"
            )

    @staticmethod
    def validate_future_date(date: Optional[datetime], field_name: str):
        """
        Validate date is not in the future

        Args:
            date: The datetime to check
            field_name: Name of the field for error message

        Raises:
            WorkflowValidationError: If date is in the future
        """
        if date and date > datetime.utcnow():
            raise WorkflowValidationError(
                f"{field_name} cannot be in the future. Got: {date}"
            )

    @staticmethod
    def validate_past_date(date: Optional[datetime], field_name: str):
        """
        Validate date is not in the past

        Args:
            date: The datetime to check
            field_name: Name of the field for error message

        Raises:
            WorkflowValidationError: If date is in the past
        """
        if date and date < datetime.utcnow():
            raise WorkflowValidationError(
                f"{field_name} must be in the future. Got: {date}"
            )

    @staticmethod
    def validate_required_field(
        value: Any,
        field_name: str,
        for_transition: str = None
    ):
        """
        Validate required field is populated

        Args:
            value: The value to check
            field_name: Name of the field
            for_transition: Optional transition name for context

        Raises:
            WorkflowValidationError: If field is missing or empty
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            msg = f"Required field '{field_name}' is missing"
            if for_transition:
                msg += f" for transition '{for_transition}'"
            raise WorkflowValidationError(msg)

    @staticmethod
    def validate_required_list(
        value: Optional[List],
        field_name: str,
        for_transition: str = None,
        min_items: int = 1
    ):
        """
        Validate required list field has items

        Args:
            value: The list to check
            field_name: Name of the field
            for_transition: Optional transition name for context
            min_items: Minimum number of items required

        Raises:
            WorkflowValidationError: If list is missing or has too few items
        """
        if not value or not isinstance(value, list) or len(value) < min_items:
            msg = f"Required field '{field_name}' must have at least {min_items} item(s)"
            if for_transition:
                msg += f" for transition '{for_transition}'"
            raise WorkflowValidationError(msg)

    @staticmethod
    def validate_terminal_state(current_state: str, terminal_states: List[str]):
        """
        Prevent transitions from terminal states

        Args:
            current_state: Current state value
            terminal_states: List of terminal state values

        Raises:
            WorkflowValidationError: If trying to transition from terminal state
        """
        if current_state in terminal_states:
            raise WorkflowValidationError(
                f"Cannot transition from terminal state '{current_state}'"
            )

    @staticmethod
    def validate_allowed_transition(
        from_state: str,
        to_state: str,
        allowed_transitions: Dict[str, List[str]]
    ):
        """
        Validate transition is allowed

        Args:
            from_state: Current state
            to_state: Target state
            allowed_transitions: Dict mapping from_state -> [allowed_to_states]

        Raises:
            WorkflowValidationError: If transition not allowed
        """
        allowed = allowed_transitions.get(from_state, [])
        if to_state not in allowed:
            raise WorkflowValidationError(
                f"Transition from '{from_state}' to '{to_state}' not allowed. "
                f"Allowed transitions: {allowed}"
            )

    @staticmethod
    async def validate_parent_exists(
        repository: Any,
        parent_id: Optional[UUID],
        parent_type: str
    ):
        """
        Validate parent entity exists

        Args:
            repository: Repository instance with get_by_id method
            parent_id: ID of parent entity
            parent_type: Type name for error message

        Raises:
            WorkflowValidationError: If parent not found
        """
        if parent_id:
            parent = await repository.get_by_id(parent_id)
            if not parent:
                raise WorkflowValidationError(
                    f"{parent_type} with ID {parent_id} not found"
                )

    @staticmethod
    def validate_no_circular_reference(
        entity_id: UUID,
        related_ids: List[UUID],
        relationship: str
    ):
        """
        Prevent circular references

        Args:
            entity_id: Current entity ID
            related_ids: List of related entity IDs
            relationship: Description of relationship for error message

        Raises:
            WorkflowValidationError: If circular reference detected
        """
        if entity_id in related_ids:
            raise WorkflowValidationError(
                f"Circular reference detected: {relationship} cannot reference itself"
            )

    @staticmethod
    def validate_list_items_have_fields(
        items: List[Dict[str, Any]],
        required_fields: List[str],
        item_type: str
    ):
        """
        Validate all items in list have required fields

        Args:
            items: List of dictionaries to validate
            required_fields: List of required field names
            item_type: Type name for error message

        Raises:
            WorkflowValidationError: If any item missing required fields
        """
        for idx, item in enumerate(items):
            for field in required_fields:
                if field not in item or not item[field]:
                    raise WorkflowValidationError(
                        f"{item_type} at index {idx} missing required field '{field}'"
                    )

    @staticmethod
    def validate_enum_value(
        value: str,
        allowed_values: List[str],
        field_name: str
    ):
        """
        Validate value is in allowed enum values

        Args:
            value: Value to check
            allowed_values: List of allowed values
            field_name: Name of the field for error message

        Raises:
            WorkflowValidationError: If value not in allowed values
        """
        if value not in allowed_values:
            raise WorkflowValidationError(
                f"Invalid value '{value}' for {field_name}. "
                f"Allowed values: {allowed_values}"
            )

    @staticmethod
    def validate_not_same_user(
        user_id_1: str,
        user_id_2: str,
        role_1: str,
        role_2: str
    ):
        """
        Validate two roles are not performed by same user (independence check)

        Args:
            user_id_1: First user ID
            user_id_2: Second user ID
            role_1: First role name
            role_2: Second role name

        Raises:
            WorkflowValidationError: If same user performing conflicting roles
        """
        if user_id_1 == user_id_2:
            raise WorkflowValidationError(
                f"User cannot be both {role_1} and {role_2} (independence violation)"
            )
