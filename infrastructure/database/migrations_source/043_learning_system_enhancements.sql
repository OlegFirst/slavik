-- =====================================================
-- Learning System Enhancements Migration
-- =====================================================
-- Phase 1: Competency Tracking + Process Gap Analysis + Gamification Foundation
-- Integrates with existing learning.exercise_results, learning.patterns, learning.scenario_learning

-- =====================================================
-- 1. COMPETENCY TRACKING SYSTEM
-- =====================================================

-- Individual competency profiles
CREATE TABLE IF NOT EXISTS learning.user_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tenant_id TEXT NOT NULL,

    -- Core BCM competencies
    bia_execution_score DECIMAL(5,2) DEFAULT 0,
    bia_exercise_count INTEGER DEFAULT 0,

    risk_assessment_score DECIMAL(5,2) DEFAULT 0,
    risk_exercise_count INTEGER DEFAULT 0,

    exercise_facilitation_score DECIMAL(5,2) DEFAULT 0,
    exercises_facilitated INTEGER DEFAULT 0,

    audit_management_score DECIMAL(5,2) DEFAULT 0,
    audits_participated INTEGER DEFAULT 0,

    plan_development_score DECIMAL(5,2) DEFAULT 0,
    plans_created INTEGER DEFAULT 0,

    incident_response_score DECIMAL(5,2) DEFAULT 0,
    incidents_handled INTEGER DEFAULT 0,

    -- Scenario-specific competencies (JSON)
    scenario_competencies JSONB DEFAULT '{}'::jsonb,
    -- Example: {"cyber": 85, "supply_chain": 72, "natural_disaster": 90}

    -- Certification tracking
    certifications JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"name": "CBCP", "issued": "2024-01-15", "expires": "2027-01-15"}]

    -- Skills decay tracking
    last_exercise_date TIMESTAMP,
    decay_risk_level TEXT CHECK (decay_risk_level IN ('low', 'medium', 'high', 'critical')),
    days_since_last_exercise INTEGER DEFAULT 0,

    -- Overall metrics
    total_exercises INTEGER DEFAULT 0,
    avg_exercise_score DECIMAL(5,2) DEFAULT 0,
    improvement_trend DECIMAL(5,2) DEFAULT 0, -- Positive = improving

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT user_competencies_user_tenant_unique UNIQUE (user_id, tenant_id)
);

CREATE INDEX idx_user_competencies_user ON learning.user_competencies(user_id);
CREATE INDEX idx_user_competencies_tenant ON learning.user_competencies(tenant_id);
CREATE INDEX idx_user_competencies_decay_risk ON learning.user_competencies(decay_risk_level);

-- Team competency matrix
CREATE TABLE IF NOT EXISTS learning.team_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    team_name TEXT NOT NULL,

    -- Capability coverage
    capability_name TEXT NOT NULL, -- e.g., "BIA Execution", "Exercise Facilitation"
    primary_user_id UUID,
    backup_user_ids UUID[],

    -- Coverage metrics
    primary_competency_score DECIMAL(5,2),
    backup_competency_scores JSONB DEFAULT '{}'::jsonb,
    -- Example: {"user_uuid_1": 75, "user_uuid_2": 68}

    coverage_status TEXT CHECK (coverage_status IN ('strong', 'adequate', 'weak', 'none')),
    gap_severity TEXT CHECK (gap_severity IN ('critical', 'high', 'medium', 'low', 'none')),

    -- Recommendations
    training_needed_for UUID[], -- Array of user IDs needing training
    recommended_actions JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT team_competencies_unique UNIQUE (tenant_id, team_name, capability_name)
);

CREATE INDEX idx_team_competencies_tenant ON learning.team_competencies(tenant_id);
CREATE INDEX idx_team_competencies_coverage ON learning.team_competencies(coverage_status);
CREATE INDEX idx_team_competencies_gap ON learning.team_competencies(gap_severity);

-- =====================================================
-- 2. PROCESS-BASED GAP ANALYSIS
-- =====================================================

