"""
Specialists API Router
Endpoints for specialist profile management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.connection import get_db
from api.dependencies import (
    get_current_user,
    get_current_user_optional,
    require_specialist,
    require_verified_specialist,
    require_admin,
    get_db_with_context,
    verify_specialist_ownership
)
from schemas.specialist import (
    SpecialistCreate,
    SpecialistUpdate,
    SpecialistResponse,
    CertificationCreate,
    CertificationResponse,
    PortfolioItemCreate,
    PortfolioItemResponse,
    SpecialistSearchFilters
)
from services.specialist_service import specialist_service
from integrations.portal_client import portal_client

router = APIRouter(prefix="/api/marketplace/specialists", tags=["specialists"])


# ============================================================================
# Specialist Profile Endpoints
# ============================================================================

@router.post("", response_model=SpecialistResponse, status_code=201)
async def create_specialist_profile(
    specialist_data: SpecialistCreate,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Create new specialist profile

    **Requires:** Specialist or Admin role

    **Business Rules:**
    - One active profile per user
    - Initial profile_completion calculated automatically
    - Starts as unverified (admin verification required)
    """
    try:
        specialist = await specialist_service.create_specialist(
            db=db,
            specialist_data=specialist_data,
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"]
        )
        return specialist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[SpecialistResponse])
