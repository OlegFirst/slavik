-- SEH Phase 1: Core Service Delivery Models
-- Migration for SEH compliance - adds Program/Service/ServiceDelivery/Participant models
-- Version: 1.0.0
-- Date: 2025-08-16

-- Programs table (replaces basic organization structure with detailed program management)
CREATE TABLE IF NOT EXISTS programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organization_profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100) NOT NULL, -- health, education, social_services, environment
    geography JSONB NOT NULL DEFAULT '{}', -- {"country": "US", "state": "CA", "city": "San Francisco", "coverage_area": "Bay Area"}
    start_at DATE NOT NULL,
    end_at DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, paused, completed, cancelled
    budget_allocated DECIMAL(15,2),
    theory_of_change TEXT,
    owner_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_program_dates CHECK (end_at IS NULL OR end_at > start_at),
    CONSTRAINT valid_budget CHECK (budget_allocated >= 0)
);

-- Services table (specific services offered within programs)
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit VARCHAR(50) NOT NULL, -- hour, session, meal, consultation, training
    delivery_mode VARCHAR(50) NOT NULL, -- in-person, remote, hybrid, self-service
    capacity INTEGER, -- max participants per delivery
    cost_per_unit DECIMAL(10,2),
    eligibility_criteria JSONB DEFAULT '{}',
    required_resources JSONB DEFAULT '[]', -- ["trained_staff", "facility", "equipment"]
    kpi_targets JSONB DEFAULT '{}', -- {"completion_rate": 0.8, "satisfaction": 4.5}
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_capacity CHECK (capacity IS NULL OR capacity > 0),
    CONSTRAINT valid_cost CHECK (cost_per_unit IS NULL OR cost_per_unit >= 0)
);

-- Participants table (pseudonymized beneficiaries)
CREATE TABLE IF NOT EXISTS participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_hash VARCHAR(255) UNIQUE NOT NULL, -- SHA-256 of PII for privacy
    cohort VARCHAR(100), -- youth, elderly, veterans, refugees
    vulnerability_tags JSONB DEFAULT '[]', -- ["low_income", "disability", "homeless"]
    enrollment_date DATE NOT NULL,
    exit_date DATE,
    exit_reason VARCHAR(100), -- completed, withdrew, ineligible, transferred
    consent_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, granted, revoked, expired
    consent_date TIMESTAMP WITH TIME ZONE,
    consent_expires_at TIMESTAMP WITH TIME ZONE,
    data_retention_until DATE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_enrollment CHECK (exit_date IS NULL OR exit_date >= enrollment_date),
    CONSTRAINT valid_consent CHECK (
        (consent_status = 'granted' AND consent_date IS NOT NULL) OR
        (consent_status != 'granted')
    )
);

-- Service Deliveries table (actual service instances delivered)
CREATE TABLE IF NOT EXISTS service_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    participant_id UUID REFERENCES participants(id) ON DELETE SET NULL, -- can be null for anonymous
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    delivered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    delivered_by UUID, -- staff/volunteer ID
    location_id UUID,
    location_type VARCHAR(50), -- facility, mobile, remote, participant_home
    attendance_verified BOOLEAN DEFAULT false,
    quality_score DECIMAL(3,2), -- 0.00 to 5.00
    feedback TEXT,
    evidence_urls JSONB DEFAULT '[]', -- ["https://storage/photo1.jpg", "https://storage/signature.pdf"]
    cost_actual DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'completed', -- scheduled, in_progress, completed, cancelled, no_show
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_quantity CHECK (quantity > 0),
    CONSTRAINT valid_quality CHECK (quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 5))
);

-- Outcomes table (hierarchy of results)
CREATE TABLE IF NOT EXISTS outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    parent_outcome_id UUID REFERENCES outcomes(id), -- for outcome hierarchy
    level VARCHAR(20) NOT NULL, -- output, outcome, impact
    name VARCHAR(255) NOT NULL,
    description TEXT,
    theory_of_change TEXT,
    timeframe_months INTEGER, -- expected time to achieve
    target_population VARCHAR(255),
    geographic_scope VARCHAR(255),
    assumptions JSONB DEFAULT '[]',
    risks JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_level CHECK (level IN ('output', 'outcome', 'impact')),
    CONSTRAINT valid_timeframe CHECK (timeframe_months IS NULL OR timeframe_months > 0)
);

-- Indicators table (measurable metrics for outcomes)
CREATE TABLE IF NOT EXISTS indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outcome_id UUID REFERENCES outcomes(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit VARCHAR(50) NOT NULL, -- count, percentage, score, currency
    direction VARCHAR(10) NOT NULL, -- up, down, stable
    frequency VARCHAR(20) NOT NULL, -- daily, weekly, monthly, quarterly, annually
    disaggregation JSONB DEFAULT '[]', -- ["gender", "age_group", "location"]
    data_source VARCHAR(255) NOT NULL, -- survey, admin_data, observation, external_api
    collection_method TEXT,
    calculation_method TEXT,
    baseline_value DECIMAL(15,4),
    baseline_date DATE,
    data_quality_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_direction CHECK (direction IN ('up', 'down', 'stable'))
);

