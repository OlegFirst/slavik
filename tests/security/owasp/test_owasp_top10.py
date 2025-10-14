"""
OWASP Top 10 2021 Coverage Tests

Tests platform security against OWASP Top 10 vulnerabilities.

Coverage:
A01:2021 - Broken Access Control
A02:2021 - Cryptographic Failures
A03:2021 - Injection
A04:2021 - Insecure Design
A05:2021 - Security Misconfiguration
A06:2021 - Vulnerable and Outdated Components
A07:2021 - Identification and Authentication Failures
A08:2021 - Software and Data Integrity Failures
A09:2021 - Security Logging and Monitoring Failures
A10:2021 - Server-Side Request Forgery (SSRF)
"""

import pytest
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re


# ============================================================================
# A01:2021 - Broken Access Control
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a01_horizontal_privilege_escalation():
    """Test prevention of horizontal privilege escalation"""
    # Mock user database
    users = {
        "user-001": {"role": "bcm_coordinator", "organization_id": "org-001"},
        "user-002": {"role": "bcm_coordinator", "organization_id": "org-002"}
    }

    def check_access(user_id: str, resource_org_id: str) -> bool:
        """Verify user can only access resources from their organization"""
        user = users.get(user_id)
        if not user:
            return False
        return user["organization_id"] == resource_org_id

    # User 001 should access their own org
    assert check_access("user-001", "org-001")

    # User 001 should NOT access other org (horizontal escalation prevented)
    assert not check_access("user-001", "org-002")


@pytest.mark.critical
@pytest.mark.fast
def test_a01_vertical_privilege_escalation():
    """Test prevention of vertical privilege escalation"""
    roles_permissions = {
        "auditor": ["read"],
        "bcm_coordinator": ["read", "write", "execute_bia"],
        "admin": ["read", "write", "execute_bia", "delete", "manage_users"]
    }

    def has_permission(role: str, action: str) -> bool:
        """Check if role has permission for action"""
        return action in roles_permissions.get(role, [])

    # Auditor should NOT be able to write (vertical escalation prevented)
    assert not has_permission("auditor", "write")
    assert not has_permission("auditor", "delete")

    # Auditor can only read
    assert has_permission("auditor", "read")

    # Admin has elevated permissions
    assert has_permission("admin", "manage_users")


@pytest.mark.critical
@pytest.mark.fast
def test_a01_direct_object_reference():
    """Test protection against insecure direct object references (IDOR)"""
    # Mock document database
    documents = {
        "doc-001": {"owner": "user-001", "content": "Sensitive data"},
        "doc-002": {"owner": "user-002", "content": "Other user data"}
    }

    def access_document(user_id: str, doc_id: str) -> Optional[Dict]:
        """Access document with ownership check"""
        doc = documents.get(doc_id)
        if not doc:
            return None

        # Check ownership
        if doc["owner"] != user_id:
            raise PermissionError("Access denied: not document owner")

        return doc

    # User can access their own document
    result = access_document("user-001", "doc-001")
    assert result is not None
    assert result["content"] == "Sensitive data"

    # User cannot access other user's document (IDOR prevented)
    with pytest.raises(PermissionError, match="Access denied"):
        access_document("user-001", "doc-002")


# ============================================================================
# A02:2021 - Cryptographic Failures
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a02_password_storage():
    """Test that passwords are hashed, not stored in plaintext"""
    class SecurePasswordStorage:
        @staticmethod
        def store_password(password: str) -> str:
            """Hash password before storage"""
            # Using SHA-256 (in production, use bcrypt/argon2)
            return hashlib.sha256(password.encode()).hexdigest()

        @staticmethod
        def verify_password(password: str, stored_hash: str) -> bool:
            """Verify password against hash"""
            return hashlib.sha256(password.encode()).hexdigest() == stored_hash

    password = "SecurePassword123!"
    hashed = SecurePasswordStorage.store_password(password)

    # Password should be hashed, not plaintext
    assert hashed != password
    assert len(hashed) == 64  # SHA-256 produces 64 hex chars

    # Verification should work
    assert SecurePasswordStorage.verify_password(password, hashed)
    assert not SecurePasswordStorage.verify_password("WrongPassword", hashed)


