"""
Test JWT Authentication
Tests JWT token handling, verification, and user extraction
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt, JWTError
import sys
from pathlib import Path

# Add shared models to path
shared_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Import common models
import importlib.util
spec = importlib.util.spec_from_file_location("common", shared_path / "models" / "common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
User = common.User

from auth.jwt_handler import (
    verify_jwt_token,
    decode_token,
    create_user_from_token
)
from auth.dependencies import get_current_user, get_optional_user


# =============================================================================
# JWT Token Verification Tests
# =============================================================================

class TestJWTVerification:
    """Test JWT token verification"""

    def test_verify_valid_token(self, valid_jwt_payload, jwt_secret_key):
        """Test verifying a valid JWT token"""
        # Create a valid token
        token = jwt.encode(valid_jwt_payload, jwt_secret_key, algorithm="HS256")

        # Verify token
        payload = verify_jwt_token(token, jwt_secret_key)

        assert payload is not None
        assert payload["sub"] == valid_jwt_payload["sub"]
        assert payload["email"] == valid_jwt_payload["email"]

    def test_verify_invalid_token(self, jwt_secret_key):
        """Test verifying an invalid JWT token raises exception"""
        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(invalid_token, jwt_secret_key)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail

    def test_verify_token_wrong_secret(self, valid_jwt_payload, jwt_secret_key):
        """Test verifying token with wrong secret raises exception"""
        # Create token with one secret
        token = jwt.encode(valid_jwt_payload, jwt_secret_key, algorithm="HS256")

        # Verify with different secret
        wrong_secret = "wrong-secret-key"

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(token, wrong_secret)

        assert exc_info.value.status_code == 401

    def test_verify_expired_token(self, expired_jwt_payload, jwt_secret_key):
        """Test verifying expired token raises exception"""
        # Create expired token
        token = jwt.encode(expired_jwt_payload, jwt_secret_key, algorithm="HS256")

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(token, jwt_secret_key)

        assert exc_info.value.status_code == 401

    def test_verify_token_different_algorithm(self, valid_jwt_payload, jwt_secret_key):
        """Test verifying token with different algorithm"""
        # Create token with HS256
        token = jwt.encode(valid_jwt_payload, jwt_secret_key, algorithm="HS256")

        # Verify with HS256 (should work)
        payload = verify_jwt_token(token, jwt_secret_key, algorithm="HS256")
        assert payload is not None


# =============================================================================
# JWT Token Decoding Tests
# =============================================================================

class TestJWTDecoding:
    """Test JWT token decoding (without verification errors)"""

    def test_decode_valid_token(self, valid_jwt_payload, jwt_secret_key):
        """Test decoding a valid token"""
        token = jwt.encode(valid_jwt_payload, jwt_secret_key, algorithm="HS256")

        payload = decode_token(token, jwt_secret_key)

        assert payload is not None
        assert payload["sub"] == valid_jwt_payload["sub"]

    def test_decode_expired_token(self, expired_jwt_payload, jwt_secret_key):
        """Test decoding expired token returns None"""
        token = jwt.encode(expired_jwt_payload, jwt_secret_key, algorithm="HS256")

        payload = decode_token(token, jwt_secret_key)

        assert payload is None

    def test_decode_invalid_token(self, jwt_secret_key):
        """Test decoding invalid token returns None"""
        invalid_token = "invalid.token.here"

        payload = decode_token(invalid_token, jwt_secret_key)

        assert payload is None

    def test_decode_token_no_expiration(self, jwt_secret_key):
        """Test decoding token without expiration claim"""
        payload_no_exp = {
            "sub": "test-user-123",
            "tenant_id": "test-org-456",
            "email": "test@example.com",
            "role": "bcm_manager"
        }

        token = jwt.encode(payload_no_exp, jwt_secret_key, algorithm="HS256")

        payload = decode_token(token, jwt_secret_key)

        assert payload is not None
        assert payload["sub"] == "test-user-123"


# =============================================================================
# User Creation from Token Tests
# =============================================================================

class TestUserCreation:
    """Test creating User objects from JWT token payload"""

    def test_create_user_from_valid_payload(self, valid_jwt_payload):
        """Test creating user from valid payload"""
        user = create_user_from_token(valid_jwt_payload)

        assert isinstance(user, User)
        assert user.user_id == valid_jwt_payload["sub"]
        assert user.tenant_id == valid_jwt_payload["tenant_id"]
        assert user.email == valid_jwt_payload["email"]
        assert user.role == valid_jwt_payload["role"]
        assert user.full_name == valid_jwt_payload["full_name"]
        assert user.is_active is True

    def test_create_user_with_organization_id(self):
        """Test creating user when payload has organization_id instead of tenant_id"""
        payload = {
            "sub": "test-user-123",
            "organization_id": "test-org-456",  # Note: organization_id instead of tenant_id
            "email": "test@example.com",
            "role": "bcm_manager",
            "full_name": "Test User",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
        }

        user = create_user_from_token(payload)

        assert user.tenant_id == "test-org-456"

    def test_create_user_missing_sub(self):
        """Test creating user without sub claim raises exception"""
        payload = {
            "tenant_id": "test-org-456",
            "email": "test@example.com",
            "role": "bcm_manager"
        }

        with pytest.raises(HTTPException) as exc_info:
            create_user_from_token(payload)

        assert exc_info.value.status_code == 401
        assert "Token missing user ID" in exc_info.value.detail

    def test_create_user_missing_tenant_id(self):
        """Test creating user without tenant_id or organization_id raises exception"""
        payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "bcm_manager"
        }

        with pytest.raises(HTTPException) as exc_info:
            create_user_from_token(payload)

        assert exc_info.value.status_code == 401
        assert "Token missing organization_id or tenant_id" in exc_info.value.detail

    def test_create_user_defaults(self):
        """Test creating user with minimal payload uses defaults"""
        payload = {
            "sub": "test-user-123",
            "tenant_id": "test-org-456",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
        }

        user = create_user_from_token(payload)

        assert user.user_id == "test-user-123"
        assert user.tenant_id == "test-org-456"
        assert "@unknown.com" in user.email  # Default email
        assert user.role == "user"  # Default role
        assert user.full_name is None

    def test_create_user_with_full_name(self):
        """Test creating user with full_name"""
        payload = {
            "sub": "test-user-123",
            "tenant_id": "test-org-456",
            "email": "test@example.com",
            "role": "admin",
            "full_name": "John Doe",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
        }

        user = create_user_from_token(payload)

        assert user.full_name == "John Doe"


# =============================================================================
# Authentication Dependency Tests
# =============================================================================

class TestGetCurrentUser:
    """Test get_current_user dependency"""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, valid_jwt_payload, jwt_secret_key):
        """Test getting current user with valid token"""
        # Create valid token
        token = jwt.encode(valid_jwt_payload, jwt_secret_key, algorithm="HS256")

        # Mock credentials
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Mock settings
        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = True
            mock_settings.JWT_SECRET_KEY = jwt_secret_key
            mock_settings.JWT_ALGORITHM = "HS256"

            user = await get_current_user(credentials)

            assert isinstance(user, User)
            assert user.user_id == valid_jwt_payload["sub"]
            assert user.tenant_id == valid_jwt_payload["tenant_id"]

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test getting current user without credentials raises exception"""
        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = True

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(None)

            assert exc_info.value.status_code == 401
            assert "Missing authentication token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, jwt_secret_key):
        """Test getting current user with invalid token raises exception"""
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")

        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = True
            mock_settings.JWT_SECRET_KEY = jwt_secret_key
            mock_settings.JWT_ALGORITHM = "HS256"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_auth_disabled(self):
        """Test getting current user when auth is disabled returns default user"""
        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = False

            user = await get_current_user(None)

            assert isinstance(user, User)
            assert user.user_id == "system"
            assert user.tenant_id == "default"
            assert user.role == "admin"

    @pytest.mark.asyncio
    async def test_get_current_user_missing_secret_key(self, valid_jwt_payload):
        """Test getting current user when JWT secret is not configured"""
        token = jwt.encode(valid_jwt_payload, "some-secret", algorithm="HS256")

        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = True
            mock_settings.JWT_SECRET_KEY = None  # Not configured

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials)

            assert exc_info.value.status_code == 500
            assert "JWT_SECRET_KEY not configured" in exc_info.value.detail