-- BCM Process definitions
CREATE TABLE IF NOT EXISTS learning.bcm_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,

    process_name TEXT NOT NULL,
    process_category TEXT NOT NULL, -- "incident_response", "recovery", "communication", etc.

    -- Process steps (ordered)
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [{"order": 1, "name": "Detect incident", "required": true}, ...]

    -- ISO 22301 mapping
    iso_clause TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT bcm_processes_unique UNIQUE (tenant_id, process_name)
);

CREATE INDEX idx_bcm_processes_tenant ON learning.bcm_processes(tenant_id);
CREATE INDEX idx_bcm_processes_category ON learning.bcm_processes(process_category);

-- Process coverage from exercises
CREATE TABLE IF NOT EXISTS learning.process_coverage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    process_id UUID REFERENCES learning.bcm_processes(id) ON DELETE CASCADE,
    scenario_type TEXT NOT NULL,

    -- Coverage metrics per process step
    step_coverage JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Example: {"step_1": {"tested": 10, "success": 8, "success_rate": 80}, ...}

    -- Overall process metrics
    total_exercises INTEGER DEFAULT 0,
    avg_success_rate DECIMAL(5,2) DEFAULT 0,

    -- Gap identification
    gaps_identified JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"step": "Activate backup systems", "success_rate": 40, "severity": "critical"}]

    gap_score DECIMAL(5,2) DEFAULT 0, -- 0 = many gaps, 100 = no gaps

    -- Recommendations
    improvement_priorities JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    last_analyzed TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT process_coverage_unique UNIQUE (tenant_id, process_id, scenario_type)
);

CREATE INDEX idx_process_coverage_tenant ON learning.process_coverage(tenant_id);
CREATE INDEX idx_process_coverage_process ON learning.process_coverage(process_id);
CREATE INDEX idx_process_coverage_gap_score ON learning.process_coverage(gap_score);

-- Role-specific competency gaps
CREATE TABLE IF NOT EXISTS learning.role_competency_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    role_name TEXT NOT NULL,

    -- Required vs actual competencies
    required_competencies JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Example: {"bia_execution": 80, "risk_assessment": 75}

    actual_competencies JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Aggregated from user_competencies for this role

    -- Gap analysis
    competency_gaps JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"competency": "audit_management", "required": 80, "actual": 45, "gap": 35}]

    critical_gaps INTEGER DEFAULT 0,
    high_gaps INTEGER DEFAULT 0,

    -- Users in this role
    user_ids UUID[],
    user_count INTEGER DEFAULT 0,

    -- Recommendations
    training_plan JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    analyzed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT role_gaps_unique UNIQUE (tenant_id, role_name)
);

CREATE INDEX idx_role_gaps_tenant ON learning.role_competency_gaps(tenant_id);
CREATE INDEX idx_role_gaps_critical ON learning.role_competency_gaps(critical_gaps);

-- =====================================================
-- 3. GAMIFICATION SYSTEM
-- =====================================================

-- User gamification profile
CREATE TABLE IF NOT EXISTS learning.gamification_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tenant_id TEXT NOT NULL,

    -- Points and levels
    total_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    level_name TEXT DEFAULT 'Novice',
    points_to_next_level INTEGER DEFAULT 500,

    -- Badges earned
    badges JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"badge_id": "first_timer", "earned_at": "2025-01-15", "category": "frequency"}]

    badge_count INTEGER DEFAULT 0,

    -- Streaks
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    last_activity_date DATE,

    -- Leaderboard stats
    rank_overall INTEGER,
    rank_team INTEGER,
    percentile DECIMAL(5,2),

    -- Achievements
    achievements JSONB DEFAULT '[]'::jsonb,
    achievement_count INTEGER DEFAULT 0,

    -- Activity summary
    exercises_completed INTEGER DEFAULT 0,
    patterns_resolved INTEGER DEFAULT 0,
    knowledge_contributions INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT gamification_profiles_user_tenant_unique UNIQUE (user_id, tenant_id)
);

