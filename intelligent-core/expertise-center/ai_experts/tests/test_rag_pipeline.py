"""
Tests for RAG Pipeline
"""

import pytest
from ..rag.pipeline import RAGPipeline
from ..rag.embeddings import EmbeddingGenerator
from ..rag.retrieval import HybridRetriever


class TestEmbeddingGenerator:
    """Test embedding generation"""

    @pytest.mark.asyncio
    async def test_embedding_generation(self):
        """Test single embedding generation"""
        generator = EmbeddingGenerator(provider="local")

        embedding = await generator.generate_embedding("Test text")

        assert isinstance(embedding, list)
        assert len(embedding) == 1024  # Default dimension

    @pytest.mark.asyncio
    async def test_batch_embedding_generation(self):
        """Test batch embedding generation"""
        generator = EmbeddingGenerator(provider="local")

        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = await generator.generate_embeddings(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 1024 for emb in embeddings)


class TestRAGPipeline:
    """Test RAG Pipeline"""

    @pytest.mark.asyncio
    async def test_rag_pipeline_initialization(self):
        """Test RAG pipeline initialization"""
        pipeline = RAGPipeline()

        assert pipeline is not None
        assert pipeline.embedding_generator is not None

    @pytest.mark.asyncio
    async def test_document_ingestion(self):
        """Test document ingestion"""
        pipeline = RAGPipeline()

        documents = [
            {'text': 'ISO 22301 clause 8.2.2 requires BIA', 'metadata': {'source': 'iso_standard'}},
            {'text': 'Critical processes must be identified', 'metadata': {'source': 'documentation'}}
        ]

        doc_ids = await pipeline.ingest_documents(documents, source_type='iso_standard')

        assert len(doc_ids) > 0

    @pytest.mark.asyncio
    async def test_retrieval(self):
        """Test RAG retrieval"""
        pipeline = RAGPipeline()

        # Ingest test documents
        documents = [
            {'text': 'BIA identifies critical processes', 'metadata': {'module': 'BIA'}},
            {'text': 'Recovery strategies define approach', 'metadata': {'module': 'Strategy'}}
        ]

        await pipeline.ingest_documents(documents)

        # Retrieve
        results = await pipeline.retrieve(
            query="critical processes",
            top_k=2
        )

        assert len(results) > 0
        assert 'content' in results[0]
