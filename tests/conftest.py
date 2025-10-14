"""
Global pytest configuration and fixtures for AI-Powered BCM Platform

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from unittest.mock import Mock, AsyncMock
import fakeredis.aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os


# ==================== Event Loop Configuration ====================
@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests

    Scope: session - One loop for entire test session
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== Database Fixtures ====================
@pytest.fixture(scope="session")
def database_url() -> str:
    """
    Test database URL from environment or default

    Export DATABASE_URL for custom test database:
        export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/test_db"
    """
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test_bcm"
    )


@pytest.fixture(scope="session")
async def test_db_engine(database_url):
    """
    Test database engine (session-scoped)

    Creates async SQLAlchemy engine for testing
    """
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Database session with automatic rollback after each test

    Usage:
        async def test_create_workflow(db_session):
            workflow = Workflow(...)
            db_session.add(workflow)
            await db_session.commit()
    """
    async_session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


# ==================== Redis/Cache Fixtures ====================
@pytest.fixture
async def redis_client():
    """
    Fake Redis client for testing (fakeredis)

    No Redis server required - all operations in-memory
    """
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake_redis
    await fake_redis.flushall()
    await fake_redis.close()


@pytest.fixture
def mock_cache():
    """
    Mock cache client with simple dict backend
    """
    cache = {}

    class MockCache:
        async def get(self, key: str) -> Any:
            return cache.get(key)

        async def set(self, key: str, value: Any, ttl: int = 3600):
            cache[key] = value

        async def delete(self, key: str):
            cache.pop(key, None)

        async def clear(self):
            cache.clear()

    return MockCache()


# ==================== EventBus Fixtures ====================
@pytest.fixture
def mock_eventbus():
    """
    Mock EventBus client for testing event-driven code

    Usage:
        async def test_case_collection(mock_eventbus):
            await collector.collect_case(workflow)
            mock_eventbus.publish.assert_called_once_with(
                topic="case.created",
                event={"case_id": "..."}
            )
    """
    eventbus = Mock()

    # Mock publish as async
    async def mock_publish(topic: str, event: Dict[str, Any]):
        pass

    eventbus.publish = AsyncMock(side_effect=mock_publish)
    eventbus.subscribe = Mock()
    return eventbus


# ==================== AI Foundation Mocks ====================
@pytest.fixture
def mock_llm_client():
    """
    Mock LLM client with deterministic responses

    Returns structured responses for testing without API calls
    """
    client = Mock()

    async def mock_generate(prompt: str, **kwargs):
        return {
            "content": "Sample LLM response for testing",
            "patterns": ["best_practice_1", "best_practice_2"],
            "recommendations": ["recommendation_1"],
            "insights": ["insight_1"],
            "model": "mock-model",
            "tokens": 100
        }

    client.generate = AsyncMock(side_effect=mock_generate)
    client.generate_stream = AsyncMock()
    return client


@pytest.fixture
def mock_rag_pipeline():
    """
    Mock RAG pipeline with sample document retrieval

    Returns ISO 22301 and BIA-related documents
    """
    pipeline = Mock()

    async def mock_retrieve(query: str, top_k: int = 5, **kwargs):
        return {
            "documents": [
                {
                    "id": "doc-iso-22301-1",
                    "content": "ISO 22301 is the international standard for Business Continuity Management",
                    "score": 0.92,
                    "metadata": {"source": "ISO 22301", "clause": "4.1"}
                },
                {
                    "id": "doc-bia-guidance",
                    "content": "Business Impact Analysis (BIA) identifies critical processes",
                    "score": 0.88,
                    "metadata": {"source": "BIA Guide", "section": "2.3"}
                },
                {
                    "id": "doc-rto-rpo",
                    "content": "RTO (Recovery Time Objective) and RPO (Recovery Point Objective)",
                    "score": 0.85,
                    "metadata": {"source": "BCM Handbook", "page": 42}
                }
            ],
            "query": query,
            "total_found": 3
        }

    pipeline.retrieve = AsyncMock(side_effect=mock_retrieve)
    pipeline.retrieve_with_reranking = AsyncMock(side_effect=mock_retrieve)
    return pipeline


@pytest.fixture
def mock_qdrant():
    """
    Mock Qdrant vector store client
    """
    client = Mock()

    def mock_search(collection_name: str, query_vector: list, limit: int = 5):
        return [
            {
                "id": f"vec-{i}",
                "score": 0.9 - (i * 0.05),
                "payload": {"text": f"Sample content {i}"}
            }
            for i in range(limit)
        ]

    client.search = Mock(side_effect=mock_search)
    client.upsert = Mock(return_value={"status": "ok"})
    client.create_collection = Mock()
    return client


