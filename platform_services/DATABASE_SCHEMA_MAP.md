# Platform Services - Database Schema Map

**Last Updated:** 2025-10-08
**Database:** PostgreSQL 15
**Primary Database:** bcm_platform
**Total Schemas:** 13+
**Total Tables:** 80+
**Architecture:** Multi-schema with service isolation

---

## Database Architecture

### Database Instance
- **Name:** bcm_platform
- **Type:** PostgreSQL 15+
- **Connection:** postgresql://user:pass@localhost:5432/bcm_platform
- **Async Driver:** asyncpg (postgresql+asyncpg://)
- **ORM:** SQLAlchemy (async)
- **Migrations:** Alembic

### Design Principles
1. **Schema Isolation:** Each service has its own schema
2. **Shared Tables:** audit_logs, change_history shared across services
3. **Multi-Tenancy:** tenant_id on all tables for data isolation
4. **Soft Deletes:** deleted_at timestamp for audit trail
5. **Timestamps:** created_at, updated_at on all tables
6. **UUID Primary Keys:** For distributed system compatibility

---

## Schema Overview

### Schema Organization

```
bcm_platform (database)
├── bia (schema) - BIA Service
├── risk (schema) - Risk Service
├── compliance (schema) - Compliance Service
├── governance (schema) - Governance Service
├── documents (schema) - Documents Service
├── validation (schema) - Validation Service
├── planning (schema) - Planning Service
├── plans (schema) - Plans Service
├── response (schema) - Response Service
├── learning (schema) - Learning Service
├── living_docs (schema) - Living Docs
├── simulation (schema) - Simulation Service
├── community (schema) - Community Service
├── public (schema) - Shared tables
│   ├── audit_logs
│   ├── change_history
│   └── tenant_config
└── Extensions
    ├── uuid-ossp
    ├── pgcrypto
    └── pg_trgm (for text search)
```

---

## Detailed Schema Definitions

### 1. BIA Schema (bia_service)

**Service:** BIA Service (Port 8012)
**ISO Clause:** 8.2.2

#### Tables

**bia_processes**
```sql
CREATE TABLE bia.bia_processes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    process_name VARCHAR(255) NOT NULL,
    process_owner VARCHAR(255) NOT NULL,
    criticality VARCHAR(50) NOT NULL, -- CRITICAL, HIGH, MEDIUM, LOW

    -- Recovery Objectives
    rto_hours DECIMAL(10,2) NOT NULL,
    rpo_hours DECIMAL(10,2) NOT NULL,
    mtpd_hours DECIMAL(10,2) NOT NULL,

    -- WHO Classification
    who_tier VARCHAR(50),
    essential_service BOOLEAN DEFAULT FALSE,

    -- ISO 22301 Compliance Fields
    recovery_strategy TEXT,
    personnel_requirements JSONB,
    facility_requirements JSONB,
    technology_requirements JSONB,
    information_requirements JSONB,
    legal_requirements JSONB,

    -- Dependencies
    upstream_processes JSONB,
    downstream_processes JSONB,
    external_providers JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    created_by UUID,
    updated_by UUID,

    CONSTRAINT check_recovery_objectives CHECK (rpo_hours <= rto_hours AND rto_hours <= mtpd_hours),
    INDEX idx_bia_tenant (tenant_id),
    INDEX idx_bia_criticality (criticality),
    INDEX idx_bia_owner (process_owner)
);
```

**bia_assessments**
```sql
CREATE TABLE bia.bia_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_id UUID REFERENCES bia.bia_processes(id),
    tenant_id UUID NOT NULL,

    assessment_date DATE NOT NULL,
    assessor_id UUID,

    -- Financial Impact
    financial_impact_1h DECIMAL(15,2),
    financial_impact_4h DECIMAL(15,2),
    financial_impact_24h DECIMAL(15,2),
    financial_impact_1week DECIMAL(15,2),

    -- Operational Impact
    operational_impact TEXT,
    reputational_impact TEXT,
    regulatory_impact TEXT,

    -- Recommendations
    recommendations TEXT,
    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_assessment_process (process_id),
    INDEX idx_assessment_date (assessment_date)
);
```

**bia_resources**
```sql
CREATE TABLE bia.bia_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_id UUID REFERENCES bia.bia_processes(id),
    tenant_id UUID NOT NULL,

    resource_type VARCHAR(50), -- PERSONNEL, FACILITY, TECHNOLOGY, INFORMATION
    resource_name VARCHAR(255),
    resource_description TEXT,
    quantity_required INTEGER,
    criticality VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**bia_dependencies**
```sql
CREATE TABLE bia.bia_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_id UUID REFERENCES bia.bia_processes(id),
    depends_on_process_id UUID REFERENCES bia.bia_processes(id),
    tenant_id UUID NOT NULL,

    dependency_type VARCHAR(50), -- UPSTREAM, DOWNSTREAM, MUTUAL
    dependency_strength VARCHAR(50), -- CRITICAL, HIGH, MEDIUM, LOW
    description TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(process_id, depends_on_process_id)
);
```

**Total Tables:** 4
**Total Columns:** 60+

---

### 2. Risk Schema (risk_service)

**Service:** Risk Service (Port 8040)
**ISO Clause:** 8.2.3

#### Tables

**risks**
```sql
CREATE TABLE risk.risks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    risk_title VARCHAR(255) NOT NULL,
    risk_description TEXT NOT NULL,
    risk_category VARCHAR(100),
    risk_owner UUID,

    -- Likelihood & Impact (1-5 scale)
    inherent_likelihood INTEGER CHECK (inherent_likelihood BETWEEN 1 AND 5),
    inherent_impact INTEGER CHECK (inherent_impact BETWEEN 1 AND 5),
    inherent_risk_score INTEGER GENERATED ALWAYS AS (inherent_likelihood * inherent_impact) STORED,

    residual_likelihood INTEGER,
    residual_impact INTEGER,
    residual_risk_score INTEGER GENERATED ALWAYS AS (residual_likelihood * residual_impact) STORED,

    -- Risk Level (AUTO-CALCULATED)
    risk_level VARCHAR(50) GENERATED ALWAYS AS (
        CASE
            WHEN inherent_risk_score >= 20 THEN 'CRITICAL'
            WHEN inherent_risk_score >= 15 THEN 'HIGH'
            WHEN inherent_risk_score >= 8 THEN 'MEDIUM'
            ELSE 'LOW'
        END
    ) STORED,

    -- Status
    status VARCHAR(50) DEFAULT 'IDENTIFIED',

    -- Review Schedule
    next_review_date DATE,
    review_frequency_days INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,

    INDEX idx_risk_tenant (tenant_id),
    INDEX idx_risk_owner (risk_owner),
    INDEX idx_risk_level (risk_level),
    INDEX idx_risk_score (inherent_risk_score)
);
```

**risk_assessments**
```sql
CREATE TABLE risk.risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    risk_id UUID REFERENCES risk.risks(id),
    tenant_id UUID NOT NULL,

    assessment_date DATE NOT NULL,
    assessor_id UUID,

    -- FAIR Analysis
    fair_loss_event_frequency JSONB,
    fair_loss_magnitude JSONB,
    fair_risk_exposure DECIMAL(15,2),
    fair_confidence_interval DECIMAL(5,2),

    -- Monte Carlo Results
    monte_carlo_iterations INTEGER,
    monte_carlo_results JSONB,

    assessment_notes TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);
