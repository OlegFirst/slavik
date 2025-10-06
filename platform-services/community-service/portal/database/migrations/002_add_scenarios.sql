-- ============================================================================
-- Portal Service - Scenario Marketplace Migration
-- ============================================================================
-- Description: Adds scenario catalog and reviews for marketplace
-- Date: 2025-10-02
-- Tables: scenarios, scenario_reviews
-- ============================================================================

-- ============================================================================
-- Table: scenarios
-- ============================================================================

CREATE TABLE portal.scenarios (
    id SERIAL PRIMARY KEY,

    -- Basic Info
    scenario_code VARCHAR(50) UNIQUE NOT NULL,
    scenario_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    -- Type & Category
    scenario_type VARCHAR(50) NOT NULL,  -- 'tabletop', 'functional', 'full_scale'
    industry VARCHAR(100),  -- 'Finance', 'Healthcare', 'Manufacturing'
    threat_type VARCHAR(100),  -- 'Cyber Attack', 'Natural Disaster', 'Pandemic'

    -- Content
    full_scenario TEXT NOT NULL,
    injects JSONB NOT NULL,  -- Array of inject objects
    learning_objectives JSONB NOT NULL,  -- Array of objectives
    duration_minutes INTEGER NOT NULL,

    -- ISO Mapping
    iso_clauses JSONB DEFAULT '[]'::jsonb,

    -- Publishing
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,

    -- Authorship
    created_by VARCHAR(255) NOT NULL,
    author_type VARCHAR(50) NOT NULL,  -- 'specialist', 'admin'

    -- Engagement
    view_count INTEGER DEFAULT 0,
    deployment_count INTEGER DEFAULT 0,
    average_rating FLOAT DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_scenarios_category ON portal.scenarios(scenario_type);
CREATE INDEX idx_scenarios_published ON portal.scenarios(published);
CREATE INDEX idx_scenarios_rating ON portal.scenarios(average_rating DESC);
CREATE INDEX idx_scenarios_deployments ON portal.scenarios(deployment_count DESC);
CREATE INDEX idx_scenarios_industry ON portal.scenarios(industry);
CREATE INDEX idx_scenarios_threat ON portal.scenarios(threat_type);

-- GIN indexes for JSONB
CREATE INDEX idx_scenarios_injects ON portal.scenarios USING GIN (injects);
CREATE INDEX idx_scenarios_iso_clauses ON portal.scenarios USING GIN (iso_clauses);

-- Trigger: auto-update updated_at
CREATE TRIGGER trigger_scenarios_updated_at
    BEFORE UPDATE ON portal.scenarios
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_articles_updated_at();

-- Trigger: auto-set published_at
CREATE OR REPLACE FUNCTION portal.set_scenario_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.published = TRUE AND OLD.published = FALSE THEN
        NEW.published_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_scenario_published_at
    BEFORE UPDATE ON portal.scenarios
    FOR EACH ROW
    EXECUTE FUNCTION portal.set_scenario_published_at();

-- ============================================================================
-- Table: scenario_reviews
-- ============================================================================

CREATE TABLE portal.scenario_reviews (
    id SERIAL PRIMARY KEY,

    -- References
    scenario_id INTEGER NOT NULL REFERENCES portal.scenarios(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,

    -- Review content
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,

    -- Usage context
    exercise_id INTEGER,  -- Reference to exercise where scenario was used

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    UNIQUE(scenario_id, user_id, tenant_id)
);

-- Indexes
CREATE INDEX idx_reviews_scenario ON portal.scenario_reviews(scenario_id);
CREATE INDEX idx_reviews_user ON portal.scenario_reviews(user_id);
CREATE INDEX idx_reviews_rating ON portal.scenario_reviews(rating);

-- Trigger: auto-update updated_at
CREATE TRIGGER trigger_reviews_updated_at
    BEFORE UPDATE ON portal.scenario_reviews
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_articles_updated_at();

-- Trigger: Update scenario average rating when review is inserted/updated/deleted
CREATE OR REPLACE FUNCTION portal.update_scenario_rating()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
        UPDATE portal.scenarios
        SET average_rating = (
            SELECT COALESCE(AVG(rating), 0.0)
            FROM portal.scenario_reviews
            WHERE scenario_id = COALESCE(NEW.scenario_id, OLD.scenario_id)
        ),
        review_count = (
            SELECT COUNT(*)
            FROM portal.scenario_reviews
            WHERE scenario_id = COALESCE(NEW.scenario_id, OLD.scenario_id)
        )
        WHERE id = COALESCE(NEW.scenario_id, OLD.scenario_id);
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_scenario_rating
    AFTER INSERT OR UPDATE OR DELETE ON portal.scenario_reviews
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_scenario_rating();

-- ============================================================================
-- Sample Data - Scenario Templates
-- ============================================================================

-- Cyber Attack Scenario
INSERT INTO portal.scenarios (
    scenario_code, scenario_name, description, scenario_type, industry, threat_type,
    full_scenario, injects, learning_objectives, duration_minutes, iso_clauses,
    created_by, author_type, published
) VALUES (
    'SCN-CYBER-001',
    'Ransomware Attack on Financial Systems',
    'A sophisticated ransomware attack targets the organization''s core financial systems, testing incident response and recovery capabilities.',
    'tabletop',
    'Finance',
    'Cyber Attack',
    '## Scenario Overview
Your organization discovers that critical financial systems have been encrypted by ransomware. The attackers demand payment within 48 hours.

## Initial Situation
- Time: Monday, 08:00 AM
- Discovery: IT team notices unusual file encryption activity
- Impact: Core banking systems, customer databases affected
- Ransom demand: 50 BTC ($2M USD)

## Your Tasks
1. Activate incident response team
2. Assess impact and containment options
3. Decide on communication strategy
4. Evaluate recovery options',
    '[
        {"time": 0, "inject": "Ransomware detected on file server", "expected_action": "Activate incident response team"},
        {"time": 30, "inject": "Second wave detected on backup systems", "expected_action": "Isolate infected systems"},
        {"time": 60, "inject": "Media inquiries received", "expected_action": "Activate communication plan"},
        {"time": 90, "inject": "Ransom deadline approaching", "expected_action": "Make recovery decision"}
    ]'::jsonb,
    '["Test incident response procedures", "Evaluate backup and recovery processes", "Practice stakeholder communication", "Test decision-making under pressure"]'::jsonb,
    120,
    '["8.4", "A.16.1"]'::jsonb,
    'admin-001',
    'admin',
    TRUE
);

-- Natural Disaster Scenario
INSERT INTO portal.scenarios (
    scenario_code, scenario_name, description, scenario_type, industry, threat_type,
    full_scenario, injects, learning_objectives, duration_minutes, iso_clauses,
    created_by, author_type, published
) VALUES (
    'SCN-DISASTER-001',
    'Earthquake Impact on Data Center',
    'A major earthquake strikes near your primary data center, testing your disaster recovery and business continuity plans.',
    'tabletop',
    'Technology',
    'Natural Disaster',
    '## Scenario Overview
A magnitude 7.2 earthquake has struck 50km from your primary data center. Initial reports indicate widespread infrastructure damage.

## Initial Situation
- Time: Tuesday, 14:30 PM
- Event: Major earthquake
- Primary data center: Status unknown, no communication
- Staff: Some injuries reported, evacuation in progress
- Services: All online services down

## Your Tasks
1. Activate business continuity plan
2. Account for all staff
3. Assess facility damage
4. Initiate failover to DR site',
    '[
        {"time": 0, "inject": "Earthquake strikes, communications lost", "expected_action": "Activate emergency response"},
        {"time": 20, "inject": "Reports of structural damage to data center", "expected_action": "Begin DR failover procedures"},
        {"time": 45, "inject": "Customers reporting service outages on social media", "expected_action": "Activate communication plan"},
        {"time": 75, "inject": "DR site capacity at 80%, performance degraded", "expected_action": "Implement load management"}
    ]'::jsonb,
    '["Test disaster recovery procedures", "Validate RTO/RPO targets", "Practice emergency communication", "Test alternate site activation"]'::jsonb,
    90,
    '["8.4", "8.5", "A.17.1"]'::jsonb,
    'admin-001',
    'admin',
    TRUE
);

