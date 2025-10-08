-- ============================================
-- BCM Platform - Unified Database
-- Migration 010: Validation Schema
-- ============================================
-- ISO 22301:2019 Clauses:
--   8.5 (Testing and Exercising)
--   9.1 (Monitoring, Measurement, Analysis, Evaluation)
--   9.2 (Internal Audit)
--   9.3 (Management Review)
--   10 (Improvement - CAPA)
-- Schema: validation (exercises, KPIs, audits, CAPA, management reviews)
-- ============================================

-- Table: validation.exercises
CREATE TABLE validation.exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Exercise identity
    exercise_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 8.5
    exercise_type VARCHAR(100) NOT NULL, -- tabletop, walkthrough, simulation, full_scale, functional, drill
    exercise_scope VARCHAR(100), -- single_process, department, organization_wide, multi_site, supply_chain

    -- Classification
    complexity_level VARCHAR(50), -- basic, intermediate, advanced, complex
    involves_external_parties BOOLEAN DEFAULT FALSE,

    -- Planning
    objectives JSONB NOT NULL, -- Array of objectives
    success_criteria JSONB, -- Array of measurable criteria

    tested_plans JSONB DEFAULT '[]'::jsonb, -- UUIDs of plans being tested
    tested_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    tested_controls JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls

    -- Scheduling
    status VARCHAR(50) DEFAULT 'planning', -- planning, scheduled, in_progress, completed, cancelled
    scheduled_start TIMESTAMPTZ,
    scheduled_end TIMESTAMPTZ,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,

    -- Participation
    exercise_director_id UUID REFERENCES auth.users(id),
    lead_facilitator_id UUID REFERENCES auth.users(id),

    participants JSONB DEFAULT '[]'::jsonb, -- {user_id, role, team, attendance_status}
    participants_count INT,
    observers JSONB DEFAULT '[]'::jsonb,
    external_participants JSONB DEFAULT '[]'::jsonb,

    -- Scenario
    scenario_id UUID, -- Will reference validation.exercise_scenarios(id)
    scenario_description TEXT,
    scenario_complexity VARCHAR(50),
    inject_schedule JSONB DEFAULT '[]'::jsonb, -- Timed injects during exercise

    -- Location and logistics
    location VARCHAR(255),
    is_virtual BOOLEAN DEFAULT FALSE,
    meeting_links JSONB DEFAULT '[]'::jsonb,
    required_resources JSONB DEFAULT '[]'::jsonb,

    -- Evaluation
    overall_score DECIMAL(5,2), -- 0-100
    evaluation_summary TEXT,
    strengths TEXT,
    weaknesses TEXT,
    lessons_learned TEXT,

    objectives_met_count INT DEFAULT 0,
    objectives_total_count INT,
    success_rate_percent DECIMAL(5,2),

    -- Compliance
    is_regulatory_requirement BOOLEAN DEFAULT FALSE,
    regulatory_frequency VARCHAR(50), -- annual, biannual, as_required
    last_similar_exercise_date DATE,
    next_required_exercise_date DATE,

    -- Outcomes
    findings_count INT DEFAULT 0,
    actions_identified_count INT DEFAULT 0,
    actions_completed_count INT DEFAULT 0,

    -- Reporting
    report_completed BOOLEAN DEFAULT FALSE,
    report_file_path VARCHAR(500),
    report_completed_at TIMESTAMPTZ,
    report_approved_by UUID REFERENCES auth.users(id),

    -- Budget
    estimated_cost DECIMAL(15,2),
    actual_cost DECIMAL(15,2),

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(exercise_code,'') || ' ' ||
            coalesce(title,'') || ' ' ||
            coalesce(description,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_exercises_org ON validation.exercises(organization_id);
CREATE INDEX idx_exercises_code ON validation.exercises(exercise_code);
CREATE INDEX idx_exercises_status ON validation.exercises(status);
CREATE INDEX idx_exercises_type ON validation.exercises(exercise_type);
CREATE INDEX idx_exercises_scheduled ON validation.exercises(scheduled_start);
CREATE INDEX idx_exercises_search ON validation.exercises USING GIN(search_vector);

CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON validation.exercises
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.exercises ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Exercises visible to org members" ON validation.exercises FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Exercises manageable by org admins" ON validation.exercises FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.exercises IS 'BCM exercises per ISO 22301:2019 Clause 8.5';

-- Table: validation.exercise_scenarios
CREATE TABLE validation.exercise_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Scenario identity
    scenario_code VARCHAR(100) NOT NULL,
    scenario_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Classification
    scenario_type VARCHAR(100) NOT NULL, -- cyber_attack, natural_disaster, supply_chain_disruption, pandemic, facility_loss, key_personnel_loss
    threat_category VARCHAR(100),
    severity_level VARCHAR(50), -- critical, high, medium, low

    -- Scenario details
    initial_situation TEXT NOT NULL, -- What participants are told at start
    trigger_event TEXT, -- What initiates the incident
    complicating_factors TEXT, -- Additional challenges during exercise

    -- Timeline
    estimated_duration_minutes INT,
    phases JSONB DEFAULT '[]'::jsonb, -- Array of {phase_name, duration_minutes, description, objectives}

    -- Injects
    injects JSONB DEFAULT '[]'::jsonb, -- Array of {inject_time, type, title, description, expected_response}
    injects_count INT DEFAULT 0,

    -- Scope and impact
    affected_processes JSONB DEFAULT '[]'::jsonb,
    affected_locations JSONB DEFAULT '[]'::jsonb,
    simulated_impacts JSONB DEFAULT '[]'::jsonb, -- {impact_type, severity, description}

    -- Learning objectives
    learning_objectives JSONB DEFAULT '[]'::jsonb,
    skills_tested JSONB DEFAULT '[]'::jsonb, -- decision_making, communication, coordination, technical_recovery, etc.

    -- Required participants
    required_roles JSONB DEFAULT '[]'::jsonb,
    min_participants INT,
    max_participants INT,

    -- Resources needed
    required_props JSONB DEFAULT '[]'::jsonb, -- Physical or digital resources needed
    technology_requirements TEXT,

    -- Usage
    is_template BOOLEAN DEFAULT FALSE,
    usage_count INT DEFAULT 0,
    last_used_date DATE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    approval_status VARCHAR(50) DEFAULT 'draft', -- draft, approved, archived
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    -- Metadata
    difficulty_rating VARCHAR(50), -- beginner, intermediate, advanced, expert
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, scenario_code)
);