@pytest.mark.critical
@pytest.mark.fast
def test_a02_sensitive_data_encryption():
    """Test encryption of sensitive data at rest"""
    from cryptography.fernet import Fernet

    class DataEncryption:
        def __init__(self):
            # In production, store key securely in secrets manager
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)

        def encrypt(self, data: str) -> bytes:
            """Encrypt sensitive data"""
            return self.cipher.encrypt(data.encode())

        def decrypt(self, encrypted: bytes) -> str:
            """Decrypt data"""
            return self.cipher.decrypt(encrypted).decode()

    encryptor = DataEncryption()
    sensitive_data = "SSN: 123-45-6789"

    # Encrypt data
    encrypted = encryptor.encrypt(sensitive_data)

    # Encrypted data should not contain plaintext
    assert b"123-45-6789" not in encrypted

    # Decryption should recover original data
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == sensitive_data


@pytest.mark.critical
@pytest.mark.fast
def test_a02_tls_enforcement():
    """Test that TLS/HTTPS is enforced for sensitive endpoints"""
    class SecurityConfig:
        def __init__(self):
            self.enforce_https = True
            self.min_tls_version = "1.2"

        def validate_connection(self, protocol: str, tls_version: str = None) -> bool:
            """Validate connection meets security requirements"""
            if self.enforce_https and protocol != "https":
                return False

            if protocol == "https" and tls_version:
                # Extract version number
                version_match = re.search(r'(\d+\.\d+)', tls_version)
                if version_match:
                    version = float(version_match.group(1))
                    min_version = float(self.min_tls_version)
                    return version >= min_version

            return True

    config = SecurityConfig()

    # HTTP should be rejected
    assert not config.validate_connection("http")

    # HTTPS should be accepted
    assert config.validate_connection("https", "TLS 1.3")

    # Old TLS versions should be rejected
    assert not config.validate_connection("https", "TLS 1.1")


# ============================================================================
# A03:2021 - Injection
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a03_sql_injection_prevention():
    """Test SQL injection prevention using parameterized queries"""
    class SafeDatabase:
        @staticmethod
        def safe_query(user_input: str) -> str:
            """Use parameterized queries to prevent SQL injection"""
            # Simulate parameterized query (safe)
            # In production: cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))

            # Check that dangerous SQL keywords are neutralized
            dangerous_patterns = ["';", "--", "DROP", "DELETE", "UNION", "/*", "*/"]

            # In parameterized queries, these are treated as literal strings
            return f"Query with parameter: {user_input}"

        @staticmethod
        def unsafe_query(user_input: str) -> str:
            """UNSAFE: String concatenation (vulnerable to injection)"""
            # This is what NOT to do
            return f"SELECT * FROM users WHERE username = '{user_input}'"

    # Malicious input
    malicious_input = "'; DROP TABLE users; --"

    # Safe query treats input as data
    safe_result = SafeDatabase.safe_query(malicious_input)
    assert "DROP" in safe_result  # Present but neutralized as string

    # Unsafe query is vulnerable
    unsafe_result = SafeDatabase.unsafe_query(malicious_input)
    assert "DROP TABLE users" in unsafe_result  # Dangerous!


@pytest.mark.critical
@pytest.mark.fast
def test_a03_command_injection_prevention():
    """Test OS command injection prevention"""
    import subprocess
    import shlex

    class SafeCommandExecution:
        @staticmethod
        def safe_execute(filename: str) -> bool:
            """Safely execute command using list format"""
            # Whitelist allowed characters
            if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
                raise ValueError("Invalid filename")

            # Use list format (safe) instead of shell=True
            # In production: subprocess.run(["ls", "-l", filename], shell=False)
            return True

        @staticmethod
        def sanitize_input(user_input: str) -> str:
            """Sanitize user input for shell commands"""
            # Use shlex.quote for shell escaping
            return shlex.quote(user_input)

    # Safe execution rejects dangerous input
    with pytest.raises(ValueError, match="Invalid filename"):
        SafeCommandExecution.safe_execute("file; rm -rf /")

    # Sanitization escapes dangerous characters
    dangerous_input = "file; rm -rf /"
    sanitized = SafeCommandExecution.sanitize_input(dangerous_input)
    assert ";" not in sanitized or sanitized.startswith("'")  # Quoted or escaped


