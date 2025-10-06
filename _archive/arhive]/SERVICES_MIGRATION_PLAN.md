# 🚀 SERVICES MIGRATION PLAN

**Migration from Sandbox to Production Architecture**

Date: October 3, 2025

---

## 📋 OVERVIEW

Мигрируем два крупных модуля из песочницы в production-ready архитектуру:

### Source (Sandbox):
- `/Users/MD/ISO-22301—копия/services/SERVICES/BCM/learning/` (1,272 строк main.py + workflows)
- `/Users/MD/ISO-22301—копия/services/SERVICES/BCM/governance/` (1,953 строк main.py + workflows)

### Target (Production):
- `/Users/MD/AI-Platform-ISO/platform-services/learning-service/`
- `/Users/MD/AI-Platform-ISO/platform-services/governance-service/`

---

## 🎯 GOALS

1. ✅ **Сохранить ВСЮ бизнес-логику** - ни одна функция не потеряется
2. ✅ **Сохранить workflows** - вся state machine logic
3. ✅ **Привести к архитектуре** - clean structure (models/api/services/repositories/events)
4. ✅ **Убрать заглушки** - интегрировать с реальными сервисами
5. ✅ **Интегрировать workflow-intelligence** - для умных workflows
6. ✅ **Создать shared libraries** - переиспользуемые компоненты

---

## 📊 CURRENT STATE ANALYSIS

### Learning Service (ISO 22301 Clauses 7.2 & 7.3)

**Business Logic:**
- ✅ Training Programs Management (CRUD + workflow)
- ✅ Training Enrollments с state machine (8 states)
- ✅ Competency Assessments & Gap Analysis
- ✅ Awareness Campaigns
- ✅ Training Templates Library
- ✅ Gamification (Points, Achievements, Leaderboard)
- ✅ BCI GPG Practice 2 (PP2: Embracing BC)

**Components Found:**
```
learning/
├── main.py (1,272 lines)          # Всё в одном файле - нужно разделить
├── database/
│   ├── models.py                   # SQLAlchemy models
│   ├── connection.py               # DB connection
│   └── __init__.py
├── workflows/
│   ├── training_workflow.py        # State machine для enrollments
│   ├── gamification_workflow.py    # Points, achievements logic
│   └── __init__.py
├── schemas/                        # Empty - models в main.py
├── api/                            # Empty - routes в main.py
└── requirements.txt
```

**State Machine (Enrollment Workflow):**
```
draft → submitted → approved → in_progress →
completed → assessed → certified → archived
```

**What needs to be done:**
1. Разделить monolithic main.py на:
   - `models/domain.py` - Pydantic models
   - `models/database.py` - SQLAlchemy models (уже есть)
   - `api/routes.py` - Все endpoints
   - `api/schemas.py` - Request/Response schemas
   - `services/training_service.py` - Business logic
   - `services/gamification_service.py` - Gamification logic
   - `repositories/training_repository.py` - Data access
   - `events/publishers.py` - Event publishing
   - `events/subscribers.py` - Event handling

2. Интегрировать с workflow-intelligence:
   - Обернуть training_workflow в WorkflowEngine
   - Добавить AI advisor для recommendations
   - Case collection для successful trainings

3. Заменить заглушки:
   - EVENTBUS_URL → shared/eventbus/client.py
   - Hardcoded config → shared/config.py

### Governance Service (ISO 22301 Clauses 4 & 5)

**Business Logic:**
- ✅ Context of Organization (Clause 4)
- ✅ Leadership & Commitment (Clause 5)
- ✅ Policy Management
- ✅ Objectives & KPIs
- ✅ Scope Definition
- ✅ Domain Intelligence Integration
- ✅ Audit Logging
- ✅ Cache Metrics

**Components Found:**
```
governance/
├── main.py (1,953 lines)           # Большой монолит - разделить
├── database/
│   ├── models.py                   # SQLAlchemy models
│   └── __init__.py
├── workflows/
│   └── governance_workflows.py     # Multiple workflows
├── domain_api.py                   # Domain intelligence
├── domain_schemas.py
├── ai_domain_integration.py        # AI integration
├── audit_logger.py                 # Audit trail
├── cache_metrics.py                # Performance monitoring
├── eventbus_client.py              # EventBus integration
├── bia_integration_example.py      # Integration example
├── deploy.sh                       # Deployment script
└── requirements.txt
```

**What needs to be done:**
1. Разделить на чистую архитектуру:
   - `models/` - Domain models
   - `api/` - REST endpoints
   - `services/` - Business logic (context, leadership, policy, objectives, scope)
   - `repositories/` - Data access
   - `events/` - Event handling

