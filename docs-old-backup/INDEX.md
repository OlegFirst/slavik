# BCM AI Platform - Documentation Index

**Complete documentation index for the entire platform**

---

## 📁 Documentation Structure

```
docs/
├── README.md                          # You are here
├── INDEX.md                           # Complete documentation index
│
├── architecture/                      # System architecture
│   ├── PLATFORM_ARCHITECTURE.md       # Overall platform design
│   ├── INFRASTRUCTURE_LAYER.md        # Infrastructure services
│   ├── INTELLIGENT_CORE_LAYER.md      # AI/ML modules
│   ├── PLATFORM_SERVICES_LAYER.md     # Business services
│   └── INTEGRATION_ARCHITECTURE.md    # Event-driven integration
│
├── modules/                           # Module documentation
│   ├── intelligent-core/              # AI Foundation, Orchestration, etc.
│   ├── platform-services/             # BIA, Documents, Planning, etc.
│   └── infrastructure/                # Database, EventBus, Gateway, etc.
│
├── api/                              # API documentation
│   ├── API_OVERVIEW.md               # All APIs overview
│   ├── REST_API.md                   # HTTP endpoints reference
│   ├── EVENTS_CATALOG.md             # Event-driven architecture
│   └── AUTH.md                       # Authentication & authorization
│
├── guides/                           # User guides
│   ├── QUICK_START.md                # Getting started (15 min)
│   ├── DEVELOPMENT.md                # Development guide
│   ├── DEPLOYMENT.md                 # Production deployment
│   ├── INTEGRATION.md                # Integration with platform
│   ├── TESTING.md                    # Testing strategy
│   └── ISO_22301_MAPPING.md          # ISO 22301 compliance
│
└── glossary/                         # Terminology
    ├── BUSINESS_TERMS.md             # BCM business terms
    ├── TECHNICAL_TERMS.md            # Technical concepts
    └── ACRONYMS.md                   # All abbreviations
```

---

## 🏗️ Architecture Documentation

### Platform Architecture
- [**PLATFORM_ARCHITECTURE.md**](architecture/PLATFORM_ARCHITECTURE.md)
  - System overview
  - Layers and components
  - Design principles
  - Technology stack

### Layer Documentation
- [**INFRASTRUCTURE_LAYER.md**](architecture/INFRASTRUCTURE_LAYER.md)
  - Database (PostgreSQL/Supabase)
  - EventBus (Redis Streams)
  - Gateway (API Gateway)
  - Observability (Prometheus/Grafana)
  - Security services

- [**INTELLIGENT_CORE_LAYER.md**](architecture/INTELLIGENT_CORE_LAYER.md)
  - AI Foundation (LLM, RAG, embeddings)
  - Orchestration (AI Orchestrator)
  - Expertise Center (Domain experts)
  - Workflow Engine (Temporal)
  - Collective Intelligence
  - Predictive Analytics

- [**PLATFORM_SERVICES_LAYER.md**](architecture/PLATFORM_SERVICES_LAYER.md)
  - BIA Service
  - Risk Service
  - Planning Service
  - Documents Service
  - Compliance Service
  - Community Service

- [**INTEGRATION_ARCHITECTURE.md**](architecture/INTEGRATION_ARCHITECTURE.md)
  - Event-driven patterns
  - Service communication
  - Data flow
  - Integration points

---

## 📦 Module Documentation

### intelligent-core/
- [INDEX.md](modules/intelligent-core/INDEX.md) - Overview
- [ai-foundation/README.md](modules/intelligent-core/ai-foundation.md) - AI Foundation
- [orchestration/README.md](modules/intelligent-core/orchestration.md) - AI Orchestration
- [expertise-center/README.md](modules/intelligent-core/expertise-center.md) - Domain Experts
- [workflow-engine/README.md](modules/intelligent-core/workflow-engine.md) - BPMN Engine
- [collective/README.md](modules/intelligent-core/collective.md) - Collective Intelligence
- [community_intelligence/README.md](modules/intelligent-core/community_intelligence.md) - Community
- [predictive/README.md](modules/intelligent-core/predictive.md) - Predictive Analytics

### platform-services/
- [INDEX.md](modules/platform-services/INDEX.md) - Overview
- [bia-service/README.md](modules/platform-services/bia-service.md) - BIA Service
- [risk-service/README.md](modules/platform-services/risk-service.md) - Risk Management
- [planning_service/README.md](modules/platform-services/planning_service.md) - BCM Planning
- [documents-service/README.md](modules/platform-services/documents-service.md) - Document Management
- [compliance-service/README.md](modules/platform-services/compliance-service.md) - Compliance
- [validation-service/README.md](modules/platform-services/validation-service.md) - Validation

### infrastructure/
- [INDEX.md](modules/infrastructure/INDEX.md) - Overview
- [database/README.md](modules/infrastructure/database.md) - Database Layer
- [runtime/eventbus/README.md](modules/infrastructure/eventbus.md) - EventBus
- [gateway/README.md](modules/infrastructure/gateway.md) - API Gateway
- [observability/README.md](modules/infrastructure/observability.md) - Monitoring & Observability
- [security/README.md](modules/infrastructure/security.md) - Security Services

