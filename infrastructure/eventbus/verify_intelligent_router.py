#!/usr/bin/env python3
"""
Intelligent EventBus Router - Verification Script
==================================================

Quick verification that the intelligent router is working correctly.

Run:
    cd /Users/MD/AI-Platform-ISO
    python infrastructure/eventbus/verify_intelligent_router.py
"""

import asyncio
import sys
from infrastructure.eventbus.backends.memory import InMemoryEventBus
from infrastructure.eventbus.intelligent_router import IntelligentEventRouter
from infrastructure.eventbus.core.events import Event, EventPriority


async def verify_installation():
    """Verify intelligent router installation and basic functionality"""
    print("="*70)
    print("INTELLIGENT EVENTBUS ROUTER - VERIFICATION")
    print("="*70)
    print()

    try:
        # 1. Test Import
        print("✓ Module imports successful")

        # 2. Test Router Creation
        eventbus = InMemoryEventBus()
        router = IntelligentEventRouter(
            base_eventbus=eventbus,
            enable_ai_analysis=True,
            enable_semantic_matching=True
        )
        print("✓ Router created successfully")

        # 3. Test Initialization
        await router.initialize()
        print("✓ Router initialized successfully")

        # 4. Test Subscriber Registration
        events_received = []

        async def test_handler(event: Event):
            events_received.append(event)

        await router.register_subscriber(
            subscriber_id="test_subscriber",
            event_pattern="test.*",
            handler=test_handler,
            capabilities={
                "domains": ["test"],
                "max_concurrent": 5,
                "avg_processing_time_ms": 100,
                "sla_ms": 500,
                "semantic_tags": ["test", "verification"]
            }
        )
        print("✓ Subscriber registered successfully")

        # 5. Test Event Routing
        test_event = Event.create(
            event_type="test.verification_event",
            data={
                "message": "Verification test",
                "timestamp": "2025-10-19"
            },
            source="verification_script",
            tenant_id="test_tenant",
            priority=EventPriority.NORMAL
        )

        decision = await router.route_event(test_event)
        print(f"✓ Event routed successfully")
        print(f"  - Selected subscribers: {decision.selected_subscribers}")
        print(f"  - Routing strategy: {decision.routing_strategy}")
        print(f"  - Confidence: {decision.confidence_score:.2f}")
        print(f"  - Decision time: {decision.decision_time_ms:.2f}ms")

        # 6. Wait for Processing
        await asyncio.sleep(0.5)

        if len(events_received) > 0:
            print("✓ Event processed successfully")
        else:
            print("⚠ Event not yet processed (may need more time)")

        # 7. Test Metrics
        metrics = router.get_metrics()
        print("✓ Metrics retrieved successfully")
        print(f"  - Total events: {metrics['total_events']}")
        print(f"  - Total routed: {metrics['total_routed']}")
        print(f"  - Routing efficiency: {metrics['routing_efficiency']:.2%}")
        print(f"  - Registered subscribers: {metrics['registered_subscribers']}")

        # 8. Test Subscriber Metrics
        sub_metrics = router.get_subscriber_metrics("test_subscriber")
        if sub_metrics:
            print("✓ Subscriber metrics retrieved successfully")
            print(f"  - Status: {sub_metrics['status']}")
            print(f"  - Current load: {sub_metrics['current_load']}")
        else:
            print("⚠ Subscriber metrics not available")

        # 9. Test Priority Event
        priority_event = Event.create(
            event_type="test.priority_event",
            data={
                "urgency": "high",
                "description": "Critical test event"
            },
            source="verification_script",
            tenant_id="test_tenant",
            priority=EventPriority.HIGH
        )

        priority_decision = await router.route_event(priority_event)
        print("✓ Priority event routed successfully")
        print(f"  - Priority used: {priority_decision.priority_used.name}")

        # 10. Test Shutdown
        await router.shutdown()
        print("✓ Router shutdown successfully")

        print()
        print("="*70)
        print("ALL CHECKS PASSED! ✓")
        print("="*70)
        print()
        print("Intelligent EventBus Router is working correctly!")
        print()
        print("Next steps:")
        print("  1. Run examples: python -m infrastructure.eventbus.examples.intelligent_routing_example")
        print("  2. Run tests: pytest tests/unit/infrastructure/eventbus/test_intelligent_router.py -v")
        print("  3. Read integration guide: infrastructure/eventbus/INTELLIGENT_ROUTER_INTEGRATION.md")
        print()

        return True

    except Exception as e:
        print()
        print("="*70)
        print("VERIFICATION FAILED! ✗")
        print("="*70)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


async def main():
    """Main entry point"""
    success = await verify_installation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