@pytest.fixture
def mock_ml_predictor():
    """
    Mock ML predictor with sample predictions
    """
    predictor = Mock()

    async def mock_predict(features: Dict[str, Any]):
        return {
            "success_probability": 0.85,
            "estimated_duration_days": 14,
            "risk_level": "medium",
            "risk_factors": ["limited_resources", "tight_timeline"],
            "confidence": 0.82,
            "model_version": "v1.0.0"
        }

    predictor.predict = AsyncMock(side_effect=mock_predict)
    return predictor


# ==================== Temporal Mocks ====================
@pytest.fixture
def mock_temporal_client():
    """
    Mock Temporal client for workflow testing
    """
    client = Mock()

    async def mock_start_workflow(workflow_id: str, workflow_type: str, args: Dict):
        return f"workflow-run-{workflow_id}"

    async def mock_get_workflow_result(workflow_run_id: str):
        return {"status": "completed", "result": {"success": True}}

    client.start_workflow = AsyncMock(side_effect=mock_start_workflow)
    client.get_workflow_result = AsyncMock(side_effect=mock_get_workflow_result)
    client.signal_workflow = AsyncMock()
    return client


# ==================== Test Data Generators ====================
@pytest.fixture
def sample_workflow_context():
    """
    Sample workflow context for testing

    Represents a typical planning workflow in draft stage
    """
    return {
        "workflow_id": "test-workflow-001",
        "module": "planning",
        "tenant_id": "tenant-test-001",
        "user_id": "user-test-001",
        "current_stage": "draft",
        "data": {
            "strategy_type": "FAST_RECOVERY",
            "target_rto_hours": 2,
            "target_rpo_hours": 1,
            "estimated_cost": 500000,
            "priority": "high"
        },
        "available_actions": ["submit_review", "update_costs", "add_stakeholders"],
        "gaps": [],
        "created_at": "2025-10-06T10:00:00Z",
        "updated_at": "2025-10-06T10:00:00Z"
    }


@pytest.fixture
def sample_organization():
    """
    Sample organization for testing
    """
    return {
        "id": "org-test-001",
        "name": "Test Healthcare Inc",
        "industry": "healthcare",
        "size": "medium",
        "maturity_level": "basic",
        "country": "US",
        "employees": 500,
        "annual_revenue": 50000000
    }


@pytest.fixture
def sample_case_data():
    """
    Sample completed workflow case for testing
    """
    return {
        "workflow_id": "completed-workflow-001",
        "module": "planning",
        "industry": "healthcare",
        "org_size": "medium",
        "total_duration_days": 18,
        "stages_completed": ["draft", "review", "approved"],
        "success": True,
        "challenges": ["budget_constraints", "stakeholder_alignment"],
        "best_practices": ["early_stakeholder_engagement", "iterative_approach"],
        "patterns_learned": ["pattern_1", "pattern_2"],
        "completion_date": "2025-09-20T15:30:00Z"
    }


@pytest.fixture
def sample_user():
    """
    Sample user for testing
    """
    return {
        "id": "user-test-001",
        "email": "test@example.com",
        "name": "Test User",
        "role": "bcm_manager",
        "tenant_id": "tenant-test-001",
        "permissions": ["workflows.read", "workflows.write", "cases.read"]
    }


# ==================== Security Testing Fixtures ====================
@pytest.fixture
def sql_injection_patterns():
    """
    Common SQL injection attack patterns for security testing
    """
    return [
        "'; DROP TABLE workflows; --",
        "' OR '1'='1",
        "'; DELETE FROM workflows WHERE '1'='1'; --",
        "' UNION SELECT null, null, null; --",
        "admin'--",
        "' OR '1'='1' --",
        "'; UPDATE workflows SET tenant_id='hacker'; --",
        "1' UNION SELECT password FROM users; --",
        "'; EXEC sp_MSForEachTable 'DROP TABLE ?'; --",
    ]


@pytest.fixture
def xss_patterns():
    """
    XSS (Cross-Site Scripting) attack patterns
    """
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg/onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'>"
    ]


@pytest.fixture
def auth_user():
    """
    Authenticated test user with JWT token

    Usage:
        async def test_protected_endpoint(auth_user, test_client):
            response = await test_client.get(
                "/api/workflows",
                headers={"Authorization": f"Bearer {auth_user['token']}"}
            )
    """
    import jwt
    from datetime import datetime, timedelta

    user_data = {
        "user_id": "test-user-001",
        "username": "testuser",
        "email": "test@example.com",
        "role": "bcm_coordinator",
        "organization_id": "org-001",
        "permissions": [
            "workflows.read",
            "workflows.write",
            "bia.execute",
            "risk.assess"
        ]
    }

    # Generate JWT token
    secret = "test-secret-key-do-not-use-in-production"
    payload = {
        "user_id": user_data["user_id"],
        "role": user_data["role"],
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, secret, algorithm="HS256")

    user_data["token"] = token
    user_data["secret"] = secret

    return user_data


