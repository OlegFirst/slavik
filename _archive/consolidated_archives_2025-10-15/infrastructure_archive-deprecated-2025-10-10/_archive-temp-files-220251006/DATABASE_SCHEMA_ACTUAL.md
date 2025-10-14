# PostgreSQL Database Schema - Actual State

**Date:** 2025-10-07
**Database:** PostgreSQL (Supabase)
**Migrations Applied:** 43/43
**Total Schemas:** 29

## Schema Inventory

### Core Platform (6 schemas)

| Schema | Purpose | Status |
|--------|---------|--------|
| **public** | Core tables, tenants, users, organizations | Active |
| **core** | Core platform functionality | Active |
| **core_auth** | Core authentication tables | Active |
| **auth** | Supabase Auth (built-in) | System |
| **extensions** | PostgreSQL extensions | System |
| **graphql** | PostgREST GraphQL | System |
| **graphql_public** | Public GraphQL endpoints | System |

### BCM Business Modules (6 schemas)

| Schema | Purpose | Service |
|--------|---------|---------|
| **bcm** | BCM shared resources | All BCM services |
| **bia** | Business Impact Analysis | bia-service |
| **risk** | Risk Management | risk-service |
| **governance** | Governance & compliance | governance-service |
| **compliance** | Compliance tracking | compliance-service |
| **validation** | Validation & KPIs | validation-service |

### Intelligent Core (6 schemas)

| Schema | Purpose | Service |
|--------|---------|---------|
| **intelligence** | AI memory, digital twins | intelligent-core |
| **workflow_intelligence** | Workflow orchestration | workflow_intelligence |
| **domain_intelligence** | Domain-specific AI | expertise-center |
| **learning** | Learning system | learning-service |
| **workflow** | Workflow engine | workflow services |
| **community** | Community contributions | community-service |

### Additional Services (5 schemas)

| Schema | Purpose | Service |
|--------|---------|---------|
| **response** | Incident response | response-service |
| **simulation** | Digital twin simulations | simulation services |
| **portal** | User portal | portal UI |
| **marketplace** | Template marketplace | marketplace |
| **seh** | System event handling | Unknown |

### System/Infrastructure (6 schemas)

| Schema | Purpose | Type |
|--------|---------|------|
| **vault** | HashiCorp Vault integration | Infrastructure |
| **audit** | Audit logs, event sourcing | Infrastructure |
| **storage** | Supabase Storage (built-in) | System |
| **realtime** | Supabase Realtime (built-in) | System |
| **extensions** | PostgreSQL extensions | System |
| **graphql_public** | Public GraphQL | System |

## Missing from Old Documentation

These schemas exist in database but were not documented:

1. **workflow_intelligence** - Major intelligent-core component
2. **learning** - Learning system schema
3. **simulation** - Digital twin data
4. **portal** - Portal functionality
5. **marketplace** - Template marketplace
6. **vault** - Vault integration
7. **auth** - Supabase auth (system)
8. **domain_intelligence** - Domain AI
9. **response** - Incident response
10. **workflow** - Workflow engine
11. **seh** - System event handling
12. **core** - Core platform
13. **core_auth** - Core auth
14. **storage** - Supabase storage
15. **realtime** - Supabase realtime
16. **graphql** - GraphQL endpoint
17. **graphql_public** - Public GraphQL

## Schema Not in Database

Documented but missing:
- **documents** - Document management (needs migration or rename)

## Supabase System Schemas

These are Supabase built-in:
- auth
- storage
- realtime
- graphql
- graphql_public
- extensions

## Migration History

Latest migrations (036-043):
- 036: Policy optimizations
- 037: Community intelligence
- 038: Gateway state
- 040: Community intelligence tables
- 041: Collective agents
- 042: Predictive service
- 043: Learning system enhancements

## Recommendations

### Immediate
1. Update SERVICE_SPEC.md with all 29 schemas
2. Document purpose of each schema
3. Map schemas to services
4. Identify orphaned schemas

### Investigation Required
- **seh** schema - Unknown purpose, needs investigation
- **documents** schema - Should exist, check if renamed or merged

### Cleanup Candidates
- Schemas without clear ownership
- Deprecated schemas from old migrations
- Test/development schemas in production

## Schema Ownership Matrix

| Service | Schemas Used | Count |
|---------|--------------|-------|
| intelligent-core | intelligence, workflow_intelligence, domain_intelligence, learning, workflow, community | 6 |
| BCM services | bcm, bia, risk, governance, compliance, validation | 6 |
| Response/Simulation | response, simulation | 2 |
| Portal/Marketplace | portal, marketplace | 2 |
| Infrastructure | vault, audit, core, core_auth | 4 |
| Supabase (system) | auth, storage, realtime, graphql, graphql_public, extensions | 6 |
| Unknown | seh | 1 |

## Next Actions

1. Complete schema documentation
2. Audit table counts per schema
3. Document schema dependencies
4. Create schema changelog
5. Add schema verification to CI/CD

---

**Documentation Status:** Updated to match reality
**Verified:** 2025-10-07
**Next Audit:** After next migration batch
