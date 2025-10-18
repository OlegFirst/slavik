-- Saga Pattern Engine Database Schema
-- PostgreSQL schema for persistent saga state storage

-- Sagas table - stores main saga execution state
CREATE TABLE IF NOT EXISTS sagas (
    -- Primary identification
    saga_id VARCHAR(100) PRIMARY KEY,
    definition_name VARCHAR(200) NOT NULL,
    definition_version VARCHAR(50) NOT NULL,

    -- Execution status
    status VARCHAR(50) NOT NULL CHECK (
        status IN ('pending', 'executing', 'completed', 'failed', 'compensating', 'compensated', 'compensation_failed')
    ),

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Execution data
    execution_context JSONB DEFAULT '{}'::jsonb,
    result JSONB,
    error TEXT,

    -- Multi-tenancy and correlation
    tenant_id VARCHAR(100),
    correlation_id VARCHAR(100),
    parent_saga_id VARCHAR(100),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT fk_parent_saga FOREIGN KEY (parent_saga_id)
        REFERENCES sagas(saga_id) ON DELETE SET NULL
);

-- Saga steps table - stores individual step execution state
CREATE TABLE IF NOT EXISTS saga_steps (
    -- Primary identification
    step_id VARCHAR(100) NOT NULL,
    step_name VARCHAR(200) NOT NULL,
    saga_id VARCHAR(100) NOT NULL,

    -- Execution status
    status VARCHAR(50) NOT NULL CHECK (
        status IN ('pending', 'executing', 'completed', 'failed', 'compensating', 'compensated', 'compensation_failed')
    ),

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Retry tracking
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,

    -- Results
    result JSONB,
    error TEXT,
    error_details JSONB,

    -- Compensation tracking
    compensation_started_at TIMESTAMP,
    compensation_completed_at TIMESTAMP,
    compensation_result JSONB,
    compensation_error TEXT,

    -- Idempotency
    idempotency_key VARCHAR(200),

    -- Output context (flows to next steps)
    output_context JSONB DEFAULT '{}'::jsonb,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    PRIMARY KEY (saga_id, step_name),
    CONSTRAINT fk_saga FOREIGN KEY (saga_id)
        REFERENCES sagas(saga_id) ON DELETE CASCADE
);

-- Indices for performance

-- Sagas indices
CREATE INDEX IF NOT EXISTS idx_sagas_status ON sagas(status);
CREATE INDEX IF NOT EXISTS idx_sagas_tenant ON sagas(tenant_id);
CREATE INDEX IF NOT EXISTS idx_sagas_correlation ON sagas(correlation_id);
CREATE INDEX IF NOT EXISTS idx_sagas_started_at ON sagas(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sagas_definition ON sagas(definition_name, definition_version);
CREATE INDEX IF NOT EXISTS idx_sagas_completed_at ON sagas(completed_at);
CREATE INDEX IF NOT EXISTS idx_sagas_tenant_status ON sagas(tenant_id, status);

-- Saga steps indices
CREATE INDEX IF NOT EXISTS idx_saga_steps_status ON saga_steps(status);
CREATE INDEX IF NOT EXISTS idx_saga_steps_idempotency ON saga_steps(idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_saga_steps_saga_id ON saga_steps(saga_id);

-- Views for monitoring and reporting

-- Active sagas view
CREATE OR REPLACE VIEW active_sagas AS
SELECT
    s.saga_id,
    s.definition_name,
    s.definition_version,
    s.status,
    s.started_at,
    EXTRACT(EPOCH FROM (NOW() - s.started_at)) as duration_seconds,
    s.tenant_id,
    s.correlation_id,
    COUNT(ss.step_name) as total_steps,
    COUNT(CASE WHEN ss.status = 'completed' THEN 1 END) as completed_steps,
    COUNT(CASE WHEN ss.status = 'failed' THEN 1 END) as failed_steps,
    COUNT(CASE WHEN ss.status = 'executing' THEN 1 END) as executing_steps
FROM sagas s
LEFT JOIN saga_steps ss ON s.saga_id = ss.saga_id
WHERE s.status IN ('executing', 'compensating')
GROUP BY s.saga_id, s.definition_name, s.definition_version, s.status,
         s.started_at, s.tenant_id, s.correlation_id;

-- Failed sagas view
CREATE OR REPLACE VIEW failed_sagas AS
SELECT
    s.saga_id,
    s.definition_name,
    s.status,
    s.error,
    s.started_at,
    s.completed_at,
    EXTRACT(EPOCH FROM (s.completed_at - s.started_at)) as duration_seconds,
    s.tenant_id,
    s.correlation_id,
    (
        SELECT json_agg(json_build_object(
            'step_name', ss.step_name,
            'status', ss.status,
            'error', ss.error,
            'attempts', ss.attempts
        ))
        FROM saga_steps ss
        WHERE ss.saga_id = s.saga_id AND ss.status IN ('failed', 'compensation_failed')
    ) as failed_steps
FROM sagas s
WHERE s.status IN ('failed', 'compensation_failed')
ORDER BY s.completed_at DESC;

-- Saga execution metrics view
CREATE OR REPLACE VIEW saga_metrics AS
SELECT
    definition_name,
    definition_version,
    COUNT(*) as total_executions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    COUNT(CASE WHEN status = 'compensated' THEN 1 END) as compensated,
    COUNT(CASE WHEN status = 'compensation_failed' THEN 1 END) as compensation_failed,
    ROUND(
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::numeric /
        NULLIF(COUNT(*), 0) * 100,
        2
    ) as success_rate,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (completed_at - started_at)))::numeric,
        2
    ) as avg_duration_seconds,
    MAX(completed_at) as last_execution
