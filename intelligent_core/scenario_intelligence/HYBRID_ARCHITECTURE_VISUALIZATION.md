# 🏗️ Гибридная Архитектура Scenario Intelligence

## ✅ Да, мы выбрали ПРАВИЛЬНО!

Наша гибридная модель объединяет **лучшее из 6 industry-standard подходов**:

1. **BPMN 2.0** - иерархия и Call Activity
2. **Event Storming (DDD)** - события и pub/sub
3. **ISO 22301** - compliance и evidence
4. **Google SRE** - runbooks и SLO
5. **Netflix Chaos Engineering** - chaos experiments
6. **AWS Well-Architected** - 6 pillars

---

## 📐 Полная Архитектура Системы

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SCENARIO INTELLIGENCE SYSTEM                             │
│                   (intelligent-core/scenario-intelligence)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
         ┌──────────▼──────────┐            ┌──────────▼──────────┐
         │   SCENARIO ENGINE   │            │    API LAYER        │
         │   (Orchestrator)    │            │   (FastAPI)         │
         └──────────┬──────────┘            └──────────┬──────────┘
                    │                                   │
         ┌──────────┴────────────────┐                │
         │                           │                │
         │  Координирует 4 движка:  │                │
         │  1. Call Engine           │                │
         │  2. Event Engine          │                │
         │  3. Chaos Engine          │                │
         │  4. Compliance Engine     │                │
         └───────────────────────────┘                │
                                                       │
┌──────────────────────────────────────────────────────┴────────────────────┐
│                         ИНТЕГРАЦИЯ С ПЛАТФОРМОЙ                            │
└────────────────────────────────────────────────────────────────────────────┘
         │                    │                    │                    │
         │                    │                    │                    │
    ┌────▼────┐          ┌───▼────┐          ┌────▼────┐         ┌────▼────┐
    │EventBus │          │Database│          │ Qdrant  │         │Learning │
    │(Existing)          │(Supabase)         │  RAG    │         │ System  │
    └─────────┘          └────────┘          └─────────┘         └─────────┘
         │                    │                    │                    │
infrastructure/       infrastructure/      intelligent-core/    intelligent-core/
   eventbus              database           ai-foundation/rag    ai-foundation/
                                                                 learning-knowledge
```

---

## 🔄 4-Уровневая Иерархия (BPMN 2.0)

```
Level 4: USER                    ┌─────────────────────────┐
(E2E Workflows)                  │  BIA Complete Workflow  │
                                 │  User Authentication    │
                                 └───────────┬─────────────┘
                                             │ Call Activity
                                             ▼
Level 3: INTER-SYSTEM            ┌─────────────────────────┐
(System Integration)             │  BIA ↔ AI Integration   │
                                 │  Platform ↔ AI Office   │
                                 └───────────┬─────────────┘
                                             │ Call Activity
                                             ▼
Level 2: SUBSYSTEM               ┌─────────────────────────┐
(Module Groups)                  │  AI Office Subsystem    │
                                 │  Platform Services      │
                                 └───────────┬─────────────┘
                                             │ Call Activity
                                             ▼
Level 1: MODULE                  ┌─────────────────────────┐
(Individual Services)            │  Vault Module           │
                                 │  BIA Service Module     │
                                 └─────────────────────────┘
```

---

## 🎯 Event-Driven Architecture (Event Storming)

```
┌──────────────────────────────────────────────────────────────────────┐
│                     EVENT-DRIVEN FLOW                                 │
└──────────────────────────────────────────────────────────────────────┘

    Scenario Execution
           │
           ▼
    ┌──────────────┐
    │  COMMANDS    │──────────────────┐
    └──────────────┘                  │
           │                          │
           ▼                          ▼
    ┌──────────────┐          ┌──────────────┐
    │ Execute      │          │ Emit Events  │
    │ Scenario     │          │ (Async)      │
    └──────┬───────┘          └──────┬───────┘
           │                         │
           ▼                         ▼
    ┌──────────────┐          ┌──────────────┐
    │ DOMAIN       │          │ EventBus     │───► scenario.execution.started
    │ EVENTS       │          │ (Existing)   │───► scenario.execution.completed
    └──────────────┘          └──────────────┘───► scenario.execution.failed
           │                         │            ───► scenario.pattern.detected
           │                         │            ───► scenario.learning.updated
           ▼                         │
    ┌──────────────┐                 │
    │ AGGREGATES   │                 │
    │ (Scenarios,  │◄────────────────┘
    │  Executions) │
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │ POLICIES     │──► Trigger next scenarios
    │ (Reactions)  │──► Update statistics
    └──────────────┘──► Send notifications
