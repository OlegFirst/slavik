-- ========================================
-- Impact Passport and Validation Tables
-- ========================================

-- Table for Impact Passports
CREATE TABLE IF NOT EXISTS impact_passports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passport_id VARCHAR(255) UNIQUE NOT NULL,
    organization_id UUID NOT NULL REFERENCES organization_profiles(id) ON DELETE CASCADE,
    passport_data JSONB NOT NULL DEFAULT '{}',
    
    -- Key metrics for quick queries
    reputation_score DECIMAL(3,2) DEFAULT 0 CHECK (reputation_score >= 0 AND reputation_score <= 1),
    reputation_level VARCHAR(50) DEFAULT 'newcomer',
    total_simulations INTEGER DEFAULT 0,
    validated_simulations INTEGER DEFAULT 0,
    average_prediction_accuracy DECIMAL(3,2) DEFAULT 0,
    impact_score DECIMAL(5,2) DEFAULT 0,
    
    -- Verifiable credentials
    verification_code VARCHAR(255),
    public_key TEXT,
    
    -- IPS integration
    ips_passport_id VARCHAR(255),
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'revoked')),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '1 year')
);

-- Table for Simulation Validations
CREATE TABLE IF NOT EXISTS simulation_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id VARCHAR(255) NOT NULL,
    organization_id UUID NOT NULL REFERENCES organization_profiles(id) ON DELETE CASCADE,
    twin_id UUID REFERENCES digital_twins(id) ON DELETE SET NULL,
    
    -- Validation details
    predictions JSONB NOT NULL DEFAULT '{}',
    evidence JSONB DEFAULT '{}',
    validation_result JSONB DEFAULT '{}',
    accuracy_metrics JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending_evidence' 
        CHECK (status IN ('pending_evidence', 'collecting', 'validating', 'validated', 'rejected', 'provisional')),
    
    -- Validation contract (if using IPS)
    contract_id VARCHAR(255),
    
    -- Certificate
    impact_certificate JSONB,
    
    -- Timestamps
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    scheduled_validation TIMESTAMPTZ,
    validated_at TIMESTAMPTZ,
    
    -- Scores
    validation_score DECIMAL(3,2) CHECK (validation_score >= 0 AND validation_score <= 1),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Table for Passport Achievements
CREATE TABLE IF NOT EXISTS passport_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passport_id UUID NOT NULL REFERENCES impact_passports(id) ON DELETE CASCADE,
    achievement_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(passport_id, achievement_id)
);

-- Table for Passport History (audit trail)
CREATE TABLE IF NOT EXISTS passport_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passport_id UUID NOT NULL REFERENCES impact_passports(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    snapshot JSONB NOT NULL,
    change_type VARCHAR(50),
    change_description TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Validation Evidence
CREATE TABLE IF NOT EXISTS validation_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    validation_id UUID NOT NULL REFERENCES simulation_validations(id) ON DELETE CASCADE,
    evidence_type VARCHAR(100) NOT NULL,
    evidence_source VARCHAR(255),
    evidence_data JSONB NOT NULL DEFAULT '{}',
    evidence_hash VARCHAR(255),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_impact_passports_org_id ON impact_passports(organization_id);
CREATE INDEX IF NOT EXISTS idx_impact_passports_reputation ON impact_passports(reputation_score DESC);
CREATE INDEX IF NOT EXISTS idx_impact_passports_status ON impact_passports(status);
CREATE INDEX IF NOT EXISTS idx_simulation_validations_org_id ON simulation_validations(organization_id);
CREATE INDEX IF NOT EXISTS idx_simulation_validations_status ON simulation_validations(status);
CREATE INDEX IF NOT EXISTS idx_simulation_validations_scheduled ON simulation_validations(scheduled_validation);
CREATE INDEX IF NOT EXISTS idx_passport_achievements_passport ON passport_achievements(passport_id);
CREATE INDEX IF NOT EXISTS idx_validation_evidence_validation ON validation_evidence(validation_id);

-- Row Level Security
ALTER TABLE impact_passports ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation_validations ENABLE ROW LEVEL SECURITY;
ALTER TABLE passport_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE passport_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE validation_evidence ENABLE ROW LEVEL SECURITY;

-- RLS Policies for impact_passports
CREATE POLICY "Public read access to passports"
    ON impact_passports FOR SELECT
    USING (status = 'active');

CREATE POLICY "Organizations can manage own passports"
    ON impact_passports FOR ALL
    USING (organization_id IN (
        SELECT id FROM organization_profiles 
        WHERE user_id = auth.uid()
    ));

-- RLS Policies for simulation_validations
CREATE POLICY "Organizations can view own validations"
    ON simulation_validations FOR SELECT
    USING (organization_id IN (
        SELECT id FROM organization_profiles 
        WHERE user_id = auth.uid()
    ));

CREATE POLICY "Organizations can create validations"
    ON simulation_validations FOR INSERT
    WITH CHECK (organization_id IN (
        SELECT id FROM organization_profiles 
        WHERE user_id = auth.uid()
    ));

-- RLS Policies for achievements
CREATE POLICY "Public read access to achievements"
    ON passport_achievements FOR SELECT
    USING (true);

-- RLS Policies for history
CREATE POLICY "Organizations can view own history"
    ON passport_history FOR SELECT
    USING (passport_id IN (
        SELECT id FROM impact_passports 
        WHERE organization_id IN (
            SELECT id FROM organization_profiles 
            WHERE user_id = auth.uid()
        )
    ));

-- RLS Policies for evidence
CREATE POLICY "Organizations can manage own evidence"
    ON validation_evidence FOR ALL
    USING (validation_id IN (
        SELECT id FROM simulation_validations 
        WHERE organization_id IN (
            SELECT id FROM organization_profiles 
            WHERE user_id = auth.uid()
        )
    ));

-- Function to update passport timestamp
CREATE OR REPLACE FUNCTION update_passport_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for passport updates
CREATE TRIGGER update_impact_passports_timestamp
    BEFORE UPDATE ON impact_passports
    FOR EACH ROW
    EXECUTE FUNCTION update_passport_timestamp();

-- Function to log passport changes
CREATE OR REPLACE FUNCTION log_passport_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO passport_history (
        passport_id,
        version,
        snapshot,
        change_type,
        change_description
    ) VALUES (
        NEW.id,
        '1.0.0',
        to_jsonb(NEW),
        TG_OP,
        CASE 
            WHEN TG_OP = 'INSERT' THEN 'Passport created'
            WHEN TG_OP = 'UPDATE' THEN 'Passport updated'
            WHEN TG_OP = 'DELETE' THEN 'Passport deleted'
        END
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for passport history
CREATE TRIGGER log_impact_passport_changes
    AFTER INSERT OR UPDATE OR DELETE ON impact_passports
    FOR EACH ROW
    EXECUTE FUNCTION log_passport_change();

-- Comments for documentation
COMMENT ON TABLE impact_passports IS 'Stores Impact Passports for organizations with reputation and achievement tracking';
COMMENT ON TABLE simulation_validations IS 'Tracks validation of simulation predictions against real-world evidence';
COMMENT ON TABLE passport_achievements IS 'Achievements earned by organizations based on their impact performance';
COMMENT ON TABLE passport_history IS 'Audit trail of all changes to Impact Passports';
COMMENT ON TABLE validation_evidence IS 'Evidence collected for validating simulation predictions';