CREATE INDEX idx_gamification_user ON learning.gamification_profiles(user_id);
CREATE INDEX idx_gamification_tenant ON learning.gamification_profiles(tenant_id);
CREATE INDEX idx_gamification_points ON learning.gamification_profiles(total_points DESC);
CREATE INDEX idx_gamification_level ON learning.gamification_profiles(level DESC);

-- Badge definitions
CREATE TABLE IF NOT EXISTS learning.badge_definitions (
    id TEXT PRIMARY KEY, -- e.g., "first_timer", "exercise_champion"
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL, -- "frequency", "performance", "improvement", "specialty", "team", "streak"

    -- Criteria for earning
    criteria JSONB NOT NULL,
    -- Example: {"exercises_completed": 1} or {"score_threshold": 90, "exercise_type": "cyber"}

    icon_url TEXT,
    color TEXT,
    rarity TEXT CHECK (rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary')),

    points_awarded INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Achievement definitions
CREATE TABLE IF NOT EXISTS learning.achievement_definitions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    -- Multi-step achievements
    milestones JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"step": 1, "requirement": "Complete 5 exercises", "points": 50}, ...]

    total_steps INTEGER DEFAULT 1,
    total_points INTEGER DEFAULT 0,

    category TEXT,
    icon_url TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Leaderboards
CREATE TABLE IF NOT EXISTS learning.leaderboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,

    leaderboard_type TEXT NOT NULL, -- "global", "team", "monthly", "scenario_specific"
    period TEXT, -- "all_time", "2025-01", "Q1-2025"
    scenario_type TEXT, -- For scenario-specific leaderboards

    -- Rankings (JSON array for performance)
    rankings JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [{"rank": 1, "user_id": "...", "score": 5000, "badges": 15}, ...]

    -- Metadata
    generated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT leaderboards_unique UNIQUE (tenant_id, leaderboard_type, period, scenario_type)
);

CREATE INDEX idx_leaderboards_tenant ON learning.leaderboards(tenant_id);
CREATE INDEX idx_leaderboards_type ON learning.leaderboards(leaderboard_type);

-- =====================================================
-- 4. KNOWLEDGE BASE INTEGRATION
-- =====================================================

-- Gap to Knowledge mappings
CREATE TABLE IF NOT EXISTS learning.gap_knowledge_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Gap identification
    gap_keyword TEXT NOT NULL, -- e.g., "slow escalation", "unclear communication"
    gap_category TEXT, -- "process", "technical", "communication", "coordination"

    -- Knowledge base references
    knowledge_article_ids UUID[], -- References to knowledge base articles
    learning_path_id UUID, -- Reference to structured learning path

    -- Resources
    recommended_resources JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"type": "article", "id": "...", "title": "...", "priority": 1}, ...]

    -- Effectiveness tracking
    times_recommended INTEGER DEFAULT 0,
    resolution_count INTEGER DEFAULT 0, -- How many times this helped resolve the gap
    effectiveness_score DECIMAL(5,2) DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT gap_knowledge_unique UNIQUE (gap_keyword)
);

CREATE INDEX idx_gap_knowledge_keyword ON learning.gap_knowledge_mappings(gap_keyword);
CREATE INDEX idx_gap_knowledge_effectiveness ON learning.gap_knowledge_mappings(effectiveness_score DESC);

-- Learning paths
CREATE TABLE IF NOT EXISTS learning.learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    path_name TEXT NOT NULL,
    description TEXT,

    -- Target audience
    target_competency TEXT, -- "bia_execution", "cyber_response", etc.
    target_score_range TEXT, -- "0-50", "50-75", "75-100"

    -- Path steps (ordered)
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [
    --   {"order": 1, "type": "read", "resource_id": "...", "duration_minutes": 20},
    --   {"order": 2, "type": "watch", "resource_id": "...", "duration_minutes": 15},
    --   {"order": 3, "type": "practice", "exercise_id": "...", "duration_minutes": 60}
    -- ]

    total_duration_minutes INTEGER,
    estimated_improvement DECIMAL(5,2), -- Expected score improvement

    -- Usage stats
    times_assigned INTEGER DEFAULT 0,
    completion_rate DECIMAL(5,2) DEFAULT 0,
    avg_improvement DECIMAL(5,2) DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_learning_paths_competency ON learning.learning_paths(target_competency);

