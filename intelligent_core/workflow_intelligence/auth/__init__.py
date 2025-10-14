"""
Authorization Framework for Workflow Intelligence

Provides decorators and middleware for enforcing permissions at application level.
Works together with RLS for defense-in-depth security.
"""

from .decorators import (
    require_tenant,
    enforce_tenant_isolation,
    require_permission,
    require_any_permission,
    require_all_permissions,
)

from .middleware import (
    AuthContext,
    get_auth_context,
    set_auth_context,
)

from .permissions import (
    Permission,
    PermissionSet,
    WorkflowPermissions,
    check_permission,
    has_any_permission,
    has_all_permissions,
)

from .exceptions import (
    AuthorizationError,
    PermissionDenied,
    TenantMismatch,
    InvalidAuthContext,
)

__all__ = [
    # Decorators
    'require_tenant',
    'enforce_tenant_isolation',
    'require_permission',
    'require_any_permission',
    'require_all_permissions',

    # Middleware
    'AuthContext',
    'get_auth_context',
    'set_auth_context',

    # Permissions
    'Permission',
    'PermissionSet',
    'WorkflowPermissions',
    'check_permission',
    'has_any_permission',
    'has_all_permissions',

    # Exceptions
    'AuthorizationError',
    'PermissionDenied',
    'TenantMismatch',
    'InvalidAuthContext',
]
