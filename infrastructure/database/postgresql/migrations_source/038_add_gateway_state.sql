-- =====================================================
-- Migration: 038 - Add Gateway State Tracking
-- Description: Add gateway_state column for parallel/inclusive gateway joins
-- Date: 2025-10-05
-- Purpose: Track gateway convergence state for parallel workflows
-- =====================================================

-- Add gateway_state column to bpmn_instances
ALTER TABLE workflow.bpmn_instances
ADD COLUMN IF NOT EXISTS gateway_state JSONB DEFAULT '{}'::jsonb;

-- Add index for gateway_state queries
CREATE INDEX IF NOT EXISTS idx_bpmn_instances_gateway_state
    ON workflow.bpmn_instances USING gin(gateway_state);

-- Comment
COMMENT ON COLUMN workflow.bpmn_instances.gateway_state IS
    'Gateway state tracking for parallel/inclusive gateway joins. Format: {
        "Gateway_123": {
            "incoming_completed": ["Flow1", "Flow2"],
            "incoming_total": ["Flow1", "Flow2", "Flow3"]
        }
    }';

-- =====================================================
-- Migration Complete
-- =====================================================

-- Record migration
INSERT INTO public.schema_migrations (version, applied_at)
VALUES ('038', NOW())
ON CONFLICT (version) DO NOTHING;
