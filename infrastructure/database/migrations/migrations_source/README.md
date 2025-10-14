## BCM Platform - Database Migrations

Complete SQL migrations for the unified BCM Platform database.

## 📋 Migration Overview

| # | Migration | Tables | ISO 22301 Clauses | Description |
|---|-----------|--------|-------------------|-------------|
| 001 | Schemas & Extensions | - | Foundation | PostgreSQL extensions and schema creation |
| 002 | RLS Functions | - | Foundation | Row-Level Security helper functions |
| 003 | Core Tables | 5 | Foundation | Organizations, users, teams (consolidated) |
| 004 | Community Schema | 6 | - | Specialist marketplace |
| 005 | Intelligence Schema | 3+ | - | Digital twins and AI systems |
| 006 | BIA/Risk Schemas | 4 | 8.2.2, 8.2.3 | Basic BIA and Risk tables |
| 007 | Governance/Audit | 5 | 5, 6, 7 | Policies, objectives, audit logs |
| 008 | Documents Schema | 5 | 7.5 | Document management |
| 009 | Response Schema | 7 | 8.4.2, 8.4.3 | Incident response & crisis management |
| 010 | Validation Schema | 11 | 8.5, 9.1, 9.2, 9.3, 10 | Exercises, KPIs, audits, CAPA |
| 011 | BIA/Risk Extensions | 8 | 8.2.2, 8.2.3 | Extended BIA and Risk tables |
| 012 | Governance/Compliance | 9 | 4.4, 5, 6, 7 | Extended governance and compliance |
| 013 | Learning/Planning | 8 | 7.2, 7.3, 8.4 | Training, awareness, plans |

**Total:** 13 migrations | **71 tables** | **Full ISO 22301:2019 coverage**

---

## 📊 Schema Organization

### Core Schemas

#### `public` (5 tables)
**Foundation:** Shared core entities
- `organizations` - Multi-tenant organizations (consolidated from 4 sources)
- `user_profiles` - User profiles (consolidated from 2 sources)
- `organization_users` - Organization membership
- `teams` - Teams within organizations
- `team_members` - Team membership

#### `auth` (0 tables, functions only)
**Authentication:** RLS helper functions

---

### Business Schemas

#### `community` (6 tables)
**Specialist Marketplace**
- `specialists`, `specialist_certifications`, `specialist_services`, `specialist_reviews`, `specialist_engagements`, `ai_digital_colleagues`

#### `intelligence` (3+ tables)
**Digital Twins & AI**
- `digital_twins`, `simulations`, `metrics` (partitioned by quarter)

---

### BCM Core Schemas

#### `bia` (6 tables)
**ISO 22301:2019 Clause 8.2.2 - Business Impact Analysis**
- `processes`, `templates`, `impact_assessments`, `dependencies`, `workflow_logs`, `exports`

#### `risk` (6 tables)
**ISO 22301:2019 Clause 8.2.3 - Risk Assessment**
- `risks`, `controls`, `assessments`, `treatments`, `templates`, `workflow_logs`

#### `bcm` (10 tables)
**ISO 22301:2019 Various Clauses - BCM Resources & Plans**
- Documents: `documents`, `document_access`, `document_approvals`, `document_tags`, `document_retention_policies`
- Resources: `resources`, `competence_records`, `communication_plans`
- Plans: `plans`, `procedures`

#### `response` (7 tables)
**ISO 22301:2019 Clauses 8.4.2, 8.4.3 - Incident Response**
- `incidents`, `response_teams`, `communication_templates`, `communications`, `notifications`, `escalations`, `timeline_events`

---

### Validation & Compliance Schemas

#### `validation` (11 tables)
**ISO 22301:2019 Clauses 8.5, 9.1, 9.2, 9.3, 10**
- Exercises: `exercises`, `exercise_scenarios`, `exercise_observations`, `exercise_actions`
- KPIs: `kpis`, `kpi_measurements`, `kpi_dashboards`
- Audits: `audit_plans`, `audit_findings`
- Improvement: `capa`, `management_reviews`

#### `compliance` (4 tables)
**Compliance Management**
- `requirements`, `evidence`, `assessments`, `gaps`

#### `governance` (4 tables)
**ISO 22301:2019 Clauses 5, 6, 7 - Leadership & Planning**
- `policies`, `policy_versions`, `roles`, `objectives`

---

### Supporting Schemas

#### `learning` (6 tables)
**ISO 22301:2019 Clauses 7.2, 7.3 - Competence & Awareness**
- `training_programs`, `enrollments`, `competency_assessments`, `awareness_campaigns`, `training_templates`, `user_achievements`

#### `audit` (2 tables)
**Unified Audit Trail**
- `logs` (consolidated from 5 sources), `domain_events`

---

## 🚀 Running Migrations

### Option 1: Automated (Docker Compose)

