-- Digital BCM Organism Memory Tables for Supabase
-- Layer 3: Deep AI Memory and Wisdom Storage

-- 1. AI Organism Memory Table
CREATE TABLE ai_organism_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Memory Classification
    memory_type VARCHAR(100) NOT NULL,     -- 'governance_wisdom', 'incident_patterns', 'scenario_effectiveness'
    memory_category VARCHAR(100) NOT NULL, -- 'strategic_decision', 'emergency_response', 'creative_pattern'
    memory_title VARCHAR(255) NOT NULL,
    memory_summary TEXT,

    -- Memory Content
    memory_content JSONB NOT NULL,         -- Structured memory data
    memory_tags TEXT[],                    -- Array of tags for search
    source_data JSONB,                     -- Original source data

    -- Memory Quality Metrics
    wisdom_level FLOAT DEFAULT 0.1,       -- How wise/valuable (0-1)
    reliability_score FLOAT DEFAULT 0.5,  -- How reliable (0-1)
    applicability_score FLOAT DEFAULT 0.5, -- How broadly applicable (0-1)

    -- Usage Tracking
    access_count INTEGER DEFAULT 0,
    successful_applications INTEGER DEFAULT 0,
    failed_applications INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ,

    -- Source Tracking
    source_organ VARCHAR(100),             -- Which AI organ created this
    source_module VARCHAR(100),            -- Which BCM module
    source_company VARCHAR(255),           -- Organization context

    -- Evolution Tracking
    memory_version INTEGER DEFAULT 1,
    parent_memory_id UUID,
    evolution_reason TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL,

    -- Constraints
    CONSTRAINT unique_memory_per_tenant UNIQUE(memory_type, memory_category, memory_title, tenant_id),
    FOREIGN KEY (parent_memory_id) REFERENCES ai_organism_memory(id)
);

-- 2. AI Learning Sessions Table
CREATE TABLE ai_learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Session Identity
    session_name VARCHAR(255) NOT NULL,
    organ_type VARCHAR(100) NOT NULL,
    learning_type VARCHAR(100) NOT NULL,   -- 'pattern_recognition', 'effectiveness_analysis', 'wisdom_extraction'
    learning_trigger VARCHAR(255),         -- What triggered this learning

    -- Learning Data
    input_data JSONB NOT NULL,             -- Input data for learning
    learning_results JSONB,                -- Results of learning session
    patterns_discovered JSONB,             -- New patterns discovered
    wisdom_extracted TEXT,                 -- Wisdom extracted from session
    confidence_score FLOAT DEFAULT 0.5,    -- Learning confidence

    -- Performance Metrics
    processing_time_ms INTEGER,
    memory_usage_mb FLOAT,
    pattern_count INTEGER DEFAULT 0,
    wisdom_quality_score FLOAT DEFAULT 0.5,

    -- Context
    related_memory_ids UUID[],             -- Related memories
    learning_context JSONB,                -- Context during learning
    tenant_id VARCHAR(100) NOT NULL,

    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Learning Evolution
    parent_session_id UUID,                -- Previous learning session
    learning_generation INTEGER DEFAULT 1, -- Generation of learning
    improvement_delta FLOAT DEFAULT 0.0,   -- How much learning improved

    FOREIGN KEY (parent_session_id) REFERENCES ai_learning_sessions(id)
);

-- 3. AI Cross-Organization Intelligence Table
CREATE TABLE ai_cross_org_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Intelligence Classification
    intelligence_type VARCHAR(100) NOT NULL, -- 'scenario_effectiveness', 'incident_patterns', 'compliance_best_practices'
    industry_sector VARCHAR(100),            -- 'healthcare', 'financial', 'manufacturing'
    organization_size VARCHAR(50),           -- 'small', 'medium', 'large', 'enterprise'
    geographic_region VARCHAR(100),          -- 'north_america', 'europe', 'asia_pacific'

    -- Intelligence Data (ANONYMIZED)
    intelligence_summary TEXT NOT NULL,
    success_patterns JSONB,
    failure_patterns JSONB,
    best_practices JSONB,
    benchmarking_data JSONB,

    -- Statistical Metrics
    sample_size INTEGER,                     -- Number of organizations contributing
    confidence_level FLOAT,
    statistical_significance FLOAT,
    data_quality_score FLOAT,

    -- Performance Benchmarks
    performance_percentiles JSONB,          -- 25th, 50th, 75th, 90th percentiles
    industry_averages JSONB,
    best_in_class_metrics JSONB,

    -- Usage and Impact
    download_count INTEGER DEFAULT 0,
    implementation_success_rate FLOAT,
    business_impact_score FLOAT,

    -- Data Freshness
    data_collection_start TIMESTAMPTZ,
    data_collection_end TIMESTAMPTZ,
    data_freshness_days INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW(),

    -- Validation
    validation_status VARCHAR(50) DEFAULT 'pending',
    validated_by VARCHAR(255),
    validation_date TIMESTAMPTZ
);

