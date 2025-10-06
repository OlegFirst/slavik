"""
Structured Logging
==================

JSON structured logging for BCM Platform services.

Features:
- JSON structured output
- Service context in every log
- Log levels (info, error, warning, debug)
- Request ID tracking
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional


class StructuredLogger:
    """
    Structured JSON logger.

    Outputs logs in JSON format with consistent structure.

    Example:
        ```python
        logger = StructuredLogger("validation-service")

        logger.info("Exercise created", extra={
            "exercise_id": 123,
            "tenant_id": "tenant456",
            "exercise_type": "tabletop"
        })

        # Output:
        # {
        #     "timestamp": "2025-10-03T10:30:00.123Z",
        #     "service": "validation-service",
        #     "level": "INFO",
        #     "message": "Exercise created",
        #     "exercise_id": 123,
        #     "tenant_id": "tenant456",
        #     "exercise_type": "tabletop"
        # }
        ```
    """

    def __init__(self, service_name: str, default_context: Optional[Dict[str, Any]] = None):
        """
        Initialize structured logger.

        Args:
            service_name: Name of the service
            default_context: Default context to include in all logs
        """
        self.service_name = service_name
        self.default_context = default_context or {}
        self.logger = logging.getLogger(service_name)

        # Configure handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log(self, level: str, message: str, **kwargs) -> None:
        """
        Log message with additional context.

        Args:
            level: Log level (info, error, warning, debug)
            message: Log message
            **kwargs: Additional context fields
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "level": level.upper(),
            "message": message,
            **self.default_context,
            **kwargs
        }

        # Convert to JSON
        log_json = json.dumps(log_entry, default=str)

        # Log using appropriate level
        log_level = getattr(logging, level.upper())
        self.logger.log(log_level, log_json)

    def info(self, message: str, **kwargs) -> None:
        """
        Log info message.

        Example:
            ```python
            logger.info("Processing complete", items_processed=150, duration_ms=234)
            ```
        """
        self.log("info", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """
        Log error message.

        Example:
            ```python
            logger.error("Database query failed", error=str(e), query="SELECT...")
            ```
        """
        self.log("error", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """
        Log warning message.

        Example:
            ```python
            logger.warning("Cache miss", cache_key="user:123")
            ```
        """
        self.log("warning", message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """
        Log debug message.

        Example:
            ```python
            logger.debug("Request received", path="/api/exercises", method="POST")
            ```
        """
        self.log("debug", message, **kwargs)

    def with_context(self, **context) -> "StructuredLogger":
        """
        Create a new logger with additional default context.

        Args:
            **context: Additional context fields

        Returns:
            StructuredLogger: New logger with extended context

        Example:
            ```python
            request_logger = logger.with_context(
                request_id="req_123",
                user_id="user_456"
            )
            request_logger.info("Processing request")
            # Output includes request_id and user_id
            ```
        """
        new_context = {**self.default_context, **context}
        return StructuredLogger(self.service_name, new_context)


# Global logger registry
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(service_name: str, **default_context) -> StructuredLogger:
    """
    Get or create logger for service.

    Args:
        service_name: Name of the service
        **default_context: Default context for all logs

    Returns:
        StructuredLogger: Logger instance

    Example:
        ```python
        logger = get_logger("validation-service")
        logger.info("Service started")
        ```
    """
    if service_name not in _loggers:
        _loggers[service_name] = StructuredLogger(service_name, default_context)
    return _loggers[service_name]


def setup_logging(service_name: str, log_level: str = "INFO") -> None:
    """
    Setup logging configuration for a service.

    Configures Python's built-in logging and creates a structured logger.

    Args:
        service_name: Name of the service
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        ```python
        setup_logging("learning-service", "INFO")
        logger = get_logger("learning-service")
        logger.info("Service initialized")
        ```
    """
    import sys

    # Convert string log level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(message)s',  # StructuredLogger handles formatting
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Create and configure service logger
    logger = get_logger(service_name)
    logger.logger.setLevel(level)

    # Set level for all existing loggers
    for existing_logger in _loggers.values():
        existing_logger.logger.setLevel(level)
