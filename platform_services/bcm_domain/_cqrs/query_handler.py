"""
Query Handler - CQRS Read Side
===============================

Handles queries (read operations) from optimized projections.

Features:
- Read from denormalized projections
- Redis caching
- Query optimization
- No business logic (just data retrieval)

Query Flow:
    1. Receive query
    2. Check cache
    3. Query projection (read model)
    4. Cache result
    5. Return data

Architecture:
    Query → Cache Check → Read Model → Cache Update → Result
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar
from functools import wraps
import redis.asyncio as redis

from .projection_builder import ProjectionBuilder

logger = logging.getLogger(__name__)

TQuery = TypeVar('TQuery', bound='Query')
TResult = TypeVar('TResult')


@dataclass
class Query(ABC):
    """
    Base Query class.

    All queries must inherit from this class.

    Attributes:
        query_id: Unique query identifier
        tenant_id: Tenant identifier
        cache_ttl: Cache TTL in seconds (None = no cache)

    Example:
        ```python
        @dataclass
        class GetBIAProcessesQuery(Query):
            criticality: Optional[str] = None
            status: Optional[str] = None
            limit: int = 100
            offset: int = 0
        ```
    """
    query_id: str = field(default_factory=lambda: f"qry_{datetime.utcnow().timestamp()}")
    tenant_id: str = ""
    cache_ttl: Optional[int] = 300  # 5 minutes default


@dataclass
class QueryResult:
    """
    Query result wrapper.

    Attributes:
        success: Whether query succeeded
        data: Query result data
        count: Number of results
        cached: Whether result from cache
        error: Error message if failed
    """
    success: bool
    data: Any = None
    count: int = 0
    cached: bool = False
    error: Optional[str] = None


def cached_query(ttl: int = 300):
    """
    Decorator for caching query results.

    Args:
        ttl: Cache TTL in seconds

    Example:
        ```python
        @cached_query(ttl=600)
        async def get_bia_processes(self, query):
            # Query logic
            return processes
        ```
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, query: Query, *args, **kwargs):
            # Generate cache key
            cache_key = self._generate_cache_key(query, func.__name__)

            # Try cache
            if self.redis and query.cache_ttl:
                try:
                    cached_data = await self.redis.get(cache_key)
                    if cached_data:
                        logger.debug(f"Cache HIT: {cache_key}")
                        data = json.loads(cached_data)
                        return QueryResult(
                            success=True,
                            data=data,
                            count=len(data) if isinstance(data, list) else 1,
                            cached=True
                        )
                except Exception as e:
                    logger.warning(f"Cache read error: {e}")

            # Execute query
            try:
                result = await func(self, query, *args, **kwargs)

                # Cache result
                if self.redis and query.cache_ttl:
                    try:
                        cache_ttl = query.cache_ttl or ttl
                        await self.redis.setex(
                            cache_key,
                            cache_ttl,
                            json.dumps(result, default=str)
                        )
                        logger.debug(f"Cache SET: {cache_key} (TTL: {cache_ttl}s)")
                    except Exception as e:
                        logger.warning(f"Cache write error: {e}")

                return QueryResult(
                    success=True,
                    data=result,
                    count=len(result) if isinstance(result, list) else 1,
                    cached=False
                )

            except Exception as e:
                logger.error(f"Query error: {e}", exc_info=True)
                return QueryResult(
                    success=False,
                    error=str(e)
                )

        return wrapper
    return decorator


