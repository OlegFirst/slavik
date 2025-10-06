"""Authentication and authorization module."""

from .jwt import JWTManager, init_jwt, get_current_user
from .permissions import Role, Permission, ROLE_PERMISSIONS, require_permission
from .dependencies import get_current_user_dep, require_role, require_admin

# Also export jwt_handler functions for direct use
try:
    from .jwt_handler import (
        create_access_token as create_token,
        verify_token,
        get_current_user as extract_user
    )
except ImportError:
    # jwt_handler not available, use legacy jwt
    pass

__all__ = [
    "JWTManager",
    "init_jwt",
    "get_current_user",
    "get_current_user_dep",
    "require_role",
    "require_admin",
    "Role",
    "Permission",
    "ROLE_PERMISSIONS",
    "require_permission",
]
