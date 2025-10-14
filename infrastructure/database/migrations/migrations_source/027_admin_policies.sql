-- ============================================
-- BCM Platform - Unified Database
-- Migration 027: Admin Access Policies
-- ============================================
-- Adds platform admin policies to existing tables
-- Now that platform_administrators table exists
-- ============================================

-- Policy: Platform admins can view all individual users
CREATE POLICY "Platform admins can view all individual users"
    ON public.individual_users FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid()) AND pa.is_active = true
        )
    );

-- Policy: Platform admins can view all user relationships
CREATE POLICY "Platform admins can view all relationships"
    ON public.user_relationships FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid()) AND pa.is_active = true
        )
    );

-- Policy: Platform admins can view all organizations
CREATE POLICY "Platform admins can view all organizations"
    ON public.organizations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid())
            AND pa.is_active = true
            AND pa.can_access_all_tenants = true
        )
    );

-- Policy: Platform admins can view all user profiles
CREATE POLICY "Platform admins can view all user profiles"
    ON public.user_profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid()) AND pa.is_active = true
        )
    );

-- Policy: Platform admins can view all teams
CREATE POLICY "Platform admins can view all teams"
    ON public.teams FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid())
            AND pa.is_active = true
            AND pa.can_access_all_tenants = true
        )
    );

-- Comments
COMMENT ON POLICY "Platform admins can view all individual users" ON public.individual_users
    IS 'Platform administrators can view all B2C user profiles';
COMMENT ON POLICY "Platform admins can view all relationships" ON public.user_relationships
    IS 'Platform administrators can view all user relationships for moderation';
COMMENT ON POLICY "Platform admins can view all organizations" ON public.organizations
    IS 'Platform administrators with can_access_all_tenants can view all organizations';
