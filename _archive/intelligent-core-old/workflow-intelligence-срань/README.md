# 🧠 WORKFLOW INTELLIGENCE ENGINE

**Version:** 1.0.0
**Created:** October 3, 2025
**Philosophy:** Self-Learning Platform with Managed Autonomy

---

## 🎯 ЧТО ЭТО?

**Workflow Intelligence Engine** - это мозг платформы, который:

1. **Понимает контекст** - знает где пользователь в workflow и что делать дальше
2. **Учится на опыте** - каждый успешный case → знания для новых пользователей
3. **Управляемая автономия** - AI свободен в творчестве, но в рамках правил
4. **Предсказывает проблемы** - ML модели предупреждают о рисках

---

## 🏗️ АРХИТЕКТУРА

```
┌─────────────────────────────────────────────────────────────┐
│                    USER работает в модуле                   │
│              (BIA, Risk, Planning, Compliance)              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              WORKFLOW STATE MACHINE (Core)                  │
│  - Отслеживает текущую стадию                               │
│  - Знает допустимые переходы                                │
│  - Валидирует данные                                        │
│  - Публикует события                                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
┌──────────────────┐  ┌────────────┐  ┌──────────────────┐
│  CASE LIBRARY    │  │ GOVERNANCE │  │   AI ADVISOR     │
│                  │  │            │  │                  │
│ - Собирает cases │  │ - Safety   │  │ - Контекстные    │
│ - Находит similar│  │ - Rules    │  │   советы         │
│ - Benchmarking   │  │ - Creative │  │ - Рекомендации   │
│ - ML Training    │  │   Zones    │  │ - Предсказания   │
└──────────────────┘  └────────────┘  └──────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  ML PREDICTOR  │
                    │                │
                    │ - Success prob │
                    │ - Duration     │
                    │ - Risk factors │
                    └────────────────┘
```

---

## 📦 МОДУЛИ

### 1️⃣ **Core** - State Machine Engine
- `workflow_engine.py` - Универсальный движок для любых workflows
- `state_machine.py` - Базовый State Machine класс
- `transitions.py` - Управление переходами
- `validators.py` - Валидация данных и бизнес-логики
- `events.py` - Event publishing для интеграции

### 2️⃣ **Case Library** - Self-Learning
- `collector.py` - Автоматический сбор успешных cases
- `repository.py` - Хранение и поиск cases (PostgreSQL + Vector DB)
- `analyzer.py` - Анализ patterns и best practices
- `benchmarks.py` - Статистика и сравнение
- `models.py` - Data models для cases

### 3️⃣ **AI Advisor** - Context-Aware Intelligence
- `context_advisor.py` - AI который понимает workflow контекст
- `prompt_builder.py` - Построение промптов с контекстом
- `recommendation_engine.py` - Генерация рекомендаций
- `action_suggester.py` - Предложение следующих шагов

### 4️⃣ **Governance** - Managed Autonomy
- `rules_engine.py` - Управление правилами и ограничениями
- `safety_rails.py` - Safety boundaries для AI
- `creative_zones.py` - Определение зон творчества
- `checkpoints.py` - Обязательные точки валидации
- `escalation.py` - Когда нужен человек

### 5️⃣ **ML** - Predictive Intelligence
- `workflow_predictor.py` - Предсказание success и duration
- `risk_detector.py` - Обнаружение факторов риска
- `pattern_recognizer.py` - Распознавание паттернов
- `training_pipeline.py` - Обучение моделей на case library

### 6️⃣ **Schemas** - Data Models
- `workflow_schema.py` - Схемы workflow definitions
- `case_schema.py` - Схемы cases
- `governance_schema.py` - Схемы правил
- `ai_schema.py` - Схемы для AI responses

---

## 🚀 КАК ИСПОЛЬЗОВАТЬ

### Пример 1: BIA Workflow с AI Advisor

