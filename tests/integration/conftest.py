"""
Fixtures for integration tests
Uses real runtime infrastructure
"""
import pytest
import asyncio
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def real_eventbus():
    """Real EventBus instance (Memory backend)"""
    from infrastructure.runtime.eventbus.factory import create_event_bus

    bus = create_event_bus(backend="memory")
    yield bus
    # Cleanup
    await bus.close() if hasattr(bus, 'close') else None


@pytest.fixture
async def redis_eventbus():
    """EventBus with Redis backend (if Redis is running)"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    try:
        from infrastructure.runtime.eventbus.factory import create_event_bus

        bus = create_event_bus(
            backend="redis",
            redis_url=redis_url
        )
        yield bus
        await bus.close()
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")


@pytest.fixture
async def rabbitmq_manager():
    """RabbitMQ Manager (if RabbitMQ is running)"""
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    try:
        from infrastructure.runtime.message_queue.rabbitmq_manager import RabbitMQManager

        mq = RabbitMQManager(url=rabbitmq_url)
        await mq.connect()
        yield mq
        await mq.disconnect()
    except Exception as e:
        pytest.skip(f"RabbitMQ not available: {e}")


@pytest.fixture
async def service_registry():
    """Service Discovery Registry"""
    from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

    registry = ServiceRegistry()
    yield registry
    # Cleanup registered services
    await registry.cleanup()


@pytest.fixture
async def test_db_session():
    """Test database session (PostgreSQL)"""
    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://localhost/test_ai_platform"
    )

    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        engine = create_async_engine(db_url, echo=False)

        async_session = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_session() as session:
            # Start transaction
            async with session.begin():
                yield session
                # Rollback after test
                await session.rollback()

        await engine.dispose()

    except Exception as e:
        pytest.skip(f"Test database not available: {e}")


@pytest.fixture
def sample_workflow_context():
    """Sample workflow context for testing"""
    from intelligent_core.workflow_intelligence.core.workflow_engine import WorkflowContext

    return WorkflowContext(
        workflow_id="integration-test-001",
        tenant_id="test-tenant-healthcare",
        module="bia",
        data={
            "organization_id": "org-healthcare-123",
            "industry": "healthcare",
            "analysis_type": "full_bia",
            "processes": [
                {
                    "name": "Patient Registration",
                    "criticality": "high",
                    "rto": "4h",
                    "rpo": "1h"
                },
                {
                    "name": "Emergency Response",
                    "criticality": "critical",
                    "rto": "1h",
                    "rpo": "15m"
                }
            ]
        }
    )


@pytest.fixture
def sample_bia_input():
    """Sample BIA workflow input"""
    return {
        "tenant_id": "test-tenant",
        "organization_id": "org-123",
        "organization_name": "Test Healthcare Organization",
        "industry": "healthcare",
        "analysis_scope": "critical_processes",
        "timeframe": "2024-2025",
        "processes": [
            {
                "id": "proc-001",
                "name": "Patient Care",
                "department": "Clinical",
                "criticality": "critical",
                "current_rto": None,
                "current_rpo": None
            },
            {
                "id": "proc-002",
                "name": "Lab Services",
                "department": "Laboratory",
                "criticality": "high",
                "current_rto": None,
                "current_rpo": None
            }
        ],
        "dependencies": [],
        "resources": []
    }


@pytest.fixture
def sample_risk_input():
    """Sample Risk Assessment input"""
    return {
        "tenant_id": "test-tenant",
        "organization_id": "org-123",
        "risk_type": "operational",
        "scope": "it_infrastructure",
        "threats": [
            {
                "id": "threat-001",
                "name": "Ransomware Attack",
                "category": "cyber",
                "likelihood": "medium"
            },
            {
                "id": "threat-002",
                "name": "Data Center Failure",
                "category": "infrastructure",
                "likelihood": "low"
            }
        ],
        "assets": [
            {
                "id": "asset-001",
                "name": "Patient Database",
                "value": "critical",
                "location": "primary_dc"
            }
        ]
    }


@pytest.fixture
async def real_workflow_engine(real_eventbus, test_db_session):
    """Real WorkflowEngine with all dependencies"""
    from intelligent_core.workflow_intelligence.core.workflow_engine import WorkflowEngine
    from intelligent_core.workflow_intelligence.storage.postgres_adapter import PostgresStorageAdapter

    storage = PostgresStorageAdapter(session=test_db_session)

    engine = WorkflowEngine(
        storage=storage,
        event_bus=real_eventbus
    )

    yield engine


@pytest.fixture
def mock_llm_responses():
    """Mock LLM responses for integration tests"""
    return {
        "bia_process_identification": {
            "processes": [
                {
                    "name": "Patient Registration",
                    "criticality": "high",
                    "rto": "4h",
                    "rpo": "1h",
                    "dependencies": ["EHR System", "Identity Verification"]
                },
                {
                    "name": "Emergency Response",
                    "criticality": "critical",
                    "rto": "1h",
                    "rpo": "15m",
                    "dependencies": ["Communication System", "Medical Supplies"]
                }
            ]
        },
        "risk_assessment": {
            "threats": [
                {
                    "name": "Ransomware Attack",
                    "likelihood": "medium",
                    "impact": "high",
                    "risk_score": 7.5
                }
            ],
            "recommendations": [
                "Implement regular backups",
                "Deploy EDR solution",
                "Conduct security training"
            ]
        }
    }


# Markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: Integration tests with real infrastructure"
    )
    config.addinivalue_line(
        "markers",
        "requires_redis: Tests requiring Redis"
    )
    config.addinivalue_line(
        "markers",
        "requires_rabbitmq: Tests requiring RabbitMQ"
    )
    config.addinivalue_line(
        "markers",
        "requires_db: Tests requiring PostgreSQL"
    )
    config.addinivalue_line(
        "markers",
        "slow: Slow running tests"
    )
