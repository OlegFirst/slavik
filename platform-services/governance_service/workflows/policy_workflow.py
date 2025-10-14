"""
Policy Workflow State Machine
Manages BCM Policy lifecycle and approval workflow (ISO 22301 Clause 5.2)
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

class PolicyState(str, Enum):
    """Policy Lifecycle States"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    ARCHIVED = "archived"

class PolicyAction(str, Enum):
    """Policy Actions"""
    CREATE = "create"
    SUBMIT_FOR_REVIEW = "submit_for_review"
    APPROVE = "approve"
    REJECT = "reject"
    ACTIVATE = "activate"
    ARCHIVE = "archive"
    REOPEN = "reopen"
    REQUEST_CHANGES = "request_changes"

# State Machine Transitions
# Format: (from_state, action) -> to_state
TRANSITIONS = {
    # Draft phase
    (PolicyState.DRAFT, PolicyAction.SUBMIT_FOR_REVIEW): PolicyState.UNDER_REVIEW,

    # Review phase
    (PolicyState.UNDER_REVIEW, PolicyAction.APPROVE): PolicyState.APPROVED,
    (PolicyState.UNDER_REVIEW, PolicyAction.REJECT): PolicyState.DRAFT,
    (PolicyState.UNDER_REVIEW, PolicyAction.REQUEST_CHANGES): PolicyState.DRAFT,

    # Approved phase
    (PolicyState.APPROVED, PolicyAction.ACTIVATE): PolicyState.ACTIVE,
    (PolicyState.APPROVED, PolicyAction.REJECT): PolicyState.DRAFT,

    # Active phase
    (PolicyState.ACTIVE, PolicyAction.ARCHIVE): PolicyState.ARCHIVED,
    (PolicyState.ACTIVE, PolicyAction.REQUEST_CHANGES): PolicyState.DRAFT,

    # Archived phase
    (PolicyState.ARCHIVED, PolicyAction.REOPEN): PolicyState.DRAFT,
}

class PolicyWorkflowEngine:
    """Policy Workflow State Machine"""

    @staticmethod
    def can_transition(from_state: str, action: str) -> bool:
        """Check if transition is allowed"""
        try:
            from_state_enum = PolicyState(from_state)
            action_enum = PolicyAction(action)
            return (from_state_enum, action_enum) in TRANSITIONS
        except (ValueError, KeyError):
            return False

    @staticmethod
    def get_next_state(from_state: str, action: str) -> Optional[str]:
        """Get next state after action"""
        try:
            from_state_enum = PolicyState(from_state)
            action_enum = PolicyAction(action)
            next_state = TRANSITIONS.get((from_state_enum, action_enum))
            return next_state.value if next_state else None
        except (ValueError, KeyError):
            return None

    @staticmethod
    def get_allowed_actions(state: str) -> List[str]:
        """Get list of allowed actions for current state"""
        try:
            state_enum = PolicyState(state)
            actions = []
            for (from_st, action), _ in TRANSITIONS.items():
                if from_st == state_enum:
                    actions.append(action.value)
            return actions
        except ValueError:
            return []

    @staticmethod
    def get_completion_percentage(state: str) -> float:
        """Get policy lifecycle completion percentage"""
        progress = {
            PolicyState.DRAFT: 0.2,
            PolicyState.UNDER_REVIEW: 0.5,
            PolicyState.APPROVED: 0.8,
            PolicyState.ACTIVE: 1.0,
            PolicyState.ARCHIVED: 1.0
        }
        try:
            return progress.get(PolicyState(state), 0.0)
        except ValueError:
            return 0.0

    @staticmethod
    def get_required_fields(state: str) -> List[str]:
        """Get required fields for state"""
        required_fields = {
            PolicyState.DRAFT: ["title", "policy_type", "content", "policy_owner"],
            PolicyState.UNDER_REVIEW: ["title", "policy_type", "content", "policy_owner", "version"],
            PolicyState.APPROVED: ["approved_by", "approved_at"],
            PolicyState.ACTIVE: ["approved_by", "approved_at", "effective_date"],
        }
        try:
            return required_fields.get(PolicyState(state), [])
        except ValueError:
            return []

    @staticmethod
    def validate_transition(policy: Dict, action: str) -> tuple[bool, Optional[str]]:
        """Validate if policy can perform action"""
        current_state = policy.get("workflow_state", PolicyState.DRAFT.value)

        # Check if transition is allowed
        if not PolicyWorkflowEngine.can_transition(current_state, action):
            return False, f"Action '{action}' not allowed in state '{current_state}'"

        # Check required fields for next state
        next_state = PolicyWorkflowEngine.get_next_state(current_state, action)
        if next_state:
            required_fields = PolicyWorkflowEngine.get_required_fields(next_state)
            missing_fields = [f for f in required_fields if not policy.get(f)]
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}"

        return True, None

    @staticmethod
    def create_workflow_log_entry(
        policy_id: int,
        from_state: str,
        to_state: str,
        action: str,
        user_id: Optional[str] = None,
        comments: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create workflow log entry"""
        return {
            "policy_id": policy_id,
            "from_state": from_state,
            "to_state": to_state,
            "action": action,
            "user_id": user_id,
            "comments": comments,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def calculate_review_deadline(start_date: datetime, policy_type: str) -> datetime:
        """Calculate review deadline based on policy type"""
        from datetime import timedelta

        # Different policies have different review cycles
        review_periods = {
            "bcms_policy": 365,  # 1 year
            "bc_policy": 365,
            "it_dr_policy": 180,  # 6 months
            "security_policy": 180,
            "hr_policy": 365,
            "other": 365
        }

        days = review_periods.get(policy_type, 365)
        return start_date + timedelta(days=days)

# Policy Validators
class PolicyValidator:
    """Validate policy data"""

    @staticmethod
    def validate_policy_content(content: str) -> tuple[bool, Optional[str]]:
        """Validate policy content is not empty and meets minimum length"""
        if not content or len(content.strip()) < 50:
            return False, "Policy content must be at least 50 characters"
        return True, None

    @staticmethod
    def validate_version(version: str) -> tuple[bool, Optional[str]]:
        """Validate version format (e.g., 1.0, 2.1)"""
        import re
        pattern = r'^\d+\.\d+$'
        if not re.match(pattern, version):
            return False, "Version must be in format X.Y (e.g., 1.0)"
        return True, None

    @staticmethod
    def validate_scope(scope: Dict) -> tuple[bool, Optional[str]]:
        """Validate policy scope"""
        if not scope:
            return False, "Policy scope is required"

        required_keys = {"applicable_departments", "applicable_locations"}
        if not all(key in scope for key in required_keys):
            return False, f"Scope must include: {required_keys}"

        return True, None

    @staticmethod
    def validate_approval(approved_by: str, approved_at: datetime) -> tuple[bool, Optional[str]]:
        """Validate approval information"""
        if not approved_by:
            return False, "Approver is required"

        if not approved_at:
            return False, "Approval date is required"

        if approved_at > datetime.utcnow():
            return False, "Approval date cannot be in the future"

        return True, None

    @staticmethod
    def validate_review_schedule(
        review_frequency_months: int,
        last_review_date: Optional[datetime],
        next_review_date: Optional[datetime]
    ) -> tuple[bool, Optional[str]]:
        """Validate review schedule"""
        if review_frequency_months < 1 or review_frequency_months > 60:
            return False, "Review frequency must be between 1 and 60 months"

        if last_review_date and next_review_date:
            if next_review_date <= last_review_date:
                return False, "Next review date must be after last review date"

        return True, None
