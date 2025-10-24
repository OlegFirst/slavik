# BIA Service Integration - Quick Start Guide

**⏱️ Total Time:** 5 minutes
**🎯 Goal:** Test bidirectional BIA Service ↔ workflow_intelligence integration
**✅ Status:** Ready for testing

---

## Prerequisites

- [ ] Redis running (EventBus)
- [ ] PostgreSQL running (case storage)
- [ ] Python 3.10+ with dependencies installed

### Quick Check

```bash
# Redis
redis-cli ping
# Expected: PONG

# PostgreSQL
psql -c "SELECT 1"
# Expected: 1 row

# Python
python3 --version
# Expected: Python 3.10+
```

---

## Step 1: Run Integration Test (2 min)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent_core/workflow_intelligence

python3 test_bia_integration.py
```

**Expected Output:**

```
🧪 BIA Service Integration Test
============================================================

✅ Test 1: Import verification
   ✓ BIA Service Listener imports OK
   ✓ PostgreSQL Adapter imports OK
   ✓ Database Manager imports OK
   ✓ EventBus imports OK

✅ Test 2: EventBus connectivity
   ✓ EventBus connected: redis://localhost:6379

✅ Test 3: PostgreSQL connectivity
   ✓ PostgreSQL connected
   ✓ Schema initialized: workflow_intelligence
   ✓ RLS enabled: True

✅ Test 4: Event listener registration
   ✓ BIA Service Listener registered
   ✓ Events: bia.assessment.completed, ...

✅ Test 5: Mock event processing
   → Publishing test event: bia.assessment.completed
   ✓ Event published successfully

============================================================
📊 Test Summary
============================================================
Total tests: 5
Passed: 5 ✓
Failed: 0 ✗

🎉 ALL TESTS PASSED!
```

**If tests fail:**
- Check Redis: `redis-cli ping`
- Check PostgreSQL: `psql bcm_platform -c "SELECT 1"`
- Check environment variables: `DATABASE_URL`, `REDIS_URL`

---

## Step 2: Start workflow_intelligence (1 min)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent_core/workflow_intelligence

python3 main.py
```

**Expected Output:**

```
INFO - Starting Workflow Intelligence Service v2.0
INFO - Port: 8037
INFO - EventBus initialized
INFO - Governance Orchestrator initialized
INFO - PDCA Rules Engine activated
INFO - PostgreSQL Storage connected for BIA integration
INFO - BIA Service Listener registered
INFO - Service ready!
═══════════════════════════════════════════════════════════
 WORKFLOW INTELLIGENCE: Nervous System ACTIVE
═══════════════════════════════════════════════════════════
 📡 EventBus: Listening for platform events
 🛡️  Governance: Validating workflows (Goals + Rules)
 🔄 PDCA: Learning from executions
 🧠 BIA Service Integration: ✅ CONNECTED
    ↳ Events: bia.assessment.completed, bia.process.created
    ↳ Learning: Cases → PostgreSQL → Benchmarks
    ↳ Storage: Multi-tenant RLS isolation
═══════════════════════════════════════════════════════════
 🎯 Platform Coverage: 8% → 15% (BIA Service connected)
 📊 Next Phase: ai_foundation integration
═══════════════════════════════════════════════════════════
```

**Service URL:** http://localhost:8037

**API Docs:** http://localhost:8037/docs

---

## Step 3: Start BIA Service (1 min)

**Option A: From terminal**

```bash
cd /Users/MD/AI-Platform-ISO/platform_services/bcm_domain/services/bia_service

python3 main.py
```

**Option B: Docker (if configured)**

```bash
docker-compose up bia-service
```

**Expected Output:**

```
INFO - Starting BIA Service
INFO - Port: 8001
INFO - EventBus initialized
INFO - Workflow Intelligence client connected
INFO - Service ready!
```

**Service URL:** http://localhost:8001

---

## Step 4: Test End-to-End Flow (1 min)

### Option A: Manual Test via API

```bash
# 1. Create BIA assessment
curl -X POST http://localhost:8001/api/v1/assessments \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "test-org-123",
    "name": "Q4 2025 BIA Assessment",
    "industry": "healthcare",
    "org_size": "medium"
  }'

# Expected response:
# {"assessment_id": "bia_abc123", "status": "in_progress"}

# 2. Add processes
curl -X POST http://localhost:8001/api/v1/assessments/bia_abc123/processes \
  -H "Content-Type: application/json" \
  -d '{
    "processes": [
      {"name": "Payment Processing", "tier": 1, "rto_hours": 4},
      {"name": "Customer Support", "tier": 2, "rto_hours": 24}
    ]
  }'

# 3. Complete assessment
curl -X POST http://localhost:8001/api/v1/assessments/bia_abc123/complete \
  -H "Content-Type: application/json" \
  -d '{
    "quality_score": 85,
    "user_satisfaction": 4.5
  }'
```

### Option B: Automated Test Script

```bash
cd /Users/MD/AI-Platform-ISO/intelligent_core/workflow_intelligence

# Run end-to-end test (TODO: create this)
python3 test_e2e_bia_flow.py
```

---

## Step 5: Verify Integration (1 min)

### Check workflow_intelligence logs

```bash
# Should see:
INFO - BIA assessment completed: bia_abc123 (2 processes, 24h, quality: 85)
INFO - Case collected for BIA: bia_abc123
INFO - Case collected: bia-case-abc123def (tenant: test-org-123)
INFO - PDCA Act phase completed for: bia_abc123
```

### Check PostgreSQL

