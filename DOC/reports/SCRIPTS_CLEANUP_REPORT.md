# 🧹 Scripts & Docker Files - Cleanup Report

**Date:** 2025-10-11
**Status:** Analysis Complete
**Action Required:** Comprehensive Cleanup + Docker Regeneration

---

## 📊 Current State

### Shell Scripts Found
- **Total:** 119+ shell scripts
- **Location:** Scattered across project
- **Issues:** Many duplicates, obsolete wrappers, old deployment scripts

### Docker Compose Files Found
- **Total:** 36+ docker-compose files
- **Location:** Multiple directories
- **Issues:** Outdated, conflicting configurations, unclear purpose

### Dockerfiles Found
- **Total:** 180+ directories with Dockerfiles
- **Issues:** Inconsistent, old patterns, missing for some services

---

## 🔍 Detailed Analysis

### 1. Shell Scripts by Category

#### A. Wrapper Scripts (intelligent-core/wrappers/)
**Status:** ⚠️ OUTDATED - Need to be replaced
```
run_expertise_center.sh
run_ai_workflow_optimizer.sh
run_workflow_engine.sh
run_ai_orchestration.sh
run_coordination_center.sh
run_event_intelligence.sh
run_community_intelligence.sh
run_ai_foundation.sh
run_predictive.sh
run_collective.sh
run_workflow_intelligence.sh
```
**Issues:**
- Simple wrappers that just cd + python
- No health checks
- No dependency management
- No environment validation

**Recommendation:** DELETE - Replace with proper startup scripts

#### B. Interface Start Scripts (DUPLICATES!)
**Status:** ❌ DUPLICATES - Clean up immediately

**Set 1:** `/interface/interface-materials/interface/admin_panel/`
```
test_compliance.sh
check-services.sh
start.sh
```

**Set 2:** `/interface/админ/admin_panel/`
```
test_compliance.sh
check-services.sh
start.sh
```

**Set 3:** `/interface/interface-materials/interface/admin-control-center/`
```
test_compliance.sh
check-services.sh
start.sh
```

**Set 4:** `/interface/админ/admin-control-center/`
```
test_compliance.sh
check-services.sh
start.sh
```

**Recommendation:** KEEP ONLY ONE SET - Delete 3 duplicates

#### C. System BCM Service Scripts
**Status:** ✅ GOOD - Keep these
```
/intelligent-core/system-bcm-service/database/migrate.sh (6.7K)
/intelligent-core/system-bcm-service/scripts/integrate-with-platform.sh (12K)
/intelligent-core/system-bcm-service/scripts/validate-deployment.sh (14K)
/intelligent-core/system-bcm-service/scripts/health-check.sh (13K)
/intelligent-core/system-bcm-service/scripts/start.sh (3.3K)
```

**Recommendation:** KEEP - Well-structured and useful

#### D. Old Deployment Scripts (можетпригодится/)
**Status:** ❌ ARCHIVE - Move to archive
```
можетпригодится/COGNITIVE ORCHESTRATION-ISO22301/BCM-v1/deploy-scripts/
  - quick-deploy.sh
  - init-odoo.sh
  - start-platform.sh
  - run_gateway.sh
```

**Recommendation:** Already in можетпригодится (archive folder) - No action needed

### 2. Docker Compose Files by Category

#### A. Active Project Docker Compose (KEEP)
```
✅ /infrastructure/observability/docker-compose.grafana.yml
✅ /intelligent-core/orchestration/ai-orchestration/docker-compose.yml
✅ /intelligent-core/system-bcm-service/docker-compose.yml
```

#### B. Interface Docker Compose (DUPLICATES!)
```
⚠️ /interface/interface-materials/interface/admin_panel/docker-compose.yml
⚠️ /interface/админ/admin_panel/docker-compose.yml
⚠️ /interface/interface-materials/interface/admin-control-center/docker-compose.yml
⚠️ /interface/админ/admin-control-center/docker-compose.yml
```

**Recommendation:** CONSOLIDATE - Keep only one

#### C. Old Docker Compose (можетпригодится/)
**Status:** ❌ ARCHIVE - Already archived

All docker-compose files in `можетпригодится/COGNITIVE ORCHESTRATION-ISO22301/` are old versions:
- docker-compose.minimal.yml
- docker-compose.quick.yml
- docker-compose.backend.yml
- docker-compose.monitoring.yml
- docker-compose.ai-agents.yml
- docker-compose.dev.yml
- docker-compose.odoo.yml
- docker-compose.docker-ai.yml
- docker-compose.production.yml
- docker-compose.full.yml
- docker-compose-current.yml
- docker-compose.infrastructure.yml
- docker-compose.frontend.yml
- docker-compose.ai.yml

