-- SEH Phase 2: Grant Management System
-- Migration for comprehensive grant tracking and management
-- Version: 1.0.0
-- Date: 2025-08-16

-- Funding Programs table (grant opportunities)
CREATE TABLE IF NOT EXISTS funding_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    funder_name VARCHAR(255) NOT NULL,
    funder_type VARCHAR(50), -- foundation, government, corporate, individual
    focus_areas JSONB DEFAULT '[]', -- ["education", "health", "environment"]
    geographic_scope VARCHAR(100), -- local, regional, national, international
    total_budget DECIMAL(15,2) NOT NULL,
    available_budget DECIMAL(15,2) NOT NULL,
    min_grant_amount DECIMAL(15,2),
    max_grant_amount DECIMAL(15,2),
    application_open_date DATE NOT NULL,
    application_close_date DATE NOT NULL,
    decision_date DATE,
    funding_start_date DATE NOT NULL,
    funding_end_date DATE NOT NULL,
    eligibility_criteria JSONB DEFAULT '{}',
    required_documents JSONB DEFAULT '[]', -- ["501c3", "annual_report", "budget"]
    evaluation_criteria JSONB DEFAULT '{}', -- {"impact": 0.4, "capacity": 0.3, "sustainability": 0.3}
    reporting_frequency VARCHAR(50), -- monthly, quarterly, annually
    status VARCHAR(50) DEFAULT 'draft', -- draft, open, closed, awarded, completed
    guidelines_url TEXT,
    contact_email VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_budget CHECK (total_budget > 0 AND available_budget >= 0 AND available_budget <= total_budget),
    CONSTRAINT valid_grant_amounts CHECK (
        (min_grant_amount IS NULL OR min_grant_amount > 0) AND
        (max_grant_amount IS NULL OR max_grant_amount >= min_grant_amount)
    ),
    CONSTRAINT valid_application_dates CHECK (application_close_date >= application_open_date),
    CONSTRAINT valid_funding_dates CHECK (funding_end_date > funding_start_date)
);

-- Grant Applications table
CREATE TABLE IF NOT EXISTS grant_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funding_program_id UUID REFERENCES funding_programs(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organization_profiles(id) ON DELETE CASCADE,
    application_number VARCHAR(100) UNIQUE,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    requested_amount DECIMAL(15,2) NOT NULL,
    project_start_date DATE NOT NULL,
    project_end_date DATE NOT NULL,
    lead_contact_name VARCHAR(255),
    lead_contact_email VARCHAR(255),
    lead_contact_phone VARCHAR(50),
    target_beneficiaries INTEGER,
    target_geography VARCHAR(255),
    proposed_outcomes JSONB DEFAULT '[]',
    budget_breakdown JSONB DEFAULT '{}', -- {"personnel": 50000, "equipment": 10000, "overhead": 5000}
    partners JSONB DEFAULT '[]', -- [{"name": "Partner Org", "role": "Implementation"}]
    sustainability_plan TEXT,
    risk_assessment JSONB DEFAULT '[]',
    submitted_at TIMESTAMP WITH TIME ZONE,
    submission_method VARCHAR(50), -- online, email, mail
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, under_review, approved, rejected, withdrawn
    review_score DECIMAL(5,2), -- 0.00 to 100.00
    review_notes TEXT,
    reviewer_id UUID,
    review_date DATE,
    documents JSONB DEFAULT '[]', -- [{"type": "proposal", "url": "https://..."}]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_requested_amount CHECK (requested_amount > 0),
    CONSTRAINT valid_project_dates CHECK (project_end_date > project_start_date),
    CONSTRAINT valid_review_score CHECK (review_score IS NULL OR (review_score >= 0 AND review_score <= 100))
);

