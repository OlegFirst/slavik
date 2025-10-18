"""
Planning Service API Routes
ISO 22301 Clause 8.3 - Business Continuity Strategy
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from ..models.domain import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyStatus,
    StrategyType,
    CostBenefitRequest,
    CostBenefitResponse,
)
from ..services.business_logic import StrategyService
from ..repositories.repository import StrategyRepository
from ..dependencies import get_strategy_service
from ..auth import UserContext, get_current_user

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.post("/", response_model=StrategyResponse, status_code=201)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Create new business continuity strategy
    ISO 22301: Clause 8.3

    Requires: Valid JWT token with tenant_id
    """
    try:
        # Enforce tenant isolation - use tenant_id from token
        if hasattr(strategy_data, 'tenant_id') and strategy_data.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot create strategy for different tenant"
            )

        return await service.create_strategy(strategy_data, current_user.user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(
    current_user: UserContext = Depends(get_current_user),
    status: Optional[StrategyStatus] = None,
    strategy_type: Optional[StrategyType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    List strategies with filters
    ISO 22301: Clause 8.3

    Requires: Valid JWT token
    Note: Automatically filters by tenant_id from token (tenant isolation)
    """
    try:
        # Use tenant_id from JWT token for security
        return await service.list_strategies(
            tenant_id=current_user.tenant_id,
            status=status,
            strategy_type=strategy_type,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Get strategy by ID
    ISO 22301: Clause 8.3

    Requires: Valid JWT token
    Note: Returns 404 if strategy doesn't belong to user's tenant
    """
    strategy = await service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # Enforce tenant isolation
    if hasattr(strategy, 'tenant_id') and strategy.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=404,
            detail="Strategy not found"  # Don't reveal it exists in another tenant
        )

    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    strategy_data: StrategyUpdate,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Update strategy
    ISO 22301: Clause 8.3

    Requires: Valid JWT token
    Note: Only draft strategies can be updated
    """
    try:
        # First verify the strategy exists and belongs to user's tenant
        existing = await service.get_strategy(strategy_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Strategy not found")

        if hasattr(existing, 'tenant_id') and existing.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=404, detail="Strategy not found")

        strategy = await service.update_strategy(strategy_id, strategy_data, current_user.user_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return strategy
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{strategy_id}", status_code=204)
async def delete_strategy(
    strategy_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Archive strategy (soft delete)
    ISO 22301: Clause 8.3

    Requires: Valid JWT token
    """
    # Verify strategy exists and belongs to user's tenant
    existing = await service.get_strategy(strategy_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if hasattr(existing, 'tenant_id') and existing.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Strategy not found")

    deleted = await service.delete_strategy(strategy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return None


@router.post("/{strategy_id}/cost-benefit", response_model=CostBenefitResponse)
async def calculate_cost_benefit(
    strategy_id: UUID,
    cost_benefit_data: CostBenefitRequest,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Calculate cost-benefit analysis for strategy
    ISO 22301: Clause 8.3 - Cost-benefit analysis requirement

    Requires: Valid JWT token
    """
    try:
        # Verify strategy exists and belongs to user's tenant
        existing = await service.get_strategy(strategy_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Strategy not found")

        if hasattr(existing, 'tenant_id') and existing.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return await service.calculate_cost_benefit(strategy_id, cost_benefit_data)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{strategy_id}/submit-review", response_model=StrategyResponse)
async def submit_for_review(
    strategy_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Submit strategy for review
    ISO 22301: Clause 8.3
    Workflow: DRAFT → REVIEW

    Requires: Valid JWT token
    """
    try:
        # Verify strategy exists and belongs to user's tenant
        existing = await service.get_strategy(strategy_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Strategy not found")

        if hasattr(existing, 'tenant_id') and existing.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return await service.submit_for_review(strategy_id, current_user.user_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{strategy_id}/approve", response_model=StrategyResponse)
async def approve_strategy(
    strategy_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    approval_notes: Optional[str] = None,
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Approve strategy
    ISO 22301: Clause 8.3
    Workflow: REVIEW → APPROVED

    Requires: Valid JWT token
    """
    try:
        # Verify strategy exists and belongs to user's tenant
        existing = await service.get_strategy(strategy_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Strategy not found")

        if hasattr(existing, 'tenant_id') and existing.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return await service.approve_strategy(strategy_id, current_user.user_id, approval_notes)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
