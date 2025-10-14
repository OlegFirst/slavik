-- KQM Database Schema
-- PostgreSQL schema for Knowledge Quality Manager
-- Created: 2025-10-11

-- =====================================================
-- SCENARIOS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS kqm_scenarios (
    -- Основные поля
    id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) NOT NULL, -- existing, generated, standard, community

    -- Классификация
    service VARCHAR(100),
    category VARCHAR(100),
    iso_clause VARCHAR(20),

    -- Метаданные
    source VARCHAR(255) NOT NULL,
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Дополнительные детали (JSON)
    inputs TEXT,
    outputs TEXT,
    events TEXT,
    components TEXT,

    -- Индексы
    CONSTRAINT valid_confidence CHECK (confidence BETWEEN 0 AND 1)
);

CREATE INDEX idx_scenarios_service ON kqm_scenarios(service);
CREATE INDEX idx_scenarios_type ON kqm_scenarios(type);
CREATE INDEX idx_scenarios_iso_clause ON kqm_scenarios(iso_clause);
CREATE INDEX idx_scenarios_created_at ON kqm_scenarios(created_at DESC);

-- =====================================================
-- KNOWLEDGE GAPS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS kqm_knowledge_gaps (
    -- Основные поля
    id VARCHAR(255) PRIMARY KEY,
    type VARCHAR(50) NOT NULL, -- standard_requirement, platform_capability, user_request, community_pattern
    description TEXT NOT NULL,
    priority INTEGER CHECK (priority >= 1 AND priority <= 10),

    -- Контекст
    standard VARCHAR(50),
    clause VARCHAR(20),
    service VARCHAR(100),
    capability VARCHAR(255),
    user_question TEXT,

    -- Метаданные
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'detected', -- detected, in_progress, resolved

    -- Индексы
    CONSTRAINT valid_priority CHECK (priority BETWEEN 1 AND 10)
);

CREATE INDEX idx_gaps_type ON kqm_knowledge_gaps(type);
CREATE INDEX idx_gaps_priority ON kqm_knowledge_gaps(priority DESC);
CREATE INDEX idx_gaps_status ON kqm_knowledge_gaps(status);
CREATE INDEX idx_gaps_detected_at ON kqm_knowledge_gaps(detected_at DESC);

-- =====================================================
-- SCENARIO VALIDATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS kqm_scenario_validations (
    -- Основные поля
    id SERIAL PRIMARY KEY,
    scenario_id VARCHAR(255) NOT NULL REFERENCES kqm_scenarios(id) ON DELETE CASCADE,

    -- Результаты валидации
    iso_compliant BOOLEAN NOT NULL,
    technically_valid BOOLEAN NOT NULL,
    expert_approved BOOLEAN NOT NULL,
    quality_score DECIMAL(3,2) CHECK (quality_score >= 0 AND quality_score <= 1),

    -- Статус
    status VARCHAR(50) NOT NULL, -- pending, in_review, approved, rejected, needs_revision
    validation_notes TEXT,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Expert info
    expert_id VARCHAR(100),
    expert_domain VARCHAR(100),

    CONSTRAINT valid_quality_score CHECK (quality_score BETWEEN 0 AND 1)
);

CREATE INDEX idx_validations_scenario ON kqm_scenario_validations(scenario_id);
CREATE INDEX idx_validations_status ON kqm_scenario_validations(status);
CREATE INDEX idx_validations_quality ON kqm_scenario_validations(quality_score DESC);

-- =====================================================
-- KNOWLEDGE METRICS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS kqm_knowledge_metrics (
    -- Основные поля
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Coverage metrics
    iso_coverage DECIMAL(3,2),
    platform_coverage DECIMAL(3,2),
    user_gaps INTEGER,
    total_scenarios INTEGER,
    iso_clauses_total INTEGER,
    iso_clauses_documented INTEGER,
    endpoints_total INTEGER,
    endpoints_documented INTEGER,

    -- Quality metrics
    validation_rate DECIMAL(3,2),
    expert_approval_rate DECIMAL(3,2),
    usage_rate DECIMAL(3,2),
    stale_count INTEGER,
    avg_confidence DECIMAL(3,2),

    -- Generation metrics
    scenarios_generated_today INTEGER,
    scenarios_generated_this_week INTEGER,
    scenarios_generated_this_month INTEGER,
    pending_validation INTEGER,
    approved_today INTEGER,

    -- Performance metrics
    search_latency_ms DECIMAL(10,2),
    generation_time_min DECIMAL(10,2),
    cache_hit_rate DECIMAL(3,2),
    avg_quality_score DECIMAL(3,2),

    -- Gaps by type (JSON)
    gaps_detected JSONB
);

CREATE INDEX idx_metrics_timestamp ON kqm_knowledge_metrics(timestamp DESC);

-- =====================================================
-- COMPLIANCE STATUS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS kqm_compliance_status (
    -- Основные поля
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- ISO 22301
    iso_22301_compliance JSONB, -- clause -> compliant

    -- NIST SP 800-34
    nist_sp_800_34_compliance JSONB,

    -- WHO Emergency
    who_emergency_compliance JSONB,

    -- Overall
    overall_compliance DECIMAL(3,2),
    critical_gaps TEXT[], -- Array of critical gap descriptions

    CONSTRAINT valid_overall_compliance CHECK (overall_compliance BETWEEN 0 AND 1)
);

CREATE INDEX idx_compliance_timestamp ON kqm_compliance_status(timestamp DESC);

