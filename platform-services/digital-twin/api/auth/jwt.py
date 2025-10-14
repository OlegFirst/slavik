"""
JWT Token Module

Handles creation and verification of JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

from jose import JWTError, jwt
from pydantic import BaseModel


# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class TokenPayload(BaseModel):
    """JWT Token Payload"""
    sub: str  # Subject (user ID)
    tenant_id: str
    email: str
    exp: datetime
    type: str  # "access" or "refresh"


def create_access_token(
    user_id: str,
    tenant_id: str,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token

    Args:
        user_id: User ID
        tenant_id: Tenant ID
        email: User email
        expires_delta: Optional expiration time delta

    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "email": email,
        "exp": expire,
        "type": "access"
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    tenant_id: str,
    email: str
) -> str:
    """
    Create JWT refresh token (longer expiration)

    Args:
        user_id: User ID
        tenant_id: Tenant ID
        email: User email

    Returns:
        JWT refresh token string
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "email": email,
        "exp": expire,
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token string
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload or None if invalid

    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type
        if payload.get("type") != expected_type:
            return None

        return payload

    except JWTError:
        return None
