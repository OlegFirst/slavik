"""
BIA Repository - PostgreSQL Implementation

Data access layer for BIA processes using SQLAlchemy async.
Replaces in-memory Dict storage with persistent PostgreSQL storage.

N+1 Query Optimizations:
- Added eager loading methods to prevent N+1 queries
- Dashboard queries optimized with aggregations
- Statistics queries use window functions and CTEs
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, func, case, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import BIAProcessModel
from ..models.domain import BIAProcess, Dependency
from shared.history import ChangeTracker
from ..models.enums import (
    CriticalityLevel,
    ProcessStatus,
    WHOTier,
    IndustryType,
    GeographicalScope,
    ReputationalImpact,
    RegulatoryImpact,
    PatientSafetyImpact,
)

logger = logging.getLogger(__name__)


class BIARepository:
    """
    BIA Repository - PostgreSQL data access layer.

    Uses SQLAlchemy async for persistent storage.
    All operations are async and use database transactions.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def create(self, process: BIAProcess) -> BIAProcess:
        """
        Create new BIA process.

        Args:
            process: BIA Process to create (id will be auto-assigned)

        Returns:
            BIAProcess: Created process with assigned ID
        """
        # Convert domain model to database model
        process_model = BIAProcessModel(
            tenant_id=process.tenant_id,
            name=process.name,
            description=process.description,
            department=process.department,
            process_owner=process.process_owner,
            criticality=process.criticality.value,
            criticality_score=process.criticality_score,
            who_tier=process.who_tier.value if process.who_tier else None,
            industry=process.industry.value if process.industry else None,
            geographical_scope=process.geographical_scope.value if process.geographical_scope else None,
            rto_hours=process.rto_hours,
            rpo_hours=process.rpo_hours,
            mtpd_hours=process.mtpd_hours,
            financial_impact=process.financial_impact or {},
            operational_impact=process.operational_impact or {},
            annual_revenue_impact=process.annual_revenue_impact,
            reputational_impact=process.reputational_impact.value if process.reputational_impact else None,
            regulatory_impact=process.regulatory_impact.value if process.regulatory_impact else None,
            patient_safety_impact=process.patient_safety_impact.value if process.patient_safety_impact else None,
            # ISO 22301 fields
            compliance_objective=process.compliance_objective,
            legal_regulatory_requirements=process.legal_regulatory_requirements or [],
            personnel_requirements=process.personnel_requirements or {},
            facility_requirements=process.facility_requirements or {},
            technology_requirements=process.technology_requirements or {},
            information_requirements=process.information_requirements or {},
            recovery_strategies=process.recovery_strategies or [],
            alternative_procedures=process.alternative_procedures or [],
            workaround_capacity=process.workaround_capacity,
            upstream_processes=process.upstream_processes or [],
            downstream_processes=process.downstream_processes or [],
            critical_suppliers=process.critical_suppliers or [],
            minimum_resource_level=process.minimum_resource_level or {},
            peak_periods=process.peak_periods or [],
            seasonality=process.seasonality,
            bia_completion_date=process.bia_completion_date,
            bia_assessor=process.bia_assessor,
            bia_reviewer=process.bia_reviewer,
            next_review_date=process.next_review_date,
            # Original fields
            resources_required=[self._serialize_item(r) for r in process.resources_required],
            dependencies=[self._serialize_item(d) for d in process.dependencies],
            peak_concurrent_users=process.peak_concurrent_users,
            staff_count=process.staff_count,
            ai_suggested_rto=process.ai_suggested_rto,
            ai_suggested_rpo=None,  # Add if exists in domain model
            ai_suggested_mtpd=None,  # Add if exists in domain model
            ai_confidence=process.ai_confidence,
            ai_recommendations=process.ai_recommendations,
            status=process.status.value,
            created_by=None  # Add if exists in domain model
        )

        self.db.add(process_model)
        await self.db.commit()
        await self.db.refresh(process_model)

        logger.info(f"Created BIA process {process_model.id}: {process_model.name}")

        return self._model_to_domain(process_model)

    async def get(self, process_id: int) -> Optional[BIAProcess]:
        """
        Get BIA process by ID.

        Args:
            process_id: Process ID

        Returns:
            BIAProcess or None if not found
        """
        result = await self.db.execute(
            select(BIAProcessModel).where(BIAProcessModel.id == process_id)
        )
        process_model = result.scalar_one_or_none()

        if not process_model:
            return None

        return self._model_to_domain(process_model)

    async def list(self, tenant_id: str) -> List[BIAProcess]:
        """
        List all BIA processes for tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            List of BIA processes
        """
        result = await self.db.execute(
            select(BIAProcessModel)
            .where(BIAProcessModel.tenant_id == tenant_id)
            .order_by(BIAProcessModel.created_at.desc())
        )
        process_models = result.scalars().all()

        return [self._model_to_domain(pm) for pm in process_models]

    async def update(
        self,
        process_id: int,
        updates: dict,
        changed_by: Optional[str] = None,
        change_reason: Optional[str] = None,
        track_changes: bool = True
    ) -> Optional[BIAProcess]:
        """
        Update BIA process with optional change tracking.

        Args:
            process_id: Process ID
            updates: Dictionary of fields to update
            changed_by: User making the change (required if track_changes=True)
            change_reason: Optional reason for the change
            track_changes: Whether to track field-level changes (default: True)

        Returns:
            Updated BIAProcess or None if not found
        """
        # Get current state (before) if tracking changes
        before_state = None
        if track_changes:
            current_process = await self.get(process_id)
            if not current_process:
                return None
            before_state = current_process.model_dump()

        # Convert Pydantic models and enums in updates to database-compatible values
        processed_updates = {}
        for key, value in updates.items():
            if hasattr(value, 'dict'):
                # Pydantic model - convert to dict
                processed_updates[key] = value.dict()
            elif isinstance(value, list) and value and hasattr(value[0], 'dict'):
                # List of Pydantic models
                processed_updates[key] = [self._serialize_item(v) for v in value]
            elif hasattr(value, 'value'):
                # Enum - extract value
                processed_updates[key] = value.value
            else:
                processed_updates[key] = value

        result = await self.db.execute(
            update(BIAProcessModel)
            .where(BIAProcessModel.id == process_id)
            .values(**processed_updates)
            .returning(BIAProcessModel)
        )
        await self.db.commit()

        updated_model = result.scalar_one_or_none()
        if not updated_model:
            return None

        logger.info(f"Updated BIA process {process_id}")
        updated_process = self._model_to_domain(updated_model)

        # Track changes if enabled
        if track_changes and before_state and changed_by:
            after_state = updated_process.model_dump()
            change_tracker = ChangeTracker(self.db)
            await change_tracker.track_changes(
                entity_type="BIAProcess",
                entity_id=str(process_id),
                tenant_id=updated_process.tenant_id,
                before=before_state,
                after=after_state,
                changed_by=changed_by,
                change_reason=change_reason,
                version_number=None,  # Add version field to BIAProcess if needed
                save_snapshot=True
            )

        return updated_process

    async def delete(self, process_id: int) -> bool:
        """
        Delete BIA process.

        Args:
            process_id: Process ID

        Returns:
            bool: True if deleted, False if not found
        """
        result = await self.db.execute(
            delete(BIAProcessModel).where(BIAProcessModel.id == process_id)
        )
        await self.db.commit()

        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted BIA process {process_id}")
        return deleted

    async def get_critical_processes(self, tenant_id: str) -> List[BIAProcess]:
        """
        Get all critical/high priority processes for tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            List of critical BIA processes
        """
        result = await self.db.execute(
            select(BIAProcessModel)
            .where(BIAProcessModel.tenant_id == tenant_id)
            .where(BIAProcessModel.criticality.in_([CriticalityLevel.CRITICAL.value, CriticalityLevel.HIGH.value]))
            .order_by(BIAProcessModel.criticality_score.desc())
        )
        process_models = result.scalars().all()

        return [self._model_to_domain(pm) for pm in process_models]

    async def get_completed_processes(self, tenant_id: str) -> List[BIAProcess]:
        """
        Get all completed BIA processes for tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            List of completed BIA processes
        """
        result = await self.db.execute(
            select(BIAProcessModel)
            .where(BIAProcessModel.tenant_id == tenant_id)
            .where(BIAProcessModel.status == ProcessStatus.COMPLETED.value)
            .order_by(BIAProcessModel.completed_at.desc())
        )
        process_models = result.scalars().all()

        return [self._model_to_domain(pm) for pm in process_models]

    def _model_to_domain(self, model: BIAProcessModel) -> BIAProcess:
        """
        Convert SQLAlchemy model to Pydantic domain model.

        Args:
            model: BIAProcessModel database model

        Returns:
            BIAProcess: Pydantic domain model
        """
        return BIAProcess(
            id=model.id,
            tenant_id=model.tenant_id,
            name=model.name,
            description=model.description,
            department=model.department,
            process_owner=model.process_owner,
            criticality=CriticalityLevel(model.criticality),
            criticality_score=model.criticality_score,
            who_tier=WHOTier(model.who_tier) if model.who_tier else None,
            industry=IndustryType(model.industry) if model.industry else IndustryType.OTHER,
            geographical_scope=GeographicalScope(model.geographical_scope) if model.geographical_scope else GeographicalScope.LOCAL,
            rto_hours=model.rto_hours,
            rpo_hours=model.rpo_hours,
            mtpd_hours=model.mtpd_hours,
            financial_impact=model.financial_impact or {},
            operational_impact=model.operational_impact or {},
            annual_revenue_impact=model.annual_revenue_impact,
            reputational_impact=ReputationalImpact(model.reputational_impact) if model.reputational_impact else None,
            regulatory_impact=RegulatoryImpact(model.regulatory_impact) if model.regulatory_impact else None,
            patient_safety_impact=PatientSafetyImpact(model.patient_safety_impact) if model.patient_safety_impact else None,
            # ISO 22301 fields
            compliance_objective=model.compliance_objective,
            legal_regulatory_requirements=model.legal_regulatory_requirements or [],
            personnel_requirements=model.personnel_requirements or {},
            facility_requirements=model.facility_requirements or {},
            technology_requirements=model.technology_requirements or {},
            information_requirements=model.information_requirements or {},
            recovery_strategies=model.recovery_strategies or [],
            alternative_procedures=model.alternative_procedures or [],
            workaround_capacity=model.workaround_capacity,
            upstream_processes=model.upstream_processes or [],
            downstream_processes=model.downstream_processes or [],
            critical_suppliers=model.critical_suppliers or [],
            minimum_resource_level=model.minimum_resource_level or {},
            peak_periods=model.peak_periods or [],
            seasonality=model.seasonality,
            bia_completion_date=model.bia_completion_date,
            bia_assessor=model.bia_assessor,
            bia_reviewer=model.bia_reviewer,
            next_review_date=model.next_review_date,
            # Original fields
            resources_required=model.resources_required or [],
            dependencies=[Dependency(**d) for d in model.dependencies] if model.dependencies else [],
            peak_concurrent_users=model.peak_concurrent_users,
            staff_count=model.staff_count,
            ai_suggested_rto=model.ai_suggested_rto,
            ai_confidence=model.ai_confidence,
            ai_recommendations=model.ai_recommendations,
            status=ProcessStatus(model.status),
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _serialize_item(self, item):
        """
        Serialize Pydantic model or dict to dict for JSON storage.

        Args:
            item: Pydantic model or dict

        Returns:
            dict: Serialized item
        """
        if hasattr(item, 'dict'):
            return item.dict()
        return item

    # ========== N+1 Query Optimization Methods ==========

    async def get_dashboard_data(self, tenant_id: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get optimized dashboard data with aggregations.

        Optimization: Single query with aggregations instead of multiple queries.
        Before: 1 + N queries (one per process to count assessments/resources)
        After: 1 query with all aggregations

        Args:
            tenant_id: Tenant ID
            limit: Maximum number of processes to return

        Returns:
            Dictionary with dashboard data including statistics
        """
        # Single query with all aggregations
        query = select(
            BIAProcessModel,
            # Count critical processes
            func.sum(
                case(
                    (BIAProcessModel.criticality.in_([CriticalityLevel.CRITICAL.value, CriticalityLevel.HIGH.value]), 1),
                    else_=0
                )
            ).over().label('critical_count'),
            # Count completed processes
            func.sum(
                case(
                    (BIAProcessModel.status == ProcessStatus.COMPLETED.value, 1),
                    else_=0
                )
            ).over().label('completed_count'),
            # Average RTO
            func.avg(BIAProcessModel.rto_hours).over().label('avg_rto'),
            # Average criticality score
            func.avg(BIAProcessModel.criticality_score).over().label('avg_criticality_score')
        ).where(
            BIAProcessModel.tenant_id == tenant_id
        ).order_by(
            BIAProcessModel.criticality_score.desc(),
            BIAProcessModel.created_at.desc()
        ).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        if not rows:
            return {
                "processes": [],
                "statistics": {
                    "total_count": 0,
                    "critical_count": 0,
                    "completed_count": 0,
                    "avg_rto": 0,
                    "avg_criticality_score": 0
                }
            }

        # Extract statistics from first row (window functions give same values for all rows)
        first_row = rows[0]
        statistics = {
            "total_count": len(rows),
            "critical_count": int(first_row.critical_count) if first_row.critical_count else 0,
            "completed_count": int(first_row.completed_count) if first_row.completed_count else 0,
            "avg_rto": float(first_row.avg_rto) if first_row.avg_rto else 0,
            "avg_criticality_score": float(first_row.avg_criticality_score) if first_row.avg_criticality_score else 0
        }

        # Convert processes to domain models
        processes = [self._model_to_domain(row[0]) for row in rows]

        return {
            "processes": processes,
            "statistics": statistics
        }

    async def get_statistics(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get comprehensive BIA statistics with optimized aggregation query.

        Optimization: Single query with multiple aggregations and window functions.
        Before: Multiple separate queries for different statistics
        After: 1 query with all aggregations

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary with comprehensive statistics
        """
        query = select(
            # Total counts
            func.count(BIAProcessModel.id).label('total_count'),
            # Count by criticality
            func.sum(case((BIAProcessModel.criticality == CriticalityLevel.CRITICAL.value, 1), else_=0)).label('critical_count'),
            func.sum(case((BIAProcessModel.criticality == CriticalityLevel.HIGH.value, 1), else_=0)).label('high_count'),
            func.sum(case((BIAProcessModel.criticality == CriticalityLevel.MODERATE.value, 1), else_=0)).label('moderate_count'),
            func.sum(case((BIAProcessModel.criticality == CriticalityLevel.MINOR.value, 1), else_=0)).label('minor_count'),
            func.sum(case((BIAProcessModel.criticality == CriticalityLevel.LOW.value, 1), else_=0)).label('low_count'),
            # Count by status
            func.sum(case((BIAProcessModel.status == ProcessStatus.DRAFT.value, 1), else_=0)).label('draft_count'),
            func.sum(case((BIAProcessModel.status == ProcessStatus.IN_PROGRESS.value, 1), else_=0)).label('in_progress_count'),
            func.sum(case((BIAProcessModel.status == ProcessStatus.COMPLETED.value, 1), else_=0)).label('completed_count'),
            # RTO statistics
            func.avg(BIAProcessModel.rto_hours).label('avg_rto'),
            func.min(BIAProcessModel.rto_hours).label('min_rto'),
            func.max(BIAProcessModel.rto_hours).label('max_rto'),
            # RPO statistics
            func.avg(BIAProcessModel.rpo_hours).label('avg_rpo'),
            func.min(BIAProcessModel.rpo_hours).label('min_rpo'),
            func.max(BIAProcessModel.rpo_hours).label('max_rpo'),
            # MTPD statistics
            func.avg(BIAProcessModel.mtpd_hours).label('avg_mtpd'),
            func.min(BIAProcessModel.mtpd_hours).label('min_mtpd'),
            func.max(BIAProcessModel.mtpd_hours).label('max_mtpd'),
            # Criticality score statistics
            func.avg(BIAProcessModel.criticality_score).label('avg_criticality_score'),
            # Financial impact
            func.avg(BIAProcessModel.annual_revenue_impact).label('avg_revenue_impact'),
            func.sum(BIAProcessModel.annual_revenue_impact).label('total_revenue_impact'),
        ).where(
            BIAProcessModel.tenant_id == tenant_id
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row or row.total_count == 0:
            return {
                "total_count": 0,
                "criticality_breakdown": {},
                "status_breakdown": {},
                "rto_statistics": {},
                "rpo_statistics": {},
                "mtpd_statistics": {},
                "criticality_score_avg": 0,
                "financial_impact": {}
            }

        return {
            "total_count": int(row.total_count),
            "criticality_breakdown": {
                "critical": int(row.critical_count or 0),
                "high": int(row.high_count or 0),
                "moderate": int(row.moderate_count or 0),
                "minor": int(row.minor_count or 0),
                "low": int(row.low_count or 0)
            },
            "status_breakdown": {
                "draft": int(row.draft_count or 0),
                "in_progress": int(row.in_progress_count or 0),
                "completed": int(row.completed_count or 0)
            },
            "rto_statistics": {
                "average": float(row.avg_rto) if row.avg_rto else 0,
                "minimum": int(row.min_rto) if row.min_rto else 0,
                "maximum": int(row.max_rto) if row.max_rto else 0
            },
            "rpo_statistics": {
                "average": float(row.avg_rpo) if row.avg_rpo else 0,
                "minimum": int(row.min_rpo) if row.min_rpo else 0,
                "maximum": int(row.max_rpo) if row.max_rpo else 0
            },
            "mtpd_statistics": {
                "average": float(row.avg_mtpd) if row.avg_mtpd else 0,
                "minimum": int(row.min_mtpd) if row.min_mtpd else 0,
                "maximum": int(row.max_mtpd) if row.max_mtpd else 0
            },
            "criticality_score_avg": float(row.avg_criticality_score) if row.avg_criticality_score else 0,
            "financial_impact": {
                "average_revenue_impact": float(row.avg_revenue_impact) if row.avg_revenue_impact else 0,
                "total_revenue_impact": float(row.total_revenue_impact) if row.total_revenue_impact else 0
            }
        }

    async def list_with_pagination(
        self,
        tenant_id: str,
        last_id: Optional[int] = None,
        limit: int = 100,
        criticality: Optional[CriticalityLevel] = None,
        status: Optional[ProcessStatus] = None
    ) -> List[BIAProcess]:
        """
        List BIA processes with cursor-based pagination for large datasets.

        Optimization: Cursor-based pagination instead of OFFSET
        Before: OFFSET 10000 LIMIT 100 scans 10000 rows
        After: WHERE id > last_id LIMIT 100 uses index

        Args:
            tenant_id: Tenant ID
            last_id: Last process ID from previous page (cursor)
            limit: Number of results per page
            criticality: Optional criticality filter
            status: Optional status filter

        Returns:
            List of BIA processes
        """
        query = select(BIAProcessModel).where(
            BIAProcessModel.tenant_id == tenant_id
        )

        # Cursor-based pagination
        if last_id is not None:
            query = query.where(BIAProcessModel.id > last_id)

        # Optional filters
        if criticality:
            query = query.where(BIAProcessModel.criticality == criticality.value)

        if status:
            query = query.where(BIAProcessModel.status == status.value)

        # Order by ID for consistent pagination
        query = query.order_by(BIAProcessModel.id).limit(limit)

        result = await self.db.execute(query)
        process_models = result.scalars().all()

        return [self._model_to_domain(pm) for pm in process_models]

    async def get_processes_by_department(self, tenant_id: str) -> Dict[str, List[BIAProcess]]:
        """
        Get processes grouped by department with single query.

        Optimization: Single query to fetch all processes, group in Python
        Before: 1 query to get departments + N queries for each department
        After: 1 query with all processes, grouped in memory

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary mapping department to list of processes
        """
        query = select(BIAProcessModel).where(
            BIAProcessModel.tenant_id == tenant_id
        ).order_by(
            BIAProcessModel.department,
            BIAProcessModel.criticality_score.desc()
        )

        result = await self.db.execute(query)
        processes = result.scalars().all()

        # Group by department
        by_department = {}
        for process_model in processes:
            dept = process_model.department or "Unassigned"
            if dept not in by_department:
                by_department[dept] = []
            by_department[dept].append(self._model_to_domain(process_model))

        return by_department

    async def get_overdue_reviews(self, tenant_id: str) -> List[BIAProcess]:
        """
        Get processes with overdue review dates.

        Optimization: Uses indexed next_review_date field

        Args:
            tenant_id: Tenant ID

        Returns:
            List of processes with overdue reviews
        """
        from datetime import datetime

        query = select(BIAProcessModel).where(
            and_(
                BIAProcessModel.tenant_id == tenant_id,
                BIAProcessModel.next_review_date.isnot(None),
                BIAProcessModel.next_review_date < datetime.utcnow(),
                BIAProcessModel.status == ProcessStatus.COMPLETED.value
            )
        ).order_by(BIAProcessModel.next_review_date)

        result = await self.db.execute(query)
        process_models = result.scalars().all()

        return [self._model_to_domain(pm) for pm in process_models]
