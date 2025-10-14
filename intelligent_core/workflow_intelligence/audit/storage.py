"""
Audit log storage backends
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncpg
import structlog

from .events import AuditEvent

logger = structlog.get_logger(__name__)


class AuditStorage(ABC):
    """Abstract base class for audit storage"""

    @abstractmethod
    async def save_event(self, event: AuditEvent) -> None:
        """Save audit event"""
        pass

    @abstractmethod
    async def get_events(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Query audit events"""
        pass


class PostgresAuditStorage(AuditStorage):
    """PostgreSQL-based audit storage with RLS"""

    def __init__(self, pool: asyncpg.Pool):
        """
        Initialize with connection pool

        Args:
            pool: asyncpg connection pool
        """
        self.pool = pool

    async def ensure_schema(self) -> None:
        """Create audit_logs table if not exists"""
        async with self.pool.acquire() as conn:
            # Create audit_logs table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_intelligence.audit_logs (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR(255) UNIQUE NOT NULL,

                    -- Event identification
                    event_type VARCHAR(100) NOT NULL,
                    event_category VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

                    -- Actor
                    user_id VARCHAR(255),
                    tenant_id VARCHAR(255) NOT NULL,

                    -- Action
                    action TEXT NOT NULL,
                    resource_type VARCHAR(100),
                    resource_id VARCHAR(255),

                    -- Result
                    success BOOLEAN NOT NULL DEFAULT TRUE,
                    error_message TEXT,

                    -- Context
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    session_id VARCHAR(255),

                    -- Metadata
                    metadata JSONB,

                    -- Security flags
                    is_security_event BOOLEAN DEFAULT FALSE,
                    is_compliance_relevant BOOLEAN DEFAULT FALSE,
                    severity VARCHAR(20) DEFAULT 'info',

                    -- ISO compliance
                    iso_clause VARCHAR(20),

                    -- Indexes for fast queries
                    created_at TIMESTAMP DEFAULT NOW()
                );

                -- Indexes for common queries
                CREATE INDEX IF NOT EXISTS idx_audit_tenant_timestamp
                    ON workflow_intelligence.audit_logs(tenant_id, timestamp DESC);

                CREATE INDEX IF NOT EXISTS idx_audit_user_timestamp
                    ON workflow_intelligence.audit_logs(user_id, timestamp DESC);

                CREATE INDEX IF NOT EXISTS idx_audit_event_type
                    ON workflow_intelligence.audit_logs(event_type, timestamp DESC);

                CREATE INDEX IF NOT EXISTS idx_audit_security_events
                    ON workflow_intelligence.audit_logs(is_security_event, timestamp DESC)
                    WHERE is_security_event = TRUE;

                CREATE INDEX IF NOT EXISTS idx_audit_compliance_events
                    ON workflow_intelligence.audit_logs(is_compliance_relevant, iso_clause, timestamp DESC)
                    WHERE is_compliance_relevant = TRUE;
            """)

            # Enable RLS on audit_logs
            await conn.execute("""
                ALTER TABLE workflow_intelligence.audit_logs ENABLE ROW LEVEL SECURITY;

                -- Drop existing policy if exists
                DROP POLICY IF EXISTS tenant_isolation_audit ON workflow_intelligence.audit_logs;

                -- Create RLS policy for tenant isolation
                CREATE POLICY tenant_isolation_audit
                ON workflow_intelligence.audit_logs
                FOR SELECT
                USING (
                    tenant_id = current_setting('app.current_tenant_id', true)
                    OR
                    -- Allow reading own user's audit logs across tenants (for compliance officers)
                    user_id = current_setting('app.current_user_id', true)
                );

                -- Allow INSERT for any tenant (audit logs should always be written)
                DROP POLICY IF EXISTS audit_insert_policy ON workflow_intelligence.audit_logs;

                CREATE POLICY audit_insert_policy
                ON workflow_intelligence.audit_logs
                FOR INSERT
                WITH CHECK (TRUE);  -- Always allow INSERT
            """)

            logger.info("audit_storage.schema.created")

    async def save_event(self, event: AuditEvent) -> None:
        """
        Save audit event to database

        Args:
            event: AuditEvent to save
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO workflow_intelligence.audit_logs
                    (event_id, event_type, event_category, timestamp,
                     user_id, tenant_id, action, resource_type, resource_id,
                     success, error_message, ip_address, user_agent, session_id,
                     metadata, is_security_event, is_compliance_relevant,
                     severity, iso_clause)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
            """,
                event.event_id,
                event.event_type,
                event.event_category,
                event.timestamp,
                event.user_id,
                event.tenant_id,
                event.action,
                event.resource_type,
                event.resource_id,
                event.success,
                event.error_message,
                event.ip_address,
                event.user_agent,
                event.session_id,
                event.metadata if event.metadata else {},
                event.is_security_event,
                event.is_compliance_relevant,
                event.severity,
                event.iso_clause
            )

        logger.debug(
            "audit.event.saved",
            event_id=event.event_id,
            event_type=event.event_type,
            user_id=event.user_id,
            tenant_id=event.tenant_id
        )

    async def get_events(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        event_category: Optional[str] = None,
        is_security_event: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit events

        Args:
            tenant_id: Filter by tenant
            user_id: Filter by user
            event_type: Filter by event type
            event_category: Filter by category
            is_security_event: Filter security events
            start_time: Events after this time
            end_time: Events before this time
            limit: Maximum number of events

        Returns:
            List of audit events as dictionaries
        """

        # Build dynamic query
        conditions = []
        params = []
        param_count = 1

        if tenant_id:
            conditions.append(f"tenant_id = ${param_count}")
            params.append(tenant_id)
            param_count += 1

        if user_id:
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
            param_count += 1

        if event_type:
            conditions.append(f"event_type = ${param_count}")
            params.append(event_type)
            param_count += 1

        if event_category:
            conditions.append(f"event_category = ${param_count}")
            params.append(event_category)
            param_count += 1

        if is_security_event is not None:
            conditions.append(f"is_security_event = ${param_count}")
            params.append(is_security_event)
            param_count += 1

        if start_time:
            conditions.append(f"timestamp >= ${param_count}")
            params.append(start_time)
            param_count += 1

        if end_time:
            conditions.append(f"timestamp <= ${param_count}")
            params.append(end_time)
            param_count += 1

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        query = f"""
            SELECT *
            FROM workflow_intelligence.audit_logs
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ${param_count}
        """
        params.append(limit)

        async with self.pool.acquire() as conn:
            # Set tenant context for RLS if provided
            if tenant_id:
                await conn.execute(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")

            rows = await conn.fetch(query, *params)

            # Reset tenant context
            if tenant_id:
                await conn.execute("RESET app.current_tenant_id")

        return [dict(row) for row in rows]

    async def get_security_events(
        self,
        tenant_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get security events for tenant"""
        return await self.get_events(
            tenant_id=tenant_id,
            is_security_event=True,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

    async def get_compliance_events(
        self,
        tenant_id: str,
        iso_clause: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get compliance-relevant events"""

        conditions = [
            f"tenant_id = $1",
            f"is_compliance_relevant = TRUE"
        ]
        params = [tenant_id]
        param_count = 2

        if iso_clause:
            conditions.append(f"iso_clause = ${param_count}")
            params.append(iso_clause)
            param_count += 1

        if start_time:
            conditions.append(f"timestamp >= ${param_count}")
            params.append(start_time)
            param_count += 1

        if end_time:
            conditions.append(f"timestamp <= ${param_count}")
            params.append(end_time)
            param_count += 1

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT *
            FROM workflow_intelligence.audit_logs
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ${param_count}
        """
        params.append(limit)

        async with self.pool.acquire() as conn:
            await conn.execute(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")
            rows = await conn.fetch(query, *params)
            await conn.execute("RESET app.current_tenant_id")

        return [dict(row) for row in rows]
