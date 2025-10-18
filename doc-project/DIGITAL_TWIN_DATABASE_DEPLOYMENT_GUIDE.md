# Digital Twin Database Integration - Deployment Guide

**Created:** 2025-10-15
**Status:** Ready for Testing
**Progress:** 100% Complete

## Overview

This guide provides step-by-step instructions for deploying and testing the PostgreSQL-backed Digital Twin services.

## What Was Changed

### Summary of Changes

1. **4 Services Migrated to PostgreSQL:**
   - `KnowledgeExchangeService` → `KnowledgeExchangeServiceDB`
   - `PeopleMatchingService` → `PeopleMatchingServiceDB`
   - `PassiveLearningEngine` → `PassiveLearningEngineDB`
   - `ContextBuilder` → `ContextBuilderDB`

2. **API Routers Updated:**
   - `/api/routers/community.py` - Now uses database-backed services
   - `/api/routers/learning.py` - Now uses database-backed services

3. **New Files Created:**
   - `/api/dependencies.py` - Dependency injection for database sessions and services
   - `/core/community/knowledge_exchange_db.py` (700 LOC)
   - `/core/community/people_matching_db.py` (600 LOC)
   - `/core/learning/passive_learning_engine_db.py` (550 LOC)
   - `/core/learning/context_builder_db.py` (550 LOC)

### Total New Code
- **Router Updates:** ~100 LOC
- **Dependencies:** ~200 LOC
- **Database-backed Services:** ~2,400 LOC
- **Documentation:** ~2,000 LOC
- **GRAND TOTAL:** ~4,700 LOC (this session)

---

## Prerequisites

### 1. Database Setup

Ensure PostgreSQL is running and accessible. You can use:
- Local PostgreSQL instance
- Docker container
- Cloud database (e.g., Supabase, AWS RDS)

### 2. Environment Variables

Create a `.env` file in the Digital Twin service root:

```bash
# Database Connection
DATABASE_URL="postgresql://user:password@host:port/database"

# OR specify components
DB_HOST=localhost
DB_PORT=5432
DB_NAME=digital_twin
DB_USER=postgres
DB_PASSWORD=your_password

# Database Pool Configuration
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=false  # Set to 'true' for SQL query logging

# Multi-tenancy
DEFAULT_TENANT_ID=default-tenant
```

### 3. Python Dependencies

Ensure these packages are installed:

```bash
pip install sqlalchemy[asyncio]
pip install asyncpg
pip install alembic
pip install fastapi
pip install uvicorn
```

---

## Deployment Steps

### Step 1: Run Database Migrations

```bash
cd /Users/MD/AI-Platform-ISO/platform_services/D_T/digital_twin

# Check migration status
alembic current

# Run migrations to create new tables
alembic upgrade head

# Verify tables were created
psql $DATABASE_URL -c "\dt"
```

**Expected Output:**
```
community_learnings
learning_feedback
user_networking_profiles
community_privacy_settings
learning_events
learning_insights
organization_contexts
```

### Step 2: Initialize Database Connection

The database connection is initialized automatically on first request. To test it manually:

```python
from api.dependencies import initialize_database

# Initialize
await initialize_database()

# Test connection
from api.dependencies import get_db_session

async with get_db_session() as session:
    result = await session.execute("SELECT 1")
    print("Database connected:", result.scalar())
```

### Step 3: Start the Service

```bash
cd /Users/MD/AI-Platform-ISO/platform_services/D_T/digital_twin

# Development mode
uvicorn main:app --reload --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 4: Verify API Endpoints

Check that all endpoints are available:

```bash
# Health check
curl http://localhost:8000/learning/health
curl http://localhost:8000/community/health

# API documentation
open http://localhost:8000/docs
```

---

## Testing Guide

### 1. Test Community Level - Knowledge Exchange

#### Contribute a Learning
```bash
curl -X POST "http://localhost:8000/community/knowledge/contribute" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test-tenant" \
  -d '{
    "twin_id": "twin-123",
    "contribution": {
      "title": "Implementing Remote Work BCP",
      "challenge": "Rapid transition to remote work during pandemic",
      "solution": "Deployed VPN, cloud collaboration tools, and virtual incident response",
      "outcome": "100% workforce remote within 2 weeks, zero service disruption",
      "effectiveness_score": 0.95,
      "topic": "remote_work",
      "challenge_type": "operational"
    },
    "industry": "technology",
    "size_category": "medium",
    "maturity_level": "intermediate"
  }'
```

#### Query Learnings
```bash
curl -X POST "http://localhost:8000/community/knowledge/query" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test-tenant" \
  -d '{
    "context": "Need help with remote work continuity planning",
    "industry": "technology",
    "size_category": "medium",
    "limit": 5
  }'