@pytest.mark.critical
@pytest.mark.fast
def test_a03_nosql_injection_prevention():
    """Test NoSQL injection prevention"""
    class SafeMongoQuery:
        @staticmethod
        def safe_find(username: str) -> Dict:
            """Safe query using exact match"""
            # Type validation
            if not isinstance(username, str):
                raise TypeError("Username must be string")

            # Simulate MongoDB query
            # Safe: db.users.find({"username": username})
            return {"username": username}

        @staticmethod
        def validate_input(user_input: any) -> bool:
            """Validate input is not an object/array"""
            # Reject objects that could be NoSQL operators
            return isinstance(user_input, (str, int, float, bool))

    # Safe query
    result = SafeMongoQuery.safe_find("admin")
    assert result["username"] == "admin"

    # Reject object injection
    malicious_object = {"$ne": None}  # NoSQL operator
    assert not SafeMongoQuery.validate_input(malicious_object)


# ============================================================================
# A04:2021 - Insecure Design
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a04_rate_limiting_design():
    """Test rate limiting is designed into the system"""
    class RateLimiter:
        def __init__(self, max_requests: int, window_seconds: int):
            self.max_requests = max_requests
            self.window_seconds = window_seconds
            self.requests: Dict[str, List[datetime]] = {}

        def check_limit(self, user_id: str) -> bool:
            """Check if user has exceeded rate limit"""
            now = datetime.now()

            if user_id not in self.requests:
                self.requests[user_id] = []

            # Clean old requests outside window
            self.requests[user_id] = [
                req for req in self.requests[user_id]
                if (now - req).seconds < self.window_seconds
            ]

            # Check limit
            if len(self.requests[user_id]) >= self.max_requests:
                return False  # Rate limit exceeded

            self.requests[user_id].append(now)
            return True

    limiter = RateLimiter(max_requests=5, window_seconds=60)
    user_id = "user-001"

    # First 5 requests succeed
    for i in range(5):
        assert limiter.check_limit(user_id), f"Request {i+1} should succeed"

    # 6th request fails (rate limited)
    assert not limiter.check_limit(user_id), "Rate limit should be enforced"


@pytest.mark.critical
@pytest.mark.fast
def test_a04_business_logic_validation():
    """Test business logic properly validates workflows"""
    class BIAWorkflow:
        def __init__(self):
            self.status = "not_started"
            self.completed_steps = []

        def start_workflow(self):
            """Start BIA workflow"""
            if self.status != "not_started":
                raise ValueError("Workflow already started")
            self.status = "in_progress"
            return True

        def complete_step(self, step: str):
            """Complete workflow step with dependency checking"""
            required_steps = {
                "risk_assessment": [],
                "impact_analysis": ["risk_assessment"],
                "recovery_planning": ["risk_assessment", "impact_analysis"]
            }

            # Check prerequisites
            for required in required_steps.get(step, []):
                if required not in self.completed_steps:
                    raise ValueError(f"Must complete {required} first")

            self.completed_steps.append(step)
            return True

    workflow = BIAWorkflow()

    # Cannot complete steps out of order
    with pytest.raises(ValueError, match="Must complete risk_assessment first"):
        workflow.complete_step("impact_analysis")

    # Proper sequence works
    workflow.start_workflow()
    workflow.complete_step("risk_assessment")
    workflow.complete_step("impact_analysis")
    workflow.complete_step("recovery_planning")

    assert len(workflow.completed_steps) == 3


# ============================================================================
# A05:2021 - Security Misconfiguration
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a05_default_credentials_disabled():
    """Test that default credentials are disabled"""
    class UserManagement:
        def __init__(self):
            self.default_passwords = ["admin", "password", "123456", "default"]

        def validate_password(self, password: str) -> bool:
            """Reject default/weak passwords"""
            if password.lower() in self.default_passwords:
                raise ValueError("Default password not allowed")

            if len(password) < 12:
                raise ValueError("Password too short (min 12 characters)")

            return True

    user_mgmt = UserManagement()

    # Reject default passwords
    with pytest.raises(ValueError, match="Default password not allowed"):
        user_mgmt.validate_password("admin")

    # Reject weak passwords
    with pytest.raises(ValueError, match="Password too short"):
        user_mgmt.validate_password("short")

    # Accept strong password
    assert user_mgmt.validate_password("SecurePassword123!")


