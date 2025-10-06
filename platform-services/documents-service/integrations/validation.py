"""
Validation Module Integration
Links documents to exercises, audits, and reviews

Integration scenarios:
1. Create exercise report from exercise data
2. Get audit evidence documents
3. Link documents to audit findings
4. Track management review documentation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from database.models import Document, DocumentType, DocumentStatus


# ============================================================================
# EXERCISE REPORT CREATION
# ============================================================================

async def create_exercise_report_document(
    exercise_id: int,
    exercise_code: str,
    exercise_name: str,
    exercise_type: str,
    exercise_date: datetime,
    observations: List[str],
    lessons_learned: List[str],
    action_items: List[str],
    participants: List[Dict[str, str]],
    tenant_id: str,
    created_by: str,
    db: AsyncSession
) -> Document:
    """
    Create exercise report document from exercise data.

    Args:
        exercise_id: Exercise ID
        exercise_code: Exercise code
        exercise_name: Exercise name
        exercise_type: tabletop, walkthrough, simulation, full_scale
        exercise_date: When exercise was conducted
        observations: List of observations
        lessons_learned: List of lessons learned
        action_items: List of action items
        participants: List of participants
        tenant_id: Tenant ID
        created_by: User creating report
        db: Database session

    Returns:
        Created document
    """
    # Generate report content
    description = f"""
Exercise Report: {exercise_name}
Type: {exercise_type}
Date: {exercise_date.strftime('%Y-%m-%d')}
Code: {exercise_code}

OBSERVATIONS:
{chr(10).join('• ' + obs for obs in observations)}

LESSONS LEARNED:
{chr(10).join('• ' + lesson for lesson in lessons_learned)}

ACTION ITEMS:
{chr(10).join('• ' + action for action in action_items)}

PARTICIPANTS:
{chr(10).join('• ' + p.get('name', 'Unknown') + ' (' + p.get('role', 'Unknown') + ')' for p in participants)}
    """.strip()

    # Create document
    document = Document(
        tenant_id=tenant_id,
        document_code=f"EXR-{exercise_code}-{datetime.utcnow().strftime('%Y%m%d')}",
        title=f"Exercise Report - {exercise_name}",
        description=description,
        document_type=DocumentType.EXERCISE_REPORT,
        classification="internal",
        is_controlled=True,
        requires_approval=True,
        owner_id=created_by,
        created_by=created_by,
        status=DocumentStatus.DRAFT,
        version="1.0",
        is_latest=True,
        file_name="",
        file_path="",
        custom_metadata={
            "linked_to": "exercise",
            "exercise_id": exercise_id,
            "exercise_code": exercise_code,
            "exercise_type": exercise_type,
            "exercise_date": exercise_date.isoformat(),
            "auto_created": True,
            "observations_count": len(observations),
            "lessons_learned_count": len(lessons_learned),
            "action_items_count": len(action_items),
            "participants_count": len(participants)
        },
        iso_clauses=["8.5"],  # ISO 22301 Clause 8.5 - Exercising and testing
        bci_practices=["PP6"]  # BCI GPG PP6 - Validation
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


async def get_exercise_reports(
    exercise_id: Optional[int] = None,
    tenant_id: Optional[str] = None,
    db: AsyncSession = None
) -> List[Document]:
    """Get all exercise reports, optionally filtered by exercise"""
    query = select(Document).where(
        Document.document_type == DocumentType.EXERCISE_REPORT
    )

    if tenant_id:
        query = query.where(Document.tenant_id == tenant_id)

    result = await db.execute(query)
    documents = result.scalars().all()

    if exercise_id:
        # Filter by exercise_id in custom_metadata
        documents = [
            doc for doc in documents
            if doc.custom_metadata and doc.custom_metadata.get('exercise_id') == exercise_id
        ]

    return documents


# ============================================================================
# AUDIT EVIDENCE MANAGEMENT
# ============================================================================

async def get_audit_evidence_documents(
    audit_id: int,
    tenant_id: str,
    iso_clauses: Optional[List[str]] = None,
    db: AsyncSession = None
) -> List[Document]:
    """
    Get documents that serve as audit evidence.

    Args:
        audit_id: Audit ID
        tenant_id: Tenant ID
        iso_clauses: Optional list of ISO clauses to filter
        db: Database session

    Returns:
        List of evidence documents
    """
    query = select(Document).where(
        and_(
            Document.tenant_id == tenant_id,
            Document.status == DocumentStatus.PUBLISHED,
            Document.is_latest == True
        )
    )

    result = await db.execute(query)
    documents = result.scalars().all()

    # Filter by ISO clauses if provided
    if iso_clauses:
        documents = [
            doc for doc in documents
            if doc.iso_clauses and any(clause in doc.iso_clauses for clause in iso_clauses)
        ]

    return documents


async def link_document_to_audit(
    document_id: int,
    audit_id: int,
    audit_code: str,
    finding_id: Optional[int] = None,
    db: AsyncSession = None
) -> bool:
    """
    Link document to audit as evidence.

    Args:
        document_id: Document ID
        audit_id: Audit ID
        audit_code: Audit code
        finding_id: Optional finding ID
        db: Database session

    Returns:
        True if successful
    """
    result = await db.execute(
        select(Document).where(Document.document_id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        return False

    if document.custom_metadata is None:
        document.custom_metadata = {}

    document.custom_metadata.update({
        "linked_to_audit": audit_id,
        "audit_code": audit_code,
        "finding_id": finding_id
    })

    await db.commit()
    return True


async def create_audit_report_document(
    audit_id: int,
    audit_code: str,
    audit_name: str,
    audit_date: datetime,
    audit_scope: str,
    findings: List[Dict[str, Any]],
    tenant_id: str,
    created_by: str,
    db: AsyncSession
) -> Document:
    """Create audit report document"""
    description = f"""
