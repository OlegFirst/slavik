"""
FastAPI Dependencies
Authentication, database sessions, and service instances
"""

import sys
from pathlib import Path

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

from typing import Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from shared.auth.dependencies import get_current_user_dep, require_role
from shared.auth.jwt_handler import get_current_user as get_user_from_token

# Keep integrations for non-auth services
from integrations.validation_client import ValidationClient
from integrations.ai_client import AIClient


# ============================================================================
# Service Clients
# ============================================================================

def get_validation_client() -> ValidationClient:
    """Get Validation service client instance"""
    return ValidationClient()


def get_ai_client() -> AIClient:
    """Get AI Orchestrator client instance"""
    return AIClient()


# ============================================================================
# Authentication (using shared library)
# ============================================================================

# Use shared library function
get_current_user = get_current_user_dep


async def get_current_user_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """
    Extract current user if token is provided, otherwise return None

    Used for endpoints that work both for authenticated and public users

    Returns:
        dict with user data or None if no token provided
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        user_data = get_user_from_token(token)
        return user_data
    except (ValueError, HTTPException):
        return None


async def get_token(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Extract JWT token from Authorization header

    Returns:
        JWT token string

    Raises:
        HTTPException 401 if token is missing or malformed
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )

    return authorization.replace("Bearer ", "")


# ============================================================================
# Authorization Checks
# ============================================================================

async def require_specialist(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require current user to be a specialist

    Raises:
        HTTPException 403 if user is not a specialist
    """
    user_type = current_user.get("user_type")

    if user_type not in ["specialist", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only specialists and admins can perform this action"
        )

    return current_user


async def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require current user to be an admin

    Raises:
        HTTPException 403 if user is not an admin
    """
    user_type = current_user.get("user_type")

    if user_type != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can perform this action"
        )

    return current_user


# ============================================================================
# Database Session Context
# ============================================================================

async def set_tenant_context(
    db: AsyncSession,
    tenant_id: Optional[str]
):
    """
    Set PostgreSQL session variable for Row Level Security

    Args:
        db: Database session
        tenant_id: Tenant ID or None for public access
    """
    if tenant_id:
        await db.execute(
            f"SET LOCAL app.current_tenant_id = '{tenant_id}'"
        )
    else:
        await db.execute(
            "SET LOCAL app.current_tenant_id = ''"
        )
