"""
Contributions API

Endpoints for managing case contributions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.auth import get_current_user
from shared.eventbus import get_eventbus_client
from ..services.contribution_service import ContributionService
from ..services.anonymizer import Anonymizer
from ..services.workflow_integration_service import WorkflowIntegrationService
from ..services.peer_review_service import PeerReviewService
from ..services.reputation_engine import ReputationEngine
from ..models.database import CaseContribution, ContributionStatus

router = APIRouter()


# --- Pydantic Models ---

class ContributionCreate(BaseModel):
    """Request to create contribution"""
    workflow_id: Optional[str] = None
    case_data: dict = Field(..., description="Anonymized case data")
    module: str = Field(..., description="BCM module (bia, risk, etc.)")
    additional_notes: Optional[str] = None


class ContributionResponse(BaseModel):
    """Contribution response"""
    id: UUID
    contributor_id: UUID
    module: str
    status: str
    submitted_at: str
    review_deadline: Optional[str] = None
    reviewers_count: int
    reviews_completed: int
    approved_at: Optional[str] = None

    class Config:
        from_attributes = True


class ContributionDetail(ContributionResponse):
    """Detailed contribution info"""
    case_data: dict
    tags: List[str]
    original_org_type: str


class AnonymizationPreview(BaseModel):
    """Preview of anonymized case"""
    workflow_id: str
    anonymized_preview: dict
    original_org_removed: bool
    original_users_removed: bool
    original_dates_generalized: bool
    risk_assessment: dict


# --- Dependencies ---

async def get_contribution_service(
    db: AsyncSession = Depends(get_db)
) -> ContributionService:
    """Get ContributionService instance"""
    anonymizer = Anonymizer()
    return ContributionService(
        db=db,
        anonymizer=anonymizer,
        case_library=None  # TODO: Inject actual case library
    )


async def get_workflow_integration(
    db: AsyncSession = Depends(get_db),
    contribution_service: ContributionService = Depends(get_contribution_service)
) -> WorkflowIntegrationService:
    """Get WorkflowIntegrationService instance"""
    eventbus = get_eventbus_client()
    anonymizer = Anonymizer()

    reputation_engine = ReputationEngine(db=db, eventbus=eventbus)
    peer_review_service = PeerReviewService(
        db=db,
        eventbus=eventbus,
        reputation_engine=reputation_engine
    )

    return WorkflowIntegrationService(
        db=db,
        eventbus=eventbus,
        anonymizer=anonymizer,
        contribution_service=contribution_service,
        peer_review_service=peer_review_service
    )


# --- Endpoints ---

@router.post("", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    request: ContributionCreate,
    current_user: dict = Depends(get_current_user),
    service: ContributionService = Depends(get_contribution_service)
):
    """
    Submit new case contribution

    Flow:
    1. Validates case data
    2. Creates contribution record
    3. Assigns peer reviewers
    4. Returns contribution ID
    """

    try:
        contribution_id = await service.submit_case(
            contributor_id=current_user['user_id'],
            case_data=request.case_data,
            module=request.module
        )

        # Get created contribution
        db = service.db
        contribution = await db.get(CaseContribution, UUID(contribution_id))

        return ContributionResponse(
            id=contribution.id,
            contributor_id=contribution.contributor_id,
            module=contribution.module,
            status=contribution.status.value,
            submitted_at=contribution.submitted_at.isoformat(),
            review_deadline=contribution.review_deadline.isoformat() if contribution.review_deadline else None,
            reviewers_count=len(contribution.reviewers) if contribution.reviewers else 0,
            reviews_completed=0,  # Just created
            approved_at=None
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/my", response_model=List[ContributionResponse])
async def get_my_contributions(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's contributions"""

    from sqlalchemy import select

    result = await db.execute(
        select(CaseContribution)
        .where(CaseContribution.contributor_id == UUID(current_user['user_id']))
        .order_by(CaseContribution.submitted_at.desc())
    )

    contributions = result.scalars().all()

    return [
        ContributionResponse(
            id=c.id,
            contributor_id=c.contributor_id,
            module=c.module,
            status=c.status.value,
            submitted_at=c.submitted_at.isoformat(),
            review_deadline=c.review_deadline.isoformat() if c.review_deadline else None,
            reviewers_count=len(c.reviewers) if c.reviewers else 0,
            reviews_completed=0,  # TODO: Count actual reviews
            approved_at=c.approved_at.isoformat() if c.approved_at else None
        )
        for c in contributions
    ]


