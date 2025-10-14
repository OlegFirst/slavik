"""
Objective Repository
Data access layer for BCM Objectives (ISO 22301 Clause 6.2)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import BCMObjective


class ObjectiveRepository:
    """Repository for BCM Objectives"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, objective: BCMObjective) -> BCMObjective:
        """Create BCM objective"""
        self.session.add(objective)
        await self.session.flush()
        await self.session.refresh(objective)
        return objective

    async def get_by_id(self, objective_id: int) -> Optional[BCMObjective]:
        """Get objective by ID"""
        result = await self.session.execute(
            select(BCMObjective).where(BCMObjective.id == objective_id)
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        objective_type: Optional[str] = None,
        owner: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BCMObjective]:
        """List objectives for tenant with filters"""
        query = select(BCMObjective).where(BCMObjective.tenant_id == tenant_id)

        if status:
            query = query.where(BCMObjective.status == status)
        if objective_type:
            query = query.where(BCMObjective.objective_type == objective_type)
        if owner:
            query = query.where(BCMObjective.objective_owner == owner)

        query = query.offset(skip).limit(limit).order_by(
            BCMObjective.created_at.desc()
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_owner(
        self,
        tenant_id: str,
        owner: str,
        status: Optional[str] = None
    ) -> List[BCMObjective]:
        """List objectives by owner"""
        query = select(BCMObjective).where(
            and_(
                BCMObjective.tenant_id == tenant_id,
                BCMObjective.objective_owner == owner
            )
        )

        if status:
            query = query.where(BCMObjective.status == status)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_status(
        self,
        tenant_id: str,
        status: str
    ) -> List[BCMObjective]:
        """List objectives by status"""
        result = await self.session.execute(
            select(BCMObjective).where(
                and_(
                    BCMObjective.tenant_id == tenant_id,
                    BCMObjective.status == status
                )
            )
        )
        return list(result.scalars().all())

    async def list_overdue(
        self,
        tenant_id: str,
        before_date: datetime
    ) -> List[BCMObjective]:
        """List overdue objectives"""
        result = await self.session.execute(
            select(BCMObjective).where(
                and_(
                    BCMObjective.tenant_id == tenant_id,
                    BCMObjective.target_date < before_date,
                    BCMObjective.status != "completed"
                )
            )
        )
        return list(result.scalars().all())

    async def list_at_risk(
        self,
        tenant_id: str,
        progress_threshold: int = 70
    ) -> List[BCMObjective]:
        """List objectives at risk (low progress)"""
        result = await self.session.execute(
            select(BCMObjective).where(
                and_(
                    BCMObjective.tenant_id == tenant_id,
                    BCMObjective.progress_percentage < progress_threshold,
                    BCMObjective.status.in_(["not_started", "in_progress"])
                )
            )
        )
        return list(result.scalars().all())

    async def update(self, objective: BCMObjective) -> BCMObjective:
        """Update objective"""
        objective.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(objective)
        return objective

    async def delete(self, objective_id: int) -> bool:
        """Delete objective"""
        objective = await self.get_by_id(objective_id)
        if objective:
            await self.session.delete(objective)
            await self.session.flush()
            return True
        return False

    async def count_by_status(self, tenant_id: str) -> dict:
        """Count objectives by status"""
        result = await self.session.execute(
            select(
                BCMObjective.status,
                func.count(BCMObjective.id)
            ).where(
                BCMObjective.tenant_id == tenant_id
            ).group_by(BCMObjective.status)
        )

        counts = {}
        for status, count in result.all():
            counts[status] = count

        return counts

    async def get_average_progress(self, tenant_id: str) -> float:
        """Get average progress across all objectives"""
        result = await self.session.execute(
            select(func.avg(BCMObjective.progress_percentage)).where(
                BCMObjective.tenant_id == tenant_id
            )
        )
        avg = result.scalar()
        return round(avg, 2) if avg else 0.0

    async def count_overdue(self, tenant_id: str) -> int:
        """Count overdue objectives"""
        result = await self.session.execute(
            select(func.count(BCMObjective.id)).where(
                and_(
                    BCMObjective.tenant_id == tenant_id,
                    BCMObjective.target_date < datetime.utcnow(),
                    BCMObjective.status != "completed"
                )
            )
        )
        return result.scalar() or 0
