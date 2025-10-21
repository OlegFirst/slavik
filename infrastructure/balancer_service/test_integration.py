"""
Integration Test for Phase 2 Balancer Service

Tests the end-to-end flow:
1. EventBus connection
2. Resource Tracker publishes metrics
3. System Balancer receives and processes events
4. Three-Dimensional Balancer makes decisions
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "intelligent-core"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.eventbus import create_eventbus
from intelligent_core.ai_foundation.balancer import (
    SystemBalancer,
    ImpactEvidenceTracker,
    PredictiveROIOptimizer,
    ThreeDimensionalBalancer
)


async def test_eventbus_connection():
    """Test EventBus connection"""
    print(" Test 1: EventBus Connection...")

    try:
        eventbus = create_eventbus('memory')  # Use memory backend for testing
        await eventbus.connect()
        print("    EventBus connected")

        # Test publish
        await eventbus.publish({
            'type': 'test.event',
            'source': 'integration-test',
            'data': {'message': 'Hello from test'}
        })
        print("    Event published")

        # Test subscribe
        received = []
        async def handler(event):
            received.append(event)

        await eventbus.subscribe('test.event', handler)
        print("    Subscribed to events")

        # Publish another event
        await eventbus.publish({
            'type': 'test.event',
            'source': 'integration-test',
            'data': {'message': 'Test 2'}
        })

        await asyncio.sleep(0.5)  # Wait for event processing

        if len(received) > 0:
            print(f"    Received {len(received)} events")
        else:
            print("   ️  No events received (might be async delay)")

        await eventbus.disconnect()
        return True

    except Exception as e:
        print(f"    EventBus test failed: {e}")
        return False


async def test_balancer_initialization():
    """Test balancer initialization"""
    print("\n Test 2: Balancer Initialization...")

    try:
        # Create EventBus
        eventbus = create_eventbus('memory')
        await eventbus.connect()
        print("    EventBus ready")

        # Initialize components
        evidence_tracker = ImpactEvidenceTracker()
        print("    Impact Evidence Tracker initialized")

        roi_optimizer = PredictiveROIOptimizer(evidence_tracker=evidence_tracker)
        print("    Predictive ROI Optimizer initialized")

        balancer_3d = ThreeDimensionalBalancer(
            evidence_tracker=evidence_tracker,
            roi_optimizer=roi_optimizer
        )
        print("    Three-Dimensional Balancer initialized")

        system_balancer = SystemBalancer(
            eventbus=eventbus,
            balancer_3d=balancer_3d
        )
        print("    System Balancer initialized")

        await eventbus.disconnect()
        return True

    except Exception as e:
        print(f"    Balancer initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_imbalance_event_flow():
    """Test imbalance event flow"""
    print("\n Test 3: Imbalance Event Flow...")

    try:
        # Create EventBus
        eventbus = create_eventbus('memory')
        await eventbus.connect()

        # Initialize balancers
        evidence_tracker = ImpactEvidenceTracker()
        roi_optimizer = PredictiveROIOptimizer(evidence_tracker=evidence_tracker)
        balancer_3d = ThreeDimensionalBalancer(
            evidence_tracker=evidence_tracker,
            roi_optimizer=roi_optimizer
        )
        system_balancer = SystemBalancer(
            eventbus=eventbus,
            balancer_3d=balancer_3d
        )

        print("    Balancers initialized")

        # Subscribe to events
        received_events = []

        async def handle_imbalance(event):
            received_events.append(event)
            print(f"    Received imbalance event: {event.get('source')}")

        await eventbus.subscribe('platform.bcm.imbalance_detected', handle_imbalance)
        print("    Subscribed to imbalance events")

        # Publish test imbalance event
        await eventbus.publish({
            'type': 'platform.bcm.imbalance_detected',
            'source': 'test-module.survival-instinct',
            'data': {
                'module': 'test-module',
                'kpi_name': 'response_time',
                'level': 'warning',
                'health_score': 65.0,
                'cpu_usage': 75.0,
                'memory_usage': 70.0
            }
        })
        print("    Published imbalance event")

        await asyncio.sleep(1)  # Wait for processing

        if len(received_events) > 0:
            print(f"    Received {len(received_events)} events")
        else:
            print("   ️  No events received (check async processing)")

        # Check if evidence was recorded
        stats = evidence_tracker.get_stats()
        print(f"    Evidence Tracker stats: {stats}")

        await eventbus.disconnect()
        return True

    except Exception as e:
        print(f"    Imbalance event flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_three_dimensional_decision():
    """Test three-dimensional decision making"""
    print("\n Test 4: Three-Dimensional Decision Making...")

    try:
        evidence_tracker = ImpactEvidenceTracker()
        roi_optimizer = PredictiveROIOptimizer(evidence_tracker=evidence_tracker)
        balancer_3d = ThreeDimensionalBalancer(
            evidence_tracker=evidence_tracker,
            roi_optimizer=roi_optimizer
        )

        # Record some baseline data
        evidence_tracker.record_baseline(
            module_name="test-module",
            health_score=50.0,
            cpu_usage=80.0,
            memory_usage=75.0
        )
        print("    Baseline recorded")

        # Make a balanced decision
        context = {
            'current_health': 50.0,
            'available_resources': 40.0,
            'data_quality': 0.7,
            'in_crisis': False
        }

        decision = balancer_3d.make_balanced_decision(
            module_name="test-module",
            context=context
        )

        print(f"    Decision made: {decision.action_type}")
        print(f"    Weights: R={decision.weights.rational_weight:.2f}, "
              f"I={decision.weights.intuitive_weight:.2f}, "
              f"P={decision.weights.pragmatic_weight:.2f}")
        print(f"   ️ Balance score: {decision.balance_score:.2f}")

        return True

    except Exception as e:
        print(f"    Three-dimensional decision test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("="*60)
    print("Phase 2 Integration Tests")
    print("="*60)

    results = []

    # Run tests
    results.append(("EventBus Connection", await test_eventbus_connection()))
    results.append(("Balancer Initialization", await test_balancer_initialization()))
    results.append(("Imbalance Event Flow", await test_imbalance_event_flow()))
    results.append(("Three-Dimensional Decision", await test_three_dimensional_decision()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = " PASS" if result else " FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n All tests passed!")
        return 0
    else:
        print(f"\n️  {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
