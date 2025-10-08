# DEPRECATED: Unified Database Gateway

**Status:** ⛔ DEPRECATED as of 2025-10-08
**Replaced By:** `/infrastructure/database/` - Intelligent Database Management Platform

---

## Why Deprecated?

This component has been **replaced by a superior architecture**:

### Old Approach (This Gateway):
- Manual CRUD API over HTTP
- Multi-database support (Odoo, MongoDB - unused)
- No monitoring
- No AI integration
- No security checks
- HTTP overhead on every query

### New Approach (Intelligent DB Management):
- Direct SQLAlchemy access via unified entry point
- Automatic query monitoring
- AI-powered optimization
- Built-in security (RLS, SQL injection detection)
- Managed by AI Orchestrator
- Zero HTTP overhead

---

## Migration Guide

### Before (Old Gateway):

```python
# HTTP request to gateway
response = await httpx.post(
    "http://localhost:8051/database/execute",
    json={
        "database": "postgres",
        "operation": "select",
        "table": "organizations",
        "where": {"id": "123"}
    }
)
data = response.json()
```

### After (New System):

```python
# Direct database access
from infrastructure.database import get_db_session
from sqlalchemy import select
from models import Organization

async with get_db_session() as session:
    result = await session.execute(
        select(Organization).where(Organization.id == "123")
    )
    org = result.scalar_one()
```

**Benefits:**
- ✅ Faster (no HTTP)
- ✅ Type-safe (SQLAlchemy models)
- ✅ Automatically monitored by DB Intelligence
- ✅ RLS automatically applied
- ✅ AI optimization suggestions

---

## Replacement Services

| Old Gateway Feature | New System Equivalent |
|---------------------|----------------------|
| `POST /database/execute` | `from infrastructure.database import get_db_session` |
| `GET /health/databases` | `GET http://localhost:8050/health` |
| Multi-database support | Use appropriate clients directly |
| Odoo integration | Not needed (using Supabase) |
| MongoDB support | Not needed |
| Redis operations | `from infrastructure.database import get_redis_client` |

---

## Timeline

- **Created:** September 2024
- **Deprecated:** October 8, 2025
- **Removal:** Will be removed in November 2025

---

## New System Documentation

See:
- `/infrastructure/database/README.md` - Overview
- `/infrastructure/database/intelligence/README.md` - Intelligence Service
- `/infrastructure/database/ARCHITECTURE_DECISION.md` - Architecture reasoning

---

**Do not use this gateway for new development.**
**Migrate existing code to the new unified system.**
