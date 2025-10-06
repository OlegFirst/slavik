"""
Redis Cache Manager
===================

Async Redis cache manager with decorator support.

Features:
- Async Redis operations
- Decorator for automatic caching
- JSON serialization/deserialization
- TTL support
- Global singleton pattern
- Multi-tenant namespacing
- Metrics tracking (cache hits/misses)
- Error handling with fallback
"""

import json
import logging
from typing import Optional, Any, Callable, Dict
from functools import wraps
import hashlib
import redis.asyncio as redis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Async Redis cache manager.

    Provides simple key-value caching with automatic JSON serialization,
    multi-tenant namespacing, and metrics tracking.

    Example:
        ```python
        # Initialize at startup
        cache = init_cache("redis://localhost:6379/0")

        # Use directly with tenant namespacing
        await cache.set("user:123", {"name": "John"}, ttl=3600, tenant_id="tenant1")
        user = await cache.get("user:123", tenant_id="tenant1")

        # Use with decorator
        @cached(ttl=3600, key_prefix="kpi:dashboard")
        async def get_kpi_dashboard(tenant_id: str):
            return await expensive_calculation(tenant_id)

        # Get cache metrics
        metrics = cache.get_metrics()
        ```
    """

    def __init__(self, redis_url: str, decode_responses: bool = True):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            decode_responses: Auto-decode responses to strings (default: True)
        """
        self.redis: Redis = redis.from_url(
            redis_url,
            decode_responses=decode_responses
        )
        # Metrics tracking
        self._metrics: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }

    def _build_key(self, key: str, tenant_id: Optional[str] = None) -> str:
        """Build cache key with optional tenant namespacing."""
        if tenant_id:
            return f"tenant:{tenant_id}:{key}"
        return key

    async def get(self, key: str, tenant_id: Optional[str] = None) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key
            tenant_id: Optional tenant ID for multi-tenant namespacing

        Returns:
            Cached value or None if not found

        Example:
            ```python
            value = await cache.get("user:123", tenant_id="tenant1")
            ```
        """
        try:
            full_key = self._build_key(key, tenant_id)
            value = await self.redis.get(full_key)
            if value:
                self._metrics["hits"] += 1
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    # Return raw value if not JSON
                    return value
            else:
                self._metrics["misses"] += 1
            return None
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600, tenant_id: Optional[str] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 3600 = 1 hour)
            tenant_id: Optional tenant ID for multi-tenant namespacing

        Returns:
            bool: True if successful

        Example:
            ```python
            await cache.set("user:123", user_data, ttl=7200, tenant_id="tenant1")
            ```
        """
        try:
            full_key = self._build_key(key, tenant_id)
            serialized = json.dumps(value, default=str)
            await self.redis.setex(full_key, ttl, serialized)
            self._metrics["sets"] += 1
            return True
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str, tenant_id: Optional[str] = None) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key
            tenant_id: Optional tenant ID for multi-tenant namespacing

        Returns:
            bool: True if key was deleted

        Example:
            ```python
            await cache.delete("user:123", tenant_id="tenant1")
            ```
        """
        try:
            full_key = self._build_key(key, tenant_id)
            result = await self.redis.delete(full_key)
            if result > 0:
                self._metrics["deletes"] += 1
            return result > 0
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str, tenant_id: Optional[str] = None) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key
            tenant_id: Optional tenant ID for multi-tenant namespacing

        Returns:
            bool: True if key exists

        Example:
            ```python
            if await cache.exists("user:123", tenant_id="tenant1"):
                print("User is cached")
            ```
        """
        try:
            full_key = self._build_key(key, tenant_id)
            result = await self.redis.exists(full_key)
            return result > 0
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str, tenant_id: Optional[str] = None) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "user:*", "bia:*")
            tenant_id: Optional tenant ID for multi-tenant namespacing

        Returns:
            int: Number of keys deleted

        Example:
            ```python
            # Clear all user caches for a tenant
            await cache.clear_pattern("user:*", tenant_id="tenant1")

            # Clear all BIA caches
            await cache.clear_pattern("bia:*", tenant_id="tenant1")
            ```
        """
        try:
            full_pattern = self._build_key(pattern, tenant_id)
            keys = []
            async for key in self.redis.scan_iter(full_pattern):
                keys.append(key)

            if keys:
                deleted = await self.redis.delete(*keys)
                self._metrics["deletes"] += deleted
                return deleted
            return 0
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Cache clear_pattern error for pattern {pattern}: {e}")
            return 0

    async def get_ttl(self, key: str, tenant_id: Optional[str] = None) -> int:
        """
        Get remaining TTL for key.

        Args:
            key: Cache key
            tenant_id: Optional tenant ID for multi-tenant namespacing

        Returns:
            int: Remaining TTL in seconds (-1 if no expiry, -2 if key doesn't exist)

        Example:
            ```python
            ttl = await cache.get_ttl("user:123", tenant_id="tenant1")
            print(f"Expires in {ttl} seconds")
            ```
        """
        try:
            full_key = self._build_key(key, tenant_id)
            return await self.redis.ttl(full_key)
        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Cache get_ttl error for key {key}: {e}")
            return -2

    async def close(self) -> None:
        """
        Close Redis connection.

        Call this during application shutdown.

        Example:
            ```python
            @app.on_event("shutdown")
            async def shutdown():
                await cache.close()
            ```
        """
        await self.redis.close()

    async def ping(self) -> bool:
        """
        Test Redis connection.

        Returns:
            bool: True if Redis is reachable

        Example:
            ```python
            if await cache.ping():
                print("Redis is healthy")
            ```
        """
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get cache metrics.

        Returns:
            dict: Cache metrics including hits, misses, hit rate, etc.

        Example:
            ```python
            metrics = cache.get_metrics()
            print(f"Cache hit rate: {metrics['hit_rate']:.2%}")
            ```
        """
        total_requests = self._metrics["hits"] + self._metrics["misses"]
        hit_rate = self._metrics["hits"] / total_requests if total_requests > 0 else 0.0

        return {
            "hits": self._metrics["hits"],
            "misses": self._metrics["misses"],
            "sets": self._metrics["sets"],
            "deletes": self._metrics["deletes"],
            "errors": self._metrics["errors"],
            "total_requests": total_requests,
            "hit_rate": hit_rate,
        }

    def reset_metrics(self) -> None:
        """
        Reset cache metrics.

        Example:
            ```python
            cache.reset_metrics()
            ```
        """
        self._metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }


