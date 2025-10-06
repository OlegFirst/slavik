-- Migration: Fix Auth RLS InitPlan Performance Issues
-- Description: Wrap auth.uid() in SELECT to prevent re-evaluation per row
-- Lint: auth_rls_initplan (WARN - PERFORMANCE)

-- Fix public.organizations policies
DROP POLICY IF EXISTS "Organizations insertable by authenticated" ON public.organizations;
CREATE POLICY "Organizations insertable by authenticated" ON public.organizations
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Fix public.user_profiles policies
DROP POLICY IF EXISTS "User profiles updatable by owner" ON public.user_profiles;
CREATE POLICY "User profiles updatable by owner" ON public.user_profiles
    FOR UPDATE
    TO authenticated
    USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "User profiles insertable on registration" ON public.user_profiles;
CREATE POLICY "User profiles insertable on registration" ON public.user_profiles
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = (SELECT auth.uid()));

-- Fix public.organization_users policies
DROP POLICY IF EXISTS "Org users visible to org members" ON public.organization_users;
CREATE POLICY "Org users visible to org members" ON public.organization_users
    FOR SELECT
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix public.teams policies
DROP POLICY IF EXISTS "Teams visible to org members" ON public.teams;
CREATE POLICY "Teams visible to org members" ON public.teams
    FOR SELECT
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

DROP POLICY IF EXISTS "teams_update" ON public.teams;
CREATE POLICY "teams_update" ON public.teams
    FOR UPDATE
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
            AND role IN ('owner', 'admin')
        )
    );

-- Fix public.team_members policies
DROP POLICY IF EXISTS "Team members visible to team members" ON public.team_members;
CREATE POLICY "Team members visible to team members" ON public.team_members
    FOR SELECT
    TO authenticated
    USING (
        team_id IN (
            SELECT team_id
            FROM public.team_members
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix compliance schema
DROP POLICY IF EXISTS "improvement_initiatives_all_consolidated_public" ON compliance.improvement_initiatives;
CREATE POLICY "improvement_initiatives_all_consolidated_public" ON compliance.improvement_initiatives
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix governance schema
DROP POLICY IF EXISTS "context_analysis_all_consolidated_public" ON governance.context_analysis;
CREATE POLICY "context_analysis_all_consolidated_public" ON governance.context_analysis
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

DROP POLICY IF EXISTS "stakeholders_all_consolidated_public" ON governance.stakeholders;
CREATE POLICY "stakeholders_all_consolidated_public" ON governance.stakeholders
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix learning schema
DROP POLICY IF EXISTS "competency_assessments_select_consolidated_public" ON learning.competency_assessments;
CREATE POLICY "competency_assessments_select_consolidated_public" ON learning.competency_assessments
    FOR SELECT
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
        OR user_id = (SELECT auth.uid())
    );

DROP POLICY IF EXISTS "enrollments_select_consolidated_public" ON learning.enrollments;
CREATE POLICY "enrollments_select_consolidated_public" ON learning.enrollments
    FOR SELECT
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
        OR user_id = (SELECT auth.uid())
    );

DROP POLICY IF EXISTS "user_achievements_select_consolidated_public" ON learning.user_achievements;
CREATE POLICY "user_achievements_select_consolidated_public" ON learning.user_achievements
    FOR SELECT
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
        OR user_id = (SELECT auth.uid())
    );

-- Fix response schema
DROP POLICY IF EXISTS "notifications_select_consolidated_public" ON response.notifications;
CREATE POLICY "notifications_select_consolidated_public" ON response.notifications
    FOR SELECT
    TO authenticated
    USING (user_id = (SELECT auth.uid()));

-- Fix validation schema
DROP POLICY IF EXISTS "kpi_alerts_all_consolidated_public" ON validation.kpi_alerts;
CREATE POLICY "kpi_alerts_all_consolidated_public" ON validation.kpi_alerts
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix bia.suppliers
DROP POLICY IF EXISTS "suppliers_tenant_isolation" ON bia.suppliers;
DROP POLICY IF EXISTS "suppliers_org_access" ON bia.suppliers;
CREATE POLICY "suppliers_access" ON bia.suppliers
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix bia.supplier_disruptions
DROP POLICY IF EXISTS "supplier_disruptions_tenant_isolation" ON bia.supplier_disruptions;
DROP POLICY IF EXISTS "supplier_disruptions_org_access" ON bia.supplier_disruptions;
CREATE POLICY "supplier_disruptions_access" ON bia.supplier_disruptions
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix portal.knowledge_articles
DROP POLICY IF EXISTS "articles_tenant_isolation" ON portal.knowledge_articles;
DROP POLICY IF EXISTS "articles_tenant_write" ON portal.knowledge_articles;
CREATE POLICY "articles_access" ON portal.knowledge_articles
    FOR ALL
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix core_auth.user_accounts
DROP POLICY IF EXISTS "ua_select_self_tenant" ON core_auth.user_accounts;
DROP POLICY IF EXISTS "ua_update_self_tenant" ON core_auth.user_accounts;
DROP POLICY IF EXISTS "ua_insert_self_tenant" ON core_auth.user_accounts;

CREATE POLICY "ua_self_access" ON core_auth.user_accounts
    FOR ALL
    TO authenticated
    USING (auth_user_id = (SELECT auth.uid()))
    WITH CHECK (auth_user_id = (SELECT auth.uid()));

-- Fix response.incidents
DROP POLICY IF EXISTS "incidents_update" ON response.incidents;
CREATE POLICY "incidents_update" ON response.incidents
    FOR UPDATE
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix risk.risks
DROP POLICY IF EXISTS "risks_update" ON risk.risks;
CREATE POLICY "risks_update" ON risk.risks
    FOR UPDATE
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- Fix bcm.documents
DROP POLICY IF EXISTS "documents_update_consolidated_authenticated" ON bcm.documents;
CREATE POLICY "documents_update" ON bcm.documents
    FOR UPDATE
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

COMMENT ON MIGRATION IS 'Fixed Auth RLS InitPlan performance issues by wrapping auth.uid() in SELECT';
