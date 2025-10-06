"""
Qdrant Vector Database Module

Provides high-level interface for vector operations.
"""

from .client import QdrantVectorDB
from .config import qdrant_config, COLLECTIONS_CONFIG

__all__ = [
    "QdrantVectorDB",
    "qdrant_config",
    "COLLECTIONS_CONFIG"
]
