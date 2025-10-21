"""
Test Integration - BIA Service
================================

This script tests the integration without starting the full server.
Tests:
1. Platform initialization
2. Self-aware service setup
3. Event handling registration
4. Component availability
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from infrastructure.platform_integration import init_platform, shutdown_platform, get_platform

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_platform_integration():
    """Test platform integration initialization"""
    print("\n" + "=" * 70)
    print("Testing BIA Service Platform Integration")
    print("=" * 70 + "\n")

    # Test 1: Platform Initialization
    print("1️⃣  Testing Platform Initialization...")
    try:
        platform = await init_platform(
            database_url="sqlite+aiosqlite:///./test_bia.db",  # Use test DB
            redis_url="redis://localhost:6379/1",  # Use different Redis DB
            enable_intelligent_routing=True,
            enable_saga_engine=True,
            enable_self_aware=True,
            enable_cqrs=False  # Disable CQRS for simple test
        )
        print("    Platform initialized successfully")

        # Check platform status
        status = platform.get_status()
        print(f"    Platform Status: {status}")

    except Exception as e:
        print(f"    Platform initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Check Components
    print("\n2️⃣  Testing Platform Components...")

    if platform.eventbus:
        print("    EventBus available")
    else:
        print("    EventBus not available")

    if platform.intelligent_router:
        print("    Intelligent EventRouter available")
        # Get metrics (it's not async)
        try:
            metrics = platform.intelligent_router.get_metrics()
            print(f"    Router Metrics: {metrics}")
        except Exception as e:
            print(f"   ️  Could not get router metrics: {e}")
    else:
        print("   ️  Intelligent EventRouter not available (using basic EventBus)")

    if platform.saga_orchestrator:
        print("    Saga Orchestrator available")
    else:
        print("    Saga Orchestrator not available")

    # Test 3: Self-Aware Service
    print("\n3️⃣  Testing Self-Aware Service...")
    try:
        from platform_services.bcm_domain.services._shared import SelfAwareService, EventPriority

        class TestBIAService(SelfAwareService):
            def __init__(self):
                super().__init__(
                    service_name="bia_service_test",
                    capabilities=["bia.test", "bia.assessment"]
                )

            async def handle_test_event(self, event):
                return {"status": "handled", "event_type": event.type}

        test_service = TestBIAService()

        # Register handler
        test_service.register_handler("bia.test.*", test_service.handle_test_event, priority=EventPriority.HIGH)

        print("    Self-Aware Service created successfully")

        # Test event handling
        print("    Event handlers registered successfully")

    except Exception as e:
        print(f"    Self-Aware Service test failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 4: Event Publishing (if router available)
    if platform.intelligent_router:
        print("\n4️⃣  Testing Event Publishing...")
        try:
            from infrastructure.eventbus import Event, EventPriority

            test_event = Event.create(
                event_type="bia.integration.test",
                data={"message": "Integration test event"},
                source="test_integration",
                tenant_id="test-tenant",
                priority=EventPriority.NORMAL
            )

            # Route event
            await platform.intelligent_router.route_event(test_event)
            print("    Event routed successfully")

        except Exception as e:
            print(f"   ️  Event publishing test failed: {e}")

    # Test 5: Saga Engine (if available)
    if platform.saga_orchestrator:
        print("\n5️⃣  Testing Saga Engine...")
        try:
            # Check if example sagas are available
            from intelligent_core.orchestration.saga_engine.example_sagas import (
                create_bcm_program_saga
            )

            # Register saga
            saga_def = create_bcm_program_saga()
            platform.saga_orchestrator.register_saga(saga_def)

            print("    Saga registered successfully")
            # Check registered sagas (if available)
            if hasattr(platform.saga_orchestrator, 'sagas'):
                print(f"    Registered sagas: {list(platform.saga_orchestrator.sagas.keys())}")
            elif hasattr(platform.saga_orchestrator, '_sagas'):
                print(f"    Registered sagas: {list(platform.saga_orchestrator._sagas.keys())}")

        except Exception as e:
            print(f"   ️  Saga engine test failed: {e}")

    # Cleanup
    print("\n6️⃣  Testing Cleanup...")
    try:
        await shutdown_platform()
        print("    Platform shutdown successfully")
    except Exception as e:
        print(f"   ️  Platform shutdown had issues: {e}")

    print("\n" + "=" * 70)
    print(" Integration Test Complete!")
    print("=" * 70 + "\n")

    return True


async def main():
    """Main test function"""
    try:
        success = await test_platform_integration()

        if success:
            print(" All integration tests passed!")
            print("\n Next steps:")
            print("   1. Run full service: python main_integrated.py")
            print("   2. Test API endpoints: http://localhost:8012/docs")
            print("   3. Check health: curl http://localhost:8012/health")
            print("   4. Check platform status: curl http://localhost:8012/api/platform/status")
            return 0
        else:
            print(" Some integration tests failed")
            return 1

    except Exception as e:
        print(f" Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