-- User learning path progress
CREATE TABLE IF NOT EXISTS learning.user_learning_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    learning_path_id UUID REFERENCES learning.learning_paths(id) ON DELETE CASCADE,

    -- Progress tracking
    current_step INTEGER DEFAULT 1,
    completed_steps INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    completion_percentage DECIMAL(5,2) DEFAULT 0,

    -- Performance
    score_before DECIMAL(5,2),
    score_after DECIMAL(5,2),
    improvement DECIMAL(5,2),

    -- Timeline
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    estimated_completion TIMESTAMP,

    -- Metadata
    status TEXT CHECK (status IN ('not_started', 'in_progress', 'completed', 'abandoned')) DEFAULT 'not_started',

    CONSTRAINT user_learning_unique UNIQUE (user_id, learning_path_id)
);

CREATE INDEX idx_user_learning_user ON learning.user_learning_progress(user_id);
CREATE INDEX idx_user_learning_path ON learning.user_learning_progress(learning_path_id);
CREATE INDEX idx_user_learning_status ON learning.user_learning_progress(status);

-- =====================================================
-- 5. GOALS & TRACKING
-- =====================================================

-- SMART Goals
CREATE TABLE IF NOT EXISTS learning.smart_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    tenant_id TEXT NOT NULL,

    -- SMART criteria
    goal_title TEXT NOT NULL,
    goal_description TEXT,

    specific TEXT, -- What exactly will be achieved
    measurable TEXT, -- How it will be measured
    achievable TEXT, -- Why it's realistic
    relevant TEXT, -- Why it matters
    time_bound TEXT, -- Deadline

    -- Metrics
    target_metric TEXT NOT NULL, -- "exercise_score", "competency_level", "exercises_completed"
    target_value DECIMAL(10,2) NOT NULL,
    current_value DECIMAL(10,2) DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0,

    -- Timeline
    start_date DATE NOT NULL,
    target_date DATE NOT NULL,
    completed_date DATE,

    -- Status
    status TEXT CHECK (status IN ('active', 'completed', 'overdue', 'abandoned')) DEFAULT 'active',

    -- Milestones
    milestones JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"milestone": "Complete 5 exercises", "target_date": "2025-02-01", "completed": true}]

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_smart_goals_user ON learning.smart_goals(user_id);
CREATE INDEX idx_smart_goals_tenant ON learning.smart_goals(tenant_id);
CREATE INDEX idx_smart_goals_status ON learning.smart_goals(status);
CREATE INDEX idx_smart_goals_target_date ON learning.smart_goals(target_date);

-- =====================================================
-- 6. ALERTS & NOTIFICATIONS
-- =====================================================

-- Learning system alerts
CREATE TABLE IF NOT EXISTS learning.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,

    alert_type TEXT NOT NULL, -- "performance_decline", "pattern_detected", "competency_decay", "goal_overdue", etc.
    severity TEXT CHECK (severity IN ('info', 'warning', 'critical')) NOT NULL,

    -- Alert content
    title TEXT NOT NULL,
    message TEXT NOT NULL,

    -- Context
    user_id UUID, -- If user-specific
    related_entity_type TEXT, -- "exercise", "pattern", "competency", "goal"
    related_entity_id UUID,

    -- Actions
    recommended_actions JSONB DEFAULT '[]'::jsonb,
    action_url TEXT,

    -- Routing
    notify_via TEXT[] DEFAULT ARRAY['in_app']::TEXT[], -- "in_app", "email", "slack"
    recipients UUID[], -- User IDs to notify

    -- Status
    status TEXT CHECK (status IN ('new', 'acknowledged', 'resolved', 'dismissed')) DEFAULT 'new',
    acknowledged_by UUID,
    acknowledged_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX idx_alerts_tenant ON learning.alerts(tenant_id);
