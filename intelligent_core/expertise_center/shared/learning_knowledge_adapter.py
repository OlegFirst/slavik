"""
Learning Knowledge Adapter for Expertise Center

Connects expertise-center to ai-foundation/learning-knowledge API
"""

import aiohttp
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class LearningKnowledgeAdapter:
    """
    Adapter for integrating expertise-center with learning-knowledge API

    Used by domain specialists to:
    - Get domain knowledge (RTO benchmarks, threat scenarios, templates)
    - Access ISO standards and best practices
    - Retrieve similar cases for context
    """

    def __init__(self, base_url: str = "http://localhost:8030"):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def get_domain_knowledge(
        self,
        domain_type: str,
        knowledge_type: str,
        industry: Optional[str] = None,
        **filters
    ) -> Dict[str, Any]:
        """
        Get domain-specific knowledge

        Args:
            domain_type: Domain (bcm, risk, governance, hr, finance)
            knowledge_type: Type of knowledge:
                - typical_rto: RTO benchmarks
                - threat_scenarios: Industry threat scenarios
                - plan_templates: BCM plan templates
                - kpi_benchmarks: Performance KPIs
                - compliance_requirements: Regulatory requirements
            industry: Industry filter (finance, healthcare, etc)
            **filters: Additional filters

        Returns:
            Domain knowledge data
        """
        try:
            params = {"knowledge_type": knowledge_type}
            if industry:
                params["industry"] = industry
            params.update(filters)

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    f"{self.base_url}/api/knowledge/domain/{domain_type}",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            f"Domain knowledge retrieved: {domain_type}/{knowledge_type}"
                        )
                        return data
                    else:
                        logger.warning(
                            f"Domain knowledge not found: {domain_type}/{knowledge_type} "
                            f"(HTTP {response.status})"
                        )
                        return {}

        except Exception as e:
            logger.error(f"Error getting domain knowledge: {e}")
            return {}

    async def get_rto_benchmarks(
        self,
        industry: str,
        process_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get RTO benchmarks for industry

        Args:
            industry: Industry type
            process_type: Specific process (email, erp, etc)

        Returns:
            RTO benchmark data
        """
        data = await self.get_domain_knowledge(
            domain_type="bcm",
            knowledge_type="typical_rto",
            industry=industry,
            process_type=process_type
        )

        # Return benchmarks or defaults
        return data.get("typical_rto", {
            "email": "4 hours",
            "erp": "8 hours",
            "website": "2 hours",
            "crm": "4 hours"
        })

    async def get_threat_scenarios(
        self,
        industry: str,
        scenario_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get threat scenarios for industry

        Args:
            industry: Industry type
            scenario_type: Type of threat (cyber, natural, operational)

        Returns:
            List of threat scenarios
        """
        data = await self.get_domain_knowledge(
            domain_type="bcm",
            knowledge_type="threat_scenarios",
            industry=industry,
            scenario_type=scenario_type
        )

        return data.get("scenarios", [])

    async def get_plan_templates(
        self,
        plan_type: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get BCM plan templates

        Args:
            plan_type: Type of plan (incident, business_continuity, recovery)
            industry: Industry filter

        Returns:
            Plan template data
        """
        data = await self.get_domain_knowledge(
            domain_type="bcm",
            knowledge_type="plan_templates",
            plan_type=plan_type,
            industry=industry
        )

        return data.get("templates", {})

    async def get_kpi_benchmarks(
        self,
        domain: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get KPI benchmarks for domain

        Args:
            domain: Domain (bcm, hr, finance)
            industry: Industry filter

        Returns:
            KPI benchmark data
        """
        data = await self.get_domain_knowledge(
            domain_type=domain,
            knowledge_type="kpi_benchmarks",
            industry=industry
        )

        return data.get("benchmarks", {})

    async def get_compliance_requirements(
        self,
        regulation: str,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get compliance requirements

        Args:
            regulation: Regulation (gdpr, sox, hipaa, etc)
            industry: Industry filter

        Returns:
            List of compliance requirements
        """
        data = await self.get_domain_knowledge(
            domain_type="governance",
            knowledge_type="compliance_requirements",
            regulation=regulation,
            industry=industry
        )

        return data.get("requirements", [])

    async def get_iso_standard(
        self,
        standard_id: str,
        clause: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get ISO standard from learning_knowledge

        Args:
            standard_id: Standard ID (e.g., "iso/iso-22301")
            clause: Specific clause (e.g., "8.2.2")

        Returns:
            Standard data or None
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    f"{self.base_url}/standards/{standard_id}",
                    params={
                        "include_clauses": "true",
                        "include_guides": "true"
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Filter by clause if specified
                        if clause and "clauses" in data:
                            data["clauses"] = [
                                c for c in data["clauses"]
                                if c.get("clause_number") == clause
                            ]

                        return data
                    else:
                        logger.warning(f"ISO standard not found: {standard_id}")
                        return None

        except Exception as e:
            logger.error(f"Error getting ISO standard: {e}")
            return None

    async def search_cases(
        self,
        module: str,
        filters: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar cases

        Args:
            module: Workflow module
            filters: Search filters (industry, org_size, etc)
            limit: Max results

        Returns:
            List of similar cases
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                search_params = {
                    "module": module,
                    "limit": limit,
                    **filters
                }

                async with session.post(
                    f"{self.base_url}/cases/search",
                    json=search_params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Case search failed: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Error searching cases: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if learning-knowledge API is available"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    return response.status == 200

        except Exception as e:
            logger.error(f"Learning-knowledge health check failed: {e}")
            return False


# Singleton instance
_adapter: Optional[LearningKnowledgeAdapter] = None


def get_learning_knowledge_adapter(
    base_url: str = "http://localhost:8030"
) -> LearningKnowledgeAdapter:
    """Get singleton Learning Knowledge adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = LearningKnowledgeAdapter(base_url)
    return _adapter
