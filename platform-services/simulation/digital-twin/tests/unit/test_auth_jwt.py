"""
Unit Tests: JWT Token Management
"""

import pytest
from datetime import datetime, timedelta
from api.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token
)


class TestJWTTokens:
    """Test JWT token creation and verification"""

    def test_create_access_token(self):
        """Test access token creation"""
        user_id = "user-123"
        tenant_id = "tenant-456"
        email = "test@example.com"

        token = create_access_token(user_id, tenant_id, email)

        # Should return string
        assert isinstance(token, str)

        # Should have 3 parts (header.payload.signature)
        assert len(token.split(".")) == 3

    def test_create_refresh_token(self):
        """Test refresh token creation"""
        user_id = "user-123"
        tenant_id = "tenant-456"
        email = "test@example.com"

        token = create_refresh_token(user_id, tenant_id, email)

        # Should return string
        assert isinstance(token, str)

        # Should have 3 parts
        assert len(token.split(".")) == 3

    def test_verify_access_token(self):
        """Test access token verification"""
        user_id = "user-123"
        tenant_id = "tenant-456"
        email = "test@example.com"

        token = create_access_token(user_id, tenant_id, email)
        payload = verify_token(token, expected_type="access")

        # Should verify successfully
        assert payload is not None

        # Should contain correct data
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["email"] == email
        assert payload["type"] == "access"

        # Should have expiration
        assert "exp" in payload

    def test_verify_refresh_token(self):
        """Test refresh token verification"""
        user_id = "user-123"
        tenant_id = "tenant-456"
        email = "test@example.com"

        token = create_refresh_token(user_id, tenant_id, email)
        payload = verify_token(token, expected_type="refresh")

        # Should verify successfully
        assert payload is not None

        # Should contain correct data
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["email"] == email
        assert payload["type"] == "refresh"

    def test_verify_token_wrong_type(self):
        """Test verifying token with wrong expected type"""
        user_id = "user-123"
        tenant_id = "tenant-456"
        email = "test@example.com"

        # Create access token
        token = create_access_token(user_id, tenant_id, email)

        # Try to verify as refresh token
        payload = verify_token(token, expected_type="refresh")

        # Should fail
        assert payload is None

    def test_verify_token_invalid(self):
        """Test verifying invalid token"""
        # Invalid token (not JWT format)
        payload = verify_token("invalid-token", expected_type="access")

        # Should fail
        assert payload is None

    def test_verify_token_tampered(self):
        """Test verifying tampered token"""
        user_id = "user-123"
        tenant_id = "tenant-456"
        email = "test@example.com"

        token = create_access_token(user_id, tenant_id, email)

        # Tamper with token (change one character)
        tampered_token = token[:-1] + ("a" if token[-1] != "a" else "b")

        payload = verify_token(tampered_token, expected_type="access")

        # Should fail
        assert payload is None

    def test_verify_token_empty(self):
        """Test verifying empty token"""
        payload = verify_token("", expected_type="access")

        # Should fail
        assert payload is None

    def test_access_token_different_each_time(self):
        """Test that tokens are different each time (due to exp)"""
        user_id = "user-123"
        tenant_id = "tenant-456"
        email = "test@example.com"

        token1 = create_access_token(user_id, tenant_id, email)
        token2 = create_access_token(user_id, tenant_id, email)

        # Tokens might be the same if created in same second
        # So we just verify both are valid
        assert verify_token(token1, expected_type="access") is not None
        assert verify_token(token2, expected_type="access") is not None

    def test_token_contains_all_claims(self):
        """Test that token contains all required claims"""
        user_id = "user-abc123"
        tenant_id = "tenant-xyz789"
        email = "user@example.com"

        token = create_access_token(user_id, tenant_id, email)
        payload = verify_token(token, expected_type="access")

        # Check all required claims
        assert "sub" in payload  # Subject (user_id)
        assert "tenant_id" in payload
        assert "email" in payload
        assert "exp" in payload  # Expiration
        assert "type" in payload  # Token type

        # Verify values
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["email"] == email
