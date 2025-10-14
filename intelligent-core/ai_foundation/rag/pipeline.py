"""
RAG Pipeline

Main orchestration for Retrieval-Augmented Generation.
Combines embeddings, retrieval, and reranking for contextual knowledge.
"""

from typing import List, Dict, Any, Optional
import logging

from .embeddings import EmbeddingGenerator, DocumentChunker
from .retrieval import HybridRetriever
from .qdrant_client import QdrantVectorStore  # Real vector DB!
from .reranking import Reranker, DiversityReranker

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG Pipeline

    Complete RAG workflow:
    1. Document ingestion and chunking
    2. Embedding generation
    3. Vector storage
    4. Hybrid retrieval
    5. Reranking
    """

    def __init__(
        self,
        knowledge_sources: Optional[List[str]] = None,
        embedding_provider: str = "voyage",
        chunk_size: int = 512,
        top_k: int = 5
    ):
        """
        Initialize RAG pipeline

        Args:
            knowledge_sources: List of knowledge source types
            embedding_provider: Embedding provider ('voyage', 'openai', 'local')
            chunk_size: Document chunk size
            top_k: Default number of results
        """
        self.knowledge_sources = knowledge_sources or []
        self.top_k = top_k

        # Initialize components
        self.embedding_generator = EmbeddingGenerator(provider=embedding_provider)
        self.chunker = DocumentChunker(chunk_size=chunk_size)
        self.vector_store = QdrantVectorStore(collection_name="bcm_knowledge")
        self.retriever = HybridRetriever(self.embedding_generator)
        self.reranker = Reranker()
        self.diversity_reranker = DiversityReranker()

        # Knowledge source configuration
        self.source_config = {
            'iso_standards': {
                'priority': 1.0,
                'type': 'iso_standard'
            },
            'bci_guidelines': {
                'priority': 0.95,
                'type': 'bci_guidelines'
            },
            'case_library': {
                'priority': 0.8,
                'type': 'case_study'
            },
            'community_annotations': {
                'priority': 0.7,
                'type': 'community'
            }
        }

    async def ingest_documents(
        self,
        documents: List[Dict[str, Any]],
        source_type: str = 'documentation'
    ) -> List[str]:
        """
        Ingest documents into RAG pipeline

        Args:
            documents: List of documents with 'text' and optional 'metadata'
            source_type: Type of source

        Returns:
            List of document IDs
        """

        logger.info(f"Ingesting {len(documents)} documents from {source_type}")

        all_doc_ids = []

        for doc in documents:
            text = doc.get('text') or doc.get('content')
            if not text:
                logger.warning(f"Skipping document without text: {doc.get('id', 'unknown')}")
                continue

            metadata = doc.get('metadata', {})
            metadata['source_type'] = source_type

            # Add source priority
            if source_type in self.source_config:
                metadata['source_priority'] = self.source_config[source_type]['priority']

            # Chunk document
            chunks = self.chunker.chunk_document(text, metadata)

            # Add chunks to vector store
            chunk_texts = [chunk['text'] for chunk in chunks]
            chunk_metadatas = [
                {k: v for k, v in chunk.items() if k != 'text'}
                for chunk in chunks
            ]

            doc_ids = await self.vector_store.add_documents(
                texts=chunk_texts,
                metadatas=chunk_metadatas
            )

            all_doc_ids.extend(doc_ids)

        logger.info(f"Ingested {len(all_doc_ids)} chunks from {len(documents)} documents")

        return all_doc_ids

    async def retrieve(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        enable_reranking: bool = True,
        enable_diversity: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge

        Args:
            query: Search query
            context: Additional context for relevance
            top_k: Number of results (default: self.top_k)
            filters: Metadata filters
            enable_reranking: Enable result reranking
            enable_diversity: Enable diversity filtering

        Returns:
            Relevant knowledge chunks
        """

        top_k = top_k or self.top_k

        logger.info(f"RAG retrieve: query='{query[:50]}...', top_k={top_k}")

        # Step 1: Hybrid retrieval
        # Retrieve more than needed for reranking
        retrieval_k = top_k * 3 if enable_reranking else top_k

        results = await self.vector_store.search(
            query=query,
            top_k=retrieval_k,
            filters=filters
        )

        if not results:
            logger.warning("No results found for query")
            return []

        logger.info(f"Retrieved {len(results)} initial results")

        # Step 2: Reranking (if enabled)
        if enable_reranking:
            results = self.reranker.rerank(
                results=results,
                context=context,
                top_k=top_k * 2 if enable_diversity else top_k
            )
            logger.info(f"Reranked to {len(results)} results")

        # Step 3: Diversity filtering (if enabled)
        if enable_diversity:
            results = self.diversity_reranker.rerank_with_diversity(
                results=results,
                top_k=top_k,
                embedding_generator=self.embedding_generator
            )
            logger.info(f"Diversity filtering to {len(results)} results")

        # Step 4: Format results
        formatted_results = self._format_results(results)

        return formatted_results

    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format results for consumption

        Args:
            results: Raw search results

        Returns:
            Formatted results
        """

        formatted = []

        for result in results:
            formatted_result = {
                'content': result.get('text', ''),
                'source': result.get('source_type', 'unknown'),
                'score': result.get('rerank_score') or result.get('score', 0.0),
                'metadata': {}
            }

            # Add relevant metadata
            for key in ['industry', 'org_size', 'module', 'stage', 'date', 'chunk_index']:
                if key in result:
                    formatted_result['metadata'][key] = result[key]

            formatted.append(formatted_result)

        return formatted

    async def build_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        max_context_length: int = 2000
    ) -> str:
        """
        Build RAG context for LLM prompt

        Args:
            query: User query
            context: Additional context
            max_context_length: Maximum context length (characters)

        Returns:
            Formatted context string
        """

        # Retrieve relevant knowledge
        results = await self.retrieve(
            query=query,
            context=context,
            enable_reranking=True
        )

        if not results:
            return ""

        # Build context string
        context_parts = []
        current_length = 0

        for i, result in enumerate(results, 1):
            content = result['content']
            source = result['source']

            # Format context item
            context_item = f"[{i}] Source: {source}\n{content}\n"

            item_length = len(context_item)

            if current_length + item_length > max_context_length:
                break

            context_parts.append(context_item)
            current_length += item_length

        context_str = "\n".join(context_parts)

        return context_str

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics"""

        vector_stats = self.vector_store.get_stats()

        return {
            'vector_store': vector_stats,
            'knowledge_sources': self.knowledge_sources,
            'embedding_provider': self.embedding_generator.provider,
            'chunk_size': self.chunker.chunk_size,
            'default_top_k': self.top_k
        }

    def clear(self):
        """Clear all stored documents"""
        self.vector_store.clear()
        logger.info("RAG pipeline cleared")


