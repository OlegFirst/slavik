"""
Risk Management - FastAPI Authentication Dependencies
ISO 22301:2019 - Security and Authentication

FastAPI dependencies for JWT authentication.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sys
from pathlib import Path

# Add shared models to path
shared_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Direct import from common module
import importlib.util
spec = importlib.util.spec_from_file_location("common", shared_path / "models" / "common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
User = common.User

from .jwt_handler import verify_jwt_token, decode_token, create_user_from_token
from config import settings


# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    FastAPI dependency to get current authenticated user.

    Requires valid JWT token in Authorization header.

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        User object from JWT token

    Raises:
        HTTPException: If authentication is required but token is missing/invalid

    Usage:
        ```python
        @router.get("/risks")
        async def list_risks(
            current_user: User = Depends(get_current_user)
        ):
            # Access user's organization
            org_id = current_user.tenant_id
            ...
        ```
    """
    # Check if authentication is disabled
    if hasattr(settings, 'JWT_AUTH_ENABLED') and not settings.JWT_AUTH_ENABLED:
        # Return a default user when auth is disabled (for development/testing)
        return User(
            user_id="system",
            tenant_id="default",
            email="system@platform.local",
            role="admin",
            full_name="System User",
            is_active=True
        )

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Get JWT settings from config
    secret_key = getattr(settings, 'JWT_SECRET_KEY', None)
    algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')

    if not secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY not configured"
        )

    # Verify and decode token
    payload = verify_jwt_token(token, secret_key, algorithm)

    # Create user from token
    user = create_user_from_token(payload)

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    FastAPI dependency to get current user (optional).

    Does not raise error if token is missing or invalid.
    Useful for endpoints that work with or without authentication.

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        User object from JWT token, or None if no valid token

    Usage:
        ```python
        @router.get("/public-risks")
        async def list_public_risks(
            current_user: Optional[User] = Depends(get_optional_user)
        ):
            if current_user:
                # Show user's private data
                org_id = current_user.tenant_id
            else:
                # Show only public data
                org_id = None
            ...
        ```
    """
    # Check if authentication is disabled
    if hasattr(settings, 'JWT_AUTH_ENABLED') and not settings.JWT_AUTH_ENABLED:
        return None

    if not credentials:
        return None

    token = credentials.credentials

    # Get JWT settings from config
    secret_key = getattr(settings, 'JWT_SECRET_KEY', None)
    algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')

    if not secret_key:
        return None

    # Decode token (doesn't raise errors)
    payload = decode_token(token, secret_key, algorithm)
    if not payload:
        return None

    try:
        user = create_user_from_token(payload)
        return user
    except Exception:
        return None


def require_role(*allowed_roles: str):
    """
    Dependency factory to require specific user roles.

    Args:
        *allowed_roles: Allowed role names

    Returns:
        FastAPI dependency function

    Usage:
        ```python
        @router.post("/critical-risks")
        async def create_critical_risk(
            current_user: User = Depends(get_current_user),
            _role_check = Depends(require_role("admin", "bcm_manager"))
        ):
            ...
        ```
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker
