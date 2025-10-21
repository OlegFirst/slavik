"""
MIO Manager Integration

Enhanced integration with MIO Manager for platform coordination
"""

import logging
import httpx
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MioManagerIntegration:
    """
    Integration with MIO Manager

    Provides:
    - Report insights to platform coordinator
    - Request task execution
    - Get coordination context
    """

    def __init__(self, base_url: str = 'http://localhost:8046'):
        """
        Initialize MIO Manager integration

        Args:
            base_url: MIO Manager base URL
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.available = False

    async def initialize(self):
        """Check if MIO Manager is available"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.available = True
                logger.info(" MIO Manager available")
            else:
                logger.warning(f"MIO Manager returned {response.status_code}")
        except Exception as e:
            logger.warning(f"MIO Manager not available: {e}")
            self.available = False

    async def report_insights(self, insights: Dict) -> bool:
        """
        Report insights to MIO Manager

        Args:
            insights: Analysis insights

        Returns:
            Success status
        """
        if not self.available:
            logger.warning("MIO Manager not available")
            return False

        try:
            response = await self.client.post(
                f"{self.base_url}/api/insights",
                json={
                    "source": "ai-event-manager",
                    "type": "event_analysis",
                    "insights": insights
                }
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Failed to report insights: {e}")
            return False

    async def request_task(self, task: Dict) -> Optional[str]:
        """
        Request task execution through MIO Manager

        Args:
            task: Task details

        Returns:
            Task ID or None
        """
        if not self.available:
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/tasks",
                json={
                    "source": "ai-event-manager",
                    "task": task
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("task_id")
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to request task: {e}")
            return None

    async def get_context(self) -> Optional[Dict]:
        """
        Get coordination context from MIO Manager

        Returns:
            Context data or None
        """
        if not self.available:
            return None

        try:
            response = await self.client.get(
                f"{self.base_url}/api/context"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
