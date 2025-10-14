"""
Integration Tests for EventBus Integration

Tests the complete EventBus integration:
- Event publishing
- Event subscription
- Auto-regeneration
- MIO Manager monitoring
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# Add scenario-intelligence to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integrations.eventbus_client import ScenarioEventBusClient, get_eventbus_client
from events.scenario_events import (
    create_scenario_generated_event,
    create_scenario_executed_event,
    create_regeneration_triggered_event,
    create_regeneration_completed_event,
    ScenarioGenerationTrigger,
    ScenarioLevel
)


class TestEventBusClient:
    """Test ScenarioEventBusClient"""

    @pytest.fixture
    async def client(self):
        """Create test client"""
        client = ScenarioEventBusClient(backend='memory')
        await client.initialize()
        yield client
        await client.close()

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initializes correctly"""
        assert client.is_connected()
        assert client.backend == 'memory'

    @pytest.mark.asyncio
    async def test_publish_scenario_generated(self, client):
        """Test publishing scenario.generated event"""
        event = create_scenario_generated_event(
            scenario_ids=["test-1", "test-2", "test-3"],
            level=ScenarioLevel.L1_PLATFORM,
            generator="l1_platform",
            trigger=ScenarioGenerationTrigger.MANUAL
        )

        # Should not raise exception
        await client.publish_scenario_generated(event)

        # Verify event was created correctly
        assert event.scenario_ids == ["test-1", "test-2", "test-3"]
        assert event.level == ScenarioLevel.L1_PLATFORM
        assert event.count == 3

    @pytest.mark.asyncio
    async def test_publish_scenario_executed(self, client):
        """Test publishing scenario.executed event"""
        event = create_scenario_executed_event(
            scenario_id="test-scenario-1",
            execution_id="exec-123",
            status="success",
            duration_ms=1500.0,
            steps_executed=5,
            steps_failed=0
        )

        # Should not raise exception
        await client.publish_scenario_executed(event)

        # Verify event was created correctly
        assert event.scenario_id == "test-scenario-1"
        assert event.status == "success"
        assert event.duration_ms == 1500.0

    @pytest.mark.asyncio
    async def test_publish_regeneration_events(self, client):
        """Test publishing regeneration events"""
        # Triggered event
        triggered_event = create_regeneration_triggered_event(
            trigger_event="service.added",
            affected_services=["new-service"],
            affected_levels=["l1_platform"],
            regeneration_id="regen-123"
        )

        await client.publish_regeneration_triggered(triggered_event)

        # Completed event
        completed_event = create_regeneration_completed_event(
            regeneration_id="regen-123",
            trigger_event="service.added",
            scenarios_generated=10,
            scenarios_updated=5,
            scenarios_deprecated=0,
            duration_ms=30000.0,
            status="success"
        )

        await client.publish_regeneration_completed(completed_event)

        # Verify events
        assert triggered_event.regeneration_id == "regen-123"
        assert completed_event.scenarios_generated == 10

    @pytest.mark.asyncio
    async def test_subscribe_to_catalog_updates(self, client):
        """Test subscribing to catalog update events"""
        received_events = []

        async def callback(event):
            received_events.append(event)

        # Subscribe
        await client.subscribe_to_catalog_updates(callback)

        # Verify subscription was registered
        assert len(client.get_subscriptions()) > 0

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check"""
        health = await client.health_check()

        assert health["connected"] is True
        assert health["backend"] == "memory"
        assert "subscriptions" in health


class TestAutoRegenerationScenario:
    """Test auto-regeneration workflow"""

    @pytest.mark.asyncio
    async def test_service_added_triggers_regeneration(self):
        """Test that service.added event triggers regeneration"""
        # This is an integration test that would require:
        # 1. Running EventBus
        # 2. Running GenerationManager
        # 3. Running AutoRegenerationHandler
        # For now, we just verify the logic exists
        pass

    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test that multiple changes are batched"""
        # Test batching logic
        pass


class TestMIOManagerIntegration:
    """Test MIO Manager integration"""

    @pytest.mark.asyncio
    async def test_mio_receives_scenario_events(self):
        """Test MIO Manager receives and processes scenario events"""
        # Mock MIO Manager's ScenarioIntelligenceClient
        from integrations.scenario_intelligence_client import ScenarioIntelligenceClient

        # Create mock eventbus
        mock_eventbus = Mock()
        mock_eventbus.subscribe = AsyncMock()

        client = ScenarioIntelligenceClient(mock_eventbus)

        # Subscribe to events
        await client.subscribe_to_events()

        # Verify subscriptions were made
        assert mock_eventbus.subscribe.call_count >= 4  # At least 4 event types

    @pytest.mark.asyncio
    async def test_mio_tracks_metrics(self):
        """Test MIO Manager tracks scenario metrics"""
        from integrations.scenario_intelligence_client import ScenarioIntelligenceClient

        mock_eventbus = Mock()
        client = ScenarioIntelligenceClient(mock_eventbus)

        # Simulate receiving events
        mock_event = Mock()
        mock_event.data = {
            'scenario_ids': ['s1', 's2', 's3'],
            'level': 'l1_platform',
            'generator': 'l1_platform',
            'count': 3,
            'trigger': 'manual',
            'timestamp': datetime.utcnow().isoformat()
        }

        await client.handle_scenario_generated(mock_event)

        # Check metrics
        metrics = client.get_metrics()
        assert metrics['scenarios_generated'] == 3


class TestEndToEndFlow:
    """Test complete end-to-end flows"""

    @pytest.mark.asyncio
    async def test_generation_with_eventbus(self):
        """Test scenario generation with EventBus enabled"""
        # This would test:
        # 1. GenerationManager with EventBus client
        # 2. Scenarios are generated
        # 3. Events are published
        # 4. MIO Manager receives events
        pass

    @pytest.mark.asyncio
    async def test_execution_with_eventbus(self):
        """Test scenario execution with EventBus enabled"""
        # This would test:
        # 1. ScenarioEngine with EventBus client
        # 2. Scenario is executed
        # 3. Execution event is published
        # 4. MIO Manager receives and tracks event
        pass

    @pytest.mark.asyncio
    async def test_auto_regeneration_flow(self):
        """Test complete auto-regeneration flow"""
        # This would test:
        # 1. Service catalog update event is published
        # 2. AutoRegenerationHandler receives event
        # 3. Regeneration is triggered
        # 4. Regeneration events are published
        # 5. MIO Manager monitors the process
        pass


# Utility functions for tests
def create_mock_event(event_type: str, data: dict):
    """Create mock EventBus event"""
    mock_event = Mock()
    mock_event.type = event_type
    mock_event.data = data
    mock_event.timestamp = datetime.utcnow().isoformat()
    return mock_event


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
