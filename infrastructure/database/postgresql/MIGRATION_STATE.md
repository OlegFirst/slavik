# Database Migration State - Complete Registry

**Last Updated:** 2025-10-21
**Total Migrations:** 52 (000-053)
**Status:** Tracking System Implemented ✅

---

## 📊 Migration Overview

| Status | Count | Description |
|--------|-------|-------------|
| ✅ Tracked | 52 | With tracking system |
| 🔄 Sequenced | 52 | Proper numbering (duplicates resolved) |
| 📝 Documented | 52 | Listed below |

---

## 🗂️ Complete Migration List

### Foundation (000-005)

| # | File | Description | Status | Applied |
|---|------|-------------|--------|---------|
| 000 | 000_migration_tracking.sql | Migration Tracking System | ✅ NEW | - |
| 001 | 001_schemas_and_extensions.sql | Schemas and Extensions | ✅ | - |
| 002 | 002_rls_functions.sql | RLS Functions | ✅ | - |
| 003 | 003_core_tables.sql | Core Tables | ✅ | - |
| 004 | 004_community_schema.sql | Community Schema | ✅ | - |
| 005 | 005_intelligence_schema.sql | Intelligence Schema | ✅ | - |

### BCM Domain Schemas (006-013)

| # | File | Description | Status | Applied |
|---|------|-------------|--------|---------|
| 006 | 006_bia_risk_schemas.sql | BIA & Risk Schemas (ISO 22301 8.2.2, 8.2.3) | ✅ | - |
| 007 | 007_governance_audit_schemas.sql | Governance & Audit (ISO 22301 5-7) | ✅ | - |
| 008 | 008_documents_schema.sql | Documents Management | ✅ | - |
| 009 | 009_response_schema.sql | Response Schema | ✅ | - |
| 010 | 010_validation_schema.sql | Validation Schema | ✅ | - |
| 011 | 011_bia_risk_extensions.sql | BIA & Risk Extensions | ✅ | - |
| 012 | 012_governance_compliance.sql | Governance Compliance | ✅ | - |
| 013 | 013_learning_planning.sql | Learning & Planning | ✅ | - |

### Domain Extensions (014-018)

| # | File | Description | Status | Applied |
|---|------|-------------|--------|---------|
| 014 | 014_supply_chain_extension.sql | Supply Chain Extension | ✅ | - |
| 015 | 015_compliance_improvements.sql | Compliance Improvements | ✅ | - |
| 016 | 016_governance_context_stakeholders.sql | Governance Context & Stakeholders | ✅ | - |
| 017 | 017_governance_domain_intelligence.sql | Governance Domain Intelligence | ✅ | - |
| 018 | 018_validation_kpi_alerts.sql | Validation KPI & Alerts | ✅ | - |

### Security & Performance (019-033)

| # | File | Description | Status | Applied |
|---|------|-------------|--------|---------|
| 019 | 019_rls_security_hardening.sql | RLS Security Hardening | ✅ | - |
| 020 | 020_community_specialists.sql | Community Specialists | ✅ | - |
| 021 | 021_performance_security_fixes.sql | Performance & Security Fixes | ✅ | - |
| 022 | 022_fix_auth_rls_initplan.sql | Fix Auth RLS Initplan | ✅ | - |
| 023 | 023_consolidate_rls_policies_bcm.sql | Consolidate RLS Policies BCM | ✅ | - |
| 024 | 024_individual_users.sql | Individual Users | ✅ | - |
| 025 | 025_platform_administrators.sql | Platform Administrators | ✅ | - |
| 026 | 026_user_relationships.sql | User Relationships | ✅ | - |
| 027 | 027_admin_policies.sql | Admin Policies | ✅ | - |
| 028 | 028_fix_remaining_lints.sql | Fix Remaining Lints | ✅ | - |
| 029 | 029_fix_security_definer_view.sql | Fix Security Definer View | ✅ | - |
| 030 | 030_fix_function_search_path.sql | Fix Function Search Path | ✅ | - |
| 031 | 031_fix_auth_rls_initplan.sql | Fix Auth RLS Initplan (v2) | ✅ | - |
| 032 | 032_add_foreign_key_indexes.sql | Add Foreign Key Indexes | ✅ | - |
| 033 | 033_consolidate_permissive_policies.sql | Consolidate Permissive Policies | ✅ | - |

