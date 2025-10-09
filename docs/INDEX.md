# AI-Platform-ISO Documentation Index

**Document Type:** Master Documentation Index
**Purpose:** Central navigation for all platform documentation
**Version:** 2.0.0
**Last Updated:** 2025-10-09

---

## Quick Navigation

### 🚀 NEW: System BCM Self-Application
- [**System BCM Launch**](/SYSTEM_BCM_LAUNCH.md) - Production-ready BCM self-application service (Port 8050)
  - 4 system scenarios (BIA, Risk, Recovery, Resources)
  - Auto-recovery procedures (7 automated)
  - Real-time monitoring (Prometheus + Grafana)
  - Practice learning engine
  - **Status**: ✅ Ready to launch!

### Getting Started
- [Platform Overview](./README.md) - What is AI-Platform-ISO and key capabilities
- [Executive Summary](./EXECUTIVE_SUMMARY.md) - Business value and theory of change
- [Getting Started Guide](./GETTING_STARTED.md) - Installation and first steps
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [Standards Compliance](./STANDARDS_COMPLIANCE.md) - ISO 22301 and related standards
- [Architecture](./ARCHITECTURE.md) - Complete system architecture
- [API Reference](./API_REFERENCE.md) - Unified API documentation

### Complete Documentation Map
- [Complete Documentation Map](./COMPLETE_DOCUMENTATION_MAP.md) - Master map of ALL documentation (320+ files, 6.5 MB)
  - Platform docs, Comprehensive capabilities, Infrastructure tools
  - Archived documentation (111 files), RAG integration guides
  - Planning tools, UI development resources, Architecture mapping

### AI Capabilities & Usage Scenarios
- [Comprehensive Platform Docs](/comprehensive-platform-docs/) - 570+ usage scenarios, AI capabilities
  - [All Usage Scenarios Catalog](/comprehensive-platform-docs/ALL_USAGE_SCENARIOS_CATALOG.md) - 570+ scenarios
  - [AI Foundation Capabilities](/comprehensive-platform-docs/AI_FOUNDATION_CAPABILITIES.md) - LLM, RAG, ML
  - [AI Orchestration Capabilities](/comprehensive-platform-docs/AI_ORCHESTRATION_CAPABILITIES.md) - Cognitive Loop
  - [Domain Expertise Capabilities](/comprehensive-platform-docs/DOMAIN_EXPERTISE_CAPABILITIES.md) - 14 AI specialists
  - [Predictive Intelligence](/comprehensive-platform-docs/PREDICTIVE_INTELLIGENCE_CAPABILITIES.md) - Forecasting
  - [Infrastructure Patterns](/comprehensive-platform-docs/INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md) - 18 patterns
  - [Business Process Scenarios](/comprehensive-platform-docs/BUSINESS_PROCESS_SCENARIOS_COMPLETE.md) - 10 end-to-end flows

### Infrastructure Tools & Automation
- [Infrastructure Tools](/infrastructure/tools/) - Automation, analyzers, generators
  - [Tools Catalog Index](/infrastructure/tools/TOOLS_CATALOG_INDEX.md) - Complete tool catalog (51 KB)
  - [Tools Comprehensive Catalog](/infrastructure/tools/TOOLS_COMPREHENSIVE_CATALOG.md) - Detailed descriptions (37 KB)
  - [Automation Plan](/infrastructure/tools/AUTOMATION_PLAN.md) - Platform automation strategy (30 KB)
  - [Web UI Guide](/infrastructure/tools/WEB_UI_GUIDE.md) - UI development guide (16 KB)

### 📚 Documentation by Sections (13 Categories)
- [**Index by Sections**](./00_INDEX_BY_SECTIONS.md) - Browse documentation by category (111+ documents)
  - [AI Capabilities](./ai-capabilities/) - 7 files: LLM, RAG, ML, Orchestration, Specialists, Predictive
  - [Architecture](./architecture/) - 15 files: C4 Model, Visualizations, Dependency Matrix, Tech specs
  - [Knowledge Library](./knowledge-library/) - 8 files: ISO flows, NIST, WHO healthcare, Best practices
  - [Integration](./integration/) - 7 files: EventBus, Knowledge integration, Event flows
  - [Guides](./guides/) - 9 files: User guides, ISO compliance, Security, Business scenarios
  - [Modules](./modules/) - 48 files: Infrastructure, Intelligent-core, Platform-services docs
  - [Business Analysis](./business-analysis/) - 3 files: Business flows catalog and analysis
  - [Deployment](./deployment/) - 4 files: Infrastructure setup, Port mapping
  - [Executive](./executive/) - 5 files: Executive summaries, Decision records, Checklists
  - [Analysis](./analysis/) - 3 files: Event system analysis, Complete analysis
  - [API](./api/) - 2 files: OpenAPI, AsyncAPI specifications
  - [Reports](./reports/) - Documentation reports and summaries
  - [Testing](./testing/) - Testing specifications and automation

