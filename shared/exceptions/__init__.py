"""Custom exceptions module for BCM Platform."""

from shared.exceptions.custom import (
    BCMException,
    ValidationException,
    ResourceNotFoundException,
    DuplicateResourceException,
    WorkflowException,
    SecurityException,
    PermissionDeniedException,
    ExternalServiceException,
    ErrorResponse,
    EntityNotFoundError,
    TenantMismatchError,
    ValidationError,
    WorkflowTransitionError,
    ConcurrencyError,
    DatabaseError,
    RateLimitException,
    ConfigurationException
)

__all__ = [
    "BCMException",
    "ValidationException",
    "ResourceNotFoundException",
    "DuplicateResourceException",
    "WorkflowException",
    "SecurityException",
    "PermissionDeniedException",
    "ExternalServiceException",
    "ErrorResponse",
    "EntityNotFoundError",
    "TenantMismatchError",
    "ValidationError",
    "WorkflowTransitionError",
    "ConcurrencyError",
    "DatabaseError",
    "RateLimitException",
    "ConfigurationException",
]
