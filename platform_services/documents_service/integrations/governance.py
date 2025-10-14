"""
Governance Module Integration
Links documents to policies and governance framework

Integration scenarios:
1. Get all documents for a policy
2. Check policy documentation requirements
3. Link document to policy
4. Track policy compliance documentation
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_

from database.models import Document, DocumentType, DocumentStatus


# ============================================================================
# POLICY DOCUMENT QUERIES
# ============================================================================

async def get_policy_documents(
    policy_id: int,
    tenant_id: str,
    db: AsyncSession
) -> List[Document]:
    """
    Get all documents linked to a policy.

    Args:
        policy_id: Policy ID
        tenant_id: Tenant ID
        db: Database session

    Returns:
        List of documents
    """
    query = select(Document).where(
        and_(
            Document.tenant_id == tenant_id,
            Document.is_latest == True
        )
    )

    result = await db.execute(query)
    documents = result.scalars().all()

    # Filter by policy_id in custom_metadata
    policy_docs = [
        doc for doc in documents
        if doc.custom_metadata and doc.custom_metadata.get('policy_id') == policy_id
    ]

    return policy_docs


async def get_policy_document_by_code(
    policy_code: str,
    tenant_id: str,
    db: AsyncSession
) -> Optional[Document]:
    """
    Get the policy document itself by code.

    Args:
        policy_code: Policy code
        tenant_id: Tenant ID
        db: Database session

    Returns:
        Policy document or None
    """
    query = select(Document).where(
        and_(
            Document.tenant_id == tenant_id,
            Document.document_type == DocumentType.POLICY,
            Document.document_code == policy_code,
            Document.is_latest == True
        )
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


# ============================================================================
# POLICY DOCUMENTATION REQUIREMENTS
# ============================================================================

POLICY_REQUIRED_DOCUMENTS = {
    "business_continuity_policy": [
        {
            "title": "Business Continuity Policy Statement",
            "document_type": DocumentType.POLICY,
            "description": "Official BC policy approved by top management",
            "iso_clause": "5.2"
        },
        {
            "title": "BC Policy Implementation Procedure",
            "document_type": DocumentType.PROCEDURE,
            "description": "How BC policy is implemented",
            "iso_clause": "5.2"
        },
        {
            "title": "BC Policy Review Schedule",
            "document_type": DocumentType.CHECKLIST,
            "description": "Policy review and update schedule",
            "iso_clause": "9.3"
        },
    ],
    "information_security_policy": [
        {
            "title": "Information Security Policy",
            "document_type": DocumentType.POLICY,
            "description": "Information security policy statement",
            "iso_clause": "7.5"
        },
        {
            "title": "Access Control Procedure",
            "document_type": DocumentType.PROCEDURE,
            "description": "Document access control procedures",
            "iso_clause": "7.5.3"
        },
    ],
    "risk_management_policy": [
        {
            "title": "Risk Management Policy",
            "document_type": DocumentType.POLICY,
            "description": "Risk management framework policy",
            "iso_clause": "6.1"
        },
        {
            "title": "Risk Assessment Methodology",
            "document_type": DocumentType.PROCEDURE,
            "description": "How risks are assessed",
            "iso_clause": "8.2.3"
        },
    ],
}


def get_policy_documentation_requirements(policy_type: str) -> List[Dict[str, Any]]:
    """Get required documents for policy type"""
    return POLICY_REQUIRED_DOCUMENTS.get(policy_type, [])


# ============================================================================
# POLICY COMPLIANCE TRACKING
# ============================================================================

async def check_policy_compliance_documentation(
    policy_id: int,
    policy_type: str,
    tenant_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Check if policy has all required compliance documentation.

    Args:
        policy_id: Policy ID
        policy_type: Policy type
        tenant_id: Tenant ID
        db: AsyncSession: Database session

    Returns:
        Compliance report
    """
    # Get required documents
    required_docs = get_policy_documentation_requirements(policy_type)

    # Get existing documents
    existing_docs = await get_policy_documents(policy_id, tenant_id, db)

    # Check which required documents exist
    existing_types = {doc.document_type for doc in existing_docs}

    missing_documents = []
    for req_doc in required_docs:
        if req_doc["document_type"] not in existing_types:
            missing_documents.append(req_doc)

    # Check if policy document itself is published
    policy_doc = next(
        (doc for doc in existing_docs if doc.document_type == DocumentType.POLICY),
        None
    )

    is_compliant = (
        len(missing_documents) == 0 and
        policy_doc is not None and
        policy_doc.status == DocumentStatus.PUBLISHED
    )

    return {
        "policy_id": policy_id,
        "policy_type": policy_type,
        "is_compliant": is_compliant,
        "total_required": len(required_docs),
        "total_existing": len(existing_docs),
        "missing_documents": missing_documents,
        "policy_status": policy_doc.status.value if policy_doc else "not_found",
        "existing_documents": [
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "document_type": doc.document_type.value,
                "status": doc.status.value,
                "iso_clauses": doc.iso_clauses
            }
            for doc in existing_docs
        ]
    }


# ============================================================================
# POLICY DOCUMENT LINKING
# ============================================================================

async def link_document_to_policy(
    document_id: int,
    policy_id: int,
    policy_code: str,
    db: AsyncSession
) -> bool:
    """Link document to policy"""
    result = await db.execute(
        select(Document).where(Document.document_id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        return False

    if document.custom_metadata is None:
        document.custom_metadata = {}

    document.custom_metadata.update({
        "linked_to": "policy",
        "policy_id": policy_id,
        "policy_code": policy_code
    })

    await db.commit()
    return True


# ============================================================================
# ISO CLAUSE COVERAGE
# ============================================================================

async def get_iso_clause_coverage(
    tenant_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Get ISO 22301 clause coverage by documents.

    Returns which clauses are covered by documents.
    """
    # Get all published documents
    query = select(Document).where(
        and_(
            Document.tenant_id == tenant_id,
            Document.status == DocumentStatus.PUBLISHED,
            Document.is_latest == True
        )
    )

    result = await db.execute(query)
    documents = result.scalars().all()

    # Collect all ISO clauses covered
    clause_coverage = {}

    for doc in documents:
        if doc.iso_clauses:
            for clause in doc.iso_clauses:
                if clause not in clause_coverage:
                    clause_coverage[clause] = []

                clause_coverage[clause].append({
                    "document_id": doc.document_id,
                    "document_code": doc.document_code,
                    "title": doc.title,
                    "document_type": doc.document_type.value
                })

    # ISO 22301 all clauses
    all_clauses = [
        "4.1", "4.2", "4.3", "4.4",
        "5.1", "5.2", "5.3",
        "6.1", "6.2", "6.3",
        "7.1", "7.2", "7.3", "7.4", "7.5",
        "8.1", "8.2", "8.3", "8.4", "8.5",
        "9.1", "9.2", "9.3",
        "10.1", "10.2"
    ]

    # Find gaps
    covered_clauses = list(clause_coverage.keys())
    missing_clauses = [c for c in all_clauses if c not in covered_clauses]

    return {
        "total_clauses": len(all_clauses),
        "covered_clauses": len(covered_clauses),
        "coverage_percent": int((len(covered_clauses) / len(all_clauses)) * 100),
        "missing_clauses": missing_clauses,
        "clause_coverage": clause_coverage
    }
