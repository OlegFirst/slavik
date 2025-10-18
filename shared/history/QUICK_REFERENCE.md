# Change History Tracking - Quick Reference

## Installation

```bash
pip install deepdiff>=6.7.0
psql -d bcm -f shared/history/migrations/001_create_change_history_table.sql
```

---

## Basic Usage

### 1. Import
```python
from shared.history import ChangeTracker
```

### 2. Track Changes in Repository
```python
async def update(self, id: int, updates: dict, changed_by: str):
    # Get before state
    before = (await self.get(id)).model_dump()

    # Apply updates
    updated = await self._do_update(id, updates)

    # Track changes
    tracker = ChangeTracker(self.db)
    await tracker.track_changes(
        entity_type="BIAProcess",
        entity_id=str(id),
        tenant_id=updated.tenant_id,
        before=before,
        after=updated.model_dump(),
        changed_by=changed_by,
        change_reason="User update"
    )

    return updated
```

### 3. Get History
```python
# Complete history
history = await tracker.get_entity_history(
    entity_type="BIAProcess",
    entity_id="123",
    tenant_id="abc"
)

# Field-specific history
changes = await tracker.get_field_history(
    entity_type="BIAProcess",
    entity_id="123",
    field_name="rto_hours",
    tenant_id="abc"
)
```

---

## API Endpoints

```http
# Complete history
GET /api/bia/history/processes/123?tenant_id=abc&limit=100

# Field history
GET /api/bia/history/processes/123/fields/rto_hours?tenant_id=abc

# Version snapshot
GET /api/bia/history/processes/123/snapshot/3?tenant_id=abc
```

---

## Common Patterns

### Disable Change Tracking
```python
await repo.update(id, updates, track_changes=False)
```

### Ignore Fields
```python
changes = tracker.detect_changes(
    before=old_state,
    after=new_state,
    ignore_fields=["updated_at", "version", "last_seen"]
)
```

### Save Snapshot
```python
await tracker.track_changes(
    ...,
    save_snapshot=True  # Default: True
)
```

---

## Key Models

```python
# Change type
ChangeType.FIELD_UPDATE
ChangeType.FIELD_ADD
ChangeType.FIELD_REMOVE
ChangeType.RECORD_CREATE
ChangeType.RECORD_DELETE
ChangeType.STATE_CHANGE

# Single change
FieldChange(
    field="rto_hours",
    old_value=24,
    new_value=12,
    changed_at=datetime.utcnow(),
    changed_by="user@example.com"
)

# History entry
ChangeHistoryEntry(
    entity_type="BIAProcess",
    entity_id="123",
    tenant_id="abc",
    change_type=ChangeType.FIELD_UPDATE,
    field_name="rto_hours",
    old_value=24,
    new_value=12,
    changed_by="user@example.com",
    change_reason="Risk assessment update"
)
```

---

## Files

- **Models**: `/Users/MD/AI-Platform-ISO/shared/history/models.py`
- **Tracker**: `/Users/MD/AI-Platform-ISO/shared/history/tracker.py`
- **Migration**: `/Users/MD/AI-Platform-ISO/shared/history/migrations/001_create_change_history_table.sql`
- **API**: `/Users/MD/AI-Platform-ISO/platform_services/bcm_domain/services/bia_service/api/history.py`
- **Full Docs**: `/Users/MD/AI-Platform-ISO/shared/history/README.md`

---

## Troubleshooting

### Import Error: "No module named 'deepdiff'"
```bash
pip install deepdiff>=6.7.0
```

### SQLAlchemy Error: "Attribute name 'metadata' is reserved"
✅ Fixed - using `change_metadata` instead

### No changes detected
- Check ignore_fields list
- Verify before/after states are different
- Ensure fields exist in both states

### Performance issues
- Disable snapshots for high-volume changes
- Implement retention policy
- Add appropriate indexes

---

## Best Practices

✅ **DO**
- Always provide `changed_by`
- Use `change_reason` for compliance
- Ignore transient fields (updated_at, etc.)
- Set appropriate query limits
- Document entity-specific ignored fields

❌ **DON'T**
- Don't track password changes (security)
- Don't snapshot very large entities
- Don't query without limits
- Don't track transient/computed fields

---

## Examples

See:
- BIA Repository: `/Users/MD/AI-Platform-ISO/platform_services/bcm_domain/services/bia_service/repositories/bia_repository.py`
- API Endpoints: `/Users/MD/AI-Platform-ISO/platform_services/bcm_domain/services/bia_service/api/history.py`
- Tests: `/Users/MD/AI-Platform-ISO/shared/history/test_tracker.py`