Audit Report: {audit_name}
Date: {audit_date.strftime('%Y-%m-%d')}
Code: {audit_code}
Scope: {audit_scope}

FINDINGS:
{chr(10).join('• [' + f.get('severity', 'INFO') + '] ' + f.get('description', '') for f in findings)}

TOTAL FINDINGS: {len(findings)}
CRITICAL: {len([f for f in findings if f.get('severity') == 'CRITICAL'])}
MAJOR: {len([f for f in findings if f.get('severity') == 'MAJOR'])}
MINOR: {len([f for f in findings if f.get('severity') == 'MINOR'])}
    """.strip()

    document = Document(
        tenant_id=tenant_id,
        document_code=f"AUD-{audit_code}-{datetime.utcnow().strftime('%Y%m%d')}",
        title=f"Audit Report - {audit_name}",
        description=description,
        document_type=DocumentType.AUDIT_REPORT,
        classification="confidential",
        is_controlled=True,
        requires_approval=True,
        owner_id=created_by,
        created_by=created_by,
        status=DocumentStatus.DRAFT,
        version="1.0",
        is_latest=True,
        file_name="",
        file_path="",
        custom_metadata={
            "linked_to": "audit",
            "audit_id": audit_id,
            "audit_code": audit_code,
            "audit_date": audit_date.isoformat(),
            "findings_count": len(findings),
            "auto_created": True
        },
        iso_clauses=["9.2"],  # ISO 22301 Clause 9.2 - Internal audit
        bci_practices=["PP6"]
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


# ============================================================================
# MANAGEMENT REVIEW DOCUMENTATION
# ============================================================================

async def create_management_review_document(
    review_id: int,
    review_code: str,
    review_date: datetime,
    review_inputs: Dict[str, Any],
    review_decisions: List[Dict[str, Any]],
    tenant_id: str,
    created_by: str,
    db: AsyncSession
) -> Document:
    """Create management review document"""
    description = f"""
Management Review
Date: {review_date.strftime('%Y-%m-%d')}
Code: {review_code}

REVIEW INPUTS:
• BCMS Performance: {review_inputs.get('performance', 'N/A')}
• Audit Results: {review_inputs.get('audit_results', 'N/A')}
• Exercise Results: {review_inputs.get('exercise_results', 'N/A')}
• Changes: {review_inputs.get('changes', 'N/A')}

DECISIONS:
{chr(10).join('• ' + d.get('decision', '') for d in review_decisions)}
    """.strip()

    document = Document(
        tenant_id=tenant_id,
        document_code=f"MGR-{review_code}-{datetime.utcnow().strftime('%Y%m%d')}",
        title=f"Management Review - {review_date.strftime('%Y-%m')}",
        description=description,
        document_type=DocumentType.MANAGEMENT_REVIEW,
        classification="confidential",
        is_controlled=True,
        requires_approval=False,  # Already approved by management
        owner_id=created_by,
        created_by=created_by,
        status=DocumentStatus.APPROVED,
        version="1.0",
        is_latest=True,
        file_name="",
        file_path="",
        custom_metadata={
            "linked_to": "management_review",
            "review_id": review_id,
            "review_code": review_code,
            "review_date": review_date.isoformat(),
            "auto_created": True
        },
        iso_clauses=["9.3"],  # ISO 22301 Clause 9.3 - Management review
        bci_practices=["PP1", "PP6"]
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


async def get_validation_documents_summary(
    tenant_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Get summary of validation documents (exercises, audits, reviews).

    Returns counts and latest documents.
    """
    # Get all validation-related documents
    query = select(Document).where(
        and_(
            Document.tenant_id == tenant_id,
            Document.document_type.in_([
                DocumentType.EXERCISE_REPORT,
                DocumentType.AUDIT_REPORT,
                DocumentType.MANAGEMENT_REVIEW
            ]),
            Document.is_latest == True
        )
    )

    result = await db.execute(query)
    documents = result.scalars().all()

    # Group by type
    by_type = {
        "exercise_reports": [],
        "audit_reports": [],
        "management_reviews": []
    }

    for doc in documents:
        if doc.document_type == DocumentType.EXERCISE_REPORT:
            by_type["exercise_reports"].append(doc)
        elif doc.document_type == DocumentType.AUDIT_REPORT:
            by_type["audit_reports"].append(doc)
        elif doc.document_type == DocumentType.MANAGEMENT_REVIEW:
            by_type["management_reviews"].append(doc)

    return {
        "total_validation_documents": len(documents),
        "exercise_reports_count": len(by_type["exercise_reports"]),
        "audit_reports_count": len(by_type["audit_reports"]),
        "management_reviews_count": len(by_type["management_reviews"]),
        "latest_exercise": by_type["exercise_reports"][0] if by_type["exercise_reports"] else None,
        "latest_audit": by_type["audit_reports"][0] if by_type["audit_reports"] else None,
        "latest_review": by_type["management_reviews"][0] if by_type["management_reviews"] else None,
    }
