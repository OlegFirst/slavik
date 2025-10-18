"""
Projects API Router
Endpoints for client project management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.connection import get_db
from api.dependencies import (
    get_current_user,
    get_current_user_optional,
    require_client,
    require_admin,
    get_db_with_context
)
from schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectSearchFilters
)
from services.project_service import project_service
from integrations.portal_client import portal_client

router = APIRouter(prefix="/api/marketplace/projects", tags=["projects"])


# ============================================================================
# Project Management Endpoints
# ============================================================================

@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Create new project

    **Requires:** Client or Admin role

    **Business Rules:**
    - Status starts as 'draft'
    - budget_min must be <= budget_max
    - start_date must be < end_date
    - Client can create multiple projects
    - Must specify service_type (bia, bcm_plan, risk_assessment, etc.)
    """
    try:
        project = await project_service.create_project(
            db=db,
            project_data=project_data,
            client_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"]
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ProjectResponse])
async def search_projects(
    # Search filters
    service_type: Optional[str] = Query(None, description="Service type filter"),
    status: Optional[str] = Query(None, description="Project status"),
    urgency_level: Optional[str] = Query(None),
    budget_type: Optional[str] = Query(None),
    work_location: Optional[str] = Query(None),
    required_skills: Optional[str] = Query(None, description="Comma-separated skills"),
    min_budget: Optional[float] = Query(None, ge=0),
    max_budget: Optional[float] = Query(None, ge=0),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search in title, description"),
    # Pagination
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    # Dependencies
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Search projects with filters

    **Public endpoint** - No authentication required

    **Filters:**
    - service_type: bia, bcm_plan, risk_assessment, iso_22301, training, exercise, consulting
    - status: draft, open, in_progress, completed, cancelled
    - urgency_level: low, medium, high, urgent
    - budget_type: hourly, fixed, retainer
    - work_location: remote, onsite, hybrid
    - required_skills: Match any skill (OR logic)
    - budget range: min_budget, max_budget
    - location: country, city
    - search: Full-text search in title/description

    **Returns:** List of projects sorted by created_at DESC
    """
    # Parse comma-separated values
    skills_list = required_skills.split(",") if required_skills else None

    filters = ProjectSearchFilters(
        service_type=service_type,
        status=status,
        urgency_level=urgency_level,
        budget_type=budget_type,
        work_location=work_location,
        required_skills=skills_list,
        min_budget=min_budget,
        max_budget=max_budget,
        country=country,
        city=city,
        search=search,
        offset=offset,
        limit=limit
    )

    # Get tenant_id from user or default (for public access)
    tenant_id = current_user["tenant_id"] if current_user else "public"

    projects = await project_service.search_projects(db, filters, tenant_id)
    return projects


@router.get("/my", response_model=List[ProjectResponse])
async def get_my_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get current user's projects

    **Requires:** Client or Admin role

    **Returns:** All projects created by current user
    """
    projects = await project_service.get_projects_by_client(
        db=db,
        client_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        status=status
    )
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get project by ID

    **Public endpoint** - No authentication required

    **Returns:** Full project details with proposals count
    """
    tenant_id = current_user["tenant_id"] if current_user else "public"

    project = await project_service.get_project(
        db=db,
        project_id=project_id,
        tenant_id=tenant_id
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Update project

    **Requires:** Project ownership or Admin role

    **Business Rules:**
    - Can only update own projects (unless admin)
    - Cannot update 'completed' or 'cancelled' projects
    - Cannot change status via this endpoint (use publish/complete/cancel)
    - budget_min must be <= budget_max
    - start_date must be < end_date
    """
    # Get project to verify ownership
    project = await project_service.get_project(db, project_id, current_user["tenant_id"])

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership (unless admin)
    if current_user["user_type"] != "admin":
        if str(project.client_id) != str(current_user["user_id"]):
            raise HTTPException(
                status_code=403,
                detail="You can only update your own projects"
            )

    try:
        project = await project_service.update_project(
            db=db,
            project_id=project_id,
            project_data=project_data,
            tenant_id=current_user["tenant_id"]
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/publish", response_model=ProjectResponse)
async def publish_project(
    project_id: int,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Publish project (change status: draft → open)

    **Requires:** Project ownership or Admin role

    **Business Rules:**
    - Can only publish 'draft' projects
    - Sets published_at timestamp
    - Makes project visible to specialists
    - Emits project.published event
    - Gets relevant Portal scenarios for recommendations
    """
    # Get project to verify ownership
    project = await project_service.get_project(db, project_id, current_user["tenant_id"])

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership (unless admin)
    if current_user["user_type"] != "admin":
        if str(project.client_id) != str(current_user["user_id"]):
            raise HTTPException(
                status_code=403,
                detail="You can only publish your own projects"
            )

    try:
        project = await project_service.publish_project(
            db=db,
            project_id=project_id,
            tenant_id=current_user["tenant_id"],
            client_id=current_user["user_id"]
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/complete", response_model=ProjectResponse)
async def complete_project(
    project_id: int,
    completion_notes: Optional[str] = None,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Mark project as complete

    **Requires:** Project ownership or Admin role

    **Business Rules:**
    - Can only complete 'in_progress' projects
    - Sets completed_at timestamp
    - Emits project.completed event
    - Should trigger review request (future)
    - Creates Portal article from case study (integration)
    """
    # Get project to verify ownership
    project = await project_service.get_project(db, project_id, current_user["tenant_id"])

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership (unless admin)
    if current_user["user_type"] != "admin":
        if str(project.client_id) != str(current_user["user_id"]):
            raise HTTPException(
                status_code=403,
                detail="You can only complete your own projects"
            )

    try:
        project = await project_service.complete_project(
            db=db,
            project_id=project_id,
            tenant_id=current_user["tenant_id"],
            client_id=current_user["user_id"],
            completion_notes=completion_notes
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/cancel", response_model=ProjectResponse)
async def cancel_project(
    project_id: int,
    cancellation_reason: Optional[str] = None,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Cancel project

    **Requires:** Project ownership or Admin role

    **Business Rules:**
    - Can cancel 'draft', 'open', or 'in_progress' projects
    - Cannot cancel 'completed' or already 'cancelled' projects
    - Sets cancelled_at timestamp
    - Emits project.cancelled event
    - If in_progress, may trigger dispute resolution (future)
    """
    # Get project to verify ownership
    project = await project_service.get_project(db, project_id, current_user["tenant_id"])

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership (unless admin)
    if current_user["user_type"] != "admin":
        if str(project.client_id) != str(current_user["user_id"]):
            raise HTTPException(
                status_code=403,
                detail="You can only cancel your own projects"
            )

    try:
        project = await project_service.cancel_project(
            db=db,
            project_id=project_id,
            tenant_id=current_user["tenant_id"],
            client_id=current_user["user_id"],
            cancellation_reason=cancellation_reason
        )
        return project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Delete project (hard delete)

    **Requires:** Project ownership or Admin role

    **Business Rules:**
    - Can only delete 'draft' projects
    - Cannot delete projects with proposals
    - Permanent deletion (not soft delete)
    - Use cancel endpoint for published projects
    """
    # Get project to verify ownership and status
    project = await project_service.get_project(db, project_id, current_user["tenant_id"])

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership (unless admin)
    if current_user["user_type"] != "admin":
        if str(project.client_id) != str(current_user["user_id"]):
            raise HTTPException(
                status_code=403,
                detail="You can only delete your own projects"
            )

    if project.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Can only delete draft projects. Use cancel endpoint for published projects."
        )

    if project.proposal_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete project with proposals"
        )

    try:
        await project_service.delete_project(
            db=db,
            project_id=project_id,
            tenant_id=current_user["tenant_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Proposals for Project
# ============================================================================

@router.get("/{project_id}/proposals")
async def get_project_proposals(
    project_id: int,
    status: Optional[str] = Query(None, description="Filter by proposal status"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get all proposals for a project

    **Requires:** Project ownership or Admin role

    **Business Rules:**
    - Only project owner can see all proposals
    - Returns list of proposals with specialist details
    - Can filter by status (pending, accepted, rejected, withdrawn)

    **Note:** This is for clients to review proposals. Specialists see proposals via /api/marketplace/proposals endpoints.
    """
    # Get project to verify ownership
    project = await project_service.get_project(db, project_id, current_user["tenant_id"])

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership (unless admin)
    if current_user["user_type"] != "admin":
        if str(project.client_id) != str(current_user["user_id"]):
            raise HTTPException(
                status_code=403,
                detail="You can only view proposals for your own projects"
            )

    # Import here to avoid circular dependency
    from services.proposal_service import proposal_service

    proposals = await proposal_service.get_proposals_by_project(
        db=db,
        project_id=project_id,
        tenant_id=current_user["tenant_id"],
        status=status
    )

    return proposals


# ============================================================================
# Integration Endpoints
# ============================================================================

@router.get("/{project_id}/scenarios")
async def get_project_scenarios(
    project_id: int,
    limit: int = Query(5, ge=1, le=20),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get related BCM scenarios from Portal

    **Public endpoint**

    Shows Portal scenarios related to project's service type

    **Integration:** Portal Service

    **Use Cases:**
    - Client creating project → See scenario templates
    - Specialist viewing project → Learn about BCM scenarios
    """
    tenant_id = current_user["tenant_id"] if current_user else "public"

    project = await project_service.get_project(db, project_id, tenant_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Search Portal for related scenarios
    scenarios = []
    try:
        if project.service_type:
            scenarios = await portal_client.search_scenarios(
                service_type=project.service_type,
                limit=limit
            )
    except Exception as e:
        # Don't fail if Portal is unavailable
        pass

    return {
        "project_id": project_id,
        "service_type": project.service_type,
        "scenarios": scenarios
    }


# ============================================================================
# Statistics
# ============================================================================

@router.get("/stats/overview")
async def get_projects_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get project statistics

    **Requires:** Authentication

    **Returns:**
    - Total projects by status
    - Projects by service type
    - Average budget
    - Total proposal count

    **For Clients:** Shows their own projects
    **For Admins:** Shows all projects in tenant
    """
    # If client, show only their projects
    client_id = None
    if current_user["user_type"] == "client":
        client_id = current_user["user_id"]

    stats = await project_service.get_project_statistics(
        db=db,
        tenant_id=current_user["tenant_id"],
        client_id=client_id
    )

    return stats


# ============================================================================
# PHASE 5: Competency-Based Specialist Matching
# ============================================================================

@router.get("/{project_id}/matching-specialists")
async def find_matching_specialists_for_project(
    project_id: int,
    min_match_score: int = Query(70, ge=0, le=100, description="Minimum competency match score (0-100)"),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Find specialists matching project requirements

    PHASE 5: Integration feature - uses competency matching algorithm

    Matching criteria:
    - Specialist competency scores vs project required_competencies
    - Returns match score 0-100
    - Filters by min_match_score threshold
    - Includes matching/missing competencies breakdown

    Algorithm uses:
    - marketplace.calculate_competency_match() SQL function
    - specialist.competency_scores (from Learning Service)
    - project.required_competencies (from Phase 4)
    """
    from sqlalchemy import select, text
    from database.models import Project, Specialist

    # Get project
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify access (project owner or admin)
    if str(project.client_id) != current_user['user_id'] and current_user.get('user_type') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    # Use SQL function to find matching specialists (from migration 008)
    query = text("""
        SELECT
            s.id as specialist_id,
            s.name as specialist_name,
            s.title,
            s.hourly_rate,
            s.currency,
            s.rating,
            s.is_verified,
            marketplace.calculate_competency_match(
                s.competency_scores,
                :required_competencies
            ) as match_score,
            s.competency_scores as competencies
        FROM marketplace.specialists s
        WHERE s.active = true
          AND s.is_verified = true
          AND s.availability_status = 'available'
          AND marketplace.calculate_competency_match(
                s.competency_scores,
                :required_competencies
              ) >= :min_match_score
        ORDER BY match_score DESC
        LIMIT :limit
    """)

    result = await db.execute(
        query,
        {
            "required_competencies": project.required_competencies or [],
            "min_match_score": min_match_score,
            "limit": limit
        }
    )

    matching_specialists = []
    for row in result:
        # Calculate matching/missing competencies breakdown
        specialist_comps = row.competencies or {}
        required_comps = project.required_competencies or []

        matching_comps = {}
        missing_comps = []

        for req in required_comps:
            area = req.get('area')
            required_level = req.get('min_level')

            if area in specialist_comps:
                specialist_comp = specialist_comps[area]
                matching_comps[area] = {
                    "required": required_level,
                    "specialist": specialist_comp.get('level'),
                    "score": specialist_comp.get('score', 0)
                }
            else:
                missing_comps.append(area)

        matching_specialists.append({
            "specialist_id": row.specialist_id,
            "name": row.specialist_name,
            "title": row.title,
            "hourly_rate": float(row.hourly_rate) if row.hourly_rate else None,
            "currency": row.currency,
            "rating": float(row.rating) if row.rating else 0.0,
            "is_verified": row.is_verified,
            "match_score": row.match_score,
            "matching_competencies": matching_comps,
            "missing_competencies": missing_comps
        })

    return {
        "project_id": project_id,
        "project_title": project.title,
        "required_competencies": project.required_competencies,
        "min_match_score": min_match_score,
        "total_matches": len(matching_specialists),
        "matching_specialists": matching_specialists
    }


@router.post("/{project_id}/set-competency-requirements")
async def set_project_competency_requirements(
    project_id: int,
    requirements: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Set competency requirements for project

    PHASE 5: Integration feature

    Body:
    {
        "required_competencies": [
            {"area": "bc_planning", "min_level": "advanced", "is_mandatory": true, "weight": 8},
            {"area": "risk_assessment", "min_level": "intermediate", "is_mandatory": true, "weight": 6}
        ]
    }

    Stores in:
    - project.required_competencies (JSONB, Phase 4 column)
    """
    from sqlalchemy import select
    from database.models import Project

    # Get project
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if str(project.client_id) != current_user['user_id'] and current_user.get('user_type') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update requirements (Phase 4 column)
    required_competencies = requirements.get('required_competencies', [])

    # Validate structure
    for req in required_competencies:
        if 'area' not in req or 'min_level' not in req:
            raise HTTPException(
                status_code=400,
                detail="Each competency requirement must have 'area' and 'min_level'"
            )

    project.required_competencies = required_competencies

    await db.commit()
    await db.refresh(project)

    return {
        "success": True,
        "project_id": project_id,
        "required_competencies": project.required_competencies,
        "total_requirements": len(required_competencies)
    }