-- =====================================================
-- SCENARIO USAGE TRACKING TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS kqm_scenario_usage (
    -- Основные поля
    id SERIAL PRIMARY KEY,
    scenario_id VARCHAR(255) NOT NULL REFERENCES kqm_scenarios(id) ON DELETE CASCADE,

    -- Usage info
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100),
    context VARCHAR(255),

    -- Feedback
    helpful BOOLEAN,
    feedback_text TEXT,

    -- Session
    session_id VARCHAR(100)
);

CREATE INDEX idx_usage_scenario ON kqm_scenario_usage(scenario_id);
CREATE INDEX idx_usage_used_at ON kqm_scenario_usage(used_at DESC);
CREATE INDEX idx_usage_helpful ON kqm_scenario_usage(helpful);

-- =====================================================
-- GENERATION QUEUE TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS kqm_generation_queue (
    -- Основные поля
    id SERIAL PRIMARY KEY,
    gap_id VARCHAR(255) NOT NULL REFERENCES kqm_knowledge_gaps(id) ON DELETE CASCADE,

    -- Queue info
    priority INTEGER,
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed

    -- Processing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,

    -- Result
    generated_scenario_id VARCHAR(255) REFERENCES kqm_scenarios(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_queue_status ON kqm_generation_queue(status);
CREATE INDEX idx_queue_priority ON kqm_generation_queue(priority DESC);

-- =====================================================
-- KNOWLEDGE VALUE TRACKING TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS kqm_knowledge_value (
    -- Основные поля
    id SERIAL PRIMARY KEY,
    scenario_id VARCHAR(255) NOT NULL REFERENCES kqm_scenarios(id) ON DELETE CASCADE,

    -- Value calculation
    confidence_score DECIMAL(3,2),
    relevance_score DECIMAL(3,2),
    reusability_score DECIMAL(3,2),
    compliance_score DECIMAL(3,2),

    -- Total value
    total_value DECIMAL(10,2),

    -- Timestamp
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_value_scenario ON kqm_knowledge_value(scenario_id);
CREATE INDEX idx_value_total ON kqm_knowledge_value(total_value DESC);

-- =====================================================
-- VIEWS
-- =====================================================

-- View: Recent approved scenarios
CREATE OR REPLACE VIEW kqm_recent_approved AS
SELECT
    s.*,
    v.quality_score,
    v.validated_at
FROM kqm_scenarios s
JOIN kqm_scenario_validations v ON s.id = v.scenario_id
WHERE v.status = 'approved'
ORDER BY v.validated_at DESC;

-- View: Gap analysis summary
CREATE OR REPLACE VIEW kqm_gap_summary AS
SELECT
    type,
    COUNT(*) as gap_count,
    AVG(priority) as avg_priority,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_count
FROM kqm_knowledge_gaps
GROUP BY type;

-- View: Latest metrics
CREATE OR REPLACE VIEW kqm_latest_metrics AS
SELECT *
FROM kqm_knowledge_metrics
ORDER BY timestamp DESC
LIMIT 1;

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function: Update scenario updated_at timestamp
CREATE OR REPLACE FUNCTION update_scenario_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_scenario_timestamp
BEFORE UPDATE ON kqm_scenarios
FOR EACH ROW
EXECUTE FUNCTION update_scenario_timestamp();

-- Function: Calculate knowledge value
CREATE OR REPLACE FUNCTION calculate_knowledge_value(
    p_scenario_id VARCHAR(255)
)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    v_confidence DECIMAL(3,2);
    v_relevance DECIMAL(3,2);
    v_reusability DECIMAL(3,2);
    v_compliance DECIMAL(3,2);
    v_value DECIMAL(10,2);
BEGIN
    -- Get scenario details
    SELECT
        confidence,
        CASE WHEN type = 'standard' THEN 0.9 ELSE 0.7 END,
        CASE WHEN type = 'standard' THEN 0.9 ELSE 0.7 END,
        CASE WHEN iso_clause IS NOT NULL THEN 1.0 ELSE 0.5 END
    INTO v_confidence, v_relevance, v_reusability, v_compliance
    FROM kqm_scenarios
    WHERE id = p_scenario_id;

    -- Calculate value
    v_value := v_confidence * v_relevance * v_reusability * v_compliance * 100;

    -- Store value
    INSERT INTO kqm_knowledge_value (
        scenario_id,
        confidence_score,
        relevance_score,
        reusability_score,
        compliance_score,
        total_value
    ) VALUES (
        p_scenario_id,
        v_confidence,
        v_relevance,
        v_reusability,
        v_compliance,
        v_value
    );

    RETURN v_value;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert initial compliance status
INSERT INTO kqm_compliance_status (
    iso_22301_compliance,
    nist_sp_800_34_compliance,
    who_emergency_compliance,
    overall_compliance,
    critical_gaps
) VALUES (
    '{}',
    '{}',
    '{}',
    0.0,
    ARRAY[]::TEXT[]
) ON CONFLICT DO NOTHING;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE kqm_scenarios IS 'Сценарии использования платформы';
COMMENT ON TABLE kqm_knowledge_gaps IS 'Обнаруженные пробелы в знаниях';
COMMENT ON TABLE kqm_scenario_validations IS 'Результаты валидации сценариев';
COMMENT ON TABLE kqm_knowledge_metrics IS 'Метрики системы знаний';
COMMENT ON TABLE kqm_compliance_status IS 'Статус соответствия стандартам';
COMMENT ON TABLE kqm_scenario_usage IS 'Отслеживание использования сценариев';
COMMENT ON TABLE kqm_generation_queue IS 'Очередь генерации сценариев';
COMMENT ON TABLE kqm_knowledge_value IS 'Экономическая ценность знаний';
