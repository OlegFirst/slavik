-- ============================================
-- BCM Platform - Unified Database
-- Migration 035: Final Lint Fixes
-- ============================================
-- Fixes remaining critical issues:
-- 1. Security definer view
-- 2. RLS policies for workflow_intelligence
-- 3. Multiple permissive policies consolidation
-- ============================================

-- ============================================
-- Part 1: Fix Security Definer View
-- ============================================

-- Recreate view with explicit security_invoker
DROP VIEW IF EXISTS public.v_mutual_relationships CASCADE;

CREATE VIEW public.v_mutual_relationships
WITH (security_invoker = true)
AS
SELECT
    LEAST(r1.user_id, r1.related_user_id) AS user_a,
    GREATEST(r1.user_id, r1.related_user_id) AS user_b,
    'friend'::text AS relationship_type,
    'accepted'::text AS status,
    GREATEST(r1.updated_at, r2.updated_at) AS last_updated_at
FROM user_relationships r1
JOIN user_relationships r2 ON (
    r2.user_id = r1.related_user_id
    AND r2.related_user_id = r1.user_id
)
WHERE
    r1.relationship_type::text = 'friend'::text
    AND r2.relationship_type::text = 'friend'::text
    AND r1.status::text = 'accepted'::text
    AND r2.status::text = 'accepted'::text
GROUP BY
    LEAST(r1.user_id, r1.related_user_id),
    GREATEST(r1.user_id, r1.related_user_id),
    GREATEST(r1.updated_at, r2.updated_at);

COMMENT ON VIEW public.v_mutual_relationships
    IS 'Shows mutual friend relationships (uses SECURITY INVOKER for proper RLS)';

-- ============================================
-- Part 2: Add RLS Policies for workflow_intelligence
-- ============================================

-- Check if tables exist first, then add policies
DO $$
BEGIN
    -- workflow_intelligence.workflow_contexts
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'workflow_intelligence'
        AND table_name = 'workflow_contexts'
    ) THEN
        EXECUTE 'DROP POLICY IF EXISTS "workflow_contexts_tenant" ON workflow_intelligence.workflow_contexts';
        EXECUTE 'CREATE POLICY "workflow_contexts_tenant" ON workflow_intelligence.workflow_contexts
            FOR ALL
            USING (
                tenant_id IN (
                    SELECT id::text
                    FROM public.organizations
                    WHERE id IN (
                        SELECT organization_id
                        FROM public.organization_users
                        WHERE user_id = auth.uid()
                    )
                )
            )';
    END IF;

    -- workflow_intelligence.workflow_cases
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'workflow_intelligence'
        AND table_name = 'workflow_cases'
    ) THEN
        EXECUTE 'DROP POLICY IF EXISTS "workflow_cases_tenant" ON workflow_intelligence.workflow_cases';
        EXECUTE 'CREATE POLICY "workflow_cases_tenant" ON workflow_intelligence.workflow_cases
            FOR ALL
            USING (
                tenant_id IN (
                    SELECT id::text
                    FROM public.organizations
                    WHERE id IN (
                        SELECT organization_id
                        FROM public.organization_users
                        WHERE user_id = auth.uid()
                    )
                )
            )';
    END IF;

    -- workflow_intelligence.ml_predictions
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'workflow_intelligence'
        AND table_name = 'ml_predictions'
    ) THEN
        EXECUTE 'DROP POLICY IF EXISTS "ml_predictions_tenant" ON workflow_intelligence.ml_predictions';
        EXECUTE 'CREATE POLICY "ml_predictions_tenant" ON workflow_intelligence.ml_predictions
            FOR ALL
            USING (
                tenant_id IN (
                    SELECT id::text
                    FROM public.organizations
                    WHERE id IN (
                        SELECT organization_id
                        FROM public.organization_users
                        WHERE user_id = auth.uid()
                    )
                )
            )';
    END IF;
END $$;

-- ============================================
-- Part 3: Consolidate Multiple Permissive Policies
-- ============================================

-- portal.knowledge_articles - consolidate manage and select
DROP POLICY IF EXISTS "knowledge_articles_manage" ON portal.knowledge_articles;
DROP POLICY IF EXISTS "knowledge_articles_select" ON portal.knowledge_articles;
CREATE POLICY "knowledge_articles_all" ON portal.knowledge_articles
    FOR ALL
    USING (
        published = true  -- Anyone can view published
        OR tenant_id::uuid IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    )
    WITH CHECK (
        tenant_id::uuid IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
            AND role IN ('owner', 'admin')
        )
    );

