"""
Authentication Service for AI-Powered BCM Platform
FastAPI + JWT + Supabase Auth + RLS Integration

Adapted from BCM_1/auth_service with new architecture:
- Uses new database managers
- Uses Redis session store
- Integrates with Supabase Auth
- Sets RLS context
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import jwt
import bcrypt
import os
import logging
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Add infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

sys.path.insert(0, '/Users/MD/AI-Platform-ISO/infrastructure/database/postgresql')
from managers.supabase_client import get_supabase_client
import redis.asyncio as redis

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "bcm-platform-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Security
security = HTTPBearer()

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    organization_domain: Optional[str] = None


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
    organization: Optional[Dict[str, Any]] = None


class UserInfo(BaseModel):
    id: str
    email: str
    full_name: str
    organization_id: Optional[str]
    role: str
    is_active: bool


# ============================================
# LIFECYCLE MANAGEMENT
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle"""
    # Startup
    logger.info("🚀 Starting Authentication Service...")

    # Initialize connections
    business_db.connect()
    await redis_manager.connect()
    await supabase_manager.connect()

    logger.info("✅ All connections initialized")

    # Check database
    result = business_db.execute("SELECT COUNT(*) FROM public.organizations", commit=False)
    org_count = result[0][0] if result else 0
    logger.info(f"📊 Organizations in database: {org_count}")

    yield

    # Shutdown
    logger.info("⏹️  Shutting down Authentication Service...")
    business_db.disconnect()
    await redis_manager.disconnect()
    await supabase_manager.disconnect()


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="BCM Authentication Service",
    description="Authentication & Authorization for AI-Powered BCM Platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# JWT UTILITIES
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


# ============================================
# DEPENDENCIES
# ============================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Get user from database
    result = business_db.execute(
        "SELECT id, email, full_name, is_active FROM public.user_profiles WHERE id = %s",
        (user_id,),
        commit=False
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    user = result[0]

    if not user[3]:  # is_active
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return {
        "id": str(user[0]),
        "email": user[1],
        "full_name": user[2],
        "is_active": user[3],
        "organization_id": payload.get("organization_id"),
        "role": payload.get("role", "user")
    }


async def set_rls_context(
    user: Dict = Depends(get_current_user),
    request: Request = None
):
    """Set RLS context for database queries"""
    # This will be used by routes that need RLS
    if hasattr(request.state, "db_cursor"):
        RLSManager.set_rls_context(
            request.state.db_cursor,
            user["id"],
            user.get("organization_id", "")
        )


# ============================================
# AUTH ENDPOINTS
# ============================================

@app.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """
    Register new user

    Creates user via Supabase Auth and user profile in database
    """
    try:
        # 1. Create user in Supabase Auth
        auth_response = supabase_manager.sign_up(
            request.email,
            request.password,
            user_metadata={"full_name": request.full_name}
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        user_id = auth_response.user.id

        # 2. Create organization if needed
        organization_id = None
        organization = None

        if request.organization_name:
            import uuid
            import time
            tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
            org_slug = f"{request.organization_name.lower().replace(' ', '-')}-{int(time.time())}"

            org_result = business_db.execute(
                """
                INSERT INTO public.organizations (name, slug, tenant_id, settings)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, slug
                """,
                (
                    request.organization_name,
                    org_slug,
                    tenant_id,
                    '{"plan": "free"}'
                ),
                commit=True
            )

            if org_result:
                organization_id = str(org_result[0][0])
                organization = {
                    "id": organization_id,
                    "name": org_result[0][1],
                    "slug": org_result[0][2]
                }

        # 3. Create user profile
        # Parse full_name into first_name and last_name
        name_parts = request.full_name.split(" ", 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        business_db.execute(
            """
            INSERT INTO public.user_profiles (id, user_id, email, first_name, last_name, is_active)
            VALUES (%s, %s, %s, %s, %s, true)
            """,
            (user_id, user_id, request.email, first_name, last_name),
            commit=True
        )

        # 4. Link user to organization
        if organization_id:
            business_db.execute(
                """
                INSERT INTO public.organization_users (organization_id, user_id, role, is_active)
                VALUES (%s, %s, %s, true)
                """,
                (organization_id, user_id, "admin"),
                commit=True
            )

        # 5. Generate JWT token
        access_token = create_access_token({
            "sub": user_id,
            "email": request.email,
            "organization_id": organization_id,
            "role": "admin" if organization_id else "user"
        })

        # 6. Create session
        session_id = await session_store.create_session(
            user_id=user_id,
            session_data={
                "email": request.email,
                "role": "admin" if organization_id else "user",
                "organization_id": organization_id
            }
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=session_id,
            expires_in=JWT_EXPIRE_MINUTES * 60,
            user={
                "id": user_id,
                "email": request.email,
                "full_name": request.full_name
            },
            organization=organization
        )

    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login user

    Authenticates with Supabase and returns JWT + session
    """
    try:
        # 1. Authenticate with Supabase
        auth_response = supabase_manager.sign_in(request.email, request.password)

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        user_id = auth_response.user.id

        # 2. Get user profile
        result = business_db.execute(
            "SELECT id, email, full_name, is_active FROM public.user_profiles WHERE id = %s",
            (user_id,),
            commit=False
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        user_data = result[0]

        if not user_data[3]:  # is_active
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # 3. Get organization
        org_result = business_db.execute(
            """
            SELECT o.id, o.name, o.slug, ou.role
            FROM public.organizations o
            JOIN public.organization_users ou ON o.id = ou.organization_id
            WHERE ou.user_id = %s AND ou.is_active = true
            LIMIT 1
            """,
            (user_id,),
            commit=False
        )

        organization = None
        organization_id = None
        role = "user"

        if org_result:
            org = org_result[0]
            organization_id = str(org[0])
            organization = {
                "id": organization_id,
                "name": org[1],
                "slug": org[2]
            }
            role = org[3]

        # 4. Generate JWT
        access_token = create_access_token({
            "sub": user_id,
            "email": user_data[1],
            "organization_id": organization_id,
            "role": role
        })

        # 5. Create session
        session_id = await session_store.create_session(
            user_id=user_id,
            session_data={
                "email": user_data[1],
                "role": role,
                "organization_id": organization_id
            }
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=session_id,
            expires_in=JWT_EXPIRE_MINUTES * 60,
            user={
                "id": user_id,
                "email": user_data[1],
                "full_name": user_data[2]
            },
            organization=organization
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/logout")
async def logout(
    session_id: str,
    user: Dict = Depends(get_current_user)
):
    """Logout user (invalidate session)"""
    await session_store.delete_session(session_id)
    return {"message": "Logged out successfully"}


@app.get("/me", response_model=UserInfo)
async def get_current_user_info(user: Dict = Depends(get_current_user)):
    """Get current user info"""
    return UserInfo(**user)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_health = business_db.health_check()
    redis_health = await redis_manager.health_check()
    supabase_health = await supabase_manager.health_check()

    return {
        "status": "healthy",
        "services": {
            "database": db_health,
            "redis": redis_health,
            "supabase": supabase_health
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
