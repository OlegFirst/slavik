"""
GitHub App Authentication
=========================

JWT and installation token management for GitHub App.
"""

import time
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import httpx

from config import config
from models import InstallationToken

logger = logging.getLogger(__name__)


class GitHubAuth:
    """
    GitHub App authentication manager.

    Handles:
    - JWT generation for GitHub App
    - Installation token management
    - Token caching and refresh
    """

    def __init__(self):
        self.app_id = config.GITHUB_APP_ID
        self.private_key = config.get_private_key()
        self.token_cache: Dict[int, InstallationToken] = {}

    def generate_jwt(self) -> str:
        """
        Generate JWT for GitHub App authentication.

        Returns:
            JWT token string
        """
        now = int(time.time())

        payload = {
            'iat': now,
            'exp': now + config.JWT_TOKEN_TTL,
            'iss': self.app_id
        }

        token = jwt.encode(
            payload,
            self.private_key,
            algorithm='RS256'
        )

        logger.debug("Generated GitHub App JWT")
        return token

    async def get_installation_token(
        self,
        installation_id: int,
        force_refresh: bool = False
    ) -> InstallationToken:
        """
        Get installation access token.

        Args:
            installation_id: GitHub App installation ID
            force_refresh: Force token refresh even if cached

        Returns:
            InstallationToken
        """
        # Check cache
        if not force_refresh and installation_id in self.token_cache:
            cached_token = self.token_cache[installation_id]
            # Check if token is still valid (with 5 min buffer)
            if cached_token.expires_at > datetime.utcnow() + timedelta(minutes=5):
                logger.debug(f"Using cached token for installation {installation_id}")
                return cached_token

        # Generate new token
        logger.info(f"Requesting new installation token for {installation_id}")

        jwt_token = self.generate_jwt()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.GITHUB_API_URL}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": config.GITHUB_API_VERSION
                }
            )

            if response.status_code != 201:
                logger.error(
                    f"Failed to get installation token: {response.status_code} - {response.text}"
                )
                raise Exception(f"Failed to get installation token: {response.status_code}")

            data = response.json()

            installation_token = InstallationToken(
                token=data['token'],
                expires_at=datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00')),
                installation_id=installation_id,
                permissions=data.get('permissions', {})
            )

            # Cache token
            self.token_cache[installation_id] = installation_token

            logger.info(f"Got new installation token for {installation_id}")
            return installation_token

    async def revoke_installation_token(self, installation_id: int):
        """
        Revoke cached installation token.

        Args:
            installation_id: Installation ID
        """
        if installation_id in self.token_cache:
            del self.token_cache[installation_id]
            logger.info(f"Revoked cached token for installation {installation_id}")

    def verify_webhook_signature(
        self,
        payload_body: bytes,
        signature_header: str
    ) -> bool:
        """
        Verify GitHub webhook signature.

        Args:
            payload_body: Raw request body
            signature_header: X-Hub-Signature-256 header value

        Returns:
            True if signature valid, False otherwise
        """
        import hmac
        import hashlib

        if not signature_header:
            logger.warning("No signature header provided")
            return False

        # Extract hash from header (format: sha256=<hash>)
        try:
            hash_algorithm, signature = signature_header.split('=')
        except ValueError:
            logger.warning(f"Invalid signature format: {signature_header}")
            return False

        if hash_algorithm != 'sha256':
            logger.warning(f"Unsupported hash algorithm: {hash_algorithm}")
            return False

        # Calculate expected signature
        mac = hmac.new(
            config.GITHUB_WEBHOOK_SECRET.encode(),
            msg=payload_body,
            digestmod=hashlib.sha256
        )
        expected_signature = mac.hexdigest()

        # Compare signatures (timing-safe comparison)
        is_valid = hmac.compare_digest(expected_signature, signature)

        if not is_valid:
            logger.warning("Webhook signature verification failed")

        return is_valid
