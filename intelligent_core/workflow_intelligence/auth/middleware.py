"""
Auth context middleware and management
"""

from typing import Optional
from contextvars import ContextVar
from dataclasses import dataclass

from .permissions import PermissionSet
from .exceptions import InvalidAuthContext


# Context variable for storing auth context in async context
_auth_context_var: ContextVar[Optional['AuthContext']] = ContextVar('auth_context', default=None)


@dataclass
class AuthContext:
    """
    Authentication and authorization context

    Contains all necessary information for authorization decisions:
    - user_id: Unique user identifier
    - tenant_id: Tenant the user belongs to
    - permissions: User's permission set
    - metadata: Additional auth metadata (JWT claims, session info, etc)
    """

    user_id: str
    tenant_id: str
    permissions: PermissionSet
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @classmethod
    def from_jwt(cls, jwt_payload: dict) -> "AuthContext":
        """
        Create AuthContext from JWT payload

        Expected JWT structure:
        {
            "sub": "user_id",
            "tenant_id": "tenant_001",
            "permissions": ["workflow.context.read", ...],
            "roles": ["workflow_user"],
            ...
        }
        """
        user_id = jwt_payload.get("sub") or jwt_payload.get("user_id")
        tenant_id = jwt_payload.get("tenant_id")

        if not user_id:
            raise InvalidAuthContext("JWT payload missing 'sub' or 'user_id'")

        if not tenant_id:
            raise InvalidAuthContext("JWT payload missing 'tenant_id'")

        # Extract permissions
        permissions = PermissionSet.from_jwt_claims(jwt_payload)

        return cls(
            user_id=user_id,
            tenant_id=tenant_id,
            permissions=permissions,
            metadata=jwt_payload
        )

    @classmethod
    def from_request_headers(cls, headers: dict) -> "AuthContext":
        """
        Create AuthContext from HTTP headers

        Expected headers:
        - X-User-ID: user_id
        - X-Tenant-ID: tenant_id
        - X-User-Permissions: comma-separated permission list

        This is simpler alternative to JWT for internal services.
        """
        user_id = headers.get("x-user-id") or headers.get("X-User-ID")
        tenant_id = headers.get("x-tenant-id") or headers.get("X-Tenant-ID")
        permissions_str = headers.get("x-user-permissions") or headers.get("X-User-Permissions") or ""

        if not user_id:
            raise InvalidAuthContext("Missing X-User-ID header")

        if not tenant_id:
            raise InvalidAuthContext("Missing X-Tenant-ID header")

        # Parse permissions
        permissions_list = [p.strip() for p in permissions_str.split(",") if p.strip()]
        permissions = PermissionSet.from_list(permissions_list)

        return cls(
            user_id=user_id,
            tenant_id=tenant_id,
            permissions=permissions,
            metadata={"headers": headers}
        )

    def has_permission(self, permission: str) -> bool:
        """Check if context has specific permission"""
        return self.permissions.has(permission)

    def has_any_permission(self, permissions: list) -> bool:
        """Check if context has any of the permissions"""
        return self.permissions.has_any(permissions)

    def has_all_permissions(self, permissions: list) -> bool:
        """Check if context has all of the permissions"""
        return self.permissions.has_all(permissions)


def get_auth_context() -> Optional[AuthContext]:
    """
    Get current auth context from async context

    Returns:
        AuthContext if set, None otherwise

    Usage:
        auth_ctx = get_auth_context()
        if not auth_ctx:
            raise InvalidAuthContext("No auth context set")
    """
    return _auth_context_var.get()


def set_auth_context(context: AuthContext) -> None:
    """
    Set auth context for current async context

    Args:
        context: AuthContext to set

    Usage:
        auth_ctx = AuthContext.from_jwt(jwt_payload)
        set_auth_context(auth_ctx)
    """
    _auth_context_var.set(context)


def clear_auth_context() -> None:
    """Clear auth context"""
    _auth_context_var.set(None)


def require_auth_context() -> AuthContext:
    """
    Get auth context, raise if not set

    Returns:
        AuthContext

    Raises:
        InvalidAuthContext if no context is set

    Usage:
        auth_ctx = require_auth_context()
        # Guaranteed to have auth_ctx here
    """
    context = get_auth_context()
    if context is None:
        raise InvalidAuthContext("No authentication context available")
    return context
