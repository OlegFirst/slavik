"""
REST API Endpoints - Community Intelligence

Provides endpoints for:
- Case contributions and peer review
- Reputation management
- Living documentation
- Predictive timelines
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ..services.contribution_service import ContributionService
from ..services.living_docs import LivingDocumentationService
from ..services.predictive_timeline import PredictiveTimelineService
from ..services.anonymizer import SmartAnonymizer
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/community", tags=["community"])

# ============= REQUEST/RESPONSE MODELS =============

class CaseSubmissionRequest(BaseModel):
    """Request to submit case for review"""
    case_data: dict
    module: str = Field(..., description="bia, risk, planning")

class CaseSubmissionResponse(BaseModel):
    contribution_id: str
    status: str
    assigned_reviewers: int
    review_deadline: datetime
    estimated_approval_days: int

class PeerReviewRequest(BaseModel):
    """Peer review submission"""
    approved: bool
    quality_score: int = Field(..., ge=1, le=10)
    feedback: Optional[str] = None
    improvements: Optional[dict] = None
    anonymization_ok: bool = True
    relevance_ok: bool = True
    completeness_ok: bool = True
    lessons_clear: bool = True

class PeerReviewResponse(BaseModel):
    review_id: str
    contribution_status: str
    reviews_completed: int
    reviews_needed: int
    reputation_earned: int

class AnnotationRequest(BaseModel):
    """Add interpretation to clause"""
    clause_id: str
    interpretation: str = Field(..., min_length=50)
    industry_specific: Optional[str] = None
    org_size: Optional[str] = None
    examples: Optional[List[str]] = None
    standard: Optional[str] = "ISO22301"

class AnnotationResponse(BaseModel):
    annotation_id: str
    synthesis_triggered: bool

class TimelineRequest(BaseModel):
    """Request predictive timeline"""
    org_id: str
    horizon_months: int = Field(default=12, ge=3, le=24)

class ReputationResponse(BaseModel):
    """User reputation details"""
    user_id: str
    total_points: int
    level: str
    contribution_points: int
    review_points: int
    helpfulness_points: int
    expertise: dict
    badges: List[str]
    contributions_count: int
    reviews_count: int

# ============= DEPENDENCIES =============

async def get_db() -> AsyncSession:
    """Database session dependency"""
    # Implementation depends on your DB setup
    from infrastructure.database.managers.db_manager import get_session
    async with get_session() as session:
        yield session

async def get_current_user(token: str = Depends(lambda: None)):
    """Get authenticated user"""
    # JWT validation - placeholder
    class MockUser:
        id = "00000000-0000-0000-0000-000000000000"
        contributions_count = 0
    return MockUser()

async def get_contribution_service(db: AsyncSession = Depends(get_db)) -> ContributionService:
    """Contribution service dependency"""
    anonymizer = SmartAnonymizer()
    # Get case_library from dependency injection
    case_library = None  # Placeholder
    return ContributionService(db, anonymizer, case_library)

# ============= CASE CONTRIBUTION ENDPOINTS =============

@router.post("/contributions", response_model=CaseSubmissionResponse)
async def submit_case(
    request: CaseSubmissionRequest,
    service: ContributionService = Depends(get_contribution_service),
    user = Depends(get_current_user)
):
    """
    Submit workflow case for community review

    Process:
    1. Auto-anonymize case data
    2. Assign 3 peer reviewers
    3. Return submission details

    Requires: User must have completed at least one workflow
    """

    # Validate user can submit
    if user.contributions_count == 0:
        if not await service.validate_first_submission(request.case_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case data incomplete. First submission requires all fields."
            )

    contribution_id = await service.submit_case(
        contributor_id=str(user.id),
        case_data=request.case_data,
        module=request.module
    )

    contribution = await service.get_contribution(contribution_id)

    return CaseSubmissionResponse(
        contribution_id=contribution_id,
        status=contribution.status.value,
        assigned_reviewers=len(contribution.reviewers),
        review_deadline=contribution.review_deadline,
        estimated_approval_days=7
    )

@router.get("/contributions/{contribution_id}")
async def get_contribution(
    contribution_id: str,
    service: ContributionService = Depends(get_contribution_service),
    user = Depends(get_current_user)
):
    """Get contribution details"""

    contribution = await service.get_contribution(contribution_id)

    if not contribution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Authorization: owner or assigned reviewer
    if str(contribution.contributor_id) != str(user.id) and str(user.id) not in [str(r) for r in contribution.reviewers]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return {
        "id": str(contribution.id),
        "status": contribution.status.value,
        "module": contribution.module,
        "submitted_at": contribution.submitted_at,
        "reviews": [
            {
                "reviewer_id": str(r.reviewer_id),
                "approved": r.approved,
                "quality_score": r.quality_score,
                "feedback": r.feedback
            }
            for r in contribution.reviews
        ],
        "is_owner": str(contribution.contributor_id) == str(user.id)
    }

@router.get("/contributions/pending-reviews")
async def get_pending_reviews(
    service: ContributionService = Depends(get_contribution_service),
    user = Depends(get_current_user)
):
    """Get contributions assigned for review"""

    pending = await service.get_pending_reviews(str(user.id))

    return {
        "count": len(pending),
        "reviews": [
            {
                "contribution_id": str(c.id),
                "module": c.module,
                "submitted_at": c.submitted_at,
                "deadline": c.review_deadline,
                "days_remaining": (c.review_deadline - datetime.utcnow()).days
            }
            for c in pending
        ]
    }

@router.post("/contributions/{contribution_id}/review", response_model=PeerReviewResponse)
async def submit_review(
    contribution_id: str,
    review: PeerReviewRequest,
    service: ContributionService = Depends(get_contribution_service),
    user = Depends(get_current_user)
):
    """
    Submit peer review for contribution

    Requires: User must be assigned reviewer
    """

    contribution = await service.get_contribution(contribution_id)
    if str(user.id) not in [str(r) for r in contribution.reviewers]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not assigned as reviewer"
        )

    review_id = await service.submit_review(
        reviewer_id=str(user.id),
        contribution_id=contribution_id,
        review=review.dict()
    )

    updated = await service.get_contribution(contribution_id)
    reviews_completed = len(updated.reviews)

    return PeerReviewResponse(
        review_id=review_id,
        contribution_status=updated.status.value,
        reviews_completed=reviews_completed,
        reviews_needed=3,
        reputation_earned=5
    )

# ============= REPUTATION ENDPOINTS =============

@router.get("/reputation/{user_id}", response_model=ReputationResponse)
async def get_reputation(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user reputation details"""

    from ..models.database import UserReputation

    reputation = await db.get(UserReputation, user_id)

    if not reputation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return ReputationResponse(
        user_id=str(reputation.user_id),
        total_points=reputation.total_points,
        level=reputation.level,
        contribution_points=reputation.contribution_points,
        review_points=reputation.review_points,
        helpfulness_points=reputation.helpfulness_points,
        expertise=reputation.expertise or {},
        badges=reputation.badges or [],
        contributions_count=reputation.contributions_count,
        reviews_count=reputation.reviews_count
    )