CREATE INDEX idx_alerts_type ON learning.alerts(alert_type);
CREATE INDEX idx_alerts_severity ON learning.alerts(severity);
CREATE INDEX idx_alerts_status ON learning.alerts(status);
CREATE INDEX idx_alerts_user ON learning.alerts(user_id);

-- =====================================================
-- 7. RLS POLICIES (Row-Level Security)
-- =====================================================

-- Enable RLS on all new tables
ALTER TABLE learning.user_competencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.team_competencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.bcm_processes ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.process_coverage ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.role_competency_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.gamification_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.badge_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.achievement_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.leaderboards ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.gap_knowledge_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.user_learning_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.smart_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning.alerts ENABLE ROW LEVEL SECURITY;

-- Tenant isolation policies (example for user_competencies, repeat pattern for others)
CREATE POLICY tenant_isolation_user_competencies ON learning.user_competencies
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tenant_isolation_team_competencies ON learning.team_competencies
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tenant_isolation_bcm_processes ON learning.bcm_processes
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tenant_isolation_process_coverage ON learning.process_coverage
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tenant_isolation_role_gaps ON learning.role_competency_gaps
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tenant_isolation_gamification ON learning.gamification_profiles
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tenant_isolation_leaderboards ON learning.leaderboards
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tenant_isolation_goals ON learning.smart_goals
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tenant_isolation_alerts ON learning.alerts
    USING (tenant_id = current_setting('app.current_tenant_id', true));

-- Badge/Achievement/Learning Path definitions are global (no tenant isolation)
-- Gap Knowledge mappings are global (no tenant isolation)

-- User-specific policies
CREATE POLICY user_access_learning_progress ON learning.user_learning_progress
    USING (user_id::text = current_setting('app.current_user_id', true));

-- =====================================================
-- 8. SEED DATA - Badge Definitions
-- =====================================================

INSERT INTO learning.badge_definitions (id, name, description, category, criteria, rarity, points_awarded) VALUES
-- Frequency badges
('first_timer', 'First Timer', 'Complete your first exercise', 'frequency', '{"exercises_completed": 1}', 'common', 50),
('regular_practitioner', 'Regular Practitioner', 'Complete 10 exercises', 'frequency', '{"exercises_completed": 10}', 'uncommon', 200),
('exercise_champion', 'Exercise Champion', 'Complete 50 exercises', 'frequency', '{"exercises_completed": 50}', 'epic', 1000),

-- Performance badges
('bronze_response', 'Bronze Response', 'Score 60-69 on any exercise', 'performance', '{"score_range": [60, 69]}', 'common', 100),
('silver_response', 'Silver Response', 'Score 70-79 on any exercise', 'performance', '{"score_range": [70, 79]}', 'uncommon', 200),
('gold_response', 'Gold Response', 'Score 80-89 on any exercise', 'performance', '{"score_range": [80, 89]}', 'rare', 300),
('platinum_response', 'Platinum Response', 'Score 90-100 on any exercise', 'performance', '{"score_range": [90, 100]}', 'legendary', 500),

-- Improvement badges
('rising_star', 'Rising Star', 'Improve score by 20+ points', 'improvement', '{"score_improvement": 20}', 'rare', 300),
('rapid_learner', 'Rapid Learner', 'Improve score by 30+ points', 'improvement', '{"score_improvement": 30}', 'epic', 500),

-- Specialty badges
('cyber_guardian', 'Cyber Guardian', 'Complete 5 cyber exercises with 75+ score', 'specialty', '{"scenario_type": "cyber", "count": 5, "min_score": 75}', 'rare', 400),
('supply_chain_expert', 'Supply Chain Expert', 'Complete 5 supply chain exercises with 75+ score', 'specialty', '{"scenario_type": "supply_chain", "count": 5, "min_score": 75}', 'rare', 400),

-- Team badges
('well_oiled_machine', 'Well-Oiled Machine', 'Team average score 80+ in exercise', 'team', '{"team_avg_score": 80}', 'rare', 300),
('zero_gaps', 'Zero Gaps', 'Exercise with no critical gaps identified', 'team', '{"critical_gaps": 0}', 'epic', 500),

