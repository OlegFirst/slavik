-- =====================================================
-- Migration 019: RLS Security Hardening & Additional Helper Functions
-- =====================================================
-- Purpose: Implement comprehensive RLS policies and missing helper functions
-- Based on: Security recommendations from local agent
-- Date: 2025-10-02
-- =====================================================

-- =====================================================
-- PART 1: NEW Helper Functions (not modifying existing)
-- =====================================================
-- Note: is_org_member and is_org_admin already exist and are used in policies
-- We only add NEW functions

-- Function: Get current organization from JWT (org_id claim)
CREATE OR REPLACE FUNCTION public.current_org()
RETURNS uuid
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = public, auth
AS $$
  SELECT NULLIF(auth.jwt() ->> 'org_id', '')::uuid;
$$;

COMMENT ON FUNCTION public.current_org() IS 'Returns current organization UUID from JWT org_id claim';

-- Function: Get all organization IDs for current user
CREATE OR REPLACE FUNCTION public.get_user_org_ids()
RETURNS SETOF uuid
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = public, auth
AS $$
  SELECT ou.organization_id
  FROM public.organization_users ou
  WHERE ou.user_id = auth.uid()
    AND ou.is_active = true;
$$;

COMMENT ON FUNCTION public.get_user_org_ids() IS 'Returns all organization UUIDs where current user is a member';

-- Function: Get user role in organization
CREATE OR REPLACE FUNCTION public.get_user_role(org uuid)
RETURNS varchar
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = public, auth
AS $$
  SELECT ou.role
  FROM public.organization_users ou
  WHERE ou.organization_id = org
    AND ou.user_id = auth.uid()
    AND ou.is_active = true
  LIMIT 1;
$$;

COMMENT ON FUNCTION public.get_user_role(uuid) IS 'Returns role of current user in specified organization';

-- Function: Check if user owns resource
CREATE OR REPLACE FUNCTION public.is_owner(owner_user_id uuid)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = public, auth
AS $$
  SELECT auth.uid() = owner_user_id;
$$;

COMMENT ON FUNCTION public.is_owner(uuid) IS 'Returns true if current user is the owner of resource';

-- =====================================================
-- PART 2: Security Hardening - Set search_path
-- =====================================================
-- Fix existing functions to have proper search_path

ALTER FUNCTION public.is_org_member(uuid) SET search_path = public, auth;
ALTER FUNCTION public.is_org_admin(uuid) SET search_path = public, auth;

-- =====================================================
-- PART 3: Critical Indexes for RLS Performance
-- =====================================================

-- Index on organization_users for membership checks
CREATE INDEX IF NOT EXISTS idx_organization_users_user_org
ON public.organization_users(user_id, organization_id)
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_organization_users_role
ON public.organization_users(organization_id, role)
WHERE is_active = true;

-- =====================================================
-- PART 4: RLS Policies - High Priority Tables
-- =====================================================

-- =====================================================
-- TABLE: public.organization_users (CRITICAL)
-- =====================================================

-- Drop existing policies if any
DROP POLICY IF EXISTS organization_users_select ON public.organization_users;
DROP POLICY IF EXISTS organization_users_insert ON public.organization_users;
DROP POLICY IF EXISTS organization_users_update ON public.organization_users;
DROP POLICY IF EXISTS organization_users_delete ON public.organization_users;

-- SELECT: See members of own organizations
CREATE POLICY organization_users_select
ON public.organization_users
FOR SELECT TO authenticated
USING (
  organization_id IN (SELECT public.get_user_org_ids())
);

-- INSERT: Only admins can add members
CREATE POLICY organization_users_insert
ON public.organization_users
FOR INSERT TO authenticated
WITH CHECK (
  public.is_org_admin(organization_id)
);

-- UPDATE: Only admins can modify members
CREATE POLICY organization_users_update
ON public.organization_users
FOR UPDATE TO authenticated
USING (
  public.is_org_admin(organization_id)
)
WITH CHECK (
  public.is_org_admin(organization_id)
);

-- DELETE: Only admins can remove members
CREATE POLICY organization_users_delete
ON public.organization_users
FOR DELETE TO authenticated
USING (
  public.is_org_admin(organization_id)
);

-- =====================================================
-- TABLE: public.teams
-- =====================================================

DROP POLICY IF EXISTS teams_select ON public.teams;
DROP POLICY IF EXISTS teams_insert ON public.teams;
DROP POLICY IF EXISTS teams_update ON public.teams;
DROP POLICY IF EXISTS teams_delete ON public.teams;

