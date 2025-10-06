"""
Evidence Repository

N+1 Query Optimizations:
- Added eager loading for requirement relationship
- Optimized verification queries with aggregations
- Dashboard data with single query
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.database import EvidenceModel, ComplianceRequirementModel
from .base_repository import BaseRepository


class EvidenceRepository(BaseRepository[EvidenceModel]):
    """Repository for Evidence management"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, EvidenceModel)

    async def get_by_requirement(self, requirement_id: UUID, tenant_id: str) -> List[EvidenceModel]:
        """Get all evidence for a requirement"""
        result = await self.db.execute(
            select(EvidenceModel)
            .where(EvidenceModel.requirement_id == requirement_id)
            .where(EvidenceModel.tenant_id == tenant_id)
        )
        return list(result.scalars().all())

    async def get_verified_evidence(self, requirement_id: UUID) -> List[EvidenceModel]:
        """Get verified evidence for requirement"""
        result = await self.db.execute(
            select(EvidenceModel)
            .where(EvidenceModel.requirement_id == requirement_id)
            .where(EvidenceModel.status == "verified")
        )
        return list(result.scalars().all())

    async def update_verification(
        self,
        evidence_id: UUID,
        verification_status: str,
        verified_by: str
    ) -> Optional[EvidenceModel]:
        """Update verification status"""
        from datetime import datetime
        await self.db.execute(
            update(EvidenceModel)
            .where(EvidenceModel.id == evidence_id)
            .values(
                verification_status=verification_status,
                verified_by=verified_by,
                verified_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        return await self.get_by_id(evidence_id)

    async def get_requirement(self, requirement_id: UUID):
        """Get requirement by ID"""
        result = await self.db.execute(
            select(ComplianceRequirementModel).where(ComplianceRequirementModel.id == requirement_id)
        )
        return result.scalar_one_or_none()

    # ========== N+1 Query Optimization Methods ==========

    async def get_evidence_with_requirement(self, evidence_id: UUID) -> Optional[EvidenceModel]:
        """
        Get evidence with requirement relationship loaded.

        Optimization: Eager load requirement with joinedload (many-to-one)
        Before: 1 query for evidence + 1 query for requirement = 2 queries
        After: 1 query with JOIN

        Args:
            evidence_id: Evidence ID

        Returns:
            Evidence with loaded requirement
        """
        result = await self.db.execute(
            select(EvidenceModel)
            .where(EvidenceModel.id == evidence_id)
            .options(joinedload(EvidenceModel.requirement))
        )
        return result.scalar_one_or_none()

    async def list_with_requirements(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        verification_status: Optional[str] = None,
        limit: int = 100
    ) -> List[EvidenceModel]:
        """
        List evidence with requirements eagerly loaded.

        Optimization: Prevent N+1 when accessing requirement
        Before: 1 query + N queries for requirements = N+1 queries
        After: 1 query with JOIN

        Args:
            tenant_id: Tenant ID
            status: Optional status filter
            verification_status: Optional verification status filter
            limit: Maximum results

        Returns:
            List of evidence with loaded requirements
        """
        query = select(EvidenceModel).where(
            EvidenceModel.tenant_id == tenant_id
        ).options(
            joinedload(EvidenceModel.requirement)
        )

        if status:
            query = query.where(EvidenceModel.status == status)

        if verification_status:
            query = query.where(EvidenceModel.verification_status == verification_status)

        query = query.order_by(EvidenceModel.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def get_dashboard_data(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get evidence dashboard data with aggregations.

        Optimization: Single query with aggregations
        Before: Multiple queries for different statistics
        After: 1 query with aggregations

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary with dashboard statistics
        """
        query = select(
            func.count(EvidenceModel.id).label('total_count'),
            # By status
            func.sum(case((EvidenceModel.status == 'draft', 1), else_=0)).label('draft_count'),
            func.sum(case((EvidenceModel.status == 'submitted', 1), else_=0)).label('submitted_count'),
            func.sum(case((EvidenceModel.status == 'under_review', 1), else_=0)).label('under_review_count'),
            func.sum(case((EvidenceModel.status == 'verified', 1), else_=0)).label('verified_count'),
            func.sum(case((EvidenceModel.status == 'rejected', 1), else_=0)).label('rejected_count'),
            # By verification status
            func.sum(case((EvidenceModel.verification_status == 'verified', 1), else_=0)).label('ver_verified_count'),
            func.sum(case((EvidenceModel.verification_status == 'expired', 1), else_=0)).label('ver_expired_count'),
            func.sum(case((EvidenceModel.verification_status == 'invalid', 1), else_=0)).label('ver_invalid_count'),
            # By evidence type
            func.sum(case((EvidenceModel.evidence_type == 'policy', 1), else_=0)).label('policy_count'),
            func.sum(case((EvidenceModel.evidence_type == 'procedure', 1), else_=0)).label('procedure_count'),
            func.sum(case((EvidenceModel.evidence_type == 'record', 1), else_=0)).label('record_count'),
        ).where(
            EvidenceModel.tenant_id == tenant_id
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row or row.total_count == 0:
            return {
                "total_count": 0,
                "status_breakdown": {},
                "verification_breakdown": {},
                "type_breakdown": {}
            }

        return {
            "total_count": int(row.total_count),
            "status_breakdown": {
                "draft": int(row.draft_count or 0),
                "submitted": int(row.submitted_count or 0),
                "under_review": int(row.under_review_count or 0),
                "verified": int(row.verified_count or 0),
                "rejected": int(row.rejected_count or 0)
            },
            "verification_breakdown": {
                "verified": int(row.ver_verified_count or 0),
                "expired": int(row.ver_expired_count or 0),
                "invalid": int(row.ver_invalid_count or 0)
            },
            "type_breakdown": {
                "policy": int(row.policy_count or 0),
                "procedure": int(row.procedure_count or 0),
                "record": int(row.record_count or 0)
            }
        }

    async def get_expiring_evidence(
        self,
        tenant_id: str,
        days_before: int = 30
    ) -> List[EvidenceModel]:
        """
        Get evidence expiring soon.

        Optimization: Uses indexed validity_period_end field

        Args:
            tenant_id: Tenant ID
            days_before: Days before expiry to alert

        Returns:
            List of expiring evidence
        """
        from datetime import timedelta

        alert_date = datetime.utcnow() + timedelta(days=days_before)

        result = await self.db.execute(
            select(EvidenceModel)
            .where(
                and_(
                    EvidenceModel.tenant_id == tenant_id,
                    EvidenceModel.validity_period_end.isnot(None),
                    EvidenceModel.validity_period_end <= alert_date,
                    EvidenceModel.validity_period_end >= datetime.utcnow(),
                    EvidenceModel.verification_status == 'verified'
                )
            )
            .order_by(EvidenceModel.validity_period_end)
        )
        return list(result.scalars().all())

    async def get_reviewer_workload(self, tenant_id: str) -> Dict[str, int]:
        """
        Get evidence review workload by reviewer.

        Optimization: Aggregation query grouped by reviewer
        Before: Load all evidence and group in Python
        After: Database aggregation

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary mapping reviewer to evidence count
        """
        query = select(
            EvidenceModel.reviewer_id,
            func.count(EvidenceModel.id).label('evidence_count')
        ).where(
            and_(
                EvidenceModel.tenant_id == tenant_id,
                EvidenceModel.reviewer_id.isnot(None),
                EvidenceModel.status.in_(['under_review', 'submitted'])
            )
        ).group_by(EvidenceModel.reviewer_id)

        result = await self.db.execute(query)
        rows = result.all()

        return {row.reviewer_id: int(row.evidence_count) for row in rows}
