"""
Planning Service - Bulk Operations API

Provides parallel processing endpoints for:
- Bulk strategy creation
- Parallel cost-benefit calculations (NPV for multiple strategies)
- Bulk approval workflow processing
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import UUID

from ..models.domain import StrategyCreate, CostBenefitRequest
from ..services.business_logic import StrategyService
from ..dependencies import get_strategy_service
from ..auth import UserContext, get_current_user
from shared.utils.parallel import parallel_map, BulkOperationReport, gather_with_semaphore
from shared.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bulk", tags=["bulk-operations"])
metrics = MetricsCollector()


# ==================== REQUEST MODELS ====================

class BulkStrategyCreateRequest(BaseModel):
    """Bulk strategy creation request"""
    strategies: List[StrategyCreate]
    max_concurrency: Optional[int] = 10


class BulkCostBenefitRequest(BaseModel):
    """Bulk cost-benefit calculation request"""
    calculations: List[Dict[str, Any]]  # List of {strategy_id, cost_benefit_data}
    max_concurrency: Optional[int] = 5  # Lower concurrency for heavy calculations


class BulkApprovalRequest(BaseModel):
    """Bulk approval request"""
    strategy_ids: List[UUID]
    approval_notes: Optional[str] = None
    max_concurrency: Optional[int] = 10


# ==================== BULK ENDPOINTS ====================

@router.post("/strategies", response_model=Dict[str, Any])
async def bulk_create_strategies(
    request: BulkStrategyCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Create multiple business continuity strategies in parallel.

    ISO 22301: Clause 8.3

    Args:
        request: Bulk strategy creation request
        current_user: Current user context
        service: Strategy service

    Returns:
        Bulk operation report with statistics
    """
    logger.info(f"Starting bulk creation of {len(request.strategies)} strategies")

    async def create_single_strategy(strategy_data: StrategyCreate):
        """Create single strategy"""
        # Enforce tenant isolation
        if hasattr(strategy_data, 'tenant_id') and strategy_data.tenant_id != current_user.tenant_id:
            raise ValueError("Cannot create strategy for different tenant")

        return await service.create_strategy(strategy_data, current_user.user_id)

    # Process in parallel
    with metrics.track_time("planning_bulk_strategy_create_duration_seconds"):
        report: BulkOperationReport = await parallel_map(
            items=request.strategies,
            func=create_single_strategy,
            max_concurrency=request.max_concurrency,
            timeout_per_item=30.0,
            continue_on_error=True
        )

    # Record metrics
    metrics.inc_counter(
        "planning_bulk_operations_total",
        labels={"operation": "strategy_create", "status": "completed"}
    )

    logger.info(
        f"Bulk strategy creation completed: {report.success_count}/{report.total_count} succeeded"
    )

    return {
        "total": report.total_count,
        "success": report.success_count,
        "failed": report.failure_count,
        "success_rate": report.success_rate,
        "duration_ms": report.total_duration_ms,
        "failures": [
            {
                "index": f.index,
                "title": f.input_data.title if hasattr(f.input_data, 'title') else None,
                "error": f.error
            }
            for f in report.failures
        ]
    }


