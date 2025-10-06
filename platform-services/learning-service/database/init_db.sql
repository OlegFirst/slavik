-- Learning Module Database Schema
-- ISO 22301 Clause 7.2 (Competence) & 7.3 (Awareness)
-- BCI GPG Practice 2 (PP2: Embracing BC)

-- Create schema
CREATE SCHEMA IF NOT EXISTS learning;

-- ==================== TRAINING PROGRAMS ====================

CREATE TABLE IF NOT EXISTS learning.training_programs (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,

    -- Program Details
    program_code VARCHAR(50) NOT NULL UNIQUE,
    program_name VARCHAR(255) NOT NULL,
    description TEXT,
    program_type VARCHAR(50) NOT NULL,

    -- Classification
    bci_training_level VARCHAR(50),
    target_audience VARCHAR(100),
    iso_clause VARCHAR(20),

    -- Content
    learning_objectives JSONB DEFAULT '[]',
    curriculum JSONB DEFAULT '[]',
    materials JSONB DEFAULT '[]',
    prerequisites JSONB DEFAULT '[]',

    -- Logistics
    duration_hours INT,
    delivery_method VARCHAR(50),
    instructor_required BOOLEAN DEFAULT FALSE,
    max_participants INT,

    -- Assessment
    assessment_required BOOLEAN DEFAULT TRUE,
    passing_score INT DEFAULT 70,
    certification_awarded BOOLEAN DEFAULT FALSE,
    certification_name VARCHAR(255),
    certification_validity_months INT,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    published_date TIMESTAMP,

    -- Metadata
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== TRAINING ENROLLMENTS ====================

CREATE TABLE IF NOT EXISTS learning.training_enrollments (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,

    -- Program & Person
    program_id INT NOT NULL REFERENCES learning.training_programs(id) ON DELETE CASCADE,
    person_id VARCHAR(255) NOT NULL,
    person_name VARCHAR(255) NOT NULL,
    person_role VARCHAR(100),
    person_department VARCHAR(100),

    -- Enrollment Details
    enrolled_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    enrollment_type VARCHAR(50),
    assigned_by VARCHAR(255),

    -- Progress Tracking
    status VARCHAR(20) NOT NULL DEFAULT 'enrolled',
    progress_percentage INT DEFAULT 0 NOT NULL CHECK (progress_percentage BETWEEN 0 AND 100),
    started_date TIMESTAMP,
    completed_date TIMESTAMP,
    due_date TIMESTAMP,

    -- Assessment Results
    assessment_attempts INT DEFAULT 0,
    assessment_score FLOAT,
    assessment_passed BOOLEAN DEFAULT FALSE,
    assessment_date TIMESTAMP,

    -- Certification
    certification_issued BOOLEAN DEFAULT FALSE,
    certification_number VARCHAR(100),
    certification_date TIMESTAMP,
    certification_expiry_date TIMESTAMP,

    -- Learning Data
    time_spent_hours FLOAT DEFAULT 0,
    modules_completed JSONB DEFAULT '[]',
    last_activity_date TIMESTAMP,

    -- Gamification
    points_earned INT DEFAULT 0,
    achievements_unlocked JSONB DEFAULT '[]',

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== COMPETENCY ASSESSMENTS ====================

CREATE TABLE IF NOT EXISTS learning.competency_assessments (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,

    -- Person & Competency
    person_id VARCHAR(255) NOT NULL,
    person_name VARCHAR(255) NOT NULL,
    person_role VARCHAR(100),
    competency_area VARCHAR(50) NOT NULL,
    competency_name VARCHAR(255) NOT NULL,

    -- BCI Framework
    bci_practice VARCHAR(10),
    competency_category VARCHAR(50),

    -- Assessment Levels
    required_level VARCHAR(20) NOT NULL,
    current_level VARCHAR(20) NOT NULL,
    target_level VARCHAR(20),

    -- Gap Analysis
    gap_exists BOOLEAN DEFAULT FALSE NOT NULL,
    gap_severity VARCHAR(20),
    gap_description TEXT,

    -- Evidence
    evidence_type VARCHAR(50),
    evidence_details JSONB,
    evidence_date TIMESTAMP,
    evidence_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(255),
    verified_date TIMESTAMP,

    -- Training Plan
    training_required BOOLEAN DEFAULT FALSE,
    recommended_programs JSONB DEFAULT '[]',
    training_plan TEXT,
    estimated_duration_hours INT,
    target_completion_date TIMESTAMP,

    -- Assessment Details
    assessment_method VARCHAR(50),
    assessment_date TIMESTAMP NOT NULL,
    assessor_id VARCHAR(255),
    assessor_name VARCHAR(255),

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    next_assessment_date TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== AWARENESS CAMPAIGNS ====================

CREATE TABLE IF NOT EXISTS learning.awareness_campaigns (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,

    -- Campaign Details
    campaign_code VARCHAR(50) NOT NULL UNIQUE,
    campaign_name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(50) NOT NULL,

    -- Target Audience
    target_groups JSONB DEFAULT '[]',
    target_audience_count INT,

    -- Content
    key_messages JSONB DEFAULT '[]',
    materials JSONB DEFAULT '[]',
    communication_channels JSONB DEFAULT '[]',

    -- Schedule
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    frequency VARCHAR(50),

    -- Execution
    status VARCHAR(20) NOT NULL DEFAULT 'planned',
    campaign_owner VARCHAR(255) NOT NULL,
    responsible_team JSONB DEFAULT '[]',

    -- Participation Tracking
    total_participants INT DEFAULT 0,
    participation_rate FLOAT,

    -- Effectiveness Metrics
    awareness_survey_sent BOOLEAN DEFAULT FALSE,
    survey_responses INT DEFAULT 0,
    survey_results JSONB,
    effectiveness_score FLOAT,

    -- Feedback
    feedback_collected JSONB DEFAULT '[]',
    lessons_learned TEXT,

    -- Metadata
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- ==================== TRAINING TEMPLATES ====================

CREATE TABLE IF NOT EXISTS learning.training_templates (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,

    -- Template Details
    template_code VARCHAR(50) NOT NULL UNIQUE,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Classification
    template_type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    iso_clause VARCHAR(20),

    -- Content
    content JSONB,
    content_format VARCHAR(20),
    form_schema JSONB,

    -- Usage
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INT DEFAULT 0,
    last_used_date TIMESTAMP,

    -- AI Enhancement
    is_ai_enhanced BOOLEAN DEFAULT FALSE,
    ai_prompt TEXT,

    -- Metadata
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== USER ACHIEVEMENTS ====================

CREATE TABLE IF NOT EXISTS learning.user_achievements (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,

    -- User
    person_id VARCHAR(255) NOT NULL,
    person_name VARCHAR(255) NOT NULL,

    -- Achievement
    achievement_code VARCHAR(50) NOT NULL,
    achievement_name VARCHAR(255) NOT NULL,
    achievement_level VARCHAR(20),

    -- Action
    action_code VARCHAR(50) NOT NULL,
    action_type VARCHAR(50) NOT NULL,

    -- Points
    points_earned INT DEFAULT 0 NOT NULL,
    total_points INT DEFAULT 0 NOT NULL,

    -- Context
    related_entity_type VARCHAR(50),
    related_entity_id INT,

    -- Achievement Details
    earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    badge_icon VARCHAR(50),
    badge_color VARCHAR(20),

    -- Streaks
    is_streak_achievement BOOLEAN DEFAULT FALSE,
    streak_count INT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== INDEXES ====================

-- Training Programs
CREATE INDEX IF NOT EXISTS idx_programs_tenant_status ON learning.training_programs(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_programs_type ON learning.training_programs(program_type);
CREATE INDEX IF NOT EXISTS idx_programs_code ON learning.training_programs(program_code);

-- Enrollments
CREATE INDEX IF NOT EXISTS idx_enrollments_tenant_person ON learning.training_enrollments(tenant_id, person_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status ON learning.training_enrollments(status);
CREATE INDEX IF NOT EXISTS idx_enrollments_program ON learning.training_enrollments(program_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_due_date ON learning.training_enrollments(due_date);

-- Competency Assessments
CREATE INDEX IF NOT EXISTS idx_competency_tenant_person ON learning.competency_assessments(tenant_id, person_id);
CREATE INDEX IF NOT EXISTS idx_competency_area ON learning.competency_assessments(competency_area);
CREATE INDEX IF NOT EXISTS idx_competency_gap ON learning.competency_assessments(gap_exists);
CREATE INDEX IF NOT EXISTS idx_competency_status ON learning.competency_assessments(status);

-- Awareness Campaigns
CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_status ON learning.awareness_campaigns(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_campaigns_type ON learning.awareness_campaigns(campaign_type);
CREATE INDEX IF NOT EXISTS idx_campaigns_code ON learning.awareness_campaigns(campaign_code);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON learning.awareness_campaigns(start_date, end_date);

-- Templates
CREATE INDEX IF NOT EXISTS idx_templates_tenant_active ON learning.training_templates(tenant_id, is_active);
CREATE INDEX IF NOT EXISTS idx_templates_type ON learning.training_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_templates_code ON learning.training_templates(template_code);

-- Achievements
CREATE INDEX IF NOT EXISTS idx_achievements_tenant_person ON learning.user_achievements(tenant_id, person_id);
CREATE INDEX IF NOT EXISTS idx_achievements_code ON learning.user_achievements(achievement_code);
CREATE INDEX IF NOT EXISTS idx_achievements_date ON learning.user_achievements(earned_date);

-- ==================== ROW LEVEL SECURITY ====================

-- Enable RLS on all tables
ALTER TABLE learning.training_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.training_enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.competency_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.awareness_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.training_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.user_achievements ENABLE ROW LEVEL SECURITY;

-- RLS Policies (tenant isolation)
CREATE POLICY tenant_isolation_programs ON learning.training_programs
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::text);

CREATE POLICY tenant_isolation_enrollments ON learning.training_enrollments
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::text);

CREATE POLICY tenant_isolation_competency ON learning.competency_assessments
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::text);

CREATE POLICY tenant_isolation_campaigns ON learning.awareness_campaigns
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::text);

CREATE POLICY tenant_isolation_templates ON learning.training_templates
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::text OR is_public = TRUE);

CREATE POLICY tenant_isolation_achievements ON learning.user_achievements
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::text);

-- ==================== TRIGGERS ====================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION learning.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON learning.training_programs
    FOR EACH ROW EXECUTE FUNCTION learning.update_updated_at_column();

CREATE TRIGGER update_enrollments_updated_at BEFORE UPDATE ON learning.training_enrollments
    FOR EACH ROW EXECUTE FUNCTION learning.update_updated_at_column();

CREATE TRIGGER update_competency_updated_at BEFORE UPDATE ON learning.competency_assessments
    FOR EACH ROW EXECUTE FUNCTION learning.update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON learning.awareness_campaigns
    FOR EACH ROW EXECUTE FUNCTION learning.update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON learning.training_templates
    FOR EACH ROW EXECUTE FUNCTION learning.update_updated_at_column();

-- ==================== VIEWS ====================

-- Training Progress Overview
CREATE OR REPLACE VIEW learning.training_progress_overview AS
SELECT
    tenant_id,
    COUNT(*) as total_enrollments,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
    COUNT(*) FILTER (WHERE status = 'enrolled') as not_started,
    ROUND(AVG(progress_percentage), 2) as avg_progress,
    COUNT(*) FILTER (WHERE assessment_passed = TRUE) as passed_assessments,
    COUNT(*) FILTER (WHERE certification_issued = TRUE) as certifications_issued
FROM learning.training_enrollments
GROUP BY tenant_id;

-- Competency Gap Summary
CREATE OR REPLACE VIEW learning.competency_gap_summary AS
SELECT
    tenant_id,
    competency_area,
    COUNT(*) as total_assessments,
    COUNT(*) FILTER (WHERE gap_exists = TRUE) as gaps_identified,
    COUNT(*) FILTER (WHERE gap_severity = 'critical') as critical_gaps,
    COUNT(*) FILTER (WHERE gap_severity = 'high') as high_gaps,
    COUNT(*) FILTER (WHERE training_required = TRUE) as training_needed
FROM learning.competency_assessments
GROUP BY tenant_id, competency_area;

-- Awareness Campaign Effectiveness
CREATE OR REPLACE VIEW learning.campaign_effectiveness AS
SELECT
    tenant_id,
    campaign_code,
    campaign_name,
    campaign_type,
    status,
    total_participants,
    participation_rate,
    effectiveness_score,
    start_date,
    end_date
FROM learning.awareness_campaigns
WHERE status IN ('in_progress', 'completed')
ORDER BY effectiveness_score DESC NULLS LAST;

-- Leaderboard View
CREATE OR REPLACE VIEW learning.points_leaderboard AS
SELECT
    tenant_id,
    person_id,
    person_name,
    SUM(points_earned) as total_points,
    COUNT(DISTINCT achievement_code) as achievements_count,
    MAX(earned_date) as last_achievement_date,
    RANK() OVER (PARTITION BY tenant_id ORDER BY SUM(points_earned) DESC) as rank
FROM learning.user_achievements
GROUP BY tenant_id, person_id, person_name;

-- ==================== COMMENTS ====================

COMMENT ON SCHEMA learning IS 'Learning & Development module - ISO 22301 Clause 7.2 & 7.3, BCI GPG PP2';

COMMENT ON TABLE learning.training_programs IS 'BC training programs (ISO 7.2)';
COMMENT ON TABLE learning.training_enrollments IS 'Individual training enrollments and progress tracking';
COMMENT ON TABLE learning.competency_assessments IS 'Competency assessments and gap analysis (ISO 7.2)';
COMMENT ON TABLE learning.awareness_campaigns IS 'BC awareness campaigns (ISO 7.3, BCI GPP PP2)';
COMMENT ON TABLE learning.training_templates IS 'Training templates, forms, and checklists library';
COMMENT ON TABLE learning.user_achievements IS 'Gamification: user achievements, points, badges';

COMMENT ON VIEW learning.training_progress_overview IS 'Training completion statistics by tenant';
COMMENT ON VIEW learning.competency_gap_summary IS 'Competency gaps by area and severity';
COMMENT ON VIEW learning.campaign_effectiveness IS 'Awareness campaign participation and effectiveness';
COMMENT ON VIEW learning.points_leaderboard IS 'Gamification leaderboard by tenant';
