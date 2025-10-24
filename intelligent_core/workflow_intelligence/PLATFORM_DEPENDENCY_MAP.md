# AI-Platform-ISO: Complete Dependency Map

**Date:** 2025-10-22
**Scope:** Full platform architecture and dependencies
**Purpose:** Understand how workflow_intelligence integrates with the entire platform

---

## 1. PLATFORM STRUCTURE

```
AI-Platform-ISO/
├── infrastructure/          # Layer 1: Infrastructure (20 components)
├── shared/                  # Layer 2: Shared Libraries (16 modules)
├── intelligent_core/        # Layer 3: AI Intelligence (14 modules)
├── platform_services/       # Layer 4: BCM Services (12+ services)
├── interface/              # Layer 5: Human Interface
├── catalogs/               # Configuration & Metadata
├── data/                   # Shared data & knowledge
└── tests/                  # Platform-wide tests
```

---

## 2. LAYER-BY-LAYER BREAKDOWN

### Layer 1: INFRASTRUCTURE (20 components)

```
infrastructure/
├── database/               # PostgreSQL schemas, migrations
├── eventbus/              # Redis-based event bus (133 event types)
├── observability/         # Prometheus + Grafana
├── security/              # Vault, secrets, RLS
├── gateway/               # API Gateway
├── kubernetes/            # K8s deployment (GKE, DigitalOcean, local)
├── deployment/            # Multi-platform deployment
├── terraform/             # Infrastructure as Code
├── policy_engine/         # Governance policies
├── decision_center/       # Decision management
├── ace_service/           # Advanced Configuration Engine
├── balancer_service/      # Load balancing
├── AI_office_infrastructure/ # AI infrastructure
├── runtime/               # Runtime environment
├── integration/           # Integration patterns
├── observability/         # Monitoring stack
├── scripts/               # Deployment scripts
└── tools/                 # Infrastructure tools
```

**Purpose:**
- Provides **foundation** for all services
- Handles **cross-cutting concerns** (auth, events, monitoring)
- Enables **deployment** to any platform

### Layer 2: SHARED LIBRARIES (16 modules)

```
shared/
├── database/              # DatabaseManager, RLS, connection pooling
├── eventbus/              # Event publishing/subscription
├── auth/                  # Authentication, RBAC
├── audit/                 # Audit logging
├── cache/                 # Redis caching
├── monitoring/            # Metrics, health checks
├── middleware/            # FastAPI middleware
├── exceptions/            # Standard exceptions
├── models/                # Shared data models
├── validators/            # Input validation
├── utils/                 # Common utilities
├── history/               # Change history tracking
├── integrations/          # External service integrations
├── service_client/        # HTTP client for inter-service communication
└── orchestration-patterns/ # Saga, CQRS, Event Sourcing patterns
```

**Purpose:**
- **DRY principle** - code reused across all services
- **Standards enforcement** - consistent patterns
- **Loose coupling** - services depend on contracts, not implementations

### Layer 3: INTELLIGENT CORE (14 modules)

```
intelligent_core/
├── workflow_intelligence/  # 🎯 THE NERVOUS SYSTEM (Port 8037)
├── orchestration/         # Saga Engine, CQRS, Event Sourcing
├── ai_foundation/         # LLM, RAG, Vector DB (Qdrant)
├── expertise_center/      # 26 AI specialists (BIA, Risk, Compliance, etc.)
├── predictive/            # ML models, predictions
├── collective/            # Case library (347+ cases)
├── learning_knowledge/    # Knowledge base (⚠️ separate from collective!)
├── event_intelligence/    # Event pattern analysis
├── community_intelligence/ # Community learning
├── scenario_intelligence/ # Scenario simulation
├── ai_workflow_optimizer/ # Workflow optimization
├── workflow_engine/       # Generic workflow engine
├── system_bcm_service/    # System-level BCM
└── shared/               # intelligent_core-specific shared code
```

