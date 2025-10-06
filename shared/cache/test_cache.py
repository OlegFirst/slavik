"""
Unit tests for Redis cache module
Tests basic cache operations, tenant isolation, and metrics
"""

import pytest
import asyncio
from redis_cache import RedisCache, init_cache, cached


@pytest.fixture
async def cache():
    """Setup Redis cache for testing"""
    cache = RedisCache("redis://localhost:6379/15")  # Use database 15 for testing
    yield cache
    # Cleanup: Clear all test keys
    await cache.clear_pattern("*")
    await cache.close()


@pytest.mark.asyncio
async def test_basic_set_get(cache):
    """Test basic set and get operations"""
    # Set a value
    success = await cache.set("test_key", {"data": "value"}, ttl=60)
    assert success is True

    # Get the value
    value = await cache.get("test_key")
    assert value == {"data": "value"}


@pytest.mark.asyncio
async def test_tenant_isolation(cache):
    """Test that tenant namespacing works correctly"""
    # Set values for different tenants
    await cache.set("user:123", {"name": "John"}, tenant_id="tenant1")
    await cache.set("user:123", {"name": "Jane"}, tenant_id="tenant2")

    # Get values - should be isolated by tenant
    tenant1_data = await cache.get("user:123", tenant_id="tenant1")
    tenant2_data = await cache.get("user:123", tenant_id="tenant2")

    assert tenant1_data["name"] == "John"
    assert tenant2_data["name"] == "Jane"


@pytest.mark.asyncio
async def test_cache_miss(cache):
    """Test cache miss returns None"""
    value = await cache.get("nonexistent_key")
    assert value is None


@pytest.mark.asyncio
async def test_delete(cache):
    """Test delete operation"""
    # Set and verify
    await cache.set("delete_me", "value")
    assert await cache.exists("delete_me") is True

    # Delete
    deleted = await cache.delete("delete_me")
    assert deleted is True
    assert await cache.exists("delete_me") is False


@pytest.mark.asyncio
async def test_ttl(cache):
    """Test TTL functionality"""
    # Set with 2 second TTL
    await cache.set("ttl_test", "value", ttl=2)

    # Should exist immediately
    assert await cache.exists("ttl_test") is True

    # Wait for expiration
    await asyncio.sleep(3)

    # Should not exist
    assert await cache.exists("ttl_test") is False


@pytest.mark.asyncio
async def test_metrics(cache):
    """Test cache metrics tracking"""
    # Reset metrics
    cache.reset_metrics()

    # Generate some hits and misses
    await cache.set("metric_key", "value")
    await cache.get("metric_key")  # Hit
    await cache.get("nonexistent")  # Miss
    await cache.get("metric_key")  # Hit

    # Check metrics
    metrics = cache.get_metrics()
    assert metrics["hits"] == 2
    assert metrics["misses"] == 1
    assert metrics["sets"] == 1
    assert metrics["hit_rate"] == 2/3  # 2 hits out of 3 requests


@pytest.mark.asyncio
async def test_clear_pattern(cache):
    """Test clearing keys by pattern"""
    # Set multiple keys
    await cache.set("user:1", "data1", tenant_id="tenant1")
    await cache.set("user:2", "data2", tenant_id="tenant1")
    await cache.set("order:1", "order1", tenant_id="tenant1")

    # Clear only user keys
    deleted = await cache.clear_pattern("user:*", tenant_id="tenant1")
    assert deleted == 2

    # Verify user keys are gone but order key remains
    assert await cache.exists("user:1", tenant_id="tenant1") is False
    assert await cache.exists("user:2", tenant_id="tenant1") is False
    assert await cache.exists("order:1", tenant_id="tenant1") is True


@pytest.mark.asyncio
async def test_cached_decorator():
    """Test the @cached decorator"""
    call_count = 0

    @cached(ttl=60, key_prefix="test")
    async def expensive_function(tenant_id: str, user_id: int):
        nonlocal call_count
        call_count += 1
        return {"user_id": user_id, "data": f"expensive_result_{call_count}"}

    # First call - should execute function
    result1 = await expensive_function(tenant_id="tenant1", user_id=123)
    assert call_count == 1
    assert result1["user_id"] == 123

    # Second call with same args - should use cache
    result2 = await expensive_function(tenant_id="tenant1", user_id=123)
    assert call_count == 1  # Function not called again
    assert result2 == result1  # Same result from cache

    # Call with different args - should execute function
    result3 = await expensive_function(tenant_id="tenant1", user_id=456)
    assert call_count == 2
    assert result3["user_id"] == 456


@pytest.mark.asyncio
async def test_ping(cache):
    """Test Redis connection ping"""
    is_alive = await cache.ping()
    assert is_alive is True


@pytest.mark.asyncio
async def test_json_serialization(cache):
    """Test JSON serialization of complex objects"""
    complex_data = {
        "string": "value",
        "number": 42,
        "float": 3.14,
        "list": [1, 2, 3],
        "nested": {"key": "value"},
        "null": None
    }

    await cache.set("complex", complex_data)
    retrieved = await cache.get("complex")

    assert retrieved == complex_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
