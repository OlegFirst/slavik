"""
Authentication Router
"""

from fastapi import APIRouter, HTTPException, status, Depends
from supabase import create_client, Client
from models import UserRegister, UserLogin, Token, UserProfile
from auth import hash_password, verify_password, create_access_token, get_current_user_id
from database import DatabaseClient
from config import get_settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])
settings = get_settings()


def get_supabase() -> Client:
    """Get Supabase client"""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def get_db() -> DatabaseClient:
    """Get database client"""
    return DatabaseClient()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegister,
    supabase: Client = Depends(get_supabase),
    db: DatabaseClient = Depends(get_db)
):
    """
    Register new user

    Creates:
    - User in Supabase Auth
    - User profile in database
    - Organization (if organization_name provided)
    - Returns JWT access token
    """
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email": request.email,
            "password": request.password,
            "email_confirm": True,  # Auto-confirm for MVP
            "user_metadata": {
                "full_name": request.full_name
            }
        })

        user_id = auth_response.user.id

        # Create user profile
        await db.create_user_profile(
            user_id=user_id,
            data={
                "full_name": request.full_name,
                "role": "specialist"
            }
        )

        # Create organization if provided
        if request.organization_name:
            await db.create_organization({
                "owner_id": user_id,
                "name": request.organization_name,
                "bcm_maturity_score": 0
            })

        # Generate access token
        access_token = create_access_token(
            user_id=user_id,
            email=request.email
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

    except Exception as e:
        # Check if user already exists
        if "already been registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    request: UserLogin,
    supabase: Client = Depends(get_supabase)
):
    """
    Login user with email and password

    Returns JWT access token
    """
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate access token
        access_token = create_access_token(
            user_id=auth_response.user.id,
            email=auth_response.user.email
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserProfile)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Get current authenticated user profile

    Requires valid JWT token
    """
    profile = await db.get_user_profile(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return UserProfile(
        id=profile["id"],
        email=profile.get("email", ""),
        full_name=profile.get("full_name"),
        role=profile.get("role", "specialist"),
        created_at=profile["created_at"]
    )


@router.post("/logout")
async def logout(user_id: str = Depends(get_current_user_id)):
    """
    Logout user

    Note: With JWT, logout is primarily client-side (delete token).
    This endpoint is for consistency and can be used for logging.
    """
    return {
        "status": "success",
        "message": "Successfully logged out"
    }
