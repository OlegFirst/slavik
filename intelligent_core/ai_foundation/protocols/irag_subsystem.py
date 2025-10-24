"""
IRAGSubsystem - Retrieval-Augmented Generation Subsystem Protocol
==================================================================

Protocol interface that EVERY RAG subsystem must implement.

Examples of implementations:
- workflow_intelligence/rag/workflow_rag_subsystem.py
- expertise_center/rag/expert_rag_subsystem.py
- orchestration/rag/orchestration_rag_subsystem.py
- ai_foundation/rag/base_rag_subsystem.py (reference implementation)

Each implementation has its own:
- Knowledge sources
- Embedding models
- Retrieval strategies
- Reranking logic
- Domain-specific context building

But all follow this protocol for coordination.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class IRAGSubsystem(ABC):
    """
    Protocol for RAG subsystems - defines standard interface.

    Every module that has RAG capabilities must implement this interface.
    The coordinator polls all implementations and aggregates results.
    """

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return subsystem metadata for discovery and coordination.

        Returns:
            dict: Metadata including:
                - name: str - Subsystem name (e.g., 'workflow_rag')
                - domain: str - Domain of expertise
                - version: str - Subsystem version
                - capabilities: List[str] - What this subsystem can retrieve
                - collections: List[str] - Available vector collections
                - status: str - 'active', 'indexing', 'degraded', 'offline'
                - source_count: int - Number of knowledge sources

        Example:
            {
                'name': 'workflow_rag',
                'domain': 'workflow',
                'version': '1.0.0',
                'capabilities': ['workflow_retrieval', 'process_context', 'best_practices'],
                'collections': ['workflow_patterns', 'process_templates', 'historical_workflows'],
                'status': 'active',
                'source_count': 1250
            }
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge for query.

        Args:
            query: Search query (natural language or structured)
            config: Optional retrieval configuration
                - top_k: int - Number of results (default: 5)
                - min_score: float - Minimum relevance score
                - collections: List[str] - Which collections to search
                - rerank: bool - Whether to rerank results
                - filters: dict - Domain-specific filters

        Returns:
            dict: Retrieval result in STANDARD format
                - subsystem: str - Name of this subsystem
                - domain: str - Domain of knowledge
                - results: List[dict] - Retrieved documents
                  Each result:
                    - id: str - Document ID
                    - content: str - Document content
                    - score: float - Relevance score [0.0-1.0]
                    - metadata: dict - Document metadata
                    - source: str - Knowledge source
                - query: str - Original query
                - result_count: int - Number of results returned
                - timestamp: str - ISO format timestamp

        Example:
            {
                'subsystem': 'workflow_rag',
                'domain': 'workflow',
                'results': [
                    {
                        'id': 'doc_123',
                        'content': 'Workflow best practice: Always validate inputs...',
                        'score': 0.92,
                        'metadata': {'type': 'best_practice', 'category': 'validation'},
                        'source': 'workflow_knowledge_base'
                    },
                    ...
                ],
                'query': 'How to validate workflow inputs?',
                'result_count': 5,
                'timestamp': '2025-10-22T10:30:00Z'
            }
        """
        pass

    @abstractmethod
    def index_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Index a new document into knowledge base.

        Args:
            document: Document to index
                - content: str - Document content
                - metadata: dict - Document metadata
                - collection: str - Target collection
                - id: Optional[str] - Document ID (auto-generate if not provided)

        Returns:
            dict: Indexing result
                - success: bool
                - document_id: str
                - collection: str
                - timestamp: str
        """
        pass

    @abstractmethod
    def update_document(self, document_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing document in knowledge base.

        Args:
            document_id: ID of document to update
            updates: Fields to update
                - content: Optional[str]
                - metadata: Optional[dict]

        Returns:
            dict: Update result
                - success: bool
                - document_id: str
                - timestamp: str
        """
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete document from knowledge base.

        Args:
            document_id: ID of document to delete

        Returns:
            dict: Deletion result
                - success: bool
                - document_id: str
                - timestamp: str
        """
        pass

    @abstractmethod
    def build_context(self, query: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """
        Build context for LLM from retrieved knowledge.

        Args:
            query: Context query
            max_tokens: Maximum context size

        Returns:
            dict: Context data
                - context: str - Formatted context string for LLM
                - sources: List[str] - Source document IDs
                - token_count: int - Approximate token count
                - subsystem: str
                - timestamp: str
        """
        pass

    @abstractmethod
    def register_with_coordinator(self, coordinator: Any) -> bool:
        """
        Register this subsystem with the central coordinator.

        Args:
            coordinator: SubsystemCoordinator instance

        Returns:
            bool: True if registration successful
        """
        pass

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """
        Return current health status of this subsystem.

        Returns:
            dict: Health status
                - healthy: bool
                - status: str - 'healthy', 'degraded', 'critical', 'offline'
                - last_retrieval: str - ISO timestamp
                - last_indexing: str - ISO timestamp
                - document_count: int
                - collection_count: int
                - error_rate: float - [0.0-1.0]
                - issues: List[str] - Any current issues
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of capabilities this subsystem provides.

        Returns:
            List[str]: Capability names

        Example:
            ['semantic_search', 'hybrid_retrieval', 'context_building', 'reranking']
        """
        pass

    @abstractmethod
    def search_by_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search knowledge base using structured filters (not semantic).

        Args:
            filters: Search filters (domain-specific)
                Example for workflow:
                {
                    'process_type': 'incident_response',
                    'status': 'approved',
                    'date_range': {'start': '2024-01-01', 'end': '2025-01-01'}
                }

        Returns:
            dict: Search results in standard format
        """
        pass


class RAGDataStandard:
    """
    Standard data format for RAG subsystem communication.

    All subsystems should format their data according to this standard
    for coordinator aggregation.
    """

    @staticmethod
    def format_retrieval_result(
        subsystem_name: str,
        domain: str,
        query: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Format retrieval result in standard way.

        Args:
            subsystem_name: Name of subsystem
            domain: Domain of expertise
            query: Original query
            results: List of retrieved documents

        Returns:
            dict: Standardized retrieval result
        """
        return {
            'subsystem': subsystem_name,
            'domain': domain,
            'query': query,
            'results': results,
            'result_count': len(results),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    @staticmethod
    def format_document(
        content: str,
        doc_id: str,
        score: float,
        metadata: Dict[str, Any],
        source: str
    ) -> Dict[str, Any]:
        """Format single document in standard way."""
        return {
            'id': doc_id,
            'content': content,
            'score': score,
            'metadata': metadata,
            'source': source
        }

    @staticmethod
    def format_context(
        context: str,
        sources: List[str],
        token_count: int,
        subsystem_name: str
    ) -> Dict[str, Any]:
        """Format context in standard way."""
        return {
            'context': context,
            'sources': sources,
            'token_count': token_count,
            'subsystem': subsystem_name,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
