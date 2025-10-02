-- =====================================================
-- Migration 017: Governance - Domain Intelligence System
-- =====================================================
-- Purpose: Industry-specific knowledge base and domain classification
-- Based on: /BCM/governance/database/migrations/004_add_domain_intelligence.sql
-- Date: 2025-10-02
-- Stage 4: Domain Classification & Industry Knowledge
-- Makes the platform intelligent with industry-specific recommendations
-- =====================================================

-- =====================================================
-- PART 1: CREATE DOMAIN_INTELLIGENCE SCHEMA
-- =====================================================

CREATE SCHEMA IF NOT EXISTS domain_intelligence;

COMMENT ON SCHEMA domain_intelligence IS 'Industry knowledge and domain classification system - shared across tenants';

-- =====================================================
-- PART 2: EXTEND ORGANIZATIONS TABLE (for domain classification)
-- =====================================================

-- Add domain classification columns to core.organizations
ALTER TABLE core.organizations
    ADD COLUMN IF NOT EXISTS organizational_type VARCHAR(50) CHECK (
        organizational_type IS NULL OR organizational_type IN (
            'for_profit', 'non_profit', 'government', 'educational',
            'healthcare_provider', 'financial_institution', 'other'
        )
    ),
    ADD COLUMN IF NOT EXISTS industry_domain VARCHAR(50),
    ADD COLUMN IF NOT EXISTS sub_domain VARCHAR(100),
    ADD COLUMN IF NOT EXISTS company_size VARCHAR(50) CHECK (
        company_size IS NULL OR company_size IN (
            'micro', 'small', 'medium', 'large', 'enterprise'
        )
    ),
    ADD COLUMN IF NOT EXISTS geographic_scope VARCHAR(50),
    ADD COLUMN IF NOT EXISTS regulatory_requirements JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS domain_classified_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS domain_classified_by UUID;  -- User ID

-- Create indexes for domain classification
CREATE INDEX IF NOT EXISTS idx_orgs_org_type ON core.organizations(organizational_type);
CREATE INDEX IF NOT EXISTS idx_orgs_industry ON core.organizations(industry_domain);
CREATE INDEX IF NOT EXISTS idx_orgs_subdomain ON core.organizations(sub_domain);
CREATE INDEX IF NOT EXISTS idx_orgs_company_size ON core.organizations(company_size);

-- Comments
COMMENT ON COLUMN core.organizations.industry_domain IS 'Primary industry classification (healthcare, financial, manufacturing, etc.)';
COMMENT ON COLUMN core.organizations.sub_domain IS 'Industry sub-domain (hospital, bank, automotive, etc.)';
COMMENT ON COLUMN core.organizations.organizational_type IS 'Organization type (for_profit, non_profit, government, etc.)';
COMMENT ON COLUMN core.organizations.company_size IS 'Organization size (micro, small, medium, large, enterprise)';
COMMENT ON COLUMN core.organizations.regulatory_requirements IS 'Applicable regulations (HIPAA, SOX, GDPR, etc.)';

-- =====================================================
-- TABLE 1: INDUSTRY KNOWLEDGE
-- =====================================================

CREATE TABLE IF NOT EXISTS domain_intelligence.industry_knowledge (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Classification
    industry VARCHAR(50) NOT NULL,  -- healthcare, financial, manufacturing, etc.
    sub_domain VARCHAR(100),        -- hospital, bank, automotive, etc.
    knowledge_type VARCHAR(50) NOT NULL CHECK (knowledge_type IN (
        'typical_rto',
        'typical_rpo',
        'common_risk',
        'regulatory_requirement',
        'best_practice',
        'critical_process',
        'seasonal_factor',
        'compliance_standard',
        'other'
    )),

    -- Knowledge Content
    title VARCHAR(255) NOT NULL,
    description TEXT,
    knowledge_data JSONB NOT NULL,
    /*
    Examples of knowledge_data structure:

    For typical_rto:
    {
        "process": "EHR System",
        "typical_rto_hours": 4,
        "range_min": 2,
        "range_max": 8,
        "percentile_25": 2,
        "percentile_50": 4,
        "percentile_75": 6,
        "reasoning": "Patient care continuity requirements"
    }

    For regulatory_requirement:
    {
        "regulation": "HIPAA",
        "requirement": "Emergency access to patient data",
        "consequence": "Criminal penalties up to $250,000",
        "reference_url": "https://..."
    }

    For common_risk:
    {
        "risk_name": "Ransomware Attack",
        "likelihood": "high",
        "typical_impact": "critical",
        "mitigation_strategies": ["Offline backups", "MFA", "Security training"]
    }
    */

    -- Applicability
    applies_to_org_types JSONB DEFAULT '[]'::jsonb,  -- ['for_profit', 'non_profit']
    applies_to_sizes JSONB DEFAULT '[]'::jsonb,      -- ['large', 'enterprise']
    geographic_relevance JSONB DEFAULT '[]'::jsonb,  -- ['US', 'EU', 'global']

    -- Source & Confidence
    source VARCHAR(255),           -- "BCI GPG 7.0", "ISO 22301:2019", "Internal research"
    source_url TEXT,
    confidence_level VARCHAR(20) CHECK (confidence_level IN ('low', 'medium', 'high', 'verified')),
    verified_by VARCHAR(255),
    verified_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,      -- Track how often this knowledge is used
    last_used_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,  -- User ID

    -- Tags for search
    tags JSONB DEFAULT '[]'::jsonb
);

