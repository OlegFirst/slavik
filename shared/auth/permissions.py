"""
RBAC Permission System
======================

Role-Based Access Control for BCM Platform.

Features:
- Role definitions
- Permission definitions
- Role-Permission mappings
- Permission decorator for endpoints
"""

from enum import Enum
from typing import Callable, Dict, List
from functools import wraps
from fastapi import Depends

from shared.auth.jwt import get_current_user
from shared.exceptions.custom import PermissionDeniedException


class Role(str, Enum):
    """
    User roles in BCM Platform.

    Hierarchy (highest to lowest):
    1. SYSTEM_ADMIN - Full system access
    2. BCM_MANAGER - Manage all BCM activities
    3. EXERCISE_COORDINATOR - Manage exercises
    4. AUDITOR - Conduct audits
    5. DOCUMENT_CONTROLLER - Manage documents
    6. APPROVER - Approve documents
    7. VIEWER - Read-only access
    """
    SYSTEM_ADMIN = "system_admin"
    BCM_MANAGER = "bcm_manager"
    EXERCISE_COORDINATOR = "exercise_coordinator"
    AUDITOR = "auditor"
    DOCUMENT_CONTROLLER = "document_controller"
    APPROVER = "approver"
    VIEWER = "viewer"


class Permission(str, Enum):
    """
    Granular permissions for BCM Platform operations.
    """

    # Exercise permissions
    EXERCISE_CREATE = "exercise:create"
    EXERCISE_UPDATE = "exercise:update"
    EXERCISE_DELETE = "exercise:delete"
    EXERCISE_START = "exercise:start"
    EXERCISE_COMPLETE = "exercise:complete"
    EXERCISE_VIEW = "exercise:view"

    # KPI permissions
    KPI_CREATE = "kpi:create"
    KPI_UPDATE = "kpi:update"
    KPI_DELETE = "kpi:delete"
    KPI_MEASURE = "kpi:measure"
    KPI_VIEW = "kpi:view"

    # Audit permissions
    AUDIT_CREATE = "audit:create"
    AUDIT_UPDATE = "audit:update"
    AUDIT_CONDUCT = "audit:conduct"
    AUDIT_CLOSE = "audit:close"
    AUDIT_VIEW = "audit:view"

    # CAPA permissions
    CAPA_CREATE = "capa:create"
    CAPA_UPDATE = "capa:update"
    CAPA_IMPLEMENT = "capa:implement"
    CAPA_VERIFY = "capa:verify"
    CAPA_VIEW = "capa:view"

    # Document permissions
    DOCUMENT_CREATE = "document:create"
    DOCUMENT_UPDATE = "document:update"
    DOCUMENT_DELETE = "document:delete"
    DOCUMENT_APPROVE = "document:approve"
    DOCUMENT_PUBLISH = "document:publish"
    DOCUMENT_VIEW = "document:view"

    # Management Review permissions
    REVIEW_CREATE = "review:create"
    REVIEW_UPDATE = "review:update"
    REVIEW_VIEW = "review:view"

    # BIA permissions
    BIA_CREATE = "bia:create"
    BIA_UPDATE = "bia:update"
    BIA_DELETE = "bia:delete"
    BIA_VIEW = "bia:view"
    BIA_COMPLETE = "bia:complete"
    BIA_AI_SUGGEST = "bia:ai_suggest"

    # Compliance/Evidence permissions
    EVIDENCE_CREATE = "evidence:create"
    EVIDENCE_UPDATE = "evidence:update"
    EVIDENCE_DELETE = "evidence:delete"
    EVIDENCE_VIEW = "evidence:view"
    EVIDENCE_SUBMIT = "evidence:submit"
    EVIDENCE_REVIEW = "evidence:review"
    EVIDENCE_VERIFY = "evidence:verify"
    EVIDENCE_REJECT = "evidence:reject"

    # Compliance Assessment permissions
    ASSESSMENT_CREATE = "assessment:create"
    ASSESSMENT_UPDATE = "assessment:update"
    ASSESSMENT_DELETE = "assessment:delete"
    ASSESSMENT_RUN = "assessment:run"
    ASSESSMENT_VIEW = "assessment:view"

    # Gap/Nonconformity permissions
    GAP_CREATE = "gap:create"
    GAP_UPDATE = "gap:update"
    GAP_VIEW = "gap:view"
    GAP_REMEDIATE = "gap:remediate"
    GAP_VERIFY = "gap:verify"

    # Administration permissions
    ADMIN_MANAGE_USERS = "admin:manage_users"
    ADMIN_MANAGE_TENANTS = "admin:manage_tenants"
    ADMIN_VIEW_LOGS = "admin:view_logs"
    ADMIN_MANAGE_CONFIG = "admin:manage_config"


