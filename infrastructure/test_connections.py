"""
Test Script - Check Infrastructure Connections
Run: python infrastructure/test_connections.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from infrastructure.database.managers.supabase_client import supabase_manager
from infrastructure.database.managers.redis_client import redis_manager


async def test_supabase():
    """Test Supabase connection"""
    print("\n" + "="*60)
    print("🔍 Testing Supabase Connection...")
    print("="*60)

    try:
        # Connect
        await supabase_manager.connect()
        print("✅ Supabase client initialized")

        # Health check
        health = await supabase_manager.health_check()
        print(f"\n📊 Health Status:")
        print(f"   PostgreSQL: {'✅' if health['postgres'] else '❌'}")
        print(f"   Auth: {'✅' if health['auth'] else '❌'}")
        print(f"   Storage: {'✅' if health['storage'] else '❌'}")

        # Test query
        print(f"\n🔍 Testing database query...")
        async with supabase_manager.get_session() as session:
            result = await session.execute("SELECT current_database(), current_user, version()")
            row = result.fetchone()
            print(f"   Database: {row[0]}")
            print(f"   User: {row[1]}")
            print(f"   Version: {row[2][:50]}...")

        # List tables
        print(f"\n📋 Listing tables...")
        async with supabase_manager.get_session() as session:
            result = await session.execute("""
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schemaname, tablename
                LIMIT 10
            """)
            tables = result.fetchall()
            if tables:
                for schema, table in tables:
                    print(f"   {schema}.{table}")
            else:
                print("   ⚠️  No tables found (migrations not applied yet)")

        print("\n✅ Supabase tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Supabase test failed: {e}")
        return False
    finally:
        await supabase_manager.disconnect()


async def test_redis():
    """Test Redis connection"""
    print("\n" + "="*60)
    print("🔍 Testing Redis Connection...")
    print("="*60)

    try:
        # Connect
        await redis_manager.connect()
        print("✅ Redis client initialized")

        # Health check
        health = await redis_manager.health_check()
        print(f"   Health: {'✅ OK' if health else '❌ Failed'}")

        # Test operations
        print(f"\n🔍 Testing Redis operations...")

        # SET
        test_key = "test:connection"
        test_value = {"status": "ok", "timestamp": "2025-10-02"}
        await redis_manager.set(test_key, test_value, ttl=60)
        print(f"   ✅ SET {test_key}")

        # GET
        retrieved = await redis_manager.get(test_key)
        print(f"   ✅ GET {test_key}: {retrieved}")

        # EXISTS
        exists = await redis_manager.exists(test_key)
        print(f"   ✅ EXISTS {test_key}: {exists}")

        # TTL
        ttl = await redis_manager.ttl(test_key)
        print(f"   ✅ TTL {test_key}: {ttl}s")

        # DELETE
        deleted = await redis_manager.delete(test_key)
        print(f"   ✅ DELETE {test_key}: {deleted}")

        # Test rate limiting
        print(f"\n🔍 Testing rate limiting...")
        rate_key = "test:rate_limit"
        for i in range(1, 6):
            allowed = await redis_manager.rate_limit(rate_key, max_requests=3, window_seconds=10)
            status = "✅ Allowed" if allowed else "❌ Rate limited"
            print(f"   Request {i}: {status}")

        # Cleanup
        await redis_manager.delete(rate_key)

        print("\n✅ Redis tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Redis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await redis_manager.disconnect()


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 Infrastructure Connection Tests")
    print("="*60)

    # Check environment variables
    print("\n📋 Checking environment variables...")
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "DATABASE_URL",
        "REDIS_HOST",
        "REDIS_PORT"
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PASSWORD" in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: NOT SET")
            missing.append(var)

    if missing:
        print(f"\n❌ Missing required environment variables: {', '.join(missing)}")
        print("   Please update .env file")
        return

    # Run tests
    results = []

    # Test Supabase
    supabase_ok = await test_supabase()
    results.append(("Supabase", supabase_ok))

    # Test Redis
    redis_ok = await test_redis()
    results.append(("Redis", redis_ok))

    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    for name, ok in results:
        status = "✅ PASSED" if ok else "❌ FAILED"
        print(f"   {name}: {status}")

    all_passed = all(ok for _, ok in results)
    if all_passed:
        print("\n✅ All tests passed! Infrastructure is ready.")
    else:
        print("\n❌ Some tests failed. Please check errors above.")

    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
