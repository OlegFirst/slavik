"""
Competence Repository
Data access layer for Competence Records (ISO 22301 Clause 7.2)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import CompetenceRecord, CompetenceLevel, EvidenceType


class CompetenceRepository:
    """Repository for Competence Records"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, record: CompetenceRecord) -> CompetenceRecord:
        """Create competence record"""
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_by_id(self, record_id: int) -> Optional[CompetenceRecord]:
        """Get competence record by ID"""
        result = await self.session.execute(
            select(CompetenceRecord).where(CompetenceRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def get_by_person_and_area(
        self,
        tenant_id: str,
        person_id: str,
        competence_area: str
    ) -> Optional[CompetenceRecord]:
        """Get competence record for person in specific area"""
        result = await self.session.execute(
            select(CompetenceRecord).where(
                and_(
                    CompetenceRecord.tenant_id == tenant_id,
                    CompetenceRecord.person_id == person_id,
                    CompetenceRecord.competence_area == competence_area
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        person_id: Optional[str] = None,
        role_id: Optional[int] = None,
        gap_exists: Optional[bool] = None,
        verified: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompetenceRecord]:
        """List competence records with filters"""
        query = select(CompetenceRecord).where(
            CompetenceRecord.tenant_id == tenant_id
        )

        if person_id:
            query = query.where(CompetenceRecord.person_id == person_id)
        if role_id:
            query = query.where(CompetenceRecord.role_id == role_id)
        if gap_exists is not None:
            query = query.where(CompetenceRecord.gap_exists == gap_exists)
        if verified is not None:
            query = query.where(CompetenceRecord.verified == verified)

        query = query.offset(skip).limit(limit).order_by(
            CompetenceRecord.created_at.desc()
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_person(
        self,
        tenant_id: str,
        person_id: str,
        gap_exists: Optional[bool] = None
    ) -> List[CompetenceRecord]:
        """List competence records for person"""
        query = select(CompetenceRecord).where(
            and_(
                CompetenceRecord.tenant_id == tenant_id,
                CompetenceRecord.person_id == person_id
            )
        )

        if gap_exists is not None:
            query = query.where(CompetenceRecord.gap_exists == gap_exists)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_role(
        self,
        role_id: int,
        gap_exists: Optional[bool] = None
    ) -> List[CompetenceRecord]:
        """List competence records for role"""
        query = select(CompetenceRecord).where(
            CompetenceRecord.role_id == role_id
        )

        if gap_exists is not None:
            query = query.where(CompetenceRecord.gap_exists == gap_exists)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_gaps(
        self,
        tenant_id: str,
        person_id: Optional[str] = None,
        training_required: Optional[bool] = None
    ) -> List[CompetenceRecord]:
        """List competence gaps"""
        query = select(CompetenceRecord).where(
            and_(
                CompetenceRecord.tenant_id == tenant_id,
                CompetenceRecord.gap_exists == True
            )
        )

        if person_id:
            query = query.where(CompetenceRecord.person_id == person_id)
        if training_required is not None:
            query = query.where(CompetenceRecord.training_required == training_required)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_unverified(
        self,
        tenant_id: str,
        person_id: Optional[str] = None
    ) -> List[CompetenceRecord]:
        """List unverified competence records"""
        query = select(CompetenceRecord).where(
            and_(
                CompetenceRecord.tenant_id == tenant_id,
                CompetenceRecord.verified == False
            )
        )

        if person_id:
            query = query.where(CompetenceRecord.person_id == person_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, record: CompetenceRecord) -> CompetenceRecord:
        """Update competence record"""
        record.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def delete(self, record_id: int) -> bool:
        """Delete competence record"""
        record = await self.get_by_id(record_id)
        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False

    async def count_gaps_by_person(self, tenant_id: str) -> dict:
        """Count competence gaps grouped by person"""
        result = await self.session.execute(
            select(
                CompetenceRecord.person_id,
                CompetenceRecord.person_name,
                func.count(CompetenceRecord.id)
            ).where(
                and_(
                    CompetenceRecord.tenant_id == tenant_id,
                    CompetenceRecord.gap_exists == True
                )
            ).group_by(
                CompetenceRecord.person_id,
                CompetenceRecord.person_name
            )
        )

        gaps = {}
        for person_id, person_name, count in result.all():
            gaps[person_id] = {
                "person_name": person_name,
                "gap_count": count
            }

        return gaps

    async def count_by_category(self, tenant_id: str) -> dict:
        """Count competence records by category"""
        result = await self.session.execute(
            select(
                CompetenceRecord.competence_category,
                func.count(CompetenceRecord.id)
            ).where(
                CompetenceRecord.tenant_id == tenant_id
            ).group_by(CompetenceRecord.competence_category)
        )

        counts = {}
        for category, count in result.all():
            counts[category or "uncategorized"] = count

        return counts