```

**risk_treatments**
```sql
CREATE TABLE risk.risk_treatments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    risk_id UUID REFERENCES risk.risks(id),
    tenant_id UUID NOT NULL,

    treatment_type VARCHAR(50), -- AVOID, REDUCE, TRANSFER, ACCEPT
    treatment_description TEXT,
    treatment_owner UUID,

    target_likelihood INTEGER,
    target_impact INTEGER,
    target_date DATE,

    cost_estimate DECIMAL(15,2),
    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**risk_controls**
```sql
CREATE TABLE risk.risk_controls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    risk_id UUID REFERENCES risk.risks(id),
    tenant_id UUID NOT NULL,

    control_name VARCHAR(255),
    control_type VARCHAR(50), -- PREVENTIVE, DETECTIVE, CORRECTIVE
    control_description TEXT,

    effectiveness VARCHAR(50), -- EFFECTIVE, PARTIALLY_EFFECTIVE, INEFFECTIVE
    testing_frequency_days INTEGER,
    last_tested_date DATE,
    next_test_date DATE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Total Tables:** 5
**Total Columns:** 70+

---

### 3. Compliance Schema (compliance_service)

**Service:** Compliance Service (Port 8014)
**ISO Clauses:** 9.2, 10.1, 10.2

#### Tables

**audits**
```sql
CREATE TABLE compliance.audits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    audit_title VARCHAR(255) NOT NULL,
    audit_type VARCHAR(50), -- INTERNAL, EXTERNAL, CERTIFICATION
    audit_scope TEXT,

    -- ISO 22301 Clauses Covered
    clauses_covered TEXT[],

    -- Schedule
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,

    -- Team
    lead_auditor UUID,
    audit_team JSONB,

    -- Status
    status VARCHAR(50), -- PLANNED, IN_PROGRESS, COMPLETED, CANCELLED

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_audit_tenant (tenant_id),
    INDEX idx_audit_status (status),
    INDEX idx_audit_dates (planned_start_date, planned_end_date)
);
```

**audit_findings**
```sql
CREATE TABLE compliance.audit_findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID REFERENCES compliance.audits(id),
    tenant_id UUID NOT NULL,

    finding_title VARCHAR(255),
    finding_description TEXT,
    severity VARCHAR(50), -- MAJOR, MINOR, OBSERVATION
    iso_clause VARCHAR(50),

    evidence TEXT,
    root_cause TEXT,
    recommendation TEXT,

    responsible_party UUID,
    due_date DATE,
    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**nonconformities**
