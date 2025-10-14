"""
Test Authentication Dependencies
Tests for JWT token validation and user context extraction
"""

import pytest
from fastapi import HTTPException
from unittest.mock import Mock, patch
from jose import jwt

from auth.dependencies import get_current_user, get_current_user_optional
from auth.models import UserContext
from config import Settings


class TestUserContextModel:
    """Test UserContext Pydantic model"""

    def test_usercontext_valid(self):
        """Test valid UserContext creation"""
        user = UserContext(
            user_id="user-123",
            tenant_id="tenant-456",
            email="test@example.com",
            roles=["bcm_manager"],
            is_superadmin=False
        )

        assert user.user_id == "user-123"
        assert user.tenant_id == "tenant-456"
        assert user.email == "test@example.com"
        assert "bcm_manager" in user.roles
        assert user.is_superadmin is False

    def test_usercontext_defaults(self):
        """Test UserContext with default values"""
        user = UserContext(
            user_id="user-123",
            tenant_id="tenant-456",
            email="test@example.com"
        )

        assert user.roles == []
        assert user.is_superadmin is False

    def test_usercontext_superadmin(self):
        """Test UserContext with superadmin flag"""
        user = UserContext(
            user_id="admin-001",
            tenant_id="tenant-admin",
            email="admin@example.com",
            roles=["superadmin"],
            is_superadmin=True
        )

        assert user.is_superadmin is True


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Test get_current_user dependency"""

    async def test_get_current_user_missing_token(self):
        """Test 401 when no Authorization header"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                authorization=None,
                x_dev_user=None,
                x_dev_tenant=None
            )

        assert exc_info.value.status_code == 401
        assert "Missing authorization header" in exc_info.value.detail

    async def test_get_current_user_invalid_scheme(self):
        """Test 401 when not using Bearer scheme"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                authorization="Basic abc123",
                x_dev_user=None,
                x_dev_tenant=None
            )

        assert exc_info.value.status_code == 401
        assert "Invalid authentication scheme" in exc_info.value.detail

    async def test_get_current_user_invalid_format(self):
        """Test 401 when Authorization header has invalid format"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                authorization="InvalidFormat",
                x_dev_user=None,
                x_dev_tenant=None
            )

        assert exc_info.value.status_code == 401
        assert "Invalid authorization header format" in exc_info.value.detail

    async def test_get_current_user_dev_mode(self, mock_settings):
        """Test dev mode bypass with X-Dev-User header"""
        with patch('auth.dependencies.settings', mock_settings):
            user = await get_current_user(
                authorization=None,
                x_dev_user="dev-user-123",
                x_dev_tenant="dev-tenant-456"
            )

            assert user.user_id == "dev-user-123"
            assert user.tenant_id == "dev-tenant-456"
            assert user.email == "dev-user-123@dev.local"
            assert "bcm_manager" in user.roles

    async def test_get_current_user_dev_mode_missing_headers(self, mock_settings):
        """Test dev mode without dev headers still requires auth"""
        with patch('auth.dependencies.settings', mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=None,
                    x_dev_user=None,
                    x_dev_tenant=None
                )

            assert exc_info.value.status_code == 401

    async def test_get_current_user_valid_token_hs256(self, mock_settings):
        """Test valid JWT token with HS256 (symmetric key)"""
        # Create a valid JWT token
        payload = {
            "sub": "user-789",
            "tenant_id": "tenant-123",
            "email": "user@example.com",
            "roles": ["bcm_manager", "strategy_editor"],
            "is_superadmin": False
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            user = await get_current_user(
                authorization=f"Bearer {token}",
                x_dev_user=None,
                x_dev_tenant=None
            )

            assert user.user_id == "user-789"
            assert user.tenant_id == "tenant-123"
            assert user.email == "user@example.com"
            assert user.roles == ["bcm_manager", "strategy_editor"]
            assert user.is_superadmin is False

    async def test_get_current_user_token_missing_sub(self, mock_settings):
        """Test token without 'sub' or 'user_id' claim"""
        payload = {
            "tenant_id": "tenant-123",
            "email": "user@example.com"
            # Missing 'sub' or 'user_id'
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {token}",
                    x_dev_user=None,
                    x_dev_tenant=None
                )

            assert exc_info.value.status_code == 401
            assert "missing user identifier" in exc_info.value.detail

    async def test_get_current_user_token_missing_tenant(self, mock_settings):
        """Test token without 'tenant_id' claim"""
        payload = {
            "sub": "user-789",
            "email": "user@example.com"
            # Missing 'tenant_id'
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {token}",
                    x_dev_user=None,
                    x_dev_tenant=None
                )

            assert exc_info.value.status_code == 401
            assert "missing tenant identifier" in exc_info.value.detail

    async def test_get_current_user_expired_token(self, mock_settings):
        """Test expired JWT token"""
        import time

        payload = {
            "sub": "user-789",
            "tenant_id": "tenant-123",
            "email": "user@example.com",
            "exp": int(time.time()) - 3600  # Expired 1 hour ago
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {token}",
                    x_dev_user=None,
                    x_dev_tenant=None
                )

            assert exc_info.value.status_code == 401
            assert "Invalid or expired token" in exc_info.value.detail

    async def test_get_current_user_invalid_signature(self, mock_settings):
        """Test token with invalid signature"""
        # Create token with different secret
        payload = {
            "sub": "user-789",
            "tenant_id": "tenant-123",
            "email": "user@example.com"
        }

        token = jwt.encode(
            payload,
            "wrong-secret-key",
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {token}",
                    x_dev_user=None,
                    x_dev_tenant=None
                )

            assert exc_info.value.status_code == 401

    async def test_get_current_user_malformed_token(self, mock_settings):
        """Test malformed JWT token"""
        with patch('auth.dependencies.settings', mock_settings):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization="Bearer not.a.valid.jwt",
                    x_dev_user=None,
                    x_dev_tenant=None
                )

            assert exc_info.value.status_code == 401

    async def test_get_current_user_with_user_id_claim(self, mock_settings):
        """Test token with 'user_id' instead of 'sub' claim"""
        payload = {
            "user_id": "user-999",  # Alternative to 'sub'
            "tenant_id": "tenant-123",
            "email": "user@example.com",
            "roles": ["viewer"]
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            user = await get_current_user(
                authorization=f"Bearer {token}",
                x_dev_user=None,
                x_dev_tenant=None
            )

            assert user.user_id == "user-999"
            assert user.tenant_id == "tenant-123"

    async def test_get_current_user_missing_email(self, mock_settings):
        """Test token without email uses default"""
        payload = {
            "sub": "user-888",
            "tenant_id": "tenant-123",
            "roles": ["bcm_manager"]
            # Missing email
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            user = await get_current_user(
                authorization=f"Bearer {token}",
                x_dev_user=None,
                x_dev_tenant=None
            )

            assert user.user_id == "user-888"
            assert user.email == "user-888@unknown.local"

    async def test_get_current_user_non_list_roles(self, mock_settings):
        """Test token with non-list roles field"""
        payload = {
            "sub": "user-777",
            "tenant_id": "tenant-123",
            "email": "user@example.com",
            "roles": "admin"  # String instead of list
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            user = await get_current_user(
                authorization=f"Bearer {token}",
                x_dev_user=None,
                x_dev_tenant=None
            )

            # Should convert to empty list
            assert user.roles == []


@pytest.mark.asyncio
class TestGetCurrentUserOptional:
    """Test get_current_user_optional dependency"""

    async def test_optional_returns_none_on_failure(self):
        """Test optional auth returns None instead of raising exception"""
        user = await get_current_user_optional(
            authorization=None,
            x_dev_user=None,
            x_dev_tenant=None
        )

        assert user is None

    async def test_optional_returns_user_on_success(self, mock_settings):
        """Test optional auth returns user with valid token"""
        payload = {
            "sub": "user-123",
            "tenant_id": "tenant-456",
            "email": "user@example.com"
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            user = await get_current_user_optional(
                authorization=f"Bearer {token}",
                x_dev_user=None,
                x_dev_tenant=None
            )

            assert user is not None
            assert user.user_id == "user-123"
            assert user.tenant_id == "tenant-456"

    async def test_optional_returns_none_on_invalid_token(self, mock_settings):
        """Test optional auth returns None with invalid token"""
        with patch('auth.dependencies.settings', mock_settings):
            user = await get_current_user_optional(
                authorization="Bearer invalid.token",
                x_dev_user=None,
                x_dev_tenant=None
            )

            assert user is None

    async def test_optional_works_with_dev_mode(self, mock_settings):
        """Test optional auth works with dev mode"""
        with patch('auth.dependencies.settings', mock_settings):
            user = await get_current_user_optional(
                authorization=None,
                x_dev_user="dev-user",
                x_dev_tenant="dev-tenant"
            )

            assert user is not None
            assert user.user_id == "dev-user"
            assert user.tenant_id == "dev-tenant"


class TestAuthenticationEdgeCases:
    """Test edge cases in authentication"""

    @pytest.mark.asyncio
    async def test_bearer_case_insensitive(self, mock_settings):
        """Test Bearer keyword is case-insensitive"""
        payload = {
            "sub": "user-123",
            "tenant_id": "tenant-456",
            "email": "user@example.com"
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            # Test with lowercase 'bearer'
            user = await get_current_user(
                authorization=f"bearer {token}",
                x_dev_user=None,
                x_dev_tenant=None
            )

            assert user.user_id == "user-123"

    @pytest.mark.asyncio
    async def test_whitespace_handling(self, mock_settings):
        """Test handling of extra whitespace in Authorization header"""
        payload = {
            "sub": "user-123",
            "tenant_id": "tenant-456",
            "email": "user@example.com"
        }

        token = jwt.encode(
            payload,
            mock_settings.JWT_SECRET,
            algorithm="HS256"
        )

        with patch('auth.dependencies.settings', mock_settings):
            # Extra spaces should work
            user = await get_current_user(
                authorization=f"Bearer  {token}",  # Extra space
                x_dev_user=None,
                x_dev_tenant=None
            )

            assert user.user_id == "user-123"

    @pytest.mark.asyncio
    async def test_superadmin_flag_handling(self, mock_settings):
        """Test various superadmin flag values"""
        test_cases = [
            (True, True),
            (False, False),
            ("true", True),
            ("false", False),
            (1, True),
            (0, False),
            (None, False),
        ]

        for value, expected in test_cases:
            payload = {
                "sub": "user-123",
                "tenant_id": "tenant-456",
                "email": "user@example.com",
                "is_superadmin": value
            }

            token = jwt.encode(
                payload,
                mock_settings.JWT_SECRET,
                algorithm="HS256"
            )

            with patch('auth.dependencies.settings', mock_settings):
                user = await get_current_user(
                    authorization=f"Bearer {token}",
                    x_dev_user=None,
                    x_dev_tenant=None
                )

                assert user.is_superadmin == expected
