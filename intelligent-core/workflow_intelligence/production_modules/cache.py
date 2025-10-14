"""
Redis Caching Layer for Process Framework

Provides caching for:
- Process definitions (rarely change)
- Document templates (rarely change)
- Active process instances (frequently accessed)
- Step execution history (read-heavy)

Reduces database load and improves response times.

Author: AI Platform Team
Date: 2025-10-11
"""

import redis
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import timedelta
from functools import wraps

logger = logging.getLogger(__name__)


# =====================================================
# Cache Configuration
# =====================================================

class CacheConfig:
    """Redis cache configuration"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        max_connections: int = 50
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.max_connections = max_connections


# =====================================================
# Process Framework Cache
# =====================================================

class ProcessFrameworkCache:
    """
    Redis caching layer for Process Framework

    TTL Strategy:
    - Process definitions: 1 hour (rarely change)
    - Document templates: 1 hour (rarely change)
    - Process instances: 5 minutes (actively updated)
    - Step history: 10 minutes (read-heavy, append-only)
    """

    # Cache key prefixes
    PREFIX_PROCESS_DEF = "process:def:"
    PREFIX_PROCESS_INSTANCE = "process:instance:"
    PREFIX_STEP_HISTORY = "process:history:"
    PREFIX_TEMPLATE = "template:"
    PREFIX_ACTIVE_INSTANCES = "process:active"

    # TTL values (seconds)
    TTL_PROCESS_DEF = 3600  # 1 hour
    TTL_TEMPLATE = 3600  # 1 hour
    TTL_INSTANCE = 300  # 5 minutes
    TTL_HISTORY = 600  # 10 minutes

    def __init__(self, config: CacheConfig):
        """Initialize Redis connection pool"""
        try:
            self.redis = redis.Redis(
                host=config.host,
                port=config.port,
                db=config.db,
                password=config.password,
                socket_timeout=config.socket_timeout,
                socket_connect_timeout=config.socket_connect_timeout,
                max_connections=config.max_connections,
                decode_responses=True  # Auto-decode bytes to strings
            )

            # Test connection
            self.redis.ping()
            self.enabled = True
            logger.info(f"Cache initialized: {config.host}:{config.port} (db={config.db})")

        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            self.enabled = False
            self.redis = None

    # =====================================================
    # Process Definitions
    # =====================================================

    def get_process_definition(self, process_id: str) -> Optional[Dict]:
        """Get process definition from cache"""
        if not self.enabled:
            return None

        try:
            key = f"{self.PREFIX_PROCESS_DEF}{process_id}"
            cached = self.redis.get(key)

            if cached:
                logger.debug(f"Cache HIT: process definition {process_id}")
                return json.loads(cached)

            logger.debug(f"Cache MISS: process definition {process_id}")
            return None

        except Exception as e:
            logger.error(f"Cache error getting process {process_id}: {e}")
            return None

    def set_process_definition(self, process_id: str, process_data: Dict):
        """Cache process definition"""
        if not self.enabled:
            return

        try:
            key = f"{self.PREFIX_PROCESS_DEF}{process_id}"
            self.redis.setex(
                key,
                self.TTL_PROCESS_DEF,
                json.dumps(process_data, default=str)
            )
            logger.debug(f"Cached process definition: {process_id}")

        except Exception as e:
            logger.error(f"Cache error setting process {process_id}: {e}")

    def invalidate_process_definition(self, process_id: str):
        """Invalidate cached process definition"""
        if not self.enabled:
            return

        try:
            key = f"{self.PREFIX_PROCESS_DEF}{process_id}"
            self.redis.delete(key)
            logger.debug(f"Invalidated process definition: {process_id}")

        except Exception as e:
            logger.error(f"Cache error invalidating process {process_id}: {e}")

    # =====================================================
    # Process Instances
    # =====================================================

    def get_process_instance(self, instance_id: str) -> Optional[Dict]:
        """Get process instance from cache"""
        if not self.enabled:
            return None

        try:
            key = f"{self.PREFIX_PROCESS_INSTANCE}{instance_id}"
            cached = self.redis.get(key)

            if cached:
                logger.debug(f"Cache HIT: instance {instance_id}")
                return json.loads(cached)

            logger.debug(f"Cache MISS: instance {instance_id}")
            return None

        except Exception as e:
            logger.error(f"Cache error getting instance {instance_id}: {e}")
            return None

    def set_process_instance(self, instance_id: str, instance_data: Dict):
        """Cache process instance"""
        if not self.enabled:
            return

        try:
            key = f"{self.PREFIX_PROCESS_INSTANCE}{instance_id}"
            self.redis.setex(
                key,
                self.TTL_INSTANCE,
                json.dumps(instance_data, default=str)
            )
            logger.debug(f"Cached instance: {instance_id}")

            # Also add to active instances set if status is active
            if instance_data.get("status") == "active":
                self.redis.sadd(self.PREFIX_ACTIVE_INSTANCES, instance_id)

        except Exception as e:
            logger.error(f"Cache error setting instance {instance_id}: {e}")

    def invalidate_process_instance(self, instance_id: str):
        """Invalidate cached process instance"""
        if not self.enabled:
            return

        try:
            key = f"{self.PREFIX_PROCESS_INSTANCE}{instance_id}"
            self.redis.delete(key)

            # Remove from active instances set
            self.redis.srem(self.PREFIX_ACTIVE_INSTANCES, instance_id)

            logger.debug(f"Invalidated instance: {instance_id}")

        except Exception as e:
            logger.error(f"Cache error invalidating instance {instance_id}: {e}")

    def get_active_instances(self) -> List[str]:
        """Get list of active instance IDs"""
        if not self.enabled:
            return []

        try:
            return list(self.redis.smembers(self.PREFIX_ACTIVE_INSTANCES))
        except Exception as e:
            logger.error(f"Cache error getting active instances: {e}")
            return []

    # =====================================================
    # Step History
    # =====================================================

    def get_step_history(self, instance_id: str) -> Optional[List[Dict]]:
        """Get step execution history from cache"""
        if not self.enabled:
            return None

        try:
            key = f"{self.PREFIX_STEP_HISTORY}{instance_id}"
            cached = self.redis.get(key)

            if cached:
                logger.debug(f"Cache HIT: history {instance_id}")
                return json.loads(cached)

            logger.debug(f"Cache MISS: history {instance_id}")
            return None

        except Exception as e:
            logger.error(f"Cache error getting history {instance_id}: {e}")
            return None

    def set_step_history(self, instance_id: str, history: List[Dict]):
        """Cache step execution history"""
        if not self.enabled:
            return

        try:
            key = f"{self.PREFIX_STEP_HISTORY}{instance_id}"
            self.redis.setex(
                key,
                self.TTL_HISTORY,
                json.dumps(history, default=str)
            )
            logger.debug(f"Cached history: {instance_id}")

        except Exception as e:
            logger.error(f"Cache error setting history {instance_id}: {e}")

    # =====================================================
    # Document Templates
    # =====================================================

    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get document template from cache"""
        if not self.enabled:
            return None

        try:
            key = f"{self.PREFIX_TEMPLATE}{template_id}"
            cached = self.redis.get(key)

            if cached:
                logger.debug(f"Cache HIT: template {template_id}")
                return json.loads(cached)

            logger.debug(f"Cache MISS: template {template_id}")
            return None

        except Exception as e:
            logger.error(f"Cache error getting template {template_id}: {e}")
            return None

    def set_template(self, template_id: str, template_data: Dict):
        """Cache document template"""
        if not self.enabled:
            return

        try:
            key = f"{self.PREFIX_TEMPLATE}{template_id}"
            self.redis.setex(
                key,
                self.TTL_TEMPLATE,
                json.dumps(template_data, default=str)
            )
            logger.debug(f"Cached template: {template_id}")

        except Exception as e:
            logger.error(f"Cache error setting template {template_id}: {e}")

    # =====================================================
    # Utility Methods
    # =====================================================

    def clear_all(self):
        """Clear all Process Framework cache"""
        if not self.enabled:
            return

        try:
            # Find all keys with our prefixes
            patterns = [
                f"{self.PREFIX_PROCESS_DEF}*",
                f"{self.PREFIX_PROCESS_INSTANCE}*",
                f"{self.PREFIX_STEP_HISTORY}*",
                f"{self.PREFIX_TEMPLATE}*",
                self.PREFIX_ACTIVE_INSTANCES
            ]

            deleted = 0
            for pattern in patterns:
                keys = self.redis.keys(pattern)
                if keys:
                    deleted += self.redis.delete(*keys)

            logger.info(f"Cleared cache: {deleted} keys deleted")

        except Exception as e:
            logger.error(f"Cache error clearing all: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.redis.info()

            # Count keys by prefix
            key_counts = {}
            for prefix in [self.PREFIX_PROCESS_DEF, self.PREFIX_PROCESS_INSTANCE,
                          self.PREFIX_STEP_HISTORY, self.PREFIX_TEMPLATE]:
                keys = self.redis.keys(f"{prefix}*")
                key_counts[prefix] = len(keys)

            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "key_counts": key_counts,
                "active_instances": len(self.get_active_instances()),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }

        except Exception as e:
            logger.error(f"Cache error getting stats: {e}")
            return {"enabled": False, "error": str(e)}

    def health_check(self) -> bool:
        """Check if cache is healthy"""
        if not self.enabled:
            return False

        try:
            self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False


