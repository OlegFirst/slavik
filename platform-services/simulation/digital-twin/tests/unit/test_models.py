"""
Unit Tests: Pydantic Models Validation
"""

import pytest
from pydantic import ValidationError
from api.routers.auth import RegisterRequest, LoginRequest


class TestAuthModels:
    """Test authentication Pydantic models"""

    def test_register_request_valid(self):
        """Test valid RegisterRequest"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "tenant_name": "Test Tenant"
        }

        request = RegisterRequest(**data)

        assert request.email == "test@example.com"
        assert request.password == "SecurePass123!"
        assert request.full_name == "Test User"
        assert request.tenant_name == "Test Tenant"

    def test_register_request_invalid_email(self):
        """Test RegisterRequest with invalid email"""
        data = {
            "email": "not-an-email",  # Invalid email
            "password": "SecurePass123!",
            "full_name": "Test User"
        }

        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        # Should contain email validation error
        errors = exc_info.value.errors()
        assert any("email" in str(error) for error in errors)

    def test_register_request_missing_email(self):
        """Test RegisterRequest without email"""
        data = {
            "password": "SecurePass123!",
            "full_name": "Test User"
        }

        with pytest.raises(ValidationError):
            RegisterRequest(**data)

    def test_register_request_missing_password(self):
        """Test RegisterRequest without password"""
        data = {
            "email": "test@example.com",
            "full_name": "Test User"
        }

        with pytest.raises(ValidationError):
            RegisterRequest(**data)

    def test_register_request_optional_tenant_name(self):
        """Test RegisterRequest with optional tenant_name"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
            # tenant_name is optional
        }

        request = RegisterRequest(**data)

        assert request.email == "test@example.com"
        assert request.tenant_name is None  # Should be None if not provided

    def test_login_request_valid(self):
        """Test valid LoginRequest"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }

        request = LoginRequest(**data)

        assert request.email == "test@example.com"
        assert request.password == "SecurePass123!"

    def test_login_request_invalid_email(self):
        """Test LoginRequest with invalid email"""
        data = {
            "email": "not-an-email",
            "password": "SecurePass123!"
        }

        with pytest.raises(ValidationError):
            LoginRequest(**data)

    def test_login_request_missing_fields(self):
        """Test LoginRequest with missing fields"""
        # Missing password
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com")

        # Missing email
        with pytest.raises(ValidationError):
            LoginRequest(password="SecurePass123!")
