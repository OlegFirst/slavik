"""
Internal Audit API
ISO 22301:2019 Clause 9.2 - Internal Audit
Provides complete audit program management for ISO 22301 compliance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import logging

from compliance.database.connection import get_db
from compliance.models.database import (
    AuditProgramModel,
    AuditModel,
    AuditFindingModel,
    AuditStatus,
    FindingSeverity,
    FindingType
)
from compliance.models.schemas import (
    AuditProgramCreate,
    AuditProgramResponse,
    AuditCreate,
    AuditResponse,
    AuditChecklistResponse,
    AuditFindingCreate,
    AuditFindingResponse,
    AuditReportResponse
)
from compliance.standards.iso_22301 import ISO_22301_REQUIREMENTS
from compliance.workflows.audit_workflow import AuditWorkflow
from compliance.repositories.audit_repository import AuditRepository
from compliance.integrations.eventbus import EventBusService
from compliance.config.settings import settings
from sqlalchemy import select, and_, func

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency injection factories
def get_audit_repository(db: AsyncSession = Depends(get_db)) -> AuditRepository:
    """Get Audit repository with database session"""
    return AuditRepository(db)


async def get_audit_workflow(
    db: AsyncSession = Depends(get_db)
) -> AuditWorkflow:
    """Dependency to get audit workflow instance"""
    eventbus = None
    if settings.eventbus_url:
        eventbus = EventBusService(settings.eventbus_url)
    return AuditWorkflow(db, eventbus)


@router.post(
    "/programs",
    response_model=AuditProgramResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_audit_program(
    program_data: AuditProgramCreate,
    db: AsyncSession = Depends(get_db)
) -> AuditProgramResponse:
    """
    Create audit program

    ISO 22301 Clause 9.2 requires:
    - Planned intervals for audits
    - Defined audit scope and criteria
    - Audit schedule

    Args:
        program_data: Audit program details
        db: Database session

    Returns:
        Created audit program
    """
    try:
        program = AuditProgramModel(
            tenant_id=program_data.tenant_id,
            name=program_data.name,
            description=program_data.description,
            start_date=program_data.start_date,
            end_date=program_data.end_date,
            frequency=program_data.frequency,  # annual, semi-annual, quarterly
            scope=program_data.scope,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(program)
        await db.commit()
        await db.refresh(program)

        logger.info(f"Audit program created: {program.id} for tenant {program.tenant_id}")

        return AuditProgramResponse.model_validate(program)

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create audit program: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit program: {str(e)}"
        )


@router.get("/programs", response_model=List[AuditProgramResponse])
async def list_audit_programs(
    tenant_id: str,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
) -> List[AuditProgramResponse]:
    """
    List audit programs

    Args:
        tenant_id: Tenant identifier
        active_only: Only return active programs
        db: Database session

    Returns:
        List of audit programs
    """
    try:
        query = select(AuditProgramModel).where(
            AuditProgramModel.tenant_id == tenant_id
        )

        if active_only:
            today = date.today()
            query = query.where(
                and_(
                    AuditProgramModel.start_date <= today,
                    AuditProgramModel.end_date >= today
                )
            )

        query = query.order_by(AuditProgramModel.start_date.desc())

        result = await db.execute(query)
        programs = result.scalars().all()

        return [AuditProgramResponse.model_validate(p) for p in programs]

    except Exception as e:
        logger.error(f"Failed to list audit programs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list audit programs: {str(e)}"
        )


@router.post(
    "/programs/{program_id}/audits",
    response_model=AuditResponse,
    status_code=status.HTTP_201_CREATED
)
async def schedule_audit(
    program_id: str,
    audit_data: AuditCreate,
    workflow: AuditWorkflow = Depends(get_audit_workflow),
    db: AsyncSession = Depends(get_db)
) -> AuditResponse:
    """
    Schedule new audit within program

    ISO 22301 Clause 9.2 requires:
    - Defined audit scope
    - Audit criteria
    - Competent auditors
    - Objectivity and impartiality

    Args:
        program_id: Audit program identifier
        audit_data: Audit details
        workflow: Audit workflow instance
        db: Database session

    Returns:
        Created audit
    """
    try:
        # Verify program exists
        program_stmt = select(AuditProgramModel).where(
            and_(
                AuditProgramModel.id == program_id,
                AuditProgramModel.tenant_id == audit_data.tenant_id
            )
        )
        program_result = await db.execute(program_stmt)
        program = program_result.scalar_one_or_none()

        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit program {program_id} not found"
            )

        # Create audit via workflow
        audit = await workflow.create_audit(
            tenant_id=audit_data.tenant_id,
            program_id=program_id,
            name=audit_data.name,
            audit_type=audit_data.audit_type,
            scope=audit_data.scope,
            criteria=audit_data.criteria,
            scheduled_date=audit_data.scheduled_date,
            lead_auditor_id=audit_data.lead_auditor_id,
            auditor_ids=audit_data.auditor_ids
        )

        logger.info(f"Audit scheduled: {audit['id']} in program {program_id}")

        return AuditResponse(**audit)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule audit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule audit: {str(e)}"
        )


@router.get("/audits", response_model=List[AuditResponse])
async def list_audits(
    tenant_id: str,
    program_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    repository: AuditRepository = Depends(get_audit_repository)
) -> List[AuditResponse]:
    """
    List audits with filters

    Args:
        tenant_id: Tenant identifier
        program_id: Optional program filter
        status_filter: Optional status filter
        db: Database session

    Returns:
        List of audits
    """
    try:
        # Use repository to list audits
        audits = await repository.list_by_tenant(
            tenant_id=tenant_id,
            program_id=program_id,
            status=status_filter
        )

        return [AuditResponse.model_validate(a) for a in audits]

    except Exception as e:
        logger.error(f"Failed to list audits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list audits: {str(e)}"
        )


@router.get("/{audit_id}/checklist", response_model=AuditChecklistResponse)
async def get_audit_checklist(
    audit_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> AuditChecklistResponse:
    """
    Get ISO 22301 clause-by-clause audit checklist

    KILLER FEATURE: Pre-built checklist based on ISO 22301 requirements

    Args:
        audit_id: Audit identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Complete audit checklist with all ISO 22301 clauses
    """
    try:
        # Verify audit exists
        audit_stmt = select(AuditModel).where(
            and_(
                AuditModel.id == audit_id,
                AuditModel.tenant_id == tenant_id
            )
        )
        audit_result = await db.execute(audit_stmt)
        audit = audit_result.scalar_one_or_none()

        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit {audit_id} not found"
            )

        # Build clause-by-clause checklist
        checklist_items = []

        for req_id, requirement in ISO_22301_REQUIREMENTS.items():
            # Get existing findings for this clause
            findings_stmt = select(AuditFindingModel).where(
                and_(
                    AuditFindingModel.audit_id == audit_id,
                    AuditFindingModel.requirement_id == req_id
                )
            )
            findings_result = await db.execute(findings_stmt)
            findings = findings_result.scalars().all()

            checklist_items.append({
                "requirement_id": req_id,
                "title": requirement["title"],
                "category": requirement["category"],
                "description": requirement["description"],
                "audit_questions": requirement.get("audit_questions", []),
                "evidence_needed": requirement.get("evidence_types", []),
                "findings_count": len(findings),
                "has_nonconformity": any(
                    f.finding_type == FindingType.NONCONFORMITY.value
                    for f in findings
                ),
                "status": "audited" if findings else "pending"
            })

        return AuditChecklistResponse(
            audit_id=audit_id,
            audit_name=audit.name,
            checklist_items=checklist_items,
            total_clauses=len(checklist_items),
            audited_clauses=sum(1 for item in checklist_items if item["status"] == "audited"),
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit checklist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit checklist: {str(e)}"
        )


@router.post("/{audit_id}/findings", response_model=AuditFindingResponse)
async def create_audit_finding(
    audit_id: str,
    finding_data: AuditFindingCreate,
    workflow: AuditWorkflow = Depends(get_audit_workflow),
    db: AsyncSession = Depends(get_db)
) -> AuditFindingResponse:
    """
    Record audit finding

    ISO 22301 Clause 9.2 requires documentation of:
    - Conformities
    - Nonconformities
    - Observations
    - Opportunities for improvement

    Args:
        audit_id: Audit identifier
        finding_data: Finding details
        workflow: Audit workflow instance
        db: Database session

    Returns:
        Created finding
    """
    try:
        # Verify audit exists
        audit_stmt = select(AuditModel).where(
            and_(
                AuditModel.id == audit_id,
                AuditModel.tenant_id == finding_data.tenant_id
            )
        )
        audit_result = await db.execute(audit_stmt)
        audit = audit_result.scalar_one_or_none()

        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit {audit_id} not found"
            )

        # Create finding via workflow
        finding = await workflow.create_finding(
            audit_id=audit_id,
            tenant_id=finding_data.tenant_id,
            requirement_id=finding_data.requirement_id,
            finding_type=finding_data.finding_type,
            severity=finding_data.severity,
            description=finding_data.description,
            evidence=finding_data.evidence,
            recommendations=finding_data.recommendations,
            auditor_id=finding_data.auditor_id
        )

        logger.info(
            f"Audit finding created: {finding['id']} "
            f"(type={finding_data.finding_type}, severity={finding_data.severity})"
        )

        return AuditFindingResponse(**finding)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create audit finding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit finding: {str(e)}"
        )


@router.get("/{audit_id}/findings", response_model=List[AuditFindingResponse])
async def list_audit_findings(
    audit_id: str,
    tenant_id: str,
    finding_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> List[AuditFindingResponse]:
    """
    List findings for audit

    Args:
        audit_id: Audit identifier
        tenant_id: Tenant identifier
        finding_type: Optional filter by type
        db: Database session

    Returns:
        List of findings
    """
    try:
        query = select(AuditFindingModel).where(
            and_(
                AuditFindingModel.audit_id == audit_id,
                AuditFindingModel.tenant_id == tenant_id
            )
        )

        if finding_type:
            query = query.where(AuditFindingModel.finding_type == finding_type)

        query = query.order_by(
            AuditFindingModel.severity.desc(),
            AuditFindingModel.created_at.desc()
        )

        result = await db.execute(query)
        findings = result.scalars().all()

        return [AuditFindingResponse.model_validate(f) for f in findings]

    except Exception as e:
        logger.error(f"Failed to list audit findings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list audit findings: {str(e)}"
        )


@router.post("/{audit_id}/start", response_model=AuditResponse)
async def start_audit(
    audit_id: str,
    tenant_id: str,
    workflow: AuditWorkflow = Depends(get_audit_workflow),
    db: AsyncSession = Depends(get_db)
) -> AuditResponse:
    """
    Start audit execution

    Workflow transition: PLANNED → IN_PROGRESS

    Args:
        audit_id: Audit identifier
        tenant_id: Tenant identifier
        workflow: Audit workflow instance
        db: Database session

    Returns:
        Updated audit
    """
    try:
        audit = await workflow.start_audit(audit_id, tenant_id)
        logger.info(f"Audit {audit_id} started")
        return AuditResponse(**audit)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to start audit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start audit: {str(e)}"
        )


@router.post("/{audit_id}/complete", response_model=AuditResponse)
async def complete_audit(
    audit_id: str,
    tenant_id: str,
    workflow: AuditWorkflow = Depends(get_audit_workflow),
    db: AsyncSession = Depends(get_db)
) -> AuditResponse:
    """
    Complete audit

    Workflow transition: IN_PROGRESS → COMPLETED

    Args:
        audit_id: Audit identifier
        tenant_id: Tenant identifier
        workflow: Audit workflow instance
        db: Database session

    Returns:
        Completed audit
    """
    try:
        audit = await workflow.complete_audit(audit_id, tenant_id)
        logger.info(f"Audit {audit_id} completed")
        return AuditResponse(**audit)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to complete audit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete audit: {str(e)}"
        )


@router.get("/{audit_id}/report", response_model=AuditReportResponse)
async def generate_audit_report(
    audit_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> AuditReportResponse:
    """
    Generate audit report

    ISO 22301 Clause 9.2 requires:
    - Report audit results to relevant management
    - Retain documented information as evidence

    Args:
        audit_id: Audit identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Complete audit report
    """
    try:
        # Get audit
        audit_stmt = select(AuditModel).where(
            and_(
                AuditModel.id == audit_id,
                AuditModel.tenant_id == tenant_id
            )
        )
        audit_result = await db.execute(audit_stmt)
        audit = audit_result.scalar_one_or_none()

        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit {audit_id} not found"
            )

        if audit.status != AuditStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audit must be completed to generate report (status: {audit.status})"
            )

        # Get all findings
        findings_stmt = select(AuditFindingModel).where(
            AuditFindingModel.audit_id == audit_id
        )
        findings_result = await db.execute(findings_stmt)
        findings = findings_result.scalars().all()

        # Aggregate findings by type
        findings_summary = {
            "conformities": sum(1 for f in findings if f.finding_type == FindingType.CONFORMITY.value),
            "nonconformities": sum(1 for f in findings if f.finding_type == FindingType.NONCONFORMITY.value),
            "observations": sum(1 for f in findings if f.finding_type == FindingType.OBSERVATION.value),
            "opportunities": sum(1 for f in findings if f.finding_type == FindingType.OPPORTUNITY.value)
        }

        # Severity breakdown (for NCs)
        severity_summary = {
            "critical": sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL.value),
            "major": sum(1 for f in findings if f.severity == FindingSeverity.MAJOR.value),
            "minor": sum(1 for f in findings if f.severity == FindingSeverity.MINOR.value)
        }

        # Clause coverage
        audited_clauses = len(set(f.requirement_id for f in findings))
        total_clauses = len(ISO_22301_REQUIREMENTS)
        coverage_percentage = (audited_clauses / total_clauses * 100) if total_clauses > 0 else 0

        return AuditReportResponse(
            audit=AuditResponse.model_validate(audit),
            findings=[AuditFindingResponse.model_validate(f) for f in findings],
            summary={
                "total_findings": len(findings),
                "findings_by_type": findings_summary,
                "severity_breakdown": severity_summary,
                "clause_coverage": {
                    "audited": audited_clauses,
                    "total": total_clauses,
                    "percentage": round(coverage_percentage, 1)
                }
            },
            generated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate audit report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate audit report: {str(e)}"
        )
