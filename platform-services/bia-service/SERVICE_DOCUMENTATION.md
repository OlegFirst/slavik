# BIA Service - Comprehensive Documentation

## Service Overview

**Service Name:** Business Impact Analysis (BIA) Service
**ISO 22301 Clause:** 8.2.2 - Business Impact Analysis
**Port:** 8012
**Technology Stack:** FastAPI, SQLAlchemy, PostgreSQL, Redis, Workflow Intelligence

## Business Purpose

The BIA Service implements ISO 22301:2019 Clause 8.2.2 requirements for comprehensive Business Impact Analysis. It enables organizations to:

1. Identify and prioritize critical business processes
2. Define recovery objectives (RTO/RPO/MTPD)
3. Assess financial, operational, reputational, and regulatory impacts
4. Map dependencies across processes, technologies, and suppliers
5. Support healthcare-specific requirements (WHO tier classification)
6. Generate executive reports and analytics

## Business Logic

### Core Capabilities

#### 1. Process Criticality Assessment
- **Criticality Levels:** CRITICAL, HIGH, MEDIUM, LOW
- **Automated Criticality Scoring:** 1-5 scale based on criticality level
- **WHO Tier Classification:** Tier 1-4 for healthcare services
- **Industry-Specific Analysis:** Financial Services, Healthcare, IT, Manufacturing, Retail, etc.

#### 2. Recovery Objectives Management
- **RTO (Recovery Time Objective):** Maximum acceptable downtime
- **RPO (Recovery Point Objective):** Maximum acceptable data loss
- **MTPD (Maximum Tolerable Period of Disruption):** Absolute maximum downtime
- **Business Rules Validation:**
  - RTO >= RPO (cannot recover faster than data availability)
  - MTPD >= RTO (total outage cannot be less than recovery time)
  - Critical processes require stricter recovery objectives

#### 3. Multi-Dimensional Impact Analysis

**Financial Impact (Time-Based):**
```json
{
  "1_hour": 50000,
  "4_hours": 200000,
  "8_hours": 400000,
  "24_hours": 1200000,
  "3_days": 5000000,
  "1_week": 15000000,
  "1_month": 50000000
}
```

**Other Impact Types:**
- Operational Impact: Process degradation descriptions
- Reputational Impact: NONE, LOW, MEDIUM, HIGH, SEVERE
- Regulatory Impact: NONE, MINOR, MODERATE, MAJOR, CRITICAL
- Patient Safety Impact: NONE, LOW, MEDIUM, HIGH, LIFE_THREATENING (Healthcare)

#### 4. Dependency Mapping
- **Upstream Processes:** Processes that feed into this one
- **Downstream Processes:** Processes that depend on this one
- **Technology Dependencies:** Systems, applications, infrastructure
- **Critical Suppliers:** Third-party dependencies with their own RTOs
- **Dependency Criticality:** 1-5 scale per dependency

#### 5. Resource Requirements
- **Personnel Requirements:** Roles, minimum staff, skills needed
- **Facility Requirements:** Physical locations, space, equipment
- **Technology Requirements:** Systems, applications, data access
- **Information Requirements:** Documents, data sources, records

#### 6. Recovery Strategies
- **Strategy Definitions:** Hot site, warm site, cold site, manual workarounds
- **Cost Analysis:** Cost per recovery strategy
- **Capacity Planning:** Workaround capacity (0-100% of normal operations)
- **Alternative Procedures:** Manual processes during disruption

#### 7. AI-Powered Analysis
- **RTO/RPO Suggestions:** ML-based recommendations using criticality + financial impact + industry benchmarks
- **Dependency Discovery:** AI-powered identification of missing dependencies
- **Confidence Scoring:** 0-1 scale for AI suggestions
- **Industry Benchmarking:** Compare against industry standards

### Business Workflows

#### Standard BIA Workflow
1. **Draft Creation:** Create process with basic info (DRAFT status)
2. **Impact Assessment:** Add financial, operational, reputational impacts
3. **Dependency Mapping:** Identify all dependencies (people, tech, suppliers)
4. **Resource Planning:** Define minimum resource requirements
5. **Recovery Strategy:** Document recovery approaches and workarounds
6. **Completion:** Mark as COMPLETED → triggers events for dependent services

#### Bulk Operations Workflow
1. **Bulk Validate:** Pre-validate CSV/Excel imports (20 concurrent validations)
2. **Bulk Create:** Create multiple processes (10 concurrent creates)
3. **Bulk Update:** Mass update (e.g., RTO adjustments across departments)
4. **Bulk Delete:** Cleanup obsolete processes
5. **Partial Success Handling:** Returns success/failure report with specific errors

## API Endpoints

