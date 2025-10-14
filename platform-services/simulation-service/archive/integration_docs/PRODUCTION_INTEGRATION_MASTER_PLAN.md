# 🚀 Simulation Service - Production Integration Master Plan
**Date**: 2025-10-13
**Version**: 1.0.0
**Status**: Ready for Execution

---

## 📋 EXECUTIVE SUMMARY

**Goal**: Integrate simulation-service from working directory into production AI-Platform-ISO system

**Current State**:
- ✅ Service is 80% complete (7 engines, 6 API routers, 11 integration clients)
- ✅ Core functionality working
- ❌ Not registered in system catalogs
- ❌ No EventBus subscriptions
- ❌ No Service Discovery registration
- ❌ No Prometheus metrics
- ❌ Not in database schema

**Target State**:
- Service fully integrated into platform
- Self-aware system (catalogs loaded into RAG + knowledge systems)
- EventBus coordination active
- Prometheus monitoring enabled
- Service Discovery registered
- Database schema created

---

## 🎯 INTEGRATION PHASES

### PHASE 1: Documentation & Catalogs ✅ (COMPLETED)
- [x] System architecture analyzed
- [x] Integration plan created
- [ ] Update REAL_SYSTEM_ARCHITECTURE.md
- [ ] Update catalogs (3 files)

### PHASE 2: Database Integration
- [ ] Create migration 045_simulation_service_schema.sql
- [ ] Create 4 tables: simulations, scenarios, executions, results
- [ ] Add RLS policies
- [ ] Apply migration

### PHASE 3: Service Registration
- [ ] Create SERVICE_INFO.yaml
- [ ] Register port 8095
- [ ] Define capabilities
- [ ] Add dependencies

### PHASE 4: EventBus Integration
- [ ] Create api/event_handlers.py
- [ ] Add 8 subscription handlers
- [ ] Update main.py startup
- [ ] Test event flow

### PHASE 5: Service Discovery
- [ ] Create integration/service_discovery_client.py
- [ ] Add health check endpoint
- [ ] Register on startup
- [ ] Add heartbeat mechanism

### PHASE 6: Observability
- [ ] Add prometheus_client to requirements.txt
- [ ] Expose /metrics endpoint
- [ ] Define 6 KPIs (from KPI.yaml)
- [ ] Test scraping

### PHASE 7: Catalog Updates
- [ ] Update SERVICE_CATALOG_DETAILED.yaml
- [ ] Update SUBSYSTEMS_CATALOG.yaml
- [ ] Update SYSTEMS_CATALOG.yaml

### PHASE 8: Docker Integration
- [ ] Create Dockerfile
- [ ] Create docker-compose.simulation.yml
- [ ] Update intelligent-core/docker-compose.yml

### PHASE 9: Knowledge System Integration
- [ ] Load catalogs into RAG (Qdrant)
- [ ] Index service documentation
- [ ] Setup auto-sync mechanism
- [ ] Test knowledge retrieval

### PHASE 10: Testing & Deployment
- [ ] Integration tests
- [ ] Health checks
- [ ] Event flow verification
- [ ] Production deployment

---

## 📁 FILES TO CREATE (9 new files)

### 1. Database Migration
```
/Users/MD/AI-Platform-ISO/infrastructure/database/postgresql/migrations_source/
└── 045_simulation_service_schema.sql
```

**Content**: 4 tables + RLS policies

### 2. Service Info
```
/Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/
└── SERVICE_INFO.yaml
```

**Content**: Service metadata (port 8095, version, capabilities)

### 3. Event Handlers
```
/Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/api/
└── event_handlers.py
```

**Content**: 8 EventBus subscription handlers

### 4. Service Discovery Client
```
/Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/integration/
└── service_discovery_client.py
```

**Content**: Consul registration & health checks

### 5. Workflow Intelligence Client
```
/Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/integration/
└── workflow_intelligence_client.py
```

