"""
Authentication Service - FastAPI + JWT
ISO 22301 BCM Platform Authentication and Multi-tenancy
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
import utils
import json
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from db import init_db, get_session, AsyncSessionLocal
import crud
from models import User

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "bcm-platform-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# Security scheme
security = HTTPBearer()

# Models
class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    tenant_domain: Optional[str] = Field(None, description="Tenant domain (optional)")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
    tenant: Dict[str, Any]

class UserInfo(BaseModel):
    id: str
    email: str
    full_name: str
    tenant_id: str
    roles: List[str]
    is_active: bool

class TenantInfo(BaseModel):
    id: str
    name: str
    domain: str
    plan: str
    is_active: bool
    settings: Dict[str, Any]

class CreateUserRequest(BaseModel):
    email: str
    password: str
    full_name: str
    tenant_id: str
    roles: List[str] = ["user"]

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Authentication service...")
    await init_db()
    async with AsyncSessionLocal() as session:
        u_count = await crud.users_count(session)
        t_count = await crud.tenants_count(session)
    logger.info(f"Configured {u_count} users and {t_count} tenants")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Authentication service...")

# Create FastAPI app
# Валидация JWT ключа
try:
    jwt_secret = utils.validate_jwt_secret()
    print(f"JWT ключ валиден")
except ValueError as e:
    print(f"Ошибка: {str(e)}")
    import sys
    sys.exit(1)
app = FastAPI(
    title="BCM Authentication Service",
    description="Authentication and multi-tenancy for ISO 22301 BCM Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")

        if user_id is None or tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_obj = await crud.get_user_by_id(session, user_id)
        if not user_obj or not user_obj.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        tenant_obj = await crud.get_tenant_by_id(session, tenant_id)
        if not tenant_obj or not tenant_obj.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = UserInfo.model_validate(user_obj, from_attributes=True).model_dump()
        tenant = TenantInfo.model_validate(tenant_obj, from_attributes=True).model_dump()

        return {"user": user, "tenant": tenant, "token_data": payload}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# Health check
@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    u_count = await crud.users_count(session)
    t_count = await crud.tenants_count(session)
    return {
        "status": "healthy",
        "service": "authentication",
        "users_count": u_count,
        "tenants_count": t_count,
    }

# Authentication endpoints
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, session: AsyncSession = Depends(get_session)):
    """Authenticate user and return JWT token"""
    try:
        # Find user
        user_obj = await crud.get_user_by_email(session, login_data.email)
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(login_data.password, user_obj.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if user is active
        if not user_obj.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )

        # Get tenant
        tenant_obj = await crud.get_tenant_by_id(session, user_obj.tenant_id)
        if not tenant_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant not found"
            )

        # Check tenant domain if provided
        if login_data.tenant_domain and tenant_obj.domain != login_data.tenant_domain:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid tenant domain"
            )
        
        # Create token
        token_data = {
            "sub": user_obj.id,
            "email": user_obj.email,
            "tenant_id": user_obj.tenant_id,
            "roles": user_obj.roles
        }
        
        access_token = create_access_token(token_data)
        
        # Clean user and tenant data for response
        user_response = UserInfo.model_validate(user_obj, from_attributes=True).model_dump()
        tenant_response = TenantInfo.model_validate(tenant_obj, from_attributes=True).model_dump()
        
        logger.info(f"User {user['email']} logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            expires_in=JWT_EXPIRE_MINUTES * 60,
            user=user_response,
            tenant=tenant_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@app.get("/api/auth/me")
async def get_current_user(auth_data = Depends(verify_token)):
    """Get current user information"""
    user = auth_data["user"]
    tenant = auth_data["tenant"]
    
    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "tenant_id": user["tenant_id"],
            "roles": user["roles"]
        },
        "tenant": {
            "id": tenant["id"],
            "name": tenant["name"],
            "domain": tenant["domain"],
            "plan": tenant["plan"],
            "settings": tenant["settings"]
        }
    }

@app.post("/api/auth/refresh")
async def refresh_token(auth_data = Depends(verify_token)):
    """Refresh JWT token"""
    user = auth_data["user"]
    
    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "tenant_id": user["tenant_id"],
        "roles": user["roles"]
    }
    
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_MINUTES * 60
    }

@app.post("/api/auth/logout")
async def logout(auth_data = Depends(verify_token)):
    """Logout user (in production, add token to blacklist)"""
    user = auth_data["user"]
    logger.info(f"User {user['email']} logged out")
    
    return {"message": "Logged out successfully"}

# User management (admin only)
@app.post("/api/auth/users", response_model=UserInfo)
async def create_user(
    user_data: CreateUserRequest,
    auth_data = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    """Create new user (admin only)"""
    current_user = auth_data["user"]

    if "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    existing = await crud.get_user_by_email(session, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    tenant = await crud.get_tenant_by_id(session, user_data.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID",
        )

    count = await crud.users_count(session)
    user_id = f"user_{count + 1:03d}"
    password_hash = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()

    user_obj = User(
        id=user_id,
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        tenant_id=user_data.tenant_id,
        roles=user_data.roles,
        is_active=True,
        created_at=datetime.utcnow(),
    )

    await crud.create_user(session, user_obj)

    logger.info(f"User {user_data.email} created by {current_user['email']}")

    return UserInfo.model_validate(user_obj, from_attributes=True)

@app.get("/api/auth/users")
async def list_users(auth_data = Depends(verify_token), session: AsyncSession = Depends(get_session)):
    """List users in current tenant"""
    current_user = auth_data["user"]
    tenant = auth_data["tenant"]

    users = await crud.list_users_by_tenant(session, tenant["id"])
    tenant_users = [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "roles": u.roles,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]

    return {"users": tenant_users}
@app.get("/api/auth/tenants")
async def list_tenants(auth_data = Depends(verify_token), session: AsyncSession = Depends(get_session)):
    """List all tenants (admin only)"""
    current_user = auth_data["user"]

    if "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    tenants = await crud.list_tenants(session)
    tenants_list = [
        {
            "id": t.id,
            "name": t.name,
            "domain": t.domain,
            "plan": t.plan,
            "is_active": t.is_active,
            "created_at": t.created_at.isoformat(),
        }
        for t in tenants
    ]

    return {"tenants": tenants_list}
@app.post("/api/auth/validate")
async def validate_token_and_tenant(token: str, tenant_id: Optional[str] = None):
    """Validate token and optionally check tenant access"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        token_tenant_id = payload.get("tenant_id")

        async with AsyncSessionLocal() as session:
            user_obj = await crud.get_user_by_id(session, user_id)
            if not user_obj or not user_obj.is_active:
                return {"valid": False, "error": "User not found or inactive"}

            if tenant_id and token_tenant_id != tenant_id:
                return {"valid": False, "error": "Tenant access denied"}

            tenant_obj = await crud.get_tenant_by_id(session, token_tenant_id)
            if not tenant_obj or not tenant_obj.is_active:
                return {"valid": False, "error": "Tenant not found or inactive"}

        return {
            "valid": True,
            "user_id": user_id,
            "email": user_obj.email,
            "tenant_id": token_tenant_id,
            "roles": user_obj.roles,
        }
        
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expired"}
    except jwt.JWTError:
        return {"valid": False, "error": "Invalid token"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
