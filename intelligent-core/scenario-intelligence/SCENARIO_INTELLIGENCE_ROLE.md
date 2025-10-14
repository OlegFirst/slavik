# Роль Scenario Intelligence в платформе

## 🎯 Что такое Scenario Intelligence?

**Scenario Intelligence** - это **"мозг тестирования и оркестрации"** вашей платформы. Это система, которая:

1. **Описывает поведение** всей платформы через executable сценарии (YAML)
2. **Тестирует** все уровни: от отдельных модулей до полных пользовательских workflows
3. **Оркестрирует** сложные процессы через композицию простых сценариев
4. **Обучается** на каждом выполнении и улучшает систему
5. **Гарантирует compliance** с ISO 22301 через встроенные проверки

---

## 🏛️ Место в архитектуре платформы

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI PLATFORM ISO 22301                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      INTELLIGENT CORE                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         🧠 SCENARIO INTELLIGENCE (Верхний слой)           │  │
│  │  "Описывает ЧТО должна делать платформа через сценарии"  │  │
│  │                                                            │  │
│  │  • 4-level testing (Module → Subsystem → Inter-sys → E2E)│  │
│  │  • BPMN Call Activity (синхронная композиция)            │  │
│  │  • Event Storming (асинхронные события)                  │  │
│  │  • Chaos Engineering (устойчивость к сбоям)              │  │
│  │  • ISO 22301 Compliance (автоматическая проверка)        │  │
│  │  • Self-learning (учится на выполнении)                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                ▼                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         🤖 AI ORCHESTRATION (Средний слой)                │  │
│  │        "КАК выполнять AI-задачи и принимать решения"     │  │
│  │                                                            │  │
│  │  • Decision Center (принятие решений)                     │  │
│  │  • Safety Monitor (контроль безопасности)                 │  │
│  │  • Memory Management (управление памятью)                 │  │
│  │  • Evolution Engine (эволюция агентов)                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                ▼                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          📚 AI FOUNDATION (Нижний слой)                   │  │
│  │         "Базовые AI capabilities: LLM, RAG, Memory"       │  │
│  │                                                            │  │
│  │  • RAG (Retrieval Augmented Generation)                   │  │
│  │  • Learning & Knowledge (обучение)                        │  │
│  │  • Embeddings (векторизация)                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
         ┌──────────────────┐    ┌──────────────────┐
         │ PLATFORM SERVICES│    │ INFRASTRUCTURE   │
         │  (Бизнес-логика) │    │   (Поддержка)    │
         │                  │    │                  │
         │ • BIA Service    │    │ • EventBus       │
         │ • Risk Service   │    │ • Database       │
         │ • Plans Service  │    │ • Monitoring     │
         │ • Document Svc   │    │ • Security       │
         └──────────────────┘    └──────────────────┘
```

---

## 🔄 Как это работает?

### Пример: Пользователь создает Risk Assessment

```
1️⃣ USER ACTION
   │
   └─→ Пользователь нажимает "Create Risk Assessment" в UI
       │
       ▼

2️⃣ SCENARIO INTELLIGENCE запускает Level 4 сценарий:
   "complete-risk-assessment-workflow.v1.0.0.yaml"
   │
   ├─→ PHASE 1: Authentication
   │   └─→ Вызывает Auth Service
   │
   ├─→ PHASE 2: AI Analysis (через Level 3 сценарий)
   │   └─→ "ai-assisted-bia-workflow"
   │       └─→ AI Orchestrator анализирует риск
   │           └─→ Analytics Specialist находит похожие риски
   │
   ├─→ PHASE 3: Create Risk Assessment (через Level 1 сценарий)
   │   └─→ "risk-service-create-risk-assessment"
   │       └─→ Risk Service сохраняет в DB
   │       └─→ Публикует событие "risk.identified"
   │
   ├─→ PHASE 4: Link to BIA
   │   └─→ BIA Service связывает risk с business process
   │
   ├─→ PHASE 5: Create Documentation (через Level 1 сценарий)
   │   └─→ "document-service-store-document"
   │       └─→ Document Service сохраняет mitigation plan
   │
   ├─→ PHASE 6: Compliance Evidence (через Level 1 сценарий)
   │   └─→ "compliance-engine-check-compliance"
   │       └─→ Compliance Engine генерирует ISO 22301 evidence
   │
   ├─→ PHASE 7: Audit Logging (через Level 1 сценарий)
   │   └─→ "audit-service-create-audit-log"
   │       └─→ Audit Service записывает immutable log
   │
   └─→ PHASE 8: Notify Stakeholders
       └─→ Notification Service уведомляет risk committee
       │
       ▼

