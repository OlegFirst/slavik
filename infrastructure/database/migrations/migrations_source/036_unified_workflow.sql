-- =====================================================
-- Migration: 036 - Unified Workflow Engine
-- Description: BPMN processes, instances, tasks tables
-- Date: 2025-10-05
-- Purpose: Support visual BPMN modeling + AI integration
-- =====================================================

-- Create workflow schema if not exists
CREATE SCHEMA IF NOT EXISTS workflow;

-- =====================================================
-- BPMN PROCESSES (Definitions)
-- =====================================================

CREATE TABLE IF NOT EXISTS workflow.bpmn_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    module TEXT,  -- bia, risk, compliance, etc

    name TEXT NOT NULL,
    description TEXT,
    bpmn_xml TEXT NOT NULL,  -- BPMN 2.0 XML content

    version TEXT DEFAULT '1.0',
    is_active BOOLEAN DEFAULT true,

    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bpmn_processes_tenant
    ON workflow.bpmn_processes(tenant_id);

CREATE INDEX idx_bpmn_processes_module
    ON workflow.bpmn_processes(tenant_id, module);

CREATE INDEX idx_bpmn_processes_active
    ON workflow.bpmn_processes(tenant_id, is_active)
    WHERE is_active = true;

-- Comments
COMMENT ON TABLE workflow.bpmn_processes IS
    'BPMN process definitions - stores BPMN 2.0 XML templates';
COMMENT ON COLUMN workflow.bpmn_processes.bpmn_xml IS
    'BPMN 2.0 XML content for visual modeling';
COMMENT ON COLUMN workflow.bpmn_processes.module IS
    'BCM module: bia, risk, compliance, planning, response, etc';

-- =====================================================
-- BPMN INSTANCES (Running Processes)
-- =====================================================

CREATE TABLE IF NOT EXISTS workflow.bpmn_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID NOT NULL REFERENCES workflow.bpmn_processes(id),
    tenant_id TEXT NOT NULL,

    status TEXT DEFAULT 'ACTIVE' NOT NULL,
    -- ACTIVE, COMPLETED, SUSPENDED, TERMINATED

    variables JSONB DEFAULT '{}'::jsonb,  -- Process variables
    current_activities TEXT[] DEFAULT '{}',  -- Currently active activity IDs

    -- Link to Workflow Intelligence (for AI integration)
    workflow_intelligence_context JSONB,  -- Cached context from WorkflowEngine

    started_by TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_instance_status CHECK (
        status IN ('ACTIVE', 'COMPLETED', 'SUSPENDED', 'TERMINATED')
    )
);

-- Indexes
CREATE INDEX idx_bpmn_instances_tenant
    ON workflow.bpmn_instances(tenant_id);

CREATE INDEX idx_bpmn_instances_process
    ON workflow.bpmn_instances(process_id);

CREATE INDEX idx_bpmn_instances_status
    ON workflow.bpmn_instances(tenant_id, status);

CREATE INDEX idx_bpmn_instances_active
    ON workflow.bpmn_instances(tenant_id, started_at DESC)
    WHERE status = 'ACTIVE';

-- GIN index for JSONB variables (for querying)
CREATE INDEX idx_bpmn_instances_variables
    ON workflow.bpmn_instances USING gin(variables);

-- Comments
COMMENT ON TABLE workflow.bpmn_instances IS
    'Running BPMN process instances with current state';
COMMENT ON COLUMN workflow.bpmn_instances.variables IS
    'Process variables that flow through workflow steps';
COMMENT ON COLUMN workflow.bpmn_instances.current_activities IS
    'Array of currently active BPMN activity IDs';
COMMENT ON COLUMN workflow.bpmn_instances.workflow_intelligence_context IS
    'Cached context from Workflow Intelligence for AI integration';

-- =====================================================
-- BPMN TASKS
-- =====================================================

CREATE TABLE IF NOT EXISTS workflow.bpmn_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID NOT NULL
        REFERENCES workflow.bpmn_instances(id) ON DELETE CASCADE,

    activity_id TEXT NOT NULL,  -- BPMN activity ID from XML
    name TEXT NOT NULL,
    task_type TEXT DEFAULT 'USER_TASK',
    -- USER_TASK, SERVICE_TASK, SCRIPT_TASK, etc

    assignee TEXT,  -- User assigned to this task
    status TEXT DEFAULT 'ACTIVE' NOT NULL,
    -- ACTIVE, COMPLETED, CANCELLED

    variables JSONB DEFAULT '{}'::jsonb,  -- Task-specific variables

    -- AI Enhancements
    ai_recommendations JSONB,  -- AI recommendations for this task
    ai_predicted_duration_hours FLOAT,  -- AI prediction of duration

    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_task_status CHECK (
        status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')
    ),
    CONSTRAINT valid_task_type CHECK (
        task_type IN (
            'USER_TASK', 'SERVICE_TASK', 'SCRIPT_TASK',
            'SEND_TASK', 'RECEIVE_TASK', 'MANUAL_TASK',
            'BUSINESS_RULE_TASK'
        )
    )
);

-- Indexes
CREATE INDEX idx_bpmn_tasks_instance
    ON workflow.bpmn_tasks(instance_id);

CREATE INDEX idx_bpmn_tasks_assignee
    ON workflow.bpmn_tasks(assignee, status)
    WHERE status = 'ACTIVE';

CREATE INDEX idx_bpmn_tasks_status
    ON workflow.bpmn_tasks(status);

CREATE INDEX idx_bpmn_tasks_activity
    ON workflow.bpmn_tasks(instance_id, activity_id);

