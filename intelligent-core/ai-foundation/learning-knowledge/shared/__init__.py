"""
Shared utilities and connections for unified learning-knowledge system
"""

from .database import (
    get_database_manager,
    get_supabase_manager,
    get_cache_manager,
    get_db_session,
    get_qdrant_client
)

__all__ = [
    'get_database_manager',
    'get_supabase_manager',
    'get_cache_manager',
    'get_db_session',
    'get_qdrant_client'
]
