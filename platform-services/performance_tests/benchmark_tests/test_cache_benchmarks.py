"""
Cache Performance Benchmark Tests
==================================

Benchmark Redis cache operations: hit ratio, read/write latency, invalidation.

Usage:
    pytest benchmark_tests/test_cache_benchmarks.py --benchmark-only
"""

import pytest
import asyncio
import redis.asyncio as redis
import os
from dotenv import load_dotenv
import random
import string

# Load environment variables
load_dotenv('.env.perf')

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def redis_client():
    """Create Redis client"""
    client = redis.from_url(REDIS_URL, decode_responses=True)
    yield client
    await client.close()


def generate_random_key(prefix="benchmark"):
    """Generate random cache key"""
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{prefix}:{suffix}"


# ============================================================================
# Basic Cache Operation Benchmarks
# ============================================================================

def test_cache_set_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Cache SET operation"""

    async def cache_set():
        key = generate_random_key()
        await redis_client.set(key, "benchmark_value", ex=300)

    benchmark(event_loop.run_until_complete, cache_set())


def test_cache_get_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Cache GET operation"""

    # Setup: Create key first
    key = "benchmark:get_test"

    async def setup():
        await redis_client.set(key, "benchmark_value", ex=300)

    event_loop.run_until_complete(setup())

    async def cache_get():
        value = await redis_client.get(key)
        return value

    result = benchmark(event_loop.run_until_complete, cache_get())
    assert result == "benchmark_value"


def test_cache_delete_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Cache DELETE operation"""

    async def cache_delete():
        key = generate_random_key()
        await redis_client.set(key, "value")
        await redis_client.delete(key)

    benchmark(event_loop.run_until_complete, cache_delete())


def test_cache_exists_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Cache EXISTS check"""

    key = "benchmark:exists_test"

    async def setup():
        await redis_client.set(key, "value", ex=300)

    event_loop.run_until_complete(setup())

    async def cache_exists():
        exists = await redis_client.exists(key)
        return exists

    result = benchmark(event_loop.run_until_complete, cache_exists())
    assert result > 0


# ============================================================================
# Cache Hit/Miss Benchmarks
# ============================================================================

def test_cache_hit_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Cache hit (key exists)"""

    key = "benchmark:hit_test"

    async def setup():
        await redis_client.set(key, "cached_value", ex=300)

    event_loop.run_until_complete(setup())

    async def cache_hit():
        value = await redis_client.get(key)
        return value is not None

    result = benchmark(event_loop.run_until_complete, cache_hit())
    assert result is True


def test_cache_miss_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Cache miss (key doesn't exist)"""

    async def cache_miss():
        key = generate_random_key("miss")
        value = await redis_client.get(key)
        return value is None

    result = benchmark(event_loop.run_until_complete, cache_miss())
    assert result is True


# ============================================================================
# Complex Data Structure Benchmarks
# ============================================================================

def test_cache_hash_set_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Hash SET operation"""

    async def hash_set():
        key = generate_random_key("hash")
        await redis_client.hset(key, mapping={
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        })
        await redis_client.expire(key, 300)

    benchmark(event_loop.run_until_complete, hash_set())


def test_cache_hash_get_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Hash GET operation"""

    key = "benchmark:hash_test"

    async def setup():
        await redis_client.hset(key, mapping={
            "field1": "value1",
            "field2": "value2"
        })
        await redis_client.expire(key, 300)

    event_loop.run_until_complete(setup())

    async def hash_get():
        value = await redis_client.hget(key, "field1")
        return value

    result = benchmark(event_loop.run_until_complete, hash_get())
    assert result == "value1"


def test_cache_list_push_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: List PUSH operation"""

    async def list_push():
        key = generate_random_key("list")
        await redis_client.rpush(key, "item1", "item2", "item3")
        await redis_client.expire(key, 300)

    benchmark(event_loop.run_until_complete, list_push())


def test_cache_list_range_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: List RANGE operation"""

    key = "benchmark:list_test"

    async def setup():
        await redis_client.rpush(key, "item1", "item2", "item3", "item4", "item5")
        await redis_client.expire(key, 300)

    event_loop.run_until_complete(setup())

    async def list_range():
        items = await redis_client.lrange(key, 0, -1)
        return items

    result = benchmark(event_loop.run_until_complete, list_range())
    assert len(result) > 0


