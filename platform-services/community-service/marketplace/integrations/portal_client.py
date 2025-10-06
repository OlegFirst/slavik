"""
Portal Service Integration for Marketplace
Enables cross-service communication between Marketplace and Portal
"""

import os
from typing import Optional, List
import httpx
import logging

logger = logging.getLogger(__name__)

PORTAL_URL = os.getenv("PORTAL_URL", "http://localhost:8031")


class PortalClient:
    """
    HTTP client for Portal Service (Port 8031)

    Use Cases:
    - Find relevant knowledge articles for specialists
    - Get BCM scenarios for project types
    - Create knowledge articles from completed projects
    - Link forum discussions to marketplace projects
    """

    def __init__(self):
        self.base_url = PORTAL_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # Knowledge Hub Integration
    # ========================================================================

    async def search_knowledge_articles(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        Search knowledge articles relevant to marketplace activities

        Use cases:
        - Recommend articles to specialists based on their skills
        - Show related content for project types
        - Help clients understand BCM concepts

        Args:
            query: Search query (e.g., "BIA", "ISO 22301", "business continuity")
            category: Filter by category (e.g., "guides", "templates")
            limit: Max results to return

        Returns:
            List of article summaries
        """
        try:
            params = {
                "q": query,
                "limit": limit
            }
            if category:
                params["category"] = category

            response = await self.client.get(
                f"{self.base_url}/api/portal/knowledge/search",
                params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to search knowledge: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error searching knowledge articles: {e}")
            return []

    async def get_article(self, article_id: int) -> Optional[dict]:
        """
        Get specific knowledge article

        Args:
            article_id: Article ID

        Returns:
            Article data or None
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/portal/knowledge/articles/{article_id}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting article: {e}")
            return None

    async def create_article_from_project(
        self,
        project_id: int,
        specialist_id: int,
        title: str,
        content: str,
        category: str,
        token: str
    ) -> Optional[dict]:
        """
        Create knowledge article from completed marketplace project

        Use case:
        - After successful project completion, specialist can contribute
          their experience as a knowledge article
        - Automatic generation from project deliverables

        Args:
            project_id: Marketplace project ID (for reference)
            specialist_id: Specialist who completed the project
            title: Article title
            content: Article content (markdown)
            category: Article category
            token: JWT token for authorization

        Returns:
            Created article data or None
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/portal/knowledge/articles",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "title": title,
                    "content": content,
                    "category": category,
                    "excerpt": content[:200],
                    "tags": ["marketplace", f"project_{project_id}"],
                    "metadata": {
                        "source": "marketplace_project",
                        "project_id": project_id,
                        "specialist_id": specialist_id
                    }
                }
            )

            if response.status_code == 201:
                logger.info(f"Article created from project {project_id}")
                return response.json()
            else:
                logger.error(f"Failed to create article: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error creating article: {e}")
            return None

    # ========================================================================
    # Scenario Integration
    # ========================================================================

    async def search_scenarios(
        self,
        service_type: str,
        limit: int = 3
    ) -> List[dict]:
        """
        Find relevant BCM scenarios for project type

        Use case:
        - When client posts a project, show relevant scenarios
        - Specialists can reference scenarios when writing proposals

        Args:
            service_type: Marketplace service type (e.g., "bia", "bcm_plan", "risk_assessment")
            limit: Max results

        Returns:
            List of relevant scenarios
        """
        try:
            # Map marketplace service types to scenario categories
            scenario_mapping = {
                "bia": "Business Impact Analysis",
                "bcm_plan": "Business Continuity Planning",
                "risk_assessment": "Risk Assessment",
                "iso_22301": "ISO 22301",
                "training": "Training",
                "exercise": "Exercise"
            }

            category = scenario_mapping.get(service_type, service_type)

            response = await self.client.get(
                f"{self.base_url}/api/portal/scenarios/search",
                params={
                    "category": category,
                    "limit": limit
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                return []

        except Exception as e:
            logger.error(f"Error searching scenarios: {e}")
            return []

    # ========================================================================
    # Forum Integration
    # ========================================================================

    async def create_forum_topic_from_project(
        self,
        project_id: int,
        title: str,
        content: str,
        category_id: int,
        token: str
    ) -> Optional[dict]:
        """
        Create forum discussion from marketplace project

        Use case:
        - Client posts project but also wants community feedback
        - Convert project request into forum question

        Args:
            project_id: Marketplace project ID
            title: Topic title
            content: Topic content
            category_id: Forum category ID
            token: JWT token

        Returns:
            Created topic data or None
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/portal/forum/topics",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "category_id": category_id,
                    "title": title,
                    "content": content,
                    "tags": ["marketplace", f"project_{project_id}"],
                    "topic_type": "question"
                }
            )

            if response.status_code == 201:
                logger.info(f"Forum topic created for project {project_id}")
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Error creating forum topic: {e}")
            return None

    async def link_forum_to_project(
        self,
        topic_id: int,
        project_id: int,
        token: str
    ) -> bool:
        """
        Link existing forum discussion to marketplace project

        Args:
            topic_id: Forum topic ID
            project_id: Marketplace project ID
            token: JWT token

        Returns:
            True if linked successfully
        """
        try:
            # This could be done via metadata or tags
            response = await self.client.patch(
                f"{self.base_url}/api/portal/forum/topics/{topic_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "metadata": {
                        "marketplace_project_id": project_id
                    }
                }
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error linking forum to project: {e}")
            return False

    # ========================================================================
    # Reputation/Gamification Integration
    # ========================================================================

    async def get_user_reputation(
        self,
        user_id: str,
        token: str
    ) -> Optional[dict]:
        """
        Get user's forum reputation score

        Use case:
        - Display community reputation on specialist profiles
        - Factor into specialist credibility score

        Args:
            user_id: User ID
            token: JWT token

        Returns:
            Reputation data (points, level, badges) or None
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/portal/forum/reputation/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting user reputation: {e}")
            return None


# Global instance
portal_client = PortalClient()
