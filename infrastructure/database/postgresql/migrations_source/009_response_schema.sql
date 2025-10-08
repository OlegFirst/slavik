-- ============================================
-- BCM Platform - Unified Database
-- Migration 009: Response Schema
-- ============================================
-- ISO 22301:2019 Clauses 8.4.2 (Incident Response), 8.4.3 (Warning & Communication)
-- Incident management, crisis response, notifications, escalations
-- Schema: response (incident response & crisis management)
-- ============================================

-- Table: response.incidents
CREATE TABLE response.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Incident identity
    incident_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- Classification
    incident_type VARCHAR(100) NOT NULL, -- disruption, threat, near_miss, exercise, drill
    severity VARCHAR(50) NOT NULL, -- critical, high, medium, low
    impact_level VARCHAR(50), -- catastrophic, major, moderate, minor, negligible
    category VARCHAR(100), -- cyber, natural_disaster, supply_chain, personnel, infrastructure, etc.

    -- ISO 22301 classification
    is_disruptive_event BOOLEAN DEFAULT FALSE,
    triggers_bcm_plan BOOLEAN DEFAULT FALSE,
    related_risks JSONB DEFAULT '[]'::jsonb, -- UUIDs of related risk.risks
    affected_processes JSONB DEFAULT '[]'::jsonb, -- UUIDs of bia.processes

    -- Status and lifecycle
    status VARCHAR(50) DEFAULT 'reported', -- reported, investigating, responding, recovering, resolved, closed
    priority VARCHAR(50), -- p1_critical, p2_high, p3_medium, p4_low

    detected_at TIMESTAMPTZ NOT NULL,
    reported_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    response_started_at TIMESTAMPTZ,
    contained_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,

    -- Response coordination
    incident_commander_id UUID REFERENCES auth.users(id),
    response_team_id UUID, -- Will reference response.response_teams(id)
    activated_plans JSONB DEFAULT '[]'::jsonb, -- Which BCM plans were activated

    -- Impact assessment
    affected_locations JSONB DEFAULT '[]'::jsonb,
    affected_departments JSONB DEFAULT '[]'::jsonb,
    affected_customers_count INT,
    estimated_financial_impact DECIMAL(15,2),
    actual_financial_impact DECIMAL(15,2),

    -- Recovery metrics
    rto_target_minutes INT, -- Recovery Time Objective
    rto_actual_minutes INT,
    rpo_target_minutes INT, -- Recovery Point Objective
    rpo_actual_minutes INT,

    -- Communications
    public_statement TEXT,
    internal_summary TEXT,
    stakeholder_notifications_sent INT DEFAULT 0,

    -- Post-incident
    root_cause TEXT,
    lessons_learned TEXT,
    corrective_actions JSONB DEFAULT '[]'::jsonb,
    preventive_actions JSONB DEFAULT '[]'::jsonb,

    -- References
    related_incidents JSONB DEFAULT '[]'::jsonb, -- UUIDs of related incidents
    external_references JSONB DEFAULT '[]'::jsonb, -- Ticket systems, etc.

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,
    custom_fields JSONB DEFAULT '{}'::jsonb,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            coalesce(incident_code,'') || ' ' ||
            coalesce(title,'') || ' ' ||
            coalesce(description,'') || ' ' ||
            coalesce(category,'')
        )
    ) STORED,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_incidents_org ON response.incidents(organization_id);
CREATE INDEX idx_incidents_code ON response.incidents(incident_code);
CREATE INDEX idx_incidents_status ON response.incidents(status);
CREATE INDEX idx_incidents_severity ON response.incidents(severity);
CREATE INDEX idx_incidents_type ON response.incidents(incident_type);
CREATE INDEX idx_incidents_detected ON response.incidents(detected_at DESC);
CREATE INDEX idx_incidents_search ON response.incidents USING GIN(search_vector);
CREATE INDEX idx_incidents_active ON response.incidents(status) WHERE status IN ('reported', 'investigating', 'responding');

CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON response.incidents
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.incidents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Incidents visible to org members" ON response.incidents FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Incidents manageable by org admins" ON response.incidents FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.incidents IS 'Incident tracking per ISO 22301:2019 Clause 8.4.2';

