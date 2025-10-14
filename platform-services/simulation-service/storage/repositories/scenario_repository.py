"""Scenario repository"""

import logging
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm_models import ScenarioORM
from models.pydantic_models import Scenario, ScenarioCategory
from storage.repositories.base_repository import BaseRepository
from storage.database import DatabaseManager

logger = logging.getLogger(__name__)


class ScenarioRepository(BaseRepository[ScenarioORM, Scenario]):
    """Repository for scenario operations"""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(
            db_manager=db_manager,
            orm_model=ScenarioORM,
            pydantic_model=Scenario,
            cache_prefix="scenario"
        )

    async def search_by_tags(
        self,
        session: AsyncSession,
        tags: List[str],
        organization_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ScenarioORM]:
        """Search scenarios by tags"""
        conditions = [ScenarioORM.tags.overlap(tags)]

        if organization_id:
            conditions.append(ScenarioORM.organization_id == organization_id)

        stmt = (
            select(ScenarioORM)
            .where(and_(*conditions))
            .order_by(ScenarioORM.quality_score.desc().nullslast())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_category(
        self,
        session: AsyncSession,
        category: ScenarioCategory,
        min_quality: float = 0.0,
        limit: int = 100
    ) -> List[ScenarioORM]:
        """List scenarios by category"""
        stmt = (
            select(ScenarioORM)
            .where(
                and_(
                    ScenarioORM.category == category,
                    or_(
                        ScenarioORM.quality_score >= min_quality,
                        ScenarioORM.quality_score.is_(None)
                    )
                )
            )
            .order_by(ScenarioORM.quality_score.desc().nullslast())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def increment_usage(
        self,
        session: AsyncSession,
        scenario_id: str
    ) -> Optional[ScenarioORM]:
        """Increment scenario usage count"""
        scenario = await self.get_by_id(session, scenario_id)
        if scenario:
            return await self.update(
                session,
                scenario_id,
                {"usage_count": scenario.usage_count + 1}
            )
        return None
