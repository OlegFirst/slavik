"""
Authentication Tests
Tests for JWT authentication and user context extraction
"""

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, patch

from plans_service.auth.dependencies import get_current_user, get_optional_user
from plans_service.auth.models import UserContext
from plans_service.config import settings


class TestUserContextModel:
    """Test UserContext Pydantic model"""

    def test_usercontext_model_valid(self):
        """Test UserContext with valid data"""
        context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            email="user@example.com",
            roles=["bcm_manager"],
            is_superadmin=False
        )

        assert context.user_id == "user_123"
        assert context.tenant_id == "tenant_456"
        assert context.email == "user@example.com"
        assert "bcm_manager" in context.roles
        assert context.is_superadmin is False

    def test_usercontext_defaults(self):
        """Test UserContext default values"""
        context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            email="user@example.com"
        )

        assert context.roles == []
        assert context.is_superadmin is False

    def test_usercontext_with_multiple_roles(self):
        """Test UserContext with multiple roles"""
        context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            email="user@example.com",
            roles=["bcm_manager", "plan_approver", "admin"]
        )

        assert len(context.roles) == 3
        assert "bcm_manager" in context.roles
        assert "plan_approver" in context.roles
        assert "admin" in context.roles

    def test_usercontext_superadmin(self):
        """Test UserContext for superadmin"""
        context = UserContext(
            user_id="admin_001",
            tenant_id="global",
            email="admin@example.com",
            is_superadmin=True
        )

        assert context.is_superadmin is True


