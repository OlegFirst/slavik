# Database Infrastructure - 3-Layer Architecture

## Structure

```
database/
├── system/              # Level 1: AI & Intelligence data
│   ├── migrations/      # System database migrations
│   ├── schemas/         # AI decision logs, knowledge graph
│   └── connection.py    # System DB connection manager
│
├── platform/            # Level 2: Platform & Coordination
│   ├── migrations/      # Platform database migrations
│   ├── schemas/         # Auth, coordination, events
│   └── connection.py    # Platform DB connection manager
│
├── business/            # Level 3: User/BCM data
│   ├── migrations/      # Business database migrations
│   ├── schemas/         # BIA, Risk, Governance, etc.
│   └── connection.py    # Business DB connection manager
│
└── managers/            # Database managers
    ├── connection_pool.py
    ├── rls_manager.py
    ├── migration_runner.py
    └── health_check.py
```

## Setup

### 1. Create 3 Supabase Projects

**System Database:**
- Name: `bcm-platform-system`
- Region: US (can be any)
- Plan: Free tier OK

**Platform Database:**
- Name: `bcm-platform-platform`
- Region: US (same as system)
- Plan: Free tier OK

**Business Database:**
- Name: `bcm-platform-business`
- Region: Customer's region (for data residency)
- Plan: Pro (for RLS and better performance)

### 2. Environment Variables

```bash
# System Database (Level 1)
SYSTEM_DATABASE_URL=postgresql://...
SYSTEM_DB_ANON_KEY=...
SYSTEM_DB_SERVICE_KEY=...

# Platform Database (Level 2)
PLATFORM_DATABASE_URL=postgresql://...
PLATFORM_DB_ANON_KEY=...
PLATFORM_DB_SERVICE_KEY=...

# Business Database (Level 3)
BUSINESS_DATABASE_URL=postgresql://...
BUSINESS_DB_ANON_KEY=...
BUSINESS_DB_SERVICE_KEY=...
```

### 3. Run Migrations

```bash
# System DB
python infrastructure/database/managers/migration_runner.py --db system

# Platform DB
python infrastructure/database/managers/migration_runner.py --db platform

# Business DB
python infrastructure/database/managers/migration_runner.py --db business
```

## Access Control

| Component                | System DB | Platform DB | Business DB |
|-------------------------|-----------|-------------|-------------|
| Intelligent Core        | ✅ R/W    | ❌          | 🟡 Read-only (via Coord) |
| Coordination Center     | ❌        | ✅ R/W      | ✅ R/W      |
| Execution Engine        | ❌        | 🟡 Read-only | ✅ R/W      |
| API Gateway             | ❌        | ✅ Read-only | ❌          |
| Frontend Apps           | ❌        | ❌          | ❌ (via API only) |

## Backup Schedule

- **System DB**: Every hour (critical AI data)
- **Platform DB**: Every 6 hours
- **Business DB**: Every 4 hours

## Security

- All connections use SSL/TLS
- RLS enabled on all tables (except System DB)
- Encryption at rest enabled
- Connection pooling with max connections limit
- Query timeout: 30s default
