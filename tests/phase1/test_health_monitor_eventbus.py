"""
Test: Health Monitor EventBus Integration (Phase 1 - Task 1.1)

Tests that Health Monitor publishes events to EventBus on status changes
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from intelligent_core.orchestration.ai_orchestration.core.health_monitor import (
    HealthMonitor,
    HealthCheck,
    HealthStatus
)
from infrastructure.eventbus import create_eventbus


@pytest.mark.asyncio
async def test_health_monitor_publishes_events():
    """Test that Health Monitor publishes events when health status changes"""

    # Create EventBus (memory backend for testing)
    bus = create_eventbus('memory')

    # Create Health Monitor
    monitor = HealthMonitor()
    await monitor.connect_eventbus(bus)

    # Track received events
    received_events = []

    async def event_handler(event):
        received_events.append(event)
        print(f"Received event: {event.event_type} - {event.data['service_name']} → {event.data['status']}")

    # Subscribe to health events
    await bus.subscribe('infrastructure.health.*', event_handler)

    # Register a mock health check (HTTP type but will fail)
    await monitor.register_check(HealthCheck(
        service_name='test_service',
        check_type='http',
        interval=2,  # Check every 2 seconds
        config={'url': 'http://localhost:99999/health'}  # Invalid port - will fail
    ))

    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor.monitor_continuously())

    # Wait for first health check (should be UNHEALTHY due to invalid port)
    await asyncio.sleep(3)

    # Stop monitoring
    await monitor.stop_monitoring()
    await asyncio.sleep(1)  # Give time to cleanup
    monitor_task.cancel()

    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

    # Verify event was published
    assert len(received_events) > 0, "No events received - EventBus integration failed"

    first_event = received_events[0]
    assert first_event.event_type == 'infrastructure.health.unhealthy'
    assert first_event.data['service_name'] == 'test_service'
    assert first_event.data['status'] == 'unhealthy'
    assert first_event.source == 'health_monitor'
    assert first_event.tenant_id == 'system'

    print(" Test PASSED: Health Monitor successfully publishes events to EventBus")


@pytest.mark.asyncio
async def test_health_monitor_status_change_detection():
    """Test that Health Monitor only publishes events when status changes"""

    bus = create_eventbus('memory')
    monitor = HealthMonitor()
    await monitor.connect_eventbus(bus)

    received_events = []

    async def event_handler(event):
        received_events.append(event)

    await bus.subscribe('infrastructure.health.*', event_handler)

    # Mock custom checker that alternates between healthy and unhealthy
    check_count = 0

    async def mock_checker(service_name, config):
        nonlocal check_count
        check_count += 1
        # Alternate: healthy, unhealthy, unhealthy (no event on 3rd), healthy
        return check_count in [1, 4]  # True = healthy

    await monitor.register_check(HealthCheck(
        service_name='test_service_2',
        check_type='custom',
        interval=1,
        custom_checker=mock_checker
    ))

    monitor_task = asyncio.create_task(monitor.monitor_continuously())

    # Wait for 4 checks (4 seconds)
    await asyncio.sleep(4.5)

    await monitor.stop_monitoring()
    await asyncio.sleep(0.5)
    monitor_task.cancel()

    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

    # Expected events:
    # 1. First check → HEALTHY (initial state)
    # 2. Second check → UNHEALTHY (status changed)
    # 3. Third check → UNHEALTHY (NO EVENT - status same)
    # 4. Fourth check → HEALTHY (status changed)

    print(f"Received {len(received_events)} events")
    for i, event in enumerate(received_events):
        print(f"  Event {i+1}: {event.event_type} - {event.data['status']}")

    # Should have 3 events (not 4, because 3rd check didn't change status)
    assert len(received_events) == 3, f"Expected 3 events (status changes only), got {len(received_events)}"

    # Verify event sequence
    assert received_events[0].data['status'] == 'healthy'
    assert received_events[1].data['status'] == 'unhealthy'
    assert received_events[2].data['status'] == 'healthy'

    print(" Test PASSED: Health Monitor only publishes events on status changes")


@pytest.mark.asyncio
async def test_health_monitor_without_eventbus():
    """Test that Health Monitor works without EventBus (backward compatibility)"""

    # Create Health Monitor WITHOUT connecting EventBus
    monitor = HealthMonitor()

    # Should work fine even without EventBus
    async def mock_checker(service_name, config):
        return True  # Always healthy

    await monitor.register_check(HealthCheck(
        service_name='test_service_3',
        check_type='custom',
        interval=1,
        custom_checker=mock_checker
    ))

    monitor_task = asyncio.create_task(monitor.monitor_continuously())
    await asyncio.sleep(2)

    await monitor.stop_monitoring()
    await asyncio.sleep(0.5)
    monitor_task.cancel()

    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

    # Should have run check successfully (no events published, but no errors either)
    results = await monitor.get_all_results()
    assert 'test_service_3' in results
    assert results['test_service_3'].status == HealthStatus.HEALTHY

    print(" Test PASSED: Health Monitor works without EventBus (backward compatible)")


if __name__ == '__main__':
    print("Running Health Monitor EventBus Integration Tests...")
    print("=" * 60)

    asyncio.run(test_health_monitor_publishes_events())
    print()
    asyncio.run(test_health_monitor_status_change_detection())
    print()
    asyncio.run(test_health_monitor_without_eventbus())
    print()
    print("=" * 60)
    print(" All tests PASSED!")
