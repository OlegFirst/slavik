-- SEH Phase 3 & 4: Business Continuity Management (BCM) and Proof of Impact (PoI)
-- Migration for resilience planning and impact verification
-- Version: 1.0.0
-- Date: 2025-08-16

-- ================== PHASE 3: BCM ENHANCEMENT ==================

-- BCM Scenarios table (business continuity scenarios)
CREATE TABLE IF NOT EXISTS bcm_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organization_profiles(id) ON DELETE CASCADE,
    scenario_name VARCHAR(255) NOT NULL,
    scenario_type VARCHAR(100) NOT NULL, -- natural_disaster, pandemic, cyber_attack, funding_loss, key_person_loss
    description TEXT,
    probability VARCHAR(50), -- very_low, low, medium, high, very_high
    impact_level VARCHAR(50), -- minimal, minor, moderate, major, catastrophic
    rto_hours INTEGER NOT NULL, -- Recovery Time Objective (max downtime)
    rpo_hours INTEGER NOT NULL, -- Recovery Point Objective (max data loss)
    critical_functions JSONB DEFAULT '[]', -- ["service_delivery", "payroll", "donor_communications"]
    dependencies JSONB DEFAULT '{}', -- {"it_systems": ["crm", "email"], "suppliers": ["vendor1"], "facilities": ["main_office"]}
    impact_assessment JSONB DEFAULT '{}', -- {"financial": 100000, "beneficiaries_affected": 500, "reputation": "high"}
    mitigation_strategies JSONB DEFAULT '[]',
    recovery_strategies JSONB DEFAULT '[]',
    minimum_resources JSONB DEFAULT '{}', -- {"staff": 10, "budget": 50000, "equipment": ["laptops", "phones"]}
    alternate_locations JSONB DEFAULT '[]',
    communication_plan JSONB DEFAULT '{}',
    escalation_matrix JSONB DEFAULT '[]', -- [{"level": 1, "role": "program_manager", "threshold": "1_hour"}]
    last_review_date DATE,
    next_review_date DATE,
    owner_id UUID,
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, testing, archived
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_rto_rpo CHECK (rto_hours >= 0 AND rpo_hours >= 0)
);

-- BCM Tests table (testing and validation)
CREATE TABLE IF NOT EXISTS bcm_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES bcm_scenarios(id) ON DELETE CASCADE,
    test_type VARCHAR(50) NOT NULL, -- tabletop, simulation, full_test
    test_name VARCHAR(255) NOT NULL,
    test_date TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_hours DECIMAL(5,2),
    participants JSONB DEFAULT '[]', -- [{"name": "John Doe", "role": "coordinator"}]
    objectives JSONB DEFAULT '[]',
    success_criteria JSONB DEFAULT '[]',
    test_scenario TEXT,
    result VARCHAR(50), -- passed, passed_with_issues, failed, incomplete
    actual_rto_hours DECIMAL(10,2),
    actual_rpo_hours DECIMAL(10,2),
    weaknesses_identified JSONB DEFAULT '[]',
    strengths_identified JSONB DEFAULT '[]',
    improvements_required JSONB DEFAULT '[]',
    lessons_learned TEXT,
    evidence_refs JSONB DEFAULT '[]', -- ["test_report.pdf", "photos/drill_photo1.jpg"]
    follow_up_actions JSONB DEFAULT '[]',
    next_test_date DATE,
    report_url TEXT,
    approved_by UUID,
    approval_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- BCM Incidents table (actual incidents and response)
CREATE TABLE IF NOT EXISTS bcm_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES bcm_scenarios(id),
    incident_type VARCHAR(100) NOT NULL,
    incident_name VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL, -- low, medium, high, critical
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    reported_by UUID,
    initial_assessment TEXT,
    activation_decision VARCHAR(50), -- activate_bcp, monitor, resolved
    activation_time TIMESTAMP WITH TIME ZONE,
    response_team JSONB DEFAULT '[]',
    affected_services JSONB DEFAULT '[]',
    affected_beneficiaries INTEGER,
    timeline JSONB DEFAULT '[]', -- [{"time": "2025-01-01T10:00:00", "action": "BCP activated"}]
    actual_downtime_hours DECIMAL(10,2),
    data_loss_assessment TEXT,
    financial_impact DECIMAL(15,2),
    recovery_completed_at TIMESTAMP WITH TIME ZONE,
    root_cause TEXT,
    corrective_actions JSONB DEFAULT '[]',
    preventive_actions JSONB DEFAULT '[]',
    post_incident_review TEXT,
    status VARCHAR(50) DEFAULT 'active', -- active, contained, recovering, resolved, closed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ================== PHASE 4: PROOF OF IMPACT ==================