2. Сохранить специальные компоненты:
   - domain_api.py → services/domain_intelligence_service.py
   - ai_domain_integration.py → services/ai_integration_service.py
   - audit_logger.py → shared/utils/audit.py (reusable!)
   - cache_metrics.py → shared/utils/metrics.py (reusable!)

3. Интегрировать с workflow-intelligence:
   - Policy approval workflow
   - Objectives workflow
   - Scope definition workflow

---

## 🏗️ TARGET ARCHITECTURE

### Directory Structure (Each Service)

```
service_name/
├── __init__.py
├── config.py                  # Service configuration
├── main.py                    # FastAPI app (clean, только setup)
│
├── models/
│   ├── __init__.py
│   ├── domain.py              # Pydantic models (request/response)
│   └── database.py            # SQLAlchemy models
│
├── api/
│   ├── __init__.py
│   ├── routes.py              # All endpoints
│   └── dependencies.py        # FastAPI dependencies
│
├── services/
│   ├── __init__.py
│   └── *.py                   # Business logic (pure Python, no FastAPI)
│
├── repositories/
│   ├── __init__.py
│   └── *.py                   # Data access layer (SQLAlchemy)
│
├── events/
│   ├── __init__.py
│   ├── publishers.py          # Publish events
│   └── subscribers.py         # Subscribe & handle events
│
├── migrations/                # Alembic
│   └── versions/
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── requirements.txt
└── README.md
```

### Shared Libraries

```
shared/
├── __init__.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py          # Async connection pool
│   ├── base.py                # Base SQLAlchemy model
│   └── session.py             # Session management
│
├── eventbus/
│   ├── __init__.py
│   ├── client.py              # EventBus client
│   ├── publisher.py           # Publishing
│   └── subscriber.py          # Subscribing
│
├── orchestrator/
│   ├── __init__.py
│   └── client.py              # Service registration
│
├── auth/
│   ├── __init__.py
│   ├── jwt.py                 # JWT handling
│   └── permissions.py         # RBAC
│
├── models/
│   ├── __init__.py
│   └── common.py              # Common Pydantic models
│
├── utils/
│   ├── __init__.py
│   ├── logging.py             # Structured logging
│   ├── metrics.py             # Prometheus metrics (from governance)
│   ├── audit.py               # Audit logger (from governance)
│   └── cache.py               # Redis cache helper
│
└── config.py                  # Base configuration
```

---

## 📝 MIGRATION STEPS

### Phase 1: Shared Libraries ✅

**Create reusable components first (other services depend on these)**

1. **Database Connection** (`shared/database/`)
   - [ ] connection.py - AsyncPG pool setup
   - [ ] base.py - Base SQLAlchemy model
   - [ ] session.py - Async session management

2. **EventBus Client** (`shared/eventbus/`)
   - [ ] client.py - EventBus HTTP client
   - [ ] publisher.py - Event publishing helper
   - [ ] subscriber.py - Event subscription helper

3. **Configuration** (`shared/config.py`)
   - [ ] Base Settings class (Pydantic Settings)
   - [ ] Environment variables management
   - [ ] Service discovery config

4. **Utilities** (`shared/utils/`)
   - [ ] audit.py - Копировать из governance/audit_logger.py
   - [ ] metrics.py - Копировать из governance/cache_metrics.py
   - [ ] logging.py - Structured JSON logging
   - [ ] cache.py - Redis helper

5. **Common Models** (`shared/models/`)
   - [ ] common.py - Shared Pydantic models (Event, HealthCheck, etc.)

### Phase 2: Learning Service Migration 🎓

**Target:** `/Users/MD/AI-Platform-ISO/platform-services/learning-service/`

#### Step 1: Models
- [ ] Copy `database/models.py` → `models/database.py`
- [ ] Extract Pydantic models from main.py → `models/domain.py`
- [ ] Create request/response schemas → `api/schemas.py`

#### Step 2: Repositories
- [ ] Create `repositories/training_repository.py`
  - CRUD for TrainingProgram
  - CRUD for TrainingEnrollment
  - CRUD for CompetencyAssessment
  - CRUD for AwarenessCampaign
  - CRUD for TrainingTemplate

- [ ] Create `repositories/gamification_repository.py`
  - UserAchievement CRUD
  - Points, streaks, leaderboard queries

#### Step 3: Services (Business Logic)
- [ ] Create `services/training_service.py`
  - Program management logic
  - Enrollment workflow logic
  - Assessment logic
  - Competency gap analysis

- [ ] Create `services/gamification_service.py`
  - Points calculation
  - Achievement checking
  - Leaderboard generation
  - Streak tracking