class KnowledgeSourceManager:
    """
    Knowledge Source Manager

    Manages different knowledge sources for RAG pipeline.
    """

    def __init__(self, rag_pipeline: RAGPipeline):
        """
        Initialize knowledge source manager

        Args:
            rag_pipeline: RAGPipeline instance
        """
        self.rag_pipeline = rag_pipeline

    async def load_iso_standards(self, standards_data: List[Dict[str, Any]]) -> int:
        """
        Load ISO 22301 standards

        Args:
            standards_data: List of standard clauses

        Returns:
            Number of documents loaded
        """

        doc_ids = await self.rag_pipeline.ingest_documents(
            documents=standards_data,
            source_type='iso_standard'
        )

        return len(doc_ids)

    async def load_case_library(self, cases: List[Dict[str, Any]]) -> int:
        """
        Load case library

        Args:
            cases: List of case studies

        Returns:
            Number of documents loaded
        """

        # Format cases for ingestion
        formatted_cases = []

        for case in cases:
            # Combine case fields into text
            text_parts = [
                f"Title: {case.get('title', '')}",
                f"Industry: {case.get('industry', '')}",
                f"Summary: {case.get('summary', '')}",
                f"Challenge: {case.get('key_challenge', '')}",
                f"Solution: {case.get('solution', '')}",
                f"Outcome: {case.get('outcome', '')}",
            ]

            if case.get('lessons_learned'):
                text_parts.append("Lessons Learned:")
                for lesson in case['lessons_learned']:
                    text_parts.append(f"- {lesson}")

            text = "\n".join(text_parts)

            formatted_cases.append({
                'text': text,
                'metadata': {
                    'case_id': case.get('id'),
                    'industry': case.get('industry'),
                    'org_size': case.get('org_size'),
                    'module': case.get('module'),
                    'success': case.get('success', True)
                }
            })

        doc_ids = await self.rag_pipeline.ingest_documents(
            documents=formatted_cases,
            source_type='case_study'
        )

        return len(doc_ids)

    async def load_community_annotations(self, annotations: List[Dict[str, Any]]) -> int:
        """
        Load community annotations

        Args:
            annotations: List of community annotations

        Returns:
            Number of documents loaded
        """

        formatted_annotations = []

        for annotation in annotations:
            text = annotation.get('text') or annotation.get('content', '')

            formatted_annotations.append({
                'text': text,
                'metadata': {
                    'clause': annotation.get('clause_id'),
                    'rating': annotation.get('rating'),
                    'date': annotation.get('created_at')
                }
            })

        doc_ids = await self.rag_pipeline.ingest_documents(
            documents=formatted_annotations,
            source_type='community'
        )

        return len(doc_ids)

    async def load_bci_guidelines(self, guidelines: List[Dict[str, Any]]) -> int:
        """
        Load BCI Good Practice Guidelines

        Args:
            guidelines: List of BCI guidelines

        Returns:
            Number of documents loaded
        """

        doc_ids = await self.rag_pipeline.ingest_documents(
            documents=guidelines,
            source_type='bci_guidelines'
        )

        return len(doc_ids)