3️⃣ RESULT
   │
   └─→ Пользователь видит: "Risk Assessment created successfully"
       + AI recommendations
       + Compliance evidence ID
       + Audit trail
```

---

## 🎭 Три роли Scenario Intelligence

### 1️⃣ РОЛЬ ТЕСТИРОВЩИКА

Scenario Intelligence = **Living Test Suite** (живой набор тестов)

**Традиционный подход:**
```python
# test_risk_service.py
def test_create_risk():
    response = client.post("/api/risk", json={...})
    assert response.status_code == 201
```

**Scenario Intelligence подход:**
```yaml
# risk-service-create-risk-assessment.v1.0.0.yaml
scenario:
  execution:
    steps:
      - action: "risk.create"
        expect:
          status: 201
          risk_id: "{{exists}}"

  compliance:
    iso_22301:
      clauses: ["8.2.3"]  # ← Автоматическая проверка!
```

**Преимущества:**
- ✅ Сценарии = исполняемая документация
- ✅ Тесты = production-ready сценарии
- ✅ Compliance встроен в каждый тест
- ✅ Один сценарий тестирует ВСЕ: функциональность + события + compliance + метрики

---

### 2️⃣ РОЛЬ ОРКЕСТРАТОРА

Scenario Intelligence = **Business Process Engine** (движок бизнес-процессов)

**Проблема без Scenario Intelligence:**
```python
# В каждом сервисе дублируется логика оркестрации:
async def create_risk_assessment(data):
    # Где живет эта логика? В каком сервисе?
    risk = await risk_service.create(data)
    await ai_service.analyze(risk)
    await bia_service.link(risk)
    await document_service.store(risk)
    await compliance_service.check(risk)
    await audit_service.log(risk)
    await notification_service.notify(risk)
    # 😱 Код оркестрации размазан по всем сервисам!
```

**С Scenario Intelligence:**
```yaml
# complete-risk-assessment-workflow.v1.0.0.yaml
# ✅ Логика оркестрации ОТДЕЛЬНО от бизнес-логики!
scenario:
  integration:
    calls:
      - scenario_id: "ai-assisted-bia-workflow"  # AI analysis
      - scenario_id: "risk-service-create-risk"  # Create risk
      - scenario_id: "document-service-store"    # Store doc
      - scenario_id: "compliance-engine-check"   # Compliance
      - scenario_id: "audit-service-log"         # Audit
```

**Преимущества:**
- ✅ Оркестрация ОТДЕЛЕНА от бизнес-логики (Separation of Concerns)
- ✅ Сценарии композируются как LEGO (Call Activity)
- ✅ Меняешь workflow - меняешь только YAML, не код сервисов
- ✅ Один workflow = один YAML файл (Single Source of Truth)

---

### 3️⃣ РОЛЬ ОБУЧАЮЩЕЙСЯ СИСТЕМЫ

Scenario Intelligence = **Self-Improving Platform** (самообучающаяся платформа)

**После каждого выполнения сценария:**
```
Scenario Intelligence собирает:
  • Duration (как долго выполнялся)
  • Success/Failure (успех или ошибка)
  • Error patterns (какие ошибки случаются часто)
  • Usage patterns (какие сценарии используются вместе)

Затем использует эти данные для:
  ✅ Предсказания следующих сценариев
  ✅ Автоматической генерации новых сценариев
  ✅ Оптимизации порядка выполнения шагов
  ✅ Раннего обнаружения проблем
