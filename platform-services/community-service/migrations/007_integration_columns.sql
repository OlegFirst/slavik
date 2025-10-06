-- ============================================================================
-- Community Service - Integration Columns Migration
-- ============================================================================
-- Version: 007
-- Description: Add foreign key columns for Learning & Governance integration
-- Created: 2025-10-03
-- Purpose: Phase 4 - Database Extensions
-- ============================================================================

-- ============================================================================
-- PORTAL SERVICE - KNOWLEDGE ARTICLES
-- ============================================================================

-- Add Learning Service integration columns
ALTER TABLE portal.knowledge_articles
ADD COLUMN related_training_program_id INTEGER,
ADD COLUMN required_competency_level VARCHAR(50);

COMMENT ON COLUMN portal.knowledge_articles.related_training_program_id IS
'Foreign key to learning.training_programs.id - Links article to training program';

COMMENT ON COLUMN portal.knowledge_articles.required_competency_level IS
'Required competency level to understand article: beginner, intermediate, advanced, expert';

-- Add Governance Service integration columns
ALTER TABLE portal.knowledge_articles
ADD COLUMN related_policy_id INTEGER,
ADD COLUMN related_policy_references JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN portal.knowledge_articles.related_policy_id IS
'Primary related policy from governance.policies.id';

COMMENT ON COLUMN portal.knowledge_articles.related_policy_references IS
'Array of policy references: [{"policy_id": 1, "section": "5.2", "relevance": "high"}]';

-- Add indexes for foreign keys
CREATE INDEX idx_articles_training_program ON portal.knowledge_articles(related_training_program_id)
WHERE related_training_program_id IS NOT NULL;

CREATE INDEX idx_articles_policy ON portal.knowledge_articles(related_policy_id)
WHERE related_policy_id IS NOT NULL;

CREATE INDEX idx_articles_policy_refs ON portal.knowledge_articles USING GIN(related_policy_references);


-- ============================================================================
-- PORTAL SERVICE - SCENARIOS
-- ============================================================================

-- Add Governance integration
ALTER TABLE portal.scenarios
ADD COLUMN related_policies JSONB DEFAULT '[]'::jsonb,
ADD COLUMN iso_clauses_covered JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN portal.scenarios.related_policies IS
'Policies tested by this scenario: [{"policy_id": 1, "test_coverage": "full"}]';

COMMENT ON COLUMN portal.scenarios.iso_clauses_covered IS
'ISO 22301 clauses covered: ["8.4", "8.5", "7.2"]';

CREATE INDEX idx_scenarios_policies ON portal.scenarios USING GIN(related_policies);
CREATE INDEX idx_scenarios_iso ON portal.scenarios USING GIN(iso_clauses_covered);


-- ============================================================================
-- PORTAL SERVICE - FORUM USERS (Reputation & Badges)
-- ============================================================================

-- Add Learning Service competencies display
ALTER TABLE portal.user_reputation
ADD COLUMN learning_competencies JSONB DEFAULT '{}'::jsonb,
ADD COLUMN certifications_count INTEGER DEFAULT 0,
ADD COLUMN last_certification_date TIMESTAMP;

COMMENT ON COLUMN portal.user_reputation.learning_competencies IS
'Competencies from Learning Service: {"bc_planning": {"level": "advanced", "score": 85}}';

COMMENT ON COLUMN portal.user_reputation.certifications_count IS
'Total certifications earned (from Learning Service)';

-- Add Governance roles for moderation
ALTER TABLE portal.user_reputation
ADD COLUMN governance_roles JSONB DEFAULT '[]'::jsonb,
ADD COLUMN is_moderator BOOLEAN DEFAULT FALSE,
ADD COLUMN moderator_since TIMESTAMP;

COMMENT ON COLUMN portal.user_reputation.governance_roles IS
'Roles from Governance Service: [{"role_code": "bcm_manager", "assigned_date": "2025-01-01"}]';

