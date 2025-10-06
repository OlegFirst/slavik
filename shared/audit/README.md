# Audit Trail Module

ISO 22301 compliant audit logging for Business Continuity Management System (BCMS) activities.

## Overview

This module provides comprehensive audit trail functionality to track all critical operations, state transitions, and security events across the BIA and Compliance modules. It supports forensic analysis, compliance reporting, and security monitoring.

## Features

- **CRUD Operation Tracking**: Log all Create, Read, Update, Delete operations
- **State Transition Logging**: Track workflow state changes with before/after states
- **Permission Auditing**: Log permission grants and revocations
- **Authentication Tracking**: Monitor login/logout events
- **Non-blocking**: Audit failures never block primary operations
- **Indexed Queries**: Optimized database indexes for fast retrieval
- **IP/User-Agent Tracking**: Capture request context for forensics

## Components

### 1. Models (`models.py`)

#### AuditAction
Enumeration of audit action types:
- `CREATE` - Entity creation
- `READ` - Entity read/access
- `UPDATE` - Entity modification
- `DELETE` - Entity deletion
- `STATE_TRANSITION` - Workflow state change
- `LOGIN/LOGOUT` - Authentication events
- `PERMISSION_GRANTED/REVOKED` - Authorization changes
- `EXPORT/IMPORT` - Data transfer operations

#### AuditCategory
Enumeration of audit event categories:
- `BIA` - Business Impact Analysis
- `COMPLIANCE` - Compliance management
- `EVIDENCE` - Evidence management
- `ASSESSMENT` - Assessments
- `GAP` - Gap analysis
- `NONCONFORMITY` - Nonconformities
- `AUDIT` - Audit activities
- `AUTHENTICATION` - Auth events
- `AUTHORIZATION` - Permission changes
- `SYSTEM` - System operations

#### AuditLogModel
SQLAlchemy model for database persistence:
- Multi-tenant support
- Optimized indexes for common queries
- JSON fields for flexible metadata storage
- IPv6 compatible IP address tracking

#### AuditLogEntry
Pydantic model for API/business logic:
- Type-safe data validation
- Automatic timestamp generation
- Optional before/after change tracking

### 2. Logger (`logger.py`)

#### AuditLogger
Core service for creating audit log entries.

**Methods:**

```python
async def log(
    user_id: str,
    tenant_id: str,
    action: AuditAction,
    category: AuditCategory,
    entity_type: str,
    entity_id: Optional[str] = None,
    description: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    success: bool = True,
    error_message: Optional[str] = None
) -> AuditLogEntry
```

**Convenience Methods:**
- `log_create()` - Log entity creation
- `log_update()` - Log entity update with before/after comparison
- `log_delete()` - Log entity deletion
- `log_state_transition()` - Log workflow state transition
- `log_permission_change()` - Log permission grant/revoke
- `log_authentication()` - Log authentication attempt
- `log_export()` - Log data export

### 3. Decorators (`decorators.py`)

Optional decorators for automatic audit logging:

```python
@audit_log(
    action=AuditAction.CREATE,
    category=AuditCategory.BIA,
    entity_type="BIAProcess",
    extract_entity_id=lambda result: str(result.id)
)
async def create_process(...):
    ...
```

**Note**: Decorators are provided for convenience but may require dependency injection setup. Direct logger usage is recommended for most cases.

## Usage Examples

### Basic Usage

```python
from shared.audit import AuditLogger, AuditAction, AuditCategory
from sqlalchemy.ext.asyncio import AsyncSession

# Initialize logger
audit = AuditLogger(db_session)

# Log entity creation
await audit.log_create(
    user_id="user123",
    tenant_id="tenant456",
    category=AuditCategory.BIA,
    entity_type="BIAProcess",
    entity_id="process789",
    entity_data={
        "name": "Critical Database",
        "criticality": "high",
        "rto_hours": 4
    }
)
```

### State Transition Logging

```python
# Log workflow state change
await audit.log_state_transition(
    user_id="user123",
    tenant_id="tenant456",
    category=AuditCategory.EVIDENCE,
    entity_type="Evidence",
    entity_id="evidence001",
    from_state="draft",
    to_state="submitted",
    metadata={
        "reviewer_id": "auditor789",
        "comments": "Evidence meets requirements"
    }
)
```

