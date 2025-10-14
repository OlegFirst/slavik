"""
Compliance Database Connection

Wraps shared database manager for compliance-specific usage.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database.connection import init_database, get_db as shared_get_db, get_db_manager


async def init_db(database_url: str, pool_size: int = 20, echo: bool = False) -> None:
    """
    Initialize compliance database connection.

    Args:
        database_url: Database connection URL
        pool_size: Connection pool size
        echo: Echo SQL statements
    """
    init_database(
        database_url=database_url,
        pool_size=pool_size,
        echo=echo
    )


async def close_db() -> None:
    """Close database connections"""
    db_manager = get_db_manager()
    await db_manager.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for compliance service.

    Yields:
        AsyncSession: Database session

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async for session in shared_get_db():
        yield session
