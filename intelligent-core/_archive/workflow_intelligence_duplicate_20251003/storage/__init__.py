"""
Storage adapters for Workflow Intelligence
"""

from .postgres_adapter import PostgresStorageAdapter
from .base import StorageAdapter

__all__ = [
    "StorageAdapter",
    "PostgresStorageAdapter",
]