-- SELECT: Members of organization
CREATE POLICY teams_select
ON public.teams
FOR SELECT TO authenticated
USING (
  public.is_org_member(organization_id)
);

-- INSERT: Admins can create teams
CREATE POLICY teams_insert
ON public.teams
FOR INSERT TO authenticated
WITH CHECK (
  public.is_org_admin(organization_id)
);

-- UPDATE: Team lead or admin
CREATE POLICY teams_update
ON public.teams
FOR UPDATE TO authenticated
USING (
  public.is_org_member(organization_id)
  AND (
    auth.uid() = created_by_user_id
    OR public.is_org_admin(organization_id)
  )
)
WITH CHECK (
  public.is_org_member(organization_id)
);

-- DELETE: Only admins
CREATE POLICY teams_delete
ON public.teams
FOR DELETE TO authenticated
USING (
  public.is_org_admin(organization_id)
);

-- =====================================================
-- TABLE: public.team_members
-- =====================================================

DROP POLICY IF EXISTS team_members_select ON public.team_members;
DROP POLICY IF EXISTS team_members_insert ON public.team_members;
DROP POLICY IF EXISTS team_members_update ON public.team_members;
DROP POLICY IF EXISTS team_members_delete ON public.team_members;

-- SELECT: Members see team memberships
CREATE POLICY team_members_select
ON public.team_members
FOR SELECT TO authenticated
USING (
  team_id IN (
    SELECT id FROM public.teams
    WHERE public.is_org_member(organization_id)
  )
);

-- INSERT: Team lead or admin
CREATE POLICY team_members_insert
ON public.team_members
FOR INSERT TO authenticated
WITH CHECK (
  team_id IN (
    SELECT t.id FROM public.teams t
    WHERE public.is_org_admin(t.organization_id)
       OR auth.uid() = t.created_by_user_id
  )
);

-- UPDATE: Team lead or admin
CREATE POLICY team_members_update
ON public.team_members
FOR UPDATE TO authenticated
USING (
  team_id IN (
    SELECT t.id FROM public.teams t
    WHERE public.is_org_admin(t.organization_id)
       OR auth.uid() = t.created_by_user_id
  )
);

-- DELETE: Team lead or admin
CREATE POLICY team_members_delete
ON public.team_members
FOR DELETE TO authenticated
USING (
  team_id IN (
    SELECT t.id FROM public.teams t
    WHERE public.is_org_admin(t.organization_id)
       OR auth.uid() = t.created_by_user_id
  )
);

-- =====================================================
-- TABLE: bcm.documents (CRITICAL)
-- =====================================================

DROP POLICY IF EXISTS documents_select ON bcm.documents;
DROP POLICY IF EXISTS documents_insert ON bcm.documents;
DROP POLICY IF EXISTS documents_update ON bcm.documents;
DROP POLICY IF EXISTS documents_delete ON bcm.documents;

-- SELECT: Members see documents
CREATE POLICY documents_select
ON bcm.documents
FOR SELECT TO authenticated
USING (
  public.is_org_member(organization_id)
);

-- INSERT: Members can create
CREATE POLICY documents_insert
ON bcm.documents
FOR INSERT TO authenticated
WITH CHECK (
  public.is_org_member(organization_id)
);

-- UPDATE: Owner or admin
CREATE POLICY documents_update
ON bcm.documents
FOR UPDATE TO authenticated
USING (
  public.is_org_member(organization_id)
  AND (
    auth.uid() = owner_id
    OR public.is_org_admin(organization_id)
  )
)
WITH CHECK (
  public.is_org_member(organization_id)
);

-- DELETE: Only admin
CREATE POLICY documents_delete
ON bcm.documents
FOR DELETE TO authenticated
USING (
  public.is_org_admin(organization_id)
);

-- =====================================================
-- TABLE: governance.policies
-- =====================================================

DROP POLICY IF EXISTS policies_select ON governance.policies;
DROP POLICY IF EXISTS policies_insert ON governance.policies;
DROP POLICY IF EXISTS policies_update ON governance.policies;
DROP POLICY IF EXISTS policies_delete ON governance.policies;

-- SELECT: Members see policies
CREATE POLICY policies_select
ON governance.policies
FOR SELECT TO authenticated
USING (
  public.is_org_member(organization_id)
);

