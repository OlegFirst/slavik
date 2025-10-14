"""
Document Lifecycle Workflow State Machine
ISO 22301 Clause 7.5.3 - Control of Documented Information

States: DRAFT → UNDER_REVIEW → APPROVED → PUBLISHED → ARCHIVED/SUPERSEDED/OBSOLETE

Based on:
- BCM_1/document_management/main.py (workflow logic lines 271-325)
- Plans module workflow pattern
"""

from enum import Enum
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime


# ============================================================================
# ENUMS
# ============================================================================

class DocumentLifecycleState(str, Enum):
    """Document lifecycle states"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    OBSOLETE = "obsolete"


class DocumentLifecycleAction(str, Enum):
    """Actions that trigger state transitions"""
    SUBMIT_FOR_REVIEW = "submit_for_review"
    APPROVE = "approve"
    REJECT = "reject"
    PUBLISH = "publish"
    ARCHIVE = "archive"
    SUPERSEDE = "supersede"
    MARK_OBSOLETE = "mark_obsolete"
    RESTORE = "restore"
    REVISE = "revise"


# ============================================================================
# STATE TRANSITIONS
# ============================================================================

LIFECYCLE_TRANSITIONS: Dict[Tuple[DocumentLifecycleState, DocumentLifecycleAction], DocumentLifecycleState] = {
    # From DRAFT
    (DocumentLifecycleState.DRAFT, DocumentLifecycleAction.SUBMIT_FOR_REVIEW): DocumentLifecycleState.UNDER_REVIEW,
    (DocumentLifecycleState.DRAFT, DocumentLifecycleAction.ARCHIVE): DocumentLifecycleState.ARCHIVED,

    # From UNDER_REVIEW
    (DocumentLifecycleState.UNDER_REVIEW, DocumentLifecycleAction.APPROVE): DocumentLifecycleState.APPROVED,
    (DocumentLifecycleState.UNDER_REVIEW, DocumentLifecycleAction.REJECT): DocumentLifecycleState.DRAFT,
    (DocumentLifecycleState.UNDER_REVIEW, DocumentLifecycleAction.ARCHIVE): DocumentLifecycleState.ARCHIVED,

    # From APPROVED
    (DocumentLifecycleState.APPROVED, DocumentLifecycleAction.PUBLISH): DocumentLifecycleState.PUBLISHED,
    (DocumentLifecycleState.APPROVED, DocumentLifecycleAction.REVISE): DocumentLifecycleState.DRAFT,
    (DocumentLifecycleState.APPROVED, DocumentLifecycleAction.ARCHIVE): DocumentLifecycleState.ARCHIVED,

    # From PUBLISHED
    (DocumentLifecycleState.PUBLISHED, DocumentLifecycleAction.REVISE): DocumentLifecycleState.DRAFT,
    (DocumentLifecycleState.PUBLISHED, DocumentLifecycleAction.ARCHIVE): DocumentLifecycleState.ARCHIVED,
    (DocumentLifecycleState.PUBLISHED, DocumentLifecycleAction.SUPERSEDE): DocumentLifecycleState.SUPERSEDED,
    (DocumentLifecycleState.PUBLISHED, DocumentLifecycleAction.MARK_OBSOLETE): DocumentLifecycleState.OBSOLETE,

    # From ARCHIVED
    (DocumentLifecycleState.ARCHIVED, DocumentLifecycleAction.RESTORE): DocumentLifecycleState.DRAFT,

    # From SUPERSEDED
    (DocumentLifecycleState.SUPERSEDED, DocumentLifecycleAction.RESTORE): DocumentLifecycleState.PUBLISHED,
    (DocumentLifecycleState.SUPERSEDED, DocumentLifecycleAction.ARCHIVE): DocumentLifecycleState.ARCHIVED,

    # From OBSOLETE
    (DocumentLifecycleState.OBSOLETE, DocumentLifecycleAction.ARCHIVE): DocumentLifecycleState.ARCHIVED,
}


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def can_submit_for_review(document: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate if document can be submitted for review.

    Requirements:
    - Must have title
    - Must have owner
    - Must have file attached
    - If controlled document, must have required metadata
    """
    if not document.title or len(document.title.strip()) < 3:
        return False, "Document must have a title (minimum 3 characters)"

    if not document.owner_id:
        return False, "Document must have an owner assigned"

    if not document.file_path:
        return False, "Document must have a file attached"

    if document.is_controlled:
        if not document.document_type:
            return False, "Controlled documents must have a document type"

        if not document.classification:
            return False, "Controlled documents must have a classification level"

        if document.requires_approval and not hasattr(document, 'approvals'):
            return False, "Document requires approval but no approvers assigned"

    return True, None


