"""
Authentication Service - Production Ready
FastAPI + JWT + Supabase

Standalone service with minimal dependencies.
All database operations via Supabase client.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client
import uvicorn

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# FastAPI app
app = FastAPI(title="BCM Auth Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

# Utilities
def create_access_token(data: dict) -> str:
    """Generate JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)

    # Get user from Supabase
    result = supabase.table("users").select("*").eq("id", payload["sub"]).execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="User not found")

    return result.data[0]

# Routes
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login"""
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = auth_response.user

        # Get user details from database
        user_data = supabase.table("users").select("*").eq("id", user.id).execute()

        user_info = user_data.data[0] if user_data.data else {
            "id": user.id,
            "email": user.email,
            "role": "user"
        }

        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user_info.get("role", "user")
        }

        access_token = create_access_token(token_data)

        return TokenResponse(
            access_token=access_token,
            expires_in=JWT_EXPIRE_MINUTES * 60,
            user=user_info
        )

    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """User signup"""
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name
                }
            }
        })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Signup failed")

        user = auth_response.user

        # Create token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": "user"
        }

        access_token = create_access_token(token_data)

        return TokenResponse(
            access_token=access_token,
            expires_in=JWT_EXPIRE_MINUTES * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": request.full_name,
                "role": "user"
            }
        )

    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@app.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user"""
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))
    logger.info(f"Starting Auth Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
