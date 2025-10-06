# Change History Tracking - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Change History System                        │
│                                                                   │
│  Track WHO changed WHAT, WHEN, WHY with field-level precision   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Application Layer                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────┐      ┌────────────────┐      ┌──────────────┐  │
│  │  BIA Service   │      │   Compliance   │      │   Evidence   │  │
│  │                │      │    Service     │      │   Service    │  │
│  └────────┬───────┘      └────────┬───────┘      └──────┬───────┘  │
│           │                       │                      │           │
│           └───────────────────────┼──────────────────────┘           │
│                                   │                                  │
│                                   ▼                                  │
│                    ┌──────────────────────────┐                      │
│                    │  Repository Pattern      │                      │
│                    │  - get(id)               │                      │
│                    │  - update(id, changes)   │                      │
│                    │  - delete(id)            │                      │
│                    └──────────┬───────────────┘                      │
│                               │                                      │
└───────────────────────────────┼──────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│                   Change History Module                               │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     ChangeTracker                             │   │
│  │                                                                │   │
│  │  detect_changes(before, after)                                │   │
│  │    ↓                                                           │   │
│  │    Uses DeepDiff to find field-level changes                  │   │
│  │    Returns: List[FieldChange]                                 │   │
│  │                                                                │   │
│  │  track_changes(entity, before, after, changed_by)             │   │
│  │    ↓                                                           │   │
│  │    1. Detect changes                                           │   │
│  │    2. Create ChangeHistoryModel entries                        │   │
│  │    3. Save snapshot (optional)                                 │   │
│  │    4. Persist to database                                      │   │
│  │                                                                │   │
│  │  get_entity_history(entity_type, entity_id)                   │   │
│  │  get_field_history(entity_type, entity_id, field_name)        │   │
│  │                                                                │   │
│  └────────────────────────┬───────────────────────────────────────┘   │
│                           │                                            │
│  ┌────────────────────────┴───────────────────────────────────────┐  │
│  │                      Data Models                               │  │
│  │                                                                 │  │
│  │  ChangeHistoryModel (SQLAlchemy)                               │  │
│  │  ChangeHistoryEntry (Pydantic)                                 │  │
│  │  FieldChange (Pydantic)                                        │  │
│  │  EntityHistory (Pydantic)                                      │  │
│  │  ChangeType (Enum)                                             │  │
│  │                                                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        PostgreSQL Database                             │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Table: change_history                                        │    │
│  │                                                                │    │
│  │  id                SERIAL PRIMARY KEY                         │    │
│  │  entity_type       VARCHAR(100)      ← BIAProcess, Evidence   │    │
│  │  entity_id         VARCHAR(255)      ← 123, 456               │    │
│  │  tenant_id         VARCHAR(255)      ← tenant_abc             │    │
│  │  change_type       VARCHAR(50)       ← field_update           │    │
│  │  field_name        VARCHAR(255)      ← rto_hours              │    │
│  │  old_value         JSONB             ← 24                     │    │
│  │  new_value         JSONB             ← 12                     │    │
│  │  changed_by        VARCHAR(255)      ← user@example.com       │    │
│  │  changed_at        TIMESTAMP         ← 2025-10-03 15:30:00    │    │
│  │  change_reason     TEXT              ← Risk assessment update │    │
│  │  version_number    INTEGER           ← 5                      │    │
│  │  snapshot          JSONB             ← {full entity state}    │    │
│  │  change_metadata   JSONB             ← {ip, user_agent, ...}  │    │
│  │                                                                │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Indexes (11 total)                                           │    │
│  │                                                                │    │
│  │  - idx_history_entity_type                                    │    │
│  │  - idx_history_entity_id                                      │    │
│  │  - idx_history_tenant_id                                      │    │
│  │  - idx_history_field_name                                     │    │
│  │  - idx_history_changed_by                                     │    │
│  │  - idx_history_changed_at                                     │    │
│  │  - idx_history_version                                        │    │
│  │  - idx_history_entity (entity_type, entity_id)                │    │
│  │  - idx_history_entity_field (entity_type, entity_id, field)   │    │
│  │  - idx_history_tenant_time (tenant_id, changed_at)            │    │
│  │  - idx_history_user_time (changed_by, changed_at)             │    │
│  │                                                                │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Update Flow with Change Tracking

```
User Request
    │
    ▼
┌─────────────────────────┐
│ API Endpoint            │
│ PUT /api/bia/process/123│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Repository.update()     │
│                         │
│ 1. Get current state    │───► before = current.model_dump()
│ 2. Apply updates        │───► updated = apply(changes)
│ 3. Track changes        │───┐
└─────────────────────────┘   │
                              ▼
                    ┌──────────────────────┐
                    │ ChangeTracker        │
                    │                      │
                    │ detect_changes()     │
                    │   ↓                  │
                    │ DeepDiff comparison  │
                    │   ↓                  │
                    │ track_changes()      │
                    │   ↓                  │
                    │ Persist to DB        │
                    └──────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ change_history table │
                    │                      │
                    │ - WHO: changed_by    │
                    │ - WHEN: changed_at   │
                    │ - WHAT: field_name   │
                    │ - FROM: old_value    │
                    │ - TO: new_value      │
                    │ - WHY: change_reason │
                    └──────────────────────┘
```