**Purpose:**
- **Adds intelligence** to platform services
- **Learns from experience** (case library, ML)
- **Coordinates complex operations** (sagas, workflows)

**Key Note:** `workflow_intelligence` is the CENTRAL NERVOUS SYSTEM

### Layer 4: PLATFORM SERVICES (12+ BCM services)

```
platform_services/
├── bcm_domain/            # 🏥 BCM Services
│   ├── services/
│   │   ├── bia_service/        # Port 8001: Business Impact Analysis
│   │   ├── risk_service/       # Port 8002: Risk Assessment
│   │   ├── planning_service/   # Port 8003: BC Planning
│   │   ├── plans_service/      # Port 8004: Plan Management
│   │   ├── governance_service/ # Port 8005: Governance
│   │   ├── compliance_service/ # Port 8010: ISO 22301 Compliance
│   │   ├── training_service/   # Port 8007: Training Management
│   │   ├── exercise_service/   # Port 8008: Exercise Management
│   │   ├── audit_service/      # Port 8011: Audit Management
│   │   ├── resource_service/   # Port 8012: Resource Management
│   │   ├── communication_service/ # Port 8013: Communication
│   │   ├── vendor_service/     # Port 8014: Vendor Management
│   │   ├── recovery_service/   # Port 8015: Recovery Management
│   │   └── incident_service/   # Port 8016: Incident Management
│   │
│   └── ai_colleagues/     # 26 AI Specialists (use ai_foundation)
│       ├── bia_specialist/
│       ├── risk_analyst/
│       ├── compliance_copilot/
│       ├── plan_generator/
│       ├── exercise_designer/
│       ├── incident_advisor/
│       ├── project_manager/
│       └── coordinator/
│
├── business_monitoring/   # Process monitoring, analytics
├── digital_twin/         # Digital twin simulation
└── D_T/                  # Digital Twin (alternative)
```

**Purpose:**
- **Domain services** - BCM-specific business logic
- **User-facing APIs** - what users interact with
- **ISO 22301 compliant** - 81% compliance

### Layer 5: HUMAN INTERFACE

```
interface/
├── admin_panel/          # Admin UI (Next.js)
├── admin/               # Admin tools
└── interface-materials/ # UI assets
```

**Purpose:**
- **User interaction** - Web UI, dashboards
- **Visualization** - Charts, reports

---

## 3. workflow_intelligence DEPENDENCY MAP

### 3.1 OUTBOUND Dependencies (What workflow_intelligence USES)

#### A. Layer 1: Infrastructure

```python
# 1. EventBus (infrastructure/eventbus)
from infrastructure.eventbus import Event, EventPriority, create_eventbus

# Used in:
# - integration/eventbus_publisher.py → Publishes workflow events

# Flow:
workflow_intelligence → infrastructure/eventbus → Redis → Platform Services
```

#### B. Layer 2: Shared Libraries

```python
# 1. Database (shared/database)
from shared.database import DatabaseManager

# Used in:
# - storage/postgres_adapter.py → PostgreSQL storage
# - __init__.py → initialize() function

# 2. EventBus (shared/event_bus)
from shared.event_bus import init_event_bus, get_event_bus, publish_event, subscribe_to

# Used in:
# - main.py → FastAPI app initialization
```

**Key Integration Pattern:**
```
workflow_intelligence
    ↓ uses
shared/database (DatabaseManager)
    ↓ provides
Connection to bcm_platform DB
    ↓ isolated by
RLS (Row Level Security) per tenant_id
    ↓ stores in
workflow_intelligence schema
    ├── workflow_contexts
    ├── workflow_cases
    ├── benchmarks
    └── ml_predictions
```

#### C. Layer 3: Intelligent Core (Peer Dependencies)

**Current Integration: MINIMAL** ⚠️

