-- ============================================
-- BCM Platform - Unified Database
-- Migration 037: Final Policy Cleanup
-- ============================================
-- Fixes last remaining multiple permissive policies:
-- 1. governance.policies (3 duplicates)
-- 2. public.team_members (3 duplicates)
-- ============================================

-- ============================================
-- Part 1: Clean governance.policies
-- ============================================

-- Remove duplicate policies
DROP POLICY IF EXISTS "policies_delete" ON governance.policies;
DROP POLICY IF EXISTS "policies_insert" ON governance.policies;
DROP POLICY IF EXISTS "policies_update_consolidated_authenticated" ON governance.policies;

-- Keep only policies_all which handles all operations
-- Verify it exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'governance'
        AND tablename = 'policies'
        AND policyname = 'policies_all'
    ) THEN
        RAISE EXCEPTION 'policies_all does not exist! Cannot proceed.';
    END IF;
END $$;

COMMENT ON POLICY "policies_all" ON governance.policies
    IS 'Consolidated policy for all operations on governance.policies';

-- ============================================
-- Part 2: Clean public.team_members
-- ============================================

-- Remove duplicate policies
DROP POLICY IF EXISTS "team_members_delete" ON public.team_members;
DROP POLICY IF EXISTS "team_members_insert" ON public.team_members;
DROP POLICY IF EXISTS "team_members_update" ON public.team_members;

-- Keep only team_members_all which handles all operations
-- Verify it exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
        AND tablename = 'team_members'
        AND policyname = 'team_members_all'
    ) THEN
        RAISE EXCEPTION 'team_members_all does not exist! Cannot proceed.';
    END IF;
END $$;

COMMENT ON POLICY "team_members_all" ON public.team_members
    IS 'Consolidated policy for all operations on public.team_members';

-- ============================================
-- Verification
-- ============================================

-- Count remaining policies
DO $$
DECLARE
    governance_policies_count INTEGER;
    team_members_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO governance_policies_count
    FROM pg_policies
    WHERE schemaname = 'governance' AND tablename = 'policies';

    SELECT COUNT(*) INTO team_members_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'team_members';

    RAISE NOTICE 'governance.policies has % policies (expected: 1)', governance_policies_count;
    RAISE NOTICE 'public.team_members has % policies (expected: 1)', team_members_count;

    IF governance_policies_count != 1 THEN
        RAISE WARNING 'governance.policies should have exactly 1 policy, but has %', governance_policies_count;
    END IF;

    IF team_members_count != 1 THEN
        RAISE WARNING 'public.team_members should have exactly 1 policy, but has %', team_members_count;
    END IF;
END $$;

-- ============================================
-- Summary
-- ============================================

-- Migration complete: Cleaned up last remaining duplicate policies
-- - governance.policies: 1 policy (policies_all)
-- - public.team_members: 1 policy (team_members_all)
-- All multiple permissive policy warnings should now be resolved!