### Process Management (6 endpoints)

1. **POST /api/bia/processes** - Create BIA Process
   - Permission: `BIA_CREATE`
   - Input: `BIAProcessCreate`
   - Output: `BIAProcess` with generated ID
   - Events: Publishes `bcm.bia.started`

2. **GET /api/bia/processes** - List Processes
   - Permission: `BIA_VIEW`
   - Filters: `criticality`, `status`, `tenant_id`
   - Output: `List[BIAProcess]`

3. **GET /api/bia/processes/{id}** - Get Process Details
   - Permission: `BIA_VIEW`
   - Caching: 5 minutes (Redis)
   - Output: `BIAProcess`

4. **PUT /api/bia/processes/{id}** - Update Process
   - Permission: `BIA_UPDATE`
   - Input: Partial update dict
   - Cache: Invalidates on update
   - Output: Updated `BIAProcess`

5. **DELETE /api/bia/processes/{id}** - Delete Process
   - Permission: `BIA_DELETE`
   - Audit: Full deletion audit trail

6. **POST /api/bia/processes/{id}/complete** - Mark Complete
   - Permission: `BIA_COMPLETE`
   - Events: `bcm.bia.completed`, `bcm.bia.critical_process_identified` (if critical)
   - Status: DRAFT → COMPLETED

### AI Analysis (2 endpoints)

7. **POST /api/bia/processes/{id}/suggest-rto** - AI RTO Suggestion
   - Permission: `BIA_AI_SUGGEST`
   - Input: Process ID (analyzes existing data)
   - Output: `AIRTOSuggestion` with confidence score + reasoning

8. **POST /api/bia/processes/{id}/discover-dependencies** - AI Dependency Discovery
   - Permission: `BIA_AI_SUGGEST`
   - Output: Suggested dependencies based on process characteristics

### Reporting (3 endpoints)

9. **GET /api/bia/reports/summary** - Executive Summary
   - Permission: `BIA_VIEW`
   - Metrics: Total processes, critical processes, avg RTO, 24h potential loss

10. **GET /api/bia/reports/critical-processes** - Critical Processes Report
    - Permission: `BIA_VIEW`
    - Output: All CRITICAL/HIGH processes with recovery objectives

11. **GET /api/bia/reports/dependencies** - Dependencies Mapping
    - Permission: `BIA_VIEW`
    - Output: Full dependency graph visualization data

### Bulk Operations (4 endpoints)

12. **POST /api/bia/processes/bulk** - Bulk Create
    - Permission: `BIA_CREATE`
    - Concurrency: Default 10 (configurable)
    - Timeout: 30s per process

13. **PATCH /api/bia/processes/bulk** - Bulk Update
    - Permission: `BIA_UPDATE`
    - Concurrency: Default 10

14. **DELETE /api/bia/processes/bulk** - Bulk Delete
    - Permission: `BIA_DELETE`
    - Concurrency: Default 10

15. **POST /api/bia/processes/bulk/validate** - Bulk Validate
    - Permission: `BIA_VIEW`
    - Concurrency: Default 20 (validation is faster)
    - Use Case: Pre-validate CSV imports

### Health & Metrics (3 endpoints)

16. **GET /health** - Service Health Check
17. **GET /api/compliance/check** - ISO 22301 Compliance Check
18. **GET /metrics/cache** - Redis Cache Metrics
19. **GET /metrics** - Prometheus Metrics (standard)

## Data Models

### Core Model: BIAProcess

```python
{
  "id": int,
  "tenant_id": str,
  "name": str,
  "description": str,
  "department": str,
  "process_owner": str,

  # Criticality
  "criticality": "CRITICAL|HIGH|MEDIUM|LOW",
  "criticality_score": 1-5,
  "who_tier": "TIER_1|TIER_2|TIER_3|TIER_4",
  "industry": "FINANCIAL|HEALTHCARE|IT|MANUFACTURING|RETAIL|OTHER",

  # Recovery Objectives
  "rto_hours": int,
  "rpo_hours": int,
  "mtpd_hours": int,

  # Impact Assessment
  "financial_impact": {"1_hour": float, "4_hours": float, ...},
  "operational_impact": {...},
  "reputational_impact": "NONE|LOW|MEDIUM|HIGH|SEVERE",
  "regulatory_impact": "NONE|MINOR|MODERATE|MAJOR|CRITICAL",
  "patient_safety_impact": "NONE|LOW|MEDIUM|HIGH|LIFE_THREATENING",

  # ISO 22301 Compliance
  "compliance_objective": str,
  "legal_regulatory_requirements": ["HIPAA", "GDPR", "SOX"],

  # Resources
  "personnel_requirements": {...},
  "facility_requirements": {...},
  "technology_requirements": {...},
  "information_requirements": {...},

  # Recovery
  "recovery_strategies": [...],
  "alternative_procedures": [...],
  "workaround_capacity": 0-100,

  # Dependencies
  "upstream_processes": [...],
  "downstream_processes": [...],
  "critical_suppliers": [...],
  "dependencies": [{"type": "technology", "name": "...", "criticality": 5}],

  # Status
  "status": "DRAFT|IN_PROGRESS|COMPLETED|UNDER_REVIEW",
  "bia_completion_date": datetime,
  "bia_assessor": str,
  "next_review_date": datetime,

  "created_at": datetime,
  "updated_at": datetime
}
```