-- PoI Claims table (impact claims to be verified)
CREATE TABLE IF NOT EXISTS poi_claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_id UUID REFERENCES indicators(id) ON DELETE CASCADE,
    measurement_id UUID REFERENCES measurements(id),
    claim_type VARCHAR(50) NOT NULL, -- outcome_achieved, milestone_reached, target_exceeded
    claim_period_start DATE NOT NULL,
    claim_period_end DATE NOT NULL,
    claimed_value DECIMAL(15,4) NOT NULL,
    baseline_value DECIMAL(15,4),
    target_value DECIMAL(15,4),
    impact_description TEXT NOT NULL,
    beneficiaries_count INTEGER,
    geographic_scope VARCHAR(255),
    methodology TEXT,
    data_sources JSONB DEFAULT '[]',
    assumptions JSONB DEFAULT '[]',
    limitations TEXT,
    evidence_package JSONB DEFAULT '[]', -- [{"type": "report", "url": "...", "hash": "..."}]
    evidence_hash VARCHAR(255) NOT NULL, -- Combined hash of all evidence
    submitter_id UUID NOT NULL,
    submission_date TIMESTAMP WITH TIME ZONE NOT NULL,
    organization_signature JSONB, -- {"signer": "CEO", "timestamp": "...", "hash": "..."}
    claim_value_usd DECIMAL(15,2), -- Monetary value of impact
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, under_verification, verified, disputed, rejected
    blockchain_tx_id VARCHAR(255), -- If using blockchain
    public_url TEXT, -- Public verification page
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_claim_period CHECK (claim_period_end >= claim_period_start)
);

-- PoI Verifications table (verification of claims)
CREATE TABLE IF NOT EXISTS poi_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES poi_claims(id) ON DELETE CASCADE,
    verifier_id UUID NOT NULL,
    verifier_type VARCHAR(50) NOT NULL, -- internal, external_auditor, peer_org, automated
    verifier_organization VARCHAR(255),
    verification_method VARCHAR(100) NOT NULL, -- document_review, site_visit, data_analysis, beneficiary_survey
    verification_date TIMESTAMP WITH TIME ZONE NOT NULL,
    verification_result VARCHAR(50) NOT NULL, -- verified, partially_verified, not_verified, inconclusive
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    verified_value DECIMAL(15,4),
    variance_from_claim DECIMAL(10,2), -- Percentage difference
    findings TEXT,
    evidence_reviewed JSONB DEFAULT '[]',
    sampling_method TEXT,
    sample_size INTEGER,
    margin_of_error DECIMAL(5,2),
    recommendations TEXT,
    verification_evidence JSONB DEFAULT '[]', -- Verifier's own evidence
    verification_hash VARCHAR(255), -- Hash of verification data
    challenges_noted TEXT,
    follow_up_required BOOLEAN DEFAULT false,
    public_attestation BOOLEAN DEFAULT false,
    attestation_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))
);

-- Ledger Entries table (immutable audit trail)
CREATE TABLE IF NOT EXISTS ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_type VARCHAR(50) NOT NULL, -- claim_submitted, verification_completed, evidence_added, dispute_raised
    entry_ref_id UUID NOT NULL, -- Reference to claim, verification, etc.
    entry_data JSONB NOT NULL, -- Core data being recorded
    hash VARCHAR(255) NOT NULL, -- SHA-256 of entry_data
    previous_hash VARCHAR(255), -- Hash of previous entry (blockchain-style)
    block_number BIGSERIAL UNIQUE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    signed_by UUID,
    signature VARCHAR(500), -- Digital signature if applicable
    merkle_root VARCHAR(255), -- For batch verification
    consensus_proof JSONB, -- If using consensus mechanism
    ipfs_hash VARCHAR(255), -- If storing in IPFS
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT immutable_ledger CHECK (false) NO INHERIT -- Prevents updates
);

-- Create function to prevent ledger updates
CREATE OR REPLACE FUNCTION prevent_ledger_update() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Ledger entries are immutable and cannot be updated or deleted';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_ledger_updates
    BEFORE UPDATE OR DELETE ON ledger_entries
    FOR EACH ROW EXECUTE FUNCTION prevent_ledger_update();