@router.post("/cost-benefit", response_model=Dict[str, Any])
async def bulk_calculate_cost_benefit(
    request: BulkCostBenefitRequest,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Calculate cost-benefit analysis (NPV) for multiple strategies in parallel.

    ISO 22301: Clause 8.3 - Cost-benefit analysis requirement

    This is computationally intensive, so we use lower concurrency.

    Args:
        request: Bulk cost-benefit calculation request
        current_user: Current user context
        service: Strategy service

    Returns:
        Bulk operation report with NPV calculations
    """
    logger.info(f"Starting bulk cost-benefit calculation for {len(request.calculations)} strategies")

    async def calculate_single_npv(calc_data: Dict[str, Any]):
        """Calculate NPV for single strategy"""
        strategy_id = UUID(calc_data["strategy_id"])
        cost_benefit_data = CostBenefitRequest(**calc_data["cost_benefit_data"])

        # Verify strategy belongs to user's tenant
        existing = await service.get_strategy(strategy_id)
        if not existing:
            raise ValueError("Strategy not found")

        if hasattr(existing, 'tenant_id') and existing.tenant_id != current_user.tenant_id:
            raise ValueError("Strategy not found")

        return await service.calculate_cost_benefit(strategy_id, cost_benefit_data)

    # Process in parallel with lower concurrency (CPU-intensive)
    with metrics.track_time("planning_bulk_npv_calculation_duration_seconds"):
        report: BulkOperationReport = await parallel_map(
            items=request.calculations,
            func=calculate_single_npv,
            max_concurrency=request.max_concurrency,
            timeout_per_item=60.0,  # NPV calculation can take time
            continue_on_error=True
        )

    # Record metrics
    metrics.inc_counter(
        "planning_bulk_operations_total",
        labels={"operation": "cost_benefit_calc", "status": "completed"}
    )

    # Calculate aggregate NPV statistics
    successful_results = [r.result for r in report.successes if r.result]
    total_npv = sum(r.get("npv", 0) for r in successful_results)
    avg_npv = total_npv / len(successful_results) if successful_results else 0

    logger.info(
        f"Bulk NPV calculation completed: {report.success_count}/{report.total_count} succeeded, "
        f"Total NPV: ${total_npv:,.2f}, Avg NPV: ${avg_npv:,.2f}"
    )

    return {
        "total": report.total_count,
        "success": report.success_count,
        "failed": report.failure_count,
        "success_rate": report.success_rate,
        "duration_ms": report.total_duration_ms,
        "aggregate_metrics": {
            "total_npv": total_npv,
            "average_npv": avg_npv,
            "positive_npv_count": sum(1 for r in successful_results if r.get("npv", 0) > 0)
        },
        "failures": [
            {
                "index": f.index,
                "strategy_id": f.input_data.get("strategy_id"),
                "error": f.error
            }
            for f in report.failures
        ]
    }


@router.post("/approve", response_model=Dict[str, Any])
async def bulk_approve_strategies(
    request: BulkApprovalRequest,
    current_user: UserContext = Depends(get_current_user),
    service: StrategyService = Depends(get_strategy_service)
):
    """
    Approve multiple strategies in parallel.

    ISO 22301: Clause 8.3
    Workflow: REVIEW → APPROVED

    Args:
        request: Bulk approval request
        current_user: Current user context
        service: Strategy service

    Returns:
        Bulk operation report with approval statistics
    """
    logger.info(f"Starting bulk approval of {len(request.strategy_ids)} strategies")

    async def approve_single_strategy(strategy_id: UUID):
        """Approve single strategy"""
        # Verify strategy exists and belongs to user's tenant
        existing = await service.get_strategy(strategy_id)
        if not existing:
            raise ValueError("Strategy not found")

        if hasattr(existing, 'tenant_id') and existing.tenant_id != current_user.tenant_id:
            raise ValueError("Strategy not found")

        return await service.approve_strategy(
            strategy_id,
            current_user.user_id,
            request.approval_notes
        )

    # Process in parallel
    with metrics.track_time("planning_bulk_approval_duration_seconds"):
        report: BulkOperationReport = await parallel_map(
            items=request.strategy_ids,
            func=approve_single_strategy,
            max_concurrency=request.max_concurrency,
            timeout_per_item=20.0,
            continue_on_error=True
        )

    # Record metrics
    metrics.inc_counter(
        "planning_bulk_operations_total",
        labels={"operation": "approval", "status": "completed"}
    )

    logger.info(
        f"Bulk approval completed: {report.success_count}/{report.total_count} approved"
    )

    return {
        "total": report.total_count,
        "success": report.success_count,
        "failed": report.failure_count,
        "success_rate": report.success_rate,
        "duration_ms": report.total_duration_ms,
        "approved_by": current_user.user_id,
        "failures": [
            {
                "index": f.index,
                "strategy_id": str(f.input_data),
                "error": f.error
            }
            for f in report.failures
        ]
    }
