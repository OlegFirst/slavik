"""
FastAPI Dependencies for Marketplace
Authentication, database sessions, and service instances
"""

import sys
from pathlib import Path

# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared"))

from typing import Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from database.connection import get_db
from shared.auth.dependencies import get_current_user_dep, require_role
from shared.auth.jwt_handler import get_current_user as get_user_from_token
from shared.eventbus import get_eventbus


# ============================================================================
# Service Clients
# ============================================================================

def get_eventbus_client():
    """Get EventBus client instance from shared library"""
    return get_eventbus()


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
    (e.g., public specialist profiles, public project listings)

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
# Authorization Checks - Marketplace Specific
# ============================================================================

async def require_specialist(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require current user to be a specialist or admin

    Specialists can:
    - Create and manage their profiles
    - Submit proposals
    - View their projects
    - Respond to reviews

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


async def require_client(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require current user to be a client or admin

    Clients can:
    - Post projects/requests
    - Review proposals
    - Hire specialists
    - Write reviews

    Raises:
        HTTPException 403 if user is not a client
    """
    user_type = current_user.get("user_type")

    if user_type not in ["client", "organization", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only clients and admins can perform this action"
        )

    return current_user


async def require_verified_specialist(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Require current user to be a verified specialist

    Verified specialists can:
    - Submit proposals on projects
    - Be matched with projects
    - Appear in specialist search

    Raises:
        HTTPException 403 if user is not a verified specialist
    """
    user_type = current_user.get("user_type")

    if user_type not in ["specialist", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only specialists can perform this action"
        )

    # Check if specialist is verified
    from database.models import Specialist
    result = await db.execute(
        text("""
            SELECT is_verified, active
            FROM marketplace.specialists
            WHERE user_id = :user_id
        """),
        {"user_id": current_user["user_id"]}
    )
    specialist = result.first()

    if not specialist:
        raise HTTPException(
            status_code=404,
            detail="Specialist profile not found. Please create your profile first."
        )

    if not specialist.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Your specialist profile must be verified before you can submit proposals"
        )

    if not specialist.active:
        raise HTTPException(
            status_code=403,
            detail="Your specialist profile is inactive"
        )

    return current_user


async def require_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require current user to be an admin

    Admins can:
    - Verify specialists
    - Moderate content
    - Access all data
    - Manage disputes

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
        # Use parameterized query to prevent SQL injection
        await db.execute(
            text("SET LOCAL app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
    else:
        await db.execute(
            text("SET LOCAL app.current_tenant_id = ''")
        )


async def get_db_with_context(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AsyncSession:
    """
    Get database session with tenant context set

    This ensures Row Level Security is applied correctly

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Database session with tenant context set
    """
    tenant_id = current_user.get("tenant_id")
    await set_tenant_context(db, tenant_id)
    return db


# ============================================================================
# Resource Ownership Verification
# ============================================================================

async def verify_specialist_ownership(
    specialist_id: int,
    current_user: dict,
    db: AsyncSession
):
    """
    Verify that current user owns the specialist profile

    Args:
        specialist_id: Specialist ID to check
        current_user: Current user data
        db: Database session

    Raises:
        HTTPException 403 if user doesn't own the specialist profile
        HTTPException 404 if specialist not found
    """
    result = await db.execute(
        text("""
            SELECT user_id
            FROM marketplace.specialists
            WHERE id = :specialist_id AND tenant_id = :tenant_id
        """),
        {
            "specialist_id": specialist_id,
            "tenant_id": current_user["tenant_id"]
        }
    )
    specialist = result.first()

    if not specialist:
        raise HTTPException(
            status_code=404,
            detail="Specialist not found"
        )

    # Admins can access any specialist
    if current_user.get("user_type") == "admin":
        return

    if str(specialist.user_id) != str(current_user["user_id"]):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this specialist profile"
        )


async def verify_project_ownership(
    project_id: int,
    current_user: dict,
    db: AsyncSession
):
    """
    Verify that current user owns the project

    Args:
        project_id: Project ID to check
        current_user: Current user data
        db: Database session

    Raises:
        HTTPException 403 if user doesn't own the project
        HTTPException 404 if project not found
    """
    result = await db.execute(
        text("""
            SELECT client_id
            FROM marketplace.projects
            WHERE id = :project_id AND tenant_id = :tenant_id
        """),
        {
            "project_id": project_id,
            "tenant_id": current_user["tenant_id"]
        }
    )
    project = result.first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Admins can access any project
    if current_user.get("user_type") == "admin":
        return

    if str(project.client_id) != str(current_user["user_id"]):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this project"
        )
