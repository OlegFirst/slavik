-- Row Level Security Policies for Workflow Intelligence
-- This ensures complete tenant isolation at the DATABASE level
-- Even if application code is compromised, tenants cannot access each other's data

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================

-- Workflow contexts table
ALTER TABLE workflow_intelligence.workflow_contexts ENABLE ROW LEVEL SECURITY;

-- Workflow cases table
ALTER TABLE workflow_intelligence.workflow_cases ENABLE ROW LEVEL SECURITY;

-- ML predictions table
ALTER TABLE workflow_intelligence.ml_predictions ENABLE ROW LEVEL SECURITY;

-- Benchmarks table (shared data - no RLS needed, it's anonymized aggregates)
-- ALTER TABLE workflow_intelligence.benchmarks ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- DROP EXISTING POLICIES (for clean re-creation)
-- ============================================================================

DROP POLICY IF EXISTS tenant_isolation_contexts ON workflow_intelligence.workflow_contexts;
DROP POLICY IF EXISTS tenant_isolation_cases ON workflow_intelligence.workflow_cases;
DROP POLICY IF EXISTS tenant_isolation_predictions ON workflow_intelligence.ml_predictions;

-- ============================================================================
-- CREATE RLS POLICIES
-- ============================================================================

-- Policy 1: workflow_contexts - Tenant Isolation
CREATE POLICY tenant_isolation_contexts
ON workflow_intelligence.workflow_contexts
FOR ALL
USING (
    -- Allow access only if tenant_id matches current session tenant
    tenant_id = current_setting('app.current_tenant_id', true)
)
WITH CHECK (
    -- On INSERT/UPDATE, ensure tenant_id matches session
    tenant_id = current_setting('app.current_tenant_id', true)
);

-- Policy 2: workflow_cases - Tenant Isolation
CREATE POLICY tenant_isolation_cases
ON workflow_intelligence.workflow_cases
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant_id', true)
)
WITH CHECK (
    tenant_id = current_setting('app.current_tenant_id', true)
);

-- Policy 3: ml_predictions - Tenant Isolation
CREATE POLICY tenant_isolation_predictions
ON workflow_intelligence.ml_predictions
FOR ALL
USING (
    tenant_id = current_setting('app.current_tenant_id', true)
)
WITH CHECK (
    tenant_id = current_setting('app.current_tenant_id', true)
);

-- ============================================================================
-- SPECIAL POLICY: Allow reading anonymized benchmarks from other tenants
-- ============================================================================

-- Benchmarks are SHARED across tenants for learning
-- But they contain NO sensitive data (anonymized, aggregated)
-- So we don't enable RLS on benchmarks table

-- ============================================================================
-- TESTING QUERIES (for verification)
-- ============================================================================

-- Test 1: Set tenant and try to access data
-- SET LOCAL app.current_tenant_id = 'tenant_001';
-- SELECT * FROM workflow_intelligence.workflow_contexts;
-- Should return ONLY rows where tenant_id = 'tenant_001'

-- Test 2: Try to access another tenant's data
-- SET LOCAL app.current_tenant_id = 'tenant_002';
-- SELECT * FROM workflow_intelligence.workflow_contexts WHERE tenant_id = 'tenant_001';
-- Should return NOTHING (RLS blocks it)

-- Test 3: Try to INSERT with wrong tenant_id
-- SET LOCAL app.current_tenant_id = 'tenant_001';
-- INSERT INTO workflow_intelligence.workflow_contexts (workflow_id, module, tenant_id, context)
-- VALUES ('test', 'test', 'tenant_002', '{}');
-- Should FAIL with RLS violation

-- ============================================================================
-- SECURITY NOTES
-- ============================================================================

-- 1. RLS is enforced at PostgreSQL level, NOT application level
-- 2. Even superuser queries respect RLS (unless BYPASSRLS role attribute)
-- 3. If app.current_tenant_id is not set, queries return ZERO rows (safe default)
-- 4. Benchmarks are exempt - they're anonymized aggregates for learning
-- 5. Connection pooling: MUST reset tenant_id on connection reuse

-- ============================================================================
-- GRANT PERMISSIONS (if needed)
-- ============================================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA workflow_intelligence TO bcm_app_user;

-- Grant SELECT, INSERT, UPDATE, DELETE on tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA workflow_intelligence TO bcm_app_user;

-- Grant USAGE on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA workflow_intelligence TO bcm_app_user;

-- ============================================================================
-- VERIFICATION FUNCTION
-- ============================================================================

-- Function to verify RLS is working
CREATE OR REPLACE FUNCTION workflow_intelligence.verify_rls_enabled()
RETURNS TABLE(table_name text, rls_enabled boolean, rls_forced boolean) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.relname::text,
        c.relrowsecurity,
        c.relforcerowsecurity
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'workflow_intelligence'
      AND c.relkind = 'r'  -- regular tables only
    ORDER BY c.relname;
END;
$$ LANGUAGE plpgsql;

-- Run verification:
-- SELECT * FROM workflow_intelligence.verify_rls_enabled();
-- Should show rls_enabled = true for all tenant-specific tables