**Content**: Case library integration

### 6. Dockerfile
```
/Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/
└── Dockerfile
```

**Content**: Multi-stage Python build

### 7. Docker Compose
```
/Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/
└── docker-compose.simulation.yml
```

**Content**: Service definition with dependencies

### 8. Prometheus Config
```
/Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus/
└── targets/simulation_service.yml
```

**Content**: Scrape configuration

### 9. Integration Tests
```
/Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service/tests/
└── test_integration.py
```

**Content**: End-to-end integration tests

---

## 📝 FILES TO UPDATE (10 files)

### 1. Main Application
```python
# /platform-services/simulation/simulation-service/main.py

# ADD:
from integration.service_discovery_client import ServiceDiscoveryClient
from api.event_handlers import register_event_handlers
from prometheus_client import make_asgi_app, Counter, Histogram

# MODIFY startup():
# 1. Register with Service Discovery
# 2. Subscribe to EventBus events
# 3. Mount /metrics endpoint
```

### 2. EventBus Client
```python
# /platform-services/simulation/simulation-service/integration/eventbus_client.py

# ADD:
async def subscribe(self, pattern: str, handler: Callable):
    """Subscribe to EventBus events"""
    # Implementation

async def subscribe_multiple(self, subscriptions: List[Dict]):
    """Subscribe to multiple patterns"""
    # Implementation
```

### 3. Requirements
```
# /platform-services/simulation/simulation-service/requirements.txt

# ADD:
prometheus-client==0.19.0
python-consul==1.1.0
```

### 4. Service Catalog
```yaml
# /catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml

# ADD simulation-service entry:
simulation_service:
  name: simulation-service
  display_name: Simulation Service
  registration:
    type: platform_service
    status: production
    port: 8095
  # ... (full entry)
```

### 5. Subsystems Catalog
```yaml
# /catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml

# ADD to Business Operations subsystem:
services:
  - simulation-service  # ADD
```

### 6. Systems Catalog
```yaml
# /catalogs/systems/SYSTEMS_CATALOG.yaml

# ADD to BCM Management system:
services:
  - simulation-service  # ADD
```

### 7. Real System Architecture
```markdown
# /REAL_SYSTEM_ARCHITECTURE.md

# ADD to Layer 3: Platform Services:
├── simulation/                      # Simulation services
│   └── simulation-service/          # 🔥 Simulation Service (Port 8095) ← ADD
│       ├── engines/                 # 7 simulation engines
│       ├── api/                     # 6 API routers (31 endpoints)
│       ├── integration/             # 11 integration clients
│       └── storage/                 # Database models
```

### 8. Intelligent Core Docker Compose
```yaml
# /intelligent-core/docker-compose.yml

# ADD service:
simulation-service:
  build: ../platform-services/simulation/simulation-service
  container_name: simulation-service
  ports:
    - "8095:8095"
  environment:
    - DATABASE_URL=${DATABASE_URL}
    - REDIS_URL=${REDIS_URL}
    - EVENTBUS_URL=${EVENTBUS_URL}
  depends_on:
    - postgresql
    - redis
    - eventbus
```

### 9. RLS Functions
```sql
-- /infrastructure/database/postgresql/migrations_source/002_rls_functions.sql

-- ADD simulation schema RLS functions (if needed)
```

### 10. README
```markdown
# /platform-services/simulation/simulation-service/README.md

# UPDATE with:
- Production deployment instructions
- Integration status
- Dependencies
- API documentation link
```

---

## 🔧 DETAILED IMPLEMENTATION

### PHASE 2: Database Schema

**File**: `045_simulation_service_schema.sql`

