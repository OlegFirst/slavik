"""
GitHub API Client
================

Full-featured GitHub API client with retry logic and rate limiting.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from config import config
from auth import GitHubAuth
from models import GitHubAPIRequest

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """GitHub API error"""
    pass


class RateLimitExceeded(Exception):
    """GitHub API rate limit exceeded"""
    pass


class GitHubClient:
    """
    GitHub API client with:
    - Installation token auth
    - Rate limiting
    - Retry with exponential backoff
    - Request tracking
    """

    def __init__(self, auth: GitHubAuth):
        self.auth = auth
        self.base_url = config.GITHUB_API_URL
        self.api_version = config.GITHUB_API_VERSION
        self.requests_log: List[GitHubAPIRequest] = []

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        installation_id: int,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated GitHub API request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            installation_id: Installation ID for auth
            json_data: JSON body (optional)
            params: Query parameters (optional)

        Returns:
            Response data
        """
        # Get installation token
        token_data = await self.auth.get_installation_token(installation_id)

        headers = {
            "Authorization": f"Bearer {token_data.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.api_version
        }

        url = f"{self.base_url}{endpoint}"
        start_time = datetime.utcnow()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params
                )

                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

                # Track request
                api_request = GitHubAPIRequest(
                    method=method,
                    endpoint=endpoint,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    rate_limit_remaining=int(response.headers.get('X-RateLimit-Remaining', 0))
                )
                self.requests_log.append(api_request)

                # Check rate limit
                if response.status_code == 403:
                    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
                    if rate_limit_remaining == '0':
                        logger.error("GitHub API rate limit exceeded")
                        raise RateLimitExceeded("GitHub API rate limit exceeded")

                # Check for errors
                if response.status_code >= 400:
                    error_msg = f"GitHub API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    api_request.error = error_msg
                    raise GitHubAPIError(error_msg)

                return response.json() if response.text else {}

        except httpx.TimeoutException as e:
            logger.error(f"GitHub API timeout: {endpoint}")
            raise GitHubAPIError(f"Request timeout: {endpoint}")
        except Exception as e:
            logger.error(f"GitHub API request failed: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, GitHubAPIError)),
        reraise=True
    )
    async def get_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        installation_id: int
    ) -> Dict[str, Any]:
        """Get pull request details"""
        return await self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/pulls/{pr_number}",
            installation_id
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, GitHubAPIError)),
        reraise=True
    )
    async def create_pr_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        installation_id: int
    ) -> Dict[str, Any]:
        """Create comment on pull request"""
        return await self._make_request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{pr_number}/comments",
            installation_id,
            json_data={"body": body}
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, GitHubAPIError)),
        reraise=True
    )
    async def get_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        installation_id: int
    ) -> Dict[str, Any]:
        """Get issue details"""
        return await self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/issues/{issue_number}",
            installation_id
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, GitHubAPIError)),
        reraise=True
    )
    async def create_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
        installation_id: int
    ) -> Dict[str, Any]:
        """Create comment on issue"""
        return await self._make_request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            installation_id,
            json_data={"body": body}
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, GitHubAPIError)),
        reraise=True
    )
    async def get_repository(
        self,
        owner: str,
        repo: str,
        installation_id: int
    ) -> Dict[str, Any]:
        """Get repository details"""
        return await self._make_request(
            "GET",
            f"/repos/{owner}/{repo}",
            installation_id
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, GitHubAPIError)),
        reraise=True
    )
    async def list_pr_files(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        installation_id: int
    ) -> List[Dict[str, Any]]:
        """List files changed in PR"""
        return await self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/pulls/{pr_number}/files",
            installation_id
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, GitHubAPIError)),
        reraise=True
    )
    async def get_commit(
        self,
        owner: str,
        repo: str,
        commit_sha: str,
        installation_id: int
    ) -> Dict[str, Any]:
        """Get commit details"""
        return await self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/commits/{commit_sha}",
            installation_id
        )

    async def get_rate_limit_status(self, installation_id: int) -> Dict[str, Any]:
        """Get current rate limit status"""
        return await self._make_request(
            "GET",
            "/rate_limit",
            installation_id
        )

    def get_request_stats(self) -> Dict[str, Any]:
        """Get API request statistics"""
        if not self.requests_log:
            return {
                "total_requests": 0,
                "avg_duration_ms": 0,
                "error_rate": 0
            }

        total = len(self.requests_log)
        avg_duration = sum(r.duration_ms for r in self.requests_log) / total
        errors = sum(1 for r in self.requests_log if r.error)

        return {
            "total_requests": total,
            "avg_duration_ms": round(avg_duration, 2),
            "error_count": errors,
            "error_rate": round((errors / total) * 100, 2),
            "last_rate_limit_remaining": self.requests_log[-1].rate_limit_remaining if self.requests_log else None
        }
