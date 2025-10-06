"""
Management Review API
ISO 22301:2019 Clause 9.3 - Management Review
Provides management review workflow for BCMS oversight
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from compliance.database.connection import get_db
from compliance.models.database import (
    ManagementReviewModel,
    ReviewStatus,
    AssessmentModel,
    AuditModel,
    GapModel,
    AssessmentStatus,
    AuditStatus,
    GapStatus
)
from compliance.models.schemas import (
    ManagementReviewCreate,
    ManagementReviewResponse,
    ManagementReviewInputs,
    ManagementReviewDecision,
    ManagementReviewReportResponse
)
from compliance.repositories.assessment_repository import AssessmentRepository
from compliance.repositories.audit_repository import AuditRepository
from compliance.repositories.gap_repository import GapRepository
from compliance.integrations.eventbus import EventBusService
from compliance.config.settings import settings
from sqlalchemy import select, and_, func, desc

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency injection factories
def get_assessment_repository(db: AsyncSession = Depends(get_db)) -> AssessmentRepository:
    """Get Assessment repository with database session"""
    return AssessmentRepository(db)


def get_audit_repository(db: AsyncSession = Depends(get_db)) -> AuditRepository:
    """Get Audit repository with database session"""
    return AuditRepository(db)


def get_gap_repository(db: AsyncSession = Depends(get_db)) -> GapRepository:
    """Get Gap repository with database session"""
    return GapRepository(db)


@router.post(
    "/",
    response_model=ManagementReviewResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_management_review(
    review_data: ManagementReviewCreate,
    db: AsyncSession = Depends(get_db)
) -> ManagementReviewResponse:
    """
    Create management review

    ISO 22301 Clause 9.3 requires:
    - Top management reviews BCMS at planned intervals
    - Ensure continuing suitability, adequacy, effectiveness

    Args:
        review_data: Review details
        db: Database session

    Returns:
        Created management review
    """
    try:
        review = ManagementReviewModel(
            tenant_id=review_data.tenant_id,
            name=review_data.name,
            scheduled_date=review_data.scheduled_date,
            review_period_start=review_data.review_period_start,
            review_period_end=review_data.review_period_end,
            chairperson_id=review_data.chairperson_id,
            attendees=review_data.attendees,
            status=ReviewStatus.PLANNED.value,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(review)
        await db.commit()
        await db.refresh(review)

        logger.info(f"Management review created: {review.id} scheduled for {review.scheduled_date}")

        return ManagementReviewResponse.model_validate(review)

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create management review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create management review: {str(e)}"
        )


@router.get("/", response_model=List[ManagementReviewResponse])
async def list_management_reviews(
    tenant_id: str,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[ManagementReviewResponse]:
    """
    List management reviews

    Args:
        tenant_id: Tenant identifier
        status_filter: Optional status filter
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session

    Returns:
        List of management reviews
    """
    try:
        query = select(ManagementReviewModel).where(
            ManagementReviewModel.tenant_id == tenant_id
        )

        if status_filter:
            query = query.where(ManagementReviewModel.status == status_filter)

        query = query.offset(skip).limit(limit).order_by(
            desc(ManagementReviewModel.scheduled_date)
        )

        result = await db.execute(query)
        reviews = result.scalars().all()

        return [ManagementReviewResponse.model_validate(r) for r in reviews]

    except Exception as e:
        logger.error(f"Failed to list management reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list management reviews: {str(e)}"
        )


@router.get("/{review_id}", response_model=ManagementReviewResponse)
async def get_management_review(
    review_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> ManagementReviewResponse:
    """
    Get management review by ID

    Args:
        review_id: Review identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Management review details
    """
    try:
        stmt = select(ManagementReviewModel).where(
            and_(
                ManagementReviewModel.id == review_id,
                ManagementReviewModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Management review {review_id} not found"
            )

        return ManagementReviewResponse.model_validate(review)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get management review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get management review: {str(e)}"
        )


@router.get("/{review_id}/inputs", response_model=ManagementReviewInputs)
async def get_review_inputs(
    review_id: str,
    tenant_id: str,
    assessment_repo: AssessmentRepository = Depends(get_assessment_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    gap_repo: GapRepository = Depends(get_gap_repository),
    db: AsyncSession = Depends(get_db)
) -> ManagementReviewInputs:
    """
    Collect management review inputs

    ISO 22301 Clause 9.3 requires review of:
    - Status of actions from previous reviews
    - Changes in external/internal issues
    - Performance information (metrics, audit results, exercise results)
    - Feedback from interested parties
    - Opportunities for continual improvement

    Args:
        review_id: Review identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Aggregated review inputs
    """
    try:
        # Get review
        review_stmt = select(ManagementReviewModel).where(
            and_(
                ManagementReviewModel.id == review_id,
                ManagementReviewModel.tenant_id == tenant_id
            )
        )
        review_result = await db.execute(review_stmt)
        review = review_result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Management review {review_id} not found"
            )

        period_start = review.review_period_start
        period_end = review.review_period_end

        # 1. Previous review actions
        previous_review_stmt = select(ManagementReviewModel).where(
            and_(
                ManagementReviewModel.tenant_id == tenant_id,
                ManagementReviewModel.status == ReviewStatus.COMPLETED.value,
                ManagementReviewModel.completed_date < review.scheduled_date
            )
        ).order_by(desc(ManagementReviewModel.completed_date)).limit(1)

        previous_result = await db.execute(previous_review_stmt)
        previous_review = previous_result.scalar_one_or_none()

        previous_actions = []
        if previous_review and previous_review.decisions:
            previous_actions = [
                {
                    "action": decision.get("action"),
                    "status": decision.get("status", "pending"),
                    "assigned_to": decision.get("assigned_to")
                }
                for decision in previous_review.decisions
            ]

        # 2. Compliance performance (assessments)
        assessments_stmt = select(AssessmentModel).where(
            and_(
                AssessmentModel.tenant_id == tenant_id,
                AssessmentModel.status == AssessmentStatus.COMPLETED.value,
                AssessmentModel.completed_at >= period_start,
                AssessmentModel.completed_at <= period_end
            )
        )
        assessments_result = await db.execute(assessments_stmt)
        assessments = assessments_result.scalars().all()

        compliance_metrics = {
            "assessments_completed": len(assessments),
            "average_score": sum(a.overall_score for a in assessments) / len(assessments) if assessments else 0,
            "latest_score": assessments[-1].overall_score if assessments else None
        }

        # 3. Internal audit results
        audits_stmt = select(AuditModel).where(
            and_(
                AuditModel.tenant_id == tenant_id,
                AuditModel.status == AuditStatus.COMPLETED.value,
                AuditModel.completed_date >= period_start,
                AuditModel.completed_date <= period_end
            )
        )
        audits_result = await db.execute(audits_stmt)
        audits = audits_result.scalars().all()

        audit_results = {
            "audits_completed": len(audits),
            "total_findings": sum(a.findings_count or 0 for a in audits),
            "nonconformities": sum(a.nonconformities_count or 0 for a in audits)
        }

        # 4. Gap/NC status
        gaps_stmt = select(
            GapModel.status,
            func.count(GapModel.id).label('count')
        ).where(
            GapModel.tenant_id == tenant_id
        ).group_by(GapModel.status)

        gaps_result = await db.execute(gaps_stmt)
        gap_status = {row.status: row.count for row in gaps_result}

        gap_summary = {
            "open": gap_status.get(GapStatus.OPEN.value, 0),
            "in_progress": gap_status.get(GapStatus.IN_PROGRESS.value, 0),
            "resolved": gap_status.get(GapStatus.RESOLVED.value, 0),
            "verified": gap_status.get(GapStatus.VERIFIED.value, 0)
        }

        # 5. Changes and improvements
        changes_summary = {
            "new_gaps_identified": gap_status.get(GapStatus.OPEN.value, 0),
            "gaps_resolved": gap_status.get(GapStatus.VERIFIED.value, 0),
            "improvement_rate": 0  # Calculate based on period comparison
        }

        return ManagementReviewInputs(
            review_id=review_id,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            previous_actions=previous_actions,
            compliance_metrics=compliance_metrics,
            audit_results=audit_results,
            gap_summary=gap_summary,
            changes_summary=changes_summary,
            generated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get review inputs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get review inputs: {str(e)}"
        )


@router.post("/{review_id}/start", response_model=ManagementReviewResponse)
async def start_review(
    review_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> ManagementReviewResponse:
    """
    Start management review

    Workflow transition: PLANNED → IN_PROGRESS

    Args:
        review_id: Review identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Updated review
    """
    try:
        stmt = select(ManagementReviewModel).where(
            and_(
                ManagementReviewModel.id == review_id,
                ManagementReviewModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Management review {review_id} not found"
            )

        if review.status != ReviewStatus.PLANNED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start review in {review.status} status"
            )

        review.status = ReviewStatus.IN_PROGRESS.value
        review.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(review)

        logger.info(f"Management review {review_id} started")

        return ManagementReviewResponse.model_validate(review)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to start review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start review: {str(e)}"
        )


@router.post("/{review_id}/decisions", response_model=ManagementReviewResponse)
async def record_decisions(
    review_id: str,
    tenant_id: str,
    decisions: List[ManagementReviewDecision],
    db: AsyncSession = Depends(get_db)
) -> ManagementReviewResponse:
    """
    Record management review decisions

    ISO 22301 Clause 9.3 requires outputs related to:
    - Decisions on improvement opportunities
    - Decisions on changes to BCMS
    - Resource needs

    Args:
        review_id: Review identifier
        tenant_id: Tenant identifier
        decisions: List of decisions made
        db: Database session

    Returns:
        Updated review with decisions
    """
    try:
        stmt = select(ManagementReviewModel).where(
            and_(
                ManagementReviewModel.id == review_id,
                ManagementReviewModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Management review {review_id} not found"
            )

        # Convert decisions to dict format
        decisions_data = [
            {
                "decision_type": d.decision_type,
                "description": d.description,
                "action": d.action,
                "assigned_to": d.assigned_to,
                "target_date": d.target_date.isoformat() if d.target_date else None,
                "priority": d.priority,
                "status": "pending"
            }
            for d in decisions
        ]

        review.decisions = decisions_data
        review.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(review)

        logger.info(f"Recorded {len(decisions)} decisions for review {review_id}")

        return ManagementReviewResponse.model_validate(review)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to record decisions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record decisions: {str(e)}"
        )


@router.post("/{review_id}/complete", response_model=ManagementReviewResponse)
async def complete_review(
    review_id: str,
    tenant_id: str,
    summary: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> ManagementReviewResponse:
    """
    Complete management review

    Workflow transition: IN_PROGRESS → COMPLETED

    Args:
        review_id: Review identifier
        tenant_id: Tenant identifier
        summary: Optional review summary
        db: Database session

    Returns:
        Completed review
    """
    try:
        stmt = select(ManagementReviewModel).where(
            and_(
                ManagementReviewModel.id == review_id,
                ManagementReviewModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Management review {review_id} not found"
            )

        if review.status != ReviewStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete review in {review.status} status"
            )

        review.status = ReviewStatus.COMPLETED.value
        review.completed_date = datetime.utcnow()
        review.summary = summary
        review.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(review)

        logger.info(f"Management review {review_id} completed")

        # Emit event
        if settings.eventbus_url:
            eventbus = EventBusService(settings.eventbus_url)
            await eventbus.emit_event(
                event_type="management_review_completed",
                source="compliance",
                data={
                    "review_id": review_id,
                    "tenant_id": tenant_id,
                    "decisions_count": len(review.decisions) if review.decisions else 0,
                    "completed_date": review.completed_date.isoformat()
                }
            )

        return ManagementReviewResponse.model_validate(review)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to complete review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete review: {str(e)}"
        )


@router.get("/{review_id}/report", response_model=ManagementReviewReportResponse)
async def generate_review_report(
    review_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> ManagementReviewReportResponse:
    """
    Generate management review report

    Comprehensive report including:
    - Review inputs
    - Discussions
    - Decisions
    - Action items

    Args:
        review_id: Review identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Complete management review report
    """
    try:
        # Get review
        stmt = select(ManagementReviewModel).where(
            and_(
                ManagementReviewModel.id == review_id,
                ManagementReviewModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Management review {review_id} not found"
            )

        # Get inputs
        inputs = await get_review_inputs(review_id, tenant_id, db)

        # Summary of decisions by type
        decisions_summary = {}
        if review.decisions:
            for decision in review.decisions:
                dec_type = decision.get("decision_type", "other")
                decisions_summary[dec_type] = decisions_summary.get(dec_type, 0) + 1

        return ManagementReviewReportResponse(
            review=ManagementReviewResponse.model_validate(review),
            inputs=inputs,
            decisions_summary=decisions_summary,
            action_items=[
                {
                    "action": d.get("action"),
                    "assigned_to": d.get("assigned_to"),
                    "target_date": d.get("target_date"),
                    "priority": d.get("priority"),
                    "status": d.get("status")
                }
                for d in (review.decisions or [])
            ],
            generated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate review report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate review report: {str(e)}"
        )
