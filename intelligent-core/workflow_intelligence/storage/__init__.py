"""
Storage adapters for Workflow Intelligence

RLS (Row Level Security) ENABLED:
- All storage operations are automatically isolated by tenant_id
- Multi-tenancy enforced at database level
- See rls_context.py for details
"""

from .postgres_adapter import PostgresStorageAdapter
from .base import StorageAdapter
from .rls_context import (
    RLSContext,
    rls_context,
    RLSPoolContext,
    rls_pool_context,
    verify_rls_enabled,
    test_rls_isolation
)

__all__ = [
    "StorageAdapter",
    "PostgresStorageAdapter",
    "RLSContext",
    "rls_context",
    "RLSPoolContext",
    "rls_pool_context",
    "verify_rls_enabled",
    "test_rls_isolation"
]
