-- MVP Platform - Database Schema
-- Supabase PostgreSQL Schema
-- Version: 1.0
-- Date: 2025-10-09

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS TABLE (managed by Supabase Auth)
-- ============================================
-- Note: Supabase provides auth.users table
-- We extend it with our custom profile table

CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    role VARCHAR(50) DEFAULT 'specialist',
    phone TEXT,
    job_title TEXT,
    avatar_url TEXT,
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    custom_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read and update their own profile
CREATE POLICY "Users can view own profile"
    ON public.user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.user_profiles FOR UPDATE
    USING (auth.uid() = id);

-- ============================================
-- ORGANIZATIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    size INTEGER,
    country VARCHAR(100),
    description TEXT,
    logo_url TEXT,
    website TEXT,
    settings JSONB DEFAULT '{}'::jsonb,
    bcm_maturity_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT organizations_owner_unique UNIQUE (owner_id)
);

CREATE INDEX idx_organizations_owner ON public.organizations(owner_id);
CREATE INDEX idx_organizations_created ON public.organizations(created_at);

-- Enable RLS
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own organization
CREATE POLICY "Users can view own organization"
    ON public.organizations FOR SELECT
    USING (auth.uid() = owner_id);

CREATE POLICY "Users can create organization"
    ON public.organizations FOR INSERT
    WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Users can update own organization"
    ON public.organizations FOR UPDATE
    USING (auth.uid() = owner_id);

-- ============================================
-- ORGANIZATION STRUCTURE TABLES
-- ============================================

-- Departments
CREATE TABLE IF NOT EXISTS public.organization_departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    head_name VARCHAR(255),
    employee_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_departments_org ON public.organization_departments(organization_id);

ALTER TABLE public.organization_departments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own organization departments"
    ON public.organization_departments FOR ALL
    USING (organization_id IN (SELECT id FROM public.organizations WHERE owner_id = auth.uid()));

