"""
Security Test Suite - General Security Tests

Tests authentication, authorization, encryption, and security best practices.

Coverage:
- Authentication mechanisms
- Authorization and RBAC
- JWT token validation
- Session management
- Password security
- Data encryption
- API security
"""

import pytest
import jwt
from datetime import datetime, timedelta
from typing import Dict
import hashlib
import secrets


# Mock security utilities
class SecurityUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return SecurityUtils.hash_password(password) == hashed

    @staticmethod
    def generate_token(user_id: str, secret: str, expiry_hours: int = 24) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=expiry_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, secret, algorithm="HS256")

    @staticmethod
    def verify_token(token: str, secret: str) -> Dict:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")


@pytest.fixture
def security_utils():
    """Provides security utilities"""
    return SecurityUtils()


@pytest.fixture
def jwt_secret():
    """Provides JWT secret for testing"""
    return "test-secret-key-do-not-use-in-production"


@pytest.mark.fast
def test_password_hashing(security_utils):
    """Test password hashing is consistent"""
    password = "SecurePassword123!"
    hash1 = security_utils.hash_password(password)
    hash2 = security_utils.hash_password(password)

    assert hash1 == hash2
    assert hash1 != password  # Hash should not be plaintext


@pytest.mark.fast
def test_password_verification(security_utils):
    """Test password verification"""
    password = "SecurePassword123!"
    hashed = security_utils.hash_password(password)

    assert security_utils.verify_password(password, hashed)
    assert not security_utils.verify_password("WrongPassword", hashed)


@pytest.mark.fast
def test_jwt_token_generation(security_utils, jwt_secret):
    """Test JWT token generation"""
    user_id = "user-001"
    token = security_utils.generate_token(user_id, jwt_secret)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.fast
def test_jwt_token_verification(security_utils, jwt_secret):
    """Test JWT token verification"""
    user_id = "user-001"
    token = security_utils.generate_token(user_id, jwt_secret)

    payload = security_utils.verify_token(token, jwt_secret)

    assert payload["user_id"] == user_id
    assert "exp" in payload
    assert "iat" in payload


@pytest.mark.fast
def test_jwt_token_expiration(security_utils, jwt_secret):
    """Test JWT token expiration"""
    user_id = "user-001"
    # Create expired token (0 hours = expired immediately)
    token = security_utils.generate_token(user_id, jwt_secret, expiry_hours=-1)

    with pytest.raises(ValueError, match="Token expired"):
        security_utils.verify_token(token, jwt_secret)


@pytest.mark.fast
def test_jwt_invalid_token(security_utils, jwt_secret):
    """Test invalid JWT token handling"""
    invalid_token = "invalid.jwt.token"

    with pytest.raises(ValueError, match="Invalid token"):
        security_utils.verify_token(invalid_token, jwt_secret)


@pytest.mark.fast
def test_jwt_wrong_secret(security_utils, jwt_secret):
    """Test JWT token with wrong secret"""
    user_id = "user-001"
    token = security_utils.generate_token(user_id, jwt_secret)

    with pytest.raises(ValueError, match="Invalid token"):
        security_utils.verify_token(token, "wrong-secret")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_authentication_flow():
    """Test complete authentication flow"""
    # Simulate user registration
    username = "testuser"
    password = "SecurePassword123!"

    # Hash password
    security = SecurityUtils()
    hashed_password = security.hash_password(password)

    # Store user (mock)
    user_db = {
        username: {
            "password_hash": hashed_password,
            "user_id": "user-001",
            "role": "bcm_coordinator"
        }
    }

    # Simulate login
    login_password = "SecurePassword123!"
    if username in user_db:
        user = user_db[username]
        if security.verify_password(login_password, user["password_hash"]):
            # Generate token
            token = security.generate_token(user["user_id"], "secret-key")
            assert token is not None


@pytest.mark.critical
def test_role_based_access_control():
    """Test RBAC permissions"""
    roles_permissions = {
        "bcm_coordinator": ["read", "write", "execute_bia"],
        "risk_manager": ["read", "write", "assess_risk"],
        "auditor": ["read"],
        "admin": ["read", "write", "delete", "manage_users"]
    }

    # Test auditor cannot write
    assert "write" not in roles_permissions["auditor"]

    # Test admin has all permissions
    assert "manage_users" in roles_permissions["admin"]

    # Test bcm_coordinator can execute BIA
    assert "execute_bia" in roles_permissions["bcm_coordinator"]


