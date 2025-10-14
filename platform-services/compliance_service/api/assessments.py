"""
Assessments API
Provides endpoints for ISO 22301 compliance assessments
JWT-based authentication with RBAC
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from datetime import datetime
import logging

from compliance.database.connection import get_db
from shared.auth import get_current_user, Permission, require_permission
from compliance.models.schemas import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentResultResponse,
    AssessmentRunRequest,
    GapResponse
)
from compliance.models.database import AssessmentModel, AssessmentStatus
from compliance.core.assessment_engine import AssessmentEngine
from compliance.core.gap_analyzer import GapAnalyzer
from compliance.repositories.assessment_repository import AssessmentRepository
from compliance.integrations.eventbus import EventBusService
from compliance.config.settings import settings
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_tenant_access(current_user: dict, tenant_id: str) -> None:
    """Verify user has access to tenant"""
    if current_user.get("tenant_id") != tenant_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: User tenant '{current_user.get('tenant_id')}' does not match resource tenant '{tenant_id}'"
        )


# Dependency injection factories
def get_assessment_repository(db: AsyncSession = Depends(get_db)) -> AssessmentRepository:
    """Get Assessment repository with database session"""
    return AssessmentRepository(db)


async def get_assessment_engine(
    db: AsyncSession = Depends(get_db)
) -> AssessmentEngine:
    """Dependency to get assessment engine instance"""
    eventbus = None
    if settings.eventbus_url:
        eventbus = EventBusService(settings.eventbus_url)
    return AssessmentEngine(db, eventbus)


async def get_gap_analyzer(
    db: AsyncSession = Depends(get_db)
) -> GapAnalyzer:
    """Dependency to get gap analyzer instance"""
    eventbus = None
    if settings.eventbus_url:
        eventbus = EventBusService(settings.eventbus_url)
    return GapAnalyzer(db, eventbus)


@router.post(
    "/",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED
)
@require_permission(Permission.ASSESSMENT_CREATE)
async def create_assessment(
    assessment_data: AssessmentCreate,
    repository: AssessmentRepository = Depends(get_assessment_repository),
    current_user: dict = Depends(get_current_user)
) -> AssessmentResponse:
    """
    Create a new compliance assessment
    Requires: ASSESSMENT_CREATE permission

    Args:
        assessment_data: Assessment creation data
        repository: Assessment repository
        current_user: Authenticated user

    Returns:
        Created assessment
    """
    try:
        # Verify tenant access
        verify_tenant_access(current_user, assessment_data.tenant_id)
        # Create assessment via repository
        assessment = await repository.create(
            tenant_id=assessment_data.tenant_id,
            name=assessment_data.name,
            description=assessment_data.description,
            target_compliance=assessment_data.target_compliance or settings.default_target_compliance
        )

        logger.info(f"Assessment created: {assessment.id} for tenant {assessment.tenant_id}")

        return AssessmentResponse.model_validate(assessment)

    except Exception as e:
        logger.error(f"Failed to create assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment: {str(e)}"
        )


@router.get("/", response_model=List[AssessmentResponse])
async def list_assessments(
    tenant_id: str,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    repository: AssessmentRepository = Depends(get_assessment_repository)
) -> List[AssessmentResponse]:
    """
    List all assessments for a tenant

    Args:
        tenant_id: Tenant identifier
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Optional status filter
        db: Database session

    Returns:
        List of assessments
    """
    try:
        # Use repository to list assessments
        assessments = await repository.list_by_tenant(
            tenant_id=tenant_id,
            status=status_filter,
            skip=skip,
            limit=limit
        )

        return [AssessmentResponse.model_validate(a) for a in assessments]

    except Exception as e:
        logger.error(f"Failed to list assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list assessments: {str(e)}"
        )


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    tenant_id: str,
    repository: AssessmentRepository = Depends(get_assessment_repository)
) -> AssessmentResponse:
    """
    Get assessment by ID

    Args:
        assessment_id: Assessment identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Assessment details
    """
    try:
        assessment = await repository.get_by_id(assessment_id, tenant_id)

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )

        return AssessmentResponse.model_validate(assessment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessment: {str(e)}"
        )


@router.post("/{assessment_id}/run", response_model=AssessmentResultResponse)
async def run_assessment(
    assessment_id: str,
    request: AssessmentRunRequest,
    engine: AssessmentEngine = Depends(get_assessment_engine),
    gap_analyzer: GapAnalyzer = Depends(get_gap_analyzer),
    db: AsyncSession = Depends(get_db)
) -> AssessmentResultResponse:
    """
    Run compliance assessment

    This endpoint executes the core assessment engine to:
    1. Evaluate evidence against ISO 22301 requirements
    2. Calculate compliance scores
    3. Identify gaps
    4. Generate remediation plan

    Args:
        assessment_id: Assessment identifier
        request: Assessment run request
        engine: Assessment engine instance
        gap_analyzer: Gap analyzer instance
        db: Database session

    Returns:
        Complete assessment results with gaps and recommendations
    """
    try:
        # Get assessment
        stmt = select(AssessmentModel).where(
            and_(
                AssessmentModel.id == assessment_id,
                AssessmentModel.tenant_id == request.tenant_id
            )
        )
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )

        # Update status to IN_PROGRESS
        assessment.status = AssessmentStatus.IN_PROGRESS.value
        assessment.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Running assessment {assessment_id} for tenant {request.tenant_id}")

        # Run assessment engine (CORE FUNCTIONALITY)
        assessment_results = await engine.assess_all_requirements(
            tenant_id=request.tenant_id,
            target_compliance=request.target_compliance or assessment.target_compliance
        )

        # Identify gaps
        gaps = await gap_analyzer.identify_gaps(
            assessment_results=assessment_results,
            tenant_id=request.tenant_id,
            target_compliance=request.target_compliance or assessment.target_compliance
        )

        # Update assessment with results
        assessment.status = AssessmentStatus.COMPLETED.value
        assessment.overall_score = assessment_results["overall_compliance"]
        assessment.compliant_count = assessment_results["summary"]["compliant"]
        assessment.partial_count = assessment_results["summary"]["partial"]
        assessment.non_compliant_count = assessment_results["summary"]["non_compliant"]
        assessment.completed_at = datetime.utcnow()
        assessment.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(assessment)

        logger.info(
            f"Assessment {assessment_id} completed: "
            f"Score={assessment.overall_score:.1f}%, "
            f"Gaps={len(gaps)}"
        )

        # Prepare response
        return AssessmentResultResponse(
            assessment=AssessmentResponse.model_validate(assessment),
            results=assessment_results,
            gaps=[GapResponse.model_validate(g) for g in gaps]
        )

    except HTTPException:
        raise
    except Exception as e:
        # Mark assessment as failed
        if assessment:
            assessment.status = AssessmentStatus.FAILED.value
            assessment.updated_at = datetime.utcnow()
            await db.commit()

        logger.error(f"Assessment {assessment_id} failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assessment failed: {str(e)}"
        )


@router.get("/{assessment_id}/results", response_model=AssessmentResultResponse)
async def get_assessment_results(
    assessment_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
) -> AssessmentResultResponse:
    """
    Get assessment results

    Args:
        assessment_id: Assessment identifier
        tenant_id: Tenant identifier
        db: Database session

    Returns:
        Assessment results with gaps
    """
    try:
        # Get assessment
        stmt = select(AssessmentModel).where(
            and_(
                AssessmentModel.id == assessment_id,
                AssessmentModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )

        if assessment.status != AssessmentStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Assessment is not completed (status: {assessment.status})"
            )

        # Get gaps for this assessment
        from compliance.models.database import GapModel

        stmt = select(GapModel).where(
            and_(
                GapModel.assessment_id == assessment_id,
                GapModel.tenant_id == tenant_id
            )
        ).order_by(GapModel.severity.desc())

        result = await db.execute(stmt)
        gaps = result.scalars().all()

        # Reconstruct results (simplified - could be stored in DB)
        results = {
            "overall_compliance": assessment.overall_score,
            "summary": {
                "compliant": assessment.compliant_count,
                "partial": assessment.partial_count,
                "non_compliant": assessment.non_compliant_count,
                "total": assessment.compliant_count + assessment.partial_count + assessment.non_compliant_count
            },
            "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None
        }

        return AssessmentResultResponse(
            assessment=AssessmentResponse.model_validate(assessment),
            results=results,
            gaps=[GapResponse.model_validate(g) for g in gaps]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get assessment results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessment results: {str(e)}"
        )


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    assessment_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete assessment

    Args:
        assessment_id: Assessment identifier
        tenant_id: Tenant identifier
        db: Database session
    """
    try:
        stmt = select(AssessmentModel).where(
            and_(
                AssessmentModel.id == assessment_id,
                AssessmentModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        assessment = result.scalar_one_or_none()

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )

        await db.delete(assessment)
        await db.commit()

        logger.info(f"Assessment {assessment_id} deleted")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete assessment: {str(e)}"
        )