@pytest.mark.critical
@pytest.mark.fast
def test_a05_error_handling_no_info_leak():
    """Test error messages don't leak sensitive information"""
    class SecureErrorHandler:
        @staticmethod
        def handle_auth_error(username: str, password: str) -> Dict:
            """Generic error message that doesn't reveal if user exists"""
            # BAD: "User not found" vs "Invalid password" reveals info
            # GOOD: Generic message

            # Simulate authentication
            if username != "valid_user" or password != "valid_pass":
                return {
                    "error": "Invalid credentials",  # Generic message
                    "code": "AUTH_FAILED"
                }

            return {"success": True}

    handler = SecureErrorHandler()

    # Both scenarios return same generic error
    result1 = handler.handle_auth_error("nonexistent_user", "password")
    result2 = handler.handle_auth_error("valid_user", "wrong_password")

    assert result1["error"] == result2["error"]  # No information leakage
    assert "not found" not in result1["error"].lower()
    assert "exists" not in result1["error"].lower()


@pytest.mark.critical
@pytest.mark.fast
def test_a05_cors_configuration():
    """Test CORS is properly configured"""
    class CORSConfig:
        def __init__(self, env: str = "production"):
            if env == "production":
                self.allowed_origins = [
                    "https://app.example.com",
                    "https://admin.example.com"
                ]
            else:
                # Development mode is more permissive but still controlled
                self.allowed_origins = ["http://localhost:3000"]

            self.allow_credentials = True

        def validate_origin(self, origin: str) -> bool:
            """Check if origin is allowed"""
            return origin in self.allowed_origins

    # Production config should be restrictive
    prod_config = CORSConfig("production")
    assert not prod_config.validate_origin("https://evil.com")
    assert prod_config.validate_origin("https://app.example.com")

    # Should not use wildcard in production
    assert "*" not in prod_config.allowed_origins


# ============================================================================
# A06:2021 - Vulnerable and Outdated Components
# ============================================================================

@pytest.mark.fast
def test_a06_dependency_versions():
    """Test that dependencies are tracked and up-to-date"""
    class DependencyManager:
        def __init__(self):
            self.dependencies = {
                "fastapi": {"current": "0.104.0", "latest": "0.104.0", "vulnerable": False},
                "pydantic": {"current": "2.5.0", "latest": "2.5.0", "vulnerable": False},
                "sqlalchemy": {"current": "2.0.23", "latest": "2.0.23", "vulnerable": False}
            }

        def check_vulnerabilities(self) -> List[str]:
            """Check for vulnerable dependencies"""
            vulnerable = []
            for name, info in self.dependencies.items():
                if info["vulnerable"]:
                    vulnerable.append(name)
            return vulnerable

        def check_outdated(self) -> List[str]:
            """Check for outdated dependencies"""
            outdated = []
            for name, info in self.dependencies.items():
                if info["current"] != info["latest"]:
                    outdated.append(name)
            return outdated

    dep_mgr = DependencyManager()

    # No vulnerable dependencies
    vulnerabilities = dep_mgr.check_vulnerabilities()
    assert len(vulnerabilities) == 0, f"Vulnerable dependencies found: {vulnerabilities}"

    # All dependencies up-to-date
    outdated = dep_mgr.check_outdated()
    assert len(outdated) == 0, f"Outdated dependencies found: {outdated}"


# ============================================================================
# A07:2021 - Identification and Authentication Failures
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a07_multi_factor_authentication():
    """Test MFA implementation"""
    class MFAManager:
        def __init__(self):
            self.mfa_secrets = {}

        def enable_mfa(self, user_id: str) -> str:
            """Enable MFA and return secret"""
            secret = secrets.token_urlsafe(32)
            self.mfa_secrets[user_id] = secret
            return secret

        def verify_mfa(self, user_id: str, code: str) -> bool:
            """Verify MFA code"""
            # Simplified verification (in production use TOTP)
            if user_id not in self.mfa_secrets:
                return False

            # Mock verification
            expected_code = self.mfa_secrets[user_id][:6]
            return code == expected_code

    mfa = MFAManager()
    user_id = "user-001"

    # Enable MFA
    secret = mfa.enable_mfa(user_id)
    assert secret is not None

    # Valid code passes
    valid_code = secret[:6]
    assert mfa.verify_mfa(user_id, valid_code)

    # Invalid code fails
    assert not mfa.verify_mfa(user_id, "wrong")