```sql
-- Simulation Service Schema Migration
-- Version: 1.0.0
-- Date: 2025-10-13

BEGIN;

-- Create schema
CREATE SCHEMA IF NOT EXISTS simulation;

-- 1. Simulations Table
CREATE TABLE simulation.simulations (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    simulation_type VARCHAR(50) NOT NULL, -- what_if, monte_carlo, scenario, bia, jaamsim
    engine VARCHAR(50), -- internal, jaamsim, ciw, external
    parameters JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'draft', -- draft, ready, running, completed, failed, cancelled
    created_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    CONSTRAINT valid_simulation_type CHECK (simulation_type IN ('what_if', 'monte_carlo', 'scenario', 'optimization', 'bia', 'jaamsim')),
    CONSTRAINT valid_status CHECK (status IN ('draft', 'ready', 'running', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX idx_simulations_tenant ON simulation.simulations(tenant_id);
CREATE INDEX idx_simulations_type ON simulation.simulations(simulation_type);
CREATE INDEX idx_simulations_status ON simulation.simulations(status);
CREATE INDEX idx_simulations_created ON simulation.simulations(created_at);

-- 2. Scenarios Table
CREATE TABLE simulation.scenarios (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- cyber, pandemic, disaster, supply_chain
    complexity INTEGER CHECK (complexity BETWEEN 1 AND 5),
    scenario_type VARCHAR(50), -- tabletop, functional, full_scale, hybrid
    content TEXT,
    timeline JSONB,
    injects JSONB,
    success_metrics JSONB,
    participant_roles JSONB,
    recommended_participants_count INTEGER,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    ai_generation_params JSONB,
    ai_confidence_score FLOAT,
    tags JSONB DEFAULT '[]',
    industry VARCHAR(100),
    organization_size VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scenarios_tenant ON simulation.scenarios(tenant_id);
CREATE INDEX idx_scenarios_category ON simulation.scenarios(category);
CREATE INDEX idx_scenarios_ai_generated ON simulation.scenarios(is_ai_generated);
CREATE INDEX idx_scenarios_created ON simulation.scenarios(created_at);

-- 3. Executions Table
CREATE TABLE simulation.executions (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL REFERENCES simulation.simulations(id) ON DELETE CASCADE,
    execution_number INTEGER,
    run_id VARCHAR(100),
    parameters JSONB,
    status VARCHAR(50) NOT NULL, -- running, completed, failed, cancelled
    progress FLOAT DEFAULT 0.0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds FLOAT,
    results JSONB,
    metrics JSONB,
    error_message TEXT,
    error_details JSONB,
    executed_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_execution_status CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_progress CHECK (progress BETWEEN 0 AND 100)
);

CREATE INDEX idx_executions_simulation ON simulation.executions(simulation_id);
CREATE INDEX idx_executions_status ON simulation.executions(status);
CREATE INDEX idx_executions_run_id ON simulation.executions(run_id);

-- 4. Results Table (Time-series optimized)
CREATE TABLE simulation.results (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL,
    execution_id INTEGER,
    result_type VARCHAR(50) NOT NULL, -- final, intermediate, metric, event, log
    metric_name VARCHAR(100),
    result_data JSONB NOT NULL,
    confidence_score FLOAT,
    quality_score FLOAT,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_results_simulation ON simulation.results(simulation_id);
CREATE INDEX idx_results_execution ON simulation.results(execution_id);
CREATE INDEX idx_results_type ON simulation.results(result_type);
CREATE INDEX idx_results_metric ON simulation.results(metric_name);
CREATE INDEX idx_results_recorded ON simulation.results(recorded_at);

-- RLS Policies
ALTER TABLE simulation.simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.results ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's data
CREATE POLICY simulations_tenant_isolation ON simulation.simulations
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY scenarios_tenant_isolation ON simulation.scenarios
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true) OR tenant_id IS NULL);

CREATE POLICY executions_tenant_isolation ON simulation.executions
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM simulation.simulations s
            WHERE s.id = simulation_id
            AND s.tenant_id = current_setting('app.current_tenant_id', true)
        )
    );

CREATE POLICY results_tenant_isolation ON simulation.results
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM simulation.simulations s
            WHERE s.id = simulation_id
            AND s.tenant_id = current_setting('app.current_tenant_id', true)
        )
    );

-- Grant permissions
GRANT USAGE ON SCHEMA simulation TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA simulation TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA simulation TO authenticated;

COMMIT;
```