```sql
-- Connect to database
psql bcm_platform

-- Check case collected
SELECT
    case_id,
    module,
    org_industry,
    org_size,
    total_duration_days,
    success,
    created_at
FROM workflow_intelligence.workflow_cases
ORDER BY created_at DESC
LIMIT 5;

-- Expected: 1 row with bia_abc123 data
```

### Check via API

```bash
# Get PDCA cycles
curl http://localhost:8037/pdca/cycles?module=bia

# Expected response:
# {
#   "cycles": [{
#     "workflow_id": "bia_abc123",
#     "module": "bia",
#     "plan": {...},
#     "do": {...},
#     "check": {...},
#     "act": {...}
#   }],
#   "total": 1
# }
```

---

## Troubleshooting

### Issue: EventBus not connecting

**Symptoms:**
```
WARNING - EventBus init failed: ConnectionError
WARNING - EventBus not available, skipping BIA listener
```

**Solution:**
```bash
# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine

# Verify
redis-cli ping
# Expected: PONG
```

### Issue: PostgreSQL not connecting

**Symptoms:**
```
ERROR - PostgreSQL connection failed: could not connect to server
```

**Solution:**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Should be:
# postgresql://user:password@localhost:5432/bcm_platform

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# If fails, set correct URL:
export DATABASE_URL="postgresql://user:password@localhost:5432/bcm_platform"
```

### Issue: BIA Service not publishing events

**Symptoms:**
```
# workflow_intelligence logs show:
INFO - BIA Service Listener registered
# But no "BIA assessment completed" messages
```

**Solution:**
```bash
# 1. Check BIA Service logs for EventBus errors
tail -f /path/to/bia_service.log | grep EventBus

# 2. Verify BIA Service EventBus configuration
# In BIA Service code:
# - Check event_bus.publish() is called
# - Check event type matches: "bia.assessment.completed"

# 3. Test Redis pub/sub manually
redis-cli
> SUBSCRIBE bia.assessment.completed
# In another terminal:
redis-cli
> PUBLISH bia.assessment.completed '{"test": "data"}'
```

### Issue: RLS isolation not working

**Symptoms:**
```
# Tenant A sees Tenant B's data
```

**Solution:**
```sql
-- Verify RLS enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'workflow_intelligence';

-- Should show: rowsecurity = true

-- Check RLS policies
SELECT schemaname, tablename, policyname, cmd
FROM pg_policies
WHERE schemaname = 'workflow_intelligence';

-- Re-apply RLS policies if needed
\i /Users/MD/AI-Platform-ISO/intelligent_core/workflow_intelligence/storage/rls_policies.sql
```

---

## Success Indicators

- ✅ workflow_intelligence logs show "BIA Service Listener registered"
- ✅ BIA Service logs show "EventBus initialized"
- ✅ Completing BIA assessment triggers case collection
- ✅ PostgreSQL contains new case in `workflow_cases` table
- ✅ API endpoint `/pdca/cycles?module=bia` returns collected case
- ✅ Each tenant sees only their own cases (RLS working)

---

## Next Steps

Once integration verified:

1. **Phase 2 continuation:**
   - Integrate Planning Service (similar pattern)
   - Create BaseServiceListener (extract common code)
   - Document service adapter pattern

2. **Phase 1 tasks:**
   - Connect to ai_foundation (LLM, RAG, Qdrant)
   - Enable ContextAdvisor for proactive recommendations
   - Train ML models (Duration, Risk, Success predictors)

3. **Production readiness:**
   - Add comprehensive error handling
   - Implement retry logic for failed events
   - Set up monitoring and alerts
   - Create dashboards (Grafana)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      BIA Service (8001)                      │
│  - Create assessments                                        │
│  - Manage processes                                          │
│  - Complete assessments                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ publish events
                     ↓
          ┌──────────────────────┐
          │   Redis EventBus     │
          │  - bia.assessment.*  │
          │  - bia.process.*     │
          └──────────┬───────────┘
                     │ subscribe
                     ↓
┌────────────────────────────────────────────────────────────┐
│           workflow_intelligence (8037)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        BIA Service Listener                          │  │
│  │  - handle_bia_assessment_completed()                 │  │
│  │  - handle_bia_process_created()                      │  │
│  │  - handle_bia_criticality_changed()                  │  │
│  │  - handle_bia_critical_process_identified()          │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│       ┌─────────────┼─────────────┐                         │
│       ↓             ↓             ↓                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                    │
│  │  Case   │  │  PDCA   │  │ Context │                    │
│  │Collector│  │ Engine  │  │ Advisor │                    │
│  └────┬────┘  └────┬────┘  └────┬────┘                    │
│       │            │            │                           │
└───────┼────────────┼────────────┼───────────────────────────┘
        │            │            │
        ↓            ↓            ↓
  ┌──────────────────────────────────┐
  │      PostgreSQL (bcm_platform)    │
  │  Schema: workflow_intelligence    │
  │  - workflow_cases (with RLS)      │
  │  - benchmarks                     │
  │  - ml_predictions                 │
  └───────────────────────────────────┘
```

---

## Documentation

- **Full Integration Doc:** `BIA_SERVICE_INTEGRATION_COMPLETE.md`
- **Architecture:** `NERVOUS_SYSTEM_ARCHITECTURE.md`
- **Dependency Map:** `PLATFORM_DEPENDENCY_MAP.md`
- **BIA Listener Code:** `integration/bia_service_listener.py`
- **Storage Adapter:** `storage/postgres_adapter.py`

---

**Partnership:** MD + Claude
**Date:** October 24, 2025
**Status:** ✅ Ready for testing

🚀 Let's activate the nervous system!
