"""
 Unified Learning & Knowledge System

Единая самообучающаяся экосистема платформы, объединяющая:
- Knowledge Management (стандарты, кейсы)
- Learning Engine (AI самообучение, паттерны)
- Human Training (программы, упражнения)
- Cross-Learning (AI ↔ Люди)

Version: 2.0.0
"""

__version__ = "2.0.0"

# Knowledge Management
from .knowledge.loader import StandardsLoader, CaseCollector
from .knowledge.indexer import VectorIndexer
from .knowledge.updater import StandardsMonitor

# Learning Engine
from .learning.engines import (
    PatternDetector,
    MLPredictor,
    SelfLearningEngine,
    CompetencyTracker
)

# Integrations
from .integrations import WorkflowIntelligenceAdapter

__all__ = [
    # Knowledge
    "StandardsLoader",
    "CaseCollector",
    "VectorIndexer",
    "StandardsMonitor",

    # Learning
    "PatternDetector",
    "MLPredictor",
    "SelfLearningEngine",
    "CompetencyTracker",

    # Integrations
    "WorkflowIntelligenceAdapter",
]
