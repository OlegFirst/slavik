"""
RAG (Retrieval-Augmented Generation) Pipeline

Provides contextual knowledge retrieval for AI experts.

Components:
- Embeddings: Generate vector embeddings for semantic search
- Retrieval: Hybrid search (vector + keyword)
- Reranking: Re-rank results by relevance
- Pipeline: Orchestrate the full RAG flow
- BaseRAGSubsystem: Reference implementation of IRAGSubsystem protocol
"""

from .pipeline import RAGPipeline
from .embeddings import EmbeddingGenerator
from .retrieval import HybridRetriever
from .reranking import Reranker
from .qdrant_wrapper import QdrantVectorStore
from .base_rag_subsystem import BaseRAGSubsystem

__all__ = [
    'RAGPipeline',
    'EmbeddingGenerator',
    'HybridRetriever',
    'Reranker',
    'QdrantVectorStore',
    'BaseRAGSubsystem',
]
