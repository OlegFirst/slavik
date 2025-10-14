"""
Unit tests for ResourceTracker

Tests resource monitoring, trend analysis, deficit prediction,
and persistence functionality.
"""

import pytest
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, patch
import psutil

# Add to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "ai-foundation"))

from utils.resource_tracker import (
    ResourceTracker,
    ResourceSnapshot,
    create_resource_tracker
)


class TestResourceSnapshot:
    """Test ResourceSnapshot dataclass"""

    def test_snapshot_creation(self):
        """Test creating a resource snapshot"""
        snapshot = ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=45.2,
            memory_percent=60.5,
            memory_mb=2048.0,
            disk_io_mb=100.5,
            network_bytes=1024000.0
        )

        assert snapshot.cpu_percent == 45.2
        assert snapshot.memory_percent == 60.5
        assert snapshot.memory_mb == 2048.0
        assert snapshot.disk_io_mb == 100.5
        assert snapshot.network_bytes == 1024000.0

    def test_snapshot_to_dict(self):
        """Test converting snapshot to dictionary"""
        snapshot = ResourceSnapshot(
            timestamp=1234567890.0,
            cpu_percent=45.2,
            memory_percent=60.5,
            memory_mb=2048.0,
            disk_io_mb=100.5,
            network_bytes=1024000.0
        )

        data = snapshot.to_dict()

        assert isinstance(data, dict)
        assert data['timestamp'] == 1234567890.0
        assert data['cpu_percent'] == 45.2
        assert data['memory_percent'] == 60.5

    def test_snapshot_from_dict(self):
        """Test creating snapshot from dictionary"""
        data = {
            'timestamp': 1234567890.0,
            'cpu_percent': 45.2,
            'memory_percent': 60.5,
            'memory_mb': 2048.0,
            'disk_io_mb': 100.5,
            'network_bytes': 1024000.0
        }

        snapshot = ResourceSnapshot.from_dict(data)

        assert snapshot.timestamp == 1234567890.0
        assert snapshot.cpu_percent == 45.2
        assert snapshot.memory_percent == 60.5


