"""
API Dependencies

FastAPI dependency injection providers for:
- Database sessions
- Service instances
- Authentication
- Multi-tenancy
"""

import logging
import os
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logger = logging.getLogger(__name__)

# ============================================
# DATABASE SESSION FACTORY
# ============================================

# Global engine and session factory
_engine = None
_session_factory = None


def get_database_url() -> str:
    """
    Get database URL from environment variables

    Required environment variables:
    - DATABASE_URL: Full PostgreSQL connection URL
    OR
    - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    """
    # Try full URL first
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Ensure it uses asyncpg driver
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return database_url

    # Build from components
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "digital_twin")
    username = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")

    return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"


async def initialize_database():
    """Initialize database engine and session factory"""
    global _engine, _session_factory

    if _engine is not None:
        return

    try:
        database_url = get_database_url()

        logger.info(f"Initializing database connection...")

        _engine = create_async_engine(
            database_url,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_pre_ping=True,  # Verify connections before using
        )

        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


async def close_database():
    """Close database connections"""
    global _engine

    if _engine:
        await _engine.dispose()
        logger.info("Database connections closed")


# ============================================
# DATABASE SESSION DEPENDENCY
# ============================================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection

    Usage in FastAPI endpoints:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    if _session_factory is None:
        await initialize_database()

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            await session.close()


# ============================================
# TENANT DEPENDENCY
# ============================================

async def get_tenant_id(
    x_tenant_id: Optional[str] = Header(None)
) -> str:
    """
    Get tenant ID from request header

    Usage:
        @router.get("/endpoint")
        async def endpoint(tenant_id: str = Depends(get_tenant_id)):
            ...
    """
    if not x_tenant_id:
        # For development, use default tenant
        default_tenant = os.getenv("DEFAULT_TENANT_ID", "default-tenant")
        logger.warning(f"No tenant ID provided, using default: {default_tenant}")
        return default_tenant

    return x_tenant_id


# ============================================
# SERVICE FACTORY DEPENDENCIES
# ============================================

from core.community.knowledge_exchange_db import KnowledgeExchangeServiceDB
from core.community.people_matching_db import PeopleMatchingServiceDB
from core.learning.passive_learning_engine_db import PassiveLearningEngineDB
from core.learning.context_builder_db import ContextBuilderDB


async def get_knowledge_exchange_service(
    db: AsyncSession = Depends(get_db_session),
    tenant_id: str = Depends(get_tenant_id)
) -> KnowledgeExchangeServiceDB:
    """Get Knowledge Exchange Service instance"""
    return KnowledgeExchangeServiceDB(db_session=db, tenant_id=tenant_id)


async def get_people_matching_service(
    db: AsyncSession = Depends(get_db_session),
    tenant_id: str = Depends(get_tenant_id)
) -> PeopleMatchingServiceDB:
    """Get People Matching Service instance"""
    return PeopleMatchingServiceDB(db_session=db, tenant_id=tenant_id)


async def get_passive_learning_engine(
    db: AsyncSession = Depends(get_db_session),
    tenant_id: str = Depends(get_tenant_id)
) -> PassiveLearningEngineDB:
    """Get Passive Learning Engine instance"""
    return PassiveLearningEngineDB(db_session=db, tenant_id=tenant_id)


async def get_context_builder(
    db: AsyncSession = Depends(get_db_session),
    tenant_id: str = Depends(get_tenant_id)
) -> ContextBuilderDB:
    """Get Context Builder instance"""
    learning_engine = await get_passive_learning_engine(db, tenant_id)
    return ContextBuilderDB(
        db_session=db,
        tenant_id=tenant_id,
        learning_engine=learning_engine
    )


# ============================================
# LEGACY SERVICE DEPENDENCIES (For Twin Matching)
# ============================================

from core.community.twin_matching_engine import TwinMatchingEngine

_twin_matching = TwinMatchingEngine()


def get_twin_matching() -> TwinMatchingEngine:
    """Get twin matching engine (in-memory, no DB yet)"""
    return _twin_matching