### Update with Change Tracking

```python
# Log update with before/after comparison
before = {
    "criticality": "medium",
    "rto_hours": 8,
    "status": "draft"
}

after = {
    "criticality": "high",
    "rto_hours": 4,
    "status": "active"
}

await audit.log_update(
    user_id="user123",
    tenant_id="tenant456",
    category=AuditCategory.BIA,
    entity_type="BIAProcess",
    entity_id="process789",
    before=before,
    after=after,
    request=request  # Optional FastAPI request for IP/user-agent
)
```

### Service Integration

```python
class BIAService:
    def __init__(self, repository: BIARepository, audit_logger: Optional[AuditLogger] = None):
        self.repo = repository
        self.audit = audit_logger

    async def create_process(
        self,
        data: BIAProcessCreate,
        user_id: str = "system",
        request: Optional[Request] = None
    ) -> BIAProcess:
        # Create process
        process = await self.repo.create(data)

        # Audit log (non-blocking)
        if self.audit:
            try:
                await self.audit.log_create(
                    user_id=user_id,
                    tenant_id=data.tenant_id,
                    category=AuditCategory.BIA,
                    entity_type="BIAProcess",
                    entity_id=str(process.id),
                    entity_data={"name": process.name},
                    request=request
                )
            except Exception as e:
                logger.warning(f"Audit logging failed: {e}")

        return process
```

### Workflow Integration

```python
class BaseWorkflow:
    def __init__(self, eventbus_client, repository, audit_logger: Optional[AuditLogger] = None):
        self.eventbus = eventbus_client
        self.repository = repository
        self.audit = audit_logger

    async def transition(
        self,
        entity_id: str,
        from_state: Enum,
        to_state: Enum,
        actor_id: str,
        tenant_id: str,
        request = None
    ):
        # Perform state transition
        await self.repository.update_status(entity_id, to_state.value)

        # Audit log state transition
        if self.audit:
            try:
                await self.audit.log_state_transition(
                    user_id=actor_id,
                    tenant_id=tenant_id,
                    category=self._get_audit_category(),
                    entity_type=self.event_prefix,
                    entity_id=entity_id,
                    from_state=from_state.value,
                    to_state=to_state.value,
                    request=request
                )
            except Exception as e:
                logger.warning(f"Audit logging failed: {e}")
```

## Database Schema

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Who
    user_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    tenant_id VARCHAR(255) NOT NULL,

    -- What
    action VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255),

    -- Details
    description TEXT,
    changes JSON,
    metadata JSON,

    -- When/Where
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),

    -- Result
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT
);

-- Indexes for common queries
CREATE INDEX idx_audit_tenant_time ON audit_logs(tenant_id, timestamp);
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, timestamp);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_category_time ON audit_logs(category, timestamp);
```

## Querying Audit Logs

### By Tenant and Time Range

```python
from datetime import datetime, timedelta
from sqlalchemy import select

# Get logs for last 7 days
start_date = datetime.utcnow() - timedelta(days=7)
stmt = select(AuditLogModel).where(
    AuditLogModel.tenant_id == "tenant123",
    AuditLogModel.timestamp >= start_date
).order_by(AuditLogModel.timestamp.desc())

results = await session.execute(stmt)
logs = results.scalars().all()
```

### By Entity

```python
# Get all logs for specific entity
stmt = select(AuditLogModel).where(
    AuditLogModel.entity_type == "BIAProcess",
    AuditLogModel.entity_id == "process789"
).order_by(AuditLogModel.timestamp)

results = await session.execute(stmt)
logs = results.scalars().all()
```

### By User Activity

```python
# Get all actions by specific user
stmt = select(AuditLogModel).where(
    AuditLogModel.user_id == "user123",
    AuditLogModel.tenant_id == "tenant456"
).order_by(AuditLogModel.timestamp.desc())

