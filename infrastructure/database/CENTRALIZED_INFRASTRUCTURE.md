# Centralized Infrastructure Migration

**Date:** 2025-10-08
**Status:** ✅ Complete

---

## Overview

Migrated Redis and RabbitMQ from `intelligent-core/` to centralized `/infrastructure/database/` to enable platform-wide sharing.

---

## Architecture Change

### Before (Decentralized)

```
intelligent-core/
├── docker-compose.yml
    ├── intelligent-core-redis (port 6379)
    ├── intelligent-core-rabbitmq (port 5673)
    └── intelligent-core-network
```

**Problem:** Each service had its own infrastructure, leading to:
- Resource duplication
- Configuration inconsistency
- Difficult cross-service communication
- Redis persistence enabled (unnecessary for cache)

### After (Centralized)

```
infrastructure/database/
├── docker-compose.yml
    ├── platform-redis (port 6379)
    ├── platform-rabbitmq (port 5673)
    └── platform-network (shared)

intelligent-core/
└── docker-compose.yml (services only, no infrastructure)
```

**Benefits:**
- Single source of truth for infrastructure
- All services share Redis cache and RabbitMQ
- Centralized configuration
- Pure in-memory Redis (no disk persistence)
- Consistent networking via `platform-network`

---

## Changes Made

### 1. Created Centralized Infrastructure

**File:** `/infrastructure/database/docker-compose.yml`

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: platform-redis
    ports: ["6379:6379"]
    networks: [platform-network]
    command: |
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save ""  # No disk persistence

  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    container_name: platform-rabbitmq
    ports:
      - "5673:5672"    # AMQP
      - "15673:15672"  # Management UI
    networks: [platform-network]
    environment:
      - RABBITMQ_DEFAULT_USER=platform
      - RABBITMQ_DEFAULT_PASS=platform_secure_2024

networks:
  platform-network:
    external: true
```

### 2. Removed Infrastructure from intelligent-core

**File:** `/intelligent-core/docker-compose.yml`

**Removed:**
- Redis service definition
- RabbitMQ service definition
- `redis-data` volume
- `rabbitmq-data` volume
- `rabbitmq-logs` volume
- `intelligent-core-network` (replaced with `platform-network`)

**Changed:**
- All services now use `platform-network` instead of `intelligent-core-network`
- Removed `depends_on: redis` from all services (Redis is external)
- Services still depend on `intelligent-core-main` where appropriate

### 3. Created Platform Network

```bash
docker network create platform-network
```

---

## Service Connections

### Redis Connection

**URL:** `redis://localhost:6379/0`

**Environment variable:**
```bash
REDIS_URL=redis://localhost:6379/0
```

**Python:**
```python
import redis.asyncio as redis
client = await redis.from_url("redis://localhost:6379/0")
```

### RabbitMQ Connection

**AMQP URL:** `amqp://platform:platform_secure_2024@localhost:5673/`

**Management UI:** http://localhost:15673
- Username: `platform`
- Password: `platform_secure_2024`

**Environment variable:**
```bash
RABBITMQ_URL=amqp://platform:platform_secure_2024@localhost:5673/
```

---

## Startup Order

### 1. Start Centralized Infrastructure First

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/database
docker-compose up -d
```

**Verify:**
```bash
docker ps --filter "name=platform-"
# Should show: platform-redis, platform-rabbitmq

redis-cli -h localhost -p 6379 PING
# Should return: PONG

curl http://localhost:15673
# Should return: RabbitMQ Management UI
```

### 2. Start Intelligent Core Services

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core
docker-compose up -d
```

Services will connect to centralized infrastructure via `platform-network`.

---

## Configuration Changes

### Redis Configuration

**Memory Management:**
- Max memory: 512MB
- Eviction policy: `allkeys-lru` (removes least recently used keys)
- Persistence: **DISABLED** (pure in-memory cache)
- No AOF (Append-Only File)
- No RDB snapshots

**Why no persistence?**
- Redis is used as cache, not primary data store
- All important data is in PostgreSQL
- Faster performance without disk I/O
- Smaller container size

### RabbitMQ Configuration

**Ports:**
- AMQP: 5673 (instead of 5672 to avoid conflicts)
- Management UI: 15673 (instead of 15672)

**Credentials:**
- User: `platform`
- Password: `platform_secure_2024`
- VHost: `/`

