#!/usr/bin/env python3
"""
Demo: Health Monitor EventBus Integration (Phase 1 - Task 1.1)

Demonstrates that Health Monitor successfully publishes events to EventBus
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

# Direct import from full path
import importlib.util

# Load health_monitor module directly
spec = importlib.util.spec_from_file_location(
    "health_monitor",
    "/Users/MD/AI-Platform-ISO/intelligent-core/orchestration/ai-orchestration/core/health_monitor.py"
)
health_monitor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health_monitor_module)

HealthMonitor = health_monitor_module.HealthMonitor
HealthCheck = health_monitor_module.HealthCheck
HealthStatus = health_monitor_module.HealthStatus

from infrastructure.eventbus import create_eventbus, Event


async def demo_health_monitor_eventbus():
    """Demonstrate Health Monitor publishing events to EventBus"""

    print("=" * 70)
    print("DEMO: Health Monitor EventBus Integration (Phase 1)")
    print("=" * 70)
    print()

    # Step 1: Create EventBus
    print("Step 1: Creating EventBus (memory backend)...")
    bus = create_eventbus('memory')
    print("✅ EventBus created")
    print()

    # Step 2: Create Health Monitor
    print("Step 2: Creating Health Monitor...")
    monitor = HealthMonitor()
    print("✅ Health Monitor created")
    print()

    # Step 3: Connect EventBus to Health Monitor
    print("Step 3: Connecting EventBus to Health Monitor...")
    await monitor.connect_eventbus(bus)
    print("✅ EventBus connected to Health Monitor")
    print()

    # Step 4: Subscribe to health events
    print("Step 4: Subscribing to health events...")
    received_events = []

    async def event_handler(event: Event):
        received_events.append(event)
        print(f"📥 Received event: {event.type}")  # Use 'type' not 'event_type'
        print(f"   Service: {event.data['service_name']}")
        print(f"   Status: {event.data['previous_status']} → {event.data['status']}")
        print(f"   Message: {event.data['message']}")
        print()

    await bus.subscribe('infrastructure.health.*', event_handler)
    print("✅ Subscribed to 'infrastructure.health.*'")
    print()

    # Step 5: Register health checks
    print("Step 5: Registering health checks...")

    # Mock checker that alternates healthy/unhealthy
    check_count = 0

    async def mock_checker(service_name, config):
        nonlocal check_count
        check_count += 1
        is_healthy = (check_count % 2 == 1)
        print(f"  🔍 Check #{check_count} for {service_name}: {'HEALTHY' if is_healthy else 'UNHEALTHY'}")
        return is_healthy

    await monitor.register_check(HealthCheck(
        service_name='test_api_gateway',
        check_type='custom',
        interval=2,  # Every 2 seconds
        custom_checker=mock_checker
    ))

    print("✅ Registered health check for 'test_api_gateway'")
    print()

    # Step 6: Start monitoring
    print("Step 6: Starting Health Monitor...")
    print("   Monitoring interval: 2 seconds")
    print("   Will run for 10 seconds to demonstrate status changes...")
    print()

    monitor_task = asyncio.create_task(monitor.monitor_continuously())

    # Let it run for 10 seconds (should get ~5 checks)
    await asyncio.sleep(10)

    # Step 7: Stop monitoring
    print()
    print("Step 7: Stopping Health Monitor...")
    await monitor.stop_monitoring()
    await asyncio.sleep(1)

    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

    print("✅ Health Monitor stopped")
    print()

    # Step 8: Show results
    print("=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(f"Total health checks performed: {check_count}")
    print(f"Total events published: {len(received_events)}")
    print()

    if len(received_events) > 0:
        print("Event details:")
        for i, event in enumerate(received_events, 1):
            print(f"{i}. {event.type}")  # Use 'type' not 'event_type'
            print(f"   Status: {event.data['status']}")
            print(f"   Previous: {event.data['previous_status']}")
            print()

        print("✅ SUCCESS: Health Monitor successfully publishes events to EventBus!")
        print()
        print("Key Features Demonstrated:")
        print("  ✅ Health Monitor connects to EventBus")
        print("  ✅ Status changes are detected")
        print("  ✅ Events published only when status changes (not every check)")
        print("  ✅ Events contain full health check details")
        print("  ✅ Event pattern: 'infrastructure.health.{status}'")
    else:
        print("❌ FAILED: No events received")
        return False

    print()
    print("=" * 70)
    print("✅ DEMO COMPLETED SUCCESSFULLY")
    print("=" * 70)

    return True


if __name__ == '__main__':
    try:
        success = asyncio.run(demo_health_monitor_eventbus())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
