"""
Global pytest configuration
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def tenant_id():
    """Default tenant ID for tests"""
    return "test-tenant-123"


@pytest.fixture
def user_id():
    """Default user ID for tests"""
    return "test-user-456"
