-- ============================================
-- BCM Platform - Unified Database
-- Migration 025: Platform Administrators
-- ============================================
-- Creates platform_administrators table for super users
-- Based on PLATFORM/clients/app/models/admin.py
-- ============================================

CREATE TABLE public.platform_administrators (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign key to user profile
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Admin level
    admin_level VARCHAR(50) NOT NULL,
    -- Levels: super_admin, admin, support, developer

    -- Department
    department VARCHAR(100),  -- Engineering, Support, Security, DevOps

    -- Permissions
    permissions JSONB DEFAULT '{}'::jsonb,  -- Detailed admin permissions
    can_access_all_tenants BOOLEAN DEFAULT false,
    can_manage_platform BOOLEAN DEFAULT false,
    can_manage_ai_agents BOOLEAN DEFAULT false,
    can_view_audit_logs BOOLEAN DEFAULT true,
    can_impersonate_users BOOLEAN DEFAULT false,  -- For support

    -- Security
    mfa_required BOOLEAN DEFAULT true,  -- 2FA always required for admins
    ip_whitelist TEXT[],  -- Allowed IP addresses

    -- Activity tracking
    last_action TIMESTAMPTZ,
    actions_count INTEGER DEFAULT 0,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT platform_administrators_admin_level_check
        CHECK (admin_level IN ('super_admin', 'admin', 'support', 'developer', 'security')),
    CONSTRAINT platform_administrators_department_check
        CHECK (department IN ('Engineering', 'Support', 'Security', 'DevOps', 'Product', 'Data'))
);

-- Indexes
CREATE INDEX idx_platform_administrators_user_id ON public.platform_administrators(user_id);
CREATE INDEX idx_platform_administrators_level ON public.platform_administrators(admin_level);
CREATE INDEX idx_platform_administrators_department ON public.platform_administrators(department);
CREATE INDEX idx_platform_administrators_active ON public.platform_administrators(is_active) WHERE is_active = true;
CREATE INDEX idx_platform_administrators_permissions ON public.platform_administrators USING GIN(permissions);

-- Auto-update timestamp trigger
CREATE TRIGGER update_platform_administrators_updated_at
    BEFORE UPDATE ON public.platform_administrators
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE public.platform_administrators ENABLE ROW LEVEL SECURITY;

-- Policy: Admins can view their own profile
CREATE POLICY "Platform admins can view own profile"
    ON public.platform_administrators FOR SELECT
    USING ((SELECT auth.uid()) = user_id);

-- Policy: Super admins can view all admins
CREATE POLICY "Super admins can view all admins"
    ON public.platform_administrators FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid())
            AND pa.admin_level = 'super_admin'
            AND pa.is_active = true
        )
    );

-- Policy: Super admins can manage all admins
CREATE POLICY "Super admins can manage all admins"
    ON public.platform_administrators FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid())
            AND pa.admin_level = 'super_admin'
            AND pa.is_active = true
        )
    );

-- Policy: Admins can update their own profile
CREATE POLICY "Platform admins can update own profile"
    ON public.platform_administrators FOR UPDATE
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

-- Comments
COMMENT ON TABLE public.platform_administrators IS 'Platform administrators - super users who manage the entire platform';
COMMENT ON COLUMN public.platform_administrators.admin_level IS 'Admin level: super_admin, admin, support, developer, security';
COMMENT ON COLUMN public.platform_administrators.can_access_all_tenants IS 'Can access data from all organizations';
COMMENT ON COLUMN public.platform_administrators.can_impersonate_users IS 'Can impersonate users for support purposes';
COMMENT ON COLUMN public.platform_administrators.mfa_required IS '2FA always required for admins';
COMMENT ON COLUMN public.platform_administrators.ip_whitelist IS 'Allowed IP addresses for admin access';
