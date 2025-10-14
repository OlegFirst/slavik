"""
Pytest configuration and fixtures for System BCM tests
"""

import pytest
import asyncio
import redis
from typing import AsyncGenerator
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def redis_client():
    """Redis client fixture"""
    client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

    # Test connection
    try:
        client.ping()
        yield client
    except redis.ConnectionError:
        pytest.skip("Redis not available")
    finally:
        client.close()


@pytest.fixture
def mock_scenarios():
    """Mock scenario data"""
    return {
        "platform_bia": {
            "critical_processes": [
                {
                    "process_id": "cp_001",
                    "name": "Event Bus (Redis Streams)",
                    "criticality": "tier_1_critical",
                    "rto": "30s",
                    "rpo": "0s"
                }
            ]
        },
        "platform_risks": {
            "risks": [
                {
                    "risk_id": "r_001",
                    "category": "availability",
                    "description": "EventBus connection failure",
                    "impact": 5,
                    "likelihood": 2
                }
            ]
        }
    }


@pytest.fixture
def performance_thresholds():
    """Performance test thresholds"""
    return {
        "cycle_duration_max": 30.0,  # seconds
        "cpu_usage_max": 50.0,  # percent
        "memory_usage_max": 50.0,  # percent
        "api_response_max": 1.0,  # seconds
        "recovery_rto_max": 300,  # seconds
    }
