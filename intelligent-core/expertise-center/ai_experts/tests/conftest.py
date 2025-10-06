"""
Pytest Configuration and Fixtures
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
def mock_context():
    """Mock workflow context"""
    return {
        'industry': 'healthcare',
        'size': 'medium',
        'module': 'BIA',
        'current_stage': 'identify_processes',
        'progress': 30,
        'maturity': 3
    }


@pytest.fixture
def mock_org_context():
    """Mock organization context"""
    return {
        'size': 'medium',
        'maturity': 3,
        'industry': 'healthcare'
    }


@pytest.fixture
def mock_workflow_data():
    """Mock workflow data"""
    return {
        'org_size': 'medium',
        'org_maturity': 3,
        'industry': 'healthcare',
        'current_stage': 'bia',
        'duration_hours': 16,
        'days_in_current_stage': 5,
        'days_since_last_activity': 1
    }