-- public.teams - consolidate all policies
DROP POLICY IF EXISTS "teams_select" ON public.teams;
DROP POLICY IF EXISTS "teams_manage" ON public.teams;
DROP POLICY IF EXISTS "Teams manageable by org admins" ON public.teams;
DROP POLICY IF EXISTS "Teams insertable by org admins" ON public.teams;
CREATE POLICY "teams_all" ON public.teams
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
        OR EXISTS (
            SELECT 1 FROM public.platform_administrators
            WHERE user_id = (SELECT auth.uid())
            AND is_active = true
            AND can_access_all_tenants = true
        )
    )
    WITH CHECK (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
            AND role IN ('owner', 'admin')
        )
    );

-- public.user_profiles - consolidate
DROP POLICY IF EXISTS "user_profiles_self" ON public.user_profiles;
DROP POLICY IF EXISTS "user_profiles_admin_view" ON public.user_profiles;
DROP POLICY IF EXISTS "User profiles publicly readable" ON public.user_profiles;
CREATE POLICY "user_profiles_all" ON public.user_profiles
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR is_public = true
        OR EXISTS (
            SELECT 1 FROM public.platform_administrators
            WHERE user_id = (SELECT auth.uid())
            AND is_active = true
        )
    )
    WITH CHECK (user_id = (SELECT auth.uid()));

-- public.user_relationships - consolidate
DROP POLICY IF EXISTS "user_relationships_view" ON public.user_relationships;
DROP POLICY IF EXISTS "user_relationships_update" ON public.user_relationships;
DROP POLICY IF EXISTS "user_relationships_insert" ON public.user_relationships;
DROP POLICY IF EXISTS "user_relationships_delete" ON public.user_relationships;
DROP POLICY IF EXISTS "Users can delete own relationships" ON public.user_relationships;
DROP POLICY IF EXISTS "Users can create relationships" ON public.user_relationships;

CREATE POLICY "user_relationships_own" ON public.user_relationships
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR related_user_id = (SELECT auth.uid())
    )
    WITH CHECK (user_id = (SELECT auth.uid()));

-- risk schema - consolidate policies
-- risk.assessments
DROP POLICY IF EXISTS "Risk assessments manageable by org admins" ON risk.assessments;
DROP POLICY IF EXISTS "Risk assessments visible to org members" ON risk.assessments;
CREATE POLICY "risk_assessments_all" ON risk.assessments
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- risk.controls
DROP POLICY IF EXISTS "Controls manageable by org admins" ON risk.controls;
DROP POLICY IF EXISTS "Controls visible to org members" ON risk.controls;
CREATE POLICY "risk_controls_all" ON risk.controls
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- risk.risks
DROP POLICY IF EXISTS "Risks manageable by org admins" ON risk.risks;
DROP POLICY IF EXISTS "Risks visible to org members" ON risk.risks;
DROP POLICY IF EXISTS "risks_update" ON risk.risks;
CREATE POLICY "risks_all" ON risk.risks
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- risk.templates
DROP POLICY IF EXISTS "Risk templates manageable by org admins" ON risk.templates;
DROP POLICY IF EXISTS "Risk templates visible to org members" ON risk.templates;
CREATE POLICY "risk_templates_all" ON risk.templates
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- risk.treatments
DROP POLICY IF EXISTS "Risk treatments manageable by org admins" ON risk.treatments;
DROP POLICY IF EXISTS "Risk treatments visible to org members" ON risk.treatments;
CREATE POLICY "risk_treatments_all" ON risk.treatments
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- validation schema - consolidate policies
-- validation.audit_findings
DROP POLICY IF EXISTS "Audit findings manageable by org admins" ON validation.audit_findings;
DROP POLICY IF EXISTS "Audit findings visible to org members" ON validation.audit_findings;
CREATE POLICY "audit_findings_all" ON validation.audit_findings
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- validation.audit_plans
DROP POLICY IF EXISTS "Audit plans manageable by org admins" ON validation.audit_plans;
DROP POLICY IF EXISTS "Audit plans visible to org members" ON validation.audit_plans;
CREATE POLICY "audit_plans_all" ON validation.audit_plans
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- ============================================
-- Summary
-- ============================================

-- Migration complete: Fixed final critical linter issues
-- - Security definer view fixed
-- - RLS policies added for workflow_intelligence
-- - Multiple permissive policies consolidated across all schemas
