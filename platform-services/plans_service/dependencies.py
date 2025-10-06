"""
Plans Service Dependencies
Dependency injection for FastAPI
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from .database import get_db
from .repositories.plan_repository import PlanRepository
from .services.plan_service import PlanService


async def get_plan_repository(
    db: AsyncSession = Depends(get_db)
) -> PlanRepository:
    """Get plan repository instance"""
    return PlanRepository(db)


async def get_plan_service(
    repo: PlanRepository = Depends(get_plan_repository)
) -> PlanService:
    """Get plan service instance"""
    return PlanService(repo)