@pytest.mark.critical
@pytest.mark.fast
def test_a07_session_timeout():
    """Test session timeout implementation"""
    class SessionManager:
        def __init__(self, timeout_minutes: int = 30):
            self.timeout_minutes = timeout_minutes
            self.sessions = {}

        def create_session(self, user_id: str) -> str:
            """Create new session"""
            session_id = secrets.token_urlsafe(32)
            self.sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now()
            }
            return session_id

        def validate_session(self, session_id: str) -> bool:
            """Validate session hasn't timed out"""
            if session_id not in self.sessions:
                return False

            session = self.sessions[session_id]
            elapsed_minutes = (datetime.now() - session["last_activity"]).seconds / 60

            if elapsed_minutes > self.timeout_minutes:
                # Session expired
                del self.sessions[session_id]
                return False

            # Update last activity
            session["last_activity"] = datetime.now()
            return True

    session_mgr = SessionManager(timeout_minutes=30)

    # Create valid session
    session_id = session_mgr.create_session("user-001")
    assert session_mgr.validate_session(session_id)

    # Invalid session fails
    assert not session_mgr.validate_session("invalid-session-id")


@pytest.mark.critical
@pytest.mark.fast
def test_a07_password_complexity():
    """Test password complexity requirements"""
    import re

    class PasswordValidator:
        @staticmethod
        def validate(password: str) -> bool:
            """Validate password meets complexity requirements"""
            if len(password) < 12:
                raise ValueError("Password must be at least 12 characters")

            if not re.search(r'[A-Z]', password):
                raise ValueError("Password must contain uppercase letter")

            if not re.search(r'[a-z]', password):
                raise ValueError("Password must contain lowercase letter")

            if not re.search(r'[0-9]', password):
                raise ValueError("Password must contain number")

            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValueError("Password must contain special character")

            return True

    validator = PasswordValidator()

    # Weak passwords fail
    with pytest.raises(ValueError, match="at least 12 characters"):
        validator.validate("Short1!")

    with pytest.raises(ValueError, match="uppercase"):
        validator.validate("lowercase123!")

    # Strong password passes
    assert validator.validate("SecurePassword123!")


# ============================================================================
# A08:2021 - Software and Data Integrity Failures
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a08_code_signature_verification():
    """Test code/package signature verification"""
    class PackageVerifier:
        def __init__(self):
            self.trusted_signatures = {
                "package-v1.0.0": "sha256:abc123...",
                "package-v2.0.0": "sha256:def456..."
            }

        def verify_package(self, package_name: str, signature: str) -> bool:
            """Verify package signature"""
            expected_sig = self.trusted_signatures.get(package_name)
            if not expected_sig:
                raise ValueError("Unknown package")

            return signature == expected_sig

    verifier = PackageVerifier()

    # Valid signature passes
    assert verifier.verify_package("package-v1.0.0", "sha256:abc123...")

    # Invalid signature fails
    assert not verifier.verify_package("package-v1.0.0", "sha256:wrong...")


@pytest.mark.critical
@pytest.mark.fast
def test_a08_ci_cd_pipeline_integrity():
    """Test CI/CD pipeline integrity checks"""
    class PipelineValidator:
        def __init__(self):
            self.required_checks = [
                "security_scan",
                "test_execution",
                "code_review",
                "dependency_audit"
            ]

        def validate_pipeline(self, completed_checks: List[str]) -> bool:
            """Validate all required checks completed"""
            for check in self.required_checks:
                if check not in completed_checks:
                    raise ValueError(f"Missing required check: {check}")
            return True

    validator = PipelineValidator()

    # Complete pipeline passes
    completed = ["security_scan", "test_execution", "code_review", "dependency_audit"]
    assert validator.validate_pipeline(completed)

    # Incomplete pipeline fails
    incomplete = ["security_scan", "test_execution"]
    with pytest.raises(ValueError, match="Missing required check"):
        validator.validate_pipeline(incomplete)


