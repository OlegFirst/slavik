"""
Database connection and session management

Provides async PostgreSQL connection pooling and Redis caching.
"""

import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker
)
from sqlalchemy import text
import redis.asyncio as aioredis

from config.settings import Settings, get_settings
from models.orm_models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages PostgreSQL and Redis connections

    Provides:
    - Async PostgreSQL connection pooling
    - Async Redis caching
    - Health checks
    - Database initialization
    """

    def __init__(self, settings: Settings):
        """
        Initialize database manager

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._engine: Optional[AsyncEngine] = None
        self._async_session_factory: Optional[async_sessionmaker] = None
        self._redis_client: Optional[aioredis.Redis] = None

    @property
    def engine(self) -> AsyncEngine:
        """Get SQLAlchemy async engine"""
        if self._engine is None:
            self._engine = create_async_engine(
                self.settings.database_url,
                pool_size=self.settings.database_pool_size,
                max_overflow=self.settings.database_max_overflow,
                echo=self.settings.debug,
                # Connection pool settings
                pool_pre_ping=True,  # Test connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
            )
            logger.info("Database engine created")
        return self._engine

    @property
    def async_session_factory(self) -> async_sessionmaker:
        """Get async session factory"""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
            logger.info("Async session factory created")
        return self._async_session_factory

    @property
    def redis(self) -> aioredis.Redis:
        """Get async Redis client"""
        if self._redis_client is None:
            self._redis_client = aioredis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis client created")
        return self._redis_client

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session context manager

        Usage:
            async with db_manager.get_session() as session:
                result = await session.execute(query)

        Yields:
            AsyncSession: Database session
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()

    async def init_db(self) -> None:
        """
        Initialize database tables

        Creates all tables defined in Base.metadata
        """
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def drop_db(self) -> None:
        """
        Drop all database tables

        WARNING: This will delete all data!
        Only use in testing or development.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.warning("Database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database: {e}")
            raise

    async def health_check(self) -> dict:
        """
        Check database and Redis health

        Returns:
            dict: Health status for PostgreSQL and Redis
        """
        health = {
            "postgres": False,
            "redis": False,
            "details": {}
        }

        # Check PostgreSQL
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    health["postgres"] = True
                    health["details"]["postgres"] = "Connected"
        except Exception as e:
            health["details"]["postgres"] = f"Error: {str(e)}"
            logger.error(f"PostgreSQL health check failed: {e}")

        # Check Redis
        try:
            await self.redis.ping()
            health["redis"] = True
            health["details"]["redis"] = "Connected"
        except Exception as e:
            health["details"]["redis"] = f"Error: {str(e)}"
            logger.error(f"Redis health check failed: {e}")

        return health

    async def close(self) -> None:
        """
        Close all database connections

        Should be called on application shutdown
        """
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine disposed")

        if self._redis_client:
            await self._redis_client.close()
            logger.info("Redis client closed")

    # Cache operations
    async def cache_get(self, key: str) -> Optional[str]:
        """
        Get value from Redis cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def cache_set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default from settings)

        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.settings.redis_cache_ttl
            await self.redis.setex(key, ttl, value)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def cache_delete(self, key: str) -> bool:
        """
        Delete value from Redis cache

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.redis.delete(key)
            logger.debug(f"Cache delete: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def cache_clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Redis key pattern (e.g., "simulation:*")

        Returns:
            Number of keys deleted
        """
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Cache cleared: {deleted} keys matching {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    Get global database manager instance

    Returns:
        DatabaseManager: Global instance
    """
    global _db_manager
    if _db_manager is None:
        settings = get_settings()
        _db_manager = DatabaseManager(settings)
    return _db_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session

    Usage:
        @app.get("/")
        async def route(session: AsyncSession = Depends(get_db_session)):
            ...

    Yields:
        AsyncSession: Database session
    """
    db_manager = get_db_manager()
    async with db_manager.get_session() as session:
        yield session


# Lifespan management for FastAPI
@asynccontextmanager
async def lifespan_manager(app):
    """
    FastAPI lifespan context manager

    Initializes database on startup, closes on shutdown

    Usage:
        app = FastAPI(lifespan=lifespan_manager)
    """
    # Startup
    db_manager = get_db_manager()
    logger.info("Initializing database...")

    try:
        # Initialize database tables
        await db_manager.init_db()

        # Check health
        health = await db_manager.health_check()
        if not health["postgres"]:
            logger.error("PostgreSQL not healthy!")
            raise Exception("PostgreSQL connection failed")

        if not health["redis"]:
            logger.warning("Redis not healthy, continuing without cache")

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Closing database connections...")
    await db_manager.close()
    logger.info("Database connections closed")
