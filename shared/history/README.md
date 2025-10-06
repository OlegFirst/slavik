# Change History Tracking Module

## Overview

The Change History module provides field-level change tracking for audit trails, compliance reporting, and rollback capabilities. It automatically detects and records what changed, who changed it, when, and why.

## Features

- **Field-level change detection**: Uses DeepDiff to detect changes at any nesting level
- **Automatic tracking**: Integrates seamlessly with repository pattern
- **Version snapshots**: Stores complete entity state for point-in-time recovery
- **Audit trails**: Complete WHO/WHEN/WHAT information for compliance
- **Rollback support**: Retrieve entity state at any previous version
- **Multi-tenant**: Full tenant isolation and context

## Database Schema

The `change_history` table stores all changes:

```sql
CREATE TABLE change_history (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100),      -- Type of entity (BIAProcess, Evidence, etc.)
    entity_id VARCHAR(255),         -- Entity identifier
    tenant_id VARCHAR(255),         -- Tenant context
    change_type VARCHAR(50),        -- Type of change
    field_name VARCHAR(255),        -- Field that changed
    old_value JSONB,                -- Previous value
    new_value JSONB,                -- New value
    changed_by VARCHAR(255),        -- User who made change
    changed_at TIMESTAMP,           -- When change occurred
    change_reason TEXT,             -- Optional reason
    version_number INTEGER,         -- Version number
    snapshot JSONB,                 -- Full entity snapshot
    metadata JSONB                  -- Additional metadata
);
```

## Installation

1. Install dependencies:
```bash
pip install deepdiff>=6.7.0
```

2. Run database migration:
```bash
psql -d your_database -f shared/history/migrations/001_create_change_history_table.sql
```

## Usage

### Basic Integration with Repository

```python
from shared.history import ChangeTracker

async def update(
    self,
    process_id: int,
    updates: dict,
    changed_by: str,
    change_reason: str = None,
    track_changes: bool = True
) -> BIAProcess:
    """Update entity with change tracking"""

    # Get current state
    if track_changes:
        current = await self.get(process_id)
        before_state = current.model_dump()

    # Apply updates
    # ... your update logic ...

    # Track changes
    if track_changes:
        after_state = updated.model_dump()
        tracker = ChangeTracker(self.db)
        await tracker.track_changes(
            entity_type="BIAProcess",
            entity_id=str(process_id),
            tenant_id=updated.tenant_id,
            before=before_state,
            after=after_state,
            changed_by=changed_by,
            change_reason=change_reason
        )

    return updated
```

### Get Entity History

```python
from shared.history import ChangeTracker

tracker = ChangeTracker(db)

# Get complete change history
history = await tracker.get_entity_history(
    entity_type="BIAProcess",
    entity_id="123",
    tenant_id="tenant_abc",
    limit=100
)

print(f"Total changes: {history.total_changes}")
print(f"Current version: {history.current_version}")
print(f"Created by: {history.created_by}")

for change in history.changes:
    print(f"{change.field_name}: {change.old_value} -> {change.new_value}")
```

### Get Field History

```python
# Track changes for a specific field
field_history = await tracker.get_field_history(
    entity_type="BIAProcess",
    entity_id="123",
    field_name="rto_hours",
    tenant_id="tenant_abc"
)

for change in field_history:
    print(f"{change.changed_at}: {change.old_value} -> {change.new_value} by {change.changed_by}")
```

### Detect Changes Without Persisting

```python
tracker = ChangeTracker(db)

changes = tracker.detect_changes(
    before={"name": "Old Name", "rto_hours": 24},
    after={"name": "New Name", "rto_hours": 12},
    ignore_fields=["updated_at"]
)

for change in changes:
    print(f"{change.field}: {change.old_value} -> {change.new_value}")
```

## API Endpoints

The module provides REST API endpoints for querying change history:

### Get Process History
```http
GET /api/bia/history/processes/{process_id}?tenant_id=abc&limit=100

Response:
{
    "entity_type": "BIAProcess",
    "entity_id": "123",
    "current_version": 5,
    "total_changes": 42,
    "changes": [...]
}
```

### Get Field History
```http
GET /api/bia/history/processes/{process_id}/fields/{field_name}?tenant_id=abc

Response:
[
    {
        "field": "rto_hours",
        "old_value": 24,
        "new_value": 12,
        "changed_at": "2025-10-03T10:30:00Z",
        "changed_by": "user@example.com"
    }
]
```

### Get Version Snapshot
```http
GET /api/bia/history/processes/{process_id}/snapshot/{version}?tenant_id=abc

Response:
{
    "id": 123,
    "name": "Critical Process",
    "rto_hours": 12,
    ...
}
```

## Change Detection

The module uses DeepDiff for intelligent change detection:

- **Nested objects**: Detects changes at any level
- **Lists**: Handles list modifications (additions, removals, reordering)
- **Type changes**: Detects when field type changes
- **Null handling**: Properly tracks null/undefined transitions

## Best Practices

1. **Always provide changed_by**: Required for audit trails
2. **Use change_reason for compliance**: Document why changes were made
3. **Enable snapshots for critical entities**: Allows full rollback
4. **Ignore transient fields**: Updated_at, timestamps, etc.
5. **Set appropriate limits**: Large histories can impact performance
6. **Regular cleanup**: Archive old changes based on retention policy

## Performance Considerations

- **Indexes**: The module creates indexes for common query patterns
- **Snapshot size**: Full snapshots increase storage; use selectively
- **Query limits**: Default 100 changes; adjust based on needs
- **Async operations**: All database operations are async

## Integration Checklist

- [ ] Install deepdiff dependency
- [ ] Run database migration
- [ ] Update repository update() method signature
- [ ] Add track_changes parameter
- [ ] Implement before/after state capture
- [ ] Call ChangeTracker.track_changes()
- [ ] Register history API routes
- [ ] Test change detection
- [ ] Test history retrieval
- [ ] Document entity-specific fields to ignore

## Example: Full Integration

See `/services/bcm/bia/repositories/bia_repository.py` for a complete integration example with the BIA module.

## Support

For issues or questions:
- Check syntax: `python3 -m py_compile shared/history/*.py`
- Review logs: Change tracker logs all operations
- Test detection: Use detect_changes() standalone