CREATE INDEX idx_reputation_moderator ON portal.user_reputation(user_id) WHERE is_moderator = TRUE;


-- ============================================================================
-- MARKETPLACE SERVICE - SPECIALISTS
-- ============================================================================

-- Add Learning Service integration
ALTER TABLE marketplace.specialists
ADD COLUMN certifications JSONB DEFAULT '[]'::jsonb,
ADD COLUMN competency_scores JSONB DEFAULT '{}'::jsonb,
ADD COLUMN last_training_date TIMESTAMP,
ADD COLUMN training_programs_completed INTEGER DEFAULT 0;

COMMENT ON COLUMN marketplace.specialists.certifications IS
'Certifications from Learning Service: [{"cert_number": "BCM-2025-001", "name": "BCM Practitioner", "expiry": "2027-01-01"}]';

COMMENT ON COLUMN marketplace.specialists.competency_scores IS
'Competency scores from Learning: {"bc_planning": {"level": "expert", "score": 95}}';

CREATE INDEX idx_specialists_certs ON marketplace.specialists USING GIN(certifications);
CREATE INDEX idx_specialists_competency ON marketplace.specialists USING GIN(competency_scores);

-- Add Governance Service integration
ALTER TABLE marketplace.specialists
ADD COLUMN verified_by_role_id INTEGER,
ADD COLUMN verification_source VARCHAR(50),
ADD COLUMN governance_competencies JSONB DEFAULT '{}'::jsonb;

COMMENT ON COLUMN marketplace.specialists.verified_by_role_id IS
'Role ID from governance.roles.id that verified this specialist';

COMMENT ON COLUMN marketplace.specialists.verification_source IS
'Verification source: governance_role, competencies, manual, learning_certification';

COMMENT ON COLUMN marketplace.specialists.governance_competencies IS
'Competencies from Governance: {"risk_assessment": {"level": "advanced", "assessed_by": "manager_001"}}';

CREATE INDEX idx_specialists_verified_role ON marketplace.specialists(verified_by_role_id)
WHERE verified_by_role_id IS NOT NULL;

CREATE INDEX idx_specialists_gov_comp ON marketplace.specialists USING GIN(governance_competencies);


-- ============================================================================
-- MARKETPLACE SERVICE - PROJECTS
-- ============================================================================

-- Add Learning/Governance requirements
ALTER TABLE marketplace.projects
ADD COLUMN required_certifications JSONB DEFAULT '[]'::jsonb,
ADD COLUMN required_competencies JSONB DEFAULT '[]'::jsonb,
ADD COLUMN related_policies JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN marketplace.projects.required_certifications IS
'Required certifications: [{"certification_name": "BCM Practitioner", "required": true}]';

COMMENT ON COLUMN marketplace.projects.required_competencies IS
'Required competencies: [{"area": "bc_planning", "min_level": "advanced"}]';

COMMENT ON COLUMN marketplace.projects.related_policies IS
'Related governance policies: [{"policy_id": 1, "relevance": "high"}]';

CREATE INDEX idx_projects_req_certs ON marketplace.projects USING GIN(required_certifications);
CREATE INDEX idx_projects_req_comp ON marketplace.projects USING GIN(required_competencies);


-- ============================================================================
-- MARKETPLACE SERVICE - PROPOSALS
-- ============================================================================

-- Add competency match score
ALTER TABLE marketplace.proposals
ADD COLUMN competency_match_score INTEGER DEFAULT 0,
ADD COLUMN matching_details JSONB DEFAULT '{}'::jsonb;

COMMENT ON COLUMN marketplace.proposals.competency_match_score IS
'Calculated match score 0-100 based on specialist competencies vs project requirements';

COMMENT ON COLUMN marketplace.proposals.matching_details IS
'Detailed match breakdown: {"bc_planning": {"required": "advanced", "specialist": "expert", "match": true}}';

CREATE INDEX idx_proposals_match_score ON marketplace.proposals(competency_match_score DESC);


-- ============================================================================
-- VALIDATION VIEWS
-- ============================================================================

