"""
Authentication Router

Endpoints for user registration, login, and token management
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field

from api.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user
)
from storage.postgres_storage import PostgreSQLStorage


router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage instance"""
    return request.app.state.app_state.storage


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(None, description="Full name")
    tenant_name: Optional[str] = Field(None, description="Tenant name (for new tenant)")


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=1800, description="Token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="JWT refresh token")


class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    full_name: Optional[str]
    tenant_id: str
    tenant_name: str
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime


class MeResponse(BaseModel):
    """Current user response"""
    user: UserResponse
    tenant: dict


# ============================================
# AUTH ENDPOINTS
# ============================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Register new user and create tenant

    Creates:
    - New tenant (if tenant_name provided)
    - New user with hashed password
    - Returns JWT tokens for immediate login
    """
    # Check if user already exists
    existing_user = await storage.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create tenant
    tenant_id = f"tenant-{uuid4().hex[:12]}"
    tenant_slug = request.tenant_name.lower().replace(" ", "-") if request.tenant_name else f"tenant-{uuid4().hex[:8]}"

    tenant_data = {
        "id": tenant_id,
        "name": request.tenant_name or f"Tenant {tenant_id}",
        "slug": tenant_slug,
        "plan": "free",
        "is_active": True,
        "is_trial": True,
    }

    tenant = await storage.create_tenant(tenant_data)

    # Create user
    user_id = f"user-{uuid4().hex[:12]}"
    hashed_pwd = hash_password(request.password)

    user_data = {
        "id": user_id,
        "tenant_id": tenant_id,
        "email": request.email,
        "hashed_password": hashed_pwd,
        "full_name": request.full_name,
        "is_active": True,
        "is_superuser": False,
        "is_email_verified": False,
        "role": "admin",  # First user is admin of tenant
    }

    user = await storage.create_user(user_data)

    # Generate tokens
    access_token = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email
    )

    refresh_token = create_refresh_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Login user with email and password

    Returns JWT access and refresh tokens
    """
    # Get user by email
    user = await storage.get_user_by_email(request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )

    # Update last login
    await storage.update_user(user.id, {"last_login": datetime.utcnow()})

    # Generate tokens
    access_token = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email
    )

    refresh_token = create_refresh_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        email=user.email
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Refresh access token using refresh token

    Returns new access and refresh tokens
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token, expected_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    email = payload.get("email")

    # Verify user still exists and is active
    user = await storage.get_user(user_id=user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    access_token = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        email=email
    )

    new_refresh_token = create_refresh_token(
        user_id=user_id,
        tenant_id=tenant_id,
        email=email
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=1800
    )


@router.get("/me", response_model=MeResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user),
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get current authenticated user information

    Requires valid JWT token
    """
    # Get tenant info
    tenant = await storage.get_tenant(tenant_id=current_user.tenant_id)

    user_response = UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        tenant_id=current_user.tenant_id,
        tenant_name=tenant.name if tenant else "Unknown",
        role=current_user.role,
        is_active=current_user.is_active,
        is_email_verified=current_user.is_email_verified,
        created_at=current_user.created_at
    )

    tenant_info = {
        "id": tenant.id,
        "name": tenant.name,
        "slug": tenant.slug,
        "plan": tenant.plan,
        "is_active": tenant.is_active,
    } if tenant else {}

    return MeResponse(
        user=user_response,
        tenant=tenant_info
    )


@router.post("/logout")
async def logout(
    current_user = Depends(get_current_active_user)
):
    """
    Logout user

    Note: With JWT, logout is client-side (delete token).
    This endpoint is for consistency and can track logout events.
    """
    # In a production app, you might:
    # - Add token to blacklist
    # - Track logout event
    # - Clear refresh tokens from database

    return {
        "status": "success",
        "message": "Successfully logged out"
    }
