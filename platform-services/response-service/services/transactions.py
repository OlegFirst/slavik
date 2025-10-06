"""
Transaction Management for Response Module

Provides database transaction context manager for atomic operations
"""

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def transaction(db: AsyncSession):
    """
    Transaction context manager for atomic database operations

    Usage:
        async with transaction(db):
            # Perform multiple database operations
            await db.execute(...)
            await db.execute(...)
            # Automatically commits on success, rolls back on exception

    Args:
        db: SQLAlchemy async session

    Yields:
        AsyncSession: The database session

    Raises:
        Exception: Re-raises any exception after rollback
    """
    try:
        yield db
        await db.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        await db.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise
