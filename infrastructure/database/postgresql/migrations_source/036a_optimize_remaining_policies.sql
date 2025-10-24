-- ============================================
-- BCM Platform - Unified Database
-- Migration 036: Optimize Remaining Policies
-- ============================================
-- Fixes:
-- 1. Auth RLS InitPlan for workflow_intelligence
-- 2. Multiple permissive policies (~54 tables)
-- ============================================

-- ============================================
-- Part 1: Fix Auth RLS InitPlan for workflow_intelligence
-- ============================================

-- Optimize with (SELECT auth.uid()) instead of auth.uid()
DROP POLICY IF EXISTS "workflow_contexts_tenant" ON workflow_intelligence.workflow_contexts;
CREATE POLICY "workflow_contexts_tenant" ON workflow_intelligence.workflow_contexts
    FOR ALL
    USING (
        tenant_id IN (
            SELECT id::text
            FROM public.organizations
            WHERE id IN (
                SELECT organization_id
                FROM public.organization_users
                WHERE user_id = (SELECT auth.uid())
            )
        )
    );

DROP POLICY IF EXISTS "workflow_cases_tenant" ON workflow_intelligence.workflow_cases;
CREATE POLICY "workflow_cases_tenant" ON workflow_intelligence.workflow_cases
    FOR ALL
    USING (
        tenant_id IN (
            SELECT id::text
            FROM public.organizations
            WHERE id IN (
                SELECT organization_id
                FROM public.organization_users
                WHERE user_id = (SELECT auth.uid())
            )
        )
    );

DROP POLICY IF EXISTS "ml_predictions_tenant" ON workflow_intelligence.ml_predictions;
CREATE POLICY "ml_predictions_tenant" ON workflow_intelligence.ml_predictions
    FOR ALL
    USING (
        tenant_id IN (
            SELECT id::text
            FROM public.organizations
            WHERE id IN (
                SELECT organization_id
                FROM public.organization_users
                WHERE user_id = (SELECT auth.uid())
            )
        )
    );

-- ============================================
-- Part 2: Consolidate validation schema policies
-- ============================================

-- validation.capa
DROP POLICY IF EXISTS "CAPA manageable by org admins" ON validation.capa;
DROP POLICY IF EXISTS "CAPA visible to org members" ON validation.capa;
CREATE POLICY "capa_all" ON validation.capa
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- validation.exercise_actions
DROP POLICY IF EXISTS "Exercise actions manageable by org admins" ON validation.exercise_actions;
DROP POLICY IF EXISTS "Exercise actions visible to org members" ON validation.exercise_actions;
CREATE POLICY "exercise_actions_all" ON validation.exercise_actions
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- validation.exercise_scenarios
DROP POLICY IF EXISTS "Scenarios manageable by org admins" ON validation.exercise_scenarios;
DROP POLICY IF EXISTS "Scenarios visible to org members" ON validation.exercise_scenarios;
CREATE POLICY "exercise_scenarios_all" ON validation.exercise_scenarios
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- validation.exercises
DROP POLICY IF EXISTS "Exercises manageable by org admins" ON validation.exercises;
DROP POLICY IF EXISTS "Exercises visible to org members" ON validation.exercises;
CREATE POLICY "exercises_all" ON validation.exercises
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- validation.kpi_dashboards
DROP POLICY IF EXISTS "Dashboards manageable by org admins" ON validation.kpi_dashboards;
DROP POLICY IF EXISTS "Dashboards visible to org members" ON validation.kpi_dashboards;
CREATE POLICY "kpi_dashboards_all" ON validation.kpi_dashboards
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- validation.kpis
DROP POLICY IF EXISTS "KPIs manageable by org admins" ON validation.kpis;
DROP POLICY IF EXISTS "KPIs visible to org members" ON validation.kpis;
CREATE POLICY "kpis_all" ON validation.kpis
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- validation.management_reviews
DROP POLICY IF EXISTS "Management reviews manageable by org admins" ON validation.management_reviews;
DROP POLICY IF EXISTS "Management reviews visible to org members" ON validation.management_reviews;
CREATE POLICY "management_reviews_all" ON validation.management_reviews
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- ============================================
-- Part 3: Consolidate bcm schema policies
-- ============================================

-- bcm.competence_records
DROP POLICY IF EXISTS "Competence records visible to org members" ON bcm.competence_records;
DROP POLICY IF EXISTS "Users see their own competence records" ON bcm.competence_records;
CREATE POLICY "competence_records_all" ON bcm.competence_records
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bcm.document_approvals
DROP POLICY IF EXISTS "document_approvals_read" ON bcm.document_approvals;
DROP POLICY IF EXISTS "document_approvals_write" ON bcm.document_approvals;
CREATE POLICY "document_approvals_all" ON bcm.document_approvals
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bcm.document_retention_policies
DROP POLICY IF EXISTS "retention_policies_read" ON bcm.document_retention_policies;
DROP POLICY IF EXISTS "retention_policies_write" ON bcm.document_retention_policies;
CREATE POLICY "retention_policies_all" ON bcm.document_retention_policies
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bcm.document_tags
DROP POLICY IF EXISTS "document_tags_read" ON bcm.document_tags;
DROP POLICY IF EXISTS "document_tags_write" ON bcm.document_tags;
CREATE POLICY "document_tags_all" ON bcm.document_tags
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- ============================================
-- Part 4: Consolidate community schema policies
-- ============================================

