"""
Governance Service - Database Connection & Session Management
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from .models import Base

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://bcm_user:password@localhost:5432/bcm_platform")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    poolclass=NullPool,  # For development; use QueuePool in production
    future=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI endpoints

    Usage:
        @app.get("/api/governance/policies")
        async def list_policies(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database (create all tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    """Drop all tables (DANGER!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Multi-tenancy context
async def set_tenant_context(session: AsyncSession, tenant_id: str):
    """
    Set tenant context for Row Level Security

    Usage:
        await set_tenant_context(db, "organization_001")
    """
    await session.execute(f"SET app.tenant_id = '{tenant_id}'")
