"""
API Authentication для Scenario Intelligence
JWT-based authentication с permission checks
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


class TokenData(BaseModel):
    """JWT token payload"""
    user_id: str
    username: str
    roles: list[str]
    permissions: list[str]


class User(BaseModel):
    """User model"""
    user_id: str
    username: str
    roles: list[str]
    permissions: list[str]


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token

    Args:
        data: Payload to encode
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Verify JWT token

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Decoded token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        roles: list = payload.get("roles", [])
        permissions: list = payload.get("permissions", [])

        if user_id is None or username is None:
            raise credentials_exception

        token_data = TokenData(
            user_id=user_id,
            username=username,
            roles=roles,
            permissions=permissions
        )

        return token_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception


async def get_current_user(token_data: TokenData = Depends(verify_token)) -> User:
    """
    Get current authenticated user

    Args:
        token_data: Decoded token data

    Returns:
        User object
    """
    return User(
        user_id=token_data.user_id,
        username=token_data.username,
        roles=token_data.roles,
        permissions=token_data.permissions
    )


def check_permission(required_permission: str):
    """
    Dependency to check if user has required permission

    Args:
        required_permission: Permission string (e.g., "scenarios:execute")

    Returns:
        Dependency function

    Usage:
        @app.post("/scenarios/execute")
        async def execute_scenario(
            user: User = Depends(check_permission("scenarios:execute"))
        ):
            ...
    """
    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        if required_permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {required_permission} required"
            )
        return user

    return permission_checker


def check_role(required_role: str):
    """
    Dependency to check if user has required role

    Args:
        required_role: Role string (e.g., "admin", "scenario_manager")

    Returns:
        Dependency function

    Usage:
        @app.post("/scenarios/register")
        async def register_scenario(
            user: User = Depends(check_role("scenario_manager"))
        ):
            ...
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if required_role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {required_role}"
            )
        return user

    return role_checker


# Permission constants
class Permissions:
    """Permission constants"""
    SCENARIOS_EXECUTE = "scenarios:execute"
    SCENARIOS_REGISTER = "scenarios:register"
    SCENARIOS_READ = "scenarios:read"
    SCENARIOS_DELETE = "scenarios:delete"
    SCENARIOS_ADMIN = "scenarios:admin"


# Role constants
class Roles:
    """Role constants"""
    ADMIN = "admin"
    SCENARIO_MANAGER = "scenario_manager"
    SCENARIO_EXECUTOR = "scenario_executor"
    VIEWER = "viewer"


# Default role permissions mapping
ROLE_PERMISSIONS = {
    Roles.ADMIN: [
        Permissions.SCENARIOS_EXECUTE,
        Permissions.SCENARIOS_REGISTER,
        Permissions.SCENARIOS_READ,
        Permissions.SCENARIOS_DELETE,
        Permissions.SCENARIOS_ADMIN,
    ],
    Roles.SCENARIO_MANAGER: [
        Permissions.SCENARIOS_EXECUTE,
        Permissions.SCENARIOS_REGISTER,
        Permissions.SCENARIOS_READ,
    ],
    Roles.SCENARIO_EXECUTOR: [
        Permissions.SCENARIOS_EXECUTE,
        Permissions.SCENARIOS_READ,
    ],
    Roles.VIEWER: [
        Permissions.SCENARIOS_READ,
    ],
}


def get_permissions_for_role(role: str) -> list[str]:
    """Get permissions for a role"""
    return ROLE_PERMISSIONS.get(role, [])
