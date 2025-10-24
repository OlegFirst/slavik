-- ============================================
-- BCM Platform - Unified Database
-- Migration 034: Fix Remaining Supabase Lints (v2)
-- ============================================
-- Fixes only what hasn't been fixed yet
-- ============================================

-- ============================================
-- Part 1: Fix Function Search Path Mutable
-- ============================================

ALTER FUNCTION core_auth.set_updated_at()
    SET search_path = core_auth, public, pg_temp;

ALTER FUNCTION workflow_intelligence.verify_rls_enabled()
    SET search_path = workflow_intelligence, public, pg_temp;

-- ============================================
-- Part 2: Move Vector Extension (already done)
-- ============================================
-- Already moved in previous attempt

-- ============================================
-- Part 3: Add RLS Policy for portal.knowledge_articles
-- ============================================

-- Note: tenant_id is VARCHAR, not UUID
DROP POLICY IF EXISTS "knowledge_articles_select" ON portal.knowledge_articles;
CREATE POLICY "knowledge_articles_select" ON portal.knowledge_articles
    FOR SELECT
    USING (
        tenant_id::uuid IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
        OR published = true -- Allow viewing published articles
    );

DROP POLICY IF EXISTS "knowledge_articles_manage" ON portal.knowledge_articles;
CREATE POLICY "knowledge_articles_manage" ON portal.knowledge_articles
    FOR ALL
    USING (
        tenant_id::uuid IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
            AND role IN ('owner', 'admin')
        )
    );

-- ============================================
-- Part 4: Remove Duplicate Indexes
-- ============================================

-- Drop the parent idx_metrics_organization which depends on the others
DROP INDEX IF EXISTS intelligence.idx_metrics_organization CASCADE;

-- ============================================
-- Summary
-- ============================================

-- Migration complete: Fixed critical Supabase linter issues
-- - Function search paths for 2 functions
-- - RLS policies for portal.knowledge_articles
-- - Duplicate indexes removed
