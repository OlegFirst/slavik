"""
JWT Token Manager
=================

JWT authentication for BCM Platform services.

Features:
- Token creation and verification
- FastAPI dependency for current user
- HTTPBearer security scheme
- Configurable expiration
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# HTTP Bearer security scheme
security = HTTPBearer()


class JWTManager:
    """
    JWT token manager.

    Handles creation and verification of JWT tokens for authentication.

    Example:
        ```python
        # Initialize at startup
        jwt_manager = init_jwt(settings.JWT_SECRET_KEY)

        # Create token
        token = jwt_manager.create_token(
            user_id="user123",
            tenant_id="tenant456",
            role="bcm_manager",
            expires_hours=24
        )

        # Verify token
        payload = jwt_manager.verify_token(token)
        ```
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize JWT manager.

        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(
        self,
        user_id: str,
        tenant_id: str,
        role: str,
        expires_hours: int = 24,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create JWT token.

        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            role: User role (e.g., "bcm_manager", "auditor")
            expires_hours: Token expiration in hours (default: 24)
            additional_claims: Additional claims to include in token

        Returns:
            str: Encoded JWT token

        Example:
            ```python
            token = jwt_manager.create_token(
                user_id="user123",
                tenant_id="tenant456",
                role="bcm_manager",
                expires_hours=12,
                additional_claims={"email": "user@example.com"}
            )
            ```
        """
        exp = datetime.utcnow() + timedelta(hours=expires_hours)

        payload = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "role": role,
            "exp": exp,
            "iat": datetime.utcnow()
        }

        # Add additional claims if provided
        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return payload.

        Args:
            token: JWT token to verify

        Returns:
            dict: Token payload

        Raises:
            HTTPException: If token is expired or invalid

        Example:
            ```python
            try:
                payload = jwt_manager.verify_token(token)
                user_id = payload["user_id"]
            except HTTPException as e:
                print(f"Invalid token: {e.detail}")
            ```
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def decode_token_no_verify(self, token: str) -> Dict[str, Any]:
        """
        Decode token without verification (for debugging only).

        Args:
            token: JWT token

        Returns:
            dict: Token payload

        Warning:
            This method does NOT verify the token signature.
            Use only for debugging or inspection purposes.
        """
        return jwt.decode(
            token,
            options={"verify_signature": False}
        )


# Global JWT manager instance
_jwt_manager: Optional[JWTManager] = None


def init_jwt(secret_key: str, algorithm: str = "HS256") -> JWTManager:
    """
    Initialize global JWT manager.

    Call this once during application startup.

    Args:
        secret_key: Secret key for signing tokens
        algorithm: JWT algorithm (default: HS256)

    Returns:
        JWTManager: Initialized JWT manager

    Example:
        ```python
        @app.on_event("startup")
        async def startup():
            init_jwt(settings.JWT_SECRET_KEY)
        ```
    """
    global _jwt_manager
    _jwt_manager = JWTManager(secret_key, algorithm)
    return _jwt_manager


def get_jwt_manager() -> JWTManager:
    """
    Get global JWT manager instance.

    Returns:
        JWTManager: Global JWT manager

    Raises:
        RuntimeError: If JWT manager not initialized
    """
    if _jwt_manager is None:
        raise RuntimeError(
            "JWT manager not initialized. Call init_jwt() during startup."
        )
    return _jwt_manager


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency for getting current user from JWT token.

    Extracts and verifies JWT token from Authorization header.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        dict: User payload from token (user_id, tenant_id, role, etc.)

    Raises:
        HTTPException: If token is missing or invalid

    Example:
        ```python
        @router.get("/profile")
        async def get_profile(current_user: dict = Depends(get_current_user)):
            return {
                "user_id": current_user["user_id"],
                "tenant_id": current_user["tenant_id"],
                "role": current_user["role"]
            }
        ```
    """
    jwt_manager = get_jwt_manager()
    token = credentials.credentials
    payload = jwt_manager.verify_token(token)
    return payload


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for optional authentication.

    Returns user if token is provided, None otherwise.

    Args:
        credentials: HTTP authorization credentials (optional)

    Returns:
        dict or None: User payload if authenticated, None otherwise

    Example:
        ```python
        @router.get("/public-data")
        async def get_data(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                # Return personalized data
                return get_user_data(user["user_id"])
            else:
                # Return public data
                return get_public_data()
        ```
    """
    if credentials is None:
        return None

    try:
        jwt_manager = get_jwt_manager()
        token = credentials.credentials
        payload = jwt_manager.verify_token(token)
        return payload
    except HTTPException:
        return None
