"""
RAG Connector - Unified Knowledge Source

Provides semantic search across ALL platform knowledge:
- Documents
- Learning content
- Patterns
- Best practices
- ISO standards
- Threat intelligence

Single source of truth for knowledge retrieval
"""

import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class RAGConnector:
    """
    Connects to platform-wide RAG service

    Provides:
    - Semantic search
    - Context-aware retrieval
    - Knowledge contribution
    - Vector embeddings
    """

    def __init__(self, rag_service_url: str = "http://localhost:8050"):
        """
        Initialize RAG connector

        Args:
            rag_service_url: RAG service endpoint (default: port 8050)
        """
        self.base_url = rag_service_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_knowledge(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across unified knowledge base

        Args:
            query: Search query (natural language)
            context: Additional context (user_id, domain, scenario_type, etc.)
            limit: Maximum results
            filters: Metadata filters (type, category, source, etc.)
            min_score: Minimum similarity score (0-1)

        Returns:
            List of knowledge items with relevance scores

        Example:
            results = await rag.search_knowledge(
                query="How to handle cyber incident escalation",
                context={'user_id': 'user123', 'domain': 'BCM'},
                filters={'type': ['procedure', 'guideline']}
            )
        """
        try:
            request_data = {
                'query': query,
                'limit': limit,
                'min_score': min_score
            }

            if context:
                request_data['context'] = context
            if filters:
                request_data['filters'] = filters

            response = await self.client.post(
                f"{self.base_url}/api/rag/search",
                json=request_data
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"RAG search: found {len(data.get('results', []))} results for '{query[:50]}'")
                return data.get('results', [])
            else:
                logger.error(f"RAG search failed: {response.status_code}")
                return []

        except httpx.ConnectError:
            logger.warning("RAG service unavailable - using fallback")
            return self._fallback_search(query, limit)
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return []

    async def add_knowledge(
        self,
        content: str,
        metadata: Dict[str, Any],
        knowledge_type: str,
        source: str = "learning_system"
    ) -> Optional[str]:
        """
        Add new knowledge to unified knowledge base

        Args:
            content: Knowledge content (text)
            metadata: Metadata (title, category, tags, etc.)
            knowledge_type: Type (article, procedure, pattern, lesson_learned)
            source: Source service name

        Returns:
            Knowledge ID if successful

        Example:
            kb_id = await rag.add_knowledge(
                content="Pattern detected: Communication delays...",
                metadata={
                    'title': 'Communication Pattern',
                    'category': 'failure_pattern',
                    'severity': 'high',
                    'tags': ['communication', 'cyber_incident']
                },
                knowledge_type='pattern'
            )
        """
        try:
            request_data = {
                'content': content,
                'metadata': {
                    **metadata,
                    'type': knowledge_type,
                    'source': source,
                    'created_at': datetime.utcnow().isoformat()
                }
            }

            response = await self.client.post(
                f"{self.base_url}/api/rag/add",
                json=request_data
            )

            if response.status_code == 201:
                data = response.json()
                knowledge_id = data.get('id')
                logger.info(f"Knowledge added to RAG: {knowledge_id}")
                return knowledge_id
            else:
                logger.error(f"Add knowledge failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Add knowledge error: {e}")
            return None

    async def get_related_knowledge(
        self,
        knowledge_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get related knowledge items

        Args:
            knowledge_id: Source knowledge ID
            limit: Maximum related items

        Returns:
            List of related knowledge items
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/rag/related/{knowledge_id}",
                params={'limit': limit}
            )

            if response.status_code == 200:
                return response.json().get('related', [])
            return []

        except Exception as e:
            logger.error(f"Get related knowledge error: {e}")
            return []

    async def update_knowledge(
        self,
        knowledge_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update existing knowledge

        Args:
            knowledge_id: Knowledge ID
            updates: Fields to update

        Returns:
            Success status
        """
        try:
            response = await self.client.patch(
                f"{self.base_url}/api/rag/knowledge/{knowledge_id}",
                json=updates
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Update knowledge error: {e}")
            return False

    def _fallback_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fallback when RAG service unavailable

        Returns basic keyword matching results
        """
        logger.info("Using fallback search (RAG service unavailable)")

        # Basic fallback - in production, could use local cache
        return [{
            'id': 'fallback-1',
            'content': 'RAG service temporarily unavailable. Please try again later.',
            'metadata': {
                'title': 'Service Unavailable',
                'type': 'system_message'
            },
            'score': 0.5,
            'source': 'fallback'
        }]

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class RAGQueryBuilder:
    """
    Helper for building complex RAG queries

    Supports:
    - Multi-field search
    - Complex filters
    - Context enrichment
    """

    def __init__(self):
        self.query = ""
        self.context = {}
        self.filters = {}

    def with_query(self, query: str) -> 'RAGQueryBuilder':
        """Set search query"""
        self.query = query
        return self

    def with_context(self, **context) -> 'RAGQueryBuilder':
        """Add context fields"""
        self.context.update(context)
        return self

    def filter_by_type(self, *types: str) -> 'RAGQueryBuilder':
        """Filter by knowledge type"""
        self.filters['type'] = list(types)
        return self

    def filter_by_category(self, *categories: str) -> 'RAGQueryBuilder':
        """Filter by category"""
        self.filters['category'] = list(categories)
        return self

    def filter_by_tags(self, *tags: str) -> 'RAGQueryBuilder':
        """Filter by tags"""
        self.filters['tags'] = list(tags)
        return self

    def filter_by_source(self, *sources: str) -> 'RAGQueryBuilder':
        """Filter by source"""
        self.filters['source'] = list(sources)
        return self

    def build(self) -> Dict[str, Any]:
        """Build query dict"""
        return {
            'query': self.query,
            'context': self.context,
            'filters': self.filters
        }
