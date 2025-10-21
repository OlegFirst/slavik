"""
DevOps Agent Integration

Connects to DevOps Agent for infrastructure scanning
"""

import logging
import httpx
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DevOpsAgentIntegration:
    """
    Integration with DevOps Agent

    Provides:
    - Infrastructure scanning
    - Event architecture analysis
    - Container and deployment monitoring
    """

    def __init__(self, base_url: str = 'http://localhost:8050', project_root: str = '/Users/MD/AI-Platform-ISO'):
        """
        Initialize DevOps Agent integration

        Args:
            base_url: DevOps Agent API base URL
            project_root: Project root path for scanning
        """
        self.base_url = base_url
        self.project_root = project_root
        self.client = httpx.AsyncClient(timeout=60.0)
        self.available = False

    async def initialize(self):
        """Check if DevOps Agent is available"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.available = True
                logger.info(" DevOps Agent available")
            else:
                logger.warning(f"DevOps Agent returned {response.status_code}")
        except Exception as e:
            logger.warning(f"DevOps Agent not available: {e}")
            self.available = False

    async def request_scan(self, scan_type: str = "events") -> Optional[Dict]:
        """
        Request infrastructure scan

        Args:
            scan_type: Type of scan (events, containers, deployments, full)

        Returns:
            Scan results or None
        """
        if not self.available:
            logger.warning("DevOps Agent not available")
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/scan",
                json={
                    "scan_type": scan_type,
                    "project_root": self.project_root
                },
                timeout=120.0
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Scan failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Failed to request scan: {e}")
            return None

    async def get_scan_results(self, scan_id: str) -> Optional[Dict]:
        """
        Get scan results by ID

        Args:
            scan_id: Scan identifier

        Returns:
            Scan results or None
        """
        if not self.available:
            return None

        try:
            response = await self.client.get(
                f"{self.base_url}/api/scan/{scan_id}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get scan results: {e}")
            return None

    async def request_auto_fix(self, issue_id: str) -> bool:
        """
        Request auto-fix for detected issue

        Args:
            issue_id: Issue identifier

        Returns:
            Success status
        """
        if not self.available:
            return False

        try:
            response = await self.client.post(
                f"{self.base_url}/api/auto-fix",
                json={"issue_id": issue_id}
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Auto-fix request failed: {e}")
            return False

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