@router.get("/reputation/leaderboard")
async def get_leaderboard(
    limit: int = Query(default=10, le=100),
    category: str = Query(default="total"),
    db: AsyncSession = Depends(get_db)
):
    """Get reputation leaderboard"""

    from ..models.database import UserReputation
    from sqlalchemy import select, desc

    sort_field = {
        'total': UserReputation.total_points,
        'contribution': UserReputation.contribution_points,
        'review': UserReputation.review_points
    }.get(category, UserReputation.total_points)

    result = await db.execute(
        select(UserReputation)
        .order_by(desc(sort_field))
        .limit(limit)
    )

    users = result.scalars().all()

    return {
        "category": category,
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": str(u.user_id),
                "points": getattr(u, f"{category}_points") if category != 'total' else u.total_points,
                "level": u.level,
                "badges": u.badges or []
            }
            for i, u in enumerate(users)
        ]
    }

# ============= LIVING DOCUMENTATION ENDPOINTS =============

async def get_living_docs_service(db: AsyncSession = Depends(get_db)):
    """Get Living Documentation Service instance"""
    from ..services.living_docs import LivingDocumentationService
    # TODO: Inject actual dependencies (knowledge_graph, case_library, llm_client)
    return LivingDocumentationService(db, None, None, None)

@router.post("/annotations", response_model=AnnotationResponse)
async def add_annotation(
    annotation: AnnotationRequest,
    service: LivingDocumentationService = Depends(get_living_docs_service),
    user = Depends(get_current_user)
):
    """
    Add interpretation to standard clause

    Requires: User reputation >= 50 points
    """

    context = {
        'standard': annotation.standard,
        'industry': annotation.industry_specific,
        'org_size': annotation.org_size,
        'examples': annotation.examples or []
    }

    annotation_id = await service.add_annotation(
        user_id=str(user.id),
        clause_id=annotation.clause_id,
        interpretation=annotation.interpretation,
        context=context
    )

    return AnnotationResponse(
        annotation_id=annotation_id,
        synthesis_triggered=True
    )

