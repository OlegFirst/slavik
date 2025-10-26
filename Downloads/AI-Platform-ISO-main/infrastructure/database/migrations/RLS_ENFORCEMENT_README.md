# RLS FORCE ENFORCEMENT - Security Hardening

## 🎯 Purpose

This migration enforces **FORCE ROW LEVEL SECURITY** on all 122 tenant-specific tables in the BCM Platform database. This is a **CRITICAL SECURITY FIX** required for production deployment.

## 🔴 Problem Statement

### Current State (Insecure)
- RLS is **ENABLED** on 122 tables
- Table owners and superusers can **BYPASS** RLS policies
- **Security risk:** Admins can accidentally or maliciously access cross-tenant data

### After Migration (Secure)
- RLS is **FORCED** on 122 tables
- **ALL users** including owners/superusers must comply with RLS policies
- **Multi-tenant data isolation** is guaranteed

## 📊 Impact

| Metric | Before | After |
|--------|--------|-------|
| Tables with RLS | 122 | 122 |
| Tables with FORCE RLS | 0 ❌ | 122 ✅ |
| Admin bypass possible | YES ❌ | NO ✅ |
| ISO 22301 Compliance | 81% | 85%+ |
| Security Score | 79/100 | 82/100 |

## ✅ Benefits

1. **Multi-Tenant Security** - Complete data isolation between organizations
2. **ISO 22301 Compliance** - Satisfies Clause 5.2 (Information Security)
3. **GDPR Compliance** - Meets Article 32 (Security of Processing)
4. **Zero Trust** - No user can bypass security policies
5. **Audit Ready** - Demonstrates robust security controls

## 📁 Files Included

### 1. `999_force_rls_enforcement.sql`
Main migration script that enables FORCE RLS on all 122 tables.

**Features:**
- Transaction-wrapped for atomicity
- Organized by schema (audit, bcm, bia, compliance, etc.)
- Built-in verification logic
- Success/failure reporting

**Execution time:** ~2-5 seconds

### 2. `check_rls_status.sql`
Diagnostic script to verify RLS enforcement status.

**Output:**
- Summary statistics
- List of tables with/without RLS
- Policy count by schema
- Security recommendations

## 🚀 Usage

### Prerequisites

```bash
# Ensure you have database access
psql -U postgres -d bcm_platform -c "SELECT version();"

# Backup database (RECOMMENDED)
pg_dump -U postgres bcm_platform > backup_before_rls_$(date +%Y%m%d).sql
```

### Step 1: Check Current Status

```bash
cd infrastructure/database/migrations
psql -U postgres -d bcm_platform -f check_rls_status.sql
```

**Expected output BEFORE migration:**
```
Tables with RLS enabled: 122
Tables with FORCE RLS: 0
⚠️ WARNING: 122 tables have RLS, but only 0 have FORCE RLS
```

### Step 2: Run Migration

```bash
psql -U postgres -d bcm_platform -f 999_force_rls_enforcement.sql
```

**Expected output:**
```
BEGIN
SET
SET
ALTER TABLE
ALTER TABLE
... (122 ALTER TABLE commands)
NOTICE:  ========================================
NOTICE:  RLS FORCE ENFORCEMENT - VERIFICATION
NOTICE:  ========================================
NOTICE:  Tables with RLS enabled: 122
NOTICE:  Tables with FORCE RLS: 122
NOTICE:  ✅ SUCCESS: FORCE RLS enabled on 122 tables
COMMIT
```

### Step 3: Verify Success

```bash
psql -U postgres -d bcm_platform -f check_rls_status.sql
```

**Expected output AFTER migration:**
```
Tables with RLS enabled: 122
Tables with FORCE RLS: 122
✅ EXCELLENT: All 122 tenant tables have FORCE RLS
```

## ✅ Testing

### Test 1: Verify RLS Enforcement

```sql
-- Connect as superuser
psql -U postgres -d bcm_platform

-- Try to query tenant data without tenant_id set
SET app.tenant_id = '';
SELECT COUNT(*) FROM bia.processes;
-- Expected: 0 rows (RLS blocks access)

-- Set tenant_id and retry
SET app.tenant_id = 'org-123';
SELECT COUNT(*) FROM bia.processes WHERE organization_id = 'org-123';
-- Expected: Returns data for org-123 only
```

### Test 2: Application Compatibility

```bash
# Run application tests
cd platform_services/bcm_domain
pytest tests/ -v

# Expected: All tests should pass
# RLS enforcement is transparent to application code
```

