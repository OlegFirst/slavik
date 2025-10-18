"""
Authentication & Authorization Middleware for Digital Twin
Integrates with infrastructure/security/auth

Provides:
- JWT token validation
- Multi-tenancy (organization_id, tenant_id)
- Row-Level Security (RLS) context
- User permission checking
"""

import logging
import httpx
import jwt
from typing import Dict, Any, Optional
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# JWT Configuration (should match auth service)
JWT_SECRET_KEY = "bcm-platform-secret-key-change-in-production"  # TODO: Move to env
JWT_ALGORITHM = "HS256"


class AuthMiddleware:
    """
    Authentication Middleware for Digital Twin

    Integrates with infrastructure/security/auth for:
    - JWT validation
    - User authentication
    - Organization/tenant context
    - RLS context setting
    """

    def __init__(
        self,
        auth_service_url: str = "http://localhost:8001",
        jwt_secret: Optional[str] = None,
        jwt_algorithm: str = "HS256"
    ):
        """
        Initialize auth middleware

        Args:
            auth_service_url: URL of auth service
            jwt_secret: JWT secret key (if validating locally)
            jwt_algorithm: JWT algorithm
        """
        self.auth_service_url = auth_service_url.rstrip('/')
        self.jwt_secret = jwt_secret or JWT_SECRET_KEY
        self.jwt_algorithm = jwt_algorithm
        self.client = httpx.AsyncClient(timeout=10.0)

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token

        Args:
            token: JWT token string

        Returns:
            Token payload with user info

        Raises:
            HTTPException if token invalid
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError as error:
            logger.error(f"JWT validation error: {error}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials
    ) -> Dict[str, Any]:
        """
        Get current authenticated user from token

        Args:
            credentials: HTTP bearer credentials

        Returns:
            User information dict with:
            - id: User ID
            - email: User email
            - organization_id: Organization ID (for multi-tenancy)
            - tenant_id: Tenant ID (for RLS)
            - role: User role
        """
        token = credentials.credentials
        payload = await self.verify_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Extract user info from token
        return {
            "id": user_id,
            "email": payload.get("email"),
            "organization_id": payload.get("organization_id"),
            "tenant_id": payload.get("tenant_id"),  # For RLS
            "role": payload.get("role", "user"),
            "is_authenticated": True
        }

    async def get_user_from_auth_service(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user info from auth service /me endpoint

        Args:
            token: JWT token

        Returns:
            User info or None if service unavailable
        """
        try:
            response = await self.client.get(
                f"{self.auth_service_url}/me",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                return response.json()

        except Exception as error:
            logger.warning(f"Failed to fetch user from auth service: {error}")

        return None

    async def check_organization_access(
        self,
        user: Dict[str, Any],
        organization_id: str
    ) -> bool:
        """
        Check if user has access to organization

        Args:
            user: User dict
            organization_id: Organization ID to check

        Returns:
            True if user has access
        """
        # User's organization must match
        user_org = user.get("organization_id")

        if not user_org:
            return False

        return user_org == organization_id

    async def check_permission(
        self,
        user: Dict[str, Any],
        permission: str
    ) -> bool:
        """
        Check if user has specific permission

        Args:
            user: User dict
            permission: Permission to check (e.g., "simulations.create")

        Returns:
            True if user has permission
        """
        role = user.get("role", "user")

        # Role-based permissions
        role_permissions = {
            "admin": "*",  # All permissions
            "manager": [
                "simulations.create",
                "simulations.read",
                "simulations.update",
                "digital_twin.read",
                "digital_twin.update",
                "topology.read"
            ],
            "user": [
                "simulations.read",
                "digital_twin.read",
                "topology.read"
            ],
            "viewer": [
                "simulations.read",
                "digital_twin.read",
                "topology.read"
            ]
        }

        permissions = role_permissions.get(role, [])

        # Admin has all permissions
        if permissions == "*":
            return True

        # Check if permission in list
        return permission in permissions

    def set_rls_context(
        self,
        db_connection: Any,
        user: Dict[str, Any]
    ):
        """
        Set Row-Level Security context for database queries

        Args:
            db_connection: Database connection
            user: User dict with tenant_id and organization_id
        """
        try:
            # Set RLS variables
            tenant_id = user.get("tenant_id") or user.get("organization_id", "")
            user_id = user.get("id", "")

            # Execute RLS context setting
            db_connection.execute(
                "SET LOCAL app.current_tenant_id = %s",
                (tenant_id,)
            )
            db_connection.execute(
                "SET LOCAL app.current_user_id = %s",
                (user_id,)
            )

            logger.debug(f"RLS context set: tenant={tenant_id}, user={user_id}")

        except Exception as error:
            logger.error(f"Failed to set RLS context: {error}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# ==================== FastAPI Dependencies ====================

# Global middleware instance
auth_middleware = AuthMiddleware()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user

    Usage:
        @app.get("/protected")
        async def protected_route(user: Dict = Depends(get_current_user)):
            return {"user_id": user["id"]}
    """
    return await auth_middleware.get_current_user(credentials)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for optional authentication

    Returns None if no token provided
    """
    if not credentials:
        return None

    try:
        return await auth_middleware.get_current_user(credentials)
    except HTTPException:
        return None


def require_permission(permission: str):
    """
    Dependency factory for permission checking

    Usage:
        @app.post("/simulations")
        async def create_simulation(
            user: Dict = Depends(require_permission("simulations.create"))
        ):
            ...
    """
    async def check_permission_dependency(
        user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        has_permission = await auth_middleware.check_permission(user, permission)

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )

        return user

    return check_permission_dependency


def require_organization_access(organization_id_param: str = "organization_id"):
    """
    Dependency factory for organization access checking

    Usage:
        @app.get("/organizations/{organization_id}/data")
        async def get_org_data(
            organization_id: str,
            user: Dict = Depends(require_organization_access())
        ):
            ...
    """
    async def check_org_access_dependency(
        request: Request,
        user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        # Get organization_id from path params
        organization_id = request.path_params.get(organization_id_param)

        if not organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID required"
            )

        has_access = await auth_middleware.check_organization_access(
            user,
            organization_id
        )

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this organization"
            )

        return user

    return check_org_access_dependency


# ==================== Request Context ====================

class RequestContext:
    """
    Request context with user and organization info

    Provides easy access to authentication context in routes
    """

    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.user_id = user["id"]
        self.organization_id = user.get("organization_id")
        self.tenant_id = user.get("tenant_id") or user.get("organization_id")
        self.role = user.get("role", "user")
        self.email = user.get("email")

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == "admin"

    @property
    def is_manager(self) -> bool:
        """Check if user is manager or above"""
        return self.role in ["admin", "manager"]

    def has_permission(self, permission: str) -> bool:
        """Check if user has permission"""
        # Simplified check - in production, use auth_middleware.check_permission
        if self.role == "admin":
            return True

        manager_permissions = [
            "simulations.create", "simulations.read", "simulations.update",
            "digital_twin.read", "digital_twin.update", "topology.read"
        ]

        user_permissions = [
            "simulations.read", "digital_twin.read", "topology.read"
        ]

        if self.role == "manager":
            return permission in manager_permissions

        return permission in user_permissions


async def get_request_context(
    user: Dict[str, Any] = Depends(get_current_user)
) -> RequestContext:
    """
    FastAPI dependency to get request context

    Usage:
        @app.get("/my-route")
        async def my_route(ctx: RequestContext = Depends(get_request_context)):
            if ctx.is_admin:
                # Admin-only logic
            return {"organization_id": ctx.organization_id}
    """
    return RequestContext(user)
