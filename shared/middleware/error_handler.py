"""
Global Error Handler Middleware
Converts exceptions to structured JSON responses
"""

import logging
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError as PydanticValidationError

from shared.exceptions import (
    BCMException,
    EntityNotFoundError,
    TenantMismatchError,
    ValidationError,
    WorkflowTransitionError,
    ConcurrencyError,
    DatabaseError,
    ExternalServiceException,
    ResourceNotFoundException,
    ValidationException,
    WorkflowException,
    PermissionDeniedException,
    SecurityException,
)

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """
    Global error handler middleware.

    Catches all exceptions and returns structured JSON responses.
    """
    try:
        response = await call_next(request)
        return response

    except BCMException as e:
        # Custom BCM exceptions
        logger.warning(
            f"BCM Exception: {e.code} - {e.message}",
            extra={
                "error_code": e.code,
                "details": e.details,
                "path": request.url.path
            }
        )

        # Map error codes to HTTP status
        status_map = {
            "ENTITY_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "RESOURCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "TENANT_MISMATCH": status.HTTP_403_FORBIDDEN,
            "PERMISSION_DENIED": status.HTTP_403_FORBIDDEN,
            "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
            "INVALID_TRANSITION": status.HTTP_400_BAD_REQUEST,
            "WORKFLOW": status.HTTP_400_BAD_REQUEST,
            "CONCURRENCY_CONFLICT": status.HTTP_409_CONFLICT,
            "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "EXTERNAL_SERVICE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
            "SECURITY": status.HTTP_403_FORBIDDEN,
            "DUPLICATE_RESOURCE": status.HTTP_409_CONFLICT,
        }

        return JSONResponse(
            status_code=status_map.get(e.code, status.HTTP_500_INTERNAL_SERVER_ERROR),
            content={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details
                }
            }
        )

    except RequestValidationError as e:
        # Pydantic validation errors (malformed requests)
        logger.warning(f"Validation error: {e}", extra={"path": request.url.path})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": e.errors()
                }
            }
        )

    except SQLAlchemyError as e:
        # Database errors
        logger.error(f"Database error: {e}", extra={"path": request.url.path}, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Database operation failed",
                    "details": {"error": str(e)}
                }
            }
        )

    except Exception as e:
        # Unexpected errors
        logger.error(
            f"Unhandled exception: {e}",
            extra={"path": request.url.path},
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error": str(e)}
                }
            }
        )


def setup_error_handlers(app):
    """
    Add exception handlers to FastAPI app.

    Usage:
        from shared.middleware.error_handler import setup_error_handlers
        setup_error_handlers(app)
    """
    @app.exception_handler(BCMException)
    async def bcm_exception_handler(request: Request, exc: BCMException):
        status_map = {
            "ENTITY_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "RESOURCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
            "TENANT_MISMATCH": status.HTTP_403_FORBIDDEN,
            "PERMISSION_DENIED": status.HTTP_403_FORBIDDEN,
            "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
            "INVALID_TRANSITION": status.HTTP_400_BAD_REQUEST,
            "WORKFLOW": status.HTTP_400_BAD_REQUEST,
            "CONCURRENCY_CONFLICT": status.HTTP_409_CONFLICT,
            "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "EXTERNAL_SERVICE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
            "EXTERNALSERVICE": status.HTTP_503_SERVICE_UNAVAILABLE,
            "SECURITY": status.HTTP_403_FORBIDDEN,
            "DUPLICATE_RESOURCE": status.HTTP_409_CONFLICT,
        }

        logger.warning(
            f"BCM Exception: {exc.code} - {exc.message}",
            extra={
                "error_code": exc.code,
                "details": exc.details,
                "path": request.url.path
            }
        )

        return JSONResponse(
            status_code=status_map.get(exc.code, 500),
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Request validation error: {exc}", extra={"path": request.url.path})
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors()
                }
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error: {exc}", extra={"path": request.url.path}, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Database operation failed",
                    "details": {"error": str(exc)}
                }
            }
        )
