"""
Database Connection Manager
============================

Async database connection manager with connection pooling.

Features:
- Connection pooling with configurable size
- Automatic connection health checks (pool_pre_ping)
- Connection recycling to prevent stale connections
- Session factory with proper error handling
- FastAPI dependency injection support
"""

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import Pool


class DatabaseManager:
    """
    Async database connection manager with pooling.

    Provides centralized database connection management with:
    - Connection pooling for optimal performance
    - Automatic connection validation
    - Proper session lifecycle management
    - Transaction rollback on errors

    Example:
        ```python
        # Initialize at startup
        db_manager = init_database(
            "postgresql+asyncpg://user:pass@localhost/bcm",
            pool_size=20
        )

        # Use in FastAPI endpoint
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
        ```
    """

    def __init__(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        """
        Initialize database manager.

        Args:
            database_url: Database connection URL (e.g., postgresql+asyncpg://...)
            pool_size: Number of connections to maintain in the pool (default: 20)
            max_overflow: Max additional connections when pool is full (default: 10)
            pool_recycle: Recycle connections after N seconds (default: 3600)
            echo: Log all SQL statements (default: False)
        """
        self.database_url = database_url

        # Create async engine with connection pooling
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Validate connections before using
            pool_recycle=pool_recycle,  # Recycle connections to prevent stale connections
            future=True  # Use SQLAlchemy 2.0 style
        )

        # Create session factory
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autocommit=False,  # Explicit transaction control
            autoflush=False  # Manual flush for better control
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session (context manager).

        Yields:
            AsyncSession: Database session

        Example:
            ```python
            async for session in db_manager.get_session():
                result = await session.execute(select(User))
                users = result.scalars().all()
            ```
        """
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def dispose(self) -> None:
        """
        Dispose database engine and close all connections.

        Call this during application shutdown.

        Example:
            ```python
            @app.on_event("shutdown")
            async def shutdown():
                await db_manager.dispose()
            ```
        """
        await self.engine.dispose()

    def get_pool_status(self) -> dict:
        """
        Get connection pool status for monitoring.

        Returns:
            dict: Pool statistics including size, checked_out, overflow
        """
        pool: Pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "checked_in": pool.checkedin()
        }


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def init_database(
    database_url: str,
    pool_size: int = 20,
    max_overflow: int = 10,
    pool_recycle: int = 3600,
    echo: bool = False
) -> DatabaseManager:
    """
    Initialize global database manager.

    Call this once during application startup.

    Args:
        database_url: Database connection URL
        pool_size: Number of connections in pool (default: 20)
        max_overflow: Max overflow connections (default: 10)
        pool_recycle: Connection recycle time in seconds (default: 3600)
        echo: Log SQL statements (default: False)

    Returns:
        DatabaseManager: Initialized database manager

    Example:
        ```python
        @app.on_event("startup")
        async def startup():
            init_database(settings.DATABASE_URL, pool_size=20)
        ```
    """
    global _db_manager
    _db_manager = DatabaseManager(
        database_url=database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
        echo=echo
    )
    return _db_manager


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session.

    Provides a database session that is automatically closed after the request.
    Transactions are automatically rolled back on errors.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        @router.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    if _db_manager is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() during startup."
        )

    async for session in _db_manager.get_session():
        yield session


def get_db_manager() -> DatabaseManager:
    """
    Get global database manager instance.

    Returns:
        DatabaseManager: Global database manager

    Raises:
        RuntimeError: If database not initialized
    """
    if _db_manager is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() during startup."
        )
    return _db_manager


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
    global _db_manager
    if _db_manager:
        await _db_manager.dispose()
        _db_manager = None


# Alias for backwards compatibility
init_db = init_database
