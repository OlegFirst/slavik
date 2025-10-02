-- ============================================
-- BCM Platform - Unified Database
-- Migration 003: Core Tables (Schema: public)
-- ============================================
-- Creates core shared tables: organizations, user_profiles, teams
-- These tables are foundational for the entire platform
-- ============================================

-- ============================================
-- Table: organizations
-- Consolidates 4 sources:
-- - COMMUNITY/clients organizations
-- - INTELLIGENCE/digital-twin organizations
-- - INTELLIGENCE organization_profiles
-- - PLATFORM bcm_companies
-- ============================================

CREATE TABLE public.organizations (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    tenant_id VARCHAR(255) UNIQUE NOT NULL,

    -- Basic info
    type VARCHAR(50) NOT NULL DEFAULT 'enterprise',
    industry VARCHAR(100),
    size VARCHAR(50),
    description TEXT,

    -- Contact
    email VARCHAR(255),
    phone VARCHAR(50),
    website VARCHAR(255),

    -- Address (JSONB for flexibility)
    address JSONB DEFAULT '{}'::jsonb,

    -- Subscription & Billing
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    subscription_start_date DATE,
    subscription_end_date DATE,
    max_users INTEGER DEFAULT 10,
    billing_info JSONB DEFAULT '{}'::jsonb,

    -- NPO-specific (from SEH)
    org_code VARCHAR(50) UNIQUE,
    pgpx_subject_id VARCHAR(100),
    mission TEXT,
    annual_budget DECIMAL(15,2),

    -- Settings & Metadata
    settings JSONB DEFAULT '{}'::jsonb,
    features JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Data residency & compliance
    data_residency VARCHAR(10) DEFAULT 'US',
    compliance_standards TEXT[],

    -- Onboarding
    onboarding_stage VARCHAR(50) DEFAULT 'new',

    -- Status & Timestamps
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(name,'') || ' ' ||
            coalesce(description,'') || ' ' ||
            coalesce(industry,'')
        )
    ) STORED
);

-- Indexes
CREATE INDEX idx_organizations_tenant_id ON public.organizations(tenant_id);
CREATE INDEX idx_organizations_slug ON public.organizations(slug);
CREATE INDEX idx_organizations_type ON public.organizations(type);
CREATE INDEX idx_organizations_subscription ON public.organizations(subscription_status) WHERE is_active = true;
CREATE INDEX idx_organizations_search ON public.organizations USING GIN(search_vector);

-- Auto-update timestamp trigger
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON public.organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Organizations visible to members"
    ON public.organizations FOR SELECT
    USING (
        tenant_id = auth.current_tenant_id()
        OR auth.is_platform_admin()
    );

CREATE POLICY "Organizations insertable by authenticated"
    ON public.organizations FOR INSERT
    WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Organizations updatable by org admins"
    ON public.organizations FOR UPDATE
    USING (auth.is_org_admin(id));

COMMENT ON TABLE public.organizations IS 'Canonical organizations table - consolidates 4 sources';

-- ============================================
-- Table: user_profiles
-- Consolidates 2 sources:
-- - COMMUNITY/clients user_profiles
-- - PLATFORM bcm_users
-- ============================================

CREATE TABLE public.user_profiles (
    -- Identity (extends auth.users)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Basic info
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(255),
    full_name VARCHAR(255) GENERATED ALWAYS AS (
        TRIM(COALESCE(first_name, '') || ' ' || COALESCE(last_name, ''))
    ) STORED,

    -- Profile
    avatar_url TEXT,
    bio TEXT,
    phone VARCHAR(50),

    -- Role & Permissions (platform-level)
    role VARCHAR(50) DEFAULT 'user',
    is_platform_admin BOOLEAN DEFAULT false,

    -- Location & Locale
    country VARCHAR(100),
    city VARCHAR(100),
    timezone VARCHAR(100) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    locale VARCHAR(10) DEFAULT 'en_US',

    -- Professional
    company VARCHAR(255),
    job_title VARCHAR(255),
    department VARCHAR(255),

    -- Social links
    linkedin_url TEXT,
    twitter_handle VARCHAR(100),
    github_handle VARCHAR(100),
    website_url TEXT,

    -- Preferences (UI/UX)
    preferences JSONB DEFAULT '{
        "theme": "light",
        "notifications": {
            "email": true,
            "push": true,
            "sms": false
        },
        "dashboard_layout": "default"
    }'::jsonb,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Onboarding
    onboarding_completed BOOLEAN DEFAULT false,
    onboarding_step VARCHAR(50),

    -- Activity tracking
    last_login_at TIMESTAMPTZ,
    login_count INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(display_name,'') || ' ' ||
            coalesce(email,'') || ' ' ||
            coalesce(job_title,'')
        )
    ) STORED
);

