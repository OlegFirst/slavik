# Service Dependency Matrix

**Last Updated:** 2025-10-06
**Version:** 2.0

---

## 📊 Quick Stats

- **Total Services:** 38
- **Dependency Count:** 87 direct dependencies
- **Cycles Detected:** 0 ✅
- **Max Depth:** 3 levels
- **Critical Services:** 6 (services with 5+ dependents)

---

## 🔗 Dependency Matrix

### Legend:
- ✅ = Direct dependency
- 🔄 = Bidirectional
- ⚠️ = High coupling (5+ dependencies)
- 🔥 = Critical service (5+ dependents)

---

## AI FOUNDATION LAYER

### workflow_intelligence 🔥

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |
| database/vector-db | ✅ | Infrastructure |
| runtime/eventbus | ✅ | Infrastructure |
| temporal-cloud | ✅ | External |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| bia-service | ✅ | Platform Service |
| risk-service | ✅ | Platform Service |
| compliance-service | ✅ | Platform Service |
| governance-service | ✅ | Platform Service |
| incident-service | ✅ | Platform Service |

**Impact Score:** 🔥 **CRITICAL** (5 dependents)

---

### ai_workflow_optimizer

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| workflow_intelligence | ✅ (via REST API) | AI Foundation |
| mio-manager | ✅ (via REST API) | Infrastructure |

**Impact Score:** Medium (2 dependents)

---

