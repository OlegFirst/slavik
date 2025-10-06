"""
Authentication Dependencies
============================

FastAPI dependencies for JWT authentication and role-based access control.

Features:
- get_current_user_dep: Dependency to get current authenticated user
- require_role: Dependency to enforce role requirements
- Support for both single role and multiple roles per user
"""

from typing import List, Dict, Any
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Try to import from jwt_handler, fall back to jwt
try:
    from shared.auth.jwt_handler import get_current_user as extract_user_from_token
    USE_JWT_HANDLER = True
except ImportError:
    from shared.auth.jwt import get_current_user
    USE_JWT_HANDLER = False


# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency for getting current authenticated user.

    Extracts JWT token from Authorization header and validates it.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        dict: User payload (user_id, tenant_id, roles or role)

    Raises:
        HTTPException: 401 if token is missing or invalid

    Example:
        ```python
        @router.get("/profile")
        async def get_profile(current_user: dict = Depends(get_current_user_dep)):
            return {
                "user_id": current_user["user_id"],
                "tenant_id": current_user["tenant_id"]
            }
        ```
    """
    if USE_JWT_HANDLER:
        # Use new jwt_handler
        token = credentials.credentials
        return extract_user_from_token(token)
    else:
        # Use existing jwt module (for backwards compatibility)
        return await get_current_user(credentials)


def require_role(*allowed_roles: str):
    """
    Dependency factory to enforce role requirements.

    Creates a dependency that checks if the current user has one of the allowed roles.
    Supports both single role (legacy) and multiple roles (new) format.

    Args:
        allowed_roles: Roles that are allowed to access the endpoint

    Returns:
        Dependency function that returns the current user

    Raises:
        HTTPException: 403 if user doesn't have required role

    Example:
        ```python
        @router.post("/programs")
        async def create_program(
            program: ProgramCreate,
            current_user: dict = Depends(require_role("admin", "bcm_manager"))
        ):
            # Only admin and bcm_manager can access this endpoint
            return await create_program_logic(program, current_user)
        ```
    """
    async def check_role(current_user: dict = Depends(get_current_user_dep)) -> Dict[str, Any]:
        # Support both "roles" (list) and "role" (string) formats
        user_roles = current_user.get("roles", [])
        if not user_roles:
            # Fallback to single role format
            single_role = current_user.get("role")
            user_roles = [single_role] if single_role else []

        # Check if user has any of the allowed roles
        has_role = any(role in user_roles for role in allowed_roles)

        if not has_role:
            raise HTTPException(
                status_code=403,
                detail=f"Access forbidden. Required roles: {', '.join(allowed_roles)}. User roles: {', '.join(user_roles)}"
            )

        return current_user

    return check_role


def require_admin():
    """
    Dependency to require admin or system_admin role.

    Shortcut for require_role("admin", "system_admin").

    Example:
        ```python
        @router.delete("/programs/{id}")
        async def delete_program(
            id: int,
            current_user: dict = Depends(require_admin())
        ):
            # Only admins can delete
            return await delete_program_logic(id)
        ```
    """
    return require_role("admin", "system_admin")


def require_manager():
    """
    Dependency to require manager-level access.

    Shortcut for require_role("admin", "bcm_manager", "manager").

    Example:
        ```python
        @router.post("/enrollments/{id}/approve")
        async def approve_enrollment(
            id: int,
            current_user: dict = Depends(require_manager())
        ):
            # Admins and managers can approve
            return await approve_enrollment_logic(id)
        ```
    """
    return require_role("admin", "bcm_manager", "manager")
