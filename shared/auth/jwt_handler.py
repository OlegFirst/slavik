"""
JWT Handler for Learning Service
Provides simple JWT token creation, verification, and user extraction
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from jose import jwt, JWTError
from fastapi import HTTPException


# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(
    user_id: str,
    tenant_id: str,
    roles: List[str],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate JWT access token.

    Args:
        user_id: User identifier
        tenant_id: Tenant identifier
        roles: List of user roles (e.g., ["admin", "bcm_manager"])
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token

    Example:
        ```python
        token = create_access_token(
            user_id="user123",
            tenant_id="tenant456",
            roles=["admin", "bcm_manager"]
        )
        ```
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    payload = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload containing user_id, tenant_id, roles, exp

    Raises:
        HTTPException: 401 if token is invalid or expired

    Example:
        ```python
        try:
            payload = verify_token(token)
            user_id = payload["user_id"]
        except HTTPException as e:
            print(f"Invalid token: {e.detail}")
        ```
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(token: str) -> Dict[str, Any]:
    """
    Extract user information from JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: User information (user_id, tenant_id, roles)

    Raises:
        HTTPException: 401 if token is invalid

    Example:
        ```python
        user = get_current_user(token)
        print(f"User: {user['user_id']}, Tenant: {user['tenant_id']}")
        ```
    """
    payload = verify_token(token)

    # Validate required fields
    user_id = payload.get("user_id")
    tenant_id = payload.get("tenant_id")
    roles = payload.get("roles")

    if not user_id or not tenant_id or not roles:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload: missing required fields",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "roles": roles
    }
