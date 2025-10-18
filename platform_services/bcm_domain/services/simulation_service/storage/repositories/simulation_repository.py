"""
Simulation repository with specialized queries

Provides simulation-specific database operations.
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.orm_models import SimulationORM, SimulationEventORM, SimulationResultORM
from models.pydantic_models import Simulation, SimulationStatus, EngineType
from storage.repositories.base_repository import BaseRepository
from storage.database import DatabaseManager

logger = logging.getLogger(__name__)


class SimulationRepository(BaseRepository[SimulationORM, Simulation]):
    """Repository for simulation operations"""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(
            db_manager=db_manager,
            orm_model=SimulationORM,
            pydantic_model=Simulation,
            cache_prefix="simulation"
        )

    async def get_with_relations(
        self,
        session: AsyncSession,
        simulation_id: str
    ) -> Optional[SimulationORM]:
        """
        Get simulation with all related entities

        Args:
            session: Database session
            simulation_id: Simulation ID

        Returns:
            Simulation with specification, scenario, events, result
        """
        stmt = (
            select(SimulationORM)
            .where(SimulationORM.id == simulation_id)
            .options(
                selectinload(SimulationORM.specification),
                selectinload(SimulationORM.scenario),
                selectinload(SimulationORM.events),
                selectinload(SimulationORM.result)
            )
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        session: AsyncSession,
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[SimulationORM]:
        """
        List simulations by organization

        Args:
            session: Database session
            organization_id: Organization ID
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of simulations
        """
        stmt = (
            select(SimulationORM)
            .where(SimulationORM.organization_id == organization_id)
            .order_by(SimulationORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_status(
        self,
        session: AsyncSession,
        status: SimulationStatus,
        organization_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SimulationORM]:
        """
        List simulations by status

        Args:
            session: Database session
            status: Simulation status
            organization_id: Optional organization filter
            limit: Maximum results

        Returns:
            List of simulations
        """
        conditions = [SimulationORM.status == status]

        if organization_id:
            conditions.append(SimulationORM.organization_id == organization_id)

        stmt = (
            select(SimulationORM)
            .where(and_(*conditions))
            .order_by(SimulationORM.created_at.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_active(
        self,
        session: AsyncSession,
        organization_id: Optional[str] = None
    ) -> List[SimulationORM]:
        """
        List active simulations (running or initializing)

        Args:
            session: Database session
            organization_id: Optional organization filter

        Returns:
            List of active simulations
        """
        conditions = [
            or_(
                SimulationORM.status == SimulationStatus.RUNNING,
                SimulationORM.status == SimulationStatus.INITIALIZING
            )
        ]

        if organization_id:
            conditions.append(SimulationORM.organization_id == organization_id)

        stmt = (
            select(SimulationORM)
            .where(and_(*conditions))
            .order_by(SimulationORM.started_at.desc())
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_engine(
        self,
        session: AsyncSession,
        engine: EngineType,
        organization_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SimulationORM]:
        """
        List simulations by engine type

        Args:
            session: Database session
            engine: Engine type
            organization_id: Optional organization filter
            limit: Maximum results

        Returns:
            List of simulations
        """
        conditions = [SimulationORM.engine == engine]

        if organization_id:
            conditions.append(SimulationORM.organization_id == organization_id)

        stmt = (
            select(SimulationORM)
            .where(and_(*conditions))
            .order_by(SimulationORM.created_at.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent(
        self,
        session: AsyncSession,
        organization_id: str,
        days: int = 7,
        limit: int = 100
    ) -> List[SimulationORM]:
        """
        List recent simulations

        Args:
            session: Database session
            organization_id: Organization ID
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of recent simulations
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        stmt = (
            select(SimulationORM)
            .where(
                and_(
                    SimulationORM.organization_id == organization_id,
                    SimulationORM.created_at >= cutoff_date
                )
            )
            .order_by(SimulationORM.created_at.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        session: AsyncSession,
        simulation_id: str,
        status: SimulationStatus,
        error_message: Optional[str] = None
    ) -> Optional[SimulationORM]:
        """
        Update simulation status

        Args:
            session: Database session
            simulation_id: Simulation ID
            status: New status
            error_message: Optional error message

        Returns:
            Updated simulation
        """
        updates = {"status": status}

        if status == SimulationStatus.RUNNING and not updates.get("started_at"):
            updates["started_at"] = datetime.utcnow()

        if status in [SimulationStatus.COMPLETED, SimulationStatus.FAILED, SimulationStatus.CANCELLED]:
            updates["completed_at"] = datetime.utcnow()

        if error_message:
            updates["error_message"] = error_message

        return await self.update(session, simulation_id, updates)

    async def update_progress(
        self,
        session: AsyncSession,
        simulation_id: str,
        progress: float,
        phase: Optional[str] = None
    ) -> Optional[SimulationORM]:
        """
        Update simulation progress

        Args:
            session: Database session
            simulation_id: Simulation ID
            progress: Progress percentage (0-100)
            phase: Optional current phase

        Returns:
            Updated simulation
        """
        updates = {"progress_percentage": progress}

        if phase:
            updates["current_phase"] = phase

        return await self.update(session, simulation_id, updates)

    async def count_by_status(
        self,
        session: AsyncSession,
        organization_id: str
    ) -> dict:
        """
        Count simulations by status

        Args:
            session: Database session
            organization_id: Organization ID

        Returns:
            Dictionary of status counts
        """
        from sqlalchemy import func

        stmt = (
            select(
                SimulationORM.status,
                func.count(SimulationORM.id)
            )
            .where(SimulationORM.organization_id == organization_id)
            .group_by(SimulationORM.status)
        )

        result = await session.execute(stmt)
        counts = {status.value: 0 for status in SimulationStatus}

        for status, count in result:
            counts[status.value] = count

        return counts

    async def get_statistics(
        self,
        session: AsyncSession,
        organization_id: str,
        days: int = 30
    ) -> dict:
        """
        Get simulation statistics

        Args:
            session: Database session
            organization_id: Organization ID
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        from sqlalchemy import func

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Total simulations
        total_stmt = (
            select(func.count(SimulationORM.id))
            .where(
                and_(
                    SimulationORM.organization_id == organization_id,
                    SimulationORM.created_at >= cutoff_date
                )
            )
        )
        total_result = await session.execute(total_stmt)
        total = total_result.scalar() or 0

        # Completed simulations
        completed_stmt = (
            select(func.count(SimulationORM.id))
            .where(
                and_(
                    SimulationORM.organization_id == organization_id,
                    SimulationORM.status == SimulationStatus.COMPLETED,
                    SimulationORM.created_at >= cutoff_date
                )
            )
        )
        completed_result = await session.execute(completed_stmt)
        completed = completed_result.scalar() or 0

        # Failed simulations
        failed_stmt = (
            select(func.count(SimulationORM.id))
            .where(
                and_(
                    SimulationORM.organization_id == organization_id,
                    SimulationORM.status == SimulationStatus.FAILED,
                    SimulationORM.created_at >= cutoff_date
                )
            )
        )
        failed_result = await session.execute(failed_stmt)
        failed = failed_result.scalar() or 0

        # Engine usage
        engine_stmt = (
            select(
                SimulationORM.engine,
                func.count(SimulationORM.id)
            )
            .where(
                and_(
                    SimulationORM.organization_id == organization_id,
                    SimulationORM.created_at >= cutoff_date
                )
            )
            .group_by(SimulationORM.engine)
        )
        engine_result = await session.execute(engine_stmt)
        engine_usage = {engine.value: count for engine, count in engine_result}

        return {
            "period_days": days,
            "total_simulations": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "engine_usage": engine_usage
        }
