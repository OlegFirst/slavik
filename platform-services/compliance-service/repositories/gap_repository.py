"""
Gap Repository
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import GapModel, ComplianceRequirementModel
from .base_repository import BaseRepository


class GapRepository(BaseRepository[GapModel]):
    """Repository for Gap management"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, GapModel)

    async def get_by_assessment(self, assessment_id: UUID) -> List[GapModel]:
        """Get gaps for assessment"""
        result = await self.db.execute(
            select(GapModel).where(GapModel.assessment_id == assessment_id)
        )
        return list(result.scalars().all())

    async def get_critical_gaps(self, tenant_id: str) -> List[GapModel]:
        """Get critical/high severity gaps"""
        result = await self.db.execute(
            select(GapModel)
            .where(GapModel.tenant_id == tenant_id)
            .where(GapModel.severity.in_(["critical", "high"]))
            .where(GapModel.status.in_(["identified", "assigned", "in_progress"]))
        )
        return list(result.scalars().all())

    async def assign_gap(
        self,
        gap_id: UUID,
        assigned_to: str,
        due_date: datetime
    ) -> Optional[GapModel]:
        """Assign gap to user"""
        await self.db.execute(
            update(GapModel)
            .where(GapModel.id == gap_id)
            .values(
                assigned_to=assigned_to,
                due_date=due_date,
                status="assigned"
            )
        )
        await self.db.commit()
        return await self.get_by_id(gap_id)

    async def update_requirement_coverage(
        self,
        requirement_id: UUID,
        coverage: float
    ):
        """Update requirement coverage based on gap resolution"""
        await self.db.execute(
            update(ComplianceRequirementModel)
            .where(ComplianceRequirementModel.id == requirement_id)
            .values(updated_at=datetime.utcnow())
        )
        await self.db.commit()

    async def get_requirement(self, requirement_id: UUID):
        """Get requirement by ID"""
        result = await self.db.execute(
            select(ComplianceRequirementModel).where(ComplianceRequirementModel.id == requirement_id)
        )
        return result.scalar_one_or_none()
