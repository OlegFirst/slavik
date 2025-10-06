-- Alembic Migration for Audit Logs Table
-- ISO 22301 Compliant Audit Trail
--
-- To create this migration with Alembic:
-- alembic revision -m "add_audit_logs_table"
--
-- Then paste the relevant parts into the generated migration file

-- ==========================================
-- CREATE TABLE
-- ==========================================

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Who performed the action
    user_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    tenant_id VARCHAR(255) NOT NULL,

    -- What action was performed
    action VARCHAR(50) NOT NULL,  -- create, update, delete, state_transition, etc.
    category VARCHAR(50) NOT NULL,  -- bia, compliance, evidence, etc.
    entity_type VARCHAR(100) NOT NULL,  -- BIAProcess, Evidence, Assessment, etc.
    entity_id VARCHAR(255),  -- ID of the entity

    -- Details of the action
    description TEXT,  -- Human-readable description
    changes JSON,  -- Before/after values for updates
    metadata JSON,  -- Additional context

    -- When and where
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),  -- IPv6 compatible (max 45 chars)
    user_agent VARCHAR(500),

    -- Result
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT
);

-- ==========================================
-- CREATE INDEXES
-- ==========================================

-- Most common query: get logs for tenant in time range
CREATE INDEX idx_audit_tenant_time ON audit_logs(tenant_id, timestamp);

-- User activity reports
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, timestamp);

-- Entity audit trail
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- Compliance reports by category
CREATE INDEX idx_audit_category_time ON audit_logs(category, timestamp);

-- Action-specific queries
CREATE INDEX idx_audit_action ON audit_logs(action);

-- Failed operations tracking
CREATE INDEX idx_audit_success ON audit_logs(success) WHERE success = FALSE;

-- ==========================================
-- ALEMBIC MIGRATION EXAMPLE
-- ==========================================

"""
# In alembic/versions/xxx_add_audit_logs_table.py

def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('tenant_id', sa.String(length=255), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_audit_tenant_time', 'audit_logs', ['tenant_id', 'timestamp'])
    op.create_index('idx_audit_user_time', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_category_time', 'audit_logs', ['category', 'timestamp'])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])


def downgrade():
    op.drop_index('idx_audit_action', table_name='audit_logs')
    op.drop_index('idx_audit_category_time', table_name='audit_logs')
    op.drop_index('idx_audit_entity', table_name='audit_logs')
    op.drop_index('idx_audit_user_time', table_name='audit_logs')
    op.drop_index('idx_audit_tenant_time', table_name='audit_logs')
    op.drop_table('audit_logs')
"""

-- ==========================================
-- SAMPLE QUERIES
-- ==========================================

-- Get all logs for a tenant in the last 7 days
SELECT * FROM audit_logs
WHERE tenant_id = 'tenant123'
  AND timestamp >= datetime('now', '-7 days')
ORDER BY timestamp DESC;

-- Get audit trail for specific entity
SELECT * FROM audit_logs
WHERE entity_type = 'BIAProcess'
  AND entity_id = 'process789'
ORDER BY timestamp ASC;

-- Get user activity
SELECT * FROM audit_logs
WHERE user_id = 'user123'
  AND tenant_id = 'tenant456'
ORDER BY timestamp DESC;

-- Get failed operations
SELECT * FROM audit_logs
WHERE success = FALSE
  AND timestamp >= datetime('now', '-1 day')
ORDER BY timestamp DESC;

-- Get state transitions by category
SELECT * FROM audit_logs
WHERE action = 'state_transition'
  AND category = 'evidence'
  AND timestamp >= datetime('now', '-30 days')
ORDER BY timestamp DESC;

-- Compliance report: all BIA operations
SELECT
    DATE(timestamp) as date,
    action,
    COUNT(*) as count
FROM audit_logs
WHERE category = 'bia'
  AND timestamp >= datetime('now', '-90 days')
GROUP BY DATE(timestamp), action
ORDER BY date DESC, action;

-- ==========================================
-- RETENTION POLICY
-- ==========================================

-- ISO 22301 typically requires 7+ years retention
-- Consider implementing partitioning for large tables

-- Example: Archive old logs (manual process)
-- CREATE TABLE audit_logs_archive_2024 AS
-- SELECT * FROM audit_logs
-- WHERE timestamp < '2025-01-01';

-- DELETE FROM audit_logs
-- WHERE timestamp < '2025-01-01';

-- ==========================================
-- PERFORMANCE NOTES
-- ==========================================

-- 1. Consider partitioning by date for very large tables
-- 2. Regularly analyze table statistics: ANALYZE audit_logs;
-- 3. Monitor index usage and adjust as needed
-- 4. Consider archiving old data to separate tables
-- 5. Use connection pooling for audit writes
-- 6. For PostgreSQL, consider BRIN indexes for timestamp columns
