"""
AI Foundation - Core AI Infrastructure
=======================================

Provides RAG, ML, Learning, Context, LLM for entire platform.

This is the foundational AI layer used by:
- workflow_intelligence
- expertise-center
- community_intelligence
- platform-services (when they need AI)

Architecture Decision: ai-foundation is separate from workflow_intelligence
to avoid tight coupling and allow independent scaling/versioning.
"""

__version__ = "1.0.0"

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

__all__ = [
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
