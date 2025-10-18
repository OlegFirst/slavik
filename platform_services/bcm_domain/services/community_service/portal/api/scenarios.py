"""
Scenario Marketplace API
Endpoints for scenario catalog, deployment, and reviews
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.scenarios import (
    ScenarioResponse, ScenarioListResponse, ScenarioListItem,
    ScenarioDeployRequest, ScenarioDeployResponse,
    ScenarioReviewCreate, ScenarioReviewResponse
)
from services.scenario_service import ScenarioService
from api.dependencies import (
    get_current_user, get_token, get_validation_client
)
from integrations.validation_client import ValidationClient

router = APIRouter(prefix="/api/portal/scenarios", tags=["Scenario Marketplace"])
scenario_service = ScenarioService()


# ============================================================================
# Scenario Catalog
# ============================================================================

@router.get("", response_model=ScenarioListResponse)
async def get_scenarios(
    scenario_type: Optional[str] = Query(None, description="Filter by type (tabletop, functional, full_scale)"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    threat_type: Optional[str] = Query(None, description="Filter by threat type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get catalog of available scenarios

    Scenarios are sorted by average rating and deployment count.

    Filters:
    - **scenario_type**: tabletop, functional, full_scale
    - **industry**: Finance, Healthcare, Manufacturing, etc.
    - **threat_type**: Cyber Attack, Natural Disaster, Pandemic, etc.
    """
    scenarios, total = await scenario_service.get_scenarios(
        db=db,
        scenario_type=scenario_type,
        industry=industry,
        threat_type=threat_type,
        published_only=True,
        page=page,
        page_size=page_size
    )

    total_pages = (total + page_size - 1) // page_size

    return ScenarioListResponse(
        scenarios=[ScenarioListItem.model_validate(s) for s in scenarios],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get scenario details

    Returns full scenario including:
    - Complete scenario description
    - List of injects/events
    - Learning objectives
    - ISO 22301 clause mapping
    - Ratings and reviews
    """
    scenario = await scenario_service.get_scenario(db, scenario_id)

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return scenario


# ============================================================================
# Scenario Deployment
# ============================================================================

@router.post("/{scenario_id}/deploy", response_model=ScenarioDeployResponse)
async def deploy_scenario(
    scenario_id: int,
    deploy_request: ScenarioDeployRequest,
    current_user: dict = Depends(get_current_user),
    token: str = Depends(get_token),
    validation_client: ValidationClient = Depends(get_validation_client),
    db: AsyncSession = Depends(get_db)
):
    """
    Deploy scenario as an exercise

    Creates a new exercise in the Validation module based on this scenario.

    - **tenant_id**: Target tenant for deployment
    - **exercise_name_override**: Optional custom name for the exercise

    The scenario's injects, objectives, and settings are automatically
    configured in the created exercise.
    """
    # Verify user has access to target tenant
    if deploy_request.tenant_id != current_user.get('tenant_id'):
        raise HTTPException(
            status_code=403,
            detail="Cannot deploy to a different tenant"
        )

    try:
        exercise = await scenario_service.deploy_scenario(
            db=db,
            scenario_id=scenario_id,
            tenant_id=deploy_request.tenant_id,
            token=token,
            validation_client=validation_client,
            exercise_name_override=deploy_request.exercise_name_override
        )

        return ScenarioDeployResponse(
            scenario_id=scenario_id,
            exercise_id=exercise['id'],
            exercise_code=exercise['exercise_code'],
            exercise_name=exercise['exercise_name']
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deployment failed: {str(e)}"
        )


# ============================================================================
# Reviews and Ratings
# ============================================================================

@router.post("/{scenario_id}/reviews", response_model=ScenarioReviewResponse, status_code=201)
async def create_review(
    scenario_id: int,
    review_data: ScenarioReviewCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update a scenario review

    - **rating**: 1-5 stars
    - **review_text**: Optional review text
    - **exercise_id**: Optional reference to exercise where scenario was used

    Users can only have one review per scenario.
    Updating a review overwrites the previous one.
    """
    review = await scenario_service.create_review(
        db=db,
        scenario_id=scenario_id,
        user_id=current_user['user_id'],
        tenant_id=current_user['tenant_id'],
        rating=review_data.rating,
        review_text=review_data.review_text,
        exercise_id=review_data.exercise_id
    )

    return review


@router.get("/{scenario_id}/reviews", response_model=list[ScenarioReviewResponse])
async def get_scenario_reviews(
    scenario_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reviews for a scenario

    Returns most recent reviews, sorted by creation date.
    """
    reviews = await scenario_service.get_scenario_reviews(
        db, scenario_id, limit
    )

    return reviews


# ============================================================================
# Popular Scenarios
# ============================================================================

@router.get("/featured/popular", response_model=list[ScenarioListItem])
async def get_popular_scenarios(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most popular scenarios

    Sorted by deployment count and average rating.
    Great for showcasing top scenarios on homepage.
    """
    scenarios = await scenario_service.get_popular_scenarios(db, limit)

    return [ScenarioListItem.model_validate(s) for s in scenarios]