-- Targets table (specific goals for indicators)
CREATE TABLE IF NOT EXISTS targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_id UUID REFERENCES indicators(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    target_value DECIMAL(15,4) NOT NULL,
    geography VARCHAR(255),
    cohort VARCHAR(100),
    justification TEXT,
    stretch_value DECIMAL(15,4), -- aspirational target
    minimum_value DECIMAL(15,4), -- minimum acceptable
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_period CHECK (period_end > period_start),
    CONSTRAINT valid_targets CHECK (
        (stretch_value IS NULL OR stretch_value >= target_value) AND
        (minimum_value IS NULL OR minimum_value <= target_value)
    )
);

-- Measurements table (actual measured values)
CREATE TABLE IF NOT EXISTS measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_id UUID REFERENCES indicators(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    measured_value DECIMAL(15,4) NOT NULL,
    target_id UUID REFERENCES targets(id), -- link to relevant target
    confidence DECIMAL(3,2) NOT NULL DEFAULT 0.95, -- 0.00 to 1.00
    sample_size INTEGER,
    margin_of_error DECIMAL(10,4),
    data_collection_method VARCHAR(255),
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    collector_id UUID,
    verification_status VARCHAR(50) DEFAULT 'pending', -- pending, verified, disputed
    evidence_ref VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_confidence CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT valid_period CHECK (period_end >= period_start),
    CONSTRAINT valid_sample CHECK (sample_size IS NULL OR sample_size > 0)
);

-- Evidence table (supporting documentation)
CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ref_type VARCHAR(50) NOT NULL, -- measurement, service_delivery, outcome, grant
    ref_id UUID NOT NULL,
    evidence_type VARCHAR(50) NOT NULL, -- photo, document, video, signature, report
    uri TEXT NOT NULL, -- storage location
    media_hash VARCHAR(255), -- SHA-256 for integrity
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    captured_at TIMESTAMP WITH TIME ZONE,
    captured_by UUID,
    location_gps JSONB, -- {"lat": 37.7749, "lng": -122.4194}
    qa_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, flagged
    qa_reviewer_id UUID,
    qa_review_date TIMESTAMP WITH TIME ZONE,
    qa_notes TEXT,
    retention_until DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_file_size CHECK (file_size_bytes IS NULL OR file_size_bytes > 0)
);

-- Create indexes for performance
CREATE INDEX idx_programs_org ON programs(organization_id);
CREATE INDEX idx_programs_status ON programs(status);
CREATE INDEX idx_programs_domain ON programs(domain);
CREATE INDEX idx_services_program ON services(program_id);
CREATE INDEX idx_services_status ON services(status);
CREATE INDEX idx_participants_cohort ON participants(cohort);
CREATE INDEX idx_participants_consent ON participants(consent_status);
CREATE INDEX idx_service_deliveries_service ON service_deliveries(service_id);
CREATE INDEX idx_service_deliveries_participant ON service_deliveries(participant_id);
CREATE INDEX idx_service_deliveries_date ON service_deliveries(delivered_at);
CREATE INDEX idx_outcomes_program ON outcomes(program_id);
CREATE INDEX idx_outcomes_level ON outcomes(level);
CREATE INDEX idx_indicators_outcome ON indicators(outcome_id);
CREATE INDEX idx_targets_indicator ON targets(indicator_id);
CREATE INDEX idx_targets_period ON targets(period_start, period_end);
CREATE INDEX idx_measurements_indicator ON measurements(indicator_id);
CREATE INDEX idx_measurements_period ON measurements(period_start, period_end);
CREATE INDEX idx_evidence_ref ON evidence(ref_type, ref_id);
CREATE INDEX idx_evidence_qa ON evidence(qa_status);

-- Add RLS policies for security
ALTER TABLE programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (expand based on your auth model)
CREATE POLICY "Users can view their organization's programs" ON programs
    FOR SELECT USING (auth.uid() IS NOT NULL);

CREATE POLICY "Users can view services" ON services
    FOR SELECT USING (auth.uid() IS NOT NULL);

CREATE POLICY "Protect participant privacy" ON participants
    FOR ALL USING (
        auth.uid() IN (
            SELECT owner_id FROM programs p
            JOIN services s ON s.program_id = p.id
            JOIN service_deliveries sd ON sd.service_id = s.id
            WHERE sd.participant_id = participants.id
        )
    );

-- Add update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_participants_updated_at BEFORE UPDATE ON participants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_service_deliveries_updated_at BEFORE UPDATE ON service_deliveries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_outcomes_updated_at BEFORE UPDATE ON outcomes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_indicators_updated_at BEFORE UPDATE ON indicators
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_targets_updated_at BEFORE UPDATE ON targets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_measurements_updated_at BEFORE UPDATE ON measurements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE programs IS 'SEH-compliant programs table for NPO service delivery tracking';
COMMENT ON TABLE services IS 'Specific services offered within programs';
COMMENT ON TABLE participants IS 'Pseudonymized beneficiaries with GDPR-compliant consent tracking';
COMMENT ON TABLE service_deliveries IS 'Actual instances of services delivered to participants';
COMMENT ON TABLE outcomes IS 'Hierarchical results framework (output/outcome/impact)';
COMMENT ON TABLE indicators IS 'Measurable metrics for tracking outcome achievement';
COMMENT ON TABLE targets IS 'Specific goals for indicators over time periods';
COMMENT ON TABLE measurements IS 'Actual measured values with confidence intervals';
COMMENT ON TABLE evidence IS 'Supporting documentation with integrity verification';