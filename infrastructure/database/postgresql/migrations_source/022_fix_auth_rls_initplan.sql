-- =====================================================
-- Migration 022: Fix auth_rls_initplan Performance Issue
-- =====================================================
-- Purpose: Replace auth.uid() with (SELECT auth.uid()) in RLS policies
-- Issue: auth.uid() is re-evaluated for each row (slow!)
-- Fix: Wrap in SELECT to evaluate once per query
-- Based on: Supabase Performance Lints (auth_rls_initplan - 42 WARN)
-- Date: 2025-10-02
-- =====================================================

-- Strategy: Drop and recreate policies with optimized auth.uid() calls

-- =====================================================
-- public.team_members
-- =====================================================

DROP POLICY IF EXISTS team_members_insert ON public.team_members;
DROP POLICY IF EXISTS team_members_update ON public.team_members;
DROP POLICY IF EXISTS team_members_delete ON public.team_members;

CREATE POLICY team_members_insert ON public.team_members
FOR INSERT TO authenticated
WITH CHECK (
    team_id IN (
        SELECT t.id FROM public.teams t
        WHERE is_org_admin(t.organization_id)
        OR (SELECT auth.uid()) = t.created_by_user_id
    )
);

CREATE POLICY team_members_update ON public.team_members
FOR UPDATE TO authenticated
USING (
    team_id IN (
        SELECT t.id FROM public.teams t
        WHERE is_org_admin(t.organization_id)
        OR (SELECT auth.uid()) = t.created_by_user_id
    )
);

CREATE POLICY team_members_delete ON public.team_members
FOR DELETE TO authenticated
USING (
    team_id IN (
        SELECT t.id FROM public.teams t
        WHERE is_org_admin(t.organization_id)
        OR (SELECT auth.uid()) = t.created_by_user_id
    )
);

-- =====================================================
-- bcm.competence_records
-- =====================================================

DROP POLICY IF EXISTS "Users see their own competence records" ON bcm.competence_records;

CREATE POLICY "Users see their own competence records" ON bcm.competence_records
FOR SELECT TO authenticated
USING (user_id = (SELECT auth.uid()));

-- =====================================================
-- bcm.documents
-- =====================================================

DROP POLICY IF EXISTS "Documents editable by owner" ON bcm.documents;

CREATE POLICY "Documents editable by owner" ON bcm.documents
FOR UPDATE TO authenticated
USING (owner_id = (SELECT auth.uid()))
WITH CHECK (owner_id = (SELECT auth.uid()));

-- =====================================================
-- governance.policies
-- =====================================================

DROP POLICY IF EXISTS "Policies editable by owner" ON governance.policies;

CREATE POLICY "Policies editable by owner" ON governance.policies
FOR UPDATE TO authenticated
USING (policy_owner_id = (SELECT auth.uid()))
WITH CHECK (policy_owner_id = (SELECT auth.uid()));

-- =====================================================
-- learning.user_achievements
-- =====================================================

DROP POLICY IF EXISTS "User achievements visible to user" ON learning.user_achievements;

CREATE POLICY "User achievements visible to user" ON learning.user_achievements
FOR SELECT TO authenticated
USING (user_id = (SELECT auth.uid()));

-- =====================================================
-- learning.enrollments
-- =====================================================

DROP POLICY IF EXISTS "Enrollments visible to enrolled user" ON learning.enrollments;

CREATE POLICY "Enrollments visible to enrolled user" ON learning.enrollments
FOR SELECT TO authenticated
USING (user_id = (SELECT auth.uid()));

-- =====================================================
-- learning.competency_assessments
-- =====================================================

DROP POLICY IF EXISTS "Competency assessments visible to user" ON learning.competency_assessments;

CREATE POLICY "Competency assessments visible to user" ON learning.competency_assessments
FOR SELECT TO authenticated
USING (user_id = (SELECT auth.uid()));

-- =====================================================
-- community.specialists (Migration 020)
-- =====================================================

DROP POLICY IF EXISTS specialists_owner_update ON community.specialists;

CREATE POLICY specialists_owner_update ON community.specialists
FOR UPDATE TO authenticated
USING ((SELECT auth.uid()) = user_id)
WITH CHECK ((SELECT auth.uid()) = user_id);

-- =====================================================
-- community.specialist_certifications
-- =====================================================

DROP POLICY IF EXISTS certifications_owner_write ON community.specialist_certifications;

CREATE POLICY certifications_owner_write ON community.specialist_certifications
FOR ALL TO authenticated
USING (
    specialist_id IN (
        SELECT id FROM community.specialists WHERE user_id = (SELECT auth.uid())
    )
);

-- =====================================================
-- community.specialist_portfolio
-- =====================================================

DROP POLICY IF EXISTS portfolio_owner_write ON community.specialist_portfolio;

CREATE POLICY portfolio_owner_write ON community.specialist_portfolio
FOR ALL TO authenticated
USING (
    specialist_id IN (
        SELECT id FROM community.specialists WHERE user_id = (SELECT auth.uid())
    )
);

-- =====================================================
-- community.specialist_services
-- =====================================================

DROP POLICY IF EXISTS services_owner_write ON community.specialist_services;

CREATE POLICY services_owner_write ON community.specialist_services
FOR ALL TO authenticated
USING (
    specialist_id IN (
        SELECT id FROM community.specialists WHERE user_id = (SELECT auth.uid())
    )
);

-- =====================================================
-- community.specialist_reviews
-- =====================================================

DROP POLICY IF EXISTS reviews_reviewer_write ON community.specialist_reviews;
DROP POLICY IF EXISTS reviews_specialist_response ON community.specialist_reviews;

CREATE POLICY reviews_reviewer_write ON community.specialist_reviews
FOR INSERT TO authenticated
WITH CHECK ((SELECT auth.uid()) = reviewer_id);

CREATE POLICY reviews_specialist_response ON community.specialist_reviews
FOR UPDATE TO authenticated
USING (
    specialist_id IN (
        SELECT id FROM community.specialists WHERE user_id = (SELECT auth.uid())
    )
    AND response IS NULL
)
WITH CHECK (response IS NOT NULL);

-- =====================================================
-- community.specialist_engagements
-- =====================================================

DROP POLICY IF EXISTS engagements_parties_access ON community.specialist_engagements;

CREATE POLICY engagements_parties_access ON community.specialist_engagements
FOR ALL TO authenticated
USING (
    specialist_id IN (
        SELECT id FROM community.specialists WHERE user_id = (SELECT auth.uid())
    )
    OR public.is_org_member(organization_id)
);

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 022: Auth RLS Initplan - COMPLETE';
    RAISE NOTICE 'Optimized: ~20 RLS policies';
    RAISE NOTICE 'Change: auth.uid() → (SELECT auth.uid())';
    RAISE NOTICE 'Impact: Policies now evaluate auth once per query, not per row';
END $$;
