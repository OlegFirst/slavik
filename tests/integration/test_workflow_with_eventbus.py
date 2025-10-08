"""
Integration tests for workflow_intelligence with EventBus
Uses real runtime infrastructure
"""
import pytest
import asyncio
from pathlib import Path
import sys

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infrastructure.runtime.eventbus.factory import create_event_bus
from infrastructure.runtime.eventbus.core.events import Event
from intelligent_core.workflow_intelligence.core.workflow_engine import WorkflowEngine, WorkflowContext


@pytest.fixture
async def eventbus():
    """Real EventBus instance (Memory backend for tests)"""
    bus = create_event_bus(backend="memory")
    yield bus
    # Cleanup if needed


@pytest.fixture
async def workflow_engine(eventbus):
    """Real WorkflowEngine with EventBus"""
    from intelligent_core.workflow_intelligence.storage.postgres_adapter import PostgresStorageAdapter

    # Use in-memory storage for tests (or test DB)
    storage = PostgresStorageAdapter(connection_string="sqlite:///:memory:")

    engine = WorkflowEngine(
        storage=storage,
        event_bus=eventbus
    )

    return engine


@pytest.mark.asyncio
@pytest.mark.integration
class TestWorkflowEngineWithEventBus:
    """Integration tests using real EventBus"""

    async def test_workflow_publishes_events_to_eventbus(self, workflow_engine, eventbus):
        """Test that workflow publishes events to real EventBus"""
        # ARRANGE
        events_received = []

        async def event_handler(event: Event):
            events_received.append(event)

        # Subscribe to workflow events
        await eventbus.subscribe("workflow.*", event_handler)

        context = WorkflowContext(
            workflow_id="test-workflow-001",
            tenant_id="test-tenant",
            module="bia",
            data={"test": "data"}
        )

        # ACT
        await workflow_engine.start_workflow(context)

        # Give eventbus time to process
        await asyncio.sleep(0.1)

        # ASSERT
        assert len(events_received) > 0
        assert events_received[0].topic.startswith("workflow.")
        assert events_received[0].payload["workflow_id"] == "test-workflow-001"


    async def test_workflow_transitions_trigger_events(self, workflow_engine, eventbus):
        """Test state transitions publish events"""
        # ARRANGE
        state_events = []

        async def state_handler(event: Event):
            if "state_transition" in event.topic:
                state_events.append(event)

        await eventbus.subscribe("workflow.state_transition", state_handler)

        context = WorkflowContext(
            workflow_id="test-workflow-002",
            tenant_id="test-tenant",
            module="bia"
        )

        # ACT
        await workflow_engine.start_workflow(context)
        await workflow_engine.transition_to("analyzing", context)

        await asyncio.sleep(0.1)

        # ASSERT
        assert len(state_events) >= 1
        transitions = [e.payload.get("to_state") for e in state_events]
        assert "analyzing" in transitions


@pytest.mark.asyncio
@pytest.mark.integration
class TestBIAWorkflowWithRealInfrastructure:
    """Integration tests for BIA workflow with real services"""

    async def test_bia_workflow_end_to_end(self, eventbus):
        """Complete BIA workflow with EventBus integration"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            BIAWorkflow,
            bia_activity_identify_processes
        )

        events = []
        async def collect_events(event: Event):
            events.append(event)

        await eventbus.subscribe("bia.*", collect_events)

        # Mock input data (would come from real source)
        input_data = {
            "tenant_id": "healthcare-org-001",
            "organization_id": "org-123",
            "industry": "healthcare",
            "analysis_scope": "critical_processes"
        }

        # ACT
        result = await bia_activity_identify_processes(input_data)

        await asyncio.sleep(0.1)

        # ASSERT
        assert result is not None
        assert "processes" in result or "status" in result

        # Check events were published
        assert len(events) > 0
        bia_events = [e for e in events if e.topic.startswith("bia.")]
        assert len(bia_events) > 0


@pytest.mark.asyncio
@pytest.mark.integration
class TestWorkflowWithServiceDiscovery:
    """Integration tests with Service Discovery"""

    async def test_workflow_registers_with_service_discovery(self):
        """Test workflow engine registers in service discovery"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        # Register workflow service
        service_info = {
            "name": "workflow-intelligence",
            "host": "localhost",
            "port": 8001,
            "iso_clause": "8.4",
            "health_check": "http://localhost:8001/health"
        }

        # ACT
        await registry.register(service_info)

        # Query service
        services = await registry.discover("workflow-intelligence")

        # ASSERT
        assert len(services) > 0
        assert services[0]["name"] == "workflow-intelligence"
        assert services[0]["iso_clause"] == "8.4"


@pytest.mark.asyncio
@pytest.mark.integration
class TestWorkflowWithRabbitMQ:
    """Integration tests with RabbitMQ (if available)"""

    @pytest.mark.skipif(
        not Path("/usr/local/bin/rabbitmq-server").exists(),
        reason="RabbitMQ not installed"
    )
    async def test_workflow_publishes_to_rabbitmq(self):
        """Test workflow publishes to RabbitMQ queue"""
        # ARRANGE
        from infrastructure.runtime.message_queue.rabbitmq_manager import RabbitMQManager

        mq = RabbitMQManager(url="amqp://guest:guest@localhost:5672/")
        await mq.connect()

        messages_received = []

        async def message_handler(message):
            messages_received.append(message)

        await mq.subscribe("workflow.tasks", message_handler)

        # ACT
        await mq.publish("workflow.tasks", {
            "task": "bia_analysis",
            "workflow_id": "test-001",
            "data": {"test": "data"}
        })

        await asyncio.sleep(0.2)

        # ASSERT
        assert len(messages_received) > 0
        assert messages_received[0]["task"] == "bia_analysis"

        await mq.disconnect()


@pytest.mark.asyncio
@pytest.mark.integration
class TestWorkflowWithRealDatabase:
    """Integration tests with real PostgreSQL (test DB)"""

    @pytest.fixture
    async def test_db_connection(self):
        """Connection to test database"""
        # Would use test database, not production!
        # export TEST_DATABASE_URL="postgresql://test:test@localhost:5432/test_db"
        import os

        db_url = os.getenv("TEST_DATABASE_URL", "postgresql://localhost/test_ai_platform")

        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        engine = create_async_engine(db_url, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            yield session

        await engine.dispose()


    async def test_workflow_persists_to_real_database(self, test_db_connection):
        """Test workflow state is persisted to real PostgreSQL"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.storage.postgres_adapter import PostgresStorageAdapter

        storage = PostgresStorageAdapter(session=test_db_connection)

        context = WorkflowContext(
            workflow_id="db-test-001",
            tenant_id="test-tenant",
            module="bia",
            data={"test": "real database"}
        )

        # ACT
        await storage.save_context(context)

        # Retrieve from DB
        retrieved = await storage.load_context("db-test-001")

        # ASSERT
        assert retrieved is not None
        assert retrieved.workflow_id == "db-test-001"
        assert retrieved.data["test"] == "real database"


# Helper to run all integration tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