### 2. History Query Flow

```
User Request
    │
    ▼
┌────────────────────────────────┐
│ GET /api/bia/history/          │
│     processes/123              │
└────────────┬───────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ History API Endpoint            │
│                                 │
│ get_process_history()           │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ ChangeTracker                   │
│                                 │
│ get_entity_history()            │
│   ↓                             │
│ Query change_history table      │
│   ↓                             │
│ Build EntityHistory response    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ EntityHistory Response          │
│                                 │
│ {                               │
│   entity_type: "BIAProcess"     │
│   entity_id: "123"              │
│   current_version: 5            │
│   total_changes: 42             │
│   changes: [...]                │
│ }                               │
└─────────────────────────────────┘
```

## Change Detection Logic

```
DeepDiff Algorithm
    │
    ├─► Values Changed
    │   │
    │   └─► FieldChange(field="rto_hours", old=24, new=12)
    │
    ├─► Dictionary Items Added
    │   │
    │   └─► FieldChange(field="rpo_hours", old=None, new=6)
    │
    └─► Dictionary Items Removed
        │
        └─► FieldChange(field="old_field", old="value", new=None)

Ignore Fields Filter
    │
    └─► Skip: updated_at, version, last_seen, etc.

Serialization
    │
    ├─► datetime → ISO string
    ├─► Enum → value
    ├─► Pydantic → dict
    └─► Other → as-is
```

## Integration Points

### 1. Repository Pattern
```python
class BIARepository:
    async def update(self, id, updates, changed_by, change_reason):
        # Before
        before = await self.get(id)

        # Update
        updated = await self._apply_updates(id, updates)

        # Track
        tracker = ChangeTracker(self.db)
        await tracker.track_changes(...)

        return updated
```

### 2. API Layer
```python
@router.put("/processes/{id}")
async def update_process(
    id: int,
    updates: ProcessUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = BIARepository(db)
    return await repo.update(
        id=id,
        updates=updates.dict(),
        changed_by=current_user.email,
        change_reason=updates.change_reason
    )
```

### 3. History Query
```python
@router.get("/history/processes/{id}")
async def get_history(
    id: int,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    tracker = ChangeTracker(db)
    return await tracker.get_entity_history(
        entity_type="BIAProcess",
        entity_id=str(id),
        tenant_id=tenant_id
    )
```

## Query Patterns

### Common Queries

1. **Get all changes for entity**
   ```sql
   SELECT * FROM change_history
   WHERE entity_type = 'BIAProcess'
     AND entity_id = '123'
     AND tenant_id = 'abc'
   ORDER BY changed_at DESC
   LIMIT 100;
   ```

2. **Get field-specific history**
   ```sql
   SELECT * FROM change_history
   WHERE entity_type = 'BIAProcess'
     AND entity_id = '123'
     AND field_name = 'rto_hours'
     AND tenant_id = 'abc'
   ORDER BY changed_at DESC;
   ```

3. **Get changes by user**
   ```sql
   SELECT * FROM change_history
   WHERE changed_by = 'user@example.com'
     AND tenant_id = 'abc'
   ORDER BY changed_at DESC
   LIMIT 50;
   ```

4. **Get changes in time range**
   ```sql
   SELECT * FROM change_history
   WHERE tenant_id = 'abc'
     AND changed_at BETWEEN '2025-10-01' AND '2025-10-03'
   ORDER BY changed_at DESC;
   ```

## Scalability Considerations

### Performance Optimizations
- **Indexes**: 11 strategic indexes for common queries
- **JSONB**: Efficient storage and GIN indexes possible
- **Async I/O**: Non-blocking database operations
- **Connection pooling**: SQLAlchemy async pool

### Storage Management
- **Retention policy**: Archive old changes
- **Partitioning**: Partition by date for large tables
- **Snapshot toggle**: Disable for high-volume entities
- **Compression**: PostgreSQL TOAST for large JSONB

### Multi-Tenancy
- **Tenant isolation**: All queries filtered by tenant_id
- **Tenant indexes**: Composite indexes include tenant_id
- **Row-level security**: Optional PostgreSQL RLS policies

## Security

### Access Control
- Changes tied to authenticated user (changed_by)
- Tenant isolation prevents cross-tenant access
- Immutable audit trail (no updates/deletes)
- Change reason required for compliance

### Data Protection
- Sensitive fields can be excluded (ignore_fields)
- Passwords never tracked
- PII handled per data protection policies
- Encryption at rest (database level)

## Future Enhancements

1. **Rollback functionality**: Restore entity to previous version
2. **Change approval**: Require approval for sensitive changes
3. **Real-time notifications**: Webhook on critical changes
4. **Compliance reports**: Pre-built audit reports
5. **Change visualization**: UI for diff display
6. **Bulk tracking**: Efficient tracking for imports
7. **Change analytics**: Patterns and insights

## Summary

The Change History system provides:
- ✅ Complete audit trail
- ✅ Field-level precision
- ✅ Multi-tenant isolation
- ✅ High performance
- ✅ Compliance-ready
- ✅ Easy integration
- ✅ Rollback capable
