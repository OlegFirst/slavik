"""
Storage Layer для Scenario Intelligence

Поддерживает:
- In-memory Registry (быстрый MVP)
- PostgreSQL Storage (постоянное хранилище)
- Qdrant Storage (semantic search)
"""

from .registry import ScenarioRegistry, global_registry

# PostgreSQL Storage (опциональный import)
PostgresScenarioStorage = None
try:
    from .postgres_storage import PostgresScenarioStorage
except ImportError as e:
    pass  # PostgreSQL storage не доступен

# Qdrant Storage (опциональный import)
QdrantScenarioStorage = None
try:
    from .qdrant_storage import QdrantScenarioStorage
except (ImportError, TypeError) as e:
    pass  # Qdrant storage не доступен

__all__ = [
    'ScenarioRegistry',
    'global_registry',
    'PostgresScenarioStorage',
    'QdrantScenarioStorage',
]
