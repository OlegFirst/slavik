"""
Learning Knowledge Client for Workflow Intelligence

Connects workflow_intelligence to ai-foundation/learning-knowledge API
"""

import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class LearningKnowledgeClient:
    """
    Client for integrating with learning-knowledge API

    Used by workflow_intelligence to:
    - Store completed workflow cases
    - Retrieve similar cases for recommendations
    - Get ISO standards and best practices
    - Trigger virtuous learning cycle
    """

    def __init__(self, base_url: str = "http://localhost:8030"):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def store_workflow_case(
        self,
        workflow_data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Store completed workflow case in learning-knowledge

        Triggers virtuous cycle:
        - Case saved to knowledge base
        - Pattern detection
        - Lesson creation (if successful)

        Args:
            workflow_data: {
                'case_id': str,
                'workflow_type': str (bia, risk, etc),
                'success_score': float,
                'steps_completed': List[Dict],
                'decisions_made': List[Dict],
                'outcomes': Dict,
                'metadata': Dict
            }
            tenant_id: Tenant identifier

        Returns:
            Result from virtuous cycle
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/cross-learning/virtuous-cycle/workflow",
                    json=workflow_data,
                    headers={"X-Tenant-ID": tenant_id}
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        logger.info(
                            f"Workflow case stored: {workflow_data.get('case_id')}. "
                            f"Lesson created: {result.get('lesson_created', False)}"
                        )
                        return result
                    else:
                        logger.warning(f"Failed to store case: {response.status}")
                        return {"error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Error storing workflow case: {e}")
            return {"error": str(e)}

    async def find_similar_cases(
        self,
        module: str,
        org_context: Dict[str, Any],
        current_stage: Optional[str] = None,
        limit: int = 5,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar workflow cases from learning-knowledge

        Args:
            module: Workflow module (bia, risk, planning, etc)
            org_context: {
                'industry': str,
                'size': str,
                'maturity_level': str
            }
            current_stage: Current workflow stage
            limit: Max number of cases
            tenant_id: Tenant ID (None for cross-tenant learning)

        Returns:
            List of similar cases with metadata
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                headers = {}
                if tenant_id:
                    headers["X-Tenant-ID"] = tenant_id

                async with session.post(
                    f"{self.base_url}/cases/search",
                    json={
                        "module": module,
                        "industry": org_context.get("industry"),
                        "org_size": org_context.get("size"),
                        "maturity_level": org_context.get("maturity_level"),
                        "limit": limit
                    },
                    headers=headers
                ) as response:
                    if response.status == 200:
                        cases = await response.json()
                        logger.info(f"Found {len(cases)} similar cases for {module}")
                        return cases
                    else:
                        logger.warning(f"Case search failed: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Error finding similar cases: {e}")
            return []

    async def get_iso_standard(
        self,
        standard_id: str,
        include_clauses: bool = True,
        include_guides: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get ISO standard from learning-knowledge

        Args:
            standard_id: Standard ID (e.g., "iso/iso-22301")
            include_clauses: Include clause details
            include_guides: Include implementation guides

        Returns:
            Standard data or None
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                params = {
                    "include_clauses": str(include_clauses).lower(),
                    "include_guides": str(include_guides).lower()
                }

                async with session.get(
                    f"{self.base_url}/standards/{standard_id}",
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Standard not found: {standard_id}")
                        return None

        except Exception as e:
            logger.error(f"Error getting ISO standard: {e}")
            return None

    async def report_pattern(
        self,
        pattern_data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Report detected pattern to learning-knowledge

        Triggers virtuous cycle:
        - Pattern recorded
        - Article creation (if threshold met)

        Args:
            pattern_data: {
                'pattern_name': str,
                'description': str,
                'occurrence_count': int,
                'confidence': float,
                'severity': str,
                'recommended_actions': List[str],
                'affected_processes': List[str],
                'context': Dict
            }
            tenant_id: Tenant identifier

        Returns:
            Result from virtuous cycle
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/cross-learning/virtuous-cycle/pattern",
                    json=pattern_data,
                    headers={"X-Tenant-ID": tenant_id}
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        logger.info(
                            f"Pattern reported: {pattern_data.get('pattern_name')}. "
                            f"Article created: {result.get('article_created', False)}"
                        )
                        return result
                    else:
                        logger.warning(f"Failed to report pattern: {response.status}")
                        return {"error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"Error reporting pattern: {e}")
            return {"error": str(e)}

    async def get_benchmarks(
        self,
        module: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get benchmarks from learning-knowledge

        Args:
            module: Workflow module
            industry: Industry filter

        Returns:
            Benchmark data
        """
        try:
            # TODO: Implement benchmarks endpoint in learning-knowledge
            # For now, return empty
            logger.info(f"Benchmarks requested for {module} (not yet implemented)")
            return {
                "module": module,
                "industry": industry,
                "benchmarks": {}
            }

        except Exception as e:
            logger.error(f"Error getting benchmarks: {e}")
            return {"benchmarks": {}}

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
_client: Optional[LearningKnowledgeClient] = None


def get_learning_knowledge_client(base_url: str = "http://localhost:8030") -> LearningKnowledgeClient:
    """Get singleton Learning Knowledge client instance"""
    global _client
    if _client is None:
        _client = LearningKnowledgeClient(base_url)
    return _client
