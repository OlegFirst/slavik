-- ============================================
-- BCM Platform - Unified Database
-- Migration 013: Learning & Planning
-- ============================================
-- ISO 22301:2019 Clauses:
--   7.2 (Competence)
--   7.3 (Awareness)
--   8.4 (Business Continuity Plans and Procedures)
-- Schemas: learning, bcm (plans and procedures)
-- ============================================

CREATE SCHEMA IF NOT EXISTS learning;
COMMENT ON SCHEMA learning IS 'Training, awareness, and competency development';

-- Table: learning.training_programs
CREATE TABLE learning.training_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Program identity
    program_code VARCHAR(100) NOT NULL,
    program_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 7.2, 7.3
    program_type VARCHAR(100) NOT NULL, -- bcm_foundation, bia, risk_assessment, incident_response, crisis_management, awareness, role_specific, technical
    training_level VARCHAR(50), -- foundation, intermediate, advanced, expert

    -- Content
    learning_objectives JSONB NOT NULL, -- Array of objectives
    syllabus TEXT,
    course_materials JSONB DEFAULT '[]'::jsonb, -- {title, file_path, type}

    -- Delivery
    delivery_method VARCHAR(100) NOT NULL, -- classroom, online, hybrid, self_paced, workshop, simulation
    delivery_platform VARCHAR(100), -- lms_name, in_person, webinar

    duration_hours DECIMAL(10,2) NOT NULL,
    prerequisites TEXT,

    -- Target audience
    target_roles JSONB DEFAULT '[]'::jsonb, -- Which roles should take this
    is_mandatory BOOLEAN DEFAULT FALSE,
    mandatory_for_roles JSONB DEFAULT '[]'::jsonb,

    -- Instructors
    instructor_ids JSONB DEFAULT '[]'::jsonb, -- UUIDs of users
    external_instructor_name VARCHAR(255),

    -- Certification
    provides_certification BOOLEAN DEFAULT FALSE,
    certification_name VARCHAR(255),
    certification_validity_years INT,

    -- Assessment
    has_assessment BOOLEAN DEFAULT TRUE,
    passing_score_percent DECIMAL(5,2),
    max_attempts INT,

    -- Scheduling
    schedule_type VARCHAR(50), -- on_demand, scheduled, recurring
    max_participants INT,
    min_participants INT,

    -- Costs
    cost_per_participant DECIMAL(15,2),
    is_free BOOLEAN DEFAULT TRUE,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, active, archived
    is_active BOOLEAN DEFAULT TRUE,

    -- Effectiveness tracking
    completion_rate_percent DECIMAL(5,2),
    average_score_percent DECIMAL(5,2),
    effectiveness_rating DECIMAL(3,2), -- 1.0-5.0 from feedback

    -- Maintenance
    owner_id UUID REFERENCES auth.users(id),
    last_updated_date DATE,
    next_review_date DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(program_code,'') || ' ' ||
            coalesce(program_name,'') || ' ' ||
            coalesce(description,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, program_code)
);