-- Grant Awards table (approved grants)
CREATE TABLE IF NOT EXISTS grant_awards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID REFERENCES grant_applications(id) ON DELETE CASCADE,
    award_number VARCHAR(100) UNIQUE,
    awarded_amount DECIMAL(15,2) NOT NULL,
    award_date DATE NOT NULL,
    agreement_signed_date DATE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    payment_schedule VARCHAR(50), -- upfront, monthly, quarterly, milestone-based
    total_disbursed DECIMAL(15,2) DEFAULT 0,
    conditions JSONB DEFAULT '[]', -- ["quarterly_reports", "site_visits", "audit"]
    deliverables JSONB DEFAULT '[]', -- [{"description": "Training completed", "due_date": "2025-06-01"}]
    performance_metrics JSONB DEFAULT '[]',
    modifications JSONB DEFAULT '[]', -- [{"date": "2025-03-01", "type": "budget_revision", "description": "..."}]
    status VARCHAR(50) DEFAULT 'active', -- pending_signature, active, on_hold, completed, terminated
    termination_reason TEXT,
    termination_date DATE,
    final_report_submitted BOOLEAN DEFAULT false,
    final_report_date DATE,
    impact_achieved JSONB DEFAULT '{}',
    lessons_learned TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_award_amount CHECK (awarded_amount > 0),
    CONSTRAINT valid_award_dates CHECK (end_date > start_date),
    CONSTRAINT valid_disbursed CHECK (total_disbursed >= 0 AND total_disbursed <= awarded_amount)
);

-- Disbursements table (actual payments)
CREATE TABLE IF NOT EXISTS disbursements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_award_id UUID REFERENCES grant_awards(id) ON DELETE CASCADE,
    tranche_number INTEGER NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    scheduled_date DATE NOT NULL,
    disbursement_date DATE,
    payment_method VARCHAR(50), -- wire, check, ach, crypto
    transaction_reference VARCHAR(255),
    conditions_met BOOLEAN DEFAULT false,
    conditions_verification JSONB DEFAULT '{}', -- {"report_submitted": true, "site_visit_completed": true}
    approval_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, processing, completed, cancelled
    approver_id UUID,
    approval_date TIMESTAMP WITH TIME ZONE,
    approval_notes TEXT,
    bank_account_details JSONB, -- encrypted/tokenized
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, pending, sent, received, failed
    failure_reason TEXT,
    receipt_confirmed BOOLEAN DEFAULT false,
    receipt_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_amount CHECK (amount > 0),
    CONSTRAINT valid_tranche CHECK (tranche_number > 0)
);

-- Reporting Requirements table
CREATE TABLE IF NOT EXISTS reporting_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_award_id UUID REFERENCES grant_awards(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL, -- progress, financial, impact, final
    frequency VARCHAR(50), -- monthly, quarterly, semi-annually, annually, one-time
    sequence_number INTEGER,
    due_date DATE NOT NULL,
    submission_date DATE,
    template_url TEXT,
    template_version VARCHAR(50),
    required_sections JSONB DEFAULT '[]', -- ["activities", "financials", "outcomes", "challenges"]
    required_attachments JSONB DEFAULT '[]', -- ["receipts", "photos", "beneficiary_list"]
    status VARCHAR(50) DEFAULT 'pending', -- pending, submitted, under_review, approved, rejected, overdue
    submitted_by UUID,
    review_status VARCHAR(50),
    reviewer_id UUID,
    review_date DATE,
    review_feedback TEXT,
    report_url TEXT,
    report_hash VARCHAR(255),
    compliance_score DECIMAL(5,2), -- 0.00 to 100.00
    follow_up_required BOOLEAN DEFAULT false,
    follow_up_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_compliance_score CHECK (compliance_score IS NULL OR (compliance_score >= 0 AND compliance_score <= 100))
);

-- Grant Budget Lines table (detailed budget tracking)
CREATE TABLE IF NOT EXISTS grant_budget_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_award_id UUID REFERENCES grant_awards(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL, -- personnel, equipment, travel, overhead, other
    subcategory VARCHAR(100),
    description TEXT,
    budgeted_amount DECIMAL(15,2) NOT NULL,
    spent_amount DECIMAL(15,2) DEFAULT 0,
    committed_amount DECIMAL(15,2) DEFAULT 0,
    variance_amount DECIMAL(15,2) GENERATED ALWAYS AS (budgeted_amount - spent_amount) STORED,
    variance_percentage DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN budgeted_amount = 0 THEN 0 
            ELSE ((budgeted_amount - spent_amount) / budgeted_amount * 100)
        END
    ) STORED,
    justification TEXT,
    restrictions TEXT,
    reallocation_allowed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_amounts CHECK (
        budgeted_amount >= 0 AND 
        spent_amount >= 0 AND 
        committed_amount >= 0
    )
);