-- View: Portal Articles with Training Programs
CREATE OR REPLACE VIEW portal.v_articles_with_training AS
SELECT
    a.id,
    a.title,
    a.category,
    a.related_training_program_id,
    a.required_competency_level,
    a.related_policy_id,
    jsonb_array_length(a.related_policy_references) as policy_refs_count,
    a.published,
    a.view_count,
    a.usefulness_score
FROM portal.knowledge_articles a
WHERE a.published = true;

COMMENT ON VIEW portal.v_articles_with_training IS
'Published articles with Learning/Governance integration data';

-- View: Verified Specialists with Certifications
CREATE OR REPLACE VIEW marketplace.v_verified_specialists AS
SELECT
    s.id,
    s.user_id,
    s.name,
    s.title,
    s.is_verified,
    s.verified_by_role_id,
    s.verification_source,
    jsonb_array_length(s.certifications) as certifications_count,
    s.competency_scores,
    s.governance_competencies,
    s.availability_status,
    s.hourly_rate
FROM marketplace.specialists s
WHERE s.active = true AND s.is_verified = true;

COMMENT ON VIEW marketplace.v_verified_specialists IS
'Active verified specialists with Learning/Governance data';

-- View: Projects with Competency Requirements
CREATE OR REPLACE VIEW marketplace.v_projects_with_requirements AS
SELECT
    p.id,
    p.title,
    p.service_type,
    p.budget_type,
    p.budget_min,
    p.budget_max,
    jsonb_array_length(p.required_certifications) as required_certs_count,
    jsonb_array_length(p.required_competencies) as required_comp_count,
    p.status,
    p.urgency,
    p.deadline
FROM marketplace.projects p
WHERE p.status = 'published';

COMMENT ON VIEW marketplace.v_projects_with_requirements IS
'Published projects with Learning/Governance requirements';


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Calculate competency match score
CREATE OR REPLACE FUNCTION marketplace.calculate_competency_match(
    specialist_competencies JSONB,
    required_competencies JSONB
) RETURNS INTEGER AS $$
DECLARE
    total_requirements INTEGER;
    matched_requirements INTEGER := 0;
    requirement JSONB;
    specialist_level TEXT;
    required_level TEXT;
    level_scores JSONB := '{"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}'::jsonb;
BEGIN
    -- Count total requirements
    total_requirements := jsonb_array_length(required_competencies);

    IF total_requirements = 0 THEN
        RETURN 100; -- No requirements = 100% match
    END IF;

    -- Check each requirement
    FOR requirement IN SELECT * FROM jsonb_array_elements(required_competencies)
    LOOP
        -- Get specialist's level for this competency
        specialist_level := specialist_competencies->(requirement->>'area')->>'level';
        required_level := requirement->>'min_level';

        -- Compare levels
        IF specialist_level IS NOT NULL AND
           (level_scores->>specialist_level)::INTEGER >= (level_scores->>required_level)::INTEGER
        THEN
            matched_requirements := matched_requirements + 1;
        END IF;
    END LOOP;

    -- Calculate percentage
    RETURN (matched_requirements * 100 / total_requirements);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION marketplace.calculate_competency_match IS
'Calculate match score (0-100) between specialist competencies and project requirements';


-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant permissions
GRANT SELECT ON portal.v_articles_with_training TO authenticated;
GRANT SELECT ON marketplace.v_verified_specialists TO authenticated;
GRANT SELECT ON marketplace.v_projects_with_requirements TO authenticated;

GRANT EXECUTE ON FUNCTION marketplace.calculate_competency_match TO authenticated;


-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Record migration
INSERT INTO portal.migration_history (version, description, applied_at)
VALUES ('007', 'Add Learning & Governance integration columns', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 007 complete: Integration columns added';
    RAISE NOTICE '   - Portal: 8 new columns + 2 views';
    RAISE NOTICE '   - Marketplace: 10 new columns + 2 views + 1 function';
END $$;
