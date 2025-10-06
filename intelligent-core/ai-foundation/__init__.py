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
from .rag.pipeline import RAGPipeline
from .rag.embeddings import EmbeddingService
from .rag.retrieval import HybridRetriever
from .rag.reranking import Reranker

# ML Module
from .ml.predictive_models import PredictiveModel
from .ml.training_pipeline import MLTrainer
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
    "EmbeddingService",
    "HybridRetriever",
    "Reranker",
    # ML
    "PredictiveModel",
    "MLTrainer",
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
