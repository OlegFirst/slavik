"""
Knowledge Center Integration Client

REAL integration with Knowledge Center for:
- Knowledge storage and retrieval
- Best practices management
- Standards and guidelines access
- Organizational learning repository
"""

import logging
from typing import Dict, List, Optional, Any
import httpx

from models.pydantic_models import SimulationResult, TaskSpecification
from config.settings import Settings

logger = logging.getLogger(__name__)


class KnowledgeCenterClient:
    """
    Knowledge Center integration client

    Provides:
    - Store simulation learnings as knowledge
    - Retrieve relevant standards and guidelines
    - Access best practices repository
    - Manage organizational knowledge base
    """

    def __init__(self, settings: Settings):
        """
        Initialize Knowledge Center client

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.base_url = settings.knowledge_center_url
        self.enabled = settings.knowledge_center_enabled
        self.timeout = 30.0

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # KNOWLEDGE STORAGE
    # ========================================================================

    async def store_simulation_knowledge(
        self,
        simulation_id: str,
        results: SimulationResult,
        specification: TaskSpecification,
        organization_id: str,
        tenant_id: str
    ) -> Optional[str]:
        """
        Store simulation results as organizational knowledge

        Creates knowledge entry with:
        - Lessons learned
        - Best practices identified
        - Recommendations
        - Metrics and outcomes

        Args:
            simulation_id: Simulation ID
            results: Simulation results
            specification: Original specification
            organization_id: Organization ID
            tenant_id: Tenant ID

        Returns:
            Knowledge entry ID or None
        """
        if not self.enabled:
            return None

        try:
            knowledge_entry = {
                "title": f"Simulation Knowledge: {specification.goal[:50]}",
                "description": specification.goal,
                "type": "simulation_learning",
                "source_id": simulation_id,
                "organization_id": organization_id,
                "tenant_id": tenant_id,

                "content": {
                    "lessons_learned": results.lessons_learned,
                    "recommendations": results.recommendations,
                    "best_practices": self._extract_best_practices(results),
                    "improvement_areas": results.improvement_areas,
                    "success_factors": self._extract_success_factors(results)
                },

                "metrics": {
                    "success_rate": results.overall_success_rate,
                    "quality_score": results.quality_score,
                    "kpis_achieved": results.kpis_achieved
                },

                "context": {
                    "scenario_category": specification.context.get("category"),
                    "complexity_level": results.complexity_level,
                    "participants": len(results.participant_performance)
                },

                "tags": self._generate_knowledge_tags(specification, results),
                "metadata": {
                    "created_from": "simulation",
                    "auto_generated": True
                }
            }

            response = await self.client.post(
                "/api/v1/knowledge/entries",
                json=knowledge_entry
            )
            response.raise_for_status()
            result = response.json()

            entry_id = result.get("id")
            logger.info(f"Knowledge entry created: {entry_id}")
            return entry_id

        except httpx.HTTPError as e:
            logger.error(f"Knowledge storage failed: {e}")
            return None

    async def retrieve_knowledge(
        self,
        query: str,
        knowledge_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve relevant knowledge

        Args:
            query: Search query
            knowledge_type: Filter by type
            limit: Maximum results

        Returns:
            List of knowledge entries
        """
        if not self.enabled:
            return []

        try:
            params = {
                "query": query,
                "limit": limit
            }
            if knowledge_type:
                params["type"] = knowledge_type

            response = await self.client.get(
                "/api/v1/knowledge/search",
                params=params
            )
            response.raise_for_status()
            result = response.json()

            return result.get("entries", [])

        except httpx.HTTPError as e:
            logger.warning(f"Knowledge retrieval failed: {e}")
            return []

    # ========================================================================
    # STANDARDS & GUIDELINES
    # ========================================================================

    async def get_iso_standard(
        self,
        standard_id: str,
        clause: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Retrieve ISO standard information

        Args:
            standard_id: Standard ID (e.g., "ISO-22301")
            clause: Specific clause (e.g., "8.4")

        Returns:
            Standard information or None
        """
        if not self.enabled:
            return None

        try:
            endpoint = f"/api/v1/standards/{standard_id}"
            if clause:
                endpoint += f"/clauses/{clause}"

            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"Standard retrieval failed: {e}")
            return None

    async def get_best_practices(
        self,
        domain: str,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve best practices for domain

        Args:
            domain: Domain area
            category: Optional category filter

        Returns:
            List of best practices
        """
        if not self.enabled:
            return []

        try:
            params = {"domain": domain}
            if category:
                params["category"] = category

            response = await self.client.get(
                "/api/v1/best-practices",
                params=params
            )
            response.raise_for_status()
            result = response.json()

            return result.get("best_practices", [])

        except httpx.HTTPError as e:
            logger.warning(f"Best practices retrieval failed: {e}")
            return []

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict:
        """Check Knowledge Center health"""
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

    # Helper methods
    def _extract_best_practices(self, results: SimulationResult) -> List[str]:
        """Extract best practices from results"""
        practices = []
        if results.overall_success_rate >= 0.8:
            practices.append("High success rate achieved through effective planning")
        return practices

    def _extract_success_factors(self, results: SimulationResult) -> List[str]:
        """Extract success factors"""
        factors = []
        if results.kpis_achieved:
            factors.append(f"Achieved {len(results.kpis_achieved)} KPIs")
        return factors

    def _generate_knowledge_tags(
        self,
        specification: TaskSpecification,
        results: SimulationResult
    ) -> List[str]:
        """Generate tags for knowledge entry"""
        tags = ["simulation", "learning"]
        tags.append(f"engine_{results.engine_used}")
        return tags