-- Grant Expenses table (actual expenses)
CREATE TABLE IF NOT EXISTS grant_expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_award_id UUID REFERENCES grant_awards(id) ON DELETE CASCADE,
    budget_line_id UUID REFERENCES grant_budget_lines(id),
    expense_date DATE NOT NULL,
    vendor_name VARCHAR(255),
    description TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    payment_method VARCHAR(50),
    invoice_number VARCHAR(100),
    receipt_url TEXT,
    approved_by UUID,
    approval_date DATE,
    reimbursable BOOLEAN DEFAULT false,
    reimbursement_status VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_expense_amount CHECK (amount > 0)
);

-- Grant Outcomes Tracking table (link grants to outcomes)
CREATE TABLE IF NOT EXISTS grant_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_award_id UUID REFERENCES grant_awards(id) ON DELETE CASCADE,
    outcome_id UUID REFERENCES outcomes(id) ON DELETE CASCADE,
    target_value DECIMAL(15,4),
    achieved_value DECIMAL(15,4),
    achievement_date DATE,
    verification_method TEXT,
    evidence_urls JSONB DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(grant_award_id, outcome_id)
);

-- Create indexes for performance
CREATE INDEX idx_funding_programs_status ON funding_programs(status);
CREATE INDEX idx_funding_programs_dates ON funding_programs(application_open_date, application_close_date);
CREATE INDEX idx_grant_applications_funding ON grant_applications(funding_program_id);
CREATE INDEX idx_grant_applications_org ON grant_applications(organization_id);
CREATE INDEX idx_grant_applications_status ON grant_applications(status);
CREATE INDEX idx_grant_awards_application ON grant_awards(application_id);
CREATE INDEX idx_grant_awards_status ON grant_awards(status);
CREATE INDEX idx_grant_awards_dates ON grant_awards(start_date, end_date);
CREATE INDEX idx_disbursements_grant ON disbursements(grant_award_id);
CREATE INDEX idx_disbursements_status ON disbursements(status);
CREATE INDEX idx_disbursements_date ON disbursements(scheduled_date);
CREATE INDEX idx_reporting_requirements_grant ON reporting_requirements(grant_award_id);
CREATE INDEX idx_reporting_requirements_due ON reporting_requirements(due_date);
CREATE INDEX idx_reporting_requirements_status ON reporting_requirements(status);
CREATE INDEX idx_grant_budget_lines_award ON grant_budget_lines(grant_award_id);
CREATE INDEX idx_grant_expenses_award ON grant_expenses(grant_award_id);
CREATE INDEX idx_grant_expenses_date ON grant_expenses(expense_date);
CREATE INDEX idx_grant_outcomes_award ON grant_outcomes(grant_award_id);

-- Add RLS policies
ALTER TABLE funding_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE grant_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE grant_awards ENABLE ROW LEVEL SECURITY;
ALTER TABLE disbursements ENABLE ROW LEVEL SECURITY;
ALTER TABLE reporting_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE grant_budget_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE grant_expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE grant_outcomes ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies
CREATE POLICY "View funding programs" ON funding_programs
    FOR SELECT USING (status IN ('open', 'closed', 'awarded', 'completed') OR auth.uid() IS NOT NULL);

CREATE POLICY "Organizations manage their applications" ON grant_applications
    FOR ALL USING (
        organization_id IN (
            SELECT id FROM organization_profiles 
            WHERE pgpx_subject_id = auth.uid()
        )
    );

-- Add update triggers
CREATE TRIGGER update_funding_programs_updated_at BEFORE UPDATE ON funding_programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_grant_applications_updated_at BEFORE UPDATE ON grant_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_grant_awards_updated_at BEFORE UPDATE ON grant_awards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_disbursements_updated_at BEFORE UPDATE ON disbursements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reporting_requirements_updated_at BEFORE UPDATE ON reporting_requirements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_grant_budget_lines_updated_at BEFORE UPDATE ON grant_budget_lines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_grant_outcomes_updated_at BEFORE UPDATE ON grant_outcomes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE funding_programs IS 'SEH-compliant funding opportunities and grant programs';
COMMENT ON TABLE grant_applications IS 'Grant applications submitted by organizations';
COMMENT ON TABLE grant_awards IS 'Approved grants with terms and conditions';
COMMENT ON TABLE disbursements IS 'Scheduled and actual grant payments';
COMMENT ON TABLE reporting_requirements IS 'Grant reporting obligations and submissions';
COMMENT ON TABLE grant_budget_lines IS 'Detailed budget categories for grant tracking';
COMMENT ON TABLE grant_expenses IS 'Actual expenses charged against grants';
COMMENT ON TABLE grant_outcomes IS 'Link between grants and achieved outcomes';