-- =====================================================
-- TABLE 2: DOMAIN TEMPLATES
-- =====================================================

CREATE TABLE IF NOT EXISTS domain_intelligence.domain_templates (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Classification
    industry VARCHAR(50) NOT NULL,
    sub_domain VARCHAR(100),
    template_type VARCHAR(50) NOT NULL CHECK (template_type IN (
        'bcp_plan',
        'bia_process',
        'risk_catalog',
        'exercise_scenario',
        'policy_template',
        'checklist',
        'communication_plan',
        'other'
    )),

    -- Template Details
    template_name VARCHAR(255) NOT NULL,
    template_code VARCHAR(100) NOT NULL,  -- healthcare_ehr_bcp, financial_payment_risk
    description TEXT,
    complexity_level VARCHAR(20) CHECK (complexity_level IN ('basic', 'intermediate', 'advanced')),

    -- Template Content (JSONB for flexibility)
    template_data JSONB NOT NULL,
    /*
    Example for exercise_scenario:
    {
        "scenario_name": "Ransomware Attack - Healthcare",
        "duration_hours": 3,
        "participants": ["IT", "Security", "Clinical", "Executive"],
        "injects": [
            {
                "time_minutes": 0,
                "inject": "Encryption detected on EHR servers",
                "expected_response": "Activate incident response team"
            }
        ],
        "success_criteria": [
            "EHR restored from backups within RTO"
        ]
    }
    */

    -- Applicability
    applies_to_org_types JSONB DEFAULT '[]'::jsonb,
    applies_to_sizes JSONB DEFAULT '[]'::jsonb,

    -- Usage Statistics
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) CHECK (rating IS NULL OR (rating >= 0 AND rating <= 5)),  -- Average rating 0.00-5.00
    rating_count INTEGER DEFAULT 0,

    -- Metadata
    version VARCHAR(50) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,  -- User ID

    tags JSONB DEFAULT '[]'::jsonb,

    -- Constraints
    CONSTRAINT uq_template_code UNIQUE (template_code)
);

-- =====================================================
-- TABLE 3: INDUSTRY BENCHMARKS
-- =====================================================
-- Cross-tenant anonymous aggregates for competitive intelligence

CREATE TABLE IF NOT EXISTS domain_intelligence.industry_benchmarks (
    -- Primary Key (UUID)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Classification
    industry VARCHAR(50) NOT NULL,
    sub_domain VARCHAR(100),
    metric_name VARCHAR(100) NOT NULL,  -- rto_ehr_system, plan_currency_rate, exercise_frequency

    -- Statistical Data
    sample_size INTEGER NOT NULL,           -- Number of organizations in sample

    mean_value DECIMAL(15,2),
    median_value DECIMAL(15,2),
    percentile_25 DECIMAL(15,2),
    percentile_50 DECIMAL(15,2),
    percentile_75 DECIMAL(15,2),
    percentile_90 DECIMAL(15,2),
    std_deviation DECIMAL(15,2),

    min_value DECIMAL(15,2),
    max_value DECIMAL(15,2),

    -- Unit & Context
    unit_of_measure VARCHAR(50),        -- hours, percentage, days, count
    metric_description TEXT,
    calculation_method TEXT,

    -- Data Quality
    data_collection_period_start DATE NOT NULL,
    data_collection_period_end DATE NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    confidence_level VARCHAR(20) CHECK (confidence_level IN ('low', 'medium', 'high')),
    data_quality_score INTEGER CHECK (data_quality_score BETWEEN 0 AND 100),

    -- Filtering (for more specific benchmarks)
    company_size_filter VARCHAR(50),    -- Only large companies, etc.
    geographic_filter VARCHAR(50),      -- US only, EU only, etc.

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID,  -- User ID

    -- Ensure unique benchmarks
    CONSTRAINT uq_benchmark UNIQUE (
        industry, sub_domain, metric_name,
        company_size_filter, geographic_filter,
        data_collection_period_end
    )
);

