# ⚡ Performance Optimization Checklist

**Date:** 2025-10-06
**Status:** Action Items
**Priority:** Production Readiness

---

## 🎯 Quick Wins (Immediate Impact)

### 1. ✅ Async Везде

**Проверить все сервисы:**

```bash
# Найти sync database calls
grep -r "def " intelligent-core/*/services/*.py | grep -v "async def" | grep "db\."

# Найти sync HTTP calls
grep -r "requests\." intelligent-core/ --include="*.py"
```

**Должно быть:**
```python
# ✅ Правильно
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    async with db.get_session() as session:
        result = await session.execute(query)

# ❌ Неправильно
def get_data():
    response = requests.get(url)  # SYNC!
    result = db.query(...)        # SYNC!
```

**Fix:**
```bash
# Replace requests → httpx
pip install httpx
# Replace all: requests.get() → httpx.AsyncClient().get()
```

---

### 2. ✅ Connection Pooling

**PostgreSQL Pool Settings:**

```python
# shared/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,              # ✅ Увеличить с 5 до 20
    max_overflow=40,           # ✅ Burst до 60 connections
    pool_pre_ping=True,        # ✅ Health check
    pool_recycle=3600,         # ✅ Recycle every hour
    echo_pool=True,            # ✅ Debug pool in dev
)
```

**Redis Pool Settings:**

```python
# shared/cache/redis_client.py
import redis.asyncio as redis

pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    max_connections=50,        # ✅ Pool size
    decode_responses=True,
)

redis_client = redis.Redis(connection_pool=pool)
```

**Action:**
```bash
# Check current settings
grep -r "create_async_engine" intelligent-core/ shared/
grep -r "ConnectionPool" intelligent-core/ shared/
```

---

### 3. ✅ Redis Caching

**Проверить что кэшируется:**

```bash
# Найти endpoints без кэширования
grep -r "@router.get" intelligent-core/*/api/*.py | wc -l
grep -r "@cached" intelligent-core/*/api/*.py | wc -l
```

**Добавить кэширование:**

```python
# shared/cache/decorators.py
from functools import wraps
import json
import hashlib

def cached(ttl: int = 300):
    """Cache decorator with TTL"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hashlib.md5(
                json.dumps(kwargs, sort_keys=True).encode()
            ).hexdigest()}"

            # Try cache
            cached_value = await redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            # Execute
            result = await func(*args, **kwargs)

            # Store
            await redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )

            return result
        return wrapper
    return decorator
```

**Использование:**

```python
from shared.cache import cached

@router.get("/api/v1/cases/search")
@cached(ttl=300)  # 5 минут
async def search_cases(query: str):
    # Expensive query
    return results
```

**Priority endpoints для кэширования:**
```python
# High traffic, low change rate
✅ /api/v1/community/cases/search
✅ /api/v1/community/reputation/leaderboard
✅ /api/v1/predictive/timeline
✅ /api/v1/living-docs/search
✅ /api/v1/collective/cases/similar
```

---

### 4. ✅ Database Indexes

**Проверить текущие индексы:**

```sql
-- Run in PostgreSQL
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

**Найти missing indexes:**

```sql
-- Queries without indexes
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100  -- High cardinality
ORDER BY tablename;
```

**Добавить критичные индексы:**

```sql
-- community_intelligence
CREATE INDEX CONCURRENTLY idx_case_contributions_status
    ON case_contributions(status) WHERE status != 'draft';

CREATE INDEX CONCURRENTLY idx_case_contributions_module
    ON case_contributions(module);

CREATE INDEX CONCURRENTLY idx_peer_reviews_reviewer
    ON peer_reviews(reviewer_id, reviewed_at DESC);

CREATE INDEX CONCURRENTLY idx_user_reputation_total
    ON user_reputation(total_points DESC);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_contributions_status_module
    ON case_contributions(status, module, submitted_at DESC);

-- Full-text search
CREATE INDEX CONCURRENTLY idx_case_contributions_search
    ON case_contributions USING gin(to_tsvector('english', case_data::text));
```

**Action Script:**

```bash
#!/bin/bash
# scripts/add_indexes.sh

psql $DATABASE_URL << EOF
-- Add all missing indexes
\i infrastructure/database/performance/indexes.sql
EOF
```

---

### 5. ✅ Load Balancing

**Docker Compose with Nginx:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - community_intelligence_1
      - community_intelligence_2
      - community_intelligence_3

  # Community Intelligence - 3 instances
  community_intelligence_1:
    build: ./intelligent-core/community_intelligence
    environment:
      - INSTANCE_ID=1
    labels:
      - "group=ai-services"
      - "service=community_intelligence"

  community_intelligence_2:
    build: ./intelligent-core/community_intelligence
    environment:
      - INSTANCE_ID=2
    labels:
      - "group=ai-services"
      - "service=community_intelligence"

  community_intelligence_3:
    build: ./intelligent-core/community_intelligence
    environment:
      - INSTANCE_ID=3
    labels:
      - "group=ai-services"
      - "service=community_intelligence"

  # Collective - 2 instances
  collective_1:
    build: ./intelligent-core/collective
    environment:
      - INSTANCE_ID=1
    labels:
      - "group=ai-services"
      - "service=collective"

  collective_2:
    build: ./intelligent-core/collective
    environment:
      - INSTANCE_ID=2
    labels:
      - "group=ai-services"
      - "service=collective"

  # Predictive - 2 instances
  predictive_1:
    build: ./intelligent-core/predictive
    labels:
      - "group=ai-services"

  predictive_2:
    build: ./intelligent-core/predictive
    labels:
      - "group=ai-services"

  # Learning System - 2 instances
  learning_system_1:
    build: ./intelligent-core/learning-system
    labels:
      - "group=ai-services"

  learning_system_2:
    build: ./intelligent-core/learning-system
    labels:
      - "group=ai-services"

  # Living Docs - 2 instances
  living_docs_1:
    build: ./intelligent-core/living-docs
    labels:
      - "group=ai-services"

  living_docs_2:
    build: ./intelligent-core/living-docs
    labels:
      - "group=ai-services"
```

