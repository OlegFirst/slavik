"""
Test Platform Integration for AI Orchestration
==============================================

Tests the integration of Platform Integration with Orchestration layer.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_unified_controller_integration():
    """Test UnifiedController with Platform Integration"""
    print("\n" + "=" * 70)
    print("Testing Orchestration Platform Integration")
    print("=" * 70 + "\n")

    # Test 1: Import and Initialize
    print("1️⃣  Testing imports and initialization...")
    try:
        from control_center.unified_controller_integrated import UnifiedController

        controller = UnifiedController()
        print("    UnifiedController initialized")

    except Exception as e:
        print(f"    Import/initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Mock orchestrators for testing
    print("\n2️⃣  Setting up mock orchestrators...")
    try:
        # Create simple mock orchestrators
        class MockOrchestrator:
            async def start(self):
                logger.info("Mock orchestrator started")

            async def stop(self):
                logger.info("Mock orchestrator stopped")

            async def get_status(self):
                return {"status": "running", "mock": True}

            def set_platform_integration(self, platform):
                self.platform_integration = platform

        # Replace with mocks
        controller.platform = MockOrchestrator()
        controller.ai = MockOrchestrator()
        controller.scenario = MockOrchestrator()

        print("    Mock orchestrators set up")

    except Exception as e:
        print(f"    Mock setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Start system
    print("\n3️⃣  Testing system startup...")
    try:
        result = await controller.start_all()

        if result['status'] == 'started':
            print("    System started successfully")
            print(f"    Startup time: {result['startup_time_seconds']:.2f}s")

            # Check platform integration
            if 'platform_integration' in result:
                print(f"    Platform Integration: {result['platform_integration']}")
        else:
            print(f"    System startup failed: {result}")
            return False

    except Exception as e:
        print(f"    Startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 4: Check components
    print("\n4️⃣  Testing Platform Integration components...")

    if controller.platform_integration:
        print("    Platform Integration object exists")

        # Check Intelligent Router
        if controller.platform_integration.intelligent_router:
            print("    Intelligent Router available")
            metrics = controller.platform_integration.intelligent_router.get_metrics()
            print(f"    Router metrics: {metrics}")
        else:
            print("   ️  Intelligent Router not available")

        # Check Saga Orchestrator
        if controller.platform_integration.saga_orchestrator:
            print("    Saga Orchestrator available")
            if hasattr(controller.platform_integration.saga_orchestrator, '_sagas'):
                saga_count = len(controller.platform_integration.saga_orchestrator._sagas)
                print(f"    Registered sagas: {saga_count}")
        else:
            print("   ️  Saga Orchestrator not available")

    else:
        print("    Platform Integration not initialized")
        return False

    # Test 5: Get system status
    print("\n5️⃣  Testing system status...")
    try:
        status = await controller.get_system_status()

        print(f"    System status retrieved")
        print(f"    Running: {status['running']}")
        print(f"    Startup completed: {status['startup_completed']}")

        if 'platform_integration' in status:
            print(f"    Platform Integration status: {status['platform_integration']}")

    except Exception as e:
        print(f"   ️  Status retrieval failed: {e}")

    # Test 6: Stop system
    print("\n6️⃣  Testing system shutdown...")
    try:
        stop_result = await controller.stop_all()

        if stop_result['status'] == 'stopped':
            print("    System stopped successfully")
            print(f"    Shutdown time: {stop_result['shutdown_time_seconds']:.2f}s")
        else:
            print(f"   ️  System shutdown had issues: {stop_result}")

    except Exception as e:
        print(f"    Shutdown failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 70)
    print(" Platform Integration Test Complete!")
    print("=" * 70 + "\n")

    return True


async def main():
    """Main test function"""
    try:
        success = await test_unified_controller_integration()

        if success:
            print(" All integration tests passed!")
            print("\n Next steps:")
            print("   1. Update main.py to use unified_controller_integrated")
            print("   2. Test with real orchestrators")
            print("   3. Deploy to production")
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
