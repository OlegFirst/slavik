-- Digital Twin Database Schema
-- PostgreSQL initialization script

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain_type VARCHAR(50),
    industry_sector VARCHAR(50),
    annual_budget DECIMAL(15,2),
    staff_count INTEGER,
    bcm_client_id INTEGER,
    health_score DECIMAL(5,2) DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Digital Twins table
CREATE TABLE IF NOT EXISTS digital_twins (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    twin_status VARCHAR(50) DEFAULT 'active',
    twin_config JSONB DEFAULT '{}',
    simulation_results JSONB DEFAULT '{}',
    ai_insights JSONB DEFAULT '{}',
    prediction_models JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Simulations table
CREATE TABLE IF NOT EXISTS simulations (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(100) UNIQUE,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    scenario_type VARCHAR(100),
    parameters JSONB DEFAULT '{}',
    results JSONB DEFAULT '{}',
    confidence_score DECIMAL(5,2),
    state VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Analyses table
CREATE TABLE IF NOT EXISTS ai_analyses (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100),
    organs_used JSONB DEFAULT '[]',
    insights JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '[]',
    confidence_level DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    metric_type VARCHAR(100),
    metric_value DECIMAL(10,2),
    metric_data JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scenarios table
CREATE TABLE IF NOT EXISTS scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    scenario_type VARCHAR(100),
    description TEXT,
    default_parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_organizations_domain ON organizations(domain_type);
CREATE INDEX IF NOT EXISTS idx_organizations_health ON organizations(health_score DESC);
CREATE INDEX IF NOT EXISTS idx_simulations_org ON simulations(organization_id);
CREATE INDEX IF NOT EXISTS idx_simulations_state ON simulations(state);
CREATE INDEX IF NOT EXISTS idx_simulations_type ON simulations(scenario_type);
CREATE INDEX IF NOT EXISTS idx_metrics_org_time ON metrics(organization_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_org ON ai_analyses(organization_id);

-- Insert sample data
INSERT INTO organizations (name, domain_type, industry_sector, annual_budget, staff_count, health_score, description)
VALUES
    ('Hope Foundation International', 'npo', 'charity', 75000000, 350, 91, 'International NPO focused on education and healthcare'),
    ('TechCorp Industries', 'corporate', 'technology', 500000000, 2500, 87, 'Leading technology solutions provider'),
    ('City Emergency Services', 'government', 'emergency', 120000000, 800, 93, 'Municipal emergency response department'),
    ('National Power Grid', 'infrastructure', 'energy', 1500000000, 5000, 89, 'Critical energy infrastructure provider')
ON CONFLICT DO NOTHING;

-- Insert sample scenarios
INSERT INTO scenarios (name, scenario_type, description, default_parameters)
VALUES
    ('Supply Chain Disruption', 'supply_chain_disruption', 'Simulates supply chain interruption impacts', '{"severity": 0.7, "recoveryTimeWeeks": 8, "alternativeSuppliers": 2}'),
    ('Cyber Security Incident', 'cyber_incident', 'Ransomware and data breach scenarios', '{"incidentType": "ransomware", "systemsAffected": 0.6, "recoveryComplexity": "high"}'),
    ('Pandemic Response', 'pandemic_response', 'COVID-like pandemic business continuity', '{"remoteWorkCapacity": 0.7, "durationMonths": 18, "staffAvailability": 0.8}'),
    ('Natural Disaster', 'natural_disaster', 'Earthquake, flood, hurricane impacts', '{"disasterType": "earthquake", "severity": 0.8, "affectedFacilities": 0.5}')
ON CONFLICT DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_digital_twins_updated_at BEFORE UPDATE ON digital_twins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO odoo;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO odoo;