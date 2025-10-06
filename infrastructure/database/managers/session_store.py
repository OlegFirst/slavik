"""
Session Store Manager
Manages user sessions in Redis with security and TTL
"""

import secrets
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
from .redis_client import redis_manager

logger = logging.getLogger(__name__)


class SessionStore:
    """
    Session management with:
    - Secure session IDs
    - Automatic expiry
    - Session data storage
    - Multi-device support
    - Activity tracking
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client or redis_manager
        self.session_prefix = "session"
        self.user_sessions_prefix = "user_sessions"
        self.default_ttl = 86400  # 24 hours

    def _session_key(self, session_id: str) -> str:
        """Generate Redis key for session"""
        return f"{self.session_prefix}:{session_id}"

    def _user_sessions_key(self, user_id: str) -> str:
        """Generate Redis key for user's session list"""
        return f"{self.user_sessions_prefix}:{user_id}"

    def generate_session_id(self) -> str:
        """Generate secure random session ID"""
        return secrets.token_urlsafe(32)

    async def create_session(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        ttl: Optional[int] = None,
        device_info: Optional[Dict] = None
    ) -> str:
        """
        Create new session

        Args:
            user_id: User ID
            session_data: Session data (user info, roles, etc.)
            ttl: Time to live in seconds (default: 24h)
            device_info: Device/browser information

        Returns:
            session_id: Generated session ID
        """
        session_id = self.generate_session_id()
        ttl = ttl or self.default_ttl

        # Prepare session object
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat(),
            "device_info": device_info or {},
            "data": session_data
        }

        # Store session
        session_key = self._session_key(session_id)
        await self.redis.set(session_key, session, ttl)

        # Add to user's session list
        user_sessions_key = self._user_sessions_key(user_id)
        await self.redis.hset(user_sessions_key, session_id, json.dumps({
            "created_at": session["created_at"],
            "device": device_info.get("device_type", "unknown") if device_info else "unknown"
        }))

        logger.info(f"Session created: {session_id} for user {user_id}")
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        session_key = self._session_key(session_id)
        session = await self.redis.get(session_key)

        if session:
            # Update last activity
            session["last_activity"] = datetime.utcnow().isoformat()
            await self.redis.set(session_key, session)

        return session

    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update session data"""
        session = await self.get_session(session_id)
        if not session:
            return False

        # Merge updates
        session["data"].update(updates)
        session["last_activity"] = datetime.utcnow().isoformat()

        # Save updated session
        session_key = self._session_key(session_id)
        ttl = await self.redis.ttl(session_key)

        if ttl > 0:
            await self.redis.set(session_key, session, ttl)
            return True

        return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        # Get session to find user_id
        session = await self.get_session(session_id)
        if not session:
            return False

        user_id = session["user_id"]

        # Delete session
        session_key = self._session_key(session_id)
        await self.redis.delete(session_key)

        # Remove from user's session list
        user_sessions_key = self._user_sessions_key(user_id)
        await self.redis.client.hdel(user_sessions_key, session_id)

        logger.info(f"Session deleted: {session_id}")
        return True

    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for user"""
        user_sessions_key = self._user_sessions_key(user_id)
        session_ids = await self.redis.hgetall(user_sessions_key)

        sessions = []
        for session_id, info in session_ids.items():
            session = await self.get_session(session_id)
            if session:  # Session still exists
                sessions.append(session)
            else:
                # Clean up expired session from list
                await self.redis.client.hdel(user_sessions_key, session_id)

        return sessions

    async def delete_all_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for user (logout from all devices)"""
        sessions = await self.get_user_sessions(user_id)
        count = 0

        for session in sessions:
            await self.delete_session(session["session_id"])
            count += 1

        logger.info(f"Deleted {count} sessions for user {user_id}")
        return count

    async def extend_session(self, session_id: str, additional_ttl: int) -> bool:
        """Extend session TTL"""
        session_key = self._session_key(session_id)
        current_ttl = await self.redis.ttl(session_key)

        if current_ttl > 0:
            new_ttl = current_ttl + additional_ttl
            await self.redis.expire(session_key, new_ttl)

            # Update expires_at
            session = await self.get_session(session_id)
            if session:
                session["expires_at"] = (datetime.utcnow() + timedelta(seconds=new_ttl)).isoformat()
                await self.redis.set(session_key, session, new_ttl)

            return True

        return False

    async def validate_session(self, session_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate session and return (is_valid, user_id)

        Returns:
            (True, user_id) if valid
            (False, None) if invalid/expired
        """
        session = await self.get_session(session_id)

        if not session:
            return False, None

        # Check if expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.utcnow() > expires_at:
            await self.delete_session(session_id)
            return False, None

        return True, session["user_id"]

    async def get_active_sessions_count(self) -> int:
        """Get total count of active sessions"""
        # This is approximate - actual count may be lower due to expired sessions
        pattern = f"{self.session_prefix}:*"
        keys = await self.redis.client.keys(pattern)
        return len(keys)


# Global instance
session_store = SessionStore()


# FastAPI dependency
async def get_current_session(session_id: Optional[str] = None) -> Optional[Dict]:
    """FastAPI dependency to get current session"""
    if not session_id:
        return None

    is_valid, user_id = await session_store.validate_session(session_id)
    if is_valid:
        return await session_store.get_session(session_id)

    return None
