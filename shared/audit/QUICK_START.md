# Audit Trail Quick Start Guide

## 5-Minute Setup

### 1. Run Database Migration (2 min)

```bash
cd /Users/MD/AI-Platform-ISO

# Create migration
alembic revision -m "add_audit_logs_table"

# Copy schema from migration_example.sql to the generated migration file

# Run migration
alembic upgrade head

# Verify table created
psql -d your_database -c "\d audit_logs"
```

### 2. Initialize Audit Logger (1 min)

```python
from shared.audit import AuditLogger
from sqlalchemy.ext.asyncio import AsyncSession

# In your FastAPI dependency
async def get_audit_logger(db: AsyncSession = Depends(get_db)):
    return AuditLogger(db)
```

### 3. Update Service (2 min)

```python
from shared.audit import AuditLogger, AuditCategory

class BIAService:
    def __init__(self, repository, audit_logger: AuditLogger = None):
        self.repo = repository
        self.audit = audit_logger

    async def create_process(self, data, user_id: str, request = None):
        # Your existing logic
        process = await self.repo.create(data)

        # Add audit logging
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

---

## Common Operations

### Log Entity Creation

```python
await audit.log_create(
    user_id="user123",
    tenant_id="tenant456",
    category=AuditCategory.BIA,
    entity_type="BIAProcess",
    entity_id="process789",
    entity_data={"name": "Critical Process"},
    request=request  # Optional
)
```

### Log Entity Update

```python
await audit.log_update(
    user_id="user123",
    tenant_id="tenant456",
    category=AuditCategory.BIA,
    entity_type="BIAProcess",
    entity_id="process789",
    before={"status": "draft", "rto_hours": 8},
    after={"status": "active", "rto_hours": 4},
    request=request
)
```

### Log State Transition

```python
await audit.log_state_transition(
    user_id="user123",
    tenant_id="tenant456",
    category=AuditCategory.EVIDENCE,
    entity_type="Evidence",
    entity_id="evidence001",
    from_state="draft",
    to_state="submitted",
    request=request
)
```

### Query Audit Logs

```python
from shared.audit import AuditLogModel
from sqlalchemy import select

# Get logs for entity
stmt = select(AuditLogModel).where(
    AuditLogModel.entity_type == "BIAProcess",
    AuditLogModel.entity_id == "process123"
).order_by(AuditLogModel.timestamp)

results = await session.execute(stmt)
logs = results.scalars().all()
```

---

## FastAPI Integration Example

```python
from fastapi import APIRouter, Depends, Request
from shared.audit import AuditLogger, AuditCategory

router = APIRouter()

@router.post("/processes")
async def create_process(
    data: BIAProcessCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    audit: AuditLogger = Depends(get_audit_logger),
    current_user: User = Depends(get_current_user)
):
    # Create service with audit logger
    service = BIAService(
        repository=BIARepository(db),
        audit_logger=audit
    )

    # Create process (audit logged automatically)
    process = await service.create_process(
        data=data,
        user_id=current_user.id,
        request=request
    )

    return process
```

---

## Troubleshooting

### Audit Logs Not Created?

1. Check database connection
2. Verify audit_logger passed to service
3. Check application logs for warnings
4. Ensure user_id and tenant_id are provided

### Performance Issues?

1. Check index usage: `EXPLAIN SELECT * FROM audit_logs WHERE...`
2. Monitor write latency
3. Consider archiving old logs
4. Review connection pool settings

### Import Errors?

```python
# Make sure PYTHONPATH includes project root
import sys
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

from shared.audit import AuditLogger
```

---

## Next Steps

1. Read full documentation: `README.md`
2. Review implementation details: `IMPLEMENTATION_SUMMARY.md`
3. Check migration guide: `migration_example.sql`
4. Set up monitoring and alerts
5. Configure retention policies

---

## Support

- Full documentation: `/Users/MD/AI-Platform-ISO/shared/audit/README.md`
- Migration guide: `/Users/MD/AI-Platform-ISO/shared/audit/migration_example.sql`
- Implementation report: `/Users/MD/AI-Platform-ISO/shared/audit/IMPLEMENTATION_SUMMARY.md`

**ISO 22301 Compliant** ✅
**Production Ready** ✅
