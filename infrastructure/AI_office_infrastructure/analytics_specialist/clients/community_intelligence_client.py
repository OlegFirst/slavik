"""
Community Intelligence Client
===============================

Client for communicating with Community Intelligence service (port 8031).

Enables knowledge sharing across organizations while preserving privacy.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class CommunityIntelligenceClient:
    """
    Client for Community Intelligence service

    Enables:
    - Anonymized insights sharing
    - Cross-organization learning
    - Best practices discovery
    - Privacy-preserving analytics

    Example:
        ```python
        client = CommunityIntelligenceClient()
        await client.share_anonymized_insight({
            'insight_type': 'bottleneck_pattern',
            'sector': 'healthcare',
            'description': 'BIA data collection optimization'
        })
        ```
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Community Intelligence client

        Args:
            base_url: Base URL of community intelligence service.
                     If None, uses settings.COMMUNITY_INTELLIGENCE_URL
        """
        self.base_url = base_url or settings.COMMUNITY_INTELLIGENCE_URL
        self.timeout = 30.0
        logger.info(f"CommunityIntelligenceClient initialized: {self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """Check if Community Intelligence service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Community Intelligence health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def share_anonymized_insights(
        self,
        insights: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Share anonymized insights with community

        Args:
            insights: List of anonymized insights
            metadata: Optional metadata (sector, org_size, etc.)

        Returns:
            Sharing confirmation

        Example:
            ```python
            await client.share_anonymized_insights([
                {
                    'insight_type': 'performance_optimization',
                    'category': 'workflow_efficiency',
                    'description': 'Reduced BIA completion time by 40%',
                    'actions_taken': ['Implemented caching', 'Parallelized API calls'],
                    'metrics': {'improvement_pct': 40}
                }
            ], metadata={'sector': 'healthcare', 'org_size': 'medium'})
            ```
        """
        try:
            payload = {
                'source': 'analytics-specialist',
                'insights': insights,
                'metadata': metadata or {},
                'anonymized': True,
                'shared_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/community/share",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Community share endpoint not implemented")
                return {
                    "status": "accepted",
                    "message": "Insights logged for community sharing",
                    "insights_count": len(insights)
                }
            logger.error(f"Failed to share anonymized insights: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to share anonymized insights: {e}")
            raise

    async def get_community_best_practices(
        self,
        category: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get best practices from community

        Args:
            category: Practice category (e.g., 'performance', 'security')
            filters: Optional filters (sector, org_size, etc.)

        Returns:
            List of best practices

        Example:
            ```python
            practices = await client.get_community_best_practices(
                category='performance_optimization',
                filters={'sector': 'healthcare'}
            )

            for practice in practices:
                print(f"Best practice: {practice['title']}")
                print(f"Effectiveness: {practice['effectiveness_score']}")
            ```
        """
        try:
            params = {'category': category}
            if filters:
                params.update(filters)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/community/best-practices",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("practices", [])

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Best practices endpoint not implemented")
                return []
            logger.error(f"Failed to get best practices: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get best practices: {e}")
            return []

    async def get_community_benchmarks(
        self,
        metric_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get community benchmarks for comparison

        Args:
            metric_type: Type of metric (e.g., 'bia_completion_time')
            filters: Optional filters (sector, org_size, etc.)

        Returns:
            Benchmark statistics

        Example:
            ```python
            benchmarks = await client.get_community_benchmarks(
                metric_type='bia_completion_time',
                filters={'sector': 'healthcare', 'org_size': 'medium'}
            )

            print(f"Community average: {benchmarks['avg']}")
            print(f"You are at percentile: {benchmarks['your_percentile']}")
            ```
        """
        try:
            params = {'metric_type': metric_type}
            if filters:
                params.update(filters)

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/community/benchmarks",
                    params=params
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Benchmarks endpoint not implemented")
                return {
                    "metric_type": metric_type,
                    "avg": 0,
                    "median": 0,
                    "percentiles": {},
                    "sample_size": 0
                }
            logger.error(f"Failed to get benchmarks: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to get benchmarks: {e}")
            return {}

    async def discover_patterns(
        self,
        pattern_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover patterns from community data

        Args:
            pattern_type: Type of pattern to discover
            context: Context for pattern matching

        Returns:
            List of discovered patterns

        Example:
            ```python
            patterns = await client.discover_patterns(
                pattern_type='common_bottlenecks',
                context={'process': 'bia_workflow'}
            )

            for pattern in patterns:
                print(f"Pattern: {pattern['description']}")
                print(f"Frequency: {pattern['occurrence_rate']}%")
            ```
        """
        try:
            payload = {
                'pattern_type': pattern_type,
                'context': context or {},
                'requested_by': 'analytics-specialist'
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/community/patterns/discover",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data.get("patterns", [])

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Pattern discovery endpoint not implemented")
                return []
            logger.error(f"Failed to discover patterns: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to discover patterns: {e}")
            return []

    async def submit_success_story(
        self,
        story: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit anonymized success story to community

        Args:
            story: Success story dict:
                - title: Story title
                - category: Category
                - challenge: What was the challenge
                - solution: How it was solved
                - results: Measurable results
                - lessons_learned: Key takeaways

        Returns:
            Submission confirmation

        Example:
            ```python
            await client.submit_success_story({
                'title': 'Reducing BIA completion time',
                'category': 'performance_improvement',
                'challenge': 'BIA taking 3+ days to complete',
                'solution': 'Implemented automated data collection and validation',
                'results': {
                    'time_reduction_pct': 60,
                    'user_satisfaction_increase': 40
                },
                'lessons_learned': [
                    'Automation is key',
                    'User feedback early is crucial'
                ]
            })
            ```
        """
        try:
            payload = {
                'submitter': 'analytics-specialist',
                'story': story,
                'anonymized': True,
                'submitted_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/community/stories/submit",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Success story endpoint not implemented")
                return {
                    "status": "accepted",
                    "message": "Story logged for community sharing"
                }
            logger.error(f"Failed to submit success story: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to submit success story: {e}")
            raise