# Role -> Permissions mapping
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    # System Admin: All permissions
    Role.SYSTEM_ADMIN: list(Permission),

    # BCM Manager: Manage all BCM activities
    Role.BCM_MANAGER: [
        # Exercises
        Permission.EXERCISE_CREATE,
        Permission.EXERCISE_UPDATE,
        Permission.EXERCISE_DELETE,
        Permission.EXERCISE_START,
        Permission.EXERCISE_COMPLETE,
        Permission.EXERCISE_VIEW,
        # KPIs
        Permission.KPI_CREATE,
        Permission.KPI_UPDATE,
        Permission.KPI_DELETE,
        Permission.KPI_MEASURE,
        Permission.KPI_VIEW,
        # Audits
        Permission.AUDIT_CREATE,
        Permission.AUDIT_UPDATE,
        Permission.AUDIT_CONDUCT,
        Permission.AUDIT_CLOSE,
        Permission.AUDIT_VIEW,
        # CAPAs
        Permission.CAPA_CREATE,
        Permission.CAPA_UPDATE,
        Permission.CAPA_IMPLEMENT,
        Permission.CAPA_VERIFY,
        Permission.CAPA_VIEW,
        # Documents
        Permission.DOCUMENT_CREATE,
        Permission.DOCUMENT_UPDATE,
        Permission.DOCUMENT_VIEW,
        # Reviews
        Permission.REVIEW_CREATE,
        Permission.REVIEW_UPDATE,
        Permission.REVIEW_VIEW,
        # BIA
        Permission.BIA_CREATE,
        Permission.BIA_UPDATE,
        Permission.BIA_DELETE,
        Permission.BIA_VIEW,
        Permission.BIA_COMPLETE,
        Permission.BIA_AI_SUGGEST,
        # Compliance/Evidence
        Permission.EVIDENCE_CREATE,
        Permission.EVIDENCE_UPDATE,
        Permission.EVIDENCE_DELETE,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_SUBMIT,
        Permission.EVIDENCE_REVIEW,
        Permission.EVIDENCE_VERIFY,
        Permission.EVIDENCE_REJECT,
        # Assessments
        Permission.ASSESSMENT_CREATE,
        Permission.ASSESSMENT_UPDATE,
        Permission.ASSESSMENT_DELETE,
        Permission.ASSESSMENT_RUN,
        Permission.ASSESSMENT_VIEW,
        # Gaps
        Permission.GAP_CREATE,
        Permission.GAP_UPDATE,
        Permission.GAP_VIEW,
        Permission.GAP_REMEDIATE,
        Permission.GAP_VERIFY,
    ],

    # Exercise Coordinator: Manage exercises
    Role.EXERCISE_COORDINATOR: [
        Permission.EXERCISE_CREATE,
        Permission.EXERCISE_UPDATE,
        Permission.EXERCISE_START,
        Permission.EXERCISE_COMPLETE,
        Permission.EXERCISE_VIEW,
        Permission.KPI_VIEW,
        Permission.DOCUMENT_VIEW,
    ],

    # Auditor: Conduct audits
    Role.AUDITOR: [
        Permission.AUDIT_CREATE,
        Permission.AUDIT_UPDATE,
        Permission.AUDIT_CONDUCT,
        Permission.AUDIT_VIEW,
        Permission.CAPA_CREATE,
        Permission.CAPA_VIEW,
        Permission.DOCUMENT_VIEW,
        Permission.EXERCISE_VIEW,
        Permission.KPI_VIEW,
        # BIA (read-only)
        Permission.BIA_VIEW,
        # Compliance (can create evidence and view assessments)
        Permission.EVIDENCE_CREATE,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_REVIEW,
        Permission.EVIDENCE_VERIFY,
        Permission.ASSESSMENT_VIEW,
        Permission.GAP_VIEW,
    ],

    # Document Controller: Manage documents
    Role.DOCUMENT_CONTROLLER: [
        Permission.DOCUMENT_CREATE,
        Permission.DOCUMENT_UPDATE,
        Permission.DOCUMENT_DELETE,
        Permission.DOCUMENT_PUBLISH,
        Permission.DOCUMENT_VIEW,
    ],

    # Approver: Approve documents
    Role.APPROVER: [
        Permission.DOCUMENT_APPROVE,
        Permission.DOCUMENT_VIEW,
    ],

    # Viewer: Read-only access
    Role.VIEWER: [
        Permission.EXERCISE_VIEW,
        Permission.KPI_VIEW,
        Permission.AUDIT_VIEW,
        Permission.CAPA_VIEW,
        Permission.DOCUMENT_VIEW,
        Permission.REVIEW_VIEW,
        Permission.BIA_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.ASSESSMENT_VIEW,
        Permission.GAP_VIEW,
    ],
}