```sql
CREATE TABLE compliance.nonconformities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    nc_type VARCHAR(50), -- MAJOR, MINOR

    -- Root Cause Analysis
    rca_method VARCHAR(50), -- 5_WHYS, FISHBONE, FAULT_TREE
    rca_template JSONB,
    root_causes TEXT[],

    -- Context
    detected_date DATE,
    detected_by UUID,
    area_affected VARCHAR(255),
    iso_clause VARCHAR(50),

    -- Status
    status VARCHAR(50), -- OPEN, IN_PROGRESS, RESOLVED, VERIFIED

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_nc_tenant (tenant_id),
    INDEX idx_nc_type (nc_type),
    INDEX idx_nc_status (status)
);
```

**corrective_actions**
```sql
CREATE TABLE compliance.corrective_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nonconformity_id UUID REFERENCES compliance.nonconformities(id),
    tenant_id UUID NOT NULL,

    action_description TEXT NOT NULL,
    action_owner UUID,

    planned_start_date DATE,
    planned_completion_date DATE,
    actual_completion_date DATE,

    resources_required TEXT,
    cost_estimate DECIMAL(15,2),

    -- Effectiveness
    effectiveness_check_date DATE,
    effectiveness_verified BOOLEAN,
    effectiveness_notes TEXT,

    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**improvements**
```sql
CREATE TABLE compliance.improvements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    improvement_title VARCHAR(255),
    improvement_description TEXT,
    improvement_type VARCHAR(50), -- PROCESS, TECHNOLOGY, TRAINING, DOCUMENTATION

    -- Metrics
    current_state TEXT,
    target_state TEXT,
    success_criteria TEXT,
    kpis JSONB,

    -- Ownership
    improvement_owner UUID,
    stakeholders JSONB,

    -- Timeline
    start_date DATE,
    target_date DATE,
    completion_date DATE,

    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Total Tables:** 8
**Total Columns:** 90+

---

### 4. Governance Schema (governance_service)

**Service:** Governance Service (Port 8013)
**ISO Clauses:** 4, 5

#### Tables

**governance_policies**
**governance_stakeholders**
**governance_responsibilities**
**governance_context**
**governance_decisions**
**governance_reviews**

**Total Tables:** 6
**Total Columns:** 60+

---

### 5. Documents Schema (documents_service)

**Service:** Documents Service (Port 8024)
**ISO Clause:** 7.5

#### Tables

**documents**
**document_versions**
**document_approvals**
**document_access**
**document_templates**
**document_metadata**
**document_embeddings** (for Qdrant integration)

**Total Tables:** 7
**Total Columns:** 70+

---

### 6. Validation Schema (validation_service)

**Service:** Validation Service (Port 8022)
**ISO Clauses:** 8.5, 9.1-9.3, 10

#### Tables

**validation_kpis**
**validation_metrics**
**validation_alerts**
**validation_thresholds**
**validation_reports**
**validation_improvements**

**Total Tables:** 6
**Total Columns:** 65+

---

### 7. Planning Schema (planning_service)

**Service:** Planning Service (Port 8011)
**ISO Clause:** 8.3