-- 4. AI Conversation Context Table
CREATE TABLE ai_conversation_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Conversation Identity
    conversation_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    chat_platform VARCHAR(100),             -- 'claude_desktop', 'web_portal', 'mcp_chat'

    -- Context Data
    conversation_history JSONB,             -- Chat history
    platform_context JSONB,                -- Current platform state when chatting
    active_workflows JSONB,                 -- Active BCM workflows
    user_preferences JSONB,                 -- User preferences and patterns

    -- AI Organ Interactions
    consulted_organs TEXT[],                -- Which organs were consulted
    organ_responses JSONB,                  -- Responses from organs
    cross_organ_collaboration JSONB,        -- Multi-organ interactions
    successful_actions TEXT[],              -- Platform actions triggered successfully

    -- Conversation Quality
    user_satisfaction_score FLOAT,
    conversation_effectiveness FLOAT,
    platform_actions_triggered INTEGER DEFAULT 0,
    ai_helpfulness_score FLOAT,

    -- Learning Data
    conversation_patterns JSONB,           -- Patterns in user conversations
    context_evolution JSONB,               -- How context changed over time
    learning_extracted TEXT,               -- What AI learned from conversation

    -- Context Persistence
    context_ttl_hours INTEGER DEFAULT 24,  -- How long to keep context
    auto_cleanup BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_interaction TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '24 hours'),

    -- Multi-tenancy
    tenant_id VARCHAR(100) NOT NULL
);

-- 5. AI Organism Evolution Table
CREATE TABLE ai_organism_evolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Evolution Event
    evolution_type VARCHAR(100) NOT NULL,   -- 'organ_upgrade', 'capability_enhancement', 'wisdom_milestone'
    organ_affected VARCHAR(100),            -- Which organ evolved
    evolution_title VARCHAR(255) NOT NULL,
    evolution_description TEXT NOT NULL,

    -- Evolution Data
    before_state JSONB,                     -- State before evolution
    after_state JSONB,                      -- State after evolution
    evolution_metrics JSONB,               -- Quantified improvements
    evolution_trigger VARCHAR(255),         -- What triggered evolution

    -- Impact Assessment
    performance_improvement FLOAT,          -- Performance delta (-1 to 1)
    capability_enhancement JSONB,           -- New capabilities gained
    wisdom_advancement FLOAT,               -- Wisdom level increase
    reliability_change FLOAT,               -- Reliability delta

    -- Validation Data
    validation_tests JSONB,                 -- Tests performed to validate evolution
    success_metrics JSONB,                  -- Success measurements
    regression_checks JSONB,               -- Regression test results
    rollback_data JSONB,                   -- Data needed for rollback if needed

    -- Evolution Approval
    auto_evolution BOOLEAN DEFAULT FALSE,   -- Was this automatic evolution?
    human_approved BOOLEAN DEFAULT FALSE,   -- Human approval status
    approved_by VARCHAR(255),              -- Who approved the evolution

    -- Context
    tenant_id VARCHAR(100) NOT NULL,
    triggered_by_user VARCHAR(255),
    related_platform_events JSONB,
    business_justification TEXT,

    -- Timestamps
    evolution_started TIMESTAMPTZ DEFAULT NOW(),
    evolution_completed TIMESTAMPTZ,
    validation_completed TIMESTAMPTZ,
    approval_date TIMESTAMPTZ
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- ai_organism_memory indexes
CREATE INDEX idx_ai_organism_memory_type ON ai_organism_memory(memory_type, tenant_id);
CREATE INDEX idx_ai_organism_memory_wisdom ON ai_organism_memory(wisdom_level DESC);
CREATE INDEX idx_ai_organism_memory_recent ON ai_organism_memory(created_at DESC);
CREATE INDEX idx_ai_organism_memory_tags ON ai_organism_memory USING GIN(memory_tags);
CREATE INDEX idx_ai_organism_memory_source ON ai_organism_memory(source_organ, source_module);

