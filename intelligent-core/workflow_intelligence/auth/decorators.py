"""
Authorization decorators for enforcing permissions
"""

from functools import wraps
from typing import Callable, List, Optional
import inspect

from .middleware import get_auth_context, require_auth_context
from .permissions import WorkflowPermissions
from .exceptions import PermissionDenied, TenantMismatch, InvalidAuthContext


def require_tenant(func: Callable) -> Callable:
    """
    Decorator: Ensure user has valid tenant_id in auth context

    Usage:
        @require_tenant
        async def get_workflow(workflow_id: str):
            # Guaranteed to have auth context with tenant_id
            auth_ctx = get_auth_context()
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get auth context
        auth_ctx = get_auth_context()

        if not auth_ctx:
            raise InvalidAuthContext("No authentication context - login required")

        if not auth_ctx.tenant_id:
            raise InvalidAuthContext("Auth context missing tenant_id")

        # Call original function
        return await func(*args, **kwargs)

    return wrapper


def enforce_tenant_isolation(tenant_id_param: str = "tenant_id") -> Callable:
    """
    Decorator: Enforce that tenant_id parameter matches user's tenant

    Args:
        tenant_id_param: Name of the tenant_id parameter in function

    Usage:
        @enforce_tenant_isolation()
        async def get_workflow(workflow_id: str, tenant_id: str):
            # Guaranteed that tenant_id matches user's tenant
            ...

        @enforce_tenant_isolation(tenant_id_param="resource_tenant")
        async def update_resource(resource_id: str, resource_tenant: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get auth context
            auth_ctx = require_auth_context()

            # Extract tenant_id from kwargs or args
            provided_tenant_id = kwargs.get(tenant_id_param)

            if provided_tenant_id is None:
                # Try to get from positional args
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())

                if tenant_id_param in param_names:
                    param_index = param_names.index(tenant_id_param)

                    # Account for 'self' in methods
                    if param_names[0] == 'self' and len(args) > param_index + 1:
                        provided_tenant_id = args[param_index + 1]
                    elif len(args) > param_index:
                        provided_tenant_id = args[param_index]

            # Validate tenant_id
            if provided_tenant_id is None:
                raise TenantMismatch(
                    f"Missing {tenant_id_param} parameter",
                    user_tenant=auth_ctx.tenant_id,
                    resource_tenant=None
                )

            if provided_tenant_id != auth_ctx.tenant_id:
                raise TenantMismatch(
                    f"Tenant mismatch: user belongs to '{auth_ctx.tenant_id}' "
                    f"but accessing resource from '{provided_tenant_id}'",
                    user_tenant=auth_ctx.tenant_id,
                    resource_tenant=provided_tenant_id
                )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_permission(permission: str) -> Callable:
    """
    Decorator: Require specific permission

    Args:
        permission: Required permission (e.g., WorkflowPermissions.WORKFLOW_CONTEXT_READ)

    Usage:
        @require_permission(WorkflowPermissions.WORKFLOW_CONTEXT_READ)
        async def get_workflow_context(workflow_id: str, tenant_id: str):
            # User has workflow.context.read permission
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get auth context
            auth_ctx = require_auth_context()

            # Check permission
            if not auth_ctx.has_permission(permission):
                raise PermissionDenied(
                    f"Missing required permission: {permission}",
                    required_permission=permission
                )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_any_permission(permissions: List[str]) -> Callable:
    """
    Decorator: Require ANY of the specified permissions

    Args:
        permissions: List of permissions (user needs at least one)

    Usage:
        @require_any_permission([
            WorkflowPermissions.WORKFLOW_CONTEXT_READ,
            WorkflowPermissions.WORKFLOW_ADMIN
        ])
        async def get_workflow_context(workflow_id: str):
            # User has either workflow.context.read OR workflow.admin
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get auth context
            auth_ctx = require_auth_context()

            # Check permissions
            if not auth_ctx.has_any_permission(permissions):
                raise PermissionDenied(
                    f"Missing any of required permissions: {', '.join(permissions)}",
                    required_permission=f"any_of({', '.join(permissions)})"
                )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_all_permissions(permissions: List[str]) -> Callable:
    """
    Decorator: Require ALL of the specified permissions

    Args:
        permissions: List of permissions (user needs all of them)

    Usage:
        @require_all_permissions([
            WorkflowPermissions.WORKFLOW_CONTEXT_UPDATE,
            WorkflowPermissions.WORKFLOW_EXECUTE
        ])
        async def execute_workflow_action(workflow_id: str, action: str):
            # User has both workflow.context.update AND workflow.execute
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get auth context
            auth_ctx = require_auth_context()

            # Check permissions
            if not auth_ctx.has_all_permissions(permissions):
                missing = [p for p in permissions if not auth_ctx.has_permission(p)]
                raise PermissionDenied(
                    f"Missing required permissions: {', '.join(missing)}",
                    required_permission=f"all_of({', '.join(permissions)})"
                )

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_workflow_access(
    permission: str,
    enforce_tenant: bool = True,
    tenant_id_param: str = "tenant_id"
) -> Callable:
    """
    Combined decorator: Permission + Tenant isolation

    Convenience decorator that combines:
    1. require_permission(permission)
    2. enforce_tenant_isolation(tenant_id_param)

    Args:
        permission: Required permission
        enforce_tenant: Whether to enforce tenant isolation (default: True)
        tenant_id_param: Name of tenant_id parameter

    Usage:
        @require_workflow_access(
            WorkflowPermissions.WORKFLOW_CONTEXT_UPDATE,
            enforce_tenant=True
        )
        async def update_workflow_context(
            workflow_id: str,
            context: dict,
            tenant_id: str
        ):
            # User has permission AND tenant_id matches
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Apply decorators in reverse order (they wrap each other)
        decorated = func

        # First: enforce tenant isolation (innermost)
        if enforce_tenant:
            decorated = enforce_tenant_isolation(tenant_id_param)(decorated)

        # Second: check permission (outermost)
        decorated = require_permission(permission)(decorated)

        return decorated

    return decorator
