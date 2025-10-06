"""
Assessment Repository

N+1 Query Optimizations:
- Added eager loading for gaps relationship
- Optimized dashboard queries with aggregations
- Added methods to fetch assessments with all related data
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import AssessmentModel, GapModel
from .base_repository import BaseRepository


class AssessmentRepository(BaseRepository[AssessmentModel]):
    """Repository for Assessment management"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AssessmentModel)

    async def get_by_standard(self, tenant_id: str, standard: str) -> List[AssessmentModel]:
        """Get assessments by standard"""
        result = await self.db.execute(
            select(AssessmentModel)
            .where(AssessmentModel.tenant_id == tenant_id)
            .where(AssessmentModel.standard == standard)
        )
        return list(result.scalars().all())

    async def get_latest(self, tenant_id: str, standard: str) -> Optional[AssessmentModel]:
        """Get latest assessment for standard"""
        result = await self.db.execute(
            select(AssessmentModel)
            .where(AssessmentModel.tenant_id == tenant_id)
            .where(AssessmentModel.standard == standard)
            .where(AssessmentModel.status == "completed")
            .order_by(AssessmentModel.completion_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_results(
        self,
        assessment_id: UUID,
        overall_score: float,
        compliance_status: str,
        requirements_assessed: dict,
        gaps_identified: dict
    ) -> Optional[AssessmentModel]:
        """Update assessment results"""
        await self.db.execute(
            update(AssessmentModel)
            .where(AssessmentModel.id == assessment_id)
            .values(
                overall_score=overall_score,
                compliance_status=compliance_status,
                requirements_assessed=requirements_assessed,
                gaps_identified=gaps_identified,
                completion_date=datetime.utcnow()
            )
        )
        await self.db.commit()
        return await self.get_by_id(assessment_id)

    async def get_assessment_results(self, assessment_id: UUID) -> dict:
        """Get assessment results"""
        assessment = await self.get_by_id(assessment_id)
        if not assessment:
            return {}
        return {
            "overall_score": assessment.overall_score,
            "compliance_status": assessment.compliance_status,
            "requirements_assessed": assessment.requirements_assessed or {},
            "gaps_identified": assessment.gaps_identified or {}
        }

    # ========== N+1 Query Optimization Methods ==========

    async def get_assessment_complete(self, assessment_id: UUID) -> Optional[AssessmentModel]:
        """
        Get assessment with all related gaps in single query.

        Optimization: Eager load gaps relationship
        Before: 1 query for assessment + 1 query for gaps = 2 queries
        After: 1 query with selectinload = 1 query

        Args:
            assessment_id: Assessment ID

        Returns:
            Assessment with loaded gaps
        """
        result = await self.db.execute(
            select(AssessmentModel)
            .where(AssessmentModel.id == assessment_id)
            .options(selectinload(AssessmentModel.gaps))
        )
        return result.scalar_one_or_none()

    async def list_with_gaps(
        self,
        tenant_id: str,
        standard: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[AssessmentModel]:
        """
        List assessments with their gaps eagerly loaded.

        Optimization: Prevent N+1 when accessing gaps
        Before: 1 query + N queries for gaps = N+1 queries
        After: 1 query with selectinload = 1 query

        Args:
            tenant_id: Tenant ID
            standard: Optional standard filter
            status: Optional status filter
            limit: Maximum results

        Returns:
            List of assessments with loaded gaps
        """
        query = select(AssessmentModel).where(
            AssessmentModel.tenant_id == tenant_id
        ).options(
            selectinload(AssessmentModel.gaps)
        )

        if standard:
            query = query.where(AssessmentModel.standard == standard)

        if status:
            query = query.where(AssessmentModel.status == status)

        query = query.order_by(AssessmentModel.completion_date.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_dashboard_data(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get assessment dashboard data with aggregations.

        Optimization: Single query with aggregations
        Before: Multiple queries for different statistics
        After: 1 query with aggregations

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary with dashboard statistics
        """
        query = select(
            func.count(AssessmentModel.id).label('total_count'),
            # By status
            func.sum(case((AssessmentModel.status == 'draft', 1), else_=0)).label('draft_count'),
            func.sum(case((AssessmentModel.status == 'in_progress', 1), else_=0)).label('in_progress_count'),
            func.sum(case((AssessmentModel.status == 'under_review', 1), else_=0)).label('under_review_count'),
            func.sum(case((AssessmentModel.status == 'approved', 1), else_=0)).label('approved_count'),
            func.sum(case((AssessmentModel.status == 'completed', 1), else_=0)).label('completed_count'),
            # By compliance status
            func.sum(case((AssessmentModel.compliance_status == 'compliant', 1), else_=0)).label('compliant_count'),
            func.sum(case((AssessmentModel.compliance_status == 'partial_compliance', 1), else_=0)).label('partial_count'),
            func.sum(case((AssessmentModel.compliance_status == 'non_compliant', 1), else_=0)).label('non_compliant_count'),
            # Scores
            func.avg(AssessmentModel.overall_score).label('avg_score'),
            func.min(AssessmentModel.overall_score).label('min_score'),
            func.max(AssessmentModel.overall_score).label('max_score'),
        ).where(
            AssessmentModel.tenant_id == tenant_id
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row or row.total_count == 0:
            return {
                "total_count": 0,
                "status_breakdown": {},
                "compliance_breakdown": {},
                "score_statistics": {}
            }

        return {
            "total_count": int(row.total_count),
            "status_breakdown": {
                "draft": int(row.draft_count or 0),
                "in_progress": int(row.in_progress_count or 0),
                "under_review": int(row.under_review_count or 0),
                "approved": int(row.approved_count or 0),
                "completed": int(row.completed_count or 0)
            },
            "compliance_breakdown": {
                "compliant": int(row.compliant_count or 0),
                "partial_compliance": int(row.partial_count or 0),
                "non_compliant": int(row.non_compliant_count or 0)
            },
            "score_statistics": {
                "average": float(row.avg_score) if row.avg_score else 0,
                "minimum": float(row.min_score) if row.min_score else 0,
                "maximum": float(row.max_score) if row.max_score else 0
            }
        }

    async def get_assessor_workload(self, tenant_id: str) -> Dict[str, int]:
        """
        Get assessment workload by assessor.

        Optimization: Aggregation query grouped by assessor
        Before: Load all assessments and group in Python
        After: Database aggregation

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary mapping assessor to assessment count
        """
        query = select(
            AssessmentModel.assessor_id,
            func.count(AssessmentModel.id).label('assessment_count')
        ).where(
            and_(
                AssessmentModel.tenant_id == tenant_id,
                AssessmentModel.assessor_id.isnot(None),
                AssessmentModel.status.in_(['in_progress', 'draft'])
            )
        ).group_by(AssessmentModel.assessor_id)

        result = await self.db.execute(query)
        rows = result.all()

        return {row.assessor_id: int(row.assessment_count) for row in rows}

    async def get_compliance_trend(
        self,
        tenant_id: str,
        standard: str,
        limit: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get compliance score trend over time for a standard.

        Optimization: Single query with ordering
        Before: Multiple queries for each time period
        After: 1 query ordered by completion date

        Args:
            tenant_id: Tenant ID
            standard: Standard name
            limit: Number of historical assessments to include

        Returns:
            List of assessment scores over time
        """
        result = await self.db.execute(
            select(
                AssessmentModel.completion_date,
                AssessmentModel.overall_score,
                AssessmentModel.compliance_status
            )
            .where(
                and_(
                    AssessmentModel.tenant_id == tenant_id,
                    AssessmentModel.standard == standard,
                    AssessmentModel.status == 'completed',
                    AssessmentModel.completion_date.isnot(None)
                )
            )
            .order_by(AssessmentModel.completion_date.desc())
            .limit(limit)
        )
        rows = result.all()

        return [
            {
                "completion_date": row.completion_date.isoformat() if row.completion_date else None,
                "overall_score": float(row.overall_score) if row.overall_score else 0,
                "compliance_status": row.compliance_status
            }
            for row in rows
        ]
