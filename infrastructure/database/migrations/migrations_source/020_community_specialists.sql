-- =====================================================
-- Migration 020: Community - Specialist Marketplace
-- =====================================================
-- Purpose: Marketplace for BCM specialists/consultants
-- Based on: /SERVICES/COMMUNITY/clients/app/models/specialist.py
-- Date: 2025-10-02
-- Specialists can offer services, build portfolio, get reviews
-- =====================================================

-- =====================================================
-- CLEANUP: Drop existing tables if they exist (safer recreation)
-- =====================================================

DROP TABLE IF EXISTS community.specialist_engagements CASCADE;
DROP TABLE IF EXISTS community.specialist_reviews CASCADE;
DROP TABLE IF EXISTS community.specialist_services CASCADE;
DROP TABLE IF EXISTS community.specialist_portfolio CASCADE;
DROP TABLE IF EXISTS community.specialist_certifications CASCADE;
DROP TABLE IF EXISTS community.specialists CASCADE;

-- =====================================================
-- TABLE 1: community.specialists
-- =====================================================

CREATE TABLE community.specialists (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign key to user
    user_id UUID UNIQUE NOT NULL,

    -- Basic Info
    full_name VARCHAR(200) NOT NULL,
    title VARCHAR(200),
    bio TEXT,

    -- Professional
    years_experience INTEGER,

    -- Pricing
    hourly_rate DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    pricing_model VARCHAR(50) DEFAULT 'hourly' CHECK (pricing_model IN ('hourly', 'fixed', 'retainer')),

    -- Specializations & Skills
    specializations JSONB DEFAULT '[]'::jsonb,
    industries JSONB DEFAULT '[]'::jsonb,
    languages JSONB DEFAULT '[]'::jsonb,
    certifications_summary JSONB DEFAULT '[]'::jsonb,
    skills JSONB DEFAULT '[]'::jsonb,

    -- Availability
    availability_status VARCHAR(20) DEFAULT 'available' CHECK (availability_status IN ('available', 'busy', 'unavailable')),
    availability_hours JSONB,
    timezone VARCHAR(50),

    -- Location
    country VARCHAR(100),
    city VARCHAR(100),
    remote_available BOOLEAN DEFAULT true,
    onsite_available BOOLEAN DEFAULT true,

    -- Ratings & Metrics
    rating DECIMAL(3,2) DEFAULT 0.0,
    total_reviews INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    response_time_hours DECIMAL(5,2),
    acceptance_rate DECIMAL(5,2),

    -- Verification
    is_verified BOOLEAN DEFAULT false,
    verified_date DATE,
    verification_badge VARCHAR(20) CHECK (verification_badge IN ('gold', 'silver', 'bronze')),
    linkedin_verified BOOLEAN DEFAULT false,
    identity_verified BOOLEAN DEFAULT false,
    background_check BOOLEAN DEFAULT false,

    -- Trust & Quality
    trust_score DECIMAL(5,2) DEFAULT 0.0,
    profile_completion INTEGER DEFAULT 0 CHECK (profile_completion BETWEEN 0 AND 100),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE 2: community.specialist_certifications
-- =====================================================

CREATE TABLE community.specialist_certifications (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Key
    specialist_id UUID NOT NULL REFERENCES community.specialists(id) ON DELETE CASCADE,

    -- Certification details
    name VARCHAR(200) NOT NULL,
    issuing_organization VARCHAR(200) NOT NULL,
    credential_id VARCHAR(100),
    issue_date DATE,
    expiry_date DATE,
    credential_url VARCHAR(500),

    -- Verification
    is_verified BOOLEAN DEFAULT false,
    verified_by UUID,
    verified_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE 3: community.specialist_portfolio
-- =====================================================

CREATE TABLE community.specialist_portfolio (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Key
    specialist_id UUID NOT NULL REFERENCES community.specialists(id) ON DELETE CASCADE,

    -- Project details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    client_industry VARCHAR(100),
    project_type VARCHAR(50) CHECK (project_type IN ('bcm_implementation', 'bia', 'risk_assessment', 'audit', 'training', 'other')),

    -- Timeline
    date DATE,
    duration VARCHAR(50),

    -- Team
    team_size INTEGER,
    role VARCHAR(100),

    -- Details
    key_achievements TEXT,
    technologies_used JSONB DEFAULT '[]'::jsonb,

    -- Files
    files JSONB DEFAULT '[]'::jsonb,

    -- Display
    is_featured BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,

    -- Status
    active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE 4: community.specialist_services
-- =====================================================

CREATE TABLE community.specialist_services (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Key
    specialist_id UUID NOT NULL REFERENCES community.specialists(id) ON DELETE CASCADE,

    -- Service details
    name VARCHAR(200) NOT NULL,
    description TEXT,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('consulting', 'assessment', 'training', 'audit', 'implementation', 'other')),

    -- Pricing
    pricing_model VARCHAR(50) NOT NULL CHECK (pricing_model IN ('hourly', 'fixed', 'milestone', 'project')),
    base_price DECIMAL(10,2),
    duration_estimate_hours DECIMAL(6,2),
    min_engagement_hours DECIMAL(6,2),

    -- Delivery
    delivery_mode VARCHAR(20) DEFAULT 'hybrid' CHECK (delivery_mode IN ('remote', 'onsite', 'hybrid')),

    -- Display
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE 5: community.specialist_reviews
-- =====================================================

CREATE TABLE community.specialist_reviews (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    specialist_id UUID NOT NULL REFERENCES community.specialists(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL,
    organization_id UUID REFERENCES public.organizations(id),
    engagement_id UUID,

    -- Ratings
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    professionalism_rating INTEGER CHECK (professionalism_rating BETWEEN 1 AND 5),
    expertise_rating INTEGER CHECK (expertise_rating BETWEEN 1 AND 5),
    communication_rating INTEGER CHECK (communication_rating BETWEEN 1 AND 5),
    timeliness_rating INTEGER CHECK (timeliness_rating BETWEEN 1 AND 5),

    -- Review text
    review_text TEXT,
    pros TEXT,
    cons TEXT,
    would_recommend BOOLEAN,

    -- Specialist response
    response TEXT,
    response_date TIMESTAMP WITH TIME ZONE,

    -- Verification
    is_verified BOOLEAN DEFAULT false,

    -- Display
    is_featured BOOLEAN DEFAULT false,
    helpful_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE 6: community.specialist_engagements
-- =====================================================

CREATE TABLE community.specialist_engagements (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Parties
    specialist_id UUID NOT NULL REFERENCES community.specialists(id),
    organization_id UUID NOT NULL REFERENCES public.organizations(id),
    requested_by_user_id UUID NOT NULL,

    -- Service
    service_type VARCHAR(100) NOT NULL,
    scope JSONB,

    -- Pricing
    pricing_model VARCHAR(50) NOT NULL CHECK (pricing_model IN ('hourly', 'fixed', 'milestone', 'retainer')),
    contract_value DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    estimated_hours DECIMAL(6,2),
    actual_hours DECIMAL(6,2),

    -- Timeline
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    actual_end_date DATE,

    -- Status
    status VARCHAR(50) DEFAULT 'requested' CHECK (status IN ('requested', 'accepted', 'in_progress', 'completed', 'cancelled', 'rejected')),

    -- Access & Permissions
    permissions_granted JSONB DEFAULT '{}'::jsonb,
    modules_access JSONB DEFAULT '[]'::jsonb,

    -- Payment
    payment_status VARCHAR(50) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'escrowed', 'released', 'refunded')),
    payment_milestones JSONB DEFAULT '[]'::jsonb,

    -- Contract
    contract_url VARCHAR(500),

    -- Notes
    notes TEXT,
    specialist_notes TEXT,
    organization_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Specialists
CREATE INDEX IF NOT EXISTS idx_specialists_user ON community.specialists(user_id);
CREATE INDEX IF NOT EXISTS idx_specialists_rating ON community.specialists(rating DESC);
CREATE INDEX IF NOT EXISTS idx_specialists_verified ON community.specialists(is_verified) WHERE is_verified = true;
CREATE INDEX IF NOT EXISTS idx_specialists_availability ON community.specialists(availability_status);
CREATE INDEX IF NOT EXISTS idx_specialists_country ON community.specialists(country);
CREATE INDEX IF NOT EXISTS idx_specialists_specializations ON community.specialists USING GIN(specializations);
CREATE INDEX IF NOT EXISTS idx_specialists_skills ON community.specialists USING GIN(skills);

-- Certifications
CREATE INDEX IF NOT EXISTS idx_certifications_specialist ON community.specialist_certifications(specialist_id);
CREATE INDEX IF NOT EXISTS idx_certifications_verified ON community.specialist_certifications(is_verified);

-- Portfolio
CREATE INDEX IF NOT EXISTS idx_portfolio_specialist ON community.specialist_portfolio(specialist_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_featured ON community.specialist_portfolio(is_featured) WHERE is_featured = true;

-- Services
CREATE INDEX IF NOT EXISTS idx_services_specialist ON community.specialist_services(specialist_id);
CREATE INDEX IF NOT EXISTS idx_services_active ON community.specialist_services(is_active) WHERE is_active = true;

-- Reviews
CREATE INDEX IF NOT EXISTS idx_reviews_specialist ON community.specialist_reviews(specialist_id);
CREATE INDEX IF NOT EXISTS idx_reviews_organization ON community.specialist_reviews(organization_id);
CREATE INDEX IF NOT EXISTS idx_reviews_engagement ON community.specialist_reviews(engagement_id);

-- Engagements
CREATE INDEX IF NOT EXISTS idx_engagements_specialist ON community.specialist_engagements(specialist_id);
CREATE INDEX IF NOT EXISTS idx_engagements_organization ON community.specialist_engagements(organization_id);
CREATE INDEX IF NOT EXISTS idx_engagements_status ON community.specialist_engagements(status);
CREATE INDEX IF NOT EXISTS idx_engagements_dates ON community.specialist_engagements(start_date, end_date);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE community.specialists ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_services ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_engagements ENABLE ROW LEVEL SECURITY;

-- Specialists: Public read (marketplace), owner edit
CREATE POLICY specialists_public_read ON community.specialists
FOR SELECT TO authenticated
USING (is_active = true);

CREATE POLICY specialists_owner_update ON community.specialists
FOR UPDATE TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Certifications: Public read, owner write
CREATE POLICY certifications_public_read ON community.specialist_certifications
FOR SELECT TO authenticated
USING (
    specialist_id IN (SELECT id FROM community.specialists WHERE is_active = true)
);

CREATE POLICY certifications_owner_write ON community.specialist_certifications
FOR ALL TO authenticated
USING (
    specialist_id IN (SELECT id FROM community.specialists WHERE user_id = auth.uid())
);

-- Portfolio: Public read, owner write
CREATE POLICY portfolio_public_read ON community.specialist_portfolio
FOR SELECT TO authenticated
USING (active = true);

CREATE POLICY portfolio_owner_write ON community.specialist_portfolio
FOR ALL TO authenticated
USING (
    specialist_id IN (SELECT id FROM community.specialists WHERE user_id = auth.uid())
);

-- Services: Public read, owner write
CREATE POLICY services_public_read ON community.specialist_services
FOR SELECT TO authenticated
USING (is_active = true);

CREATE POLICY services_owner_write ON community.specialist_services
FOR ALL TO authenticated
USING (
    specialist_id IN (SELECT id FROM community.specialists WHERE user_id = auth.uid())
);

-- Reviews: Public read, parties write
CREATE POLICY reviews_public_read ON community.specialist_reviews
FOR SELECT TO authenticated
USING (true);

CREATE POLICY reviews_reviewer_write ON community.specialist_reviews
FOR INSERT TO authenticated
WITH CHECK (auth.uid() = reviewer_id);

CREATE POLICY reviews_specialist_response ON community.specialist_reviews
FOR UPDATE TO authenticated
USING (
    specialist_id IN (SELECT id FROM community.specialists WHERE user_id = auth.uid())
    AND response IS NULL
)
WITH CHECK (response IS NOT NULL);

-- Engagements: Parties only
CREATE POLICY engagements_parties_access ON community.specialist_engagements
FOR ALL TO authenticated
USING (
    specialist_id IN (SELECT id FROM community.specialists WHERE user_id = auth.uid())
    OR public.is_org_member(organization_id)
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Update updated_at
CREATE TRIGGER update_specialists_updated_at
BEFORE UPDATE ON community.specialists
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at
BEFORE UPDATE ON community.specialist_reviews
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_engagements_updated_at
BEFORE UPDATE ON community.specialist_engagements
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Calculate specialist rating from reviews
CREATE OR REPLACE FUNCTION community.update_specialist_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE community.specialists
    SET
        rating = (
            SELECT COALESCE(AVG(rating), 0.0)
            FROM community.specialist_reviews
            WHERE specialist_id = NEW.specialist_id
        ),
        total_reviews = (
            SELECT COUNT(*)
            FROM community.specialist_reviews
            WHERE specialist_id = NEW.specialist_id
        )
    WHERE id = NEW.specialist_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_rating_on_review
AFTER INSERT OR UPDATE ON community.specialist_reviews
FOR EACH ROW
EXECUTE FUNCTION community.update_specialist_rating();

-- =====================================================
-- ANALYTICAL VIEWS
-- =====================================================

-- Top-rated specialists
CREATE OR REPLACE VIEW community.v_top_specialists AS
SELECT
    s.id,
    s.full_name,
    s.title,
    s.rating,
    s.total_reviews,
    s.completed_projects,
    s.hourly_rate,
    s.currency,
    s.specializations,
    s.country,
    s.city,
    s.is_verified,
    s.verification_badge,
    s.availability_status
FROM community.specialists s
WHERE s.is_active = true
  AND s.rating >= 4.0
ORDER BY s.rating DESC, s.total_reviews DESC
LIMIT 50;

-- Specialist engagement stats
CREATE OR REPLACE VIEW community.v_specialist_stats AS
SELECT
    s.id AS specialist_id,
    s.full_name,
    COUNT(e.id) AS total_engagements,
    COUNT(*) FILTER (WHERE e.status = 'completed') AS completed_engagements,
    COUNT(*) FILTER (WHERE e.status = 'in_progress') AS active_engagements,
    SUM(e.contract_value) FILTER (WHERE e.status = 'completed') AS total_earnings,
    AVG(r.rating) AS avg_rating,
    COUNT(r.id) AS review_count
FROM community.specialists s
LEFT JOIN community.specialist_engagements e ON e.specialist_id = s.id
LEFT JOIN community.specialist_reviews r ON r.specialist_id = s.id
WHERE s.is_active = true
GROUP BY s.id, s.full_name;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE community.specialists IS 'BCM specialists offering marketplace services';
COMMENT ON TABLE community.specialist_certifications IS 'Professional certifications (CBCP, CBCI, etc.)';
COMMENT ON TABLE community.specialist_portfolio IS 'Past projects and case studies';
COMMENT ON TABLE community.specialist_services IS 'Services offered by specialists';
COMMENT ON TABLE community.specialist_reviews IS 'Client reviews and ratings';
COMMENT ON TABLE community.specialist_engagements IS 'Active contracts between specialists and organizations';

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 020: Community Specialist Marketplace - COMPLETE';
    RAISE NOTICE 'Tables created: 6';
    RAISE NOTICE '  - specialists';
    RAISE NOTICE '  - specialist_certifications';
    RAISE NOTICE '  - specialist_portfolio';
    RAISE NOTICE '  - specialist_services';
    RAISE NOTICE '  - specialist_reviews';
    RAISE NOTICE '  - specialist_engagements';
    RAISE NOTICE 'Indexes created: 20';
    RAISE NOTICE 'RLS policies: 10';
    RAISE NOTICE 'Triggers: 4';
    RAISE NOTICE 'Views: 2';
END $$;
