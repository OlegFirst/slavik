"""
Pytest configuration and fixtures for expertise-center tests
"""

import pytest
import httpx
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Create async HTTP client for tests"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
def base_url():
    """Base URL for expertise-center service"""
    return "http://localhost:8035"


@pytest.fixture
def sample_context():
    """Sample context for test requests"""
    return {
        "industry": "finance",
        "organization_size": "medium",
        "organization_id": "test-org-001"
    }


@pytest.fixture
def sample_expert_request(sample_context):
    """Sample expert request"""
    return {
        "query": "Test query for expert",
        "context": sample_context,
        "organization_id": "test-org-001"
    }
