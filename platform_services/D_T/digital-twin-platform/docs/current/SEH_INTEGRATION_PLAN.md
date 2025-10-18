# SEH Integration Plan for Digital Twin Module

## Current Status
- ✅ Basic Digital Twin functionality (organizations, twins, simulations)
- ✅ Theory of Change engine implemented
- ✅ Supabase + Express + Web UI architecture
- ✅ JWT authentication base
- ⚠️ Missing SEH canonical data model
- ⚠️ No Salesforce integration
- ⚠️ Limited event streaming

## Integration Phases

### Phase 1: Data Model Extension (Week 1)
**Priority: CRITICAL**

1. **Canonical Tables** (based on SEH CDM)
   - [ ] programs, services, participants, service_deliveries
   - [ ] outcomes, indicators, targets, measurements, evidence
   - [ ] funding_programs, grant_applications, grant_awards, disbursements
   - [ ] bcm_scenarios, bcm_tests
   - [ ] consents

2. **Migration Scripts**
   ```sql
   -- Location: /database/migrations/006_seh_canonical_models.sql
   -- Based on: seh-integration/SEH_CSV_Templates.zip
   ```

### Phase 2: API Integration (Week 1-2)
**Priority: HIGH**

1. **Implement SEH OpenAPI Endpoints**
   ```
   POST /api/v1/measurements:batch
   GET  /api/v1/indicators/{id}/measurements
   POST /api/v1/sim/run
   POST /api/v1/impact/optimize
   GET  /api/v1/grants/{id}/disbursements
   ```

2. **Event System**
   - indicator.measured
   - service.delivery.recorded
   - grant.disbursement.made
   - bcm.test.completed

### Phase 3: Salesforce Integration (Week 2)
**Priority: HIGH**

1. **OAuth2 Setup**
   - Connected App configuration
   - Token management

2. **Sync Jobs**
   - Programs → Program__c (PMM)
   - Services → Service__c (PMM)
   - ServiceDelivery → Service_Delivery__c
   - Measurements → Outcome Management

3. **Bulk API Implementation**
   - Batch upserts (100k records)
   - Change Data Capture subscription

### Phase 4: Enhanced Simulations (Week 2-3)
**Priority: MEDIUM**

1. **AnyLogic Integration**
   - capacity_sweep
   - routing_vrp
   - bcm_outage
   - disbursement optimization

2. **ToC Policy Search**
   - Monte Carlo runs (1000+)
   - Grid/EA/BO optimization
   - Policy recommendations

### Phase 5: DevOps & Observability (Week 3)
**Priority: MEDIUM**

1. **Environment Setup**
   ```yaml
   dev:
     SUPABASE_URL: dev.supabase.co
     SALESFORCE_URL: test.salesforce.com
   stage:
     SUPABASE_URL: stage.supabase.co
     SALESFORCE_URL: sandbox.salesforce.com
   prod:
     SUPABASE_URL: prod.supabase.co
     SALESFORCE_URL: production.salesforce.com
   ```

2. **CI/CD Pipeline**
   - JSON Schema validation
   - SQL linting
   - E2E Postman tests
   - Load testing for simulations

3. **Observability**
   - API metrics (p95 latency)
   - Queue depth monitoring
   - Simulation duration tracking
   - Error rate dashboards

## Implementation Files

### Core Extensions
- `/database/migrations/006_seh_canonical_models.sql`
- `/src/api/seh-endpoints.js`
- `/src/events/domain-events.js`
- `/src/salesforce/connector.js`

### Workers
- `/seh-integration/workers/worker_runner.ts`
- `/seh-integration/workers/simulation-worker.js`

### Configuration
- `/seh-integration/api/openapi.yaml`
- `/seh-integration/devops/seh_worker_ci.yml`
- `/config/environments/`

## Security & Compliance

1. **Authentication**
   - Bearer JWT with roles/tenants
   - Scoped permissions per endpoint
   - Audit trail for sensitive operations

2. **Data Privacy**
   - PII pseudonymization
   - Consent management
   - GDPR compliance
   - 7-year retention for measurements

## Testing Strategy

1. **Unit Tests**
   - Domain logic
   - API endpoints
   - Event handlers

2. **Integration Tests**
   - Salesforce sync
   - Simulation runs
   - ToC optimization

3. **E2E Tests**
   - Full workflow from data intake to reports
   - Postman collection execution

## Success Metrics

- [ ] All SEH canonical tables created
- [ ] API endpoints match OpenAPI spec
- [ ] Salesforce bi-directional sync working
- [ ] Simulations return valid results
- [ ] ToC optimization converges
- [ ] 95% test coverage
- [ ] p95 API latency < 500ms
- [ ] Zero critical security issues

## Next Steps

1. **Immediate** (Today)
   - Create canonical tables migration
   - Implement batch measurement API
   - Setup basic event system

2. **This Week**
   - Complete API endpoints
   - Start Salesforce connector
   - Enhance simulation engine

3. **Next Week**
   - Full integration testing
   - DevOps pipeline setup
   - Documentation update

## Resources
- SEH OpenAPI: `/seh-integration/SEH_OpenAPI_v1.yaml`
- Postman Collection: `/seh-integration/SEH_Postman_Collection_v1.json`
- CSV Templates: `/seh-integration/SEH_CSV_Templates.zip`
- Mapping Notes: `/seh-integration/SEH_Mapping_Notes.md`