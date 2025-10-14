"""
Gaps API
Provides endpoints for gap management and remediation tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import logging

from compliance.database.connection import get_db
from compliance.models.schemas import (
    GapResponse,
    GapUpdate,
    GapRemediationUpdate,
    RootCauseAnalysisCreate,
    RootCauseAnalysisResponse,
    EffectivenessReviewCreate,
    EffectivenessReviewResponse
)
from compliance.models.database import GapModel, GapStatus, GapSeverity
from compliance.workflows.gap_workflow import GapWorkflow
from compliance.repositories.gap_repository import GapRepository
from compliance.integrations.eventbus import EventBusService
from compliance.config.settings import settings
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency injection factories
def get_gap_repository(db: AsyncSession = Depends(get_db)) -> GapRepository:
    """Get Gap repository with database session"""
    return GapRepository(db)


async def get_gap_workflow(
    db: AsyncSession = Depends(get_db)
) -> GapWorkflow:
    """Dependency to get gap workflow instance"""
    eventbus = None
    if settings.eventbus_url:
        eventbus = EventBusService(settings.eventbus_url)
    return GapWorkflow(db, eventbus)


@router.get("/", response_model=List[GapResponse])
async def list_gaps(
    tenant_id: str,
    assessment_id: Optional[str] = None,
    requirement_id: Optional[str] = None,
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    repository: GapRepository = Depends(get_gap_repository)
) -> List[GapResponse]:
    """
    List gaps with optional filters

    Args:
        tenant_id: Tenant identifier
        assessment_id: Optional assessment filter
        requirement_id: Optional requirement filter
        severity: Optional severity filter (critical, high, medium, low)
        status_filter: Optional status filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of gaps ordered by severity
    """
    try:
        # Use repository to list gaps
        gaps = await repository.list_by_tenant(
            tenant_id=tenant_id,
            assessment_id=assessment_id,
            requirement_id=requirement_id,
            severity=severity,
            status=status_filter,
            skip=skip,
            limit=limit
        )

        return [GapResponse.model_validate(g) for g in gaps]

    except Exception as e:
        logger.error(f"Failed to list gaps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list gaps: {str(e)}"
        )


@router.get("/{gap_id}", response_model=GapResponse)
async def get_gap(
    gap_id: str,
    tenant_id: str,
    repository: GapRepository = Depends(get_gap_repository)
) -> GapResponse:
    """
    Get gap by ID

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Gap details
    """
    try:
        gap = await repository.get_by_id(gap_id, tenant_id)

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        return GapResponse.model_validate(gap)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get gap: {str(e)}"
        )


@router.patch("/{gap_id}", response_model=GapResponse)
async def update_gap(
    gap_id: str,
    tenant_id: str,
    update_data: GapUpdate,
    repository: GapRepository = Depends(get_gap_repository)
) -> GapResponse:
    """
    Update gap metadata

    Note: Status changes should use workflow transitions

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        update_data: Fields to update
        db: Database session

    Returns:
        Updated gap
    """
    try:
        # Update fields via repository
        update_dict = update_data.model_dump(exclude_unset=True)

        gap = await repository.update(gap_id, tenant_id, update_dict)

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        logger.info(f"Gap {gap_id} updated")

        return GapResponse.model_validate(gap)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update gap: {str(e)}"
        )


@router.post("/{gap_id}/start-remediation", response_model=GapResponse)
async def start_remediation(
    gap_id: str,
    tenant_id: str,
    remediation_data: GapRemediationUpdate,
    workflow: GapWorkflow = Depends(get_gap_workflow),
    db: AsyncSession = Depends(get_db)
) -> GapResponse:
    """
    Start gap remediation

    Workflow transition: OPEN → IN_PROGRESS

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        remediation_data: Remediation plan details
        workflow: Gap workflow instance
        db: Database session

    Returns:
        Gap with remediation started
    """
    try:
        # Get gap
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        # Start remediation via workflow
        updated_gap = await workflow.start_remediation(
            gap_id=gap_id,
            tenant_id=tenant_id,
            assignee_id=remediation_data.assignee_id,
            remediation_plan=remediation_data.remediation_plan,
            target_date=remediation_data.target_date
        )

        logger.info(f"Remediation started for gap {gap_id}")

        return GapResponse(**updated_gap)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start remediation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start remediation: {str(e)}"
        )


@router.post("/{gap_id}/update-progress", response_model=GapResponse)
async def update_remediation_progress(
    gap_id: str,
    tenant_id: str,
    progress: int,
    notes: Optional[str] = None,
    workflow: GapWorkflow = Depends(get_gap_workflow),
    db: AsyncSession = Depends(get_db)
) -> GapResponse:
    """
    Update remediation progress

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        progress: Progress percentage (0-100)
        notes: Optional progress notes
        workflow: Gap workflow instance
        db: Database session

    Returns:
        Gap with updated progress
    """
    try:
        if not 0 <= progress <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Progress must be between 0 and 100"
            )

        # Get gap
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        # Update progress via workflow
        updated_gap = await workflow.update_progress(
            gap_id=gap_id,
            tenant_id=tenant_id,
            progress=progress,
            notes=notes
        )

        logger.info(f"Gap {gap_id} progress updated: {progress}%")

        return GapResponse(**updated_gap)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        )


@router.post("/{gap_id}/resolve", response_model=GapResponse)
async def resolve_gap(
    gap_id: str,
    tenant_id: str,
    resolution_notes: Optional[str] = None,
    workflow: GapWorkflow = Depends(get_gap_workflow),
    db: AsyncSession = Depends(get_db)
) -> GapResponse:
    """
    Resolve gap

    Workflow transition: IN_PROGRESS → RESOLVED

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        resolution_notes: Optional resolution summary
        workflow: Gap workflow instance
        db: Database session

    Returns:
        Resolved gap
    """
    try:
        # Get gap
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        # Resolve via workflow
        updated_gap = await workflow.resolve_gap(
            gap_id=gap_id,
            tenant_id=tenant_id,
            resolution_notes=resolution_notes
        )

        logger.info(f"Gap {gap_id} resolved")

        return GapResponse(**updated_gap)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve gap: {str(e)}"
        )


@router.post("/{gap_id}/verify", response_model=GapResponse)
async def verify_gap_resolution(
    gap_id: str,
    tenant_id: str,
    verifier_id: str,
    verification_notes: Optional[str] = None,
    workflow: GapWorkflow = Depends(get_gap_workflow),
    db: AsyncSession = Depends(get_db)
) -> GapResponse:
    """
    Verify gap resolution

    Workflow transition: RESOLVED → VERIFIED

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        verifier_id: Verifier user ID
        verification_notes: Optional verification notes
        workflow: Gap workflow instance
        db: Database session

    Returns:
        Verified gap
    """
    try:
        # Get gap
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        # Verify via workflow
        updated_gap = await workflow.verify_resolution(
            gap_id=gap_id,
            tenant_id=tenant_id,
            verifier_id=verifier_id,
            notes=verification_notes
        )

        logger.info(f"Gap {gap_id} verified by {verifier_id}")

        return GapResponse(**updated_gap)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify gap: {str(e)}"
        )


@router.post("/{gap_id}/reopen", response_model=GapResponse)
async def reopen_gap(
    gap_id: str,
    tenant_id: str,
    reason: str,
    workflow: GapWorkflow = Depends(get_gap_workflow),
    db: AsyncSession = Depends(get_db)
) -> GapResponse:
    """
    Reopen gap

    Workflow transition: RESOLVED → OPEN

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        reason: Reason for reopening
        workflow: Gap workflow instance
        db: Database session

    Returns:
        Reopened gap
    """
    try:
        # Get gap
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        # Reopen via workflow
        updated_gap = await workflow.reopen_gap(
            gap_id=gap_id,
            tenant_id=tenant_id,
            reason=reason
        )

        logger.info(f"Gap {gap_id} reopened: {reason}")

        return GapResponse(**updated_gap)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reopen gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reopen gap: {str(e)}"
        )


@router.get("/severity/{severity}", response_model=List[GapResponse])
async def get_gaps_by_severity(
    severity: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[GapResponse]:
    """
    Get all gaps with specific severity level

    Args:
        severity: Severity level (critical, high, medium, low)
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        List of gaps with specified severity
    """
    try:
        # Validate severity
        try:
            GapSeverity(severity)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity: {severity}. Must be one of: critical, high, medium, low"
            )

        stmt = select(GapModel).where(
            and_(
                GapModel.tenant_id == tenant_id,
                GapModel.severity == severity
            )
        ).order_by(GapModel.current_score.asc())

        result = await db.execute(stmt)
        gaps = result.scalars().all()

        return [GapResponse.model_validate(g) for g in gaps]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get gaps by severity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get gaps by severity: {str(e)}"
        )


# ============================================================================
# ROOT CAUSE ANALYSIS (ISO 22301 Clause 10.1)
# ============================================================================

@router.post("/{gap_id}/rca", response_model=RootCauseAnalysisResponse)
async def create_root_cause_analysis(
    gap_id: str,
    rca_data: RootCauseAnalysisCreate,
    db: AsyncSession = Depends(get_db)
) -> RootCauseAnalysisResponse:
    """
    Conduct Root Cause Analysis for gap/nonconformity

    ISO 22301 Clause 10.1 requires:
    - Evaluate need for action to eliminate causes of nonconformity
    - Root cause analysis to prevent recurrence

    Supports multiple RCA methods:
    - 5 Whys
    - Fishbone (Ishikawa)
    - Fault Tree Analysis

    Args:
        gap_id: Gap identifier
        rca_data: RCA details
        db: Database session

    Returns:
        Root cause analysis results
    """
    try:
        # Verify gap exists
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == rca_data.tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        # Store RCA data in gap metadata
        if not gap.metadata:
            gap.metadata = {}

        rca_record = {
            "method": rca_data.method,  # "5_whys", "fishbone", "fault_tree"
            "conducted_by": rca_data.conducted_by,
            "conducted_at": datetime.utcnow().isoformat(),
            "analysis": rca_data.analysis,
            "root_causes": rca_data.root_causes,
            "contributing_factors": rca_data.contributing_factors,
            "preventive_actions": rca_data.preventive_actions
        }

        if "rca_history" not in gap.metadata:
            gap.metadata["rca_history"] = []

        gap.metadata["rca_history"].append(rca_record)
        gap.metadata["latest_rca"] = rca_record
        gap.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(gap)

        logger.info(f"RCA completed for gap {gap_id} using {rca_data.method} method")

        return RootCauseAnalysisResponse(
            gap_id=gap_id,
            **rca_record
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create RCA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create RCA: {str(e)}"
        )


@router.get("/{gap_id}/rca", response_model=List[RootCauseAnalysisResponse])
async def get_root_cause_analyses(
    gap_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[RootCauseAnalysisResponse]:
    """
    Get all Root Cause Analyses for gap

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        List of RCA records
    """
    try:
        # Get gap
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        # Get RCA history from metadata
        rca_history = gap.metadata.get("rca_history", []) if gap.metadata else []

        return [
            RootCauseAnalysisResponse(
                gap_id=gap_id,
                **rca
            )
            for rca in rca_history
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get RCA history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get RCA history: {str(e)}"
        )


# ============================================================================
# EFFECTIVENESS REVIEW (ISO 22301 Clause 10.1)
# ============================================================================

@router.post("/{gap_id}/effectiveness-review", response_model=EffectivenessReviewResponse)
async def create_effectiveness_review(
    gap_id: str,
    review_data: EffectivenessReviewCreate,
    workflow: GapWorkflow = Depends(get_gap_workflow),
    db: AsyncSession = Depends(get_db)
) -> EffectivenessReviewResponse:
    """
    Conduct effectiveness review of corrective actions

    ISO 22301 Clause 10.1 requires:
    - Review effectiveness of corrective action taken
    - Make changes to BCMS if necessary

    This validates that the corrective action actually resolved the issue.

    Args:
        gap_id: Gap identifier
        review_data: Review details
        workflow: Gap workflow instance
        db: Database session

    Returns:
        Effectiveness review results
    """
    try:
        # Verify gap exists and is in RESOLVED status
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == review_data.tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        if gap.status != GapStatus.RESOLVED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Effectiveness review requires gap to be RESOLVED (current: {gap.status})"
            )

        # Store review data
        if not gap.metadata:
            gap.metadata = {}

        review_record = {
            "reviewed_by": review_data.reviewed_by,
            "reviewed_at": datetime.utcnow().isoformat(),
            "review_date": review_data.review_date.isoformat(),
            "is_effective": review_data.is_effective,
            "evidence": review_data.evidence,
            "findings": review_data.findings,
            "follow_up_actions": review_data.follow_up_actions,
            "conclusion": review_data.conclusion
        }

        if "effectiveness_reviews" not in gap.metadata:
            gap.metadata["effectiveness_reviews"] = []

        gap.metadata["effectiveness_reviews"].append(review_record)
        gap.metadata["latest_effectiveness_review"] = review_record
        gap.updated_at = datetime.utcnow()

        # If effective, move to VERIFIED
        # If not effective, reopen
        if review_data.is_effective:
            gap.status = GapStatus.VERIFIED.value
            gap.verified_at = datetime.utcnow()
            gap.verified_by = review_data.reviewed_by
            logger.info(f"Gap {gap_id} verified as effectively resolved")
        else:
            gap.status = GapStatus.OPEN.value
            logger.warning(f"Gap {gap_id} reopened - corrective action not effective")

        await db.commit()
        await db.refresh(gap)

        return EffectivenessReviewResponse(
            gap_id=gap_id,
            **review_record
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create effectiveness review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create effectiveness review: {str(e)}"
        )


@router.get("/{gap_id}/effectiveness-reviews", response_model=List[EffectivenessReviewResponse])
async def get_effectiveness_reviews(
    gap_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[EffectivenessReviewResponse]:
    """
    Get all effectiveness reviews for gap

    Args:
        gap_id: Gap identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        List of effectiveness review records
    """
    try:
        # Get gap
        stmt = select(GapModel).where(
            and_(
                GapModel.id == gap_id,
                GapModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if not gap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gap {gap_id} not found"
            )

        # Get reviews from metadata
        reviews = gap.metadata.get("effectiveness_reviews", []) if gap.metadata else []

        return [
            EffectivenessReviewResponse(
                gap_id=gap_id,
                **review
            )
            for review in reviews
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get effectiveness reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get effectiveness reviews: {str(e)}"
        )