**Recommendation:** Already archived - No action needed

### 3. Dockerfiles Analysis

#### A. Services WITH Dockerfiles (47 total)
```
✅ Infrastructure (7):
  - analytics-specialist
  - balancer-service
  - api-gateway
  - github-integration
  - notification-service
  - Service Discovery (needs creation)
  - EventBus (needs creation)

✅ Intelligent Core (11):
  - ai-orchestration
  - coordination-center
  - ai-foundation/learning-knowledge
  - ai_workflow_optimizer
  - collective
  - community_intelligence
  - event_intelligence
  - expertise-center (multiple)
  - predictive
  - system-bcm-service
  - workflow-engine (needs creation)

✅ Platform Services (18):
  - bia-service
  - compliance-monitoring
  - process-analytics
  - marketplace
  - portal
  - compliance-service
  - documents-service
  - governance-service
  - learning-service
  - living-docs
  - planning_service
  - plans_service
  - response-service
  - risk-service
  - digital-twin (multiple)
  - scenario_orchestrator (multiple)
  - simulation (multiple)
  - validation-service

✅ Interface (7):
  - admin-control-center (multiple)
  - admin_panel (multiple)
  - api-gateway
  - web-app
  - mvp-platform (frontend + backend)

⚠️ Archive (156):
  - можетпригодится/* (old versions)
```

#### B. Services WITHOUT Dockerfiles (Critical Services)
```
❌ Infrastructure:
  - /infrastructure/runtime/service-discovery (PORT 8500) ⚠️ CRITICAL
  - /infrastructure/runtime/eventbus (PORT 8001) ⚠️ CRITICAL
  - /infrastructure/runtime/message-queue (PORT 8002)
  - /infrastructure/runtime/realtime-websocket (PORT 8050)
  - /infrastructure/security/auth
  - /infrastructure/security/secrets-manager
  - /infrastructure/AI-office-infrastructure/orchestrator
  - /infrastructure/AI-office-infrastructure/agent-router
  - /infrastructure/AI-office-infrastructure/project-agent
  - /infrastructure/AI-office-infrastructure/devops-agent
  - /infrastructure/AI-office-infrastructure/ai-event-manager
  - /infrastructure/AI-office-infrastructure/mio-manager
  - /infrastructure/integration/mcp-server
  - /infrastructure/integration/partisia-contracts

❌ Intelligent Core:
  - /intelligent-core/workflow-engine (PORT 8030) ⚠️ CRITICAL
  - /intelligent-core/workflow_intelligence
```

---

## 🎯 Action Plan

### Phase 1: Immediate Cleanup (Today)

#### Task 1.1: Remove Duplicate Interface Scripts
```bash
# Keep: /interface/админ/admin_panel/ and /interface/админ/admin-control-center/
# Delete: /interface/interface-materials/interface/*

rm -rf /Users/MD/AI-Platform-ISO/interface/interface-materials/interface/admin_panel
rm -rf /Users/MD/AI-Platform-ISO/interface/interface-materials/interface/admin-control-center
```

#### Task 1.2: Remove Obsolete Wrapper Scripts
```bash
# These will be replaced with proper startup scripts
rm -rf /Users/MD/AI-Platform-ISO/intelligent-core/wrappers/
```

#### Task 1.3: Remove Duplicate Docker Compose
```bash
# Keep only the ones in /interface/админ/
rm /Users/MD/AI-Platform-ISO/interface/interface-materials/interface/admin_panel/docker-compose.yml
rm /Users/MD/AI-Platform-ISO/interface/interface-materials/interface/admin-control-center/docker-compose.yml
```

### Phase 2: Create New Dockerfiles (Priority Services)

#### Template: Standard Service Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:{PORT}/health')" || exit 1

