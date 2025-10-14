"""
GitHub Integration Client - Token management and API integration

From /services/ai_orchestrator/main.py (GitHubTokenManager class)
"""

import os
import json
import base64
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GitHubTokenManager:
    """
    GitHub user token management

    Features:
    - GitHub JWT exchange to internal tokens
    - Token refresh
    - User lookup by token
    - Token expiration handling
    - Supabase integration for user tracking
    """

    def __init__(self, supabase_client=None):
        """
        Initialize GitHub token manager

        Args:
            supabase_client: Optional Supabase client for event tracking
        """
        self.active_tokens = {}  # user_id -> token_data
        self.supabase = supabase_client
        self.repo_name = os.getenv("GITHUB_REPO", "SEH-foundation/ISO-22301")

        logger.info("GitHubTokenManager initialized")

    async def exchange_github_token(self, github_jwt: str) -> Dict[str, Any]:
        """
        Exchange GitHub JWT for internal token

        Args:
            github_jwt: GitHub JWT token

        Returns:
            Internal token data with expiration
        """
        try:
            logger.info("Exchanging GitHub JWT for internal token")

            # Decode GitHub JWT (simplified - in production verify signature)
            payload = github_jwt.split('.')[1]

            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)

            try:
                user_data = json.loads(base64.b64decode(payload))
            except Exception as e:
                logger.error(f"Failed to decode GitHub JWT: {e}")
                # Fallback to anonymous token
                return self._create_anonymous_token()

            user_id = user_data.get('sub', 'anonymous')
            username = user_data.get('login', 'unknown')

            # Create internal token
            internal_token = f"bcm_user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Token data
            token_data = {
                "user_id": user_id,
                "username": username,
                "github_data": user_data,
                "internal_token": internal_token,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=8)
            }

            # Save in memory (in production - use Redis/Database)
            self.active_tokens[user_id] = token_data

            # Track in Supabase for analytics
            if self.supabase:
                try:
                    self.supabase.table("github_events").insert({
                        "repo_full_name": self.repo_name,
                        "event_type": "token_exchange",
                        "event_action": "user_authenticated",
                        "github_id": user_id,
                        "payload": {
                            "username": username,
                            "auth_time": datetime.now().isoformat()
                        },
                        "processed": True,
                        "ai_analysis": {"user_authenticated": True}
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to track token exchange in Supabase: {e}")

            logger.info(f"Token exchanged successfully for user: {username}")

            return {
                "token": internal_token,
                "token_type": "bearer",
                "expires_in": 28800,  # 8 hours in seconds
                "user_id": user_id,
                "username": username,
                "created_at": token_data["created_at"].isoformat()
            }

        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return self._create_anonymous_token()

    def _create_anonymous_token(self) -> Dict[str, Any]:
        """Create anonymous fallback token"""
        anon_token = f"bcm_anon_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "token": anon_token,
            "token_type": "bearer",
            "expires_in": 28800,
            "user_id": "anonymous",
            "username": "anonymous"
        }

    async def refresh_token(self, old_token: str) -> Dict[str, Any]:
        """
        Refresh expired token

        Args:
            old_token: Old internal token to refresh

        Returns:
            New token data

        Raises:
            ValueError: If token is invalid or user not found
        """
        logger.info("Refreshing token")

        # Find user by old token
        user_data = None
        for uid, data in self.active_tokens.items():
            if data["internal_token"] == old_token:
                user_data = data
                break

        if not user_data:
            logger.warning("Token refresh failed - user not found")
            raise ValueError("Invalid refresh token")

        # Check if token is not too old (max 30 days)
        if user_data["created_at"] < datetime.now() - timedelta(days=30):
            logger.warning("Token too old - requires re-authentication")
            raise ValueError("Token expired - re-authentication required")

        # Create new token
        new_token = f"bcm_user_{user_data['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Update token data
        user_data["internal_token"] = new_token
        user_data["created_at"] = datetime.now()
        user_data["expires_at"] = datetime.now() + timedelta(hours=8)

        logger.info(f"Token refreshed for user: {user_data['username']}")

        return {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": 28800,
            "user_id": user_data["user_id"],
            "username": user_data["username"]
        }

    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from token

        Args:
            token: Internal token

        Returns:
            User data if token is valid, None otherwise
        """
        for user_data in self.active_tokens.values():
            if user_data["internal_token"] == token:
                # Check if token is still valid
                if user_data["expires_at"] > datetime.now():
                    return user_data
                else:
                    logger.debug(f"Token expired for user: {user_data.get('username', 'unknown')}")

        return None

    def revoke_token(self, token: str) -> bool:
        """
        Revoke token (logout)

        Args:
            token: Token to revoke

        Returns:
            True if revoked, False if not found
        """
        for uid, data in list(self.active_tokens.items()):
            if data["internal_token"] == token:
                del self.active_tokens[uid]
                logger.info(f"Token revoked for user: {data.get('username', 'unknown')}")
                return True

        return False

    def get_active_users_count(self) -> int:
        """Get count of active users with valid tokens"""
        now = datetime.now()
        active_count = sum(
            1 for data in self.active_tokens.values()
            if data["expires_at"] > now
        )

        return active_count

    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from memory

        Returns:
            Number of tokens removed
        """
        now = datetime.now()
        expired_users = [
            uid for uid, data in self.active_tokens.items()
            if data["expires_at"] <= now
        ]

        for uid in expired_users:
            del self.active_tokens[uid]

        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired tokens")

        return len(expired_users)