### Test 3: Performance Check

```sql
-- Check query performance (minimal impact expected)
EXPLAIN ANALYZE SELECT * FROM bia.processes WHERE organization_id = 'org-123';

-- RLS adds minimal overhead (<5% typically)
```

## 🔧 Troubleshooting

### Issue: Migration fails with "permission denied"

**Solution:**
```bash
# Ensure you're running as database owner or superuser
psql -U postgres -d bcm_platform -f 999_force_rls_enforcement.sql
```

### Issue: Application queries return empty results

**Cause:** Tenant context not set

**Solution:**
```python
# Ensure app sets tenant_id before queries
await connection.execute("SET app.tenant_id = %s", [tenant_id])
```

### Issue: "policy for command does not exist"

**Cause:** RLS policy not defined for specific operation

**Solution:**
```sql
-- Check existing policies
SELECT * FROM pg_policies WHERE tablename = 'your_table';

-- Add missing policy if needed
CREATE POLICY "policy_name" ON schema.table FOR SELECT ...
```

## 🔄 Rollback (Emergency Only)

**⚠️ NOT RECOMMENDED** - Only use if migration causes critical issues

```sql
BEGIN;

-- Disable FORCE RLS (reverts to ENABLE RLS)
ALTER TABLE schema.table DISABLE FORCE ROW LEVEL SECURITY;
-- Repeat for all 122 tables

COMMIT;
```

**Better approach:** Fix the root cause instead of rolling back security

## 📋 Deployment Checklist

- [ ] **Backup database** before migration
- [ ] **Run check_rls_status.sql** to verify current state
- [ ] **Execute 999_force_rls_enforcement.sql** in staging environment
- [ ] **Test application** functionality in staging
- [ ] **Verify RLS enforcement** with check_rls_status.sql
- [ ] **Monitor application logs** for RLS-related errors
- [ ] **Execute migration in production** during maintenance window
- [ ] **Re-verify** RLS status in production
- [ ] **Update security documentation** with new RLS status

## 📊 Affected Schemas

| Schema | Tables | Description |
|--------|--------|-------------|
| audit | 2 | Audit logs, domain events |
| bcm | 12 | BCM plans, documents, procedures |
| bia | 10 | Business Impact Analysis |
| community | 23 | Specialists, peer reviews |
| compliance | 5 | Assessments, evidence, gaps |
| governance | 6 | Policies, roles, objectives |
| intelligence | 3 | Digital twins, metrics |
| learning | 20 | Training, competencies |
| public | 15 | Users, organizations, teams |
| response | 7 | Incidents, escalations |
| risk | 6 | Risk assessments, controls |
| scenario_intelligence | 3 | Scenarios, executions |
| validation | 13 | Exercises, audits, KPIs |
| workflow | 4 | BPMN processes, tasks |
| workflow_intelligence | 1 | PDCA cycles |
| **TOTAL** | **122** | All tenant-specific tables |

## 🔒 Security Considerations

### What FORCE RLS Prevents

1. **Admin data leakage** - DB admins cannot accidentally query cross-tenant data
2. **Debugging mistakes** - Engineers must explicitly set tenant context
3. **SQL injection** - Even successful injection cannot bypass tenant isolation
4. **Privilege escalation** - Compromised admin accounts still respect RLS

### What FORCE RLS Does NOT Prevent

1. **Application bugs** - Code must still set correct tenant_id
2. **Authentication bypass** - Access control happens at application layer
3. **Database backups** - Backups contain all tenant data (encrypt backups!)

## 📖 References

- **30-Day Remediation Plan**: `docs/30_DAY_REMEDIATION_PLAN.md` (Day 1-2)
- **PostgreSQL RLS Docs**: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- **ISO 22301 Clause 5.2**: Information Security Requirements
- **GDPR Article 32**: Security of Processing

## 🎯 Success Criteria

✅ All 122 tenant tables have FORCE RLS enabled
✅ Application tests pass without modification
✅ Query performance impact < 5%
✅ No cross-tenant data leakage possible
✅ Security audit score improves to 82/100+

## 📞 Support

For questions or issues:
- **Slack**: #bcm-platform-security
- **Email**: security@ai-platform.com
- **Docs**: docs/SECURITY_AUDIT_REPORT_2025-10-19.md

---

**Status:** ✅ READY FOR PRODUCTION
**Risk Level:** LOW (security improvement only)
**Estimated Time:** 2-5 seconds execution
**Rollback Available:** Yes (not recommended)

Last Updated: 2025-10-26