-- Pandemic Scenario
INSERT INTO portal.scenarios (
    scenario_code, scenario_name, description, scenario_type, industry, threat_type,
    full_scenario, injects, learning_objectives, duration_minutes, iso_clauses,
    created_by, author_type, published
) VALUES (
    'SCN-PANDEMIC-001',
    'Rapid Spread Infectious Disease',
    'A highly contagious disease outbreak forces rapid transition to remote operations and tests pandemic response plans.',
    'tabletop',
    'Healthcare',
    'Pandemic',
    '## Scenario Overview
Health authorities announce a rapidly spreading infectious disease in your region. Government mandates work-from-home orders within 24 hours.

## Initial Situation
- Time: Thursday, 16:00 PM
- Announcement: Mandatory lockdown starting tomorrow
- Staff: 80% need remote work setup
- Critical operations: Must continue on-site
- Supply chain: Disruptions expected

## Your Tasks
1. Activate pandemic response plan
2. Enable remote work capabilities
3. Identify essential on-site staff
4. Secure critical supplies',
    '[
        {"time": 0, "inject": "Government announces lockdown", "expected_action": "Activate pandemic plan"},
        {"time": 30, "inject": "VPN capacity reached, some staff cannot connect", "expected_action": "Implement VPN priority system"},
        {"time": 60, "inject": "3 essential staff report illness symptoms", "expected_action": "Activate backup staffing plan"},
        {"time": 90, "inject": "Supply delivery delayed indefinitely", "expected_action": "Source alternate suppliers"}
    ]'::jsonb,
    '["Test remote work capabilities", "Validate essential staff identification", "Practice supply chain continuity", "Test health and safety protocols"]'::jsonb,
    120,
    '["8.3", "8.4", "A.11.1"]'::jsonb,
    'admin-001',
    'admin',
    TRUE
);

-- ============================================================================
-- Rollback Script
-- ============================================================================

/*
-- Drop triggers
DROP TRIGGER IF EXISTS trigger_update_scenario_rating ON portal.scenario_reviews;
DROP TRIGGER IF EXISTS trigger_reviews_updated_at ON portal.scenario_reviews;
DROP TRIGGER IF EXISTS trigger_scenario_published_at ON portal.scenarios;
DROP TRIGGER IF EXISTS trigger_scenarios_updated_at ON portal.scenarios;

-- Drop functions
DROP FUNCTION IF EXISTS portal.update_scenario_rating();
DROP FUNCTION IF EXISTS portal.set_scenario_published_at();

-- Drop tables
DROP TABLE IF EXISTS portal.scenario_reviews CASCADE;
DROP TABLE IF EXISTS portal.scenarios CASCADE;
*/