CREATE INDEX idx_training_programs_org ON learning.training_programs(organization_id);
CREATE INDEX idx_training_programs_code ON learning.training_programs(program_code);
CREATE INDEX idx_training_programs_type ON learning.training_programs(program_type);
CREATE INDEX idx_training_programs_active ON learning.training_programs(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_training_programs_search ON learning.training_programs USING GIN(search_vector);

CREATE TRIGGER update_training_programs_updated_at BEFORE UPDATE ON learning.training_programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE learning.training_programs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Training programs visible to org members" ON learning.training_programs FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Training programs manageable by org admins" ON learning.training_programs FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE learning.training_programs IS 'Training programs per ISO 22301:2019 Clauses 7.2, 7.3';

-- Table: learning.enrollments
CREATE TABLE learning.enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID NOT NULL REFERENCES learning.training_programs(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Learner
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name VARCHAR(255),
    user_role VARCHAR(100),

    -- Enrollment
    enrollment_date TIMESTAMPTZ DEFAULT NOW(),
    enrollment_type VARCHAR(50) DEFAULT 'self_enrolled', -- self_enrolled, assigned, mandatory

    assigned_by UUID REFERENCES auth.users(id),
    assignment_reason TEXT,

    -- Schedule
    scheduled_start_date DATE,
    scheduled_end_date DATE,
    due_date DATE, -- For mandatory training

    actual_start_date DATE,
    actual_completion_date DATE,

    -- Progress
    status VARCHAR(50) DEFAULT 'enrolled', -- enrolled, in_progress, completed, failed, dropped, overdue
    progress_percent DECIMAL(5,2) DEFAULT 0,

    time_spent_hours DECIMAL(10,2),
    last_accessed_at TIMESTAMPTZ,

    -- Assessment
    attempts_count INT DEFAULT 0,
    best_score_percent DECIMAL(5,2),
    final_score_percent DECIMAL(5,2),
    passed BOOLEAN,

    -- Completion
    completion_certificate_path VARCHAR(500),
    certificate_issued_at TIMESTAMPTZ,

    -- Certification
    certification_number VARCHAR(100),
    certification_issued_date DATE,
    certification_expiry_date DATE,

    -- Feedback
    feedback_rating INT, -- 1-5 stars
    feedback_comments TEXT,
    feedback_submitted_at TIMESTAMPTZ,

    -- Reminder tracking
    reminder_sent_count INT DEFAULT 0,
    last_reminder_sent_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_enrollments_program ON learning.enrollments(program_id);
CREATE INDEX idx_enrollments_org ON learning.enrollments(organization_id);
CREATE INDEX idx_enrollments_user ON learning.enrollments(user_id, status);
CREATE INDEX idx_enrollments_status ON learning.enrollments(status);
CREATE INDEX idx_enrollments_overdue ON learning.enrollments(due_date) WHERE status NOT IN ('completed', 'dropped') AND due_date < CURRENT_DATE;
CREATE INDEX idx_enrollments_expiring_cert ON learning.enrollments(certification_expiry_date) WHERE passed = TRUE AND certification_expiry_date IS NOT NULL;

CREATE TRIGGER update_enrollments_updated_at BEFORE UPDATE ON learning.enrollments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE learning.enrollments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enrollments visible to org members" ON learning.enrollments FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Users see their own enrollments" ON learning.enrollments FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE learning.enrollments IS 'Training enrollments and completion tracking';

-- Table: learning.competency_assessments
CREATE TABLE learning.competency_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Assessment identity
    assessment_code VARCHAR(100),
    assessment_title VARCHAR(255) NOT NULL,

    -- Subject
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name VARCHAR(255),
    user_role VARCHAR(100),

    -- Competency area (ISO 22301 Clause 7.2)
    competency_area VARCHAR(100) NOT NULL, -- bcm_planning, bia, risk_assessment, incident_response, crisis_management, audit
    competency_framework VARCHAR(100), -- internal, iso_22301, cisa, cbcp

    -- Assessment details
    assessment_type VARCHAR(100) NOT NULL, -- self_assessment, manager_assessment, peer_assessment, 360_review, skills_test, simulation
    assessment_date DATE NOT NULL,

    assessor_id UUID REFERENCES auth.users(id),
    assessor_name VARCHAR(255),
    assessor_role VARCHAR(100),

    -- Competency rating
    competency_level VARCHAR(50) NOT NULL, -- novice, competent, proficient, expert
    competency_score DECIMAL(5,2), -- 0-100

    -- Evaluation criteria
    evaluation_criteria JSONB DEFAULT '[]'::jsonb, -- {criterion, rating, comments}

    -- Findings
    strengths TEXT,
    areas_for_improvement TEXT,
    recommendations TEXT,

    -- Development plan
    development_actions JSONB DEFAULT '[]'::jsonb, -- {action, priority, due_date}
    recommended_training JSONB DEFAULT '[]'::jsonb, -- UUIDs of learning.training_programs

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, completed, approved
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    -- Next assessment
    next_assessment_date DATE,

    -- Metadata
    notes TEXT,
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_competency_assessments_org ON learning.competency_assessments(organization_id);
CREATE INDEX idx_competency_assessments_user ON learning.competency_assessments(user_id, assessment_date DESC);
CREATE INDEX idx_competency_assessments_area ON learning.competency_assessments(competency_area);
CREATE INDEX idx_competency_assessments_date ON learning.competency_assessments(assessment_date DESC);

CREATE TRIGGER update_competency_assessments_updated_at BEFORE UPDATE ON learning.competency_assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE learning.competency_assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Competency assessments visible to org admins" ON learning.competency_assessments FOR SELECT
    USING (auth.is_org_admin(organization_id));

CREATE POLICY "Users see their own competency assessments" ON learning.competency_assessments FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE learning.competency_assessments IS 'Competency assessments per ISO 22301 Clause 7.2';

-- Table: learning.awareness_campaigns
CREATE TABLE learning.awareness_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Campaign identity
    campaign_code VARCHAR(100) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 7.3 (Awareness)
    campaign_type VARCHAR(100) NOT NULL, -- bcm_awareness, incident_preparedness, cyber_security, safety, compliance

    -- Objectives
    objectives JSONB NOT NULL, -- Array of campaign objectives
    target_audience VARCHAR(100), -- all_staff, managers, executives, specific_roles
    target_roles JSONB DEFAULT '[]'::jsonb,

    -- Content
    key_messages JSONB DEFAULT '[]'::jsonb,
    materials JSONB DEFAULT '[]'::jsonb, -- {title, type, file_path, url}

    -- Delivery channels
    channels JSONB DEFAULT '[]'::jsonb, -- email, poster, intranet, video, workshop, newsletter, digital_signage

    -- Schedule
    start_date DATE NOT NULL,
    end_date DATE,
    is_ongoing BOOLEAN DEFAULT FALSE,

    milestone_schedule JSONB DEFAULT '[]'::jsonb, -- {date, activity, deliverable}

    -- Status
    status VARCHAR(50) DEFAULT 'planning', -- planning, active, paused, completed, cancelled

    -- Ownership
    campaign_owner_id UUID REFERENCES auth.users(id),
    campaign_team JSONB DEFAULT '[]'::jsonb, -- {user_id, role}

    -- Budget
    estimated_budget DECIMAL(15,2),
    actual_cost DECIMAL(15,2),

    -- Effectiveness tracking
    reach_target INT, -- How many people should be reached
    actual_reach INT, -- How many were reached
    engagement_target INT, -- Expected interactions
    actual_engagement INT, -- Actual interactions

    effectiveness_metrics JSONB DEFAULT '[]'::jsonb, -- {metric_name, target_value, actual_value}

    -- Evaluation
    evaluation_method VARCHAR(100), -- survey, quiz, observation, participation_rate
    evaluation_results JSONB,
    effectiveness_rating VARCHAR(50), -- highly_effective, effective, needs_improvement, ineffective

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, campaign_code)
);