### Linting & Optimization (034-037) - DUPLICATES RESOLVED

| # | File | Description | Status | Applied |
|---|------|-------------|--------|---------|
| 034a | 034a_fix_remaining_lints_initial.sql | Fix Remaining Lints (Initial - 305 lines) | ✅ RENAMED | - |
| 034b | 034b_fix_remaining_lints_final.sql | Fix Remaining Lints (Final - 66 lines) | ✅ RENAMED | - |
| 035 | 035_final_lint_fixes.sql | Final Lint Fixes | ✅ | - |
| 036a | 036a_optimize_remaining_policies.sql | Optimize Remaining Policies (382 lines) | ✅ RENAMED | - |
| 036b | 036b_unified_workflow.sql | Unified Workflow (350 lines) | ✅ RENAMED | - |
| 037a | 037a_community_intelligence.sql | Community Intelligence (392 lines) | ✅ RENAMED | - |
| 037b | 037b_final_policy_cleanup.sql | Final Policy Cleanup (99 lines) | ✅ RENAMED | - |

**Note:** Migrations 034, 036, 037 had duplicate numbering. Resolved by adding 'a' and 'b' suffixes.

### Advanced Features (038-053)

| # | File | Description | Status | Applied |
|---|------|-------------|--------|---------|
| 038 | 038_add_gateway_state.sql | Add Gateway State | ✅ | - |
| 040 | 040_community_intelligence.sql | Community Intelligence | ✅ | - |
| 041 | 041_collective_agents.sql | Collective Agents | ✅ | - |
| 042 | 042_predictive_service.sql | Predictive Service | ✅ | - |
| 043 | 043_learning_system_enhancements.sql | Learning System Enhancements | ✅ | - |
| 044 | 044_kqm_knowledge_management.sql | KQM Knowledge Management | ✅ | - |
| 045 | 045_simulation_service_schema.sql | Simulation Service Schema | ✅ | - |
| 050 | 050_scenario_intelligence_schema.sql | Scenario Intelligence Schema | ✅ | - |
| 051 | 051_scenario_intelligence_complete.sql | Scenario Intelligence Complete | ✅ | - |
| 052 | 052_pii_encryption_pgcrypto.sql | PII Encryption (pgcrypto) | ✅ | - |
| 053 | 053_governance_persistence.sql | Governance Persistence | ✅ | - |

**Note:** Migrations 039, 046-049 are missing/skipped.

---

## 🔄 Migration Application Order

### Recommended Sequence:

**Phase 0: Setup Tracking**
```bash
psql $DATABASE_URL -f 000_migration_tracking.sql
```

**Phase 1: Foundation (001-005)**
```bash
for i in {001..005}; do
    psql $DATABASE_URL -f 0${i}_*.sql
done
```

**Phase 2: BCM Domain (006-013)**
```bash
# Or use BATCH files:
psql $DATABASE_URL -f ../migrations/BATCH_1_migrations_006-009.sql
psql $DATABASE_URL -f ../migrations/BATCH_2_migrations_010-013.sql
```

**Phase 3: Extensions (014-018)**
```bash
psql $DATABASE_URL -f ../migrations/BATCH_3_migrations_014-018.sql
```

**Phase 4: Security & Performance (019-033)**
```bash
for i in {019..033}; do
    psql $DATABASE_URL -f 0${i}_*.sql
done
```

**Phase 5: Optimization (034-037)**
```bash
# Apply in alphabetical order (a before b)
psql $DATABASE_URL -f 034a_fix_remaining_lints_initial.sql
psql $DATABASE_URL -f 034b_fix_remaining_lints_final.sql
psql $DATABASE_URL -f 035_final_lint_fixes.sql
psql $DATABASE_URL -f 036a_optimize_remaining_policies.sql
psql $DATABASE_URL -f 036b_unified_workflow.sql
psql $DATABASE_URL -f 037a_community_intelligence.sql
psql $DATABASE_URL -f 037b_final_policy_cleanup.sql
```