# ============================================================================
# BATCH AI ASSESSMENT (from sandbox bcm_compliance_models.py:334-362)
# ============================================================================

@router.post("/batch-ai-scan", response_model=Dict)
async def batch_ai_assessment(
    tenant_id: str,
    requirement_ids: Optional[List[str]] = None,
    mode: str = "investigative",
    limit: int = 10,
    engine: AssessmentEngine = Depends(get_assessment_engine),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Trigger batch AI compliance scanning for multiple requirements

    Based on sandbox bcm_compliance_models.py:334-362

    Performs AI-powered compliance assessment for:
    - All requirements (if requirement_ids is None)
    - Specific requirements (if requirement_ids provided)
    - Limited batch size for performance

    Args:
        tenant_id: Tenant identifier
        requirement_ids: Optional list of requirement IDs to scan (None = all pending)
        mode: AI Guardian mode (vigilant/investigative/preventive/corrective)
        limit: Maximum requirements to scan in one batch (default 10)
        engine: Assessment engine instance
        db: Database session

    Returns:
        Batch scan results with success/error counts
    """
    try:
        from compliance.integrations.ai_orchestrator import ComplianceAIClient
        from compliance.standards.iso_22301 import ISO_22301_REQUIREMENTS

        ai_client = ComplianceAIClient(settings.ai_orchestration_url) if settings.ai_enabled else None

        if not ai_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="AI features are disabled"
            )

        # Determine which requirements to scan
        if requirement_ids:
            # Scan specific requirements
            requirements_to_scan = [
                (req_id, ISO_22301_REQUIREMENTS[req_id])
                for req_id in requirement_ids
                if req_id in ISO_22301_REQUIREMENTS
            ]
        else:
            # Scan all requirements (limited by limit parameter)
            requirements_to_scan = list(ISO_22301_REQUIREMENTS.items())[:limit]

        logger.info(
            f"Starting batch AI assessment for {len(requirements_to_scan)} requirements "
            f"(tenant={tenant_id}, mode={mode})"
        )

        # Process each requirement
        results = []
        for req_id, requirement in requirements_to_scan:
            try:
                # Get current compliance status for this requirement
                assessment_result = await engine.assess_requirement(req_id, tenant_id)

                current_score = assessment_result.get('score', 0)
                current_status = assessment_result.get('status', 'unknown')
                evidence_count = len(assessment_result.get('evidence_provided', []))

                # Perform AI scan
                ai_scan_result = await ai_client.scan_compliance(
                    requirement_id=req_id,
                    requirement_title=requirement['title'],
                    requirement_description=requirement['description'],
                    current_status=current_status,
                    evidence_count=evidence_count,
                    mode=mode
                )

                # Extract compliance insights
                insights = ai_client.extract_compliance_insights(
                    ai_scan_result.get('analysis', '')
                )

                results.append({
                    'requirement_id': req_id,
                    'status': 'success',
                    'current_score': current_score,
                    'ai_score': insights.get('score', 0),
                    'ai_assessment': insights.get('assessment', ''),
                    'recommendations': insights.get('recommendations', []),
                    'identified_gaps': insights.get('gaps', [])
                })

                logger.info(f"AI scan completed for {req_id}: score={insights.get('score')}")

            except Exception as e:
                logger.error(f"AI scan failed for {req_id}: {e}")
                results.append({
                    'requirement_id': req_id,
                    'status': 'error',
                    'error': str(e)
                })

        # Calculate summary
        successful = len([r for r in results if r['status'] == 'success'])
        errors = len([r for r in results if r['status'] == 'error'])

        avg_ai_score = sum(
            r.get('ai_score', 0) for r in results if r['status'] == 'success'
        ) / successful if successful > 0 else 0

        logger.info(
            f"Batch AI assessment completed: "
            f"{successful} successful, {errors} errors, avg_score={avg_ai_score:.1f}%"
        )

        return {
            'total_scanned': len(results),
            'successful': successful,
            'errors': errors,
            'average_ai_score': round(avg_ai_score, 1),
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch AI assessment failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch AI assessment failed: {str(e)}"
        )
