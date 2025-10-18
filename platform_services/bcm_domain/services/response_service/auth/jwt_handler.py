"""
Response Module - JWT Token Handler
ISO 22301:2019 Clause 8.4 - Security and Authentication

Handles JWT token verification and validation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
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


def verify_jwt_token(token: str, secret_key: str, algorithm: str = "HS256") -> Dict[str, Any]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string
        secret_key: Secret key for verification
        algorithm: JWT algorithm (default: HS256)

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_token(token: str, secret_key: str, algorithm: str = "HS256") -> Optional[Dict[str, Any]]:
    """
    Decode JWT token without verification (for optional auth).

    Args:
        token: JWT token string
        secret_key: Secret key for verification
        algorithm: JWT algorithm (default: HS256)

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])

        # Check expiration
        exp = payload.get("exp")
        if exp:
            if datetime.fromtimestamp(exp) < datetime.utcnow():
                return None

        return payload
    except JWTError:
        return None


def create_user_from_token(payload: Dict[str, Any]) -> User:
    """
    Create User object from JWT token payload.

    Expected token structure:
    {
        "sub": "user_id",
        "organization_id": "org_id",  # or "tenant_id"
        "email": "user@example.com",
        "role": "bcm_manager",
        "full_name": "John Doe",
        "exp": 1234567890
    }

    Args:
        payload: JWT token payload

    Returns:
        User object

    Raises:
        HTTPException: If required fields are missing
    """
    try:
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID (sub claim)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Support both organization_id and tenant_id
        tenant_id = payload.get("organization_id") or payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing organization_id or tenant_id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email = payload.get("email", f"{user_id}@unknown.com")
        role = payload.get("role", "user")
        full_name = payload.get("full_name")

        return User(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            role=role,
            full_name=full_name,
            is_active=True
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token payload: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