```

---

## 🔬 Chaos Engineering Flow (Netflix)

```
┌────────────────────────────────────────────────────────────────┐
│              CHAOS EXPERIMENT EXECUTION                         │
└────────────────────────────────────────────────────────────────┘

1. Define Hypothesis
   "System handles vault unavailability gracefully"
           │
           ▼
2. Measure Steady State (Before)
   ┌─────────────────────────┐
   │ api_success_rate: 0.99  │
   │ latency_p95: 200ms      │
   └─────────────┬───────────┘
                 │
                 ▼
3. Progressive Rollout
   Phase 1: 10% traffic ───► Inject chaos (latency: 5000ms)
                 │
                 ├─► Monitor metrics
                 │
                 ├─► Check abort conditions
                 │   (error_rate > 0.05 → ABORT)
                 │
   Phase 2: 25% traffic ───► Continue if safe
                 │
                 ▼
4. Measure Steady State (After)
   ┌─────────────────────────┐
   │ api_success_rate: 0.97  │ ◄─ Still acceptable?
   │ latency_p95: 800ms      │
   └─────────────┬───────────┘
                 │
                 ▼
5. Validate Hypothesis
   ✅ System degraded gracefully (fallback worked)
   ❌ System failed (hypothesis false)
```

---

## 📋 Compliance Flow (ISO 22301)

```
┌────────────────────────────────────────────────────────────────┐
│               ISO 22301 COMPLIANCE ENGINE                       │
└────────────────────────────────────────────────────────────────┘

Scenario Execution
     │
     ▼
┌─────────────────┐
│ Check Clauses   │
│ 7.5.3, 8.2.2    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate        │
│ Evidence        │
│ - execution_log │
│ - test_report   │
│ - screenshot    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Apply Retention │
│ Policy          │
│ 7 years         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐          ┌─────────────────┐
│ Store Evidence  │─────────►│ evidence_vault  │
│ (PostgreSQL)    │          │ (table)         │
└─────────────────┘          └─────────────────┘
```

---

## 💾 Storage Architecture (Hybrid)

```
┌──────────────────────────────────────────────────────────────────┐
│                    HYBRID STORAGE SYSTEM                          │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   FILE-BASED    │     │   POSTGRESQL     │     │   QDRANT RAG     │
│   (Git/YAML)    │────►│   (Supabase)     │────►│  (Embeddings)    │
└─────────────────┘     └──────────────────┘     └──────────────────┘
         │                       │                         │
         │                       │                         │
    Version Control         Persistent Store       Semantic Search
    Human-readable         ACID Transactions        Similar scenarios
    Easy to edit           Statistics triggers      Pattern matching
         │                       │                         │
         ▼                       ▼                         ▼
    scenarios/             scenario_intelligence     scenarios (collection)
    ├─ level1/            ├─ scenarios                ├─ embeddings
    ├─ level2/            ├─ executions               ├─ metadata
    ├─ level3/            ├─ statistics               └─ vectors
    └─ level4/            ├─ patterns
                          ├─ predictions
                          └─ evidence_vault
```

---

## 🧠 Learning & Intelligence Flow

```
┌────────────────────────────────────────────────────────────────┐
│                LEARNING & INTELLIGENCE SYSTEM                   │
└────────────────────────────────────────────────────────────────┘

    Scenario Execution
           │
           ▼
    ┌──────────────┐
    │ Record       │
    │ Execution    │──────► PostgreSQL executions table
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Update       │
    │ Statistics   │──────► PostgreSQL statistics table (trigger)
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Detect       │
    │ Patterns     │──────► ML Pattern Detector [TODO]
    └──────┬───────┘        - Sequential patterns
           │                - Parallel patterns
           │                - Temporal patterns
           ▼
    ┌──────────────┐
    │ Predict      │
    │ Next         │──────► ML Predictor [TODO]
    └──────┬───────┘        - Based on history
           │                - Based on patterns
           │                - Confidence scoring
           ▼
    ┌──────────────┐
    │ Auto-        │
    │ Generate     │──────► Auto-Generator [TODO]
    └──────────────┘        - Template-based
                            - ML-based
                            - Validated output
