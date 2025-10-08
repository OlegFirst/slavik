"""
Redis Cache Implementation

Standalone Redis cache for Digital Twin service
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import timedelta

import redis.asyncio as aioredis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


# ============================================
# REDIS CACHE
# ============================================

class RedisCache:
    """
    Redis Cache

    Standalone async Redis cache for performance optimization
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Redis cache

        Args:
            config: Redis configuration
        """
        self.config = config

        # Connection settings
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 6379)
        self.db = config.get('db', 0)
        self.password = config.get('password')
        self.prefix = config.get('prefix', 'dt:')  # Digital Twin prefix

        # Default TTLs (in seconds)
        self.default_ttl = config.get('default_ttl', 3600)  # 1 hour
        self.ttl_config = {
            'organization': config.get('organization_ttl', 1800),  # 30 min
            'simulation': config.get('simulation_ttl', 3600),  # 1 hour
            'metrics': config.get('metrics_ttl', 300),  # 5 min
            'health_score': config.get('health_score_ttl', 600),  # 10 min
            'prediction': config.get('prediction_ttl', 7200),  # 2 hours
        }

        # Redis client
        self.client: Optional[Redis] = None

        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }

        logger.info(f"Redis Cache initialized: {self.host}:{self.port}/{self.db}")

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        try:
            self.client = await aioredis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.config.get('max_connections', 50)
            )

            # Test connection
            await self.client.ping()

            logger.info("Redis cache connected successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis cache closed")

    def _make_key(self, key_type: str, identifier: str) -> str:
        """
        Make cache key with prefix

        Args:
            key_type: Type of cached object
            identifier: Unique identifier

        Returns:
            Prefixed cache key
        """
        return f"{self.prefix}{key_type}:{identifier}"

    async def get(
        self,
        key_type: str,
        identifier: str,
        default: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key_type: Type of cached object
            identifier: Unique identifier
            default: Default value if not found

        Returns:
            Cached value or default
        """
        if not self.client:
            return default

        key = self._make_key(key_type, identifier)

        try:
            value = await self.client.get(key)

            if value is not None:
                self.stats['hits'] += 1
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            else:
                self.stats['misses'] += 1
                logger.debug(f"Cache miss: {key}")
                return default

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache get error for {key}: {e}")
            return default

    async def set(
        self,
        key_type: str,
        identifier: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key_type: Type of cached object
            identifier: Unique identifier
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)

        Returns:
            True if successful
        """
        if not self.client:
            return False

        key = self._make_key(key_type, identifier)

        # Determine TTL
        if ttl is None:
            ttl = self.ttl_config.get(key_type, self.default_ttl)

        try:
            serialized = json.dumps(value, default=str)  # default=str handles datetime
            await self.client.setex(key, ttl, serialized)

            self.stats['sets'] += 1
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

            return True

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache set error for {key}: {e}", exc_info=True)
            return False

    async def delete(self, key_type: str, identifier: str) -> bool:
        """
        Delete value from cache

        Args:
            key_type: Type of cached object
            identifier: Unique identifier

        Returns:
            True if deleted
        """
        if not self.client:
            return False

        key = self._make_key(key_type, identifier)

        try:
            deleted = await self.client.delete(key)

            if deleted:
                self.stats['deletes'] += 1
                logger.debug(f"Cache delete: {key}")

            return bool(deleted)

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache delete error for {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Pattern to match (e.g., "organization:*")

        Returns:
            Number of keys deleted
        """
        if not self.client:
            return 0

        full_pattern = f"{self.prefix}{pattern}"

        try:
            keys = []
            async for key in self.client.scan_iter(match=full_pattern):
                keys.append(key)

            if keys:
                deleted = await self.client.delete(*keys)
                self.stats['deletes'] += deleted
                logger.info(f"Deleted {deleted} keys matching {full_pattern}")
                return deleted

            return 0

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Cache delete pattern error for {full_pattern}: {e}")
            return 0

    async def exists(self, key_type: str, identifier: str) -> bool:
        """
        Check if key exists

        Args:
            key_type: Type of cached object
            identifier: Unique identifier

        Returns:
            True if exists
        """
        if not self.client:
            return False

        key = self._make_key(key_type, identifier)

        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for {key}: {e}")
            return False

    async def expire(self, key_type: str, identifier: str, ttl: int) -> bool:
        """
        Set expiration on existing key

        Args:
            key_type: Type of cached object
            identifier: Unique identifier
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        if not self.client:
            return False

        key = self._make_key(key_type, identifier)

        try:
            return bool(await self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error for {key}: {e}")
            return False

    # ============================================
    # SPECIALIZED CACHE OPERATIONS
    # ============================================

    async def cache_organization(
        self,
        org_id: str,
        org_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache organization data"""
        return await self.set('organization', org_id, org_data, ttl)

    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get cached organization"""
        return await self.get('organization', org_id)

    async def invalidate_organization(self, org_id: str) -> bool:
        """Invalidate organization cache"""
        return await self.delete('organization', org_id)

    async def cache_simulation(
        self,
        sim_id: str,
        sim_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache simulation result"""
        return await self.set('simulation', sim_id, sim_data, ttl)

    async def get_simulation(self, sim_id: str) -> Optional[Dict[str, Any]]:
        """Get cached simulation"""
        return await self.get('simulation', sim_id)

    async def cache_metrics(
        self,
        twin_id: str,
        metric_name: str,
        metrics_data: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache metrics data"""
        key = f"{twin_id}:{metric_name}"
        return await self.set('metrics', key, metrics_data, ttl)

    async def get_metrics(
        self,
        twin_id: str,
        metric_name: str
    ) -> Optional[Any]:
        """Get cached metrics"""
        key = f"{twin_id}:{metric_name}"
        return await self.get('metrics', key)

    async def cache_health_score(
        self,
        twin_id: str,
        health_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache health score"""
        return await self.set('health_score', twin_id, health_data, ttl)

    async def get_health_score(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get cached health score"""
        return await self.get('health_score', twin_id)

    async def cache_prediction(
        self,
        pred_id: str,
        pred_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Cache prediction"""
        return await self.set('prediction', pred_id, pred_data, ttl)

    async def get_prediction(self, pred_id: str) -> Optional[Dict[str, Any]]:
        """Get cached prediction"""
        return await self.get('prediction', pred_id)

    # ============================================
    # LIST OPERATIONS
    # ============================================

    async def push_to_list(
        self,
        list_key: str,
        value: Any,
        max_length: Optional[int] = None
    ) -> bool:
        """
        Push value to list (left push)

        Args:
            list_key: List key
            value: Value to push
            max_length: Max list length (trim if exceeded)

        Returns:
            True if successful
        """
        if not self.client:
            return False

        key = f"{self.prefix}list:{list_key}"

        try:
            serialized = json.dumps(value, default=str)
            await self.client.lpush(key, serialized)

            # Trim if max_length specified
            if max_length:
                await self.client.ltrim(key, 0, max_length - 1)

            return True

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Push to list error for {key}: {e}")
            return False

    async def get_list(
        self,
        list_key: str,
        start: int = 0,
        end: int = -1
    ) -> List[Any]:
        """
        Get list values

        Args:
            list_key: List key
            start: Start index
            end: End index (-1 = all)

        Returns:
            List of values
        """
        if not self.client:
            return []

        key = f"{self.prefix}list:{list_key}"

        try:
            values = await self.client.lrange(key, start, end)
            return [json.loads(v) for v in values]

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Get list error for {key}: {e}")
            return []

    # ============================================
    # SET OPERATIONS
    # ============================================

    async def add_to_set(self, set_key: str, *values: str) -> bool:
        """
        Add values to set

        Args:
            set_key: Set key
            values: Values to add

        Returns:
            True if successful
        """
        if not self.client or not values:
            return False

        key = f"{self.prefix}set:{set_key}"

        try:
            await self.client.sadd(key, *values)
            return True

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Add to set error for {key}: {e}")
            return False

    async def remove_from_set(self, set_key: str, *values: str) -> bool:
        """
        Remove values from set

        Args:
            set_key: Set key
            values: Values to remove

        Returns:
            True if successful
        """
        if not self.client or not values:
            return False

        key = f"{self.prefix}set:{set_key}"

        try:
            await self.client.srem(key, *values)
            return True

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Remove from set error for {key}: {e}")
            return False

    async def is_in_set(self, set_key: str, value: str) -> bool:
        """
        Check if value is in set

        Args:
            set_key: Set key
            value: Value to check

        Returns:
            True if in set
        """
        if not self.client:
            return False

        key = f"{self.prefix}set:{set_key}"

        try:
            return bool(await self.client.sismember(key, value))
        except Exception as e:
            logger.error(f"Is in set error for {key}: {e}")
            return False

    async def get_set_members(self, set_key: str) -> List[str]:
        """
        Get all set members

        Args:
            set_key: Set key

        Returns:
            List of members
        """
        if not self.client:
            return []

        key = f"{self.prefix}set:{set_key}"

        try:
            members = await self.client.smembers(key)
            return list(members)
        except Exception as e:
            logger.error(f"Get set members error for {key}: {e}")
            return []

    # ============================================
    # HASH OPERATIONS
    # ============================================

    async def set_hash_field(
        self,
        hash_key: str,
        field: str,
        value: Any
    ) -> bool:
        """
        Set hash field value

        Args:
            hash_key: Hash key
            field: Field name
            value: Field value

        Returns:
            True if successful
        """
        if not self.client:
            return False

        key = f"{self.prefix}hash:{hash_key}"

        try:
            serialized = json.dumps(value, default=str)
            await self.client.hset(key, field, serialized)
            return True

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Set hash field error for {key}.{field}: {e}")
            return False

    async def get_hash_field(
        self,
        hash_key: str,
        field: str,
        default: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Get hash field value

        Args:
            hash_key: Hash key
            field: Field name
            default: Default value

        Returns:
            Field value or default
        """
        if not self.client:
            return default

        key = f"{self.prefix}hash:{hash_key}"

        try:
            value = await self.client.hget(key, field)

            if value is not None:
                return json.loads(value)
            return default

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Get hash field error for {key}.{field}: {e}")
            return default

    async def get_hash_all(self, hash_key: str) -> Dict[str, Any]:
        """
        Get all hash fields

        Args:
            hash_key: Hash key

        Returns:
            Dictionary of fields
        """
        if not self.client:
            return {}

        key = f"{self.prefix}hash:{hash_key}"

        try:
            values = await self.client.hgetall(key)
            return {k: json.loads(v) for k, v in values.items()}

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Get hash all error for {key}: {e}")
            return {}

    # ============================================
    # UTILITIES
    # ============================================

    async def clear_all(self) -> bool:
        """
        Clear all cache keys with prefix

        Returns:
            True if successful
        """
        try:
            count = await self.delete_pattern("*")
            logger.info(f"Cleared {count} cache keys")
            return True

        except Exception as e:
            logger.error(f"Clear all error: {e}")
            return False

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Statistics dictionary
        """
        stats = self.stats.copy()

        # Calculate hit rate
        total_requests = stats['hits'] + stats['misses']
        if total_requests > 0:
            stats['hit_rate'] = stats['hits'] / total_requests
        else:
            stats['hit_rate'] = 0.0

        # Get Redis info
        if self.client:
            try:
                info = await self.client.info('stats')
                stats['redis_stats'] = {
                    'total_connections_received': info.get('total_connections_received', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                }
            except Exception as e:
                logger.error(f"Failed to get Redis stats: {e}")

        return stats

    async def health_check(self) -> bool:
        """
        Check Redis connection health

        Returns:
            True if healthy
        """
        if not self.client:
            return False

        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