CREATE INDEX idx_awareness_campaigns_org ON learning.awareness_campaigns(organization_id);
CREATE INDEX idx_awareness_campaigns_code ON learning.awareness_campaigns(campaign_code);
CREATE INDEX idx_awareness_campaigns_type ON learning.awareness_campaigns(campaign_type);
CREATE INDEX idx_awareness_campaigns_status ON learning.awareness_campaigns(status);
CREATE INDEX idx_awareness_campaigns_active ON learning.awareness_campaigns(status, start_date, end_date) WHERE status = 'active';

CREATE TRIGGER update_awareness_campaigns_updated_at BEFORE UPDATE ON learning.awareness_campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE learning.awareness_campaigns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Awareness campaigns visible to org members" ON learning.awareness_campaigns FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Awareness campaigns manageable by org admins" ON learning.awareness_campaigns FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE learning.awareness_campaigns IS 'Awareness campaigns per ISO 22301:2019 Clause 7.3';

-- Table: learning.training_templates
CREATE TABLE learning.training_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Template identity
    template_code VARCHAR(100) NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Template type
    template_type VARCHAR(100) NOT NULL, -- course_template, module_template, assessment_template, certificate_template

    -- Content
    template_content JSONB NOT NULL, -- Full template structure
    learning_objectives JSONB DEFAULT '[]'::jsonb,
    recommended_duration_hours DECIMAL(10,2),

    -- Customization
    customizable_fields JSONB DEFAULT '[]'::jsonb,
    default_values JSONB DEFAULT '{}'::jsonb,

    -- Usage
    is_system_template BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INT DEFAULT 0,

    -- Industry/standard alignment
    aligned_standards JSONB DEFAULT '[]'::jsonb, -- ISO_22301, ISO_27001, etc.
    industry VARCHAR(100), -- financial, healthcare, manufacturing, etc.

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_training_templates_org ON learning.training_templates(organization_id);
CREATE INDEX idx_training_templates_type ON learning.training_templates(template_type);
CREATE INDEX idx_training_templates_active ON learning.training_templates(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_training_templates_updated_at BEFORE UPDATE ON learning.training_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE learning.training_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Training templates visible to all org members" ON learning.training_templates FOR SELECT
    USING (organization_id IS NULL OR auth.is_org_member(organization_id));

COMMENT ON TABLE learning.training_templates IS 'Training and course templates';

-- Table: learning.user_achievements
CREATE TABLE learning.user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- User
    user_id UUID NOT NULL REFERENCES auth.users(id),

    -- Achievement
    achievement_type VARCHAR(100) NOT NULL, -- training_completed, certification_earned, exercise_participated, perfect_score, fast_learner, streak
    achievement_name VARCHAR(255) NOT NULL,
    achievement_description TEXT,

    -- Context
    related_program_id UUID REFERENCES learning.training_programs(id),
    related_enrollment_id UUID REFERENCES learning.enrollments(id),

    -- Details
    achievement_date DATE NOT NULL,
    achievement_value JSONB, -- Additional context (score, duration, etc.)

    -- Badge/Certificate
    badge_image_path VARCHAR(500),
    certificate_path VARCHAR(500),

    -- Visibility
    is_visible BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_achievements_org ON learning.user_achievements(organization_id);
CREATE INDEX idx_user_achievements_user ON learning.user_achievements(user_id, achievement_date DESC);
CREATE INDEX idx_user_achievements_type ON learning.user_achievements(achievement_type);

ALTER TABLE learning.user_achievements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Achievements visible to org members" ON learning.user_achievements FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Users see their own achievements" ON learning.user_achievements FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE learning.user_achievements IS 'User achievements and gamification';

-- =========================
-- BCM PLANS AND PROCEDURES
-- =========================

-- Table: bcm.plans (Consolidated from planning/ and plans/)
CREATE TABLE bcm.plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Plan identity
    plan_code VARCHAR(100) NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 8.4
    plan_type VARCHAR(100) NOT NULL, -- bcm_policy, bcm_strategy, bccp (Business Continuity Plan), irp (Incident Response), drp (Disaster Recovery), crp (Crisis Recovery), sop (Standard Operating Procedure)
    plan_scope VARCHAR(100), -- organization_wide, division, department, process_specific, site_specific

    -- Hierarchy
    parent_plan_id UUID REFERENCES bcm.plans(id),
    is_master_plan BOOLEAN DEFAULT FALSE,

    -- Content
    plan_content TEXT, -- Main plan content
    plan_structure JSONB DEFAULT '[]'::jsonb, -- {section_number, section_title, content}

    -- Key elements (ISO 22301 requirements)
    purpose_and_scope TEXT,
    roles_and_responsibilities JSONB DEFAULT '[]'::jsonb,
    activation_criteria TEXT,
    escalation_procedures TEXT,
    communication_procedures TEXT,
    recovery_procedures TEXT,

    -- Versioning
    version VARCHAR(50) DEFAULT '1.0',
    version_date DATE,
    is_current_version BOOLEAN DEFAULT TRUE,

    -- Related entities
    related_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    related_risks JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.risks
    related_plans JSONB DEFAULT '[]'::jsonb, -- Related/dependent plans

    -- Resources
    required_resources JSONB DEFAULT '[]'::jsonb, -- UUIDs of bcm.resources
    contact_lists JSONB DEFAULT '[]'::jsonb, -- Key contacts

    -- Recovery objectives
    rto_minutes INT, -- Recovery Time Objective
    rpo_minutes INT, -- Recovery Point Objective

    -- Status and lifecycle
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, active, under_revision, archived, superseded
    approval_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected

    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    published_date DATE,
    effective_date DATE,
    review_date DATE,
    next_review_date DATE,

    -- Ownership
    owner_id UUID REFERENCES auth.users(id) NOT NULL,
    author_id UUID REFERENCES auth.users(id),

    -- Testing and validation
    last_tested_date DATE,
    test_results VARCHAR(50), -- successful, partially_successful, failed, not_tested
    next_test_date DATE,

    -- Activation tracking
    times_activated INT DEFAULT 0,
    last_activation_date DATE,
    last_activation_incident_id UUID, -- UUID of response.incidents

    -- Access control
    is_confidential BOOLEAN DEFAULT FALSE,
    authorized_roles JSONB DEFAULT '[]'::jsonb,
    authorized_users JSONB DEFAULT '[]'::jsonb,

    -- Files
    file_path VARCHAR(500),
    file_format VARCHAR(50), -- pdf, docx, html
    file_size_bytes BIGINT,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(plan_code,'') || ' ' ||
            coalesce(plan_name,'') || ' ' ||
            coalesce(description,'') || ' ' ||
            coalesce(plan_type,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, plan_code)
);