-- GIN index for AI recommendations
CREATE INDEX idx_bpmn_tasks_ai_recommendations
    ON workflow.bpmn_tasks USING gin(ai_recommendations);

-- Comments
COMMENT ON TABLE workflow.bpmn_tasks IS
    'BPMN tasks (userTask, serviceTask, etc) with AI enhancements';
COMMENT ON COLUMN workflow.bpmn_tasks.activity_id IS
    'BPMN activity ID from process XML definition';
COMMENT ON COLUMN workflow.bpmn_tasks.assignee IS
    'User or service assigned to complete this task';
COMMENT ON COLUMN workflow.bpmn_tasks.ai_recommendations IS
    'AI-generated recommendations for completing this task';
COMMENT ON COLUMN workflow.bpmn_tasks.ai_predicted_duration_hours IS
    'AI-predicted duration in hours based on similar tasks';

-- =====================================================
-- PROCESS ANALYTICS (for process mining)
-- =====================================================

CREATE TABLE IF NOT EXISTS workflow.process_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID NOT NULL
        REFERENCES workflow.bpmn_instances(id) ON DELETE CASCADE,

    activity_id TEXT NOT NULL,
    activity_type TEXT NOT NULL,

    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (completed_at - started_at))::INTEGER
    ) STORED,

    variables_snapshot JSONB,  -- Variables at this point in time

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_process_analytics_instance
    ON workflow.process_analytics(instance_id);

CREATE INDEX idx_process_analytics_activity
    ON workflow.process_analytics(activity_id);

CREATE INDEX idx_process_analytics_duration
    ON workflow.process_analytics(activity_id, duration_seconds)
    WHERE duration_seconds IS NOT NULL;

-- Comments
COMMENT ON TABLE workflow.process_analytics IS
    'Process mining data - tracks execution time and patterns';
COMMENT ON COLUMN workflow.process_analytics.duration_seconds IS
    'Computed duration in seconds for analytics';

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

ALTER TABLE workflow.bpmn_processes ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow.bpmn_instances ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow.bpmn_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow.process_analytics ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Tenant Isolation

CREATE POLICY tenant_isolation_bpmn_processes
    ON workflow.bpmn_processes
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true)::text);

CREATE POLICY tenant_isolation_bpmn_instances
    ON workflow.bpmn_instances
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true)::text);

CREATE POLICY tenant_isolation_bpmn_tasks
    ON workflow.bpmn_tasks
    FOR ALL
    USING (
        instance_id IN (
            SELECT id FROM workflow.bpmn_instances
            WHERE tenant_id = current_setting('app.current_tenant', true)::text
        )
    );

CREATE POLICY tenant_isolation_process_analytics
    ON workflow.process_analytics
    FOR ALL
    USING (
        instance_id IN (
            SELECT id FROM workflow.bpmn_instances
            WHERE tenant_id = current_setting('app.current_tenant', true)::text
        )
    );

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function: Get active tasks for instance
CREATE OR REPLACE FUNCTION workflow.get_active_tasks(p_instance_id UUID)
RETURNS TABLE (
    task_id UUID,
    activity_id TEXT,
    name TEXT,
    assignee TEXT,
    ai_tip TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id AS task_id,
        t.activity_id,
        t.name,
        t.assignee,
        COALESCE(
            t.ai_recommendations->0->>'message',
            'Complete task: ' || t.name
        ) AS ai_tip
    FROM workflow.bpmn_tasks t
    WHERE t.instance_id = p_instance_id
      AND t.status = 'ACTIVE'
    ORDER BY t.created_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION workflow.get_active_tasks IS
    'Get active tasks for process instance with AI tips';

-- Function: Calculate process duration statistics
CREATE OR REPLACE FUNCTION workflow.get_process_duration_stats(
    p_process_id UUID,
    p_tenant_id TEXT
)
RETURNS TABLE (
    total_instances BIGINT,
    avg_duration_hours FLOAT,
    min_duration_hours FLOAT,
    max_duration_hours FLOAT,
    completion_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total_instances,
        AVG(EXTRACT(EPOCH FROM (completed_at - started_at)) / 3600)::FLOAT AS avg_duration_hours,
        MIN(EXTRACT(EPOCH FROM (completed_at - started_at)) / 3600)::FLOAT AS min_duration_hours,
        MAX(EXTRACT(EPOCH FROM (completed_at - started_at)) / 3600)::FLOAT AS max_duration_hours,
        (COUNT(*) FILTER (WHERE status = 'COMPLETED')::FLOAT / COUNT(*))::FLOAT AS completion_rate
    FROM workflow.bpmn_instances
    WHERE process_id = p_process_id
      AND tenant_id = p_tenant_id
      AND started_at IS NOT NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION workflow.get_process_duration_stats IS
    'Calculate duration statistics for process (for benchmarking)';

-- =====================================================
-- GRANTS
-- =====================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA workflow TO authenticated, service_role;

-- Grant table permissions
GRANT ALL ON workflow.bpmn_processes TO authenticated, service_role;
GRANT ALL ON workflow.bpmn_instances TO authenticated, service_role;
GRANT ALL ON workflow.bpmn_tasks TO authenticated, service_role;
GRANT ALL ON workflow.process_analytics TO authenticated, service_role;

-- Grant function permissions
GRANT EXECUTE ON FUNCTION workflow.get_active_tasks TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION workflow.get_process_duration_stats TO authenticated, service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Insert migration record
INSERT INTO public.schema_migrations (version, applied_at)
VALUES (
    '036',
    NOW()
)
ON CONFLICT (version) DO NOTHING;

COMMENT ON SCHEMA workflow IS
    'Unified Workflow Engine: BPMN processes + AI integration - Migration 036';