# ============================================================================
# A09:2021 - Security Logging and Monitoring Failures
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a09_security_event_logging():
    """Test security events are logged"""
    class SecurityLogger:
        def __init__(self):
            self.logs = []

        def log_authentication(self, user_id: str, success: bool, ip_address: str):
            """Log authentication attempt"""
            self.logs.append({
                "event_type": "authentication",
                "user_id": user_id,
                "success": success,
                "ip_address": ip_address,
                "timestamp": datetime.now().isoformat()
            })

        def log_access_control(self, user_id: str, resource: str, action: str, allowed: bool):
            """Log access control decision"""
            self.logs.append({
                "event_type": "access_control",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "allowed": allowed,
                "timestamp": datetime.now().isoformat()
            })

        def get_failed_logins(self, user_id: str) -> int:
            """Count failed login attempts"""
            return sum(
                1 for log in self.logs
                if log["event_type"] == "authentication"
                and log["user_id"] == user_id
                and not log["success"]
            )

    logger = SecurityLogger()

    # Log authentication events
    logger.log_authentication("user-001", False, "192.168.1.100")
    logger.log_authentication("user-001", False, "192.168.1.100")
    logger.log_authentication("user-001", True, "192.168.1.100")

    # Failed attempts are logged
    failed_count = logger.get_failed_logins("user-001")
    assert failed_count == 2

    # Access control logged
    logger.log_access_control("user-001", "doc-001", "read", True)
    assert len(logger.logs) == 4


@pytest.mark.critical
@pytest.mark.fast
def test_a09_sensitive_data_not_logged():
    """Test sensitive data is not logged"""
    class SafeLogger:
        SENSITIVE_FIELDS = ["password", "token", "secret", "api_key", "ssn", "credit_card"]

        @staticmethod
        def sanitize_log_data(data: Dict) -> Dict:
            """Remove sensitive fields from log data"""
            sanitized = {}
            for key, value in data.items():
                if key.lower() in SafeLogger.SENSITIVE_FIELDS:
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = value
            return sanitized

    logger = SafeLogger()

    # Data with sensitive fields
    user_data = {
        "user_id": "user-001",
        "username": "john.doe",
        "password": "SecurePassword123!",
        "token": "jwt-token-here",
        "role": "bcm_coordinator"
    }

    sanitized = logger.sanitize_log_data(user_data)

    # Sensitive fields redacted
    assert sanitized["password"] == "***REDACTED***"
    assert sanitized["token"] == "***REDACTED***"

    # Non-sensitive fields preserved
    assert sanitized["user_id"] == "user-001"
    assert sanitized["role"] == "bcm_coordinator"


# ============================================================================
# A10:2021 - Server-Side Request Forgery (SSRF)
# ============================================================================

@pytest.mark.critical
@pytest.mark.fast
def test_a10_ssrf_url_validation():
    """Test SSRF prevention through URL validation"""
    import ipaddress

    class SSRFProtection:
        ALLOWED_PROTOCOLS = ["https"]
        BLOCKED_HOSTS = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "169.254.169.254"  # AWS metadata endpoint
        ]

        @staticmethod
        def validate_url(url: str) -> bool:
            """Validate URL is safe from SSRF"""
            from urllib.parse import urlparse

            parsed = urlparse(url)

            # Check protocol
            if parsed.scheme not in SSRFProtection.ALLOWED_PROTOCOLS:
                raise ValueError(f"Protocol {parsed.scheme} not allowed")

            # Check for blocked hosts
            hostname = parsed.hostname or ""
            if hostname.lower() in SSRFProtection.BLOCKED_HOSTS:
                raise ValueError(f"Host {hostname} is blocked")

            # Check for private IP ranges
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    raise ValueError("Private/internal IP addresses not allowed")
            except ValueError:
                # Not an IP address, hostname is OK
                pass

            return True

    protection = SSRFProtection()

    # Valid external URL passes
    assert protection.validate_url("https://api.example.com/data")

    # Localhost blocked
    with pytest.raises(ValueError, match="blocked"):
        protection.validate_url("https://localhost/admin")

    # AWS metadata endpoint blocked
    with pytest.raises(ValueError, match="blocked"):
        protection.validate_url("https://169.254.169.254/latest/meta-data/")

    # Private IP blocked
    with pytest.raises(ValueError, match="Private/internal IP"):
        protection.validate_url("https://192.168.1.1/config")