class TestResourceTracker:
    """Unit tests for ResourceTracker"""

    def test_initialization(self):
        """Test ResourceTracker initialization"""
        tracker = ResourceTracker(
            snapshot_interval_seconds=60.0,
            history_size=100,
            storage_path="/tmp/test_resource_history.json"
        )

        assert tracker.snapshot_interval == 60.0
        assert tracker.history_size == 100
        assert tracker.storage_path == "/tmp/test_resource_history.json"
        assert tracker.is_running == False
        assert len(tracker.history) == 0

    def test_take_snapshot(self):
        """Test taking a resource snapshot"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)
        snapshot = tracker.take_snapshot()

        # Validate snapshot
        assert isinstance(snapshot, ResourceSnapshot)
        assert snapshot.timestamp > 0
        assert snapshot.cpu_percent >= 0
        assert snapshot.cpu_percent <= 100
        assert snapshot.memory_percent >= 0
        assert snapshot.memory_percent <= 100
        assert snapshot.memory_mb >= 0

        # Check history
        assert len(tracker.history) == 1
        assert tracker.stats['total_snapshots'] == 1

    def test_multiple_snapshots(self):
        """Test taking multiple snapshots"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=5)

        # Take 3 snapshots
        for _ in range(3):
            tracker.take_snapshot()
            time.sleep(0.1)  # Small delay

        assert len(tracker.history) == 3
        assert tracker.stats['total_snapshots'] == 3

    def test_history_size_limit(self):
        """Test history size limit (maxlen)"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=3)

        # Take 5 snapshots (should keep only last 3)
        for _ in range(5):
            tracker.take_snapshot()

        assert len(tracker.history) == 3  # maxlen enforced
        assert tracker.stats['total_snapshots'] == 5  # but stats count all

    def test_calculate_trend_insufficient_data(self):
        """Test trend calculation with insufficient data"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # No snapshots
        trend = tracker.calculate_trend('cpu_percent')
        assert trend == 0.0

        # One snapshot
        tracker.take_snapshot()
        trend = tracker.calculate_trend('cpu_percent')
        assert trend == 0.0

    def test_calculate_trend_stable(self):
        """Test trend calculation with stable values"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Mock stable CPU values
        with patch.object(psutil, 'cpu_percent', return_value=50.0):
            for _ in range(5):
                tracker.take_snapshot()

        trend = tracker.calculate_trend('cpu_percent')

        # Should be close to 0 (stable)
        assert -0.1 <= trend <= 0.1

    def test_calculate_trend_window_size(self):
        """Test trend calculation with different window sizes"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=20)

        # Generate 10 snapshots
        for _ in range(10):
            tracker.take_snapshot()

        # Different window sizes should work
        trend_5 = tracker.calculate_trend('cpu_percent', window_size=5)
        trend_10 = tracker.calculate_trend('cpu_percent', window_size=10)

        assert -1.0 <= trend_5 <= 1.0
        assert -1.0 <= trend_10 <= 1.0

    def test_predict_deficit_no_data(self):
        """Test deficit prediction with no data"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        deficit = tracker.predict_deficit('cpu_percent', threshold_percent=90.0)
        assert deficit is None

    def test_predict_deficit_negative_trend(self):
        """Test deficit prediction with decreasing trend"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Mock decreasing CPU
        cpu_values = [80.0, 75.0, 70.0, 65.0, 60.0]
        for cpu in cpu_values:
            with patch.object(psutil, 'cpu_percent', return_value=cpu):
                tracker.take_snapshot()

        # Should not predict deficit (trend is down)
        deficit = tracker.predict_deficit('cpu_percent', threshold_percent=90.0)
        assert deficit is None

    def test_predict_deficit_already_exceeded(self):
        """Test deficit prediction when already at threshold"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Mock high CPU (already at threshold)
        with patch.object(psutil, 'cpu_percent', return_value=95.0):
            tracker.take_snapshot()

        deficit = tracker.predict_deficit('cpu_percent', threshold_percent=90.0)

        # Should return 0 (already exceeded)
        assert deficit == 0.0

    def test_detect_resource_state_no_data(self):
        """Test resource state detection with no data"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        state = tracker.detect_resource_state()
        assert state == "normal"

    def test_detect_resource_state_deficit(self):
        """Test deficit state detection"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Mock high resource usage (deficit)
        with patch.object(psutil, 'cpu_percent', return_value=85.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 85.0
                mock_mem.return_value.used = 8000 * 1024 * 1024
                tracker.take_snapshot()

        state = tracker.detect_resource_state()
        assert state == "deficit"

        # Stats should increment
        assert tracker.stats['deficit_events'] >= 1

    def test_detect_resource_state_surplus(self):
        """Test surplus state detection"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Mock low resource usage (surplus)
        with patch.object(psutil, 'cpu_percent', return_value=20.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 30.0
                mock_mem.return_value.used = 2000 * 1024 * 1024
                tracker.take_snapshot()

        state = tracker.detect_resource_state()
        assert state == "surplus"

        # Stats should increment
        assert tracker.stats['surplus_events'] >= 1

    def test_detect_resource_state_normal(self):
        """Test normal state detection"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Mock normal resource usage
        with patch.object(psutil, 'cpu_percent', return_value=50.0):
            with patch.object(psutil, 'virtual_memory') as mock_mem:
                mock_mem.return_value.percent = 60.0
                mock_mem.return_value.used = 4000 * 1024 * 1024
                tracker.take_snapshot()

        state = tracker.detect_resource_state()
        assert state == "normal"

    def test_get_available_resources_no_data(self):
        """Test getting available resources with no data"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        available = tracker.get_available_resources()

        # Should return defaults
        assert 'cpu_percent' in available
        assert 'memory_mb' in available
        assert 'time_seconds' in available
        assert 'disk_io_mb' in available
        assert available['cpu_percent'] == 50.0
        assert available['memory_mb'] == 1000.0
        assert available['time_seconds'] == 60.0
        assert available['disk_io_mb'] == 100.0

    def test_get_available_resources_with_data(self):
        """Test getting available resources with actual data"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Take snapshot
        tracker.take_snapshot()

        available = tracker.get_available_resources()

        # Validate structure
        assert 'cpu_percent' in available
        assert 'memory_mb' in available
        assert 'time_seconds' in available
        assert 'disk_io_mb' in available

        # Values should be reasonable
        assert available['cpu_percent'] >= 0
        assert available['memory_mb'] >= 0
        assert available['time_seconds'] == 60.0
        assert available['disk_io_mb'] == 100.0

    def test_get_stats(self):
        """Test getting tracker statistics"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        # Take some snapshots
        for _ in range(3):
            tracker.take_snapshot()

        stats = tracker.get_stats()

        assert 'total_snapshots' in stats
        assert 'deficit_events' in stats
        assert 'surplus_events' in stats
        assert 'history_size' in stats
        assert 'resource_state' in stats

        assert stats['total_snapshots'] == 3
        assert stats['history_size'] == 3

    def test_persistence_save(self, tmp_path):
        """Test saving history to file"""
        storage_path = tmp_path / "resource_history.json"

        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=10,
            storage_path=str(storage_path)
        )

        # Generate snapshots
        for _ in range(3):
            tracker.take_snapshot()

        # Save
        tracker._save_history()

        # File should exist
        assert storage_path.exists()

        # Should be valid JSON
        import json
        with open(storage_path) as f:
            data = json.load(f)

        assert 'snapshots' in data
        assert 'stats' in data
        assert 'saved_at' in data
        assert len(data['snapshots']) == 3

    def test_persistence_load(self, tmp_path):
        """Test loading history from file"""
        storage_path = tmp_path / "resource_history.json"

        # Create tracker and save
        tracker1 = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=10,
            storage_path=str(storage_path)
        )

        for _ in range(5):
            tracker1.take_snapshot()

        tracker1._save_history()
        initial_stats = tracker1.stats.copy()

        # Load in new tracker
        tracker2 = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=10,
            storage_path=str(storage_path)
        )

        # History should be loaded
        assert len(tracker2.history) == 5
        assert tracker2.stats['total_snapshots'] == initial_stats['total_snapshots']

    def test_stop(self):
        """Test stopping the tracker"""
        tracker = ResourceTracker(snapshot_interval_seconds=1.0, history_size=10)

        tracker.is_running = True
        tracker.stop()

        assert tracker.is_running == False