CREATE INDEX idx_plans_org ON bcm.plans(organization_id);
CREATE INDEX idx_plans_code ON bcm.plans(plan_code);
CREATE INDEX idx_plans_type ON bcm.plans(plan_type);
CREATE INDEX idx_plans_status ON bcm.plans(status);
CREATE INDEX idx_plans_current ON bcm.plans(is_current_version) WHERE is_current_version = TRUE;
CREATE INDEX idx_plans_search ON bcm.plans USING GIN(search_vector);
CREATE INDEX idx_plans_review_due ON bcm.plans(next_review_date) WHERE status = 'active';

CREATE TRIGGER update_plans_updated_at BEFORE UPDATE ON bcm.plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE bcm.plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Plans visible to org members" ON bcm.plans FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Plans manageable by org admins" ON bcm.plans FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE bcm.plans IS 'Business continuity plans and procedures per ISO 22301:2019 Clause 8.4';

-- Table: bcm.procedures (Consolidated)
CREATE TABLE bcm.procedures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES bcm.plans(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Procedure identity
    procedure_code VARCHAR(100) NOT NULL,
    procedure_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Classification
    procedure_type VARCHAR(100) NOT NULL, -- activation, response, recovery, communication, escalation, restoration, technical
    procedure_category VARCHAR(100), -- operational, technical, administrative

    -- Content
    procedure_steps JSONB NOT NULL, -- Array of {step_number, action, responsible_role, estimated_time, critical}
    decision_points JSONB DEFAULT '[]'::jsonb, -- {point_number, decision, criteria, yes_action, no_action}

    -- Execution context
    when_to_execute TEXT,
    trigger_conditions JSONB DEFAULT '[]'::jsonb,

    -- Roles
    responsible_role VARCHAR(100),
    supporting_roles JSONB DEFAULT '[]'::jsonb,

    -- Resources needed
    required_resources JSONB DEFAULT '[]'::jsonb,
    required_tools JSONB DEFAULT '[]'::jsonb,
    required_access JSONB DEFAULT '[]'::jsonb,

    -- Timing
    estimated_duration_minutes INT,
    must_complete_within_minutes INT, -- SLA/RTO requirement

    -- Dependencies
    depends_on JSONB DEFAULT '[]'::jsonb, -- UUIDs of other procedures
    blocks JSONB DEFAULT '[]'::jsonb, -- Procedures that depend on this

    -- Quality checks
    verification_steps JSONB DEFAULT '[]'::jsonb,
    success_criteria TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_reviewed_date DATE,
    next_review_date DATE,

    -- Testing
    last_tested_date DATE,
    test_success_rate DECIMAL(5,2),

    -- Usage tracking
    times_executed INT DEFAULT 0,
    average_execution_time_minutes INT,
    last_executed_date DATE,

    -- Files
    flowchart_path VARCHAR(500),
    detailed_document_path VARCHAR(500),

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, procedure_code)
);

