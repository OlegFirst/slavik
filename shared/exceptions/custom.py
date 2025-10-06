"""
Custom Exception Classes
=========================

Hierarchical exception classes for BCM Platform.

Exception Hierarchy:
- BCMException (base)
  |- ValidationException (business rule validation failures)
  |- ResourceNotFoundException (resource not found)
  |- DuplicateResourceException (resource already exists)
  |- WorkflowException (invalid workflow transitions)
  |- SecurityException (security violations)
  |- PermissionDeniedException (insufficient permissions)
  |- ExternalServiceException (external service failures)
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Standard error response model.

    Used for consistent error responses across all services.

    Example:
        ```python
        {
            "error_code": "RESOURCE_NOT_FOUND",
            "message": "Exercise with id=123 not found",
            "details": {"exercise_id": 123},
            "timestamp": "2025-10-03T10:30:00Z"
        }
        ```
    """
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": {"field": "email", "error": "Invalid email format"},
                "timestamp": "2025-10-03T10:30:00Z"
            }
        }


class BCMException(Exception):
    """
    Base exception for BCM Platform.

    All custom exceptions should inherit from this class.

    Attributes:
        message: Human-readable error message
        code: Error code for programmatic handling
        details: Additional error context

    Example:
        ```python
        raise BCMException(
            "Failed to create exercise",
            code="EXERCISE_CREATION_FAILED",
            details={"tenant_id": "tenant123", "reason": "Invalid date"}
        )
        ```
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code or self.__class__.__name__.replace("Exception", "").upper()
        self.details = details or {}
        super().__init__(self.message)

    def to_response(self) -> ErrorResponse:
        """
        Convert exception to error response model.

        Returns:
            ErrorResponse: Standardized error response
        """
        return ErrorResponse(
            error_code=self.code,
            message=self.message,
            details=self.details,
            timestamp=datetime.utcnow()
        )

    def __str__(self) -> str:
        if self.details:
            return f"{self.code}: {self.message} | Details: {self.details}"
        return f"{self.code}: {self.message}"


class ValidationException(BCMException):
    """
    Business rule validation failed.

    Raised when input data is valid structurally but violates business rules.

    Example:
        ```python
        # Exercise date in past
        raise ValidationException(
            "Planned date cannot be in the past",
            details={"planned_date": "2024-01-01", "current_date": "2025-10-03"}
        )

        # Invalid KPI thresholds
        raise ValidationException(
            "For higher_better KPIs: critical < warning < target",
            code="INVALID_KPI_THRESHOLDS",
            details={"critical": 90, "warning": 80, "target": 70}
        )
        ```
    """
    pass


class ResourceNotFoundException(BCMException):
    """
    Resource not found.

    Raised when a requested resource doesn't exist.

    Example:
        ```python
        raise ResourceNotFoundException(
            f"Exercise with id={exercise_id} not found",
            details={"exercise_id": exercise_id, "tenant_id": tenant_id}
        )
        ```
    """
    pass


class DuplicateResourceException(BCMException):
    """
    Resource already exists.

    Raised when attempting to create a resource that already exists.

    Example:
        ```python
        raise DuplicateResourceException(
            f"Exercise code {code} already exists",
            details={"exercise_code": code, "existing_id": existing.id}
        )
        ```
    """
    pass


class WorkflowException(BCMException):
    """
    Workflow transition not allowed.

    Raised when an invalid workflow state transition is attempted.

    Example:
        ```python
        # Cannot start completed exercise
        raise WorkflowException(
            "Cannot start exercise in COMPLETED status",
            details={
                "exercise_id": exercise.id,
                "current_status": "COMPLETED",
                "attempted_transition": "start"
            }
        )

        # Cannot approve without review
        raise WorkflowException(
            "Document must be reviewed before approval",
            code="INVALID_APPROVAL_TRANSITION",
            details={"document_id": doc.id, "current_status": "DRAFT"}
        )
        ```
    """
    pass


class SecurityException(BCMException):
    """
    Security violation.

    Raised for security-related issues like malware detection,
    invalid tokens, or suspicious activity.

    Example:
        ```python
        # Malware detected
        raise SecurityException(
            f"Malicious file detected: {threat_name}",
            code="MALWARE_DETECTED",
            details={"file_name": file.filename, "threat": threat_name}
        )

        # File type mismatch
        raise SecurityException(
            "File type mismatch detected",
            details={"declared_type": "pdf", "actual_type": "exe"}
        )
        ```
    """
    pass


class PermissionDeniedException(BCMException):
    """
    User lacks required permission.

    Raised when a user attempts an action they don't have permission for.

    Example:
        ```python
        # Missing permission
        raise PermissionDeniedException(
            f"User lacks permission: {permission}",
            details={
                "user_id": user.id,
                "required_permission": permission,
                "user_role": user.role
            }
        )

        # Tenant access denied
        raise PermissionDeniedException(
            "User does not have access to this tenant",
            code="TENANT_ACCESS_DENIED",
            details={"user_id": user.id, "tenant_id": tenant_id}
        )
        ```
    """
    pass


class ExternalServiceException(BCMException):
    """
    External service failed.

    Raised when communication with external services fails
    (EventBus, AI services, email, etc.).

    Example:
        ```python
        # EventBus connection failed
        raise ExternalServiceException(
            "Failed to publish event to EventBus",
            code="EVENTBUS_PUBLISH_FAILED",
            details={
                "event_type": "exercise.created",
                "error": str(e)
            }
        )

        # OpenAI API failed
        raise ExternalServiceException(
            "AI classification failed",
            code="AI_SERVICE_ERROR",
            details={"service": "OpenAI", "model": "gpt-4", "error": str(e)}
        )
        ```
    """
    pass


class RateLimitException(BCMException):
    """
    Rate limit exceeded.

    Raised when a user or service exceeds allowed request rate.

    Example:
        ```python
        raise RateLimitException(
            "Rate limit exceeded for AI analysis",
            details={
                "limit": "10 requests/minute",
                "retry_after": 45
            }
        )
        ```
    """
    pass


class ConfigurationException(BCMException):
    """
    Configuration error.

    Raised when service configuration is invalid or missing.

    Example:
        ```python
        raise ConfigurationException(
            "Database URL not configured",
            code="MISSING_DATABASE_URL"
        )
        ```
    """
    pass


class EntityNotFoundError(BCMException):
    """
    Entity not found in database.

    Raised when a specific entity (BIA, Assessment, Evidence, etc.) is not found.

    Example:
        ```python
        raise EntityNotFoundError(
            "BIAProcess",
            "process-123",
            details={"tenant_id": "tenant-456"}
        )
        ```
    """

    def __init__(self, entity_type: str, entity_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"{entity_type} with ID {entity_id} not found"
        super().__init__(
            message=message,
            code="ENTITY_NOT_FOUND",
            details={
                "entity_type": entity_type,
                "entity_id": entity_id,
                **(details or {})
            }
        )


class TenantMismatchError(BCMException):
    """
    Tenant mismatch - user trying to access different tenant's data.

    Raised when user attempts to access resources from a different tenant.

    Example:
        ```python
        raise TenantMismatchError(
            user_tenant="tenant-123",
            resource_tenant="tenant-456"
        )
        ```
    """

    def __init__(self, user_tenant: str, resource_tenant: str):
        super().__init__(
            message="Access denied: tenant mismatch",
            code="TENANT_MISMATCH",
            details={
                "user_tenant": user_tenant,
                "resource_tenant": resource_tenant
            }
        )


class ValidationError(BCMException):
    """
    Business logic validation failure.

    Similar to ValidationException but with field-specific validation.

    Example:
        ```python
        raise ValidationError(
            field="rto_hours",
            message="RTO cannot exceed 168 hours (7 days)"
        )
        ```
    """

    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation failed: {message}",
            code="VALIDATION_ERROR",
            details={"field": field, "validation_message": message}
        )


class WorkflowTransitionError(BCMException):
    """
    Invalid workflow transition attempted.

    Raised when trying to transition from one status to another in an invalid way.

    Example:
        ```python
        raise WorkflowTransitionError(
            current_status="APPROVED",
            transition="submit_for_review",
            allowed_transitions=["archive", "revoke"]
        )
        ```
    """

    def __init__(self, current_status: str, transition: str, allowed_transitions: list):
        super().__init__(
            message=f"Cannot execute '{transition}' from status '{current_status}'",
            code="INVALID_TRANSITION",
            details={
                "current_status": current_status,
                "attempted_transition": transition,
                "allowed_transitions": allowed_transitions
            }
        )


class ConcurrencyError(BCMException):
    """
    Optimistic lock failure - version mismatch.

    Raised when entity was modified by another user (version conflict).

    Example:
        ```python
        raise ConcurrencyError(
            entity_id="evidence-123",
            expected_version=5,
            actual_version=6
        )
        ```
    """

    def __init__(self, entity_id: str, expected_version: int, actual_version: int):
        super().__init__(
            message="Entity was modified by another user. Please refresh and try again.",
            code="CONCURRENCY_CONFLICT",
            details={
                "entity_id": entity_id,
                "expected_version": expected_version,
                "actual_version": actual_version
            }
        )


class DatabaseError(BCMException):
    """
    Database operation failure.

    Raised when database operations fail unexpectedly.

    Example:
        ```python
        raise DatabaseError(
            operation="create_assessment",
            details="Unique constraint violation"
        )
        ```
    """

    def __init__(self, operation: str, details: str):
        super().__init__(
            message=f"Database operation failed: {operation}",
            code="DATABASE_ERROR",
            details={"operation": operation, "error": details}
        )
