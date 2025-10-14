"""
Community Intelligence Integration Client

REAL integration with Community Intelligence for:
- Template sharing and discovery
- Community contributions
- Anonymous knowledge exchange
- Cross-organization learning
"""

import logging
from typing import Dict, List, Optional
import httpx

from models.pydantic_models import Scenario, SimulationResult
from config.settings import Settings

logger = logging.getLogger(__name__)


class CommunityIntelligenceClient:
    """
    Community Intelligence integration client

    Provides:
    - Share simulation templates with community
    - Discover templates from other organizations
    - Anonymous contribution mechanism
    - Quality-based filtering
    """

    def __init__(self, settings: Settings):
        """Initialize Community Intelligence client"""
        self.settings = settings
        self.base_url = settings.community_intelligence_url
        self.enabled = settings.community_intelligence_enabled
        self.timeout = 30.0

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # TEMPLATE SHARING
    # ========================================================================

    async def contribute_template(
        self,
        scenario: Scenario,
        results: Optional[SimulationResult] = None,
        organization_id: str,
        tenant_id: str,
        anonymize: bool = True
    ) -> Optional[str]:
        """
        Contribute simulation template to community

        Args:
            scenario: Scenario to share
            results: Optional results for quality validation
            organization_id: Organization ID
            tenant_id: Tenant ID
            anonymize: Whether to anonymize contribution

        Returns:
            Community template ID or None
        """
        if not self.enabled:
            return None

        try:
            contribution = {
                "template": scenario.model_dump(),
                "anonymize": anonymize,
                "organization_id": organization_id if not anonymize else None,
                "tenant_id": tenant_id,
                "quality_score": results.quality_score if results else None,
                "usage_count": scenario.usage_count,
                "metadata": {
                    "contributed_from": "simulation_service",
                    "has_results": results is not None
                }
            }

            response = await self.client.post(
                "/api/v1/community/templates/contribute",
                json=contribution
            )
            response.raise_for_status()
            result = response.json()

            template_id = result.get("template_id")
            logger.info(f"Template contributed to community: {template_id}")
            return template_id

        except httpx.HTTPError as e:
            logger.error(f"Template contribution failed: {e}")
            return None

    async def search_community_templates(
        self,
        query: str,
        category: Optional[str] = None,
        min_quality: float = 7.0,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search community templates

        Args:
            query: Search query
            category: Optional category filter
            min_quality: Minimum quality score
            limit: Maximum results

        Returns:
            List of community templates
        """
        if not self.enabled:
            return []

        try:
            params = {
                "query": query,
                "min_quality": min_quality,
                "limit": limit
            }
            if category:
                params["category"] = category

            response = await self.client.get(
                "/api/v1/community/templates/search",
                params=params
            )
            response.raise_for_status()
            result = response.json()

            templates = result.get("templates", [])
            logger.info(f"Found {len(templates)} community templates")
            return templates

        except httpx.HTTPError as e:
            logger.warning(f"Community template search failed: {e}")
            return []

    async def get_community_template(
        self,
        template_id: str
    ) -> Optional[Dict]:
        """Get specific community template"""
        if not self.enabled:
            return None

        try:
            response = await self.client.get(
                f"/api/v1/community/templates/{template_id}"
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"Community template retrieval failed: {e}")
            return None

    async def rate_template(
        self,
        template_id: str,
        rating: float,
        feedback: Optional[str] = None
    ) -> bool:
        """Rate community template"""
        if not self.enabled:
            return False

        try:
            response = await self.client.post(
                f"/api/v1/community/templates/{template_id}/rate",
                json={"rating": rating, "feedback": feedback}
            )
            response.raise_for_status()
            return True

        except httpx.HTTPError as e:
            logger.warning(f"Template rating failed: {e}")
            return False

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict:
        """Check Community Intelligence health"""
        if not self.enabled:
            return {"status": "disabled", "connected": False}

        try:
            response = await self.client.get("/health", timeout=5.0)
            response.raise_for_status()
            return {
                "status": "healthy",
                "connected": True,
                "response": response.json()
            }
        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
