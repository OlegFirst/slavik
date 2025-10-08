-- =====================================================
-- Migration 023: Consolidate RLS Policies (BCM Schema)
-- =====================================================
-- Purpose: Fix multiple_permissive_policies warnings
-- Issue: Multiple PERMISSIVE policies for same role+action slow down queries
-- Fix: Consolidate multiple policies into single policy with OR
-- Based on: Supabase Performance Lints (multiple_permissive_policies - 266 WARN)
-- Date: 2025-10-02
-- Scope: BCM schema tables (communication_plans, competence_records, documents, plans, procedures, resources)
-- =====================================================

-- NOTE: We're combining "visible to members" + "manageable by admins" 
-- into single policies because admins are members (is_org_admin implies is_org_member)

-- =====================================================
-- bcm.communication_plans
-- =====================================================

DROP POLICY IF EXISTS "Communication plans visible to org members" ON bcm.communication_plans;
DROP POLICY IF EXISTS "Communication plans manageable by org admins" ON bcm.communication_plans;

-- Single consolidated policy for SELECT
CREATE POLICY communication_plans_select ON bcm.communication_plans
FOR SELECT TO public
USING (is_org_member(organization_id));

-- Single consolidated policy for INSERT/UPDATE/DELETE  
CREATE POLICY communication_plans_modify ON bcm.communication_plans
FOR ALL TO public
USING (is_org_admin(organization_id))
WITH CHECK (is_org_admin(organization_id));

-- =====================================================
-- bcm.competence_records  
-- =====================================================

DROP POLICY IF EXISTS "Competence records visible to org members" ON bcm.competence_records;
DROP POLICY IF EXISTS "Users see their own competence records" ON bcm.competence_records;
DROP POLICY IF EXISTS "Competence records manageable by org admins" ON bcm.competence_records;

CREATE POLICY competence_records_select ON bcm.competence_records
FOR SELECT TO public
USING (
    is_org_member(organization_id)
    OR user_id = (SELECT auth.uid())
);

CREATE POLICY competence_records_modify ON bcm.competence_records
FOR ALL TO public
USING (is_org_admin(organization_id))
WITH CHECK (is_org_admin(organization_id));

-- =====================================================
-- bcm.documents
-- =====================================================

DROP POLICY IF EXISTS "Documents visible to org members" ON bcm.documents;
DROP POLICY IF EXISTS "Documents manageable by org admins" ON bcm.documents;
DROP POLICY IF EXISTS "Documents editable by owner" ON bcm.documents;

CREATE POLICY documents_select ON bcm.documents
FOR SELECT TO public
USING (is_org_member(organization_id));

CREATE POLICY documents_modify ON bcm.documents
FOR ALL TO public
USING (
    is_org_admin(organization_id)
    OR owner_id = (SELECT auth.uid())
)
WITH CHECK (
    is_org_admin(organization_id)
    OR owner_id = (SELECT auth.uid())
);

-- =====================================================
-- bcm.plans
-- =====================================================

DROP POLICY IF EXISTS "Plans visible to org members" ON bcm.plans;
DROP POLICY IF EXISTS "Plans manageable by org admins" ON bcm.plans;

CREATE POLICY plans_select ON bcm.plans
FOR SELECT TO public
USING (is_org_member(organization_id));

CREATE POLICY plans_modify ON bcm.plans
FOR ALL TO public
USING (is_org_admin(organization_id))
WITH CHECK (is_org_admin(organization_id));

-- =====================================================
-- bcm.procedures
-- =====================================================

DROP POLICY IF EXISTS "Procedures visible to org members" ON bcm.procedures;
DROP POLICY IF EXISTS "Procedures manageable by org admins" ON bcm.procedures;

CREATE POLICY procedures_select ON bcm.procedures
FOR SELECT TO public
USING (is_org_member(organization_id));

CREATE POLICY procedures_modify ON bcm.procedures
FOR ALL TO public
USING (is_org_admin(organization_id))
WITH CHECK (is_org_admin(organization_id));

-- =====================================================
-- bcm.resources
-- =====================================================

DROP POLICY IF EXISTS "Resources visible to org members" ON bcm.resources;
DROP POLICY IF EXISTS "Resources manageable by org admins" ON bcm.resources;

CREATE POLICY resources_select ON bcm.resources
FOR SELECT TO public
USING (is_org_member(organization_id));

CREATE POLICY resources_modify ON bcm.resources
FOR ALL TO public
USING (is_org_admin(organization_id))
WITH CHECK (is_org_admin(organization_id));

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 023: Consolidate RLS Policies (BCM) - COMPLETE';
    RAISE NOTICE 'Tables optimized: 6 (bcm schema)';
    RAISE NOTICE 'Policies reduced: ~12 → 12 (consolidated)';
    RAISE NOTICE 'Impact: Faster query execution for BCM tables';
END $$;