```

**Пример обучения:**

```python
# После 100 выполнений "risk-assessment-workflow":
learner.get_statistics("risk-assessment-workflow")
# {
#   "success_rate": 0.97,
#   "avg_duration_ms": 5230,
#   "common_patterns": [
#     "часто выполняется после BIA creation",
#     "AI recommendations принимаются в 85% случаев"
#   ],
#   "detected_issues": [
#     "AI analysis timeout в 3% случаев"
#   ]
# }

# Система АВТОМАТИЧЕСКИ предлагает:
# "Увеличить timeout для AI analysis с 10s до 15s"
```

---

## 🌟 Уникальность подхода

### Традиционный подход к тестированию:

```
Tests (unit) ────┐
                 ├─→ Отдельный код
Integration Tests├─→ Отдельный код
E2E Tests ───────┤
                 │
Production Code ─┘─→ Другой код (дублирование!)

❌ Tests ≠ Production
❌ Тесты устаревают
❌ Нет связи между тестами и compliance
```

### Scenario Intelligence подход:

```
Scenarios = Tests = Production Workflows = Compliance

✅ Один YAML = Тест + Production + Compliance + Documentation
✅ Сценарии самодокументируются (Gherkin)
✅ Compliance встроен в каждый сценарий
✅ Тесты = живая документация
```

---

## 📊 Примеры использования

### 1. Тестирование после деплоя

```bash
# Запустить все Level 1 сценарии (smoke tests модулей)
curl -X POST http://scenario-intelligence:8090/scenarios/execute-batch \
  -d '{"filter": {"level": 1}}'

# Запустить критические E2E workflows
curl -X POST http://scenario-intelligence:8090/scenarios/execute-batch \
  -d '{"scenario_ids": [
    "complete-risk-assessment-workflow",
    "incident-response-workflow",
    "bia-complete-workflow"
  ]}'
```

### 2. Chaos Engineering

```yaml
# chaos-vault-outage.yaml
scenario:
  chaos:
    hypothesis: "Платформа работает при недоступности Vault"
    actions:
      - type: "service_outage"
        target: "vault"
        duration: 60
    steady_state:
      metrics:
        - name: "api_success_rate"
          threshold: 0.95  # Минимум 95% успешных запросов
```

### 3. Compliance Audit

```bash
# Проверить все сценарии на compliance с ISO 22301
curl http://scenario-intelligence:8090/scenarios/compliance-report

# Response:
# {
#   "standard": "ISO_22301",
#   "coverage": {
#     "clause_4.1": ["compliance-engine-check-compliance"],
#     "clause_8.2.2": ["bia-service-create-bia", "risk-service-create-risk"],
#     "clause_8.5": ["incident-response-workflow"]
#   },
#   "missing_clauses": [],
#   "compliance_score": 100
# }
```

### 4. User Workflow Monitoring

```bash
# Получить статистику E2E workflows за последнюю неделю
curl http://scenario-intelligence:8090/scenarios/statistics?level=4&period=7d

# Response:
# {
#   "complete-risk-assessment-workflow": {
#     "executions": 156,
#     "success_rate": 0.97,
#     "avg_duration_ms": 5230,
#     "p95_duration_ms": 8100
#   },
#   "incident-response-workflow": {
#     "executions": 23,
#     "success_rate": 0.99,
#     "avg_duration_ms": 12450
#   }
# }
```

---

## 🔗 Интеграция с другими компонентами

### 1. Workflow Intelligence Integration

```yaml
# Scenario Intelligence вызывает Workflow Intelligence:
scenario:
  steps:
    - id: "start_temporal_workflow"
      action: "http.post"
      params:
        url: "http://workflow-intelligence:8020/api/v1/workflows/start"
        body:
          workflow_type: "bia_creation"
```

### 2. AI Orchestrator Integration

```yaml
# Scenario Intelligence делегирует AI-задачи:
scenario:
  steps:
    - id: "request_ai_analysis"
      action: "http.post"
      params:
        url: "http://ai-orchestrator:8000/api/v1/tasks"
        body:
          task_type: "risk_analysis"
