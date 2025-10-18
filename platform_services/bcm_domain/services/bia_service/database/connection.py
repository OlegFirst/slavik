"""
BIA Database Connection

Wrapper around shared database connection manager.
Provides BIA-specific database initialization and session management.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.connection import init_database, get_db as shared_get_db, get_db_manager


async def init_db(database_url: str, pool_size: int = 20, echo: bool = False) -> None:
    """
    Initialize BIA database connection.

    Args:
        database_url: Database connection URL (e.g., postgresql+asyncpg://...)
        pool_size: Connection pool size (default: 20)
        echo: Log SQL statements (default: False)

    Example:
        ```python
        await init_db(
            database_url="postgresql+asyncpg://user:pass@localhost/bcm",
            pool_size=20,
            echo=True
        )
        ```
    """
    init_database(database_url=database_url, pool_size=pool_size, echo=echo)


async def close_db() -> None:
    """
    Close database connections and dispose engine.

    Call this during application shutdown.

    Example:
        ```python
        @app.on_event("shutdown")
        async def shutdown():
            await close_db()
        ```
    """
    db_manager = get_db_manager()
    await db_manager.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for BIA service.

    FastAPI dependency injection compatible.
    Automatically handles session lifecycle and rollback on errors.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        @router.get("/processes")
        async def list_processes(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(BIAProcessModel))
            return result.scalars().all()
        ```
    """
    async for session in shared_get_db():
        yield session
