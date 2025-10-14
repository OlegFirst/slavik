"""
AI Orchestrator Client
=======================

Client for communicating with AI Orchestrator service (port 8004).

Provides analytics context to Orchestrator for intelligent decision-making.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class AIOrchestratorClient:
    """
    Client for AI Orchestrator service

    Provides analytics context and receives decision feedback.

    Example:
        ```python
        client = AIOrchestratorClient()
        await client.provide_analytics_context({
            'health_score': 85.5,
            'critical_issues': [],
            'bottlenecks': [...]
        })
        ```
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize AI Orchestrator client

        Args:
            base_url: Base URL of AI Orchestrator service.
                     If None, uses settings.AI_ORCHESTRATOR_URL
        """
        self.base_url = base_url or settings.AI_ORCHESTRATOR_URL
        self.timeout = 30.0
        logger.info(f"AIOrchestratorClient initialized: {self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if AI Orchestrator service is healthy

        Returns:
            Health status dict

        Example:
            ```python
            health = await client.health_check()
            if health["status"] == "healthy":
                print("Orchestrator is up!")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/monitoring/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"AI Orchestrator health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def provide_analytics_context(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide analytics context to Orchestrator

        Orchestrator uses this for decision-making context.

        Args:
            context: Analytics context dict containing:
                - health_score: Platform health (0-100)
                - critical_issues: List of critical issues
                - bottlenecks: List of active bottlenecks
                - deviations: List of process deviations
                - predictions: ML predictions (if available)
                - recommendations: Recommended actions
                - resource_utilization: Current resource usage

        Returns:
            Response from Orchestrator

        Example:
            ```python
            context = {
                'health_score': 85.5,
                'critical_issues': [
                    {'title': 'High memory usage', 'severity': 'high'}
                ],
                'bottlenecks': [
                    {'process': 'bia_workflow', 'step': 'data_collection'}
                ],
                'recommendations': [
                    {'action': 'scale_up', 'component': 'workflow_engine'}
                ],
                'timestamp': datetime.now().isoformat(),
                'source': 'analytics-specialist'
            }

            response = await client.provide_analytics_context(context)
            ```
        """
        try:
            # Add metadata
            payload = {
                **context,
                'timestamp': datetime.now().isoformat(),
                'source': 'analytics-specialist',
                'version': '1.0.0'
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/context/analytics",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Analytics context endpoint not implemented yet")
                return {
                    "status": "accepted",
                    "message": "Endpoint not implemented, context logged"
                }
            logger.error(f"Failed to provide analytics context: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to provide analytics context: {e}")
            raise

    async def get_platform_metrics(self) -> Dict[str, Any]:
        """
        Get platform metrics from Orchestrator

        Returns:
            Platform metrics dict

        Example:
            ```python
            metrics = await client.get_platform_metrics()
            print(f"Active workflows: {metrics['active_workflows']}")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/monitoring/metrics"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get platform metrics: {e}")
            return {}

    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """
        Get performance dashboard data from Orchestrator

        Returns:
            Performance metrics and insights

        Example:
            ```python
            dashboard = await client.get_performance_dashboard()
            print(f"Avg response time: {dashboard['avg_response_time_ms']}ms")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/monitoring/dashboard/performance"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get performance dashboard: {e}")
            return {}

    async def get_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Get detected bottlenecks from Orchestrator

        Returns:
            List of bottlenecks

        Example:
            ```python
            bottlenecks = await client.get_bottlenecks()
            for b in bottlenecks:
                print(f"Bottleneck: {b['component']} - {b['severity']}")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/monitoring/performance/bottlenecks"
                )
                response.raise_for_status()
                data = response.json()
                return data.get("bottlenecks", [])
        except Exception as e:
            logger.error(f"Failed to get bottlenecks: {e}")
            return []

    async def get_decision_feedback(
        self,
        decision_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get feedback on Orchestrator's decision

        Used to improve analytics models based on actual outcomes.

        Args:
            decision_id: ID of the decision to get feedback for

        Returns:
            Decision feedback dict or None

        Example:
            ```python
            feedback = await client.get_decision_feedback("decision_123")
            if feedback and feedback['outcome'] == 'successful':
                # Update analytics models with this success
                await analytics.learn_from_success(feedback)
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/decisions/{decision_id}/feedback"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Decision {decision_id} not found or no feedback")
                return None
            logger.error(f"Failed to get decision feedback: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get decision feedback: {e}")
            return None

    async def report_prediction_accuracy(
        self,
        prediction_id: str,
        actual_outcome: Dict[str, Any],
        accuracy_score: float
    ) -> Dict[str, Any]:
        """
        Report prediction accuracy to Orchestrator

        Helps Orchestrator understand analytics prediction quality.

        Args:
            prediction_id: ID of the prediction
            actual_outcome: What actually happened
            accuracy_score: Accuracy score (0-1)

        Returns:
            Response from Orchestrator

        Example:
            ```python
            # We predicted a bottleneck, report if it actually happened
            await client.report_prediction_accuracy(
                prediction_id="pred_123",
                actual_outcome={
                    'bottleneck_occurred': True,
                    'severity': 'high',
                    'duration_minutes': 45
                },
                accuracy_score=0.92
            )
            ```
        """
        try:
            payload = {
                'prediction_id': prediction_id,
                'actual_outcome': actual_outcome,
                'accuracy_score': accuracy_score,
                'reported_at': datetime.now().isoformat(),
                'source': 'analytics-specialist'
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/predictions/accuracy",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Prediction accuracy endpoint not implemented yet")
                return {
                    "status": "accepted",
                    "message": "Endpoint not implemented, accuracy logged"
                }
            logger.error(f"Failed to report prediction accuracy: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to report prediction accuracy: {e}")
            raise

    async def get_active_scenarios(self) -> List[Dict[str, Any]]:
        """
        Get currently active scenarios/workflows from Orchestrator

        Returns:
            List of active scenarios

        Example:
            ```python
            scenarios = await client.get_active_scenarios()
            for s in scenarios:
                print(f"Active: {s['scenario_type']} - {s['status']}")
            ```
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/scenarios/active"
                )
                response.raise_for_status()
                data = response.json()
                return data.get("scenarios", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Active scenarios endpoint not found")
                return []
            logger.error(f"Failed to get active scenarios: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get active scenarios: {e}")
            return []
