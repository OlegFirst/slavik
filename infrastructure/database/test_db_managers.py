"""
Test Database Managers
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from managers.db_manager import (
    system_db, platform_db, business_db,
    initialize_all_databases, shutdown_all_databases,
    health_check_all, MigrationRunner, RLSManager
)
import asyncio


async def test_connection_managers():
    """Test all database connection managers"""

    print("=" * 70)
    print("🧪 Testing Database Connection Managers")
    print("=" * 70)

    # 1. Initialize all databases
    print("\n1️⃣  Initializing database connections...")
    await initialize_all_databases()

    # 2. Health check
    print("\n2️⃣  Running health checks...")
    health = await health_check_all()

    for db_name, status in health.items():
        print(f"\n{db_name}:")
        for key, value in status.items():
            icon = "✅" if (key == "connected" and value) or (key == "error" and not value) else "❌" if key == "error" and value else "📊"
            print(f"  {icon} {key}: {value}")

    # 3. Test BusinessDB queries
    print("\n3️⃣  Testing BusinessDB queries...")

    try:
        # Test simple query
        result = business_db.execute("SELECT COUNT(*) FROM public.organizations", commit=False)
        org_count = result[0][0] if result else 0
        print(f"  ✅ Organizations count: {org_count}")

        # Test with RLS context
        with business_db.get_cursor() as cur:
            # Set RLS context (simulated user)
            test_user_id = "00000000-0000-0000-0000-000000000000"
            test_tenant_id = "00000000-0000-0000-0000-000000000000"

            RLSManager.set_rls_context(cur, test_user_id, test_tenant_id)

            cur.execute("SHOW app.current_user_id")
            current_user = cur.fetchone()[0]
            print(f"  ✅ RLS context set: user_id = {current_user}")

            RLSManager.clear_rls_context(cur)
            print(f"  ✅ RLS context cleared")

    except Exception as e:
        print(f"  ❌ Query test failed: {e}")

    # 4. Test Migration Runner
    print("\n4️⃣  Testing Migration Runner...")

    try:
        runner = MigrationRunner(business_db)
        applied = runner.get_applied_migrations()
        print(f"  ✅ Applied migrations: {len(applied)}")
        if applied:
            print(f"     Latest: {applied[-1]}")

    except Exception as e:
        print(f"  ❌ Migration runner test failed: {e}")

    # 5. Cleanup
    print("\n5️⃣  Shutting down connections...")
    await shutdown_all_databases()

    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_connection_managers())
