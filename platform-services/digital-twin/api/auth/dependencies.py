"""
Authentication Dependencies

FastAPI dependencies for protected routes
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt import verify_token
from storage.postgres_storage import PostgreSQLStorage


# HTTP Bearer token scheme
security = HTTPBearer()


def get_storage() -> PostgreSQLStorage:
    """Get storage instance (will be injected by app)"""
    from api.app import storage
    return storage


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer credentials
        storage: Database storage

    Returns:
        User model

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token
    token = credentials.credentials
    payload = verify_token(token, expected_type="access")

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    try:
        user = await storage.get_user(user_id=user_id)
    except Exception:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Get current active user (not disabled)

    Args:
        current_user: Current user from get_current_user

    Returns:
        Active user model

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return current_user


async def require_admin(
    current_user = Depends(get_current_active_user)
):
    """
    Require user to be admin within their tenant

    Args:
        current_user: Current active user

    Returns:
        Admin user

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user


async def require_superuser(
    current_user = Depends(get_current_active_user)
):
    """
    Require user to be superuser (platform admin)

    Args:
        current_user: Current active user

    Returns:
        Superuser

    Raises:
        HTTPException: If user is not superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )

    return current_user
