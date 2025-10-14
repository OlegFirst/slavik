"""
Authentication Middleware
Production-grade JWT authentication with public endpoint whitelist
"""

import logging
from typing import Callable, Optional
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from utils.jwt_handler import (
    jwt_handler,
    TokenExpiredError,
    TokenInvalidError,
    TokenMissingClaimsError,
)

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware

    Features:
    - JWT token validation for protected endpoints
    - Public endpoint whitelist (no auth required)
    - Extract and attach user context to request.state
    - Proper WWW-Authenticate header on 401 responses
    - Bearer token extraction from Authorization header
    - Path-based authentication bypass for public routes
    """

    def __init__(self, app):
        """Initialize authentication middleware"""
        super().__init__(app)
        self.public_endpoints = set(settings.public_endpoints)
        logger.info(f"Auth middleware initialized with {len(self.public_endpoints)} public endpoints")

    def _is_public_endpoint(self, path: str) -> bool:
        """
        Check if endpoint is public (no auth required)

        Args:
            path: Request path

        Returns:
            True if endpoint is public
        """
        # Exact match
        if path in self.public_endpoints:
            return True

        # Prefix match for wildcards
        for public_path in self.public_endpoints:
            if public_path.endswith("*"):
                prefix = public_path.rstrip("*")
                if path.startswith(prefix):
                    return True
            elif path.startswith(public_path):
                return True

        return False

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header

        Args:
            request: FastAPI request object

        Returns:
            JWT token string or None if not found
        """
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        # Expected format: "Bearer <token>"
        parts = auth_header.split()

        if len(parts) != 2:
            logger.warning(f"Malformed Authorization header: {len(parts)} parts")
            return None

        scheme, token = parts

        if scheme.lower() != "bearer":
            logger.warning(f"Invalid auth scheme: {scheme}")
            return None

        return token

    def _create_unauthorized_response(
        self,
        message: str,
        error_type: str = "invalid_token"
    ) -> JSONResponse:
        """
        Create 401 Unauthorized response with proper WWW-Authenticate header

        Args:
            message: Error message
            error_type: Error type for WWW-Authenticate header

        Returns:
            JSONResponse with 401 status
        """
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "unauthorized",
                "message": message,
                "error_type": error_type,
            },
            headers={
                "WWW-Authenticate": f'Bearer realm="API Gateway", error="{error_type}", error_description="{message}"',
            },
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through authentication middleware

        Args:
            request: FastAPI request
            call_next: Next middleware/handler in chain

        Returns:
            Response from downstream handlers or 401 if auth fails
        """
        path = request.url.path
        method = request.method

        # Skip authentication for public endpoints
        if self._is_public_endpoint(path):
            logger.debug(f"Public endpoint accessed: {method} {path}")
            return await call_next(request)

        # Extract token from Authorization header
        token = self._extract_token(request)

        if not token:
            logger.warning(f"No token provided for protected endpoint: {method} {path}")
            return self._create_unauthorized_response(
                message="Missing or invalid Authorization header",
                error_type="invalid_request"
            )

        try:
            # Validate token and extract claims
            claims = jwt_handler.extract_claims(token)

            # Attach user context to request state
            request.state.user_id = claims.get("user_id")
            request.state.tenant_id = claims.get("tenant_id")
            request.state.roles = claims.get("roles", [])
            request.state.email = claims.get("email")
            request.state.token_exp = claims.get("exp")
            request.state.token_iat = claims.get("iat")
            request.state.authenticated = True

            # Store full claims for advanced use cases
            request.state.user_claims = claims

            logger.info(
                f"Authenticated request: user={request.state.user_id}, "
                f"tenant={request.state.tenant_id}, "
                f"path={method} {path}"
            )

            # Continue to next middleware/handler
            response = await call_next(request)

            return response

        except TokenExpiredError:
            logger.warning(f"Expired token used for: {method} {path}")
            return self._create_unauthorized_response(
                message="Token has expired",
                error_type="invalid_token"
            )

        except TokenInvalidError as e:
            logger.warning(f"Invalid token for {method} {path}: {str(e)}")
            return self._create_unauthorized_response(
                message=f"Invalid token: {str(e)}",
                error_type="invalid_token"
            )

        except TokenMissingClaimsError as e:
            logger.error(f"Token missing required claims for {method} {path}: {str(e)}")
            return self._create_unauthorized_response(
                message=f"Token missing required claims: {str(e)}",
                error_type="invalid_token"
            )

        except Exception as e:
            logger.exception(f"Unexpected auth error for {method} {path}: {str(e)}")
            return self._create_unauthorized_response(
                message="Authentication failed",
                error_type="invalid_token"
            )


def get_current_user(request: Request) -> dict:
    """
    Helper function to get current authenticated user from request state

    Args:
        request: FastAPI request object

    Returns:
        Dict with user information

    Raises:
        ValueError: If user is not authenticated
    """
    if not getattr(request.state, "authenticated", False):
        raise ValueError("Request is not authenticated")

    return {
        "user_id": request.state.user_id,
        "tenant_id": request.state.tenant_id,
        "roles": request.state.roles,
        "email": request.state.email,
    }


def require_role(request: Request, required_role: str) -> bool:
    """
    Check if authenticated user has required role

    Args:
        request: FastAPI request object
        required_role: Role to check for

    Returns:
        True if user has role

    Raises:
        ValueError: If user is not authenticated or lacks role
    """
    if not getattr(request.state, "authenticated", False):
        raise ValueError("Request is not authenticated")

    roles = request.state.roles or []

    if required_role not in roles:
        raise ValueError(f"User lacks required role: {required_role}")

    return True


def require_any_role(request: Request, required_roles: list) -> bool:
    """
    Check if authenticated user has any of the required roles

    Args:
        request: FastAPI request object
        required_roles: List of acceptable roles

    Returns:
        True if user has at least one role

    Raises:
        ValueError: If user is not authenticated or lacks all roles
    """
    if not getattr(request.state, "authenticated", False):
        raise ValueError("Request is not authenticated")

    roles = request.state.roles or []

    if not any(role in roles for role in required_roles):
        raise ValueError(f"User lacks any required role: {required_roles}")

    return True


class OptionalAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Optional authentication middleware - validates token if present but doesn't require it

    Useful for endpoints that behave differently for authenticated vs anonymous users
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with optional authentication"""
        auth_header = request.headers.get("Authorization")

        # Default to unauthenticated
        request.state.authenticated = False
        request.state.user_id = None
        request.state.tenant_id = None
        request.state.roles = []

        if auth_header:
            try:
                # Extract token
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    token = parts[1]

                    # Validate and extract claims
                    claims = jwt_handler.extract_claims(token)

                    # Attach user context
                    request.state.user_id = claims.get("user_id")
                    request.state.tenant_id = claims.get("tenant_id")
                    request.state.roles = claims.get("roles", [])
                    request.state.email = claims.get("email")
                    request.state.authenticated = True

                    logger.debug(f"Optional auth: authenticated as {request.state.user_id}")

            except Exception as e:
                logger.debug(f"Optional auth failed (continuing as anonymous): {str(e)}")

        # Continue regardless of auth status
        return await call_next(request)
