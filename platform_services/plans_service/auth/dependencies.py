"""
Authentication Dependencies
FastAPI dependencies for JWT token validation and user context extraction
"""

import jwt
from fastapi import HTTPException, Security, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from .models import UserContext
from ..config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    x_dev_user: Optional[str] = Header(None, description="Development bypass header")
) -> UserContext:
    """
    Validate JWT token and extract user context

    Args:
        credentials: HTTP Bearer token from Authorization header
        x_dev_user: Development bypass header (only works if JWT_PUBLIC_KEY is empty)

    Returns:
        UserContext: User context with user_id, tenant_id, email, roles

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Security:
        - Validates JWT signature using JWT_PUBLIC_KEY
        - Verifies token expiration
        - Extracts user claims (user_id, tenant_id, email, roles)
        - Development mode: allows bypass with X-Dev-User header if JWT_PUBLIC_KEY is empty
    """

    # Development bypass - only if JWT_PUBLIC_KEY is not configured
    if not settings.JWT_PUBLIC_KEY and x_dev_user:
        logger.warning(f"DEV MODE: Bypassing authentication for user: {x_dev_user}")
        parts = x_dev_user.split(":")
        user_id = parts[0] if parts else x_dev_user
        tenant_id = parts[1] if len(parts) > 1 else "dev_tenant"
        email = parts[2] if len(parts) > 2 else f"{user_id}@dev.local"

        return UserContext(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            roles=["bcm_manager", "plan_approver"],
            is_superadmin=False
        )

    # Production mode - require JWT token
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Decode and validate JWT token
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE if settings.JWT_AUDIENCE else None,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": bool(settings.JWT_AUDIENCE),
            }
        )

        # Extract user information from token claims
        user_id = payload.get("sub") or payload.get("user_id")
        tenant_id = payload.get("tenant_id") or payload.get("org_id")
        email = payload.get("email")
        roles = payload.get("roles", [])
        is_superadmin = payload.get("is_superadmin", False)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing tenant_id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserContext(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email or f"{user_id}@unknown",
            roles=roles if isinstance(roles, list) else [],
            is_superadmin=is_superadmin
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid JWT token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    x_dev_user: Optional[str] = Header(None)
) -> Optional[UserContext]:
    """
    Optional authentication - returns None if no token provided

    Useful for endpoints that support both authenticated and anonymous access

    Args:
        credentials: HTTP Bearer token from Authorization header
        x_dev_user: Development bypass header

    Returns:
        Optional[UserContext]: User context if authenticated, None otherwise
    """
    if not credentials and not x_dev_user:
        return None

    try:
        return await get_current_user(credentials, x_dev_user)
    except HTTPException:
        return None