@pytest.fixture
def mock_jwt_manager():
    """
    Mock JWT token manager for authentication testing

    Usage:
        def test_token_generation(mock_jwt_manager):
            token = mock_jwt_manager.create_token("user-001")
            assert mock_jwt_manager.verify_token(token)
    """
    import jwt
    from datetime import datetime, timedelta

    class JWTManager:
        def __init__(self):
            self.secret = "test-secret-key"
            self.algorithm = "HS256"

        def create_token(self, user_id: str, role: str = "user", expiry_hours: int = 24):
            """Create JWT token"""
            payload = {
                "user_id": user_id,
                "role": role,
                "exp": datetime.utcnow() + timedelta(hours=expiry_hours),
                "iat": datetime.utcnow()
            }
            return jwt.encode(payload, self.secret, algorithm=self.algorithm)

        def verify_token(self, token: str) -> Dict[str, Any]:
            """Verify and decode token"""
            try:
                return jwt.decode(token, self.secret, algorithms=[self.algorithm])
            except jwt.ExpiredSignatureError:
                raise ValueError("Token expired")
            except jwt.InvalidTokenError:
                raise ValueError("Invalid token")

        def create_expired_token(self, user_id: str):
            """Create already-expired token for testing"""
            payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() - timedelta(hours=1),
                "iat": datetime.utcnow() - timedelta(hours=2)
            }
            return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    return JWTManager()


@pytest.fixture
def mock_rbac_manager():
    """
    Mock RBAC (Role-Based Access Control) manager

    Usage:
        def test_authorization(mock_rbac_manager):
            assert mock_rbac_manager.can_user_perform("bcm_coordinator", "execute_bia")
            assert not mock_rbac_manager.can_user_perform("auditor", "delete_plan")
    """
    class RBACManager:
        def __init__(self):
            self.roles_permissions = {
                "auditor": [
                    "workflows.read",
                    "plans.read",
                    "reports.read"
                ],
                "bcm_coordinator": [
                    "workflows.read",
                    "workflows.write",
                    "bia.execute",
                    "risk.assess",
                    "plans.read",
                    "plans.write"
                ],
                "risk_manager": [
                    "workflows.read",
                    "workflows.write",
                    "risk.read",
                    "risk.write",
                    "risk.assess"
                ],
                "admin": [
                    "workflows.*",
                    "plans.*",
                    "risk.*",
                    "bia.*",
                    "users.manage",
                    "system.configure"
                ]
            }

        def can_user_perform(self, role: str, permission: str) -> bool:
            """Check if role has permission"""
            role_perms = self.roles_permissions.get(role, [])

            # Check exact match
            if permission in role_perms:
                return True

            # Check wildcard permissions (e.g., "workflows.*")
            for perm in role_perms:
                if perm.endswith(".*"):
                    prefix = perm[:-2]
                    if permission.startswith(prefix):
                        return True

            return False

        def get_user_permissions(self, role: str) -> list:
            """Get all permissions for role"""
            return self.roles_permissions.get(role, [])

    return RBACManager()


@pytest.fixture
def mock_session_manager():
    """
    Mock session manager for session testing

    Usage:
        async def test_session_timeout(mock_session_manager):
            session_id = await mock_session_manager.create_session("user-001")
            assert await mock_session_manager.is_valid(session_id)
    """
    import secrets
    from datetime import datetime, timedelta

    class SessionManager:
        def __init__(self, timeout_minutes: int = 30):
            self.sessions = {}
            self.timeout_minutes = timeout_minutes

        async def create_session(self, user_id: str, metadata: Dict = None) -> str:
            """Create new session"""
            session_id = secrets.token_urlsafe(32)
            self.sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "metadata": metadata or {}
            }
            return session_id

        async def is_valid(self, session_id: str) -> bool:
            """Check if session is valid and not expired"""
            if session_id not in self.sessions:
                return False

            session = self.sessions[session_id]
            elapsed = (datetime.now() - session["last_activity"]).total_seconds() / 60

            if elapsed > self.timeout_minutes:
                await self.destroy_session(session_id)
                return False

            # Update last activity
            session["last_activity"] = datetime.now()
            return True

        async def destroy_session(self, session_id: str):
            """Destroy session"""
            self.sessions.pop(session_id, None)

        async def get_session_data(self, session_id: str) -> Dict:
            """Get session data"""
            return self.sessions.get(session_id)

    return SessionManager()