# ============================================================================
# TTL and Expiration Benchmarks
# ============================================================================

def test_cache_set_with_expiry_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: SET with expiration"""

    async def set_with_expiry():
        key = generate_random_key("expiry")
        await redis_client.setex(key, 300, "value_with_ttl")

    benchmark(event_loop.run_until_complete, set_with_expiry())


def test_cache_ttl_check_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: TTL check"""

    key = "benchmark:ttl_test"

    async def setup():
        await redis_client.setex(key, 300, "value")

    event_loop.run_until_complete(setup())

    async def check_ttl():
        ttl = await redis_client.ttl(key)
        return ttl

    result = benchmark(event_loop.run_until_complete, check_ttl())
    assert result > 0


# ============================================================================
# Pipeline Benchmarks
# ============================================================================

def test_cache_pipeline_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Pipeline operations"""

    async def pipeline_ops():
        pipe = redis_client.pipeline()
        for i in range(10):
            key = f"benchmark:pipe:{i}"
            pipe.set(key, f"value_{i}", ex=300)
        await pipe.execute()

    benchmark(event_loop.run_until_complete, pipeline_ops())


# ============================================================================
# Bulk Operations Benchmarks
# ============================================================================

def test_cache_bulk_set_10_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Bulk SET 10 keys"""

    async def bulk_set():
        pipe = redis_client.pipeline()
        for i in range(10):
            key = generate_random_key("bulk10")
            pipe.set(key, f"value_{i}", ex=300)
        await pipe.execute()

    benchmark(event_loop.run_until_complete, bulk_set())


def test_cache_bulk_set_100_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Bulk SET 100 keys"""

    async def bulk_set():
        pipe = redis_client.pipeline()
        for i in range(100):
            key = generate_random_key("bulk100")
            pipe.set(key, f"value_{i}", ex=300)
        await pipe.execute()

    benchmark(event_loop.run_until_complete, bulk_set())


def test_cache_bulk_get_10_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Bulk GET 10 keys"""

    keys = []

    async def setup():
        nonlocal keys
        pipe = redis_client.pipeline()
        for i in range(10):
            key = f"benchmark:bulkget10:{i}"
            keys.append(key)
            pipe.set(key, f"value_{i}", ex=300)
        await pipe.execute()

    event_loop.run_until_complete(setup())

    async def bulk_get():
        pipe = redis_client.pipeline()
        for key in keys:
            pipe.get(key)
        results = await pipe.execute()
        return results

    result = benchmark(event_loop.run_until_complete, bulk_get())
    assert len(result) == 10


# ============================================================================
# Cache Invalidation Benchmarks
# ============================================================================

def test_cache_pattern_delete_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: Pattern-based deletion"""

    async def setup():
        # Create keys with pattern
        pipe = redis_client.pipeline()
        for i in range(10):
            key = f"benchmark:pattern:delete:{i}"
            pipe.set(key, f"value_{i}", ex=300)
        await pipe.execute()

    event_loop.run_until_complete(setup())

    async def pattern_delete():
        # Find and delete keys matching pattern
        cursor = 0
        keys_to_delete = []
        while True:
            cursor, keys = await redis_client.scan(
                cursor,
                match="benchmark:pattern:delete:*",
                count=100
            )
            keys_to_delete.extend(keys)
            if cursor == 0:
                break

        if keys_to_delete:
            await redis_client.delete(*keys_to_delete)

    benchmark(event_loop.run_until_complete, pattern_delete())


# ============================================================================
# Connection Benchmarks
# ============================================================================

def test_cache_ping_benchmark(benchmark, event_loop, redis_client):
    """Benchmark: PING command (connection health)"""

    async def cache_ping():
        response = await redis_client.ping()
        return response

    result = benchmark(event_loop.run_until_complete, cache_ping())
    assert result is True