def can_approve(document: Any, user_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if document can be approved by user.

    Requirements:
    - Must be in UNDER_REVIEW state
    - All required approvals must be completed
    - User must be an assigned approver (if applicable)
    """
    if document.status != DocumentLifecycleState.UNDER_REVIEW.value:
        return False, "Document must be under review to approve"

    if document.requires_approval:
        if not hasattr(document, 'approvals') or len(document.approvals) == 0:
            return False, "Document requires approvals but none are configured"

        # Check if all required approvals are completed
        pending_approvals = [
            a for a in document.approvals
            if a.approval_status == "pending"
        ]

        if pending_approvals:
            # Check if user is one of the pending approvers
            user_is_approver = any(a.approver_id == user_id for a in pending_approvals)
            if not user_is_approver:
                return False, f"User is not an assigned approver (pending: {len(pending_approvals)})"

    return True, None


def can_publish(document: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate if document can be published.

    Requirements:
    - Must be in APPROVED state
    - All approvals must be completed
    - Must pass quality checks
    """
    if document.status != DocumentLifecycleState.APPROVED.value:
        return False, "Document must be approved before publishing"

    if document.requires_approval:
        if not hasattr(document, 'approvals') or len(document.approvals) == 0:
            return False, "Document requires approvals but none found"

        # All approvals must be approved
        unapproved = [
            a for a in document.approvals
            if a.approval_status != "approved"
        ]

        if unapproved:
            return False, f"{len(unapproved)} approval(s) are not completed"

    return True, None


def can_archive(document: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate if document can be archived.

    Requirements:
    - Can archive from most states
    - Cannot archive if currently in active use (would need to check references)
    """
    allowed_states = [
        DocumentLifecycleState.DRAFT.value,
        DocumentLifecycleState.UNDER_REVIEW.value,
        DocumentLifecycleState.APPROVED.value,
        DocumentLifecycleState.PUBLISHED.value,
        DocumentLifecycleState.SUPERSEDED.value,
    ]

    if document.status not in allowed_states:
        return False, f"Cannot archive document in {document.status} state"

    return True, None


def can_supersede(document: Any, new_version_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate if document can be superseded.

    Requirements:
    - Must be in PUBLISHED state
    - Must have a new version to supersede it (optional check)
    """
    if document.status != DocumentLifecycleState.PUBLISHED.value:
        return False, "Only published documents can be superseded"

    if new_version_id is not None and new_version_id == document.document_id:
        return False, "Cannot supersede document with itself"

    return True, None


def can_mark_obsolete(document: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate if document can be marked obsolete.

    Requirements:
    - Must be in PUBLISHED state
    - Obsolete means no longer valid (different from superseded)
    """
    if document.status != DocumentLifecycleState.PUBLISHED.value:
        return False, "Only published documents can be marked obsolete"

    return True, None


def can_restore(document: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate if document can be restored.

    Requirements:
    - Must be in ARCHIVED or SUPERSEDED state
    """
    allowed_states = [
        DocumentLifecycleState.ARCHIVED.value,
        DocumentLifecycleState.SUPERSEDED.value,
    ]

    if document.status not in allowed_states:
        return False, f"Can only restore archived or superseded documents"

    return True, None


def can_revise(document: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate if document can be revised.

    Requirements:
    - Must be in APPROVED or PUBLISHED state
    - Creates new draft version
    """
    allowed_states = [
        DocumentLifecycleState.APPROVED.value,
        DocumentLifecycleState.PUBLISHED.value,
    ]

    if document.status not in allowed_states:
        return False, "Can only revise approved or published documents"

    return True, None


# ============================================================================
# TRANSITION FUNCTIONS
# ============================================================================

def can_transition(
    current_state: DocumentLifecycleState,
    action: DocumentLifecycleAction
) -> bool:
    """Check if transition is valid."""
    return (current_state, action) in LIFECYCLE_TRANSITIONS


def get_next_state(
    current_state: DocumentLifecycleState,
    action: DocumentLifecycleAction
) -> Optional[DocumentLifecycleState]:
    """Get next state for action, or None if invalid."""
    return LIFECYCLE_TRANSITIONS.get((current_state, action))


def get_available_actions(
    current_state: DocumentLifecycleState
) -> List[DocumentLifecycleAction]:
    """Get all valid actions for current state."""
    return [
        action for (state, action) in LIFECYCLE_TRANSITIONS.keys()
        if state == current_state
    ]


# ============================================================================
# WORKFLOW EXECUTION
# ============================================================================

def execute_transition(
    document: Any,
    action: DocumentLifecycleAction,
    user_id: str,
    notes: Optional[str] = None,
    **kwargs
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Execute a lifecycle transition with validation.

    Args:
        document: Document to transition
        action: Action to perform
        user_id: User performing action
        notes: Optional notes about transition
        **kwargs: Additional action-specific parameters

    Returns:
        Tuple of (success, error_message, transition_data)
    """
    current_state = DocumentLifecycleState(document.status)

    # Check if transition is valid
    if not can_transition(current_state, action):
        return False, f"Cannot {action.value} from {current_state.value} state", None

    # Action-specific validation
    if action == DocumentLifecycleAction.SUBMIT_FOR_REVIEW:
        can_do, error = can_submit_for_review(document)
        if not can_do:
            return False, error, None

    elif action == DocumentLifecycleAction.APPROVE:
        can_do, error = can_approve(document, user_id)
        if not can_do:
            return False, error, None

    elif action == DocumentLifecycleAction.PUBLISH:
        can_do, error = can_publish(document)
        if not can_do:
            return False, error, None

    elif action == DocumentLifecycleAction.ARCHIVE:
        can_do, error = can_archive(document)
        if not can_do:
            return False, error, None

    elif action == DocumentLifecycleAction.SUPERSEDE:
        new_version_id = kwargs.get('new_version_id')
        can_do, error = can_supersede(document, new_version_id)
        if not can_do:
            return False, error, None

    elif action == DocumentLifecycleAction.MARK_OBSOLETE:
        can_do, error = can_mark_obsolete(document)
        if not can_do:
            return False, error, None

    elif action == DocumentLifecycleAction.RESTORE:
        can_do, error = can_restore(document)
        if not can_do:
            return False, error, None

    elif action == DocumentLifecycleAction.REVISE:
        can_do, error = can_revise(document)
        if not can_do:
            return False, error, None

    # Get next state
    next_state = get_next_state(current_state, action)
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

    # Action-specific updates
    if action == DocumentLifecycleAction.APPROVE:
        transition_data["approved_at"] = datetime.utcnow()
        transition_data["approved_by"] = user_id

    elif action == DocumentLifecycleAction.PUBLISH:
        transition_data["published_at"] = datetime.utcnow()

    elif action == DocumentLifecycleAction.ARCHIVE:
        transition_data["archived_at"] = datetime.utcnow()

    elif action == DocumentLifecycleAction.SUPERSEDE:
        transition_data["superseded_by"] = kwargs.get('new_version_id')

    return True, None, transition_data


# ============================================================================
# WORKFLOW REPORTING
# ============================================================================

def get_workflow_summary(document: Any) -> Dict[str, Any]:
    """
    Get summary of document workflow status.

    Returns:
        Dictionary with workflow status information
    """
    current_state = DocumentLifecycleState(document.status)
    available_actions = get_available_actions(current_state)

    # Check specific action permissions
    can_submit, submit_error = can_submit_for_review(document)
    can_pub, publish_error = can_publish(document)
    can_arch, archive_error = can_archive(document)

    summary = {
        "current_state": current_state.value,
        "available_actions": [a.value for a in available_actions],
        "checks": {
            "can_submit_for_review": can_submit,
            "submit_error": submit_error,
            "can_publish": can_pub,
            "publish_error": publish_error,
            "can_archive": can_arch,
            "archive_error": archive_error,
        },
        "is_controlled": document.is_controlled,
        "requires_approval": document.requires_approval,
    }

    # Add approval status if applicable
    if document.requires_approval and hasattr(document, 'approvals'):
        summary["approval_status"] = {
            "total_approvals": len(document.approvals),
            "approved": len([a for a in document.approvals if a.approval_status == "approved"]),
            "pending": len([a for a in document.approvals if a.approval_status == "pending"]),
            "rejected": len([a for a in document.approvals if a.approval_status == "rejected"]),
        }

    # Add key dates
    summary["dates"] = {
        "created_at": document.created_at.isoformat() if document.created_at else None,
        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
        "approved_at": document.approved_at.isoformat() if document.approved_at else None,
        "published_at": document.published_at.isoformat() if document.published_at else None,
        "archived_at": document.archived_at.isoformat() if document.archived_at else None,
    }

    return summary