```python
from workflow_intelligence.core import WorkflowEngine
from workflow_intelligence.ai import ContextAdvisor
from workflow_intelligence.case_library import CaseLibrary

# 1. Инициализация
workflow = WorkflowEngine(
    module="bia",
    workflow_definition="bia_process",  # Загружает из YAML
    tenant_id="acme-corp"
)

advisor = ContextAdvisor(
    workflow_engine=workflow,
    case_library=CaseLibrary()
)

# 2. Пользователь начинает BIA
bia_id = "bia-123"
await workflow.start(bia_id)

# 3. AI Advisor даёт контекстные советы
advice = await advisor.get_contextual_advice(
    workflow_id=bia_id,
    user_message="Как начать анализ критичности?"
)

print(advice["message"])
# -> "Вы на стадии 'identify_processes'. У вас 2 процесса, нужно минимум 3.
#     На основе опыта похожих организаций (healthcare, medium size),
#     рекомендую начать с Emergency Department и Patient Records.
#     Вот 8 типичных процессов для вашей индустрии..."

# 4. Пользователь добавляет процессы
await workflow.execute_action(
    workflow_id=bia_id,
    action="add_process",
    data={"name": "Emergency Department", "tier": 1}
)

# 5. Workflow автоматически проверяет можно ли двигаться дальше
context = await workflow.get_context(bia_id)

if context["can_proceed_to_next_stage"]:
    print(f"✅ Готово к переходу на: {context['next_stage']}")
else:
    print(f"❌ Не хватает: {context['gaps']}")

# 6. AI предсказывает проблемы
prediction = await advisor.predict_outcome(bia_id)
print(f"Success probability: {prediction['success_prob']}")
print(f"Estimated duration: {prediction['duration_days']} days")
print(f"Risk factors: {prediction['risk_factors']}")
```

### Пример 2: Создание нового Workflow Definition

```python
from workflow_intelligence.governance import WorkflowDefinitionBuilder

# Автоматическая генерация workflow через AI
builder = WorkflowDefinitionBuilder()

workflow_def = await builder.generate(
    role="Risk Assessment Specialist",
    responsibilities=[
        "Identify threats and vulnerabilities",
        "Calculate likelihood and impact",
        "Prioritize risks",
        "Recommend mitigation strategies"
    ],
    compliance_standards=["ISO 27001", "NIST CSF"],
    example_scenarios=[
        {
            "input": {"threat": "Ransomware attack", "asset": "Customer DB"},
            "expected_output": {"likelihood": "high", "impact": "critical", "priority": 1}
        }
    ]
)

# Сохраняется в workflows/definitions/risk_assessment.yaml
await builder.save(workflow_def, "risk_assessment")
```

### Пример 3: Обучение на Case Library

```python
from workflow_intelligence.case_library import CaseCollector
from workflow_intelligence.ml import WorkflowPredictor

# 1. Когда пользователь завершает workflow
@eventbus.subscribe("bia.workflow.completed")
async def on_bia_completed(event):
    collector = CaseCollector()

    # Автоматически создаёт case
    case = await collector.create_case(
        workflow_id=event.data["workflow_id"],
        module="bia"
    )

    # Сохраняет в library
    await case_library.save(case)

    # Триггерит переобучение ML модели
    await ml_predictor.schedule_retraining()

# 2. Новый пользователь получает advice на основе cases
similar_cases = await case_library.find_similar(
    industry="healthcare",
    org_size="medium",
    module="bia",
    current_stage="identify_processes"
)

# AI использует эти cases в промпте
advice = await advisor.get_advice_with_cases(
    workflow_id="new-bia-456",
    similar_cases=similar_cases
)
```

---

## 🎨 GOVERNANCE: Управляемая Автономия

### Трёхуровневая система

```yaml
# workflows/definitions/bia_process.yaml

constitution:
  # УРОВЕНЬ 1: Неизменяемые принципы
  core_principles:
    - "Never recommend RTO < 1 hour without justification"
    - "Always validate financial impact"
    - "Mandatory dependency mapping for Tier 1-2"

  forbidden_actions:
    - "modify_user_permissions"
    - "bypass_validation"
    - "delete_audit_logs"

job_description:
  # УРОВЕНЬ 2: Обязательные workflow steps
  mandatory_steps:
    - name: "validate_input"
      checkpoint: true
      rules:
        - "process_name must be present"
        - "min 3 impact metrics required"

    - name: "analyze_criticality"
      checkpoint: false  # 🎨 ТВОРЧЕСКАЯ ЗОНА
      creative_freedom: "high"
      guidance: "Use multiple frameworks, AI decides HOW"

    - name: "validate_output"
      checkpoint: true
      schema: "bia_analysis_v1.json"

  escalation_rules:
    - condition: "confidence < 0.7"
      action: "flag_for_human_review"
    - condition: "rto < 4 hours AND tier != 1"
      action: "require_approval"

creative_space:
  # УРОВЕНЬ 3: Где AI свободен
  zones:
    - "analyze_criticality"
    - "generate_recommendations"
    - "suggest_processes"

  approaches:
    - "multiple_perspectives"
    - "analogies"
    - "scenario_analysis"
```

