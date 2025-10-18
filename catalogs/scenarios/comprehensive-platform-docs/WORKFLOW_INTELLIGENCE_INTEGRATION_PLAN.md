# Workflow Intelligence - Интеграция с Модульными Офисами

## 🔍 ЧТО УЖЕ ЕСТЬ В `/workflow_intelligence/`

### ✅ **ПОЛНАЯ РЕАЛИЗАЦИЯ:**

#### 1. **Core - Workflow Engine** (`/core/`)
```python
# workflow_engine.py
class WorkflowEngine:
    """
    Универсальный движок для ЛЮБЫХ workflows

    Возможности:
    - Оборачивает существующие state machines
    - Event publishing (EventBus integration)
    - Context generation для AI
    - Gap analysis (что не хватает)
    - Action validation
    - Audit trail
    """

    async def start(workflow_id, initial_data):
        # Запускает workflow

    async def execute_action(workflow_id, action, action_data):
        # Выполняет действие (add_process, analyze_impact, etc)
        # 1. Валидация
        # 2. State Machine переход
        # 3. Publish event
        # 4. Update storage

    async def get_context(workflow_id) -> WorkflowContext:
        # Полный контекст для AI:
        # - current_stage
        # - progress_percentage
        # - gaps (что не хватает)
        # - available_actions
        # - can_proceed_to_next_stage
```

#### 2. **State Machine** (`/core/state_machine.py`)
```python
class StateMachine:
    """
    Расширенная State Machine с:
    - State transitions с валидацией
    - Hooks (on_enter, on_exit, on_validate)
    - Rollback capability
    - Snapshots для recovery
    - Timeout support
    - Audit trail
    """

    def define_transition(from_state, to_state, condition, validators, ...):
        # Определяет переход

    async def transition_to(next_state, data):
        # Выполняет переход с валидацией
```

#### 3. **BIA Workflow Example** (`/workflows/bia_workflow.py`)
```python
class BIAStage:
    NOT_STARTED = "not_started"
    IDENTIFY_PROCESSES = "identify_processes"
    ANALYZE_DEPENDENCIES = "analyze_dependencies"
    ASSESS_IMPACT = "assess_impact"
    DETERMINE_RTO = "determine_rto"
    REVIEW_RESULTS = "review_results"
    COMPLETED = "completed"

class BIAWorkflowEngine(StateMachine):
    """
    BIA-специфичный workflow

    Transitions:
    - NOT_STARTED → IDENTIFY_PROCESSES
    - IDENTIFY_PROCESSES → ANALYZE_DEPENDENCIES (requires: min 3 processes)
    - ANALYZE_DEPENDENCIES → ASSESS_IMPACT (requires: dependencies mapped)
    - ASSESS_IMPACT → DETERMINE_RTO (requires: impacts assessed)
    - DETERMINE_RTO → REVIEW_RESULTS (requires: RTO/RPO defined)
    - REVIEW_RESULTS → COMPLETED (or back to IDENTIFY_PROCESSES)

    Validators:
    - _validate_processes(): min 3, required fields
    - _validate_dependencies(): min 2 per process
    - _validate_impacts(): all 4 types (financial, operational, reputational, regulatory)
    - _validate_rto(): RTO, RPO, MTPD, rationale
    """
```

#### 4. **AI Context Builder** (`/integration/ai_context_builder.py`)
```python
class AIContextBuilder:
    """
    Собирает ПОЛНЫЙ контекст для AI Advisor

    Объединяет:
    1. Workflow state (откуда, куда, что сделано)
    2. Similar successful cases (из Case Library)
    3. Industry benchmarks
    4. Gaps (что не хватает)
    5. Trending patterns
    6. Comparison to benchmarks
    """

    async def build_full_context(org_context, user_message) -> dict:
        return {
            "workflow": workflow_context,
            "similar_cases": [...],  # 3 successful cases
            "benchmarks": {...},     # industry averages
            "comparison": {...},     # how we compare
            "trending": [...],       # what's trending
            "prompt": "..."          # formatted для LLM
        }
```

#### 5. **Case Library** (`/case_library/`)
```python
# collector.py
class CaseCollector:
    """
    Автоматически собирает cases из workflow events

    Слушает:
    - *.workflow.action.taken
    - *.workflow.step.completed
    - *.workflow.challenge.encountered
    - *.workflow.completed

    Когда workflow завершен:
    - Compile all events → journey
    - Extract patterns с AI
    - Create embeddings для semantic search
    - Trigger ML retraining
    """

# repository.py
class CaseRepository:
    """
    Поиск и анализ cases

    Методы:
    - find_similar_cases(industry, module, stage)
    - get_benchmarks(industry, size, module)
    - compare_to_benchmarks(current_metrics, industry)
    - get_trending_patterns(module, days=30)
    """
```

