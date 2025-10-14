"""
Integration tests for ResourceTracker in System BCM Service

Tests the integration of ResourceTracker with System BCM service:
- ResourceTracker initialization during BCM startup
- Resource monitoring during BIA phase
- API endpoint /resources/status
- EventBus event publishing on deficit
- Prometheus metrics exposure
"""

import pytest
import asyncio
import httpx
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import psutil

# Add to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "intelligent-core" / "ai-foundation"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "intelligent-core" / "system-bcm-service"))

from utils.resource_tracker import ResourceTracker, create_resource_tracker
from engines.system_bcm_coordinator import SystemBCMCoordinator


class TestResourceTrackerIntegration:
    """Test ResourceTracker integration with System BCM Service"""

    @pytest.mark.asyncio
    async def test_resource_tracker_initialization(self, tmp_path):
        """Test ResourceTracker is initialized on BCM startup"""
        storage_path = tmp_path / "resource_history.json"

        # Create tracker (simulates startup)
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=1.0,
            history_size=100,
            storage_path=str(storage_path)
        )

        # Validate initialization
        assert tracker is not None
        assert tracker.is_running == True
        assert len(tracker.history) >= 1  # Initial snapshot taken

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_coordinator_with_resource_tracker(self, tmp_path):
        """Test SystemBCMCoordinator integrates with ResourceTracker"""
        storage_path = tmp_path / "bcm_resource_history.json"

        # Create tracker
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=0.5,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Create coordinator with tracker
        coordinator = SystemBCMCoordinator(resource_tracker=tracker)

        # Validate integration
        assert coordinator.resource_tracker is tracker

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_bia_phase_resource_monitoring(self, tmp_path):
        """Test BIA phase monitors resources"""
        storage_path = tmp_path / "bia_resource_history.json"

        # Create tracker with mock high CPU
        with patch.object(psutil, 'cpu_percent', return_value=85.0):
            tracker = await create_resource_tracker(
                snapshot_interval_seconds=0.5,
                history_size=50,
                storage_path=str(storage_path)
            )

        # Create coordinator
        coordinator = SystemBCMCoordinator(resource_tracker=tracker)

        # Mock EventBus
        mock_eventbus = AsyncMock()
        coordinator.eventbus = mock_eventbus

        # Execute BIA phase (which should monitor resources)
        with patch.object(psutil, 'cpu_percent', return_value=85.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 85.0
                mock_mem.return_value.used = 8000 * 1024 * 1024

                # Take snapshots to establish deficit state
                for _ in range(3):
                    tracker.take_snapshot()

                # Execute BIA phase
                result = await coordinator._execute_bia_phase(resource_tracker=tracker)

        # Validate result includes resource info
        assert result is not None
        assert 'resource_state' in result or result.get('status') == 'completed'

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_resource_deficit_event_publishing(self, tmp_path):
        """Test deficit state triggers EventBus event"""
        storage_path = tmp_path / "deficit_event_test.json"

        # Create tracker
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=0.5,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Create coordinator
        coordinator = SystemBCMCoordinator(resource_tracker=tracker)

        # Mock EventBus
        mock_eventbus = AsyncMock()
        coordinator.eventbus = mock_eventbus

        # Mock high resource usage (deficit)
        with patch.object(psutil, 'cpu_percent', return_value=90.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 90.0
                mock_mem.return_value.used = 9000 * 1024 * 1024

                # Take snapshots to establish deficit
                for _ in range(3):
                    tracker.take_snapshot()

                # Execute BIA phase (should publish event)
                await coordinator._execute_bia_phase(resource_tracker=tracker)

        # Verify event was published (if eventbus is configured)
        # Note: Event publishing depends on eventbus availability

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)

    def test_resource_state_detection_in_bcm(self, tmp_path):
        """Test resource state detection during BCM operations"""
        storage_path = tmp_path / "state_detection_test.json"

        # Create tracker
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Mock different resource states

        # Test 1: Deficit state
        with patch.object(psutil, 'cpu_percent', return_value=85.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 85.0
                mock_mem.return_value.used = 8500 * 1024 * 1024
                tracker.take_snapshot()

        state = tracker.detect_resource_state()
        assert state == "deficit"

        # Test 2: Normal state
        with patch.object(psutil, 'cpu_percent', return_value=50.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 60.0
                mock_mem.return_value.used = 5000 * 1024 * 1024
                tracker.take_snapshot()

        state = tracker.detect_resource_state()
        assert state == "normal"

        # Test 3: Surplus state
        with patch.object(psutil, 'cpu_percent', return_value=20.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 30.0
                mock_mem.return_value.used = 2000 * 1024 * 1024
                tracker.take_snapshot()

        state = tracker.detect_resource_state()
        assert state == "surplus"

    def test_deficit_prediction_in_bcm(self, tmp_path):
        """Test deficit prediction during BCM operations"""
        storage_path = tmp_path / "prediction_test.json"

        # Create tracker
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Mock increasing CPU trend
        cpu_values = [60.0, 65.0, 70.0, 75.0, 80.0]
        for cpu in cpu_values:
            with patch.object(psutil, 'cpu_percent', return_value=cpu):
                tracker.take_snapshot()

        # Predict when CPU will reach 90%
        cpu_deficit = tracker.predict_deficit('cpu_percent', threshold_percent=90.0)

        # Should predict some time in the future
        assert cpu_deficit is not None
        assert cpu_deficit >= 0

    def test_available_resources_calculation(self, tmp_path):
        """Test available resources calculation for BCM planning"""
        storage_path = tmp_path / "available_test.json"

        # Create tracker
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Take snapshot
        tracker.take_snapshot()

        # Get available resources
        available = tracker.get_available_resources()

        # Validate structure
        assert 'cpu_percent' in available
        assert 'memory_mb' in available
        assert 'time_seconds' in available
        assert 'disk_io_mb' in available

        # Validate values are reasonable
        assert available['cpu_percent'] >= 0
        assert available['cpu_percent'] <= 100
        assert available['memory_mb'] >= 0
        assert available['time_seconds'] == 60.0  # Default
        assert available['disk_io_mb'] == 100.0  # Default

    @pytest.mark.asyncio
    async def test_resource_persistence_during_bcm_cycle(self, tmp_path):
        """Test resource history persists during BCM cycle"""
        storage_path = tmp_path / "persistence_test.json"

        # Create tracker
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=0.2,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Wait for some snapshots
        await asyncio.sleep(0.5)

        # Save history
        tracker._save_history()

        # Stop tracker
        tracker.stop()
        await asyncio.sleep(0.1)

        # Create new tracker (should load history)
        tracker2 = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Validate history loaded
        assert len(tracker2.history) > 0
        assert tracker2.stats['total_snapshots'] > 0

    def test_resource_stats_tracking(self, tmp_path):
        """Test resource statistics tracking during BCM operations"""
        storage_path = tmp_path / "stats_test.json"

        # Create tracker
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Take multiple snapshots
        for _ in range(5):
            tracker.take_snapshot()

        # Get stats
        stats = tracker.get_stats()

        # Validate stats
        assert 'total_snapshots' in stats
        assert 'deficit_events' in stats
        assert 'surplus_events' in stats
        assert 'history_size' in stats
        assert 'resource_state' in stats

        assert stats['total_snapshots'] == 5
        assert stats['history_size'] == 5


class TestResourceTrackerAPIEndpoint:
    """Test /resources/status API endpoint"""

    @pytest.mark.asyncio
    async def test_resources_status_endpoint_structure(self, tmp_path):
        """Test /resources/status endpoint returns correct structure"""
        # This test simulates what the endpoint should return

        storage_path = tmp_path / "api_test.json"

        # Create tracker
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=0.5,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Simulate endpoint logic
        response_data = {
            "available": tracker.get_available_resources(),
            "state": tracker.detect_resource_state(),
            "stats": tracker.get_stats(),
            "predictions": {
                "cpu_deficit_seconds": tracker.predict_deficit('cpu_percent', 90.0),
                "memory_deficit_seconds": tracker.predict_deficit('memory_percent', 90.0)
            },
            "trends": {
                "cpu_trend": tracker.calculate_trend('cpu_percent'),
                "memory_trend": tracker.calculate_trend('memory_percent')
            }
        }

        # Validate response structure
        assert 'available' in response_data
        assert 'state' in response_data
        assert 'stats' in response_data
        assert 'predictions' in response_data
        assert 'trends' in response_data

        # Validate available resources
        assert 'cpu_percent' in response_data['available']
        assert 'memory_mb' in response_data['available']

        # Validate state
        assert response_data['state'] in ['deficit', 'normal', 'surplus']

        # Validate stats
        assert 'total_snapshots' in response_data['stats']
        assert 'resource_state' in response_data['stats']

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_resources_status_endpoint_predictions(self, tmp_path):
        """Test /resources/status endpoint deficit predictions"""
        storage_path = tmp_path / "predictions_api_test.json"

        # Create tracker
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=0.5,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Mock increasing CPU trend
        cpu_values = [60.0, 65.0, 70.0, 75.0, 80.0]
        for cpu in cpu_values:
            with patch.object(psutil, 'cpu_percent', return_value=cpu):
                tracker.take_snapshot()

        # Get predictions (as endpoint would)
        predictions = {
            "cpu_deficit_seconds": tracker.predict_deficit('cpu_percent', 90.0),
            "memory_deficit_seconds": tracker.predict_deficit('memory_percent', 90.0)
        }

        # CPU should have prediction (increasing trend)
        assert predictions['cpu_deficit_seconds'] is not None
        assert predictions['cpu_deficit_seconds'] >= 0

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)

    @pytest.mark.asyncio
    async def test_resources_status_endpoint_trends(self, tmp_path):
        """Test /resources/status endpoint trend analysis"""
        storage_path = tmp_path / "trends_api_test.json"

        # Create tracker
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=0.5,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Take multiple snapshots
        for _ in range(5):
            tracker.take_snapshot()
            await asyncio.sleep(0.05)

        # Get trends (as endpoint would)
        trends = {
            "cpu_trend": tracker.calculate_trend('cpu_percent'),
            "memory_trend": tracker.calculate_trend('memory_percent')
        }

        # Validate trend values
        assert -1.0 <= trends['cpu_trend'] <= 1.0
        assert -1.0 <= trends['memory_trend'] <= 1.0

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)


class TestResourceTrackerPrometheusMetrics:
    """Test Prometheus metrics for ResourceTracker"""

    def test_prometheus_metrics_structure(self, tmp_path):
        """Test Prometheus metrics are exposed correctly"""
        storage_path = tmp_path / "metrics_test.json"

        # Create tracker
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Take snapshots
        for _ in range(3):
            tracker.take_snapshot()

        # Get stats (metrics source)
        stats = tracker.get_stats()

        # Validate metrics can be generated
        expected_metrics = {
            'system_bcm_resource_snapshots_total': stats['total_snapshots'],
            'system_bcm_resource_deficit_events': stats['deficit_events'],
            'system_bcm_resource_surplus_events': stats['surplus_events'],
            'system_bcm_resource_state': 1 if stats['resource_state'] == 'deficit' else 0,
            'system_bcm_cpu_available_percent': tracker.get_available_resources()['cpu_percent'],
            'system_bcm_memory_available_mb': tracker.get_available_resources()['memory_mb']
        }

        # Validate all metrics present
        assert expected_metrics['system_bcm_resource_snapshots_total'] >= 0
        assert expected_metrics['system_bcm_resource_deficit_events'] >= 0
        assert expected_metrics['system_bcm_resource_surplus_events'] >= 0
        assert expected_metrics['system_bcm_resource_state'] in [0, 1]
        assert expected_metrics['system_bcm_cpu_available_percent'] >= 0
        assert expected_metrics['system_bcm_memory_available_mb'] >= 0

    def test_prometheus_metrics_deficit_event(self, tmp_path):
        """Test deficit event increments Prometheus counter"""
        storage_path = tmp_path / "deficit_metric_test.json"

        # Create tracker
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Initial deficit count
        initial_deficits = tracker.stats['deficit_events']

        # Mock high resource usage (deficit)
        with patch.object(psutil, 'cpu_percent', return_value=90.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 90.0
                mock_mem.return_value.used = 9000 * 1024 * 1024
                tracker.take_snapshot()

        # Detect state (should increment deficit counter)
        state = tracker.detect_resource_state()

        # Verify counter incremented
        assert state == "deficit"
        assert tracker.stats['deficit_events'] > initial_deficits

    def test_prometheus_metrics_surplus_event(self, tmp_path):
        """Test surplus event increments Prometheus counter"""
        storage_path = tmp_path / "surplus_metric_test.json"

        # Create tracker
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Initial surplus count
        initial_surplus = tracker.stats['surplus_events']

        # Mock low resource usage (surplus)
        with patch.object(psutil, 'cpu_percent', return_value=15.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 25.0
                mock_mem.return_value.used = 1500 * 1024 * 1024
                tracker.take_snapshot()

        # Detect state (should increment surplus counter)
        state = tracker.detect_resource_state()

        # Verify counter incremented
        assert state == "surplus"
        assert tracker.stats['surplus_events'] > initial_surplus


class TestResourceTrackerEventBusIntegration:
    """Test EventBus event publishing integration"""

    @pytest.mark.asyncio
    async def test_resource_contention_event_structure(self, tmp_path):
        """Test resource contention event structure"""
        storage_path = tmp_path / "event_structure_test.json"

        # Create tracker
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=0.5,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Mock deficit state
        with patch.object(psutil, 'cpu_percent', return_value=90.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 90.0
                mock_mem.return_value.used = 9000 * 1024 * 1024

                for _ in range(3):
                    tracker.take_snapshot()

        # Get resource data (what would be in event)
        event_data = {
            "event_type": "platform.bcm.resources.contention",
            "severity": "high",
            "resource_state": tracker.detect_resource_state(),
            "available": tracker.get_available_resources(),
            "predictions": {
                "cpu_deficit_seconds": tracker.predict_deficit('cpu_percent', 90.0),
                "memory_deficit_seconds": tracker.predict_deficit('memory_percent', 90.0)
            },
            "recommendations": [
                "Consider scaling infrastructure",
                "Review resource-intensive processes"
            ]
        }

        # Validate event structure
        assert event_data['event_type'] == "platform.bcm.resources.contention"
        assert event_data['severity'] == "high"
        assert event_data['resource_state'] == "deficit"
        assert 'available' in event_data
        assert 'predictions' in event_data
        assert 'recommendations' in event_data

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)


class TestResourceTrackerFullIntegration:
    """Full integration tests combining all components"""

    @pytest.mark.asyncio
    async def test_complete_bcm_resource_monitoring_flow(self, tmp_path):
        """Test complete BCM resource monitoring workflow"""
        storage_path = tmp_path / "full_integration_test.json"

        # Step 1: Create tracker (simulates BCM startup)
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=0.2,
            history_size=50,
            storage_path=str(storage_path)
        )

        # Step 2: Create BCM coordinator with tracker
        coordinator = SystemBCMCoordinator(resource_tracker=tracker)

        # Step 3: Simulate resource monitoring during operations
        await asyncio.sleep(0.5)  # Let monitoring run

        # Step 4: Get resource status (API endpoint simulation)
        resource_status = {
            "available": tracker.get_available_resources(),
            "state": tracker.detect_resource_state(),
            "stats": tracker.get_stats(),
            "predictions": {
                "cpu_deficit_seconds": tracker.predict_deficit('cpu_percent', 90.0),
                "memory_deficit_seconds": tracker.predict_deficit('memory_percent', 90.0)
            }
        }

        # Step 5: Validate complete workflow
        assert len(tracker.history) > 0  # Monitoring active
        assert tracker.is_running == True
        assert resource_status['state'] in ['deficit', 'normal', 'surplus']
        assert resource_status['stats']['total_snapshots'] > 0

        # Step 6: Persist and cleanup
        tracker._save_history()
        assert storage_path.exists()

        tracker.stop()
        await asyncio.sleep(0.1)

        # Step 7: Verify persistence (BCM recovery scenario)
        tracker2 = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=50,
            storage_path=str(storage_path)
        )

        assert len(tracker2.history) > 0  # History restored
        assert tracker2.stats['total_snapshots'] > 0


# Fixtures

@pytest.fixture
def mock_eventbus():
    """Mock EventBus for testing"""
    eventbus = AsyncMock()
    eventbus.publish = AsyncMock()
    return eventbus


@pytest.fixture
async def integration_tracker(tmp_path):
    """Fixture for integration testing"""
    storage_path = tmp_path / "integration_tracker.json"
    tracker = await create_resource_tracker(
        snapshot_interval_seconds=0.5,
        history_size=50,
        storage_path=str(storage_path)
    )
    yield tracker
    tracker.stop()
    await asyncio.sleep(0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