CREATE INDEX idx_scenarios_org ON validation.exercise_scenarios(organization_id);
CREATE INDEX idx_scenarios_type ON validation.exercise_scenarios(scenario_type);
CREATE INDEX idx_scenarios_active ON validation.exercise_scenarios(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_scenarios_updated_at BEFORE UPDATE ON validation.exercise_scenarios
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.exercise_scenarios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Scenarios visible to org members" ON validation.exercise_scenarios FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Scenarios manageable by org admins" ON validation.exercise_scenarios FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.exercise_scenarios IS 'Exercise scenarios and templates per ISO 22301 Clause 8.5';

-- Add foreign key now that exercise_scenarios exists
ALTER TABLE validation.exercises
    ADD CONSTRAINT fk_exercises_scenario
    FOREIGN KEY (scenario_id) REFERENCES validation.exercise_scenarios(id);

-- Table: validation.exercise_observations
CREATE TABLE validation.exercise_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id UUID NOT NULL REFERENCES validation.exercises(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Observation details
    observation_type VARCHAR(100) NOT NULL, -- strength, weakness, gap, risk, improvement_opportunity
    severity VARCHAR(50), -- critical, high, medium, low
    category VARCHAR(100), -- communication, decision_making, coordination, technical, procedural, resource

    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- Context
    observed_at TIMESTAMPTZ NOT NULL,
    phase VARCHAR(100), -- Which phase of exercise this occurred in
    related_objective_id VARCHAR(100), -- Which objective this relates to

    affected_plan_id UUID, -- Which plan had the issue
    affected_process_id UUID, -- Which process

    -- Observer
    observer_id UUID REFERENCES auth.users(id),
    observer_role VARCHAR(100),

    -- Impact
    impact_assessment TEXT,
    potential_consequences TEXT,

    -- Evidence
    evidence JSONB DEFAULT '[]'::jsonb, -- Photos, videos, documents, logs
    witness_statements JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, acknowledged, action_planned, resolved, closed
    resolution_notes TEXT,
    resolved_at TIMESTAMPTZ,

    -- Priority
    requires_immediate_action BOOLEAN DEFAULT FALSE,
    action_deadline DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_observations_exercise ON validation.exercise_observations(exercise_id);
CREATE INDEX idx_observations_org ON validation.exercise_observations(organization_id);
CREATE INDEX idx_observations_type ON validation.exercise_observations(observation_type);
CREATE INDEX idx_observations_severity ON validation.exercise_observations(severity);
CREATE INDEX idx_observations_status ON validation.exercise_observations(status);

CREATE TRIGGER update_observations_updated_at BEFORE UPDATE ON validation.exercise_observations
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.exercise_observations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Observations visible to org members" ON validation.exercise_observations FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE validation.exercise_observations IS 'Observations during exercises';

-- Table: validation.exercise_actions
CREATE TABLE validation.exercise_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id UUID NOT NULL REFERENCES validation.exercises(id) ON DELETE CASCADE,
    observation_id UUID REFERENCES validation.exercise_observations(id),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Action details
    action_code VARCHAR(100),
    action_title VARCHAR(500) NOT NULL,
    action_description TEXT NOT NULL,

    action_type VARCHAR(100) NOT NULL, -- corrective, preventive, improvement
    priority VARCHAR(50) NOT NULL, -- critical, high, medium, low

    -- Assignment
    assigned_to_id UUID REFERENCES auth.users(id),
    assigned_to_team_id UUID REFERENCES public.teams(id),
    assigned_to_role VARCHAR(100),

    -- Timeline
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, completed, cancelled, overdue
    due_date DATE NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Progress
    progress_percent INT DEFAULT 0,
    progress_notes TEXT,

    -- Resources
    estimated_effort_hours DECIMAL(10,2),
    actual_effort_hours DECIMAL(10,2),
    budget_required DECIMAL(15,2),

    -- Verification
    requires_verification BOOLEAN DEFAULT TRUE,
    verification_method TEXT,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,
    verification_notes TEXT,

    -- Effectiveness
    effectiveness_rating INT, -- 1-5 scale
    effectiveness_notes TEXT,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_exercise_actions_exercise ON validation.exercise_actions(exercise_id);
CREATE INDEX idx_exercise_actions_org ON validation.exercise_actions(organization_id);
CREATE INDEX idx_exercise_actions_assigned ON validation.exercise_actions(assigned_to_id, status);
CREATE INDEX idx_exercise_actions_status ON validation.exercise_actions(status);
CREATE INDEX idx_exercise_actions_overdue ON validation.exercise_actions(due_date) WHERE status != 'completed' AND due_date < CURRENT_DATE;

CREATE TRIGGER update_exercise_actions_updated_at BEFORE UPDATE ON validation.exercise_actions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.exercise_actions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Exercise actions visible to org members" ON validation.exercise_actions FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Exercise actions manageable by org admins" ON validation.exercise_actions FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.exercise_actions IS 'Actions from exercise observations per ISO 22301 Clause 10';

-- Table: validation.kpis
CREATE TABLE validation.kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- KPI identity
    kpi_code VARCHAR(100) NOT NULL,
    kpi_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 9.1
    kpi_category VARCHAR(100) NOT NULL, -- bcms_performance, plan_effectiveness, process_performance, objective_achievement, incident_metrics
    iso_clause VARCHAR(20), -- Which ISO clause this monitors

    -- Measurement
    measurement_unit VARCHAR(50) NOT NULL, -- percentage, count, minutes, hours, days, currency, ratio
    measurement_method TEXT,
    data_source VARCHAR(255), -- Where data comes from

    calculation_formula TEXT, -- How to calculate the KPI
    aggregation_method VARCHAR(50), -- sum, average, max, min, count, percentage

    -- Targets
    target_value DECIMAL(15,2),
    target_operator VARCHAR(10), -- >=, <=, =, >, <
    target_description TEXT,

    warning_threshold DECIMAL(15,2),
    critical_threshold DECIMAL(15,2),

    -- Frequency
    measurement_frequency VARCHAR(50) NOT NULL, -- daily, weekly, monthly, quarterly, annually, per_incident, real_time
    reporting_frequency VARCHAR(50), -- daily, weekly, monthly, quarterly, annually

    -- Ownership
    owner_id UUID REFERENCES auth.users(id),
    data_collector_id UUID REFERENCES auth.users(id),

    -- Related entities
    related_objectives JSONB DEFAULT '[]'::jsonb, -- UUIDs of governance.objectives
    related_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    related_risks JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.risks

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'active', -- active, on_target, at_risk, critical, paused

    -- Current value
    current_value DECIMAL(15,2),
    current_status VARCHAR(50), -- on_target, warning, critical
    last_measured_at TIMESTAMPTZ,

    -- Trend analysis
    trend VARCHAR(50), -- improving, stable, declining
    trend_calculation_period INT, -- Days to look back for trend

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, kpi_code)
);

CREATE INDEX idx_kpis_org ON validation.kpis(organization_id);
CREATE INDEX idx_kpis_code ON validation.kpis(kpi_code);
CREATE INDEX idx_kpis_category ON validation.kpis(kpi_category);
CREATE INDEX idx_kpis_status ON validation.kpis(status);
CREATE INDEX idx_kpis_active ON validation.kpis(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_kpis_updated_at BEFORE UPDATE ON validation.kpis
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.kpis ENABLE ROW LEVEL SECURITY;

CREATE POLICY "KPIs visible to org members" ON validation.kpis FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "KPIs manageable by org admins" ON validation.kpis FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.kpis IS 'Key Performance Indicators per ISO 22301:2019 Clause 9.1';

-- Table: validation.kpi_measurements
CREATE TABLE validation.kpi_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id UUID NOT NULL REFERENCES validation.kpis(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Measurement
    measured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    measurement_period_start DATE,
    measurement_period_end DATE,

    measured_value DECIMAL(15,2) NOT NULL,
    target_value DECIMAL(15,2),

    -- Status at time of measurement
    status VARCHAR(50) NOT NULL, -- on_target, warning, critical, no_target

    variance DECIMAL(15,2), -- Difference from target
    variance_percent DECIMAL(5,2), -- Percentage difference

    -- Context
    measured_by UUID REFERENCES auth.users(id),
    measurement_notes TEXT,

    data_quality VARCHAR(50) DEFAULT 'verified', -- verified, estimated, unverified
    data_source_reference VARCHAR(500),

    -- Related entities
    related_incident_id UUID, -- If measurement is incident-related
    related_exercise_id UUID REFERENCES validation.exercises(id),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_kpi_measurements_kpi ON validation.kpi_measurements(kpi_id, measured_at DESC);
CREATE INDEX idx_kpi_measurements_org ON validation.kpi_measurements(organization_id);
CREATE INDEX idx_kpi_measurements_period ON validation.kpi_measurements(measurement_period_start, measurement_period_end);
CREATE INDEX idx_kpi_measurements_status ON validation.kpi_measurements(status);

ALTER TABLE validation.kpi_measurements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "KPI measurements visible to org members" ON validation.kpi_measurements FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE validation.kpi_measurements IS 'Historical KPI measurements per ISO 22301 Clause 9.1';

-- Table: validation.kpi_dashboards
CREATE TABLE validation.kpi_dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Dashboard identity
    dashboard_code VARCHAR(100) NOT NULL,
    dashboard_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Configuration
    dashboard_type VARCHAR(100), -- executive, operational, compliance, incident_metrics
    kpi_ids JSONB NOT NULL, -- Array of KPI UUIDs to include

    layout_config JSONB, -- Dashboard layout and visualization settings
    refresh_frequency_seconds INT DEFAULT 300,

    -- Access
    is_public BOOLEAN DEFAULT FALSE,
    authorized_roles JSONB DEFAULT '[]'::jsonb,
    authorized_users JSONB DEFAULT '[]'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, dashboard_code)
);

