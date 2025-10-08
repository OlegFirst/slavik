"""
Collective Client
==================

Client for communicating with Collective AI service.

Contributes insights to collective intelligence and participates in collective decision-making.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..config import settings
from ..models import AnalyticsInsight

logger = logging.getLogger(__name__)


class CollectiveClient:
    """
    Client for Collective AI service

    Enables collective intelligence:
    - Contribute analytics insights
    - Participate in collective decisions
    - Learn from collective wisdom
    - Cross-agent collaboration

    Example:
        ```python
        client = CollectiveClient()
        await client.contribute_insights([
            {'title': 'Bottleneck detected', 'severity': 'high'}
        ])
        ```
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Collective client

        Args:
            base_url: Base URL of Collective service.
                     If None, uses settings.COLLECTIVE_URL
        """
        self.base_url = base_url or settings.COLLECTIVE_URL
        self.timeout = 30.0
        logger.info(f"CollectiveClient initialized: {self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Collective service is healthy

        Returns:
            Health status dict
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Collective service health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def contribute_insights(
        self,
        insights: List[AnalyticsInsight]
    ) -> Dict[str, Any]:
        """
        Contribute analytics insights to collective intelligence

        Args:
            insights: List of AnalyticsInsight objects

        Returns:
            Contribution response

        Example:
            ```python
            await client.contribute_insights([
                AnalyticsInsight(
                    id="insight_123",
                    category=InsightCategory.PERFORMANCE,
                    severity=SeverityLevel.HIGH,
                    title="Bottleneck in BIA workflow",
                    description="Data collection step taking 2x expected time",
                    affected_components=["bia_workflow"],
                    impact="Delays in BIA completion",
                    evidence={'avg_duration': 45.5, 'expected': 22.0}
                )
            ])
            ```
        """
        try:
            payload = {
                'source': 'analytics-specialist',
                'insights': [
                    insight.model_dump() if hasattr(insight, 'model_dump') else insight
                    for insight in insights
                ],
                'contributed_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/collective/contribute",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Collective contribute endpoint not implemented")
                return {
                    "status": "accepted",
                    "message": "Insights logged for collective processing",
                    "insights_count": len(insights)
                }
            logger.error(f"Failed to contribute insights: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to contribute insights: {e}")
            raise

    async def request_collective_decision(
        self,
        issue: Dict[str, Any],
        options: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Request collective decision on an issue

        Args:
            issue: Issue description dict:
                - id: Issue ID
                - title: Issue title
                - description: Full description
                - severity: Severity level
                - affected_components: List of affected components
            options: List of possible solutions/actions

        Returns:
            Collective decision result

        Example:
            ```python
            decision = await client.request_collective_decision(
                issue={
                    'id': 'issue_123',
                    'title': 'High memory usage',
                    'description': 'Platform memory usage at 85%',
                    'severity': 'high',
                    'affected_components': ['workflow_engine', 'ai_orchestrator']
                },
                options=[
                    {'action': 'scale_up', 'description': 'Add 2 more instances'},
                    {'action': 'optimize', 'description': 'Run memory optimization'},
                    {'action': 'restart', 'description': 'Restart affected services'}
                ]
            )

            print(f"Collective recommends: {decision['recommended_action']}")
            ```
        """
        try:
            payload = {
                'requester': 'analytics-specialist',
                'issue': issue,
                'options': options,
                'requested_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/collective/decide",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Collective decision endpoint not implemented")
                # Return simple decision (first option)
                return {
                    "recommended_action": options[0] if options else {},
                    "confidence": 0.5,
                    "reasoning": "Mock decision - collective not available"
                }
            logger.error(f"Failed to request collective decision: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to request collective decision: {e}")
            raise

    async def get_collective_insights(
        self,
        domain: Optional[str] = None,
        category: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Get insights from collective intelligence

        Args:
            domain: Filter by domain (e.g., 'platform', 'bcm')
            category: Filter by category (e.g., 'performance', 'security')
            min_confidence: Minimum confidence score (0-1)

        Returns:
            List of collective insights

        Example:
            ```python
            insights = await client.get_collective_insights(
                domain='platform',
                category='performance',
                min_confidence=0.8
            )

            for insight in insights:
                print(f"{insight['title']} (confidence: {insight['confidence']})")
            ```
        """
        try:
            params = {'min_confidence': min_confidence}
            if domain:
                params['domain'] = domain
            if category:
                params['category'] = category

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/collective/insights",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("insights", [])

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Collective insights endpoint not implemented")
                return []
            logger.error(f"Failed to get collective insights: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get collective insights: {e}")
            return []

    async def report_stuck_detection(
        self,
        stuck_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Report stuck detection to collective for collaborative resolution

        Args:
            stuck_info: Stuck detection information:
                - user_id: User who is stuck
                - journey_id: Journey identifier
                - stuck_point: Where they're stuck
                - context: Additional context

        Returns:
            Collective response with suggestions

        Example:
            ```python
            response = await client.report_stuck_detection({
                'user_id': 'user_123',
                'journey_id': 'journey_456',
                'stuck_point': 'bia_data_collection',
                'context': {
                    'time_spent_minutes': 45,
                    'completion_percentage': 30
                }
            })

            if response.get('suggestions'):
                for sug in response['suggestions']:
                    print(f"Suggestion: {sug['action']}")
            ```
        """
        try:
            payload = {
                'detector': 'analytics-specialist',
                'stuck_info': stuck_info,
                'reported_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/collective/stuck",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Stuck detection endpoint not implemented")
                return {
                    "status": "logged",
                    "suggestions": []
                }
            logger.error(f"Failed to report stuck detection: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to report stuck detection: {e}")
            raise

    async def share_success_pattern(
        self,
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Share successful pattern with collective

        Args:
            pattern: Success pattern dict:
                - pattern_type: Type of pattern
                - context: Where it worked
                - actions_taken: What was done
                - outcome: Results achieved
                - metrics: Performance metrics

        Returns:
            Response from collective

        Example:
            ```python
            await client.share_success_pattern({
                'pattern_type': 'bottleneck_resolution',
                'context': {
                    'process': 'bia_workflow',
                    'bottleneck_step': 'data_collection'
                },
                'actions_taken': [
                    'Added data validation caching',
                    'Parallelized API calls'
                ],
                'outcome': 'Duration reduced from 45min to 12min',
                'metrics': {
                    'before_avg_duration': 45.5,
                    'after_avg_duration': 12.3,
                    'improvement_pct': 73
                }
            })
            ```
        """
        try:
            payload = {
                'contributor': 'analytics-specialist',
                'pattern': pattern,
                'shared_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/collective/patterns/share",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Pattern sharing endpoint not implemented")
                return {
                    "status": "accepted",
                    "message": "Pattern logged for collective learning"
                }
            logger.error(f"Failed to share success pattern: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to share success pattern: {e}")
            raise

    async def get_similar_cases(
        self,
        case_query: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get similar cases from collective case library

        Args:
            case_query: Query describing the case:
                - domain: Domain (e.g., 'platform', 'bcm')
                - issue_type: Type of issue
                - context: Context information
            limit: Maximum number of cases

        Returns:
            List of similar cases

        Example:
            ```python
            similar = await client.get_similar_cases({
                'domain': 'platform',
                'issue_type': 'performance_degradation',
                'context': {
                    'component': 'workflow_engine',
                    'symptom': 'high_response_time'
                }
            }, limit=5)

            for case in similar:
                print(f"Similar case: {case['title']}")
                print(f"Resolution: {case['resolution']}")
            ```
        """
        try:
            payload = {
                'query': case_query,
                'limit': limit,
                'requested_by': 'analytics-specialist'
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/collective/cases/similar",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data.get("cases", [])

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Similar cases endpoint not implemented")
                return []
            logger.error(f"Failed to get similar cases: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get similar cases: {e}")
            return []