---

## Platform-Level Documentation (/docs/)

### Strategic and Executive

| Document | Description | Audience |
|----------|-------------|----------|
| [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md) | Business value proposition, theory of change, market opportunity | C-Suite, Board, Investors |
| [README.md](./README.md) | Platform overview, capabilities, quick start | All users |

### Getting Started

| Document | Description | Audience |
|----------|-------------|----------|
| [GETTING_STARTED.md](./GETTING_STARTED.md) | Installation, configuration, first workflow | Developers, Admins |

### Architecture and Design

| Document | Description | Audience |
|----------|-------------|----------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Complete platform architecture (C4 Model, all layers) | Architects, Developers |
| [API_REFERENCE.md](./API_REFERENCE.md) | Unified API documentation (150+ endpoints) | Developers, Integrators |

### Deployment and Operations

| Document | Description | Audience |
|----------|-------------|----------|
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Production deployment guide (Docker, Kubernetes, HA) | DevOps, SysAdmins |

### Standards and Compliance

| Document | Description | Audience |
|----------|-------------|----------|
| [STANDARDS_COMPLIANCE.md](./STANDARDS_COMPLIANCE.md) | ISO 22301, ISO 27001 compliance mapping | Compliance Officers, Auditors |

---

## Infrastructure Layer (/infrastructure/)

### Overview
[Infrastructure README](/infrastructure/README.md) - Complete infrastructure layer documentation

### Core Components

| Component | Port/Service | Description | Documentation |
|-----------|--------------|-------------|---------------|
| **EventBus** | Redis/RabbitMQ | Event-driven messaging system | /infrastructure/eventbus/README.md |
| **Database** | PostgreSQL | Multi-tenant database layer | /infrastructure/database/README.md |
| **Security** | - | Authentication, authorization, encryption | /infrastructure/security/README.md |
| **API Gateway** | 8000 | Unified API gateway and routing | /infrastructure/gateway/README.md |
| **Observability** | 9090/3000 | Prometheus/Grafana monitoring | /infrastructure/observability/README.md |
| **Vector DB** | 6333 | Qdrant vector database | /infrastructure/vector-db/README.md |
| **Runtime** | - | Service discovery, message queue, WebSocket | /infrastructure/runtime/README.md |

---

## Intelligent Core Layer (/intelligent-core/)

### Overview
[Intelligent Core README](/intelligent-core/README.md) - AI and intelligent systems layer

### Modules

| Module | Port | Description | Documentation |
|--------|------|-------------|---------------|
| **ai-foundation** | - | Multi-model LLM orchestration, RAG, ML | [README](/intelligent-core/ai-foundation/README.md) |
| **workflow_intelligence** | 8037 | Workflow orchestration with Temporal Cloud | [README](/intelligent-core/workflow_intelligence/README.md) |
| **expertise-center** | 8036 | Domain specialists and tactical assistants | [README](/intelligent-core/expertise-center/README.md) |
| **collective** | 8032 | Collective intelligence and privacy-preserving agents | [README](/intelligent-core/collective/README.md) |
| **predictive** | 8031 | Risk forecasting and scenario simulation | [README](/intelligent-core/predictive/README.md) |
| **community_intelligence** | 8038 | Community knowledge and peer learning | [README](/intelligent-core/community_intelligence/README.md) |
| **event_intelligence** | 8039 | Real-time event pattern detection | [README](/intelligent-core/event_intelligence/README.md) |
| **learning-system** | 8033 | Training and knowledge management | [README](/intelligent-core/learning-system/README.md) |
| **knowledge-system** | 8034 | Standards library and knowledge base | [README](/intelligent-core/knowledge-system/README.md) |
| **workflow-engine** | 8041 | BPMN workflow execution engine | [README](/intelligent-core/workflow-engine/README.md) |
| **orchestration** | - | Service coordination and routing | [README](/intelligent-core/orchestration/README.md) |
| **ai_workflow_optimizer** | - | Workflow optimization with AI | [README](/intelligent-core/ai_workflow_optimizer/README.md) |
| **shared** | - | Shared utilities and libraries | [README](/intelligent-core/shared/README.md) |
| **wrappers** | - | External service wrappers | [README](/intelligent-core/wrappers/README.md) |

**Total:** 14 intelligent core modules

---

## Platform Services Layer (/platform-services/)

### Overview
[Platform Services README](/platform-services/README.md) - Business continuity management services

### Services