# =============================================================================
# Optional Authentication Tests
# =============================================================================

class TestGetOptionalUser:
    """Test get_optional_user dependency"""

    @pytest.mark.asyncio
    async def test_get_optional_user_valid_token(self, valid_jwt_payload, jwt_secret_key):
        """Test getting optional user with valid token"""
        token = jwt.encode(valid_jwt_payload, jwt_secret_key, algorithm="HS256")

        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = True
            mock_settings.JWT_SECRET_KEY = jwt_secret_key
            mock_settings.JWT_ALGORITHM = "HS256"

            user = await get_optional_user(credentials)

            assert isinstance(user, User)
            assert user.user_id == valid_jwt_payload["sub"]

    @pytest.mark.asyncio
    async def test_get_optional_user_no_credentials(self):
        """Test getting optional user without credentials returns None"""
        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = True

            user = await get_optional_user(None)

            assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_invalid_token(self, jwt_secret_key):
        """Test getting optional user with invalid token returns None"""
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")

        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = True
            mock_settings.JWT_SECRET_KEY = jwt_secret_key
            mock_settings.JWT_ALGORITHM = "HS256"

            user = await get_optional_user(credentials)

            assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_auth_disabled(self):
        """Test getting optional user when auth is disabled returns None"""
        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = False

            user = await get_optional_user(None)

            assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_expired_token(self, expired_jwt_payload, jwt_secret_key):
        """Test getting optional user with expired token returns None"""
        token = jwt.encode(expired_jwt_payload, jwt_secret_key, algorithm="HS256")

        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with patch('auth.dependencies.settings') as mock_settings:
            mock_settings.JWT_AUTH_ENABLED = True
            mock_settings.JWT_SECRET_KEY = jwt_secret_key
            mock_settings.JWT_ALGORITHM = "HS256"

            user = await get_optional_user(credentials)

            assert user is None


