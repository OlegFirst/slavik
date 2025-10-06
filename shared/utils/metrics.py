"""
Prometheus Metrics
==================

Metrics collection for BCM Platform services.

Features:
- Request duration tracking
- Database query metrics
- Cache hit/miss tracking
- Custom business metrics
"""

from typing import Optional, Callable
from functools import wraps
import time
from prometheus_client import Counter, Histogram, Gauge, Summary


class MetricsCollector:
    """
    Metrics collector for Prometheus.

    Provides common metrics for BCM Platform services.

    Example:
        ```python
        metrics = MetricsCollector("validation")

        # Track request
        with metrics.track_request("POST", "/exercises"):
            result = await create_exercise(data)

        # Track database query
        with metrics.track_query("insert", "exercises"):
            await db.execute(query)
        ```
    """

    def __init__(self, service_name: str):
        """
        Initialize metrics collector.

        Args:
            service_name: Name of the service
        """
        self.service_name = service_name

        # HTTP request metrics
        self.request_count = Counter(
            f"{service_name}_http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"]
        )

        self.request_duration = Histogram(
            f"{service_name}_http_request_duration_seconds",
            "HTTP request duration",
            ["method", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]
        )

        # Database metrics
        self.db_query_count = Counter(
            f"{service_name}_db_queries_total",
            "Total database queries",
            ["operation", "table"]
        )

        self.db_query_duration = Histogram(
            f"{service_name}_db_query_duration_seconds",
            "Database query duration",
            ["operation", "table"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
        )

        # Cache metrics
        self.cache_hits = Counter(
            f"{service_name}_cache_hits_total",
            "Total cache hits",
            ["cache_key_prefix"]
        )

        self.cache_misses = Counter(
            f"{service_name}_cache_misses_total",
            "Total cache misses",
            ["cache_key_prefix"]
        )

        # Business metrics
        self.business_events = Counter(
            f"{service_name}_business_events_total",
            "Total business events",
            ["event_type", "entity"]
        )

        # Active connections
        self.active_connections = Gauge(
            f"{service_name}_active_connections",
            "Active connections",
            ["connection_type"]
        )

    def track_request(self, method: str, endpoint: str, status: int = 200):
        """
        Track HTTP request.

        Example:
            ```python
            with metrics.track_request("POST", "/exercises", 201):
                result = await create_exercise(data)
            ```
        """
        class RequestTracker:
            def __init__(self, collector, method, endpoint, status):
                self.collector = collector
                self.method = method
                self.endpoint = endpoint
                self.status = status
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time
                self.collector.request_duration.labels(
                    method=self.method,
                    endpoint=self.endpoint
                ).observe(duration)
                self.collector.request_count.labels(
                    method=self.method,
                    endpoint=self.endpoint,
                    status=self.status
                ).inc()

        return RequestTracker(self, method, endpoint, status)

    def track_query(self, operation: str, table: str):
        """
        Track database query.

        Example:
            ```python
            with metrics.track_query("select", "exercises"):
                result = await db.execute(query)
            ```
        """
        class QueryTracker:
            def __init__(self, collector, operation, table):
                self.collector = collector
                self.operation = operation
                self.table = table
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time
                self.collector.db_query_duration.labels(
                    operation=self.operation,
                    table=self.table
                ).observe(duration)
                self.collector.db_query_count.labels(
                    operation=self.operation,
                    table=self.table
                ).inc()

        return QueryTracker(self, operation, table)


# Decorator functions for easier usage

def track_request_duration(service_name: str, endpoint: str):
    """
    Decorator to track request duration.

    Example:
        ```python
        @track_request_duration("validation", "/exercises")
        async def create_exercise(exercise_data):
            ...
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # Record metric here
                pass
        return wrapper
    return decorator


def track_database_query(operation: str, table: str):
    """
    Decorator to track database query performance.

    Example:
        ```python
        @track_database_query("select", "exercises")
        async def get_exercises(tenant_id):
            ...
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # Record metric here
                pass
        return wrapper
    return decorator


def track_cache_hit(cache_key_prefix: str, hit: bool):
    """
    Track cache hit/miss.

    Example:
        ```python
        cached_value = await cache.get(key)
        if cached_value:
            track_cache_hit("exercises", hit=True)
        else:
            track_cache_hit("exercises", hit=False)
        ```
    """
    # Record metric here
    pass