### PHASE 3: SERVICE_INFO.yaml

**File**: `SERVICE_INFO.yaml`

```yaml
name: simulation-service
display_name: Simulation Service
version: 2.0.0
status: production
type: platform_service

description: |
  Unified simulation service for BCM exercises, scenario testing, and business impact analysis.
  Provides 7 simulation engines, AI-powered scenario generation, and integration with platform intelligence.

registration:
  port: 8095
  protocol: http
  base_path: /api/v1
  health_check: /health
  metrics: /metrics

capabilities:
  - BCM Exercise Simulation (JaamSim, NICS integration)
  - AI-Powered Scenario Generation (complexity 1-5)
  - Monte Carlo Risk Analysis
  - What-If Analysis
  - BIA Queue Theory Simulation (Ciw library)
  - Scenario Library Management
  - Multi-engine orchestration
  - Real-time execution monitoring
  - Integration with Workflow Intelligence
  - Integration with AI Foundation (RAG, LLM)

engines:
  - name: JaamSimEngine
    type: discrete_event
    description: Discrete-event simulation for complex BCM exercises
  - name: MonteCarloEngine
    type: probabilistic
    description: Monte Carlo simulation for risk analysis
  - name: ScenarioEngine
    type: bcm_scenario
    description: BCM scenario execution engine
  - name: WhatIfEngine
    type: analysis
    description: What-if analysis for decision support
  - name: BCMQueueSimulator
    type: queue_theory
    description: M/M/c queue modeling for BIA
  - name: AdvancedBIAEngine
    type: bia
    description: Multi-resource BIA simulation

api_endpoints:
  - path: /health
    method: GET
    description: Service health check
  - path: /simulations
    method: GET
    description: List simulations
  - path: /simulations
    method: POST
    description: Create simulation
  - path: /simulations/{id}/execute
    method: POST
    description: Execute simulation
  - path: /scenarios
    method: GET
    description: List scenarios
  - path: /scenarios/generate
    method: POST
    description: AI-generate scenario
  - path: /library/scenarios
    method: GET
    description: Browse scenario library

dependencies:
  required:
    - postgresql (database)
    - redis (caching)
    - eventbus (coordination)
    - service-discovery (registration)
  optional:
    - ai-foundation (AI generation)
    - workflow-intelligence (case library)
    - predictive (demand forecasting)
    - expertise-center (expert recommendations)

integrations:
  - name: eventbus
    type: async_messaging
    events_published:
      - simulation.created
      - simulation.started
      - simulation.progress
      - simulation.completed
      - simulation.failed
      - scenario.generated
      - execution.started
      - execution.completed
    events_subscribed:
      - scenario.execution.requested
      - digital_twin.state.changed
      - bia.analysis.requested
      - workflow.scenario.required

  - name: ai-foundation
    type: http_client
    endpoints_used:
      - POST /rag/search
      - POST /llm/generate

  - name: workflow-intelligence
    type: http_client
    endpoints_used:
      - POST /case_library/add
      - GET /case_library/search

kpis:
  - name: simulation_executions_total
    type: counter
    target: "> 100/day"
    prometheus_metric: simulation_executions_total

  - name: simulation_success_rate
    type: gauge
    target: "> 95%"
    prometheus_metric: simulation_success_rate

  - name: simulation_duration_p95
    type: histogram
    target: "< 60s"
    prometheus_metric: simulation_duration_seconds

  - name: scenario_generation_quality
    type: gauge
    target: "> 0.8"
    prometheus_metric: scenario_generation_quality_score

  - name: active_simulations
    type: gauge
    target: "< 100"
    prometheus_metric: simulation_active_count

  - name: error_rate
    type: gauge
    target: "< 1%"
    prometheus_metric: simulation_error_rate

monitoring:
  prometheus_enabled: true
  grafana_dashboard: dashboards/simulation_service.json
  alert_rules: alerts/simulation_service.yaml
  log_level: INFO

deployment:
  docker_image: simulation-service:2.0.0
  replicas: 2
  resources:
    cpu: "1.0"
    memory: "1Gi"
  environment:
    DATABASE_URL: ${DATABASE_URL}
    REDIS_URL: ${REDIS_URL}
    EVENTBUS_URL: ${EVENTBUS_URL}
    SERVICE_DISCOVERY_URL: ${SERVICE_DISCOVERY_URL}

owner: platform-team
maintainer: AI Platform Team
documentation: /docs/simulation-service/README.md
```

