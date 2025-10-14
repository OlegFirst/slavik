"""
Plans Module Integration
Links documents to business continuity plans

Integration scenarios:
1. Get all documents for a plan
2. Create plan template documents
3. Check plan document completeness
4. Link document to plan
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from database.models import Document, DocumentType


# ============================================================================
# PLAN DOCUMENT QUERIES
# ============================================================================

async def get_plan_documents(
    plan_id: int,
    tenant_id: str,
    db: AsyncSession
) -> List[Document]:
    """
    Get all documents linked to a plan.

    Finds documents where custom_metadata contains plan_id.

    Args:
        plan_id: Plan ID
        tenant_id: Tenant ID
        db: Database session

    Returns:
        List of documents
    """
    # Query documents with plan_id in custom_metadata
    # Note: This uses JSONB contains operator in PostgreSQL
    query = select(Document).where(
        and_(
            Document.tenant_id == tenant_id,
            Document.is_latest == True,
            Document.custom_metadata.op('?')('plan_id')  # Has plan_id key
        )
    )

    result = await db.execute(query)
    documents = result.scalars().all()

    # Filter by plan_id value (additional Python filter)
    plan_docs = [
        doc for doc in documents
        if doc.custom_metadata.get('plan_id') == plan_id
    ]

    return plan_docs


async def get_plan_documents_by_code(
    plan_code: str,
    tenant_id: str,
    db: AsyncSession
) -> List[Document]:
    """
    Get all documents linked to a plan by plan code.

    Args:
        plan_code: Plan code (e.g., "PLAN-001")
        tenant_id: Tenant ID
        db: Database session

    Returns:
        List of documents
    """
    # Search documents with plan_code in title or custom_metadata
    query = select(Document).where(
        and_(
            Document.tenant_id == tenant_id,
            Document.is_latest == True,
            or_(
                Document.title.ilike(f'%{plan_code}%'),
                Document.description.ilike(f'%{plan_code}%')
            )
        )
    )

    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# PLAN DOCUMENT TEMPLATES
# ============================================================================

PLAN_TEMPLATE_DOCUMENTS = {
    "business_continuity": [
        {
            "title": "{plan_name} - Business Continuity Plan",
            "document_type": DocumentType.PLAN,
            "description": "Main business continuity plan document",
            "required": True
        },
        {
            "title": "{plan_name} - Response Procedures",
            "document_type": DocumentType.PROCEDURE,
            "description": "Step-by-step response procedures",
            "required": True
        },
        {
            "title": "{plan_name} - Recovery Procedures",
            "document_type": DocumentType.PROCEDURE,
            "description": "Recovery and restoration procedures",
            "required": True
        },
        {
            "title": "{plan_name} - Contact List",
            "document_type": DocumentType.CONTACT_LIST,
            "description": "Emergency contact information",
            "required": True
        },
        {
            "title": "{plan_name} - Communication Templates",
            "document_type": DocumentType.COMMUNICATION,
            "description": "Pre-approved communication templates",
            "required": True
        },
        {
            "title": "{plan_name} - Resource Lists",
            "document_type": DocumentType.CHECKLIST,
            "description": "Critical resources and dependencies",
            "required": False
        },
    ],
    "disaster_recovery": [
        {
            "title": "{plan_name} - Disaster Recovery Plan",
            "document_type": DocumentType.PLAN,
            "description": "Main disaster recovery plan",
            "required": True
        },
        {
            "title": "{plan_name} - IT Recovery Procedures",
            "document_type": DocumentType.PROCEDURE,
            "description": "IT system recovery procedures",
            "required": True
        },
        {
            "title": "{plan_name} - Data Backup Procedures",
            "document_type": DocumentType.PROCEDURE,
            "description": "Backup and restore procedures",
            "required": True
        },
    ],
    "incident_response": [
        {
            "title": "{plan_name} - Incident Response Plan",
            "document_type": DocumentType.PLAN,
            "description": "Incident response procedures",
            "required": True
        },
        {
            "title": "{plan_name} - Incident Classification",
            "document_type": DocumentType.CHECKLIST,
            "description": "Incident severity classification guide",
            "required": True
        },
    ],
    "crisis_management": [
        {
            "title": "{plan_name} - Crisis Management Plan",
            "document_type": DocumentType.PLAN,
            "description": "Crisis management framework",
            "required": True
        },
        {
            "title": "{plan_name} - Crisis Communication Plan",
            "document_type": DocumentType.COMMUNICATION,
            "description": "Crisis communication strategy",
            "required": True
        },
    ],
}


def get_plan_template_documents(plan_type: str) -> List[Dict[str, Any]]:
    """
    Get template documents for plan type.

    Args:
        plan_type: Plan type (business_continuity, disaster_recovery, etc.)

    Returns:
        List of template document definitions
    """
    return PLAN_TEMPLATE_DOCUMENTS.get(
        plan_type,
        PLAN_TEMPLATE_DOCUMENTS["business_continuity"]  # Default
    )


# ============================================================================
# PLAN DOCUMENT COMPLETENESS
# ============================================================================

async def check_plan_document_completeness(
    plan_id: int,
    plan_type: str,
    tenant_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Check if plan has all required documents.

    Args:
        plan_id: Plan ID
        plan_type: Plan type
        tenant_id: Tenant ID
        db: Database session

    Returns:
        Completeness report with missing documents
    """
    # Get required documents for plan type
    required_templates = get_plan_template_documents(plan_type)
    required_docs = [t for t in required_templates if t.get("required", True)]

    # Get existing documents for plan
    existing_docs = await get_plan_documents(plan_id, tenant_id, db)

    # Check which required documents exist
    existing_types = {doc.document_type for doc in existing_docs}

    missing_documents = []
    for template in required_docs:
        if template["document_type"] not in existing_types:
            missing_documents.append({
                "title": template["title"].replace("{plan_name}", "Plan"),
                "document_type": template["document_type"].value,
                "description": template["description"]
            })

    return {
        "plan_id": plan_id,
        "plan_type": plan_type,
        "total_required": len(required_docs),
        "total_existing": len(existing_docs),
        "is_complete": len(missing_documents) == 0,
        "completeness_percent": int((len(existing_docs) / len(required_docs)) * 100) if required_docs else 100,
        "missing_documents": missing_documents,
        "existing_documents": [
            {
                "document_id": doc.document_id,
                "document_code": doc.document_code,
                "title": doc.title,
                "document_type": doc.document_type.value,
                "status": doc.status.value
            }
            for doc in existing_docs
        ]
    }


