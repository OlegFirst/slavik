"""
Peer Reviews API

Endpoints for peer review process
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.auth import get_current_user
from shared.eventbus import get_eventbus_client
from ..services.peer_review_service import PeerReviewService
from ..services.reputation_engine import ReputationEngine
from ..models.database import PeerReview, CaseContribution

router = APIRouter()


# --- Pydantic Models ---

class ReviewSubmit(BaseModel):
    """Submit peer review"""
    contribution_id: UUID
    approved: bool = Field(..., description="Approve or reject contribution")
    quality_score: int = Field(..., ge=1, le=10, description="Quality score 1-10")
    feedback: str = Field(..., min_length=10, description="Detailed feedback")
    suggested_improvements: str | None = None

    # Quality checks
    anonymization_ok: bool = Field(default=True, description="Anonymization adequate")
    relevance_ok: bool = Field(default=True, description="Relevant to module")
    completeness_ok: bool = Field(default=True, description="Complete information")
    lessons_clear: bool = Field(default=True, description="Clear lessons learned")


class ReviewResponse(BaseModel):
    """Peer review response"""
    id: UUID
    contribution_id: UUID
    reviewer_id: UUID
    approved: bool
    quality_score: int
    reviewed_at: str

    class Config:
        from_attributes = True


class ReviewDetail(ReviewResponse):
    """Detailed review info"""
    feedback: str
    suggested_improvements: str | None
    anonymization_ok: bool
    relevance_ok: bool
    completeness_ok: bool
    lessons_clear: bool


class PendingReviewItem(BaseModel):
    """Pending review item"""
    contribution_id: UUID
    module: str
    submitted_at: str
    review_deadline: str
    days_remaining: int
    case_summary: str


# --- Dependencies ---

async def get_peer_review_service(
    db: AsyncSession = Depends(get_db)
) -> PeerReviewService:
    """Get PeerReviewService instance"""
    eventbus = get_eventbus_client()
    reputation_engine = ReputationEngine(db=db, eventbus=eventbus)

    return PeerReviewService(
        db=db,
        eventbus=eventbus,
        reputation_engine=reputation_engine
    )


# --- Endpoints ---

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def submit_review(
    request: ReviewSubmit,
    current_user: dict = Depends(get_current_user),
    service: PeerReviewService = Depends(get_peer_review_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit peer review for contribution

    Requirements:
    - Must be assigned as reviewer
    - Can only review once
    - Must provide feedback if rejecting
    """

    try:
        peer_review = await service.submit_review(
            reviewer_id=UUID(current_user['user_id']),
            contribution_id=request.contribution_id,
            review_data={
                'approved': request.approved,
                'quality_score': request.quality_score,
                'feedback': request.feedback,
                'suggested_improvements': request.suggested_improvements,
                'anonymization_ok': request.anonymization_ok,
                'relevance_ok': request.relevance_ok,
                'completeness_ok': request.completeness_ok,
                'lessons_clear': request.lessons_clear
            }
        )

        return ReviewResponse(
            id=peer_review.id,
            contribution_id=peer_review.contribution_id,
            reviewer_id=peer_review.reviewer_id,
            approved=peer_review.approved,
            quality_score=peer_review.quality_score,
            reviewed_at=peer_review.reviewed_at.isoformat()
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/pending", response_model=List[PendingReviewItem])
async def get_pending_reviews(
    current_user: dict = Depends(get_current_user),
    service: PeerReviewService = Depends(get_peer_review_service)
):
    """
    Get contributions pending review by current user

    Returns list sorted by deadline (urgent first)
    """

    from datetime import datetime

    contributions = await service.get_pending_reviews(
        user_id=UUID(current_user['user_id'])
    )

    items = []
    for contrib in contributions:
        # Calculate days remaining
        if contrib.review_deadline:
            days_remaining = (contrib.review_deadline - datetime.utcnow()).days
        else:
            days_remaining = 0

        # Extract summary from case data
        case_summary = contrib.case_data.get('summary', 'No summary available')
        if len(case_summary) > 200:
            case_summary = case_summary[:200] + "..."

        items.append(PendingReviewItem(
            contribution_id=contrib.id,
            module=contrib.module,
            submitted_at=contrib.submitted_at.isoformat(),
            review_deadline=contrib.review_deadline.isoformat() if contrib.review_deadline else "",
            days_remaining=days_remaining,
            case_summary=case_summary
        ))

    return items


@router.get("/my", response_model=List[ReviewDetail])
async def get_my_reviews(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    service: PeerReviewService = Depends(get_peer_review_service)
):
    """Get reviews submitted by current user"""

    reviews = await service.get_user_reviews(
        user_id=UUID(current_user['user_id']),
        limit=limit
    )

    return [
        ReviewDetail(
            id=r.id,
            contribution_id=r.contribution_id,
            reviewer_id=r.reviewer_id,
            approved=r.approved,
            quality_score=r.quality_score,
            reviewed_at=r.reviewed_at.isoformat(),
            feedback=r.feedback or "",
            suggested_improvements=r.suggested_improvements,
            anonymization_ok=r.anonymization_ok,
            relevance_ok=r.relevance_ok,
            completeness_ok=r.completeness_ok,
            lessons_clear=r.lessons_clear
        )
        for r in reviews
    ]


@router.get("/{review_id}", response_model=ReviewDetail)
async def get_review(
    review_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get review details"""

    review = await db.get(PeerReview, review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    # Check access (reviewer or admin)
    user_id = UUID(current_user['user_id'])
    is_reviewer = review.reviewer_id == user_id
    is_admin = current_user.get('is_admin', False)

    if not (is_reviewer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return ReviewDetail(
        id=review.id,
        contribution_id=review.contribution_id,
        reviewer_id=review.reviewer_id,
        approved=review.approved,
        quality_score=review.quality_score,
        reviewed_at=review.reviewed_at.isoformat(),
        feedback=review.feedback or "",
        suggested_improvements=review.suggested_improvements,
        anonymization_ok=review.anonymization_ok,
        relevance_ok=review.relevance_ok,
        completeness_ok=review.completeness_ok,
        lessons_clear=review.lessons_clear
    )