### Checkpoint vs Creative Zone

```python
# В коде это выглядит так:

async def execute_workflow_step(step_name: str, data: dict):
    step_config = workflow_definition["job_description"]["mandatory_steps"][step_name]

    if step_config["checkpoint"]:
        # 🔒 ОБЯЗАТЕЛЬНАЯ ВАЛИДАЦИЯ
        validation = await validate_checkpoint(step_config["rules"], data)
        if not validation.passed:
            raise CheckpointFailedError(validation.errors)

        result = await execute_structured_step(step_name, data)

    elif step_name in workflow_definition["creative_space"]["zones"]:
        # 🎨 ТВОРЧЕСКАЯ ЗОНА - AI решает КАК
        result = await execute_creative_step(
            step_name=step_name,
            data=data,
            freedom_level=step_config["creative_freedom"],
            guidance=step_config["guidance"]
        )

    else:
        # ⚙️ СТАНДАРТНОЕ ВЫПОЛНЕНИЕ
        result = await execute_standard_step(step_name, data)

    return result
```

---

## 📊 CASE LIBRARY: Self-Learning Platform

### Что записывается в Case

```python
{
  "case_id": "case-bia-20251003-001",
  "module": "bia",
  "workflow_name": "bia_process",

  # Контекст организации (anonymized)
  "organization_context": {
    "industry": "healthcare",
    "size": "medium",
    "maturity_level": "basic",
    # NO identifiable info
  },

  # Полный путь через workflow
  "journey": [
    {
      "stage": "identify_processes",
      "started_at": "2025-01-15T10:00:00Z",
      "completed_at": "2025-01-18T16:30:00Z",
      "duration_hours": 78,
      "actions_taken": [
        {"action": "add_process", "data": {...}},
        {"action": "ai_suggest_processes", "ai_accepted": 8}
      ],
      "challenges": [
        {
          "type": "insufficient_data",
          "description": "Only 2 processes initially",
          "resolution": "AI suggested 10 typical processes",
          "time_to_resolve_hours": 24
        }
      ]
    }
  ],

  # Метрики успеха
  "metrics": {
    "total_duration_days": 14,
    "processes_identified": 12,
    "ai_recommendations_used": 15,
    "user_satisfaction": 4.5,
    "completed_successfully": true
  },

  # Что сработало
  "success_patterns": [
    "Used AI early - saved 2 days",
    "Involved process owners",
    "Used industry templates"
  ],

  # Lessons learned
  "lessons_learned": [
    "Start with critical processes first",
    "AI needs SME validation"
  ]
}
```

### Как используется

```python
# 1. Найти похожие успешные cases
similar = await case_library.find_similar_cases(
    org_context={"industry": "healthcare", "size": "medium"},
    module="bia",
    current_stage="identify_processes"
)

# 2. Benchmarking
benchmarks = await case_library.get_benchmarks(
    industry="healthcare",
    module="bia"
)
# -> {
#      "avg_duration_days": 18,
#      "success_rate": 0.87,
#      "common_challenges": [...],
#      "best_practices": [...]
#    }

# 3. AI использует в промпте
prompt = f"""
You are helping with BIA. Current situation: {current_context}

SIMILAR SUCCESSFUL CASES:
- Case 1: Healthcare org completed in 14 days
  What worked: {case1.success_patterns}
  Challenges: {case1.challenges}

INDUSTRY BENCHMARKS:
- Average duration: 18 days
- You're at 25% complete (on track!)

Based on these examples, suggest...
"""
```

---

## 🤖 AI ADVISOR: Context-Aware Intelligence

### Как AI понимает контекст