- [ ] Create `services/awareness_service.py`
  - Campaign management
  - Campaign execution logic

#### Step 4: Workflows Integration
- [ ] Keep `workflows/training_workflow.py` (state machine)
- [ ] Keep `workflows/gamification_workflow.py`
- [ ] Integrate with workflow-intelligence:
  - Wrap enrollment workflow в WorkflowEngine
  - Add AI advisor для training recommendations
  - Case collection для successful trainings

#### Step 5: API Routes
- [ ] Create `api/routes.py` with all endpoints:
  - Training Programs: CRUD, start, publish, archive
  - Enrollments: create, progress, complete, assess, certify
  - Competency: assessments, gap analysis
  - Awareness: campaigns
  - Templates: library
  - Gamification: points, achievements, leaderboard

#### Step 6: Events
- [ ] Create `events/publishers.py`
  - training.program.created
  - training.enrollment.started
  - training.enrollment.completed
  - training.achievement.earned

- [ ] Create `events/subscribers.py`
  - Listen to governance events (if needed)
  - Listen to user events (if needed)

#### Step 7: Main App
- [ ] Create clean `main.py`:
  - FastAPI app setup
  - CORS middleware
  - Router включение
  - Lifespan (startup/shutdown)
  - Service registration

#### Step 8: Configuration
- [ ] Create `config.py`
  - Extend shared/config.py
  - Learning-specific settings

#### Step 9: Tests
- [ ] Copy existing tests if any
- [ ] Create unit tests for services
- [ ] Create integration tests for API

### Phase 3: Governance Service Migration 🏛️

**Target:** `/Users/MD/AI-Platform-ISO/platform-services/governance-service/`

#### Step 1: Models
- [ ] Copy `database/models.py` → `models/database.py`
- [ ] Extract Pydantic from main.py → `models/domain.py`
- [ ] Copy `domain_schemas.py` → `models/domain_intelligence.py`

#### Step 2: Repositories
- [ ] Create `repositories/context_repository.py`
- [ ] Create `repositories/leadership_repository.py`
- [ ] Create `repositories/policy_repository.py`
- [ ] Create `repositories/objectives_repository.py`
- [ ] Create `repositories/scope_repository.py`

#### Step 3: Services
- [ ] Create `services/context_service.py` (Clause 4)
- [ ] Create `services/leadership_service.py` (Clause 5)
- [ ] Create `services/policy_service.py`
- [ ] Create `services/objectives_service.py`
- [ ] Create `services/scope_service.py`
- [ ] Copy `domain_api.py` → `services/domain_intelligence_service.py`
- [ ] Copy `ai_domain_integration.py` → `services/ai_integration_service.py`

#### Step 4: Workflows
- [ ] Copy `workflows/governance_workflows.py`
- [ ] Integrate with workflow-intelligence:
  - Policy approval workflow
  - Objectives workflow
  - Scope definition workflow

#### Step 5: API Routes
- [ ] Create `api/routes.py` with all endpoints
- [ ] Create `api/domain_routes.py` (domain intelligence endpoints)

#### Step 6: Events
- [ ] Create `events/publishers.py`
  - governance.organization.created
  - governance.policy.approved
  - governance.objectives.set

- [ ] Create `events/subscribers.py`
  - Listen to relevant events

#### Step 7: Main App
- [ ] Create clean `main.py`

#### Step 8: Configuration
- [ ] Create `config.py`

#### Step 9: Tests
- [ ] Migrate tests

### Phase 4: Integration & Testing 🔗

- [ ] Test service-to-service communication
- [ ] Test EventBus integration
- [ ] Test workflow-intelligence integration
- [ ] Test shared libraries
- [ ] End-to-end testing

### Phase 5: Documentation 📚

- [ ] README for learning-service
- [ ] README for governance-service
- [ ] API documentation (OpenAPI)
- [ ] Integration guide
- [ ] Deployment guide

---

## 🔧 TECHNICAL DECISIONS

### 1. Workflow Integration Strategy

**Current:** Custom state machines in each service
**Target:** Wrap with workflow-intelligence for:
- Context-aware AI advice
- Case collection & learning
- Benchmarking
- Event-driven architecture

**Example:**
```python
# In learning-service
from workflow_intelligence import WorkflowEngine
from workflows.training_workflow import TrainingStateMachine

# Wrap existing state machine
training_workflow = WorkflowEngine.from_existing_state_machine(
    module="training",
    state_machine=TrainingStateMachine,
    storage_adapter=storage
)

# Now has:
# - Events
# - Context for AI
# - Gap analysis
# - Case collection
```