-- PoI Disputes table (challenges to claims)
CREATE TABLE IF NOT EXISTS poi_disputes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES poi_claims(id) ON DELETE CASCADE,
    verification_id UUID REFERENCES poi_verifications(id),
    raised_by UUID NOT NULL,
    raised_by_org VARCHAR(255),
    dispute_type VARCHAR(50) NOT NULL, -- methodology, data_quality, calculation_error, fraud
    dispute_description TEXT NOT NULL,
    supporting_evidence JSONB DEFAULT '[]',
    requested_action VARCHAR(100), -- re_verify, adjust_value, reject_claim
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, critical
    assigned_to UUID,
    investigation_notes TEXT,
    resolution VARCHAR(100), -- upheld, rejected, partially_upheld, settled
    resolution_date DATE,
    resolution_details TEXT,
    adjusted_value DECIMAL(15,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- PoI Certificates table (final impact certificates)
CREATE TABLE IF NOT EXISTS poi_certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES poi_claims(id) ON DELETE CASCADE,
    certificate_number VARCHAR(100) UNIQUE NOT NULL,
    issue_date DATE NOT NULL,
    issuer_organization VARCHAR(255) NOT NULL,
    impact_summary TEXT NOT NULL,
    verified_value DECIMAL(15,4) NOT NULL,
    value_unit VARCHAR(100) NOT NULL,
    beneficiaries_served INTEGER,
    sdg_alignment JSONB DEFAULT '[]', -- ["SDG1", "SDG4"]
    validity_period_months INTEGER,
    expires_at DATE,
    certificate_url TEXT,
    qr_code TEXT, -- For verification
    blockchain_cert_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    revoked BOOLEAN DEFAULT false,
    revocation_date DATE,
    revocation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_bcm_scenarios_org ON bcm_scenarios(organization_id);
CREATE INDEX idx_bcm_scenarios_type ON bcm_scenarios(scenario_type);
CREATE INDEX idx_bcm_scenarios_status ON bcm_scenarios(status);
CREATE INDEX idx_bcm_tests_scenario ON bcm_tests(scenario_id);
CREATE INDEX idx_bcm_tests_date ON bcm_tests(test_date);
CREATE INDEX idx_bcm_incidents_scenario ON bcm_incidents(scenario_id);
CREATE INDEX idx_bcm_incidents_severity ON bcm_incidents(severity);
CREATE INDEX idx_bcm_incidents_status ON bcm_incidents(status);
CREATE INDEX idx_poi_claims_indicator ON poi_claims(indicator_id);
CREATE INDEX idx_poi_claims_status ON poi_claims(status);
CREATE INDEX idx_poi_claims_period ON poi_claims(claim_period_start, claim_period_end);
CREATE INDEX idx_poi_verifications_claim ON poi_verifications(claim_id);
CREATE INDEX idx_poi_verifications_result ON poi_verifications(verification_result);
CREATE INDEX idx_ledger_entries_type ON ledger_entries(entry_type);
CREATE INDEX idx_ledger_entries_ref ON ledger_entries(entry_ref_id);
CREATE INDEX idx_ledger_entries_block ON ledger_entries(block_number);
CREATE INDEX idx_poi_disputes_claim ON poi_disputes(claim_id);
CREATE INDEX idx_poi_disputes_status ON poi_disputes(resolution);
CREATE INDEX idx_poi_certificates_claim ON poi_certificates(claim_id);
CREATE INDEX idx_poi_certificates_number ON poi_certificates(certificate_number);

-- Add RLS policies
ALTER TABLE bcm_scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE poi_claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE poi_verifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE ledger_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE poi_disputes ENABLE ROW LEVEL SECURITY;
ALTER TABLE poi_certificates ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies
CREATE POLICY "Organizations manage their BCM" ON bcm_scenarios
    FOR ALL USING (
        organization_id IN (
            SELECT id FROM organization_profiles 
            WHERE pgpx_subject_id = auth.uid()
        )
    );

CREATE POLICY "Public can view verified claims" ON poi_claims
    FOR SELECT USING (status = 'verified' OR submitter_id = auth.uid());

CREATE POLICY "Public can view ledger" ON ledger_entries
    FOR SELECT USING (true);

-- Add update triggers
CREATE TRIGGER update_bcm_scenarios_updated_at BEFORE UPDATE ON bcm_scenarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_tests_updated_at BEFORE UPDATE ON bcm_tests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bcm_incidents_updated_at BEFORE UPDATE ON bcm_incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_poi_claims_updated_at BEFORE UPDATE ON poi_claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_poi_verifications_updated_at BEFORE UPDATE ON poi_verifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_poi_disputes_updated_at BEFORE UPDATE ON poi_disputes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_poi_certificates_updated_at BEFORE UPDATE ON poi_certificates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE bcm_scenarios IS 'Business continuity scenarios for resilience planning';
COMMENT ON TABLE bcm_tests IS 'BCM testing and validation records';
COMMENT ON TABLE bcm_incidents IS 'Actual incidents and recovery tracking';
COMMENT ON TABLE poi_claims IS 'Impact claims submitted for verification';
COMMENT ON TABLE poi_verifications IS 'Independent verification of impact claims';
COMMENT ON TABLE ledger_entries IS 'Immutable audit trail for all PoI activities';
COMMENT ON TABLE poi_disputes IS 'Challenges and disputes to impact claims';
COMMENT ON TABLE poi_certificates IS 'Verified impact certificates for proven outcomes';