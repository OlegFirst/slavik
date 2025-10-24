"""
AI Foundation - Core AI Infrastructure
=======================================

FEDERATED ARCHITECTURE - Version 2.0
-------------------------------------

ai_foundation defines PROTOCOLS and COORDINATES, not monopolizes.

Architecture:
- Protocols: Interface definitions for ML/RAG/Learning subsystems
- Coordinator: Central hub for subsystem coordination
- Reference Implementations: Base subsystems wrapping existing code
- Legacy API: Backward-compatible exports (deprecated)

Philosophy:
Like a nervous system - nerves (subsystems) are EVERYWHERE,
brain (coordinator) COORDINATES but doesn't control.

Each module (workflow_intelligence, expertise_center, orchestration)
implements protocol interfaces with domain-specific logic.

Usage:
------
New (Federated):
    from ai_foundation.coordinator import get_global_coordinator
    from ai_foundation.protocols import IMLSubsystem

    coordinator = get_global_coordinator()
    result = coordinator.coordinate_ml_prediction(features)

Legacy (Deprecated):
    from ai_foundation.ml import WorkflowPredictor  # Still works
"""

__version__ = "2.0.0"  # Federated architecture

# RAG Module
from .rag.pipeline import RAGPipeline, KnowledgeSourceManager
from .rag.embeddings import EmbeddingGenerator
from .rag.retrieval import HybridRetriever
from .rag.reranking import Reranker
from .rag.qdrant_wrapper import QdrantVectorStore
from .rag.setup_collections import QdrantCollectionSetup

# ML Module
from .ml.predictive_models import WorkflowPredictor
from .ml.training_pipeline import TrainingPipeline
from .ml.anomaly_detection import AnomalyDetector

# Learning Module
from .learning.self_learning_engine import SelfLearningEngine
from .learning.pattern_extractor import PatternExtractor
from .learning.rule_generator import RuleGenerator

# Context Module
from .context.context_builder import ContextBuilder

# LLM Module
from .llm.llm_router import LLMRouter

# ===========================
# FEDERATED ARCHITECTURE (v2.0)
# ===========================

# Protocols - Interface definitions
from .protocols import IMLSubsystem, IRAGSubsystem, ILearningSubsystem
from .protocols import MLDataStandard, RAGDataStandard, LearningDataStandard

# Coordinator - Central coordination hub
from .coordinator import SubsystemCoordinator, get_global_coordinator

# Reference Implementations
from .ml.base_ml_subsystem import BaseMLSubsystem

# ===========================
# LEGACY API (Backward Compatible, Deprecated)
# ===========================

# RAG Module (Legacy)
from .rag.pipeline import RAGPipeline, KnowledgeSourceManager
from .rag.embeddings import EmbeddingGenerator
from .rag.retrieval import HybridRetriever
from .rag.reranking import Reranker
from .rag.qdrant_wrapper import QdrantVectorStore
from .rag.setup_collections import QdrantCollectionSetup

# ML Module (Legacy)
from .ml.predictive_models import WorkflowPredictor
from .ml.training_pipeline import TrainingPipeline
from .ml.anomaly_detection import AnomalyDetector

# Learning Module (Legacy)
from .learning.self_learning_engine import SelfLearningEngine
from .learning.pattern_extractor import PatternExtractor
from .learning.rule_generator import RuleGenerator

# Context Module
from .context.context_builder import ContextBuilder

# LLM Module
from .llm.llm_router import LLMRouter

__all__ = [
    # === FEDERATED ARCHITECTURE (v2.0) ===
    # Protocols
    "IMLSubsystem",
    "IRAGSubsystem",
    "ILearningSubsystem",
    "MLDataStandard",
    "RAGDataStandard",
    "LearningDataStandard",
    # Coordinator
    "SubsystemCoordinator",
    "get_global_coordinator",
    # Reference Implementations
    "BaseMLSubsystem",

    # === LEGACY API (Deprecated) ===
    # RAG
    "RAGPipeline",
    "KnowledgeSourceManager",
    "EmbeddingGenerator",
    "HybridRetriever",
    "Reranker",
    "QdrantVectorStore",
    "QdrantCollectionSetup",
    # ML
    "WorkflowPredictor",
    "TrainingPipeline",
    "AnomalyDetector",
    # Learning
    "SelfLearningEngine",
    "PatternExtractor",
    "RuleGenerator",
    # Context
    "ContextBuilder",
    # LLM
    "LLMRouter",
]
