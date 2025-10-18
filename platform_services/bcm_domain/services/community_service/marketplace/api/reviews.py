"""
Reviews API Router
Endpoints for client reviews and specialist responses
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.connection import get_db
from api.dependencies import (
    get_current_user,
    get_current_user_optional,
    require_client,
    require_specialist,
    require_admin,
    get_db_with_context
)
from schemas.review import (
    ReviewCreate,
    ReviewResponse,
    SpecialistResponseCreate
)
from services.review_service import review_service

router = APIRouter(prefix="/api/marketplace/reviews", tags=["reviews"])


# ============================================================================
# Review Management Endpoints (Client)
# ============================================================================

@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    review_data: ReviewCreate,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Create review for specialist (Client action)

    **Requires:** Client role

    **Business Rules:**
    - Can only review after project completion
    - One review per project-specialist pair
    - Reviewer must be project client
    - Rating 1-5 required
    - All category ratings optional but must be 1-5 if provided:
      - communication_rating
      - quality_rating
      - professionalism_rating
      - timeliness_rating
    - Updates specialist overall rating automatically
    - Auto-verified (since client must own project)

    **Flow:**
    1. Project completed
    2. Client writes review
    3. Specialist rating updated automatically
    4. Specialist can respond to review
    """
    try:
        review = await review_service.create_review(
            db=db,
            review_data=review_data,
            reviewer_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"]
        )
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ReviewResponse])
async def list_reviews(
    # Filters
    specialist_id: Optional[int] = Query(None, description="Filter by specialist"),
    project_id: Optional[int] = Query(None, description="Filter by project"),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    verified_only: bool = Query(False),
    # Pagination
    limit: int = Query(20, ge=1, le=100),
    # Dependencies
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    List reviews with filters

    **Public endpoint** - No authentication required

    **Filters:**
    - specialist_id: Show all reviews for a specialist
    - project_id: Show review for a project
    - min_rating: Minimum rating filter
    - verified_only: Only show verified reviews

    **Returns:** Public reviews only (is_public=True)
    """
    tenant_id = current_user["tenant_id"] if current_user else "public"

    # If specialist_id provided, get specialist reviews
    if specialist_id:
        reviews = await review_service.get_reviews_by_specialist(
            db=db,
            specialist_id=specialist_id,
            tenant_id=tenant_id,
            public_only=True,
            limit=limit
        )

        # Apply min_rating filter if provided
        if min_rating:
            reviews = [r for r in reviews if r.rating >= min_rating]

        # Apply verified_only filter
        if verified_only:
            reviews = [r for r in reviews if r.is_verified]

        return reviews

    # If project_id provided, get project reviews
    if project_id:
        reviews = await review_service.get_reviews_by_project(
            db=db,
            project_id=project_id,
            tenant_id=tenant_id
        )

        # Apply filters
        if min_rating:
            reviews = [r for r in reviews if r.rating >= min_rating]
        if verified_only:
            reviews = [r for r in reviews if r.is_verified]

        return reviews

    # Otherwise, get recent reviews
    reviews = await review_service.get_recent_reviews(
        db=db,
        tenant_id=tenant_id,
        limit=limit
    )

    # Apply filters
    if min_rating:
        reviews = [r for r in reviews if r.rating >= min_rating]
    if verified_only:
        reviews = [r for r in reviews if r.is_verified]

    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get review by ID

    **Public endpoint** for public reviews

    **Access Control:**
    - Public reviews: Anyone can view
    - Private reviews: Only reviewer, specialist, or admin
    """
    tenant_id = current_user["tenant_id"] if current_user else "public"

    review = await review_service.get_review(
        db=db,
        review_id=review_id,
        tenant_id=tenant_id
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Check access for private reviews
    if not review.is_public:
        if not current_user:
            raise HTTPException(
                status_code=403,
                detail="This review is private"
            )

        user_type = current_user["user_type"]
        user_id = current_user["user_id"]

        # Allow access for: reviewer, specialist, admin
        is_reviewer = str(review.reviewer_id) == str(user_id)
        is_specialist = str(review.specialist.user_id) == str(user_id)
        is_admin = user_type == "admin"

        if not (is_reviewer or is_specialist or is_admin):
            raise HTTPException(
                status_code=403,
                detail="You don't have access to this private review"
            )

    return review


# ============================================================================
# Specialist Response
# ============================================================================

@router.post("/{review_id}/respond", response_model=ReviewResponse)
async def respond_to_review(
    review_id: int,
    response_data: SpecialistResponseCreate,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Specialist responds to review

    **Requires:** Specialist role (must be reviewed specialist)

    **Business Rules:**
    - Only the reviewed specialist can respond
    - Can respond only once
    - Sets responded_at timestamp
    - Emits review.responded event

    **Use Cases:**
    - Thank client for positive review
    - Address concerns in negative review
    - Provide context or clarification
    - Show professionalism
    """
    # Get specialist_id
    from services.specialist_service import specialist_service

    specialist = await specialist_service.get_specialist_by_user(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"]
    )

    if not specialist:
        raise HTTPException(
            status_code=404,
            detail="Specialist profile not found"
        )

    try:
        review = await review_service.respond_to_review(
            db=db,
            review_id=review_id,
            response_data=response_data,
            specialist_id=specialist.id,
            tenant_id=current_user["tenant_id"],
            user_id=current_user["user_id"]
        )
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Specialist Reviews & Statistics
# ============================================================================

@router.get("/specialists/{specialist_id}/reviews", response_model=List[ReviewResponse])
async def get_specialist_reviews(
    specialist_id: int,
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all reviews for a specialist

    **Public endpoint**

    Shows specialist's track record and reputation

    **Returns:** Public reviews sorted by created_at DESC
    """
    tenant_id = current_user["tenant_id"] if current_user else "public"

    reviews = await review_service.get_reviews_by_specialist(
        db=db,
        specialist_id=specialist_id,
        tenant_id=tenant_id,
        public_only=True,
        limit=limit
    )

    return reviews


@router.get("/specialists/{specialist_id}/stats")
async def get_specialist_review_stats(
    specialist_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get review statistics for specialist

    **Public endpoint**

    **Returns:**
    - Overall rating and count
    - Rating distribution (5 stars, 4 stars, 3 stars, 2 stars, 1 star)
    - Category averages:
      - communication
      - quality
      - professionalism
      - timeliness
    - Response rate (% of reviews with specialist response)

    **Use Cases:**
    - Specialist profile page
    - Client decision-making
    - Marketplace analytics
    """
    tenant_id = current_user["tenant_id"] if current_user else "public"

    stats = await review_service.get_review_statistics(
        db=db,
        specialist_id=specialist_id,
        tenant_id=tenant_id
    )

    return stats


# ============================================================================
# Admin Moderation
# ============================================================================

@router.post("/{review_id}/hide", response_model=ReviewResponse)
async def hide_review(
    review_id: int,
    reason: str = Query(..., description="Reason for hiding"),
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Hide review (Admin action)

    **Requires:** Admin role

    **Business Rules:**
    - Only admins can hide reviews
    - Sets is_public = False
    - Does NOT delete - keeps for records
    - Recalculates specialist rating (excluding hidden review)

    **Use Cases:**
    - Inappropriate content
    - Spam or fake review
    - Violation of terms of service
    - Legal/compliance issues
    """
    try:
        review = await review_service.hide_review(
            db=db,
            review_id=review_id,
            tenant_id=current_user["tenant_id"],
            admin_id=current_user["user_id"],
            reason=reason
        )
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{review_id}/verify", response_model=ReviewResponse)
async def verify_review(
    review_id: int,
    verified: bool = Query(..., description="Verification status"),
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Verify or unverify review (Admin action)

    **Requires:** Admin role

    **Use Cases:**
    - Mark legitimate reviews as verified (trust badge)
    - Flag suspicious reviews as unverified
    - Quality control

    **Note:** Most reviews auto-verified since client must own project
    """
    try:
        review = await review_service.verify_review(
            db=db,
            review_id=review_id,
            tenant_id=current_user["tenant_id"],
            verified=verified
        )
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# My Reviews (Client view)
# ============================================================================

@router.get("/my/written")
async def get_my_written_reviews(
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get reviews written by me (Client view)

    **Requires:** Client role

    **Returns:** All reviews written by current user

    **Use Cases:**
    - Client dashboard
    - Review history
    - Track feedback given
    """
    reviews = await review_service.get_reviews_by_client(
        db=db,
        client_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        limit=limit
    )

    return reviews