-- ai_learning_sessions indexes
CREATE INDEX idx_learning_sessions_organ ON ai_learning_sessions(organ_type, tenant_id);
CREATE INDEX idx_learning_sessions_recent ON ai_learning_sessions(started_at DESC);
CREATE INDEX idx_learning_sessions_quality ON ai_learning_sessions(learning_confidence DESC);
CREATE INDEX idx_learning_sessions_type ON ai_learning_sessions(learning_type);

-- ai_cross_org_intelligence indexes
CREATE INDEX idx_cross_org_intelligence_type ON ai_cross_org_intelligence(intelligence_type, industry_sector);
CREATE INDEX idx_cross_org_intelligence_quality ON ai_cross_org_intelligence(confidence_level DESC);
CREATE INDEX idx_cross_org_intelligence_fresh ON ai_cross_org_intelligence(data_freshness_days ASC);

-- ai_conversation_context indexes
CREATE INDEX idx_conversation_context_user ON ai_conversation_context(user_id, tenant_id);
CREATE INDEX idx_conversation_context_recent ON ai_conversation_context(last_interaction DESC);
CREATE INDEX idx_conversation_context_active ON ai_conversation_context(expires_at) WHERE expires_at > NOW();

-- ai_organism_evolution indexes
CREATE INDEX idx_organism_evolution_organ ON ai_organism_evolution(organ_affected, tenant_id);
CREATE INDEX idx_organism_evolution_timeline ON ai_organism_evolution(evolution_started DESC);
CREATE INDEX idx_organism_evolution_type ON ai_organism_evolution(evolution_type);

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Enable RLS on all tables
ALTER TABLE ai_organism_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_learning_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_cross_org_intelligence ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversation_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_organism_evolution ENABLE ROW LEVEL SECURITY;

-- RLS Policies for tenant isolation
CREATE POLICY "ai_memory_tenant_isolation" ON ai_organism_memory
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY "learning_sessions_tenant_isolation" ON ai_learning_sessions
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY "conversation_context_tenant_isolation" ON ai_conversation_context
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY "organism_evolution_tenant_isolation" ON ai_organism_evolution
    FOR ALL USING (tenant_id = current_setting('app.current_tenant', true));

-- Cross-org intelligence is read-only for all tenants
CREATE POLICY "cross_org_intelligence_read_all" ON ai_cross_org_intelligence
    FOR SELECT USING (TRUE);

-- ========================================
-- FUNCTIONS FOR AI MEMORY OPERATIONS
-- ========================================

-- Function to store AI organ memory
CREATE OR REPLACE FUNCTION store_ai_memory(
    p_memory_type VARCHAR(100),
    p_memory_category VARCHAR(100),
    p_memory_title VARCHAR(255),
    p_memory_content JSONB,
    p_source_organ VARCHAR(100),
    p_tenant_id VARCHAR(100)
)
RETURNS UUID AS $$
DECLARE
    memory_id UUID;
BEGIN
    INSERT INTO ai_organism_memory (
        memory_type, memory_category, memory_title, memory_content,
        source_organ, tenant_id
    ) VALUES (
        p_memory_type, p_memory_category, p_memory_title, p_memory_content,
        p_source_organ, p_tenant_id
    )
    RETURNING id INTO memory_id;

    RETURN memory_id;
END;
$$ LANGUAGE plpgsql;

-- Function to retrieve relevant memories
CREATE OR REPLACE FUNCTION get_relevant_memories(
    p_context_type VARCHAR(100),
    p_tenant_id VARCHAR(100),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE(
    memory_id UUID,
    memory_title VARCHAR(255),
    memory_content JSONB,
    wisdom_level FLOAT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.memory_title,
        m.memory_content,
        m.wisdom_level,
        m.created_at
    FROM ai_organism_memory m
    WHERE
        m.memory_type = p_context_type
        AND m.tenant_id = p_tenant_id
        AND m.wisdom_level > 0.3
    ORDER BY m.wisdom_level DESC, m.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to update memory wisdom based on usage
CREATE OR REPLACE FUNCTION update_memory_wisdom(
    p_memory_id UUID,
    p_success BOOLEAN,
    p_application_context JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE ai_organism_memory
    SET
        access_count = access_count + 1,
        successful_applications = CASE WHEN p_success THEN successful_applications + 1 ELSE successful_applications END,
        failed_applications = CASE WHEN NOT p_success THEN failed_applications + 1 ELSE failed_applications END,
        last_accessed = NOW(),
        wisdom_level = LEAST(1.0, wisdom_level + CASE WHEN p_success THEN 0.1 ELSE -0.05 END),
        updated_at = NOW()
    WHERE id = p_memory_id;
END;
$$ LANGUAGE plpgsql;