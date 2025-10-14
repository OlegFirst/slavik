-- ACE Playbooks Storage Schema
-- For Agentic Context Engineering (ACE) framework
-- Stores evolving context playbooks for all intelligent-core modules

-- ============================================================================
-- ACE Playbooks Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS ace_playbooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Task identification
    task_type VARCHAR(255) NOT NULL,
    module_name VARCHAR(255),  -- e.g., "ai_orchestration", "scenario_intelligence"

    -- Playbook content
    playbook JSONB NOT NULL,

    -- Playbook structure:
    -- {
    --   "strategies": ["strategy1", "strategy2", ...],
    --   "patterns": [{"type": "...", "confidence": 0.9}, ...],
    --   "domain_knowledge": ["knowledge1", "knowledge2", ...],
    --   "successful_examples": [{"input": {...}, "output": {...}}, ...],
    --   "failed_examples": [{"input": {...}, "output": {...}, "reason": "..."}, ...]
    -- }

    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,

    -- Statistics
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    avg_effectiveness FLOAT DEFAULT 0.0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,

    -- Constraints
    UNIQUE(task_type, version)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Primary lookup by task type
CREATE INDEX IF NOT EXISTS idx_ace_playbooks_task
ON ace_playbooks(task_type);

-- Lookup by module
CREATE INDEX IF NOT EXISTS idx_ace_playbooks_module
ON ace_playbooks(module_name);

-- Get latest version
CREATE INDEX IF NOT EXISTS idx_ace_playbooks_task_version
ON ace_playbooks(task_type, version DESC);

-- Usage statistics
CREATE INDEX IF NOT EXISTS idx_ace_playbooks_usage
ON ace_playbooks(usage_count DESC);

-- GIN index for JSONB playbook queries
CREATE INDEX IF NOT EXISTS idx_ace_playbooks_playbook_gin
ON ace_playbooks USING GIN (playbook);

-- ============================================================================
-- ACE Trajectory Log (for analysis)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ace_trajectory_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Reference to playbook
    playbook_id UUID REFERENCES ace_playbooks(id) ON DELETE CASCADE,
    task_type VARCHAR(255) NOT NULL,

    -- Trajectory data
    input_context JSONB,
    output_result JSONB,
    trajectory JSONB,

    -- Analysis
    insights JSONB,
    effectiveness FLOAT,
    success BOOLEAN,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for ace_trajectory_log
CREATE INDEX IF NOT EXISTS idx_trajectory_playbook ON ace_trajectory_log(playbook_id);
CREATE INDEX IF NOT EXISTS idx_trajectory_task ON ace_trajectory_log(task_type);
CREATE INDEX IF NOT EXISTS idx_trajectory_success ON ace_trajectory_log(success);
CREATE INDEX IF NOT EXISTS idx_trajectory_created ON ace_trajectory_log(created_at DESC);

-- ============================================================================
-- Playbook Evolution History
-- ============================================================================

CREATE TABLE IF NOT EXISTS ace_playbook_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Reference
    playbook_id UUID REFERENCES ace_playbooks(id) ON DELETE CASCADE,
    task_type VARCHAR(255) NOT NULL,

    -- Change tracking
    version_from INTEGER,
    version_to INTEGER,
    changes JSONB,

    -- What triggered the update
    trigger_type VARCHAR(100),  -- e.g., "trajectory_analysis", "manual_update"
    trigger_data JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for ace_playbook_history
CREATE INDEX IF NOT EXISTS idx_history_playbook ON ace_playbook_history(playbook_id);
CREATE INDEX IF NOT EXISTS idx_history_task ON ace_playbook_history(task_type);
CREATE INDEX IF NOT EXISTS idx_history_created ON ace_playbook_history(created_at DESC);

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to get latest playbook for a task
CREATE OR REPLACE FUNCTION get_latest_ace_playbook(p_task_type VARCHAR)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT playbook INTO result
    FROM ace_playbooks
    WHERE task_type = p_task_type
    ORDER BY version DESC
    LIMIT 1;

    RETURN COALESCE(result, '{
        "strategies": [],
        "patterns": [],
        "domain_knowledge": [],
        "successful_examples": [],
        "failed_examples": []
    }'::JSONB);
END;
$$ LANGUAGE plpgsql;

