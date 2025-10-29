-- SEH Canonical Data Model for Digital Twin Integration
-- Version: 1.0
-- Date: 2025-08-16

-- ============================================
-- PROGRAMS & SERVICES
-- ============================================

CREATE TABLE IF NOT EXISTS programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organization_profiles(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    budget_total DECIMAL(15,2),
    budget_spent DECIMAL(15,2) DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    service_type VARCHAR(100),
    delivery_method VARCHAR(50), -- in-person, remote, hybrid
    capacity_per_day INTEGER,
    average_duration_minutes INTEGER,
    cost_per_delivery DECIMAL(10,2),
    eligibility_criteria JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- PARTICIPANTS & SERVICE DELIVERY
-- ============================================

CREATE TABLE IF NOT EXISTS participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organization_profiles(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    participant_code VARCHAR(100) UNIQUE NOT NULL, -- Pseudonymized ID
    enrollment_date DATE,
    exit_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    demographics JSONB DEFAULT '{}', -- Aggregated/non-PII data
    needs_assessment JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS service_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    participant_id UUID REFERENCES participants(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    delivery_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    duration_minutes INTEGER,
    delivery_status VARCHAR(50) DEFAULT 'completed', -- scheduled, completed, cancelled, no-show
    delivery_location VARCHAR(255),
    delivered_by VARCHAR(255), -- Staff member or system
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- OUTCOMES & MEASUREMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    outcome_type VARCHAR(50), -- short-term, medium-term, long-term, impact
    theory_of_change_node VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outcome_id UUID REFERENCES outcomes(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit_of_measure VARCHAR(100),
    data_source VARCHAR(255),
    collection_frequency VARCHAR(50), -- daily, weekly, monthly, quarterly, annual
    disaggregation_dimensions JSONB DEFAULT '[]', -- age, gender, location, etc.
    calculation_method TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_id UUID REFERENCES indicators(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    target_value DECIMAL(15,4) NOT NULL,
    stretch_target_value DECIMAL(15,4),
    minimum_acceptable DECIMAL(15,4),
    justification TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(indicator_id, period_start, period_end)
);

CREATE TABLE IF NOT EXISTS measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_id UUID REFERENCES indicators(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    value DECIMAL(15,4) NOT NULL,
    disaggregation JSONB DEFAULT '{}', -- Breakdown by dimensions
    data_quality_score DECIMAL(3,2) CHECK (data_quality_score >= 0 AND data_quality_score <= 1),
    confidence_level DECIMAL(3,2) CHECK (confidence_level >= 0 AND confidence_level <= 1),
    verification_status VARCHAR(50) DEFAULT 'pending', -- pending, verified, disputed
    verified_by VARCHAR(255),
    verified_at TIMESTAMPTZ,
    notes TEXT,
    evidence_ids UUID[] DEFAULT ARRAY[]::UUID[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- EVIDENCE & DOCUMENTATION
-- ============================================

CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    measurement_id UUID REFERENCES measurements(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    evidence_type VARCHAR(50), -- document, photo, video, data_export, system_log
    file_url TEXT,
    file_hash VARCHAR(64), -- SHA-256 for integrity
    description TEXT,
    collected_date DATE,
    collected_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- GRANTS & FUNDING
-- ============================================

CREATE TABLE IF NOT EXISTS funding_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organization_profiles(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    total_budget DECIMAL(15,2),
    available_budget DECIMAL(15,2),
    start_date DATE,
    end_date DATE,
    eligibility_criteria JSONB DEFAULT '{}',
    application_process JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS grant_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funding_program_id UUID REFERENCES funding_programs(id) ON DELETE CASCADE,
    applicant_organization_id UUID REFERENCES organization_profiles(id),
    external_id VARCHAR(255) UNIQUE,
    application_date DATE NOT NULL,
    requested_amount DECIMAL(15,2) NOT NULL,
    project_title VARCHAR(255),
    project_description TEXT,
    status VARCHAR(50) DEFAULT 'submitted', -- submitted, under_review, approved, rejected, withdrawn
    review_notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS grant_awards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID REFERENCES grant_applications(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    award_date DATE NOT NULL,
    awarded_amount DECIMAL(15,2) NOT NULL,
    award_period_start DATE,
    award_period_end DATE,
    payment_schedule JSONB DEFAULT '[]', -- Array of disbursement plans
    performance_conditions JSONB DEFAULT '[]',
    reporting_requirements JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS disbursements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_award_id UUID REFERENCES grant_awards(id) ON DELETE CASCADE,
    external_id VARCHAR(255) UNIQUE,
    disbursement_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    tranche_number INTEGER,
    payment_method VARCHAR(50),
    transaction_reference VARCHAR(255),
    conditions_met JSONB DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reporting_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_award_id UUID REFERENCES grant_awards(id) ON DELETE CASCADE,
    report_type VARCHAR(50), -- financial, narrative, impact, audit
    due_date DATE NOT NULL,
    submitted_date DATE,
    status VARCHAR(50) DEFAULT 'pending', -- pending, submitted, approved, rejected, overdue
    report_url TEXT,
    feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- BUSINESS CONTINUITY MANAGEMENT (BCM)
-- ============================================

CREATE TABLE IF NOT EXISTS bcm_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organization_profiles(id) ON DELETE CASCADE,
    scenario_name VARCHAR(255) NOT NULL,
    scenario_type VARCHAR(50), -- natural_disaster, cyber_attack, pandemic, power_outage, etc.
    description TEXT,
    probability VARCHAR(20), -- very_low, low, medium, high, very_high
    impact_level VARCHAR(20), -- minimal, minor, moderate, major, catastrophic
    rto_hours INTEGER, -- Recovery Time Objective
    rpo_hours INTEGER, -- Recovery Point Objective
    critical_functions JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '[]',
    mitigation_strategies JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bcm_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES bcm_scenarios(id) ON DELETE CASCADE,
    test_date DATE NOT NULL,
    test_type VARCHAR(50), -- tabletop, simulation, full_interruption
    participants JSONB DEFAULT '[]',
    objectives JSONB DEFAULT '[]',
    results JSONB DEFAULT '{}',
    actual_rto_hours DECIMAL(10,2),
    actual_rpo_hours DECIMAL(10,2),
    issues_identified JSONB DEFAULT '[]',
    lessons_learned TEXT,
    improvement_actions JSONB DEFAULT '[]',
    test_status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, completed, cancelled
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- CONSENT MANAGEMENT
-- ============================================

CREATE TABLE IF NOT EXISTS consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID REFERENCES participants(id) ON DELETE CASCADE,
    consent_type VARCHAR(50) NOT NULL, -- data_processing, marketing, research, sharing
    consent_given BOOLEAN NOT NULL,
    consent_date TIMESTAMPTZ NOT NULL,
    expiry_date DATE,
    withdrawal_date TIMESTAMPTZ,
    consent_method VARCHAR(50), -- written, verbal, electronic
    consent_version VARCHAR(20),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(participant_id, consent_type, consent_date)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_programs_org ON programs(organization_id);
CREATE INDEX idx_programs_status ON programs(status);
CREATE INDEX idx_services_program ON services(program_id);
CREATE INDEX idx_service_deliveries_service ON service_deliveries(service_id);
CREATE INDEX idx_service_deliveries_participant ON service_deliveries(participant_id);
CREATE INDEX idx_service_deliveries_date ON service_deliveries(delivery_date);
CREATE INDEX idx_participants_org ON participants(organization_id);
CREATE INDEX idx_participants_status ON participants(status);
CREATE INDEX idx_outcomes_program ON outcomes(program_id);
CREATE INDEX idx_indicators_outcome ON indicators(outcome_id);
CREATE INDEX idx_targets_indicator ON targets(indicator_id);
CREATE INDEX idx_measurements_indicator ON measurements(indicator_id);
CREATE INDEX idx_measurements_period ON measurements(period_start, period_end);
CREATE INDEX idx_evidence_measurement ON evidence(measurement_id);
CREATE INDEX idx_grant_awards_application ON grant_awards(application_id);
CREATE INDEX idx_disbursements_award ON disbursements(grant_award_id);
CREATE INDEX idx_disbursements_date ON disbursements(disbursement_date);
CREATE INDEX idx_bcm_tests_scenario ON bcm_tests(scenario_id);
CREATE INDEX idx_consents_participant ON consents(participant_id);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

ALTER TABLE programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE funding_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE grant_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE grant_awards ENABLE ROW LEVEL SECURITY;
ALTER TABLE disbursements ENABLE ROW LEVEL SECURITY;
ALTER TABLE reporting_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE consents ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (adjust based on your auth model)
CREATE POLICY "Organizations can manage their own programs"
    ON programs FOR ALL
    USING (organization_id IN (
        SELECT id FROM organization_profiles 
        WHERE auth_user_id = auth.uid()
    ));

-- Add similar policies for other tables...

-- ============================================
-- TRIGGER FUNCTIONS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to relevant tables
CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_participants_updated_at BEFORE UPDATE ON participants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
-- Add more triggers as needed...

-- ============================================
-- DOMAIN EVENTS (for CDC/webhooks)
-- ============================================

CREATE TABLE IF NOT EXISTS domain_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_domain_events_type ON domain_events(event_type);
CREATE INDEX idx_domain_events_aggregate ON domain_events(aggregate_type, aggregate_id);
CREATE INDEX idx_domain_events_created ON domain_events(created_at);

-- Function to emit domain events
CREATE OR REPLACE FUNCTION emit_domain_event()
RETURNS TRIGGER AS $$
DECLARE
    event_type TEXT;
    aggregate_type TEXT;
BEGIN
    -- Determine event type based on operation and table
    aggregate_type := TG_TABLE_NAME;
    
    IF TG_OP = 'INSERT' THEN
        event_type := aggregate_type || '.created';
    ELSIF TG_OP = 'UPDATE' THEN
        event_type := aggregate_type || '.updated';
    ELSIF TG_OP = 'DELETE' THEN
        event_type := aggregate_type || '.deleted';
    END IF;
    
    -- Special event types for specific tables
    IF TG_TABLE_NAME = 'measurements' AND TG_OP = 'INSERT' THEN
        event_type := 'indicator.measured';
    ELSIF TG_TABLE_NAME = 'service_deliveries' AND TG_OP = 'INSERT' THEN
        event_type := 'service.delivery.recorded';
    ELSIF TG_TABLE_NAME = 'disbursements' AND TG_OP = 'INSERT' THEN
        event_type := 'grant.disbursement.made';
    ELSIF TG_TABLE_NAME = 'bcm_tests' AND NEW.test_status = 'completed' THEN
        event_type := 'bcm.test.completed';
    END IF;
    
    -- Insert event
    INSERT INTO domain_events (event_type, aggregate_id, aggregate_type, payload, metadata)
    VALUES (
        event_type,
        CASE WHEN TG_OP = 'DELETE' THEN OLD.id ELSE NEW.id END,
        aggregate_type,
        to_jsonb(CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END),
        jsonb_build_object(
            'operation', TG_OP,
            'table', TG_TABLE_NAME,
            'schema', TG_TABLE_SCHEMA
        )
    );
    
    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$ LANGUAGE plpgsql;

-- Attach event triggers to key tables
CREATE TRIGGER emit_measurement_events
    AFTER INSERT OR UPDATE ON measurements
    FOR EACH ROW EXECUTE FUNCTION emit_domain_event();

CREATE TRIGGER emit_service_delivery_events
    AFTER INSERT ON service_deliveries
    FOR EACH ROW EXECUTE FUNCTION emit_domain_event();

CREATE TRIGGER emit_disbursement_events
    AFTER INSERT ON disbursements
    FOR EACH ROW EXECUTE FUNCTION emit_domain_event();

CREATE TRIGGER emit_bcm_test_events
    AFTER UPDATE ON bcm_tests
    FOR EACH ROW 
    WHEN (NEW.test_status = 'completed' AND OLD.test_status != 'completed')
    EXECUTE FUNCTION emit_domain_event();