class TestGetCurrentUser:
    """Test get_current_user dependency"""

    @pytest.mark.asyncio
    async def test_get_current_user_missing_token(self):
        """Test 401 when no Authorization header"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None, x_dev_user=None)

        assert exc_info.value.status_code == 401
        assert "Missing authentication token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_dev_mode(self):
        """Test dev mode bypass with X-Dev-User header"""
        with patch.object(settings, 'JWT_PUBLIC_KEY', ''):
            # Dev mode enabled (no JWT_PUBLIC_KEY)
            user_context = await get_current_user(
                credentials=None,
                x_dev_user="test_user:test_tenant:test@example.com"
            )

            assert user_context.user_id == "test_user"
            assert user_context.tenant_id == "test_tenant"
            assert user_context.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_dev_mode_simple(self):
        """Test dev mode with simple user ID only"""
        with patch.object(settings, 'JWT_PUBLIC_KEY', ''):
            user_context = await get_current_user(
                credentials=None,
                x_dev_user="simple_user"
            )

            assert user_context.user_id == "simple_user"
            assert user_context.tenant_id == "dev_tenant"
            assert "simple_user@dev.local" in user_context.email

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test valid JWT token"""
        # Create a valid token
        secret_key = "test-secret-key"
        payload = {
            "sub": "user_123",
            "tenant_id": "tenant_456",
            "email": "user@example.com",
            "roles": ["bcm_manager"],
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with patch.object(settings, 'JWT_AUDIENCE', None):
                    user_context = await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                    assert user_context.user_id == "user_123"
                    assert user_context.tenant_id == "tenant_456"
                    assert user_context.email == "user@example.com"
                    assert "bcm_manager" in user_context.roles

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self):
        """Test expired JWT token"""
        secret_key = "test-secret-key"
        payload = {
            "sub": "user_123",
            "tenant_id": "tenant_456",
            "email": "user@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                assert exc_info.value.status_code == 401
                assert "expired" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test invalid JWT token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', 'test-key'):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_missing_user_id(self):
        """Test token without user_id"""
        secret_key = "test-secret-key"
        payload = {
            # Missing "sub" or "user_id"
            "tenant_id": "tenant_456",
            "email": "user@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                assert exc_info.value.status_code == 401
                assert "user_id" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_missing_tenant_id(self):
        """Test token without tenant_id"""
        secret_key = "test-secret-key"
        payload = {
            "sub": "user_123",
            # Missing "tenant_id" or "org_id"
            "email": "user@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                assert exc_info.value.status_code == 401
                assert "tenant_id" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_tenant_isolation_check(self):
        """Test tenant_id extracted from token"""
        secret_key = "test-secret-key"
        payload = {
            "sub": "user_123",
            "tenant_id": "tenant_abc",
            "email": "user@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with patch.object(settings, 'JWT_AUDIENCE', None):
                    user_context = await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                    assert user_context.tenant_id == "tenant_abc"

    @pytest.mark.asyncio
    async def test_get_current_user_with_org_id(self):
        """Test token with org_id instead of tenant_id"""
        secret_key = "test-secret-key"
        payload = {
            "sub": "user_123",
            "org_id": "org_456",  # Using org_id instead
            "email": "user@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with patch.object(settings, 'JWT_AUDIENCE', None):
                    user_context = await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                    assert user_context.tenant_id == "org_456"

    @pytest.mark.asyncio
    async def test_get_current_user_with_user_id_claim(self):
        """Test token with user_id instead of sub"""
        secret_key = "test-secret-key"
        payload = {
            "user_id": "user_789",  # Using user_id instead of sub
            "tenant_id": "tenant_456",
            "email": "user@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with patch.object(settings, 'JWT_AUDIENCE', None):
                    user_context = await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                    assert user_context.user_id == "user_789"

    @pytest.mark.asyncio
    async def test_get_current_user_roles_handling(self):
        """Test roles are correctly extracted"""
        secret_key = "test-secret-key"
        payload = {
            "sub": "user_123",
            "tenant_id": "tenant_456",
            "email": "user@example.com",
            "roles": ["admin", "bcm_manager", "plan_approver"],
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with patch.object(settings, 'JWT_AUDIENCE', None):
                    user_context = await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                    assert len(user_context.roles) == 3
                    assert "admin" in user_context.roles
                    assert "bcm_manager" in user_context.roles

    @pytest.mark.asyncio
    async def test_get_current_user_superadmin(self):
        """Test superadmin flag extraction"""
        secret_key = "test-secret-key"
        payload = {
            "sub": "admin_001",
            "tenant_id": "global",
            "email": "admin@example.com",
            "is_superadmin": True,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with patch.object(settings, 'JWT_AUDIENCE', None):
                    user_context = await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                    assert user_context.is_superadmin is True

    @pytest.mark.asyncio
    async def test_get_current_user_default_email(self):
        """Test default email when not provided"""
        secret_key = "test-secret-key"
        payload = {
            "sub": "user_123",
            "tenant_id": "tenant_456",
            # No email provided
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with patch.object(settings, 'JWT_AUDIENCE', None):
                    user_context = await get_current_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                    assert "@unknown" in user_context.email


class TestGetOptionalUser:
    """Test get_optional_user dependency"""

    @pytest.mark.asyncio
    async def test_get_optional_user_no_credentials(self):
        """Test returns None when no credentials provided"""
        user_context = await get_optional_user(
            credentials=None,
            x_dev_user=None
        )

        assert user_context is None

    @pytest.mark.asyncio
    async def test_get_optional_user_valid_token(self):
        """Test returns user context for valid token"""
        secret_key = "test-secret-key"
        payload = {
            "sub": "user_123",
            "tenant_id": "tenant_456",
            "email": "user@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', secret_key):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                with patch.object(settings, 'JWT_AUDIENCE', None):
                    user_context = await get_optional_user(
                        credentials=credentials,
                        x_dev_user=None
                    )

                    assert user_context is not None
                    assert user_context.user_id == "user_123"

    @pytest.mark.asyncio
    async def test_get_optional_user_invalid_token(self):
        """Test returns None for invalid token instead of raising"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )

        with patch.object(settings, 'JWT_PUBLIC_KEY', 'test-key'):
            with patch.object(settings, 'JWT_ALGORITHM', 'HS256'):
                user_context = await get_optional_user(
                    credentials=credentials,
                    x_dev_user=None
                )

                assert user_context is None

    @pytest.mark.asyncio
    async def test_get_optional_user_dev_mode(self):
        """Test dev mode works with optional user"""
        with patch.object(settings, 'JWT_PUBLIC_KEY', ''):
            user_context = await get_optional_user(
                credentials=None,
                x_dev_user="test_user"
            )

            assert user_context is not None
            assert user_context.user_id == "test_user"
