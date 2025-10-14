# Platform Architecture

**Platform**: AI-Platform-ISO v2.0.0
**Architecture Style**: Microservices + Event-Driven + AI-Enhanced
**Last Updated**: 2025-10-09

---

## Overview

Complete architecture documentation for the AI-Platform-ISO Business Continuity Management platform with integrated AI capabilities.

---

## Architecture Documents

### Core Architecture

1. **[UNIFIED_PLATFORM_ARCHITECTURE.md](./UNIFIED_PLATFORM_ARCHITECTURE.md)** - Complete platform architecture overview
2. **[TECHNICAL_ARCHITECTURE_SPECIFICATION.md](./TECHNICAL_ARCHITECTURE_SPECIFICATION.md)** - Technical implementation details
3. **[COMPLETE_ARCHITECTURE_PACKAGE.md](./COMPLETE_ARCHITECTURE_PACKAGE.md)** - All architecture artifacts in one package

### C4 Model Documentation

4. **[C4_LEVEL1_SYSTEM_CONTEXT.md](./C4_LEVEL1_SYSTEM_CONTEXT.md)** - System context diagram
5. **[C4_LEVEL2_CONTAINERS.md](./C4_LEVEL2_CONTAINERS.md)** - Container architecture
6. **[C4_LEVEL3_COMPONENTS.md](./C4_LEVEL3_COMPONENTS.md)** - Component details

### Visualization & Analysis

7. **[ARCHITECTURE_VISUALIZATIONS.md](./ARCHITECTURE_VISUALIZATIONS.md)** - Architecture diagrams
8. **[DEPENDENCY_MATRIX.md](./DEPENDENCY_MATRIX.md)** - Service dependency mapping
9. **[PLATFORM_ARCHITECTURE.md](./PLATFORM_ARCHITECTURE.md)** - Platform-wide architecture view

### Tools & Automation

10. **[ARCHITECTURE_AUTOMATION_GUIDE.md](./ARCHITECTURE_AUTOMATION_GUIDE.md)** - Automation tools
11. **[ARCHITECTURE_TOOLS_SUMMARY.md](./ARCHITECTURE_TOOLS_SUMMARY.md)** - Architecture tooling

### Additional Resources

12. **[ARCHITECTURE_ALTERNATIVES_ANALYSIS.md](./ARCHITECTURE_ALTERNATIVES_ANALYSIS.md)** - Design alternatives
13. **[QUICK_VISUALIZATION.md](./QUICK_VISUALIZATION.md)** - Quick architecture reference
14. **[SERVICE_CATALOG.yaml](./SERVICE_CATALOG.yaml)** - Complete service catalog

---

## Current Platform Architecture (2025-10-09)

### Layer 1: Infrastructure

**Components**:
- **EventBus** (Redis Streams + RabbitMQ) - Event-driven messaging
- **Database** (PostgreSQL + Supabase) - Multi-tenant data storage with RLS
- **Vector DB** (Qdrant) - RAG pipeline, vector search
- **API Gateway** (FastAPI) - Unified API routing (Port 8000)
- **Security** (Vault + JWT) - Secrets management, authentication
- **Observability** (Prometheus + Grafana) - Monitoring, metrics, alerting

**Patterns**: Event Choreography, Saga, Event Sourcing, Circuit Breaker

---

### Layer 2: Intelligent Core (11 Modules)

| Module | Port | Description |
|--------|------|-------------|
| **ai-foundation** | - | LLM routing, RAG, ML models |
| **workflow_intelligence** | 8037 | Temporal workflows, orchestration |
| **expertise-center** | 8036 | 14 domain AI specialists |
| **collective** | 8032 | Collective intelligence (347+ cases) |
| **predictive** | 8031 | ML predictions, forecasting |
| **community_intelligence** | 8038 | Community learning |
| **event_intelligence** | 8039 | Event pattern detection |
| **orchestration** | - | Cognitive Loop (6 steps) |
| **ai_workflow_optimizer** | - | Workflow optimization |
| **workflow-engine** | 8041 | BPMN execution |
| **system-bcm-service** | 8050 | Platform BCM self-application |