@router.get("/{contribution_id}", response_model=ContributionDetail)
async def get_contribution(
    contribution_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get contribution details

    Access:
    - Contributors can see their own contributions
    - Assigned reviewers can see contributions
    - Admins can see all
    """

    contribution = await db.get(CaseContribution, contribution_id)

    if not contribution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contribution not found"
        )

    user_id = UUID(current_user['user_id'])

    # Check access
    is_contributor = contribution.contributor_id == user_id
    is_reviewer = user_id in (contribution.reviewers or [])
    is_admin = current_user.get('is_admin', False)
    is_approved = contribution.status == ContributionStatus.APPROVED

    if not (is_contributor or is_reviewer or is_admin or is_approved):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return ContributionDetail(
        id=contribution.id,
        contributor_id=contribution.contributor_id,
        module=contribution.module,
        status=contribution.status.value,
        submitted_at=contribution.submitted_at.isoformat(),
        review_deadline=contribution.review_deadline.isoformat() if contribution.review_deadline else None,
        reviewers_count=len(contribution.reviewers) if contribution.reviewers else 0,
        reviews_completed=0,  # TODO: Count
        approved_at=contribution.approved_at.isoformat() if contribution.approved_at else None,
        case_data=contribution.case_data,
        tags=contribution.tags or [],
        original_org_type=contribution.original_org_type or "unknown"
    )


@router.delete("/{contribution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_contribution(
    contribution_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Withdraw contribution (only before approval)
    """

    contribution = await db.get(CaseContribution, contribution_id)

    if not contribution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contribution not found"
        )

    # Check ownership
    if contribution.contributor_id != UUID(current_user['user_id']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only withdraw your own contributions"
        )

    # Check status
    if contribution.status not in [ContributionStatus.PENDING_REVIEW, ContributionStatus.IN_REVIEW]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only withdraw pending or in-review contributions"
        )

    # Delete
    await db.delete(contribution)
    await db.commit()


@router.post("/preview-anonymization", response_model=AnonymizationPreview)
async def preview_anonymization(
    workflow_id: str,
    current_user: dict = Depends(get_current_user),
    service: WorkflowIntegrationService = Depends(get_workflow_integration)
):
    """
    Preview how workflow will be anonymized before submitting

    Returns:
    - Anonymized data preview
    - Risk assessment
    - What was removed/generalized
    """

    try:
        preview = await service.preview_anonymized_case(
            user_id=UUID(current_user['user_id']),
            workflow_id=workflow_id
        )

        return preview

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/from-workflow/{workflow_id}", response_model=ContributionResponse)
async def create_contribution_from_workflow(
    workflow_id: str,
    additional_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: WorkflowIntegrationService = Depends(get_workflow_integration),
    db: AsyncSession = Depends(get_db)
):
    """
    Create contribution from completed workflow

    User accepts contribution offer
    """

    try:
        contribution_id = await service.submit_contribution_from_workflow(
            user_id=UUID(current_user['user_id']),
            workflow_id=workflow_id,
            module="bia",  # TODO: Get from workflow
            additional_notes=additional_notes
        )

        # Get created contribution
        contribution = await db.get(CaseContribution, UUID(contribution_id))

        return ContributionResponse(
            id=contribution.id,
            contributor_id=contribution.contributor_id,
            module=contribution.module,
            status=contribution.status.value,
            submitted_at=contribution.submitted_at.isoformat(),
            review_deadline=contribution.review_deadline.isoformat() if contribution.review_deadline else None,
            reviewers_count=len(contribution.reviewers) if contribution.reviewers else 0,
            reviews_completed=0,
            approved_at=None
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