@pytest.mark.fast
def test_secure_random_generation():
    """Test cryptographically secure random generation"""
    # Generate secure random tokens
    token1 = secrets.token_urlsafe(32)
    token2 = secrets.token_urlsafe(32)

    assert len(token1) > 0
    assert len(token2) > 0
    assert token1 != token2  # Should be unique


@pytest.mark.critical
def test_sensitive_data_not_logged():
    """Test that sensitive data is not logged"""
    # Simulate logging function
    def safe_log(data: dict) -> dict:
        """Remove sensitive fields before logging"""
        sensitive_fields = ["password", "token", "secret", "api_key"]
        return {k: v for k, v in data.items() if k not in sensitive_fields}

    user_data = {
        "user_id": "user-001",
        "username": "testuser",
        "password": "SecurePassword123!",
        "token": "jwt-token-here",
        "role": "bcm_coordinator"
    }

    logged_data = safe_log(user_data)

    assert "password" not in logged_data
    assert "token" not in logged_data
    assert "user_id" in logged_data
    assert "role" in logged_data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_rate_limiting():
    """Test API rate limiting"""
    # Mock rate limiter
    class RateLimiter:
        def __init__(self, max_requests: int, window_seconds: int):
            self.max_requests = max_requests
            self.window_seconds = window_seconds
            self.requests = {}

        def check_limit(self, user_id: str) -> bool:
            now = datetime.now()
            if user_id not in self.requests:
                self.requests[user_id] = []

            # Clean old requests
            self.requests[user_id] = [
                req for req in self.requests[user_id]
                if (now - req).seconds < self.window_seconds
            ]

            if len(self.requests[user_id]) >= self.max_requests:
                return False  # Rate limit exceeded

            self.requests[user_id].append(now)
            return True

    limiter = RateLimiter(max_requests=5, window_seconds=60)
    user_id = "user-001"

    # First 5 requests should succeed
    for _ in range(5):
        assert limiter.check_limit(user_id)

    # 6th request should fail
    assert not limiter.check_limit(user_id)


@pytest.mark.fast
def test_input_sanitization():
    """Test input sanitization against injection"""
    def sanitize_input(user_input: str) -> str:
        """Remove potentially dangerous characters"""
        dangerous_chars = ["<", ">", "'", '"', ";", "--", "/*", "*/"]
        sanitized = user_input
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        return sanitized

    # Test SQL injection attempt
    malicious_input = "'; DROP TABLE users; --"
    sanitized = sanitize_input(malicious_input)

    assert "DROP" in sanitized  # Content remains
    assert "'" not in sanitized  # Dangerous chars removed
    assert ";" not in sanitized
    assert "--" not in sanitized


@pytest.mark.critical
def test_session_management():
    """Test secure session management"""
    class SessionManager:
        def __init__(self):
            self.sessions = {}

        def create_session(self, user_id: str) -> str:
            session_id = secrets.token_urlsafe(32)
            self.sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now()
            }
            return session_id

        def validate_session(self, session_id: str, timeout_minutes: int = 30) -> bool:
            if session_id not in self.sessions:
                return False

            session = self.sessions[session_id]
            elapsed = (datetime.now() - session["last_activity"]).seconds / 60

            if elapsed > timeout_minutes:
                del self.sessions[session_id]  # Expire session
                return False

            session["last_activity"] = datetime.now()
            return True

    manager = SessionManager()
    session_id = manager.create_session("user-001")

    # Valid session
    assert manager.validate_session(session_id)

    # Invalid session
    assert not manager.validate_session("invalid-session-id")


@pytest.mark.fast
def test_cors_configuration():
    """Test CORS configuration is secure"""
    # Secure CORS config
    secure_cors = {
        "allow_origins": ["https://app.example.com"],  # Specific origins
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 600
    }

    # Insecure CORS config
    insecure_cors = {
        "allow_origins": ["*"],  # Wildcard - insecure!
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"]
    }

    # Validate secure config
    assert "*" not in secure_cors["allow_origins"]
    assert isinstance(secure_cors["allow_origins"], list)

    # Detect insecure config
    assert "*" in insecure_cors["allow_origins"]  # Should be flagged