---

### Layer 3: Platform Services (12 Services)

| Service | Port | ISO Clause | Description |
|---------|------|------------|-------------|
| **bia-service** | 8001 | 8.2 | Business Impact Analysis |
| **risk-service** | 8002 | 8.3 | Risk Assessment & Treatment |
| **compliance-service** | 8003 | 9.1 | ISO 22301 Compliance |
| **planning-service** | 8004 | 8.4 | BC Plan Development |
| **response-service** | 8005 | 8.4 | Incident Response |
| **documents-service** | 8006 | 7.5 | Document Management |
| **governance-service** | 8007 | 5.0 | Leadership & Governance |
| **validation-service** | 8008 | 8.5 | Exercise & Testing |
| **learning-service** | 8009 | 7.3 | Training & Awareness |
| **bcm-coordination-service** | 8010 | - | Service orchestration |
| **community-service** | 8011 | - | Community & Knowledge |
| **monitoring** | 8012 | 9.0 | Performance Monitoring |

---

### Layer 4: Integration

**Components**:
- API Gateway (Port 8000)
- EventBus (Redis Streams)
- WebSocket (Real-time communication)
- External integrations (Odoo, Salesforce, etc.)

---

## Architecture Patterns

### 1. Event-Driven Architecture

**Implementation**: Redis Streams + RabbitMQ

**Patterns**:
- **Event Choreography**: Services react independently to events
- **Saga Pattern**: Distributed transactions with compensation
- **Event Sourcing**: Complete audit trail of all state changes
- **Dead Letter Queue**: Failed event handling

**Events Published**: 100+ event types across all services

---

### 2. Microservices Architecture

**Characteristics**:
- Independent deployment
- Service isolation
- API-first design
- Database per service (where appropriate)

**Communication**:
- Synchronous: REST APIs (FastAPI)
- Asynchronous: EventBus (Redis Streams)
- Real-time: WebSocket

---

### 3. Multi-Tenancy

**Implementation**: Row-Level Security (RLS) in PostgreSQL

**Features**:
- Complete data isolation between tenants
- Shared infrastructure
- Tenant-specific configurations
- Performance optimization per tenant

---

### 4. AI-Enhanced Architecture

**Integration Points**:
- LLM routing for intelligent task distribution
- RAG pipeline for knowledge retrieval
- ML models for predictions
- Cognitive orchestration for decision-making

---

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Workflow**: Temporal Cloud
- **Task Queue**: Celery + Redis

### Data Layer
- **Database**: PostgreSQL 15+ (Supabase)
- **Vector DB**: Qdrant
- **Cache**: Redis
- **Message Queue**: RabbitMQ

### AI/ML
- **LLM**: Claude (Opus/Sonnet/Haiku), GPT-4
- **Embeddings**: Sentence Transformers
- **ML**: scikit-learn, XGBoost
- **Vector Search**: Qdrant

### Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose (dev), Kubernetes (prod)
- **Monitoring**: Prometheus + Grafana
- **Secrets**: HashiCorp Vault
- **Gateway**: FastAPI

### Frontend (Optional)
- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI**: Tailwind CSS
- **State**: Zustand

---

## Deployment Architecture

### Development
```
Docker Compose
├── Infrastructure (EventBus, DB, Redis, Qdrant)
├── Intelligent Core (11 modules)
├── Platform Services (12 services)
└── Monitoring (Prometheus, Grafana)
```

### Production
```
Kubernetes
├── Infrastructure Namespace
│   ├── PostgreSQL (Supabase)
│   ├── Redis Cluster
│   ├── RabbitMQ Cluster
│   └── Qdrant Cluster
├── Intelligent-Core Namespace
│   └── 11 Deployments
├── Platform-Services Namespace
│   └── 12 Deployments
└── Monitoring Namespace
    ├── Prometheus
    ├── Grafana
    └── Alertmanager
```