#### 6. **EventBus Integration** (`/integration/eventbus_publisher.py`)
```python
class EventBusPublisher:
    """
    Публикация событий в Redis EventBus

    События:
    - workflow.started
    - workflow.stage.changed
    - workflow.action.taken
    - workflow.completed
    - workflow.validation.failed
    """
```

---

## 🏢 **КАК ЭТО ИНТЕГРИРУЕТСЯ С ОФИСАМИ**

### **Архитектура:**

```
BCM Office (например, Risk Office)
│
├── /ai/                           # AI компоненты
│   ├── specialist.py              # Диалог с пользователем
│   ├── expert.py                  # Бизнес-логика + Tools
│   └── organ.py                   # LLM анализ
│
├── /services/
│   └── risk_service.py            # Бизнес-методы (assess_risk, etc)
│
├── /workflow/
│   └── risk_workflow.py           # Risk State Machine
│       ├── Extends: StateMachine (from workflow_intelligence)
│       ├── Stages: identify_risks → analyze → FAIR → treatment → completed
│       └── Validators: validate each stage
│
├── /tools/
│   └── risk_tools.py              # DB operations
│
└── /events/
    ├── publishers.py              # Publish to EventBus
    └── subscribers.py             # Subscribe to other offices
```

---

## 🔌 **ИНТЕГРАЦИЯ - ПОШАГОВО**

### **Шаг 1: Risk Office использует Workflow Intelligence**

```python
# risk/workflow/risk_workflow.py
from workflow_intelligence.core.state_machine import StateMachine
from workflow_intelligence.core.workflow_engine import WorkflowEngine

class RiskStage:
    IDENTIFY_RISKS = "identify_risks"
    ANALYZE_LIKELIHOOD = "analyze_likelihood"
    CALCULATE_IMPACT = "calculate_impact"
    FAIR_ANALYSIS = "fair_analysis"
    TREATMENT_PLANNING = "treatment_planning"
    COMPLETED = "completed"

class RiskWorkflow(StateMachine):
    """Risk workflow extends базовый StateMachine"""

    def __init__(self, risk_id, org_context):
        super().__init__(workflow_id=risk_id, initial_state=RiskStage.IDENTIFY_RISKS)
        self.org_context = org_context
        self._setup_transitions()

    def _setup_transitions(self):
        # IDENTIFY_RISKS → ANALYZE_LIKELIHOOD
        self.define_transition(
            from_state=RiskStage.IDENTIFY_RISKS,
            to_state=RiskStage.ANALYZE_LIKELIHOOD,
            condition=lambda data: len(data.get('risks', [])) >= 1,
            validators=[self._validate_risks],
            required_data=['risks'],
            on_enter=self._on_start_analysis
        )

        # ANALYZE_LIKELIHOOD → CALCULATE_IMPACT
        self.define_transition(
            from_state=RiskStage.ANALYZE_LIKELIHOOD,
            to_state=RiskStage.CALCULATE_IMPACT,
            validators=[self._validate_likelihood],
            required_data=['risks', 'likelihood_scores']
        )

        # ... остальные transitions

    def _validate_risks(self, data):
        """Валидатор для рисков"""
        risks = data.get('risks', [])
        if len(risks) < 1:
            raise ValidationError("Need at least 1 risk identified")

        for risk in risks:
            if not risk.get('description'):
                raise ValidationError("Risk must have description")
```

### **Шаг 2: RiskExpert использует Workflow Context**

```python
# risk/ai/expert.py
from workflow_intelligence.integration.ai_context_builder import AIContextBuilder

class RiskExpert:
    def __init__(self, tools, organ, case_library, workflow_engine):
        self.tools = tools
        self.organ = organ
        self.case_library = case_library
        self.workflow = workflow_engine

        # AI Context Builder
        self.ai_context = AIContextBuilder(
            workflow_engine=self.workflow,
            case_repository=self.case_library
        )

    async def assess_risk(self, process_id, org_context):
        """Оценка риска с полным контекстом"""

        # 1. Build FULL context для AI
        context = await self.ai_context.build_full_context(
            org_context=org_context,
            user_message="Assess risks for this process"
        )

        # context содержит:
        # - workflow state (где мы в Risk Workflow)
        # - similar successful risk assessments
        # - industry benchmarks (average risk scores)
        # - gaps (что не хватает для следующего stage)
        # - trending patterns (что успешно работало недавно)

        # 2. Get process data (Tools)
        process = await self.tools.get_process(process_id)
        dependencies = await self.tools.get_dependencies(process_id)

        # 3. LLM Analysis (Organ) с ПОЛНЫМ контекстом
        analysis = await self.organ.analyze({
            "process": process,
            "dependencies": dependencies,
            "workflow_context": context,  # ← ВОТ ОНО!
            "similar_cases": context["similar_cases"],
            "benchmarks": context["benchmarks"]
        })

        # 4. Save to DB
        await self.tools.save_risk_assessment(analysis)

        # 5. Execute workflow action (автоматически publish event)
        await self.workflow.execute_action(
            workflow_id=org_context['risk_workflow_id'],
            action="risk_assessed",
            action_data=analysis
        )

        return analysis
```

