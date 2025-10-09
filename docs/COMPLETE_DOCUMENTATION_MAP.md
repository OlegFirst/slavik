# AI-Platform-ISO: Complete Documentation Map

**Version**: 2.0.0
**Date**: 2025-10-09
**Status**: Production Ready

---

## Overview

This document provides a complete map of all documentation across the AI-Platform-ISO project, including active documentation, archived historical materials, and infrastructure tools.

**Total Documentation Assets**:
- Active Documentation: 180+ professional documents
- Archived Documentation: 111 historical documents (13 categories)
- Comprehensive Platform Docs: 7 capability documents (352 KB)
- Infrastructure Tools: 8 catalogs + 30+ automation scripts
- Total Size: ~2.5 GB across all documentation

---

## 1. Active Documentation (`/docs/`)

### Platform-Level Documentation

| Document | Size | Purpose | Key Sections |
|----------|------|---------|--------------|
| **INDEX.md** | 9.6K | Master navigation | Role-based access, Service catalog |
| **EXECUTIVE_SUMMARY.md** | 16K | Theory of Change | Problem/Solution, Business impact |
| **README.md** | 15K | Platform overview | Architecture, Quick start |
| **GETTING_STARTED.md** | 20K | Installation guide | 45-60 min setup, First workflow |
| **DEPLOYMENT_GUIDE.md** | 27K | Production deployment | Docker/K8s, Security, HA, DR |
| **STANDARDS_COMPLIANCE.md** | 28K | ISO compliance | ISO 22301:2019, 27001:2022, GDPR |
| **ARCHITECTURE.md** | 73K | C4 Model architecture | 5 layers, Tech stack, Patterns |
| **API_REFERENCE.md** | 40K | API documentation | 150+ endpoints, Examples |

**Total**: 228 KB, 8 files

---

## 2. Comprehensive Platform Docs (`/comprehensive-platform-docs/`)

### AI Capabilities & Scenarios

These documents contain detailed technical specifications of platform capabilities and 570+ usage scenarios.

| Document | Size | Content | RAG Priority |
|----------|------|---------|--------------|
| **AI_FOUNDATION_CAPABILITIES.md** | 45KB | LLM routing, RAG pipeline, ML predictions, Self-learning | HIGH |
| **AI_ORCHESTRATION_CAPABILITIES.md** | 38KB | Cognitive Loop (6 steps), Memory systems (4 layers), Safety | HIGH |
| **DOMAIN_EXPERTISE_CAPABILITIES.md** | 42KB | 14 AI specialists, Collective intelligence, Case library (347+) | HIGH |
| **PREDICTIVE_INTELLIGENCE_CAPABILITIES.md** | 35KB | Timeline prediction, Certification forecasting, Event intelligence | HIGH |
| **INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md** | 52KB | 18 infrastructure patterns (Event Bus, Saga, Circuit Breaker) | HIGH |
| **BUSINESS_PROCESS_SCENARIOS_COMPLETE.md** | 78KB | 10 end-to-end scenarios (Certification journey, Incident response) | MAXIMUM |
| **ALL_USAGE_SCENARIOS_CATALOG.md** | 112KB | 570+ usage scenarios (Platform services, Intelligent core, Infrastructure) | MAXIMUM |
| **MASTER_INDEX.md** | 24KB | RAG integration guide, Search strategy, Embedding configuration | HIGH |

**Total**: 426 KB, 8 files

**Key Content**:
- 14 Domain AI Specialists
- 570+ Usage Scenarios
- 18 Infrastructure Patterns
- 10 End-to-End Business Flows
- 347+ Collective Intelligence Cases
- Complete RAG Integration Guide

**Status**: Ready for Qdrant/RAG integration

---

## 3. Infrastructure Documentation (`/infrastructure/`)

### Layer Overview

| Document | Size | Purpose |
|----------|------|---------|
| **infrastructure/README.md** | 18KB | Infrastructure layer overview, Component catalog |
| **infrastructure/OVERVIEW.md** | - | Infrastructure architecture |
| **infrastructure/QUICK_REFERENCE.md** | - | Quick reference guide |

### Component Documentation

Each infrastructure component has dedicated documentation:

```
infrastructure/
├── eventbus/                  # Event-driven messaging
│   ├── README.md             # EventBus overview
│   └── docs/                 # Technical specs
├── database/                  # PostgreSQL + Supabase
│   ├── README.md
│   └── migrations/
├── observability/            # Monitoring stack
│   ├── README.md
│   ├── prometheus/
│   └── grafana/
├── security/                 # Security infrastructure
│   ├── README.md
│   └── vault/
├── gateway/                  # API Gateway
│   └── README.md
└── tools/                    # Automation tools (see section 5)
    └── README.md
```

---

## 4. Module Documentation

### Intelligent Core (`/intelligent-core/`)

14 AI modules, each with complete documentation package:

```
module-name/
├── README.md                 # Professional overview
└── docs/
    ├── ARCHITECTURE.md       # Module architecture
    ├── TECHNICAL_SPECIFICATION.md
    ├── BUSINESS_LOGIC.md     # Core algorithms
    ├── API.md                # Module API
    ├── INTEGRATION.md        # Integration patterns
    └── DEPLOYMENT.md         # Deployment guide
```

**Modules**:
1. **ai-foundation** - LLM routing, RAG, ML models
2. **workflow_intelligence** - Temporal workflows, Orchestration
3. **expertise-center** - 14 domain specialists
4. **collective** - Collective intelligence, Case library
5. **predictive** - ML predictions, Forecasting
6. **event-intelligence** - Event processing, Pattern learning
7. **orchestration** - Cognitive loop, Decision engine
8. **community-intelligence** - Community learning
9. **workflow-engine** - Workflow execution
10. **ai-workflow-optimizer** - Workflow optimization
11. **devops-ai/** - AI DevOps tools
    - project-agent
    - mio-manager
    - agent-router
12. **living-docs** - Living documentation engine
13. **simulation/** - Digital twin, Scenario generation
14. **содоо** - BCM control dashboard

**Total**: ~98 documents (14 modules × 7 docs)

---

### Platform Services (`/platform-services/`)

12 BCM services, each with documentation package:

```
service-name/
├── README.md                 # Service overview
└── docs/
    ├── TECHNICAL_SPECIFICATION.md
    ├── API.md
    ├── BUSINESS_LOGIC.md
    ├── INTEGRATION.md
    └── DEPLOYMENT.md
```

**Services** (mapped to ISO 22301 clauses):

| Service | ISO Clause | Purpose |
|---------|------------|---------|
| **bia-service** | 8.2 | Business Impact Analysis |
| **risk-service** | 8.3 | Risk Assessment & Treatment |
| **compliance-service** | 9.1 | ISO 22301 Compliance Monitoring |
| **planning-service** | 8.4 | BC Plan Development & Journey Planning |
| **response-service** | 8.4 | Incident Response & Crisis Management |
| **documents-service** | 7.5 | Document Management & Living Docs |
| **governance-service** | 5.0 | Leadership & Governance |
| **validation-service** | 8.5 | Exercise & Testing |
| **learning-service** | 7.3 | Training & Awareness |
| **bcm-coordination-service** | - | Cross-service coordination |
| **community-service** | - | Community & Knowledge sharing |
| **monitoring** | 9.0 | Performance Monitoring |

**Total**: ~72 documents (12 services × 6 docs)

---

## 5. Infrastructure Tools (`/infrastructure/tools/`)

### Documentation Catalogs

| Document | Size | Purpose |
|----------|------|---------|
| **README.md** | 1.8KB | Tools overview |
| **TOOLS_CATALOG_INDEX.md** | 51KB | Complete tool catalog index |
| **TOOLS_COMPREHENSIVE_CATALOG.md** | 37KB | Detailed tool descriptions |
| **TOOLS_QUICK_REFERENCE.md** | 9.2KB | Quick reference guide |
| **TOOLS_INTEGRATION_COMPLETE.md** | 15KB | Integration patterns |
| **AUTOMATION_PLAN.md** | 30KB | Automation strategy |
| **GITHUB_ACTIONS_CONSTRAINTS.md** | 27KB | CI/CD constraints |
| **WEB_UI_GUIDE.md** | 16KB | UI development guide |

**Total**: 187 KB, 8 files

### Tool Categories

#### 5.1 Analyzers (`analyzers/`)

**Purpose**: Code analysis, dependency mapping, metrics discovery

- `dependency_validator.py` - Validate service dependencies
- `dependency_mapper.py` - Map service dependency graph
- `dependency_reconciler.py` - Reconcile dependency conflicts
- `discover_services.py` - Auto-discover services
- `business_logic_mapper.py` - Map business logic flows
- `ast_analyzer.py` - Python AST analysis
- `api_mapper.py` - Map API endpoints
- `metrics_discovery.py` - Discover Prometheus metrics
- `module_scanner.py` - Scan module structure
- `generate_improved_compose.py` - Generate docker-compose files

**Total**: 10 Python analyzers

#### 5.2 Documentation Generators (`doc-generators/`)

**Purpose**: Auto-generate documentation from code

- `documentation_generator.py` - Generate service docs
- `event_catalog_generator.py` - Generate event catalog
- `test_generator.py` - Generate test documentation
- `ui_blueprint_gen.py` - Generate UI blueprints
- `prometheus_config_generator.py` - Generate Prometheus config

**Total**: 5 Python generators

#### 5.3 Batch Update Scripts

**Purpose**: Bulk documentation updates

- `batch-update-docs.sh` - Update all documentation
- `batch-update-platform-services.sh` - Update service docs
- `batch-update-all-platform-services.sh` - Update all services
- `batch-update-infrastructure.sh` - Update infrastructure docs
- `update-docs.sh` - General doc updater
- `archive-old-docs.sh` - Archive old documentation
- `check-docs-freshness.sh` - Check doc freshness
- `validate_docs.sh` - Validate documentation quality

**Total**: 8 bash scripts

#### 5.4 Docker Management (`docker-management/`)

- `docker_manager.py` - Docker container management
- Helper scripts for container orchestration

#### 5.5 Auto-Generated Tools (`auto-generated/`)

- API specifications
- OpenAPI/AsyncAPI schemas
- Service catalogs

---

## 6. Archived Documentation (`/_archive/docs-old-backup/`)

### Archive Structure

Historical documentation preserved for reference and context recovery.

| Section | Size | Files | Purpose |
|---------|------|-------|---------|
| **ai-capabilities/** | 272KB | 9 files | Historical AI capability docs |
| **analysis/** | 40KB | 3 files | Event system analysis |
| **api/** | 72KB | 2 files | API specifications (OpenAPI, AsyncAPI) |
| **architecture/** | 428KB | 18 files | C4 Model, Architecture visualizations |
| **business-analysis/** | 60KB | 3 files | Business flows analysis |
| **deployment/** | 68KB | 3 files | Deployment guides |
| **executive/** | 68KB | 5 files | Executive summaries, Decision records |
| **guides/** | 284KB | 9 files | User guides, Quick references |
| **integration/** | 124KB | 7 files | Integration documentation |
| **knowledge-library/** | 448KB | 8 files | BCM knowledge base (WHO, NIST, ISO flows) |
| **modules/** | 216KB | - | Old module documentation |
| **reports/** | 8KB | - | Historical reports |
| **testing/** | 8KB | - | Testing documentation |

**Total**: ~2.1 MB, 111 files across 13 categories

**Status**: Preserved for historical reference, not for active use

---

## 7. Project Documentation (`/doc-project/`)

### Special Purpose Documentation

- **FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md** - Complete architecture spec
- **TASK_*.md** - Project task documentation
- Historical project planning documents

---

## 8. Documentation Usage Guide

### For Different Roles

#### Developers
**Start here**:
1. `/docs/README.md` - Platform overview
2. `/docs/ARCHITECTURE.md` - Architecture deep dive
3. `/docs/API_REFERENCE.md` - API endpoints
4. Module-specific `/intelligent-core/{module}/docs/`

#### DevOps Engineers
**Start here**:
1. `/docs/DEPLOYMENT_GUIDE.md` - Production deployment
2. `/infrastructure/README.md` - Infrastructure overview
3. `/infrastructure/tools/TOOLS_CATALOG_INDEX.md` - Automation tools

#### Business Analysts
**Start here**:
1. `/docs/EXECUTIVE_SUMMARY.md` - Business case
2. `/comprehensive-platform-docs/ALL_USAGE_SCENARIOS_CATALOG.md` - 570+ scenarios
3. `/comprehensive-platform-docs/BUSINESS_PROCESS_SCENARIOS_COMPLETE.md` - End-to-end flows

#### ISO Auditors
**Start here**:
1. `/docs/STANDARDS_COMPLIANCE.md` - ISO 22301:2019 mapping
2. `/platform-services/{service}/docs/` - Service-level compliance
3. `/docs/API_REFERENCE.md` - ISO clause mappings

#### AI/ML Engineers
**Start here**:
1. `/comprehensive-platform-docs/AI_FOUNDATION_CAPABILITIES.md` - LLM, RAG, ML
2. `/comprehensive-platform-docs/AI_ORCHESTRATION_CAPABILITIES.md` - Cognitive loop
3. `/intelligent-core/ai-foundation/docs/` - AI implementation details

#### System Architects
**Start here**:
1. `/docs/ARCHITECTURE.md` - Complete C4 Model
2. `/comprehensive-platform-docs/INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md` - 18 patterns
3. `/_archive/docs-old-backup/architecture/` - Historical architecture decisions

---

## 9. Documentation for Planning & UI Development

### Planning Tools

**Location**: `/infrastructure/tools/`

**Key Resources**:
- **TOOLS_CATALOG_INDEX.md** (51KB) - Complete catalog of all automation tools
- **AUTOMATION_PLAN.md** (30KB) - Platform automation strategy
- **WEB_UI_GUIDE.md** (16KB) - UI development guidelines

**Analyzers for Planning**:
```bash
# Discover all services
python infrastructure/tools/analyzers/discover_services.py

# Map dependencies
python infrastructure/tools/analyzers/dependency_mapper.py

# Map API endpoints
python infrastructure/tools/analyzers/api_mapper.py

# Map business logic
python infrastructure/tools/analyzers/business_logic_mapper.py

# Discover metrics
python infrastructure/tools/analyzers/metrics_discovery.py
```

### UI Development Resources

**Documentation**:
- `/infrastructure/tools/WEB_UI_GUIDE.md` - Complete UI development guide
- `/docs/API_REFERENCE.md` - 150+ API endpoints for frontend integration
- `/comprehensive-platform-docs/ALL_USAGE_SCENARIOS_CATALOG.md` - User workflows

**Auto-Generated UI Specs**:
```
infrastructure/tools/auto-generated/
├── ui-specs/
│   ├── dashboard-wireframes/
│   ├── component-catalog/
│   └── api-integration-examples/
```

**UI Generation**:
```bash
# Generate UI blueprints
python infrastructure/tools/doc-generators/ui_blueprint_gen.py
```

### Architecture Mapping Tools

**For Creating System Maps**:

1. **Service Discovery**:
   ```bash
   python infrastructure/tools/analyzers/discover_services.py > services.json
   ```

2. **Dependency Mapping**:
   ```bash
   python infrastructure/tools/analyzers/dependency_mapper.py > dependencies.json
   ```

3. **API Mapping**:
   ```bash
   python infrastructure/tools/analyzers/api_mapper.py > api-map.json
   ```

4. **Business Logic Mapping**:
   ```bash
   python infrastructure/tools/analyzers/business_logic_mapper.py > logic-map.json
   ```

**Output**: JSON files ready for visualization in:
- Mermaid diagrams
- D3.js visualizations
- Architecture decision records
- UI component planning

### Complete Platform Map Generation

**Location**: `/infrastructure/tools/analyzers/`

**Usage**:
```bash
# Generate complete platform map
cd /Users/MD/AI-Platform-ISO/infrastructure/tools

# 1. Discover all services
python analyzers/discover_services.py --output json > platform-map.json

# 2. Map all dependencies
python analyzers/dependency_mapper.py --include-external >> platform-map.json

# 3. Map all APIs
python analyzers/api_mapper.py --include-events >> platform-map.json

# 4. Map business logic
python analyzers/business_logic_mapper.py --include-workflows >> platform-map.json

# 5. Validate everything
python analyzers/dependency_validator.py platform-map.json
```

**Output Format**: Structured JSON suitable for:
- Frontend visualization
- Planning dashboards
- Architecture documentation
- Dependency analysis

---

## 10. Quick Navigation

### Most Important Documents

**For Getting Started**:
1. `/docs/README.md` - Start here
2. `/docs/GETTING_STARTED.md` - Installation (45-60 min)
3. `/docs/ARCHITECTURE.md` - System understanding

**For Development**:
1. `/docs/API_REFERENCE.md` - 150+ endpoints
2. `/intelligent-core/{module}/docs/TECHNICAL_SPECIFICATION.md`
3. `/platform-services/{service}/docs/API.md`

**For Usage Examples**:
1. `/comprehensive-platform-docs/ALL_USAGE_SCENARIOS_CATALOG.md` - 570+ scenarios
2. `/comprehensive-platform-docs/BUSINESS_PROCESS_SCENARIOS_COMPLETE.md` - 10 flows
3. `/docs/GETTING_STARTED.md` - First workflow example

**For Compliance**:
1. `/docs/STANDARDS_COMPLIANCE.md` - ISO 22301:2019
2. `/platform-services/compliance-service/docs/` - Compliance implementation

**For AI/ML**:
1. `/comprehensive-platform-docs/AI_FOUNDATION_CAPABILITIES.md`
2. `/comprehensive-platform-docs/AI_ORCHESTRATION_CAPABILITIES.md`
3. `/intelligent-core/ai-foundation/docs/`

**For Infrastructure**:
1. `/infrastructure/README.md`
2. `/comprehensive-platform-docs/INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md`
3. `/infrastructure/tools/TOOLS_CATALOG_INDEX.md`

**For Planning & UI**:
1. `/infrastructure/tools/TOOLS_CATALOG_INDEX.md` - All automation tools
2. `/infrastructure/tools/WEB_UI_GUIDE.md` - UI development
3. `/docs/ARCHITECTURE.md` - System architecture for planning

---

## 11. Documentation Statistics

### By Category

| Category | Files | Size | Status |
|----------|-------|------|--------|
| Platform docs | 8 | 228 KB | ✅ Production |
| Comprehensive docs | 8 | 426 KB | ✅ Production |
| Infrastructure docs | 15+ | 187 KB | ✅ Production |
| Intelligent core | ~98 | ~2 MB | ✅ Production |
| Platform services | ~72 | ~1.5 MB | ✅ Production |
| Tools catalog | 8 | 187 KB | ✅ Production |
| Archive | 111 | 2.1 MB | 📦 Archive |
| **TOTAL** | **~320** | **~6.5 MB** | **✅ Complete** |

### Quality Metrics

- ✅ Zero emojis in production docs
- ✅ Zero Russian text in production docs
- ✅ 100% English professional documentation
- ✅ ISO/IEC/IEEE 26514:2022 compliant
- ✅ Complete API documentation (150+ endpoints)
- ✅ Complete architecture documentation (C4 Model)
- ✅ Complete compliance mapping (ISO 22301:2019)
- ✅ 570+ usage scenarios documented
- ✅ 18 infrastructure patterns documented
- ✅ 14 AI specialists documented

---

## 12. Maintenance

### Documentation Updates

**Automated**:
```bash
# Update all documentation
/infrastructure/tools/batch-update-docs.sh

# Validate documentation
/infrastructure/tools/validate_docs.sh

# Check freshness
/infrastructure/tools/check-docs-freshness.sh
```

**Manual**:
- Platform docs: Update `/docs/` when major features added
- Module docs: Update when module architecture changes
- Service docs: Update when API contracts change
- Comprehensive docs: Update when new capabilities added

### Version Control

- Documentation version tracks platform version
- Current version: **2.0.0**
- Last major update: 2025-10-09
- Next scheduled review: Quarterly

---

## Contact & Support

**Documentation Issues**: Create issue in project repository
**Documentation Requests**: Contact platform team
**Architecture Questions**: See `/docs/ARCHITECTURE.md`
**API Questions**: See `/docs/API_REFERENCE.md`

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-10-09
**Version**: 2.0.0
**Maintained By**: AI-Platform-ISO Core Team