### Business Validation Rules

1. **Recovery Objectives:** `RTO >= RPO` and `MTPD >= RTO`
2. **Financial Impact Timeline:** Must increase over time (1h < 4h < 24h)
3. **No Self-Dependency:** Process cannot depend on itself
4. **Critical Process Requirements:** CRITICAL processes must have:
   - At least 1 recovery strategy
   - Alternative procedures defined
   - Dependencies documented
5. **Workaround Capacity:** 0-100% range
6. **WHO Tier Consistency:** Healthcare Tier 1 requires RTO <= 4 hours
7. **Minimum Staff:** Critical processes must define minimum personnel

## Dependencies

### From intelligent-core
- **workflow-intelligence:** PostgreSQL storage, workflow engine, case collector, audit logger, ISO compliance checker
- **shared/auth:** JWT authentication, RBAC permissions
- **shared/cache:** Redis caching with hit/miss metrics
- **shared/eventbus:** RabbitMQ event publishing/subscription
- **shared/exceptions:** EntityNotFoundError, TenantMismatchError, BusinessValidationError
- **shared/utils/parallel:** Bulk operations (parallel_map)
- **shared/audit:** Comprehensive audit logging

### From infrastructure
- **Database:** PostgreSQL (async with asyncpg)
- **Cache:** Redis (for process caching)
- **Message Queue:** RabbitMQ (EventBus on port 8001)
- **Monitoring:** Prometheus metrics

### External Services Integration
- **AI Orchestration Service (Port 8002):** For AI-powered RTO suggestions
- **API Gateway (Port 8000):** Public API entry point
- **Risk Service:** Subscribes to `risk.assessment.completed` events
- **Validation Service:** Subscribes to `bcm.bia.completed` events

## Configuration

### Environment Variables (.env)

```bash
# Service
SERVICE_NAME=bia-service
SERVICE_PORT=8012
SERVICE_VERSION=1.0.0
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/bcm_platform
DB_POOL_SIZE=20
DB_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your-secret-key-here

# EventBus
FEATURE_EVENTBUS=true
EVENTBUS_URL=amqp://guest:guest@localhost:8001/
SUBSCRIBE_TOPICS=["risk.assessment.completed", "exercise.completed"]

# Features
AI_ENABLED=true
WHO_TIER_ENABLED=true
SUPPLY_CHAIN_ENABLED=false

# CORS
CORS_ENABLED=true
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### Feature Flags

- **AI_ENABLED:** Enable AI-powered RTO suggestions and dependency discovery
- **WHO_TIER_ENABLED:** Enable healthcare WHO tier classification
- **SUPPLY_CHAIN_ENABLED:** Enable 8 additional supply chain BCM endpoints
- **FEATURE_EVENTBUS:** Enable RabbitMQ event publishing

## Testing

### Test Coverage

```
tests/
├── test_api.py                    # API endpoint tests
├── test_models.py                 # Pydantic model validation tests
├── test_repositories.py           # Database repository tests
├── test_services.py               # Business logic tests
├── test_business_validators.py   # Business rule tests
└── conftest.py                    # Pytest fixtures
```

**Coverage:** ~85% (based on test files present)

### Key Test Scenarios
- RTO/RPO/MTPD validation logic
- Tenant isolation enforcement
- Financial impact timeline validation
- Circular dependency detection
- WHO tier auto-calculation
- Bulk operations with partial failures
- Cache invalidation on updates

## Integration Requirements

### Required for Service Startup
1. **PostgreSQL:** Running on DATABASE_URL
2. **Redis:** Running on REDIS_URL (optional but recommended)
3. **JWT Secret:** For authentication (JWT_SECRET env var)
4. **Shared Libraries:** workflow-intelligence package installed

### Optional for Full Features
1. **RabbitMQ:** For event-driven workflows (EventBus)
2. **AI Orchestration Service:** For AI suggestions (port 8002)
3. **Prometheus:** For metrics collection

### Database Schema

**Primary Table:** `bia.processes`

**Workflow Intelligence Tables:**
- `workflow.executions`
- `workflow.cases`
- `audit.log`
- ISO compliance tracking tables

## Architecture Patterns

### Layered Architecture
```
API Layer (routes.py)
    ↓