-- Streak badges
('week_streak', '7-Day Streak', 'Active 7 days in a row', 'streak', '{"streak_days": 7}', 'uncommon', 200),
('month_streak', '30-Day Streak', 'Active 30 days in a row', 'streak', '{"streak_days": 30}', 'epic', 800),
('quarter_streak', 'Quarter Streak', 'Active 90 days in a row', 'streak', '{"streak_days": 90}', 'legendary', 2000)
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- 9. FUNCTIONS & TRIGGERS
-- =====================================================

-- Function to update user competency after exercise
CREATE OR REPLACE FUNCTION learning.update_user_competency_after_exercise()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert user competency based on exercise result
    INSERT INTO learning.user_competencies (
        user_id,
        tenant_id,
        total_exercises,
        avg_exercise_score,
        last_exercise_date,
        days_since_last_exercise,
        scenario_competencies
    )
    VALUES (
        NEW.participant_user_id, -- Assuming this field exists or will be added
        NEW.tenant_id,
        1,
        NEW.overall_score,
        NEW.conducted_at,
        0,
        jsonb_build_object(NEW.scenario_type, NEW.overall_score)
    )
    ON CONFLICT (user_id, tenant_id) DO UPDATE SET
        total_exercises = learning.user_competencies.total_exercises + 1,
        avg_exercise_score = (
            (learning.user_competencies.avg_exercise_score * learning.user_competencies.total_exercises + NEW.overall_score)
            / (learning.user_competencies.total_exercises + 1)
        ),
        last_exercise_date = NEW.conducted_at,
        days_since_last_exercise = 0,
        scenario_competencies = learning.user_competencies.scenario_competencies ||
            jsonb_build_object(
                NEW.scenario_type,
                COALESCE((learning.user_competencies.scenario_competencies->NEW.scenario_type)::numeric, 0) * 0.7 + NEW.overall_score * 0.3
            ),
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate decay risk
CREATE OR REPLACE FUNCTION learning.calculate_decay_risk()
RETURNS void AS $$
BEGIN
    UPDATE learning.user_competencies
    SET
        days_since_last_exercise = EXTRACT(DAY FROM NOW() - last_exercise_date)::INTEGER,
        decay_risk_level = CASE
            WHEN EXTRACT(DAY FROM NOW() - last_exercise_date) <= 30 THEN 'low'
            WHEN EXTRACT(DAY FROM NOW() - last_exercise_date) <= 90 THEN 'medium'
            WHEN EXTRACT(DAY FROM NOW() - last_exercise_date) <= 180 THEN 'high'
            ELSE 'critical'
        END,
        updated_at = NOW()
    WHERE last_exercise_date IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 10. COMMENTS & DOCUMENTATION
-- =====================================================

COMMENT ON TABLE learning.user_competencies IS 'Individual BCM competency tracking with skills decay analysis';
COMMENT ON TABLE learning.team_competencies IS 'Team capability coverage matrix with gap identification';
COMMENT ON TABLE learning.bcm_processes IS 'BCM process definitions mapped to ISO 22301';
COMMENT ON TABLE learning.process_coverage IS 'Exercise coverage analysis per BCM process and scenario';
COMMENT ON TABLE learning.role_competency_gaps IS 'Role-based competency gap analysis';
COMMENT ON TABLE learning.gamification_profiles IS 'User gamification status: points, badges, levels, streaks';
COMMENT ON TABLE learning.badge_definitions IS 'Badge catalog with earning criteria';
COMMENT ON TABLE learning.leaderboards IS 'Generated leaderboards by type and period';
COMMENT ON TABLE learning.gap_knowledge_mappings IS 'Maps exercise gaps to knowledge base resources';
COMMENT ON TABLE learning.learning_paths IS 'Structured learning paths for competency improvement';
COMMENT ON TABLE learning.smart_goals IS 'User SMART goals with progress tracking';
COMMENT ON TABLE learning.alerts IS 'Learning system alerts and notifications';

-- Migration complete
COMMENT ON SCHEMA learning IS 'Learning System with Competency Tracking, Gap Analysis, Gamification - v2.0';
