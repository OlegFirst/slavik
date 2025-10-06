"""
Reputation API

Endpoints for community reputation and leaderboards
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from shared.database import get_db
from shared.auth import get_current_user
from shared.eventbus import get_eventbus_client
from ..services.reputation_engine import ReputationEngine
from ..models.database import UserReputation, ReputationTransaction

router = APIRouter()


# --- Pydantic Models ---

class ReputationProfile(BaseModel):
    """User reputation profile"""
    user_id: UUID
    total_points: int
    level: str
    expertise: dict  # Module-specific expertise

    # Contribution stats
    contribution_points: int
    contributions_count: int
    cases_approved: int
    cases_rejected: int
    avg_case_quality: float

    # Review stats
    review_points: int
    reviews_count: int
    helpful_reviews_count: int

    # Marketplace
    marketplace_priority: int

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: UUID
    total_points: int
    level: str
    contributions_count: int
    reviews_count: int


class TransactionItem(BaseModel):
    """Reputation transaction"""
    id: UUID
    points: int
    reason: str
    created_at: str

    class Config:
        from_attributes = True


class ExpertiseLevelResponse(BaseModel):
    """Expertise level in module"""
    module: str
    level: str  # novice, intermediate, advanced, expert
    points: int


# --- Dependencies ---

async def get_reputation_engine(
    db: AsyncSession = Depends(get_db)
) -> ReputationEngine:
    """Get ReputationEngine instance"""
    eventbus = get_eventbus_client()
    return ReputationEngine(db=db, eventbus=eventbus)


# --- Endpoints ---

@router.get("/{user_id}", response_model=ReputationProfile)
async def get_reputation(
    user_id: UUID,
    engine: ReputationEngine = Depends(get_reputation_engine)
):
    """Get user reputation profile"""

    reputation = await engine.get_reputation(user_id)

    if not reputation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reputation profile not found"
        )

    return ReputationProfile(
        user_id=reputation.user_id,
        total_points=reputation.total_points,
        level=reputation.level,
        expertise=reputation.expertise,
        contribution_points=reputation.contribution_points,
        contributions_count=reputation.contributions_count,
        cases_approved=reputation.cases_approved,
        cases_rejected=reputation.cases_rejected,
        avg_case_quality=reputation.avg_case_quality,
        review_points=reputation.review_points,
        reviews_count=reputation.reviews_count,
        helpful_reviews_count=reputation.helpful_reviews_count,
        marketplace_priority=reputation.marketplace_priority
    )


@router.get("/{user_id}/expertise/{module}", response_model=ExpertiseLevelResponse)
async def get_expertise_level(
    user_id: UUID,
    module: str,
    engine: ReputationEngine = Depends(get_reputation_engine)
):
    """Get user's expertise level in specific module"""

    reputation = await engine.get_reputation(user_id)

    if not reputation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reputation profile not found"
        )

    level = await engine.get_expertise_level(user_id, module)
    points = reputation.expertise.get(module, 0)

    return ExpertiseLevelResponse(
        module=module,
        level=level,
        points=points
    )


@router.get("/leaderboard/global", response_model=List[LeaderboardEntry])
async def get_global_leaderboard(
    limit: int = Query(default=10, le=100),
    engine: ReputationEngine = Depends(get_reputation_engine)
):
    """
    Get global leaderboard (top contributors by total points)
    """

    leaderboard = await engine.get_leaderboard(module=None, limit=limit)

    return [
        LeaderboardEntry(
            rank=idx + 1,
            user_id=entry.user_id,
            total_points=entry.total_points,
            level=entry.level,
            contributions_count=entry.contributions_count,
            reviews_count=entry.reviews_count
        )
        for idx, entry in enumerate(leaderboard)
    ]


@router.get("/leaderboard/{module}", response_model=List[LeaderboardEntry])
async def get_module_leaderboard(
    module: str,
    limit: int = Query(default=10, le=100),
    engine: ReputationEngine = Depends(get_reputation_engine)
):
    """
    Get module-specific leaderboard

    Top experts in specific BCM module (bia, risk, etc.)
    """

    leaderboard = await engine.get_leaderboard(module=module, limit=limit)

    return [
        LeaderboardEntry(
            rank=idx + 1,
            user_id=entry.user_id,
            total_points=entry.expertise.get(module, 0),
            level=entry.level,
            contributions_count=entry.contributions_count,
            reviews_count=entry.reviews_count
        )
        for idx, entry in enumerate(leaderboard)
    ]


@router.get("/transactions/{user_id}", response_model=List[TransactionItem])
async def get_transactions(
    user_id: UUID,
    limit: int = Query(default=20, le=100),
    current_user: dict = Depends(get_current_user),
    engine: ReputationEngine = Depends(get_reputation_engine)
):
    """
    Get reputation transaction history

    Only user can see their own transactions
    """

    # Check access
    if str(user_id) != current_user['user_id'] and not current_user.get('is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own transactions"
        )

    transactions = await engine.get_transactions(user_id, limit=limit)

    return [
        TransactionItem(
            id=t.id,
            points=t.points,
            reason=t.reason,
            created_at=t.created_at.isoformat()
        )
        for t in transactions
    ]
