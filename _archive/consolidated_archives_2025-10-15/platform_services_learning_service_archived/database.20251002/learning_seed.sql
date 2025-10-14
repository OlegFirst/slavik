-- Learning Module Seed Data
-- Extracted from BCM_1: bcm_training, bcm_templates, bcm_content_training_bridge
-- ISO 22301 Clause 7.2 (Competence) & 7.3 (Awareness)

-- Create Learning schema
CREATE SCHEMA IF NOT EXISTS learning;

-------------------
-- COMPETENCY AREAS
-------------------

CREATE TABLE IF NOT EXISTS learning.competency_areas (
    id SERIAL PRIMARY KEY,
    area_code VARCHAR(50) NOT NULL UNIQUE,
    area_name VARCHAR(255) NOT NULL,
    description TEXT,
    iso_clause VARCHAR(20),
    level_count INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed competency areas (from bcm_training/ai_learning_coach.py)
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

-------------------
-- LEARNING STYLES
-------------------

CREATE TABLE IF NOT EXISTS learning.learning_styles (
    id SERIAL PRIMARY KEY,
    style_code VARCHAR(50) NOT NULL UNIQUE,
    style_name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed learning styles (from bcm_training/ai_learning_coach.py)
INSERT INTO learning.learning_styles (style_code, style_name, description, icon) VALUES
('adaptive', 'Adaptive - Personalized Learning', 'AI-powered adaptive learning paths based on individual progress and preferences', '🎯'),
('intensive', 'Intensive - Accelerated Training', 'Fast-paced, concentrated learning for rapid skill acquisition', '🔥'),
('supportive', 'Supportive - Guided Learning', 'Structured guidance with mentor support and checkpoints', '🤝'),
('challenging', 'Challenging - Advanced Training', 'Advanced scenarios and complex problem-solving for experts', '💪'),
('self_paced', 'Self-Paced Learning', 'Learn at your own pace with flexible scheduling', '⏱️'),
('collaborative', 'Collaborative Learning', 'Team-based learning with peer interaction', '👥')
ON CONFLICT (style_code) DO NOTHING;

-------------------
-- TRAINING PROGRAM TYPES
-------------------

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

-- Seed program types (from bcm_training/__manifest__.py)
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

-------------------
-- TEMPLATE TYPES
-------------------

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

-- Seed template types (from bcm_templates/models/models.py)
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

-------------------
-- SCENARIO CATEGORIES
-------------------

CREATE TABLE IF NOT EXISTS learning.scenario_categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) NOT NULL UNIQUE,
    category_name VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(20),
    icon VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed scenario categories (from bcm_content_training_bridge)
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

-------------------
-- GAMIFICATION: ACHIEVEMENT TYPES
-------------------

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

-- Seed achievement types (from gamification_bridge.py + custom)
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

-------------------
-- GAMIFICATION: POINTS ACTIONS
-------------------

CREATE TABLE IF NOT EXISTS learning.points_actions (
    id SERIAL PRIMARY KEY,
    action_code VARCHAR(50) NOT NULL UNIQUE,
    action_name VARCHAR(255) NOT NULL,
    description TEXT,
    points_awarded INT NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed points actions (from gamification_bridge.py + enhanced)
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

-------------------
-- INDEXES
-------------------

CREATE INDEX IF NOT EXISTS idx_competency_areas_code ON learning.competency_areas(area_code);
CREATE INDEX IF NOT EXISTS idx_learning_styles_code ON learning.learning_styles(style_code);
CREATE INDEX IF NOT EXISTS idx_program_types_code ON learning.program_types(type_code);
CREATE INDEX IF NOT EXISTS idx_template_types_code ON learning.template_types(type_code);
CREATE INDEX IF NOT EXISTS idx_scenario_categories_code ON learning.scenario_categories(category_code);
CREATE INDEX IF NOT EXISTS idx_achievement_types_code ON learning.achievement_types(achievement_code);
CREATE INDEX IF NOT EXISTS idx_points_actions_code ON learning.points_actions(action_code);

-------------------
-- COMMENTS
-------------------

COMMENT ON SCHEMA learning IS 'Learning & Development module - ISO 22301 Clause 7.2 & 7.3';
COMMENT ON TABLE learning.competency_areas IS 'BCM competency areas (extracted from bcm_training/ai_learning_coach.py)';
COMMENT ON TABLE learning.learning_styles IS 'Learning styles and coaching approaches (extracted from bcm_training)';
COMMENT ON TABLE learning.program_types IS 'Training program types (extracted from bcm_training/__manifest__.py)';
COMMENT ON TABLE learning.template_types IS 'Training templates and forms (extracted from bcm_templates)';
COMMENT ON TABLE learning.scenario_categories IS 'Training scenario categories (extracted from bcm_content_training_bridge)';
COMMENT ON TABLE learning.achievement_types IS 'Gamification achievements (extracted from gamification_bridge.py)';
COMMENT ON TABLE learning.points_actions IS 'Gamification points system (extracted from gamification_bridge.py + enhanced)';

-- Summary View
CREATE OR REPLACE VIEW learning.seed_data_summary AS
SELECT
    'Competency Areas' as data_type,
    COUNT(*) as record_count
FROM learning.competency_areas
UNION ALL
SELECT 'Learning Styles', COUNT(*) FROM learning.learning_styles
UNION ALL
SELECT 'Program Types', COUNT(*) FROM learning.program_types
UNION ALL
SELECT 'Template Types', COUNT(*) FROM learning.template_types
UNION ALL
SELECT 'Scenario Categories', COUNT(*) FROM learning.scenario_categories
UNION ALL
SELECT 'Achievement Types', COUNT(*) FROM learning.achievement_types
UNION ALL
SELECT 'Points Actions', COUNT(*) FROM learning.points_actions;

-- Expected output:
-- Competency Areas: 10
-- Learning Styles: 6
-- Program Types: 8
-- Template Types: 14
-- Scenario Categories: 10
-- Achievement Types: 19
-- Points Actions: 21
-- TOTAL: 88 seed records