#### Tables

**strategies**
```sql
CREATE TABLE planning.strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    name VARCHAR(255) NOT NULL,
    strategy_type VARCHAR(50), -- PREVENTIVE, DETECTIVE, CORRECTIVE, RECOVERY
    description TEXT,

    implementation_timeframe VARCHAR(50),
    approval_status VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**strategy_resources**
**cost_benefit_analyses**
**strategy_approvals**

**Total Tables:** 4
**Total Columns:** 45+

---

### 8. Plans Schema (plans_service)

**Service:** Plans Service (Port 8023)
**ISO Clause:** 8.4

#### Tables

**plans**
```sql
CREATE TABLE plans.plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    plan_name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50), -- RESPONSE, RECOVERY, CONTINUITY
    scope TEXT,

    version VARCHAR(50),
    status VARCHAR(50),
    approval_status VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**procedures**
```sql
CREATE TABLE plans.procedures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id UUID REFERENCES plans.plans(id),
    tenant_id UUID NOT NULL,

    procedure_name VARCHAR(255),
    procedure_steps JSONB,
    execution_order INTEGER,

    -- Dependencies (for DAG validation)
    depends_on_procedures UUID[],

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Circular dependency prevention
    CONSTRAINT no_self_reference CHECK (id != ALL(depends_on_procedures))
);
```

**plan_resources**
**plan_exercises**
**plan_versions**

**Total Tables:** 5
**Total Columns:** 55+

---

### 9. Response Schema (response_service)

**Service:** Response Service (Port 8041)
**ISO Clause:** 8.4.5

#### Tables

**incidents**
**incident_timeline**
**incident_teams**
**incident_escalations**
**incident_communications**
**lessons_learned**

**Total Tables:** 6
**Total Columns:** 70+

---

### 10. Learning Schema (learning_service)

**Service:** Learning Service (Port 8021)
**ISO Clauses:** 7.2, 7.3

#### Tables

**training_programs**
**training_enrollments**
**training_assessments**
**training_certifications**
**competency_profiles**
**learning_paths**

**Total Tables:** 6
**Total Columns:** 60+

---

### 11. Living Docs Schema (living_docs)

**Service:** Living Docs (Port 8034)

#### Tables

**documentation_pages**
**documentation_interactions**
**documentation_gaps**
**documentation_improvements**
**personalized_content**

**Total Tables:** 5
**Total Columns:** 45+

---

### 12. Simulation Schema (simulation)

**Service:** Simulation (Ports 8031+)

#### Tables

**simulations**
**simulation_scenarios**
**simulation_results**
**digital_twin_organizations**
**digital_twin_exercises**
**thehive_cases**
**monte_carlo_runs**

**Total Tables:** 7
**Total Columns:** 75+

---

### 13. Community Schema (community_service)

**Service:** Community Service (Ports 8032-8033)

#### Tables

**community_members**
**community_posts**
**community_knowledge**
**community_reviews**
**community_marketplace_items**

**Total Tables:** 5
**Total Columns:** 50+

---

## Shared Tables (Public Schema)

### audit_logs
```sql
CREATE TABLE public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    -- Context
    service_name VARCHAR(100),
    table_name VARCHAR(100),
    record_id UUID,

    -- Action
    action_type VARCHAR(50), -- CREATE, READ, UPDATE, DELETE
    action_description TEXT,

    -- User Context
    user_id UUID,
    user_name VARCHAR(255),
    user_role VARCHAR(100),
    ip_address INET,

    -- Request Context
    request_id UUID,
    session_id UUID,

    -- Data
    old_values JSONB,
    new_values JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_audit_tenant (tenant_id),
    INDEX idx_audit_service (service_name),
    INDEX idx_audit_table (table_name),
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_created (created_at),
    INDEX idx_audit_action (action_type)
);
```

### change_history
```sql
CREATE TABLE public.change_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    -- Record Context
    table_name VARCHAR(100),
    record_id UUID,

    -- Changes (using DeepDiff)
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,

    -- User Context
    changed_by UUID,
    changed_at TIMESTAMP DEFAULT NOW(),

    -- Metadata
    change_reason TEXT,

    INDEX idx_change_tenant (tenant_id),
    INDEX idx_change_table_record (table_name, record_id),
    INDEX idx_change_date (changed_at)
);
```

