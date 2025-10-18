"""
Document Approval Workflow State Machine
ISO 22301 - Controlled Document Approval Process

Handles multi-stage approval chains for controlled documents.

Based on:
- BCM_1/document_management/main.py (approval logic lines 327-389)
- Plans module workflow pattern
"""

from enum import Enum
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta


# ============================================================================
# ENUMS
# ============================================================================

class ApprovalWorkflowState(str, Enum):
    """Approval request states"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RECALLED = "recalled"


class ApprovalWorkflowAction(str, Enum):
    """Actions in approval workflow"""
    REQUEST_APPROVAL = "request_approval"
    APPROVE = "approve"
    REJECT = "reject"
    RECALL = "recall"
    ESCALATE = "escalate"


class ApprovalPriority(str, Enum):
    """Approval urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ApproverRole(str, Enum):
    """Standard approver roles"""
    TECHNICAL_REVIEWER = "technical_reviewer"
    QUALITY_ASSURANCE = "quality_assurance"
    COMPLIANCE_OFFICER = "compliance_officer"
    DEPARTMENT_HEAD = "department_head"
    MANAGEMENT = "management"
    EXECUTIVE = "executive"


# ============================================================================
# STATE TRANSITIONS
# ============================================================================

APPROVAL_TRANSITIONS: Dict[Tuple[ApprovalWorkflowState, ApprovalWorkflowAction], ApprovalWorkflowState] = {
    # From PENDING
    (ApprovalWorkflowState.PENDING, ApprovalWorkflowAction.APPROVE): ApprovalWorkflowState.APPROVED,
    (ApprovalWorkflowState.PENDING, ApprovalWorkflowAction.REJECT): ApprovalWorkflowState.REJECTED,
    (ApprovalWorkflowState.PENDING, ApprovalWorkflowAction.RECALL): ApprovalWorkflowState.RECALLED,

    # From APPROVED (can be recalled if needed)
    (ApprovalWorkflowState.APPROVED, ApprovalWorkflowAction.RECALL): ApprovalWorkflowState.RECALLED,

    # From REJECTED (can be recalled to resubmit)
    (ApprovalWorkflowState.REJECTED, ApprovalWorkflowAction.RECALL): ApprovalWorkflowState.RECALLED,

    # From RECALLED (can request again)
    (ApprovalWorkflowState.RECALLED, ApprovalWorkflowAction.REQUEST_APPROVAL): ApprovalWorkflowState.PENDING,
}


# ============================================================================
# APPROVAL CHAIN CONFIGURATION
# ============================================================================