@router.get("/guidance/{clause_id}")
async def get_synthesized_guidance(
    clause_id: str,
    industry: Optional[str] = Query(None),
    service: LivingDocumentationService = Depends(get_living_docs_service)
):
    """
    Get synthesized guidance for clause

    Combines:
    - Official standard text
    - Community interpretations
    - Real case examples
    """

    context = {'industry': industry} if industry else None
    guidance = await service.get_living_documentation(clause_id, context=context)

    if not guidance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No guidance available for this clause yet"
        )

    return {
        "clause_id": clause_id,
        "official_text": guidance.get('official_text'),
        "unified_guidance": guidance.get('unified_guidance'),
        "practical_steps": guidance.get('practical_steps', []),
        "common_pitfalls": guidance.get('common_pitfalls', []),
        "success_patterns": guidance.get('success_patterns', []),
        "sources_count": guidance.get('metadata', {}).get('sources_count', 0),
        "last_updated": guidance.get('metadata', {}).get('last_synthesized'),
        "version": guidance.get('metadata', {}).get('synthesis_version', 1)
    }

@router.post("/annotations/{annotation_id}/vote")
async def vote_annotation(
    annotation_id: str,
    vote_type: str = Query(..., regex="^(up|down|helpful)$"),
    service: LivingDocumentationService = Depends(get_living_docs_service),
    user = Depends(get_current_user)
):
    """Vote on annotation quality"""

    await service.vote_annotation(str(user.id), annotation_id, vote_type)

    return {"status": "voted"}

# ============= PREDICTIVE TIMELINE ENDPOINTS =============

async def get_predictive_service():
    """Get Predictive Timeline Service instance"""
    from ..services.predictive_timeline import PredictiveTimelineService
    # TODO: Inject actual dependencies (workflow_engine, case_library, ml_predictor)
    return PredictiveTimelineService(None, None, None)

class TimelineResponse(BaseModel):
    """Timeline prediction response"""
    organization: dict
    timeline: List[dict]
    milestones: List[dict]
    critical_path: List[str]
    estimated_completion: Optional[str]
    confidence_overall: float

@router.post("/timeline/predict", response_model=TimelineResponse)
async def predict_timeline(
    request: TimelineRequest,
    service: PredictiveTimelineService = Depends(get_predictive_service),
    user = Depends(get_current_user)
):
    """
    Predict organization's BCM journey timeline

    Returns:
    - Predicted milestones
    - Resource needs
    - Critical path
    """

    timeline = await service.predict_timeline(
        org_id=request.org_id,
        horizon_months=request.horizon_months
    )

    return TimelineResponse(**timeline)

