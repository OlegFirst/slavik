# Simulation Service Integration Summary
**Quick Reference Guide**

**Date**: 2025-10-13
**Full Plan**: [SIMULATION_SERVICE_INTEGRATION_PLAN.md](./SIMULATION_SERVICE_INTEGRATION_PLAN.md)

---

## Current Status: 80% Complete

### What's Working
- Core simulation engine (JaamSim, SimPy)
- Database models (SQLAlchemy ORM)
- API endpoints (FastAPI)
- EventBus client (publishing)
- AI Foundation client
- Scenario generation
- Storage layer

### What's Missing
- Database schema in production DB
- EventBus subscriptions (handlers not registered)
- Service Discovery registration
- Prometheus metrics endpoint
- MIO Manager monitoring
- Service Catalog entries
- Docker integration

---

## Integration Points Needed

### 1. Database (CRITICAL)
**Action**: Create dedicated `simulation` schema in platform PostgreSQL
- Migration: `045_simulation_service_schema.sql`
- Tables: simulations, scenarios, executions, results
- RLS policies for multi-tenancy
- **Time**: 4-6 hours

### 2. EventBus (HIGH)
**Action**: Register event subscriptions + handlers
- Subscribe to 8 event types (scenario requests, twin updates, etc.)
- Create event_handlers.py
- Start consumer in main.py
- **Time**: 6-8 hours

### 3. Service Discovery (HIGH)
**Action**: Register service with Consul
- Create SERVICE_INFO.yaml
- Implement service_discovery_client.py
- Register in lifespan
- **Time**: 3-4 hours

### 4. Prometheus (HIGH)
**Action**: Expose /metrics endpoint
- Add prometheus_client
- Define 6 metrics
- Instrument code
- **Time**: 2-3 hours

### 5. Catalog (MEDIUM)
**Action**: Add to 3 catalog files
- SERVICE_CATALOG_DETAILED.yaml
- SUBSYSTEMS_CATALOG.yaml
- SYSTEMS_CATALOG.yaml
- **Time**: 1-2 hours

---

## Quick Start Checklist

### Critical Path (Must Do First)
```bash
# Phase 1: Database
[ ] Create migration 045_simulation_service_schema.sql
[ ] Add RLS helper functions
[ ] Run migration
[ ] Test with real data

# Phase 2: EventBus
[ ] Create api/event_handlers.py (8 handlers)
[ ] Update integration/eventbus_client.py (add subscriptions)
[ ] Update main.py (start consumer)
[ ] Test event flow

# Phase 3: Service Discovery
[ ] Create SERVICE_INFO.yaml
[ ] Create integration/service_discovery_client.py
[ ] Update main.py (register/deregister)
[ ] Verify registration

# Phase 4: Prometheus
[ ] Add prometheus-client to requirements.txt
[ ] Define metrics in main.py
[ ] Mount /metrics endpoint
[ ] Instrument orchestrator.py
[ ] Test metrics output
```

### Integration Path (Do Next)
```bash
# Phase 5: Catalog
[ ] Update SERVICE_CATALOG_DETAILED.yaml
[ ] Update SUBSYSTEMS_CATALOG.yaml
[ ] Update SYSTEMS_CATALOG.yaml

# Phase 6-8: AI Integration
[ ] Test AI Foundation connection
[ ] Register with Scenario Intelligence
[ ] Create Workflow Intelligence client

# Phase 9: Docker
[ ] Create Dockerfile
[ ] Create docker-compose.simulation.yml
[ ] Test container build

# Phase 10: Testing
[ ] Create integration tests
[ ] Run end-to-end test
[ ] Verify MIO Manager sees service
```

---

## File Creation Checklist

### New Files to Create (7 files)
```
1. /infrastructure/database/postgresql/migrations_source/045_simulation_service_schema.sql
2. /platform-services/simulation/simulation-service/SERVICE_INFO.yaml
3. /platform-services/simulation/simulation-service/api/event_handlers.py
4. /platform-services/simulation/simulation-service/integration/service_discovery_client.py
5. /platform-services/simulation/simulation-service/integration/workflow_intelligence_client.py
6. /platform-services/simulation/simulation-service/Dockerfile
7. /platform-services/simulation/simulation-service/docker-compose.simulation.yml
```

### Files to Update (8 files)
```
1. /platform-services/simulation/simulation-service/main.py (add integrations)
2. /platform-services/simulation/simulation-service/integration/eventbus_client.py (add subscriptions)
3. /platform-services/simulation/simulation-service/requirements.txt (add prometheus_client)
4. /infrastructure/database/postgresql/migrations_source/002_rls_functions.sql (add helpers)
5. /catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml (add entry)
6. /catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml (add entry)
7. /catalogs/systems/SYSTEMS_CATALOG.yaml (add entry)
8. /intelligent-core/docker-compose.yml (add simulation-service)
```