@pytest.mark.asyncio
class TestResourceTrackerAsync:
    """Async tests for ResourceTracker"""

    async def test_create_resource_tracker(self):
        """Test async resource tracker creation"""
        tracker = await create_resource_tracker(
            snapshot_interval_seconds=1.0,
            history_size=10,
            storage_path="/tmp/test_async_resource.json"
        )

        assert tracker is not None
        assert isinstance(tracker, ResourceTracker)

        # Should have taken initial snapshot
        assert len(tracker.history) >= 1

        # Should be running
        assert tracker.is_running == True

        # Cleanup
        tracker.stop()
        await asyncio.sleep(0.1)

    async def test_monitoring_loop(self, tmp_path):
        """Test monitoring loop runs"""
        storage_path = tmp_path / "monitor_test.json"

        tracker = ResourceTracker(
            snapshot_interval_seconds=0.2,  # Fast for testing
            history_size=10,
            storage_path=str(storage_path)
        )

        # Start monitoring in background
        task = asyncio.create_task(tracker.run_monitoring_loop())

        # Wait a bit
        await asyncio.sleep(0.5)

        # Should have taken snapshots
        assert len(tracker.history) > 0

        # Stop
        tracker.stop()
        await asyncio.sleep(0.1)

        # Cancel task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    async def test_monitoring_loop_saves_history(self, tmp_path):
        """Test monitoring loop saves history periodically"""
        storage_path = tmp_path / "monitor_save_test.json"

        tracker = ResourceTracker(
            snapshot_interval_seconds=0.1,
            history_size=10,
            storage_path=str(storage_path)
        )

        # Start monitoring
        task = asyncio.create_task(tracker.run_monitoring_loop())

        # Wait for multiple cycles
        await asyncio.sleep(0.5)

        # Stop
        tracker.stop()
        await asyncio.sleep(0.1)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # File should exist with saved data
        assert storage_path.exists()


class TestResourceTrackerIntegration:
    """Integration tests combining multiple features"""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: create, snapshot, analyze, persist"""
        storage_path = tmp_path / "full_workflow.json"

        # Create tracker
        tracker = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=10,
            storage_path=str(storage_path)
        )

        # Take multiple snapshots
        for _ in range(5):
            tracker.take_snapshot()
            time.sleep(0.05)

        # Analyze
        state = tracker.detect_resource_state()
        available = tracker.get_available_resources()
        stats = tracker.get_stats()
        trend = tracker.calculate_trend('cpu_percent')

        # Validate
        assert state in ["deficit", "normal", "surplus"]
        assert available['cpu_percent'] >= 0
        assert stats['total_snapshots'] == 5
        assert -1.0 <= trend <= 1.0

        # Persist
        tracker._save_history()
        assert storage_path.exists()

        # Load in new tracker
        tracker2 = ResourceTracker(
            snapshot_interval_seconds=1.0,
            history_size=10,
            storage_path=str(storage_path)
        )

        # Should have same history
        assert len(tracker2.history) == 5
        assert tracker2.stats['total_snapshots'] == 5


# Fixtures

@pytest.fixture
def tracker():
    """Basic tracker fixture"""
    return ResourceTracker(
        snapshot_interval_seconds=1.0,
        history_size=10,
        storage_path="/tmp/test_tracker.json"
    )


@pytest.fixture
def tracker_with_data(tracker):
    """Tracker with sample data"""
    for _ in range(5):
        tracker.take_snapshot()
    return tracker


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
