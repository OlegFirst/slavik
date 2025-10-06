"""
Authorization exceptions
"""


class AuthorizationError(Exception):
    """Base class for authorization errors"""
    pass


class PermissionDenied(AuthorizationError):
    """User does not have required permission"""

    def __init__(self, message: str = "Permission denied", required_permission: str = None):
        self.required_permission = required_permission
        super().__init__(message)


class TenantMismatch(AuthorizationError):
    """Tenant ID mismatch - user trying to access another tenant's data"""

    def __init__(
        self,
        message: str = "Tenant mismatch",
        user_tenant: str = None,
        resource_tenant: str = None
    ):
        self.user_tenant = user_tenant
        self.resource_tenant = resource_tenant
        super().__init__(message)


class InvalidAuthContext(AuthorizationError):
    """Auth context is missing or invalid"""

    def __init__(self, message: str = "Invalid or missing auth context"):
        super().__init__(message)
