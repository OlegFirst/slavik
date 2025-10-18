"""Improvement Initiatives API - ISO 10.2"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header
import logging
import uuid

from ..schemas import (
    ImprovementInitiative,
    ImprovementInitiativeCreate,
    ImprovementInitiativeUpdate,
    ImprovementProgressUpdate,
    ImprovementVerification,
    ImprovementsDashboard,
    ROIAnalysis,
    InitiativeStatus,
    InitiativePriority,
    InitiativeSource,
)
from ..storage import (
    get_all_initiatives,
    get_initiative,
    create_initiative,
    update_initiative,
    get_next_number,
)
from ..utils import (
    generate_initiative_code,
    calculate_roi,
    calculate_benefits_total,
    publish_event,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/improvements", response_model=ImprovementInitiative)
async def create_improvement_initiative(
    initiative_data: ImprovementInitiativeCreate,
    current_user: str = Header(..., alias="X-User-ID")
):
    """Create improvement initiative (ISO 10.2)"""
    try:
        # Generate initiative ID and code
        initiative_id = str(uuid.uuid4())
        count = get_next_number() - 1
        initiative_code = generate_initiative_code(initiative_data.tenant_id, count)

        # Create initiative
        initiative = ImprovementInitiative(
            id=initiative_id,
            tenant_id=initiative_data.tenant_id,
            initiative_code=initiative_code,
            title=initiative_data.title,
            description=initiative_data.description,
            initiative_type=initiative_data.initiative_type,
            source=initiative_data.source,
            source_reference_id=initiative_data.source_reference_id,
            source_module=initiative_data.source_module,
            business_case=initiative_data.business_case,
            problem_statement=initiative_data.problem_statement,
            proposed_solution=initiative_data.proposed_solution,
            expected_benefits=initiative_data.expected_benefits or [],
            estimated_cost=initiative_data.estimated_cost,
            estimated_effort_days=initiative_data.estimated_effort_days,
            roi=initiative_data.roi,
            payback_period_months=initiative_data.payback_period_months,
            npv=initiative_data.npv,
            priority=initiative_data.priority,
            urgency=initiative_data.urgency,
            impact_level=initiative_data.impact_level,
            owner_id=initiative_data.owner_id,
            team_members=initiative_data.team_members or [],
            target_completion_date=initiative_data.target_completion_date,
            implementation_plan=initiative_data.implementation_plan,
            related_risks=initiative_data.related_risks or [],
            related_objectives=initiative_data.related_objectives or [],
            related_processes=initiative_data.related_processes or [],
            created_by=current_user,
            created_at=datetime.now()
        )

        create_initiative(initiative)

        # Publish event
        await publish_event("bcm.compliance.improvement_created", {
            "tenant_id": initiative_data.tenant_id,
            "initiative_id": initiative_id,
            "initiative_code": initiative_code,
            "title": initiative_data.title,
            "source": initiative_data.source
        })

        logger.info(f"Created improvement initiative: {initiative_code}")
        return initiative

    except Exception as e:
        logger.error(f"Create improvement initiative failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/improvements", response_model=List[ImprovementInitiative])
async def list_improvement_initiatives(
    tenant_id: str = Query(...),
    status: Optional[InitiativeStatus] = None,
    priority: Optional[InitiativePriority] = None,
    source: Optional[InitiativeSource] = None
):
    """List improvement initiatives with filters"""
    try:
        all_initiatives = get_all_initiatives()
        initiatives = [
            i for i in all_initiatives.values()
            if i.tenant_id == tenant_id
        ]

        if status:
            initiatives = [i for i in initiatives if i.status == status]
        if priority:
            initiatives = [i for i in initiatives if i.priority == priority]
        if source:
            initiatives = [i for i in initiatives if i.source == source]

        # Sort by created_at desc
        initiatives.sort(key=lambda x: x.created_at, reverse=True)

        return initiatives

    except Exception as e:
        logger.error(f"List improvement initiatives failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/improvements/{initiative_id}", response_model=ImprovementInitiative)
async def get_improvement_initiative(
    initiative_id: str,
    tenant_id: str = Query(...)
):
    """Get improvement initiative by ID"""
    try:
        initiative = get_initiative(initiative_id)

        if not initiative:
            raise HTTPException(status_code=404, detail=f"Initiative {initiative_id} not found")

        if initiative.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return initiative

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get improvement initiative failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/improvements/{initiative_id}", response_model=ImprovementInitiative)
async def update_improvement_initiative(
    initiative_id: str,
    updates: ImprovementInitiativeUpdate,
    tenant_id: str = Query(...)
):
    """Update improvement initiative"""
    try:
        initiative = get_initiative(initiative_id)

        if not initiative:
            raise HTTPException(status_code=404, detail=f"Initiative {initiative_id} not found")

        if initiative.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update fields
        update_data = updates.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(initiative, key, value)

        initiative.updated_at = datetime.now()
        update_initiative(initiative_id, initiative)

        logger.info(f"Updated initiative {initiative.initiative_code}")
        return initiative

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update improvement initiative failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/improvements/{initiative_id}/progress")
async def update_initiative_progress(
    initiative_id: str,
    progress_data: ImprovementProgressUpdate,
    tenant_id: str = Query(...)
):
    """Update initiative progress"""
    try:
        initiative = get_initiative(initiative_id)

        if not initiative:
            raise HTTPException(status_code=404, detail=f"Initiative {initiative_id} not found")

        if initiative.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update progress
        if progress_data.progress_percentage is not None:
            initiative.progress_percentage = progress_data.progress_percentage
        if progress_data.milestones is not None:
            initiative.milestones = progress_data.milestones
        if progress_data.status is not None:
            initiative.status = progress_data.status

        initiative.updated_at = datetime.now()
        update_initiative(initiative_id, initiative)

        logger.info(f"Initiative {initiative.initiative_code} progress updated: {initiative.progress_percentage}%")
        return {
            "message": "Progress updated",
            "progress_percentage": initiative.progress_percentage,
            "status": initiative.status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update progress failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improvements/{initiative_id}/verify")
async def verify_improvement(
    initiative_id: str,
    verification_data: ImprovementVerification,
    tenant_id: str = Query(...)
):
    """Verify improvement initiative"""
    try:
        initiative = get_initiative(initiative_id)

        if not initiative:
            raise HTTPException(status_code=404, detail=f"Initiative {initiative_id} not found")

        if initiative.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update verification
        initiative.verification_method = verification_data.verification_method
        initiative.verification_date = datetime.now()
        initiative.verification_result = verification_data.verification_result
        initiative.benefits_realized = verification_data.benefits_realized or []
        initiative.actual_cost = verification_data.actual_cost
        initiative.actual_effort_days = verification_data.actual_effort_days
        initiative.actual_roi = verification_data.actual_roi
        initiative.lessons_learned = verification_data.lessons_learned
        initiative.challenges_faced = verification_data.challenges_faced
        initiative.success_factors = verification_data.success_factors
        initiative.status = InitiativeStatus.VERIFIED
        initiative.updated_at = datetime.now()

        update_initiative(initiative_id, initiative)

        # Publish event
        await publish_event("bcm.compliance.improvement_verified", {
            "tenant_id": tenant_id,
            "initiative_id": initiative_id,
            "initiative_code": initiative.initiative_code,
            "verification_result": verification_data.verification_result,
            "actual_roi": verification_data.actual_roi
        })

        logger.info(f"Initiative {initiative.initiative_code} verified: {initiative.verification_result}")
        return {
            "message": "Initiative verified",
            "verification_result": initiative.verification_result,
            "actual_roi": initiative.actual_roi
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify improvement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/improvements/dashboard", response_model=ImprovementsDashboard)
async def get_improvements_dashboard(tenant_id: str = Query(...)):
    """Get improvements dashboard"""
    try:
        all_initiatives = get_all_initiatives()
        initiatives = [i for i in all_initiatives.values() if i.tenant_id == tenant_id]

        # Calculate stats
        total = len(initiatives)
        by_status = {}
        by_source = {}
        total_roi = 0.0
        total_benefits = 0.0

        for i in initiatives:
            # Count by status
            by_status[i.status.value] = by_status.get(i.status.value, 0) + 1
            # Count by source
            by_source[i.source.value] = by_source.get(i.source.value, 0) + 1
            # Sum ROI
            if i.actual_roi:
                total_roi += i.actual_roi
            # Sum benefits
            total_benefits += calculate_benefits_total(i.benefits_realized or [])

        avg_roi = total_roi / total if total > 0 else 0

        return ImprovementsDashboard(
            tenant_id=tenant_id,
            total_initiatives=total,
            by_status=by_status,
            by_source=by_source,
            average_roi=round(avg_roi, 2),
            total_benefits_realized=total_benefits,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Improvements dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/improvements/roi-analysis", response_model=ROIAnalysis)
async def analyze_improvements_roi(
    tenant_id: str = Query(...),
    period_months: int = Query(default=12, ge=1, le=60)
):
    """ROI analysis of improvements"""
    try:
        from datetime import timedelta

        all_initiatives = get_all_initiatives()
        cutoff_date = datetime.now() - timedelta(days=period_months*30)

        initiatives = [
            i for i in all_initiatives.values()
            if i.tenant_id == tenant_id
            and i.created_at >= cutoff_date
            and i.status in [InitiativeStatus.IMPLEMENTED, InitiativeStatus.VERIFIED, InitiativeStatus.CLOSED]
        ]

        total_investment = sum(i.actual_cost or i.estimated_cost or 0 for i in initiatives)
        total_benefits = 0.0
        best_performers = []

        for i in initiatives:
            benefits = calculate_benefits_total(i.benefits_realized or [])
            total_benefits += benefits

            if i.actual_roi:
                best_performers.append({
                    "initiative_code": i.initiative_code,
                    "title": i.title,
                    "roi": i.actual_roi,
                    "benefits": benefits
                })

        best_performers.sort(key=lambda x: x["roi"], reverse=True)
        overall_roi = calculate_roi(total_benefits, total_investment)

        return ROIAnalysis(
            period_months=period_months,
            total_investment=total_investment,
            total_benefits_realized=total_benefits,
            overall_roi=round(overall_roi, 2),
            initiatives_count=len(initiatives),
            best_performers=best_performers[:10],
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"ROI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