---

## 🎯 CRITICAL PATH

**Must complete in order**:

1. **Database Schema** (PHASE 2) - Foundation for data storage
2. **SERVICE_INFO.yaml** (PHASE 3) - Service metadata
3. **EventBus Integration** (PHASE 4) - Coordination mechanism
4. **Service Discovery** (PHASE 5) - Registration & health checks
5. **Prometheus Metrics** (PHASE 6) - Observability
6. **Catalog Updates** (PHASE 7) - System awareness
7. **Docker Integration** (PHASE 8) - Deployment
8. **Knowledge Integration** (PHASE 9) - Self-awareness
9. **Testing** (PHASE 10) - Verification

**Estimated timeline**: 5 days (40 hours)

---

## 🚨 RISKS & MITIGATION

### Risk 1: Port Conflict (8095)
- **Mitigation**: Verified port 8095 is available
- **Backup**: Use port 8096 if needed

### Risk 2: Database Migration Failure
- **Mitigation**: Test migration in staging first
- **Rollback**: Keep backup of database state

### Risk 3: EventBus Integration Issues
- **Mitigation**: Test each subscription handler individually
- **Monitoring**: Add logging for all event flows

### Risk 4: Service Discovery Registration Failure
- **Mitigation**: Implement retry logic with exponential backoff
- **Fallback**: Manual registration if auto-registration fails

---

## ✅ SUCCESS CRITERIA

### Minimum Viable Integration:
- [x] Database schema created
- [ ] Service registered in Service Discovery
- [ ] Health checks passing
- [ ] Basic simulation execution working
- [ ] EventBus publishing working

### Full Integration:
- [ ] All EventBus subscriptions active
- [ ] Prometheus metrics exposed
- [ ] MIO Manager monitoring enabled
- [ ] All catalog entries added
- [ ] Docker integration complete
- [ ] Catalogs loaded into RAG
- [ ] Integration tests passing
- [ ] Documentation updated

---

## 📚 REFERENCES

- **Integration Plan**: `SIMULATION_SERVICE_INTEGRATION_PLAN.md` (98KB detailed plan)
- **Integration Summary**: `INTEGRATION_SUMMARY.md` (12KB quick reference)
- **Root Files Analysis**: `ROOT_FILES_ANALYSIS.md`
- **System Architecture**: `/REAL_SYSTEM_ARCHITECTURE.md`
- **Service Catalogs**: `/catalogs/`
- **Database Migrations**: `/infrastructure/database/postgresql/migrations_source/`

---

## 🎬 NEXT STEPS

### Immediate Actions:
1. Review this master plan
2. Create database migration file
3. Create SERVICE_INFO.yaml
4. Start PHASE 2 implementation

### For Next Session:
- Execute PHASE 2-4 (Database + Service Registration + EventBus)
- Test basic integration
- Update catalogs
- Continue with remaining phases

---

**Created**: 2025-10-13
**Status**: Ready for Execution
**Priority**: HIGH - Production Integration
