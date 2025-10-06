-- ============================================================================
-- Community Service - Junction Tables Migration
-- ============================================================================
-- Version: 008
-- Description: Create junction tables for many-to-many relationships
-- Created: 2025-10-03
-- Purpose: Phase 4 - Link Portal/Marketplace to Learning/Governance
-- ============================================================================

-- ============================================================================
-- PORTAL: ARTICLE COMPETENCIES
-- ============================================================================

CREATE TABLE portal.article_competencies (
    -- Composite primary key
    article_id INTEGER NOT NULL,
    competency_area VARCHAR(100) NOT NULL,

    -- Relationship metadata
    relevance VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    required_level VARCHAR(20), -- beginner, intermediate, advanced, expert
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),

    PRIMARY KEY (article_id, competency_area),

    -- Foreign key to articles (no FK to Learning - different DB)
    FOREIGN KEY (article_id) REFERENCES portal.knowledge_articles(id) ON DELETE CASCADE
);

CREATE INDEX idx_article_comp_article ON portal.article_competencies(article_id);
CREATE INDEX idx_article_comp_area ON portal.article_competencies(competency_area);
CREATE INDEX idx_article_comp_level ON portal.article_competencies(required_level);

COMMENT ON TABLE portal.article_competencies IS
'Links knowledge articles to competency areas from Learning Service';

COMMENT ON COLUMN portal.article_competencies.competency_area IS
'Competency area code from Learning Service (e.g., "bc_planning", "risk_assessment")';

COMMENT ON COLUMN portal.article_competencies.relevance IS
'How relevant is this competency to understanding the article';


-- ============================================================================
-- PORTAL: SCENARIO POLICIES
-- ============================================================================

CREATE TABLE portal.scenario_policies (
    -- Composite primary key
    scenario_id INTEGER NOT NULL,
    policy_id INTEGER NOT NULL, -- Reference to governance.policies.id

    -- Testing metadata
    test_coverage VARCHAR(20) DEFAULT 'partial', -- none, partial, full
    iso_clauses_tested JSONB DEFAULT '[]'::jsonb, -- ["8.4", "8.5"]
    last_tested_date TIMESTAMP,
    test_results TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (scenario_id, policy_id),

    -- Foreign key to scenarios (no FK to Governance - different DB)
    FOREIGN KEY (scenario_id) REFERENCES portal.scenarios(id) ON DELETE CASCADE
);

CREATE INDEX idx_scenario_policy_scenario ON portal.scenario_policies(scenario_id);
CREATE INDEX idx_scenario_policy_policy ON portal.scenario_policies(policy_id);
CREATE INDEX idx_scenario_policy_coverage ON portal.scenario_policies(test_coverage);

COMMENT ON TABLE portal.scenario_policies IS
'Links BCM scenarios to governance policies they test';

COMMENT ON COLUMN portal.scenario_policies.test_coverage IS
'How thoroughly the scenario tests the policy: none, partial, full';


-- ============================================================================
-- MARKETPLACE: SPECIALIST COMPETENCIES
-- ============================================================================

CREATE TABLE marketplace.specialist_competencies (
    -- Composite primary key
    specialist_id INTEGER NOT NULL,
    competency_area VARCHAR(100) NOT NULL,

    -- Competency details
    proficiency_level VARCHAR(20) NOT NULL, -- beginner, intermediate, advanced, expert
    score INTEGER DEFAULT 0, -- 0-100
    source VARCHAR(50), -- learning_service, governance_service, self_assessed, client_verified

    -- Evidence
    certifications_count INTEGER DEFAULT 0,
    trainings_completed INTEGER DEFAULT 0,
    projects_completed INTEGER DEFAULT 0,
    evidence_notes TEXT,

    -- Assessment
    last_assessed_date TIMESTAMP,
    assessed_by VARCHAR(255),
    next_review_date TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (specialist_id, competency_area),

    FOREIGN KEY (specialist_id) REFERENCES marketplace.specialists(id) ON DELETE CASCADE,

    CHECK (score >= 0 AND score <= 100)
);

CREATE INDEX idx_spec_comp_specialist ON marketplace.specialist_competencies(specialist_id);
CREATE INDEX idx_spec_comp_area ON marketplace.specialist_competencies(competency_area);
CREATE INDEX idx_spec_comp_level ON marketplace.specialist_competencies(proficiency_level);
CREATE INDEX idx_spec_comp_score ON marketplace.specialist_competencies(score DESC);
CREATE INDEX idx_spec_comp_source ON marketplace.specialist_competencies(source);

