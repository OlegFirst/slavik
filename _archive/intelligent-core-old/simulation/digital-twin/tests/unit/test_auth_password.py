"""
Unit Tests: Password Hashing
"""

import pytest
from api.auth.password import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing functionality"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "SecurePass123!"
        hashed = hash_password(password)

        # Should be hashed (not same as original)
        assert hashed != password

        # Should be bcrypt hash (starts with $2b$)
        assert hashed.startswith("$2b$")

        # Should be long enough
        assert len(hashed) >= 60

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "SecurePass123!"
        hashed = hash_password(password)

        # Should verify successfully
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "SecurePass123!"
        hashed = hash_password(password)

        # Should fail verification
        assert verify_password("WrongPassword", hashed) is False

    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salt)"""
        password = "SecurePass123!"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different (different salt)
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_hash_password_empty(self):
        """Test hashing empty password"""
        password = ""
        hashed = hash_password(password)

        # Should still hash
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_hash_password_special_characters(self):
        """Test hashing password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        # Should hash and verify
        assert verify_password(password, hashed) is True

    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters"""
        password = "Пароль123!"
        hashed = hash_password(password)

        # Should hash and verify
        assert verify_password(password, hashed) is True

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "SecurePass123!"
        hashed = hash_password(password)

        # Should fail with different case
        assert verify_password("securepass123!", hashed) is False
        assert verify_password("SECUREPASS123!", hashed) is False