# ============================================================================
# PLAN DOCUMENT LINKING
# ============================================================================

async def link_document_to_plan(
    document_id: int,
    plan_id: int,
    plan_code: str,
    db: AsyncSession
) -> bool:
    """
    Link existing document to a plan.

    Updates document.custom_metadata to include plan reference.

    Args:
        document_id: Document ID
        plan_id: Plan ID
        plan_code: Plan code
        db: Database session

    Returns:
        True if successful
    """
    # Get document
    result = await db.execute(
        select(Document).where(Document.document_id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        return False

    # Update custom_metadata
    if document.custom_metadata is None:
        document.custom_metadata = {}

    document.custom_metadata.update({
        "linked_to": "plan",
        "plan_id": plan_id,
        "plan_code": plan_code
    })

    await db.commit()
    return True


async def unlink_document_from_plan(
    document_id: int,
    db: AsyncSession
) -> bool:
    """
    Unlink document from plan.

    Args:
        document_id: Document ID
        db: Database session

    Returns:
        True if successful
    """
    # Get document
    result = await db.execute(
        select(Document).where(Document.document_id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        return False

    # Remove plan reference from custom_metadata
    if document.custom_metadata:
        document.custom_metadata.pop("linked_to", None)
        document.custom_metadata.pop("plan_id", None)
        document.custom_metadata.pop("plan_code", None)

    await db.commit()
    return True


# ============================================================================
# PLAN DOCUMENT STATUS
# ============================================================================

async def get_plan_document_status(
    plan_id: int,
    tenant_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Get status summary of all plan documents.

    Args:
        plan_id: Plan ID
        tenant_id: Tenant ID
        db: Database session

    Returns:
        Status summary
    """
    documents = await get_plan_documents(plan_id, tenant_id, db)

    # Group by status
    status_counts = {}
    for doc in documents:
        status = doc.status.value
        status_counts[status] = status_counts.get(status, 0) + 1

    # Check readiness (all documents should be published)
    published_count = status_counts.get("published", 0)
    total_count = len(documents)

    is_ready = (
        total_count > 0 and
        published_count == total_count and
        total_count >= 3  # Minimum required documents
    )

    return {
        "plan_id": plan_id,
        "total_documents": total_count,
        "status_breakdown": status_counts,
        "is_ready": is_ready,
        "readiness_percent": int((published_count / total_count) * 100) if total_count > 0 else 0,
        "documents": [
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "document_type": doc.document_type.value,
                "status": doc.status.value,
                "version": doc.version
            }
            for doc in documents
        ]
    }
