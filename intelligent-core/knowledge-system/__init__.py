"""
Knowledge System - Centralized Knowledge Management

Unified system for managing domain knowledge:
- Standards (ISO, BCI, WHO, NIST)
- Cases (Workflow, Community, Simulation)
- External sources (Auto-updating)

Features:
- Domain-based organization
- Vector search (Qdrant)
- Knowledge Graph (Neo4j)
- Auto-update workflows
- Multi-level caching
"""

__version__ = "1.0.0"

from .loader.standards_loader import StandardsLoader
from .loader.case_loader import CaseCollector
from .api.query import KnowledgeAPI, KnowledgeQuery

__all__ = [
    "StandardsLoader",
    "CaseCollector",
    "KnowledgeAPI",
    "KnowledgeQuery",
]