---

## Port Map

### Infrastructure
- 5432: PostgreSQL
- 6379: Redis
- 5672: RabbitMQ
- 6333: Qdrant
- 8000: API Gateway
- 8200: Vault
- 9090: Prometheus
- 3000: Grafana

### Intelligent Core
- 8031-8041: AI Modules
- 8050: System BCM Service

### Platform Services
- 8001-8012: BCM Services

**Total Ports**: 20 mapped services

---

## Dependency Map

### Service Dependencies (Top-Level)

```
Platform Services
    ↓ depends on
Intelligent Core
    ↓ depends on
Infrastructure
```

### Key Dependencies

**All Services**:
- EventBus (messaging)
- PostgreSQL (data)

**AI Services**:
- Qdrant (RAG)
- Redis (working memory)

**Workflow Services**:
- Temporal Cloud

---

## High Availability

### RTO/RPO Targets
- **RTO**: 4 hours
- **RPO**: 1 hour

### HA Components
- PostgreSQL: Master-replica setup
- Redis: Cluster mode (3+ nodes)
- RabbitMQ: Cluster (3 nodes)
- Qdrant: Distributed mode

### Backup Strategy
- Database: Hourly snapshots
- Vector DB: Daily backups
- Configuration: Version controlled

---

## Security Architecture

### Authentication
- JWT tokens
- OAuth 2.0 / OIDC
- API keys for service-to-service

### Authorization
- Role-Based Access Control (RBAC)
- Row-Level Security (RLS)
- Attribute-Based Access Control (ABAC)

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Secrets management (Vault)
- PII anonymization (k-anonymity k=5)

---

## Scalability

### Horizontal Scaling
- Stateless services
- Load balancing (nginx/k8s ingress)
- Auto-scaling based on CPU/memory

### Vertical Scaling
- Database optimization
- Query performance tuning
- Caching strategies

### Current Capacity
- Supports: 1000+ concurrent users
- Handles: 10,000+ events/second
- Stores: Unlimited organizations (multi-tenant)

---

## Monitoring & Observability

### Metrics
- **Prometheus**: Service metrics, business metrics
- **Grafana**: Dashboards (20+ dashboards)
- **Custom Metrics**: 100+ metric types

### Logging
- Structured logging (JSON)
- Centralized logs (optional: ELK/Loki)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Tracing
- OpenTelemetry compatible
- Distributed tracing support
- Performance monitoring

### Alerting
- Prometheus Alertmanager
- Alert rules: 50+ rules
- Notification channels: Email, Slack, PagerDuty

---

## Architecture Diagrams

See visualization documents:
- [ARCHITECTURE_VISUALIZATIONS.md](./ARCHITECTURE_VISUALIZATIONS.md) - All diagrams
- [C4 Model](./C4_LEVEL1_SYSTEM_CONTEXT.md) - C4 architecture
- [DEPENDENCY_MATRIX.md](./DEPENDENCY_MATRIX.md) - Dependency graph

---

## Generated Maps

- [platform-map.json](/docs/platform-map.json) - Complete JSON architecture map
- [platform-architecture.mmd](/docs/platform-architecture.mmd) - Mermaid diagram

---

## Statistics

- **Total Services**: 12 platform services
- **Total Modules**: 11 intelligent core modules
- **Total Infrastructure Components**: 6
- **Total Dependencies Mapped**: 74
- **Total API Endpoints**: 150+
- **ISO 22301 Clauses Covered**: 10/10

---

## Quick References

- [Platform README](/docs/README.md)
- [API Reference](/docs/API_REFERENCE.md)
- [Deployment Guide](/docs/DEPLOYMENT_GUIDE.md)
- [Architecture Map](/docs/COMPLETE_DOCUMENTATION_MAP.md)

---

**Status**: ✅ Complete architecture documented
**Last Review**: 2025-10-09
**Next Review**: 2026-01-09 (Quarterly)
**Maintained By**: Platform Architecture Team
