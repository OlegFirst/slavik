-- ============================================
-- BCM Platform - Unified Database
-- Migration 004: Community Schema
-- ============================================
-- Creates Community marketplace tables: specialists, services, reviews, AI colleagues
-- Schema: community
-- ============================================

-- Table: community.specialists
CREATE TABLE community.specialists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Profile
    full_name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    bio TEXT,
    years_experience INTEGER,

    -- Pricing
    hourly_rate DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Expertise
    specializations JSONB DEFAULT '[]'::jsonb,
    industries JSONB DEFAULT '[]'::jsonb,
    certifications_summary TEXT,
    languages JSONB DEFAULT '[]'::jsonb,
    skills JSONB DEFAULT '[]'::jsonb,

    -- Location
    country VARCHAR(100),
    city VARCHAR(100),
    timezone VARCHAR(100),
    remote_available BOOLEAN DEFAULT true,
    onsite_available BOOLEAN DEFAULT false,

    -- Availability
    availability_status VARCHAR(50) DEFAULT 'available',
    available_from DATE,

    -- Stats
    rating DECIMAL(3,2) DEFAULT 0.0,
    total_reviews INTEGER DEFAULT 0,
    total_engagements INTEGER DEFAULT 0,
    profile_completion INTEGER DEFAULT 0,

    -- Verification
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES auth.users(id),

    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(full_name,'') || ' ' ||
            coalesce(title,'') || ' ' ||
            coalesce(bio,'')
        )
    ) STORED
);

CREATE INDEX idx_specialists_rating ON community.specialists(rating DESC) WHERE is_active = true;
CREATE INDEX idx_specialists_availability ON community.specialists(availability_status) WHERE is_active = true;
CREATE INDEX idx_specialists_search ON community.specialists USING GIN(search_vector);
CREATE INDEX idx_specialists_specializations ON community.specialists USING GIN(specializations);

CREATE TRIGGER update_specialists_updated_at BEFORE UPDATE ON community.specialists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE community.specialists ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Specialists publicly readable" ON community.specialists FOR SELECT USING (is_active = true);
CREATE POLICY "Specialists updatable by owner" ON community.specialists FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Specialists insertable by owner" ON community.specialists FOR INSERT WITH CHECK (user_id = auth.uid());

-- Table: community.specialist_certifications
CREATE TABLE community.specialist_certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_id UUID NOT NULL REFERENCES community.specialists(id) ON DELETE CASCADE,

    certification_name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255),
    issue_date DATE,
    expiry_date DATE,
    credential_id VARCHAR(255),
    credential_url TEXT,

    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_certifications_specialist ON community.specialist_certifications(specialist_id);

ALTER TABLE community.specialist_certifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Certifications publicly readable" ON community.specialist_certifications FOR SELECT USING (true);

-- Table: community.specialist_services
CREATE TABLE community.specialist_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_id UUID NOT NULL REFERENCES community.specialists(id) ON DELETE CASCADE,

    service_name VARCHAR(255) NOT NULL,
    description TEXT,
    duration_hours INTEGER,
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_services_specialist ON community.specialist_services(specialist_id) WHERE is_active = true;

ALTER TABLE community.specialist_services ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Services publicly readable" ON community.specialist_services FOR SELECT USING (is_active = true);

-- Table: community.specialist_reviews
CREATE TABLE community.specialist_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_id UUID NOT NULL REFERENCES community.specialists(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES auth.users(id),
    organization_id UUID REFERENCES public.organizations(id),

    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_title VARCHAR(255),
    review_text TEXT,
    would_recommend BOOLEAN DEFAULT true,

    specialist_response TEXT,
    responded_at TIMESTAMPTZ,

    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reviews_specialist ON community.specialist_reviews(specialist_id);

ALTER TABLE community.specialist_reviews ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Reviews publicly readable" ON community.specialist_reviews FOR SELECT USING (true);

-- Table: community.specialist_engagements
CREATE TABLE community.specialist_engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_id UUID NOT NULL REFERENCES community.specialists(id),
    client_organization_id UUID NOT NULL REFERENCES public.organizations(id),
    requested_by_user_id UUID NOT NULL REFERENCES auth.users(id),

    engagement_type VARCHAR(50),
    description TEXT,

    -- Workflow
    status VARCHAR(50) DEFAULT 'requested',

    -- Timeline
    start_date DATE,
    end_date DATE,

    -- Budget
    budget DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Deliverables
    deliverables JSONB DEFAULT '[]'::jsonb,

    -- Completion
    completed_at TIMESTAMPTZ,
    completion_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_engagements_specialist ON community.specialist_engagements(specialist_id);
CREATE INDEX idx_engagements_client ON community.specialist_engagements(client_organization_id);

CREATE TRIGGER update_engagements_updated_at BEFORE UPDATE ON community.specialist_engagements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE community.specialist_engagements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Engagements visible to parties" ON community.specialist_engagements FOR SELECT
    USING (
        requested_by_user_id = auth.uid()
        OR EXISTS (SELECT 1 FROM community.specialists WHERE id = specialist_id AND user_id = auth.uid())
        OR auth.is_org_admin(client_organization_id)
    );

-- Table: community.ai_digital_colleagues
CREATE TABLE community.ai_digital_colleagues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Identity
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    ai_type VARCHAR(50),
    description TEXT,

    -- Capabilities
    capabilities JSONB DEFAULT '[]'::jsonb,

    -- Permissions
    permission_level VARCHAR(50) DEFAULT 'read_only',
    requires_approval_for JSONB DEFAULT '[]'::jsonb,

    -- Trust metrics
    trust_score DECIMAL(5,2) DEFAULT 0.0,
    total_actions INTEGER DEFAULT 0,
    successful_actions INTEGER DEFAULT 0,
    failed_actions INTEGER DEFAULT 0,

    -- Configuration
    model_config JSONB DEFAULT '{}'::jsonb,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_colleagues_org ON community.ai_digital_colleagues(organization_id) WHERE is_active = true;

CREATE TRIGGER update_ai_colleagues_updated_at BEFORE UPDATE ON community.ai_digital_colleagues
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE community.ai_digital_colleagues ENABLE ROW LEVEL SECURITY;

CREATE POLICY "AI colleagues visible to org members" ON community.ai_digital_colleagues FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "AI colleagues manageable by org admins" ON community.ai_digital_colleagues FOR ALL
    USING (auth.is_org_admin(organization_id));

-- Now add the foreign key to team_members
ALTER TABLE public.team_members
    ADD CONSTRAINT fk_team_members_ai_colleague
    FOREIGN KEY (ai_colleague_id) REFERENCES community.ai_digital_colleagues(id) ON DELETE CASCADE;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 004 completed: Community schema created (6 tables)';
END
$$;