### 2. EventBus Integration

**Current:** Hardcoded URLs, manual HTTP calls
**Target:** Shared EventBus client

```python
# shared/eventbus/client.py
from shared.eventbus import EventBusClient

eventbus = EventBusClient(url=settings.EVENTBUS_URL)

# Publish
await eventbus.publish(
    topic="training.enrollment.completed",
    data={"enrollment_id": enrollment_id}
)

# Subscribe
@eventbus.subscribe("governance.organization.created")
async def on_organization_created(event):
    # Handle event
    pass
```

### 3. Database Connection

**Current:** Per-service connection setup
**Target:** Shared connection pool

```python
# shared/database/connection.py
from shared.database import get_db_pool, get_session

# In service
async with get_session() as session:
    result = await repository.get_training(session, training_id)
```

### 4. Configuration Management

**Current:** Hardcoded constants
**Target:** Environment-based config

```python
# shared/config.py
class BaseSettings(BaseSettings):
    SERVICE_NAME: str
    DATABASE_URL: str
    EVENTBUS_URL: str
    REDIS_URL: str
    # ...

# learning-service/config.py
class LearningSettings(BaseSettings):
    SERVICE_NAME: str = "learning"
    SERVICE_PORT: int = 8021
    # Learning-specific settings
```

---

## ⚠️ CRITICAL: DON'T LOSE ANYTHING

### Learning Service - Must Preserve:

✅ **Enrollment State Machine:**
```python
# All 8 states and transitions
States: draft, submitted, approved, in_progress,
        completed, assessed, certified, archived

# State transition logic
can_transition(), get_next_state(), validate_transition()
```

✅ **Gamification System:**
```python
# Points calculation
calculate_points(action_category, metadata)

# Achievements
check_achievements(user_id, total_points, completed_trainings)

# Leaderboard
get_leaderboard_rank(user_id, tenant_id)
```

✅ **All Validation Logic:**
```python
validate_enrollment_data()
validate_progress_update()
validate_assessment_score()
can_start_training()
can_complete_training()
can_issue_certification()
```

✅ **All Business Rules:**
- Passing score requirements
- Certification criteria
- Competency level calculations
- Gap analysis logic

### Governance Service - Must Preserve:

✅ **Domain Intelligence:**
```python
# All domain intelligence logic from domain_api.py
- get_intelligent_suggestions()
- get_iso_recommendations()
- get_bci_best_practices()
```

✅ **AI Integration:**
```python
# ai_domain_integration.py
- AI-powered recommendations
- Context analysis
- Pattern recognition
```

✅ **Audit Logging:**
```python
# audit_logger.py
- All audit trail functionality
- Compliance logging
```

✅ **Cache & Metrics:**
```python
# cache_metrics.py
- Performance monitoring
- Cache hit rates
- Response time tracking
```

✅ **All Workflows:**
```python
# governance_workflows.py
- Policy approval workflow
- Objectives workflow
- Scope definition workflow
```

---

## 📈 SUCCESS CRITERIA

### Must Have:
- [ ] ✅ All business logic migrated (0% loss)
- [ ] ✅ All workflows working
- [ ] ✅ All endpoints functional
- [ ] ✅ All tests passing
- [ ] ✅ Stubs removed (real EventBus, real DB, real config)
- [ ] ✅ Clean architecture (models/api/services/repositories/events)
- [ ] ✅ Shared libraries working
- [ ] ✅ Services can communicate
- [ ] ✅ Documentation complete

### Nice to Have:
- [ ] Workflow-intelligence integrated
- [ ] AI advisor working
- [ ] Case collection active
- [ ] Monitoring & metrics
- [ ] Performance optimization

---

## 🚀 EXECUTION ORDER

1. **Week 1 Day 1-2:** Shared Libraries
2. **Week 1 Day 3-5:** Learning Service Migration
3. **Week 2 Day 1-3:** Governance Service Migration
4. **Week 2 Day 4-5:** Integration & Testing
5. **Week 3:** Polish, documentation, deployment

---

## 📞 NEXT STEPS

**Ready to execute?**

Choose approach:
1. **Big Bang:** Migrate everything at once (risky)
2. **Incremental:** One service at a time (safer) ✅ RECOMMENDED
3. **Hybrid:** Shared libs first, then services in parallel

**Recommended: Incremental Approach**
1. Start with Shared Libraries
2. Then Learning Service (smaller, simpler)
3. Then Governance Service (larger, more complex)
4. Finally integrate & test

---

**Ready to start? Lets do Phase 1: Shared Libraries! 🚀**

Created by Claude & MD, October 3, 2025