# =============================================================================
# Role-Based Authorization Tests
# =============================================================================

class TestRoleBasedAuth:
    """Test role-based authorization"""

    @pytest.mark.asyncio
    async def test_require_role_authorized(self, test_user):
        """Test role requirement with authorized user"""
        from auth.dependencies import require_role

        # Test user has role "bcm_manager"
        role_checker = require_role("bcm_manager", "admin")

        # Should not raise exception
        result = await role_checker(test_user)
        assert result == test_user

    @pytest.mark.asyncio
    async def test_require_role_unauthorized(self, test_user):
        """Test role requirement with unauthorized user"""
        from auth.dependencies import require_role

        # Test user has role "bcm_manager" but we require "admin"
        role_checker = require_role("admin", "super_admin")

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(test_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_multiple_roles(self, admin_user):
        """Test role requirement with multiple allowed roles"""
        from auth.dependencies import require_role

        # Admin user should be authorized
        role_checker = require_role("admin", "super_admin", "bcm_manager")

        result = await role_checker(admin_user)
        assert result == admin_user


# =============================================================================
# Token Payload Edge Cases
# =============================================================================

class TestTokenEdgeCases:
    """Test edge cases in token handling"""

    def test_token_with_extra_claims(self, jwt_secret_key):
        """Test token with extra custom claims"""
        payload = {
            "sub": "test-user-123",
            "tenant_id": "test-org-456",
            "email": "test@example.com",
            "role": "bcm_manager",
            "full_name": "Test User",
            "custom_claim": "custom_value",  # Extra claim
            "department": "Security",  # Another extra claim
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
        }

        token = jwt.encode(payload, jwt_secret_key, algorithm="HS256")
        decoded = verify_jwt_token(token, jwt_secret_key)

        # Should decode successfully
        assert decoded is not None
        assert decoded["sub"] == "test-user-123"
        assert decoded["custom_claim"] == "custom_value"

        # User creation should still work
        user = create_user_from_token(decoded)
        assert user.user_id == "test-user-123"

    def test_token_with_unicode_characters(self, jwt_secret_key):
        """Test token with unicode characters in payload"""
        payload = {
            "sub": "test-user-123",
            "tenant_id": "test-org-456",
            "email": "test@example.com",
            "role": "bcm_manager",
            "full_name": "José García",  # Unicode characters
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
        }

        token = jwt.encode(payload, jwt_secret_key, algorithm="HS256")
        decoded = verify_jwt_token(token, jwt_secret_key)

        user = create_user_from_token(decoded)
        assert user.full_name == "José García"

    def test_token_with_very_long_expiration(self, jwt_secret_key):
        """Test token with very long expiration"""
        payload = {
            "sub": "test-user-123",
            "tenant_id": "test-org-456",
            "email": "test@example.com",
            "role": "bcm_manager",
            "exp": (datetime.utcnow() + timedelta(days=365)).timestamp()  # 1 year
        }

        token = jwt.encode(payload, jwt_secret_key, algorithm="HS256")
        decoded = verify_jwt_token(token, jwt_secret_key)

        assert decoded is not None
        assert decoded["sub"] == "test-user-123"
