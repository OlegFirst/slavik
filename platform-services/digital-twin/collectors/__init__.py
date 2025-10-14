"""
Data Collectors

Plugin-based data collection system
"""

from .base import (
    DataCollector,
    RESTCollector,
    DatabaseCollector,
    FileCollector,
    CollectionResult,
    CollectionStatus,
    EntityType,
)

from .manager import (
    CollectorManager,
    CollectorStatus,
    CollectorInfo,
    get_collector_manager,
    register_builtin_collectors,
)

__all__ = [
    # Base classes
    "DataCollector",
    "RESTCollector",
    "DatabaseCollector",
    "FileCollector",
    "CollectionResult",
    "CollectionStatus",
    "EntityType",
    # Manager
    "CollectorManager",
    "CollectorStatus",
    "CollectorInfo",
    "get_collector_manager",
    "register_builtin_collectors",
]