```

#### Get Statistics
```bash
curl "http://localhost:8000/community/knowledge/statistics" \
  -H "X-Tenant-ID: test-tenant"
```

### 2. Test Community Level - People Matching

#### Create Profile
```bash
curl -X POST "http://localhost:8000/community/people/profile?twin_id=twin-123" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test-tenant" \
  -d '{
    "user_id": "user-456",
    "display_name": "Sarah BCM Pro",
    "role": "bcm_manager",
    "experience_level": "intermediate",
    "bio": "5 years in BCM, ISO 22301 certified",
    "expertise_areas": ["bia", "risk_assessment", "crisis_management"],
    "current_challenges": ["cloud_resilience", "supply_chain"],
    "learning_interests": ["cyber_resilience"],
    "languages": ["en", "es"],
    "open_to_mentoring": true,
    "seeking_mentor": false,
    "open_to_collaboration": true,
    "visibility_level": "public",
    "show_organization": false,
    "show_real_name": true
  }'
```

#### Find Peers
```bash
curl -X POST "http://localhost:8000/community/people/find-peers" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test-tenant" \
  -d '{
    "user_id": "user-456",
    "criteria": {
      "purpose": "collaboration",
      "role": "bcm_manager",
      "expertise_areas": ["bia"],
      "limit": 10
    }
  }'
```

#### Get Network Statistics
```bash
curl "http://localhost:8000/community/people/statistics" \
  -H "X-Tenant-ID: test-tenant"
```

### 3. Test Passive Learning System

#### Learn from BIA
```bash
curl -X POST "http://localhost:8000/learning/learn/bia/twin-123" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: test-tenant" \
  -d '{
    "critical_functions": ["payment_processing", "customer_support"],
    "rto_rpo": [
      {"function": "payment", "rto_hours": 2, "rpo_hours": 0},
      {"function": "support", "rto_hours": 4, "rpo_hours": 1}
    ],
    "completion_time_days": 14,
    "details_provided": 0.85
  }'
```

#### Get Accumulated Insights
```bash
curl "http://localhost:8000/learning/insights/twin-123" \
  -H "X-Tenant-ID: test-tenant"
```

#### Detect Patterns
```bash
curl "http://localhost:8000/learning/patterns/twin-123" \
  -H "X-Tenant-ID: test-tenant"
```

### 4. Test Context Building

#### Build Context
```bash
curl "http://localhost:8000/learning/context/twin-123" \
  -H "X-Tenant-ID: test-tenant"
```

#### Get Recommendations
```bash
curl "http://localhost:8000/learning/recommendations/twin-123" \
  -H "X-Tenant-ID: test-tenant"
```

#### Compare Contexts
```bash
curl "http://localhost:8000/learning/context/compare/twin-123/twin-456" \
  -H "X-Tenant-ID: test-tenant"
```

---

## Database Verification

### Check Data in PostgreSQL

```sql
-- Connect to database
psql $DATABASE_URL

-- Check learning events
SELECT COUNT(*) FROM learning_events;
SELECT twin_id, source, created_at FROM learning_events ORDER BY created_at DESC LIMIT 5;

-- Check accumulated insights
SELECT COUNT(*) FROM learning_insights;
SELECT twin_id, insight_type, source_event_count FROM learning_insights;

-- Check community learnings
SELECT COUNT(*) FROM community_learnings;
SELECT title, industry, effectiveness_score, times_used FROM community_learnings;

-- Check user profiles
SELECT COUNT(*) FROM user_networking_profiles;
SELECT display_name, role, experience_level FROM user_networking_profiles;

-- Check context cache
SELECT COUNT(*) FROM organization_contexts;
SELECT twin_id, last_updated FROM organization_contexts;
```

---

## Performance Monitoring

### 1. Database Query Performance

```sql
-- Enable query timing
\timing on

-- Check slow queries (PostgreSQL 12+)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- queries taking > 100ms
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;
```

### 2. Connection Pool Monitoring

Add to your monitoring dashboard:

```python
from api.dependencies import _engine

# Get pool status
if _engine:
    pool = _engine.pool
    print(f"Pool size: {pool.size()}")
    print(f"Checked out: {pool.checkedout()}")
    print(f"Overflow: {pool.overflow()}")
    print(f"Checked in: {pool.checkedin()}")
