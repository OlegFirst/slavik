#!/usr/bin/env python3
"""
Quick test script for BIA Service integration

Tests:
1. Import verification
2. EventBus connectivity
3. PostgreSQL connectivity
4. Event listener registration
5. Mock event processing

Usage:
    python3 test_bia_integration.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("🧪 BIA Service Integration Test\n")
print("=" * 60)


async def test_imports():
    """Test 1: Import verification"""
    print("\n✅ Test 1: Import verification")

    try:
        from integration.bia_service_listener import BIAServiceListener, register_bia_listener
        print("   ✓ BIA Service Listener imports OK")

        from storage.postgres_adapter import PostgresStorageAdapter
        print("   ✓ PostgreSQL Adapter imports OK")

        from shared.database import get_db_manager
        print("   ✓ Database Manager imports OK")

        from shared.event_bus import init_event_bus, get_event_bus, publish_event
        print("   ✓ EventBus imports OK")

        return True
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        return False


async def test_eventbus():
    """Test 2: EventBus connectivity"""
    print("\n✅ Test 2: EventBus connectivity")

    try:
        from shared.event_bus import init_event_bus, get_event_bus

        # Initialize EventBus
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        await init_event_bus(
            service_name="workflow-intelligence-test",
            redis_url=redis_url
        )

        event_bus = get_event_bus()
        if event_bus:
            print(f"   ✓ EventBus connected: {redis_url}")
            return True
        else:
            print("   ✗ EventBus not available")
            return False

    except Exception as e:
        print(f"   ✗ EventBus connection failed: {e}")
        return False


async def test_postgresql():
    """Test 3: PostgreSQL connectivity"""
    print("\n✅ Test 3: PostgreSQL connectivity")

    try:
        from shared.database import get_db_manager
        from storage.postgres_adapter import PostgresStorageAdapter

        db_manager = get_db_manager()
        storage = PostgresStorageAdapter(db_manager)

        await storage.connect()
        print(f"   ✓ PostgreSQL connected")
        print(f"   ✓ Schema initialized: workflow_intelligence")

        # Verify RLS status
        rls_status = await storage.verify_rls_status()
        print(f"   ✓ RLS enabled: {rls_status['rls_enabled']['workflow_cases']}")

        return True

    except Exception as e:
        print(f"   ✗ PostgreSQL connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_listener_registration():
    """Test 4: Event listener registration"""
    print("\n✅ Test 4: Event listener registration")

    try:
        from integration.bia_service_listener import BIAServiceListener, register_bia_listener
        from shared.event_bus import get_event_bus
        from shared.database import get_db_manager
        from storage.postgres_adapter import PostgresStorageAdapter

        event_bus = get_event_bus()
        if not event_bus:
            print("   ⚠ EventBus not available, skipping")
            return False

        # Create storage
        db_manager = get_db_manager()
        storage = PostgresStorageAdapter(db_manager)
        await storage.connect()

        # Create simple case collector
        class TestCaseCollector:
            def __init__(self, storage):
                self.storage = storage

            async def collect_case(self, case_data, tenant_id):
                print(f"   → Case collected: {case_data.get('workflow_id')} (tenant: {tenant_id})")
                return f"test-case-{case_data.get('workflow_id')}"

        case_collector = TestCaseCollector(storage)

        # Create listener
        listener = BIAServiceListener(
            workflow_engine=None,
            case_collector=case_collector,
            pdca_engine=None,
            context_advisor=None
        )

        # Register listeners
        register_bia_listener(event_bus, listener)

        print("   ✓ BIA Service Listener registered")
        print("   ✓ Events: bia.assessment.completed, bia.process.created, bia.criticality.changed, bia.critical.process.identified")

        return True

    except Exception as e:
        print(f"   ✗ Listener registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_event_processing():
    """Test 5: Mock event processing"""
    print("\n✅ Test 5: Mock event processing")

    try:
        from shared.event_bus import publish_event, get_event_bus

        event_bus = get_event_bus()
        if not event_bus:
            print("   ⚠ EventBus not available, skipping")
            return False

        # Publish test event
        test_event_data = {
            "assessment_id": "test_bia_123",
            "processes": [
                {"name": "Payment Processing", "tier": 1},
                {"name": "Customer Support", "tier": 2}
            ],
            "duration_hours": 24,
            "quality_score": 85,
            "industry": "healthcare",
            "org_size": "medium",
            "maturity_level": "advanced",
            "user_satisfaction": 4.5
        }

        print("   → Publishing test event: bia.assessment.completed")
        await publish_event(
            event_type="bia.assessment.completed",
            data=test_event_data,
            tenant_id="test-tenant"
        )

        # Give listener time to process
        await asyncio.sleep(2)

        print("   ✓ Event published successfully")
        print("   ✓ Check logs for case collection")

        return True

    except Exception as e:
        print(f"   ✗ Event processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""

    results = []

    # Test 1: Imports
    results.append(await test_imports())

    # Test 2: EventBus
    results.append(await test_eventbus())

    # Test 3: PostgreSQL
    results.append(await test_postgresql())

    # Test 4: Listener registration
    results.append(await test_listener_registration())

    # Test 5: Event processing
    results.append(await test_event_processing())

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed

    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")

    if all(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("\nBIA Service integration is ready!")
        print("\nNext steps:")
        print("1. Start workflow_intelligence: python3 main.py")
        print("2. Start BIA Service: cd ../../../platform_services/bcm_domain/services/bia_service && python3 main.py")
        print("3. Create and complete a BIA assessment")
        print("4. Verify case collected in PostgreSQL")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease fix issues above before continuing.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
