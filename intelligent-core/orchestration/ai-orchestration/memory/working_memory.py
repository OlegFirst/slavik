"""
Working Memory
==============

Redis-based temporary memory for:
- Current context
- Active workflows
- Recent events
- Session data

TTL: 1 hour (auto-expires)
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from infrastructure.database.managers.redis_client import redis_manager
from infrastructure.eventbus.core.events import Event

logger = logging.getLogger(__name__)


class WorkingMemory:
    """
    Redis-based working memory for temporary context.

    Features:
    - Fast access (in-memory)
    - Automatic expiration (1 hour TTL)
    - Recent events tracking
    - Session state

    Example:
        ```python
        memory = WorkingMemory()
        await memory.initialize()

        # Store current context
        await memory.store('current_situation', situation_data)

        # Retrieve
        data = await memory.retrieve('current_situation')
        ```
    """

    # TTL in seconds (1 hour)
    DEFAULT_TTL = 3600

    # Key prefixes
    PREFIX_EVENT = 'working:event:'
    PREFIX_CONTEXT = 'working:context:'
    PREFIX_SESSION = 'working:session:'

    def __init__(self):
        self.redis = redis_manager
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize working memory."""
        # Ensure Redis is connected
        if not self.redis.client:
            await self.redis.connect()

        self.initialized = True
        logger.info("WorkingMemory initialized")

    async def store(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store item in working memory.

        Args:
            key: Storage key
            value: Data to store
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            bool: Success status
        """
        try:
            full_key = f"{self.PREFIX_CONTEXT}{key}"
            ttl = ttl or self.DEFAULT_TTL

            await self.redis.set(full_key, value, ttl)
            return True

        except Exception as e:
            logger.error(f"Error storing in working memory: {e}")
            return False

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from working memory."""
        try:
            full_key = f"{self.PREFIX_CONTEXT}{key}"
            return await self.redis.get(full_key)

        except Exception as e:
            logger.error(f"Error retrieving from working memory: {e}")
            return None

    async def store_event(self, event: Event) -> bool:
        """
        Store event in working memory.

        Args:
            event: Event to store

        Returns:
            bool: Success status
        """
        try:
            # Store individual event
            event_key = f"{self.PREFIX_EVENT}{event.id}"
            await self.redis.set(event_key, event.to_dict(), self.DEFAULT_TTL)

            # Add to recent events list
            await self._add_to_recent_events(event)

            return True

        except Exception as e:
            logger.error(f"Error storing event: {e}")
            return False

    async def get_recent_events(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent events from working memory.

        Args:
            limit: Maximum events to return

        Returns:
            List of recent events
        """
        try:
            # Get from list
            events_key = f"{self.PREFIX_EVENT}recent"
            event_ids = await self.redis.client.lrange(events_key, 0, limit - 1)

            events = []
            for event_id in event_ids:
                event_key = f"{self.PREFIX_EVENT}{event_id}"
                event_data = await self.redis.get(event_key)
                if event_data:
                    events.append(event_data)

            return events

        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
            return []

    async def find_recent_similar(
        self,
        situation: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar situations in recent events.

        Simple keyword matching for now.
        TODO: Implement semantic similarity.
        """
        try:
            recent_events = await self.get_recent_events(limit=100)

            # Extract keywords from situation
            keywords = self._extract_keywords(situation)

            # Score events by keyword overlap
            scored = []
            for event in recent_events:
                score = self._calculate_similarity(keywords, event)
                if score > 0:
                    scored.append((score, event))

            # Sort by score and return top N
            scored.sort(key=lambda x: x[0], reverse=True)
            return [event for _, event in scored[:limit]]

        except Exception as e:
            logger.error(f"Error finding similar: {e}")
            return []

    async def clear_session(self, session_id: str) -> bool:
        """Clear session data."""
        try:
            pattern = f"{self.PREFIX_SESSION}{session_id}:*"
            await self.redis.delete_pattern(pattern)
            return True

        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return False

    async def close(self) -> None:
        """Close working memory (no-op, Redis managed globally)."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get working memory statistics."""
        return {
            'type': 'working',
            'backend': 'redis',
            'ttl_seconds': self.DEFAULT_TTL,
            'initialized': self.initialized
        }

    # Private methods

    async def _add_to_recent_events(self, event: Event) -> None:
        """Add event to recent events list."""
        try:
            events_key = f"{self.PREFIX_EVENT}recent"

            # Add to left of list (newest first)
            await self.redis.lpush(events_key, event.id)

            # Trim list to 1000 most recent
            await self.redis.client.ltrim(events_key, 0, 999)

            # Set expiry on list
            await self.redis.expire(events_key, self.DEFAULT_TTL)

        except Exception as e:
            logger.error(f"Error adding to recent events: {e}")

    def _extract_keywords(self, data: Dict[str, Any]) -> set:
        """Extract keywords from data for similarity matching."""
        keywords = set()

        # Convert to string and split
        text = json.dumps(data).lower()

        # Simple keyword extraction (TODO: improve)
        words = text.split()
        keywords.update(w for w in words if len(w) > 3)

        return keywords

    def _calculate_similarity(
        self,
        keywords: set,
        event: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between keywords and event."""
        if not keywords:
            return 0.0

        # Extract keywords from event
        event_keywords = self._extract_keywords(event)

        if not event_keywords:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(keywords & event_keywords)
        union = len(keywords | event_keywords)

        return intersection / union if union > 0 else 0.0
