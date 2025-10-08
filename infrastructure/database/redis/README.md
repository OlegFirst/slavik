# Redis - In-Memory Data Store

**Status:** ✅ Running
**Version:** 8.2.1
**Port:** 6379
**Container:** intelligent-core-redis

---

## Overview

Redis serves as the platform's in-memory data store for caching, sessions, rate limiting, and service registry.

### Current Status

```
✅ Container: intelligent-core-redis
✅ Port: 6379 (localhost)
✅ Health: healthy
✅ Keys: 1 (service_registry)
✅ Commands processed: 301+
✅ Cache hits: 37
```

---

## Usage

### Session Storage

```python
from infrastructure.database.managers.cache_manager import CacheManager

cache = CacheManager()

# Store session
await cache.set(f"session:{user_id}", {
    "user_id": user_id,
    "token": token,
    "expires_at": expires_at
}, ttl=3600)

# Get session
session = await cache.get(f"session:{user_id}")
```

### Rate Limiting

```python
from infrastructure.database.managers.rate_limiter import RateLimiter

limiter = RateLimiter(redis_client)

# Check rate limit
is_allowed = await limiter.check_rate_limit(
    user_id="user123",
    max_requests=100,
    window=60
)
```

### Service Registry

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Register service
r.hset('service_registry', 'workflow-engine', json.dumps({
    'name': 'workflow-engine',
    'status': 'running',
    'port': 8020,
    'registered_at': datetime.utcnow().isoformat()
}))

# Get service
service = json.loads(r.hget('service_registry', 'workflow-engine'))
```

### Cache Layer

```python
# Cache expensive computations
cache_key = f"embedding:{text_hash}"
cached = await cache.get(cache_key)

if cached:
    return cached

# Compute and cache
result = await generate_embedding(text)
await cache.set(cache_key, result, ttl=3600)
return result
```

---

## Configuration

### Docker Container

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    container_name: intelligent-core-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
```

### Environment Variables

```bash
# Local Docker
REDIS_URL=redis://localhost:6379/0

# Cloud Backup (Upstash)
UPSTASH_REDIS_URL=redis://:password@endpoint.upstash.io:port
```

---

## Data Structures

### Current Keys

```bash
# Check all keys
redis-cli KEYS "*"

# Current keys:
service_registry (hash)
  ├── redis: {...}
  ├── postgres: {...}
  └── rabbitmq: {...}
```

### Key Patterns

| Pattern | Type | TTL | Usage |
|---------|------|-----|-------|
| `session:{user_id}` | String | 3600s | User sessions |
| `rate_limit:{user_id}:{endpoint}` | String | 60s | Rate limiting |
| `cache:{key}` | String | 300s | General cache |
| `service_registry` | Hash | - | Service discovery |
| `workflow:{id}:state` | String | 86400s | Workflow state |
| `lock:{resource}` | String | 30s | Distributed locks |

---

## Monitoring

### Health Check

```bash
# CLI
redis-cli PING
# Expected: PONG

# Python
import redis
r = redis.Redis(host='localhost', port=6379)
print(r.ping())  # True
```

### Statistics

```bash
# Get info
redis-cli INFO stats

# Key stats:
total_commands_processed: 301
keyspace_hits: 37
keyspace_misses: 16
```

### Memory Usage

```bash
# Check memory
redis-cli INFO memory | grep used_memory_human
# used_memory_human: 1.2M
```

---

## Operations

### Backup

```bash
# Manual backup
redis-cli SAVE

# Get dump file
docker cp intelligent-core-redis:/data/dump.rdb ./redis-backup.rdb
```

### Clear Cache

```bash
# Clear all keys in DB 0
redis-cli -n 0 FLUSHDB

# Clear all databases
redis-cli FLUSHALL
```

### Debug Commands

```bash
# Monitor all commands
redis-cli MONITOR

# Get slow log
redis-cli SLOWLOG GET 10

# Check key type
redis-cli TYPE service_registry

# Get key TTL
redis-cli TTL session:user123
```

---

## Integration

### Gateway

Gateway uses Redis for:
- Rate limiting (sliding window)
- Health check caching
- Service discovery cache

**Config:** `/infrastructure/gateway/api-gateway/.env`
```
REDIS_URL=redis://localhost:6379/0
```

### Auth Service

Auth service uses Redis for:
- Session storage
- Token blacklist
- Rate limiting

**Config:** `/infrastructure/security/auth/.env`
```
REDIS_URL=redis://localhost:6379/1
```

### Workflow Engine

Workflow engine uses Redis for:
- State caching
- Distributed locks
- Event queuing

**Config:** `/intelligent-core/workflow_intelligence/.env`
```
REDIS_URL=redis://localhost:6379/2
```

---

## Performance

### Benchmarks

```bash
# Run benchmark
redis-benchmark -q -n 100000

# Results (typical):
PING_INLINE: 50000 requests/sec
GET: 45000 requests/sec
SET: 48000 requests/sec
LPUSH: 44000 requests/sec
```

### Optimization

**Connection Pooling:**
```python
import redis.asyncio as aioredis

pool = aioredis.ConnectionPool.from_url(
    "redis://localhost:6379",
    max_connections=50,
    socket_timeout=5
)

redis_client = aioredis.Redis(connection_pool=pool)
```

**Pipeline for Bulk Operations:**
```python
pipe = redis_client.pipeline()
for i in range(1000):
    pipe.set(f"key:{i}", f"value:{i}")
await pipe.execute()
```

---

## Troubleshooting

### Connection Refused

```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis
docker start intelligent-core-redis

# Check logs
docker logs intelligent-core-redis
```

### High Memory Usage

```bash
# Check memory
redis-cli INFO memory

# Find large keys
redis-cli --bigkeys

# Set eviction policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Slow Performance

```bash
# Check slow log
redis-cli SLOWLOG GET 10

# Monitor real-time
redis-cli MONITOR

# Check connection count
redis-cli INFO clients
```

---

## Security

### Production Checklist

- [ ] Enable password authentication
- [ ] Bind to specific IP (not 0.0.0.0)
- [ ] Use TLS for connections
- [ ] Disable dangerous commands (FLUSHALL, CONFIG)
- [ ] Set maxmemory limit
- [ ] Enable AOF persistence

### Password Protection

```bash
# Set password
redis-cli CONFIG SET requirepass "your-strong-password"

# Connect with password
redis-cli -a "your-strong-password"
```

---

## Documentation

- [Redis Official Docs](https://redis.io/docs/)
- [CacheManager Implementation](../managers/cache_manager.py)
- [RateLimiter Implementation](../managers/rate_limiter.py)

---

**Last Updated:** 2025-10-07
**Docker Image:** redis:7-alpine
**Container:** intelligent-core-redis