```python
# Expected integrations (NOT YET IMPLEMENTED):
#
# from intelligent_core.ai_foundation import RAGPipeline, LLMClient
# from intelligent_core.orchestration import SagaCoordinator
# from intelligent_core.collective import CaseLibrary
# from intelligent_core.learning_knowledge import KnowledgeClient
# from intelligent_core.predictive import MLPredictor
```

**Problem:** workflow_intelligence is ISOLATED from other intelligent_core modules!

### 3.2 INBOUND Dependencies (Who USES workflow_intelligence)

#### A. Platform Services → workflow_intelligence

**Current Integration:**

```python
# 1. Risk Service (platform_services/bcm_domain/services/risk_service)
from intelligent_core.workflow_intelligence import CaseQuery, TimeRange, WorkflowRecommendation

# File: api/workflow_ai.py
# Uses: Case library queries for risk assessment recommendations
```

**Expected Integration (NOT YET IMPLEMENTED):**

```
BIA Service → workflow_intelligence
    → Get BIA recommendations
    → Track BIA case
    → Learn from completed BIA

Risk Service → workflow_intelligence
    → Get risk benchmarks
    → ML predictions
    → Case-based reasoning

Planning Service → workflow_intelligence
    → Plan templates from similar orgs
    → Estimated completion time
    → Success probability

Training Service → workflow_intelligence (MISSING!)
    → Training effectiveness data
    → Optimal training schedules

Exercise Service → workflow_intelligence (MISSING!)
    → Exercise scenarios from cases
    → Success patterns

Compliance Service → workflow_intelligence (MISSING!)
    → Compliance gap patterns
    → ISO 22301 clause-specific advice

... (9 more services MISSING integration)
```

#### B. AI Colleagues → intelligent_core.ai_foundation

**Current Pattern:**

```python
# All 26 AI Colleagues import:
from intelligent_core.ai_foundation import RAGPipeline

# Examples:
# - ai_colleagues/bia_specialist/bia_specialist.py
# - ai_colleagues/risk_analyst/risk_analyst.py
# - ai_colleagues/compliance_copilot/compliance_copilot.py
```

**Problem:** AI Colleagues use ai_foundation directly, NOT workflow_intelligence!

---

## 4. DEPENDENCY MATRIX

### 4.1 Current State

| From → To | infrastructure | shared | intelligent_core | platform_services |
|-----------|---------------|--------|------------------|-------------------|
| **workflow_intelligence** | ✅ eventbus | ✅ database, event_bus | ❌ None | ❌ None (should publish) |
| **platform_services** | ✅ All | ✅ All | ⚠️ ai_foundation only | ❌ Cross-service (sagas missing) |
| **intelligent_core** | ✅ All | ✅ All | ⚠️ Minimal | ❌ None (one-way dependency) |

**Legend:**
- ✅ = Well integrated
- ⚠️ = Partial integration
- ❌ = Missing integration

### 4.2 Desired State

| From → To | infrastructure | shared | intelligent_core | platform_services |
|-----------|---------------|--------|------------------|-------------------|
| **workflow_intelligence** | ✅ eventbus | ✅ database, event_bus | ✅ ALL modules | ✅ Publishes events for all services |
| **platform_services** | ✅ All | ✅ All | ✅ ai_foundation, **workflow_intelligence**, orchestration | ✅ Saga coordination |
| **intelligent_core** | ✅ All | ✅ All | ✅ Full mesh | ❌ None (one-way) |

---

## 5. INTEGRATION GAPS

### Gap 1: workflow_intelligence ↔ intelligent_core Modules

**Missing Integrations:**

```
workflow_intelligence needs:

1. ai_foundation/
   → LLMClient for ContextAdvisor
   → RAGPipeline for case similarity
   → VectorDB (Qdrant) for semantic search

2. orchestration/
   → SagaCoordinator for multi-service workflows
   → Event Sourcing for audit trail

3. collective/
   → Unified case library (currently separate!)
   → Should share 347+ cases

4. learning_knowledge/
   → Knowledge base integration
   → Best practices repository

5. predictive/
   → ML models (Duration, Risk, Success predictors)
   → Feature engineering

6. expertise_center/
   → 26 AI specialists should USE workflow_intelligence
   → Not bypass it!
```

