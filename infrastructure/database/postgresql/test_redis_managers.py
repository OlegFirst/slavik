"""
Test Redis Managers
Tests for CacheManager, SessionStore, and RateLimiter
"""

import asyncio
import time
from managers.redis_client import redis_manager
from managers.cache_manager import cache_manager, cache_user
from managers.session_store import session_store
from managers.rate_limiter import rate_limiter, RateLimitStrategy


async def test_cache_manager():
    """Test Cache Manager"""
    print("\n" + "="*70)
    print(" Testing Cache Manager")
    print("="*70)

    # Test decorator
    @cache_user(ttl=5)
    async def get_user_data(user_id: str):
        print(f"   Fetching user {user_id} from database...")
        await asyncio.sleep(0.1)  # Simulate DB query
        return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}

    # First call - cache miss
    print("\n1️⃣  First call (should hit database):")
    result1 = await get_user_data("123")
    print(f"   Result: {result1}")

    # Second call - cache hit
    print("\n2️⃣  Second call (should hit cache):")
    result2 = await get_user_data("123")
    print(f"   Result: {result2}")

    # Check stats
    print("\n Cache Stats:")
    stats = cache_manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test invalidation
    print("\n3️⃣  Invalidating cache...")
    await get_user_data.invalidate("123")
    result3 = await get_user_data("123")
    print(f"   After invalidation (should hit database again)")

    # Test get_or_set
    print("\n4️⃣  Testing get_or_set...")
    async def expensive_computation():
        await asyncio.sleep(0.1)
        return {"result": "computed"}

    value = await cache_manager.get_or_set("expensive:key", expensive_computation, ttl=60)
    print(f"   Computed value: {value}")

    value2 = await cache_manager.get_or_set("expensive:key", expensive_computation, ttl=60)
    print(f"   Cached value: {value2}")


async def test_session_store():
    """Test Session Store"""
    print("\n" + "="*70)
    print(" Testing Session Store")
    print("="*70)

    # Create session
    print("\n1️⃣  Creating session...")
    session_id = await session_store.create_session(
        user_id="user_123",
        session_data={"username": "john_doe", "role": "admin"},
        ttl=300,  # 5 minutes
        device_info={"device_type": "desktop", "browser": "Chrome"}
    )
    print(f"   Session created: {session_id[:16]}...")

    # Get session
    print("\n2️⃣  Retrieving session...")
    session = await session_store.get_session(session_id)
    print(f"   User ID: {session['user_id']}")
    print(f"   Username: {session['data']['username']}")
    print(f"   Created: {session['created_at']}")

    # Update session
    print("\n3️⃣  Updating session...")
    await session_store.update_session(session_id, {"last_page": "/dashboard"})
    updated_session = await session_store.get_session(session_id)
    print(f"   Last page: {updated_session['data'].get('last_page')}")

    # Create another session for same user
    print("\n4️⃣  Creating second session (different device)...")
    session_id2 = await session_store.create_session(
        user_id="user_123",
        session_data={"username": "john_doe", "role": "admin"},
        device_info={"device_type": "mobile", "browser": "Safari"}
    )

    # Get all user sessions
    print("\n5️⃣  Getting all user sessions...")
    user_sessions = await session_store.get_user_sessions("user_123")
    print(f"   Active sessions: {len(user_sessions)}")
    for s in user_sessions:
        device = s['device_info'].get('device_type', 'unknown')
        print(f"     - {device}: {s['session_id'][:16]}...")

    # Validate session
    print("\n6️⃣  Validating session...")
    is_valid, user_id = await session_store.validate_session(session_id)
    print(f"   Valid: {is_valid}, User: {user_id}")

    # Delete session
    print("\n7️⃣  Deleting session...")
    await session_store.delete_session(session_id)
    is_valid_after, _ = await session_store.validate_session(session_id)
    print(f"   Valid after delete: {is_valid_after}")

    # Cleanup
    await session_store.delete_all_user_sessions("user_123")


async def test_rate_limiter():
    """Test Rate Limiter"""
    print("\n" + "="*70)
    print(" Testing Rate Limiter")
    print("="*70)

    # Test Fixed Window
    print("\n1️⃣  Fixed Window (5 requests per 10 seconds):")
    for i in range(7):
        allowed, info = await rate_limiter.check_rate_limit(
            identifier="user_456",
            resource="api:test",
            max_requests=5,
            window_seconds=10,
            strategy=RateLimitStrategy.FIXED_WINDOW
        )
        status = " ALLOWED" if allowed else " BLOCKED"
        print(f"  Request {i+1}: {status} - Remaining: {info['remaining']}, Reset: {info['reset_at']}")

    # Reset for next test
    await rate_limiter.reset_rate_limit("user_456", "api:test")

    # Test Sliding Window
    print("\n2️⃣  Sliding Window (3 requests per 5 seconds):")
    for i in range(5):
        allowed, info = await rate_limiter.check_rate_limit(
            identifier="user_789",
            resource="api:sliding",
            max_requests=3,
            window_seconds=5,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        )
        status = " ALLOWED" if allowed else " BLOCKED"
        print(f"  Request {i+1}: {status} - Remaining: {info['remaining']}")
        await asyncio.sleep(0.5)

    # Test Token Bucket
    print("\n3️⃣  Token Bucket (10 tokens max, refill 2/sec):")
    for i in range(12):
        allowed, info = await rate_limiter.check_rate_limit_token_bucket(
            identifier="user_bucket",
            resource="api:bucket",
            max_tokens=10,
            refill_rate=2.0,
            cost=1
        )
        status = " ALLOWED" if allowed else " BLOCKED"
        print(f"  Request {i+1}: {status} - Tokens: {info['tokens_remaining']}/{info['max_tokens']}")
        await asyncio.sleep(0.3)


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" Redis Managers Test Suite")
    print("="*70)

    # Connect to Redis
    print("\n Connecting to Redis...")
    await redis_manager.connect()
    print(" Connected!")

    try:
        # Run tests
        await test_cache_manager()
        await test_session_store()
        await test_rate_limiter()

        print("\n" + "="*70)
        print(" ALL TESTS PASSED!")
        print("="*70)

    finally:
        # Disconnect
        print("\n Disconnecting from Redis...")
        await redis_manager.disconnect()
        print(" Disconnected!")


if __name__ == "__main__":
    asyncio.run(main())
