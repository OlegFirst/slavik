-- =====================================================
-- Migration 015: Compliance - Improvement Initiatives
-- =====================================================
-- Purpose: Integrate Compliance Improvement Initiatives from Stage 2
-- Based on: /BCM/compliance/migrations/002_add_improvement_initiatives.sql
-- Date: 2025-10-02
-- ISO 22301:2019 Clause 10.2 (Continual Improvement)
-- =====================================================

-- =====================================================
-- TABLE: compliance.improvement_initiatives
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance.improvement_initiatives (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,

    -- Identification
    initiative_code VARCHAR(50) NOT NULL,  -- IMP-2024-001 (unique per organization)
    title VARCHAR(500) NOT NULL,

    -- Classification
    initiative_type VARCHAR(50) NOT NULL CHECK (initiative_type IN (
        'process_optimization',
        'technology_upgrade',
        'training',
        'documentation',
        'risk_mitigation',
        'compliance',
        'performance',
        'other'
    )),

    source VARCHAR(50) NOT NULL CHECK (source IN (
        'audit_finding',
        'management_review',
        'exercise_lesson',
        'incident_lesson',
        'risk_assessment',
        'stakeholder_feedback',
        'internal_suggestion',
        'regulatory_change'
    )),

    source_reference VARCHAR(255),  -- Reference to audit finding, exercise, etc.

    -- Description
    description TEXT NOT NULL,
    current_state TEXT,
    desired_state TEXT,
    gap_analysis TEXT,

    -- Benefits & ROI
    expected_benefits JSONB DEFAULT '[]'::jsonb,  -- [{benefit: "...", metric: "...", target: "..."}]
    cost_estimate DECIMAL(15,2),
    roi DECIMAL(10,2),  -- ROI percentage
    benefits_realized JSONB DEFAULT '[]'::jsonb,  -- [{benefit: "...", actual: "...", date: "..."}]
    actual_cost DECIMAL(15,2),

    -- Priority & Impact
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    impact_level VARCHAR(20) CHECK (impact_level IN ('low', 'medium', 'high')),
    urgency VARCHAR(20) CHECK (urgency IN ('low', 'medium', 'high')),

    -- Ownership & Accountability
    owner VARCHAR(255) NOT NULL,
    sponsor VARCHAR(255),
    assigned_team JSONB DEFAULT '[]'::jsonb,  -- [{"name": "...", "role": "..."}]

    -- Planning
    planned_start_date DATE,
    planned_end_date DATE,
    estimated_effort_hours INTEGER,

    -- Execution
    actual_start_date DATE,
    actual_end_date DATE,
    actual_effort_hours INTEGER,

    -- Status & Progress
    status VARCHAR(50) DEFAULT 'identified' CHECK (status IN (
        'identified',
        'approved',
        'planned',
        'in_progress',
        'on_hold',
        'completed',
        'verified',
        'closed',
        'cancelled'
    )),

    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    milestones JSONB DEFAULT '[]'::jsonb,  -- [{name: "...", date: "...", status: "..."}]

    -- Implementation Details
    implementation_plan TEXT,
    resources_required JSONB DEFAULT '{}'::jsonb,
    dependencies JSONB DEFAULT '[]'::jsonb,
    risks JSONB DEFAULT '[]'::jsonb,

    -- Verification & Effectiveness
    verification_method VARCHAR(255),
    verification_criteria TEXT,
    verification_date DATE,
    verified_by VARCHAR(255),
    verification_status VARCHAR(20) CHECK (verification_status IN ('pending', 'passed', 'failed', 'partial')),
    verification_notes TEXT,

    effectiveness_criteria TEXT,
    effectiveness_review_date DATE,
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    effectiveness_notes TEXT,

    -- Approval Workflow
    approval_status VARCHAR(20) DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    approved_by VARCHAR(255),
    approved_at TIMESTAMP WITH TIME ZONE,
    approval_notes TEXT,

    -- Change Management
    change_impact_assessment TEXT,
    communication_plan TEXT,
    training_required BOOLEAN DEFAULT false,
    training_completed BOOLEAN DEFAULT false,

    -- Integration with other modules (UUID arrays for relationships)
    related_risks UUID[],
    related_findings UUID[],
    related_incidents UUID[],
    related_exercises UUID[],

    -- Document Management
    attachments JSONB DEFAULT '[]'::jsonb,
    related_documents JSONB DEFAULT '[]'::jsonb,

    -- Audit Trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,  -- User ID
    updated_by UUID,  -- User ID

    -- Additional Notes
    notes TEXT,
    lessons_learned TEXT,
    closure_notes TEXT,

    -- Constraints
    CONSTRAINT uq_improvement_code_per_org UNIQUE (organization_id, initiative_code)
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Primary lookups
CREATE INDEX idx_improvements_tenant ON compliance.improvement_initiatives(tenant_id);
CREATE INDEX idx_improvements_organization ON compliance.improvement_initiatives(organization_id);
CREATE INDEX idx_improvements_code ON compliance.improvement_initiatives(initiative_code);

-- Filtering & search
CREATE INDEX idx_improvements_type ON compliance.improvement_initiatives(initiative_type);
CREATE INDEX idx_improvements_source ON compliance.improvement_initiatives(source);
CREATE INDEX idx_improvements_status ON compliance.improvement_initiatives(status);
CREATE INDEX idx_improvements_priority ON compliance.improvement_initiatives(priority);
CREATE INDEX idx_improvements_owner ON compliance.improvement_initiatives(owner);

-- Date-based queries
CREATE INDEX idx_improvements_planned_end ON compliance.improvement_initiatives(planned_end_date);
CREATE INDEX idx_improvements_created ON compliance.improvement_initiatives(created_at);

-- Verification & effectiveness
CREATE INDEX idx_improvements_verification ON compliance.improvement_initiatives(verification_status);
CREATE INDEX idx_improvements_effectiveness ON compliance.improvement_initiatives(effectiveness_rating);

-- Composite indexes for common queries
CREATE INDEX idx_improvements_tenant_status ON compliance.improvement_initiatives(tenant_id, status);
CREATE INDEX idx_improvements_tenant_priority ON compliance.improvement_initiatives(tenant_id, priority);
CREATE INDEX idx_improvements_org_status ON compliance.improvement_initiatives(organization_id, status);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

ALTER TABLE compliance.improvement_initiatives ENABLE ROW LEVEL SECURITY;

-- Policy: Tenant isolation
CREATE POLICY improvement_initiatives_tenant_isolation
ON compliance.improvement_initiatives
USING (
    tenant_id = current_setting('app.current_tenant_id', true)::text
);

-- Policy: Organization-level access
CREATE POLICY improvement_initiatives_org_access
ON compliance.improvement_initiatives
USING (
    organization_id IN (
        SELECT id FROM public.organizations
        WHERE tenant_id = current_setting('app.current_tenant_id', true)::text
    )
);

-- Policy: Platform admin full access
CREATE POLICY improvement_initiatives_platform_admin
ON compliance.improvement_initiatives
USING (
    current_setting('app.is_platform_admin', true)::boolean = true
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Auto-update updated_at timestamp
CREATE TRIGGER update_improvements_updated_at
BEFORE UPDATE ON compliance.improvement_initiatives
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger: Auto-generate initiative_code if not provided
CREATE OR REPLACE FUNCTION compliance.generate_improvement_code()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
    new_code VARCHAR(50);
    current_year INTEGER;
BEGIN
    IF NEW.initiative_code IS NULL OR NEW.initiative_code = '' THEN
        current_year := EXTRACT(YEAR FROM CURRENT_DATE);

        -- Get next sequential number for this organization and year
        SELECT COALESCE(
            MAX(
                CAST(
                    SPLIT_PART(initiative_code, '-', 3) AS INTEGER
                )
            ), 0
        ) + 1
        INTO next_num
        FROM compliance.improvement_initiatives
        WHERE organization_id = NEW.organization_id
          AND initiative_code LIKE 'IMP-' || current_year || '-%';

        -- Generate code: IMP-2024-001
        new_code := 'IMP-' || current_year || '-' || LPAD(next_num::TEXT, 3, '0');
        NEW.initiative_code := new_code;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_improvement_code_trigger
BEFORE INSERT ON compliance.improvement_initiatives
FOR EACH ROW
EXECUTE FUNCTION compliance.generate_improvement_code();

-- =====================================================
-- ANALYTICAL VIEWS
-- =====================================================

-- View: Active improvement initiatives summary
CREATE OR REPLACE VIEW compliance.v_active_improvements AS
SELECT
    i.id,
    i.organization_id,
    i.tenant_id,
    i.initiative_code,
    i.title,
    i.initiative_type,
    i.source,
    i.status,
    i.priority,
    i.progress_percentage,
    i.owner,
    i.planned_start_date,
    i.planned_end_date,
    i.actual_start_date,
    i.actual_end_date,

    -- Calculated fields
    CASE
        WHEN i.actual_end_date IS NOT NULL THEN
            i.actual_end_date - i.actual_start_date
        WHEN i.actual_start_date IS NOT NULL THEN
            CURRENT_DATE - i.actual_start_date
        ELSE NULL
    END AS days_in_progress,

    CASE
        WHEN i.planned_end_date < CURRENT_DATE AND i.status NOT IN ('completed', 'verified', 'closed', 'cancelled')
        THEN true
        ELSE false
    END AS is_overdue,

    i.verification_status,
    i.effectiveness_rating,
    i.created_at
FROM compliance.improvement_initiatives i
WHERE i.status NOT IN ('cancelled', 'closed');

-- View: Improvement initiatives by source
CREATE OR REPLACE VIEW compliance.v_improvements_by_source AS
SELECT
    organization_id,
    tenant_id,
    source,
    COUNT(*) AS total_initiatives,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_count,
    COUNT(*) FILTER (WHERE status IN ('in_progress', 'planned')) AS active_count,
    COUNT(*) FILTER (WHERE verification_status = 'passed') AS verified_count,
    AVG(effectiveness_rating) AS avg_effectiveness,
    SUM(cost_estimate) AS total_estimated_cost,
    SUM(actual_cost) AS total_actual_cost
FROM compliance.improvement_initiatives
GROUP BY organization_id, tenant_id, source
ORDER BY total_initiatives DESC;

-- View: Improvement initiatives requiring attention
CREATE OR REPLACE VIEW compliance.v_improvements_requiring_attention AS
SELECT
    i.id,
    i.organization_id,
    i.tenant_id,
    i.initiative_code,
    i.title,
    i.priority,
    i.status,
    i.progress_percentage,
    i.planned_end_date,
    i.owner,

    -- Attention reasons
    CASE
        WHEN i.planned_end_date < CURRENT_DATE AND i.status NOT IN ('completed', 'verified', 'closed', 'cancelled')
        THEN 'Overdue'
        WHEN i.verification_status = 'failed'
        THEN 'Verification failed'
        WHEN i.status = 'on_hold' AND (CURRENT_DATE - i.updated_at::date) > 30
        THEN 'On hold for 30+ days'
        WHEN i.priority = 'critical' AND i.status = 'identified'
        THEN 'Critical priority not started'
        WHEN i.effectiveness_rating < 3 AND i.status = 'verified'
        THEN 'Low effectiveness rating'
        ELSE 'Other'
    END AS attention_reason
FROM compliance.improvement_initiatives i
WHERE
    (i.planned_end_date < CURRENT_DATE AND i.status NOT IN ('completed', 'verified', 'closed', 'cancelled'))
    OR i.verification_status = 'failed'
    OR (i.status = 'on_hold' AND (CURRENT_DATE - i.updated_at::date) > 30)
    OR (i.priority = 'critical' AND i.status = 'identified')
    OR (i.effectiveness_rating < 3 AND i.status = 'verified');

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE compliance.improvement_initiatives IS 'ISO 22301 Clause 10.2 - Continual improvement initiatives tracking';
COMMENT ON COLUMN compliance.improvement_initiatives.initiative_code IS 'Unique code per organization (IMP-2024-001)';
COMMENT ON COLUMN compliance.improvement_initiatives.source IS 'Origin of improvement initiative (audit, review, incident, etc.)';
COMMENT ON COLUMN compliance.improvement_initiatives.verification_status IS 'Verification outcome after implementation';
COMMENT ON COLUMN compliance.improvement_initiatives.effectiveness_rating IS 'Rating 1-5 of actual effectiveness after implementation';
COMMENT ON COLUMN compliance.improvement_initiatives.roi IS 'Return on Investment percentage';

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 015: Compliance Improvement Initiatives - COMPLETE';
    RAISE NOTICE 'Tables created: 1';
    RAISE NOTICE 'Views created: 3';
    RAISE NOTICE 'Indexes created: 15';
    RAISE NOTICE 'RLS policies: 3';
    RAISE NOTICE 'Triggers: 2';
END $$;