```

---

## 🔌 Integration Points

### 1. EventBus Integration (infrastructure/eventbus)

```python
from infrastructure.eventbus import create_eventbus, Event

# Use EXISTING EventBus
eventbus = create_eventbus('memory')  # or 'redis'

# Publish scenario events
event = Event.create(
    event_type='scenario.execution.completed',
    data={'scenario_id': 'xxx', 'status': 'success'},
    source='scenario-intelligence'
)
await eventbus.publish(event)
```

### 2. Database Integration (infrastructure/database)

```python
from infrastructure.database.managers.db_manager import DatabaseManager

# Use EXISTING DatabaseManager
db = ScenarioDatabaseManager()  # extends DatabaseManager
db.connect()

# Save to PostgreSQL
db.save_scenario(scenario)
db.save_execution(scenario_id, version, result, context)
stats = db.get_statistics(scenario_id)
```

### 3. AI Event Manager Integration

```python
# AI Event Manager subscribes to scenario events
# infrastructure/AI-office-infrastructure/ai-event-manager

await eventbus.subscribe(
    'scenario.execution.failed',
    handle_scenario_failure  # analyze and suggest fixes
)
```

---

## 🎭 Scenario Types Matrix

```
┌──────────────┬─────────────┬──────────────┬──────────────┬─────────────┐
│ Level        │ Functional  │ Chaos        │ Security     │ Workflow    │
├──────────────┼─────────────┼──────────────┼──────────────┼─────────────┤
│ 1 (Module)   │ ✅ Testing  │ ✅ Resilience│ ✅ Pen Test  │ ❌ N/A      │
│              │ individual  │ of module    │ of module    │             │
│              │ functions   │              │              │             │
├──────────────┼─────────────┼──────────────┼──────────────┼─────────────┤
│ 2 (Subsystem)│ ✅ Testing  │ ✅ Subsystem │ ✅ Multi-    │ ⚠️  Internal│
│              │ subsystem   │ failover     │ service auth │ workflows   │
│              │ integration │              │              │             │
├──────────────┼─────────────┼──────────────┼──────────────┼─────────────┤
│ 3 (Inter-    │ ✅ Cross-   │ ✅ Network   │ ✅ Cross-    │ ✅ Service  │
│    System)   │ system API  │ partitions   │ boundary auth│ orchestr.   │
├──────────────┼─────────────┼──────────────┼──────────────┼─────────────┤
│ 4 (User)     │ ⚠️  E2E     │ ❌ Too broad │ ✅ Auth flow │ ✅ Business │
│              │ functional  │              │              │ processes   │
└──────────────┴─────────────┴──────────────┴──────────────┴─────────────┘

✅ = Primary use case
⚠️  = Secondary use case
❌ = Not recommended
```

---

## 🚀 Execution Flow (Complete)

```
┌──────────────────────────────────────────────────────────────────────┐
│                    FULL EXECUTION FLOW                                │
└──────────────────────────────────────────────────────────────────────┘

1. API Request
   POST /scenarios/execute
        │
        ▼
2. Load Scenario
   Registry.get_scenario(id)
        │                              ┌──────────────┐
        ├─────────────────────────────►│ PostgreSQL   │
        │                              └──────────────┘
        ▼
3. Publish Event: scenario.execution.started
        │                              ┌──────────────┐
        ├─────────────────────────────►│ EventBus     │
        │                              └──────────────┘
        ▼
4. Execute Scenario (ScenarioEngine)
        │
        ├──► Call Engine ──────► Execute sub-scenarios (BPMN)
        │
        ├──► Event Engine ─────► Emit domain events (Event Storming)
        │
        ├──► Chaos Engine ─────► Inject chaos (Netflix)
        │
        └──► Compliance Engine ─► Check ISO compliance
        │
        ▼
