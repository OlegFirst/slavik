"""
Error Handling and Retry Logic for Process Framework

Provides:
- Custom exception classes
- Retry decorators for transient failures
- Error classification
- Logging and monitoring integration

Author: AI Platform Team
Date: 2025-10-11
"""

from typing import Optional, Callable, Type, Tuple, Any
from functools import wraps
import time
import logging
from datetime import datetime
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)

logger = logging.getLogger(__name__)


# =====================================================
# Custom Exceptions
# =====================================================

class ProcessFrameworkError(Exception):
    """Base exception for Process Framework"""
    pass


class ProcessNotFoundError(ProcessFrameworkError):
    """Process definition not found"""
    pass


class ProcessInstanceNotFoundError(ProcessFrameworkError):
    """Process instance not found"""
    pass


class ValidationError(ProcessFrameworkError):
    """Form validation failed"""

    def __init__(self, errors: dict):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")


class StepExecutionError(ProcessFrameworkError):
    """Step execution failed"""

    def __init__(self, step_id: str, reason: str):
        self.step_id = step_id
        self.reason = reason
        super().__init__(f"Step {step_id} execution failed: {reason}")


class DatabaseError(ProcessFrameworkError):
    """Database operation failed"""
    pass


class TransientDatabaseError(DatabaseError):
    """Transient database error (can be retried)"""
    pass


class PermanentDatabaseError(DatabaseError):
    """Permanent database error (should not retry)"""
    pass


class AIServiceError(ProcessFrameworkError):
    """AI service error"""
    pass


class TransientAIServiceError(AIServiceError):
    """Transient AI service error (can be retried)"""
    pass


class AuthorizationError(ProcessFrameworkError):
    """User not authorized for operation"""

    def __init__(self, user: str, operation: str):
        self.user = user
        self.operation = operation
        super().__init__(f"User {user} not authorized for {operation}")


class ProcessStateError(ProcessFrameworkError):
    """Invalid process state for operation"""

    def __init__(self, current_state: str, required_state: str):
        self.current_state = current_state
        self.required_state = required_state
        super().__init__(
            f"Process in state '{current_state}', required '{required_state}'"
        )


# =====================================================
# Error Classification
# =====================================================

def is_transient_error(exception: Exception) -> bool:
    """
    Determine if error is transient and can be retried

    Transient errors:
    - Network timeouts
    - Database connection errors
    - AI service temporary unavailability
    - Rate limiting

    Permanent errors:
    - Validation errors
    - Authorization errors
    - Data integrity violations
    """
    transient_types = (
        TransientDatabaseError,
        TransientAIServiceError,
        TimeoutError,
        ConnectionError
    )

    permanent_types = (
        ValidationError,
        AuthorizationError,
        ProcessNotFoundError,
        ProcessInstanceNotFoundError,
        PermanentDatabaseError
    )

    if isinstance(exception, permanent_types):
        return False

    if isinstance(exception, transient_types):
        return True

    # Check error message for common transient indicators
    error_msg = str(exception).lower()
    transient_indicators = [
        "timeout",
        "connection",
        "unavailable",
        "rate limit",
        "too many requests",
        "service unavailable",
        "gateway timeout"
    ]

    return any(indicator in error_msg for indicator in transient_indicators)


# =====================================================
# Retry Decorators
# =====================================================

def retry_on_transient_error(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    exponential_base: int = 2
):
    """
    Retry decorator for transient errors

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        exponential_base: Base for exponential backoff

    Usage:
        @retry_on_transient_error(max_attempts=3)
        def my_function():
            # code that might fail transiently
    """

    def should_retry(exception):
        should = is_transient_error(exception)
        if should:
            logger.warning(f"Transient error detected, will retry: {exception}")
        else:
            logger.error(f"Permanent error detected, will not retry: {exception}")
        return should

    return retry(
        retry=retry_if_exception_type(Exception) & retry_if_exception(should_retry),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=min_wait,
            min=min_wait,
            max=max_wait,
            exp_base=exponential_base
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )


