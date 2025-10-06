"""Middleware module for BCM Platform."""

from shared.middleware.error_handler import setup_error_handlers, error_handler_middleware

__all__ = [
    "setup_error_handlers",
    "error_handler_middleware",
]