```

### 3. Application Metrics

Monitor these metrics:
- Request latency per endpoint
- Database query count per request
- Cache hit rate (organization contexts)
- Learning event ingestion rate
- Community contributions per day

---

## Troubleshooting

### Problem: Database Connection Fails

**Symptoms:**
```
RuntimeError: Storage not initialized. Call initialize() first.
```

**Solution:**
1. Check environment variables are set correctly
2. Verify PostgreSQL is running: `pg_isready -h $DB_HOST -p $DB_PORT`
3. Test connection manually: `psql $DATABASE_URL -c "SELECT 1"`
4. Check firewall/network access

### Problem: Migration Fails

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check alembic configuration
cat alembic.ini

# Verify migration file exists
ls alembic/versions/

# Run migration with verbose output
alembic upgrade head --sql  # Preview SQL
alembic upgrade head  # Execute
```

### Problem: Slow Query Performance

**Symptoms:**
- API requests taking > 1 second
- High database CPU usage

**Solution:**
1. Check indexes are created:
```sql
-- Should see indexes on:
-- learning_events: (twin_id, created_at)
-- learning_insights: (twin_id, insight_type)
-- community_learnings: (industry, size_category, maturity_level)
-- user_networking_profiles: (user_id)
\di
```

2. Enable query logging:
```bash
# In .env
DB_ECHO=true
```

3. Analyze slow queries:
```sql
EXPLAIN ANALYZE
SELECT * FROM learning_events WHERE twin_id = 'twin-123';
```

### Problem: Context Cache Not Working

**Symptoms:**
- `build_context()` always recalculating
- High database load

**Solution:**
```sql
-- Check context cache entries
SELECT twin_id, last_updated,
       EXTRACT(EPOCH FROM (NOW() - last_updated)) as age_seconds
FROM organization_contexts;

-- Cache should be < 3600 seconds (1 hour)
-- If older, check UPSERT logic in context_builder_db.py
```

---

## Production Checklist

Before deploying to production:

- [ ] Database migrations tested and verified
- [ ] Environment variables configured securely (use secrets manager)
- [ ] Database connection pool sized appropriately (start with 20, tune based on load)
- [ ] Indexes verified on all foreign keys and query columns
- [ ] Database backups configured (daily at minimum)
- [ ] Monitoring and alerting set up
- [ ] Load testing performed (target: 100 req/s)
- [ ] Security review completed:
  - [ ] SQL injection protection (SQLAlchemy handles this)
  - [ ] Tenant isolation verified
  - [ ] Authentication/authorization on all endpoints
  - [ ] Sensitive data anonymization working
- [ ] Documentation reviewed and updated
- [ ] Rollback plan prepared
- [ ] Team trained on new architecture

---

## Rollback Plan

If issues occur in production:

### 1. Quick Rollback (Keep Database)

```bash
# Revert API routers to use in-memory services
cd /Users/MD/AI-Platform-ISO/platform_services/D_T/digital_twin/api/routers

# Restore from git
git checkout HEAD~1 community.py learning.py

# Restart service
systemctl restart digital-twin
```

### 2. Full Rollback (Remove Database Changes)

```bash
# Rollback migrations
alembic downgrade -1  # Rollback one migration

# Or rollback all community/learning migrations
alembic downgrade b7c8d9e0f1a2  # Rollback to before community tables

# Restart service with old code
git checkout main~5  # Or appropriate commit
systemctl restart digital-twin
```

### 3. Data Export (Before Rollback)

```bash
# Export data to preserve learnings
pg_dump -t community_learnings -t learning_events -t learning_insights \
  $DATABASE_URL > /backup/digital_twin_data_$(date +%Y%m%d).sql
```

---

## Next Steps

After successful deployment:

1. **Monitor for 48 hours** - Watch error rates, performance metrics
2. **Gather user feedback** - Are features working as expected?
3. **Performance tuning** - Adjust pool sizes, add indexes as needed
4. **Advanced Features** - Implement semantic search, real-time updates
5. **Documentation** - Update user guides with new capabilities

---

## Support

For issues or questions:
1. Check this guide first
2. Review database logs: `tail -f /var/log/postgresql/postgresql.log`
3. Check application logs: `tail -f digital_twin.log`
4. Consult the comprehensive documentation: `DIGITAL_TWIN_DATABASE_INTEGRATION_COMPLETE.md`

---

## Metrics to Track

### Day 1
- Successful deployments
- Error rate < 1%
- Average response time < 500ms
- Database connections < 80% of pool

### Week 1
- Learning events created per day
- Community contributions per week
- Context cache hit rate > 80%
- User profiles created

### Month 1
- Total learnings shared
- Peer matches made
- Pattern insights generated
- User engagement metrics

---

**Deployment Status:** ✅ Ready for Production Testing
**Last Updated:** 2025-10-15
**Version:** 1.0.0
