# Services Distinction - Platform vs Business

**Date**: 2025-10-12
**Purpose**: Clarify distinction between platform and business services

---

## 🎯 Two Types of Services

### 1. 🔧 Platform Services (Системные сервисы)

**Location**: [`/catalogs/platform-services/`](/Users/MD/AI-Platform-ISO/catalogs/platform-services/)

**What**: Infrastructure and platform-level microservices that run the platform itself

**Examples**:
- PostgreSQL (database)
- Redis (cache)
- API Gateway (routing)
- Auth Service (authentication)
- MIO Manager (AI coordinator)
- EventBus (event processing)

**Total**: 46 services

**Purpose**: Make the platform work (infrastructure, AI Office, runtime, etc.)

**Users**: Platform administrators, DevOps, System architects

**Catalog**: `SERVICE_CATALOG_DETAILED.yaml`

---

### 2. 📋 Business Services (Программные сервисы для пользователей)

**Location**: [`/catalogs/business-services/`](/Users/MD/AI-Platform-ISO/catalogs/business-services/)

**What**: BCM business capabilities that end users interact with

**Examples**:
- BIA Service (Business Impact Analysis)
- Risk Assessment Service
- BCM Plans Service
- Incident Response Service
- Compliance Monitoring
- Learning & Training

**Total**: 10 services

**Purpose**: Provide BCM functionality to end users

**Users**: BCM Managers, Risk Analysts, Compliance Officers, Incident Coordinators

**Catalog**: `BUSINESS_SERVICES_CATALOG.yaml`

---

## 📊 Comparison

| Aspect | Platform Services | Business Services |
|--------|------------------|------------------|
| **Purpose** | Run the platform | Provide BCM capabilities |
| **Users** | Administrators, DevOps | Business users, BCM Managers |
| **Count** | 46 | 10 |
| **Layer** | Infrastructure | Application |
| **Examples** | PostgreSQL, Redis, EventBus | BIA, Risk Assessment, Plans |
| **Catalog** | SERVICE_CATALOG_DETAILED.yaml | BUSINESS_SERVICES_CATALOG.yaml |
| **ISO 22301** | Supporting infrastructure | Core BCM clauses (8.2, 8.3, 8.4) |

---

## 🏗️ Architecture Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│              BUSINESS SERVICES (L4)                      │
│         (What users interact with)                      │
│                                                          │
│  BIA, Risk, Plans, Response, Compliance, etc.           │
│                         (10)                             │
└──────────────────────┬──────────────────────────────────┘
                       │ uses
                       ▼
┌─────────────────────────────────────────────────────────┐
│           FUNCTIONAL SYSTEMS (L3)                        │
│       (Functional capabilities)                          │
│                                                          │
│  Security, Monitoring, AI Orchestration, etc.           │
│                         (19)                             │
└──────────────────────┬──────────────────────────────────┘
                       │ composed of
                       ▼
┌─────────────────────────────────────────────────────────┐
│              SUBSYSTEMS (L2)                             │
│          (Technical grouping)                            │
│                                                          │
│  Database Infrastructure, AI Office, Platform Services  │
│                         (11)                             │
└──────────────────────┬──────────────────────────────────┘
                       │ composed of
                       ▼
┌─────────────────────────────────────────────────────────┐
│           PLATFORM SERVICES (L1)                         │
│            (Infrastructure)                              │
│                                                          │
│  PostgreSQL, Redis, Auth, MIO, EventBus, etc.           │
│                         (46)                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Scenario Generation Strategy

### For Platform Services (46 scenarios)
- **Template**: `golden_standard_l1.yaml`
- **Focus**: Service health, performance, dependencies, resilience
- **Examples**:
  - `l1-platform-postgresql` - Test PostgreSQL service
  - `l1-platform-redis` - Test Redis service
  - `l1-platform-auth-service` - Test Auth Service

### For Business Services (10 scenarios)
- **Template**: `golden_standard_l1_business.yaml` (specialized)
- **Focus**: User workflows, business logic, ISO 22301 compliance
- **Examples**:
  - `l1-business-bia-service` - Test BIA creation workflow
  - `l1-business-risk-service` - Test risk assessment workflow
  - `l1-business-plans-service` - Test plan creation workflow

---

## 📂 Directory Structure

```
catalogs/
├── platform-services/           # Platform infrastructure services
│   ├── SERVICE_CATALOG_DETAILED.yaml    # 46 platform services
│   └── README.md
│
├── business-services/           # Business capability services
│   ├── BUSINESS_SERVICES_CATALOG.yaml   # 10 BCM services
│   └── README.md
│
├── subsystems/                  # Technical subsystems (11)
│   └── SUBSYSTEMS_CATALOG.yaml
│
├── systems/                     # Functional systems (19)
│   └── SYSTEMS_CATALOG.yaml
│
├── scenarios/                   # Generated scenarios
│   ├── l1/
│   │   ├── platform/           # 46 platform service scenarios
│   │   └── business/           # 10 business service scenarios
│   ├── l2/                     # 11 subsystem scenarios
│   ├── l3/                     # 19 functional system scenarios
│   └── l4/                     # User E2E workflows
│
└── templates/                   # Golden standards
    ├── golden_standard_l1.yaml                # Platform services
    ├── golden_standard_l1_business.yaml       # Business services
    ├── golden_standard_l2.yaml
    ├── golden_standard_l3.yaml
    └── golden_standard_l4.yaml
```

---

## 🔗 Integration

### Platform Services Integration
```
Platform Service (L1)
    ↓ part of
Technical Subsystem (L2)
    ↓ part of
Functional System (L3)
    ↓ used by
Business Service (L4)
```

**Example**:
```
PostgreSQL (L1 - platform service)
    ↓ part of
Database Infrastructure (L2 - subsystem)
    ↓ part of
Data Storage System (L3 - functional system)
    ↓ used by
BIA Service (L4 - business service)
```

---

## 📊 Statistics

### Platform Services (46)
- **Infrastructure**: Database (4), Runtime (3), Gateway (1), Security (3), EventBus (1), Observability (2)
- **AI Office**: 7 AI specialists
- **Intelligent Core**: 12 AI services
- **Platform Business Logic**: 11 BCM backend services
- **Shared**: 2 utilities

### Business Services (10)
- **BCM Core**: BIA, Risk, Plans (3)
- **BCM Operations**: Response, Validation (2)
- **Governance**: Compliance, Governance (2)
- **Competence**: Learning (1)
- **Support**: Documents (1)
- **Strategy**: Planning (1)

---

## ✅ Key Takeaway

**Platform Services** = Infrastructure that runs the platform
**Business Services** = Capabilities that users consume

Both are essential, but serve different purposes and different audiences.

---

**Last Updated**: 2025-10-12
**Status**: ✅ CATALOGS SEPARATED