| Service | Port | ISO Clauses | Description | Documentation |
|---------|------|-------------|-------------|---------------|
| **bia-service** | 8012 | 8.2.2 | Business Impact Analysis automation | [README](/platform-services/bia-service/README.md) |
| **risk-service** | 8040 | 8.2.3 | Risk assessment and management (FAIR) | [README](/platform-services/risk-service/README.md) |
| **compliance-service** | 8014 | 9.2, 10.1, 10.2 | ISO 22301 compliance monitoring | [README](/platform-services/compliance-service/README.md) |
| **response-service** | 8050 | 8.4 | Incident response coordination | [README](/platform-services/response-service/README.md) |
| **governance-service** | 8030 | 4, 5, 7 | BCM governance and policies | [README](/platform-services/governance-service/README.md) |
| **planning-service** | 8035 | 8.3 | Business continuity strategy planning | [README](/platform-services/planning-service/README.md) |
| **plans-service** | 8045 | 8.4.2 | BC plans and procedures | [README](/platform-services/plans-service/README.md) |
| **documents-service** | 8060 | 7.5 | Document management | [README](/platform-services/documents-service/README.md) |
| **learning-service** | 8055 | 7.2, 10.2 | Training and awareness | [README](/platform-services/learning-service/README.md) |
| **validation-service** | 8065 | 8.5 | Testing and exercise management | [README](/platform-services/validation-service/README.md) |
| **community-service** | 8075 | All | Community features and collaboration | [README](/platform-services/community-service/README.md) |
| **bcm-coordination** | 8070 | All | BCM program coordination | [README](/platform-services/bcm-coordination-service/README.md) |

**Total:** 12 platform services covering all ISO 22301 clauses

---

## Documentation by Role

### For Business Users

**Getting Started:**
- [Platform Overview](./README.md)
- [Executive Summary](./EXECUTIVE_SUMMARY.md)

**BCM Implementation:**
- [BIA Service](/platform-services/bia-service/README.md)
- [Risk Service](/platform-services/risk-service/README.md)
- [Compliance Service](/platform-services/compliance-service/README.md)

### For Developers

**Getting Started:**
- [Getting Started Guide](./GETTING_STARTED.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [API Reference](./API_REFERENCE.md)

**Development:**
- [Intelligent Core Modules](/intelligent-core/README.md)
- [Platform Services](/platform-services/README.md)
- [Infrastructure Layer](/infrastructure/README.md)

### For DevOps Engineers

**Deployment:**
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Infrastructure Overview](/infrastructure/README.md)

**Monitoring:**
- [Observability](/infrastructure/observability/README.md)

### For Compliance Officers

**Standards:**
- [Standards Compliance](./STANDARDS_COMPLIANCE.md)
- [Compliance Service](/platform-services/compliance-service/README.md)

**ISO 22301 Implementation:**
- All Platform Services (complete clause coverage)

### For Architects

**System Design:**
- [Architecture Overview](./ARCHITECTURE.md)
- [Infrastructure Layer](/infrastructure/README.md)
- [Intelligent Core Layer](/intelligent-core/README.md)

---

## Documentation Statistics

**Platform-Level Docs:** 12 files
- Core: EXECUTIVE_SUMMARY, README, GETTING_STARTED, DEPLOYMENT_GUIDE, STANDARDS_COMPLIANCE, ARCHITECTURE, API_REFERENCE
- Maps: COMPLETE_DOCUMENTATION_MAP, PLATFORM_ARCHITECTURE_MAP, ARCHIVE_INVENTORY
- Generated: platform-map.json, platform-architecture.mmd

**Comprehensive Platform Docs:** 8 files (426 KB)
- AI capabilities, 570+ usage scenarios, 18 infrastructure patterns, 10 business flows

**Infrastructure Tools:** 8 documentation files + 30+ automation scripts (187 KB)
- Tools catalogs, analyzers, generators, automation plans

**Infrastructure:** 1 layer overview + 7 component READMEs

**Intelligent Core:** 1 layer overview + 14 module doc packages (14 READMEs + ~84 technical docs)

**Platform Services:** 1 layer overview + 12 service doc packages (12 READMEs + ~72 technical docs)

**Archive:** 13 sections, 111 files (2.1 MB) - preserved for reference

**Total Active Documentation Files:** ~320+ professional technical documents

**Total Content:** ~6.5 MB documentation (active + archive)

**Standards Compliance:** ISO/IEC/IEEE 26514:2022 (Documentation), ISO/IEC/IEEE 42010:2011 (Architecture)

---

## Documentation Standards

All documentation follows these standards:
- **Language:** Professional English only
- **Format:** Markdown with consistent structure
- **Code Examples:** Tested and working
- **Diagrams:** ASCII/text-based for version control
- **Versioning:** Semantic versioning with dates
- **Maintenance:** Quarterly review cycle

**No emojis, no Russian text, no informal language in production documentation.**

---

## Document Information

**Document Version:** 2.0.0
**Created:** 2025-10-09
**Last Updated:** 2025-10-09
**Next Review:** 2026-01-09
**Maintained By:** Documentation Team
**Standards Compliance:** ISO/IEC/IEEE 26514:2022