CREATE INDEX idx_kpi_dashboards_org ON validation.kpi_dashboards(organization_id);
CREATE INDEX idx_kpi_dashboards_active ON validation.kpi_dashboards(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_kpi_dashboards_updated_at BEFORE UPDATE ON validation.kpi_dashboards
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.kpi_dashboards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Dashboards visible to org members" ON validation.kpi_dashboards FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Dashboards manageable by org admins" ON validation.kpi_dashboards FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.kpi_dashboards IS 'KPI dashboards for monitoring and reporting';

-- Table: validation.audit_plans
CREATE TABLE validation.audit_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Audit identity
    audit_code VARCHAR(100) NOT NULL,
    audit_title VARCHAR(500) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 9.2
    audit_type VARCHAR(100) NOT NULL, -- internal, external, certification, surveillance, compliance
    audit_scope TEXT NOT NULL, -- What is being audited

    -- Classification
    audit_standard VARCHAR(100), -- ISO_22301, ISO_27001, SOC2, custom
    audited_clauses JSONB DEFAULT '[]'::jsonb, -- Which ISO clauses

    audited_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    audited_locations JSONB DEFAULT '[]'::jsonb,
    audited_departments JSONB DEFAULT '[]'::jsonb,

    -- Planning
    status VARCHAR(50) DEFAULT 'planning', -- planning, scheduled, in_progress, fieldwork_complete, reporting, completed, cancelled

    planned_start_date DATE NOT NULL,
    planned_end_date DATE NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,

    -- Team
    lead_auditor_id UUID REFERENCES auth.users(id),
    audit_team JSONB DEFAULT '[]'::jsonb, -- {user_id, role, is_external}
    auditee_contacts JSONB DEFAULT '[]'::jsonb,

    -- Methodology
    audit_criteria TEXT,
    audit_methodology TEXT,
    sample_size INT,
    sampling_method VARCHAR(100),

    -- Schedule
    audit_schedule JSONB DEFAULT '[]'::jsonb, -- {date, time, activity, location, participants}

    -- Findings summary
    findings_count INT DEFAULT 0,
    critical_findings_count INT DEFAULT 0,
    major_findings_count INT DEFAULT 0,
    minor_findings_count INT DEFAULT 0,
    observations_count INT DEFAULT 0,

    -- Compliance
    is_regulatory_requirement BOOLEAN DEFAULT FALSE,
    regulatory_body VARCHAR(255),
    certification_body VARCHAR(255),

    -- Outcomes
    overall_conformity VARCHAR(50), -- conformant, non_conformant, partial_conformance
    certification_decision VARCHAR(50), -- granted, denied, conditional, pending

    report_issued_date DATE,
    report_file_path VARCHAR(500),

    -- Follow-up
    next_audit_date DATE,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_audit_id UUID REFERENCES validation.audit_plans(id),

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, audit_code)
);

CREATE INDEX idx_audit_plans_org ON validation.audit_plans(organization_id);
CREATE INDEX idx_audit_plans_code ON validation.audit_plans(audit_code);
CREATE INDEX idx_audit_plans_status ON validation.audit_plans(status);
CREATE INDEX idx_audit_plans_type ON validation.audit_plans(audit_type);
CREATE INDEX idx_audit_plans_dates ON validation.audit_plans(planned_start_date, planned_end_date);

CREATE TRIGGER update_audit_plans_updated_at BEFORE UPDATE ON validation.audit_plans
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.audit_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Audit plans visible to org members" ON validation.audit_plans FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Audit plans manageable by org admins" ON validation.audit_plans FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.audit_plans IS 'Internal audit plans per ISO 22301:2019 Clause 9.2';

-- Table: validation.audit_findings
CREATE TABLE validation.audit_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audit_plan_id UUID NOT NULL REFERENCES validation.audit_plans(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Finding identity
    finding_code VARCHAR(100) NOT NULL,
    finding_title VARCHAR(500) NOT NULL,
    finding_description TEXT NOT NULL,

    -- Classification
    finding_type VARCHAR(100) NOT NULL, -- non_conformance, observation, opportunity_for_improvement
    severity VARCHAR(50) NOT NULL, -- critical, major, minor

    -- ISO context
    iso_clause VARCHAR(20), -- Which clause is non-conformant
    requirement_text TEXT, -- The specific requirement

    -- Evidence
    evidence TEXT NOT NULL,
    evidence_files JSONB DEFAULT '[]'::jsonb,
    root_cause TEXT,

    -- Impact
    impact_assessment TEXT,
    affected_processes JSONB DEFAULT '[]'::jsonb,
    affected_controls JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, action_planned, in_progress, verification_pending, closed

    -- Response
    auditee_response TEXT,
    corrective_action_plan TEXT,
    target_closure_date DATE,

    actual_closure_date DATE,
    closed_by UUID REFERENCES auth.users(id),
    closure_notes TEXT,

    -- Verification
    verification_required BOOLEAN DEFAULT TRUE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,
    verification_method TEXT,
    verification_evidence TEXT,

    -- Recurrence tracking
    is_repeat_finding BOOLEAN DEFAULT FALSE,
    previous_finding_id UUID REFERENCES validation.audit_findings(id),
    recurrence_count INT DEFAULT 0,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(organization_id, finding_code)
);

CREATE INDEX idx_audit_findings_plan ON validation.audit_findings(audit_plan_id);
CREATE INDEX idx_audit_findings_org ON validation.audit_findings(organization_id);
CREATE INDEX idx_audit_findings_severity ON validation.audit_findings(severity);
CREATE INDEX idx_audit_findings_status ON validation.audit_findings(status);
CREATE INDEX idx_audit_findings_open ON validation.audit_findings(status) WHERE status != 'closed';

CREATE TRIGGER update_audit_findings_updated_at BEFORE UPDATE ON validation.audit_findings
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.audit_findings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Audit findings visible to org members" ON validation.audit_findings FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Audit findings manageable by org admins" ON validation.audit_findings FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.audit_findings IS 'Audit findings per ISO 22301 Clause 9.2';

-- Table: validation.capa
CREATE TABLE validation.capa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- CAPA identity (Corrective and Preventive Actions)
    capa_code VARCHAR(100) NOT NULL,
    capa_title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- ISO 22301 Clause 10
    capa_type VARCHAR(100) NOT NULL, -- corrective, preventive
    action_category VARCHAR(100), -- process_improvement, control_enhancement, plan_update, training, resource_allocation

    -- Source
    source_type VARCHAR(100) NOT NULL, -- audit_finding, incident, exercise, management_review, risk_assessment, complaint, near_miss
    source_reference_id UUID, -- UUID of the source (finding, incident, etc.)
    source_description TEXT,

    -- Root cause
    root_cause_analysis TEXT,
    root_cause_method VARCHAR(100), -- 5_whys, fishbone, fault_tree, pareto, other
    contributing_factors JSONB DEFAULT '[]'::jsonb,

    -- Action plan
    action_plan TEXT NOT NULL,
    implementation_steps JSONB DEFAULT '[]'::jsonb, -- {step_number, description, assigned_to, due_date, status}

    -- Assignment
    assigned_to_id UUID REFERENCES auth.users(id),
    assigned_to_team_id UUID REFERENCES public.teams(id),
    action_owner_id UUID REFERENCES auth.users(id) NOT NULL,

    -- Timeline
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, implemented, verification_pending, verified, effective, ineffective, closed
    priority VARCHAR(50) NOT NULL, -- critical, high, medium, low

    target_completion_date DATE NOT NULL,
    actual_completion_date DATE,

    implemented_at TIMESTAMPTZ,
    implemented_by UUID REFERENCES auth.users(id),

    -- Verification
    requires_verification BOOLEAN DEFAULT TRUE,
    verification_method TEXT,
    verification_criteria TEXT,

    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES auth.users(id),
    verification_evidence TEXT,
    verification_result VARCHAR(50), -- effective, partially_effective, ineffective

    -- Effectiveness review
    effectiveness_review_date DATE,
    effectiveness_rating INT, -- 1-5 scale
    effectiveness_notes TEXT,
    reviewed_by UUID REFERENCES auth.users(id),

    -- Related entities
    related_risks JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.risks
    related_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    related_controls JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls
    related_objectives JSONB DEFAULT '[]'::jsonb, -- UUIDs of governance.objectives

    -- Impact
    expected_benefits TEXT,
    actual_benefits TEXT,
    estimated_cost DECIMAL(15,2),
    actual_cost DECIMAL(15,2),

    -- Recurrence prevention
    preventive_measures JSONB DEFAULT '[]'::jsonb,
    systemic_changes_made TEXT,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, capa_code)
);

CREATE INDEX idx_capa_org ON validation.capa(organization_id);
CREATE INDEX idx_capa_code ON validation.capa(capa_code);
CREATE INDEX idx_capa_type ON validation.capa(capa_type);
CREATE INDEX idx_capa_status ON validation.capa(status);
CREATE INDEX idx_capa_priority ON validation.capa(priority);
CREATE INDEX idx_capa_assigned ON validation.capa(assigned_to_id, status);
CREATE INDEX idx_capa_overdue ON validation.capa(target_completion_date) WHERE status NOT IN ('verified', 'closed') AND target_completion_date < CURRENT_DATE;

CREATE TRIGGER update_capa_updated_at BEFORE UPDATE ON validation.capa
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.capa ENABLE ROW LEVEL SECURITY;

CREATE POLICY "CAPA visible to org members" ON validation.capa FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "CAPA manageable by org admins" ON validation.capa FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.capa IS 'Corrective and Preventive Actions per ISO 22301:2019 Clause 10';

