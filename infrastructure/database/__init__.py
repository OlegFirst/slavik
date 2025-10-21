"""
Unified Database Access Point - Single Entry Point for All Services

This module provides centralized database access for the entire platform.
All services should use this instead of creating direct database connections.

Usage:
    from infrastructure.database import get_database, get_db_session

    # Async context
    db = await get_database()
    async with db.get_session() as session:
        result = await session.execute(query)

    # FastAPI dependency
    @app.get("/data")
    async def get_data(db: AsyncSession = Depends(get_db_session)):
        result = await db.execute(select(Model))
        return result.scalars().all()
"""

import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

# Import managers
from infrastructure.database.postgresql.managers.supabase_client import (
    SupabaseManager,
    supabase_manager
)
from infrastructure.database.postgresql.managers.db_manager import (
    DatabaseManager,
    SystemDBManager,
    PlatformDBManager,
    BusinessDBManager,
    RLSManager,
    system_db,
    platform_db,
    business_db
)

logger = logging.getLogger(__name__)

# =============================================================================
# DATABASE INSTANCES
# =============================================================================

# Primary database instance (Supabase with SQLAlchemy)
_primary_db: Optional[SupabaseManager] = None

# Legacy sync managers (for migrations, admin tasks)
_system_db: SystemDBManager = system_db
_platform_db: PlatformDBManager = platform_db
_business_db: BusinessDBManager = business_db


# =============================================================================
# INITIALIZATION
# =============================================================================

async def initialize_database():
    """
    Initialize all database connections
    Should be called on application startup
    """
    global _primary_db

    if _primary_db is None:
        _primary_db = supabase_manager
        await _primary_db.connect()
        logger.info(" Database connections initialized")

    # Initialize sync managers for admin tasks
    try:
        _system_db.connect(min_conn=1, max_conn=5)
        _platform_db.connect(min_conn=1, max_conn=5)
        _business_db.connect(min_conn=2, max_conn=10)
        logger.info(" Sync database managers initialized")
    except Exception as e:
        logger.warning(f"️  Sync managers initialization failed (non-critical): {e}")


async def shutdown_database():
    """
    Shutdown all database connections
    Should be called on application shutdown
    """
    global _primary_db

    if _primary_db:
        await _primary_db.disconnect()
        _primary_db = None
        logger.info(" Database connections closed")

    # Shutdown sync managers
    try:
        _system_db.disconnect()
        _platform_db.disconnect()
        _business_db.disconnect()
        logger.info(" Sync database managers closed")
    except Exception as e:
        logger.warning(f"️  Sync managers shutdown failed: {e}")


# =============================================================================
# DATABASE ACCESS
# =============================================================================

async def get_database() -> SupabaseManager:
    """
    Get primary database manager instance

    Returns:
        SupabaseManager: Initialized database manager

    Raises:
        RuntimeError: If database not initialized
    """
    global _primary_db

    if _primary_db is None:
        # Auto-initialize if not done
        logger.warning("Database not initialized, auto-initializing...")
        await initialize_database()

    return _primary_db


@asynccontextmanager
async def get_db_session():
    """
    Get async database session (context manager)

    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)

    Yields:
        AsyncSession: SQLAlchemy async session
    """
    db = await get_database()
    async with db.get_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# FastAPI dependency version
async def get_db_session_dependency():
    """
    FastAPI dependency for database session

    Usage:
        @app.get("/data")
        async def get_data(db: AsyncSession = Depends(get_db_session_dependency)):
            result = await db.execute(query)
            return result.scalars().all()
    """
    async with get_db_session() as session:
        yield session


# =============================================================================
# LEGACY SYNC ACCESS (for migrations, admin tasks)
# =============================================================================

def get_system_db() -> SystemDBManager:
    """Get System DB manager (sync)"""
    return _system_db


def get_platform_db() -> PlatformDBManager:
    """Get Platform DB manager (sync)"""
    return _platform_db


def get_business_db() -> BusinessDBManager:
    """Get Business DB manager (sync)"""
    return _business_db


# =============================================================================
# HEALTH CHECKS
# =============================================================================

async def health_check() -> Dict[str, Any]:
    """
    Check health of all database services

    Returns:
        Dict with health status of all database components
    """
    health = {
        "status": "unknown",
        "primary_db": {},
        "sync_managers": {}
    }

    try:
        # Check primary database
        db = await get_database()
        health["primary_db"] = await db.health_check()

        # Check sync managers
        try:
            health["sync_managers"] = {
                "system_db": _system_db.health_check(),
                "platform_db": _platform_db.health_check(),
                "business_db": _business_db.health_check(),
            }
        except Exception as e:
            health["sync_managers"]["error"] = str(e)

        # Overall status
        postgres_ok = health["primary_db"].get("postgres", False)
        if postgres_ok:
            health["status"] = "healthy"
        else:
            health["status"] = "degraded"

    except Exception as e:
        health["status"] = "unhealthy"
        health["error"] = str(e)
        logger.error(f"Database health check failed: {e}")

    return health


# =============================================================================
# UTILITIES
# =============================================================================

async def set_rls_context(session, user_id: str, tenant_id: str):
    """
    Set Row Level Security context for current session

    Args:
        session: SQLAlchemy async session
        user_id: Current user ID
        tenant_id: Current tenant/organization ID
    """
    await session.execute(f"SET LOCAL app.current_user_id = '{user_id}'")
    await session.execute(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")


async def clear_rls_context(session):
    """Clear Row Level Security context"""
    await session.execute("RESET app.current_user_id")
    await session.execute("RESET app.current_tenant_id")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Initialization
    'initialize_database',
    'shutdown_database',

    # Primary access
    'get_database',
    'get_db_session',
    'get_db_session_dependency',

    # Legacy sync access
    'get_system_db',
    'get_platform_db',
    'get_business_db',

    # Health
    'health_check',

    # Utilities
    'set_rls_context',
    'clear_rls_context',

    # Managers (for advanced usage)
    'SupabaseManager',
    'DatabaseManager',
    'RLSManager',
]