async def search_specialists(
    # Search filters
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    specializations: Optional[str] = Query(None, description="Comma-separated specializations"),
    industries: Optional[str] = Query(None, description="Comma-separated industries"),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    verified_only: bool = Query(True, description="Only show verified specialists"),
    availability_status: Optional[str] = Query(None),
    min_hourly_rate: Optional[float] = Query(None, ge=0),
    max_hourly_rate: Optional[float] = Query(None, ge=0),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search in name, title, bio"),
    # Pagination
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    # Dependencies
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Search specialists with filters

    **Public endpoint** - No authentication required for basic search

    **Filters:**
    - skills: Match any skill (OR logic)
    - specializations: Match any specialization
    - industries: Match any industry
    - min_rating: Minimum rating (0-5)
    - verified_only: Only verified specialists (default: true)
    - availability_status: available, busy, unavailable
    - hourly_rate range
    - location: country, city
    - search: Full-text search in name/title/bio

    **Returns:** List of specialists sorted by rating DESC
    """
    # Parse comma-separated values
    skills_list = skills.split(",") if skills else None
    specializations_list = specializations.split(",") if specializations else None
    industries_list = industries.split(",") if industries else None

    filters = SpecialistSearchFilters(
        skills=skills_list,
        specializations=specializations_list,
        industries=industries_list,
        min_rating=min_rating,
        verified_only=verified_only,
        availability_status=availability_status,
        min_hourly_rate=min_hourly_rate,
        max_hourly_rate=max_hourly_rate,
        country=country,
        city=city,
        search=search,
        offset=offset,
        limit=limit
    )

    # Get tenant_id from user or default (for public access)
    tenant_id = current_user["tenant_id"] if current_user else "public"

    specialists = await specialist_service.search_specialists(db, filters, tenant_id)
    return specialists


@router.get("/me", response_model=SpecialistResponse)
async def get_my_specialist_profile(
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get current user's specialist profile

    **Requires:** Specialist or Admin role
    """
    specialist = await specialist_service.get_specialist_by_user(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"]
    )

    if not specialist:
        raise HTTPException(
            status_code=404,
            detail="Specialist profile not found. Create one first."
        )

    return specialist


@router.get("/{specialist_id}", response_model=SpecialistResponse)
async def get_specialist(
    specialist_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specialist profile by ID

    **Public endpoint** - No authentication required

    **Returns:** Full specialist profile with certifications and portfolio
    """
    tenant_id = current_user["tenant_id"] if current_user else "public"

    specialist = await specialist_service.get_specialist(
        db=db,
        specialist_id=specialist_id,
        tenant_id=tenant_id
    )

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    # Get related Portal content (knowledge articles about their expertise)
    try:
        if specialist.specializations and len(specialist.specializations) > 0:
            articles = await portal_client.search_knowledge_articles(
                query=specialist.specializations[0],
                limit=3
            )
            # Could add to response metadata
    except Exception as e:
        pass  # Don't fail if Portal is unavailable

    return specialist


@router.put("/{specialist_id}", response_model=SpecialistResponse)
async def update_specialist(
    specialist_id: int,
    specialist_data: SpecialistUpdate,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Update specialist profile

    **Requires:** Specialist ownership or Admin role

    **Business Rules:**
    - Can only update own profile (unless admin)
    - Cannot change verification status (admin only)
    - Profile completion recalculated automatically
    """
    # Verify ownership
    await verify_specialist_ownership(specialist_id, current_user, db)

    try:
        specialist = await specialist_service.update_specialist(
            db=db,
            specialist_id=specialist_id,
            specialist_data=specialist_data,
            tenant_id=current_user["tenant_id"],
            user_id=current_user["user_id"]
        )
        return specialist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{specialist_id}", status_code=204)
async def deactivate_specialist(
    specialist_id: int,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Deactivate specialist profile (soft delete)

    **Requires:** Specialist ownership or Admin role

    **Note:** This sets active=False, doesn't delete the record
    """
    # Verify ownership
    await verify_specialist_ownership(specialist_id, current_user, db)

    specialist = await specialist_service.get_specialist(
        db, specialist_id, current_user["tenant_id"]
    )

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    specialist.active = False
    await db.commit()


# ============================================================================
# Admin Endpoints
# ============================================================================

@router.post("/{specialist_id}/verify", response_model=SpecialistResponse)
async def verify_specialist(
    specialist_id: int,
    verified: bool,
    verification_notes: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Verify or unverify specialist

    **Requires:** Admin role

    **Business Rules:**
    - Only admins can verify specialists
    - Verification status affects proposal eligibility
    - Should validate certifications before verifying
    """
    try:
        specialist = await specialist_service.verify_specialist(
            db=db,
            specialist_id=specialist_id,
            verified=verified,
            verified_by=current_user["user_id"],
            verification_notes=verification_notes,
            tenant_id=current_user["tenant_id"]
        )
        return specialist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Certifications
# ============================================================================

@router.post("/{specialist_id}/certifications", response_model=CertificationResponse, status_code=201)
async def add_certification(
    specialist_id: int,
    cert_data: CertificationCreate,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Add certification to specialist profile

    **Requires:** Specialist ownership

    **Business Rules:**
    - Updates profile completion
    - Starts as unverified (admin verification needed)
    """
    # Verify ownership
    await verify_specialist_ownership(specialist_id, current_user, db)

    try:
        certification = await specialist_service.add_certification(
            db=db,
            specialist_id=specialist_id,
            cert_data=cert_data,
            tenant_id=current_user["tenant_id"]
        )
        return certification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{specialist_id}/certifications/{cert_id}", status_code=204)
async def delete_certification(
    specialist_id: int,
    cert_id: int,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Delete certification

    **Requires:** Specialist ownership
    """
    # Verify ownership
    await verify_specialist_ownership(specialist_id, current_user, db)

    try:
        await specialist_service.delete_certification(
            db=db,
            cert_id=cert_id,
            specialist_id=specialist_id,
            tenant_id=current_user["tenant_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Portfolio
# ============================================================================

@router.post("/{specialist_id}/portfolio", response_model=PortfolioItemResponse, status_code=201)
async def add_portfolio_item(
    specialist_id: int,
    portfolio_data: PortfolioItemCreate,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Add portfolio item

    **Requires:** Specialist ownership

    **Business Rules:**
    - Updates profile completion
    - Images and documents URLs should be validated
    """
    # Verify ownership
    await verify_specialist_ownership(specialist_id, current_user, db)

    try:
        portfolio = await specialist_service.add_portfolio_item(
            db=db,
            specialist_id=specialist_id,
            portfolio_data=portfolio_data,
            tenant_id=current_user["tenant_id"]
        )
        return portfolio
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{specialist_id}/portfolio/{portfolio_id}", status_code=204)
async def delete_portfolio_item(
    specialist_id: int,
    portfolio_id: int,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Delete portfolio item

    **Requires:** Specialist ownership
    """
    # Verify ownership
    await verify_specialist_ownership(specialist_id, current_user, db)

    try:
        await specialist_service.delete_portfolio_item(
            db=db,
            portfolio_id=portfolio_id,
            specialist_id=specialist_id,
            tenant_id=current_user["tenant_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Integration Endpoints
# ============================================================================

@router.get("/{specialist_id}/knowledge-articles")
async def get_specialist_knowledge(
    specialist_id: int,
    limit: int = Query(5, ge=1, le=20),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get related knowledge articles from Portal

    **Public endpoint**

    Shows knowledge articles related to specialist's expertise

    **Integration:** Portal Service
    """
    tenant_id = current_user["tenant_id"] if current_user else "public"

    specialist = await specialist_service.get_specialist(db, specialist_id, tenant_id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    # Search Portal for related content
    articles = []
    try:
        if specialist.specializations and len(specialist.specializations) > 0:
            articles = await portal_client.search_knowledge_articles(
                query=specialist.specializations[0],
                limit=limit
            )
    except Exception as e:
        # Don't fail if Portal is unavailable
        pass

    return {
        "specialist_id": specialist_id,
        "specializations": specialist.specializations,
        "articles": articles
    }


@router.get("/{specialist_id}/community-reputation")
async def get_specialist_community_reputation(
    specialist_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get specialist's Portal community reputation

    **Requires:** Authentication

    Shows forum reputation, badges, contributions

    **Integration:** Portal Service
    """
    specialist = await specialist_service.get_specialist(
        db, specialist_id, current_user["tenant_id"]
    )
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    # Get Portal reputation
    reputation = None
    try:
        # Need token to access Portal
        token = current_user.get("token")  # Would need to pass this through
        # reputation = await portal_client.get_user_reputation(
        #     user_id=specialist.user_id,
        #     token=token
        # )
    except Exception as e:
        pass

    return {
        "specialist_id": specialist_id,
        "user_id": str(specialist.user_id),
        "portal_reputation": reputation or {"message": "Portal integration pending"}
    }


# ============================================================================
# PHASE 5: Specialist Verification via Governance
# ============================================================================

@router.post("/{specialist_id}/verify-via-governance")
async def verify_specialist_via_governance(
    specialist_id: int,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify specialist via Governance Service

    PHASE 5: Integration feature

    Checks:
    - Person has BCM role in Governance
    - Person has required competencies (≥3)

    Auto-sets:
    - is_verified = True
    - verified_by_role_id = role ID from governance
    - verification_source = "governance_role"
    """
    from integrations.governance_client import get_governance_client
    from sqlalchemy import select
    from database.models import Specialist

    # Get specialist
    result = await db.execute(
        select(Specialist).where(Specialist.id == specialist_id)
    )
    specialist = result.scalar_one_or_none()

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    # Get JWT token
    token = current_user.get('token', '')

    # Verify via Governance Service
    governance_client = get_governance_client()
    verification_result = await governance_client.verify_specialist(
        person_id=str(specialist.user_id),
        token=token
    )

    if verification_result.get('is_verified'):
        # Update specialist verification
        specialist.is_verified = True
        specialist.verified_by_role_id = verification_result.get('role_code')
        specialist.verification_source = verification_result.get('verification_source')
        specialist.verification_notes = verification_result.get('notes')

        await db.commit()
        await db.refresh(specialist)

        return {
            "success": True,
            "specialist_id": specialist_id,
            "verification_result": verification_result,
            "message": f"Specialist verified via {verification_result.get('verification_source')}"
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Specialist verification failed: {verification_result.get('notes', 'No BCM role or competencies')}"
        )


@router.post("/{specialist_id}/sync-competencies")
async def sync_specialist_competencies(
    specialist_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync specialist competencies from Learning Service

    PHASE 5: Integration feature

    Fetches:
    - Certifications from Learning Service
    - Competency scores (training + certifications)

    Updates:
    - specialist.certifications_jsonb
    - specialist.competency_scores
    - specialist.training_programs_completed
    """
    from integrations.learning_client import get_learning_client
    from sqlalchemy import select
    from database.models import Specialist

    # Get specialist
    result = await db.execute(
        select(Specialist).where(Specialist.id == specialist_id)
    )
    specialist = result.scalar_one_or_none()

    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    # Verify ownership (only specialist or admin)
    if str(specialist.user_id) != current_user['user_id'] and current_user.get('user_type') != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get JWT token
    token = current_user.get('token', '')

    # Fetch Learning Service data
    learning_client = get_learning_client()
    certifications = await learning_client.get_person_certifications(
        person_id=str(specialist.user_id),
        token=token
    )
    competencies = await learning_client.get_person_competencies(
        person_id=str(specialist.user_id),
        token=token
    )

    # Update specialist (Phase 4 columns)
    specialist.certifications_jsonb = certifications
    specialist.competency_scores = competencies
    specialist.training_programs_completed = sum(
        comp.get('trainings_count', 0) for comp in competencies.values()
    ) if isinstance(competencies, dict) else 0

    # Update last_training_date if available
    if certifications:
        issued_dates = [cert.get('issued_date') for cert in certifications if cert.get('issued_date')]
        if issued_dates:
            specialist.last_training_date = max(issued_dates)

    await db.commit()
    await db.refresh(specialist)

    return {
        "success": True,
        "specialist_id": specialist_id,
        "certifications_count": len(certifications),
        "competencies_count": len(competencies) if isinstance(competencies, dict) else 0,
        "competencies": competencies
    }