@router.get("/insights/similar-orgs/{org_id}")
async def get_similar_org_insights(
    org_id: str,
    limit: int = Query(default=5, le=20),
    service: PredictiveTimelineService = Depends(get_predictive_service)
):
    """Get insights from similar organizations"""

    insights = await service.get_similar_org_insights(org_id, limit)

    return insights

@router.get("/timeline/{org_id}/next-steps")
async def get_next_steps(
    org_id: str,
    count: int = Query(default=3, le=10),
    service: PredictiveTimelineService = Depends(get_predictive_service)
):
    """Get immediate next steps for organization"""

    timeline = await service.predict_timeline(org_id, horizon_months=3)

    # Extract next N events
    next_events = timeline['timeline'][:count]

    return {
        "org_id": org_id,
        "next_steps": [
            {
                "action": event['name'],
                "when": event['predicted_date'],
                "confidence": event['confidence'],
                "preparation": event['preparation_actions']
            }
            for event in next_events
        ]
    }

@router.get("/marketplace/demand-forecast")
async def get_demand_forecast(
    specialty: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    horizon_days: int = Query(default=90, ge=7, le=365)
):
    """
    Forecast demand for consultants/auditors

    Useful for experts to plan capacity
    """

    # TODO: Implement actual demand forecasting
    # For now, return placeholder
    return {
        "specialty": specialty or "all",
        "region": region or "all",
        "horizon_days": horizon_days,
        "forecast": [
            {
                "period": "2025-10-12 to 2025-10-19",
                "expected_requests": 12,
                "confidence": 0.84,
                "peak_dates": ["2025-10-15", "2025-10-16"]
            }
        ]
    }

@router.get("/clauses/search")
async def search_clauses(
    query: str = Query(..., min_length=3),
    standard: str = Query(default="ISO22301"),
    service: LivingDocumentationService = Depends(get_living_docs_service)
):
    """Search clauses by keyword"""

    results = await service.search_living_docs(query, filters={'standard': standard})

    return {
        "query": query,
        "standard": standard,
        "results": results or []
    }


# ============= STATISTICS & ANALYTICS =============

@router.get("/stats/community")
async def get_community_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get community statistics"""

    from ..models.database import CaseContribution, UserReputation, CommunityAnnotation
    from sqlalchemy import func, select

    # Total contributions
    contrib_count = await db.scalar(
        select(func.count()).select_from(CaseContribution)
    )

    # Approved cases
    approved_count = await db.scalar(
        select(func.count())
        .select_from(CaseContribution)
        .where(CaseContribution.added_to_library == True)
    )

    # Active contributors
    active_contributors = await db.scalar(
        select(func.count())
        .select_from(UserReputation)
        .where(UserReputation.contributions_count > 0)
    )

    # Annotations
    annotations_count = await db.scalar(
        select(func.count()).select_from(CommunityAnnotation)
    )

    return {
        "total_contributions": contrib_count or 0,
        "approved_cases": approved_count or 0,
        "approval_rate": (approved_count / contrib_count) if contrib_count and contrib_count > 0 else 0,
        "active_contributors": active_contributors or 0,
        "community_annotations": annotations_count or 0,
        "coverage": {
            "iso22301_clauses_annotated": 45,  # TODO: Calculate from actual data
            "total_iso22301_clauses": 83
        }
    }

@router.get("/stats/impact")
async def get_impact_stats(
    db: AsyncSession = Depends(get_db)
):
    """Measure community impact"""

    # TODO: Calculate from actual data
    # - Cases used in AI advice
    # - Annotations that improved guidance
    # - Time saved by using community knowledge

    return {
        "cases_referenced_in_advice": 0,  # Calculate from actual usage
        "organizations_helped": 0,
        "avg_time_saved_hours": 0,
        "knowledge_quality_score": 0.0
    }

# ============= HEALTH CHECK =============

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "community_intelligence",
        "version": "1.0.0"
    }