### tenant_config
```sql
CREATE TABLE public.tenant_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID UNIQUE NOT NULL,
    tenant_name VARCHAR(255) NOT NULL,

    -- Configuration
    config JSONB,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_tenant_active (is_active)
);
```

---

## Database Extensions

```sql
-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Encryption functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- JSON functions (built-in PostgreSQL 15+)
-- No extension needed
```

---

## Indexing Strategy

### Index Types Used

1. **B-Tree Indexes** (default)
   - Primary keys
   - Foreign keys
   - Equality searches
   - Range queries

2. **GIN Indexes**
   - JSONB columns
   - Text arrays
   - Full-text search

3. **Generated Columns**
   - risk_score (computed from likelihood * impact)
   - risk_level (computed from risk_score)

### Index Naming Convention
```
idx_{table}_{column(s)}
```

Examples:
- `idx_bia_tenant`
- `idx_risk_level`
- `idx_audit_tenant_service`

---

## Foreign Key Relationships

### Cross-Schema References
Generally avoided for service isolation. When needed:
- Use UUID references
- Implement at application layer
- Maintain referential integrity via EventBus

### Within-Schema References
Standard foreign keys with cascading deletes/updates where appropriate.

---

## Data Migration Strategy

### Alembic Migrations

Each service maintains its own migration history:

```
platform-services/
├── bia-service/
│   └── alembic/
│       └── versions/
│           ├── 001_initial_schema.py
│           └── 002_add_who_classification.py
├── risk-service/
│   └── alembic/
│       └── versions/
│           ├── 001_initial_schema.py
│           └── 002_add_fair_analysis.py
└── ...
```

### Migration Commands
```bash
# Create new migration
cd bia-service
alembic revision --autogenerate -m "Add WHO classification"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Performance Optimization

### Connection Pooling
```python
# SQLAlchemy async connection pool
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)
```

### Query Optimization
1. **Eager Loading:** Prevent N+1 queries
2. **Indexes:** On foreign keys, tenant_id, status fields
3. **Partitioning:** Consider for audit_logs (by created_at)
4. **Materialized Views:** For complex reporting queries

---

## Backup & Recovery

### Backup Strategy
1. **Full Backup:** Daily at 2 AM UTC
2. **Incremental Backup:** Every 6 hours
3. **WAL Archiving:** Continuous
4. **Retention:** 30 days

### Point-in-Time Recovery (PITR)
```bash
# Restore to specific timestamp
pg_restore --dbname=bcm_platform --time="2025-10-08 10:00:00"
```

---

## Security Considerations

### Row-Level Security (RLS)
```sql
-- Enable RLS on all tables
ALTER TABLE bia.bia_processes ENABLE ROW LEVEL SECURITY;

-- Policy for tenant isolation
CREATE POLICY tenant_isolation ON bia.bia_processes
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

### Encryption
- **At Rest:** PostgreSQL native encryption
- **In Transit:** SSL/TLS connections
- **Sensitive Fields:** pgcrypto for PII

### Access Control
- **Service Accounts:** Each service has its own DB user
- **Least Privilege:** Services can only access their schema
- **Audit Trail:** All DML operations logged

---

## Monitoring & Metrics

### Key Metrics
1. **Connection Pool:** Active/idle connections
2. **Query Performance:** Slow query log (>1s)
3. **Table Size:** Monitor growth trends
4. **Index Usage:** Unused indexes
5. **Lock Contention:** Deadlocks, wait times

### Prometheus Metrics
```python
# Database connection pool metrics
db_connections_active = Gauge('db_connections_active', 'Active database connections')
db_connections_idle = Gauge('db_connections_idle', 'Idle database connections')
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration')
```

---

## Quick Reference

### Connect to Database
```bash
# From host
psql -h localhost -p 5432 -U bcm_user -d bcm_platform

# From container
docker-compose exec postgres psql -U bcm_user -d bcm_platform
```

### List All Schemas
```sql
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT IN ('pg_catalog', 'information_schema');
```

### List All Tables
```sql
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename;
```

### Table Size Report
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Index Usage Report
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

---

**Document Version:** 1.0.0
**Maintained By:** Platform Database Team
**Related Documents:**
- [Platform Services Catalog](./PLATFORM_SERVICES_COMPLETE_CATALOG.md)
- [Port Allocation](./PORT_ALLOCATION.md)
- [Architecture Overview](./ARCHITECTURE.md)