@pytest.fixture
def password_validator():
    """
    Password complexity validator fixture

    Usage:
        def test_password_strength(password_validator):
            assert password_validator.is_valid("SecurePassword123!")
            assert not password_validator.is_valid("weak")
    """
    import re

    class PasswordValidator:
        def __init__(self):
            self.min_length = 12
            self.require_uppercase = True
            self.require_lowercase = True
            self.require_digit = True
            self.require_special = True
            self.blocked_passwords = [
                "password", "admin", "123456", "qwerty", "default"
            ]

        def is_valid(self, password: str) -> tuple[bool, list]:
            """
            Validate password complexity
            Returns: (is_valid, errors)
            """
            errors = []

            if len(password) < self.min_length:
                errors.append(f"Password must be at least {self.min_length} characters")

            if self.require_uppercase and not re.search(r'[A-Z]', password):
                errors.append("Password must contain uppercase letter")

            if self.require_lowercase and not re.search(r'[a-z]', password):
                errors.append("Password must contain lowercase letter")

            if self.require_digit and not re.search(r'\d', password):
                errors.append("Password must contain digit")

            if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors.append("Password must contain special character")

            if password.lower() in self.blocked_passwords:
                errors.append("Password is too common")

            return (len(errors) == 0, errors)

    return PasswordValidator()


@pytest.fixture
def ssrf_validator():
    """
    SSRF (Server-Side Request Forgery) validator

    Usage:
        def test_url_validation(ssrf_validator):
            assert ssrf_validator.is_safe("https://api.example.com")
            assert not ssrf_validator.is_safe("http://localhost/admin")
    """
    import ipaddress
    from urllib.parse import urlparse

    class SSRFValidator:
        def __init__(self):
            self.allowed_protocols = ["https"]
            self.blocked_hosts = [
                "localhost",
                "127.0.0.1",
                "0.0.0.0",
                "169.254.169.254",  # AWS metadata
                "metadata.google.internal",  # GCP metadata
            ]

        def is_safe(self, url: str) -> tuple[bool, str]:
            """
            Validate URL is safe from SSRF
            Returns: (is_safe, reason)
            """
            try:
                parsed = urlparse(url)

                # Check protocol
                if parsed.scheme not in self.allowed_protocols:
                    return (False, f"Protocol {parsed.scheme} not allowed")

                hostname = parsed.hostname or ""

                # Check blocked hosts
                if hostname.lower() in self.blocked_hosts:
                    return (False, f"Host {hostname} is blocked")

                # Check for private IP ranges
                try:
                    ip = ipaddress.ip_address(hostname)
                    if ip.is_private or ip.is_loopback or ip.is_link_local:
                        return (False, "Private/internal IP not allowed")
                except ValueError:
                    # Not an IP, that's OK
                    pass

                return (True, "URL is safe")

            except Exception as e:
                return (False, f"Invalid URL: {str(e)}")

    return SSRFValidator()


@pytest.fixture
def rate_limiter():
    """
    Rate limiter for API security testing

    Usage:
        async def test_rate_limiting(rate_limiter):
            for i in range(5):
                assert await rate_limiter.check_limit("user-001")
            # 6th request should fail
            assert not await rate_limiter.check_limit("user-001")
    """
    from datetime import datetime

    class RateLimiter:
        def __init__(self, max_requests: int = 100, window_seconds: int = 60):
            self.max_requests = max_requests
            self.window_seconds = window_seconds
            self.requests = {}

        async def check_limit(self, identifier: str) -> bool:
            """Check if identifier has exceeded rate limit"""
            now = datetime.now()

            if identifier not in self.requests:
                self.requests[identifier] = []

            # Clean old requests outside window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if (now - req_time).total_seconds() < self.window_seconds
            ]

            # Check limit
            if len(self.requests[identifier]) >= self.max_requests:
                return False

            # Record request
            self.requests[identifier].append(now)
            return True

        async def reset(self, identifier: str):
            """Reset rate limit for identifier"""
            self.requests.pop(identifier, None)

    return RateLimiter()


