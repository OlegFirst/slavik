"""
Authentication Middleware
=========================

FastAPI middleware for authentication.
"""

from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from shared.auth.jwt import get_jwt_manager
from shared.exceptions.custom import ErrorResponse
from datetime import datetime


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT authentication.

    Automatically validates JWT tokens for protected routes.

    Example:
        ```python
        from shared.auth.middleware import AuthenticationMiddleware

        app.add_middleware(
            AuthenticationMiddleware,
            exclude_paths=["/health", "/docs", "/openapi.json"]
        )
        ```
    """

    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Get authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    error_code="MISSING_TOKEN",
                    message="Missing or invalid authorization header",
                    timestamp=datetime.utcnow()
                ).dict()
            )

        # Extract token
        token = auth_header.split(" ")[1]

        # Verify token
        try:
            jwt_manager = get_jwt_manager()
            payload = jwt_manager.verify_token(token)

            # Add user info to request state
            request.state.user = payload

        except Exception as e:
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    error_code="INVALID_TOKEN",
                    message=str(e),
                    timestamp=datetime.utcnow()
                ).dict()
            )

        return await call_next(request)
