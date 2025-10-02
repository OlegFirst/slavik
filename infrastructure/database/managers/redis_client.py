"""
Redis Client Manager
Caching, session storage, rate limiting
"""

import os
import json
import redis.asyncio as redis
from typing import Optional, Any, List
import logging

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Async Redis client for:
    - Caching
    - Session storage
    - Rate limiting
    - Pub/Sub (Event Bus)
    """

    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.password = os.getenv("REDIS_PASSWORD")
        self.db = int(os.getenv("REDIS_DB", 0))
        self.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", 50))

        self.client: Optional[redis.Redis] = None
        self.pool: Optional[redis.ConnectionPool] = None

    async def connect(self):
        """Initialize Redis connection pool"""
        try:
            # Create connection pool
            self.pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                decode_responses=True,  # Auto decode bytes to str
                socket_timeout=int(os.getenv("REDIS_SOCKET_TIMEOUT", 5)),
                socket_connect_timeout=int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", 5))
            )

            # Create client
            self.client = redis.Redis(connection_pool=self.pool)

            # Test connection
            await self.client.ping()

            logger.info(f"✅ Redis connected: {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connections"""
        if self.client:
            await self.client.close()
            logger.info("✅ Redis connections closed")

    async def health_check(self) -> bool:
        """Check Redis health"""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    # ============================================
    # CACHE OPERATIONS
    # ============================================

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.client.get(key)
            if value:
                # Try to parse JSON
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL (seconds)"""
        try:
            # Serialize to JSON if not string
            if not isinstance(value, str):
                value = json.dumps(value)

            if ttl:
                return await self.client.setex(key, ttl, value)
            else:
                return await self.client.set(key, value)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return await self.client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern (e.g., 'user:123:*')"""
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE_PATTERN error for pattern {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on existing key"""
        try:
            return await self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -1

    # ============================================
    # HASH OPERATIONS (for complex objects)
    # ============================================

    async def hset(self, key: str, field: str, value: Any) -> bool:
        """Set field in hash"""
        try:
            if not isinstance(value, str):
                value = json.dumps(value)
            return await self.client.hset(key, field, value)
        except Exception as e:
            logger.error(f"Redis HSET error: {e}")
            return False

    async def hget(self, key: str, field: str) -> Optional[Any]:
        """Get field from hash"""
        try:
            value = await self.client.hget(key, field)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis HGET error: {e}")
            return None

    async def hgetall(self, key: str) -> dict:
        """Get all fields from hash"""
        try:
            data = await self.client.hgetall(key)
            # Try to parse JSON values
            result = {}
            for field, value in data.items():
                try:
                    result[field] = json.loads(value)
                except:
                    result[field] = value
            return result
        except Exception as e:
            logger.error(f"Redis HGETALL error: {e}")
            return {}

    # ============================================
    # LIST OPERATIONS (for queues)
    # ============================================

    async def lpush(self, key: str, *values) -> int:
        """Push values to left of list"""
        try:
            serialized = [json.dumps(v) if not isinstance(v, str) else v for v in values]
            return await self.client.lpush(key, *serialized)
        except Exception as e:
            logger.error(f"Redis LPUSH error: {e}")
            return 0

    async def rpop(self, key: str) -> Optional[Any]:
        """Pop value from right of list"""
        try:
            value = await self.client.rpop(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis RPOP error: {e}")
            return None

    async def llen(self, key: str) -> int:
        """Get list length"""
        try:
            return await self.client.llen(key)
        except Exception as e:
            logger.error(f"Redis LLEN error: {e}")
            return 0

    # ============================================
    # RATE LIMITING
    # ============================================

    async def rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if rate limit exceeded

        Args:
            key: Rate limit key (e.g., 'rate:user:123' or 'rate:ip:1.2.3.4')
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if allowed, False if rate limited
        """
        try:
            # Increment counter
            count = await self.client.incr(key)

            # Set expiry on first request
            if count == 1:
                await self.client.expire(key, window_seconds)

            # Check if exceeded
            return count <= max_requests

        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            # On error, allow request (fail open)
            return True

    # ============================================
    # PUB/SUB (Event Bus)
    # ============================================

    async def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        try:
            if not isinstance(message, str):
                message = json.dumps(message)
            return await self.client.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis PUBLISH error: {e}")
            return 0

    async def subscribe(self, *channels: str):
        """Subscribe to channels (returns async generator)"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe(*channels)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    try:
                        yield json.loads(data)
                    except:
                        yield data
        finally:
            await pubsub.unsubscribe(*channels)
            await pubsub.close()

    # ============================================
    # UTILITY METHODS
    # ============================================

    def generate_cache_key(self, *parts) -> str:
        """Generate cache key from parts"""
        return ":".join(str(p) for p in parts)


# Global instance
redis_manager = RedisManager()


# Helper functions
async def cache_get(key: str) -> Optional[Any]:
    """Quick cache get"""
    return await redis_manager.get(key)


async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Quick cache set"""
    return await redis_manager.set(key, value, ttl)


async def cache_delete(key: str) -> bool:
    """Quick cache delete"""
    return await redis_manager.delete(key)
