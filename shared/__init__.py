"""
BCM Platform Shared Library
============================

Shared modules for all BCM Platform services.

Modules:
- database: Database connection pooling and session management
- cache: Redis caching with decorators
- auth: JWT authentication and RBAC
- eventbus: RabbitMQ event publishing and subscription
- exceptions: Custom exception hierarchy
- utils: Logging, metrics, validators
- models: Common Pydantic models
- config: Shared configuration
"""

__version__ = "1.0.0"

from .database.connection import DatabaseManager, init_database, get_db
from .cache.redis_cache import RedisCache, init_cache, cached
from .auth.jwt import JWTManager, init_jwt, get_current_user
from .exceptions.custom import (
    BCMException,
    ValidationException,
    ResourceNotFoundException,
    DuplicateResourceException,
    WorkflowException,
    SecurityException,
    PermissionDeniedException,
    ExternalServiceException,
    ErrorResponse
)

__all__ = [
    # Database
    "DatabaseManager",
    "init_database",
    "get_db",
    # Cache
    "RedisCache",
    "init_cache",
    "cached",
    # Auth
    "JWTManager",
    "init_jwt",
    "get_current_user",
    # Exceptions
    "BCMException",
    "ValidationException",
    "ResourceNotFoundException",
    "DuplicateResourceException",
    "WorkflowException",
    "SecurityException",
    "PermissionDeniedException",
    "ExternalServiceException",
    "ErrorResponse",
]