5. Save Execution
        │                              ┌──────────────┐
        ├─────────────────────────────►│ PostgreSQL   │
        │                              │ - executions │
        │                              │ - statistics │ (auto-trigger)
        │                              └──────────────┘
        ▼
6. Publish Event: scenario.execution.completed
        │                              ┌──────────────┐
        ├─────────────────────────────►│ EventBus     │
        │                              └──────────────┘
        ▼
7. Learning
   ScenarioLearner.record_execution()
        │                              ┌──────────────┐
        ├─────────────────────────────►│ PostgreSQL   │
        │                              │ - patterns   │
        │                              │ - predictions│
        │                              └──────────────┘
        ▼
8. Return Result
   {status, duration, result, evidence}
```

---

## 📊 Почему Гибридная Модель ПРАВИЛЬНАЯ?

### ✅ Преимущества:

1. **BPMN 2.0** дает нам:
   - Четкую иерархию (4 уровня)
   - Call Activity для композиции
   - Boundary Events для обработки ошибок
   - Стандартную нотацию

2. **Event Storming** дает нам:
   - Асинхронную архитектуру
   - Domain Events для слабой связности
   - Event-driven реактивность
   - Масштабируемость

3. **ISO 22301** дает нам:
   - Автоматизацию compliance
   - Генерацию evidence
   - Retention policies
   - Audit trail

4. **Google SRE** дает нам:
   - Runbook-style execution
   - SLO/Error budget tracking
   - Toil reduction
   - Operational excellence

5. **Netflix Chaos** дает нам:
   - Hypothesis-driven testing
   - Progressive rollout
   - Steady state verification
   - Resilience validation

6. **AWS Well-Architected** дает нам:
   - 6 pillars (security, reliability, performance, cost, ops, sustainability)
   - Best practices
   - Review framework
   - Holistic view

### ❌ Если бы выбрали ОДНУ модель:

- **Только BPMN**: нет событий, нет chaos, нет compliance automation
- **Только Event Storming**: нет иерархии, сложнее композиция
- **Только ISO**: слишком формально, нет техн. деталей
- **Только SRE**: только operational, нет business процессов
- **Только Chaos**: только resilience testing, нет workflows
- **Только AWS**: слишком generic, нет domain-specific деталей

### 🎯 Гибридная модель = Best of All Worlds!

Каждый framework дополняет другие:
- BPMN структурирует
- Events связывают
- ISO обеспечивает compliance
- SRE операционализирует
- Chaos тестирует resilience
- AWS дает holistic view

---

## 🎓 Выводы

### ✅ Мы выбрали ПРАВИЛЬНО потому что:

1. **Максимальная гибкость** - можем использовать любой аспект любого framework
2. **Полнота покрытия** - нет пробелов (testing + operations + compliance + business)
3. **Industry standard** - используем проверенные подходы
4. **Расширяемость** - легко добавить новые аспекты
5. **Pragmatic** - берем только нужное из каждого framework

### 🚀 Следующие Шаги:

1. ✅ PostgreSQL integration - DONE (миграция применена)
2. ✅ EventBus integration - DONE (использует существующий EventBus)
3. 🔄 Создать 10-15 базовых сценариев
4. 🔄 Реализовать Pattern Detector (ML)
5. 🔄 Реализовать Predictor (ML)
6. 🔄 Добавить Qdrant RAG для семантического поиска

---

## 📞 Резюме

**Гибридная архитектура Scenario Intelligence - это правильный выбор!**

Она объединяет:
- ✅ Структуру (BPMN)
- ✅ События (Event Storming)
- ✅ Compliance (ISO 22301)
- ✅ Operations (SRE)
- ✅ Resilience (Netflix Chaos)
- ✅ Best Practices (AWS)

И интегрируется с СУЩЕСТВУЮЩЕЙ инфраструктурой:
- ✅ infrastructure/eventbus (EventBus)
- ✅ infrastructure/database (DatabaseManager)
- ✅ infrastructure/AI-office-infrastructure (AI Event Manager)

**Результат**: мощная, гибкая, расширяемая система сценарного интеллекта! 🎉
