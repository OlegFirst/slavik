"""
Document Retention Workflow
ISO 22301 Clause 7.5 - Documented Information Retention

Automated retention policy enforcement:
- Calculate retention periods
- Schedule archival
- Handle legal holds
- Manage destruction

Based on:
- BCM_1/document_management/main.py (retention logic lines 391-452)
"""

from enum import Enum
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime, timedelta


# ============================================================================
# ENUMS
# ============================================================================

class RetentionPhase(str, Enum):
    """Document retention lifecycle phases"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    PENDING_DESTRUCTION = "pending_destruction"
    DESTROYED = "destroyed"
    LEGAL_HOLD = "legal_hold"


class RetentionAction(str, Enum):
    """Retention workflow actions"""
    ARCHIVE = "archive"
    EXTEND_RETENTION = "extend_retention"
    SCHEDULE_DESTRUCTION = "schedule_destruction"
    DESTROY = "destroy"
    PLACE_LEGAL_HOLD = "place_legal_hold"
    RELEASE_LEGAL_HOLD = "release_legal_hold"
    RESTORE_FROM_ARCHIVE = "restore_from_archive"


class DestructionStatus(str, Enum):
    """Document destruction statuses"""
    NOT_SCHEDULED = "not_scheduled"
    SCHEDULED = "scheduled"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DESTROYED = "destroyed"
    CANCELLED = "cancelled"


# ============================================================================
# RETENTION PERIODS (ISO 22301 & HIPAA)
# ============================================================================

ISO_22301_RETENTION_PERIODS = {
    # Core BCMS Documents (ISO 22301 requirement: 3-7 years)
    "policy": 7,  # Keep policies for 7 years after superseded
    "procedure": 5,  # Procedures for 5 years
    "plan": 5,  # BC plans for 5 years
    "risk_assessment": 7,  # Risk assessments for 7 years
    "bia": 7,  # BIA for 7 years
    "exercise_report": 5,  # Exercise reports for 5 years
    "audit_report": 7,  # Internal audits for 7 years
    "management_review": 7,  # Management reviews for 7 years

    # Supporting Documents
    "form": 3,  # Completed forms for 3 years
    "training_material": 3,  # Training for 3 years
    "evidence": 5,  # Evidence for 5 years
    "contract": 7,  # Contracts for 7 years after expiry
    "sop": 5,  # SOPs for 5 years

    # General Documents
    "report": 3,
    "communication": 1,
    "other": 3,
}

HIPAA_RETENTION_PERIODS = {
    # HIPAA requirements (6 years minimum)
    "policy": 6,
    "procedure": 6,
    "audit_report": 6,
    "training_material": 6,
    "risk_assessment": 6,
    "evidence": 6,
}


# ============================================================================
# RETENTION CALCULATION
# ============================================================================

def calculate_retention_period(
    document: Any,
    compliance_frameworks: Optional[List[str]] = None
) -> int:
    """
    Calculate retention period in years for document.

    Args:
        document: Document to calculate retention for
        compliance_frameworks: List of frameworks (e.g., ["ISO 22301", "HIPAA"])

    Returns:
        Retention period in years
    """
    # Start with ISO 22301 default
    iso_retention = ISO_22301_RETENTION_PERIODS.get(
        document.document_type,
        3  # Default 3 years
    )

    retention_years = iso_retention

    # Check if HIPAA applies (use maximum retention)
    if compliance_frameworks and "HIPAA" in compliance_frameworks:
        hipaa_retention = HIPAA_RETENTION_PERIODS.get(document.document_type, 6)
        retention_years = max(retention_years, hipaa_retention)

    # Check if document has custom retention
    if hasattr(document, 'retention_years') and document.retention_years:
        retention_years = max(retention_years, document.retention_years)

    return retention_years


def calculate_expiration_date(
    document: Any,
    retention_policy: Optional[Any] = None
) -> Optional[datetime]:
    """
    Calculate when document expires based on retention policy.

    Args:
        document: Document to calculate expiration for
        retention_policy: Retention policy to apply (if any)

    Returns:
        Expiration datetime or None if permanent
    """
    # Check if permanent retention
    if document.is_permanent:
        return None

    if retention_policy and retention_policy.is_permanent:
        return None

    # Determine retention years
    if retention_policy:
        retention_years = retention_policy.retention_years
        trigger_type = retention_policy.trigger_type
    else:
        retention_years = document.retention_years or 3
        trigger_type = "creation_date"

    # Determine trigger date
    trigger_date = None

    if trigger_type == "creation_date":
        trigger_date = document.created_at
    elif trigger_type == "approval_date":
        trigger_date = document.approved_at or document.created_at
    elif trigger_type == "publication_date":
        trigger_date = document.published_at or document.created_at
    elif trigger_type == "last_modified":
        trigger_date = document.updated_at or document.created_at
    else:
        trigger_date = document.created_at

    if not trigger_date:
        return None

    # Calculate expiration
    expiration = trigger_date + timedelta(days=retention_years * 365)

    return expiration


def is_retention_expired(document: Any) -> bool:
    """
    Check if document retention period has expired.

    Args:
        document: Document to check

    Returns:
        True if retention expired, False otherwise
    """
    if document.is_permanent:
        return False

    if not document.expiration_date:
        return False

    return datetime.utcnow() >= document.expiration_date


def days_until_expiration(document: Any) -> Optional[int]:
    """
    Calculate days until document expires.

    Args:
        document: Document to check

    Returns:
        Days until expiration or None if permanent/no expiration
    """
    if document.is_permanent or not document.expiration_date:
        return None

    delta = document.expiration_date - datetime.utcnow()
    return delta.days


# ============================================================================
# ARCHIVAL LOGIC
# ============================================================================

def should_archive_document(
    document: Any,
    retention_policy: Optional[Any] = None,
    archive_threshold_days: int = 365
) -> Tuple[bool, Optional[str]]:
    """
    Determine if document should be archived.

    Criteria:
    - Document is in terminal state (published, superseded)
    - Document hasn't been accessed recently
    - Archive period specified in policy

    Args:
        document: Document to check
        retention_policy: Applicable retention policy
        archive_threshold_days: Days of inactivity before archival

    Returns:
        Tuple of (should_archive, reason)
    """
    # Already archived
    if document.status == "archived":
        return False, "Already archived"

    # Active documents don't archive
    if document.status in ["draft", "under_review"]:
        return False, "Document is still active"

    # Check policy archive rules
    if retention_policy and retention_policy.archive_after_days:
        trigger_date = document.published_at or document.created_at
        days_since_trigger = (datetime.utcnow() - trigger_date).days

        if days_since_trigger >= retention_policy.archive_after_days:
            return True, f"Policy requires archive after {retention_policy.archive_after_days} days"

    # Check inactivity period
    if document.updated_at:
        days_inactive = (datetime.utcnow() - document.updated_at).days

        if days_inactive >= archive_threshold_days:
            return True, f"Inactive for {days_inactive} days"

    return False, None


# ============================================================================
# DESTRUCTION LOGIC
# ============================================================================

def can_schedule_destruction(
    document: Any,
    retention_policy: Optional[Any] = None
) -> Tuple[bool, Optional[str]]:
    """
    Check if document can be scheduled for destruction.

    Requirements:
    - Retention period must be expired
    - Must not be permanent retention
    - Must not be on legal hold
    - Must be in archived state

    Args:
        document: Document to check
        retention_policy: Applicable retention policy

    Returns:
        Tuple of (can_schedule, reason)
    """
    # Check permanent retention
    if document.is_permanent:
        return False, "Document has permanent retention"

    if retention_policy and retention_policy.is_permanent:
        return False, "Policy requires permanent retention"

    # Check legal hold
    if hasattr(document, 'legal_hold_active') and document.legal_hold_active:
        return False, "Document is on legal hold"

    # Check if archived
    if document.status != "archived":
        return False, "Document must be archived before destruction can be scheduled"

    # Check if retention expired
    if not is_retention_expired(document):
        days_left = days_until_expiration(document)
        return False, f"Retention period not expired ({days_left} days remaining)"

    # Check if review required
    if retention_policy and retention_policy.require_review_before_destruction:
        # Would need to check if review was completed
        # For now, just note the requirement
        pass

    return True, None


def calculate_destruction_date(
    document: Any,
    retention_policy: Optional[Any] = None
) -> Optional[datetime]:
    """
    Calculate when document can be destroyed.

    Args:
        document: Document to calculate for
        retention_policy: Applicable retention policy

    Returns:
        Destruction date or None if permanent
    """
    if document.is_permanent:
        return None

    if retention_policy and retention_policy.is_permanent:
        return None

    # Get expiration date
    expiration = document.expiration_date
    if not expiration:
        expiration = calculate_expiration_date(document, retention_policy)

    if not expiration:
        return None

    # Add destruction buffer from policy
    if retention_policy and retention_policy.destroy_after_days:
        destruction_date = expiration + timedelta(days=retention_policy.destroy_after_days)
    else:
        # Default: destroy 90 days after expiration
        destruction_date = expiration + timedelta(days=90)

    return destruction_date


# ============================================================================
# LEGAL HOLD
# ============================================================================

def can_place_legal_hold(
    document: Any,
    user_id: str,
    reason: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Check if legal hold can be placed on document.

    Requirements:
    - Document must exist and not be destroyed
    - User must have authority (would check permissions)
    - Must provide reason

    Args:
        document: Document to place hold on
        user_id: User placing hold
        reason: Reason for legal hold

    Returns:
        Tuple of (can_place, error_message)
    """
    if document.status == "destroyed":
        return False, "Cannot place legal hold on destroyed document"

    if hasattr(document, 'legal_hold_active') and document.legal_hold_active:
        return False, "Document already has active legal hold"

    if not reason or len(reason.strip()) < 20:
        return False, "Legal hold reason must be provided (minimum 20 characters)"

    return True, None


