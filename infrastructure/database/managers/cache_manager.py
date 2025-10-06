"""
Advanced Cache Manager
Decorator-based caching with TTL, invalidation, and smart strategies
"""

import functools
import hashlib
import json
from typing import Optional, Any, Callable, List
import logging
from .redis_client import redis_manager

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Advanced caching with:
    - Decorator for easy caching
    - TTL strategies (fixed, sliding, smart)
    - Cache invalidation patterns
    - Cache warming
    - Statistics tracking
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client or redis_manager
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate deterministic cache key from function arguments"""
        # Create string representation of args and kwargs
        key_parts = [prefix]

        if args:
            key_parts.extend([str(arg) for arg in args])

        if kwargs:
            # Sort kwargs for deterministic key
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(json.dumps(sorted_kwargs, sort_keys=True))

        # Join and hash if too long
        key_str = ":".join(key_parts)
        if len(key_str) > 200:
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            return f"{prefix}:{key_hash}"

        return key_str

    def cached(
        self,
        ttl: int = 300,  # 5 minutes default
        prefix: Optional[str] = None,
        key_builder: Optional[Callable] = None
    ):
        """
        Decorator for caching function results

        Args:
            ttl: Time to live in seconds
            prefix: Cache key prefix (defaults to function name)
            key_builder: Custom function to build cache key

        Example:
            @cache_manager.cached(ttl=600)
            async def get_user(user_id: str):
                return await db.get_user(user_id)
        """
        def decorator(func: Callable):
            func_prefix = prefix or f"cache:{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    cache_key = self.cache_key(func_prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = await self.redis.get(cache_key)
                if cached_value is not None:
                    self.stats["hits"] += 1
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached_value

                # Cache miss - execute function
                self.stats["misses"] += 1
                logger.debug(f"Cache MISS: {cache_key}")

                result = await func(*args, **kwargs)

                # Store in cache
                if result is not None:
                    await self.redis.set(cache_key, result, ttl)
                    self.stats["sets"] += 1

                return result

            # Add invalidation method to function
            async def invalidate(*args, **kwargs):
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    cache_key = self.cache_key(func_prefix, *args, **kwargs)
                await self.redis.delete(cache_key)
                self.stats["deletes"] += 1

            wrapper.invalidate = invalidate
            return wrapper

        return decorator

    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: int = 300
    ) -> Any:
        """
        Get from cache or compute and set

        Args:
            key: Cache key
            factory: Async function to call if cache miss
            ttl: Time to live in seconds
        """
        # Try cache first
        value = await self.redis.get(key)
        if value is not None:
            self.stats["hits"] += 1
            return value

        # Cache miss - compute value
        self.stats["misses"] += 1
        value = await factory()

        # Store in cache
        if value is not None:
            await self.redis.set(key, value, ttl)
            self.stats["sets"] += 1

        return value

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern

        Example: invalidate_pattern("user:123:*")
        """
        count = await self.redis.delete_pattern(pattern)
        self.stats["deletes"] += count
        return count

    async def warm_cache(
        self,
        keys_and_factories: List[tuple[str, Callable, int]]
    ):
        """
        Pre-populate cache with multiple keys

        Args:
            keys_and_factories: List of (key, factory_func, ttl) tuples

        Example:
            await cache.warm_cache([
                ("top_users", get_top_users, 3600),
                ("recent_posts", get_recent_posts, 1800)
            ])
        """
        logger.info(f"Warming cache with {len(keys_and_factories)} keys...")

        for key, factory, ttl in keys_and_factories:
            try:
                value = await factory()
                await self.redis.set(key, value, ttl)
                self.stats["sets"] += 1
                logger.debug(f"Cache warmed: {key}")
            except Exception as e:
                logger.error(f"Failed to warm cache for {key}: {e}")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.2f}%"
        }

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }


# Global instance
cache_manager = CacheManager()


# Common cache strategies

class CacheStrategies:
    """Pre-defined caching strategies for common use cases"""

    # User data: 5 minutes
    USER_CACHE_TTL = 300

    # Organization data: 10 minutes
    ORG_CACHE_TTL = 600

    # Static/reference data: 1 hour
    STATIC_CACHE_TTL = 3600

    # Expensive queries: 15 minutes
    EXPENSIVE_QUERY_TTL = 900

    # Real-time data: 30 seconds
    REALTIME_CACHE_TTL = 30

    # Long-lived config: 1 day
    CONFIG_CACHE_TTL = 86400


# Convenience decorators with pre-configured TTLs

def cache_user(ttl: int = CacheStrategies.USER_CACHE_TTL):
    """Cache user data"""
    return cache_manager.cached(ttl=ttl, prefix="user")


def cache_org(ttl: int = CacheStrategies.ORG_CACHE_TTL):
    """Cache organization data"""
    return cache_manager.cached(ttl=ttl, prefix="org")


def cache_query(ttl: int = CacheStrategies.EXPENSIVE_QUERY_TTL):
    """Cache expensive query results"""
    return cache_manager.cached(ttl=ttl, prefix="query")
