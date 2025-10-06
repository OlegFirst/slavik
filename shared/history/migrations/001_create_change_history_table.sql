-- Change History Table Migration
-- Purpose: Create change_history table for field-level change tracking
-- Task: 3.5 - Change History Tracking

-- Create change_history table
CREATE TABLE IF NOT EXISTS change_history (
    id SERIAL PRIMARY KEY,

    -- What entity
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,

    -- What changed
    change_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(255),
    old_value JSONB,
    new_value JSONB,

    -- Who/When
    changed_by VARCHAR(255) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Context
    change_reason TEXT,
    version_number INTEGER,
    snapshot JSONB,
    change_metadata JSONB
);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_history_entity_type ON change_history(entity_type);
CREATE INDEX IF NOT EXISTS idx_history_entity_id ON change_history(entity_id);
CREATE INDEX IF NOT EXISTS idx_history_tenant_id ON change_history(tenant_id);
CREATE INDEX IF NOT EXISTS idx_history_field_name ON change_history(field_name);
CREATE INDEX IF NOT EXISTS idx_history_changed_by ON change_history(changed_by);
CREATE INDEX IF NOT EXISTS idx_history_changed_at ON change_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_history_version ON change_history(version_number);

-- Composite indexes for complex queries
CREATE INDEX IF NOT EXISTS idx_history_entity ON change_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_history_entity_field ON change_history(entity_type, entity_id, field_name);
CREATE INDEX IF NOT EXISTS idx_history_tenant_time ON change_history(tenant_id, changed_at);
CREATE INDEX IF NOT EXISTS idx_history_user_time ON change_history(changed_by, changed_at);

-- Add comments for documentation
COMMENT ON TABLE change_history IS 'Field-level change tracking for audit trails and rollback';
COMMENT ON COLUMN change_history.entity_type IS 'Type of entity (e.g., BIAProcess, Evidence, Control)';
COMMENT ON COLUMN change_history.entity_id IS 'Unique identifier of the entity';
COMMENT ON COLUMN change_history.tenant_id IS 'Tenant context for multi-tenancy';
COMMENT ON COLUMN change_history.change_type IS 'Type of change (field_update, field_add, field_remove, etc.)';
COMMENT ON COLUMN change_history.field_name IS 'Name of the field that changed';
COMMENT ON COLUMN change_history.old_value IS 'Previous field value (JSONB for flexibility)';
COMMENT ON COLUMN change_history.new_value IS 'New field value (JSONB for flexibility)';
COMMENT ON COLUMN change_history.changed_by IS 'User who made the change';
COMMENT ON COLUMN change_history.changed_at IS 'Timestamp of the change';
COMMENT ON COLUMN change_history.change_reason IS 'Optional reason for the change';
COMMENT ON COLUMN change_history.version_number IS 'Version number of the entity';
COMMENT ON COLUMN change_history.snapshot IS 'Complete entity snapshot at this point in time';
COMMENT ON COLUMN change_history.change_metadata IS 'Additional metadata (IP address, user agent, etc.)';