COMMENT ON TABLE marketplace.specialist_competencies IS
'Detailed competency records for specialists (from Learning/Governance/Projects)';

COMMENT ON COLUMN marketplace.specialist_competencies.source IS
'Where competency data came from: learning_service, governance_service, self_assessed, client_verified';

COMMENT ON COLUMN marketplace.specialist_competencies.score IS
'Calculated score 0-100 based on certifications, trainings, and project history';


-- ============================================================================
-- MARKETPLACE: PROJECT COMPETENCY REQUIREMENTS
-- ============================================================================

CREATE TABLE marketplace.project_competency_requirements (
    -- Composite primary key
    project_id INTEGER NOT NULL,
    competency_area VARCHAR(100) NOT NULL,

    -- Requirement details
    minimum_level VARCHAR(20) NOT NULL, -- beginner, intermediate, advanced, expert
    is_mandatory BOOLEAN DEFAULT true,
    weight INTEGER DEFAULT 1, -- Importance weight for matching (1-10)

    -- Matching
    matching_specialists_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (project_id, competency_area),

    FOREIGN KEY (project_id) REFERENCES marketplace.projects(id) ON DELETE CASCADE,

    CHECK (weight >= 1 AND weight <= 10)
);

CREATE INDEX idx_proj_req_project ON marketplace.project_competency_requirements(project_id);
CREATE INDEX idx_proj_req_area ON marketplace.project_competency_requirements(competency_area);
CREATE INDEX idx_proj_req_level ON marketplace.project_competency_requirements(minimum_level);
CREATE INDEX idx_proj_req_mandatory ON marketplace.project_competency_requirements(is_mandatory);

COMMENT ON TABLE marketplace.project_competency_requirements IS
'Competency requirements for projects (used in specialist matching)';

COMMENT ON COLUMN marketplace.project_competency_requirements.weight IS
'Importance weight 1-10 for matching algorithm (10 = critical skill)';


-- ============================================================================
-- MARKETPLACE: SPECIALIST CERTIFICATIONS (Normalized)
-- ============================================================================

CREATE TABLE marketplace.specialist_certifications_normalized (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL,

    -- Certification details (from Learning Service)
    certification_number VARCHAR(100) NOT NULL UNIQUE,
    certification_name VARCHAR(255) NOT NULL,
    program_code VARCHAR(50),
    program_name VARCHAR(255),

    -- Dates
    issued_date DATE NOT NULL,
    expiry_date DATE,
    is_expired BOOLEAN GENERATED ALWAYS AS (expiry_date IS NOT NULL AND expiry_date < CURRENT_DATE) STORED,

    -- Verification
    verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP,
    verified_by VARCHAR(255),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (specialist_id) REFERENCES marketplace.specialists(id) ON DELETE CASCADE
);

CREATE INDEX idx_spec_cert_specialist ON marketplace.specialist_certifications_normalized(specialist_id);
CREATE INDEX idx_spec_cert_number ON marketplace.specialist_certifications_normalized(certification_number);
CREATE INDEX idx_spec_cert_expiry ON marketplace.specialist_certifications_normalized(expiry_date)
WHERE expiry_date IS NOT NULL;
CREATE INDEX idx_spec_cert_active ON marketplace.specialist_certifications_normalized(specialist_id)
WHERE is_expired = false;

COMMENT ON TABLE marketplace.specialist_certifications_normalized IS
'Normalized certification records (alternative to JSONB in specialists.certifications)';

COMMENT ON COLUMN marketplace.specialist_certifications_normalized.is_expired IS
'Auto-calculated: true if expiry_date < current_date';


-- ============================================================================
-- TRIGGER: Update specialist certification count
-- ============================================================================

CREATE OR REPLACE FUNCTION marketplace.update_specialist_cert_count()
RETURNS TRIGGER AS $$
BEGIN
    -- Update certifications_count in specialist_competencies
    UPDATE marketplace.specialist_competencies
    SET certifications_count = (
        SELECT COUNT(*)
        FROM marketplace.specialist_certifications_normalized
        WHERE specialist_id = NEW.specialist_id
          AND is_expired = false
    )
    WHERE specialist_id = NEW.specialist_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_cert_count
AFTER INSERT OR UPDATE ON marketplace.specialist_certifications_normalized
FOR EACH ROW
EXECUTE FUNCTION marketplace.update_specialist_cert_count();


-- ============================================================================
-- VIEWS: Enhanced Specialist Profiles
-- ============================================================================

