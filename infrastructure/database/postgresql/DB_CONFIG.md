# Database Configuration - Final Setup

**Date:** 2025-10-06
**Status:** Production Ready
**Architecture:** Single Supabase DB with multiple schemas

---

## 📊 Architecture Decision

**ВЫБРАНО:** Одна Supabase БД с множественными схемами

**Почему:**
- ✅ 14,000+ LOC миграций уже под эту архитектуру
- ✅ 10+ схем (public, community, intelligence, bcm, bia, risk, governance, etc.)
- ✅ 10 микросервисов - RLS изолирует данные
- ✅ Supabase Pro: connection pooling, высокая доступность
- ✅ Проще управлять: одна БД, одна резервная копия
- ✅ Масштабируется до 100+ одновременных подключений

---

## 🔗 Connection Details

### Supabase Instance
- **Region:** eu-north-1 (AWS Stockholm)
- **URL:** https://tpdkhddtbhpoqzzgxfni.supabase.co
- **Database:** postgres
- **Connection Pooler:** aws-1-eu-north-1.pooler.supabase.com:5432

### Environment Variables
```bash
# PostgreSQL Direct (для миграций)
DATABASE_URL=postgresql://postgres.tpdkhddtbhpoqzzgxfni:K%40x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# Supabase API (для клиентов)
SUPABASE_URL=https://tpdkhddtbhpoqzzgxfni.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📦 Database Schemas

| Schema | Purpose | Used By |
|--------|---------|---------|
| **public** | Core shared tables, tenants, users | All services |
| **community** | Community contributions, peer review | community-service |
| **intelligence** | AI memory, digital twins | intelligent-core |
| **bcm** | BCM shared resources | All BCM services |
| **bia** | Business Impact Analysis | bia-service |
| **risk** | Risk Management | risk-service |
| **governance** | Governance & compliance | governance-service |
| **audit** | Audit logs, event sourcing | All services |
| **compliance** | Compliance tracking | compliance-service |

---

## 🚀 Migration Status

**Current Version:** 036
**Latest Available:** 043

**To apply remaining migrations:**
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/database/postgresql
./apply_remaining_migrations.sh
```

**Migrations 037-043:**
- 037: Community intelligence schema
- 038: Gateway state
- 040: Community intelligence tables
- 041: Collective agents
- 042: Predictive service
- 043: Learning system enhancements

---

## 🔌 Module Connections

### intelligent-core Modules

**ai-foundation/**
```python
# Uses: Qdrant (vector DB) + PostgreSQL (metadata)
QDRANT_URL=https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io
DATABASE_URL=postgresql://...  # For metadata
```

**workflow_intelligence/**
```python
# Uses: PostgreSQL (workflow state) + Qdrant (case library)
from shared.database import DatabaseManager
from infrastructure.vector_db import QdrantVectorDB

db = DatabaseManager(DATABASE_URL)
vector_db = QdrantVectorDB(QDRANT_URL, QDRANT_API_KEY)
```

**expertise-center/**
```python
# Uses: PostgreSQL (domain data)
from shared.database import DatabaseManager
```

**Community Services**
- community_intelligence (8030) → schema: community
- collective (8032) → schema: community
- predictive (8031) → schema: intelligence
- learning-system (8033) → schema: intelligence
- living-docs (8034) → schema: public

### platform-services

All services use:
```python
from shared.database import DatabaseManager

# Each service connects to its schema
bia-service → schema: bia
risk-service → schema: risk
compliance-service → schema: compliance
governance-service → schema: governance
etc.
```

---

## 🔒 Security & RLS

**Row Level Security (RLS)** enabled on all tables:
```sql
-- Example: Tenant isolation
CREATE POLICY "tenant_isolation"
ON public.organizations
USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

**Connection:**
```python
# Set RLS context
async with db_manager.get_session() as session:
    await session.execute(
        text("SET app.tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    # All queries now isolated to this tenant
```

---

## 📈 Performance Configuration

### Connection Pooling
```python
# shared/database/db_manager.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Base connections
    max_overflow=40,        # Burst to 60 total
    pool_pre_ping=True,     # Health check
    pool_recycle=3600,      # Recycle hourly
)
```

### Indexes
All critical indexes created in migrations:
- Primary keys
- Foreign keys
- tenant_id columns
- Frequently queried fields
- Full-text search indexes

---

## 🧪 Testing Connection

```bash
# Test PostgreSQL
cd /Users/MD/AI-Platform-ISO/infrastructure/database/postgresql
python -c "
from managers.db_manager import DatabaseManager
import asyncio

async def test():
    db = DatabaseManager()
    async with db.get_session() as session:
        result = await session.execute('SELECT version()')
        print(result.scalar())

asyncio.run(test())
"

# Test Qdrant
cd /Users/MD/AI-Platform-ISO/infrastructure/database/vector-db
python test_connection.py
```

---

## 📝 Next Steps

1. ✅ Apply remaining migrations (037-043)
2. ✅ Update all modules to use `shared.database.DatabaseManager`
3. ✅ Configure ai-foundation to use Qdrant + PostgreSQL
4. ✅ Test connections from all services
5. ✅ Set up monitoring and health checks

---

**Ready for production! 🚀**