# Run
CMD ["python", "main.py"]
```

#### Priority Services to Create:

1. **Service Discovery** (PORT 8500) - CRITICAL
   - Location: `/infrastructure/runtime/service-discovery/`
   - Depends: None
   - Priority: 1

2. **EventBus** (PORT 8001) - CRITICAL
   - Location: `/infrastructure/runtime/eventbus/`
   - Depends: None
   - Priority: 1

3. **Workflow Engine** (PORT 8030) - CRITICAL
   - Location: `/intelligent-core/workflow-engine/`
   - Depends: EventBus
   - Priority: 2

4. **Message Queue** (PORT 8002)
   - Location: `/infrastructure/runtime/message-queue/`
   - Depends: None
   - Priority: 2

5. **Realtime WebSocket** (PORT 8050)
   - Location: `/infrastructure/runtime/realtime-websocket/`
   - Depends: EventBus
   - Priority: 2

### Phase 3: Create docker-compose.full-stack.yml

Structure:
```yaml
version: '3.8'

services:
  # Layer 1: Core Infrastructure (no dependencies)
  postgres:
  redis:
  service-discovery:
  eventbus:

  # Layer 2: Runtime Services (depend on Layer 1)
  message-queue:
  realtime-websocket:
  auth-service:
  secrets-manager:

  # Layer 3: Platform Services (depend on Layer 2)
  workflow-engine:
  ai-orchestration:
  coordination-center:
  system-bcm-service:
  community-intelligence:

  # Layer 4: Business Services (depend on Layer 3)
  bia-service:
  compliance-service:
  governance-service:
  risk-service:
  response-service:
  documents-service:
  plans-service:

  # Layer 5: AI Office Infrastructure (depend on Layer 3)
  orchestrator:
  agent-router:
  project-agent:
  analytics-specialist:
  ai-event-manager:

  # Layer 6: Interface (depend on all layers)
  admin-panel:
  api-gateway:

  # Layer 7: Observability (monitor all layers)
  prometheus:
  grafana:
```

### Phase 4: Create Startup Scripts

#### startup-full-stack.sh
```bash
#!/bin/bash
# Start entire platform in correct order

echo "🚀 Starting AI Platform ISO Full Stack..."

# Check prerequisites
./scripts/check-prerequisites.sh || exit 1

# Start by layers
docker-compose -f docker-compose.full-stack.yml up -d postgres redis
sleep 5

docker-compose -f docker-compose.full-stack.yml up -d service-discovery eventbus
sleep 5

docker-compose -f docker-compose.full-stack.yml up -d message-queue realtime-websocket auth-service
sleep 5

docker-compose -f docker-compose.full-stack.yml up -d workflow-engine ai-orchestration
sleep 5

docker-compose -f docker-compose.full-stack.yml up -d bia-service compliance-service governance-service
sleep 5

docker-compose -f docker-compose.full-stack.yml up -d orchestrator agent-router
sleep 5

docker-compose -f docker-compose.full-stack.yml up -d admin-panel api-gateway
sleep 5

docker-compose -f docker-compose.full-stack.yml up -d prometheus grafana

echo "✅ Full stack started!"
echo "📊 Check status: docker-compose -f docker-compose.full-stack.yml ps"
```

---

## 📈 Summary

### Files to DELETE
- ❌ `/intelligent-core/wrappers/` (11 files) - Obsolete wrapper scripts
- ❌ `/interface/interface-materials/interface/admin_panel/` (3 files) - Duplicate scripts
- ❌ `/interface/interface-materials/interface/admin-control-center/` (3 files) - Duplicate scripts
- ❌ Duplicate docker-compose files (2 files)

**Total to delete:** ~20 files

### Files to CREATE
- ✅ 16 new Dockerfiles for critical services
- ✅ 1 docker-compose.full-stack.yml
- ✅ 1 startup-full-stack.sh
- ✅ 1 check-prerequisites.sh
- ✅ 1 health-check-all.sh

**Total to create:** ~20 files

### Files to KEEP
- ✅ System BCM Service scripts (5 files) - Well structured
- ✅ Active docker-compose files (~10 files) - In use
- ✅ можетпригодится/* - Already archived, no action needed

---

## 🎯 Next Steps

1. ✅ **Confirm cleanup plan with user**
2. ⏳ **Execute Phase 1: Cleanup** (5 minutes)
3. ⏳ **Execute Phase 2: Create Dockerfiles** (30 minutes)
4. ⏳ **Execute Phase 3: Create docker-compose.full-stack.yml** (20 minutes)
5. ⏳ **Execute Phase 4: Create startup scripts** (15 minutes)
6. ⏳ **Test full stack startup** (10 minutes)

**Total Time:** ~1.5 hours

---

**Last Updated:** 2025-10-11
**Status:** ✅ Ready for cleanup
**Port Conflicts:** ✅ Already fixed (8030, 8050)