@pytest.fixture
def input_sanitizer():
    """
    Input sanitizer for injection prevention testing

    Usage:
        def test_input_sanitization(input_sanitizer):
            dirty = "'; DROP TABLE users; --"
            clean = input_sanitizer.sanitize_sql(dirty)
            assert "DROP" not in clean or clean != dirty
    """
    import re
    import html

    class InputSanitizer:
        def sanitize_sql(self, user_input: str) -> str:
            """Sanitize input for SQL (remove dangerous chars)"""
            dangerous = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
            sanitized = user_input
            for char in dangerous:
                sanitized = sanitized.replace(char, "")
            return sanitized

        def sanitize_html(self, user_input: str) -> str:
            """Sanitize HTML to prevent XSS"""
            return html.escape(user_input)

        def sanitize_shell(self, user_input: str) -> str:
            """Sanitize for shell command injection"""
            # Only allow alphanumeric, dash, underscore, dot
            return re.sub(r'[^a-zA-Z0-9_\-\.]', '', user_input)

        def sanitize_path(self, user_input: str) -> str:
            """Sanitize file path to prevent directory traversal"""
            # Remove ../ and ../
            sanitized = user_input.replace("../", "").replace("..\\", "")
            # Only allow safe characters
            sanitized = re.sub(r'[^a-zA-Z0-9_\-\./]', '', sanitized)
            return sanitized

    return InputSanitizer()


@pytest.fixture
def security_logger():
    """
    Security event logger for testing logging mechanisms

    Usage:
        def test_failed_login_logging(security_logger):
            security_logger.log_auth_failure("user-001", "192.168.1.1")
            events = security_logger.get_events("authentication")
            assert len(events) == 1
    """
    from datetime import datetime

    class SecurityLogger:
        def __init__(self):
            self.events = []
            self.sensitive_fields = [
                "password", "token", "secret", "api_key",
                "ssn", "credit_card", "private_key"
            ]

        def log_auth_success(self, user_id: str, ip_address: str, metadata: Dict = None):
            """Log successful authentication"""
            self.events.append({
                "event_type": "authentication",
                "status": "success",
                "user_id": user_id,
                "ip_address": ip_address,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            })

        def log_auth_failure(self, user_id: str, ip_address: str, reason: str = None):
            """Log failed authentication"""
            self.events.append({
                "event_type": "authentication",
                "status": "failure",
                "user_id": user_id,
                "ip_address": ip_address,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })

        def log_access_control(self, user_id: str, resource: str, action: str, allowed: bool):
            """Log access control decision"""
            self.events.append({
                "event_type": "access_control",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "allowed": allowed,
                "timestamp": datetime.now().isoformat()
            })

        def sanitize_log_data(self, data: Dict) -> Dict:
            """Remove sensitive fields from log data"""
            return {
                k: "***REDACTED***" if k in self.sensitive_fields else v
                for k, v in data.items()
            }

        def get_events(self, event_type: str = None) -> list:
            """Get logged events, optionally filtered by type"""
            if event_type:
                return [e for e in self.events if e.get("event_type") == event_type]
            return self.events

        def get_failed_attempts(self, user_id: str) -> int:
            """Count failed authentication attempts for user"""
            return sum(
                1 for e in self.events
                if e.get("event_type") == "authentication"
                and e.get("user_id") == user_id
                and e.get("status") == "failure"
            )

    return SecurityLogger()


# ==================== AI Foundation Integration Fixtures ====================
@pytest.fixture
def mock_ai_foundation():
    """
    Complete mock AI foundation for analyzers/specialists

    Provides all AI services (RAG, LLM, ML, anomaly detection, knowledge)
    """
    return {
        "rag": mock_rag_pipeline(),
        "llm": mock_llm_client(),
        "predictor": mock_ml_predictor(),
        "anomaly_detector": Mock(),
        "knowledge": Mock()
    }


# ==================== VCR Configuration ====================
@pytest.fixture(scope="module")
def vcr_config():
    """
    VCR configuration for recording/replaying HTTP calls

    Use with @pytest.mark.vcr decorator:
        @pytest.mark.vcr(cassette_name="test_llm_call.yaml")
        def test_llm_integration(llm_client):
            response = llm_client.generate("test prompt")
    """
    return {
        "filter_headers": [
            "authorization",
            "api-key",
            "x-api-key",
            "cookie",
            "set-cookie"
        ],
        "record_mode": "once",  # Record once, then replay
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "cassette_library_dir": "tests/fixtures/vcr_cassettes",
        "decode_compressed_response": True
    }


# ==================== Test Markers ====================
def pytest_configure(config):
    """
    Register custom pytest markers
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "vcr: marks tests that use VCR for HTTP recording"
    )


# ==================== Async Test Helpers ====================
@pytest.fixture
def async_timeout():
    """Default timeout for async tests (10 seconds)"""
    return 10


# ==================== Cleanup ====================
@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """
    Automatic cleanup after each test

    Ensures clean state for next test
    """
    yield
    # Cleanup code here if needed
    pass