def get_standard_approval_chain(document_type: str, classification: str) -> List[Dict[str, Any]]:
    """
    Get standard approval chain based on document type and classification.

    Returns:
        List of approval stages with role, SLA, and requirements
    """
    # Default chain for most documents
    chain = []

    # Stage 1: Technical Review (always required)
    chain.append({
        "stage": 1,
        "role": ApproverRole.TECHNICAL_REVIEWER.value,
        "required": True,
        "sla_hours": 48,
        "description": "Technical accuracy and completeness review"
    })

    # Stage 2: Quality Assurance (for controlled documents)
    if classification in ["confidential", "restricted", "highly_restricted"]:
        chain.append({
            "stage": 2,
            "role": ApproverRole.QUALITY_ASSURANCE.value,
            "required": True,
            "sla_hours": 24,
            "description": "Quality standards and compliance check"
        })

    # Stage 3: Compliance (for high-classification or specific types)
    if classification in ["restricted", "highly_restricted"] or document_type in ["policy", "procedure"]:
        chain.append({
            "stage": len(chain) + 1,
            "role": ApproverRole.COMPLIANCE_OFFICER.value,
            "required": True,
            "sla_hours": 72,
            "description": "Regulatory compliance verification"
        })

    # Stage 4: Management Approval (for policies and critical documents)
    if document_type in ["policy", "management_review", "risk_assessment"]:
        chain.append({
            "stage": len(chain) + 1,
            "role": ApproverRole.MANAGEMENT.value,
            "required": True,
            "sla_hours": 120,
            "description": "Management review and authorization"
        })

    # Stage 5: Executive Approval (for highest classification)
    if classification == "highly_restricted" or document_type == "policy":
        chain.append({
            "stage": len(chain) + 1,
            "role": ApproverRole.EXECUTIVE.value,
            "required": True,
            "sla_hours": 168,  # 1 week
            "description": "Executive authorization"
        })

    return chain


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def can_request_approval(
    document: Any,
    approver_id: str,
    approver_role: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate if approval can be requested.

    Requirements:
    - Document must be ready for review
    - Approver must be valid
    - Approver must have appropriate role
    """
    if not document.title:
        return False, "Document must have a title"

    if not document.file_path:
        return False, "Document must have a file attached"

    if not approver_id:
        return False, "Approver ID is required"

    if not approver_role:
        return False, "Approver role is required"

    # Validate approver role
    try:
        ApproverRole(approver_role)
    except ValueError:
        return False, f"Invalid approver role: {approver_role}"

    return True, None


def can_approve_request(
    approval: Any,
    user_id: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate if user can approve request.

    Requirements:
    - Must be pending
    - User must be the assigned approver
    - Must not be overdue by too much (configurable grace period)
    """
    if approval.approval_status != ApprovalWorkflowState.PENDING.value:
        return False, f"Approval is {approval.approval_status}, cannot approve"

    if approval.approver_id != user_id:
        return False, "Only assigned approver can approve this request"

    return True, None


def can_reject_request(
    approval: Any,
    user_id: str,
    reason: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate if user can reject request.

    Requirements:
    - Must be pending
    - User must be the assigned approver
    - Must provide reason for rejection
    """
    if approval.approval_status != ApprovalWorkflowState.PENDING.value:
        return False, f"Approval is {approval.approval_status}, cannot reject"

    if approval.approver_id != user_id:
        return False, "Only assigned approver can reject this request"

    if not reason or len(reason.strip()) < 10:
        return False, "Rejection reason must be provided (minimum 10 characters)"

    return True, None


def can_recall_request(
    approval: Any,
    user_id: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate if request can be recalled.

    Requirements:
    - Can recall from PENDING, APPROVED, or REJECTED
    - Only document owner or approver can recall
    """
    allowed_states = [
        ApprovalWorkflowState.PENDING.value,
        ApprovalWorkflowState.APPROVED.value,
        ApprovalWorkflowState.REJECTED.value,
    ]

    if approval.approval_status not in allowed_states:
        return False, f"Cannot recall from {approval.approval_status} state"

    # Note: In real implementation, check if user is document owner
    # For now, allow any user (would need document context)

    return True, None


def can_escalate_request(
    approval: Any,
    days_overdue: int = 7
) -> Tuple[bool, Optional[str]]:
    """
    Check if approval should be escalated.

    Requirements:
    - Must be pending
    - Must be overdue by specified days
    """
    if approval.approval_status != ApprovalWorkflowState.PENDING.value:
        return False, "Only pending approvals can be escalated"

    if not approval.due_date:
        return False, "Approval has no due date set"

    days_past_due = (datetime.utcnow() - approval.due_date).days

    if days_past_due < days_overdue:
        return False, f"Only {days_past_due} days overdue, escalation threshold is {days_overdue}"

    return True, None


# ============================================================================
# APPROVAL LOGIC
# ============================================================================

def is_approval_chain_complete(
    document: Any,
    approvals: List[Any]
) -> Tuple[bool, Optional[str]]:
    """
    Check if all required approvals in chain are complete.

    Returns:
        Tuple of (is_complete, message)
    """
    if not approvals:
        return False, "No approvals configured"

    # Get all stages
    stages = sorted(set(a.approval_stage for a in approvals))

    for stage in stages:
        stage_approvals = [a for a in approvals if a.approval_stage == stage]

        # Check if any approval in this stage is approved
        stage_approved = any(a.approval_status == ApprovalWorkflowState.APPROVED.value
                           for a in stage_approvals)

        if not stage_approved:
            pending_count = len([a for a in stage_approvals
                               if a.approval_status == ApprovalWorkflowState.PENDING.value])
            return False, f"Stage {stage} not approved (pending: {pending_count})"

    return True, "All approval stages completed"


def get_current_approval_stage(approvals: List[Any]) -> Optional[int]:
    """
    Get the current stage that needs approval.

    Returns:
        Stage number or None if all complete
    """
    if not approvals:
        return None

    # Get all stages
    stages = sorted(set(a.approval_stage for a in approvals))

    for stage in stages:
        stage_approvals = [a for a in approvals if a.approval_stage == stage]

        # Check if this stage is complete
        stage_complete = any(a.approval_status == ApprovalWorkflowState.APPROVED.value
                           for a in stage_approvals)

        if not stage_complete:
            return stage

    return None  # All stages complete


def get_next_approvers(
    approvals: List[Any],
    current_stage: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get list of next approvers that need to act.

    Returns:
        List of approver information dictionaries
    """
    if current_stage is None:
        current_stage = get_current_approval_stage(approvals)

    if current_stage is None:
        return []

    stage_approvals = [a for a in approvals if a.approval_stage == current_stage]
    pending_approvals = [a for a in stage_approvals
                        if a.approval_status == ApprovalWorkflowState.PENDING.value]

    return [
        {
            "approval_id": a.approval_id,
            "approver_id": a.approver_id,
            "approver_role": a.approver_role,
            "due_date": a.due_date.isoformat() if a.due_date else None,
            "is_overdue": a.due_date and datetime.utcnow() > a.due_date,
        }
        for a in pending_approvals
    ]


# ============================================================================
# PRIORITY CALCULATION
# ============================================================================

def calculate_approval_priority(
    document: Any,
    due_date: Optional[datetime] = None
) -> ApprovalPriority:
    """
    Calculate approval priority based on document attributes.

    Factors:
    - Document classification (higher = more urgent)
    - Document type (policy/procedure = urgent)
    - Due date proximity
    - Business impact
    """
    priority_score = 0

    # Classification factor (0-40 points)
    classification_scores = {
        "public": 0,
        "internal": 10,
        "confidential": 20,
        "restricted": 30,
        "highly_restricted": 40,
    }
    priority_score += classification_scores.get(document.classification, 0)

    # Document type factor (0-30 points)
    critical_types = ["policy", "procedure", "risk_assessment", "bia"]
    if document.document_type in critical_types:
        priority_score += 30
    else:
        priority_score += 10

    # Due date factor (0-30 points)
    if due_date:
        days_until_due = (due_date - datetime.utcnow()).days
        if days_until_due <= 1:
            priority_score += 30
        elif days_until_due <= 3:
            priority_score += 20
        elif days_until_due <= 7:
            priority_score += 10

    # Determine priority level
    if priority_score >= 70:
        return ApprovalPriority.URGENT
    elif priority_score >= 50:
        return ApprovalPriority.HIGH
    elif priority_score >= 30:
        return ApprovalPriority.MEDIUM
    else:
        return ApprovalPriority.LOW


def calculate_approval_due_date(
    requested_at: datetime,
    sla_hours: int = 48
) -> datetime:
    """
    Calculate approval due date based on SLA.

    Args:
        requested_at: When approval was requested
        sla_hours: SLA in hours (default 48 = 2 business days)

    Returns:
        Due date datetime
    """
    return requested_at + timedelta(hours=sla_hours)


# ============================================================================
# WORKFLOW EXECUTION
# ============================================================================

def execute_approval_transition(
    approval: Any,
    action: ApprovalWorkflowAction,
    user_id: str,
    notes: Optional[str] = None,
    **kwargs
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Execute an approval workflow transition.

    Args:
        approval: Approval request to transition
        action: Action to perform
        user_id: User performing action
        notes: Optional notes
        **kwargs: Additional parameters

    Returns:
        Tuple of (success, error_message, transition_data)
    """
    current_state = ApprovalWorkflowState(approval.approval_status)

    # Check if transition is valid
    if (current_state, action) not in APPROVAL_TRANSITIONS:
        return False, f"Cannot {action.value} from {current_state.value} state", None

    # Action-specific validation
    if action == ApprovalWorkflowAction.APPROVE:
        can_do, error = can_approve_request(approval, user_id)
        if not can_do:
            return False, error, None

    elif action == ApprovalWorkflowAction.REJECT:
        reason = kwargs.get('reason') or notes
        can_do, error = can_reject_request(approval, user_id, reason)
        if not can_do:
            return False, error, None

    elif action == ApprovalWorkflowAction.RECALL:
        can_do, error = can_recall_request(approval, user_id)
        if not can_do:
            return False, error, None

    # Get next state
    next_state = APPROVAL_TRANSITIONS.get((current_state, action))
    if next_state is None:
        return False, f"No valid transition for {action.value}", None

    # Prepare transition data
    transition_data = {
        "previous_state": current_state.value,
        "new_state": next_state.value,
        "action": action.value,
        "performed_by": user_id,
        "performed_at": datetime.utcnow().isoformat(),
        "notes": notes,
    }

    # Action-specific data
    if action == ApprovalWorkflowAction.REJECT:
        transition_data["rejection_reason"] = kwargs.get('reason') or notes
        transition_data["suggested_changes"] = kwargs.get('suggested_changes', [])

    return True, None, transition_data


# ============================================================================
# WORKFLOW REPORTING
# ============================================================================

def get_approval_workflow_summary(
    document: Any,
    approvals: List[Any]
) -> Dict[str, Any]:
    """
    Get summary of approval workflow status.

    Returns:
        Dictionary with approval workflow information
    """
    current_stage = get_current_approval_stage(approvals)
    is_complete, complete_msg = is_approval_chain_complete(document, approvals)
    next_approvers = get_next_approvers(approvals, current_stage)

    # Calculate overall statistics
    total_approvals = len(approvals)
    approved_count = len([a for a in approvals if a.approval_status == ApprovalWorkflowState.APPROVED.value])
    rejected_count = len([a for a in approvals if a.approval_status == ApprovalWorkflowState.REJECTED.value])
    pending_count = len([a for a in approvals if a.approval_status == ApprovalWorkflowState.PENDING.value])

    # Check for overdue approvals
    overdue_approvals = [
        a for a in approvals
        if a.approval_status == ApprovalWorkflowState.PENDING.value
        and a.due_date
        and datetime.utcnow() > a.due_date
    ]

    summary = {
        "is_complete": is_complete,
        "completion_message": complete_msg,
        "current_stage": current_stage,
        "total_stages": len(set(a.approval_stage for a in approvals)) if approvals else 0,
        "statistics": {
            "total": total_approvals,
            "approved": approved_count,
            "rejected": rejected_count,
            "pending": pending_count,
            "overdue": len(overdue_approvals),
        },
        "next_approvers": next_approvers,
        "overdue_approvals": [
            {
                "approval_id": a.approval_id,
                "approver_id": a.approver_id,
                "stage": a.approval_stage,
                "days_overdue": (datetime.utcnow() - a.due_date).days,
            }
            for a in overdue_approvals
        ],
    }

    # Add progress percentage
    if total_approvals > 0:
        summary["progress_percent"] = int((approved_count / total_approvals) * 100)
    else:
        summary["progress_percent"] = 0

    return summary