def retry_database_operation(max_attempts: int = 3):
    """
    Retry decorator specifically for database operations

    Retries on:
    - Connection errors
    - Deadlocks
    - Lock timeouts

    Does not retry on:
    - Constraint violations
    - Data integrity errors
    """

    def is_retryable_db_error(exception):
        if isinstance(exception, TransientDatabaseError):
            return True

        if isinstance(exception, PermanentDatabaseError):
            return False

        # Check psycopg2 error codes
        error_msg = str(exception).lower()
        retryable_patterns = [
            "connection",
            "deadlock",
            "lock timeout",
            "could not serialize",
            "canceling statement due to conflict"
        ]

        return any(pattern in error_msg for pattern in retryable_patterns)

    return retry(
        retry=retry_if_exception(is_retryable_db_error),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


def retry_ai_service_call(max_attempts: int = 3):
    """
    Retry decorator for AI service calls

    Retries on:
    - Service unavailable
    - Rate limiting
    - Timeouts

    Does not retry on:
    - Invalid requests
    - Authorization errors
    """

    def is_retryable_ai_error(exception):
        if isinstance(exception, TransientAIServiceError):
            return True

        error_msg = str(exception).lower()
        retryable_patterns = [
            "rate limit",
            "too many requests",
            "service unavailable",
            "timeout",
            "503",
            "429"
        ]

        return any(pattern in error_msg for pattern in retryable_patterns)

    return retry(
        retry=retry_if_exception(is_retryable_ai_error),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )


# =====================================================
# Circuit Breaker Pattern
# =====================================================

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures

    States:
    - CLOSED: Normal operation
    - OPEN: Failing, reject requests immediately
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection

        Usage:
            circuit_breaker = CircuitBreaker()
            result = circuit_breaker.call(my_function, arg1, arg2)
        """
        if self.state == "OPEN":
            # Check if recovery timeout has passed
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise ProcessFrameworkError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Success - reset circuit breaker
            if self.state == "HALF_OPEN":
                self._reset()
                logger.info("Circuit breaker reset to CLOSED state")

            return result

        except self.expected_exception as e:
            self._record_failure()
            raise

    def _record_failure(self):
        """Record a failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"Circuit breaker OPENED after {self.failure_count} failures"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt to reset circuit"""
        if self.last_failure_time is None:
            return False

        return (time.time() - self.last_failure_time) >= self.recovery_timeout

    def _reset(self):
        """Reset circuit breaker to CLOSED state"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"


# =====================================================
# Error Context Manager
# =====================================================

class ErrorContext:
    """
    Context manager for standardized error handling

    Usage:
        with ErrorContext("executing step", step_id="bia_init"):
            # code that might fail
    """

    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting: {self.operation}", extra=self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        if exc_type is None:
            # Success
            logger.info(
                f"Completed: {self.operation} ({duration:.2f}s)",
                extra=self.context
            )
        else:
            # Error
            logger.error(
                f"Failed: {self.operation} ({duration:.2f}s) - {exc_val}",
                extra=self.context,
                exc_info=True
            )

        # Don't suppress exception
        return False


# =====================================================
# Error Logging and Monitoring
# =====================================================

def log_error_with_context(
    exception: Exception,
    operation: str,
    **context
):
    """
    Log error with full context for debugging

    Args:
        exception: The exception that occurred
        operation: Description of operation being performed
        **context: Additional context (user_id, process_id, etc.)
    """
    error_data = {
        "operation": operation,
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "timestamp": datetime.now().isoformat(),
        "is_transient": is_transient_error(exception),
        **context
    }

    logger.error(
        f"Error in {operation}: {exception}",
        extra=error_data,
        exc_info=True
    )

    # TODO: Send to monitoring system (Sentry, Datadog, etc.)


# =====================================================
# Safe Execution Wrapper
# =====================================================

def safe_execute(
    func: Callable,
    default_value: Any = None,
    log_errors: bool = True,
    operation_name: Optional[str] = None
) -> Tuple[Any, Optional[Exception]]:
    """
    Safely execute function and return (result, error)

    Args:
        func: Function to execute
        default_value: Value to return on error
        log_errors: Whether to log errors
        operation_name: Name for logging

    Returns:
        Tuple of (result, error) where error is None on success

    Usage:
        result, error = safe_execute(lambda: risky_operation())
        if error:
            handle_error(error)
    """
    try:
        result = func()
        return result, None
    except Exception as e:
        if log_errors:
            log_error_with_context(
                e,
                operation_name or "safe_execute",
                function=func.__name__ if hasattr(func, '__name__') else str(func)
            )
        return default_value, e


# =====================================================
# Graceful Degradation
# =====================================================

class GracefulDegradation:
    """
    Helper for graceful degradation when services fail

    Usage:
        degradation = GracefulDegradation()

        # Try primary service
        if not degradation.try_service(primary_service):
            # Fallback to secondary
            degradation.try_service(secondary_service)

        if degradation.all_failed():
            # Use default behavior
            degradation.use_default()
    """

    def __init__(self):
        self.failures = []
        self.success = None

    def try_service(self, func: Callable, *args, **kwargs) -> bool:
        """
        Try to execute service function

        Returns True if successful, False otherwise
        """
        try:
            result = func(*args, **kwargs)
            self.success = result
            return True
        except Exception as e:
            self.failures.append({
                "function": func.__name__,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            logger.warning(f"Service {func.__name__} failed: {e}")
            return False

    def all_failed(self) -> bool:
        """Check if all attempts failed"""
        return self.success is None and len(self.failures) > 0

    def use_default(self, default_value: Any = None):
        """Use default value after all failures"""
        logger.warning(
            f"All services failed ({len(self.failures)} attempts), using default"
        )
        self.success = default_value
        return default_value

    def get_result(self, default: Any = None):
        """Get result or default"""
        return self.success if self.success is not None else default