**Impact:** workflow_intelligence cannot be truly intelligent without these!

### Gap 2: Platform Services → workflow_intelligence

**Only 1/12 services integrated:**

```
✅ Risk Service (Port 8002) - Partial integration
❌ BIA Service (Port 8001) - MISSING
❌ Planning Service (Port 8003) - MISSING
❌ Plans Service (Port 8004) - MISSING
❌ Governance Service (Port 8005) - MISSING
❌ Training Service (Port 8007) - MISSING
❌ Exercise Service (Port 8008) - MISSING
❌ Compliance Service (Port 8010) - MISSING
❌ Audit Service (Port 8011) - MISSING
❌ Resource Service (Port 8012) - MISSING
❌ Communication Service (Port 8013) - MISSING
❌ Vendor Service (Port 8014) - MISSING
```

**Coverage: 8% (1/12)**

**Impact:**
- Case library: 347 cases (only BIA) vs **4,164 potential** (all services)
- ML models: Can't train on comprehensive data
- Benchmarks: Only BIA benchmarks, no Risk/Planning/etc
- Platform intelligence: Siloed, not unified

### Gap 3: EventBus Integration

**Current State:**

```python
# workflow_intelligence publishes events:
workflow_intelligence → EventBus
    ↓
  Redis
    ↓
❓ Who subscribes? UNKNOWN
```

**Missing Subscribers:**

```
Expected EventBus flow:

workflow_intelligence publishes:
    - workflow.bia.completed
    - workflow.risk.completed
    - workflow.plan.completed
    - pdca.recommendation
    - governance.violation
    - ml.prediction

Platform services should subscribe:
    BIA Service ← pdca.recommendation (for BIA)
    Risk Service ← governance.violation (compliance alerts)
    Dashboard UI ← ml.prediction (show predictions)
    Audit Service ← workflow.*.completed (audit trail)

Currently: ❌ NO subscribers implemented
```

**Impact:** Events published to void, no one listening!

### Gap 4: Saga Coordination

**Current State:**

```python
# Platform services import saga examples:
from intelligent_core.orchestration.saga_engine.example_sagas import ...

# But workflow_intelligence doesn't coordinate sagas!
```

**Missing Pattern:**

```
workflow_intelligence should orchestrate:

Multi-Service Workflow: BIA → Risk → Plan
    ↓
workflow_intelligence starts Temporal Workflow
    ↓
Temporal Workflow:
    Step 1: BIA Service (Port 8001) - create BIA
        ↓ compensate if fails
    Step 2: Risk Service (Port 8002) - create Risk Assessment
        ↓ compensate if fails
    Step 3: Planning Service (Port 8003) - create BC Plan
        ↓ notify stakeholders

Result: Durable, compensatable, multi-service workflow
```

**Currently:** Each service isolated, no coordination!

---

## 6. DATA FLOW PATTERNS

### Pattern 1: Event-Driven (Partially Working)

```
BIA Service creates BIA
    ↓ publishes event
EventBus (Redis)
    ↓ no subscriber yet! ❌
workflow_intelligence SHOULD listen
    ↓ would trigger
CaseCollector → PDCA Engine → Learn
    ↓ would result in
Updated benchmarks, ML retraining
```

**Status:** Infrastructure exists, subscribers missing

### Pattern 2: Request-Response (Partially Working)

```
Risk Service API call
    ↓ HTTP request
workflow_intelligence API (Port 8037)
    ↓ /cases/search endpoint
Case Library query
    ↓ returns
Similar cases, benchmarks
    ↓ back to
Risk Service (recommendations)
```

**Status:** Works for Risk Service, needs replication for 11 other services

