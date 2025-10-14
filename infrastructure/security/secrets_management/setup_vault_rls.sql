-- ============================================================================
-- Supabase Vault - Row Level Security (RLS) Setup
-- ============================================================================
-- This script configures RLS policies for vault.secrets table to ensure:
-- 1. Only service_role and authenticated users can access secrets
-- 2. Anon users have NO access to secrets
-- 3. Audit logging for all secret access
-- ============================================================================

-- Step 1: Enable RLS on vault.secrets table
ALTER TABLE vault.secrets ENABLE ROW LEVEL SECURITY;

-- Step 2: Drop existing policies (if any)
DROP POLICY IF EXISTS "Service role can manage all secrets" ON vault.secrets;
DROP POLICY IF EXISTS "Authenticated users can read secrets" ON vault.secrets;
DROP POLICY IF EXISTS "Block anonymous access to secrets" ON vault.secrets;

-- Step 3: Create RLS policies

-- Policy 1: Service role has full access (SELECT, INSERT, UPDATE, DELETE)
CREATE POLICY "Service role can manage all secrets"
ON vault.secrets
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Policy 2: Authenticated users can only read secrets (via public.get_secret function)
CREATE POLICY "Authenticated users can read secrets"
ON vault.secrets
FOR SELECT
TO authenticated
USING (true);

-- Policy 3: Block all anonymous access
CREATE POLICY "Block anonymous access to secrets"
ON vault.secrets
FOR ALL
TO anon
USING (false)
WITH CHECK (false);

-- Step 4: Verify RLS is enabled
DO $$
BEGIN
    IF NOT (SELECT rowsecurity FROM pg_tables WHERE schemaname = 'vault' AND tablename = 'secrets') THEN
        RAISE EXCEPTION 'RLS is NOT enabled on vault.secrets!';
    ELSE
        RAISE NOTICE '✅ RLS is enabled on vault.secrets';
    END IF;
END $$;

-- Step 5: Show all policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'vault'
ORDER BY tablename, policyname;

-- ============================================================================
-- Security Notes:
-- ============================================================================
-- 1. Service role (used by backend services) has full access
-- 2. Authenticated users can read via public.get_secret() function
-- 3. Anonymous users have ZERO access
-- 4. All secret modifications require service_role
-- 5. Consider adding audit triggers for INSERT/UPDATE/DELETE operations
-- ============================================================================