-- INSERT: Admins create policies
CREATE POLICY policies_insert
ON governance.policies
FOR INSERT TO authenticated
WITH CHECK (
  public.is_org_admin(organization_id)
);

-- UPDATE: Owner or admin
CREATE POLICY policies_update
ON governance.policies
FOR UPDATE TO authenticated
USING (
  public.is_org_member(organization_id)
  AND (
    auth.uid() = policy_owner_id
    OR public.is_org_admin(organization_id)
  )
)
WITH CHECK (
  public.is_org_member(organization_id)
);

-- DELETE: Only admin
CREATE POLICY policies_delete
ON governance.policies
FOR DELETE TO authenticated
USING (
  public.is_org_admin(organization_id)
);

-- =====================================================
-- TABLE: response.incidents (CRITICAL)
-- =====================================================

DROP POLICY IF EXISTS incidents_select ON response.incidents;
DROP POLICY IF EXISTS incidents_insert ON response.incidents;
DROP POLICY IF EXISTS incidents_update ON response.incidents;
DROP POLICY IF EXISTS incidents_delete ON response.incidents;

-- SELECT: Members see incidents
CREATE POLICY incidents_select
ON response.incidents
FOR SELECT TO authenticated
USING (
  public.is_org_member(organization_id)
);

-- INSERT: Members can report
CREATE POLICY incidents_insert
ON response.incidents
FOR INSERT TO authenticated
WITH CHECK (
  public.is_org_member(organization_id)
);

-- UPDATE: Incident commander or admin
CREATE POLICY incidents_update
ON response.incidents
FOR UPDATE TO authenticated
USING (
  public.is_org_member(organization_id)
  AND (
    auth.uid() = incident_commander_id
    OR public.is_org_admin(organization_id)
  )
)
WITH CHECK (
  public.is_org_member(organization_id)
);

-- DELETE: Only admin
CREATE POLICY incidents_delete
ON response.incidents
FOR DELETE TO authenticated
USING (
  public.is_org_admin(organization_id)
);

-- =====================================================
-- TABLE: risk.risks (CRITICAL)
-- =====================================================

DROP POLICY IF EXISTS risks_select ON risk.risks;
DROP POLICY IF EXISTS risks_insert ON risk.risks;
DROP POLICY IF EXISTS risks_update ON risk.risks;
DROP POLICY IF EXISTS risks_delete ON risk.risks;

-- SELECT: Members see risks
CREATE POLICY risks_select
ON risk.risks
FOR SELECT TO authenticated
USING (
  public.is_org_member(organization_id)
);

-- INSERT: Members can identify risks
CREATE POLICY risks_insert
ON risk.risks
FOR INSERT TO authenticated
WITH CHECK (
  public.is_org_member(organization_id)
);

-- UPDATE: Risk owner or admin
CREATE POLICY risks_update
ON risk.risks
FOR UPDATE TO authenticated
USING (
  public.is_org_member(organization_id)
  AND (
    auth.uid() = risk_owner_id
    OR public.is_org_admin(organization_id)
  )
)
WITH CHECK (
  public.is_org_member(organization_id)
);

-- DELETE: Only admin
CREATE POLICY risks_delete
ON risk.risks
FOR DELETE TO authenticated
USING (
  public.is_org_admin(organization_id)
);

-- =====================================================
-- PART 5: Grant Schema Usage
-- =====================================================

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA bcm TO authenticated;
GRANT USAGE ON SCHEMA governance TO authenticated;
GRANT USAGE ON SCHEMA response TO authenticated;
GRANT USAGE ON SCHEMA risk TO authenticated;

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 019: RLS Security Hardening - COMPLETE';
    RAISE NOTICE 'New helper functions: 3 (current_org, get_user_org_ids, get_user_role, is_owner)';
    RAISE NOTICE 'Existing functions hardened: 2 (search_path set)';
    RAISE NOTICE 'Indexes created: 2';
    RAISE NOTICE 'RLS policies updated: 7 critical tables';
    RAISE NOTICE '  - organization_users (4 policies)';
    RAISE NOTICE '  - teams (4 policies)';
    RAISE NOTICE '  - team_members (4 policies)';
    RAISE NOTICE '  - bcm.documents (4 policies)';
    RAISE NOTICE '  - governance.policies (4 policies)';
    RAISE NOTICE '  - response.incidents (4 policies)';
    RAISE NOTICE '  - risk.risks (4 policies)';
END $$;
