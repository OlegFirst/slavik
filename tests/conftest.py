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