---

## Migration Steps Performed

1. ✅ Created `/infrastructure/database/docker-compose.yml` with centralized services
2. ✅ Created `platform-network` Docker network
3. ✅ Stopped old `intelligent-core-redis` and `intelligent-core-rabbitmq` containers
4. ✅ Started new `platform-redis` and `platform-rabbitmq` containers
5. ✅ Updated `/intelligent-core/docker-compose.yml`:
   - Removed Redis and RabbitMQ service definitions
   - Changed network from `intelligent-core-network` to `platform-network`
   - Removed `depends_on: redis` from all services
   - Removed volume definitions
6. ✅ Updated `/infrastructure/database/README.md` with centralized architecture
7. ✅ Verified all services healthy

---

## Verification

### Current Status

```bash
$ docker ps --filter "name=platform-"
NAMES               STATUS                      PORTS
platform-rabbitmq   Up (healthy)               0.0.0.0:5673->5672/tcp, 0.0.0.0:15673->15672/tcp
platform-redis      Up (healthy)               0.0.0.0:6379->6379/tcp
```

### Test Redis

```bash
$ redis-cli -h localhost -p 6379 PING
PONG
✅ Redis healthy
```

### Test RabbitMQ

```bash
$ curl -s -u platform:platform_secure_2024 http://localhost:15673/api/overview | jq .rabbitmq_version
"3.13.7"
✅ RabbitMQ healthy
```

---

## Breaking Changes

### For Existing Services

If any service was hardcoded to use:
- `intelligent-core-redis` → Change to `platform-redis` or `localhost:6379`
- `intelligent-core-rabbitmq` → Change to `platform-rabbitmq` or `localhost:5673`
- Port `5672` → Change to `5673` for RabbitMQ
- Port `15672` → Change to `15673` for RabbitMQ Management UI

### For Docker Networks

If any service was using `intelligent-core-network`:
- Add service to `platform-network` in its docker-compose.yml
- Or update network references to use `platform-network`

---

## Rollback Plan

If issues arise, rollback by:

```bash
# Stop centralized infrastructure
cd /Users/MD/AI-Platform-ISO/infrastructure/database
docker-compose down

# Restore intelligent-core infrastructure
cd /Users/MD/AI-Platform-ISO/intelligent-core
git checkout HEAD -- docker-compose.yml
docker-compose up -d
```

---

## Next Steps

### Services to Update

Update these services to use centralized infrastructure:

1. **API Gateway** (`/infrastructure/gateway/api-gateway/`)
   - Already uses `redis://localhost:6379` ✅
   - No changes needed

2. **Auth Service** (`/infrastructure/security/auth-service/`)
   - Verify Redis connection
   - Update if using old container name

3. **Monitoring Service** (`/infrastructure/monitoring/`)
   - Update to use centralized RabbitMQ for events

4. **Notification Service** (`/infrastructure/notification-service/`)
   - Update to use centralized RabbitMQ

5. **All Intelligent Core Services**
   - Already configured via docker-compose.yml
   - Verify environment variables point to localhost:6379 and localhost:5673

### Documentation Updates

- ✅ `/infrastructure/database/README.md` - Updated with centralized architecture
- ✅ `/infrastructure/database/CENTRALIZED_INFRASTRUCTURE.md` - This document
- 🔲 `/infrastructure/gateway/README.md` - Update to reference centralized Redis
- 🔲 `/infrastructure/runtime/README.md` - Update to reference centralized RabbitMQ

---

## Troubleshooting

### Redis Connection Failed

```bash
# Check Redis is running
docker ps --filter "name=platform-redis"

# Check Redis logs
docker logs platform-redis

# Test connection
redis-cli -h localhost -p 6379 PING
```

### RabbitMQ Connection Failed

```bash
# Check RabbitMQ is running
docker ps --filter "name=platform-rabbitmq"

# Check RabbitMQ logs
docker logs platform-rabbitmq

# Check management UI
curl -u platform:platform_secure_2024 http://localhost:15673/api/overview
```

### Service Can't Find Redis/RabbitMQ

```bash
# Verify service is on platform-network
docker network inspect platform-network

# Add service to network if needed
docker network connect platform-network <container-name>

# Or update docker-compose.yml to use platform-network
```

---

**Migration completed successfully! ✅**

All infrastructure services are now centralized and ready for platform-wide use.
