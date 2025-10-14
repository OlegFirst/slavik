"""Task specification repository"""

import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm_models import TaskSpecificationORM
from models.pydantic_models import TaskSpecification
from storage.repositories.base_repository import BaseRepository
from storage.database import DatabaseManager

logger = logging.getLogger(__name__)


class SpecificationRepository(BaseRepository[TaskSpecificationORM, TaskSpecification]):
    """Repository for task specifications"""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(
            db_manager=db_manager,
            orm_model=TaskSpecificationORM,
            pydantic_model=TaskSpecification,
            cache_prefix="specification"
        )

    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: str,
        limit: int = 100
    ) -> List[TaskSpecificationORM]:
        """List specifications by user"""
        stmt = (
            select(TaskSpecificationORM)
            .where(TaskSpecificationORM.created_by == user_id)
            .order_by(TaskSpecificationORM.created_at.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())
