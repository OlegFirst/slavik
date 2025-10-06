"""
Permission definitions and checking
"""

from enum import Enum
from typing import List, Set
from dataclasses import dataclass


class Permission(str, Enum):
    """Base permission enumeration"""
    pass


class WorkflowPermissions(Permission):
    """
    Workflow-specific permissions

    Naming convention: <module>.<resource>.<action>
    """

    # Workflow context permissions
    WORKFLOW_CONTEXT_READ = "workflow.context.read"
    WORKFLOW_CONTEXT_CREATE = "workflow.context.create"
    WORKFLOW_CONTEXT_UPDATE = "workflow.context.update"
    WORKFLOW_CONTEXT_DELETE = "workflow.context.delete"

    # Workflow case permissions
    WORKFLOW_CASE_READ = "workflow.case.read"
    WORKFLOW_CASE_CREATE = "workflow.case.create"
    WORKFLOW_CASE_UPDATE = "workflow.case.update"
    WORKFLOW_CASE_DELETE = "workflow.case.delete"

    # Workflow execution permissions
    WORKFLOW_EXECUTE = "workflow.execute"
    WORKFLOW_EXECUTE_ACTION = "workflow.execute_action"

    # Benchmarks (read-only for most users)
    WORKFLOW_BENCHMARKS_READ = "workflow.benchmarks.read"
    WORKFLOW_BENCHMARKS_ADMIN = "workflow.benchmarks.admin"

    # ML predictions
    WORKFLOW_PREDICTION_READ = "workflow.prediction.read"
    WORKFLOW_PREDICTION_CREATE = "workflow.prediction.create"

    # Admin permissions
    WORKFLOW_ADMIN = "workflow.admin"


@dataclass
class PermissionSet:
    """
    Set of permissions for a user

    Can be loaded from:
    - JWT claims
    - Database
    - External auth service (Keycloak, Auth0, etc)
    """
    permissions: Set[str]

    def has(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions or WorkflowPermissions.WORKFLOW_ADMIN.value in self.permissions

    def has_any(self, permissions: List[str]) -> bool:
        """Check if user has ANY of the permissions"""
        if WorkflowPermissions.WORKFLOW_ADMIN.value in self.permissions:
            return True
        return any(p in self.permissions for p in permissions)

    def has_all(self, permissions: List[str]) -> bool:
        """Check if user has ALL of the permissions"""
        if WorkflowPermissions.WORKFLOW_ADMIN.value in self.permissions:
            return True
        return all(p in self.permissions for p in permissions)

    @classmethod
    def from_list(cls, permissions: List[str]) -> "PermissionSet":
        """Create PermissionSet from list of permission strings"""
        return cls(permissions=set(permissions))

    @classmethod
    def from_jwt_claims(cls, claims: dict) -> "PermissionSet":
        """
        Extract permissions from JWT claims

        Supports multiple claim formats:
        - {"permissions": ["workflow.context.read", ...]}
        - {"scope": "workflow.context.read workflow.context.create"}
        - {"roles": ["workflow_admin"]} -> mapped to permissions
        """
        permissions = set()

        # Standard permissions claim
        if "permissions" in claims:
            permissions.update(claims["permissions"])

        # OAuth2 scope claim (space-separated)
        if "scope" in claims:
            scopes = claims["scope"].split()
            permissions.update(scopes)

        # Role-based mapping
        if "roles" in claims:
            roles = claims["roles"]
            permissions.update(_map_roles_to_permissions(roles))

        return cls(permissions=permissions)


def _map_roles_to_permissions(roles: List[str]) -> Set[str]:
    """
    Map roles to permissions

    Example role mappings:
    - workflow_admin -> all workflow permissions
    - workflow_user -> read/create permissions
    - workflow_viewer -> read-only permissions
    """
    permissions = set()

    for role in roles:
        if role == "workflow_admin":
            permissions.add(WorkflowPermissions.WORKFLOW_ADMIN.value)
        elif role == "workflow_user":
            permissions.update([
                WorkflowPermissions.WORKFLOW_CONTEXT_READ.value,
                WorkflowPermissions.WORKFLOW_CONTEXT_CREATE.value,
                WorkflowPermissions.WORKFLOW_CONTEXT_UPDATE.value,
                WorkflowPermissions.WORKFLOW_CASE_READ.value,
                WorkflowPermissions.WORKFLOW_CASE_CREATE.value,
                WorkflowPermissions.WORKFLOW_EXECUTE.value,
                WorkflowPermissions.WORKFLOW_EXECUTE_ACTION.value,
                WorkflowPermissions.WORKFLOW_BENCHMARKS_READ.value,
                WorkflowPermissions.WORKFLOW_PREDICTION_READ.value,
            ])
        elif role == "workflow_viewer":
            permissions.update([
                WorkflowPermissions.WORKFLOW_CONTEXT_READ.value,
                WorkflowPermissions.WORKFLOW_CASE_READ.value,
                WorkflowPermissions.WORKFLOW_BENCHMARKS_READ.value,
                WorkflowPermissions.WORKFLOW_PREDICTION_READ.value,
            ])

    return permissions


def check_permission(user_permissions: PermissionSet, required_permission: str) -> bool:
    """
    Check if user has required permission

    Args:
        user_permissions: User's permission set
        required_permission: Permission to check

    Returns:
        True if user has permission, False otherwise
    """
    return user_permissions.has(required_permission)


def has_any_permission(user_permissions: PermissionSet, required_permissions: List[str]) -> bool:
    """Check if user has ANY of the required permissions"""
    return user_permissions.has_any(required_permissions)


def has_all_permissions(user_permissions: PermissionSet, required_permissions: List[str]) -> bool:
    """Check if user has ALL of the required permissions"""
    return user_permissions.has_all(required_permissions)
