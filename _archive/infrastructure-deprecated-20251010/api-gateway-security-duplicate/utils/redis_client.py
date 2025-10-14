"""
Redis Client
Production-grade async Redis client with connection pooling
"""

import logging
from typing import Optional, Any, Union
import asyncio
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError, ConnectionError, TimeoutError

from config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Production-grade async Redis client

    Features:
    - Connection pooling for optimal performance
    - Async operations with proper error handling
    - Health check capabilities
    - Graceful error handling and retry logic
    - Automatic reconnection
    - Thread-safe operations
    """

    def __init__(self):
        """Initialize Redis client with connection pool"""
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[aioredis.Redis] = None
        self._is_connected: bool = False
        self._connection_lock = asyncio.Lock()

        # Parse Redis URL
        self.redis_url = settings.redis_url
        self.redis_password = settings.redis_password

        logger.info(f"Redis client initialized with URL: {self._sanitize_url(self.redis_url)}")

    def _sanitize_url(self, url: str) -> str:
        """Sanitize Redis URL for logging (remove password)"""
        if self.redis_password and self.redis_password in url:
            return url.replace(self.redis_password, "***")
        return url

    async def connect(self) -> None:
        """
        Establish Redis connection with connection pooling

        Raises:
            ConnectionError: If connection fails
        """
        async with self._connection_lock:
            if self._is_connected:
                logger.debug("Redis already connected")
                return

            try:
                # Create connection pool
                self._pool = ConnectionPool.from_url(
                    self.redis_url,
                    password=self.redis_password if self.redis_password else None,
                    max_connections=settings.max_connections,
                    decode_responses=True,
                    encoding="utf-8",
                    socket_keepalive=True,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )

                # Create Redis client from pool
                self._client = aioredis.Redis(connection_pool=self._pool)

                # Test connection
                await self._client.ping()

                self._is_connected = True
                logger.info("Redis connection established successfully")

            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                self._is_connected = False
                raise ConnectionError(f"Redis connection failed: {str(e)}") from e

    async def disconnect(self) -> None:
        """Close Redis connection and cleanup resources"""
        async with self._connection_lock:
            if self._client:
                try:
                    await self._client.close()
                    logger.info("Redis client closed")
                except Exception as e:
                    logger.error(f"Error closing Redis client: {str(e)}")

            if self._pool:
                try:
                    await self._pool.disconnect()
                    logger.info("Redis connection pool closed")
                except Exception as e:
                    logger.error(f"Error closing Redis pool: {str(e)}")

            self._is_connected = False
            self._client = None
            self._pool = None

    async def ensure_connected(self) -> None:
        """Ensure Redis is connected, reconnect if necessary"""
        if not self._is_connected or not self._client:
            await self.connect()

    @asynccontextmanager
    async def _get_client(self):
        """Context manager to ensure connection before operations"""
        await self.ensure_connected()
        try:
            yield self._client
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis connection error: {str(e)}")
            self._is_connected = False
            raise

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis

        Args:
            key: Redis key

        Returns:
            Value as string or None if key doesn't exist

        Raises:
            RedisError: If operation fails
        """
        try:
            async with self._get_client() as client:
                value = await client.get(key)
                logger.debug(f"GET {key}: {'found' if value else 'not found'}")
                return value
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {str(e)}")
            raise RedisError(f"Failed to get key '{key}': {str(e)}") from e

    async def set(
        self,
        key: str,
        value: Union[str, int, float],
        expire: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis with optional expiration

        Args:
            key: Redis key
            value: Value to store
            expire: Expiration time in seconds (optional)

        Returns:
            True if successful

        Raises:
            RedisError: If operation fails
        """
        try:
            async with self._get_client() as client:
                if expire:
                    result = await client.setex(key, expire, value)
                else:
                    result = await client.set(key, value)

                logger.debug(f"SET {key} (expire: {expire}s): {result}")
                return bool(result)
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {str(e)}")
            raise RedisError(f"Failed to set key '{key}': {str(e)}") from e

    async def delete(self, *keys: str) -> int:
        """
        Delete one or more keys from Redis

        Args:
            *keys: Keys to delete

        Returns:
            Number of keys deleted

        Raises:
            RedisError: If operation fails
        """
        try:
            async with self._get_client() as client:
                count = await client.delete(*keys)
                logger.debug(f"DELETE {keys}: {count} keys removed")
                return count
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {str(e)}")
            raise RedisError(f"Failed to delete keys: {str(e)}") from e

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis

        Args:
            key: Redis key

        Returns:
            True if key exists, False otherwise
        """
        try:
            async with self._get_client() as client:
                exists = await client.exists(key)
                return bool(exists)
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {str(e)}")
            return False

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        Increment value in Redis (atomic operation)

        Args:
            key: Redis key
            amount: Amount to increment by (default: 1)

        Returns:
            New value after increment

        Raises:
            RedisError: If operation fails
        """
        try:
            async with self._get_client() as client:
                value = await client.incrby(key, amount)
                logger.debug(f"INCR {key} by {amount}: {value}")
                return value
        except Exception as e:
            logger.error(f"Redis INCR error for key '{key}': {str(e)}")
            raise RedisError(f"Failed to increment key '{key}': {str(e)}") from e

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on existing key

        Args:
            key: Redis key
            seconds: Expiration time in seconds

        Returns:
            True if expiration was set

        Raises:
            RedisError: If operation fails
        """
        try:
            async with self._get_client() as client:
                result = await client.expire(key, seconds)
                logger.debug(f"EXPIRE {key} in {seconds}s: {result}")
                return bool(result)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {str(e)}")
            raise RedisError(f"Failed to set expiration on key '{key}': {str(e)}") from e

    async def ttl(self, key: str) -> int:
        """
        Get time-to-live for key

        Args:
            key: Redis key

        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            async with self._get_client() as client:
                ttl = await client.ttl(key)
                return ttl
        except Exception as e:
            logger.error(f"Redis TTL error for key '{key}': {str(e)}")
            return -2

    async def zadd(
        self,
        key: str,
        mapping: dict,
        nx: bool = False,
        xx: bool = False
    ) -> int:
        """
        Add members to sorted set

        Args:
            key: Redis key
            mapping: Dict of {member: score}
            nx: Only add new elements (don't update)
            xx: Only update existing elements

        Returns:
            Number of elements added

        Raises:
            RedisError: If operation fails
        """
        try:
            async with self._get_client() as client:
                count = await client.zadd(key, mapping, nx=nx, xx=xx)
                logger.debug(f"ZADD {key}: {count} elements added")
                return count
        except Exception as e:
            logger.error(f"Redis ZADD error for key '{key}': {str(e)}")
            raise RedisError(f"Failed to add to sorted set '{key}': {str(e)}") from e

    async def zremrangebyscore(
        self,
        key: str,
        min_score: Union[int, float],
        max_score: Union[int, float]
    ) -> int:
        """
        Remove elements from sorted set by score range

        Args:
            key: Redis key
            min_score: Minimum score (inclusive)
            max_score: Maximum score (inclusive)

        Returns:
            Number of elements removed

        Raises:
            RedisError: If operation fails
        """
        try:
            async with self._get_client() as client:
                count = await client.zremrangebyscore(key, min_score, max_score)
                logger.debug(f"ZREMRANGEBYSCORE {key} [{min_score}, {max_score}]: {count} removed")
                return count
        except Exception as e:
            logger.error(f"Redis ZREMRANGEBYSCORE error for key '{key}': {str(e)}")
            raise RedisError(f"Failed to remove from sorted set '{key}': {str(e)}") from e

    async def zcard(self, key: str) -> int:
        """
        Get number of elements in sorted set

        Args:
            key: Redis key

        Returns:
            Number of elements in sorted set
        """
        try:
            async with self._get_client() as client:
                count = await client.zcard(key)
                return count
        except Exception as e:
            logger.error(f"Redis ZCARD error for key '{key}': {str(e)}")
            return 0

    async def health_check(self) -> dict:
        """
        Perform health check on Redis connection

        Returns:
            Dict with health check results:
                - status: 'healthy' or 'unhealthy'
                - connected: bool
                - latency_ms: Response time in milliseconds
                - error: Error message if unhealthy
        """
        import time

        health = {
            "status": "unhealthy",
            "connected": False,
            "latency_ms": None,
            "error": None,
        }

        try:
            start = time.time()

            async with self._get_client() as client:
                # Ping Redis
                await asyncio.wait_for(
                    client.ping(),
                    timeout=settings.health_check_timeout
                )

                latency = (time.time() - start) * 1000  # Convert to ms

                health.update({
                    "status": "healthy",
                    "connected": True,
                    "latency_ms": round(latency, 2),
                })

                logger.debug(f"Redis health check passed (latency: {latency:.2f}ms)")

        except asyncio.TimeoutError:
            error_msg = "Health check timeout"
            health["error"] = error_msg
            logger.error(f"Redis health check failed: {error_msg}")

        except Exception as e:
            error_msg = str(e)
            health["error"] = error_msg
            logger.error(f"Redis health check failed: {error_msg}")

        return health

    async def flush_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        WARNING: Use with caution in production!

        Args:
            pattern: Redis key pattern (e.g., "ratelimit:*")

        Returns:
            Number of keys deleted
        """
        try:
            async with self._get_client() as client:
                keys = []
                async for key in client.scan_iter(match=pattern):
                    keys.append(key)

                if keys:
                    count = await client.delete(*keys)
                    logger.warning(f"FLUSH pattern '{pattern}': {count} keys deleted")
                    return count
                else:
                    logger.debug(f"No keys found matching pattern '{pattern}'")
                    return 0

        except Exception as e:
            logger.error(f"Redis FLUSH error for pattern '{pattern}': {str(e)}")
            raise RedisError(f"Failed to flush pattern '{pattern}': {str(e)}") from e

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._is_connected


# Global Redis client instance
redis_client = RedisClient()


async def get_redis_client() -> RedisClient:
    """Get global Redis client instance and ensure connection"""
    await redis_client.ensure_connected()
    return redis_client