-- Table: response.response_teams
CREATE TABLE response.response_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Team identity
    team_code VARCHAR(100) NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Team type
    team_type VARCHAR(100) NOT NULL, -- imt (Incident Management Team), cmt (Crisis Management Team), brt (Business Recovery Team), technical, communications

    -- Activation
    is_standing_team BOOLEAN DEFAULT TRUE, -- Permanent vs. ad-hoc
    activation_criteria TEXT,
    activation_authority VARCHAR(100), -- Who can activate this team

    is_active BOOLEAN DEFAULT TRUE,
    activated_at TIMESTAMPTZ,
    deactivated_at TIMESTAMPTZ,

    -- Team composition
    team_lead_id UUID REFERENCES auth.users(id),
    deputy_lead_id UUID REFERENCES auth.users(id),
    members JSONB DEFAULT '[]'::jsonb, -- Array of {user_id, role, primary_contact}

    -- Contact information
    primary_contact_phone VARCHAR(50),
    primary_contact_email VARCHAR(255),
    emergency_contacts JSONB DEFAULT '[]'::jsonb,

    -- Responsibilities
    roles_and_responsibilities TEXT,
    authority_level VARCHAR(50), -- strategic, tactical, operational
    decision_making_authority TEXT,

    -- Resources
    assembly_location VARCHAR(255),
    alternate_location VARCHAR(255),
    communication_channels JSONB DEFAULT '[]'::jsonb, -- Teams, Slack, radio frequencies, etc.

    required_resources JSONB DEFAULT '[]'::jsonb,
    available_resources JSONB DEFAULT '[]'::jsonb,

    -- Training and readiness
    training_requirements TEXT,
    last_training_date DATE,
    next_training_date DATE,
    last_exercise_date DATE,
    readiness_status VARCHAR(50), -- ready, training_required, not_ready

    -- Performance metrics
    activations_count INT DEFAULT 0,
    average_activation_time_minutes INT,
    incidents_handled JSONB DEFAULT '[]'::jsonb, -- UUIDs of incidents

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, team_code)
);

CREATE INDEX idx_response_teams_org ON response.response_teams(organization_id);
CREATE INDEX idx_response_teams_type ON response.response_teams(team_type);
CREATE INDEX idx_response_teams_active ON response.response_teams(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_response_teams_updated_at BEFORE UPDATE ON response.response_teams
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.response_teams ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Response teams visible to org members" ON response.response_teams FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Response teams manageable by org admins" ON response.response_teams FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.response_teams IS 'Response teams (IMT, CMT, BRT) per ISO 22301';

-- Add foreign key now that response_teams exists
ALTER TABLE response.incidents
    ADD CONSTRAINT fk_incidents_response_team
    FOREIGN KEY (response_team_id) REFERENCES response.response_teams(id);

-- Table: response.communication_templates
CREATE TABLE response.communication_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Template identity
    template_code VARCHAR(100) NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Classification
    template_type VARCHAR(100) NOT NULL, -- internal, external, customer, media, regulatory, supplier
    incident_types JSONB DEFAULT '[]'::jsonb, -- Which incident types this applies to
    severity_levels JSONB DEFAULT '[]'::jsonb, -- Which severity levels

    -- Content
    subject_template TEXT,
    body_template TEXT, -- Supports placeholders like {{incident_code}}, {{severity}}, etc.

    -- Delivery
    delivery_channels JSONB DEFAULT '[]'::jsonb, -- email, sms, push, phone, teams, slack, public_website
    default_recipients JSONB DEFAULT '[]'::jsonb, -- Roles or specific users

    requires_approval BOOLEAN DEFAULT FALSE,
    approver_role VARCHAR(100),

    -- Timing
    send_timing VARCHAR(50), -- immediate, scheduled, manual
    send_delay_minutes INT,

    -- Compliance
    regulatory_requirements TEXT,
    must_notify_within_hours INT, -- Legal requirement to notify within X hours

    -- Localization
    language VARCHAR(10) DEFAULT 'en',
    translations JSONB DEFAULT '{}'::jsonb, -- {lang_code: {subject, body}}

    -- Usage tracking
    usage_count INT DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Metadata
    tags JSONB DEFAULT '[]'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),

    UNIQUE(organization_id, template_code)
);

