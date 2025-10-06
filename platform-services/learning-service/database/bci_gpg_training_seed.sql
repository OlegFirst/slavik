-- BCI GPG Practice 2 (PP2): Embracing BC - Training Module Seed Data
-- Source: /services/knowledge-base/standards/BCI_GPG/six_practices.md
-- Source: /services/knowledge-base/standards/WHO/health_emergency_bcm.md
-- ISO 22301 Clause 7.2 (Competence) & 7.3 (Awareness)

-------------------
-- BCI TRAINING LEVELS
-------------------

CREATE TABLE IF NOT EXISTS learning.bci_training_levels (
    id SERIAL PRIMARY KEY,
    level_code VARCHAR(50) NOT NULL UNIQUE,
    level_name VARCHAR(255) NOT NULL,
    target_audience VARCHAR(100),
    description TEXT,
    typical_duration_hours INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed BCI training levels (from BCI GPG PP2)
INSERT INTO learning.bci_training_levels (level_code, level_name, target_audience, description, typical_duration_hours) VALUES
('basic_awareness', 'Basic Awareness', 'all_staff', 'BC importance and individual roles - for all employees', 1),
('intermediate', 'Intermediate Training', 'line_managers', 'BC management for line managers and supervisors', 4),
('advanced', 'Advanced BC Training', 'bc_team', 'Comprehensive BC training for BC team members', 16),
('specialist', 'BC Specialist', 'bc_professionals', 'Expert-level BC professional training', 40),
('leadership', 'BC Leadership', 'executives', 'Strategic BC for senior leadership', 8)
ON CONFLICT (level_code) DO NOTHING;

-------------------
-- HEALTHCARE TRAINING (WHO)
-------------------

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

-- Seed healthcare-specific training (from WHO health_emergency_bcm.md)
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

-------------------
-- BCI COMPETENCY FRAMEWORK
-------------------

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

-- Seed BCI competency framework (from BCI GPG PP2)
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

-------------------
-- AWARENESS CAMPAIGN TYPES
-------------------

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

-- Seed awareness campaign types (from BCI GPG PP2)
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

-------------------
-- TRAINING ASSESSMENT METHODS
-------------------

CREATE TABLE IF NOT EXISTS learning.assessment_methods (
    id SERIAL PRIMARY KEY,
    method_code VARCHAR(50) NOT NULL UNIQUE,
    method_name VARCHAR(255) NOT NULL,
    description TEXT,
    assessment_type VARCHAR(50),
    passing_score INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed assessment methods
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

-------------------
-- KPIs FOR TRAINING (from BCI GPG PP6)
-------------------

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

-- Seed training KPIs (from BCI GPG PP6 + WHO)
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

-------------------
-- INDEXES
-------------------

CREATE INDEX IF NOT EXISTS idx_bci_training_levels_code ON learning.bci_training_levels(level_code);
CREATE INDEX IF NOT EXISTS idx_healthcare_training_code ON learning.healthcare_training_types(training_code);
CREATE INDEX IF NOT EXISTS idx_bci_competency_code ON learning.bci_competency_framework(competency_code);
CREATE INDEX IF NOT EXISTS idx_awareness_campaign_code ON learning.awareness_campaign_types(campaign_code);
CREATE INDEX IF NOT EXISTS idx_assessment_methods_code ON learning.assessment_methods(method_code);
CREATE INDEX IF NOT EXISTS idx_training_kpis_code ON learning.training_kpis(kpi_code);

-------------------
-- COMMENTS
-------------------

COMMENT ON TABLE learning.bci_training_levels IS 'BCI GPG PP2: BC training levels (Basic to Expert)';
COMMENT ON TABLE learning.healthcare_training_types IS 'WHO/CMS healthcare-specific training requirements';
COMMENT ON TABLE learning.bci_competency_framework IS 'BCI GPG competency framework across 6 Professional Practices';
COMMENT ON TABLE learning.awareness_campaign_types IS 'BCI GPG PP2: Awareness campaign templates';
COMMENT ON TABLE learning.assessment_methods IS 'Training assessment and evaluation methods';
COMMENT ON TABLE learning.training_kpis IS 'BCI GPG PP6: Key Performance Indicators for training';

-- Summary View
CREATE OR REPLACE VIEW learning.bci_seed_summary AS
SELECT
    'BCI Training Levels' as data_type,
    COUNT(*) as record_count
FROM learning.bci_training_levels
UNION ALL
SELECT 'Healthcare Training Types', COUNT(*) FROM learning.healthcare_training_types
UNION ALL
SELECT 'BCI Competency Framework', COUNT(*) FROM learning.bci_competency_framework
UNION ALL
SELECT 'Awareness Campaign Types', COUNT(*) FROM learning.awareness_campaign_types
UNION ALL
SELECT 'Assessment Methods', COUNT(*) FROM learning.assessment_methods
UNION ALL
SELECT 'Training KPIs', COUNT(*) FROM learning.training_kpis;

-- Expected output:
-- BCI Training Levels: 5
-- Healthcare Training Types: 8
-- BCI Competency Framework: 11
-- Awareness Campaign Types: 8
-- Assessment Methods: 10
-- Training KPIs: 10
-- TOTAL: 52 seed records
