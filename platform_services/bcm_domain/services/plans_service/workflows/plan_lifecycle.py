"""
Plan Lifecycle Workflow
ISO 22301 Clause 8.4 - Plan approval and activation workflow
"""

from enum import Enum
from typing import Tuple, Dict, Any, Optional
from datetime import datetime

from ..models.domain import PlanStatus


class PlanWorkflowAction(str, Enum):
    """Plan workflow actions"""
    SUBMIT_FOR_REVIEW = "submit_for_review"
    APPROVE = "approve"
    REJECT = "reject"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    ARCHIVE = "archive"


def execute_plan_transition(
    plan: Any,
    action: PlanWorkflowAction,
    user_id: str,
    **kwargs
) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Execute plan workflow transition

    Returns:
        Tuple[success, error_message, update_dict]
    """
    current_status = plan.status

    # Define valid transitions
    transitions = {
        PlanStatus.DRAFT: {
            PlanWorkflowAction.SUBMIT_FOR_REVIEW: PlanStatus.UNDER_REVIEW
        },
        PlanStatus.UNDER_REVIEW: {
            PlanWorkflowAction.APPROVE: PlanStatus.APPROVED,
            PlanWorkflowAction.REJECT: PlanStatus.DRAFT
        },
        PlanStatus.APPROVED: {
            PlanWorkflowAction.ACTIVATE: PlanStatus.ACTIVE,
            PlanWorkflowAction.ARCHIVE: PlanStatus.ARCHIVED
        },
        PlanStatus.ACTIVE: {
            PlanWorkflowAction.DEACTIVATE: PlanStatus.APPROVED,
            PlanWorkflowAction.ARCHIVE: PlanStatus.ARCHIVED
        }
    }

    # Check if transition is valid
    if current_status not in transitions:
        return False, f"No transitions available from {current_status}", {}

    if action not in transitions[current_status]:
        return False, f"Cannot {action} from {current_status} status", {}

    # Execute transition
    new_status = transitions[current_status][action]
    update_dict = {
        "status": new_status,
        "updated_by": user_id,
        "updated_at": datetime.utcnow()
    }

    # Action-specific updates
    if action == PlanWorkflowAction.SUBMIT_FOR_REVIEW:
        # Validate plan has minimum required content
        if not plan.objective or not plan.scope:
            return False, "Plan must have objective and scope before review", {}

        if not plan.procedures or len(plan.procedures) == 0:
            return False, "Plan must have at least one procedure", {}

        update_dict["submitted_for_review_at"] = datetime.utcnow()

    elif action == PlanWorkflowAction.APPROVE:
        update_dict["approved_by_user_id"] = user_id
        update_dict["approval_date"] = datetime.utcnow()
        update_dict["approval_notes"] = kwargs.get("approval_notes")

    elif action == PlanWorkflowAction.ACTIVATE:
        # Validate plan has contact lists
        if not plan.contact_lists or len(plan.contact_lists) == 0:
            return False, "Plan must have at least one contact list before activation", {}

        update_dict["activated_at"] = datetime.utcnow()
        update_dict["activated_by"] = user_id

    elif action == PlanWorkflowAction.DEACTIVATE:
        update_dict["deactivated_at"] = datetime.utcnow()

    return True, None, update_dict


def get_workflow_summary(plan: Any) -> Dict[str, Any]:
    """Get workflow status summary"""
    return {
        "current_status": plan.status.value,
        "can_submit_review": plan.status == PlanStatus.DRAFT,
        "can_approve": plan.status == PlanStatus.UNDER_REVIEW,
        "can_reject": plan.status == PlanStatus.UNDER_REVIEW,
        "can_activate": plan.status == PlanStatus.APPROVED,
        "can_deactivate": plan.status == PlanStatus.ACTIVE,
        "can_archive": plan.status in [PlanStatus.APPROVED, PlanStatus.ACTIVE],
        "is_editable": plan.status == PlanStatus.DRAFT,
        "submitted_at": plan.submitted_for_review_at,
        "approved_at": plan.approval_date,
        "approved_by": plan.approved_by_user_id,
        "activated_at": plan.activated_at if hasattr(plan, 'activated_at') else None,
    }
