"""
Planning Service Dependencies
Dependency injection for FastAPI
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from .database import get_db
from .repositories.repository import StrategyRepository
from .services.business_logic import StrategyService


async def get_strategy_repository(
    db: AsyncSession = Depends(get_db)
) -> StrategyRepository:
    """Get strategy repository instance"""
    return StrategyRepository(db)


async def get_strategy_service(
    repo: StrategyRepository = Depends(get_strategy_repository)
) -> StrategyService:
    """Get strategy service instance"""
    return StrategyService(repo)
