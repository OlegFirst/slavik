"""
Centralized Error Handlers for Plans Service
Provides consistent error responses and logging
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors
    Returns 422 with detailed validation errors
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": exc.body if hasattr(exc, 'body') else None
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors
    Logs full exception but returns safe error message to client
    """
    logger.error(
        f"Unexpected error on {request.url.path}: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else None
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error. Please contact support if the issue persists.",
            "error_id": None  # Could generate unique error ID for support tracking
        }
    )


async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError (business logic errors)
    Returns 400 Bad Request with error message
    """
    logger.warning(f"Business logic error on {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc)
        }
    )
