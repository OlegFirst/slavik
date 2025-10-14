"""Pytest configuration and fixtures for Workflow Intelligence tests"""

import pytest
import asyncio
import os
from typing import AsyncGenerator
from workflow_intelligence.storage.postgres_adapter import PostgresStorageAdapter


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def database_url() -> str:
    """Get test database URL from environment"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/test_bcm"
    )


@pytest.fixture
async def storage(database_url: str) -> AsyncGenerator[PostgresStorageAdapter, None]:
    """Create PostgresStorageAdapter for testing"""
    adapter = PostgresStorageAdapter(database_url)
    await adapter.connect()

    # Clean up test data before each test
    async with adapter.pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE workflow_intelligence.workflow_contexts CASCADE")
        await conn.execute("TRUNCATE TABLE workflow_intelligence.workflow_cases CASCADE")
        await conn.execute("TRUNCATE TABLE workflow_intelligence.benchmarks CASCADE")
        await conn.execute("TRUNCATE TABLE workflow_intelligence.ml_predictions CASCADE")

    yield adapter

    # Clean up after test
    async with adapter.pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE workflow_intelligence.workflow_contexts CASCADE")
        await conn.execute("TRUNCATE TABLE workflow_intelligence.workflow_cases CASCADE")
        await conn.execute("TRUNCATE TABLE workflow_intelligence.benchmarks CASCADE")
        await conn.execute("TRUNCATE TABLE workflow_intelligence.ml_predictions CASCADE")

    await adapter.close()


@pytest.fixture
def sample_workflow_context():
    """Sample workflow context for testing"""
    return {
        "workflow_id": "test-workflow-001",
        "module": "planning",
        "tenant_id": "tenant-test",
        "current_stage": "draft",
        "data": {
            "strategy_type": "FAST_RECOVERY",
            "target_rto_hours": 2,
            "estimated_cost": 500000
        },
        "available_actions": ["submit_review", "update_costs"],
        "gaps": []
    }


@pytest.fixture
def sample_case_data():
    """Sample completed case for testing"""
    return {
        "workflow_id": "completed-workflow-001",
        "module": "planning",
        "industry": "healthcare",
        "org_size": "medium",
        "total_duration_days": 18,
        "stages_completed": ["draft", "review", "approved"],
        "success": True,
        "challenges": ["budget_constraints"],
        "best_practices": ["early_stakeholder_engagement"]
    }


@pytest.fixture
def malicious_sql_injections():
    """Common SQL injection attack patterns for testing"""
    return [
        "'; DROP TABLE workflow_contexts; --",
        "' OR '1'='1",
        "'; DELETE FROM workflow_cases WHERE '1'='1'; --",
        "' UNION SELECT null, null, null, null; --",
        "admin'--",
        "' OR '1'='1' --",
        "'; UPDATE workflow_contexts SET tenant_id='hacker'; --",
        "1' UNION SELECT password FROM users; --",
        "'; EXEC sp_MSForEachTable 'DROP TABLE ?'; --"
    ]


@pytest.fixture
def sample_org_context():
    """Sample organization context for testing"""
    return {
        "industry": "healthcare",
        "size": "medium",
        "maturity_level": "basic"
    }


@pytest.fixture
def sample_prediction():
    """Sample ML prediction for testing"""
    return {
        "success_probability": 0.85,
        "estimated_duration_days": 14,
        "risk_level": "medium",
        "risk_factors": ["limited_resources", "tight_timeline"],
        "model_version": "v1.0"
    }