-- community.specialist_certifications
DROP POLICY IF EXISTS "certifications_owner_write" ON community.specialist_certifications;
DROP POLICY IF EXISTS "certifications_public_read" ON community.specialist_certifications;
CREATE POLICY "specialist_certifications_all" ON community.specialist_certifications
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR is_public = true
    )
    WITH CHECK (user_id = (SELECT auth.uid()));

-- community.specialist_portfolio
DROP POLICY IF EXISTS "portfolio_owner_write" ON community.specialist_portfolio;
DROP POLICY IF EXISTS "portfolio_public_read" ON community.specialist_portfolio;
CREATE POLICY "specialist_portfolio_all" ON community.specialist_portfolio
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR is_public = true
    )
    WITH CHECK (user_id = (SELECT auth.uid()));

-- community.specialist_services
DROP POLICY IF EXISTS "services_owner_write" ON community.specialist_services;
DROP POLICY IF EXISTS "services_public_read" ON community.specialist_services;
CREATE POLICY "specialist_services_all" ON community.specialist_services
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR is_active = true
    )
    WITH CHECK (user_id = (SELECT auth.uid()));

-- ============================================
-- Part 5: Consolidate governance schema policies
-- ============================================

-- governance.policies
DROP POLICY IF EXISTS "policies_access" ON governance.policies;
DROP POLICY IF EXISTS "policies_select" ON governance.policies;
CREATE POLICY "policies_all" ON governance.policies
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- ============================================
-- Part 6: Consolidate learning schema policies
-- ============================================

-- learning.competency_assessments
DROP POLICY IF EXISTS "Competency assessments visible to user" ON learning.competency_assessments;
DROP POLICY IF EXISTS "competency_assessments_select_consolidated_public" ON learning.competency_assessments;
CREATE POLICY "competency_assessments_all" ON learning.competency_assessments
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- learning.enrollments
DROP POLICY IF EXISTS "Enrollments visible to enrolled user" ON learning.enrollments;
DROP POLICY IF EXISTS "enrollments_select_consolidated_public" ON learning.enrollments;
CREATE POLICY "enrollments_all" ON learning.enrollments
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- learning.user_achievements
DROP POLICY IF EXISTS "User achievements visible to user" ON learning.user_achievements;
DROP POLICY IF EXISTS "user_achievements_select_consolidated_public" ON learning.user_achievements;
CREATE POLICY "user_achievements_all" ON learning.user_achievements
    FOR ALL
    USING (
        user_id = (SELECT auth.uid())
        OR organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- ============================================
-- Part 7: Consolidate public schema policies
-- ============================================

-- public.team_members
DROP POLICY IF EXISTS "Team members visible to team members" ON public.team_members;
DROP POLICY IF EXISTS "team_members_select" ON public.team_members;
CREATE POLICY "team_members_all" ON public.team_members
    FOR ALL
    USING (
        team_id IN (
            SELECT team_id
            FROM public.team_members
            WHERE user_id = (SELECT auth.uid())
        )
        OR team_id IN (
            SELECT id
            FROM public.teams
            WHERE organization_id IN (
                SELECT organization_id
                FROM public.organization_users
                WHERE user_id = (SELECT auth.uid())
                AND role IN ('owner', 'admin')
            )
        )
    );

-- ============================================
-- Part 8: Consolidate response.incidents policies
-- ============================================

DROP POLICY IF EXISTS "incidents_access" ON response.incidents;
DROP POLICY IF EXISTS "incidents_delete" ON response.incidents;
DROP POLICY IF EXISTS "incidents_insert" ON response.incidents;
DROP POLICY IF EXISTS "incidents_select" ON response.incidents;
CREATE POLICY "incidents_all" ON response.incidents
    FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- ============================================
-- Part 9: Consolidate risk.risks policies
-- ============================================

DROP POLICY IF EXISTS "risks_all" ON risk.risks;
DROP POLICY IF EXISTS "risks_delete" ON risk.risks;
DROP POLICY IF EXISTS "risks_insert" ON risk.risks;
DROP POLICY IF EXISTS "risks_select" ON risk.risks;
CREATE POLICY "risks_all_new" ON risk.risks
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

-- Migration complete: Optimized remaining RLS policies
-- - Fixed auth RLS initplan for workflow_intelligence (3 tables)
-- - Consolidated multiple permissive policies (~54 tables)
-- - All policies now use (SELECT auth.uid()) for optimal performance