---

## Configuration Changes

### settings.py (Verify These URLs)
```python
# Current configuration (check these are correct):
port: 8095
eventbus_url: "http://localhost:8055"
ai_orchestrator_url: "http://localhost:8026"
workflow_intelligence_url: "http://localhost:8037"
ai_foundation_url: "http://localhost:8025"
scenario_orchestrator_url: "http://localhost:8090"  # Note: Port 8090 (Scenario Intelligence)

# Need to add:
service_discovery_url: "http://localhost:8500"
prometheus_url: "http://localhost:9090"
mio_manager_url: "http://localhost:8046"
```

### Database URL (Change This)
```python
# FROM (dedicated database):
database_url: "postgresql://simulation_user:simulation_pass@localhost:5432/simulation_db"

# TO (platform database):
database_url: "postgresql://postgres:<password>@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
# Note: Schema is already set to 'simulation' in models.py ✓
```

---

## Event Integration Map

### Events to Publish (Already Implemented ✓)
```python
simulation.created              # When simulation configured
simulation.started              # When execution starts
simulation.progress.updated     # Progress updates
simulation.completed            # When finished successfully
simulation.failed               # When execution fails
simulation.scenario.generated   # AI-generated scenario
simulation.case.created         # Learning case extracted
simulation.knowledge.stored     # Knowledge added to RAG
```

### Events to Subscribe (NOT YET IMPLEMENTED ✗)
```python
scenario.execution.requested    # Scenario Intelligence → Execute scenario
digital_twin.state.changed      # Digital Twin → Update simulation
predictive.demand.forecasted    # Predictive → Adjust simulation load
workflow.pdca.plan              # Workflow Intelligence → Test PDCA
bia.critical_function.identified # BIA Service → Simulate impact
community.scenario.shared       # Community → Import scenario
governance.policy.changed       # Governance → Test compliance
workflow.test.requested         # General test request
```

---

## Database Schema

### Tables in simulation schema
```sql
simulation.simulations          -- Main simulation configs
simulation.scenarios            -- BCM exercise scenarios
simulation.executions           -- Execution history
simulation.results              -- Time-series results
```

### Existing vs New
```
intelligence.simulations        -- FOR Digital Twin (existing)
simulation.simulations          -- FOR BCM Exercises (new)

These serve different purposes:
- intelligence.simulations = Digital Twin predictions/forecasts
- simulation.simulations = BCM exercise simulations/testing
```

---

## Service Discovery Info

### Registration Data
```yaml
Service Name: simulation-service
Port: 8095
Health Check: /health (every 10s)
Tags: [simulation, bcm, platform-services]
Category: platform_services
Subsystem: bcm_business_logic
Functional System: testing_validation
ISO Clauses: [8.4.6, 8.5, 10.1]
```

### KPIs to Track
```
1. simulation_executions_total (counter)
2. simulation_duration_seconds (histogram)
3. scenario_generation_duration_seconds (histogram)
4. simulation_results_quality_score (gauge)
5. active_simulations (gauge)
6. scenarios_library_size (gauge)
```

---

## Dependencies Overview

### Critical (Must Have)
- PostgreSQL (5432) - Database
- Redis (6379) - Cache + EventBus backend
- EventBus (8055) - Event coordination
- Service Discovery (8500) - Service registry
- Prometheus (9090) - Metrics

### Integration (Should Have)
- MIO Manager (8046) - Monitoring
- AI Foundation (8025) - RAG + LLM
- Scenario Intelligence (8090) - Scenarios
- Workflow Intelligence (8037) - PDCA

### Optional (Nice to Have)
- Community Intelligence (8030)
- Predictive (8031)
- Digital Twin (8096)

---

## Testing Strategy

### Unit Tests (Existing)
- Core simulation logic
- Scenario generation
- Metrics calculation

### Integration Tests (To Add)
```python
test_database_integration()         # Database CRUD + RLS
test_eventbus_pub_sub()             # Event publishing/subscribing
test_service_discovery()            # Registration/health checks
test_prometheus_metrics()           # Metrics exposure
test_mio_manager_monitoring()       # MIO sees service
test_full_simulation_flow()         # End-to-end
```

---

## Common Issues & Solutions

### Issue 1: Database Connection Fails
**Symptom**: `postgresql://simulation_user` connection refused
**Solution**: Update DATABASE_URL to use platform database URL