results = await session.execute(stmt)
logs = results.scalars().all()
```

## ISO 22301 Compliance

This audit module satisfies ISO 22301:2019 requirements for:

- **Clause 7.5**: Documented information control
- **Clause 9.1**: Monitoring and measurement
- **Clause 10.2**: Nonconformity and corrective action tracking

### Audit Trail Requirements Met

1. **Who**: User ID, email, tenant context
2. **What**: Action, category, entity type, entity ID
3. **When**: UTC timestamp with microsecond precision
4. **Where**: IP address, user agent
5. **Why**: Description, metadata
6. **How**: Changes (before/after states)
7. **Result**: Success/failure with error messages

### Retention and Immutability

- Audit logs should be retained per organizational policy (typically 7+ years)
- Consider implementing append-only storage
- Regular backups to immutable storage (S3 Glacier, etc.)
- Implement log signing for tamper detection

## Performance Considerations

### Indexes

The module includes optimized indexes for common query patterns:
- Tenant + Time (most common filter)
- User + Time (user activity reports)
- Entity Type + ID (entity audit trail)
- Category + Time (compliance reports)

### Async Operations

All audit logging is asynchronous and non-blocking:
- Primary operations never wait for audit completion
- Failures are logged but don't interrupt workflows
- Use connection pooling for database sessions

### Monitoring

Monitor audit logging health:
- Failed audit log attempts (application logs)
- Audit log write latency
- Audit table size growth
- Index performance

## Error Handling

Audit logging follows "fail-safe" principles:

1. **Never block primary operations**: Wrapped in try/except
2. **Log failures prominently**: Warning level logs
3. **Preserve context**: Include user, tenant, entity info in error logs
4. **Consider alerting**: For audit system failures

```python
if self.audit:
    try:
        await self.audit.log_create(...)
    except Exception as e:
        logger.warning(f"Audit logging failed: {e}", extra={
            "user_id": user_id,
            "tenant_id": tenant_id,
            "entity_type": "BIAProcess",
            "entity_id": entity_id
        })
```

## Migration Guide

To add audit logging to an existing service:

1. **Add audit logger to service constructor**:
   ```python
   def __init__(self, repository, audit_logger: Optional[AuditLogger] = None):
       self.repo = repository
       self.audit = audit_logger
   ```

2. **Add user_id and request parameters to methods**:
   ```python
   async def create_entity(
       self,
       data: EntityCreate,
       user_id: str = "system",
       request: Optional[Request] = None
   ):
   ```

3. **Add audit logging after operations**:
   ```python
   entity = await self.repo.create(data)

   if self.audit:
       try:
           await self.audit.log_create(...)
       except Exception as e:
           logger.warning(f"Audit logging failed: {e}")
   ```

## Testing

### Unit Tests

```python
import pytest
from shared.audit import AuditLogger, AuditAction, AuditCategory

@pytest.mark.asyncio
async def test_log_create(db_session):
    audit = AuditLogger(db_session)

    entry = await audit.log_create(
        user_id="test_user",
        tenant_id="test_tenant",
        category=AuditCategory.BIA,
        entity_type="BIAProcess",
        entity_id="test123",
        entity_data={"name": "Test Process"}
    )

    assert entry.action == AuditAction.CREATE
    assert entry.category == AuditCategory.BIA
    assert entry.success is True
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_bia_service_creates_audit_log(db_session):
    audit = AuditLogger(db_session)
    service = BIAService(repository, audit_logger=audit)

    process = await service.create_process(
        data=BIAProcessCreate(...),
        user_id="user123"
    )

    # Verify audit log was created
    logs = await get_audit_logs(entity_id=str(process.id))
    assert len(logs) == 1
    assert logs[0].action == AuditAction.CREATE
```

## Future Enhancements

- **Log Aggregation**: Integrate with centralized logging (ELK, Splunk)
- **Real-time Alerting**: Trigger alerts on suspicious activity
- **Compliance Reports**: Pre-built reports for ISO 22301 audits
- **Log Signing**: Cryptographic signing for tamper detection
- **Data Retention Policies**: Automatic archival and deletion
- **Advanced Analytics**: ML-based anomaly detection

## License

Proprietary - AI Platform ISO 22301 BCMS

## Support

For questions or issues, contact the platform team.
