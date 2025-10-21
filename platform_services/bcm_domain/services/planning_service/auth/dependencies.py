"""
Authentication Dependencies for Planning Service
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from jose import JWTError, jwt
from .models import UserContext
from ..config import settings

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_dev_user: Optional[str] = Header(None),
    x_dev_tenant: Optional[str] = Header(None)
) -> UserContext:
    """
    Dependency to extract and validate current user from JWT token.

    In production: Validates JWT token from Authorization header
    In development: Allows bypass with X-Dev-User and X-Dev-Tenant headers

    Args:
        authorization: Bearer token from Authorization header
        x_dev_user: Development mode user ID (only if JWT_PUBLIC_KEY is empty)
        x_dev_tenant: Development mode tenant ID (only if JWT_PUBLIC_KEY is empty)

    Returns:
        UserContext: Validated user context

    Raises:
        HTTPException: 401 if authentication fails
    """

    # Development mode bypass
    if not settings.JWT_PUBLIC_KEY or settings.JWT_PUBLIC_KEY == "PLACEHOLDER_DEV_MODE":
        if x_dev_user and x_dev_tenant:
            logger.warning(
                " DEVELOPMENT MODE: Using dev headers for authentication. "
                "Never use in production!"
            )
            return UserContext(
                user_id=x_dev_user,
                tenant_id=x_dev_tenant,
                email=f"{x_dev_user}@dev.local",
                roles=["bcm_manager", "strategy_editor"],
                is_superadmin=False
            )
        else:
            logger.warning(
                " DEVELOPMENT MODE: No JWT_PUBLIC_KEY configured and no dev headers provided. "
                "Set X-Dev-User and X-Dev-Tenant headers for development."
            )

    # Validate Authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer' token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate JWT token
    try:
        # Use public key if available, otherwise fall back to secret
        if settings.JWT_PUBLIC_KEY and settings.JWT_PUBLIC_KEY != "PLACEHOLDER_DEV_MODE":
            key = settings.JWT_PUBLIC_KEY
            algorithms = [settings.JWT_ALGORITHM]
        else:
            # Fallback for symmetric key (HS256)
            key = settings.JWT_SECRET
            algorithms = ["HS256", settings.JWT_ALGORITHM]

        payload = jwt.decode(
            token,
            key,
            algorithms=algorithms,
            audience=settings.JWT_AUDIENCE if hasattr(settings, 'JWT_AUDIENCE') else None,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": hasattr(settings, 'JWT_AUDIENCE'),
            }
        )

        # Extract user information from token
        user_id = payload.get("sub") or payload.get("user_id")
        tenant_id = payload.get("tenant_id")
        email = payload.get("email")
        roles = payload.get("roles", [])
        is_superadmin = payload.get("is_superadmin", False)

        # Validate required fields
        if not user_id:
            logger.error("JWT token missing 'sub' or 'user_id' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not tenant_id:
            logger.error("JWT token missing 'tenant_id' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing tenant identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserContext(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email or f"{user_id}@unknown.local",
            roles=roles if isinstance(roles, list) else [],
            is_superadmin=bool(is_superadmin)
        )

    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    x_dev_user: Optional[str] = Header(None),
    x_dev_tenant: Optional[str] = Header(None)
) -> Optional[UserContext]:
    """
    Optional authentication dependency.
    Returns None if no valid credentials provided instead of raising exception.

    Useful for endpoints that have different behavior for authenticated vs unauthenticated users.
    """
    try:
        return await get_current_user(authorization, x_dev_user, x_dev_tenant)
    except HTTPException:
        return None