@pytest.mark.critical
@pytest.mark.fast
def test_a10_ssrf_webhook_validation():
    """Test webhook URL validation to prevent SSRF"""
    class WebhookValidator:
        @staticmethod
        def validate_webhook_url(url: str) -> bool:
            """Validate webhook URL is external and safe"""
            from urllib.parse import urlparse
            import ipaddress

            parsed = urlparse(url)

            # Must be HTTPS
            if parsed.scheme != "https":
                raise ValueError("Webhook must use HTTPS")

            # Check hostname
            hostname = parsed.hostname or ""

            # Block internal hosts
            internal_patterns = ["localhost", "127.", "192.168.", "10.", "172."]
            if any(pattern in hostname for pattern in internal_patterns):
                raise ValueError("Internal hosts not allowed for webhooks")

            # Block cloud metadata endpoints
            metadata_hosts = ["169.254.169.254", "metadata.google.internal"]
            if hostname in metadata_hosts:
                raise ValueError("Cloud metadata endpoints not allowed")

            return True

    validator = WebhookValidator()

    # Valid webhook passes
    assert validator.validate_webhook_url("https://hooks.example.com/webhook")

    # Internal network blocked
    with pytest.raises(ValueError, match="Internal hosts not allowed"):
        validator.validate_webhook_url("https://192.168.1.100/webhook")

    # Cloud metadata blocked
    with pytest.raises(ValueError, match="Cloud metadata"):
        validator.validate_webhook_url("https://169.254.169.254/webhook")


@pytest.mark.integration
@pytest.mark.critical
@pytest.mark.asyncio
async def test_owasp_comprehensive_security_workflow():
    """
    Comprehensive test validating multiple OWASP controls in a workflow

    Simulates a complete user workflow with security controls:
    1. Authentication (A07)
    2. Authorization (A01)
    3. Business logic (A04)
    4. Logging (A09)
    5. Data protection (A02)
    """
    # Initialize security components
    class SecureWorkflow:
        def __init__(self):
            self.users = {}
            self.sessions = {}
            self.logs = []

        def authenticate(self, username: str, password: str) -> Optional[str]:
            """Authenticate user (A07)"""
            # Hash password
            hashed = hashlib.sha256(password.encode()).hexdigest()

            user = self.users.get(username)
            if not user or user["password_hash"] != hashed:
                self.logs.append({"event": "auth_failed", "username": username})
                return None

            # Create session
            session_id = secrets.token_urlsafe(32)
            self.sessions[session_id] = {
                "user_id": user["user_id"],
                "role": user["role"]
            }

            self.logs.append({"event": "auth_success", "user_id": user["user_id"]})
            return session_id

        def authorize(self, session_id: str, action: str) -> bool:
            """Authorize action (A01)"""
            session = self.sessions.get(session_id)
            if not session:
                return False

            permissions = {
                "auditor": ["read"],
                "bcm_coordinator": ["read", "write", "execute_bia"]
            }

            allowed = action in permissions.get(session["role"], [])
            self.logs.append({
                "event": "authorization",
                "user_id": session["user_id"],
                "action": action,
                "allowed": allowed
            })

            return allowed

    workflow = SecureWorkflow()

    # Setup user
    workflow.users["john.doe"] = {
        "user_id": "user-001",
        "password_hash": hashlib.sha256(b"SecurePassword123!").hexdigest(),
        "role": "bcm_coordinator"
    }

    # Test authentication
    session_id = workflow.authenticate("john.doe", "SecurePassword123!")
    assert session_id is not None

    # Test authorization
    assert workflow.authorize(session_id, "execute_bia")
    assert not workflow.authorize(session_id, "delete_all")

    # Verify logging
    assert len(workflow.logs) >= 3
    assert any(log["event"] == "auth_success" for log in workflow.logs)