### workflow_engine

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |
| runtime/eventbus | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| platform-services/* | ✅ (12 services) | Platform Services |

**Impact Score:** 🔥 **CRITICAL** (13 dependents)

---

### expertise_center ⚠️

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| community_intelligence | ✅ | AI Service |
| collective | ✅ | AI Service |
| learning-system | ✅ | AI Service |
| living-docs | ✅ | AI Service |
| workflow_intelligence | ✅ | AI Foundation |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| platform-services/* | ✅ (12 services) | Platform Services |

**Impact Score:** 🔥 **CRITICAL** (12 dependents)
**Coupling:** ⚠️ **HIGH** (5 dependencies)

---

## AI SERVICES LAYER

### community_intelligence

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |
| runtime/eventbus | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| expertise_center | ✅ | AI Foundation |
| CommunitySpecialistAI | ✅ | Tactical Assistant |

**Impact Score:** Medium (2 dependents)

---

### collective

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |
| runtime/eventbus | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| expertise_center | ✅ | AI Foundation |
| CommunitySpecialistAI | ✅ | Tactical Assistant |

**Impact Score:** Medium (2 dependents)

---

### predictive

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |

**Impact Score:** Low (1 dependent)

---

### learning_system

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| expertise_center | ✅ | AI Foundation |
| LearningSpecialistAI | ✅ | Tactical Assistant |
| learning-service | ✅ | Platform Service |

**Impact Score:** Medium (3 dependents)

---

### living_docs

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |
| database/vector-db | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| expertise_center | ✅ | AI Foundation |
| DocumentsSpecialistAI | ✅ | Tactical Assistant |
| documents-service | ✅ | Platform Service |

**Impact Score:** Medium (3 dependents)

---

## PLATFORM SERVICES LAYER

### bia-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| expertise_center (BIASpecialistAI) | ✅ | AI Foundation |
| database/postgresql | ✅ | Infrastructure |
| runtime/eventbus | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | - |

**Impact Score:** Low (leaf service)

---

### risk-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| expertise_center (RiskAnalystAI) | ✅ | AI Foundation |
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | - |

**Impact Score:** Low (leaf service)

---

### compliance-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| expertise_center (ComplianceCopilotAI) | ✅ | AI Foundation |
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | - |

**Impact Score:** Low (leaf service)

---

### governance-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| expertise_center (GovernanceSpecialistAI) | ✅ | AI Foundation |
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | - |

**Impact Score:** Low (leaf service)

---

### incident-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| expertise_center (IncidentAdvisorAI) | ✅ | AI Foundation |
| database/postgresql | ✅ | Infrastructure |
| runtime/eventbus | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | - |

**Impact Score:** Low (leaf service)

---

### validation-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| expertise_center (ValidationSpecialistAI) | ✅ | AI Foundation |
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | - |

**Impact Score:** Low (leaf service)

---

### documents-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| living-docs | ✅ | AI Service |
| expertise_center (DocumentsSpecialistAI) | ✅ | AI Foundation |
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | - |

**Impact Score:** Low (leaf service)

---

### learning-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| learning-system | ✅ | AI Service |
| expertise_center (LearningSpecialistAI) | ✅ | AI Foundation |
| database/postgresql | ✅ | Infrastructure |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | - |

**Impact Score:** Low (leaf service)

---

### Other Platform Services

| **Service** | **Dependencies** | **Dependents** | **Impact** |
|-------------|------------------|----------------|------------|
| response-service | database/postgresql, eventbus | 0 | Low |
| recovery-service | database/postgresql | 0 | Low |
| planning-service | database/postgresql | 0 | Low |
| stakeholder-service | database/postgresql | 0 | Low |

---

## INFRASTRUCTURE LAYER

### database/postgresql 🔥

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| Supabase (external) | ✅ | External |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| ai_workflow_optimizer | ✅ | AI Foundation |
| workflow_engine | ✅ | AI Foundation |
| community_intelligence | ✅ | AI Service |
| collective | ✅ | AI Service |
| predictive | ✅ | AI Service |
| learning_system | ✅ | AI Service |
| living_docs | ✅ | AI Service |
| bia-service | ✅ | Platform Service |
| risk-service | ✅ | Platform Service |
| compliance-service | ✅ | Platform Service |
| governance-service | ✅ | Platform Service |
| incident-service | ✅ | Platform Service |
| validation-service | ✅ | Platform Service |
| documents-service | ✅ | Platform Service |
| response-service | ✅ | Platform Service |
| recovery-service | ✅ | Platform Service |
| planning-service | ✅ | Platform Service |
| stakeholder-service | ✅ | Platform Service |
| learning-service | ✅ | Platform Service |
| api-gateway | ✅ | Infrastructure |
| database-gateway | ✅ | Infrastructure |

| **Total Dependents** | **24 services** |

**Impact Score:** 🔥🔥🔥 **CRITICAL** (24 dependents)

---

### database/vector-db

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| Qdrant Cloud (external) | ✅ | External |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| living_docs | ✅ | AI Service |

**Impact Score:** Medium (2 dependents)

---

### runtime/eventbus 🔥

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| Redis Cloud (external) | ✅ | External |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| workflow_intelligence | ✅ | AI Foundation |
| workflow_engine | ✅ | AI Foundation |
| community_intelligence | ✅ | AI Service |
| collective | ✅ | AI Service |
| bia-service | ✅ | Platform Service |
| incident-service | ✅ | Platform Service |

**Impact Score:** 🔥 **CRITICAL** (6 dependents)

---

### gateway/api-gateway 🔥

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| database/postgresql | ✅ | Infrastructure |
| Redis Cloud | ✅ | External |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| ALL services | ✅ | All |

**Impact Score:** 🔥🔥🔥 **CRITICAL** (Entry point for all services)

---

### gateway/agent-router

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| Redis Cloud | ✅ | External |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| api-gateway | ✅ | Infrastructure |
| expertise_center | ✅ | AI Foundation |

**Impact Score:** Medium (2 dependents)

---

### observability/mio-manager

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| prometheus | ✅ | Infrastructure |
| grafana | ✅ | Infrastructure |
| notification-service | ✅ | Infrastructure |
| ai_workflow_optimizer | ✅ (via API) | AI Foundation |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| None | - | Monitoring hub |

**Impact Score:** Low (monitoring service)

---

### observability/notification-service

| **Depends On** | **Status** | **Type** |
|----------------|------------|----------|
| SMTP (external) | ✅ | External |
| Twilio (external) | ✅ | External |
| Firebase (external) | ✅ | External |

| **Used By** | **Status** | **Type** |
|-------------|------------|----------|
| mio-manager | ✅ | Infrastructure |
| ALL services | ✅ (for alerts) | All |

**Impact Score:** High (notification hub)

---

## 📈 DEPENDENCY GRAPHS

### Top 5 Most Depended Upon Services (Critical)

| **Rank** | **Service** | **Dependents** | **Status** |
|----------|-------------|----------------|------------|
| 1 | database/postgresql | 24 | 🔥🔥🔥 |
| 2 | gateway/api-gateway | 38 (all) | 🔥🔥🔥 |
| 3 | workflow_engine | 13 | 🔥 |
| 4 | expertise_center | 12 | 🔥 |
| 5 | runtime/eventbus | 6 | 🔥 |

### Top 5 Services with Most Dependencies (Highly Coupled)

| **Rank** | **Service** | **Dependencies** | **Status** |
|----------|-------------|------------------|------------|
| 1 | expertise_center | 5 | ⚠️ |
| 2 | workflow_intelligence | 4 | ⚠️ |
| 3 | bia-service | 4 | Medium |
| 4 | incident-service | 4 | Medium |
| 5 | documents-service | 3 | Low |

---

## 🎯 DEPENDENCY LAYERS

```
Layer 0 (External)
├── Temporal Cloud
├── Supabase
├── Qdrant Cloud
├── Redis Cloud
├── SMTP/Twilio/Firebase

Layer 1 (Infrastructure)
├── database/postgresql ←─────────────────────┐
├── database/vector-db                        │
├── runtime/eventbus                          │
├── gateway/api-gateway                       │
└── observability/*                           │
                                              │
Layer 2 (AI Foundation)                       │
├── workflow_intelligence ←───────────────┐   │
├── ai_workflow_optimizer                 │   │
├── workflow_engine                       │   │
└── expertise_center                      │   │
                                          │   │
Layer 3 (AI Services)                     │   │
├── community_intelligence ───────────────┤   │
├── collective                            │   │
├── predictive                            │   │
├── learning_system ──────────────────────┤   │
└── living_docs ──────────────────────────┤   │
                                          │   │
Layer 4 (Platform Services)               │   │
├── bia-service ──────────────────────────┴───┤
├── risk-service                              │
├── compliance-service                        │
├── governance-service                        │
├── incident-service ─────────────────────────┤
├── validation-service                        │
├── documents-service ────────────────────────┤
├── learning-service ─────────────────────────┤
└── 4 other services ─────────────────────────┘
```

---

## ⚠️ RISK ANALYSIS

### Single Points of Failure (SPOF)

| **Service** | **Dependents** | **Risk** | **Mitigation** |
|-------------|----------------|----------|----------------|
| database/postgresql | 24 | 🔥🔥🔥 CRITICAL | Supabase HA + Read replicas |
| gateway/api-gateway | 38 | 🔥🔥🔥 CRITICAL | Multiple instances + Load balancer |
| workflow_engine | 13 | 🔥 HIGH | Horizontal scaling |
| expertise_center | 12 | 🔥 HIGH | Cache AI responses |
| runtime/eventbus | 6 | 🔥 MEDIUM | Redis Cluster mode |

### Circular Dependencies

✅ **None detected** (Clean dependency graph)

### High Coupling Services

| **Service** | **Dependencies** | **Risk** | **Recommendation** |
|-------------|------------------|----------|---------------------|
| expertise_center | 5 | ⚠️ HIGH | Consider facade pattern |
| workflow_intelligence | 4 | ⚠️ MEDIUM | Already well-architected |

---

## 📊 STATISTICS

- **Average Dependencies per Service:** 2.3
- **Average Dependents per Service:** 2.3
- **Longest Dependency Chain:** 4 levels (External → Infrastructure → AI Foundation → AI Services → Platform Services)
- **Services with 0 dependencies:** 0
- **Leaf Services (0 dependents):** 12 (all platform services)
- **Hub Services (5+ dependents):** 5

---

## 🔄 UPDATE HISTORY

| **Date** | **Version** | **Changes** |
|----------|-------------|-------------|
| 2025-10-06 | 2.0 | Complete dependency audit post-reorganization |
| 2025-10-05 | 1.5 | Added AI services dependencies |
| 2025-10-04 | 1.0 | Initial dependency matrix |

---

## 📝 NOTES

- This matrix is auto-generated from `SERVICE_CATALOG.yaml`
- Update frequency: Daily during active development
- Dependency changes require architecture review
- Critical services have monitoring SLAs

---

**Legend:**
- 🔥🔥🔥 = CRITICAL (20+ dependents)
- 🔥🔥 = VERY HIGH (10-19 dependents)
- 🔥 = HIGH (5-9 dependents)
- ⚠️ = High coupling warning (5+ dependencies)