def has_permission(user_role: str, required_permission: Permission) -> bool:
    """
    Check if user role has required permission.

    Args:
        user_role: User's role
        required_permission: Required permission

    Returns:
        bool: True if user has permission

    Example:
        ```python
        if has_permission(user.role, Permission.EXERCISE_CREATE):
            # Allow exercise creation
            pass
        ```
    """
    try:
        role = Role(user_role)
        permissions = ROLE_PERMISSIONS.get(role, [])
        return required_permission in permissions
    except ValueError:
        # Invalid role
        return False


def get_user_permissions(user_role: str) -> List[Permission]:
    """
    Get all permissions for a user role.

    Args:
        user_role: User's role

    Returns:
        list: List of permissions

    Example:
        ```python
        permissions = get_user_permissions("bcm_manager")
        print(f"BCM Manager has {len(permissions)} permissions")
        ```
    """
    try:
        role = Role(user_role)
        return ROLE_PERMISSIONS.get(role, [])
    except ValueError:
        return []


def require_permission(permission: Permission):
    """
    Decorator to enforce permission requirements on endpoints.

    Args:
        permission: Required permission

    Returns:
        Decorator function

    Raises:
        PermissionDeniedException: If user lacks required permission

    Example:
        ```python
        @router.post("/exercises")
        @require_permission(Permission.EXERCISE_CREATE)
        async def create_exercise(
            exercise: ExerciseCreate,
            current_user: dict = Depends(get_current_user)
        ):
            # User has EXERCISE_CREATE permission
            return await exercise_service.create(exercise)
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            # Get user's role
            user_role = current_user.get("role")

            # Check permission
            if not has_permission(user_role, permission):
                raise PermissionDeniedException(
                    f"User lacks required permission: {permission.value}",
                    details={
                        "user_id": current_user.get("user_id"),
                        "user_role": user_role,
                        "required_permission": permission.value
                    }
                )

            # Execute function
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permissions: Permission):
    """
    Decorator to require ANY of the specified permissions.

    Args:
        permissions: Required permissions (user needs at least one)

    Returns:
        Decorator function

    Example:
        ```python
        @router.get("/documents/{id}")
        @require_any_permission(
            Permission.DOCUMENT_VIEW,
            Permission.DOCUMENT_UPDATE,
            Permission.DOCUMENT_APPROVE
        )
        async def get_document(id: int, current_user: dict = Depends(get_current_user)):
            # User has at least one of the specified permissions
            return await doc_service.get(id)
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            user_role = current_user.get("role")

            # Check if user has any of the required permissions
            has_any = any(has_permission(user_role, perm) for perm in permissions)

            if not has_any:
                raise PermissionDeniedException(
                    f"User lacks any of required permissions: {[p.value for p in permissions]}",
                    details={
                        "user_id": current_user.get("user_id"),
                        "user_role": user_role,
                        "required_permissions": [p.value for p in permissions]
                    }
                )

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(*permissions: Permission):
    """
    Decorator to require ALL of the specified permissions.

    Args:
        permissions: Required permissions (user needs all)

    Returns:
        Decorator function

    Example:
        ```python
        @router.post("/documents/{id}/publish")
        @require_all_permissions(
            Permission.DOCUMENT_UPDATE,
            Permission.DOCUMENT_PUBLISH
        )
        async def publish_document(id: int, current_user: dict = Depends(get_current_user)):
            # User has all specified permissions
            return await doc_service.publish(id)
        ```
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            user_role = current_user.get("role")

            # Check if user has all required permissions
            missing_permissions = [
                perm for perm in permissions
                if not has_permission(user_role, perm)
            ]

            if missing_permissions:
                raise PermissionDeniedException(
                    f"User lacks required permissions: {[p.value for p in missing_permissions]}",
                    details={
                        "user_id": current_user.get("user_id"),
                        "user_role": user_role,
                        "missing_permissions": [p.value for p in missing_permissions]
                    }
                )

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