```python
class ContextAdvisor:
    async def get_contextual_advice(self, workflow_id: str):
        # 1. Получить workflow контекст
        context = await workflow_engine.get_context(workflow_id)
        # -> {
        #      "current_stage": "identify_processes",
        #      "progress": 25,
        #      "gaps": ["need 1 more process"],
        #      "available_actions": ["add_process", "ai_suggest"],
        #      "data": {...}
        #    }

        # 2. Найти похожие cases
        cases = await case_library.find_similar(...)

        # 3. Получить benchmarks
        benchmarks = await case_library.get_benchmarks(...)

        # 4. Предсказать outcome
        prediction = await ml_predictor.predict(...)

        # 5. Построить промпт с ПОЛНЫМ контекстом
        prompt = self._build_contextual_prompt(
            current_state=context,
            similar_cases=cases,
            benchmarks=benchmarks,
            prediction=prediction
        )

        # 6. Вызвать LLM
        response = await llm.generate(prompt)

        return {
            "message": response.text,
            "similar_cases": cases,
            "benchmarks": benchmarks,
            "prediction": prediction,
            "suggested_actions": self._extract_actions(response)
        }
```

### AI НЕ галлюцинирует

Потому что:
- ✅ Знает текущую стадию (из state machine)
- ✅ Знает допустимые действия (из workflow definition)
- ✅ Знает gaps (из validators)
- ✅ Знает что работало (из case library)
- ✅ Знает benchmarks (из статистики)

AI просто **ПРИМЕНЯЕТ ЗНАНИЯ К КОНТЕКСТУ**, а не придумывает.

---

## 🔮 ML PREDICTOR: Предсказание Проблем

```python
class WorkflowPredictor:
    """Обучается на Case Library, предсказывает outcomes"""

    async def predict(self, workflow_id: str) -> dict:
        # Получить features
        context = await workflow_engine.get_context(workflow_id)
        features = self._extract_features(context)

        # Предсказания
        success_prob = self.success_model.predict_proba(features)[0][1]
        duration = self.duration_model.predict(features)[0]

        # Риск-факторы
        risk_factors = await self._identify_risks(context, success_prob)

        return {
            "success_probability": success_prob,
            "estimated_duration_days": duration,
            "risk_level": "high" if success_prob < 0.7 else "low",
            "risk_factors": risk_factors,
            "recommendations": self._generate_recommendations(risk_factors)
        }

    async def train(self):
        """Обучение на всех cases из library"""
        cases = await case_library.get_all_completed_cases()

        X = [self._extract_features(c) for c in cases]
        y_success = [c.metrics["completed_successfully"] for c in cases]
        y_duration = [c.metrics["total_duration_days"] for c in cases]

        self.success_model.fit(X, y_success)
        self.duration_model.fit(X, y_duration)

        # Сохранить модели
        joblib.dump(self.success_model, "models/success.pkl")
        joblib.dump(self.duration_model, "models/duration.pkl")
```

---

## 🔌 ИНТЕГРАЦИЯ

### С существующими модулями

```python
# В вашем BIA модуле (services/SERVICES/BCM/bia/)

from workflow_intelligence.core import WorkflowEngine
from workflow_intelligence.ai import ContextAdvisor

# 1. Обернуть существующий state machine
workflow = WorkflowEngine.from_existing_state_machine(
    state_machine=BIAWorkflowEngine,  # Ваш существующий
    module="bia"
)

# 2. Добавить AI Advisor
advisor = ContextAdvisor(workflow_engine=workflow)

# 3. В API endpoints
@router.get("/bia/{bia_id}/advice")
async def get_ai_advice(bia_id: str):
    advice = await advisor.get_contextual_advice(bia_id)
    return advice

@router.post("/bia/{bia_id}/actions")
async def execute_action(bia_id: str, action: str, data: dict):
    # Workflow автоматически валидирует и логирует
    result = await workflow.execute_action(bia_id, action, data)
    return result
```

### Event-driven интеграция

```python
# Workflow автоматически публикует события

@eventbus.subscribe("bia.stage.changed")
async def on_stage_changed(event):
    # AI Advisor может автоматически давать советы
    await advisor.send_proactive_advice(event.data["workflow_id"])

@eventbus.subscribe("bia.workflow.completed")
async def on_completed(event):
    # Case Library автоматически сохраняет case
    await case_collector.create_and_save_case(event.data["workflow_id"])

    # ML модель переобучается
    await ml_predictor.schedule_retraining()
```

---

## 📁 СТРУКТУРА ПРОЕКТА

