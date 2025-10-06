"""
Knowledge Base Client - Structured Knowledge Management

Provides access to structured knowledge:
- Documents
- Procedures
- Guidelines
- Lessons learned
- Best practices

Complements RAG with structured metadata
"""

import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class KnowledgeType(str, Enum):
    """Knowledge item types"""
    DOCUMENT = "document"
    PROCEDURE = "procedure"
    GUIDELINE = "guideline"
    LESSON_LEARNED = "lesson_learned"
    BEST_PRACTICE = "best_practice"
    PATTERN = "pattern"
    ARTICLE = "article"
    TRAINING_MATERIAL = "training_material"


class KnowledgeClient:
    """
    Client for Knowledge Base Service

    Provides:
    - CRUD operations
    - Search and filtering
    - Categorization
    - Version control
    """

    def __init__(self, kb_service_url: str = "http://localhost:8040"):
        """
        Initialize Knowledge Base client

        Args:
            kb_service_url: KB service endpoint (default: port 8040)
        """
        self.base_url = kb_service_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def create_article(
        self,
        title: str,
        content: str,
        category: str,
        knowledge_type: KnowledgeType = KnowledgeType.ARTICLE,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create new knowledge article

        Args:
            title: Article title
            content: Article content (markdown)
            category: Category (bcm, risk, compliance, etc.)
            knowledge_type: Type of knowledge
            tags: Tags for filtering
            metadata: Additional metadata

        Returns:
            Article ID if successful

        Example:
            article_id = await kb.create_article(
                title="Cyber Incident Escalation Procedure",
                content="## Overview\\n\\nSteps for escalation...\\n",
                category="procedures",
                knowledge_type=KnowledgeType.PROCEDURE,
                tags=["cyber", "escalation", "critical"],
                metadata={'iso_reference': 'ISO 22301:2019 8.4'}
            )
        """
        try:
            request_data = {
                'title': title,
                'content': content,
                'category': category,
                'type': knowledge_type.value,
                'tags': tags or [],
                'metadata': metadata or {},
                'created_at': datetime.utcnow().isoformat()
            }

            response = await self.client.post(
                f"{self.base_url}/api/knowledge/articles",
                json=request_data
            )

            if response.status_code == 201:
                data = response.json()
                article_id = data.get('id')
                logger.info(f"Knowledge article created: {article_id}")
                return article_id
            else:
                logger.error(f"Create article failed: {response.status_code}")
                return None

        except httpx.ConnectError:
            logger.warning("KB service unavailable")
            return None
        except Exception as e:
            logger.error(f"Create article error: {e}")
            return None

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base

        Args:
            query: Search query
            filters: Filters (category, type, tags, etc.)
            limit: Maximum results

        Returns:
            List of matching articles

        Example:
            results = await kb.search(
                query="communication failure",
                filters={
                    'category': 'lessons_learned',
                    'tags': ['communication']
                }
            )
        """
        try:
            params = {
                'q': query,
                'limit': limit
            }

            if filters:
                params.update(filters)

            response = await self.client.get(
                f"{self.base_url}/api/knowledge/search",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"KB search: found {len(data.get('results', []))} results")
                return data.get('results', [])
            return []

        except Exception as e:
            logger.error(f"KB search error: {e}")
            return []

    async def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Get article by ID

        Args:
            article_id: Article ID

        Returns:
            Article data
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/knowledge/articles/{article_id}"
            )

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Get article error: {e}")
            return None

    async def update_article(
        self,
        article_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update article

        Args:
            article_id: Article ID
            updates: Fields to update

        Returns:
            Success status
        """
        try:
            response = await self.client.patch(
                f"{self.base_url}/api/knowledge/articles/{article_id}",
                json=updates
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Update article error: {e}")
            return False

    async def delete_article(self, article_id: str) -> bool:
        """
        Delete article

        Args:
            article_id: Article ID

        Returns:
            Success status
        """
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/knowledge/articles/{article_id}"
            )

            return response.status_code == 204

        except Exception as e:
            logger.error(f"Delete article error: {e}")
            return False

    async def list_by_category(
        self,
        category: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List articles by category

        Args:
            category: Category name
            limit: Maximum results

        Returns:
            List of articles
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/knowledge/categories/{category}",
                params={'limit': limit}
            )

            if response.status_code == 200:
                return response.json().get('articles', [])
            return []

        except Exception as e:
            logger.error(f"List by category error: {e}")
            return []

    async def list_by_tags(
        self,
        tags: List[str],
        match_all: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List articles by tags

        Args:
            tags: Tags to filter by
            match_all: Require all tags (True) or any tag (False)
            limit: Maximum results

        Returns:
            List of articles
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/knowledge/tags",
                params={
                    'tags': ','.join(tags),
                    'match_all': match_all,
                    'limit': limit
                }
            )

            if response.status_code == 200:
                return response.json().get('articles', [])
            return []

        except Exception as e:
            logger.error(f"List by tags error: {e}")
            return []

    async def get_related(
        self,
        article_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get related articles

        Args:
            article_id: Source article ID
            limit: Maximum results

        Returns:
            List of related articles
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/knowledge/articles/{article_id}/related",
                params={'limit': limit}
            )

            if response.status_code == 200:
                return response.json().get('related', [])
            return []

        except Exception as e:
            logger.error(f"Get related error: {e}")
            return []

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class KnowledgeArticleBuilder:
    """
    Helper for building knowledge articles

    Ensures consistent structure
    """

    def __init__(self):
        self.title = ""
        self.content = ""
        self.category = ""
        self.knowledge_type = KnowledgeType.ARTICLE
        self.tags = []
        self.metadata = {}

    def with_title(self, title: str) -> 'KnowledgeArticleBuilder':
        """Set title"""
        self.title = title
        return self

    def with_content(self, content: str) -> 'KnowledgeArticleBuilder':
        """Set content"""
        self.content = content
        return self

    def with_category(self, category: str) -> 'KnowledgeArticleBuilder':
        """Set category"""
        self.category = category
        return self

    def with_type(self, knowledge_type: KnowledgeType) -> 'KnowledgeArticleBuilder':
        """Set knowledge type"""
        self.knowledge_type = knowledge_type
        return self

    def add_tag(self, *tags: str) -> 'KnowledgeArticleBuilder':
        """Add tags"""
        self.tags.extend(tags)
        return self

    def add_metadata(self, key: str, value: Any) -> 'KnowledgeArticleBuilder':
        """Add metadata field"""
        self.metadata[key] = value
        return self

    def with_iso_reference(self, reference: str) -> 'KnowledgeArticleBuilder':
        """Add ISO reference"""
        self.metadata['iso_reference'] = reference
        return self

    def with_severity(self, severity: str) -> 'KnowledgeArticleBuilder':
        """Add severity"""
        self.metadata['severity'] = severity
        return self

    def with_author(self, author: str) -> 'KnowledgeArticleBuilder':
        """Add author"""
        self.metadata['author'] = author
        return self

    def build(self) -> Dict[str, Any]:
        """Build article data"""
        return {
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'type': self.knowledge_type.value,
            'tags': self.tags,
            'metadata': self.metadata
        }