---

## 🌐 API Documentation

### REST API
- [**API_OVERVIEW.md**](api/API_OVERVIEW.md) - All platform APIs
- [**REST_API.md**](api/REST_API.md) - Complete HTTP endpoints reference
- [**AUTH.md**](api/AUTH.md) - Authentication & authorization

### Events
- [**EVENTS_CATALOG.md**](api/EVENTS_CATALOG.md) - All platform events
  - Event schemas
  - Publishers & subscribers
  - Event flow diagrams

---

## 📖 User Guides

### Getting Started
- [**QUICK_START.md**](guides/QUICK_START.md) - 15-minute quick start
- [**DEVELOPMENT.md**](guides/DEVELOPMENT.md) - Development environment setup
- [**DEPLOYMENT.md**](guides/DEPLOYMENT.md) - Production deployment guide

### Integration & Usage
- [**INTEGRATION.md**](guides/INTEGRATION.md) - Integrate with platform
- [**TESTING.md**](guides/TESTING.md) - Testing strategy & guidelines

### Compliance
- [**ISO_22301_MAPPING.md**](guides/ISO_22301_MAPPING.md) - ISO 22301 compliance mapping

---

## 📝 Glossary & Reference

### Terminology
- [**BUSINESS_TERMS.md**](glossary/BUSINESS_TERMS.md) - BCM business terminology
- [**TECHNICAL_TERMS.md**](glossary/TECHNICAL_TERMS.md) - Platform technical concepts
- [**ACRONYMS.md**](glossary/ACRONYMS.md) - All abbreviations and acronyms

---

## 🔍 Quick Find

### By Role

**Business Analyst / BCM Manager:**
- Platform Overview: [PLATFORM_ARCHITECTURE.md](architecture/PLATFORM_ARCHITECTURE.md#business-overview)
- BCM Services: [PLATFORM_SERVICES_LAYER.md](architecture/PLATFORM_SERVICES_LAYER.md)
- ISO 22301: [ISO_22301_MAPPING.md](guides/ISO_22301_MAPPING.md)

**Developer:**
- Quick Start: [QUICK_START.md](guides/QUICK_START.md)
- Development Guide: [DEVELOPMENT.md](guides/DEVELOPMENT.md)
- API Reference: [REST_API.md](api/REST_API.md)

**DevOps / SRE:**
- Deployment: [DEPLOYMENT.md](guides/DEPLOYMENT.md)
- Infrastructure: [INFRASTRUCTURE_LAYER.md](architecture/INFRASTRUCTURE_LAYER.md)
- Observability: [infrastructure/observability](modules/infrastructure/observability.md)

**Architect:**
- Platform Architecture: [PLATFORM_ARCHITECTURE.md](architecture/PLATFORM_ARCHITECTURE.md)
- Integration Patterns: [INTEGRATION_ARCHITECTURE.md](architecture/INTEGRATION_ARCHITECTURE.md)
- All Layers: [architecture/](architecture/)

### By Topic

**AI/ML:**
- AI Foundation: [ai-foundation](modules/intelligent-core/ai-foundation.md)
- LLM Integration: [INTELLIGENT_CORE_LAYER.md](architecture/INTELLIGENT_CORE_LAYER.md#ai-foundation)
- RAG Pipeline: [ai-foundation](modules/intelligent-core/ai-foundation.md#rag)

**Event-Driven Architecture:**
- EventBus: [eventbus](modules/infrastructure/eventbus.md)
- Events Catalog: [EVENTS_CATALOG.md](api/EVENTS_CATALOG.md)
- Integration Patterns: [INTEGRATION_ARCHITECTURE.md](architecture/INTEGRATION_ARCHITECTURE.md)

**Workflow & Orchestration:**
- Workflow Engine: [workflow-engine](modules/intelligent-core/workflow-engine.md)
- AI Orchestrator: [orchestration](modules/intelligent-core/orchestration.md)
- BPMN: [workflow-engine](modules/intelligent-core/workflow-engine.md#bpmn)

**Security:**
- Authentication: [AUTH.md](api/AUTH.md)
- API Gateway: [gateway](modules/infrastructure/gateway.md)
- Security Services: [security](modules/infrastructure/security.md)

---

## 📊 Documentation Standards

All documentation follows:

- **ISO 9001** - Quality management for documentation
- **ISO/IEC 26514** - Technical documentation standards
- **Markdown** - GitHub Flavored Markdown
- **Diagrams** - Mermaid for architecture diagrams
- **API Docs** - OpenAPI 3.0 / AsyncAPI 3.0

---

## 🔄 Document Updates

| Document | Last Updated | Status |
|----------|-------------|--------|
| Platform Architecture | 2025-10-07 | ✅ Current |
| Infrastructure Layer | 2025-10-07 | ✅ Current |
| Intelligent Core Layer | 2025-10-07 | ✅ Current |
| Platform Services Layer | 2025-10-07 | ✅ Current |
| API Reference | 2025-10-07 | ✅ Current |
| Quick Start Guide | 2025-10-07 | ✅ Current |

---

<sub>Documentation Index | Version 1.0.0 | Last Updated: 2025-10-07</sub>
