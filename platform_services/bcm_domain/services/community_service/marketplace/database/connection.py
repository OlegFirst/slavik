"""
Database connection for Marketplace Service
Uses shared Supabase connection from community_service
"""

import sys
from pathlib import Path

# Add parent directory to path to import shared modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import (
    engine,
    AsyncSessionLocal,
    Base,
    get_db,
    get_db_with_context,
    init_db as shared_init_db,
    close_db as shared_close_db,
    check_db_health
)

# Re-export for compatibility
async def init_db():
    """Initialize database connection"""
    await shared_init_db()


async def close_db():
    """Close database connection"""
    await shared_close_db()


__all__ = [
    "engine",
    "AsyncSessionLocal",
    "Base",
    "get_db",
    "get_db_with_context",
    "init_db",
    "close_db",
    "check_db_health"
]
