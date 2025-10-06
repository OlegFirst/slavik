"""
Query Profiler - SQLAlchemy Query Performance Monitoring

This module provides tools for profiling SQLAlchemy queries to detect:
- Slow queries
- N+1 query patterns
- Excessive query execution
- Query plan analysis

Usage:
    from shared.database.query_profiler import QueryProfiler, enable_profiling

    # Enable profiling
    enable_profiling(engine, slow_query_threshold_ms=100)

    # Or use context manager for specific code blocks
    with QueryProfiler(engine) as profiler:
        # Execute queries
        result = await session.execute(query)

        # Get report
        report = profiler.get_report()
"""

import logging
import time
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import Pool
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class QueryStats:
    """Statistics for a single query pattern"""

    def __init__(self, query_text: str):
        self.query_text = query_text
        self.execution_count = 0
        self.total_duration_ms = 0.0
        self.min_duration_ms = float('inf')
        self.max_duration_ms = 0.0
        self.first_seen = datetime.utcnow()
        self.last_seen = datetime.utcnow()
        self.execution_times: List[float] = []

    def add_execution(self, duration_ms: float):
        """Record a query execution"""
        self.execution_count += 1
        self.total_duration_ms += duration_ms
        self.min_duration_ms = min(self.min_duration_ms, duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)
        self.last_seen = datetime.utcnow()
        self.execution_times.append(duration_ms)

    @property
    def avg_duration_ms(self) -> float:
        """Calculate average execution time"""
        if self.execution_count == 0:
            return 0.0
        return self.total_duration_ms / self.execution_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "query": self.query_text[:200],  # Truncate for readability
            "execution_count": self.execution_count,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "min_duration_ms": round(self.min_duration_ms, 2),
            "max_duration_ms": round(self.max_duration_ms, 2),
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat()
        }