CREATE OR REPLACE VIEW marketplace.v_specialist_full_profile AS
SELECT
    s.id,
    s.user_id,
    s.name,
    s.title,
    s.bio,
    s.is_verified,
    s.verified_by_role_id,
    s.verification_source,
    s.availability_status,
    s.hourly_rate,

    -- Certifications
    COUNT(DISTINCT sc.id) FILTER (WHERE sc.is_expired = false) as active_certifications,
    jsonb_agg(
        DISTINCT jsonb_build_object(
            'certification_number', sc.certification_number,
            'certification_name', sc.certification_name,
            'issued_date', sc.issued_date,
            'expiry_date', sc.expiry_date
        )
    ) FILTER (WHERE sc.id IS NOT NULL AND sc.is_expired = false) as certifications_detail,

    -- Competencies
    jsonb_object_agg(
        scomp.competency_area,
        jsonb_build_object(
            'level', scomp.proficiency_level,
            'score', scomp.score,
            'source', scomp.source
        )
    ) FILTER (WHERE scomp.competency_area IS NOT NULL) as competencies_detail,

    -- Projects
    COUNT(DISTINCT pr.id) FILTER (WHERE pr.status = 'completed') as completed_projects,

    -- Updated
    s.updated_at

FROM marketplace.specialists s
LEFT JOIN marketplace.specialist_certifications_normalized sc ON s.id = sc.specialist_id
LEFT JOIN marketplace.specialist_competencies scomp ON s.id = scomp.specialist_id
LEFT JOIN marketplace.proposals prop ON s.id = prop.specialist_id AND prop.status = 'accepted'
LEFT JOIN marketplace.projects pr ON prop.project_id = pr.id

WHERE s.active = true

GROUP BY s.id;

COMMENT ON VIEW marketplace.v_specialist_full_profile IS
'Complete specialist profile with certifications, competencies, and project history';


-- ============================================================================
-- FUNCTION: Find Matching Specialists for Project
-- ============================================================================

CREATE OR REPLACE FUNCTION marketplace.find_matching_specialists(
    p_project_id INTEGER,
    p_min_match_score INTEGER DEFAULT 70
)
RETURNS TABLE (
    specialist_id INTEGER,
    specialist_name VARCHAR,
    match_score INTEGER,
    matching_competencies JSONB,
    missing_competencies JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id as specialist_id,
        s.name as specialist_name,
        marketplace.calculate_competency_match(
            s.competency_scores,
            (SELECT required_competencies FROM marketplace.projects WHERE id = p_project_id)
        ) as match_score,

        -- Matching competencies
        (
            SELECT jsonb_object_agg(req->>'area', s.competency_scores->(req->>'area'))
            FROM jsonb_array_elements(p.required_competencies) req
            WHERE s.competency_scores ? (req->>'area')
        ) as matching_competencies,

        -- Missing competencies
        (
            SELECT jsonb_agg(req->>'area')
            FROM jsonb_array_elements(p.required_competencies) req
            WHERE NOT (s.competency_scores ? (req->>'area'))
        ) as missing_competencies

    FROM marketplace.specialists s
    CROSS JOIN marketplace.projects p
    WHERE p.id = p_project_id
      AND s.active = true
      AND s.is_verified = true
      AND s.availability_status = 'available'
      AND marketplace.calculate_competency_match(
            s.competency_scores,
            p.required_competencies
          ) >= p_min_match_score
    ORDER BY match_score DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION marketplace.find_matching_specialists IS
'Find specialists matching project competency requirements with minimum score';


-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT SELECT ON portal.article_competencies TO authenticated;
GRANT SELECT ON portal.scenario_policies TO authenticated;
GRANT SELECT ON marketplace.specialist_competencies TO authenticated;
GRANT SELECT ON marketplace.project_competency_requirements TO authenticated;
GRANT SELECT ON marketplace.specialist_certifications_normalized TO authenticated;
GRANT SELECT ON marketplace.v_specialist_full_profile TO authenticated;

GRANT EXECUTE ON FUNCTION marketplace.find_matching_specialists TO authenticated;


-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Record migration
INSERT INTO portal.migration_history (version, description, applied_at)
VALUES ('008', 'Create junction tables for Learning/Governance integration', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 008 complete: Junction tables created';
    RAISE NOTICE '   - Portal: 2 junction tables (article_competencies, scenario_policies)';
    RAISE NOTICE '   - Marketplace: 3 junction tables + 1 normalized table';
    RAISE NOTICE '   - Added: 1 view + 1 matching function';
END $$;
