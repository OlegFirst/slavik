# EventBus Database Migration Fix

## Problem Statement

The EventBus service was failing to start on existing deployments that had an `events` table without the `event_id` column. This happened because:

1. **Old deployments**: Had `events` table created without `event_id` column
2. **EventBus service**: Tried to create `CREATE UNIQUE INDEX idx_event_id ON events(event_id)`
3. **Result**: PostgreSQL error - column `event_id` does not exist

## Root Cause

The EventBus service initialization code assumed the `event_id` column always exists when creating indexes, but existing databases might have been created with an older schema that lacked this column.

## Solution Implemented

### Migration Logic

Added conditional column creation using PostgreSQL DO blocks:

```sql
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'events' AND column_name = 'event_id'
    ) THEN
        ALTER TABLE events ADD COLUMN event_id VARCHAR(255) UNIQUE;
    END IF;
END $$;
```

### Implementation Locations

1. **EventBus Service** (`backend/eventbus/main.py`):
   - Added migration logic in the lifespan startup
   - Executes before index creation
   - Ensures idempotent operation

2. **Init Script** (`scripts/init-postgres.sh`):
   - Added same migration logic for consistency
   - Handles fresh database installations
   - Provides fallback for manual database initialization

### Execution Flow

```
EventBus Startup
    ↓
Create Table (if not exists)
    ↓
Check for event_id column
    ↓
Add column if missing ← MIGRATION STEP
    ↓
Create indexes (now safe)
    ↓
Service ready
```

## Backward Compatibility

| Scenario | Before Fix | After Fix |
|----------|------------|-----------|
| Fresh installation | ✅ Works | ✅ Works |
| Existing DB with event_id | ✅ Works | ✅ Works |
| Existing DB without event_id | ❌ Fails | ✅ Works (migrated) |

## Testing

### Test Coverage

- **Unit Tests** (`tests/test_eventbus_migration.py`):
  - SQL syntax validation
  - Migration logic verification
  - Idempotency testing

- **Integration Tests**:
  - Old database simulation
  - New database verification
  - Error scenario coverage

### Running Tests

```bash
# Run migration-specific tests
python -m pytest tests/test_eventbus_migration.py -v

# Run all tests to ensure no regression
python -m pytest tests/test_simple.py -v
```

## Deployment Considerations

### For Existing Deployments

1. **No manual intervention required** - migration runs automatically
2. **Zero downtime** - column addition is non-blocking
3. **Idempotent** - safe to run multiple times
4. **No data loss** - only adds missing schema elements

### For New Deployments

1. **No change in behavior** - works as before
2. **Migration logic** - runs but skips column addition
3. **Consistent schema** - ensures uniform database structure

## Error Handling

The migration logic handles common error scenarios:

- **Permission issues**: Uses same DB user as EventBus service
- **Column exists**: Skips addition (idempotent)
- **Constraint conflicts**: Uses IF NOT EXISTS patterns
- **Transaction safety**: Each step is independently safe

## Monitoring

### Success Indicators

- EventBus service starts without errors
- Health endpoint responds successfully
- Database indexes are created properly
- Event publishing/retrieval works normally

### Failure Indicators

- Service fails to start with database errors
- Missing indexes in database schema
- Event operations fail with column errors

## Future Maintenance

### Best Practices

1. **Always use conditional DDL** - `IF NOT EXISTS`, `IF EXISTS`
2. **Test migrations thoroughly** - both old and new schemas
3. **Document schema changes** - maintain migration history
4. **Version database schema** - consider Alembic for complex migrations

### Schema Evolution

For future schema changes:

1. Add migration logic before using new columns
2. Use same pattern: check existence → add if missing
3. Update both service code and init scripts
4. Add comprehensive tests for new migration

## References

- **Issue**: [P1] Missing migration for existing events tables
- **Files Modified**:
  - `backend/eventbus/main.py`
  - `scripts/init-postgres.sh`
  - `tests/test_eventbus_migration.py`
- **PostgreSQL Documentation**: information_schema.columns
- **Testing Framework**: pytest with asyncio support