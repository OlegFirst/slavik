"""
Redis Cache Helper
"""

import redis.asyncio as aioredis
import json
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class CacheClient:
    """Async Redis cache client"""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        self.client = await aioredis.from_url(self.redis_url)
        logger.info("Connected to Redis")

    async def close(self):
        """Close connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None

        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache"""
        if not self.client:
            return False

        try:
            await self.client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str):
        """Delete from cache"""
        if not self.client:
            return False

        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False


# Global instance
_cache: Optional[CacheClient] = None


def init_cache(redis_url: str) -> CacheClient:
    """Initialize global cache"""
    global _cache
    _cache = CacheClient(redis_url)
    return _cache


def get_cache() -> CacheClient:
    """Get global cache"""
    if _cache is None:
        raise RuntimeError("Cache not initialized")
    return _cache
