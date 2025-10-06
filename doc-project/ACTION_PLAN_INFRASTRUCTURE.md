# INFRASTRUCTURE ACTION PLAN

Date: 2025-10-03

---

## CONFIRMED STATE

**Database (Supabase):**
- Migrations applied: 001-024
- Remaining: 025-033 (9 migrations)
- Issue: Stopped at policy fixes

**Redis (Upstash):**
- Working, configured

**EventBus:**
- Location: /infrastructure/event-bus/
- Features: FastAPI + Redis + RabbitMQ with fallback
- Dependencies: /infrastructure/message-queue/rabbitmq_manager.py
- Status: Code ready, needs deployment

**Neo4j:**
- Required for Knowledge Graph
- Status: Not deployed

---

## TASK BREAKDOWN

### Task 1: Complete Database Migrations (025-033)

**Files to apply in order:**
```
025_platform_administrators.sql     - Platform admin users table
026_user_relationships.sql          - User relationship management
027_admin_policies.sql              - RLS policies for admins
028_fix_remaining_lints.sql         - Supabase security fixes
029_fix_security_definer_view.sql   - View security fix
030_fix_function_search_path.sql    - Function security
031_fix_auth_rls_initplan.sql       - Auth RLS optimization
032_add_foreign_key_indexes.sql     - Performance indexes
033_consolidate_permissive_policies.sql - Policy consolidation
```

**Agent task:**
```bash
# For each migration 025-033:
psql "$DATABASE_URL" -f infrastructure/database/migrations_source/XXX_*.sql

# Verify after each:
# - Check for errors
# - Verify tables/policies created
# - Log completion
```

### Task 2: Deploy Infrastructure Services (Docker)

**Create: /Users/MD/AI-Platform-ISO/docker-compose.infrastructure.yml**

```yaml
version: '3.8'

services:
  # Neo4j - Knowledge Graph
  neo4j:
    image: neo4j:5.12
    container_name: bcm-neo4j
    ports:
      - "7474:7474"  # HTTP Browser
      - "7687:7687"  # Bolt Protocol
    environment:
      NEO4J_AUTH: neo4j/bcm_neo4j_password
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
      NEO4J_dbms_memory_heap_initial__size: 512m
      NEO4J_dbms_memory_heap_max__size: 2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    networks:
      - bcm-network

  # RabbitMQ - Message Queue
  rabbitmq:
    image: rabbitmq:3.12-management
    container_name: bcm-rabbitmq
    ports:
      - "5672:5672"   # AMQP protocol
      - "15672:15672" # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: bcm_user
      RABBITMQ_DEFAULT_PASS: bcm_rabbitmq_password
      RABBITMQ_DEFAULT_VHOST: /
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - bcm-network

  # EventBus Service
  eventbus:
    build:
      context: ./infrastructure/event-bus
      dockerfile: Dockerfile
    container_name: bcm-eventbus
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=${REDIS_URL}
      - POSTGRES_URL=${DATABASE_URL}
      - RABBITMQ_URL=amqp://bcm_user:bcm_rabbitmq_password@rabbitmq:5672/
      - CORS_ORIGINS=http://localhost:3000,http://localhost:8000
    depends_on:
      rabbitmq:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - bcm-network
    restart: unless-stopped

volumes:
  neo4j_data:
  neo4j_logs:
  rabbitmq_data:

networks:
  bcm-network:
    driver: bridge
```

**Agent task:**
- Create docker-compose.infrastructure.yml with above content
- Verify file syntax
- Document how to start: `docker-compose -f docker-compose.infrastructure.yml up -d`

### Task 3: Initialize Neo4j with ISO 22301 Data

**Create: /Users/MD/AI-Platform-ISO/scripts/init_neo4j.py**

Based on FINAL_PATFORM_INTFRASTRUCTURE.md (lines 90-179), create script to:
- Connect to Neo4j
- Create ISO 22301:2019 standard node
- Create clauses (4, 5, 6, 7, 8, 9, 10)
- Create requirements for key clauses (8.2.2, etc.)

**Agent task:**
- Create init_neo4j.py script
- Run after Neo4j is up
- Verify data with: `MATCH (s:Standard) RETURN s`

### Task 4: Verify All Infrastructure

**Agent task: Create verification script**

```bash
#!/bin/bash
# infrastructure/verify_infrastructure.sh

echo "Checking infrastructure..."

# 1. Supabase PostgreSQL
echo "1. Testing PostgreSQL..."
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"

# 2. Redis
echo "2. Testing Redis..."
redis-cli -u "$REDIS_URL" ping

# 3. Neo4j
echo "3. Testing Neo4j..."
curl -u neo4j:bcm_neo4j_password http://localhost:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"MATCH (n) RETURN count(n)"}]}'

# 4. RabbitMQ
echo "4. Testing RabbitMQ..."
curl -u bcm_user:bcm_rabbitmq_password http://localhost:15672/api/overview

# 5. EventBus
echo "5. Testing EventBus..."
curl http://localhost:8001/health

echo "Infrastructure check complete!"
```

---

## AGENT ASSIGNMENTS

**Agent-Infrastructure:**
1. Apply migrations 025-033 sequentially
2. Create docker-compose.infrastructure.yml
3. Create init_neo4j.py script
4. Create verify_infrastructure.sh script
5. Document any errors

**Success Criteria:**
- All 33 migrations applied
- docker-compose up runs without errors
- All 5 infrastructure components pass health checks
- Neo4j contains ISO 22301 data

---

## DELIVERABLES

After completion:
1. Database fully migrated (033/033)
2. Neo4j running with ISO data
3. RabbitMQ running
4. EventBus running and connected to RabbitMQ
5. Verification script confirms all healthy

---

## NOTES

**Do NOT touch yet:**
- Orchestrators (waiting for architecture)
- BCM services (Phase 2)
- AI services (Phase 6)
- Frontend (Phase 7)

**This is pure infrastructure layer only.**

---

Ready for agent launch.