class QueryProfiler:
    """
    Query profiler for SQLAlchemy async engines.

    Tracks query execution, detects N+1 patterns, and identifies slow queries.
    """

    def __init__(
        self,
        engine: Engine,
        slow_query_threshold_ms: float = 100.0,
        n_plus_one_threshold: int = 10,
        enable_logging: bool = True
    ):
        """
        Initialize query profiler.

        Args:
            engine: SQLAlchemy engine to profile
            slow_query_threshold_ms: Threshold for slow query warnings (ms)
            n_plus_one_threshold: Number of similar queries to trigger N+1 warning
            enable_logging: Whether to log warnings
        """
        self.engine = engine
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.n_plus_one_threshold = n_plus_one_threshold
        self.enable_logging = enable_logging

        # Statistics
        self.query_stats: Dict[str, QueryStats] = {}
        self.query_count = 0
        self.total_duration_ms = 0.0
        self.slow_queries: List[Dict[str, Any]] = []
        self.n_plus_one_warnings: List[Dict[str, Any]] = []

        # Event listeners
        self._listeners_attached = False

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def start(self):
        """Start profiling queries"""
        if not self._listeners_attached:
            event.listen(self.engine, "before_cursor_execute", self._before_cursor_execute)
            event.listen(self.engine, "after_cursor_execute", self._after_cursor_execute)
            self._listeners_attached = True

            if self.enable_logging:
                logger.info("Query profiling started")

    def stop(self):
        """Stop profiling queries"""
        if self._listeners_attached:
            event.remove(self.engine, "before_cursor_execute", self._before_cursor_execute)
            event.remove(self.engine, "after_cursor_execute", self._after_cursor_execute)
            self._listeners_attached = False

            if self.enable_logging:
                logger.info("Query profiling stopped")

    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for pattern matching.

        Removes parameter values to group similar queries.
        """
        # Simple normalization - replace numbers and quoted strings
        import re
        normalized = re.sub(r'\d+', '?', query)
        normalized = re.sub(r"'[^']*'", "'?'", normalized)
        normalized = re.sub(r'"[^"]*"', '"?"', normalized)
        return normalized

    def _before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Event handler before query execution"""
        context._query_start_time = time.perf_counter()

    def _after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Event handler after query execution"""
        if not hasattr(context, '_query_start_time'):
            return

        # Calculate execution time
        duration_ms = (time.perf_counter() - context._query_start_time) * 1000

        # Update global stats
        self.query_count += 1
        self.total_duration_ms += duration_ms

        # Normalize query for pattern matching
        normalized_query = self._normalize_query(statement)

        # Update query-specific stats
        if normalized_query not in self.query_stats:
            self.query_stats[normalized_query] = QueryStats(normalized_query)

        query_stat = self.query_stats[normalized_query]
        query_stat.add_execution(duration_ms)

        # Check for slow query
        if duration_ms > self.slow_query_threshold_ms:
            slow_query_info = {
                "query": statement[:500],
                "duration_ms": round(duration_ms, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.slow_queries.append(slow_query_info)

            if self.enable_logging:
                logger.warning(
                    f"Slow query detected ({duration_ms:.2f}ms > {self.slow_query_threshold_ms}ms): "
                    f"{statement[:200]}"
                )

        # Check for potential N+1 pattern
        if query_stat.execution_count >= self.n_plus_one_threshold:
            # Only warn once per pattern
            if not any(w["pattern"] == normalized_query for w in self.n_plus_one_warnings):
                n_plus_one_info = {
                    "pattern": normalized_query[:200],
                    "execution_count": query_stat.execution_count,
                    "total_duration_ms": round(query_stat.total_duration_ms, 2),
                    "avg_duration_ms": round(query_stat.avg_duration_ms, 2)
                }
                self.n_plus_one_warnings.append(n_plus_one_info)

                if self.enable_logging:
                    logger.warning(
                        f"Potential N+1 query pattern detected: {query_stat.execution_count} executions "
                        f"of similar query (avg {query_stat.avg_duration_ms:.2f}ms): {normalized_query[:200]}"
                    )

    def get_report(self) -> Dict[str, Any]:
        """
        Generate profiling report.

        Returns:
            Dictionary with profiling statistics
        """
        # Sort queries by total duration
        sorted_queries = sorted(
            self.query_stats.values(),
            key=lambda x: x.total_duration_ms,
            reverse=True
        )

        return {
            "summary": {
                "total_queries": self.query_count,
                "total_duration_ms": round(self.total_duration_ms, 2),
                "avg_query_duration_ms": round(
                    self.total_duration_ms / self.query_count if self.query_count > 0 else 0,
                    2
                ),
                "unique_query_patterns": len(self.query_stats),
                "slow_queries_count": len(self.slow_queries),
                "n_plus_one_warnings_count": len(self.n_plus_one_warnings)
            },
            "top_queries_by_duration": [
                q.to_dict() for q in sorted_queries[:10]
            ],
            "slow_queries": self.slow_queries[-10:],  # Last 10 slow queries
            "n_plus_one_warnings": self.n_plus_one_warnings
        }

    def print_report(self):
        """Print formatted profiling report"""
        report = self.get_report()

        print("\n" + "="*80)
        print("QUERY PROFILING REPORT")
        print("="*80)

        print("\nSUMMARY:")
        for key, value in report["summary"].items():
            print(f"  {key}: {value}")

        if report["top_queries_by_duration"]:
            print("\nTOP QUERIES BY TOTAL DURATION:")
            for i, query in enumerate(report["top_queries_by_duration"], 1):
                print(f"\n  {i}. Executions: {query['execution_count']}, "
                      f"Total: {query['total_duration_ms']}ms, "
                      f"Avg: {query['avg_duration_ms']}ms")
                print(f"     {query['query']}")

        if report["n_plus_one_warnings"]:
            print("\nN+1 QUERY WARNINGS:")
            for i, warning in enumerate(report["n_plus_one_warnings"], 1):
                print(f"\n  {i}. Executions: {warning['execution_count']}, "
                      f"Total: {warning['total_duration_ms']}ms")
                print(f"     {warning['pattern']}")

        if report["slow_queries"]:
            print("\nRECENT SLOW QUERIES:")
            for i, slow in enumerate(report["slow_queries"][-5:], 1):
                print(f"\n  {i}. Duration: {slow['duration_ms']}ms at {slow['timestamp']}")
                print(f"     {slow['query'][:200]}")

        print("\n" + "="*80 + "\n")

    def reset(self):
        """Reset profiler statistics"""
        self.query_stats.clear()
        self.query_count = 0
        self.total_duration_ms = 0.0
        self.slow_queries.clear()
        self.n_plus_one_warnings.clear()


# Global profiler instance
_global_profiler: Optional[QueryProfiler] = None


def enable_profiling(
    engine: Engine,
    slow_query_threshold_ms: float = 100.0,
    n_plus_one_threshold: int = 10,
    enable_logging: bool = True
) -> QueryProfiler:
    """
    Enable global query profiling.

    Args:
        engine: SQLAlchemy engine to profile
        slow_query_threshold_ms: Threshold for slow query warnings (ms)
        n_plus_one_threshold: Number of similar queries to trigger N+1 warning
        enable_logging: Whether to log warnings

    Returns:
        QueryProfiler instance
    """
    global _global_profiler

    if _global_profiler is not None:
        _global_profiler.stop()

    _global_profiler = QueryProfiler(
        engine,
        slow_query_threshold_ms=slow_query_threshold_ms,
        n_plus_one_threshold=n_plus_one_threshold,
        enable_logging=enable_logging
    )
    _global_profiler.start()

    return _global_profiler


def disable_profiling():
    """Disable global query profiling"""
    global _global_profiler

    if _global_profiler is not None:
        _global_profiler.stop()
        _global_profiler = None


def get_global_profiler() -> Optional[QueryProfiler]:
    """Get the global profiler instance"""
    return _global_profiler


@contextmanager
def profile_queries(
    engine: Engine,
    slow_query_threshold_ms: float = 100.0,
    n_plus_one_threshold: int = 10,
    print_report: bool = True
):
    """
    Context manager for profiling queries in a specific code block.

    Usage:
        with profile_queries(engine) as profiler:
            # Execute queries
            result = await session.execute(query)
        # Report is automatically printed on exit

    Args:
        engine: SQLAlchemy engine to profile
        slow_query_threshold_ms: Threshold for slow query warnings (ms)
        n_plus_one_threshold: Number of similar queries to trigger N+1 warning
        print_report: Whether to print report on exit

    Yields:
        QueryProfiler instance
    """
    profiler = QueryProfiler(
        engine,
        slow_query_threshold_ms=slow_query_threshold_ms,
        n_plus_one_threshold=n_plus_one_threshold,
        enable_logging=True
    )

    try:
        profiler.start()
        yield profiler
    finally:
        profiler.stop()
        if print_report:
            profiler.print_report()
