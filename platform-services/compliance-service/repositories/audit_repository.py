"""
Audit Repository

N+1 Query Optimizations:
- Added eager loading for nonconformities relationship
- Optimized dashboard queries with aggregations
- Added methods to fetch audits with all related data in single query
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import AuditModel, NonconformityModel
from .base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditModel]):
    """Repository for Audit management"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AuditModel)

    async def get_by_type(self, tenant_id: str, audit_type: str) -> List[AuditModel]:
        """Get audits by type"""
        result = await self.db.execute(
            select(AuditModel)
            .where(AuditModel.tenant_id == tenant_id)
            .where(AuditModel.audit_type == audit_type)
        )
        return list(result.scalars().all())

    async def get_upcoming(self, tenant_id: str) -> List[AuditModel]:
        """Get upcoming audits"""
        result = await self.db.execute(
            select(AuditModel)
            .where(AuditModel.tenant_id == tenant_id)
            .where(AuditModel.planned_date > datetime.utcnow())
            .where(AuditModel.status == "planned")
        )
        return list(result.scalars().all())

    async def update_findings(
        self,
        audit_id: UUID,
        findings: list,
        nc_ids: list
    ) -> Optional[AuditModel]:
        """Update audit findings"""
        await self.db.execute(
            update(AuditModel)
            .where(AuditModel.id == audit_id)
            .values(
                findings=findings,
                nc_ids=nc_ids
            )
        )
        await self.db.commit()
        return await self.get_by_id(audit_id)

    async def update_result(
        self,
        audit_id: UUID,
        overall_result: str,
        audit_report_url: str
    ) -> Optional[AuditModel]:
        """Update audit result"""
        await self.db.execute(
            update(AuditModel)
            .where(AuditModel.id == audit_id)
            .values(
                overall_result=overall_result,
                audit_report_url=audit_report_url,
                completion_date=datetime.utcnow()
            )
        )
        await self.db.commit()
        return await self.get_by_id(audit_id)

    # ========== N+1 Query Optimization Methods ==========

    async def get_audit_with_details(self, audit_id: UUID) -> Optional[AuditModel]:
        """
        Get audit with all related nonconformities in single query.

        Optimization: Eager load nonconformities relationship
        Before: 1 query for audit + 1 query for NCs = 2 queries
        After: 1 query with selectinload = 1 query

        Args:
            audit_id: Audit ID

        Returns:
            Audit with loaded nonconformities
        """
        result = await self.db.execute(
            select(AuditModel)
            .where(AuditModel.id == audit_id)
            .options(selectinload(AuditModel.nonconformities))
        )
        return result.scalar_one_or_none()

    async def list_with_nonconformities(
        self,
        tenant_id: str,
        audit_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditModel]:
        """
        List audits with their nonconformities eagerly loaded.

        Optimization: Prevent N+1 when accessing nonconformities
        Before: 1 query + N queries for NCs = N+1 queries
        After: 1 query with selectinload = 1 query

        Args:
            tenant_id: Tenant ID
            audit_type: Optional audit type filter
            status: Optional status filter
            limit: Maximum results

        Returns:
            List of audits with loaded nonconformities
        """
        query = select(AuditModel).where(
            AuditModel.tenant_id == tenant_id
        ).options(
            selectinload(AuditModel.nonconformities)
        )

        if audit_type:
            query = query.where(AuditModel.audit_type == audit_type)

        if status:
            query = query.where(AuditModel.status == status)

        query = query.order_by(AuditModel.planned_date.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_dashboard_data(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get audit dashboard data with aggregations.

        Optimization: Single query with aggregations
        Before: Multiple queries for different statistics
        After: 1 query with aggregations

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary with dashboard statistics
        """
        query = select(
            func.count(AuditModel.id).label('total_count'),
            func.sum(case((AuditModel.status == 'planned', 1), else_=0)).label('planned_count'),
            func.sum(case((AuditModel.status == 'in_progress', 1), else_=0)).label('in_progress_count'),
            func.sum(case((AuditModel.status == 'completed', 1), else_=0)).label('completed_count'),
            func.sum(case((AuditModel.audit_type == 'internal', 1), else_=0)).label('internal_count'),
            func.sum(case((AuditModel.audit_type == 'external', 1), else_=0)).label('external_count'),
            func.sum(case((AuditModel.audit_type == 'certification', 1), else_=0)).label('certification_count'),
            func.sum(case((AuditModel.overall_result == 'pass', 1), else_=0)).label('pass_count'),
            func.sum(case((AuditModel.overall_result == 'fail', 1), else_=0)).label('fail_count'),
        ).where(
            AuditModel.tenant_id == tenant_id
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row or row.total_count == 0:
            return {
                "total_count": 0,
                "status_breakdown": {},
                "type_breakdown": {},
                "result_breakdown": {}
            }

        return {
            "total_count": int(row.total_count),
            "status_breakdown": {
                "planned": int(row.planned_count or 0),
                "in_progress": int(row.in_progress_count or 0),
                "completed": int(row.completed_count or 0)
            },
            "type_breakdown": {
                "internal": int(row.internal_count or 0),
                "external": int(row.external_count or 0),
                "certification": int(row.certification_count or 0)
            },
            "result_breakdown": {
                "pass": int(row.pass_count or 0),
                "fail": int(row.fail_count or 0)
            }
        }

    async def get_upcoming_with_preparation_status(
        self,
        tenant_id: str,
        days_ahead: int = 30
    ) -> List[AuditModel]:
        """
        Get upcoming audits with preparation status.

        Optimization: Uses indexed planned_date field

        Args:
            tenant_id: Tenant ID
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming audits
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)

        result = await self.db.execute(
            select(AuditModel)
            .where(
                and_(
                    AuditModel.tenant_id == tenant_id,
                    AuditModel.planned_date.isnot(None),
                    AuditModel.planned_date <= cutoff_date,
                    AuditModel.planned_date >= datetime.utcnow(),
                    AuditModel.status.in_(['planned', 'preparation'])
                )
            )
            .order_by(AuditModel.planned_date)
        )
        return list(result.scalars().all())

    async def get_certification_expiry_alerts(
        self,
        tenant_id: str,
        days_before: int = 90
    ) -> List[AuditModel]:
        """
        Get audits with certifications expiring soon.

        Optimization: Uses indexed certification_valid_until field

        Args:
            tenant_id: Tenant ID
            days_before: Days before expiry to alert

        Returns:
            List of audits with expiring certifications
        """
        from datetime import timedelta

        alert_date = datetime.utcnow() + timedelta(days=days_before)

        result = await self.db.execute(
            select(AuditModel)
            .where(
                and_(
                    AuditModel.tenant_id == tenant_id,
                    AuditModel.certification_valid_until.isnot(None),
                    AuditModel.certification_valid_until <= alert_date,
                    AuditModel.audit_type == 'certification'
                )
            )
            .order_by(AuditModel.certification_valid_until)
        )
        return list(result.scalars().all())
