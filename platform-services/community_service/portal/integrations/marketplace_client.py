"""
Marketplace Service Integration for Portal
Enables cross-service communication between Portal and Marketplace
"""

import os
from typing import Optional, List
import httpx
import logging

logger = logging.getLogger(__name__)

MARKETPLACE_URL = os.getenv("MARKETPLACE_URL", "http://localhost:8032")


class MarketplaceClient:
    """
    HTTP client for Marketplace Service (Port 8032)

    Use Cases:
    - Search for specialists to recommend
    - Display specialist profiles in Portal
    - Link knowledge articles to specialists
    - Show marketplace opportunities in Forum
    """

    def __init__(self):
        self.base_url = MARKETPLACE_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # Specialist Search & Profiles
    # ========================================================================

    async def search_specialists(
        self,
        skills: Optional[List[str]] = None,
        service_type: Optional[str] = None,
        verified_only: bool = True,
        limit: int = 5
    ) -> List[dict]:
        """
        Search for specialists in marketplace

        Use cases:
        - Recommend specialists in knowledge articles
        - Show "Need help?" in Forum posts
        - Display experts for specific topics

        Args:
            skills: Filter by skills (e.g., ["ISO 22301", "BIA"])
            service_type: Filter by service type
            verified_only: Only return verified specialists
            limit: Max results

        Returns:
            List of specialist profiles
        """
        try:
            params = {
                "verified_only": verified_only,
                "limit": limit
            }
            if skills:
                params["skills"] = ",".join(skills)
            if service_type:
                params["service_type"] = service_type

            response = await self.client.get(
                f"{self.base_url}/api/marketplace/specialists/search",
                params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to search specialists: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error searching specialists: {e}")
            return []

    async def get_specialist(self, specialist_id: int) -> Optional[dict]:
        """
        Get specialist profile

        Args:
            specialist_id: Specialist ID

        Returns:
            Specialist data or None
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/marketplace/specialists/{specialist_id}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting specialist: {e}")
            return None

    # ========================================================================
    # Project Opportunities
    # ========================================================================

    async def get_active_projects(
        self,
        service_type: Optional[str] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        Get active marketplace projects

        Use case:
        - Show "Work Opportunities" in Portal sidebar
        - Recommend projects to forum users based on their expertise

        Args:
            service_type: Filter by service type
            limit: Max results

        Returns:
            List of active projects
        """
        try:
            params = {
                "status": "open",
                "limit": limit
            }
            if service_type:
                params["service_type"] = service_type

            response = await self.client.get(
                f"{self.base_url}/api/marketplace/projects",
                params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                return []

        except Exception as e:
            logger.error(f"Error getting active projects: {e}")
            return []

    # ========================================================================
    # Recommendations
    # ========================================================================

    async def recommend_specialists_for_article(
        self,
        article_category: str,
        article_tags: List[str],
        limit: int = 3
    ) -> List[dict]:
        """
        Recommend specialists relevant to knowledge article

        Use case:
        - Show "Experts on this topic" in article sidebar
        - Match article topics with specialist skills

        Args:
            article_category: Article category
            article_tags: Article tags
            limit: Max specialists to return

        Returns:
            List of recommended specialists
        """
        # Map article topics to marketplace skills
        skills_mapping = {
            "bia": ["Business Impact Analysis", "BIA"],
            "bcm": ["Business Continuity", "BCM", "ISO 22301"],
            "risk": ["Risk Assessment", "Risk Management"],
            "iso_22301": ["ISO 22301", "BCM"],
            "training": ["BCM Training", "Training"],
            "exercise": ["BCM Exercise", "Testing"]
        }

        # Extract relevant skills from tags
        relevant_skills = []
        for tag in article_tags:
            tag_lower = tag.lower()
            if tag_lower in skills_mapping:
                relevant_skills.extend(skills_mapping[tag_lower])

        # Also check category
        category_lower = article_category.lower()
        if category_lower in skills_mapping:
            relevant_skills.extend(skills_mapping[category_lower])

        if relevant_skills:
            return await self.search_specialists(
                skills=relevant_skills,
                verified_only=True,
                limit=limit
            )
        else:
            return []

    async def recommend_projects_for_user(
        self,
        user_skills: List[str],
        limit: int = 5
    ) -> List[dict]:
        """
        Recommend marketplace projects based on forum user's expertise

        Use case:
        - User who answers many BIA questions → recommend BIA projects
        - Based on forum reputation and topic expertise

        Args:
            user_skills: Skills inferred from forum activity
            limit: Max projects

        Returns:
            List of recommended projects
        """
        # This would match user_skills with project.required_skills
        # For now, simplified version
        try:
            params = {
                "status": "open",
                "limit": limit
            }

            response = await self.client.get(
                f"{self.base_url}/api/marketplace/projects",
                params=params
            )

            if response.status_code == 200:
                projects = response.json()
                # TODO: Filter and rank by skill match
                return projects
            else:
                return []

        except Exception as e:
            logger.error(f"Error recommending projects: {e}")
            return []


# Global instance
marketplace_client = MarketplaceClient()
