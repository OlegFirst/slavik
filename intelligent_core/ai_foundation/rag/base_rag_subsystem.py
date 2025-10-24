"""
Base RAG Subsystem - Reference Implementation
==============================================

Reference implementation of IRAGSubsystem using ai_foundation's existing RAG code.

This wraps the existing RAG implementations (vector search, retrieval, context building)
into the IRAGSubsystem protocol, serving as:
1. A working implementation for general RAG tasks
2. A reference example for other modules to implement their own

Other modules should implement IRAGSubsystem with their own domain logic,
not just reuse this implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import os
import uuid

from ..protocols import IRAGSubsystem, RAGDataStandard

# Vector DB imports
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant not available. Install with: pip install qdrant-client")

# Embedding imports
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning("SentenceTransformers not available. Install with: pip install sentence-transformers")


logger = logging.getLogger(__name__)


class BaseRAGSubsystem(IRAGSubsystem):
    """
    Reference RAG subsystem implementation.

    Uses Qdrant for vector storage and sentence-transformers for embeddings.
    Provides basic RAG functionality that other modules can extend.

    Domain: 'base' - General-purpose RAG
    """

    def __init__(
        self,
        collection_name: str = "base_knowledge",
        qdrant_host: str = None,
        qdrant_port: int = 6333,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize base RAG subsystem.

        Args:
            collection_name: Name of Qdrant collection
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            embedding_model: SentenceTransformer model name
        """
        self.name = "base_rag"
        self.domain = "base"
        self.version = "1.0.0"
        self.collection_name = collection_name

        # Initialize Qdrant client
        if QDRANT_AVAILABLE:
            host = qdrant_host or os.getenv('QDRANT_HOST', 'localhost')
            self.qdrant = QdrantClient(host=host, port=qdrant_port)
            self._ensure_collection_exists()
        else:
            self.qdrant = None
            logger.warning("Running without Qdrant support")

        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        else:
            self.embedding_model = None
            self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
            logger.warning("Running without embedding support")

        # Track health
        self._last_retrieval = None
        self._last_indexing = None
        self._error_count = 0
        self._retrieval_count = 0
        self._document_count = 0

        logger.info(f"BaseRAGSubsystem initialized: {self.name}")

    def _ensure_collection_exists(self):
        """Ensure Qdrant collection exists."""
        if not self.qdrant:
            return

        try:
            collections = self.qdrant.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")

    def get_metadata(self) -> Dict[str, Any]:
        """Return subsystem metadata."""
        return {
            'name': self.name,
            'domain': self.domain,
            'version': self.version,
            'capabilities': [
                'semantic_search',
                'hybrid_retrieval',
                'context_building',
                'document_management'
            ],
            'collections': [self.collection_name],
            'status': 'active' if (self.qdrant and self.embedding_model) else 'degraded',
            'source_count': self._document_count
        }

    def retrieve(self, query: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge for query.

        Args:
            query: Search query
            config: Retrieval configuration

        Returns:
            dict: Retrieval result in standard format
        """
        try:
            config = config or {}
            top_k = config.get('top_k', 5)
            min_score = config.get('min_score', 0.0)

            if not self.qdrant or not self.embedding_model:
                return self._fallback_retrieve(query, config)

            # Generate query embedding
            query_vector = self.embedding_model.encode(query).tolist()

            # Search Qdrant
            search_results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )

            # Format results
            results = []
            for hit in search_results:
                if hit.score >= min_score:
                    results.append(
                        RAGDataStandard.format_document(
                            content=hit.payload.get('content', ''),
                            doc_id=str(hit.id),
                            score=float(hit.score),
                            metadata=hit.payload.get('metadata', {}),
                            source=hit.payload.get('source', 'unknown')
                        )
                    )

            self._last_retrieval = datetime.utcnow()
            self._retrieval_count += 1

            return RAGDataStandard.format_retrieval_result(
                subsystem_name=self.name,
                domain=self.domain,
                query=query,
                results=results
            )

        except Exception as e:
            logger.error(f"Retrieval error in BaseRAGSubsystem: {e}")
            self._error_count += 1
            return RAGDataStandard.format_retrieval_result(
                subsystem_name=self.name,
                domain=self.domain,
                query=query,
                results=[]
            )

    def _fallback_retrieve(self, query: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback retrieval when services unavailable."""
        logger.warning("Using fallback retrieval (no Qdrant/embeddings)")
        return RAGDataStandard.format_retrieval_result(
            subsystem_name=self.name,
            domain=self.domain,
            query=query,
            results=[]
        )

    def index_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Index a new document into knowledge base.

        Args:
            document: Document to index
                - content: str
                - metadata: dict
                - collection: str (optional)
                - id: str (optional)

        Returns:
            dict: Indexing result
        """
        try:
            if not self.qdrant or not self.embedding_model:
                raise RuntimeError("Qdrant or embedding model not available")

            content = document.get('content', '')
            if not content:
                raise ValueError("Document content is required")

            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()

            # Generate document ID
            doc_id = document.get('id', str(uuid.uuid4()))

            # Prepare payload
            payload = {
                'content': content,
                'metadata': document.get('metadata', {}),
                'source': document.get('source', 'unknown'),
                'indexed_at': datetime.utcnow().isoformat() + 'Z'
            }

            # Index in Qdrant
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )

            self._last_indexing = datetime.utcnow()
            self._document_count += 1

            return {
                'success': True,
                'document_id': doc_id,
                'collection': self.collection_name,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Indexing error in BaseRAGSubsystem: {e}")
            self._error_count += 1
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def update_document(self, document_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing document in knowledge base.

        Args:
            document_id: ID of document to update
            updates: Fields to update

        Returns:
            dict: Update result
        """
        try:
            if not self.qdrant:
                raise RuntimeError("Qdrant not available")

            # Get existing document
            existing = self.qdrant.retrieve(
                collection_name=self.collection_name,
                ids=[document_id]
            )

            if not existing:
                raise ValueError(f"Document {document_id} not found")

            # Merge updates
            payload = existing[0].payload
            if 'content' in updates:
                payload['content'] = updates['content']
            if 'metadata' in updates:
                payload['metadata'].update(updates['metadata'])
            payload['updated_at'] = datetime.utcnow().isoformat() + 'Z'

            # Re-embed if content changed
            if 'content' in updates and self.embedding_model:
                embedding = self.embedding_model.encode(updates['content']).tolist()
            else:
                embedding = existing[0].vector

            # Update in Qdrant
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=document_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )

            return {
                'success': True,
                'document_id': document_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Update error in BaseRAGSubsystem: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete document from knowledge base.

        Args:
            document_id: ID of document to delete

        Returns:
            dict: Deletion result
        """
        try:
            if not self.qdrant:
                raise RuntimeError("Qdrant not available")

            self.qdrant.delete(
                collection_name=self.collection_name,
                points_selector=[document_id]
            )

            self._document_count = max(0, self._document_count - 1)

            return {
                'success': True,
                'document_id': document_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Deletion error in BaseRAGSubsystem: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def build_context(self, query: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """
        Build context for LLM from retrieved knowledge.

        Args:
            query: Context query
            max_tokens: Maximum context size

        Returns:
            dict: Context data
        """
        try:
            # Retrieve relevant documents
            retrieval_result = self.retrieve(query, config={'top_k': 10})
            results = retrieval_result.get('results', [])

            if not results:
                return RAGDataStandard.format_context(
                    context="",
                    sources=[],
                    token_count=0,
                    subsystem_name=self.name
                )

            # Build context string
            context_parts = []
            sources = []
            token_count = 0

            for result in results:
                content = result['content']
                # Rough token estimation (1 token ≈ 4 chars)
                content_tokens = len(content) // 4

                if token_count + content_tokens > max_tokens:
                    break

                context_parts.append(f"[Score: {result['score']:.2f}] {content}")
                sources.append(result['id'])
                token_count += content_tokens

            context = "\n\n".join(context_parts)

            return RAGDataStandard.format_context(
                context=context,
                sources=sources,
                token_count=token_count,
                subsystem_name=self.name
            )

        except Exception as e:
            logger.error(f"Context building error in BaseRAGSubsystem: {e}")
            return RAGDataStandard.format_context(
                context="",
                sources=[],
                token_count=0,
                subsystem_name=self.name
            )

    def register_with_coordinator(self, coordinator: Any) -> bool:
        """
        Register this subsystem with the central coordinator.

        Args:
            coordinator: SubsystemCoordinator instance

        Returns:
            bool: True if registration successful
        """
        try:
            return coordinator.register_rag(self.name, self)
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Return current health status."""
        error_rate = (
            self._error_count / max(self._retrieval_count, 1)
            if self._retrieval_count > 0
            else 0.0
        )

        healthy = (
            error_rate < 0.1 and
            self.qdrant is not None and
            self.embedding_model is not None
        )

        status = 'healthy' if healthy else ('degraded' if self.qdrant else 'critical')

        issues = []
        if not self.qdrant:
            issues.append("Qdrant client not available")
        if not self.embedding_model:
            issues.append("Embedding model not available")
        if error_rate >= 0.1:
            issues.append(f"High error rate: {error_rate:.2%}")

        return {
            'healthy': healthy,
            'status': status,
            'last_retrieval': (
                self._last_retrieval.isoformat() + 'Z'
                if self._last_retrieval else None
            ),
            'last_indexing': (
                self._last_indexing.isoformat() + 'Z'
                if self._last_indexing else None
            ),
            'document_count': self._document_count,
            'collection_count': 1,
            'error_rate': error_rate,
            'issues': issues
        }

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities."""
        return [
            'semantic_search',
            'hybrid_retrieval',
            'context_building',
            'document_management'
        ]

    def search_by_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search knowledge base using structured filters.

        Args:
            filters: Search filters

        Returns:
            dict: Search results in standard format
        """
        try:
            if not self.qdrant:
                raise RuntimeError("Qdrant not available")

            # Convert filters to Qdrant filter format
            # This is a basic implementation - real one would be more sophisticated
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            qdrant_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=f"metadata.{key}",
                            match=MatchValue(value=value)
                        )
                    )
                if conditions:
                    qdrant_filter = Filter(must=conditions)

            # Scroll through all matching documents
            scroll_result = self.qdrant.scroll(
                collection_name=self.collection_name,
                scroll_filter=qdrant_filter,
                limit=100
            )

            results = []
            for point in scroll_result[0]:
                results.append(
                    RAGDataStandard.format_document(
                        content=point.payload.get('content', ''),
                        doc_id=str(point.id),
                        score=1.0,  # No relevance score for filter-based search
                        metadata=point.payload.get('metadata', {}),
                        source=point.payload.get('source', 'unknown')
                    )
                )

            return RAGDataStandard.format_retrieval_result(
                subsystem_name=self.name,
                domain=self.domain,
                query=str(filters),
                results=results
            )

        except Exception as e:
            logger.error(f"Filter search error in BaseRAGSubsystem: {e}")
            return RAGDataStandard.format_retrieval_result(
                subsystem_name=self.name,
                domain=self.domain,
                query=str(filters),
                results=[]
            )
