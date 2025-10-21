"""
GitHub Integration Client

Connects to GitHub Integration service for repository operations
"""

import logging
import httpx
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GitHubIntegrationClient:
    """
    Integration with GitHub Integration service

    Provides:
    - Create issues for event gaps
    - Create pull requests for fixes
    - Track issue status
    """

    def __init__(self, base_url: str = 'http://localhost:8051'):
        """
        Initialize GitHub Integration client

        Args:
            base_url: GitHub Integration service base URL
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.available = False

    async def initialize(self):
        """Check if GitHub Integration service is available"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.available = True
                logger.info(" GitHub Integration service available")
            else:
                logger.warning(f"GitHub Integration returned {response.status_code}")
        except Exception as e:
            logger.warning(f"GitHub Integration service not available: {e}")
            self.available = False

    async def create_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[str]:
        """
        Create GitHub issue

        Args:
            title: Issue title
            body: Issue description
            labels: Issue labels

        Returns:
            Issue URL or None
        """
        if not self.available:
            logger.warning("GitHub Integration service not available")
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/issues",
                json={
                    "title": title,
                    "body": body,
                    "labels": labels or []
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("issue_url")
            else:
                logger.error(f"Failed to create issue: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return None

    async def create_pull_request(self, title: str, body: str, branch: str) -> Optional[str]:
        """
        Create pull request

        Args:
            title: PR title
            body: PR description
            branch: Branch name

        Returns:
            PR URL or None
        """
        if not self.available:
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/pull-requests",
                json={
                    "title": title,
                    "body": body,
                    "branch": branch
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("pr_url")
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None

    async def get_issue_status(self, issue_number: int) -> Optional[Dict]:
        """
        Get issue status

        Args:
            issue_number: Issue number

        Returns:
            Issue status or None
        """
        if not self.available:
            return None

        try:
            response = await self.client.get(
                f"{self.base_url}/api/issues/{issue_number}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get issue status: {e}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