CREATE INDEX idx_procedures_plan ON bcm.procedures(plan_id);
CREATE INDEX idx_procedures_org ON bcm.procedures(organization_id);
CREATE INDEX idx_procedures_type ON bcm.procedures(procedure_type);
CREATE INDEX idx_procedures_active ON bcm.procedures(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_procedures_updated_at BEFORE UPDATE ON bcm.procedures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE bcm.procedures ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Procedures visible to org members" ON bcm.procedures FOR SELECT
    USING (auth.is_org_member(organization_id));

CREATE POLICY "Procedures manageable by org admins" ON bcm.procedures FOR ALL
    USING (auth.is_org_admin(organization_id));

COMMENT ON TABLE bcm.procedures IS 'Detailed procedures for BCM plans per ISO 22301 Clause 8.4';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 013 completed: Learning & Planning (8 tables)';
    RAISE NOTICE '   Learning Schema (NEW):';
    RAISE NOTICE '   - training_programs: Training courses (ISO 22301 Clauses 7.2, 7.3)';
    RAISE NOTICE '   - enrollments: Training enrollment and completion tracking';
    RAISE NOTICE '   - competency_assessments: Competency evaluations';
    RAISE NOTICE '   - awareness_campaigns: BCM awareness campaigns';
    RAISE NOTICE '   - training_templates: Course templates';
    RAISE NOTICE '   - user_achievements: Gamification and badges';
    RAISE NOTICE '   BCM Schema:';
    RAISE NOTICE '   - plans: Business continuity plans (ISO 22301 Clause 8.4)';
    RAISE NOTICE '   - procedures: Detailed operational procedures';
END
$$;
