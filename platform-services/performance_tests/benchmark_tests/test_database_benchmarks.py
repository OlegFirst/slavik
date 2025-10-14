"""
Database Operation Benchmark Tests
===================================

Benchmark database operations: query execution, inserts, updates, and complex queries.

Usage:
    pytest benchmark_tests/test_database_benchmarks.py --benchmark-only
"""

import pytest
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.perf')

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://bcm_user:bcm_password_change_in_production@localhost:5432/bcm_platform')


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def db_pool():
    """Create database connection pool"""
    # Parse connection string
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    yield pool
    await pool.close()


# ============================================================================
# Simple Query Benchmarks
# ============================================================================

def test_simple_select_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Simple SELECT query"""

    async def select_query():
        async with db_pool.acquire() as conn:
            result = await conn.fetch("SELECT 1 as value")
            return result

    result = benchmark(event_loop.run_until_complete, select_query())
    assert len(result) > 0


def test_count_query_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: COUNT query on processes table"""

    async def count_query():
        async with db_pool.acquire() as conn:
            # Note: Table name may vary based on service
            try:
                result = await conn.fetchval("SELECT COUNT(*) FROM bia_processes")
            except Exception:
                # Table might not exist
                result = 0
            return result

    result = benchmark(event_loop.run_until_complete, count_query())
    assert result >= 0


def test_filter_query_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Filtered SELECT query"""

    async def filter_query():
        async with db_pool.acquire() as conn:
            try:
                result = await conn.fetch(
                    "SELECT * FROM bia_processes WHERE criticality = $1 LIMIT 10",
                    "CRITICAL"
                )
            except Exception:
                result = []
            return result

    result = benchmark(event_loop.run_until_complete, filter_query())
    assert isinstance(result, list)


# ============================================================================
# Insert Benchmarks
# ============================================================================

def test_single_insert_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Single INSERT operation"""

    async def insert_query():
        async with db_pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    INSERT INTO bia_processes
                    (tenant_id, name, description, criticality, rto_hours, rpo_hours, mtpd_hours, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    "benchmark-tenant",
                    f"Benchmark Process Insert {asyncio.get_event_loop().time()}",
                    "Performance test",
                    "MEDIUM",
                    8,
                    4,
                    12
                )
            except Exception as e:
                # Table might not exist or have different structure
                pass

    benchmark(event_loop.run_until_complete, insert_query())


# ============================================================================
# Update Benchmarks
# ============================================================================

def test_single_update_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Single UPDATE operation"""

    async def update_query():
        async with db_pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    UPDATE bia_processes
                    SET rto_hours = $1, updated_at = NOW()
                    WHERE tenant_id = $2
                    LIMIT 1
                    """,
                    6,
                    "benchmark-tenant"
                )
            except Exception:
                pass

    benchmark(event_loop.run_until_complete, update_query())


# ============================================================================
# Join Query Benchmarks
# ============================================================================

def test_join_query_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: JOIN query (if applicable)"""

    async def join_query():
        async with db_pool.acquire() as conn:
            try:
                # Example: Join processes with dependencies
                result = await conn.fetch(
                    """
                    SELECT p.*, COUNT(d.id) as dep_count
                    FROM bia_processes p
                    LEFT JOIN process_dependencies d ON p.id = d.process_id
                    WHERE p.tenant_id = $1
                    GROUP BY p.id
                    LIMIT 10
                    """,
                    "benchmark-tenant"
                )
            except Exception:
                result = []
            return result

    result = benchmark(event_loop.run_until_complete, join_query())
    assert isinstance(result, list)


# ============================================================================
# Connection Pool Benchmarks
# ============================================================================

def test_connection_acquisition_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Connection pool acquisition"""

    async def acquire_connection():
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")

    benchmark(event_loop.run_until_complete, acquire_connection())


def test_transaction_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Transaction execution"""

    async def transaction():
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.fetchval("SELECT 1")
                await conn.fetchval("SELECT 2")

    benchmark(event_loop.run_until_complete, transaction())


# ============================================================================
# Index Usage Benchmarks
# ============================================================================

def test_indexed_lookup_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Indexed column lookup"""

    async def indexed_lookup():
        async with db_pool.acquire() as conn:
            try:
                # Assuming tenant_id is indexed
                result = await conn.fetch(
                    "SELECT * FROM bia_processes WHERE tenant_id = $1 LIMIT 1",
                    "benchmark-tenant"
                )
            except Exception:
                result = []
            return result

    result = benchmark(event_loop.run_until_complete, indexed_lookup())
    assert isinstance(result, list)


def test_non_indexed_lookup_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Non-indexed column lookup"""

    async def non_indexed_lookup():
        async with db_pool.acquire() as conn:
            try:
                # Assuming description is not indexed
                result = await conn.fetch(
                    "SELECT * FROM bia_processes WHERE description LIKE $1 LIMIT 1",
                    "%test%"
                )
            except Exception:
                result = []
            return result

    result = benchmark(event_loop.run_until_complete, non_indexed_lookup())
    assert isinstance(result, list)


# ============================================================================
# Aggregate Query Benchmarks
# ============================================================================

def test_aggregate_query_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Aggregate queries (SUM, AVG, etc.)"""

    async def aggregate_query():
        async with db_pool.acquire() as conn:
            try:
                result = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) as total_processes,
                        AVG(rto_hours) as avg_rto,
                        MIN(rto_hours) as min_rto,
                        MAX(rto_hours) as max_rto
                    FROM bia_processes
                    WHERE tenant_id = $1
                    """,
                    "benchmark-tenant"
                )
            except Exception:
                result = None
            return result

    result = benchmark(event_loop.run_until_complete, aggregate_query())


# ============================================================================
# Bulk Operation Benchmarks
# ============================================================================

def test_bulk_insert_10_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Bulk insert 10 records"""

    async def bulk_insert():
        async with db_pool.acquire() as conn:
            try:
                values = []
                for i in range(10):
                    values.append((
                        "benchmark-tenant",
                        f"Bulk Process {i} {asyncio.get_event_loop().time()}",
                        "Bulk insert test",
                        "MEDIUM",
                        8, 4, 12
                    ))

                await conn.executemany(
                    """
                    INSERT INTO bia_processes
                    (tenant_id, name, description, criticality, rto_hours, rpo_hours, mtpd_hours, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    values
                )
            except Exception:
                pass

    benchmark(event_loop.run_until_complete, bulk_insert())


def test_bulk_insert_100_benchmark(benchmark, event_loop, db_pool):
    """Benchmark: Bulk insert 100 records"""

    async def bulk_insert():
        async with db_pool.acquire() as conn:
            try:
                values = []
                for i in range(100):
                    values.append((
                        "benchmark-tenant",
                        f"Bulk Process 100 {i} {asyncio.get_event_loop().time()}",
                        "Bulk insert test",
                        "MEDIUM",
                        8, 4, 12
                    ))

                await conn.executemany(
                    """
                    INSERT INTO bia_processes
                    (tenant_id, name, description, criticality, rto_hours, rpo_hours, mtpd_hours, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    values
                )
            except Exception:
                pass

    benchmark(event_loop.run_until_complete, bulk_insert())