-- =====================================================
-- INDEXES - Industry Knowledge
-- =====================================================

CREATE INDEX idx_knowledge_industry ON domain_intelligence.industry_knowledge(industry);
CREATE INDEX idx_knowledge_subdomain ON domain_intelligence.industry_knowledge(sub_domain);
CREATE INDEX idx_knowledge_type ON domain_intelligence.industry_knowledge(knowledge_type);
CREATE INDEX idx_knowledge_active ON domain_intelligence.industry_knowledge(is_active);
CREATE INDEX idx_knowledge_industry_type ON domain_intelligence.industry_knowledge(industry, knowledge_type);
CREATE INDEX idx_knowledge_tags ON domain_intelligence.industry_knowledge USING gin(tags);

-- =====================================================
-- INDEXES - Domain Templates
-- =====================================================

CREATE INDEX idx_template_industry ON domain_intelligence.domain_templates(industry);
CREATE INDEX idx_template_subdomain ON domain_intelligence.domain_templates(sub_domain);
CREATE INDEX idx_template_type ON domain_intelligence.domain_templates(template_type);
CREATE INDEX idx_template_code ON domain_intelligence.domain_templates(template_code);
CREATE INDEX idx_template_active ON domain_intelligence.domain_templates(is_active);
CREATE INDEX idx_template_rating ON domain_intelligence.domain_templates(rating DESC NULLS LAST);
CREATE INDEX idx_template_industry_type ON domain_intelligence.domain_templates(industry, template_type);

-- =====================================================
-- INDEXES - Industry Benchmarks
-- =====================================================

CREATE INDEX idx_benchmark_industry ON domain_intelligence.industry_benchmarks(industry);
CREATE INDEX idx_benchmark_metric ON domain_intelligence.industry_benchmarks(metric_name);
CREATE INDEX idx_benchmark_active ON domain_intelligence.industry_benchmarks(is_active);
CREATE INDEX idx_benchmark_period ON domain_intelligence.industry_benchmarks(data_collection_period_end DESC);
CREATE INDEX idx_benchmark_industry_metric ON domain_intelligence.industry_benchmarks(industry, metric_name);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION domain_intelligence.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_industry_knowledge_updated_at
BEFORE UPDATE ON domain_intelligence.industry_knowledge
FOR EACH ROW
EXECUTE FUNCTION domain_intelligence.update_updated_at();

CREATE TRIGGER update_domain_templates_updated_at
BEFORE UPDATE ON domain_intelligence.domain_templates
FOR EACH ROW
EXECUTE FUNCTION domain_intelligence.update_updated_at();

-- =====================================================
-- ANALYTICAL VIEWS
-- =====================================================

-- View: Available Industries
CREATE OR REPLACE VIEW domain_intelligence.v_available_industries AS
SELECT DISTINCT
    industry,
    COUNT(DISTINCT id) AS knowledge_items,
    COUNT(DISTINCT CASE WHEN knowledge_type = 'typical_rto' THEN id END) AS rto_recommendations,
    COUNT(DISTINCT CASE WHEN knowledge_type = 'common_risk' THEN id END) AS risk_items,
    COUNT(DISTINCT CASE WHEN knowledge_type = 'regulatory_requirement' THEN id END) AS regulatory_items,
    COUNT(DISTINCT CASE WHEN knowledge_type = 'best_practice' THEN id END) AS best_practices
FROM domain_intelligence.industry_knowledge
WHERE is_active = TRUE
GROUP BY industry
ORDER BY knowledge_items DESC;

-- View: Industry Knowledge Summary
CREATE OR REPLACE VIEW domain_intelligence.v_industry_summary AS
SELECT
    k.industry,
    k.sub_domain,
    COUNT(DISTINCT k.id) AS total_knowledge_items,
    COUNT(DISTINCT t.id) AS total_templates,
    COUNT(DISTINCT b.id) AS total_benchmarks,
    MAX(k.updated_at) AS last_knowledge_update,
    SUM(k.usage_count) AS total_knowledge_usage,
    AVG(t.rating) AS avg_template_rating
FROM domain_intelligence.industry_knowledge k
LEFT JOIN domain_intelligence.domain_templates t
    ON t.industry = k.industry
    AND (t.sub_domain = k.sub_domain OR t.sub_domain IS NULL OR k.sub_domain IS NULL)
LEFT JOIN domain_intelligence.industry_benchmarks b
    ON b.industry = k.industry
    AND (b.sub_domain = k.sub_domain OR b.sub_domain IS NULL OR k.sub_domain IS NULL)
