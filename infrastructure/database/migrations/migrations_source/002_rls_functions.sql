-- ============================================
-- BCM Platform - Unified Database
-- Migration 002: RLS Helper Functions
-- ============================================
-- Creates RLS helper functions for multi-tenancy and security
-- These functions are used in RLS policies across all tables
-- ============================================

-- Get current user ID from JWT token
CREATE OR REPLACE FUNCTION auth.uid()
RETURNS UUID AS $$
    SELECT COALESCE(
        current_setting('request.jwt.claims', true)::json->>'sub',
        NULL
    )::UUID;
$$ LANGUAGE sql STABLE SECURITY DEFINER;

COMMENT ON FUNCTION auth.uid() IS 'Returns the UUID of the current authenticated user from JWT token';

-- Get all JWT claims as JSON
CREATE OR REPLACE FUNCTION auth.jwt()
RETURNS JSON AS $$
    SELECT COALESCE(
        current_setting('request.jwt.claims', true)::json,
        '{}'::json
    );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

COMMENT ON FUNCTION auth.jwt() IS 'Returns all JWT claims as JSON object';

-- Get current tenant ID (for multi-tenancy)
CREATE OR REPLACE FUNCTION auth.current_tenant_id()
RETURNS VARCHAR AS $$
    SELECT COALESCE(
        current_setting('app.tenant_id', true),
        auth.jwt()->>'tenant_id'
    );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

COMMENT ON FUNCTION auth.current_tenant_id() IS 'Returns tenant_id from session variable or JWT token';

-- Check if current user is platform admin
CREATE OR REPLACE FUNCTION auth.is_platform_admin()
RETURNS BOOLEAN AS $$
    SELECT COALESCE(
        (auth.jwt()->>'is_platform_admin')::boolean,
        false
    );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

COMMENT ON FUNCTION auth.is_platform_admin() IS 'Returns true if current user is platform administrator';

-- Check if current user is member of organization
CREATE OR REPLACE FUNCTION auth.is_org_member(org_id UUID)
RETURNS BOOLEAN AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.organization_users
        WHERE organization_id = org_id
        AND user_id = auth.uid()
        AND is_active = true
    );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

COMMENT ON FUNCTION auth.is_org_member(UUID) IS 'Returns true if current user is member of specified organization';

-- Check if current user is admin of organization
CREATE OR REPLACE FUNCTION auth.is_org_admin(org_id UUID)
RETURNS BOOLEAN AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.organization_users
        WHERE organization_id = org_id
        AND user_id = auth.uid()
        AND is_admin = true
        AND is_active = true
    );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

COMMENT ON FUNCTION auth.is_org_admin(UUID) IS 'Returns true if current user is admin of specified organization';

-- Auto-update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS 'Trigger function to automatically update updated_at timestamp';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 002 completed: RLS helper functions created';
END
$$;
