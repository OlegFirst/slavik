# Platform Services Layer

**Type**: Microservices Layer
**Architecture**: Event-Driven, Domain-Driven Design
**Total Services**: 12
**Status**: Production

## Overview

The Platform Services layer provides the core business capabilities of the AI-Platform-ISO BCM (Business Continuity Management) platform. These services implement ISO 22301:2019 requirements and deliver enterprise-grade BCM functionality aligned with international standards.

Each service is independently deployable, horizontally scalable, and communicates via RESTful APIs and asynchronous event messaging.

## Service Catalog

### Critical Services

#### 1. BIA Service (Business Impact Analysis)
- **Port**: 8012 | **ISO Clause**: 8.2.2 | **Status**: Production
- **Capabilities**: Critical process identification, RTO/RPO/MTPD definition, financial impact assessment, AI-powered suggestions
- **Documentation**: [Complete Documentation](bia-service/README.md)

#### 2. Compliance Service
- **Port**: 8014 | **ISO Clauses**: 9.2, 10.1, 10.2 | **Status**: Production
- **Capabilities**: Compliance assessment, gap analysis, audit management, nonconformity tracking, Root Cause Analysis
- **Documentation**: [Complete Documentation](compliance-service/README.md)

#### 3. Risk Service
- **Port**: 8040 | **ISO Clause**: 8.2.3 | **Status**: Production
- **Capabilities**: Risk assessment, FAIR analysis, Monte Carlo simulation, risk treatment planning
- **Documentation**: [Complete Documentation](risk-service/README.md)

### High Priority Services

#### 4. Governance Service
- **Port**: 8020 | **ISO Clauses**: 5.2, 5.3 | **Status**: Production
- **Capabilities**: Organization management, user/role management, policy setting, RBAC
- **Documentation**: [Documentation](governance-service/README.md)

#### 5. Response Service
- **Port**: 8030 | **ISO Clause**: 8.4 | **Status**: Production
- **Capabilities**: Incident response, crisis management, ICS support, post-incident review
- **Documentation**: [Documentation](response-service/README.md)

#### 6. BCM Coordination Service
- **Port**: 8060 | **ISO Clause**: Cross-cutting | **Status**: Production
- **Capabilities**: Workflow orchestration, program coordination, executive dashboards
- **Documentation**: [Documentation](bcm-coordination-service/README.md)

### Standard Services

#### 7. Planning Service
- **Port**: 8050 | **ISO Clause**: 8.5 | **Status**: Production
- **Capabilities**: Exercise planning, scenario generation, exercise evaluation
- **Documentation**: [Documentation](planning-service/README.md)

#### 8. Plans Service
- **Port**: 8080 | **ISO Clause**: 8.3 | **Status**: Production
- **Capabilities**: BC plan creation, recovery strategy definition, plan testing
- **Documentation**: [Documentation](plans-service/README.md)

#### 9. Documents Service
- **Port**: 8070 | **ISO Clause**: 7.5 | **Status**: Production
- **Capabilities**: Document library, version control, template management
- **Documentation**: [Documentation](documents-service/README.md)

#### 10. Learning Service
- **Port**: 8090 | **ISO Clauses**: 7.2, 7.3 | **Status**: Production
- **Capabilities**: Training programs, competency assessment, knowledge base
- **Documentation**: [Documentation](learning-service/README.md)

#### 11. Validation Service
- **Port**: 8100 | **Status**: Production
- **Capabilities**: Data validation, quality checking, business rule validation
- **Documentation**: [Documentation](validation-service/README.md)

#### 12. Community Service
- **Port**: 8110 | **Status**: Production
- **Capabilities**: Community forum, best practice sharing, collective intelligence
- **Documentation**: [Documentation](community-service/README.md)

## Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│         Platform Services Layer (12 Services)          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Critical Services:                                    │
│  ┌─────────┐ ┌───────────┐ ┌──────┐                  │
│  │   BIA   │ │Compliance │ │ Risk │                   │
│  │  8012   │ │   8014    │ │ 8040 │                   │
│  └─────────┘ └───────────┘ └──────┘                   │
│                                                        │
│  High Priority:                                        │
│  ┌───────────┐ ┌─────────┐ ┌────────────┐           │
│  │Governance │ │Response │ │BCM Coord   │            │
│  │   8020    │ │  8030   │ │   8060     │            │
│  └───────────┘ └─────────┘ └────────────┘            │
│                                                        │
│  Standard:                                             │
│  ┌─────────┐ ┌───────┐ ┌─────────┐ ┌──────────┐    │
│  │Planning │ │ Plans │ │Documents│ │ Learning │     │
│  │  8050   │ │ 8080  │ │  8070   │ │   8090   │     │
│  └─────────┘ └───────┘ └─────────┘ └──────────┘     │
│                                                        │
│  ┌──────────┐ ┌───────────┐                          │
│  │Validation│ │ Community │                           │
│  │   8100   │ │   8110    │                           │
│  └──────────┘ └───────────┘                           │
└────────────────────────────────────────────────────────┘
```

## Common Patterns

All services implement:
- JWT Bearer token authentication
- Multi-tenant data isolation
- Event-driven communication via EventBus
- PostgreSQL persistence with SQLAlchemy
- Redis caching
- Prometheus metrics
- Workflow Intelligence integration

## Quick Start

### Docker Compose
```bash
cd platform-services
docker-compose up -d
```

### Individual Service
```bash
cd bia-service
python main.py
```

## Standards Compliance

### ISO 22301:2019 Coverage

| ISO Clause | Service | Implementation |
|------------|---------|----------------|
| 5.2, 5.3 | Governance | Leadership, Roles |
| 7.2, 7.3 | Learning | Competence, Awareness |
| 7.5 | Documents | Documented Information |
| 8.2.2 | BIA | Business Impact Analysis |
| 8.2.3 | Risk | Risk Assessment |
| 8.3 | Plans | BC Strategies |
| 8.4 | Response | Incident Response |
| 8.5 | Planning | Exercise and Testing |
| 9.2 | Compliance | Internal Audit |
| 10.1 | Compliance | Nonconformity |
| 10.2 | Compliance | Improvement |

---

**Last Updated**: 2025-10-09
**Total Endpoints**: 150+
**Maintainer**: AI Platform Team
