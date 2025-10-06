"""
Integration Test Configuration and Shared Fixtures

Provides shared fixtures for integration testing across all BCM services:
- Docker service management
- Service URLs and health checks
- Authentication helpers
- Database cleanup
- EventBus helpers
"""

import asyncio
import os
import time
from typing import AsyncGenerator, Dict, List
import pytest
import httpx
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load test environment
load_dotenv(".env.test")


# ===== SESSION FIXTURES =====

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def service_urls() -> Dict[str, str]:
    """
    Service URLs for integration tests.

    Uses localhost URLs when accessing from host machine.
    Docker network URLs are used for inter-service communication.
    """
    return {
        "bia": os.getenv("BIA_SERVICE_URL", "http://localhost:8012"),
        "planning": os.getenv("PLANNING_SERVICE_URL", "http://localhost:8011"),
        "plans": os.getenv("PLANS_SERVICE_URL", "http://localhost:8023"),
        "compliance": os.getenv("COMPLIANCE_SERVICE_URL", "http://localhost:8014"),
        "eventbus": os.getenv("EVENTBUS_URL", "http://localhost:8001"),
    }


@pytest.fixture(scope="session")
def jwt_secret() -> str:
    """JWT secret for test token generation"""
    return os.getenv("JWT_SECRET", "test-secret-DO-NOT-USE-IN-PRODUCTION")


@pytest.fixture(scope="session")
def jwt_algorithm() -> str:
    """JWT algorithm for test tokens"""
    return os.getenv("JWT_ALGORITHM", "HS256")


# ===== HEALTH CHECK FIXTURES =====

async def wait_for_service(url: str, timeout: int = 60, interval: int = 2) -> bool:
    """
    Wait for a service to become healthy.

    Args:
        url: Service health check URL
        timeout: Maximum wait time in seconds
        interval: Check interval in seconds

    Returns:
        True if service is healthy, False otherwise
    """
    start_time = time.time()

    async with httpx.AsyncClient(timeout=5.0) as client:
        while time.time() - start_time < timeout:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return True
            except (httpx.ConnectError, httpx.TimeoutException):
                pass

            await asyncio.sleep(interval)

    return False


@pytest.fixture(scope="session")
async def wait_for_services(service_urls: Dict[str, str]) -> None:
    """
    Wait for all services to be healthy before running tests.

    This fixture runs once per test session and blocks until all
    services are responding to health checks.
    """
    health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", "60"))

    print("\n🔍 Waiting for services to become healthy...")

    services_to_check = {
        "BIA": f"{service_urls['bia']}/health",
        "Planning": f"{service_urls['planning']}/health",
        "Plans": f"{service_urls['plans']}/health",
        "Compliance": f"{service_urls['compliance']}/health",
    }

    for service_name, health_url in services_to_check.items():
        print(f"   Checking {service_name} at {health_url}...")

        is_healthy = await wait_for_service(health_url, timeout=health_check_timeout)

        if not is_healthy:
            pytest.fail(f"❌ {service_name} service failed to become healthy within {health_check_timeout}s")

        print(f"   ✅ {service_name} is healthy")

    print("✅ All services are healthy!\n")


# ===== AUTHENTICATION FIXTURES =====

@pytest.fixture
def create_jwt_token(jwt_secret: str, jwt_algorithm: str):
    """
    Factory fixture to create JWT tokens for testing.

    Returns a function that creates tokens with custom claims.
    """
    def _create_token(
        user_id: str = "test-user-123",
        tenant_id: str = "test-tenant-456",
        email: str = "test@example.com",
        roles: List[str] = None,
        expires_in_minutes: int = 60
    ) -> str:
        """
        Create a JWT token for testing.

        Args:
            user_id: User identifier
            tenant_id: Tenant identifier for multi-tenancy
            email: User email
            roles: List of user roles
            expires_in_minutes: Token expiration time

        Returns:
            Encoded JWT token
        """
        if roles is None:
            roles = ["bcm_user"]

        payload = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "email": email,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            "iat": datetime.utcnow(),
        }

        return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)

    return _create_token


