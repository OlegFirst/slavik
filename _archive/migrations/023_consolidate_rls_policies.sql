-- Migration to consolidate multiple permissive RLS policies
-- Generated automatically to fix performance warnings
-- This consolidates policies with OR conditions for better performance

BEGIN;


-- ============================================
-- Table: bcm.documents
-- ============================================

-- Consolidating 2 policies for authenticated/UPDATE:
--   - documents_update
--   - Documents editable by owner
DROP POLICY IF EXISTS "documents_update" ON "bcm"."documents";
DROP POLICY IF EXISTS "Documents editable by owner" ON "bcm"."documents";
CREATE POLICY "documents_update_consolidated_authenticated"
    ON "bcm"."documents"
    AS PERMISSIVE
    FOR UPDATE
    TO authenticated
    USING ((is_org_member(organization_id) AND ((auth.uid() = owner_id) OR is_org_admin(organization_id))) OR (owner_id = ( SELECT auth.uid() AS uid)))
    WITH CHECK ((is_org_member(organization_id)) OR (owner_id = ( SELECT auth.uid() AS uid)));


-- ============================================
-- Table: compliance.improvement_initiatives
-- ============================================

-- Consolidating 3 policies for public/ALL:
--   - improvement_initiatives_tenant_isolation
--   - improvement_initiatives_platform_admin
--   - improvement_initiatives_org_access
DROP POLICY IF EXISTS "improvement_initiatives_tenant_isolation" ON "compliance"."improvement_initiatives";
DROP POLICY IF EXISTS "improvement_initiatives_platform_admin" ON "compliance"."improvement_initiatives";
DROP POLICY IF EXISTS "improvement_initiatives_org_access" ON "compliance"."improvement_initiatives";
CREATE POLICY "improvement_initiatives_all_consolidated_public"
    ON "compliance"."improvement_initiatives"
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (((tenant_id)::text = current_setting('app.current_tenant_id'::text, true)) OR ((current_setting('app.is_platform_admin'::text, true))::boolean = true) OR (organization_id IN ( SELECT organizations.id
   FROM organizations
  WHERE ((organizations.tenant_id)::text = current_setting('app.current_tenant_id'::text, true)))));


-- ============================================
-- Table: governance.context_analysis
-- ============================================

-- Consolidating 3 policies for public/ALL:
--   - context_analysis_platform_admin
--   - context_analysis_org_access
--   - context_analysis_tenant_isolation
DROP POLICY IF EXISTS "context_analysis_platform_admin" ON "governance"."context_analysis";
DROP POLICY IF EXISTS "context_analysis_org_access" ON "governance"."context_analysis";
DROP POLICY IF EXISTS "context_analysis_tenant_isolation" ON "governance"."context_analysis";
CREATE POLICY "context_analysis_all_consolidated_public"
    ON "governance"."context_analysis"
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (((current_setting('app.is_platform_admin'::text, true))::boolean = true) OR (organization_id IN ( SELECT organizations.id
   FROM organizations
  WHERE ((organizations.tenant_id)::text = current_setting('app.current_tenant_id'::text, true)))) OR ((tenant_id)::text = current_setting('app.current_tenant_id'::text, true)));


-- ============================================
-- Table: governance.policies
-- ============================================

-- Consolidating 2 policies for authenticated/UPDATE:
--   - policies_update
--   - Policies editable by owner
DROP POLICY IF EXISTS "policies_update" ON "governance"."policies";
DROP POLICY IF EXISTS "Policies editable by owner" ON "governance"."policies";
CREATE POLICY "policies_update_consolidated_authenticated"
    ON "governance"."policies"
    AS PERMISSIVE
    FOR UPDATE
    TO authenticated
    USING ((is_org_member(organization_id) AND ((auth.uid() = policy_owner_id) OR is_org_admin(organization_id))) OR (policy_owner_id = ( SELECT auth.uid() AS uid)))
    WITH CHECK ((is_org_member(organization_id)) OR (policy_owner_id = ( SELECT auth.uid() AS uid)));


-- ============================================
-- Table: governance.stakeholders
-- ============================================

-- Consolidating 3 policies for public/ALL:
--   - stakeholders_platform_admin
--   - stakeholders_org_access
--   - stakeholders_tenant_isolation
DROP POLICY IF EXISTS "stakeholders_platform_admin" ON "governance"."stakeholders";
DROP POLICY IF EXISTS "stakeholders_org_access" ON "governance"."stakeholders";
DROP POLICY IF EXISTS "stakeholders_tenant_isolation" ON "governance"."stakeholders";
CREATE POLICY "stakeholders_all_consolidated_public"
    ON "governance"."stakeholders"
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (((current_setting('app.is_platform_admin'::text, true))::boolean = true) OR (organization_id IN ( SELECT organizations.id
   FROM organizations
  WHERE ((organizations.tenant_id)::text = current_setting('app.current_tenant_id'::text, true)))) OR ((tenant_id)::text = current_setting('app.current_tenant_id'::text, true)));


