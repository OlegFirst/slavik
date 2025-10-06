"""
AI Orchestrator Client
======================

Client for interacting with AI Orchestrator service.
"""

import logging
from typing import Dict, Any, Optional
import httpx
from config import config
from models import AIDeploymentStrategy

logger = logging.getLogger(__name__)


class AIClient:
    """
    Client for AI Orchestrator integration.

    Provides deployment strategy recommendations and analysis.
    """

    def __init__(self):
        self.base_url = config.AI_ORCHESTRATOR_URL
        self.timeout = config.AI_ORCHESTRATOR_TIMEOUT

    async def get_deployment_strategy(
        self,
        services: list,
        context: Dict[str, Any]
    ) -> Optional[AIDeploymentStrategy]:
        """
        Request AI-optimized deployment strategy.

        Args:
            services: List of services to deploy
            context: Deployment context (current state, history, etc.)

        Returns:
            AIDeploymentStrategy or None if AI unavailable
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/deployment/orchestrate",
                    json={
                        "services": services,
                        "context": context
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return AIDeploymentStrategy(**data.get("result", {}))
                else:
                    logger.warning(
                        f"AI Orchestrator returned {response.status_code}: {response.text}"
                    )
                    return None

        except httpx.TimeoutException:
            logger.warning("AI Orchestrator request timed out")
            return None
        except Exception as e:
            logger.error(f"Failed to get AI deployment strategy: {e}")
            return None

    async def analyze_deployment_result(
        self,
        deployment_id: str,
        result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Send deployment results to AI for analysis and learning.

        Args:
            deployment_id: Deployment ID
            result: Deployment result data

        Returns:
            Analysis insights or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/claude/analyze-deployment",
                    json={
                        "deployment_id": deployment_id,
                        "result": result
                    }
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"AI analysis failed: {response.status_code}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Failed to analyze deployment with AI: {e}")
            return None

    async def report_service_issue(
        self,
        service_name: str,
        issue_type: str,
        details: Dict[str, Any]
    ):
        """
        Report service issue to AI Orchestrator for alerting.

        Args:
            service_name: Name of service with issue
            issue_type: Type of issue (down, slow, error)
            details: Additional details
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    f"{self.base_url}/alerts/service-issue",
                    json={
                        "service": service_name,
                        "issue_type": issue_type,
                        "details": details
                    }
                )
                logger.info(f"Reported {issue_type} issue for {service_name} to AI")

        except Exception as e:
            logger.error(f"Failed to report service issue: {e}")

    async def health_check(self) -> bool:
        """
        Check if AI Orchestrator is available.

        Returns:
            True if available, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False