CREATE INDEX idx_comm_templates_org ON response.communication_templates(organization_id);
CREATE INDEX idx_comm_templates_type ON response.communication_templates(template_type);
CREATE INDEX idx_comm_templates_active ON response.communication_templates(is_active) WHERE is_active = TRUE;

CREATE TRIGGER update_comm_templates_updated_at BEFORE UPDATE ON response.communication_templates
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.communication_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Comm templates visible to org members" ON response.communication_templates FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Comm templates manageable by org admins" ON response.communication_templates FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.communication_templates IS 'Communication templates per ISO 22301:2019 Clause 8.4.3';

-- Table: response.communications
CREATE TABLE response.communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES response.incidents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Communication identity
    communication_code VARCHAR(100),

    -- Source
    template_id UUID REFERENCES response.communication_templates(id),
    communication_type VARCHAR(100) NOT NULL, -- internal, external, customer, media, regulatory, supplier

    -- Content
    subject VARCHAR(500),
    body TEXT NOT NULL,

    -- Delivery
    delivery_channel VARCHAR(50) NOT NULL, -- email, sms, push, phone, teams, slack, public_website
    recipients JSONB NOT NULL, -- Array of {type: "user"/"email"/"phone", value, name}
    recipients_count INT,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, pending_approval, approved, sent, delivered, failed

    scheduled_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES auth.users(id),
    sent_at TIMESTAMPTZ,

    -- Delivery tracking
    delivered_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    opened_count INT DEFAULT 0,
    clicked_count INT DEFAULT 0,

    delivery_status JSONB DEFAULT '{}'::jsonb, -- {recipient_id: {status, delivered_at, opened_at}}

    -- Errors
    error_message TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,

    -- Compliance
    is_regulatory_notification BOOLEAN DEFAULT FALSE,
    regulatory_deadline TIMESTAMPTZ,
    confirmation_required BOOLEAN DEFAULT FALSE,
    confirmations_received JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_communications_incident ON response.communications(incident_id);
CREATE INDEX idx_communications_org ON response.communications(organization_id);
CREATE INDEX idx_communications_status ON response.communications(status);
CREATE INDEX idx_communications_sent ON response.communications(sent_at DESC);
CREATE INDEX idx_communications_scheduled ON response.communications(scheduled_at) WHERE status = 'approved';

CREATE TRIGGER update_communications_updated_at BEFORE UPDATE ON response.communications
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.communications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Communications visible to org members" ON response.communications FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Communications manageable by org admins" ON response.communications FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.communications IS 'Communications sent during incidents per ISO 22301 Clause 8.4.3';

-- Table: response.notifications
CREATE TABLE response.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES response.incidents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Notification identity
    notification_type VARCHAR(100) NOT NULL, -- incident_alert, status_update, escalation, resolution, task_assignment

    -- Recipient
    user_id UUID REFERENCES auth.users(id),
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(50),
    recipient_name VARCHAR(255),

    -- Content
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(50) DEFAULT 'normal', -- urgent, high, normal, low

    -- Delivery
    delivery_channel VARCHAR(50) NOT NULL, -- email, sms, push, in_app, phone_call

    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, delivered, read, failed
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,

    -- Response tracking
    requires_acknowledgment BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ,
    acknowledgment_response TEXT,

    -- Retry logic
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    next_retry_at TIMESTAMPTZ,
    error_message TEXT,

    -- Action link
    action_url VARCHAR(500), -- Deep link to incident or task
    action_label VARCHAR(100),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_incident ON response.notifications(incident_id);
CREATE INDEX idx_notifications_user ON response.notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_status ON response.notifications(status);
CREATE INDEX idx_notifications_unread ON response.notifications(user_id, read_at) WHERE read_at IS NULL;
CREATE INDEX idx_notifications_pending_retry ON response.notifications(next_retry_at) WHERE status = 'failed' AND next_retry_at IS NOT NULL;

CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON response.notifications
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Notifications visible to org members" ON response.notifications FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Users see their own notifications" ON response.notifications FOR SELECT
    USING (user_id = auth.uid());

COMMENT ON TABLE response.notifications IS 'Individual stakeholder notifications during incidents';