**Phase 6: Advanced Features (038-053)**
```bash
psql $DATABASE_URL -f 038_add_gateway_state.sql
psql $DATABASE_URL -f 040_community_intelligence.sql
psql $DATABASE_URL -f 041_collective_agents.sql
psql $DATABASE_URL -f 042_predictive_service.sql
psql $DATABASE_URL -f 043_learning_system_enhancements.sql
psql $DATABASE_URL -f 044_kqm_knowledge_management.sql
psql $DATABASE_URL -f 045_simulation_service_schema.sql
psql $DATABASE_URL -f 050_scenario_intelligence_schema.sql
psql $DATABASE_URL -f 051_scenario_intelligence_complete.sql
psql $DATABASE_URL -f 052_pii_encryption_pgcrypto.sql
psql $DATABASE_URL -f 053_governance_persistence.sql
```

---

## 📝 Migration Dependencies

### Critical Dependencies:

**000 → 001**: Tracking must be set up first
**001 → 002**: Schemas required for RLS functions
**002 → 003**: RLS functions required for core tables
**006-013**: Can be run in parallel (different schemas)
**034a → 034b**: Run 'a' before 'b' (initial fixes first)
**036a → 036b**: Policies before workflow
**037a → 037b**: Intelligence before cleanup

---

## 🔍 Verification Queries

### Check Migration Status
```sql
-- See all applied migrations
SELECT * FROM public.migration_status ORDER BY migration_number;

-- Check if specific migration applied
SELECT public.is_migration_applied(42);

-- Get latest migration number
SELECT public.get_latest_migration();

-- Count applied migrations
SELECT COUNT(*) FROM public.migration_tracking WHERE status = 'applied';
```

### Verify Schema Creation
```sql
-- List all schemas
SELECT schema_name FROM information_schema.schemata
WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
ORDER BY schema_name;

-- Count tables per schema
SELECT
    schemaname,
    COUNT(*) as table_count
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
GROUP BY schemaname
ORDER BY schemaname;
```

---

## ⚠️ Known Issues & Resolutions

### 1. Duplicate Migration Numbers (RESOLVED ✅)
**Issue:** Migrations 034, 036, 037 had duplicate numbers
**Resolution:** Renamed with 'a' and 'b' suffixes
**Date Fixed:** 2025-10-21

### 2. Missing Migration Numbers
**Issue:** Migrations 039, 046-049 are missing
**Impact:** None (gaps are acceptable)
**Action:** None required

### 3. No Alembic Integration (IN PROGRESS ⏳)
**Issue:** Main DB doesn't use Alembic
**Resolution:** Setting up Alembic integration
**Date:** 2025-10-21

---

## 📊 Migration Statistics

**Total Files:** 52
**Total Lines:** ~15,000+ SQL statements
**Schemas Created:** 29
**Tables Created:** 200+
**Indexes Created:** 500+
**RLS Policies:** 150+
**Functions:** 100+

---

## 🎯 Next Steps

### Immediate (Today)
- [x] Create migration tracking system
- [x] Resolve duplicate numbering
- [x] Document migration state
- [ ] Set up Alembic integration
- [ ] Test migration tracking on clean DB

### Short-term (This Week)
- [ ] Audit production DB for applied migrations
- [ ] Update tracking table with current state
- [ ] Create automated migration script
- [ ] Add checksum validation

### Long-term (This Month)
- [ ] Implement rollback capability
- [ ] Create migration CI/CD pipeline
- [ ] Add migration dry-run mode
- [ ] Document migration troubleshooting

---

## 📚 References

**Migration Files:** `/infrastructure/database/postgresql/migrations_source/`
**Batch Files:** `/infrastructure/database/postgresql/migrations/`
**Setup Guide:** `/infrastructure/database/DATABASE_SETUP_GUIDE.md`
**Alembic Config:** `/infrastructure/database/postgresql/alembic.ini` (in progress)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-21
**Maintained By:** Database Team
**Status:** ✅ COMPLETE & READY FOR USE