# Global cache instance
_cache: Optional[RedisCache] = None


def init_cache(redis_url: str) -> RedisCache:
    """
    Initialize global cache.

    Call this once during application startup.

    Args:
        redis_url: Redis connection URL

    Returns:
        RedisCache: Initialized cache

    Example:
        ```python
        @app.on_event("startup")
        async def startup():
            init_cache(settings.REDIS_URL)
        ```
    """
    global _cache
    _cache = RedisCache(redis_url)
    return _cache


def get_cache() -> RedisCache:
    """
    Get global cache instance.

    Returns:
        RedisCache: Global cache

    Raises:
        RuntimeError: If cache not initialized
    """
    if _cache is None:
        raise RuntimeError(
            "Cache not initialized. Call init_cache() during startup."
        )
    return _cache


def cached(ttl: int = 3600, key_prefix: str = "", use_tenant: bool = True):
    """
    Decorator for caching function results with multi-tenant support.

    Args:
        ttl: Time to live in seconds (default: 3600 = 1 hour)
        key_prefix: Prefix for cache keys (default: "")
        use_tenant: If True, automatically extract tenant_id from function args/kwargs (default: True)

    Returns:
        Decorator function

    Example:
        ```python
        @cached(ttl=300, key_prefix="kpi:dashboard")
        async def get_kpi_dashboard(tenant_id: str):
            # Expensive calculation
            return await calculate_dashboard(tenant_id)

        # First call: cache miss, executes function
        result = await get_kpi_dashboard("tenant123")

        # Second call within 5 minutes: cache hit, returns cached value
        result = await get_kpi_dashboard("tenant123")
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache
            cache = get_cache()

            # Extract tenant_id if use_tenant is True
            tenant_id = None
            if use_tenant:
                # Check kwargs first
                tenant_id = kwargs.get("tenant_id")
                # If not in kwargs, check if first arg looks like tenant_id
                if not tenant_id and args:
                    # Try to find tenant_id in function signature
                    import inspect
                    sig = inspect.signature(func)
                    params = list(sig.parameters.keys())
                    if "tenant_id" in params:
                        tenant_idx = params.index("tenant_id")
                        if len(args) > tenant_idx:
                            tenant_id = args[tenant_idx]

            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]

            # Add positional arguments to key (excluding tenant_id if use_tenant)
            if args:
                args_str = ":".join(str(arg) for arg in args)
                key_parts.append(args_str)

            # Add keyword arguments to key (sorted for consistency, excluding tenant_id if use_tenant)
            if kwargs:
                filtered_kwargs = {k: v for k, v in kwargs.items() if not (use_tenant and k == "tenant_id")}
                if filtered_kwargs:
                    kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(filtered_kwargs.items()))
                    key_parts.append(kwargs_str)

            # Create final cache key (hash if too long)
            cache_key = ":".join(filter(None, key_parts))
            if len(cache_key) > 200:
                # Hash long keys to prevent Redis key size issues
                hash_digest = hashlib.md5(cache_key.encode()).hexdigest()
                cache_key = f"{key_prefix}:{func.__name__}:{hash_digest}"

            # Try to get from cache
            cached_value = await cache.get(cache_key, tenant_id=tenant_id)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(cache_key, result, ttl, tenant_id=tenant_id)

            return result
        return wrapper
    return decorator
