"""
Event Publishers for Documents Service
Publishes events to EventBus when document actions occur

Events published:
- bcm.document.uploaded
- bcm.document.approved
- bcm.document.published
- bcm.document.archived
- bcm.document.expired
- bcm.document.shared
"""

from typing import Dict, Any, Optional
from .eventbus import EventBus, DocumentEvents, publish_document_event


# ============================================================================
# DOCUMENT LIFECYCLE EVENTS
# ============================================================================

async def publish_document_uploaded(
    eventbus: EventBus,
    document_id: int,
    document_code: str,
    title: str,
    document_type: str,
    file_name: str,
    file_size: int,
    user_id: str,
    tenant_id: str
):
    """
    Publish document uploaded event.

    Triggered when: File is uploaded to document

    Subscribers: Plans, Governance, Audit (for evidence tracking)
    """
    await publish_document_event(
        eventbus,
        DocumentEvents.UPLOADED,
        document_id=document_id,
        document_code=document_code,
        title=title,
        user_id=user_id,
        document_type=document_type,
        file_name=file_name,
        file_size=file_size,
        tenant_id=tenant_id
    )


async def publish_document_approved(
    eventbus: EventBus,
    document_id: int,
    document_code: str,
    title: str,
    document_type: str,
    approved_by: str,
    tenant_id: str
):
    """
    Publish document approved event.

    Triggered when: Document passes all approvals

    Subscribers: Governance (policy tracking), Plans (plan dependencies)
    """
    await publish_document_event(
        eventbus,
        DocumentEvents.APPROVED,
        document_id=document_id,
        document_code=document_code,
        title=title,
        user_id=approved_by,
        document_type=document_type,
        tenant_id=tenant_id
    )


async def publish_document_rejected(
    eventbus: EventBus,
    document_id: int,
    document_code: str,
    title: str,
    rejected_by: str,
    reason: str,
    tenant_id: str
):
    """
    Publish document rejected event.

    Triggered when: Approval is rejected

    Subscribers: Notification service (notify owner)
    """
    await publish_document_event(
        eventbus,
        DocumentEvents.REJECTED,
        document_id=document_id,
        document_code=document_code,
        title=title,
        user_id=rejected_by,
        reason=reason,
        tenant_id=tenant_id
    )


async def publish_document_published(
    eventbus: EventBus,
    document_id: int,
    document_code: str,
    title: str,
    document_type: str,
    version: str,
    published_by: str,
    tenant_id: str,
    iso_clauses: Optional[list] = None
):
    """
    Publish document published event.

    Triggered when: Document is published (made available)

    Subscribers:
    - Governance (policy compliance)
    - Plans (plan readiness)
    - Validation (audit evidence)
    - Search indexer
    """
    await publish_document_event(
        eventbus,
        DocumentEvents.PUBLISHED,
        document_id=document_id,
        document_code=document_code,
        title=title,
        user_id=published_by,
        document_type=document_type,
        version=version,
        tenant_id=tenant_id,
        iso_clauses=iso_clauses or []
    )


async def publish_document_archived(
    eventbus: EventBus,
    document_id: int,
    document_code: str,
    title: str,
    archived_by: str,
    reason: str,
    tenant_id: str
):
    """
    Publish document archived event.

    Triggered when: Document is archived (retention workflow)

    Subscribers: Governance (compliance tracking), Audit trail
    """
    await publish_document_event(
        eventbus,
        DocumentEvents.ARCHIVED,
        document_id=document_id,
        document_code=document_code,
        title=title,
        user_id=archived_by,
        reason=reason,
        tenant_id=tenant_id
    )


async def publish_document_expired(
    eventbus: EventBus,
    document_id: int,
    document_code: str,
    title: str,
    expiration_date: str,
    retention_years: int,
    tenant_id: str
):
    """
    Publish document expired event.

    Triggered when: Document retention period expires

    Subscribers: Governance (review required), Notification service
    """
    await publish_document_event(
        eventbus,
        DocumentEvents.EXPIRED,
        document_id=document_id,
        document_code=document_code,
        title=title,
        user_id="system",
        expiration_date=expiration_date,
        retention_years=retention_years,
        tenant_id=tenant_id
    )


async def publish_document_shared(
    eventbus: EventBus,
    document_id: int,
    document_code: str,
    title: str,
    shared_by: str,
    shared_with: str,
    permission_level: str,
    tenant_id: str
):
    """
    Publish document shared event.

    Triggered when: Document is shared with another user

    Subscribers: Notification service (notify recipient)
    """
    await publish_document_event(
        eventbus,
        DocumentEvents.SHARED,
        document_id=document_id,
        document_code=document_code,
        title=title,
        user_id=shared_by,
        shared_with=shared_with,
        permission_level=permission_level,
        tenant_id=tenant_id
    )


async def publish_document_version_created(
    eventbus: EventBus,
    document_id: int,
    document_code: str,
    title: str,
    new_version: str,
    previous_version: str,
    created_by: str,
    tenant_id: str
):
    """
    Publish document version created event.

    Triggered when: New version of document is created

    Subscribers: Plans (if plan document), Notification service
    """
    await publish_document_event(
        eventbus,
        DocumentEvents.VERSION_CREATED,
        document_id=document_id,
        document_code=document_code,
        title=title,
        user_id=created_by,
        new_version=new_version,
        previous_version=previous_version,
        tenant_id=tenant_id
    )


# ============================================================================
# BATCH EVENTS
# ============================================================================

async def publish_batch_operation(
    eventbus: EventBus,
    operation: str,
    document_ids: list,
    performed_by: str,
    tenant_id: str,
    **extra_data
):
    """
    Publish batch operation event.

    Triggered when: Multiple documents are affected by single operation

    Operations: bulk_approve, bulk_archive, bulk_tag, bulk_export
    """
    data = {
        "operation": operation,
        "document_ids": document_ids,
        "document_count": len(document_ids),
        "user_id": performed_by,
        "tenant_id": tenant_id,
        **extra_data
    }

    await eventbus.publish(f"bcm.document.batch.{operation}", data)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def should_publish_event(document_type: str, event_type: str) -> bool:
    """
    Determine if event should be published for document type.

    Some document types might not need all events.
    """
    # Critical document types always publish all events
    critical_types = ["policy", "procedure", "plan", "bia", "risk_assessment"]

    if document_type in critical_types:
        return True

    # Other types skip some events
    skip_events = {
        "form": [DocumentEvents.APPROVED],  # Forms don't need approval events
        "template": [DocumentEvents.APPROVED],
    }

    return event_type not in skip_events.get(document_type, [])