-- Table: response.escalations
CREATE TABLE response.escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES response.incidents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Escalation details
    escalation_level INT NOT NULL, -- 1, 2, 3, etc.
    escalation_reason TEXT NOT NULL,

    previous_severity VARCHAR(50),
    new_severity VARCHAR(50) NOT NULL,

    previous_priority VARCHAR(50),
    new_priority VARCHAR(50),

    -- Escalation triggers
    triggered_by VARCHAR(100), -- manual, automatic, threshold_exceeded, sla_breach, impact_increase
    trigger_details JSONB,

    -- Who was escalated to
    escalated_to_user_id UUID REFERENCES auth.users(id),
    escalated_to_team_id UUID REFERENCES response.response_teams(id),
    escalated_to_role VARCHAR(100),

    -- Response
    status VARCHAR(50) DEFAULT 'pending', -- pending, acknowledged, accepted, rejected
    acknowledged_at TIMESTAMPTZ,
    response_received_at TIMESTAMPTZ,
    response_notes TEXT,

    -- SLA tracking
    escalation_sla_minutes INT,
    response_sla_minutes INT,
    sla_breached BOOLEAN DEFAULT FALSE,

    -- Actions taken
    actions_taken TEXT,
    additional_resources_allocated JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_escalations_incident ON response.escalations(incident_id, created_at DESC);
CREATE INDEX idx_escalations_org ON response.escalations(organization_id);
CREATE INDEX idx_escalations_level ON response.escalations(escalation_level);
CREATE INDEX idx_escalations_pending ON response.escalations(status) WHERE status = 'pending';

CREATE TRIGGER update_escalations_updated_at BEFORE UPDATE ON response.escalations
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE response.escalations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Escalations visible to org members" ON response.escalations FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Escalations manageable by org admins" ON response.escalations FOR ALL
    USING (public.is_org_admin(organization_id));

COMMENT ON TABLE response.escalations IS 'Incident escalation tracking';

-- Table: response.timeline_events
CREATE TABLE response.timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES response.incidents(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Event details
    event_type VARCHAR(100) NOT NULL, -- status_change, comment, action_taken, decision_made, resource_allocated, communication_sent, escalation, milestone_reached
    event_title VARCHAR(500) NOT NULL,
    event_description TEXT,

    occurred_at TIMESTAMPTZ DEFAULT NOW(),

    -- Context
    previous_status VARCHAR(50),
    new_status VARCHAR(50),

    -- Actor
    actor_id UUID REFERENCES auth.users(id),
    actor_name VARCHAR(255),
    actor_role VARCHAR(100),

    -- Related entities
    related_communication_id UUID REFERENCES response.communications(id),
    related_escalation_id UUID REFERENCES response.escalations(id),
    related_team_id UUID REFERENCES response.response_teams(id),

    -- Visibility
    is_public BOOLEAN DEFAULT FALSE, -- Public events shown in status pages
    is_milestone BOOLEAN DEFAULT FALSE, -- Key milestones highlighted in timeline

    -- Attachments and evidence
    attachments JSONB DEFAULT '[]'::jsonb, -- {filename, file_path, file_type, uploaded_by, uploaded_at}

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_timeline_incident ON response.timeline_events(incident_id, occurred_at DESC);
CREATE INDEX idx_timeline_org ON response.timeline_events(organization_id);
CREATE INDEX idx_timeline_type ON response.timeline_events(event_type);
CREATE INDEX idx_timeline_public ON response.timeline_events(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_timeline_milestones ON response.timeline_events(incident_id, is_milestone) WHERE is_milestone = TRUE;

ALTER TABLE response.timeline_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Timeline events visible to org members" ON response.timeline_events FOR SELECT
    USING (public.is_org_member(organization_id));

CREATE POLICY "Public timeline events visible to all" ON response.timeline_events FOR SELECT
    USING (is_public = TRUE);

COMMENT ON TABLE response.timeline_events IS 'Audit trail of incident events per ISO 22301';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 009 completed: Response schema created (7 tables)';
    RAISE NOTICE '   - incidents: Main incident tracking';
    RAISE NOTICE '   - response_teams: IMT, CMT, BRT teams';
    RAISE NOTICE '   - communication_templates: Pre-defined templates';
    RAISE NOTICE '   - communications: Communications sent';
    RAISE NOTICE '   - notifications: Individual notifications';
    RAISE NOTICE '   - escalations: Escalation tracking';
    RAISE NOTICE '   - timeline_events: Incident audit trail';
END
$$;