class QueryHandler:
    """
    Query Handler for CQRS read operations.

    Queries optimized projections with Redis caching.

    Example:
        ```python
        # Initialize
        query_handler = QueryHandler(
            projection_builder=projection_builder,
            redis_url="redis://localhost:6379/0"
        )

        # Execute query
        query = GetBIAProcessesQuery(
            tenant_id="tenant_123",
            criticality="CRITICAL"
        )

        result = await query_handler.handle(query)

        if result.success:
            for process in result.data:
                print(process["name"])
        ```
    """

    def __init__(
        self,
        projection_builder: ProjectionBuilder,
        redis_url: str = "redis://localhost:6379/0"
    ):
        """
        Initialize Query Handler.

        Args:
            projection_builder: Projection builder for accessing read models
            redis_url: Redis connection URL
        """
        self.projection_builder = projection_builder
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self._cache_hits = 0
        self._cache_misses = 0

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False
            )
            await self.redis.ping()
            logger.info("Query Handler connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.redis = None

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Query Handler Redis connection closed")

    def _generate_cache_key(self, query: Query, query_name: str) -> str:
        """
        Generate cache key for query.

        Args:
            query: Query object
            query_name: Query method name

        Returns:
            Cache key string
        """
        # Convert query to dict
        query_dict = {
            k: v for k, v in query.__dict__.items()
            if k not in ["query_id", "cache_ttl"]
        }

        # Sort for consistent keys
        query_str = json.dumps(query_dict, sort_keys=True, default=str)

        # Create key
        return f"cqrs:query:{query_name}:{hash(query_str)}"

    async def invalidate_cache(
        self,
        pattern: str = "*",
        tenant_id: Optional[str] = None
    ) -> int:
        """
        Invalidate cache by pattern.

        Args:
            pattern: Redis key pattern
            tenant_id: Optional tenant filter

        Returns:
            Number of keys deleted

        Example:
            ```python
            # Invalidate all BIA queries for tenant
            await query_handler.invalidate_cache(
                pattern="cqrs:query:get_bia_*",
                tenant_id="tenant_123"
            )
            ```
        """
        if not self.redis:
            return 0

        try:
            full_pattern = f"cqrs:query:{pattern}"
            if tenant_id:
                full_pattern = f"{full_pattern}:*{tenant_id}*"

            # Scan for keys
            deleted = 0
            async for key in self.redis.scan_iter(match=full_pattern):
                await self.redis.delete(key)
                deleted += 1

            logger.info(f"Invalidated {deleted} cache keys matching {full_pattern}")
            return deleted

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache stats dictionary

        Example:
            ```python
            stats = await query_handler.get_cache_stats()
            print(f"Hit rate: {stats['hit_rate']:.2%}")
            ```
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "total_queries": total,
            "hit_rate": hit_rate
        }

    # Example Query Methods

    @cached_query(ttl=300)
    async def get_bia_processes(
        self,
        query: 'GetBIAProcessesQuery'
    ) -> List[Dict[str, Any]]:
        """
        Get BIA processes list.

        Args:
            query: GetBIAProcessesQuery

        Returns:
            List of BIA processes

        Example:
            ```python
            query = GetBIAProcessesQuery(
                tenant_id="tenant_123",
                criticality="CRITICAL",
                limit=50
            )
            result = await query_handler.get_bia_processes(query)
            ```
        """
        async with self.projection_builder.pool.acquire() as conn:
            # Build dynamic query
            where_clauses = ["tenant_id = $1"]
            params = [query.tenant_id]
            param_count = 1

            if query.criticality:
                param_count += 1
                where_clauses.append(f"criticality = ${param_count}")
                params.append(query.criticality)

            if query.status:
                param_count += 1
                where_clauses.append(f"status = ${param_count}")
                params.append(query.status)

            where_clause = " AND ".join(where_clauses)

            # Execute query
            sql = f"""
                SELECT id, tenant_id, name, criticality, rto_hours,
                       rpo_hours, mtpd_hours, status, created_at, updated_at
                FROM read_bia_processes
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_count + 1} OFFSET ${param_count + 2}
            """
            params.extend([query.limit, query.offset])

            rows = await conn.fetch(sql, *params)

            return [dict(row) for row in rows]

    @cached_query(ttl=600)
    async def get_bia_process_detail(
        self,
        query: 'GetBIAProcessDetailQuery'
    ) -> Optional[Dict[str, Any]]:
        """
        Get single BIA process details.

        Args:
            query: GetBIAProcessDetailQuery

        Returns:
            BIA process details or None

        Example:
            ```python
            query = GetBIAProcessDetailQuery(
                tenant_id="tenant_123",
                process_id="bia_123"
            )
            result = await query_handler.get_bia_process_detail(query)
            ```
        """
        async with self.projection_builder.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT id, tenant_id, name, criticality, rto_hours,
                       rpo_hours, mtpd_hours, status, created_at, updated_at
                FROM read_bia_processes
                WHERE id = $1 AND tenant_id = $2
            """, query.process_id, query.tenant_id)

            return dict(row) if row else None

    @cached_query(ttl=300)
    async def get_bia_summary(
        self,
        query: 'GetBIASummaryQuery'
    ) -> Optional[Dict[str, Any]]:
        """
        Get BIA summary statistics.

        Args:
            query: GetBIASummaryQuery

        Returns:
            Summary statistics

        Example:
            ```python
            query = GetBIASummaryQuery(tenant_id="tenant_123")
            result = await query_handler.get_bia_summary(query)
            print(f"Total processes: {result['total_processes']}")
            ```
        """
        async with self.projection_builder.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT tenant_id, total_processes, critical_count,
                       high_count, medium_count, low_count,
                       completed_count, draft_count, avg_rto_hours, updated_at
                FROM read_bia_summary
                WHERE tenant_id = $1
            """, query.tenant_id)

            return dict(row) if row else None

    @cached_query(ttl=300)
    async def get_critical_processes(
        self,
        query: 'GetCriticalProcessesQuery'
    ) -> List[Dict[str, Any]]:
        """
        Get critical BIA processes.

        Args:
            query: GetCriticalProcessesQuery

        Returns:
            List of critical processes

        Example:
            ```python
            query = GetCriticalProcessesQuery(
                tenant_id="tenant_123",
                limit=20
            )
            result = await query_handler.get_critical_processes(query)
            ```
        """
        async with self.projection_builder.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, tenant_id, name, criticality, rto_hours,
                       rpo_hours, mtpd_hours, status
                FROM read_bia_processes
                WHERE tenant_id = $1
                  AND criticality IN ('CRITICAL', 'HIGH')
                  AND status = 'COMPLETED'
                ORDER BY
                    CASE criticality
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                    END,
                    rto_hours ASC
                LIMIT $2
            """, query.tenant_id, query.limit)

            return [dict(row) for row in rows]

    async def handle(
        self,
        query: Query,
        handler_method: Optional[str] = None
    ) -> QueryResult:
        """
        Generic query handler.

        Args:
            query: Query object
            handler_method: Method name to call (auto-detected if None)

        Returns:
            QueryResult

        Example:
            ```python
            query = GetBIAProcessesQuery(tenant_id="tenant_123")
            result = await query_handler.handle(query)

            # Or specify handler
            result = await query_handler.handle(
                query,
                handler_method="get_bia_processes"
            )
            ```
        """
        # Auto-detect handler method
        if not handler_method:
            query_type = type(query).__name__
            handler_method = self._infer_handler_method(query_type)

        # Get handler
        handler = getattr(self, handler_method, None)
        if not handler:
            return QueryResult(
                success=False,
                error=f"No handler found for {handler_method}"
            )

        # Execute
        try:
            return await handler(query)
        except Exception as e:
            logger.error(f"Query handler error: {e}", exc_info=True)
            return QueryResult(
                success=False,
                error=str(e)
            )

    def _infer_handler_method(self, query_type: str) -> str:
        """
        Infer handler method from query type.

        Example:
            GetBIAProcessesQuery → get_bia_processes
        """
        # Remove "Query" suffix
        if query_type.endswith("Query"):
            query_type = query_type[:-5]

        # Convert to snake_case
        import re
        method_name = re.sub(r'(?<!^)(?=[A-Z])', '_', query_type).lower()

        return method_name


# Example Query Classes

@dataclass
class GetBIAProcessesQuery(Query):
    """Query for listing BIA processes."""
    criticality: Optional[str] = None
    status: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass
class GetBIAProcessDetailQuery(Query):
    """Query for single BIA process."""
    process_id: str = ""


@dataclass
class GetBIASummaryQuery(Query):
    """Query for BIA summary statistics."""
    pass


@dataclass
class GetCriticalProcessesQuery(Query):
    """Query for critical processes."""
    limit: int = 20
