"""
Database Connection Manager

Manages PostgreSQL connections for Unified Workflow Engine
"""

import os
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database connection manager for Workflow Engine

    Uses SQLAlchemy async for PostgreSQL connection
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager

        Args:
            database_url: PostgreSQL connection string
                         If None, uses DATABASE_URL env var
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL not provided")

        # Convert postgresql:// to postgresql+asyncpg://
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1
            )

        self.engine = None
        self.session_factory = None

    async def connect(self):
        """Initialize database engine and session factory"""

        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                poolclass=NullPool,  # Supabase manages connection pooling
                echo=False,  # Set to True for SQL debugging
                future=True
            )

            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info(" Database connected successfully")

        except Exception as e:
            logger.error(f" Failed to connect to database: {e}")
            raise

    async def disconnect(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database disconnected")

    def get_session(self) -> AsyncSession:
        """
        Get database session

        Returns:
            AsyncSession: SQLAlchemy async session

        Usage:
            async with db.get_session() as session:
                result = await session.execute(query)
        """
        if not self.session_factory:
            raise RuntimeError("Database not connected. Call connect() first")

        return self.session_factory()

    async def set_tenant(self, session: AsyncSession, tenant_id: str):
        """
        Set tenant context for RLS

        Args:
            session: Database session
            tenant_id: Tenant identifier

        This sets the PostgreSQL session variable that RLS policies use
        """
        await session.execute(
            text("SET app.current_tenant = :tenant_id"),
            {"tenant_id": tenant_id}
        )


# Global instance (singleton pattern)
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager

    if _db_manager is None:
        _db_manager = DatabaseManager()

    return _db_manager


async def init_db():
    """Initialize global database manager"""
    db = get_db_manager()
    await db.connect()
    return db
