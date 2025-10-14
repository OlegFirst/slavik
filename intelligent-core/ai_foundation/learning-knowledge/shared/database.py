"""
Shared Database Connections

Использует существующие managers из /infrastructure/database/
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

# Import existing infrastructure managers
import sys
from pathlib import Path

# Add infrastructure to path
infra_path = Path(__file__).parents[4] / "infrastructure" / "database" / "postgresql"
if str(infra_path) not in sys.path:
    sys.path.insert(0, str(infra_path))

from managers.db_manager import DatabaseManager
from managers.supabase_client import SupabaseManager
from managers.cache_manager import CacheManager

# Singleton instances
_db_manager: DatabaseManager = None
_supabase_manager: SupabaseManager = None
_cache_manager: CacheManager = None


def get_database_manager() -> DatabaseManager:
    """Get DatabaseManager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(name="learning-knowledge")
    return _db_manager


def get_supabase_manager() -> SupabaseManager:
    """Get Supabase manager singleton"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager


def get_cache_manager() -> CacheManager:
    """Get CacheManager singleton"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session (for FastAPI Depends)

    Usage:
        @app.get("/...")
        async def endpoint(session: AsyncSession = Depends(get_db_session)):
            result = await session.execute(...)
    """
    db = get_database_manager()
    async with db.get_session() as session:
        yield session


# For Qdrant vector DB
def get_qdrant_client():
    """Get Qdrant client"""
    from pathlib import Path
    import sys

    vector_path = Path(__file__).parents[4] / "infrastructure" / "database" / "vector-db"
    if str(vector_path) not in sys.path:
        sys.path.insert(0, str(vector_path))

    from qdrant.client import QdrantVectorDB
    return QdrantVectorDB()