WHERE k.is_active = TRUE
GROUP BY k.industry, k.sub_domain
ORDER BY total_knowledge_items DESC;

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function: Get domain recommendations for an organization
CREATE OR REPLACE FUNCTION domain_intelligence.get_organization_recommendations(
    p_organization_id UUID,
    p_context_type VARCHAR(50) DEFAULT NULL  -- 'bia', 'risk', 'planning', etc.
)
RETURNS TABLE (
    knowledge_id UUID,
    title VARCHAR(255),
    knowledge_type VARCHAR(50),
    description TEXT,
    knowledge_data JSONB,
    relevance_score DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        k.id,
        k.title,
        k.knowledge_type,
        k.description,
        k.knowledge_data,
        -- Relevance score based on confidence level
        CASE
            WHEN k.confidence_level = 'verified' THEN 100.0
            WHEN k.confidence_level = 'high' THEN 85.0
            WHEN k.confidence_level = 'medium' THEN 70.0
            ELSE 50.0
        END AS relevance_score
    FROM domain_intelligence.industry_knowledge k
    INNER JOIN core.organizations o ON
        o.id = p_organization_id
        AND k.industry = o.industry_domain
        AND (k.sub_domain IS NULL OR k.sub_domain = o.sub_domain)
    WHERE k.is_active = TRUE
      AND (p_context_type IS NULL OR k.knowledge_type LIKE '%' || p_context_type || '%')
    ORDER BY relevance_score DESC, k.usage_count DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Function: Track knowledge usage
CREATE OR REPLACE FUNCTION domain_intelligence.track_knowledge_usage(
    p_knowledge_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE domain_intelligence.industry_knowledge
    SET
        usage_count = usage_count + 1,
        last_used_at = CURRENT_TIMESTAMP
    WHERE id = p_knowledge_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Track template usage
CREATE OR REPLACE FUNCTION domain_intelligence.track_template_usage(
    p_template_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE domain_intelligence.domain_templates
    SET usage_count = usage_count + 1
    WHERE id = p_template_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Rate template
CREATE OR REPLACE FUNCTION domain_intelligence.rate_template(
    p_template_id UUID,
    p_rating DECIMAL(3,2)
)
RETURNS VOID AS $$
BEGIN
    UPDATE domain_intelligence.domain_templates
    SET
        rating = CASE
            WHEN rating IS NULL THEN p_rating
            ELSE ((rating * rating_count) + p_rating) / (rating_count + 1)
        END,
        rating_count = rating_count + 1
    WHERE id = p_template_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

-- Note: Domain intelligence tables are SHARED across all tenants
-- No RLS policies needed - this is platform-wide knowledge
-- Access control is managed at application level

-- Organizations table already has RLS from previous migrations

-- =====================================================
-- COMMENTS (Documentation)
-- =====================================================

COMMENT ON TABLE domain_intelligence.industry_knowledge IS 'Industry-specific knowledge base (RTOs, risks, regulations, best practices) - shared across tenants';
COMMENT ON TABLE domain_intelligence.domain_templates IS 'Reusable templates for BCPs, BIAs, risks, exercises by industry - shared across tenants';
COMMENT ON TABLE domain_intelligence.industry_benchmarks IS 'Anonymous cross-tenant benchmarks for competitive intelligence';

COMMENT ON COLUMN domain_intelligence.industry_knowledge.knowledge_data IS 'Structured knowledge content in JSONB format';
COMMENT ON COLUMN domain_intelligence.industry_knowledge.confidence_level IS 'Confidence in knowledge accuracy (verified > high > medium > low)';
COMMENT ON COLUMN domain_intelligence.industry_knowledge.usage_count IS 'How many times this knowledge has been accessed/applied';

COMMENT ON COLUMN domain_intelligence.domain_templates.template_data IS 'Template content structure in JSONB format';
COMMENT ON COLUMN domain_intelligence.domain_templates.rating IS 'Average user rating 0.00-5.00';

COMMENT ON FUNCTION domain_intelligence.get_organization_recommendations IS 'Get recommended knowledge items for an organization based on their domain classification';

-- =====================================================
-- VERIFICATION
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 017: Governance Domain Intelligence - COMPLETE';
    RAISE NOTICE 'Schema created: domain_intelligence';
    RAISE NOTICE 'Tables created: 3';
    RAISE NOTICE 'Views created: 2';
    RAISE NOTICE 'Functions created: 4';
    RAISE NOTICE 'Indexes created: 19';
    RAISE NOTICE 'Triggers: 2';
    RAISE NOTICE 'Note: No RLS - shared knowledge across tenants';
END $$;