@pytest.fixture
def auth_headers(create_jwt_token):
    """
    Create authentication headers for API requests.

    Returns headers dict with Authorization bearer token.
    """
    token = create_jwt_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def auth_headers_tenant_a(create_jwt_token):
    """Auth headers for Tenant A user"""
    token = create_jwt_token(
        user_id="user-a",
        tenant_id="tenant-a",
        email="usera@example.com",
        roles=["bcm_user", "bcm_manager"]
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def auth_headers_tenant_b(create_jwt_token):
    """Auth headers for Tenant B user"""
    token = create_jwt_token(
        user_id="user-b",
        tenant_id="tenant-b",
        email="userb@example.com",
        roles=["bcm_user"]
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def admin_auth_headers(create_jwt_token):
    """Auth headers for admin user with all permissions"""
    token = create_jwt_token(
        user_id="admin-user",
        tenant_id="test-tenant",
        email="admin@example.com",
        roles=["bcm_admin", "bcm_manager", "bcm_user"]
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# ===== HTTP CLIENT FIXTURES =====

@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Async HTTP client for making API requests.

    Configured with reasonable timeouts for integration tests.
    """
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=10.0),
        follow_redirects=True
    ) as client:
        yield client


# ===== TEST DATA CLEANUP FIXTURES =====

@pytest.fixture
async def cleanup_test_data(http_client: httpx.AsyncClient, service_urls: Dict[str, str], admin_auth_headers: Dict[str, str]):
    """
    Cleanup test data after each test.

    This is a yielding fixture that provides cleanup after test execution.
    Stores resource IDs created during test and deletes them afterwards.
    """
    created_resources = {
        "bia_processes": [],
        "strategies": [],
        "plans": [],
        "audits": [],
        "nonconformities": [],
    }

    # Yield control to test
    yield created_resources

    # Cleanup after test
    print("\n🧹 Cleaning up test data...")

    # Delete Plans
    for plan_id in created_resources.get("plans", []):
        try:
            await http_client.delete(
                f"{service_urls['plans']}/api/plans/plans/{plan_id}",
                headers=admin_auth_headers
            )
        except Exception as e:
            print(f"   ⚠️ Failed to delete plan {plan_id}: {e}")

    # Delete Strategies
    for strategy_id in created_resources.get("strategies", []):
        try:
            await http_client.delete(
                f"{service_urls['planning']}/api/strategies/{strategy_id}",
                headers=admin_auth_headers
            )
        except Exception as e:
            print(f"   ⚠️ Failed to delete strategy {strategy_id}: {e}")

    # Delete BIA Processes
    for process_id in created_resources.get("bia_processes", []):
        try:
            await http_client.delete(
                f"{service_urls['bia']}/processes/{process_id}",
                headers=admin_auth_headers
            )
        except Exception as e:
            print(f"   ⚠️ Failed to delete BIA process {process_id}: {e}")

    # Delete Nonconformities
    for nc_id in created_resources.get("nonconformities", []):
        try:
            await http_client.delete(
                f"{service_urls['compliance']}/api/nonconformities/{nc_id}",
                headers=admin_auth_headers
            )
        except Exception as e:
            print(f"   ⚠️ Failed to delete NC {nc_id}: {e}")

    # Delete Audits
    for audit_id in created_resources.get("audits", []):
        try:
            await http_client.delete(
                f"{service_urls['compliance']}/api/audit/audits/{audit_id}",
                headers=admin_auth_headers
            )
        except Exception as e:
            print(f"   ⚠️ Failed to delete audit {audit_id}: {e}")

    print("✅ Cleanup complete\n")


# ===== EVENTBUS HELPER FIXTURES =====

@pytest.fixture
async def eventbus_helper(http_client: httpx.AsyncClient, service_urls: Dict[str, str]):
    """
    Helper for EventBus operations in tests.

    Provides methods to publish events and check event delivery.
    """
    class EventBusHelper:
        def __init__(self, client: httpx.AsyncClient, eventbus_url: str):
            self.client = client
            self.eventbus_url = eventbus_url

        async def publish_event(self, event_type: str, payload: dict, tenant_id: str = "test-tenant"):
            """Publish an event to the EventBus"""
            event_data = {
                "event_type": event_type,
                "payload": payload,
                "tenant_id": tenant_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

            try:
                response = await self.client.post(
                    f"{self.eventbus_url}/publish",
                    json=event_data,
                    timeout=5.0
                )
                return response.status_code == 200
            except Exception as e:
                print(f"Failed to publish event: {e}")
                return False

        async def get_events(self, topic: str = None, limit: int = 100):
            """Retrieve events from EventBus (for verification)"""
            try:
                params = {"limit": limit}
                if topic:
                    params["topic"] = topic

                response = await self.client.get(
                    f"{self.eventbus_url}/events",
                    params=params,
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                return []
            except Exception as e:
                print(f"Failed to get events: {e}")
                return []

    return EventBusHelper(http_client, service_urls["eventbus"])


# ===== RETRY HELPER =====

@pytest.fixture
def retry_async():
    """
    Retry helper for flaky operations in integration tests.

    Returns an async function that retries operations with exponential backoff.
    """
    async def _retry(
        func,
        max_attempts: int = 3,
        initial_delay: float = 0.5,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Retry an async function with exponential backoff.

        Args:
            func: Async function to retry
            max_attempts: Maximum number of attempts
            initial_delay: Initial delay between retries in seconds
            backoff_factor: Multiplier for delay after each attempt
            exceptions: Tuple of exceptions to catch and retry

        Returns:
            Result of successful function call

        Raises:
            Last exception if all retries fail
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(max_attempts):
            try:
                return await func()
            except exceptions as e:
                last_exception = e

                if attempt < max_attempts - 1:
                    print(f"   ⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor

        raise last_exception

    return _retry


# ===== PYTEST CONFIGURATION =====

def pytest_configure(config):
    """
    Pytest configuration hook.

    Registers custom markers and configurations.
    """
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring all services"
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running tests (> 5s)"
    )
    config.addinivalue_line(
        "markers", "requires_docker: Tests requiring Docker"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.

    Adds 'integration' marker to all tests in integration-tests directory.
    """
    for item in items:
        # Add integration marker to all tests
        if "integration-tests" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.requires_docker)
