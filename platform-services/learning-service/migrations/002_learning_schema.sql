-- ==================================================================================
-- LEARNING SERVICE - DATABASE MIGRATION
-- ==================================================================================
-- Version: 002
-- Service: Learning Service (ISO 22301 Clause 7.2 & 7.3, BCI GPG PP2)
-- Description: Complete learning schema with 6 core tables + 13 reference tables
-- Total Seed Records: 140 (88 learning_seed + 52 bci_gpg_seed)
-- ==================================================================================

-- Create Learning schema
CREATE SCHEMA IF NOT EXISTS learning;

-- ==================== PART 1: CORE TABLES ====================

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

-- ==================== PART 2: REFERENCE TABLES & SEED DATA ====================

-- ==================== COMPETENCY AREAS (10 records) ====================

CREATE TABLE IF NOT EXISTS learning.competency_areas (
    id SERIAL PRIMARY KEY,
    area_code VARCHAR(50) NOT NULL UNIQUE,
    area_name VARCHAR(255) NOT NULL,
    description TEXT,
    iso_clause VARCHAR(20),
    level_count INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.competency_areas (area_code, area_name, description, iso_clause) VALUES
('incident_response', 'Incident Response & Management', 'Skills in detecting, responding to, and managing incidents', '8.3'),
('business_continuity', 'Business Continuity Planning', 'BCP development, implementation, and maintenance', '8.2'),
('risk_assessment', 'Risk Assessment & Analysis', 'Identifying, analyzing, and treating BC risks', '6.1'),
('crisis_communication', 'Crisis Communication', 'Stakeholder communication during crises', '7.4'),
('bia_execution', 'Business Impact Analysis', 'Conducting BIA and determining criticality', '8.2.2'),
('recovery_operations', 'Recovery Operations', 'IT and business recovery procedures', '8.4'),
('exercise_management', 'Exercise & Testing', 'Planning and conducting BC exercises', '8.5'),
('compliance_audit', 'ISO 22301 Compliance & Audit', 'Understanding standard requirements', '9.2'),
('leadership_governance', 'BC Leadership & Governance', 'Strategic BC leadership and decision-making', '5.1'),
('resource_management', 'BC Resource Management', 'Managing people, technology, facilities for BC', '7.1')
ON CONFLICT (area_code) DO NOTHING;

-- ==================== LEARNING STYLES (6 records) ====================

CREATE TABLE IF NOT EXISTS learning.learning_styles (
    id SERIAL PRIMARY KEY,
    style_code VARCHAR(50) NOT NULL UNIQUE,
    style_name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.learning_styles (style_code, style_name, description, icon) VALUES
('adaptive', 'Adaptive - Personalized Learning', 'AI-powered adaptive learning paths based on individual progress and preferences', '🎯'),
('intensive', 'Intensive - Accelerated Training', 'Fast-paced, concentrated learning for rapid skill acquisition', '🔥'),
('supportive', 'Supportive - Guided Learning', 'Structured guidance with mentor support and checkpoints', '🤝'),
('challenging', 'Challenging - Advanced Training', 'Advanced scenarios and complex problem-solving for experts', '💪'),
('self_paced', 'Self-Paced Learning', 'Learn at your own pace with flexible scheduling', '⏱️'),
('collaborative', 'Collaborative Learning', 'Team-based learning with peer interaction', '👥')
ON CONFLICT (style_code) DO NOTHING;

-- ==================== TRAINING PROGRAM TYPES (8 records) ====================

CREATE TABLE IF NOT EXISTS learning.program_types (
    id SERIAL PRIMARY KEY,
    type_code VARCHAR(50) NOT NULL UNIQUE,
    type_name VARCHAR(255) NOT NULL,
    description TEXT,
    target_audience VARCHAR(100),
    typical_duration_hours INT,
    iso_clause VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.program_types (type_code, type_name, description, target_audience, typical_duration_hours, iso_clause) VALUES
('bcm_awareness', 'General BCM Awareness', 'Introduction to business continuity concepts for all staff', 'all_staff', 2, '7.3'),
('role_based', 'Role-Based BCM Training', 'Specific training for assigned BC roles', 'bc_team', 8, '7.2'),
('crisis_response', 'Crisis Response Training', 'Crisis management and emergency response', 'crisis_team', 16, '8.3'),
('certification_prep', 'ISO 22301 Certification Preparation', 'Preparation for ISO 22301 certifications', 'bc_professionals', 40, '9.2'),
('simulation_exercise', 'Simulation & Exercise Training', 'Hands-on training through simulations', 'bc_team', 4, '8.5'),
('leadership_bc', 'BC Leadership Program', 'Strategic BC leadership for executives', 'management', 12, '5.1'),
('technical_recovery', 'Technical Recovery Training', 'IT disaster recovery and system restoration', 'it_team', 24, '8.4'),
('bia_specialist', 'BIA Specialist Training', 'Advanced BIA techniques and analysis', 'bia_analysts', 16, '8.2.2')
ON CONFLICT (type_code) DO NOTHING;

-- ==================== TEMPLATE TYPES (14 records) ====================

CREATE TABLE IF NOT EXISTS learning.template_types (
    id SERIAL PRIMARY KEY,
    type_code VARCHAR(50) NOT NULL UNIQUE,
    type_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    file_format VARCHAR(20),
    iso_clause VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.template_types (type_code, type_name, category, description, file_format, iso_clause) VALUES
-- Training Forms
('bia_form', 'BIA Assessment Form', 'form', 'Business Impact Analysis questionnaire template', 'html', '8.2.2'),
('risk_form', 'Risk Assessment Form', 'form', 'Risk identification and analysis form', 'html', '6.1'),
('exercise_form', 'Exercise Evaluation Form', 'form', 'Exercise performance evaluation and feedback', 'html', '8.5'),
('training_assessment', 'Training Assessment Form', 'form', 'Learning assessment and quiz template', 'html', '7.2'),
('competency_matrix', 'Competency Matrix Template', 'form', 'Skills and competency tracking matrix', 'html', '7.2'),

-- Training Checklists
('exercise_checklist', 'Exercise Preparation Checklist', 'checklist', 'Exercise planning and execution checklist', 'html', '8.5'),
('audit_checklist', 'Internal Audit Checklist', 'checklist', 'ISO 22301 compliance audit checklist', 'html', '9.2'),
('training_checklist', 'Training Delivery Checklist', 'checklist', 'Training session preparation checklist', 'html', '7.2'),

-- Training Documents
('training_plan', 'Training Plan Template', 'document', 'Annual BC training plan template', 'html', '7.2'),
('awareness_campaign', 'Awareness Campaign Template', 'document', 'BC awareness campaign planning', 'html', '7.3'),
('learning_path', 'Learning Path Template', 'document', 'Structured learning journey template', 'html', '7.2'),

-- Training Reports
('training_report', 'Training Completion Report', 'report', 'Training attendance and completion report', 'html', '7.2'),
('competency_report', 'Competency Gap Analysis Report', 'report', 'Skills gap analysis and recommendations', 'html', '7.2'),
('exercise_report', 'Exercise After-Action Report', 'report', 'Exercise outcomes and lessons learned', 'html', '8.5')
ON CONFLICT (type_code) DO NOTHING;

-- ==================== SCENARIO CATEGORIES (10 records) ====================

CREATE TABLE IF NOT EXISTS learning.scenario_categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) NOT NULL UNIQUE,
    category_name VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(20),
    icon VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.scenario_categories (category_code, category_name, description, difficulty_level, icon) VALUES
('crisis_scenarios', 'Crisis Scenarios', 'Emergency and crisis simulation scenarios', 'advanced', '🚨'),
('exercise_scenarios', 'Exercise Scenarios', 'Training exercise scenarios for skill development', 'intermediate', '🎯'),
('response_playbooks', 'Response Playbooks', 'Step-by-step response procedures', 'beginner', '📋'),
('industry_specific', 'Industry-Specific Scenarios', 'Scenarios tailored to specific industries', 'intermediate', '🏢'),
('tabletop_exercises', 'Tabletop Exercise Scenarios', 'Discussion-based exercise scenarios', 'beginner', '🗣️'),
('functional_tests', 'Functional Test Scenarios', 'Realistic functional testing scenarios', 'advanced', '⚙️'),
('pandemic_response', 'Pandemic Response Scenarios', 'Health crisis and pandemic scenarios', 'intermediate', '🦠'),
('cyber_incident', 'Cyber Incident Scenarios', 'Cybersecurity incident simulations', 'advanced', '💻'),
('natural_disaster', 'Natural Disaster Scenarios', 'Natural hazard response scenarios', 'intermediate', '🌪️'),
('supply_chain', 'Supply Chain Disruption', 'Supply chain continuity scenarios', 'intermediate', '🚚')
ON CONFLICT (category_code) DO NOTHING;

-- ==================== ACHIEVEMENT TYPES (19 records) ====================

CREATE TABLE IF NOT EXISTS learning.achievement_types (
    id SERIAL PRIMARY KEY,
    achievement_code VARCHAR(50) NOT NULL UNIQUE,
    achievement_name VARCHAR(255) NOT NULL,
    description TEXT,
    points_value INT DEFAULT 0,
    badge_icon VARCHAR(50),
    achievement_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.achievement_types (achievement_code, achievement_name, description, points_value, badge_icon, achievement_level) VALUES
-- Learning Achievements
('first_training', 'First Training Completed', 'Completed your first training module', 50, '🎓', 'bronze'),
('training_streak_7', '7-Day Learning Streak', 'Trained for 7 consecutive days', 100, '🔥', 'silver'),
('training_streak_30', '30-Day Learning Streak', 'Trained for 30 consecutive days', 500, '💪', 'gold'),
('perfect_score', 'Perfect Assessment', 'Achieved 100% on training assessment', 200, '💯', 'gold'),
('fast_learner', 'Fast Learner', 'Completed training in record time', 150, '⚡', 'silver'),

-- Competency Achievements
('competency_master', 'Competency Master', 'Reached expert level in a competency area', 300, '🏆', 'gold'),
('gap_closer', 'Gap Closer', 'Closed a competency gap', 200, '✅', 'silver'),
('skill_collector', 'Skill Collector', 'Achieved competency in 5+ areas', 400, '🌟', 'platinum'),

-- Contribution Achievements
('content_creator', 'Content Creator', 'Created training content or templates', 50, '✍️', 'bronze'),
('template_master', 'Template Master', 'Created 10+ templates', 250, '📄', 'gold'),
('scenario_expert', 'Scenario Expert', 'Created or reviewed scenarios', 100, '🎯', 'silver'),
('quality_reviewer', 'Quality Reviewer', 'Provided 20+ reviews', 200, '👁️', 'gold'),
('power_user', 'Power User', 'Used system features extensively', 150, '⚙️', 'silver'),
('mentor', 'Mentor', 'Helped others learn and develop', 300, '🤝', 'platinum'),

-- Certification Achievements
('iso_certified', 'ISO 22301 Certified', 'Completed ISO 22301 certification', 1000, '🏅', 'platinum'),
('bc_professional', 'BC Professional', 'Completed advanced BC training', 500, '💼', 'gold'),

-- Team Achievements
('team_player', 'Team Player', 'Participated in team challenges', 75, '👥', 'bronze'),
('department_champion', 'Department Champion', 'Top learner in department', 400, '🥇', 'platinum'),
('awareness_ambassador', 'Awareness Ambassador', 'Promoted BC awareness', 150, '📢', 'silver')
ON CONFLICT (achievement_code) DO NOTHING;

-- ==================== POINTS ACTIONS (21 records) ====================

CREATE TABLE IF NOT EXISTS learning.points_actions (
    id SERIAL PRIMARY KEY,
    action_code VARCHAR(50) NOT NULL UNIQUE,
    action_name VARCHAR(255) NOT NULL,
    description TEXT,
    points_awarded INT NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.points_actions (action_code, action_name, description, points_awarded, category) VALUES
-- Training Actions
('training_start', 'Start Training', 'Enrolled in a training program', 10, 'training'),
('training_complete', 'Complete Training', 'Successfully completed a training program', 100, 'training'),
('assessment_pass', 'Pass Assessment', 'Passed training assessment (70%+)', 50, 'training'),
('assessment_excellence', 'Assessment Excellence', 'Scored 90%+ on assessment', 100, 'training'),
('certification_earned', 'Certification Earned', 'Earned professional certification', 500, 'training'),

-- Competency Actions
('competency_level_up', 'Competency Level Up', 'Advanced to next competency level', 150, 'competency'),
('gap_identified', 'Gap Identified', 'Completed competency assessment', 25, 'competency'),
('gap_closed', 'Gap Closed', 'Closed a competency gap', 200, 'competency'),

-- Awareness Actions
('awareness_participate', 'Awareness Participation', 'Participated in awareness campaign', 25, 'awareness'),
('awareness_survey', 'Survey Completion', 'Completed awareness survey', 15, 'awareness'),

-- Content Actions
('content_create', 'Create Content', 'Created training content', 50, 'content'),
('content_review', 'Review Content', 'Reviewed training material', 10, 'content'),
('content_use', 'Use Content', 'Used training template or scenario', 5, 'content'),
('content_rate', 'Rate Content', 'Rated training material', 3, 'content'),

-- Collaboration Actions
('help_peer', 'Help Peer', 'Assisted another learner', 50, 'collaboration'),
('mentor_session', 'Mentor Session', 'Conducted mentoring session', 75, 'collaboration'),
('team_challenge', 'Team Challenge', 'Completed team learning challenge', 100, 'collaboration'),

-- Engagement Actions
('daily_login', 'Daily Login', 'Logged in to learning platform', 2, 'engagement'),
('streak_milestone', 'Streak Milestone', 'Maintained learning streak', 25, 'engagement'),
('share_knowledge', 'Share Knowledge', 'Shared learning insights', 20, 'engagement')
ON CONFLICT (action_code) DO NOTHING;

-- ==================== BCI TRAINING LEVELS (5 records) ====================

CREATE TABLE IF NOT EXISTS learning.bci_training_levels (
    id SERIAL PRIMARY KEY,
    level_code VARCHAR(50) NOT NULL UNIQUE,
    level_name VARCHAR(255) NOT NULL,
    target_audience VARCHAR(100),
    description TEXT,
    typical_duration_hours INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.bci_training_levels (level_code, level_name, target_audience, description, typical_duration_hours) VALUES
('basic_awareness', 'Basic Awareness', 'all_staff', 'BC importance and individual roles - for all employees', 1),
('intermediate', 'Intermediate Training', 'line_managers', 'BC management for line managers and supervisors', 4),
('advanced', 'Advanced BC Training', 'bc_team', 'Comprehensive BC training for BC team members', 16),
('specialist', 'BC Specialist', 'bc_professionals', 'Expert-level BC professional training', 40),
('leadership', 'BC Leadership', 'executives', 'Strategic BC for senior leadership', 8)
ON CONFLICT (level_code) DO NOTHING;

-- ==================== HEALTHCARE TRAINING TYPES (8 records) ====================

CREATE TABLE IF NOT EXISTS learning.healthcare_training_types (
    id SERIAL PRIMARY KEY,
    training_code VARCHAR(50) NOT NULL UNIQUE,
    training_name VARCHAR(255) NOT NULL,
    description TEXT,
    regulatory_requirement VARCHAR(100),
    frequency VARCHAR(50),
    duration_hours INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.healthcare_training_types (training_code, training_name, description, regulatory_requirement, frequency, duration_hours) VALUES
('emergency_prep_annual', 'Annual Emergency Preparedness', 'CMS-required annual emergency preparedness exercise', 'CMS Emergency Preparedness Rule', 'annual', 4),
('cross_training', 'Clinical Cross-Training', 'Staff cross-training to work multiple units during surge', 'Joint Commission', 'quarterly', 8),
('just_in_time', 'Just-In-Time Training', 'Rapid training for surge capacity and volunteer staff', 'WHO guidelines', 'as_needed', 2),
('hva_training', 'Hazard Vulnerability Assessment', 'Training on conducting HVA for healthcare facilities', 'CMS', 'annual', 4),
('evacuation_drill', 'Evacuation Drill Training', 'Fire, flood, and emergency evacuation procedures', 'Joint Commission', 'quarterly', 1),
('mass_casualty', 'Mass Casualty Incident Response', 'MCI triage and surge capacity training', 'WHO', 'semi_annual', 6),
('pandemic_response', 'Pandemic Response Training', 'Infectious disease outbreak and PPE protocols', 'CDC/WHO', 'annual', 4),
('staff_family_prep', 'Staff Family Preparedness', 'Family preparedness so staff can report during crisis', 'Recommended', 'annual', 2)
ON CONFLICT (training_code) DO NOTHING;

-- ==================== BCI COMPETENCY FRAMEWORK (11 records) ====================

CREATE TABLE IF NOT EXISTS learning.bci_competency_framework (
    id SERIAL PRIMARY KEY,
    competency_code VARCHAR(50) NOT NULL UNIQUE,
    competency_name VARCHAR(255) NOT NULL,
    bci_practice VARCHAR(10),
    description TEXT,
    level_basic TEXT,
    level_intermediate TEXT,
    level_advanced TEXT,
    level_expert TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.bci_competency_framework (competency_code, competency_name, bci_practice, description, level_basic, level_intermediate, level_advanced, level_expert) VALUES
('bc_awareness', 'BC Awareness & Culture', 'PP2', 'Understanding BC importance and organizational BC culture',
    'Knows BC policy exists',
    'Understands own BC role',
    'Promotes BC culture in team',
    'Drives BC culture change'),

('training_delivery', 'Training & Education', 'PP2', 'Delivering BC training and education programs',
    'Completed BC training',
    'Can train others on basic BC',
    'Develops training curriculum',
    'Designs enterprise training strategy'),

('communication', 'BC Communication', 'PP2', 'Internal and external BC communication',
    'Receives BC updates',
    'Communicates BC to team',
    'Manages stakeholder communication',
    'Leads crisis communication'),

('engagement', 'BC Engagement', 'PP2', 'Engaging stakeholders in BC',
    'Participates in BC activities',
    'Engages team in BC',
    'Builds BC champions network',
    'Drives organizational BC engagement'),

('policy_governance', 'Policy & Governance', 'PP1', 'BC policy and governance understanding',
    'Aware of BC policy',
    'Applies BC policy',
    'Contributes to policy development',
    'Owns BC governance framework'),

('bia_execution', 'BIA Execution', 'PP3', 'Business impact analysis skills',
    'Provides BIA input',
    'Facilitates BIA workshops',
    'Leads BIA projects',
    'Designs BIA methodology'),

('risk_assessment', 'Risk Assessment', 'PP3', 'BC risk assessment capabilities',
    'Identifies risks',
    'Assesses risks',
    'Leads risk assessments',
    'Develops risk frameworks'),

('strategy_design', 'BC Strategy Design', 'PP4', 'Developing BC strategies',
    'Understands BC strategies',
    'Implements BC strategies',
    'Designs BC strategies',
    'Leads strategic BC planning'),

('plan_development', 'BC Plan Development', 'PP5', 'Creating BC plans',
    'Knows BC plans exist',
    'Uses BC plans',
    'Writes BC plans',
    'Designs BC planning framework'),

('exercise_management', 'Exercise & Testing', 'PP6', 'BC exercise and testing',
    'Participates in exercises',
    'Facilitates tabletop exercises',
    'Designs exercise programs',
    'Leads enterprise exercise strategy'),

('continuous_improvement', 'BC Improvement', 'PP6', 'Continuous improvement of BC',
    'Provides feedback',
    'Implements improvements',
    'Leads improvement projects',
    'Drives BC maturity advancement')
ON CONFLICT (competency_code) DO NOTHING;

-- ==================== AWARENESS CAMPAIGN TYPES (8 records) ====================

CREATE TABLE IF NOT EXISTS learning.awareness_campaign_types (
    id SERIAL PRIMARY KEY,
    campaign_code VARCHAR(50) NOT NULL UNIQUE,
    campaign_name VARCHAR(255) NOT NULL,
    description TEXT,
    target_audience VARCHAR(100),
    recommended_frequency VARCHAR(50),
    communication_channels TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.awareness_campaign_types (campaign_code, campaign_name, description, target_audience, recommended_frequency, communication_channels) VALUES
('bc_importance', 'BC Importance Campaign', 'Communicate why BC matters to the organization', 'all_staff', 'quarterly', ARRAY['email', 'intranet', 'posters', 'town_halls']),
('individual_roles', 'Individual BC Roles', 'Explain individual roles and responsibilities in BC', 'all_staff', 'semi_annual', ARRAY['email', 'team_meetings', 'training']),
('leadership_visibility', 'Leadership BC Visibility', 'Demonstrate management commitment to BC', 'all_staff', 'quarterly', ARRAY['video_messages', 'town_halls', 'newsletters']),
('bc_champions', 'BC Champions Recognition', 'Recognize and celebrate BC champions', 'all_staff', 'monthly', ARRAY['intranet', 'awards', 'newsletters']),
('lessons_learned', 'Lessons Learned Sharing', 'Share insights from exercises and incidents', 'bc_team', 'after_each_event', ARRAY['debriefs', 'reports', 'presentations']),
('new_hire_orientation', 'New Employee BC Orientation', 'BC introduction for new hires', 'new_employees', 'continuous', ARRAY['onboarding', 'elearning', 'handbook']),
('seasonal_reminders', 'Seasonal BC Reminders', 'Seasonal hazard awareness (hurricane, flu season)', 'all_staff', 'seasonal', ARRAY['email', 'posters', 'alerts']),
('bc_week', 'Business Continuity Awareness Week', 'Annual BC awareness campaign week', 'all_staff', 'annual', ARRAY['events', 'intranet', 'activities', 'swag'])
ON CONFLICT (campaign_code) DO NOTHING;

-- ==================== ASSESSMENT METHODS (10 records) ====================

CREATE TABLE IF NOT EXISTS learning.assessment_methods (
    id SERIAL PRIMARY KEY,
    method_code VARCHAR(50) NOT NULL UNIQUE,
    method_name VARCHAR(255) NOT NULL,
    description TEXT,
    assessment_type VARCHAR(50),
    passing_score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.assessment_methods (method_code, method_name, description, assessment_type, passing_score) VALUES
('multiple_choice', 'Multiple Choice Quiz', 'Standard multiple choice assessment', 'knowledge', 70),
('scenario_based', 'Scenario-Based Assessment', 'Real-world scenario problem-solving', 'application', 75),
('practical_demo', 'Practical Demonstration', 'Hands-on demonstration of skills', 'skill', 80),
('tabletop_exercise', 'Tabletop Exercise Performance', 'Performance during tabletop exercise', 'competency', 70),
('peer_review', 'Peer Review', 'Assessment by peers or supervisor', 'competency', 75),
('self_assessment', 'Self-Assessment', 'Individual competency self-evaluation', 'awareness', 60),
('simulation', 'Simulation Exercise', 'Performance in simulation scenario', 'competency', 80),
('written_assignment', 'Written Assignment', 'Case study or plan development', 'application', 75),
('oral_examination', 'Oral Examination', 'Verbal Q&A with assessor', 'knowledge', 70),
('portfolio', 'Competency Portfolio', 'Collection of evidence over time', 'competency', 75)
ON CONFLICT (method_code) DO NOTHING;

-- ==================== TRAINING KPIs (10 records) ====================

CREATE TABLE IF NOT EXISTS learning.training_kpis (
    id SERIAL PRIMARY KEY,
    kpi_code VARCHAR(50) NOT NULL UNIQUE,
    kpi_name VARCHAR(255) NOT NULL,
    description TEXT,
    measurement_method TEXT,
    target_value VARCHAR(50),
    reporting_frequency VARCHAR(50),
    iso_clause VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO learning.training_kpis (kpi_code, kpi_name, description, measurement_method, target_value, reporting_frequency, iso_clause) VALUES
('training_completion', 'Training Completion Rate', 'Percentage of required training completed', '(Completed / Required) * 100', '≥95%', 'monthly', '7.2'),
('awareness_participation', 'Awareness Campaign Participation', 'Engagement rate in awareness activities', '(Participants / Total Staff) * 100', '≥80%', 'quarterly', '7.3'),
('competency_gap_closure', 'Competency Gap Closure Rate', 'Rate at which competency gaps are closed', '(Gaps Closed / Total Gaps) * 100', '≥70%', 'quarterly', '7.2'),
('exercise_participation', 'Exercise Participation Rate', 'Staff participation in BC exercises', '(Exercise Participants / BC Team) * 100', '≥90%', 'quarterly', '8.5'),
('certification_achievement', 'Professional Certification Rate', 'Percentage of BC team with certifications', '(Certified / BC Team) * 100', '≥50%', 'annual', '7.2'),
('training_effectiveness', 'Training Effectiveness Score', 'Post-training assessment average scores', 'Average assessment score', '≥80%', 'per_training', '7.2'),
('time_to_competency', 'Time to Achieve Competency', 'Average time to reach target competency level', 'Average days from start to competent', '≤90 days', 'quarterly', '7.2'),
('training_satisfaction', 'Training Satisfaction Score', 'Participant satisfaction with training', 'Average satisfaction survey score (1-5)', '≥4.0', 'per_training', '7.2'),
('overdue_training', 'Overdue Training Count', 'Number of staff with overdue required training', 'Count of overdue assignments', '≤5%', 'weekly', '7.2'),
('new_hire_completion', 'New Hire BC Training Completion', 'New employees completing BC orientation within 30 days', '(Completed / New Hires) * 100', '100%', 'monthly', '7.3')
ON CONFLICT (kpi_code) DO NOTHING;

-- ==================== PART 3: INDEXES ====================

-- Core Tables Indexes
CREATE INDEX IF NOT EXISTS idx_programs_tenant_status ON learning.training_programs(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_programs_type ON learning.training_programs(program_type);
CREATE INDEX IF NOT EXISTS idx_programs_code ON learning.training_programs(program_code);

CREATE INDEX IF NOT EXISTS idx_enrollments_tenant_person ON learning.training_enrollments(tenant_id, person_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status ON learning.training_enrollments(status);
CREATE INDEX IF NOT EXISTS idx_enrollments_program ON learning.training_enrollments(program_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_due_date ON learning.training_enrollments(due_date);

CREATE INDEX IF NOT EXISTS idx_competency_tenant_person ON learning.competency_assessments(tenant_id, person_id);
CREATE INDEX IF NOT EXISTS idx_competency_area ON learning.competency_assessments(competency_area);
CREATE INDEX IF NOT EXISTS idx_competency_gap ON learning.competency_assessments(gap_exists);
CREATE INDEX IF NOT EXISTS idx_competency_status ON learning.competency_assessments(status);

CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_status ON learning.awareness_campaigns(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_campaigns_type ON learning.awareness_campaigns(campaign_type);
CREATE INDEX IF NOT EXISTS idx_campaigns_code ON learning.awareness_campaigns(campaign_code);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON learning.awareness_campaigns(start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_templates_tenant_active ON learning.training_templates(tenant_id, is_active);
CREATE INDEX IF NOT EXISTS idx_templates_type ON learning.training_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_templates_code ON learning.training_templates(template_code);

CREATE INDEX IF NOT EXISTS idx_achievements_tenant_person ON learning.user_achievements(tenant_id, person_id);
CREATE INDEX IF NOT EXISTS idx_achievements_code ON learning.user_achievements(achievement_code);
CREATE INDEX IF NOT EXISTS idx_achievements_date ON learning.user_achievements(earned_date);

-- Reference Tables Indexes
CREATE INDEX IF NOT EXISTS idx_competency_areas_code ON learning.competency_areas(area_code);
CREATE INDEX IF NOT EXISTS idx_learning_styles_code ON learning.learning_styles(style_code);
CREATE INDEX IF NOT EXISTS idx_program_types_code ON learning.program_types(type_code);
CREATE INDEX IF NOT EXISTS idx_template_types_code ON learning.template_types(type_code);
CREATE INDEX IF NOT EXISTS idx_scenario_categories_code ON learning.scenario_categories(category_code);
CREATE INDEX IF NOT EXISTS idx_achievement_types_code ON learning.achievement_types(achievement_code);
CREATE INDEX IF NOT EXISTS idx_points_actions_code ON learning.points_actions(action_code);
CREATE INDEX IF NOT EXISTS idx_bci_training_levels_code ON learning.bci_training_levels(level_code);
CREATE INDEX IF NOT EXISTS idx_healthcare_training_code ON learning.healthcare_training_types(training_code);
CREATE INDEX IF NOT EXISTS idx_bci_competency_code ON learning.bci_competency_framework(competency_code);
CREATE INDEX IF NOT EXISTS idx_awareness_campaign_code ON learning.awareness_campaign_types(campaign_code);
CREATE INDEX IF NOT EXISTS idx_assessment_methods_code ON learning.assessment_methods(method_code);
CREATE INDEX IF NOT EXISTS idx_training_kpis_code ON learning.training_kpis(kpi_code);

-- ==================== PART 4: ROW LEVEL SECURITY ====================

-- Enable RLS on all core tables
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

-- ==================== PART 5: TRIGGERS ====================

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

-- ==================== PART 6: VIEWS ====================

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

-- Seed Data Summary
CREATE OR REPLACE VIEW learning.seed_data_summary AS
SELECT 'Competency Areas' as data_type, COUNT(*) as record_count FROM learning.competency_areas
UNION ALL SELECT 'Learning Styles', COUNT(*) FROM learning.learning_styles
UNION ALL SELECT 'Program Types', COUNT(*) FROM learning.program_types
UNION ALL SELECT 'Template Types', COUNT(*) FROM learning.template_types
UNION ALL SELECT 'Scenario Categories', COUNT(*) FROM learning.scenario_categories
UNION ALL SELECT 'Achievement Types', COUNT(*) FROM learning.achievement_types
UNION ALL SELECT 'Points Actions', COUNT(*) FROM learning.points_actions
UNION ALL SELECT 'BCI Training Levels', COUNT(*) FROM learning.bci_training_levels
UNION ALL SELECT 'Healthcare Training Types', COUNT(*) FROM learning.healthcare_training_types
UNION ALL SELECT 'BCI Competency Framework', COUNT(*) FROM learning.bci_competency_framework
UNION ALL SELECT 'Awareness Campaign Types', COUNT(*) FROM learning.awareness_campaign_types
UNION ALL SELECT 'Assessment Methods', COUNT(*) FROM learning.assessment_methods
UNION ALL SELECT 'Training KPIs', COUNT(*) FROM learning.training_kpis;

-- ==================== PART 7: COMMENTS ====================

COMMENT ON SCHEMA learning IS 'Learning & Development module - ISO 22301 Clause 7.2 & 7.3, BCI GPG PP2';

-- Core Tables
COMMENT ON TABLE learning.training_programs IS 'BC training programs (ISO 7.2)';
COMMENT ON TABLE learning.training_enrollments IS 'Individual training enrollments and progress tracking';
COMMENT ON TABLE learning.competency_assessments IS 'Competency assessments and gap analysis (ISO 7.2)';
COMMENT ON TABLE learning.awareness_campaigns IS 'BC awareness campaigns (ISO 7.3, BCI GPG PP2)';
COMMENT ON TABLE learning.training_templates IS 'Training templates, forms, and checklists library';
COMMENT ON TABLE learning.user_achievements IS 'Gamification: user achievements, points, badges';

-- Reference Tables
COMMENT ON TABLE learning.competency_areas IS 'BCM competency areas (10 records)';
COMMENT ON TABLE learning.learning_styles IS 'Learning styles and coaching approaches (6 records)';
COMMENT ON TABLE learning.program_types IS 'Training program types (8 records)';
COMMENT ON TABLE learning.template_types IS 'Training templates and forms (14 records)';
COMMENT ON TABLE learning.scenario_categories IS 'Training scenario categories (10 records)';
COMMENT ON TABLE learning.achievement_types IS 'Gamification achievements (19 records)';
COMMENT ON TABLE learning.points_actions IS 'Gamification points system (21 records)';
COMMENT ON TABLE learning.bci_training_levels IS 'BCI GPG PP2: BC training levels (5 records)';
COMMENT ON TABLE learning.healthcare_training_types IS 'WHO/CMS healthcare-specific training (8 records)';
COMMENT ON TABLE learning.bci_competency_framework IS 'BCI GPG competency framework (11 records)';
COMMENT ON TABLE learning.awareness_campaign_types IS 'BCI GPG PP2: Awareness campaign templates (8 records)';
COMMENT ON TABLE learning.assessment_methods IS 'Training assessment methods (10 records)';
COMMENT ON TABLE learning.training_kpis IS 'BCI GPG PP6: Training KPIs (10 records)';

-- Views
COMMENT ON VIEW learning.training_progress_overview IS 'Training completion statistics by tenant';
COMMENT ON VIEW learning.competency_gap_summary IS 'Competency gaps by area and severity';
COMMENT ON VIEW learning.campaign_effectiveness IS 'Awareness campaign participation and effectiveness';
COMMENT ON VIEW learning.points_leaderboard IS 'Gamification leaderboard by tenant';
COMMENT ON VIEW learning.seed_data_summary IS 'Summary of all seed data (140 total records)';

-- ==================================================================================
-- MIGRATION COMPLETE
-- ==================================================================================
-- Created: 6 core tables + 13 reference tables = 19 tables
-- Inserted: 140 seed records (88 + 52)
-- Created: 4 views for analytics
-- Enabled: Row Level Security with tenant isolation
-- ==================================================================================