### Issue 2: EventBus Events Not Received
**Symptom**: Events published but no handlers execute
**Solution**: Start consumer in main.py lifespan with `await eventbus_client.start_consumer()`

### Issue 3: Service Not in Service Discovery
**Symptom**: MIO Manager doesn't see service
**Solution**: Create SERVICE_INFO.yaml and register in main.py

### Issue 4: Prometheus Not Scraping
**Symptom**: No metrics in Prometheus UI
**Solution**: Add /metrics endpoint with prometheus_client

### Issue 5: RLS Blocking Queries
**Symptom**: No data returned even though it exists
**Solution**: Check tenant_id matches, verify RLS policies created

---

## Timeline

### Aggressive (3 days)
- Day 1: Database + EventBus (10-14 hours)
- Day 2: Service Discovery + Prometheus + Catalog (6-9 hours)
- Day 3: AI Integration + Docker + Testing (8-12 hours)

### Realistic (5 days)
- Day 1: Phase 1 (Database) - 6 hours
- Day 2: Phase 2 (EventBus) - 8 hours
- Day 3: Phase 3-4 (Service Discovery + Prometheus) - 6 hours
- Day 4: Phase 5-8 (Catalog + AI + Workflow + Docker) - 8 hours
- Day 5: Phase 10 (Testing + Verification) - 6 hours

### Conservative (7 days)
- Add 2 days buffer for issues/debugging

---

## Success Criteria

### Minimum Viable Integration (MVP)
- [ ] Database schema created
- [ ] EventBus publishing working
- [ ] Service registered in Service Discovery
- [ ] /health endpoint working
- [ ] Can create and execute basic simulation

### Full Integration
- [ ] All EventBus subscriptions working
- [ ] Prometheus metrics exposed
- [ ] MIO Manager monitoring active
- [ ] All catalog entries added
- [ ] Docker container builds
- [ ] Integration tests passing
- [ ] Can generate AI scenarios
- [ ] PDCA integration working

---

## Next Actions

### Immediate (Do Now)
1. Review full integration plan
2. Set up development environment
3. Start Phase 1 (Database)

### Today
1. Complete Phase 1 (Database)
2. Start Phase 2 (EventBus)

### This Week
1. Complete Phases 1-4 (Critical path)
2. Start Phase 5-7 (Integrations)

---

## Resources

### Documentation
- Full Plan: [SIMULATION_SERVICE_INTEGRATION_PLAN.md](./SIMULATION_SERVICE_INTEGRATION_PLAN.md)
- System Architecture: `/Users/MD/AI-Platform-ISO/REAL_SYSTEM_ARCHITECTURE.md`
- Service Catalog: `/catalogs/README.md`
- EventBus: `/infrastructure/eventbus/README.md`
- Service Discovery: `/infrastructure/runtime/service-discovery/README.md`

### Key Files
- Settings: `config/settings.py`
- Main App: `main.py`
- EventBus Client: `integration/eventbus_client.py`
- Database: `storage/database.py`
- Models: `storage/models.py`

### Contact
- Platform Team: platform-team@company.com
- Integration Questions: See full plan Section 16

---

## Appendix: Architecture Quick Reference

```
AI-Platform-ISO
├── Layer 0: Infrastructure
│   ├── PostgreSQL (5432)
│   ├── Redis (6379)
│   ├── EventBus (8055)
│   ├── API Gateway (8000)
│   ├── Service Discovery (8500)
│   ├── Prometheus (9090)
│   └── Grafana (3000)
│
├── Layer 1: AI Office (8 Agents)
│   ├── MIO Manager (8046) ← EYES: Monitors all services
│   ├── AI Orchestrator (8026)
│   └── ... (6 more agents)
│
├── Layer 2: Intelligent Core (12 Services)
│   ├── Workflow Intelligence (8037) ← BRAIN: Goals + Rules
│   ├── AI Orchestration (8030)
│   ├── Scenario Intelligence (8090) ← Integration point
│   ├── AI Foundation (8025) ← Integration point
│   └── ... (8 more services)
│
├── Layer 3: Platform Services (11 Services)
│   ├── BIA Service (8008)
│   ├── Risk Service (8009)
│   ├── ... (7 more services)
│   └── Simulation Service (8095) ← YOU ARE HERE
│
└── Layer 4: Interface
    └── Admin Panel (3030)
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-13
**Status**: Ready for Implementation

For detailed information, see [SIMULATION_SERVICE_INTEGRATION_PLAN.md](./SIMULATION_SERVICE_INTEGRATION_PLAN.md)