```

### 3. EventBus Integration

```yaml
# Scenario Intelligence публикует события:
scenario:
  integration:
    events:
      emits:
        - event_type: "scenario.execution.completed"
          payload:
            scenario_id: "..."
            duration_ms: 5230
```

### 4. Policy Engine Integration

```python
# Policy Engine использует сценарии для enforcement:
policy = {
    "name": "RequireRiskAssessmentForHighImpactBIA",
    "condition": "bia.financial_impact > 100000",
    "action": {
        "type": "trigger_scenario",
        "scenario_id": "risk-service-create-risk-assessment"
    }
}
```

---

## 📈 Метрики успеха

После внедрения Scenario Intelligence вы получаете:

### 1. Видимость
```
✅ 100% покрытие критических workflows сценариями
✅ Real-time dashboard выполнения
✅ Автоматические отчеты по compliance
```

### 2. Качество
```
✅ Success rate по каждому сценарию
✅ Раннее обнаружение regression
✅ Автоматическое тестирование после деплоя
```

### 3. Скорость
```
✅ Быстрый onboarding (сценарии = документация)
✅ Быстрое добавление новых workflows (просто YAML)
✅ Быстрое изменение бизнес-процессов (меняем сценарий, не код)
```

### 4. Compliance
```
✅ Автоматическая проверка ISO 22301
✅ Автоматическая генерация evidence
✅ Audit trail из коробки
```

---

## 🎯 Итог: Зачем нужен Scenario Intelligence?

### Без Scenario Intelligence:
```
❌ Тесты отдельно, production code отдельно
❌ Оркестрация размазана по всем сервисам
❌ Compliance проверяется вручную
❌ Нет единой картины работы платформы
❌ Трудно добавлять новые workflows
❌ Трудно понять, что делает платформа
```

### С Scenario Intelligence:
```
✅ Сценарии = тесты = production = compliance
✅ Оркестрация централизована и декларативна
✅ Compliance встроен в каждый сценарий
✅ Единая картина в виде графа сценариев
✅ Новый workflow = новый YAML файл
✅ Документация = исполняемые сценарии (Gherkin)
✅ Система самообучается и улучшается
```

---

## 🚀 Следующие шаги

### Сейчас доступно:
1. ✅ **14 базовых сценариев** (Level 1-4)
2. ✅ **API для выполнения** (http://localhost:8090)
3. ✅ **Обучение на каждом выполнении**
4. ✅ **Standalone работа** (in-memory)

### В разработке:
1. 🔄 **PostgreSQL integration** - персистентное хранилище
2. 🔄 **Qdrant RAG integration** - семантический поиск сценариев
3. 🔄 **EventBus integration** - публикация событий
4. 🔄 **API authentication** - безопасность

### В планах:
1. 📋 **Visual dashboard** - UI для мониторинга
2. 📋 **Scenario editor** - UI для создания сценариев
3. 📋 **Auto-generation** - AI генерирует сценарии
4. 📋 **A/B testing** - сравнение вариантов сценариев

---

## 💡 Главное

**Scenario Intelligence** - это не просто система тестирования. Это:

🧠 **Единый язык описания поведения платформы**
🎭 **Живая документация** (executable specifications)
🔄 **Движок оркестрации** для сложных процессов
📊 **Система мониторинга** и метрик
🎓 **Обучающаяся система**, которая становится умнее
✅ **Гарантия compliance** с ISO 22301

**Аналогия:**
- **Kubernetes** описывает **ЧТО** должно быть развернуто (declarative)
- **Scenario Intelligence** описывает **ЧТО** должна делать платформа (declarative)

Вместо того чтобы писать императивный код для каждого workflow, вы описываете его декларативно в YAML, и Scenario Intelligence выполняет его, тестирует, мониторит и обучается.

---

**Scenario Intelligence = BDD (Behavior-Driven Development) + BPMN + Event Storming + Chaos Engineering + ISO Compliance на стероидах! 🚀**