-- ============================================
-- Table: learning.competency_assessments
-- ============================================

-- Consolidating 2 policies for public/SELECT:
--   - Users see their own competency assessments
--   - Competency assessments visible to org admins
DROP POLICY IF EXISTS "Users see their own competency assessments" ON "learning"."competency_assessments";
DROP POLICY IF EXISTS "Competency assessments visible to org admins" ON "learning"."competency_assessments";
CREATE POLICY "competency_assessments_select_consolidated_public"
    ON "learning"."competency_assessments"
    AS PERMISSIVE
    FOR SELECT
    TO public
    USING ((user_id = auth.uid()) OR (is_org_admin(organization_id)));


-- ============================================
-- Table: learning.enrollments
-- ============================================

-- Consolidating 2 policies for public/SELECT:
--   - Enrollments visible to org members
--   - Users see their own enrollments
DROP POLICY IF EXISTS "Enrollments visible to org members" ON "learning"."enrollments";
DROP POLICY IF EXISTS "Users see their own enrollments" ON "learning"."enrollments";
CREATE POLICY "enrollments_select_consolidated_public"
    ON "learning"."enrollments"
    AS PERMISSIVE
    FOR SELECT
    TO public
    USING ((is_org_member(organization_id)) OR (user_id = auth.uid()));


-- ============================================
-- Table: learning.user_achievements
-- ============================================

-- Consolidating 2 policies for public/SELECT:
--   - Users see their own achievements
--   - Achievements visible to org members
DROP POLICY IF EXISTS "Users see their own achievements" ON "learning"."user_achievements";
DROP POLICY IF EXISTS "Achievements visible to org members" ON "learning"."user_achievements";
CREATE POLICY "user_achievements_select_consolidated_public"
    ON "learning"."user_achievements"
    AS PERMISSIVE
    FOR SELECT
    TO public
    USING ((user_id = auth.uid()) OR (is_org_member(organization_id)));


-- ============================================
-- Table: response.notifications
-- ============================================

-- Consolidating 2 policies for public/SELECT:
--   - Users see their own notifications
--   - Notifications visible to org members
DROP POLICY IF EXISTS "Users see their own notifications" ON "response"."notifications";
DROP POLICY IF EXISTS "Notifications visible to org members" ON "response"."notifications";
CREATE POLICY "notifications_select_consolidated_public"
    ON "response"."notifications"
    AS PERMISSIVE
    FOR SELECT
    TO public
    USING ((user_id = auth.uid()) OR (is_org_member(organization_id)));


-- ============================================
-- Table: response.timeline_events
-- ============================================

-- Consolidating 2 policies for public/SELECT:
--   - Timeline events visible to org members
--   - Public timeline events visible to all
DROP POLICY IF EXISTS "Timeline events visible to org members" ON "response"."timeline_events";
DROP POLICY IF EXISTS "Public timeline events visible to all" ON "response"."timeline_events";
CREATE POLICY "timeline_events_select_consolidated_public"
    ON "response"."timeline_events"
    AS PERMISSIVE
    FOR SELECT
    TO public
    USING ((is_org_member(organization_id)) OR (is_public = true));


-- ============================================
-- Table: validation.kpi_alerts
-- ============================================

-- Consolidating 3 policies for public/ALL:
--   - kpi_alerts_platform_admin
--   - kpi_alerts_org_access
--   - kpi_alerts_tenant_isolation
DROP POLICY IF EXISTS "kpi_alerts_platform_admin" ON "validation"."kpi_alerts";
DROP POLICY IF EXISTS "kpi_alerts_org_access" ON "validation"."kpi_alerts";
DROP POLICY IF EXISTS "kpi_alerts_tenant_isolation" ON "validation"."kpi_alerts";
CREATE POLICY "kpi_alerts_all_consolidated_public"
    ON "validation"."kpi_alerts"
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (((current_setting('app.is_platform_admin'::text, true))::boolean = true) OR (organization_id IN ( SELECT organizations.id
   FROM organizations
  WHERE ((organizations.tenant_id)::text = current_setting('app.current_tenant_id'::text, true)))) OR ((tenant_id)::text = current_setting('app.current_tenant_id'::text, true)));


COMMIT;

-- Summary:
-- Tables affected: 11
-- Total consolidations: 11
-- Policies before: 26
-- Policies after: 11
-- Policies removed: 15