def can_release_legal_hold(
    document: Any,
    user_id: str,
    reason: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Check if legal hold can be released.

    Requirements:
    - Document must have active legal hold
    - User must have authority
    - Must provide reason

    Args:
        document: Document to release hold from
        user_id: User releasing hold
        reason: Reason for release

    Returns:
        Tuple of (can_release, error_message)
    """
    if not hasattr(document, 'legal_hold_active') or not document.legal_hold_active:
        return False, "Document does not have active legal hold"

    if not reason or len(reason.strip()) < 20:
        return False, "Release reason must be provided (minimum 20 characters)"

    return True, None


# ============================================================================
# WORKFLOW EXECUTION
# ============================================================================

def execute_retention_action(
    document: Any,
    action: RetentionAction,
    user_id: str,
    retention_policy: Optional[Any] = None,
    **kwargs
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Execute a retention workflow action.

    Args:
        document: Document to act on
        action: Retention action to perform
        user_id: User performing action
        retention_policy: Applicable retention policy
        **kwargs: Additional action parameters

    Returns:
        Tuple of (success, error_message, action_data)
    """
    action_data = {
        "action": action.value,
        "performed_by": user_id,
        "performed_at": datetime.utcnow().isoformat(),
    }

    if action == RetentionAction.ARCHIVE:
        should_archive, reason = should_archive_document(document, retention_policy)

        if not should_archive:
            return False, f"Cannot archive: {reason}", None

        action_data["archived_at"] = datetime.utcnow().isoformat()
        action_data["reason"] = reason

        return True, None, action_data

    elif action == RetentionAction.SCHEDULE_DESTRUCTION:
        can_schedule, error = can_schedule_destruction(document, retention_policy)

        if not can_schedule:
            return False, error, None

        destruction_date = calculate_destruction_date(document, retention_policy)

        action_data["destruction_scheduled_for"] = destruction_date.isoformat() if destruction_date else None
        action_data["requires_review"] = retention_policy.require_review_before_destruction if retention_policy else True

        return True, None, action_data

    elif action == RetentionAction.PLACE_LEGAL_HOLD:
        reason = kwargs.get('reason')
        can_place, error = can_place_legal_hold(document, user_id, reason)

        if not can_place:
            return False, error, None

        action_data["legal_hold_reason"] = reason
        action_data["legal_hold_placed_at"] = datetime.utcnow().isoformat()
        action_data["legal_hold_placed_by"] = user_id

        return True, None, action_data

    elif action == RetentionAction.RELEASE_LEGAL_HOLD:
        reason = kwargs.get('reason')
        can_release, error = can_release_legal_hold(document, user_id, reason)

        if not can_release:
            return False, error, None

        action_data["legal_hold_release_reason"] = reason
        action_data["legal_hold_released_at"] = datetime.utcnow().isoformat()
        action_data["legal_hold_released_by"] = user_id

        return True, None, action_data

    elif action == RetentionAction.EXTEND_RETENTION:
        additional_years = kwargs.get('additional_years', 1)
        reason = kwargs.get('reason')

        if not reason:
            return False, "Reason for retention extension is required", None

        current_retention = document.retention_years or 3
        new_retention = current_retention + additional_years

        # Recalculate expiration
        new_expiration = calculate_expiration_date(document, retention_policy)

        action_data["previous_retention_years"] = current_retention
        action_data["new_retention_years"] = new_retention
        action_data["new_expiration_date"] = new_expiration.isoformat() if new_expiration else None
        action_data["extension_reason"] = reason

        return True, None, action_data

    elif action == RetentionAction.RESTORE_FROM_ARCHIVE:
        if document.status != "archived":
            return False, "Only archived documents can be restored", None

        action_data["restored_at"] = datetime.utcnow().isoformat()
        action_data["restored_to_status"] = "published"  # or original status

        return True, None, action_data

    return False, f"Unknown retention action: {action.value}", None


# ============================================================================
# RETENTION REPORTING
# ============================================================================

def get_retention_status(
    document: Any,
    retention_policy: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get comprehensive retention status for document.

    Returns:
        Dictionary with retention information
    """
    expiration = document.expiration_date or calculate_expiration_date(document, retention_policy)
    days_left = days_until_expiration(document)
    is_expired = is_retention_expired(document)
    should_archive, archive_reason = should_archive_document(document, retention_policy)
    can_destroy, destroy_reason = can_schedule_destruction(document, retention_policy)

    status = {
        "retention_years": document.retention_years,
        "is_permanent": document.is_permanent,
        "expiration_date": expiration.isoformat() if expiration else None,
        "days_until_expiration": days_left,
        "is_expired": is_expired,
        "current_phase": RetentionPhase.ACTIVE.value if document.status not in ["archived"] else RetentionPhase.ARCHIVED.value,
        "should_archive": should_archive,
        "archive_reason": archive_reason,
        "can_schedule_destruction": can_destroy,
        "destruction_eligibility_reason": destroy_reason,
    }

    # Add legal hold info
    if hasattr(document, 'legal_hold_active'):
        status["legal_hold_active"] = document.legal_hold_active
        if document.legal_hold_active:
            status["legal_hold_placed_at"] = document.legal_hold_placed_at.isoformat() if hasattr(document, 'legal_hold_placed_at') else None

    # Add policy info
    if retention_policy:
        status["policy"] = {
            "policy_id": retention_policy.policy_id,
            "policy_name": retention_policy.policy_name,
            "retention_years": retention_policy.retention_years,
            "archive_after_days": retention_policy.archive_after_days,
            "destroy_after_days": retention_policy.destroy_after_days,
            "require_review_before_destruction": retention_policy.require_review_before_destruction,
        }

    return status


def get_documents_pending_retention_action(
    documents: List[Any],
    action_type: str
) -> List[Dict[str, Any]]:
    """
    Get documents that need retention actions.

    Args:
        documents: List of documents to check
        action_type: Type of action ("archive", "destroy", "review")

    Returns:
        List of documents needing action with details
    """
    pending = []

    for doc in documents:
        if action_type == "archive":
            should_archive, reason = should_archive_document(doc)
            if should_archive:
                pending.append({
                    "document_id": doc.document_id,
                    "document_code": doc.document_code,
                    "title": doc.title,
                    "reason": reason,
                    "priority": "high" if (datetime.utcnow() - doc.updated_at).days > 730 else "normal",
                })

        elif action_type == "destroy":
            can_destroy, reason = can_schedule_destruction(doc)
            if can_destroy:
                pending.append({
                    "document_id": doc.document_id,
                    "document_code": doc.document_code,
                    "title": doc.title,
                    "expiration_date": doc.expiration_date.isoformat() if doc.expiration_date else None,
                    "days_overdue": (datetime.utcnow() - doc.expiration_date).days if doc.expiration_date else 0,
                })

    return pending