-- Table: validation.management_reviews
CREATE TABLE validation.management_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Review identity
    review_code VARCHAR(100) NOT NULL,
    review_title VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 9.3
    review_type VARCHAR(100) DEFAULT 'scheduled', -- scheduled, ad_hoc, post_incident, post_exercise

    -- Scheduling
    status VARCHAR(50) DEFAULT 'planning', -- planning, scheduled, in_progress, completed, cancelled
    scheduled_date DATE NOT NULL,
    actual_date DATE,
    duration_hours DECIMAL(5,2),

    -- Participants
    chairperson_id UUID REFERENCES auth.users(id),
    attendees JSONB DEFAULT '[]'::jsonb, -- {user_id, name, role, attended}
    required_attendees JSONB DEFAULT '[]'::jsonb,
    attendance_rate_percent DECIMAL(5,2),

    -- Agenda (ISO 22301 Clause 9.3 requirements)
    agenda JSONB DEFAULT '[]'::jsonb,

    -- Inputs to review (ISO 22301:2019 9.3.2)
    inputs JSONB DEFAULT '{}'::jsonb, -- {
        -- bcms_performance: {...},
        -- nonconformities_capa: {...},
        -- monitoring_measurement_results: {...},
        -- audit_results: {...},
        -- objectives_achievement: {...},
        -- risk_opportunities: {...},
        -- adequacy_resources: {...},
        -- stakeholder_communications: {...},
        -- improvement_recommendations: {...}
    -- }

    -- Outputs (ISO 22301:2019 9.3.3)
    decisions_made JSONB DEFAULT '[]'::jsonb,
    improvement_opportunities JSONB DEFAULT '[]'::jsonb,
    changes_to_bcms JSONB DEFAULT '[]'::jsonb,
    resource_needs JSONB DEFAULT '[]'::jsonb,

    -- Action items
    action_items_count INT DEFAULT 0,
    actions_completed_count INT DEFAULT 0,

    -- Documentation
    minutes_file_path VARCHAR(500),
    minutes_completed BOOLEAN DEFAULT FALSE,
    minutes_approved_by UUID REFERENCES auth.users(id),
    minutes_approved_at TIMESTAMPTZ,

    presentation_files JSONB DEFAULT '[]'::jsonb,
    supporting_documents JSONB DEFAULT '[]'::jsonb,

    -- Key metrics reviewed
    kpis_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of validation.kpis
    incidents_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of incidents
    exercises_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of exercises
    audits_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of audit_plans

    -- Outcomes
    overall_bcms_effectiveness VARCHAR(50), -- highly_effective, effective, needs_improvement, inadequate
    strategic_direction_confirmed BOOLEAN,
    policy_review_required BOOLEAN,
    objectives_review_required BOOLEAN,

    -- Follow-up
    next_review_date DATE,
    follow_up_required BOOLEAN DEFAULT FALSE,

    -- Compliance
    is_regulatory_requirement BOOLEAN DEFAULT TRUE, -- ISO 22301 requires management reviews
    frequency_months INT DEFAULT 12, -- At least annually

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, review_code)
);

CREATE INDEX idx_mgmt_reviews_org ON validation.management_reviews(organization_id);
CREATE INDEX idx_mgmt_reviews_code ON validation.management_reviews(review_code);
CREATE INDEX idx_mgmt_reviews_status ON validation.management_reviews(status);
CREATE INDEX idx_mgmt_reviews_date ON validation.management_reviews(scheduled_date DESC);

CREATE TRIGGER update_mgmt_reviews_updated_at BEFORE UPDATE ON validation.management_reviews
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE validation.management_reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Management reviews visible to org members" ON validation.management_reviews FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Management reviews manageable by org admins" ON validation.management_reviews FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE validation.management_reviews IS 'Management reviews per ISO 22301:2019 Clause 9.3';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 010 completed: Validation schema created (11 tables)';
    RAISE NOTICE '   - exercises: BCM exercises and drills (ISO 22301 Clause 8.5)';
    RAISE NOTICE '   - exercise_scenarios: Exercise scenarios and templates';
    RAISE NOTICE '   - exercise_observations: Observations during exercises';
    RAISE NOTICE '   - exercise_actions: Actions from exercises';
    RAISE NOTICE '   - kpis: Key Performance Indicators (ISO 22301 Clause 9.1)';
    RAISE NOTICE '   - kpi_measurements: Historical KPI data';
    RAISE NOTICE '   - kpi_dashboards: KPI visualization dashboards';
    RAISE NOTICE '   - audit_plans: Internal audit plans (ISO 22301 Clause 9.2)';
    RAISE NOTICE '   - audit_findings: Audit findings and non-conformances';
    RAISE NOTICE '   - capa: Corrective and Preventive Actions (ISO 22301 Clause 10)';
    RAISE NOTICE '   - management_reviews: Management reviews (ISO 22301 Clause 9.3)';
END
$$;
-- ============================================
-- BCM Platform - Unified Database
-- Migration 011: BIA/Risk Extensions
-- ============================================
-- Additional tables for BIA and Risk modules
-- Extends migrations 006 (bia.processes, bia.templates, risk.risks, risk.controls)
-- ISO 22301:2019 Clauses 8.2.2 (BIA), 8.2.3 (Risk Assessment)
-- ============================================