-- Processes
CREATE TABLE IF NOT EXISTS public.organization_processes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    department_id UUID REFERENCES public.organization_departments(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    criticality VARCHAR(50),
    owner_person VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_processes_org ON public.organization_processes(organization_id);
CREATE INDEX idx_processes_dept ON public.organization_processes(department_id);

ALTER TABLE public.organization_processes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own organization processes"
    ON public.organization_processes FOR ALL
    USING (organization_id IN (SELECT id FROM public.organizations WHERE owner_id = auth.uid()));

-- ============================================
-- BIA MODULE TABLES
-- ============================================

-- BIA Analyses
CREATE TABLE IF NOT EXISTS public.bia_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    collection_method VARCHAR(50),
    compliance_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_bia_org ON public.bia_analyses(organization_id);
CREATE INDEX idx_bia_status ON public.bia_analyses(status);

ALTER TABLE public.bia_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own organization BIAs"
    ON public.bia_analyses FOR ALL
    USING (organization_id IN (SELECT id FROM public.organizations WHERE owner_id = auth.uid()));

-- BIA Processes (enriched from organization_processes)
CREATE TABLE IF NOT EXISTS public.bia_processes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES public.bia_analyses(id) ON DELETE CASCADE,
    process_id UUID REFERENCES public.organization_processes(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    criticality VARCHAR(50) NOT NULL,
    rto_hours INTEGER,
    rpo_hours INTEGER,
    mtpd_hours INTEGER,
    financial_impact_per_hour DECIMAL(15, 2),
    category VARCHAR(100),
    owner_department VARCHAR(255),
    owner_person VARCHAR(255),
    dependencies JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_processes_analysis ON public.bia_processes(analysis_id);
CREATE INDEX idx_bia_processes_criticality ON public.bia_processes(criticality);

ALTER TABLE public.bia_processes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own BIA processes"
    ON public.bia_processes FOR ALL
    USING (analysis_id IN (
        SELECT id FROM public.bia_analyses WHERE organization_id IN (
            SELECT id FROM public.organizations WHERE owner_id = auth.uid()
        )
    ));

-- BIA Dependencies
CREATE TABLE IF NOT EXISTS public.bia_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES public.bia_analyses(id) ON DELETE CASCADE,
    source_process_id UUID NOT NULL REFERENCES public.bia_processes(id) ON DELETE CASCADE,
    target_process_id UUID NOT NULL REFERENCES public.bia_processes(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50) NOT NULL,
    dependency_strength INTEGER DEFAULT 5,
    ai_detected BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_deps_analysis ON public.bia_dependencies(analysis_id);
CREATE INDEX idx_bia_deps_source ON public.bia_dependencies(source_process_id);

ALTER TABLE public.bia_dependencies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own BIA dependencies"
    ON public.bia_dependencies FOR ALL
    USING (analysis_id IN (
        SELECT id FROM public.bia_analyses WHERE organization_id IN (
            SELECT id FROM public.organizations WHERE owner_id = auth.uid()
        )
    ));

-- BIA Questions (for questionnaire collection method)
CREATE TABLE IF NOT EXISTS public.bia_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES public.bia_analyses(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    options JSONB,
    sequence_number INTEGER NOT NULL,
    ai_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_questions_analysis ON public.bia_questions(analysis_id);

ALTER TABLE public.bia_questions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own BIA questions"
    ON public.bia_questions FOR ALL
    USING (analysis_id IN (
        SELECT id FROM public.bia_analyses WHERE organization_id IN (
            SELECT id FROM public.organizations WHERE owner_id = auth.uid()
        )
    ));

-- BIA Answers
CREATE TABLE IF NOT EXISTS public.bia_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_id UUID NOT NULL REFERENCES public.bia_questions(id) ON DELETE CASCADE,
    answer_text TEXT,
    answer_number DECIMAL(15, 2),
    answer_choice JSONB,
    answered_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_answers_question ON public.bia_answers(question_id);

ALTER TABLE public.bia_answers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own BIA answers"
    ON public.bia_answers FOR ALL
    USING (question_id IN (
        SELECT id FROM public.bia_questions WHERE analysis_id IN (
            SELECT id FROM public.bia_analyses WHERE organization_id IN (
                SELECT id FROM public.organizations WHERE owner_id = auth.uid()
            )
        )
    ));

-- BIA Findings & Recommendations
CREATE TABLE IF NOT EXISTS public.bia_findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES public.bia_analyses(id) ON DELETE CASCADE,
    finding_type VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    affected_processes JSONB DEFAULT '[]'::jsonb,
    iso_clause VARCHAR(50),
    recommended_action TEXT,
    status VARCHAR(50) DEFAULT 'new',
    user_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bia_findings_analysis ON public.bia_findings(analysis_id);
CREATE INDEX idx_bia_findings_severity ON public.bia_findings(severity);

ALTER TABLE public.bia_findings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access own BIA findings"
    ON public.bia_findings FOR ALL
    USING (analysis_id IN (
        SELECT id FROM public.bia_analyses WHERE organization_id IN (
            SELECT id FROM public.organizations WHERE owner_id = auth.uid()
        )
    ));

-- ============================================
-- AI PROMPTS & LOGS
-- ============================================

CREATE TABLE IF NOT EXISTS public.ai_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    template TEXT NOT NULL,
    variables JSONB,
    category VARCHAR(100),
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_prompts_name ON public.ai_prompts(name);
CREATE INDEX idx_ai_prompts_category ON public.ai_prompts(category);

-- AI Logs (for tracking usage)
CREATE TABLE IF NOT EXISTS public.ai_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    organization_id UUID REFERENCES public.organizations(id),
    prompt_name VARCHAR(255),
    model VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_logs_user ON public.ai_logs(user_id);
CREATE INDEX idx_ai_logs_org ON public.ai_logs(organization_id);
CREATE INDEX idx_ai_logs_created ON public.ai_logs(created_at);

-- ============================================
-- AUDIT LOG
-- ============================================

CREATE TABLE IF NOT EXISTS public.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    organization_id UUID REFERENCES public.organizations(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    ip_address VARCHAR(50),
    user_agent TEXT,
    changes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON public.audit_log(user_id);
CREATE INDEX idx_audit_org ON public.audit_log(organization_id);
CREATE INDEX idx_audit_action ON public.audit_log(action);
CREATE INDEX idx_audit_created ON public.audit_log(created_at);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON public.organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON public.organization_departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processes_updated_at BEFORE UPDATE ON public.organization_processes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bia_analyses_updated_at BEFORE UPDATE ON public.bia_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bia_processes_updated_at BEFORE UPDATE ON public.bia_processes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bia_findings_updated_at BEFORE UPDATE ON public.bia_findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_prompts_updated_at BEFORE UPDATE ON public.ai_prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SEED DATA - AI PROMPTS
-- ============================================

INSERT INTO public.ai_prompts (name, template, variables, category, version) VALUES
(
    'generate_processes_for_industry',
    'You are a BCM (Business Continuity Management) expert. Generate a list of critical business processes for a {industry} organization with {size} employees in {country}.

Return a JSON array of processes, each with:
- name: Process name
- description: Brief description
- category: Process category (Operations, IT, Finance, HR, etc.)
- criticality: critical, high, medium, or low

Return ONLY valid JSON, no additional text.',
    '{"industry": "string", "size": "integer", "country": "string"}',
    'processes',
    1
),
(
    'analyze_bia_questionnaire',
    'You are a BCM expert analyzing Business Impact Analysis questionnaire responses.

Questionnaire responses:
{responses}

Analyze the responses and provide:
1. Identified critical processes
2. Recommended RTO/RPO for each process
3. Dependencies between processes
4. Key findings and recommendations

Return a JSON object with these fields:
- processes: array of {name, criticality, rto_hours, rpo_hours}
- dependencies: array of {source, target, type}
- findings: array of {type, severity, title, description, recommendation}

Return ONLY valid JSON.',
    '{"responses": "object"}',
    'bia',
    1
),
(
    'calculate_process_rto',
    'You are a BCM expert. Calculate the recommended Recovery Time Objective (RTO) for this business process:

Process: {process_name}
Description: {process_description}
Industry: {industry}
Criticality: {criticality}

Consider:
- Industry standards
- Process criticality
- Typical downtime tolerance
- Regulatory requirements

Return a JSON object:
{
  "rto_hours": <number>,
  "rpo_hours": <number>,
  "mtpd_hours": <number>,
  "rationale": "<explanation>",
  "confidence": <0.0-1.0>
}',
    '{"process_name": "string", "process_description": "string", "industry": "string", "criticality": "string"}',
    'bia',
    1
);

-- ============================================
-- END OF SCHEMA
-- ============================================