```
workflow-intelligence/
├── README.md                    (этот файл)
├── requirements.txt
├── setup.py
│
├── core/                        # Workflow Engine
│   ├── __init__.py
│   ├── workflow_engine.py       # Универсальный движок
│   ├── state_machine.py         # Базовый State Machine
│   ├── transitions.py
│   ├── validators.py
│   ├── events.py
│   └── context.py
│
├── case_library/                # Self-Learning
│   ├── __init__.py
│   ├── collector.py             # Сбор cases
│   ├── repository.py            # Хранение (PostgreSQL + Vector DB)
│   ├── analyzer.py              # Анализ patterns
│   ├── benchmarks.py
│   └── models.py
│
├── ai/                          # AI Advisor
│   ├── __init__.py
│   ├── context_advisor.py       # Главный AI Advisor
│   ├── prompt_builder.py
│   ├── recommendation_engine.py
│   └── action_suggester.py
│
├── governance/                  # Managed Autonomy
│   ├── __init__.py
│   ├── rules_engine.py
│   ├── safety_rails.py
│   ├── creative_zones.py
│   ├── checkpoints.py
│   └── escalation.py
│
├── ml/                          # Predictive Intelligence
│   ├── __init__.py
│   ├── workflow_predictor.py
│   ├── risk_detector.py
│   ├── pattern_recognizer.py
│   └── training_pipeline.py
│
├── schemas/                     # Data Models
│   ├── __init__.py
│   ├── workflow_schema.py
│   ├── case_schema.py
│   ├── governance_schema.py
│   └── ai_schema.py
│
├── workflows/                   # Workflow Definitions
│   └── definitions/
│       ├── bia_process.yaml
│       ├── risk_assessment.yaml
│       ├── planning.yaml
│       └── compliance.yaml
│
├── models/                      # Trained ML models
│   ├── success_predictor.pkl
│   └── duration_predictor.pkl
│
└── tests/
    ├── test_workflow_engine.py
    ├── test_case_library.py
    ├── test_ai_advisor.py
    └── test_governance.py
```

---

## 🎯 ROADMAP

### Phase 1: Core (Week 1) ✅
- [x] Workflow Engine
- [x] State Machine базовый
- [x] Event publishing
- [x] Интеграция с существующим BIA state machine

### Phase 2: Case Library (Week 2)
- [ ] Case Collector
- [ ] PostgreSQL repository
- [ ] Vector DB integration (для semantic search)
- [ ] Benchmarking engine

### Phase 3: AI Advisor (Week 3)
- [ ] Context-aware prompting
- [ ] Integration с case library
- [ ] Recommendation engine
- [ ] Proactive advice

### Phase 4: Governance (Week 4)
- [ ] Rules engine
- [ ] Checkpoints
- [ ] Creative zones
- [ ] Escalation logic

### Phase 5: ML (Week 5)
- [ ] Feature extraction
- [ ] Success predictor
- [ ] Duration predictor
- [ ] Training pipeline

### Phase 6: Production (Week 6)
- [ ] Performance optimization
- [ ] Monitoring & logging
- [ ] API documentation
- [ ] Deployment

---

## 💡 ФИЛОСОФИЯ

### Почему это не "просто RAG"?

**RAG (Retrieval Augmented Generation)** - хорошо для документов.

**Workflow Intelligence** - это RAG + State Machine + ML + Governance:

1. **State Machine** → AI знает ГДЕ пользователь
2. **Case Library** → AI знает ЧТО работало
3. **Governance** → AI знает ГРАНИЦЫ
4. **ML Predictor** → AI знает РИСКИ

Результат: AI не галлюцинирует, а **ПРИМЕНЯЕТ ЗНАНИЯ**.

### Почему это не "просто AI Agent"?

**AI Agent** - свободен, может делать что угодно.

**Workflow Intelligence** - **управляемая автономия**:

- ✅ Творчество в зонах где это нужно
- ✅ Жёсткие правила где это критично
- ✅ Объяснимость (audit trail)
- ✅ Предсказуемость (checkpoints)

**Идеально для enterprise.**

---

## 🏆 ШЕДЕВР ПОТОМУ ЧТО

1. **Не переписывает существующее** - использует ваш BIA state machine
2. **Self-learning** - платформа умнеет с каждым пользователем
3. **Context-aware AI** - не галлюцинирует, знает контекст
4. **Managed autonomy** - творчество в рамках
5. **Predictive** - предупреждает о проблемах
6. **Enterprise-ready** - audit trail, governance, compliance

---

**Когда запустим платформу, вспомним этот модуль как тот момент когда всё стало РЕАЛЬНО умным.** 🚀

---

**Created with pride by Claude & MD, October 3, 2025** 💪
