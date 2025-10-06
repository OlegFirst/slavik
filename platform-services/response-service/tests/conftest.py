"""
Response Module - Pytest Configuration and Shared Fixtures
ISO 22301:2019 Clause 8.4 - Incident Response

Shared test fixtures for all test modules
"""

import pytest
import asyncio
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, Mock
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from models.database import Base
from models.domain import (
    IncidentCreate, IncidentUpdate, IncidentSeverity, IncidentStatus, IncidentType,
    ResponseActionCreate, ResponseActionUpdate, ActionStatus, ActionPriority,
    ResponseTeamCreate, ResponseTeamMemberCreate, TeamMemberRole,
    CommunicationLogCreate, CommunicationType,
    RecoveryMetricsCreate, RecoveryMetricsUpdate
)


# ============================================================================
# Pytest Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
async def test_db_engine():
    """Create in-memory SQLite database engine for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_db_session():
    """Create mock database session"""
    session = AsyncMock(spec=AsyncSession)
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()
    return session


# ============================================================================
# ID Fixtures
# ============================================================================

@pytest.fixture
def org_id() -> UUID:
    """Standard organization ID for testing"""
    return uuid4()


@pytest.fixture
def user_id() -> UUID:
    """Standard user ID for testing"""
    return uuid4()


@pytest.fixture
def incident_id() -> UUID:
    """Standard incident ID for testing"""
    return uuid4()


@pytest.fixture
def team_id() -> UUID:
    """Standard team ID for testing"""
    return uuid4()


@pytest.fixture
def action_id() -> UUID:
    """Standard action ID for testing"""
    return uuid4()


# ============================================================================
# Domain Model Fixtures
# ============================================================================

@pytest.fixture
def sample_incident_create() -> IncidentCreate:
    """Sample incident create data"""
    return IncidentCreate(
        title="Critical System Outage",
        description="Production database server is down",
        incident_type=IncidentType.SYSTEM_FAILURE,
        severity=IncidentSeverity.CRITICAL,
        affected_systems=["database-prod-01", "api-gateway"],
        affected_locations=["us-east-1", "eu-west-1"],
        estimated_impact="All customer transactions affected",
        detected_by="Monitoring System",
        detected_at=datetime.utcnow(),
        tags=["production", "database", "critical"]
    )


@pytest.fixture
def sample_incident_update() -> IncidentUpdate:
    """Sample incident update data"""
    return IncidentUpdate(
        title="Updated: Critical System Outage",
        description="Production database server restored",
        status=IncidentStatus.RESOLVED,
        root_cause="Hardware failure on primary DB server",
        lessons_learned="Implement automatic failover to standby server"
    )


@pytest.fixture
def sample_action_create() -> ResponseActionCreate:
    """Sample response action create data"""
    return ResponseActionCreate(
        title="Restart database service",
        description="Attempt to restart the database service on primary server",
        action_type="recovery",
        priority=ActionPriority.URGENT,
        assigned_to=uuid4(),
        assigned_to_name="John Doe",
        due_date=datetime.utcnow(),
        estimated_hours=2.0,
        checklist=["Check server status", "Verify connections", "Restart service"]
    )


@pytest.fixture
def sample_action_update() -> ResponseActionUpdate:
    """Sample response action update data"""
    return ResponseActionUpdate(
        status=ActionStatus.COMPLETED,
        completion_notes="Database service successfully restarted",
        actual_hours=1.5
    )


@pytest.fixture
def sample_team_create() -> ResponseTeamCreate:
    """Sample response team create data"""
    return ResponseTeamCreate(
        name="Critical Incident Response Team",
        description="Primary team for critical incidents",
        is_active=True,
        activation_criteria={"severity": ["critical", "high"]},
        escalation_procedures={"level_1": "Notify manager", "level_2": "Notify executive"},
        members=[
            ResponseTeamMemberCreate(
                user_id=uuid4(),
                role=TeamMemberRole.INCIDENT_MANAGER,
                name="Jane Smith",
                email="jane.smith@example.com",
                phone="+1-555-0001",
                is_primary=True,
                availability_status="available"
            ),
            ResponseTeamMemberCreate(
                user_id=uuid4(),
                role=TeamMemberRole.TECHNICAL_LEAD,
                name="Bob Johnson",
                email="bob.johnson@example.com",
                phone="+1-555-0002",
                is_primary=False,
                availability_status="available"
            )
        ]
    )


@pytest.fixture
def sample_communication_create() -> CommunicationLogCreate:
    """Sample communication log create data"""
    return CommunicationLogCreate(
        communication_type=CommunicationType.EMAIL,
        subject="Incident Update: Critical System Outage",
        content="The database has been restored and services are operational",
        sender="incident.response@example.com",
        recipients=["stakeholder1@example.com", "stakeholder2@example.com"],
        cc_recipients=["management@example.com"],
        channel="email",
        is_stakeholder_notification=True,
        metadata={"incident_status": "resolved"}
    )


@pytest.fixture
def sample_metrics_create() -> RecoveryMetricsCreate:
    """Sample recovery metrics create data"""
    return RecoveryMetricsCreate(
        service_name="Production Database",
        target_rto_hours=4.0,
        target_rpo_hours=1.0,
        actual_rto_hours=3.5,
        actual_rpo_hours=0.5,
        downtime_start=datetime.utcnow(),
        downtime_end=datetime.utcnow(),
        impact_description="Complete service outage affecting all transactions",
        recovery_actions=["Failover to standby", "Restore from backup"]
    )


@pytest.fixture
def sample_metrics_update() -> RecoveryMetricsUpdate:
    """Sample recovery metrics update data"""
    return RecoveryMetricsUpdate(
        actual_rto_hours=4.2,
        actual_rpo_hours=1.2,
        impact_description="Updated: Service restored with minimal data loss"
    )


# ============================================================================
# Mock Event Publisher Fixtures
# ============================================================================

@pytest.fixture
def mock_event_publisher():
    """Create mock event publisher"""
    publisher = AsyncMock()
    publisher.enabled = False
    publisher.broker_connected = False
    publisher.publish_incident_created = AsyncMock()
    publisher.publish_incident_updated = AsyncMock()
    publisher.publish_incident_status_changed = AsyncMock()
    publisher.publish_incident_resolved = AsyncMock()
    publisher.publish_incident_closed = AsyncMock()
    publisher.publish_incident_escalated = AsyncMock()
    publisher.publish_stakeholder_notification = AsyncMock()
    publisher.publish_metrics_updated = AsyncMock()
    publisher.publish_compliance_violation = AsyncMock()
    publisher.connect = AsyncMock()
    publisher.disconnect = AsyncMock()
    return publisher


# ============================================================================
# Mock RabbitMQ Fixtures
# ============================================================================

@pytest.fixture
def mock_rabbitmq_connection():
    """Create mock RabbitMQ connection"""
    connection = AsyncMock()
    connection.is_closed = False
    connection.close = AsyncMock()
    return connection


@pytest.fixture
def mock_rabbitmq_channel():
    """Create mock RabbitMQ channel"""
    channel = AsyncMock()
    channel.is_closed = False
    channel.close = AsyncMock()
    channel.set_qos = AsyncMock()
    channel.declare_exchange = AsyncMock()
    channel.declare_queue = AsyncMock()
    return channel


@pytest.fixture
def mock_rabbitmq_exchange():
    """Create mock RabbitMQ exchange"""
    exchange = AsyncMock()
    exchange.publish = AsyncMock()
    return exchange


@pytest.fixture
def mock_rabbitmq_queue():
    """Create mock RabbitMQ queue"""
    queue = AsyncMock()
    queue.bind = AsyncMock()
    queue.consume = AsyncMock()
    return queue


# ============================================================================
# Mock User Fixtures (for API testing)
# ============================================================================

@pytest.fixture
def mock_user(org_id, user_id):
    """Create mock authenticated user"""
    user = Mock()
    user.user_id = str(user_id)
    user.tenant_id = str(org_id)
    user.email = "test@example.com"
    user.username = "testuser"
    return user


# ============================================================================
# Test Data Helpers
# ============================================================================

@pytest.fixture
def incident_number_generator():
    """Generate incident numbers for testing"""
    counter = 0

    def generate(org_id: UUID) -> str:
        nonlocal counter
        counter += 1
        year = datetime.utcnow().year
        org_prefix = str(org_id)[:8].upper()
        return f"INC-{year}-{org_prefix}-{counter:04d}"

    return generate
