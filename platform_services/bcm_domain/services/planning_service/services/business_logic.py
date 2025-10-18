"""
Planning Service Business Logic
ISO 22301 Clause 8.3 - Business Continuity Strategy
"""

from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
import logging

from ..repositories.repository import StrategyRepository
from ..models.domain import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyStatus,
    StrategyType,
    CostBenefitRequest,
    CostBenefitResponse,
    ROIAnalysis,
)
from ..models.database import Strategy
from ..events.publishers import publish_event
from shared.cache import get_cache, cached

logger = logging.getLogger(__name__)


class StrategyService:
    """Business logic for strategy management"""

    def __init__(self, repository: StrategyRepository):
        self.repo = repository

    async def create_strategy(
        self,
        strategy_data: StrategyCreate,
        created_by: str
    ) -> StrategyResponse:
        """
        Create new business continuity strategy
        ISO 8.3 - Determine and select BC strategies
        """
        # Generate strategy number
        strategy_number = f"STRAT-{datetime.now().year}-{uuid4().hex[:6].upper()}"

        # Create strategy
        strategy = Strategy(
            id=uuid4(),
            tenant_id=strategy_data.tenant_id,
            strategy_number=strategy_number,
            name=strategy_data.name,
            description=strategy_data.description,
            strategy_type=strategy_data.strategy_type,
            strategy_phase=strategy_data.strategy_phase,
            status=StrategyStatus.DRAFT,
            objective=strategy_data.objective,
            scope=strategy_data.scope,
            risk_mitigation=strategy_data.risk_mitigation,
            created_by=created_by,
        )

        created_strategy = await self.repo.create(strategy)

        # Publish event to EventBus
        try:
            await publish_event(
                topic="planning.strategy.created",
                data={
                    "strategy_id": str(created_strategy.id),
                    "tenant_id": created_strategy.tenant_id,
                    "strategy_number": created_strategy.strategy_number,
                    "name": created_strategy.name,
                    "strategy_type": created_strategy.strategy_type.value,
                    "strategy_phase": created_strategy.strategy_phase.value,
                    "status": created_strategy.status.value,
                    "created_by": created_by,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.info(f"Published planning.strategy.created event for strategy {created_strategy.strategy_number}")
        except Exception as e:
            logger.warning(f"Failed to publish planning.strategy.created event: {e}")

        return self._to_response(created_strategy)

    @cached(ttl=300, key_prefix="planning:strategy")
    async def get_strategy(self, strategy_id: UUID, tenant_id: str = None) -> Optional[StrategyResponse]:
        """
        Get strategy by ID

        Cached for 300 seconds (5 minutes) per tenant.
        """
        strategy = await self.repo.get_by_id(strategy_id)
        if not strategy:
            return None
        return self._to_response(strategy)

    async def list_strategies(
        self,
        tenant_id: str,
        status: Optional[StrategyStatus] = None,
        strategy_type: Optional[StrategyType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StrategyResponse]:
        """List strategies with filters"""
        strategies = await self.repo.get_by_tenant(
            tenant_id=tenant_id,
            status=status,
            strategy_type=strategy_type,
            skip=skip,
            limit=limit
        )
        return [self._to_response(s) for s in strategies]

    async def update_strategy(
        self,
        strategy_id: UUID,
        strategy_data: StrategyUpdate,
        updated_by: str
    ) -> Optional[StrategyResponse]:
        """Update strategy"""
        strategy = await self.repo.get_by_id(strategy_id)
        if not strategy:
            return None

        # Only allow updates to draft strategies
        if strategy.status != StrategyStatus.DRAFT:
            raise ValueError(f"Cannot update strategy in {strategy.status} status")

        # Build update dict
        update_data = strategy_data.model_dump(exclude_unset=True)
        update_data["updated_by"] = updated_by
        update_data["updated_at"] = datetime.now()

        updated_strategy = await self.repo.update(strategy_id, update_data)
        return self._to_response(updated_strategy)

    async def calculate_cost_benefit(
        self,
        strategy_id: UUID,
        cost_benefit_data: CostBenefitRequest
    ) -> CostBenefitResponse:
        """
        Calculate cost-benefit analysis for strategy
        ISO 8.3 - Cost-benefit analysis requirement
        """
        strategy = await self.repo.get_by_id(strategy_id)
        if not strategy:
            raise ValueError("Strategy not found")

        # Calculate costs with proper discounting
        # Initial investment (year 0 - no discounting)
        initial_cost = (
            cost_benefit_data.cost_breakdown.capex +
            cost_benefit_data.cost_breakdown.training +
            cost_benefit_data.cost_breakdown.other
        )

        # Annual recurring costs
        annual_recurring_cost = (
            cost_benefit_data.cost_breakdown.opex +
            cost_benefit_data.cost_breakdown.maintenance
        )

        # Calculate NPV of recurring costs (discounted)
        discounted_recurring_costs = 0
        for year in range(1, cost_benefit_data.implementation_years + 1):
            discounted_recurring_costs += annual_recurring_cost / ((1 + cost_benefit_data.discount_rate) ** year)

        # Total cost (NPV)
        total_cost = initial_cost + discounted_recurring_costs

        # Calculate total benefits (sum of quantitative benefits)
        total_benefits = sum(cost_benefit_data.expected_benefits.quantitative_benefits.values())
        total_annual_benefits = total_benefits / cost_benefit_data.implementation_years

        # Calculate cost-benefit ratio
        cost_benefit_ratio = total_benefits / total_cost if total_cost > 0 else 0

        # Calculate Payback Period with discounting
        payback_period_months = self._calculate_payback_period(
            initial_cost,
            total_annual_benefits - annual_recurring_cost,  # Net annual cash flow
            cost_benefit_data.discount_rate
        )

        # Calculate ROI
        roi_percentage = ((total_benefits - total_cost) / total_cost * 100) if total_cost > 0 else 0

        # Calculate NPV (net benefits - net costs)
        npv = self._calculate_npv(
            initial_cost,
            total_annual_benefits,
            annual_recurring_cost,
            cost_benefit_data.implementation_years,
            cost_benefit_data.discount_rate
        )

        roi_analysis = ROIAnalysis(
            total_investment=total_cost,
            annual_savings=total_annual_benefits,
            payback_period_months=payback_period_months,
            roi_percentage=roi_percentage,
            net_present_value=npv
        )

        # Determine recommendation
        recommendation = self._determine_recommendation(cost_benefit_ratio, roi_percentage)
        confidence_level = self._assess_confidence(cost_benefit_data)

        # Update strategy with cost-benefit data
        await self.repo.update(strategy_id, {
            "estimated_cost": total_cost,
            "cost_breakdown": cost_benefit_data.cost_breakdown.model_dump(),
            "expected_benefits": cost_benefit_data.expected_benefits.model_dump(),
            "roi_analysis": roi_analysis.model_dump(),
            "cost_benefit_ratio": cost_benefit_ratio,
        })

        cost_benefit_response = CostBenefitResponse(
            strategy_id=str(strategy_id),
            total_cost=total_cost,
            total_benefits=total_benefits,
            cost_benefit_ratio=cost_benefit_ratio,
            roi_analysis=roi_analysis,
            recommendation=recommendation,
            confidence_level=confidence_level
        )

        # Publish event to EventBus
        try:
            await publish_event(
                topic="planning.cost_benefit.completed",
                data={
                    "strategy_id": str(strategy_id),
                    "tenant_id": strategy.tenant_id,
                    "strategy_number": strategy.strategy_number,
                    "total_cost": total_cost,
                    "total_benefits": total_benefits,
                    "cost_benefit_ratio": cost_benefit_ratio,
                    "roi_percentage": roi_percentage,
                    "payback_period_months": payback_period_months,
                    "net_present_value": npv,
                    "recommendation": recommendation,
                    "confidence_level": confidence_level,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.info(f"Published planning.cost_benefit.completed event for strategy {strategy.strategy_number}")
        except Exception as e:
            logger.warning(f"Failed to publish planning.cost_benefit.completed event: {e}")

        return cost_benefit_response

    async def submit_for_review(
        self,
        strategy_id: UUID,
        submitted_by: str
    ) -> StrategyResponse:
        """Submit strategy for review"""
        strategy = await self.repo.get_by_id(strategy_id)
        if not strategy:
            raise ValueError("Strategy not found")

        if strategy.status != StrategyStatus.DRAFT:
            raise ValueError("Only draft strategies can be submitted for review")

        # Validate required fields
        if not strategy.objective or not strategy.scope:
            raise ValueError("Strategy must have objective and scope")

        updated_strategy = await self.repo.update(strategy_id, {
            "status": StrategyStatus.REVIEW,
            "submitted_for_review_at": datetime.now(),
        })

        return self._to_response(updated_strategy)

    async def approve_strategy(
        self,
        strategy_id: UUID,
        approved_by: str,
        approval_notes: Optional[str] = None
    ) -> StrategyResponse:
        """Approve strategy"""
        strategy = await self.repo.get_by_id(strategy_id)
        if not strategy:
            raise ValueError("Strategy not found")

        if strategy.status != StrategyStatus.REVIEW:
            raise ValueError("Only strategies in review can be approved")

        updated_strategy = await self.repo.update(strategy_id, {
            "status": StrategyStatus.APPROVED,
            "approved_by": approved_by,
            "approved_at": datetime.now(),
            "approval_notes": approval_notes,
        })

        # Publish event to EventBus
        try:
            await publish_event(
                topic="planning.strategy.approved",
                data={
                    "strategy_id": str(updated_strategy.id),
                    "tenant_id": updated_strategy.tenant_id,
                    "strategy_number": updated_strategy.strategy_number,
                    "name": updated_strategy.name,
                    "strategy_type": updated_strategy.strategy_type.value,
                    "status": updated_strategy.status.value,
                    "approved_by": approved_by,
                    "approval_notes": approval_notes,
                    "approved_at": updated_strategy.approved_at.isoformat(),
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.info(f"Published planning.strategy.approved event for strategy {updated_strategy.strategy_number}")
        except Exception as e:
            logger.warning(f"Failed to publish planning.strategy.approved event: {e}")

        return self._to_response(updated_strategy)

    async def delete_strategy(self, strategy_id: UUID) -> bool:
        """Soft delete strategy"""
        return await self.repo.delete(strategy_id)

    # Helper methods

    def _to_response(self, strategy: Strategy) -> StrategyResponse:
        """Convert database model to response model"""
        from ..models.domain import CostBreakdown, BenefitAnalysis, ROIAnalysis, ResourceRequirement, ImplementationPhase

        return StrategyResponse(
            id=str(strategy.id),
            tenant_id=strategy.tenant_id,
            strategy_number=strategy.strategy_number,
            name=strategy.name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            strategy_phase=strategy.strategy_phase,
            status=strategy.status,
            objective=strategy.objective,
            scope=strategy.scope or [],
            risk_mitigation=strategy.risk_mitigation or [],
            estimated_cost=strategy.estimated_cost,
            cost_breakdown=CostBreakdown(**strategy.cost_breakdown) if strategy.cost_breakdown else None,
            expected_benefits=BenefitAnalysis(**strategy.expected_benefits) if strategy.expected_benefits else None,
            roi_analysis=ROIAnalysis(**strategy.roi_analysis) if strategy.roi_analysis else None,
            cost_benefit_ratio=strategy.cost_benefit_ratio,
            resource_requirements=[ResourceRequirement(**r) for r in strategy.resource_requirements] if strategy.resource_requirements else [],
            resource_gaps=strategy.resource_gaps or [],
            implementation_phases=[ImplementationPhase(**p) for p in strategy.implementation_phases] if strategy.implementation_phases else [],
            dependencies=strategy.dependencies or [],
            success_criteria=strategy.success_criteria or [],
            linked_bia_ids=strategy.linked_bia_ids or [],
            linked_risk_ids=strategy.linked_risk_ids or [],
            submitted_for_review_at=strategy.submitted_for_review_at,
            reviewed_by=strategy.reviewed_by,
            reviewed_at=strategy.reviewed_at,
            approved_by=strategy.approved_by,
            approved_at=strategy.approved_at,
            created_by=strategy.created_by,
            created_at=strategy.created_at,
            updated_by=strategy.updated_by,
            updated_at=strategy.updated_at,
        )

    def _calculate_npv(
        self,
        initial_investment: float,
        annual_benefits: float,
        annual_costs: float,
        years: int,
        discount_rate: float
    ) -> float:
        """
        Calculate Net Present Value

        NPV = -Initial Investment + Σ(Net Cash Flow / (1 + r)^t)
        where Net Cash Flow = Annual Benefits - Annual Costs
        """
        npv = -initial_investment

        for year in range(1, years + 1):
            net_cash_flow = annual_benefits - annual_costs
            discounted_flow = net_cash_flow / ((1 + discount_rate) ** year)
            npv += discounted_flow

        return npv

    def _calculate_payback_period(
        self,
        initial_investment: float,
        annual_net_cash_flow: float,
        discount_rate: float,
        max_years: int = 20
    ) -> float:
        """
        Calculate discounted payback period in months

        Returns number of months until cumulative cash flow becomes positive
        """
        if annual_net_cash_flow <= 0:
            return float('inf')  # Will never pay back

        cumulative_cash_flow = -initial_investment

        for month in range(1, max_years * 12 + 1):
            year_fraction = month / 12.0
            monthly_cash_flow = annual_net_cash_flow / 12

            # Apply discounting
            discounted_flow = monthly_cash_flow / ((1 + discount_rate) ** year_fraction)
            cumulative_cash_flow += discounted_flow

            if cumulative_cash_flow >= 0:
                return month

        return 999  # Exceeds max_years

    def _determine_recommendation(self, cost_benefit_ratio: float, roi_percentage: float) -> str:
        """Determine recommendation based on analysis"""
        if cost_benefit_ratio >= 2.0 and roi_percentage >= 50:
            return "proceed"
        elif cost_benefit_ratio >= 1.0 and roi_percentage >= 0:
            return "review"
        else:
            return "reject"

    def _assess_confidence(self, cost_benefit_data: CostBenefitRequest) -> str:
        """Assess confidence level of analysis"""
        # Simple heuristic - check if we have quantitative benefits
        if len(cost_benefit_data.expected_benefits.quantitative_benefits) >= 3:
            return "high"
        elif len(cost_benefit_data.expected_benefits.quantitative_benefits) >= 1:
            return "medium"
        else:
            return "low"
