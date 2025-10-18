"""Simulation result repository"""

import logging
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.orm_models import SimulationResultORM, ExerciseMetricsORM
from models.pydantic_models import SimulationResult
from storage.repositories.base_repository import BaseRepository
from storage.database import DatabaseManager

logger = logging.getLogger(__name__)


class ResultRepository(BaseRepository[SimulationResultORM, SimulationResult]):
    """Repository for simulation results"""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(
            db_manager=db_manager,
            orm_model=SimulationResultORM,
            pydantic_model=SimulationResult,
            cache_prefix="result"
        )

    async def get_with_metrics(
        self,
        session: AsyncSession,
        result_id: str
    ) -> Optional[SimulationResultORM]:
        """Get result with metrics"""
        stmt = (
            select(SimulationResultORM)
            .where(SimulationResultORM.id == result_id)
            .options(selectinload(SimulationResultORM.metrics))
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_simulation(
        self,
        session: AsyncSession,
        simulation_id: str
    ) -> Optional[SimulationResultORM]:
        """Get result by simulation ID"""
        stmt = (
            select(SimulationResultORM)
            .where(SimulationResultORM.simulation_id == simulation_id)
            .options(selectinload(SimulationResultORM.metrics))
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_high_quality(
        self,
        session: AsyncSession,
        min_quality: float = 8.0,
        limit: int = 100
    ) -> List[SimulationResultORM]:
        """List high-quality results"""
        stmt = (
            select(SimulationResultORM)
            .where(SimulationResultORM.quality_score >= min_quality)
            .order_by(SimulationResultORM.quality_score.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_contribution_worthy(
        self,
        session: AsyncSession,
        limit: int = 100
    ) -> List[SimulationResultORM]:
        """List results worthy of community contribution"""
        stmt = (
            select(SimulationResultORM)
            .where(SimulationResultORM.contribution_worthy == True)
            .order_by(SimulationResultORM.quality_score.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())