-- Indexes
CREATE INDEX idx_user_profiles_user_id ON public.user_profiles(user_id);
CREATE INDEX idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX idx_user_profiles_role ON public.user_profiles(role) WHERE is_active = true;
CREATE INDEX idx_user_profiles_search ON public.user_profiles USING GIN(search_vector);

-- Auto-update timestamp trigger
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "User profiles publicly readable"
    ON public.user_profiles FOR SELECT
    USING (true);

CREATE POLICY "User profiles updatable by owner"
    ON public.user_profiles FOR UPDATE
    USING (user_id = auth.uid());

CREATE POLICY "User profiles insertable on registration"
    ON public.user_profiles FOR INSERT
    WITH CHECK (user_id = auth.uid());

COMMENT ON TABLE public.user_profiles IS 'Extended user profiles - consolidates 2 sources';

-- ============================================
-- Table: organization_users
-- User ↔ Organization membership
-- ============================================

CREATE TABLE public.organization_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Role in organization
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    is_admin BOOLEAN DEFAULT false,
    is_primary_contact BOOLEAN DEFAULT false,

    -- Position
    title VARCHAR(255),
    department VARCHAR(255),

    -- Permissions (org-specific)
    permissions JSONB DEFAULT '{
        "can_invite_users": false,
        "can_purchase_services": false,
        "can_manage_billing": false,
        "can_configure_settings": false
    }'::jsonb,

    -- Notification preferences (org-specific)
    notification_prefs JSONB DEFAULT '{
        "incidents": true,
        "exercises": true,
        "reports": false
    }'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT true,

    -- Invitation tracking
    invited_by UUID REFERENCES auth.users(id),
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    joined_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint
    UNIQUE(organization_id, user_id)
);

-- Indexes
CREATE INDEX idx_org_users_org_id ON public.organization_users(organization_id) WHERE is_active = true;
CREATE INDEX idx_org_users_user_id ON public.organization_users(user_id) WHERE is_active = true;
CREATE INDEX idx_org_users_role ON public.organization_users(organization_id, role);

-- Auto-update timestamp trigger
CREATE TRIGGER update_organization_users_updated_at
    BEFORE UPDATE ON public.organization_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE public.organization_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Org users visible to org members"
    ON public.organization_users FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id FROM public.organization_users
            WHERE user_id = auth.uid() AND is_active = true
        )
    );

CREATE POLICY "Org users manageable by admins"
    ON public.organization_users FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE public.organization_users IS 'User membership in organizations';

-- ============================================
-- Table: teams
-- Collaborative teams (humans + AI)
-- ============================================

CREATE TABLE public.teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic info
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Organization linkage (nullable for cross-org teams)
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Type
    team_type VARCHAR(50) NOT NULL DEFAULT 'project',

    -- Visibility
    is_public BOOLEAN DEFAULT false,

    -- Settings
    settings JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Creator
    created_by_user_id UUID REFERENCES auth.users(id),

    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_teams_org_id ON public.teams(organization_id) WHERE is_active = true;
CREATE INDEX idx_teams_type ON public.teams(team_type);

-- Auto-update timestamp trigger
CREATE TRIGGER update_teams_updated_at
    BEFORE UPDATE ON public.teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Teams visible to org members"
    ON public.teams FOR SELECT
    USING (
        is_public = true
        OR organization_id IN (
            SELECT organization_id FROM public.organization_users
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Teams manageable by org admins"
    ON public.teams FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE public.teams IS 'Teams supporting both human and AI members';

-- ============================================
-- Table: team_members
-- Team membership (humans OR AI)
-- ============================================

CREATE TABLE public.team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Team
    team_id UUID NOT NULL REFERENCES public.teams(id) ON DELETE CASCADE,

    -- Member (EITHER user OR AI, not both)
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    ai_colleague_id UUID, -- FK added later after community.ai_digital_colleagues created

    -- Role in team
    role VARCHAR(50) DEFAULT 'member',

    -- Permissions
    permissions JSONB DEFAULT '{}'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    added_by UUID REFERENCES auth.users(id),

    -- Constraints
    CHECK (
        (user_id IS NOT NULL AND ai_colleague_id IS NULL) OR
        (user_id IS NULL AND ai_colleague_id IS NOT NULL)
    ),
    UNIQUE(team_id, user_id),
    UNIQUE(team_id, ai_colleague_id)
);

-- Indexes
CREATE INDEX idx_team_members_team_id ON public.team_members(team_id) WHERE is_active = true;
CREATE INDEX idx_team_members_user_id ON public.team_members(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_team_members_ai_id ON public.team_members(ai_colleague_id) WHERE ai_colleague_id IS NOT NULL;

-- RLS
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Team members visible to team members"
    ON public.team_members FOR SELECT
    USING (
        team_id IN (
            SELECT team_id FROM public.team_members
            WHERE user_id = auth.uid() AND is_active = true
        )
    );

COMMENT ON TABLE public.team_members IS 'Team membership supporting both users and AI colleagues';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 003 completed: Core tables created (5 tables)';
END
$$;