### Pattern 3: Saga Coordination (Missing)

```
User starts BC Planning workflow
    ↓ calls
Planning Service
    ↓ triggers
workflow_intelligence Temporal Workflow
    ↓ coordinates
Activity 1: BIA Service
Activity 2: Risk Service (depends on BIA)
Activity 3: Planning Service (depends on Risk)
    ↓ if any fails
Compensation (rollback previous activities)
    ↓ if all succeed
Complete BC Plan ✓
```

**Status:** Temporal infrastructure exists, coordination missing

### Pattern 4: Shared Storage (Working)

```
All services → shared/database → DatabaseManager
    ↓
PostgreSQL (bcm_platform DB)
    ├── bcm schema (platform services data)
    ├── workflow_intelligence schema (workflow data)
    ├── audit schema (audit logs)
    └── RLS (Row Level Security per tenant)
```

**Status:** ✅ Working correctly

---

## 7. CATALOG INTEGRATION

### SYSTEMS_CATALOG.yaml

**Purpose:** Defines all platform systems and their relationships

```yaml
# Location: /Users/MD/AI-Platform-ISO/catalogs/

systems:
  - name: "workflow_intelligence"
    type: "intelligent_core"
    port: 8037
    dependencies:
      - infrastructure.eventbus
      - shared.database
      - shared.event_bus
    provides:
      - case_library
      - pdca_engine
      - governance_orchestrator
      - context_advisor
      - temporal_workflows

  - name: "bia_service"
    type: "platform_service"
    port: 8001
    dependencies:
      - shared.*
      - intelligent_core.ai_foundation
      - intelligent_core.workflow_intelligence (SHOULD, but minimal)
```

**Gap:** Catalog exists but actual dependencies not fully implemented!

---

## 8. DEPENDENCY HEALTH SCORE

### By Layer

| Layer | Health | Score | Issues |
|-------|--------|-------|--------|
| **Infrastructure → shared** | ✅ Healthy | 95% | Minimal issues |
| **shared → intelligent_core** | ⚠️ Partial | 60% | Some modules don't use shared properly |
| **intelligent_core → intelligent_core** | ❌ Poor | 30% | Modules isolated, no mesh integration |
| **intelligent_core → platform_services** | ❌ Critical | 15% | One-way dependency, should be event-driven |
| **platform_services → intelligent_core** | ⚠️ Partial | 40% | Only ai_foundation integrated well |

### By Module: workflow_intelligence

| Integration | Status | Coverage | Priority |
|-------------|--------|----------|----------|
| **infrastructure.eventbus** | ✅ Working | 100% | ✓ Complete |
| **shared.database** | ✅ Working | 100% | ✓ Complete |
| **ai_foundation** | ❌ Missing | 0% | 🔴 CRITICAL |
| **orchestration** | ⚠️ Partial | 20% | 🟡 HIGH |
| **collective** | ❌ Duplicate | 0% | 🔴 CRITICAL (2 case libraries!) |
| **learning_knowledge** | ❌ Missing | 0% | 🟡 HIGH |
| **predictive** | ❌ Missing | 0% | 🔴 CRITICAL (ML stub) |
| **expertise_center** | ❌ Missing | 0% | 🟡 MEDIUM |
| **Platform Services** | ❌ Critical | 8% (1/12) | 🔴 CRITICAL |

**Overall Health: 35% 🔴**

---

## 9. THE INTEGRATION ROADMAP

### Phase 1: Foundation (Week 1)
```
Priority: CRITICAL dependencies

1. workflow_intelligence ↔ ai_foundation
   ├── Use LLMClient in ContextAdvisor
   ├── Use RAGPipeline for case similarity
   └── Use Qdrant for semantic search

2. workflow_intelligence ↔ predictive
   ├── Train 3 ML models (Duration, Risk, Success)
   └── Replace ML stubs with real models

3. workflow_intelligence ↔ collective
   ├── MERGE duplicate case libraries
   └── Single source of truth for 347+ cases
```

