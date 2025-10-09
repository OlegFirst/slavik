# PHASE 1: INFRASTRUCTURE - ACTION PLAN

Status: Draft for approval
Date: 2025-10-03

---

## CURRENT STATE

**What we have:**
- Supabase PostgreSQL (cloud) - credentials in .env
- Upstash Redis (cloud) - credentials in .env
- docker-compose.yml in platform-services/ - local PostgreSQL + Redis
- No Neo4j
- No unified docker-compose for all services

**Problem:** Cloud services configured but not used. Docker-compose uses local versions.

---

## DECISION: HYBRID APPROACH

**Use cloud services for data layer:**
- PostgreSQL: Supabase (already configured)
- Redis: Upstash (already configured)

**Use docker for application layer:**
- EventBus service
- All BCM services
- Optional: Neo4j (if needed for Knowledge Graph)

**Why:**
- Supabase already has data, migrations applied
- Upstash reliable, no need to manage Redis
- Focus on application layer, not infrastructure management

---

## PHASE 1 TASKS

### Task 1: Verify Cloud Infrastructure

**PostgreSQL (Supabase):**
```bash
# Test connection
psql "postgresql://postgres.tpdkhddtbhpoqzzgxfni:K%40x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

# Check tables
\dt

# Expected: Should see migrated tables or empty DB
```

**Redis (Upstash):**
```bash
# Test connection
redis-cli -h redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com \
          -p 10023 \
          -a tldJWwUq7lAwOHuCa9pSD7sVfjQFYPYN \
          ping

# Expected: PONG
```

### Task 2: Database Migrations

**Check migration status:**
```bash
# Navigate to infrastructure/database
cd /Users/MD/AI-Platform-ISO/infrastructure/database

# Check what migrations exist
ls -la migrations_source/

# Expected: 33 SQL files
```

**Apply migrations (if not already applied):**
```bash
# Using migrations_source/BATCH_1.sql, BATCH_2.sql, BATCH_3.sql
# Or individual migration files

# Test with one migration first
psql <connection_string> -f migrations_source/001_schemas_and_extensions.sql
```

**Question for MD:**
- Were migrations already applied to Supabase?
- Or do we need to apply all 33 files?

### Task 3: EventBus Deployment

**Decision needed:**
- Use /infrastructure/event-bus/ (with RabbitMQ support)
- Or simpler version for now?

**For MVP, propose simple HTTP EventBus:**
```yaml
# In docker-compose
eventbus:
  build: ./infrastructure/event-bus
  ports:
    - "8001:8001"
  environment:
    - REDIS_URL=${REDIS_URL}
```

### Task 4: Create Root docker-compose.yml

**Purpose:** Single command to start all application services

**Structure:**
```yaml
services:
  # No postgres - using Supabase
  # No redis - using Upstash

  eventbus:
    # Event bus service

  bia-service:
    # BIA Service

  risk-service:
    # Risk Service

  # ... other services
```

**Location:** /Users/MD/AI-Platform-ISO/docker-compose.dev.yml

---

## WHAT NOT TO DO (YET)

- Neo4j - only if Knowledge Graph is needed for MVP
- Orchestrators - waiting for architecture decision
- AI Services - Phase 6
- Frontend - Phase 7

---

## DELIVERABLES

After Phase 1 completion:

1. Verified cloud infrastructure working
2. Database migrations applied
3. EventBus running
4. docker-compose.dev.yml created
5. All services can connect to DB and Redis

---

## QUESTIONS FOR MD

1. **Migrations:** Already applied to Supabase or need to apply?

2. **EventBus:** Simple HTTP version or full RabbitMQ setup?

3. **Neo4j:** Need for MVP or defer to later?

4. **API Keys:**
   - OPENAI_API_KEY in .env says "YOUR_OPENAI_KEY_HERE"
   - ANTHROPIC_API_KEY same
   - Need real keys for testing or mock for now?

---

## NEXT STEP

After MD answers questions above:
- I create specific task breakdown for agents
- MD launches agents with tasks
- I coordinate and review

---

Status: Waiting for MD approval and answers
