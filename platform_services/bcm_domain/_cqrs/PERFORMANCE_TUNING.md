# CQRS Performance Tuning Guide

Complete guide to optimizing CQRS performance for production workloads.

## Table of Contents

- [Performance Metrics](#performance-metrics)
- [Database Optimization](#database-optimization)
- [Caching Strategies](#caching-strategies)
- [Event Store Optimization](#event-store-optimization)
- [Projection Optimization](#projection-optimization)
- [Query Optimization](#query-optimization)
- [Monitoring](#monitoring)
- [Load Testing](#load-testing)

## Performance Metrics

### Target Performance

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Command Throughput | 2000/sec | 1000/sec | <500/sec |
| Query Throughput (cached) | 50000/sec | 10000/sec | <5000/sec |
| Query Throughput (uncached) | 5000/sec | 1000/sec | <500/sec |
| Command Latency (p50) | <10ms | <50ms | >100ms |
| Command Latency (p99) | <50ms | <200ms | >500ms |
| Query Latency (cached, p50) | <1ms | <5ms | >10ms |
| Query Latency (uncached, p50) | <10ms | <50ms | >100ms |
| Projection Lag | <50ms | <200ms | >1000ms |
| Event Replay Speed | 10000/sec | 5000/sec | <1000/sec |

### Measuring Performance

```python
import time
from _cqrs import get_command_handler, get_query_handler

# Measure command throughput
async def measure_command_throughput(iterations=1000):
    cmd_handler = get_command_handler()

    start = time.time()
    for i in range(iterations):
        await cmd_handler.handle(
            command=CreateBIAProcessCommand(...),
            executor=lambda agg, cmd: agg.create(...),
            aggregate_type="BIAProcess",
            create_new=True
        )

    elapsed = time.time() - start
    throughput = iterations / elapsed
    print(f"Command throughput: {throughput:.2f} commands/sec")

# Measure query latency
async def measure_query_latency(iterations=1000):
    query_handler = get_query_handler()
    query = GetBIAProcessesQuery(tenant_id="tenant_123")

    latencies = []
    for i in range(iterations):
        start = time.time()
        await query_handler.get_bia_processes(query)
        latencies.append((time.time() - start) * 1000)  # ms

    latencies.sort()
    p50 = latencies[len(latencies)//2]
    p99 = latencies[int(len(latencies)*0.99)]

    print(f"Query latency p50: {p50:.2f}ms, p99: {p99:.2f}ms")
```

## Database Optimization

### 1. Connection Pooling

**Problem:** Too many connections or connection overhead

**Solution:**
```python
from _cqrs import EventStore, ProjectionBuilder

# Optimize pool sizes
event_store = EventStore(database_url)
event_store.pool = await asyncpg.create_pool(
    database_url,
    min_size=5,      # Minimum connections
    max_size=20,     # Maximum connections
    max_queries=50000,  # Recycle after 50k queries
    max_inactive_connection_lifetime=300  # 5 minutes
)

# Separate pools for read and write
write_pool = await asyncpg.create_pool(
    database_url,
    min_size=5,
    max_size=10  # Fewer write connections
)

read_pool = await asyncpg.create_pool(
    database_url,
    min_size=10,
    max_size=30  # More read connections
)
```

**Configuration Guide:**
- **Low load** (<100 QPS): min_size=2, max_size=10
- **Medium load** (100-1000 QPS): min_size=5, max_size=20
- **High load** (>1000 QPS): min_size=10, max_size=50

### 2. Indexes

**Critical Indexes:**

```sql
-- Event Store
CREATE INDEX CONCURRENTLY idx_events_aggregate
ON cqrs_events(aggregate_type, aggregate_id, version);

CREATE INDEX CONCURRENTLY idx_events_type
ON cqrs_events(event_type);

CREATE INDEX CONCURRENTLY idx_events_tenant
ON cqrs_events((metadata->>'tenant_id'));

CREATE INDEX CONCURRENTLY idx_events_created
ON cqrs_events(created_at DESC);

-- Read Models
CREATE INDEX CONCURRENTLY idx_read_bia_tenant_criticality
ON read_bia_processes(tenant_id, criticality);

CREATE INDEX CONCURRENTLY idx_read_bia_tenant_status
ON read_bia_processes(tenant_id, status);

CREATE INDEX CONCURRENTLY idx_read_bia_composite
ON read_bia_processes(tenant_id, criticality, status, created_at DESC);

-- Covering index for common queries
CREATE INDEX CONCURRENTLY idx_read_bia_covering
ON read_bia_processes(tenant_id, status)
INCLUDE (id, name, criticality, rto_hours);
```

**Verify Index Usage:**
```sql
-- Check query plan
EXPLAIN ANALYZE
SELECT * FROM read_bia_processes
WHERE tenant_id = 'tenant_123' AND criticality = 'CRITICAL';

-- Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY schemaname, tablename;
```

### 3. Query Optimization

**Use EXPLAIN ANALYZE:**
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT id, name, criticality, rto_hours
FROM read_bia_processes
WHERE tenant_id = $1
  AND status = $2
ORDER BY created_at DESC
LIMIT 100;
```

**Optimize with CTEs:**
```sql
-- Bad: Nested subqueries
SELECT * FROM (
    SELECT * FROM read_bia_processes WHERE tenant_id = $1
) WHERE criticality = 'CRITICAL';

-- Good: CTE
WITH tenant_processes AS (
    SELECT * FROM read_bia_processes WHERE tenant_id = $1
)
SELECT * FROM tenant_processes WHERE criticality = 'CRITICAL';
```

### 4. Vacuum and Analyze

**Configure autovacuum:**
```sql
-- Per-table configuration
ALTER TABLE cqrs_events SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

ALTER TABLE read_bia_processes SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);

-- Manual vacuum
VACUUM ANALYZE cqrs_events;
VACUUM ANALYZE read_bia_processes;
```

## Caching Strategies

### 1. Redis Configuration

```python
import redis.asyncio as redis

# Optimize Redis connection
redis_client = await redis.from_url(
    "redis://localhost:6379/0",
    encoding="utf-8",
    decode_responses=False,
    max_connections=50,
    socket_keepalive=True,
    socket_timeout=5.0,
    socket_connect_timeout=5.0,
    retry_on_timeout=True
)
```

**Redis Settings:**
```conf
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 10

# Persistence (adjust based on needs)
save 900 1      # Save if 1 key changed in 15 min
save 300 10     # Save if 10 keys changed in 5 min
save 60 10000   # Save if 10k keys changed in 1 min

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
```

### 2. Cache TTL Strategy

```python
from query_handler import cached_query

# Frequently changing data: Short TTL
@cached_query(ttl=60)  # 1 minute
async def get_active_processes(self, query):
    ...

# Moderately stable data: Medium TTL
@cached_query(ttl=300)  # 5 minutes
async def get_bia_processes(self, query):
    ...

# Stable data: Long TTL
@cached_query(ttl=3600)  # 1 hour
async def get_bia_statistics(self, query):
    ...

# Computed/expensive queries: Very long TTL
@cached_query(ttl=86400)  # 24 hours
async def get_annual_report(self, query):
    ...
```

### 3. Cache Warming

```python
async def warm_cache():
    """Pre-populate cache with common queries."""
    query_handler = get_query_handler()

    # Get all tenants
    tenants = await get_active_tenants()

    # Warm cache for each tenant
    for tenant_id in tenants:
        # Common queries
        await query_handler.get_bia_processes(
            GetBIAProcessesQuery(tenant_id=tenant_id)
        )

        await query_handler.get_bia_summary(
            GetBIASummaryQuery(tenant_id=tenant_id)
        )

        await query_handler.get_critical_processes(
            GetCriticalProcessesQuery(tenant_id=tenant_id)
        )

    logger.info(f"Cache warmed for {len(tenants)} tenants")

# Run on startup
@app.on_event("startup")
async def startup():
    await warm_cache()
```

### 4. Smart Cache Invalidation

```python
from read_model_updater import ReadModelConfig

# Granular invalidation
updater.register_config(ReadModelConfig(
    projection_name="bia_process_list",
    event_types=["BIAProcessCreated"],
    cache_patterns=[
        # Invalidate only list queries, not detail queries
        "cqrs:query:get_bia_processes:*",
        "cqrs:query:get_bia_summary:*"
        # NOT: "cqrs:query:get_bia_process_detail:*"
    ]
))

# Tenant-specific invalidation
async def invalidate_tenant_cache(tenant_id: str):
    query_handler = get_query_handler()

    # Invalidate only this tenant's cache
    await query_handler.invalidate_cache(
        pattern="*",
        tenant_id=tenant_id
    )
```

## Event Store Optimization

### 1. Snapshot Configuration

```python
from command_handler import CommandHandler

# Tune snapshot frequency
command_handler = get_command_handler()

# High-volume aggregates: More frequent snapshots
command_handler._snapshot_threshold = 25  # Every 25 events

# Low-volume aggregates: Less frequent snapshots
command_handler._snapshot_threshold = 100  # Every 100 events

# Manual snapshot for critical aggregates
async def snapshot_critical_aggregates():
    event_store = get_event_store()

    # Get critical process IDs
    critical_ids = await get_critical_process_ids()

    for process_id in critical_ids:
        # Load aggregate
        aggregate = await command_handler.load_aggregate(
            "BIAProcess",
            process_id
        )

        # Save snapshot
        await event_store.save_snapshot(
            "BIAProcess",
            process_id,
            aggregate.version,
            aggregate.to_dict()
        )

    logger.info(f"Saved snapshots for {len(critical_ids)} aggregates")
```

### 2. Event Partitioning

```sql
-- Partition events by date for better performance
CREATE TABLE cqrs_events (
    id BIGSERIAL,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    ...
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE cqrs_events_2025_01 PARTITION OF cqrs_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE cqrs_events_2025_02 PARTITION OF cqrs_events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Automate partition creation
CREATE OR REPLACE FUNCTION create_event_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE := DATE_TRUNC('month', CURRENT_DATE);
    partition_name TEXT := 'cqrs_events_' || TO_CHAR(partition_date, 'YYYY_MM');
BEGIN
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF cqrs_events
         FOR VALUES FROM (%L) TO (%L)',
        partition_name,
        partition_date,
        partition_date + INTERVAL '1 month'
    );
END;
$$ LANGUAGE plpgsql;
```

### 3. Batch Event Processing

```python
async def process_events_batch():
    """Process events in batches for better performance."""
    projection_builder = get_projection_builder()
    event_store = get_event_store()

    batch_size = 1000
    events_batch = []

    async for event in event_store.get_all_events(batch_size=batch_size):
        events_batch.append(event)

        if len(events_batch) >= 100:  # Process in sub-batches
            # Batch apply to projections
            for event in events_batch:
                await projection_builder.apply_event(event)

            events_batch.clear()

            # Commit and continue
            await asyncio.sleep(0.01)  # Yield control

    # Process remaining
    for event in events_batch:
        await projection_builder.apply_event(event)
```

## Projection Optimization

### 1. Denormalization

**Bad: Normalized (requires joins)**
```sql
-- Multiple tables
CREATE TABLE read_bia_processes (id, name, ...);
CREATE TABLE read_bia_dependencies (process_id, dependency_id, ...);
CREATE TABLE read_bia_financial (process_id, period, amount, ...);

-- Query requires joins
SELECT p.*, d.*, f.*
FROM read_bia_processes p
LEFT JOIN read_bia_dependencies d ON p.id = d.process_id
LEFT JOIN read_bia_financial f ON p.id = f.process_id;
```

**Good: Denormalized (single query)**
```sql
-- Single table with JSONB
CREATE TABLE read_bia_processes (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500),
    dependencies JSONB,  -- Denormalized
    financial_impact JSONB,  -- Denormalized
    ...
);

-- Fast query
SELECT * FROM read_bia_processes WHERE id = $1;

-- Index on JSONB fields
CREATE INDEX idx_bia_dependencies ON read_bia_processes
USING GIN (dependencies);
```

### 2. Materialized Aggregates

```sql
-- Pre-calculate aggregates in projection
CREATE TABLE read_bia_summary (
    tenant_id VARCHAR(255) PRIMARY KEY,
    total_processes INTEGER,
    critical_count INTEGER,
    avg_rto_hours FLOAT,
    max_rto_hours INTEGER,  -- Pre-calculated
    min_rto_hours INTEGER,  -- Pre-calculated
    total_financial_impact NUMERIC(15,2),  -- Pre-calculated
    updated_at TIMESTAMP
);

-- Update on each event
async def _update_summary(event: Event):
    # Recalculate aggregates
    stats = await conn.fetchrow("""
        SELECT
            COUNT(*) as total,
            AVG(rto_hours) as avg_rto,
            MAX(rto_hours) as max_rto,
            MIN(rto_hours) as min_rto
        FROM read_bia_processes
        WHERE tenant_id = $1
    """, event.metadata.tenant_id)

    # Update summary
    await conn.execute("""
        UPDATE read_bia_summary
        SET total_processes = $1,
            avg_rto_hours = $2,
            max_rto_hours = $3,
            min_rto_hours = $4
        WHERE tenant_id = $5
    """, stats['total'], stats['avg_rto'],
         stats['max_rto'], stats['min_rto'],
         event.metadata.tenant_id)
```

### 3. Incremental Updates

```python
# Bad: Full recalculation
async def update_summary(tenant_id: str):
    # Recalculate everything
    stats = await conn.fetchrow("""
        SELECT COUNT(*), AVG(rto_hours), SUM(financial_impact)
        FROM read_bia_processes
        WHERE tenant_id = $1
    """, tenant_id)
    # ...

# Good: Incremental update
async def update_summary_incremental(event: Event):
    if event.event_type == "BIAProcessCreated":
        # Just increment counts
        await conn.execute("""
            UPDATE read_bia_summary
            SET total_processes = total_processes + 1,
                critical_count = critical_count +
                    CASE WHEN $2 = 'CRITICAL' THEN 1 ELSE 0 END
            WHERE tenant_id = $1
        """, event.metadata.tenant_id, event.data['criticality'])
```

## Query Optimization

### 1. Pagination

```python
# Bad: OFFSET-based pagination (slow for large offsets)
async def get_processes_bad(limit=100, offset=0):
    return await conn.fetch("""
        SELECT * FROM read_bia_processes
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)

# Good: Cursor-based pagination
async def get_processes_good(limit=100, after_id=None):
    if after_id:
        return await conn.fetch("""
            SELECT * FROM read_bia_processes
            WHERE id > $1
            ORDER BY id ASC
            LIMIT $2
        """, after_id, limit)
    else:
        return await conn.fetch("""
            SELECT * FROM read_bia_processes
            ORDER BY id ASC
            LIMIT $1
        """, limit)
```

### 2. Projection Selection

```python
# Bad: SELECT *
async def get_process_bad(process_id: str):
    return await conn.fetchrow("""
        SELECT * FROM read_bia_processes
        WHERE id = $1
    """, process_id)

# Good: SELECT specific columns
async def get_process_good(process_id: str):
    return await conn.fetchrow("""
        SELECT id, name, criticality, rto_hours, status
        FROM read_bia_processes
        WHERE id = $1
    """, process_id)
```

### 3. Query Result Streaming

```python
# For large result sets, stream instead of loading all
async def stream_processes(tenant_id: str):
    """Stream large result sets."""
    async with projection_builder.pool.acquire() as conn:
        async with conn.transaction():
            # Use cursor for streaming
            async for record in conn.cursor("""
                SELECT id, name, criticality
                FROM read_bia_processes
                WHERE tenant_id = $1
            """, tenant_id):
                yield dict(record)
                await asyncio.sleep(0)  # Yield control
```

## Monitoring

### 1. Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Command metrics
command_counter = Counter(
    'cqrs_commands_total',
    'Total commands executed',
    ['command_type', 'status']
)

command_duration = Histogram(
    'cqrs_command_duration_seconds',
    'Command execution duration',
    ['command_type']
)

# Query metrics
query_counter = Counter(
    'cqrs_queries_total',
    'Total queries executed',
    ['query_type', 'cached']
)

query_duration = Histogram(
    'cqrs_query_duration_seconds',
    'Query execution duration',
    ['query_type', 'cached']
)

# Projection metrics
projection_lag = Gauge(
    'cqrs_projection_lag_seconds',
    'Projection lag behind event store',
    ['projection_name']
)

# Use in code
with command_duration.labels(command_type='CreateBIA').time():
    result = await command_handler.handle(...)

command_counter.labels(
    command_type='CreateBIA',
    status='success' if result.success else 'error'
).inc()
```

### 2. Health Checks

```python
@app.get("/health/cqrs")
async def cqrs_health():
    """CQRS health check."""
    from _cqrs import get_event_store, get_projection_builder

    health = {
        "status": "healthy",
        "checks": {}
    }

    # Event Store
    try:
        event_store = get_event_store()
        await event_store.pool.fetchval("SELECT 1")
        health["checks"]["event_store"] = "healthy"
    except Exception as e:
        health["checks"]["event_store"] = f"unhealthy: {e}"
        health["status"] = "unhealthy"

    # Projections
    try:
        builder = get_projection_builder()
        status = await builder.get_projection_status()

        for proj in status:
            # Check if projection is recent
            age = (datetime.utcnow() - proj['last_updated']).total_seconds()
            if age > 300:  # 5 minutes
                health["checks"][proj['name']] = f"stale: {age:.0f}s"
                health["status"] = "degraded"
            else:
                health["checks"][proj['name']] = "healthy"
    except Exception as e:
        health["checks"]["projections"] = f"unhealthy: {e}"
        health["status"] = "unhealthy"

    return health
```

## Load Testing

### Example Load Test Script

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import statistics

async def load_test_commands(
    concurrent_users=100,
    requests_per_user=100
):
    """Load test command throughput."""
    from _cqrs import get_command_handler

    cmd_handler = get_command_handler()

    async def execute_commands(user_id: int):
        latencies = []

        for i in range(requests_per_user):
            start = time.time()

            result = await cmd_handler.handle(
                command=CreateBIAProcessCommand(
                    tenant_id=f"tenant_{user_id % 10}",
                    name=f"Process {user_id}_{i}",
                    criticality="HIGH",
                    rto_hours=4
                ),
                executor=lambda agg, cmd: agg.create(...),
                aggregate_type="BIAProcess",
                create_new=True
            )

            latencies.append(time.time() - start)

        return latencies

    # Run concurrent users
    start = time.time()

    tasks = [
        execute_commands(user_id)
        for user_id in range(concurrent_users)
    ]

    all_latencies = await asyncio.gather(*tasks)

    elapsed = time.time() - start

    # Flatten latencies
    latencies = [l for sublist in all_latencies for l in sublist]
    latencies.sort()

    # Results
    total_requests = concurrent_users * requests_per_user
    throughput = total_requests / elapsed

    p50 = latencies[len(latencies)//2] * 1000
    p95 = latencies[int(len(latencies)*0.95)] * 1000
    p99 = latencies[int(len(latencies)*0.99)] * 1000

    print(f"""
Load Test Results:
==================
Concurrent Users: {concurrent_users}
Requests per User: {requests_per_user}
Total Requests: {total_requests}
Duration: {elapsed:.2f}s
Throughput: {throughput:.2f} req/sec

Latency:
  p50: {p50:.2f}ms
  p95: {p95:.2f}ms
  p99: {p99:.2f}ms
  min: {min(latencies)*1000:.2f}ms
  max: {max(latencies)*1000:.2f}ms
  avg: {statistics.mean(latencies)*1000:.2f}ms
    """)

# Run test
asyncio.run(load_test_commands(
    concurrent_users=100,
    requests_per_user=100
))
```

## Recommended Configuration

### Development
```python
# development.py
CQRS_CONFIG = {
    "event_store_pool": {"min_size": 2, "max_size": 5},
    "projection_pool": {"min_size": 2, "max_size": 5},
    "snapshot_threshold": 100,
    "cache_ttl": 60,
    "batch_size": 100
}
```

### Production
```python
# production.py
CQRS_CONFIG = {
    "event_store_pool": {"min_size": 10, "max_size": 30},
    "projection_pool": {"min_size": 10, "max_size": 50},
    "snapshot_threshold": 50,
    "cache_ttl": 300,
    "batch_size": 1000
}
```

### High-Performance
```python
# high_performance.py
CQRS_CONFIG = {
    "event_store_pool": {"min_size": 20, "max_size": 100},
    "projection_pool": {"min_size": 30, "max_size": 150},
    "snapshot_threshold": 25,
    "cache_ttl": 600,
    "batch_size": 5000,
    "redis_max_connections": 100
}
```

---

## Summary Checklist

Performance optimization checklist:

- [ ] Database indexes created and verified
- [ ] Connection pools configured appropriately
- [ ] Cache TTLs optimized per query type
- [ ] Cache warming implemented for hot data
- [ ] Snapshots enabled and tuned
- [ ] Projections denormalized properly
- [ ] Queries use specific column selection
- [ ] Pagination uses cursor-based approach
- [ ] Monitoring and metrics in place
- [ ] Load tests passed with acceptable performance
- [ ] Health checks implemented
- [ ] Autovacuum configured
- [ ] Redis maxmemory policy set

Follow this guide to achieve optimal CQRS performance in production!
