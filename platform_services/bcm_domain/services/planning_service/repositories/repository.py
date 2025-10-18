"""
Planning Service Repository (Data Access Layer)

N+1 Query Optimizations:
- Added dashboard queries with aggregations
- Optimized statistics queries
- Added cursor-based pagination
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, case, and_
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..models.database import Strategy
from ..models.domain import StrategyStatus, StrategyType


class StrategyRepository:
    """Strategy data access repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, strategy: Strategy) -> Strategy:
        """Create new strategy"""
        self.session.add(strategy)
        await self.session.commit()
        await self.session.refresh(strategy)
        return strategy

    async def get_by_id(self, strategy_id: UUID) -> Optional[Strategy]:
        """Get strategy by ID"""
        result = await self.session.execute(
            select(Strategy).where(Strategy.id == strategy_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tenant(
        self,
        tenant_id: str,
        status: Optional[StrategyStatus] = None,
        strategy_type: Optional[StrategyType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Strategy]:
        """Get strategies by tenant with filters"""
        query = select(Strategy).where(
            Strategy.tenant_id == tenant_id,
            Strategy.active == True
        )

        if status:
            query = query.where(Strategy.status == status)

        if strategy_type:
            query = query.where(Strategy.strategy_type == strategy_type)

        query = query.offset(skip).limit(limit).order_by(Strategy.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, strategy_id: UUID, update_data: dict) -> Optional[Strategy]:
        """Update strategy"""
        await self.session.execute(
            update(Strategy)
            .where(Strategy.id == strategy_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(strategy_id)

    async def delete(self, strategy_id: UUID) -> bool:
        """Soft delete strategy"""
        result = await self.session.execute(
            update(Strategy)
            .where(Strategy.id == strategy_id)
            .values(active=False)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_number(self, strategy_number: str) -> Optional[Strategy]:
        """Get strategy by strategy_number"""
        result = await self.session.execute(
            select(Strategy).where(Strategy.strategy_number == strategy_number)
        )
        return result.scalar_one_or_none()

    async def count_by_tenant(self, tenant_id: str, status: Optional[StrategyStatus] = None) -> int:
        """Count strategies by tenant"""
        query = select(Strategy).where(
            Strategy.tenant_id == tenant_id,
            Strategy.active == True
        )

        if status:
            query = query.where(Strategy.status == status)

        result = await self.session.execute(query)
        return len(list(result.scalars().all()))

    # ========== N+1 Query Optimization Methods ==========

    async def get_dashboard_data(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get strategy dashboard data with aggregations.

        Optimization: Single query with aggregations
        Before: Multiple queries for different statistics
        After: 1 query with aggregations

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary with dashboard statistics
        """
        query = select(
            func.count(Strategy.id).label('total_count'),
            # By status
            func.sum(case((Strategy.status == StrategyStatus.DRAFT, 1), else_=0)).label('draft_count'),
            func.sum(case((Strategy.status == StrategyStatus.UNDER_REVIEW, 1), else_=0)).label('under_review_count'),
            func.sum(case((Strategy.status == StrategyStatus.APPROVED, 1), else_=0)).label('approved_count'),
            func.sum(case((Strategy.status == StrategyStatus.IMPLEMENTED, 1), else_=0)).label('implemented_count'),
            # By type
            func.sum(case((Strategy.strategy_type == StrategyType.RELOCATION, 1), else_=0)).label('relocation_count'),
            func.sum(case((Strategy.strategy_type == StrategyType.RECIPROCAL_ARRANGEMENT, 1), else_=0)).label('reciprocal_count'),
            func.sum(case((Strategy.strategy_type == StrategyType.REDUNDANCY, 1), else_=0)).label('redundancy_count'),
            func.sum(case((Strategy.strategy_type == StrategyType.WORKAROUND, 1), else_=0)).label('workaround_count'),
            # Cost-benefit
            func.avg(Strategy.cost_benefit_ratio).label('avg_cost_benefit_ratio'),
            func.avg(Strategy.estimated_cost).label('avg_estimated_cost'),
            func.sum(Strategy.estimated_cost).label('total_estimated_cost'),
        ).where(
            and_(
                Strategy.tenant_id == tenant_id,
                Strategy.active == True
            )
        )

        result = await self.session.execute(query)
        row = result.first()

        if not row or row.total_count == 0:
            return {
                "total_count": 0,
                "status_breakdown": {},
                "type_breakdown": {},
                "cost_analysis": {}
            }

        return {
            "total_count": int(row.total_count),
            "status_breakdown": {
                "draft": int(row.draft_count or 0),
                "under_review": int(row.under_review_count or 0),
                "approved": int(row.approved_count or 0),
                "implemented": int(row.implemented_count or 0)
            },
            "type_breakdown": {
                "relocation": int(row.relocation_count or 0),
                "reciprocal_arrangement": int(row.reciprocal_count or 0),
                "redundancy": int(row.redundancy_count or 0),
                "workaround": int(row.workaround_count or 0)
            },
            "cost_analysis": {
                "avg_cost_benefit_ratio": float(row.avg_cost_benefit_ratio) if row.avg_cost_benefit_ratio else 0,
                "avg_estimated_cost": float(row.avg_estimated_cost) if row.avg_estimated_cost else 0,
                "total_estimated_cost": float(row.total_estimated_cost) if row.total_estimated_cost else 0
            }
        }

    async def get_strategies_by_cost_effectiveness(
        self,
        tenant_id: str,
        min_cost_benefit_ratio: float = 1.0,
        limit: int = 100
    ) -> List[Strategy]:
        """
        Get strategies ordered by cost-effectiveness.

        Optimization: Uses indexed cost_benefit_ratio field
        Before: Load all and sort in Python
        After: Database ordering with index

        Args:
            tenant_id: Tenant ID
            min_cost_benefit_ratio: Minimum CBR threshold
            limit: Maximum results

        Returns:
            List of cost-effective strategies
        """
        result = await self.session.execute(
            select(Strategy)
            .where(
                and_(
                    Strategy.tenant_id == tenant_id,
                    Strategy.active == True,
                    Strategy.cost_benefit_ratio >= min_cost_benefit_ratio
                )
            )
            .order_by(Strategy.cost_benefit_ratio.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_with_pagination(
        self,
        tenant_id: str,
        last_id: Optional[UUID] = None,
        limit: int = 100,
        status: Optional[StrategyStatus] = None,
        strategy_type: Optional[StrategyType] = None
    ) -> List[Strategy]:
        """
        List strategies with cursor-based pagination.

        Optimization: Cursor-based pagination instead of OFFSET
        Before: OFFSET 10000 LIMIT 100 scans 10000 rows
        After: WHERE id > last_id LIMIT 100 uses index

        Args:
            tenant_id: Tenant ID
            last_id: Last strategy ID from previous page (cursor)
            limit: Number of results per page
            status: Optional status filter
            strategy_type: Optional type filter

        Returns:
            List of strategies
        """
        query = select(Strategy).where(
            and_(
                Strategy.tenant_id == tenant_id,
                Strategy.active == True
            )
        )

        # Cursor-based pagination
        if last_id is not None:
            query = query.where(Strategy.id > last_id)

        # Optional filters
        if status:
            query = query.where(Strategy.status == status)

        if strategy_type:
            query = query.where(Strategy.strategy_type == strategy_type)

        # Order by ID for consistent pagination
        query = query.order_by(Strategy.id).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_approvals(self, tenant_id: str) -> List[Strategy]:
        """
        Get strategies pending approval.

        Optimization: Uses indexed status and submitted_for_review_at fields

        Args:
            tenant_id: Tenant ID

        Returns:
            List of strategies pending approval
        """
        result = await self.session.execute(
            select(Strategy)
            .where(
                and_(
                    Strategy.tenant_id == tenant_id,
                    Strategy.active == True,
                    Strategy.status == StrategyStatus.UNDER_REVIEW,
                    Strategy.submitted_for_review_at.isnot(None)
                )
            )
            .order_by(Strategy.submitted_for_review_at)
        )
        return list(result.scalars().all())

    async def get_implementation_timeline(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get implementation timeline for approved strategies.

        Optimization: Single query with ordering
        Before: Multiple queries for each strategy
        After: 1 query ordered by start date

        Args:
            tenant_id: Tenant ID

        Returns:
            List of strategies with implementation timeline
        """
        result = await self.session.execute(
            select(
                Strategy.id,
                Strategy.strategy_number,
                Strategy.name,
                Strategy.implementation_started_at,
                Strategy.implementation_completed_at,
                Strategy.implementation_status
            )
            .where(
                and_(
                    Strategy.tenant_id == tenant_id,
                    Strategy.active == True,
                    Strategy.status.in_([StrategyStatus.APPROVED, StrategyStatus.IMPLEMENTED]),
                    Strategy.implementation_started_at.isnot(None)
                )
            )
            .order_by(Strategy.implementation_started_at)
        )
        rows = result.all()

        return [
            {
                "id": str(row.id),
                "strategy_number": row.strategy_number,
                "name": row.name,
                "started_at": row.implementation_started_at.isoformat() if row.implementation_started_at else None,
                "completed_at": row.implementation_completed_at.isoformat() if row.implementation_completed_at else None,
                "status": row.implementation_status
            }
            for row in rows
        ]