FROM sagas
WHERE completed_at IS NOT NULL
GROUP BY definition_name, definition_version
ORDER BY total_executions DESC;

-- Step performance metrics view
CREATE OR REPLACE VIEW step_metrics AS
SELECT
    s.definition_name,
    ss.step_name,
    COUNT(*) as total_executions,
    COUNT(CASE WHEN ss.status = 'completed' THEN 1 END) as successful,
    COUNT(CASE WHEN ss.status = 'failed' THEN 1 END) as failed,
    ROUND(
        COUNT(CASE WHEN ss.status = 'completed' THEN 1 END)::numeric /
        NULLIF(COUNT(*), 0) * 100,
        2
    ) as success_rate,
    ROUND(AVG(ss.attempts)::numeric, 2) as avg_attempts,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (ss.completed_at - ss.started_at)))::numeric,
        2
    ) as avg_duration_seconds,
    MAX(ss.completed_at) as last_execution
FROM saga_steps ss
JOIN sagas s ON ss.saga_id = s.saga_id
WHERE ss.completed_at IS NOT NULL
GROUP BY s.definition_name, ss.step_name
ORDER BY s.definition_name, ss.step_name;

-- Functions for maintenance

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
DROP TRIGGER IF EXISTS update_sagas_updated_at ON sagas;
CREATE TRIGGER update_sagas_updated_at
    BEFORE UPDATE ON sagas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_saga_steps_updated_at ON saga_steps;
CREATE TRIGGER update_saga_steps_updated_at
    BEFORE UPDATE ON saga_steps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Cleanup function for old completed sagas
CREATE OR REPLACE FUNCTION cleanup_old_sagas(older_than_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH deleted AS (
        DELETE FROM sagas
        WHERE
            completed_at < NOW() - (older_than_days || ' days')::INTERVAL
            AND status IN ('completed', 'compensated')
        RETURNING saga_id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get saga with all steps
CREATE OR REPLACE FUNCTION get_saga_with_steps(p_saga_id VARCHAR)
RETURNS JSON AS $$
BEGIN
    RETURN (
        SELECT json_build_object(
            'saga', row_to_json(s),
            'steps', (
                SELECT json_agg(row_to_json(ss))
                FROM saga_steps ss
                WHERE ss.saga_id = s.saga_id
            )
        )
        FROM sagas s
        WHERE s.saga_id = p_saga_id
    );
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE sagas IS 'Main saga execution state storage';
COMMENT ON TABLE saga_steps IS 'Individual step execution state within sagas';
COMMENT ON VIEW active_sagas IS 'Currently executing or compensating sagas';
COMMENT ON VIEW failed_sagas IS 'Failed sagas with error details';
COMMENT ON VIEW saga_metrics IS 'Execution metrics per saga definition';
COMMENT ON VIEW step_metrics IS 'Performance metrics per step';
COMMENT ON FUNCTION cleanup_old_sagas IS 'Remove old completed sagas to save space';
COMMENT ON FUNCTION get_saga_with_steps IS 'Retrieve complete saga state including all steps';

-- Sample queries for monitoring

-- Query: Find stuck sagas (executing for more than 1 hour)
-- SELECT * FROM active_sagas WHERE duration_seconds > 3600;

-- Query: Get success rate by tenant
-- SELECT
--     tenant_id,
--     COUNT(*) as total,
--     ROUND(COUNT(CASE WHEN status = 'completed' THEN 1 END)::numeric / COUNT(*) * 100, 2) as success_rate
-- FROM sagas
-- WHERE completed_at IS NOT NULL
-- GROUP BY tenant_id;

-- Query: Find sagas that required compensation
-- SELECT * FROM sagas WHERE status IN ('compensated', 'compensation_failed') ORDER BY completed_at DESC;

-- Query: Get average execution time by hour of day
-- SELECT
--     EXTRACT(HOUR FROM started_at) as hour,
--     COUNT(*) as executions,
--     ROUND(AVG(EXTRACT(EPOCH FROM (completed_at - started_at)))::numeric, 2) as avg_duration
-- FROM sagas
-- WHERE completed_at IS NOT NULL
-- GROUP BY hour
-- ORDER BY hour;