### **Шаг 3: EventBus связывает офисы**

```python
# risk/events/publishers.py
from workflow_intelligence.integration.eventbus_publisher import EventBusPublisher

eventbus = EventBusPublisher()

# В RiskService:
await eventbus.publish("risk.assessed", {
    "org_id": org_id,
    "process_id": process_id,
    "risk_score": 85,
    "severity": "high"
})

# bia/events/subscribers.py
from infrastructure.eventbus import EventBusClient

eventbus = EventBusClient()

@eventbus.subscribe("risk.assessed")
async def on_risk_assessed(event):
    """Когда Risk Office оценил риск → BIA Office связывает с процессом"""
    process_id = event.data["process_id"]
    risk_score = event.data["risk_score"]

    # Update BIA process with risk info
    await bia_service.update_process_risk(process_id, risk_score)

    # Trigger BIA workflow action if needed
    if risk_score > 80:
        await bia_workflow.execute_action(
            workflow_id=bia_id,
            action="high_risk_identified",
            action_data=event.data
        )
```

### **Шаг 4: Case Collector собирает ВСЁ**

```python
# workflow_intelligence/case_library/collector.py автоматически:

# 1. Слушает ВСЕ события:
@eventbus.subscribe("*.workflow.*")
async def collect_event(event):
    await db.workflow_events.insert(event)

# 2. Когда workflow завершен:
@eventbus.subscribe("*.workflow.completed")
async def create_case(event):
    # Get all events for this workflow
    events = await db.workflow_events.filter(workflow_id=event.workflow_id)

    # Build journey
    journey = build_journey(events)

    # AI extracts patterns
    patterns = await ai_extract_patterns(journey)

    # Create case
    case = WorkflowCase(
        module="risk",  # ← office name
        journey=journey,
        patterns=patterns,
        success=True
    )

    await db.cases.insert(case)

    # Create embedding for semantic search
    await vector_db.upsert(case)
```

---

## ✅ **ПРЕИМУЩЕСТВА ИНТЕГРАЦИИ**

### 1. **Офисы получают готовую инфраструктуру:**
- ✅ State Machine с валидацией
- ✅ Event publishing автоматом
- ✅ Context для AI из коробки
- ✅ Case Library автоматически собирает опыт
- ✅ Audit trail бесплатно

### 2. **Workflow Intelligence знает о всех офисах:**
- ✅ Case Library собирает cases из ВСЕХ офисов
- ✅ ML обучается на данных ВСЕХ офисов
- ✅ Benchmarks по всем модулям (risk, bia, compliance...)

### 3. **Офисы работают вместе через Events:**
```
Risk Office: "risk.high_severity_detected"
    ↓
BIA Office: "Обновим критичность процесса"
    ↓
Compliance Office: "Проверим требования для high-risk processes"
    ↓
Planning Office: "Создадим emergency plan"
```

---

## 🎯 **ИТОГО:**

### **ЧТО ДЕЛАТЬ:**

1. **Каждый офис создаёт свой Workflow:**
   ```python
   class RiskWorkflow(StateMachine)  # extends из workflow_intelligence
   class BIAWorkflow(StateMachine)
   class ComplianceWorkflow(StateMachine)
   # и т.д.
   ```

2. **Каждый Expert использует AIContextBuilder:**
   ```python
   context = await ai_context_builder.build_full_context(org, msg)
   # Получает: workflow state + similar cases + benchmarks
   ```

3. **Все офисы публикуют события:**
   ```python
   await eventbus.publish("risk.assessed", {...})
   await eventbus.publish("bia.completed", {...})
   ```

4. **Case Library собирает автоматически:**
   - Подписан на `*.workflow.*`
   - Создаёт cases когда `*.workflow.completed`
   - ML переобучается

---

## 🚀 **НЕ НУЖНО ДУБЛИРОВАТЬ!**

**Workflow Intelligence УЖЕ ЕСТЬ!** Офисы просто **ИСПОЛЬЗУЮТ**:
- Наследуют StateMachine
- Используют AIContextBuilder
- Публикуют в EventBus
- Case Library работает автоматом

**Это и есть Intelligent Platform!** 🧠
