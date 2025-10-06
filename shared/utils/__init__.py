"""Utilities module for logging, metrics, validators, and parallel processing."""

from shared.utils.logging import StructuredLogger, get_logger, setup_logging
from shared.utils.metrics import (
    MetricsCollector,
    track_request_duration,
    track_database_query,
    track_cache_hit
)
from shared.utils.validators import (
    validate_email,
    validate_tenant_id,
    validate_date_range,
    validate_url
)
from shared.utils.parallel import (
    parallel_map,
    batched_process,
    gather_with_semaphore,
    parallel_map_with_progress,
    OperationResult,
    OperationStatus,
    BulkOperationReport,
    ProgressTracker
)

__all__ = [
    "StructuredLogger",
    "get_logger",
    "setup_logging",
    "MetricsCollector",
    "track_request_duration",
    "track_database_query",
    "track_cache_hit",
    "validate_email",
    "validate_tenant_id",
    "validate_date_range",
    "validate_url",
    "parallel_map",
    "batched_process",
    "gather_with_semaphore",
    "parallel_map_with_progress",
    "OperationResult",
    "OperationStatus",
    "BulkOperationReport",
    "ProgressTracker",
]