**Nginx Config:**

```nginx
# infrastructure/nginx/nginx.conf

upstream community_intelligence {
    least_conn;  # Load balancing algorithm
    server community_intelligence_1:8030;
    server community_intelligence_2:8030;
    server community_intelligence_3:8030;
}

upstream collective {
    least_conn;
    server collective_1:8032;
    server collective_2:8032;
}

upstream predictive {
    least_conn;
    server predictive_1:8031;
    server predictive_2:8031;
}

upstream learning_system {
    least_conn;
    server learning_system_1:8033;
    server learning_system_2:8033;
}

upstream living_docs {
    least_conn;
    server living_docs_1:8034;
    server living_docs_2:8034;
}

server {
    listen 80;

    # Community Intelligence
    location /api/v1/community/ {
        proxy_pass http://community_intelligence;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Collective
    location /api/v1/collective/ {
        proxy_pass http://collective;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Predictive
    location /api/v1/predictive/ {
        proxy_pass http://predictive;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Learning System
    location /api/v1/learning/ {
        proxy_pass http://learning_system;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Living Docs
    location /api/v1/docs/ {
        proxy_pass http://living_docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Management Commands:**

```bash
# Start all AI services with load balancing
docker-compose up -d --scale community_intelligence=3 --scale collective=2

# Start specific group
docker-compose up -d $(docker-compose config --services | grep -E "community_intelligence|collective|predictive|learning|living")

# Check health
docker-compose ps --filter "label=group=ai-services"

# Logs from AI services
docker-compose logs -f --tail=100 $(docker-compose config --services | grep -E "community|collective|predictive|learning|living")
```

---

## 📊 Monitoring & Metrics

**Add Prometheus metrics:**

```python
# shared/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'endpoint', 'method', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['service', 'endpoint']
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['service', 'query_type']
)

# Cache metrics
cache_hits = Counter('cache_hits_total', 'Cache hits', ['service'])
cache_misses = Counter('cache_misses_total', 'Cache misses', ['service'])

# Active connections
active_connections = Gauge(
    'active_connections',
    'Active connections',
    ['service', 'type']  # type: db, redis, http
)
```

**Middleware:**

```python
# shared/middleware/metrics.py
from fastapi import Request
import time

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    request_count.labels(
        service=SERVICE_NAME,
        endpoint=request.url.path,
        method=request.method,
        status=response.status_code
    ).inc()

    request_duration.labels(
        service=SERVICE_NAME,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

---

## 🚀 Deployment Checklist

### Before Production:

- [ ] ✅ All endpoints async
- [ ] ✅ Connection pooling configured (PostgreSQL: 20, Redis: 50)
- [ ] ✅ Redis caching on high-traffic endpoints
- [ ] ✅ Database indexes created (CONCURRENTLY)
- [ ] ✅ Load balancing configured (Nginx + multiple instances)
- [ ] ✅ Monitoring enabled (Prometheus metrics)
- [ ] ✅ Health checks configured
- [ ] ✅ Graceful shutdown implemented

### Performance Targets:

```
Response Time (p95):
- GET requests: < 200ms
- POST requests: < 500ms
- Complex queries: < 1s

Throughput:
- 1000 req/s per service
- 5000 req/s total platform

Cache Hit Rate:
- > 80% for read endpoints

Database:
- Query time p95 < 100ms
- Connection pool utilization < 80%
```

---

## 📁 File Structure

```
infrastructure/
├── nginx/
│   ├── nginx.conf              # Load balancer config
│   └── ssl/                    # SSL certificates
├── database/
│   └── performance/
│       ├── indexes.sql         # Performance indexes
│       └── analyze.sql         # Query analysis
└── monitoring/
    ├── prometheus.yml          # Prometheus config
    └── grafana/
        └── dashboards/

shared/
├── cache/
│   ├── decorators.py           # @cached decorator
│   └── redis_client.py         # Connection pool
├── database/
│   └── connection.py           # PostgreSQL pool
└── monitoring/
    ├── metrics.py              # Prometheus metrics
    └── middleware.py           # Metrics middleware

scripts/
├── performance/
│   ├── add_indexes.sh          # Add DB indexes
│   ├── benchmark.sh            # Load testing
│   └── analyze_slow_queries.sh # Find slow queries
└── deployment/
    └── scale_services.sh       # Auto-scaling script
```

---

## ⚡ Quick Start

```bash
# 1. Check current async usage
grep -r "def " intelligent-core/*/services/*.py | grep -v "async def" | wc -l

# 2. Add indexes
psql $DATABASE_URL -f infrastructure/database/performance/indexes.sql

# 3. Deploy with load balancing
docker-compose up -d --scale community_intelligence=3 --scale collective=2

# 4. Monitor
docker-compose logs -f nginx
```

---

**Ready for production! ⚡**
