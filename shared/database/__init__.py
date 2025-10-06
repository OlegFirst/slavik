"""Database module for connection pooling and session management."""

from .connection import DatabaseManager, init_database, init_db, get_db, close_db, get_db_manager
from .base import Base
from .query_profiler import (
    QueryProfiler,
    enable_profiling,
    disable_profiling,
    get_global_profiler,
    profile_queries
)
from .pagination import (
    CursorPage,
    KeysetPage,
    CursorEncoder,
    paginate_cursor,
    paginate_keyset,
    paginate_offset
)

__all__ = [
    "DatabaseManager",
    "init_database",
    "init_db",  # alias for init_database
    "get_db",
    "close_db",
    "get_db_manager",
    "Base",
    # Query profiling
    "QueryProfiler",
    "enable_profiling",
    "disable_profiling",
    "get_global_profiler",
    "profile_queries",
    # Pagination
    "CursorPage",
    "KeysetPage",
    "CursorEncoder",
    "paginate_cursor",
    "paginate_keyset",
    "paginate_offset"
]