```bash
# Start services (migrations auto-run on postgres startup)
docker-compose up -d

# Verify migrations
docker-compose exec postgres psql -U postgres -d bcm_platform -c "\dt"
```

### Option 2: Manual Execution

```bash
cd migrations

# Run all migrations in order
for file in 0*.sql; do
    echo "Running $file..."
    docker-compose exec -T postgres psql -U postgres -d bcm_platform < "$file"
done
```

### Option 3: Individual Migration

```bash
# Run specific migration
docker-compose exec -T postgres psql -U postgres -d bcm_platform < 008_documents_schema.sql
```

---

## ✅ Verification

### Check All Tables

```sql
-- Connect to database
docker-compose exec postgres psql -U postgres -d bcm_platform

-- List all tables by schema
\dt public.*
\dt community.*
\dt intelligence.*
\dt bia.*
\dt risk.*
\dt bcm.*
\dt response.*
\dt validation.*
\dt compliance.*
\dt governance.*
\dt learning.*
\dt audit.*
```

### Count Tables

```sql
SELECT
    schemaname,
    COUNT(*) as table_count
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
GROUP BY schemaname
ORDER BY schemaname;
```

Expected result: **~71 tables** across 12 schemas

---

## 🔐 Row-Level Security (RLS)

All tables have RLS enabled with policies:

### Standard Policies

```sql
-- SELECT: Visible to organization members
CREATE POLICY "visible_to_org_members" FOR SELECT
    USING (auth.is_org_member(organization_id));

-- ALL: Manageable by organization admins
CREATE POLICY "manageable_by_org_admins" FOR ALL
    USING (auth.is_org_admin(organization_id));
```

### Testing RLS

```sql
-- Set tenant context
SET app.tenant_id = 'tenant_0001_acme';
SET app.current_user_id = 'user-uuid';
SET app.is_platform_admin = FALSE;

-- Query (automatically filtered by RLS)
SELECT * FROM public.organizations;
```

---

## 📈 Key Features

### Consolidations

Eliminated duplications:

1. **organizations** - 4 implementations → 1 canonical table
2. **user_profiles** - 2 implementations → 1 canonical table
3. **audit.logs** - 5 implementations → 1 unified table

### ISO 22301:2019 Compliance

Full coverage of all clauses:

- ✅ Clause 4.4 - BCMS processes
- ✅ Clause 5 - Leadership
- ✅ Clause 6 - Planning
- ✅ Clause 7 - Support (Resources, Competence, Awareness, Communication, Documented Info)
- ✅ Clause 8.2.2 - Business Impact Analysis
- ✅ Clause 8.2.3 - Risk Assessment
- ✅ Clause 8.4 - Business Continuity Plans
- ✅ Clause 8.4.2 - Incident Response
- ✅ Clause 8.4.3 - Warning and Communication
- ✅ Clause 8.5 - Exercising and Testing
- ✅ Clause 9.1 - Monitoring, Measurement, Analysis, Evaluation
- ✅ Clause 9.2 - Internal Audit
- ✅ Clause 9.3 - Management Review
- ✅ Clause 10 - Improvement (CAPA)

### Multi-tenancy

Every table includes:
- `organization_id` - Tenant identifier
- RLS policies for automatic data isolation
- Indexes on `organization_id` for performance

### Full-text Search

Key tables include `search_vector` columns using PostgreSQL's `tsvector`:
- `organizations`, `documents`, `incidents`, `exercises`, `requirements`, `plans`

### Time-series Partitioning

`intelligence.metrics` table partitioned by quarter for performance

### Audit Trails

Every table includes:
- `created_at`, `updated_at` - Automatic timestamps
- `created_by`, `updated_by` - User tracking
- Trigger: `update_updated_at_column()`

Plus dedicated workflow log tables in bia, risk, and response schemas

---

## 🔧 Maintenance

### Adding a New Migration

1. Create file: `014_new_feature.sql`
2. Follow pattern from existing migrations
3. Include indexes, RLS policies, triggers, and success message

### Re-running Migrations

Migrations use:
- `CREATE TABLE IF NOT EXISTS`
- `CREATE INDEX IF NOT EXISTS`
- For safety when re-running

---

## 📚 Related Documentation

- **[DATABASE_ARCHITECTURE.md](../DATABASE_ARCHITECTURE.md)** - Complete schema design
- **[README.md](../README.md)** - Project overview and setup
- **[QUICKSTART.md](../QUICKSTART.md)** - Quick start guide
- **[gateway/README.md](../gateway/README.md)** - API Gateway documentation

---

## 🎯 Migration Status

✅ **All migrations complete!**

**Total: 13 migrations | 71 tables | Full ISO 22301:2019 coverage**

**Next Steps:**
1. Update DATABASE_ARCHITECTURE.md with all 71 tables
2. Add API endpoints to Gateway for new modules
3. Create seed data for testing

---

**Built for BCM Platform** | PostgreSQL 16 | ISO 22301:2019 Compliant
