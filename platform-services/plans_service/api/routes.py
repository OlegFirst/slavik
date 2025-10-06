"""
Plans Service API Routes
ISO 22301 Clause 8.4 - Business Continuity Plans and Procedures
Complete API from old plans/main.py refactored to new architecture
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.domain import (
    PlanCreate, PlanUpdate, PlanResponse,
    ProcedureCreate, ProcedureUpdate, ProcedureResponse,
    ResourceCreate, ResourceUpdate, ResourceResponse,
    ContactListCreate, ContactListResponse,
    ActivationCreate, ActivationResponse,
    ReviewCreate, ReviewResponse,
    PlanStatus, PlanType, PlanPriority,
)
from ..services.plan_service import PlanService
from ..dependencies import get_plan_service
from ..workflows.plan_lifecycle import get_workflow_summary
from ..auth import UserContext, get_current_user

router = APIRouter(prefix="/api/plans", tags=["plans"])


# ==================== PLAN MANAGEMENT ====================

@router.post("/plans", response_model=PlanResponse, status_code=201)
async def create_plan(
    plan: PlanCreate,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Create new business continuity plan - ISO 22301: 8.4.1, 8.4.4"""
    return await service.create_plan(plan, current_user.user_id)


@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(
    current_user: UserContext = Depends(get_current_user),
    plan_type: Optional[PlanType] = None,
    status: Optional[PlanStatus] = None,
    priority: Optional[PlanPriority] = None,
    review_due: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: PlanService = Depends(get_plan_service)
):
    """List business continuity plans with filters - ISO 22301: 8.4.1"""
    return await service.list_plans(
        tenant_id=current_user.tenant_id,
        plan_type=plan_type,
        status=status,
        priority=priority,
        review_due=review_due,
        skip=skip,
        limit=limit
    )


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int = Path(...),
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Get plan details - ISO 22301: 8.4.1"""
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    # Enforce tenant isolation
    if plan.tenant_id != current_user.tenant_id and not current_user.is_superadmin:
        raise HTTPException(403, "Access denied to this plan")
    return plan


@router.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan_update: PlanUpdate,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Update plan (DRAFT only) - ISO 22301: 8.4.1"""
    try:
        plan = await service.update_plan(plan_id, plan_update, current_user.user_id)
        if not plan:
            raise HTTPException(404, "Plan not found")
        return plan
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: int,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Archive plan (soft delete) - ISO 22301: 8.4.1"""
    deleted = await service.delete_plan(plan_id)
    if not deleted:
        raise HTTPException(404, "Plan not found")


# ==================== PLAN WORKFLOW ====================

@router.post("/plans/{plan_id}/submit-review")
async def submit_for_review(
    plan_id: int,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Submit plan for review (DRAFT → UNDER_REVIEW) - ISO 22301: 8.4.1"""
    try:
        plan = await service.submit_for_review(plan_id, current_user.user_id)
        return {
            "plan_id": plan.plan_id,
            "status": plan.status.value,
            "message": "Plan submitted for review"
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/plans/{plan_id}/approve")
async def approve_plan(
    plan_id: int,
    current_user: UserContext = Depends(get_current_user),
    approval_notes: Optional[str] = Body(None),
    service: PlanService = Depends(get_plan_service)
):
    """Approve plan (UNDER_REVIEW → APPROVED) - ISO 22301: 8.4.1"""
    try:
        plan = await service.approve_plan(plan_id, current_user.user_id, approval_notes)
        return {
            "plan_id": plan.plan_id,
            "status": plan.status.value,
            "approved_by": current_user.user_id,
            "message": "Plan approved successfully"
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/plans/{plan_id}/activate")
async def activate_plan(
    plan_id: int,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Activate plan (APPROVED → ACTIVE) - ISO 22301: 8.4.1"""
    try:
        plan = await service.activate_plan(plan_id, current_user.user_id)
        return {
            "plan_id": plan.plan_id,
            "status": plan.status.value,
            "message": "Plan activated successfully"
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/plans/{plan_id}/workflow")
async def get_workflow_status(
    plan_id: int,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Get workflow status and available actions"""
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")

    # Convert to dict for workflow summary (need actual Plan model)
    from ..repositories.plan_repository import PlanRepository
    repo = service.repo
    db_plan = await repo.get_by_id(plan_id)

    return get_workflow_summary(db_plan)


# ==================== PROCEDURE MANAGEMENT ====================

@router.post("/plans/{plan_id}/procedures", response_model=ProcedureResponse, status_code=201)
async def add_procedure(
    plan_id: int,
    procedure: ProcedureCreate,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Add procedure to plan - ISO 22301: 8.4.4"""
    try:
        return await service.add_procedure(plan_id, procedure, current_user.user_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/plans/{plan_id}/procedures", response_model=List[ProcedureResponse])
async def list_procedures(
    plan_id: int,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """List plan procedures - ISO 22301: 8.4.4"""
    return await service.list_procedures(plan_id)


@router.put("/plans/{plan_id}/procedures/{procedure_id}", response_model=ProcedureResponse)
async def update_procedure(
    plan_id: int,
    procedure_id: int,
    procedure_update: ProcedureUpdate,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Update procedure - ISO 22301: 8.4.4"""
    try:
        proc = await service.update_procedure(procedure_id, procedure_update, current_user.user_id)
        if not proc:
            raise HTTPException(404, "Procedure not found")
        return proc
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/plans/{plan_id}/procedures/{procedure_id}", status_code=204)
async def delete_procedure(
    plan_id: int,
    procedure_id: int,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Delete procedure - ISO 22301: 8.4.4"""
    deleted = await service.delete_procedure(procedure_id)
    if not deleted:
        raise HTTPException(404, "Procedure not found")


# ==================== RESOURCE MANAGEMENT ====================

@router.post("/plans/{plan_id}/resources", response_model=ResourceResponse, status_code=201)
async def add_resource(
    plan_id: int,
    resource: ResourceCreate,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Add resource to plan - ISO 22301: 8.4.4"""
    try:
        return await service.add_resource(plan_id, resource, current_user.user_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/plans/{plan_id}/resources", response_model=List[ResourceResponse])
async def list_resources(
    plan_id: int,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """List plan resources - ISO 22301: 8.4.4"""
    return await service.list_resources(plan_id)


# ==================== CONTACT LISTS ====================

@router.post("/contact-lists", response_model=ContactListResponse, status_code=201)
async def create_contact_list(
    contact_list: ContactListCreate,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Create contact list - ISO 22301: 8.4.3"""
    return await service.add_contact_list(contact_list, current_user.user_id)


@router.get("/contact-lists", response_model=List[ContactListResponse])
async def list_contact_lists(
    plan_id: int = Query(...),
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """List contact lists for plan - ISO 22301: 8.4.3"""
    return await service.list_contact_lists(plan_id)


# ==================== PLAN ACTIVATION ====================

@router.post("/plans/{plan_id}/activate-real", response_model=ActivationResponse, status_code=201)
async def activate_for_incident(
    plan_id: int,
    activation: ActivationCreate,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Activate plan for real incident - ISO 22301: 8.4.2"""
    try:
        return await service.activate_for_incident(plan_id, activation, current_user.user_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/activations", response_model=List[ActivationResponse])
async def list_activations(
    plan_id: int = Query(...),
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """List plan activations - ISO 22301: 8.5"""
    return await service.list_activations(plan_id)


# ==================== PLAN REVIEWS ====================

@router.post("/plans/{plan_id}/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    plan_id: int,
    review: ReviewCreate,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """Create plan review - ISO 22301: 8.4"""
    try:
        return await service.create_review(plan_id, review, current_user.user_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/plans/{plan_id}/reviews", response_model=List[ReviewResponse])
async def list_reviews(
    plan_id: int,
    current_user: UserContext = Depends(get_current_user),
    service: PlanService = Depends(get_plan_service)
):
    """List plan reviews - ISO 22301: 8.4"""
    return await service.list_reviews(plan_id)