# =====================================================
# Cache Decorators
# =====================================================

def cached(cache_key_func: callable, ttl: int = 300):
    """
    Decorator for caching function results

    Args:
        cache_key_func: Function to generate cache key from args
        ttl: Time to live in seconds

    Usage:
        @cached(lambda process_id: f"process:{process_id}", ttl=3600)
        def get_process(process_id):
            # expensive database query
            return process_data
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get cache instance (assumes it's passed or available globally)
            cache = kwargs.get("cache") or globals().get("_cache")

            if not cache or not cache.enabled:
                # Cache not available, execute function
                return func(*args, **kwargs)

            # Generate cache key
            try:
                key = cache_key_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error generating cache key: {e}")
                return func(*args, **kwargs)

            # Try to get from cache
            try:
                cached_value = cache.redis.get(key)
                if cached_value:
                    logger.debug(f"Cache HIT: {key}")
                    return json.loads(cached_value)
            except Exception as e:
                logger.error(f"Cache read error: {e}")

            # Cache miss - execute function
            logger.debug(f"Cache MISS: {key}")
            result = func(*args, **kwargs)

            # Store in cache
            try:
                cache.redis.setex(key, ttl, json.dumps(result, default=str))
            except Exception as e:
                logger.error(f"Cache write error: {e}")

            return result

        return wrapper

    return decorator


# =====================================================
# Singleton Instance
# =====================================================

_cache: Optional[ProcessFrameworkCache] = None


def get_cache() -> Optional[ProcessFrameworkCache]:
    """Get global cache instance"""
    return _cache


def init_cache(config: CacheConfig) -> ProcessFrameworkCache:
    """Initialize global cache instance"""
    global _cache
    _cache = ProcessFrameworkCache(config)
    logger.info("Process Framework cache initialized")
    return _cache


def close_cache():
    """Close global cache instance"""
    global _cache
    if _cache and _cache.redis:
        _cache.redis.close()
        _cache = None
        logger.info("Process Framework cache closed")