-- Function to update playbook and increment version
CREATE OR REPLACE FUNCTION update_ace_playbook(
    p_task_type VARCHAR,
    p_module_name VARCHAR,
    p_playbook JSONB,
    p_insights JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    current_version INTEGER;
    new_version INTEGER;
    new_id UUID;
    old_playbook JSONB;
BEGIN
    -- Get current version
    SELECT COALESCE(MAX(version), 0), playbook
    INTO current_version, old_playbook
    FROM ace_playbooks
    WHERE task_type = p_task_type;

    new_version := current_version + 1;

    -- Insert new version
    INSERT INTO ace_playbooks (
        task_type,
        module_name,
        playbook,
        version,
        created_at,
        updated_at
    ) VALUES (
        p_task_type,
        p_module_name,
        p_playbook,
        new_version,
        NOW(),
        NOW()
    )
    RETURNING id INTO new_id;

    -- Log history
    IF old_playbook IS NOT NULL THEN
        INSERT INTO ace_playbook_history (
            playbook_id,
            task_type,
            version_from,
            version_to,
            changes,
            trigger_type,
            trigger_data,
            created_at
        ) VALUES (
            new_id,
            p_task_type,
            current_version,
            new_version,
            jsonb_build_object(
                'old_size', jsonb_array_length(old_playbook->'strategies'),
                'new_size', jsonb_array_length(p_playbook->'strategies')
            ),
            'trajectory_analysis',
            p_insights,
            NOW()
        );
    END IF;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- Function to log trajectory
CREATE OR REPLACE FUNCTION log_ace_trajectory(
    p_playbook_id UUID,
    p_task_type VARCHAR,
    p_input JSONB,
    p_output JSONB,
    p_trajectory JSONB,
    p_insights JSONB,
    p_effectiveness FLOAT,
    p_success BOOLEAN
)
RETURNS UUID AS $$
DECLARE
    new_id UUID;
BEGIN
    INSERT INTO ace_trajectory_log (
        playbook_id,
        task_type,
        input_context,
        output_result,
        trajectory,
        insights,
        effectiveness,
        success,
        created_at
    ) VALUES (
        p_playbook_id,
        p_task_type,
        p_input,
        p_output,
        p_trajectory,
        p_insights,
        p_effectiveness,
        p_success,
        NOW()
    )
    RETURNING id INTO new_id;

    -- Update playbook statistics
    UPDATE ace_playbooks
    SET
        usage_count = usage_count + 1,
        last_used_at = NOW(),
        success_rate = (
            SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
            FROM ace_trajectory_log
            WHERE playbook_id = p_playbook_id
        ),
        avg_effectiveness = (
            SELECT AVG(effectiveness)
            FROM ace_trajectory_log
            WHERE playbook_id = p_playbook_id
        )
    WHERE id = p_playbook_id;

    RETURN new_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Statistics Views
-- ============================================================================

CREATE OR REPLACE VIEW ace_playbook_stats AS
SELECT
    p.id,
    p.task_type,
    p.module_name,
    p.version,
    p.usage_count,
    p.success_rate,
    p.avg_effectiveness,
    jsonb_array_length(p.playbook->'strategies') as strategies_count,
    jsonb_array_length(p.playbook->'patterns') as patterns_count,
    jsonb_array_length(p.playbook->'domain_knowledge') as knowledge_count,
    jsonb_array_length(p.playbook->'successful_examples') as successful_examples_count,
    jsonb_array_length(p.playbook->'failed_examples') as failed_examples_count,
    p.created_at,
    p.updated_at,
    p.last_used_at
FROM ace_playbooks p;

-- View for playbook evolution over time
CREATE OR REPLACE VIEW ace_playbook_evolution AS
SELECT
    task_type,
    version,
    jsonb_array_length(playbook->'strategies') as strategies_count,
    usage_count,
    success_rate,
    avg_effectiveness,
    created_at
FROM ace_playbooks
ORDER BY task_type, version;

-- ============================================================================
-- Grants (adjust user as needed)
-- ============================================================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE ON ace_playbooks TO bcm_app_user;
-- GRANT SELECT, INSERT ON ace_trajectory_log TO bcm_app_user;
-- GRANT SELECT, INSERT ON ace_playbook_history TO bcm_app_user;
-- GRANT EXECUTE ON FUNCTION get_latest_ace_playbook TO bcm_app_user;
-- GRANT EXECUTE ON FUNCTION update_ace_playbook TO bcm_app_user;
-- GRANT EXECUTE ON FUNCTION log_ace_trajectory TO bcm_app_user;

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Example: Initial playbook for AI Orchestration
INSERT INTO ace_playbooks (
    task_type,
    module_name,
    playbook,
    version
) VALUES (
    'ai_task_delegation',
    'ai_orchestration',
    '{
        "strategies": ["Use DecisionCenter for complex tasks", "Apply SafetyMonitor checks"],
        "patterns": [],
        "domain_knowledge": ["AI agents work best with clear context", "Safety is priority #1"],
        "successful_examples": [],
        "failed_examples": []
    }'::JSONB,
    1
) ON CONFLICT (task_type, version) DO NOTHING;

-- Example: Initial playbook for Scenario Generation
INSERT INTO ace_playbooks (
    task_type,
    module_name,
    playbook,
    version
) VALUES (
    'scenario_generation_L1',
    'scenario_intelligence',
    '{
        "strategies": ["Use BCM framework context", "Validate with community"],
        "patterns": [],
        "domain_knowledge": ["ISO 22301 healthcare focus", "NIST guidelines important"],
        "successful_examples": [],
        "failed_examples": []
    }'::JSONB,
    1
) ON CONFLICT (task_type, version) DO NOTHING;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE ace_playbooks IS 'Stores evolving context playbooks for ACE framework';
COMMENT ON TABLE ace_trajectory_log IS 'Logs execution trajectories for analysis and learning';
COMMENT ON TABLE ace_playbook_history IS 'Tracks evolution of playbooks over time';
COMMENT ON FUNCTION get_latest_ace_playbook IS 'Returns the latest version of a playbook for a given task type';
COMMENT ON FUNCTION update_ace_playbook IS 'Creates new version of playbook and logs changes';
COMMENT ON FUNCTION log_ace_trajectory IS 'Logs trajectory execution and updates statistics';
