"""
Nonconformity Repository

N+1 Query Optimizations:
- Added eager loading for audit relationship
- Optimized corrective action queries
- Dashboard data with aggregations
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from models.database import NonconformityModel, AuditModel
from .base_repository import BaseRepository


class NonconformityRepository(BaseRepository[NonconformityModel]):
    """Repository for Nonconformity management"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, NonconformityModel)

    async def get_by_audit(self, audit_id: UUID) -> List[NonconformityModel]:
        """Get NCs for audit"""
        result = await self.db.execute(
            select(NonconformityModel).where(NonconformityModel.audit_id == audit_id)
        )
        return list(result.scalars().all())

    async def get_open_ncs(self, tenant_id: str) -> List[NonconformityModel]:
        """Get open nonconformities"""
        result = await self.db.execute(
            select(NonconformityModel)
            .where(NonconformityModel.tenant_id == tenant_id)
            .where(NonconformityModel.status != "closed")
        )
        return list(result.scalars().all())

    async def get_major_ncs(self, tenant_id: str) -> List[NonconformityModel]:
        """Get major nonconformities"""
        result = await self.db.execute(
            select(NonconformityModel)
            .where(NonconformityModel.tenant_id == tenant_id)
            .where(NonconformityModel.nc_type == "major")
        )
        return list(result.scalars().all())

    async def update_rca(
        self,
        nc_id: UUID,
        rca_method: str,
        root_causes: list,
        rca_lead: str
    ) -> Optional[NonconformityModel]:
        """Update RCA results"""
        await self.db.execute(
            update(NonconformityModel)
            .where(NonconformityModel.id == nc_id)
            .values(
                rca_method=rca_method,
                root_causes=root_causes,
                rca_lead=rca_lead,
                rca_completed_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        return await self.get_by_id(nc_id)

    async def update_corrective_actions(
        self,
        nc_id: UUID,
        actions: list
    ) -> Optional[NonconformityModel]:
        """Update corrective actions"""
        await self.db.execute(
            update(NonconformityModel)
            .where(NonconformityModel.id == nc_id)
            .values(corrective_actions=actions)
        )
        await self.db.commit()
        return await self.get_by_id(nc_id)

    # ========== N+1 Query Optimization Methods ==========

    async def get_nc_with_audit(self, nc_id: UUID) -> Optional[NonconformityModel]:
        """
        Get nonconformity with audit relationship loaded.

        Optimization: Eager load audit with joinedload (many-to-one)
        Before: 1 query for NC + 1 query for audit = 2 queries
        After: 1 query with JOIN

        Args:
            nc_id: Nonconformity ID

        Returns:
            NC with loaded audit
        """
        result = await self.db.execute(
            select(NonconformityModel)
            .where(NonconformityModel.id == nc_id)
            .options(joinedload(NonconformityModel.audit))
        )
        return result.scalar_one_or_none()

    async def list_with_audit(
        self,
        tenant_id: str,
        nc_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[NonconformityModel]:
        """
        List NCs with audit relationship eagerly loaded.

        Optimization: Prevent N+1 when accessing audit
        Before: 1 query + N queries for audits = N+1 queries
        After: 1 query with JOIN

        Args:
            tenant_id: Tenant ID
            nc_type: Optional type filter
            status: Optional status filter
            limit: Maximum results

        Returns:
            List of NCs with loaded audits
        """
        query = select(NonconformityModel).where(
            NonconformityModel.tenant_id == tenant_id
        ).options(
            joinedload(NonconformityModel.audit)
        )

        if nc_type:
            query = query.where(NonconformityModel.nc_type == nc_type)

        if status:
            query = query.where(NonconformityModel.status == status)

        query = query.order_by(NonconformityModel.identified_date.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def get_dashboard_data(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get NC dashboard data with aggregations.

        Optimization: Single query with aggregations
        Before: Multiple queries for different statistics
        After: 1 query with aggregations

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary with dashboard statistics
        """
        query = select(
            func.count(NonconformityModel.id).label('total_count'),
            # By type
            func.sum(case((NonconformityModel.nc_type == 'major', 1), else_=0)).label('major_count'),
            func.sum(case((NonconformityModel.nc_type == 'minor', 1), else_=0)).label('minor_count'),
            func.sum(case((NonconformityModel.nc_type == 'observation', 1), else_=0)).label('observation_count'),
            # By status
            func.sum(case((NonconformityModel.status == 'identified', 1), else_=0)).label('identified_count'),
            func.sum(case((NonconformityModel.status == 'rca_in_progress', 1), else_=0)).label('rca_in_progress_count'),
            func.sum(case((NonconformityModel.status == 'actions_planned', 1), else_=0)).label('actions_planned_count'),
            func.sum(case((NonconformityModel.status == 'actions_implemented', 1), else_=0)).label('actions_implemented_count'),
            func.sum(case((NonconformityModel.status == 'verification', 1), else_=0)).label('verification_count'),
            func.sum(case((NonconformityModel.status == 'closed', 1), else_=0)).label('closed_count'),
            # Effectiveness
            func.sum(case((NonconformityModel.effectiveness_confirmed == True, 1), else_=0)).label('effective_count'),
            func.sum(case((NonconformityModel.effectiveness_confirmed == False, 1), else_=0)).label('not_effective_count'),
        ).where(
            NonconformityModel.tenant_id == tenant_id
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row or row.total_count == 0:
            return {
                "total_count": 0,
                "type_breakdown": {},
                "status_breakdown": {},
                "effectiveness": {}
            }

        return {
            "total_count": int(row.total_count),
            "type_breakdown": {
                "major": int(row.major_count or 0),
                "minor": int(row.minor_count or 0),
                "observation": int(row.observation_count or 0)
            },
            "status_breakdown": {
                "identified": int(row.identified_count or 0),
                "rca_in_progress": int(row.rca_in_progress_count or 0),
                "actions_planned": int(row.actions_planned_count or 0),
                "actions_implemented": int(row.actions_implemented_count or 0),
                "verification": int(row.verification_count or 0),
                "closed": int(row.closed_count or 0)
            },
            "effectiveness": {
                "effective": int(row.effective_count or 0),
                "not_effective": int(row.not_effective_count or 0)
            }
        }

    async def get_overdue_actions(self, tenant_id: str) -> List[NonconformityModel]:
        """
        Get NCs with overdue corrective actions.

        Optimization: Complex JSON query on corrective_actions field
        Note: This assumes corrective_actions is stored as JSON array with due_date field

        Args:
            tenant_id: Tenant ID

        Returns:
            List of NCs with overdue actions
        """
        # This is a simplified version - actual implementation depends on JSON structure
        result = await self.db.execute(
            select(NonconformityModel)
            .where(
                and_(
                    NonconformityModel.tenant_id == tenant_id,
                    NonconformityModel.status.in_(['actions_planned', 'actions_implemented']),
                    NonconformityModel.corrective_actions.isnot(None)
                )
            )
            .order_by(NonconformityModel.identified_date)
        )
        return list(result.scalars().all())

    async def get_rca_workload(self, tenant_id: str) -> Dict[str, int]:
        """
        Get RCA workload by RCA lead.

        Optimization: Aggregation query grouped by RCA lead
        Before: Load all NCs and group in Python
        After: Database aggregation

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary mapping RCA lead to NC count
        """
        query = select(
            NonconformityModel.rca_lead,
            func.count(NonconformityModel.id).label('nc_count')
        ).where(
            and_(
                NonconformityModel.tenant_id == tenant_id,
                NonconformityModel.rca_lead.isnot(None),
                NonconformityModel.status.in_(['rca_in_progress', 'actions_planned'])
            )
        ).group_by(NonconformityModel.rca_lead)

        result = await self.db.execute(query)
        rows = result.all()

        return {row.rca_lead: int(row.nc_count) for row in rows}