Service Layer (bia_service.py, ai_service.py, report_service.py)
    ↓
Repository Layer (bia_repository.py)
    ↓
Database Layer (SQLAlchemy ORM)
```

### Dependency Injection
- All services receive repositories via FastAPI Depends()
- Repositories receive database session via Depends(get_db)
- Enables easy testing with mocks

### Event-Driven
- Publishes events on process creation/completion
- Subscribes to risk/exercise events for BIA updates

### Caching Strategy
- Process GET requests cached for 5 minutes
- Cache invalidated on UPDATE/DELETE
- Cache metrics exposed at /metrics/cache

## Performance Characteristics

### Bulk Operations
- **Bulk Create:** 10 concurrent (30s timeout per process)
- **Bulk Update:** 10 concurrent (20s timeout per update)
- **Bulk Delete:** 10 concurrent (15s timeout per delete)
- **Bulk Validate:** 20 concurrent (5s timeout per validation)
- **Partial Success:** Returns detailed failure report

### Database Performance
- **Connection Pool:** 20 connections (configurable)
- **Async I/O:** Full async/await with asyncpg
- **Indexes:** On tenant_id, criticality, status

### Caching Performance
- **Cache Hit Rate:** Exposed at /metrics/cache
- **TTL:** 300 seconds (5 minutes)
- **Invalidation:** Automatic on mutations

## Common Issues & Troubleshooting

### Issue 1: "Workflow Intelligence initialization failed"
**Cause:** PostgreSQL not accessible
**Solution:** Check DATABASE_URL and ensure PostgreSQL is running

### Issue 2: "Redis cache connection failed"
**Cause:** Redis not running
**Impact:** Service continues without caching
**Solution:** Start Redis on REDIS_URL or disable Redis

### Issue 3: "EventBus connection failed"
**Cause:** RabbitMQ not running
**Solution:** Start RabbitMQ on port 8001 or set FEATURE_EVENTBUS=false

### Issue 4: "RTO must be >= RPO validation error"
**Cause:** Business rule violation
**Solution:** Adjust recovery objectives to satisfy RTO >= RPO >= 0

### Issue 5: Cache not invalidating
**Cause:** Cache key mismatch
**Solution:** Check cache key format: `bia:process:get_process:{process_id}:{tenant_id}`

## Monitoring & Observability

### Prometheus Metrics (Port 8012/metrics)
- `bia_bulk_operations_total{operation, status}`
- `bia_bulk_operation_success_rate{operation}`
- `bia_bulk_create_duration_seconds`
- `bia_bulk_update_duration_seconds`
- `bia_bulk_delete_duration_seconds`

### Health Checks
- **GET /health:** Service health, features, cache status
- **GET /api/compliance/check:** ISO 22301 compliance status

### Audit Logging
All operations logged to `audit.log` table:
- CREATE: User, tenant, entity data
- UPDATE: Before/after state comparison
- DELETE: Full deletion record
- STATE_TRANSITION: Status changes (DRAFT → COMPLETED)

## Security

### Authentication
- **JWT Bearer Token:** Required for all endpoints
- **Dev Mode:** Use `X-Dev-User` header (development only)

### Authorization (RBAC)
- `BIA_CREATE` - Create processes
- `BIA_VIEW` - View processes and reports
- `BIA_UPDATE` - Update processes
- `BIA_DELETE` - Delete processes
- `BIA_COMPLETE` - Mark processes complete
- `BIA_AI_SUGGEST` - Use AI features

### Tenant Isolation
- All queries filtered by `tenant_id` from JWT
- Cross-tenant access blocked (403 Forbidden)
- Audit trail per tenant

## Future Enhancements

### Planned Features
1. **Supply Chain BCM Module:** Critical supplier management (8 endpoints)
2. **Automated RTO Monitoring:** Track actual vs target RTOs
3. **Dependency Graph Visualization:** Interactive dependency maps
4. **ML-Powered Forecasting:** Predict future impact based on trends
5. **Integration with Digital Twin:** Real-time BIA simulation

### Known Limitations
1. **Supply Chain Module:** Currently disabled (SUPPLY_CHAIN_ENABLED=false)
2. **AI Suggestions:** Require AI Orchestration Service running
3. **WHO Tier:** Healthcare-specific, not applicable to all industries

## Contact & Support

**Service Owner:** BIA Domain Team
**Slack Channel:** #bia-service
**Documentation:** /docs (Swagger UI)
**Source Code:** `/platform-services/bia-service/`