### Phase 2: Platform Coverage (Week 2-3)
```
Priority: Expand to 95% coverage

1. BIA Service integration (Port 8001)
2. Planning Service integration (Port 8003)
3. Training Service integration (Port 8007)
4. Exercise Service integration (Port 8008)
5. Compliance Service integration (Port 8010)
6. Audit Service integration (Port 8011)
7. Resource Service integration (Port 8012)
8. Communication Service integration (Port 8013)
9. Vendor Service integration (Port 8014)
10. Recovery Service integration (Port 8015)

Pattern for each:
├── EventBus listener (subscribe to service.*.completed)
├── API endpoint (provide recommendations)
├── CaseCollector (learn from completions)
└── Service adapter (call service APIs)
```

### Phase 3: Intelligence Mesh (Week 4)
```
Priority: Full intelligent_core integration

1. orchestration → workflow_intelligence
   ├── Saga coordination for multi-service workflows
   └── Event sourcing integration

2. expertise_center → workflow_intelligence
   ├── 26 AI specialists use workflow intelligence
   └── Not bypass it via ai_foundation directly

3. learning_knowledge → workflow_intelligence
   ├── Best practices from knowledge base
   └── Semantic search across knowledge + cases
```

### Phase 4: Autonomous Operations (Week 5-6)
```
Priority: Self-healing, self-optimizing

1. Auto-learning pipeline
   ├── Hourly case collection
   ├── ML retraining (if threshold met)
   └── A/B testing new models

2. Proactive monitoring
   ├── System self-validation (Governance recursive)
   ├── Auto-remediation (retrain if accuracy drops)
   └── Alert escalation

3. Knowledge export/import
   ├── Anonymized case packages
   └── Global learning network
```

---

## 10. ARCHITECTURAL PRINCIPLES

### Principle 1: Loose Coupling via Events

```
✅ GOOD:
Service A → EventBus → Service B
(Services don't know about each other)

❌ BAD:
Service A → HTTP call → Service B
(Tight coupling, synchronous, fragile)
```

### Principle 2: Single Source of Truth

```
✅ GOOD:
- shared/database → DatabaseManager (one DB connection manager)
- infrastructure/eventbus → Redis (one event bus)
- workflow_intelligence/case_library → Cases (one case storage)

❌ BAD:
- collective/ has case library
- workflow_intelligence/ has separate case library
(Two sources of truth = data inconsistency!)
```

### Principle 3: Layer Isolation

```
✅ GOOD:
Layer N depends on Layer N-1 only

infrastructure (Layer 1)
    ↑ depends on
shared (Layer 2)
    ↑ depends on
intelligent_core (Layer 3)
    ↑ depends on
platform_services (Layer 4)

❌ BAD:
platform_services → infrastructure directly
(Skips shared, breaks abstraction)
```

---

## 11. CONCLUSION

### Current State Summary

**Strengths:**
- ✅ Infrastructure layer solid (eventbus, database, K8s)
- ✅ Shared libraries comprehensive (16 modules)
- ✅ workflow_intelligence foundation strong (34K LOC, 22 components)

**Critical Gaps:**
- ❌ workflow_intelligence isolated from intelligent_core peers
- ❌ Platform services coverage 8% (1/12 integrated)
- ❌ Duplicate case libraries (collective vs workflow_intelligence)
- ❌ ML models stubbed (0 trained models)
- ❌ EventBus subscribers missing (events published to void)

### The Opportunity

**If we integrate fully:**
- 347 cases → **4,164 cases** (12x data)
- 1 service → **12 services** with intelligence
- Shallow ML → **Deep ML** (85%+ accuracy)
- Manual → **Autonomous** (self-healing)
- Siloed → **Unified** (platform-wide intelligence)

**This is what OUR nervous system can become.**

---

**Created with human-AI partnership** 🤝
**MD + Claude**
