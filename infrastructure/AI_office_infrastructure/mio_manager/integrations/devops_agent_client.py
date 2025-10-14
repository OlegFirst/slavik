#!/usr/bin/env python3
"""
DevOps Agent Client

Integration client for MIO Manager ↔ DevOps Agent communication
"""

import httpx
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DevOpsAgentClient:
    """Client for DevOps Agent integration"""

    def __init__(self, base_url: str = "http://localhost:8060"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def health_check(self) -> Dict:
        """Check DevOps Agent health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"DevOps Agent health check failed: {e}")
            return {}

    async def trigger_scan(self, scan_type: str = "full") -> Dict:
        """
        Trigger infrastructure scan

        Args:
            scan_type: 'full', 'events', 'containers', 'deployments'

        Returns:
            Scan results
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/scan",
                json={"scan_type": scan_type}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to trigger scan: {e}")
            return {"status": "error", "error": str(e)}

    async def get_latest_report(self) -> Dict:
        """Get latest DevOps report"""
        try:
            response = await self.client.get(f"{self.base_url}/reports/latest")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get latest report: {e}")
            return {}

    async def get_report_history(self, limit: int = 10) -> list:
        """Get report history"""
        try:
            response = await self.client.get(
                f"{self.base_url}/reports/history",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get report history: {e}")
            return []

    async def get_status(self) -> Dict:
        """Get DevOps Agent status"""
        try:
            response = await self.client.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"status": "unknown", "error": str(e)}

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