-- Table: bia.impact_assessments
CREATE TABLE bia.impact_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES bia.processes(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Assessment identity
    assessment_code VARCHAR(100),
    assessment_title VARCHAR(255) NOT NULL,

    -- Timeframes (ISO 22301 key concept)
    time_period VARCHAR(50) NOT NULL, -- 0-4h, 4-24h, 1-3d, 3-7d, 1-2w, 2-4w, 1-3m, 3-6m
    time_hours INT, -- Hours from disruption start

    -- Impact categories
    financial_impact DECIMAL(15,2),
    financial_impact_description TEXT,

    operational_impact VARCHAR(50), -- catastrophic, major, moderate, minor, negligible
    operational_impact_description TEXT,

    reputational_impact VARCHAR(50),
    reputational_impact_description TEXT,

    legal_regulatory_impact VARCHAR(50),
    legal_regulatory_impact_description TEXT,

    customer_impact VARCHAR(50),
    customer_impact_description TEXT,
    estimated_customers_affected INT,

    -- Quantitative metrics
    revenue_loss_per_hour DECIMAL(15,2),
    productivity_loss_percent DECIMAL(5,2),
    data_loss_volume VARCHAR(100),

    -- Dependencies affected
    affected_dependencies JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.dependencies
    cascading_impacts TEXT,

    -- Recovery priorities
    priority_score INT, -- Calculated from impacts
    is_critical_timeframe BOOLEAN DEFAULT FALSE, -- Within MTPD?

    -- Scenario
    disruption_scenario TEXT,
    assumptions TEXT,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, outdated
    assessed_by UUID REFERENCES auth.users(id),
    assessed_at TIMESTAMPTZ DEFAULT NOW(),
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_impact_assessments_process ON bia.impact_assessments(process_id);
CREATE INDEX idx_impact_assessments_org ON bia.impact_assessments(organization_id);
CREATE INDEX idx_impact_assessments_timeframe ON bia.impact_assessments(time_period);
CREATE INDEX idx_impact_assessments_critical ON bia.impact_assessments(is_critical_timeframe) WHERE is_critical_timeframe = TRUE;

CREATE TRIGGER update_impact_assessments_updated_at BEFORE UPDATE ON bia.impact_assessments
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bia.impact_assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Impact assessments visible to org members" ON bia.impact_assessments FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Impact assessments manageable by org admins" ON bia.impact_assessments FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE bia.impact_assessments IS 'Time-based impact assessments per ISO 22301 Clause 8.2.2';

-- Table: bia.dependencies
CREATE TABLE bia.dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES bia.processes(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Dependency identity
    dependency_type VARCHAR(100) NOT NULL, -- people, technology, supplier, facility, information, process, utility, transport
    dependency_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Criticality
    criticality VARCHAR(50) NOT NULL, -- critical, high, medium, low
    impact_if_unavailable TEXT,

    -- For People dependencies
    key_roles JSONB DEFAULT '[]'::jsonb, -- Required roles/skills
    minimum_staff_count INT,
    current_staff_count INT,
    succession_plan_exists BOOLEAN DEFAULT FALSE,

    -- For Technology dependencies
    system_name VARCHAR(255),
    system_owner_id UUID REFERENCES auth.users(id),
    rto_minutes INT, -- Recovery Time Objective
    rpo_minutes INT, -- Recovery Point Objective
    backup_exists BOOLEAN DEFAULT FALSE,
    redundancy_level VARCHAR(50), -- none, partial, full

    -- For Supplier dependencies
    supplier_name VARCHAR(255),
    supplier_contact JSONB, -- {name, email, phone}
    contract_number VARCHAR(100),
    alternative_suppliers JSONB DEFAULT '[]'::jsonb,
    supplier_recovery_plan_exists BOOLEAN DEFAULT FALSE,

    -- For Facility dependencies
    facility_name VARCHAR(255),
    facility_location VARCHAR(255),
    alternate_facility_exists BOOLEAN DEFAULT FALSE,
    alternate_facility_location VARCHAR(255),

    -- Availability requirements
    required_availability_percent DECIMAL(5,2),
    maximum_acceptable_outage_hours DECIMAL(10,2),

    -- Relationships
    depends_on JSONB DEFAULT '[]'::jsonb, -- UUIDs of other dependencies
    supports JSONB DEFAULT '[]'::jsonb, -- UUIDs of processes this supports

    -- Risk mitigation
    single_point_of_failure BOOLEAN DEFAULT FALSE,
    mitigation_measures TEXT,
    backup_arrangements TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_verified_date DATE,
    next_review_date DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_dependencies_process ON bia.dependencies(process_id);
CREATE INDEX idx_dependencies_org ON bia.dependencies(organization_id);
CREATE INDEX idx_dependencies_type ON bia.dependencies(dependency_type);
CREATE INDEX idx_dependencies_criticality ON bia.dependencies(criticality);
CREATE INDEX idx_dependencies_spof ON bia.dependencies(single_point_of_failure) WHERE single_point_of_failure = TRUE;

CREATE TRIGGER update_dependencies_updated_at BEFORE UPDATE ON bia.dependencies
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bia.dependencies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Dependencies visible to org members" ON bia.dependencies FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Dependencies manageable by org admins" ON bia.dependencies FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE bia.dependencies IS 'Process dependencies per ISO 22301 Clause 8.2.2';

-- Table: bia.workflow_logs
CREATE TABLE bia.workflow_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID REFERENCES bia.processes(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Workflow event
    event_type VARCHAR(100) NOT NULL, -- created, status_changed, submitted, approved, rejected, updated, commented
    event_description TEXT,

    -- Context
    previous_status VARCHAR(50),
    new_status VARCHAR(50),

    previous_data JSONB, -- Snapshot before change
    new_data JSONB, -- Snapshot after change

    -- Actor
    actor_id UUID REFERENCES auth.users(id),
    actor_name VARCHAR(255),
    actor_role VARCHAR(100),

    -- Approval workflow
    approval_stage INT,
    approver_id UUID REFERENCES auth.users(id),
    approval_decision VARCHAR(50), -- approved, rejected, returned
    approval_comments TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bia_workflow_logs_process ON bia.workflow_logs(process_id, created_at DESC);
CREATE INDEX idx_bia_workflow_logs_org ON bia.workflow_logs(organization_id);
CREATE INDEX idx_bia_workflow_logs_event ON bia.workflow_logs(event_type);
CREATE INDEX idx_bia_workflow_logs_actor ON bia.workflow_logs(actor_id);

ALTER TABLE bia.workflow_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BIA workflow logs visible to org members" ON bia.workflow_logs FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE bia.workflow_logs IS 'Audit trail for BIA workflow events';

-- Table: bia.exports
CREATE TABLE bia.exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Export details
    export_type VARCHAR(100) NOT NULL, -- full_bia, process_report, impact_matrix, dependency_map, summary_report
    export_format VARCHAR(50) NOT NULL, -- pdf, excel, csv, json, docx

    -- Scope
    process_ids JSONB DEFAULT '[]'::jsonb, -- UUIDs of processes to include
    include_confidential BOOLEAN DEFAULT FALSE,

    -- Filters
    filters JSONB DEFAULT '{}'::jsonb, -- Applied filters

    -- File
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size_bytes BIGINT,

    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, generating, completed, failed
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,

    -- Generation details
    generated_by UUID REFERENCES auth.users(id),
    generation_duration_seconds INT,

    -- Access
    downloaded_count INT DEFAULT 0,
    last_downloaded_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bia_exports_org ON bia.exports(organization_id, created_at DESC);
CREATE INDEX idx_bia_exports_status ON bia.exports(status);
CREATE INDEX idx_bia_exports_generated_by ON bia.exports(generated_by, created_at DESC);

ALTER TABLE bia.exports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BIA exports visible to org members" ON bia.exports FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE bia.exports IS 'BIA report exports and downloads';

-- ======================
-- RISK SCHEMA EXTENSIONS
-- ======================

-- Table: risk.assessments
CREATE TABLE risk.assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id UUID NOT NULL REFERENCES risk.risks(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Assessment identity
    assessment_code VARCHAR(100),
    assessment_title VARCHAR(255),

    -- Assessment type
    assessment_type VARCHAR(100) NOT NULL, -- initial, reassessment, post_incident, scheduled, ad_hoc
    methodology VARCHAR(100), -- quantitative, qualitative, semi_quantitative, bow_tie, fmea

    -- ISO 22301 Clause 8.2.3
    likelihood_score INT NOT NULL, -- 1-5 scale
    likelihood_rationale TEXT,

    consequence_score INT NOT NULL, -- 1-5 scale
    consequence_rationale TEXT,

    -- Risk level
    risk_score INT, -- likelihood * consequence
    risk_level VARCHAR(50), -- critical, high, medium, low
    risk_priority INT, -- For prioritization

    -- Timeframe
    assessment_date DATE NOT NULL,
    review_date DATE,
    next_assessment_date DATE,

    -- Assessors
    lead_assessor_id UUID REFERENCES auth.users(id),
    assessment_team JSONB DEFAULT '[]'::jsonb, -- {user_id, role}

    -- Context
    threat_sources JSONB DEFAULT '[]'::jsonb,
    vulnerabilities JSONB DEFAULT '[]'::jsonb,
    existing_controls JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls

    -- Impact analysis
    financial_impact DECIMAL(15,2),
    operational_impact TEXT,
    reputational_impact TEXT,
    compliance_impact TEXT,

    -- Treatment decision
    treatment_decision VARCHAR(100), -- accept, mitigate, transfer, avoid
    treatment_justification TEXT,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, review, approved, superseded
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    -- Residual risk (after controls)
    residual_likelihood_score INT,
    residual_consequence_score INT,
    residual_risk_score INT,
    residual_risk_level VARCHAR(50),

    -- Metadata
    assumptions TEXT,
    limitations TEXT,
    confidence_level VARCHAR(50), -- high, medium, low
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_risk_assessments_risk ON risk.assessments(risk_id, assessment_date DESC);
CREATE INDEX idx_risk_assessments_org ON risk.assessments(organization_id);
CREATE INDEX idx_risk_assessments_level ON risk.assessments(risk_level);
CREATE INDEX idx_risk_assessments_date ON risk.assessments(assessment_date DESC);

CREATE TRIGGER update_risk_assessments_updated_at BEFORE UPDATE ON risk.assessments
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE risk.assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk assessments visible to org members" ON risk.assessments FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Risk assessments manageable by org admins" ON risk.assessments FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE risk.assessments IS 'Risk assessments per ISO 22301:2019 Clause 8.2.3';

-- Table: risk.treatments
CREATE TABLE risk.treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id UUID NOT NULL REFERENCES risk.risks(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Treatment identity
    treatment_code VARCHAR(100),
    treatment_title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- Treatment strategy
    strategy VARCHAR(100) NOT NULL, -- mitigate_likelihood, mitigate_consequence, transfer, accept, avoid
    rationale TEXT,

    -- Implementation
    implementation_plan TEXT,
    implementation_steps JSONB DEFAULT '[]'::jsonb, -- {step_number, description, assigned_to, due_date, status}

    -- Assignment
    owner_id UUID REFERENCES auth.users(id) NOT NULL,
    assigned_to_id UUID REFERENCES auth.users(id),
    assigned_to_team_id UUID REFERENCES public.teams(id),

    -- Timeline
    status VARCHAR(50) DEFAULT 'planned', -- planned, in_progress, implemented, verified, ineffective, cancelled
    priority VARCHAR(50) NOT NULL, -- critical, high, medium, low

    planned_start_date DATE,
    planned_completion_date DATE NOT NULL,
    actual_start_date DATE,
    actual_completion_date DATE,

    -- Resources
    estimated_cost DECIMAL(15,2),
    actual_cost DECIMAL(15,2),
    budget_approved BOOLEAN DEFAULT FALSE,
    required_resources TEXT,

    -- Controls to implement
    controls_to_implement JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls

    -- Effectiveness
    expected_risk_reduction TEXT,
    expected_residual_risk_level VARCHAR(50),

    actual_risk_reduction TEXT,
    effectiveness_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,

    -- Dependencies
    depends_on JSONB DEFAULT '[]'::jsonb, -- UUIDs of other treatments
    blocks JSONB DEFAULT '[]'::jsonb, -- UUIDs of treatments waiting for this

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_risk_treatments_risk ON risk.treatments(risk_id);
CREATE INDEX idx_risk_treatments_org ON risk.treatments(organization_id);
CREATE INDEX idx_risk_treatments_owner ON risk.treatments(owner_id, status);
CREATE INDEX idx_risk_treatments_status ON risk.treatments(status);
CREATE INDEX idx_risk_treatments_overdue ON risk.treatments(planned_completion_date) WHERE status NOT IN ('implemented', 'verified', 'cancelled') AND planned_completion_date < CURRENT_DATE;

CREATE TRIGGER update_risk_treatments_updated_at BEFORE UPDATE ON risk.treatments
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE risk.treatments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk treatments visible to org members" ON risk.treatments FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Risk treatments manageable by org admins" ON risk.treatments FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE risk.treatments IS 'Risk treatment plans per ISO 22301 Clause 8.2.3';

-- Table: risk.templates
CREATE TABLE risk.templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Template identity
    template_code VARCHAR(100) NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Template type
    template_type VARCHAR(100) NOT NULL, -- risk, control, assessment, treatment
    category VARCHAR(100), -- cyber, physical, operational, strategic, compliance, financial

    -- Template content (for risks)
    risk_name_template VARCHAR(255),
    risk_description_template TEXT,
    threat_sources_template JSONB DEFAULT '[]'::jsonb,
    vulnerabilities_template JSONB DEFAULT '[]'::jsonb,

    -- Template content (for controls)
    control_name_template VARCHAR(255),
    control_description_template TEXT,
    control_type VARCHAR(100), -- preventive, detective, corrective
    implementation_guidance TEXT,

    -- Suggested ratings
    suggested_likelihood INT,
    suggested_consequence INT,
    suggested_priority VARCHAR(50),

    -- Related standards
    iso_22301_clauses JSONB DEFAULT '[]'::jsonb,
    other_frameworks JSONB DEFAULT '[]'::jsonb, -- NIST, CIS, etc.

    -- Usage
    is_system_template BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INT DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, template_code)
);

CREATE INDEX idx_risk_templates_org ON risk.templates(organization_id);
CREATE INDEX idx_risk_templates_type ON risk.templates(template_type);
CREATE INDEX idx_risk_templates_category ON risk.templates(category);
CREATE INDEX idx_risk_templates_active ON risk.templates(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_risk_templates_updated_at BEFORE UPDATE ON risk.templates
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE risk.templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk templates visible to org members" ON risk.templates FOR SELECT
    USING (organization_id IS NULL OR public.is_org_member(organization_id));

CREATE POLICY "Risk templates manageable by org admins" ON risk.templates FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE risk.templates IS 'Risk and control templates for standardization';

-- Table: risk.workflow_logs
CREATE TABLE risk.workflow_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id UUID REFERENCES risk.risks(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Workflow event
    event_type VARCHAR(100) NOT NULL, -- created, assessment_completed, treatment_planned, status_changed, escalated, review_completed
    event_description TEXT,

    -- Context
    previous_status VARCHAR(50),
    new_status VARCHAR(50),

    previous_risk_level VARCHAR(50),
    new_risk_level VARCHAR(50),

    previous_data JSONB,
    new_data JSONB,

    -- Actor
    actor_id UUID REFERENCES auth.users(id),
    actor_name VARCHAR(255),
    actor_role VARCHAR(100),

    -- Related entities
    related_assessment_id UUID REFERENCES risk.assessments(id),
    related_treatment_id UUID REFERENCES risk.treatments(id),
    related_control_id UUID REFERENCES risk.controls(id),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_risk_workflow_logs_risk ON risk.workflow_logs(risk_id, created_at DESC);
CREATE INDEX idx_risk_workflow_logs_org ON risk.workflow_logs(organization_id);
CREATE INDEX idx_risk_workflow_logs_event ON risk.workflow_logs(event_type);
CREATE INDEX idx_risk_workflow_logs_actor ON risk.workflow_logs(actor_id);

ALTER TABLE risk.workflow_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Risk workflow logs visible to org members" ON risk.workflow_logs FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE risk.workflow_logs IS 'Audit trail for risk management workflow events';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 011 completed: BIA/Risk extensions (8 tables)';
    RAISE NOTICE '   BIA Schema:';
    RAISE NOTICE '   - impact_assessments: Time-based impact analysis';
    RAISE NOTICE '   - dependencies: Process dependencies (people, tech, suppliers, facilities)';
    RAISE NOTICE '   - workflow_logs: BIA workflow audit trail';
    RAISE NOTICE '   - exports: BIA report exports';
    RAISE NOTICE '   Risk Schema:';
    RAISE NOTICE '   - assessments: Risk assessments with likelihood/consequence';
    RAISE NOTICE '   - treatments: Risk treatment plans';
    RAISE NOTICE '   - templates: Risk and control templates';
    RAISE NOTICE '   - workflow_logs: Risk workflow audit trail';
END
$$;
-- ============================================
-- BCM Platform - Unified Database
-- Migration 012: Governance & Compliance Extensions
-- ============================================
-- Extends migration 007 (governance.policies, governance.roles, governance.objectives)
-- ISO 22301:2019 Clauses:
--   5 (Leadership)
--   6 (Planning)
--   7 (Support)
--   4.4 (BCMS and its processes)
-- Schemas: governance, bcm
-- ============================================

-- Table: governance.policy_versions
CREATE TABLE governance.policy_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID NOT NULL REFERENCES governance.policies(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Version details
    version_number VARCHAR(50) NOT NULL,
    version_date DATE NOT NULL,

    -- Content snapshot
    policy_name VARCHAR(255) NOT NULL,
    policy_content TEXT NOT NULL,

    -- Approval
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,
    approval_notes TEXT,

    -- Change tracking
    change_summary TEXT,
    changed_sections JSONB DEFAULT '[]'::jsonb,
    change_reason VARCHAR(100), -- scheduled_review, regulatory_change, incident, improvement, correction

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, superseded, archived
    effective_date DATE,
    expiry_date DATE,

    -- Files
    file_path VARCHAR(500),
    file_hash VARCHAR(128), -- SHA-256 for integrity

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_policy_versions_policy ON governance.policy_versions(policy_id, version_date DESC);
CREATE INDEX idx_policy_versions_org ON governance.policy_versions(organization_id);
CREATE INDEX idx_policy_versions_status ON governance.policy_versions(status);

ALTER TABLE governance.policy_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Policy versions visible to org members" ON governance.policy_versions FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE governance.policy_versions IS 'Policy version history for audit trail';

-- Table: bcm.resources
CREATE TABLE bcm.resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Resource identity
    resource_code VARCHAR(100) NOT NULL,
    resource_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 7.1 (Resources)
    resource_type VARCHAR(100) NOT NULL, -- financial, people, equipment, facility, technology, knowledge, suppliers, partners
    resource_category VARCHAR(100), -- critical, important, standard, backup

    -- For People resources
    role_title VARCHAR(255),
    required_skills JSONB DEFAULT '[]'::jsonb,
    current_staff_count INT,
    required_staff_count INT,
    training_required TEXT,

    -- For Equipment/Technology resources
    equipment_type VARCHAR(100),
    quantity_available INT,
    quantity_required INT,
    location VARCHAR(255),
    maintenance_schedule TEXT,
    replacement_cost DECIMAL(15,2),

    -- For Facility resources
    facility_name VARCHAR(255),
    facility_type VARCHAR(100), -- office, datacenter, warehouse, alternate_site
    capacity VARCHAR(100),
    access_requirements TEXT,

    -- For Financial resources
    annual_budget DECIMAL(15,2),
    allocated_budget DECIMAL(15,2),
    spent_budget DECIMAL(15,2),

    -- Availability
    availability_status VARCHAR(50) DEFAULT 'available', -- available, in_use, unavailable, maintenance
    is_shared_resource BOOLEAN DEFAULT FALSE,
    shared_with JSONB DEFAULT '[]'::jsonb, -- Which processes/teams share this

    -- Owner and responsibility
    owner_id UUID REFERENCES auth.users(id),
    custodian_id UUID REFERENCES auth.users(id),
    responsible_team_id UUID REFERENCES public.teams(id),

    -- Allocation
    allocated_to_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    allocated_to_teams JSONB DEFAULT '[]'::jsonb, -- UUIDs of teams

    -- Procurement
    procurement_status VARCHAR(50), -- approved, pending, procured, delivered
    vendor_name VARCHAR(255),
    vendor_contact JSONB,
    procurement_lead_time_days INT,

    -- Criticality for BCM
    is_critical_resource BOOLEAN DEFAULT FALSE,
    single_point_of_failure BOOLEAN DEFAULT FALSE,
    backup_available BOOLEAN DEFAULT FALSE,
    backup_resource_id UUID REFERENCES bcm.resources(id),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_verified_date DATE,
    next_review_date DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, resource_code)
);

CREATE INDEX idx_bcm_resources_org ON bcm.resources(organization_id);
CREATE INDEX idx_bcm_resources_code ON bcm.resources(resource_code);
CREATE INDEX idx_bcm_resources_type ON bcm.resources(resource_type);
CREATE INDEX idx_bcm_resources_critical ON bcm.resources(is_critical_resource) WHERE is_critical_resource = TRUE;
CREATE INDEX idx_bcm_resources_spof ON bcm.resources(single_point_of_failure) WHERE single_point_of_failure = TRUE;

CREATE TRIGGER update_bcm_resources_updated_at BEFORE UPDATE ON bcm.resources
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.resources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "BCM resources visible to org members" ON bcm.resources FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "BCM resources manageable by org admins" ON bcm.resources FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE bcm.resources IS 'BCM resources per ISO 22301:2019 Clause 7.1';

-- Table: bcm.competence_records
CREATE TABLE bcm.competence_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Person
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name VARCHAR(255),
    user_role VARCHAR(100),

    -- ISO 22301 Clause 7.2 (Competence)
    competency_area VARCHAR(100) NOT NULL, -- bcm_planning, bia, risk_assessment, incident_response, crisis_management, exercise_facilitation, audit

    -- Competency level
    competency_level VARCHAR(50) NOT NULL, -- novice, intermediate, advanced, expert
    assessment_method VARCHAR(100), -- training, certification, experience, exercise_performance, manager_assessment

    -- Evidence
    evidence_type VARCHAR(100), -- certification, training_completion, work_experience, exercise_participation, assessment
    evidence_description TEXT,
    evidence_file_path VARCHAR(500),

    -- Certification details
    certification_name VARCHAR(255),
    certification_body VARCHAR(255),
    certification_number VARCHAR(100),
    certification_date DATE,
    certification_expiry_date DATE,

    -- Training details
    training_course_name VARCHAR(255),
    training_provider VARCHAR(255),
    training_completion_date DATE,
    training_hours DECIMAL(10,2),

    -- Experience details
    years_of_experience DECIMAL(5,2),
    relevant_roles JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'current', -- current, expiring_soon, expired, pending_renewal
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,

    -- Renewal
    renewal_required BOOLEAN DEFAULT FALSE,
    renewal_due_date DATE,
    renewal_reminder_sent BOOLEAN DEFAULT FALSE,

    -- Metadata
    notes TEXT,
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_competence_records_org ON bcm.competence_records(organization_id);
CREATE INDEX idx_competence_records_user ON bcm.competence_records(user_id);
CREATE INDEX idx_competence_records_area ON bcm.competence_records(competency_area);
CREATE INDEX idx_competence_records_status ON bcm.competence_records(status);
CREATE INDEX idx_competence_records_expiring ON bcm.competence_records(certification_expiry_date) WHERE certification_expiry_date IS NOT NULL AND status = 'current';

CREATE TRIGGER update_competence_records_updated_at BEFORE UPDATE ON bcm.competence_records
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.competence_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Competence records visible to org members" ON bcm.competence_records FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Users see their own competence records" ON bcm.competence_records FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE bcm.competence_records IS 'Competency evidence per ISO 22301:2019 Clause 7.2';

-- Table: bcm.communication_plans
CREATE TABLE bcm.communication_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Plan identity
    plan_code VARCHAR(100) NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ISO 22301 Clause 7.4 (Communication)
    plan_type VARCHAR(100) NOT NULL, -- stakeholder_engagement, incident_communication, awareness, training, reporting

    -- Stakeholder groups
    stakeholder_groups JSONB NOT NULL, -- Array of {group_name, type, priority, contact_method}

    -- Communication matrix
    what_to_communicate JSONB DEFAULT '[]'::jsonb, -- Topics/information to communicate
    when_to_communicate JSONB DEFAULT '[]'::jsonb, -- Timing/triggers
    how_to_communicate JSONB DEFAULT '[]'::jsonb, -- Channels/methods
    who_communicates JSONB DEFAULT '[]'::jsonb, -- Roles responsible

    -- Channels
    primary_channels JSONB DEFAULT '[]'::jsonb, -- email, sms, phone, teams, slack, website, social_media
    backup_channels JSONB DEFAULT '[]'::jsonb,

    -- Templates
    message_templates JSONB DEFAULT '[]'::jsonb, -- {template_name, audience, content}

    -- Approval requirements
    requires_approval BOOLEAN DEFAULT FALSE,
    approval_authority VARCHAR(100),
    approval_workflow JSONB,

    -- Frequency
    communication_frequency VARCHAR(50), -- as_needed, daily, weekly, monthly, quarterly, annual
    scheduled_communications JSONB DEFAULT '[]'::jsonb,

    -- Effectiveness
    effectiveness_measures JSONB DEFAULT '[]'::jsonb, -- How to measure success
    last_effectiveness_review_date DATE,
    effectiveness_rating VARCHAR(50), -- highly_effective, effective, needs_improvement, ineffective

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, active, under_review, archived
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,

    is_active BOOLEAN DEFAULT TRUE,
    activation_triggers JSONB DEFAULT '[]'::jsonb, -- When this plan activates

    -- Maintenance
    owner_id UUID REFERENCES auth.users(id),
    last_reviewed_date DATE,
    next_review_date DATE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, plan_code)
);

CREATE INDEX idx_comm_plans_org ON bcm.communication_plans(organization_id);
CREATE INDEX idx_comm_plans_code ON bcm.communication_plans(plan_code);
CREATE INDEX idx_comm_plans_type ON bcm.communication_plans(plan_type);
CREATE INDEX idx_comm_plans_status ON bcm.communication_plans(status);
CREATE INDEX idx_comm_plans_active ON bcm.communication_plans(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_comm_plans_updated_at BEFORE UPDATE ON bcm.communication_plans
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.communication_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Communication plans visible to org members" ON bcm.communication_plans FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Communication plans manageable by org admins" ON bcm.communication_plans FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE bcm.communication_plans IS 'Communication plans per ISO 22301:2019 Clause 7.4';

-- =========================
-- COMPLIANCE SCHEMA
-- =========================

CREATE SCHEMA IF NOT EXISTS compliance;
COMMENT ON SCHEMA compliance IS 'Compliance management and tracking';

-- Table: compliance.requirements
CREATE TABLE compliance.requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Requirement identity
    requirement_code VARCHAR(100) NOT NULL,
    requirement_title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,

    -- Source
    framework VARCHAR(100) NOT NULL, -- ISO_22301, ISO_27001, GDPR, SOC2, HIPAA, PCI_DSS, custom
    framework_version VARCHAR(50),
    clause_reference VARCHAR(50), -- e.g., "8.2.2" for ISO 22301

    -- Classification
    requirement_type VARCHAR(100), -- mandatory, recommended, optional, best_practice
    category VARCHAR(100), -- governance, risk, operations, technical, documentation

    -- Applicability
    applies_to VARCHAR(100), -- entire_organization, specific_processes, specific_systems
    applicable_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes
    applicable_systems JSONB DEFAULT '[]'::jsonb,

    is_applicable BOOLEAN DEFAULT TRUE,
    applicability_rationale TEXT,

    -- Compliance status
    compliance_status VARCHAR(50) NOT NULL DEFAULT 'not_assessed', -- compliant, partially_compliant, non_compliant, not_applicable, not_assessed
    compliance_percentage DECIMAL(5,2),

    -- Evidence
    evidence_required TEXT,
    evidence_description TEXT,

    -- Implementation
    implementation_guidance TEXT,
    control_objectives TEXT,

    -- Ownership
    owner_id UUID REFERENCES auth.users(id),
    responsible_team_id UUID REFERENCES public.teams(id),

    -- Related entities
    related_policies JSONB DEFAULT '[]'::jsonb, -- UUIDs of governance.policies
    related_controls JSONB DEFAULT '[]'::jsonb, -- UUIDs of risk.controls
    related_procedures JSONB DEFAULT '[]'::jsonb,

    -- Assessment
    last_assessment_date DATE,
    next_assessment_date DATE,
    assessment_frequency_months INT DEFAULT 12,

    -- Priority
    priority VARCHAR(50), -- critical, high, medium, low
    regulatory_deadline DATE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(requirement_code,'') || ' ' ||
            coalesce(requirement_title,'') || ' ' ||
            coalesce(description,'') || ' ' ||
            coalesce(framework,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, requirement_code)
);

CREATE INDEX idx_compliance_requirements_org ON compliance.requirements(organization_id);
CREATE INDEX idx_compliance_requirements_code ON compliance.requirements(requirement_code);
CREATE INDEX idx_compliance_requirements_framework ON compliance.requirements(framework);
CREATE INDEX idx_compliance_requirements_status ON compliance.requirements(compliance_status);
CREATE INDEX idx_compliance_requirements_search ON compliance.requirements USING GIN(search_vector);
CREATE INDEX idx_compliance_requirements_non_compliant ON compliance.requirements(compliance_status) WHERE compliance_status IN ('non_compliant', 'partially_compliant');

CREATE TRIGGER update_compliance_requirements_updated_at BEFORE UPDATE ON compliance.requirements
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE compliance.requirements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance requirements visible to org members" ON compliance.requirements FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Compliance requirements manageable by org admins" ON compliance.requirements FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE compliance.requirements IS 'Compliance requirements from various frameworks';

-- Table: compliance.evidence
CREATE TABLE compliance.evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES compliance.requirements(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Evidence identity
    evidence_code VARCHAR(100),
    evidence_title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Evidence type
    evidence_type VARCHAR(100) NOT NULL, -- document, screenshot, log_export, report, certificate, attestation, interview_notes, observation
    evidence_source VARCHAR(100), -- manual_upload, automated_collection, system_export, audit

    -- File details
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    file_hash VARCHAR(128), -- SHA-256

    -- Content
    evidence_content TEXT, -- For text-based evidence
    evidence_url VARCHAR(500), -- For external evidence

    -- Collection
    collected_date DATE NOT NULL,
    collection_method VARCHAR(100), -- manual, automated, screenshot, export
    collected_by UUID REFERENCES auth.users(id),

    -- Validity
    valid_from DATE NOT NULL,
    valid_until DATE,
    is_current BOOLEAN DEFAULT TRUE,

    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES auth.users(id),
    verified_at TIMESTAMPTZ,
    verification_notes TEXT,

    -- Retention
    retention_period_years INT,
    disposal_date DATE,

    -- Related entities
    related_audit_id UUID, -- UUID of validation.audit_plans
    related_assessment_id UUID, -- UUID of compliance.assessments

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_compliance_evidence_requirement ON compliance.evidence(requirement_id);
CREATE INDEX idx_compliance_evidence_org ON compliance.evidence(organization_id);
CREATE INDEX idx_compliance_evidence_type ON compliance.evidence(evidence_type);
CREATE INDEX idx_compliance_evidence_current ON compliance.evidence(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_compliance_evidence_expiring ON compliance.evidence(valid_until) WHERE is_current = TRUE AND valid_until IS NOT NULL;

CREATE TRIGGER update_compliance_evidence_updated_at BEFORE UPDATE ON compliance.evidence
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE compliance.evidence ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance evidence visible to org members" ON compliance.evidence FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE compliance.evidence IS 'Evidence of compliance with requirements';

-- Table: compliance.assessments
CREATE TABLE compliance.assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES compliance.requirements(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Assessment details
    assessment_code VARCHAR(100),
    assessment_date DATE NOT NULL,
    assessment_type VARCHAR(100) NOT NULL, -- self_assessment, internal_audit, external_audit, certification, continuous_monitoring

    -- Assessor
    assessor_id UUID REFERENCES auth.users(id),
    assessor_name VARCHAR(255),
    assessor_role VARCHAR(100),

    -- Findings
    compliance_status VARCHAR(50) NOT NULL, -- compliant, partially_compliant, non_compliant, not_applicable
    compliance_score DECIMAL(5,2), -- 0-100

    findings TEXT,
    strengths TEXT,
    weaknesses TEXT,
    recommendations TEXT,

    -- Evidence reviewed
    evidence_reviewed JSONB DEFAULT '[]'::jsonb, -- UUIDs of compliance.evidence

    -- Gaps identified
    gaps_identified JSONB DEFAULT '[]'::jsonb, -- {gap_description, severity, impact}

    -- Actions required
    corrective_actions_required BOOLEAN DEFAULT FALSE,
    action_items JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, in_review, completed, approved
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

CREATE INDEX idx_compliance_assessments_requirement ON compliance.assessments(requirement_id, assessment_date DESC);
CREATE INDEX idx_compliance_assessments_org ON compliance.assessments(organization_id);
CREATE INDEX idx_compliance_assessments_status ON compliance.assessments(compliance_status);
CREATE INDEX idx_compliance_assessments_date ON compliance.assessments(assessment_date DESC);

CREATE TRIGGER update_compliance_assessments_updated_at BEFORE UPDATE ON compliance.assessments
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE compliance.assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance assessments visible to org members" ON compliance.assessments FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE compliance.assessments IS 'Compliance assessments for requirements';

-- Table: compliance.gaps
CREATE TABLE compliance.gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES compliance.requirements(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Gap identity
    gap_code VARCHAR(100),
    gap_title VARCHAR(500) NOT NULL,
    gap_description TEXT NOT NULL,

    -- Source
    identified_by VARCHAR(100), -- self_assessment, audit, incident, exercise, risk_assessment
    identified_date DATE NOT NULL,
    identified_by_user_id UUID REFERENCES auth.users(id),

    related_assessment_id UUID REFERENCES compliance.assessments(id),

    -- Severity
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low
    priority VARCHAR(50) NOT NULL, -- immediate, urgent, high, medium, low

    -- Impact
    impact_description TEXT,
    potential_consequences TEXT,
    regulatory_risk TEXT,

    -- Remediation
    remediation_plan TEXT,
    remediation_owner_id UUID REFERENCES auth.users(id),
    target_closure_date DATE NOT NULL,
    actual_closure_date DATE,

    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, action_planned, in_progress, verification_pending, closed, accepted_risk
    resolution_notes TEXT,

    -- Related CAPA
    related_capa_id UUID, -- UUID of validation.capa

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_compliance_gaps_requirement ON compliance.gaps(requirement_id);
CREATE INDEX idx_compliance_gaps_org ON compliance.gaps(organization_id);
CREATE INDEX idx_compliance_gaps_severity ON compliance.gaps(severity);
CREATE INDEX idx_compliance_gaps_status ON compliance.gaps(status);
CREATE INDEX idx_compliance_gaps_open ON compliance.gaps(status) WHERE status NOT IN ('closed', 'accepted_risk');
CREATE INDEX idx_compliance_gaps_overdue ON compliance.gaps(target_closure_date) WHERE status NOT IN ('closed', 'accepted_risk') AND target_closure_date < CURRENT_DATE;

CREATE TRIGGER update_compliance_gaps_updated_at BEFORE UPDATE ON compliance.gaps
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE compliance.gaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Compliance gaps visible to org members" ON compliance.gaps FOR SELECT
    USING (public.is_org_member(organization_id));

COMMENT ON TABLE compliance.gaps IS 'Compliance gaps and remediation tracking';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 012 completed: Governance & Compliance (9 tables)';
    RAISE NOTICE '   Governance Schema Extensions:';
    RAISE NOTICE '   - policy_versions: Policy version history';
    RAISE NOTICE '   BCM Schema:';
    RAISE NOTICE '   - resources: BCM resources (ISO 22301 Clause 7.1)';
    RAISE NOTICE '   - competence_records: Competency tracking (ISO 22301 Clause 7.2)';
    RAISE NOTICE '   - communication_plans: Communication planning (ISO 22301 Clause 7.4)';
    RAISE NOTICE '   Compliance Schema (NEW):';
    RAISE NOTICE '   - requirements: Compliance requirements from frameworks';
    RAISE NOTICE '   - evidence: Evidence of compliance';
    RAISE NOTICE '   - assessments: Compliance assessments';
    RAISE NOTICE '   - gaps: Compliance gaps and remediation';
END
$$;
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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.training_programs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Training programs visible to org members" ON learning.training_programs FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Training programs manageable by org admins" ON learning.training_programs FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.enrollments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enrollments visible to org members" ON learning.enrollments FOR SELECT
    USING (public.is_org_member(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.competency_assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Competency assessments visible to org admins" ON learning.competency_assessments FOR SELECT
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.awareness_campaigns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Awareness campaigns visible to org members" ON learning.awareness_campaigns FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Awareness campaigns manageable by org admins" ON learning.awareness_campaigns FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE learning.training_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Training templates visible to all org members" ON learning.training_templates FOR SELECT
    USING (organization_id IS NULL OR public.is_org_member(organization_id));

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
    USING (public.is_org_member(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Plans visible to org members" ON bcm.plans FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Plans manageable by org admins" ON bcm.plans FOR ALL
    USING (public.is_org_admin(organization_id));

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
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE bcm.procedures ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Procedures visible to org members" ON bcm.procedures FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Procedures manageable by org admins" ON bcm.procedures FOR ALL
    USING (public.is_org_admin(organization_id));

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
