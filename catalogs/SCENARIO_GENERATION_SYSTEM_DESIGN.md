# Scenario Generation System - Architecture & Design

**Date**: 2025-10-12
**Status**: 🎯 DESIGN PHASE
**Integration**: AI Office + Intelligent Core + EventBus

---

## 🎯 Vision

**Автоматическая система генерации, доработки и архивации сценариев** с полной интеграцией через EventBus, координируемая AI Office.

### Ключевые принципы:
1. **Золотой стандарт** - шаблоны-эталоны для каждого уровня (L1-L4)
2. **EventBus координация** - все видят все события
3. **AI Office управление** - MIO наблюдает, Analytics анализирует, Project управляет
4. **Intelligent Core решения** - AI Orchestration принимает решения
5. **Непрерывное улучшение** - сценарии дорабатываются на основе выполнений

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCENARIO GENERATION SYSTEM                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │   SCENARIO   │ │   SCENARIO   │ │   SCENARIO   │
        │   MANAGER    │ │  GENERATOR   │ │   ARCHIVE    │
        │ (Управление) │ │ (Создание)   │ │ (Хранение)   │
        └──────────────┘ └──────────────┘ └──────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                ▼
                        ┌──────────────┐
                        │   EVENTBUS   │
                        │ (Choreography)│
                        └──────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  AI OFFICE   │      │ INTELLIGENT  │      │   PLATFORM   │
│              │      │    CORE      │      │   SERVICES   │
├──────────────┤      ├──────────────┤      ├──────────────┤
│ MIO Manager  │◄────►│ AI           │      │ Execution    │
│ Analytics    │      │ Orchestration│      │ Results      │
│ Project Agent│      │              │      │              │
│ Orchestrator │      │ Predictive   │      │ Monitoring   │
│ DevOps Agent │      │ Learning     │      │              │
│ DB Intel     │      │ Community    │      │              │
│ Agent Router │      │              │      │              │
│ Event Manager│      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## 🎭 Components

### 1. Scenario Manager (Управляющий и исполнитель)

**Роль**: Главный AI сотрудник системы генерации сценариев

**Location**: `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/manager/`

**Responsibilities**:
- Управление жизненным циклом сценариев
- Координация генерации (L1-L4)
- Публикация событий в EventBus
- Интеграция с AI Office
- Архивация и версионирование

**API Endpoints**:
```python
POST   /scenarios/generate        # Генерация сценариев
POST   /scenarios/improve          # Улучшение сценариев
GET    /scenarios/{id}             # Получение сценария
POST   /scenarios/{id}/archive     # Архивация
GET    /scenarios/stats            # Статистика
POST   /scenarios/batch-generate   # Массовая генерация
```

**EventBus Integration**:
```python
# Публикует:
- scenario.generation.started
- scenario.generation.completed
- scenario.generation.failed
- scenario.improvement.needed
- scenario.archived

# Подписывается на:
- execution.completed (от Platform Services)
- analysis.completed (от Analytics Specialist)
- improvement.recommended (от Predictive)
```

---

### 2. Scenario Generator (Генераторы)

**Location**: `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/generators/`

**4 специализированных генератора**:

#### 2.1 L1 Generator (Service Level)
```python
class L1ServiceGenerator:
    """
    Генерирует сценарии уровня L1 (Service)

    Input: SERVICE_CATALOG_DETAILED.yaml (46 services)
    Output: 46 L1 scenarios
    Template: golden_standard_l1.yaml
    """
    async def generate_from_catalog(self):
        # Читает каталог сервисов
        # Для каждого сервиса создаёт L1 сценарий
        # Публикует событие scenario.l1.generated
```

#### 2.2 L2 Generator (Subsystem Level)
```python
class L2SubsystemGenerator:
    """
    Генерирует сценарии уровня L2 (Subsystem)

    Input: SUBSYSTEMS_CATALOG.yaml (11 subsystems)
    Output: 11 L2 scenarios
    Template: golden_standard_l2.yaml
    """
    async def generate_from_subsystems(self):
        # Читает каталог подсистем
        # Комбинирует L1 сценарии
        # Создаёт межсервисные сценарии
```

#### 2.3 L3 Generator (System Level)
```python
class L3SystemGenerator:
    """
    Генерирует сценарии уровня L3 (Functional System)

    Input: SYSTEMS_CATALOG.yaml (19 functional systems)
    Output: 19+ L3 scenarios
    Template: golden_standard_l3.yaml
    """
    async def generate_from_systems(self):
        # Читает каталог функциональных систем
        # Комбинирует L2 сценарии
        # Создаёт межсистемные сценарии
```

#### 2.4 L4 Generator (User Workflow)
```python
class L4WorkflowGenerator:
    """
    Генерирует сценарии уровня L4 (User E2E)

    Input: User requirements + AI generation
    Output: User workflows
    Template: golden_standard_l4.yaml
    Integration: Scenario Orchestrator (AI-powered)
    """
    async def generate_ai_powered(self, user_story: str):
        # Использует Orchestrator Adapter
        # AI генерирует E2E workflow
        # Интегрирует с существующими L1-L3
```

---

### 3. Golden Standards (Шаблоны-эталоны)

**Location**: `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/templates/`

#### 3.1 L1 Golden Standard
```yaml
# golden_standard_l1.yaml
meta:
  id: "l1-service-{service_name}"
  level: 1
  type: "service"
  service: "{service_name}"
  status: "template"
  version: "1.0.0"
  created: "auto-generated"

description:
  summary: "{service_description}"
  purpose: "Validate {service_name} service operations"
  business_value: "{business_value}"

test_scenarios:
  - name: "Service Startup"
    steps:
      - action: "start_service"
        service: "{service_name}"
        expected: "healthy status"
      - action: "check_health"
        endpoint: "/health"
        expected: "status: healthy"
      - action: "verify_metrics"
        endpoint: "/metrics"
        expected: "prometheus metrics available"

  - name: "Service Operations"
    steps:
      - action: "execute_primary_function"
        description: "{primary_function}"
        expected: "successful execution"

  - name: "Service Dependencies"
    steps:
      - action: "verify_dependencies"
        dependencies: [{dependencies}]
        expected: "all dependencies available"

  - name: "Service Resilience"
    steps:
      - action: "simulate_failure"
        type: "{failure_type}"
        expected: "graceful degradation"
      - action: "verify_recovery"
        expected: "service recovered"

monitoring:
  metrics:
    - "{service_name}_requests_total"
    - "{service_name}_errors_total"
    - "{service_name}_latency_seconds"

  alerts:
    - condition: "error_rate > 5%"
      action: "notify_devops"
    - condition: "latency > 1s"
      action: "investigate_performance"

success_criteria:
  - "Service starts successfully"
  - "Health check passes"
  - "Primary function works"
  - "Dependencies available"
  - "Resilience verified"

execution_history: []
learning_data: {}
```

#### 3.2 L2 Golden Standard
```yaml
# golden_standard_l2.yaml
meta:
  id: "l2-subsystem-{subsystem_name}"
  level: 2
  type: "subsystem"
  subsystem: "{subsystem_name}"
  services: [{service_list}]
  status: "template"

description:
  summary: "Integration testing for {subsystem_name}"
  purpose: "Validate inter-service communication within subsystem"

test_scenarios:
  - name: "Subsystem Startup Sequence"
    steps:
      - action: "start_services_in_order"
        services: [{services_in_order}]
        expected: "all services healthy"

  - name: "Inter-Service Communication"
    steps:
      - action: "test_service_to_service"
        from: "{service_a}"
        to: "{service_b}"
        expected: "successful communication"

  - name: "Subsystem Integration"
    steps:
      - action: "execute_subsystem_workflow"
        workflow: "{workflow_name}"
        expected: "workflow completes successfully"

  - name: "Subsystem Failover"
    steps:
      - action: "fail_one_service"
        service: "{service_name}"
        expected: "subsystem continues operation"
      - action: "verify_recovery"
        expected: "failed service recovers"

integration_patterns:
  - pattern: "{integration_pattern_1}"
  - pattern: "{integration_pattern_2}"
```

#### 3.3 L3 Golden Standard
```yaml
# golden_standard_l3.yaml
meta:
  id: "l3-system-{system_name}"
  level: 3
  type: "functional_system"
  functional_system: "{system_name}"
  subsystems: [{subsystem_list}]
  status: "template"

description:
  summary: "End-to-end testing for {system_name}"
  purpose: "Validate functional system capabilities"
  business_value: "{business_value}"

test_scenarios:
  - name: "System Capability Test"
    steps:
      - action: "execute_primary_capability"
        capability: "{primary_capability}"
        expected: "capability works E2E"

  - name: "Cross-Subsystem Integration"
    steps:
      - action: "test_subsystem_collaboration"
        subsystems: [{subsystem_a}, {subsystem_b}]
        expected: "seamless collaboration"

  - name: "System-Level Resilience"
    steps:
      - action: "fail_subsystem"
        subsystem: "{subsystem_name}"
        expected: "system adapts and continues"

functional_requirements:
  - requirement: "{requirement_1}"
  - requirement: "{requirement_2}"

iso_22301_mapping:
  clause: "{iso_clause}"
  description: "{iso_requirement}"
```

#### 3.4 L4 Golden Standard
```yaml
# golden_standard_l4.yaml
meta:
  id: "l4-workflow-{workflow_name}"
  level: 4
  type: "user_workflow"
  workflow: "{workflow_name}"
  systems_involved: [{system_list}]
  status: "template"

description:
  user_story: "{user_story}"
  purpose: "Validate complete user workflow"
  business_value: "{business_value}"

workflow_steps:
  - step: 1
    actor: "user"
    action: "{action_1}"
    system: "{system_name}"
    expected: "{expected_result_1}"

  - step: 2
    actor: "system"
    action: "{action_2}"
    triggers: ["{event_1}", "{event_2}"]
    expected: "{expected_result_2}"

  - step: 3
    actor: "ai"
    action: "{ai_action}"
    ai_service: "{ai_service_name}"
    expected: "{ai_expected_result}"

success_criteria:
  - "User completes workflow successfully"
  - "All systems respond within SLA"
  - "Data persisted correctly"
  - "Audit trail created"

user_acceptance:
  scenario: "{acceptance_scenario}"
  expected_outcome: "{expected_outcome}"
```

---

### 4. Scenario Archive (Архивация)

**Location**: `/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/archive/`

**Structure**:
```
archive/
├── l1/
│   ├── v1.0/
│   │   ├── service-auth-service-v1.0.yaml
│   │   └── service-postgresql-v1.0.yaml
│   └── v2.0/
│       └── service-auth-service-v2.0.yaml
├── l2/
│   └── v1.0/
│       └── subsystem-security-v1.0.yaml
├── l3/
│   └── v1.0/
│       └── system-security-system-v1.0.yaml
└── l4/
    └── v1.0/
        └── workflow-bia-creation-v1.0.yaml
```

**Versioning Strategy**:
- Semantic versioning: v{major}.{minor}.{patch}
- Major: Breaking changes (API changes, structure changes)
- Minor: New features (new scenarios, new steps)
- Patch: Improvements (better descriptions, fixed bugs)

---

## 🔄 Workflow: Scenario Generation

### Phase 1: Initial Generation (Массовая генерация)

```
1. Scenario Manager получает запрос на генерацию
   └─► POST /scenarios/batch-generate
        {
          "levels": ["l1", "l2", "l3"],
          "mode": "initial",
          "use_golden_standards": true
        }

2. Scenario Manager публикует событие
   └─► EventBus: scenario.generation.started
        {
          "request_id": "gen-001",
          "levels": ["l1", "l2", "l3"],
          "total_scenarios": 76
        }

3. MIO Manager видит событие (подписка)
   └─► Начинает мониторинг процесса
   └─► Обновляет dashboard

4. Scenario Manager запускает генераторы параллельно
   ├─► L1 Generator: 46 scenarios (из SERVICE_CATALOG)
   ├─► L2 Generator: 11 scenarios (из SUBSYSTEMS_CATALOG)
   └─► L3 Generator: 19 scenarios (из SYSTEMS_CATALOG)

5. Каждый генератор:
   ├─► Читает соответствующий каталог
   ├─► Загружает золотой стандарт
   ├─► Заполняет шаблон данными
   ├─► Валидирует результат
   ├─► Сохраняет в PostgreSQL (scenario_intelligence schema)
   ├─► Сохраняет файл в /catalogs/scenarios/
   └─► Публикует событие scenario.{level}.generated

6. Analytics Specialist видит события (подписка)
   └─► Анализирует качество сгенерированных сценариев
   └─► Проверяет полноту покрытия
   └─► Публикует scenario.quality.analyzed

7. Project Agent видит события (подписка)
   └─► Создаёт задачи для проверки сценариев
   └─► Назначает задачи DevOps Agent
   └─► Публикует tasks.created

8. Scenario Manager завершает генерацию
   └─► EventBus: scenario.generation.completed
        {
          "request_id": "gen-001",
          "generated": {
            "l1": 46,
            "l2": 11,
            "l3": 19
          },
          "total": 76,
          "duration_seconds": 45,
          "quality_score": 0.95
        }

9. MIO Manager видит завершение
   └─► Обновляет статус
   └─► Отправляет уведомление
   └─► Логирует в мониторинг
```

---

## 🔄 Workflow: Scenario Improvement (Доработка)

### Phase 2: Continuous Improvement (На основе выполнений)

```
1. Platform Services выполняет сценарий
   └─► Сценарий L1: service-postgresql
   └─► Результат: FAILED (connection timeout)
   └─► EventBus: execution.completed
        {
          "scenario_id": "l1-service-postgresql",
          "status": "failed",
          "error": "connection timeout after 5s",
          "execution_time": 5.2,
          "timestamp": "2025-10-12T10:30:00Z"
        }

2. Event Intelligence видит событие (подписка)
   └─► Анализирует ошибку
   └─► Обнаруживает паттерн: timeout issues
   └─► Публикует pattern.detected

3. Analytics Specialist видит событие (подписка)
   └─► Анализирует историю выполнений PostgreSQL
   └─► Находит 3 недавних timeout'а
   └─► Делает вывод: "Timeout threshold too low"
   └─► Публикует analysis.completed
        {
          "scenario_id": "l1-service-postgresql",
          "issue": "timeout_threshold_too_low",
          "recommendation": "increase timeout from 5s to 10s",
          "confidence": 0.85
        }

4. Predictive Service видит событие (подписка)
   └─► Предсказывает: "С текущим timeout будет 30% failures"
   └─► Публикует prediction.created
        {
          "scenario_id": "l1-service-postgresql",
          "predicted_failure_rate": 0.30,
          "recommended_action": "update_scenario"
        }

5. AI Orchestration видит события (подписка)
   └─► Агрегирует context:
        - Ошибка выполнения
        - Анализ от Analytics Specialist
        - Предсказание от Predictive
   └─► Принимает решение: "Approve scenario improvement"
   └─► Публикует decision.made
        {
          "decision": "improve_scenario",
          "scenario_id": "l1-service-postgresql",
          "changes": {
            "timeout": "10s"
          },
          "approved_by": "ai-orchestration",
          "confidence": 0.90
        }

6. Scenario Manager видит решение (подписка)
   └─► Загружает текущий сценарий v1.0
   └─► Применяет изменения (timeout: 10s)
   └─► Создаёт новую версию v1.1
   └─► Архивирует старую версию
   └─► Публикует scenario.improved
        {
          "scenario_id": "l1-service-postgresql",
          "old_version": "1.0",
          "new_version": "1.1",
          "changes": ["increased timeout to 10s"],
          "reason": "reduce failure rate"
        }

7. Project Agent видит улучшение (подписка)
   └─► Создаёт задачу: "Re-test PostgreSQL scenario v1.1"
   └─► Назначает DevOps Agent
   └─► Публикует task.created

8. DevOps Agent видит задачу (подписка)
   └─► Запускает сценарий v1.1
   └─► Результат: SUCCESS
   └─► Публикует execution.completed
        {
          "scenario_id": "l1-service-postgresql",
          "version": "1.1",
          "status": "success",
          "execution_time": 8.5
        }

9. MIO Manager видит всё (подписка на все события)
   └─► Обновляет dashboard
   └─► Показывает: "PostgreSQL scenario improved: v1.0 → v1.1"
   └─► Логирует success
```

---

## 🔄 Workflow: AI-Powered L4 Generation

### Phase 3: User Workflow Generation (AI-генерация)

```
1. User submits request via UI
   └─► "Create BIA workflow for healthcare organization"

2. UI → API Gateway → Scenario Manager
   └─► POST /scenarios/generate-l4
        {
          "user_story": "As a BCM Manager, I want to create BIA for hospital ICU department",
          "category": "bia",
          "complexity": 3,
          "duration_hours": 4
        }

3. Scenario Manager
   └─► Публикует EventBus: scenario.l4.generation.requested
   └─► Использует Orchestrator Adapter

4. Orchestrator Adapter
   └─► Вызывает Scenario Orchestrator (platform-services)
        POST /scenarios/generate
        {
          "category": "bia",
          "complexity": 3
        }

5. Scenario Orchestrator (AI-powered)
   └─► AI Orchestration генерирует E2E workflow
   └─► Использует LLM (OpenAI/Claude)
   └─► Возвращает JSON workflow

6. Orchestrator Adapter
   └─► Конвертирует JSON → L4 YAML (golden standard)
   └─► Добавляет metadata, steps, success_criteria

7. Scenario Manager
   └─► Сохраняет L4 scenario
   └─► Публикует EventBus: scenario.l4.generated

8. Analytics Specialist (подписка)
   └─► Валидирует L4 сценарий
   └─► Проверяет интеграцию с L1-L3
   └─► Публикует validation.completed

9. Community Intelligence (подписка)
   └─► Проверяет похожие сценарии в сообществе
   └─► Предлагает улучшения из peer knowledge
   └─► Публикует community.feedback

10. Scenario Manager
    └─► Агрегирует feedback
    └─► Создаёт финальную версию
    └─► Публикует scenario.ready
```

---

## 📊 EventBus Events Specification

### Scenario Events

```yaml
# scenario.generation.started
event_type: scenario.generation.started
source: scenario-manager
data:
  request_id: string
  levels: [string]
  mode: string  # initial | improvement | ai_powered
  total_scenarios: int
  timestamp: datetime

# scenario.{level}.generated
event_type: scenario.l1.generated | scenario.l2.generated | scenario.l3.generated | scenario.l4.generated
source: scenario-manager
data:
  scenario_id: string
  level: int
  type: string
  file_path: string
  database_id: string
  version: string
  timestamp: datetime

# scenario.generation.completed
event_type: scenario.generation.completed
source: scenario-manager
data:
  request_id: string
  generated:
    l1: int
    l2: int
    l3: int
    l4: int
  total: int
  duration_seconds: float
  quality_score: float
  timestamp: datetime

# scenario.improved
event_type: scenario.improved
source: scenario-manager
data:
  scenario_id: string
  old_version: string
  new_version: string
  changes: [string]
  reason: string
  approved_by: string
  timestamp: datetime

# scenario.archived
event_type: scenario.archived
source: scenario-manager
data:
  scenario_id: string
  version: string
  archive_path: string
  reason: string
  timestamp: datetime
```

### Execution Events

```yaml
# execution.completed
event_type: execution.completed
source: platform-service | devops-agent
data:
  scenario_id: string
  version: string
  status: string  # success | failed | partial
  execution_time: float
  error: string | null
  metrics: dict
  timestamp: datetime

# execution.started
event_type: execution.started
source: platform-service
data:
  scenario_id: string
  version: string
  executor: string
  timestamp: datetime
```

### Analysis Events

```yaml
# analysis.completed
event_type: analysis.completed
source: analytics-specialist
data:
  scenario_id: string
  issue: string | null
  recommendation: string | null
  confidence: float
  metrics: dict
  timestamp: datetime

# pattern.detected
event_type: pattern.detected
source: event-intelligence
data:
  pattern_type: string
  affected_scenarios: [string]
  description: string
  severity: string
  timestamp: datetime

# prediction.created
event_type: prediction.created
source: predictive-service
data:
  scenario_id: string
  predicted_failure_rate: float
  recommended_action: string
  confidence: float
  timestamp: datetime
```

### Decision Events

```yaml
# decision.made
event_type: decision.made
source: ai-orchestration
data:
  decision: string  # improve_scenario | keep_scenario | archive_scenario
  scenario_id: string
  changes: dict | null
  approved_by: string
  confidence: float
  reasoning: string
  timestamp: datetime
```

### Task Events

```yaml
# task.created
event_type: task.created
source: project-agent
data:
  task_id: string
  task_type: string
  scenario_id: string
  assignee: string
  priority: string
  description: string
  timestamp: datetime

# task.completed
event_type: task.completed
source: devops-agent | project-agent
data:
  task_id: string
  status: string
  result: dict
  timestamp: datetime
```

---

## 🎯 AI Office Integration

### MIO Manager Role

**Observatory & Coordination**

```python
# Подписывается на ВСЕ события
subscriptions = [
    "scenario.*",
    "execution.*",
    "analysis.*",
    "decision.*",
    "task.*"
]

async def observe_scenario_system(event):
    """Наблюдает за системой генерации сценариев"""
    # Обновляет dashboard
    # Отслеживает прогресс
    # Публикует обзоры
    # Координирует AI Office
```

### Analytics Specialist Role

**Analysis & Insights**

```python
subscriptions = [
    "scenario.*.generated",
    "execution.completed",
    "pattern.detected"
]

async def analyze_scenario_quality(event):
    """Анализирует качество сценариев"""
    # Проверяет полноту
    # Анализирует результаты выполнений
    # Находит bottlenecks
    # Рекомендует улучшения
    await publish("analysis.completed", analysis)
```

### Project Agent Role

**Task Management**

```python
subscriptions = [
    "scenario.generation.completed",
    "scenario.improved",
    "decision.made"
]

async def manage_scenario_tasks(event):
    """Управляет задачами по сценариям"""
    # Создаёт задачи на проверку
    # Назначает DevOps Agent
    # Отслеживает выполнение
    await publish("task.created", task)
```

### Orchestrator Role

**Coordination**

```python
subscriptions = [
    "task.created",
    "agent.*"
]

async def coordinate_agents(event):
    """Координирует AI агентов"""
    # Распределяет задачи
    # Балансирует нагрузку
    # Разрешает конфликты
```

### DevOps Agent Role

**Execution & Testing**

```python
subscriptions = [
    "task.created",
    "scenario.improved"
]

async def execute_scenario_tasks(event):
    """Выполняет задачи по сценариям"""
    # Запускает тесты
    # Валидирует сценарии
    # Публикует результаты
    await publish("execution.completed", result)
```

### DB Intelligence Role

**Database Performance**

```python
subscriptions = [
    "scenario.*.generated",  # Отслеживает сохранение
    "execution.completed"     # Анализирует query performance
]

async def optimize_scenario_storage(event):
    """Оптимизирует хранение сценариев"""
    # Анализирует query performance
    # Оптимизирует индексы
    # Рекомендует архивацию старых версий
```

### Agent Router Role

**Request Routing**

```python
async def route_scenario_request(request):
    """Маршрутизирует запросы к сценариям"""
    # Определяет целевой агент
    # Балансирует нагрузку
    # Возвращает результат
```

### AI Event Manager Role

**Event Orchestration**

```python
subscriptions = [
    "scenario.*",
    "execution.*",
    "analysis.*"
]

async def orchestrate_scenario_events(event):
    """Оркестрирует события сценариев"""
    # Агрегирует связанные события
    # Обнаруживает причинно-следственные связи
    # Координирует реакции
```

---

## 🧠 Intelligent Core Integration

### AI Orchestration Role

**Decision Making**

```python
subscriptions = [
    "analysis.completed",
    "prediction.created",
    "pattern.detected"
]

async def decide_scenario_improvement(context):
    """Принимает решения об улучшении сценариев"""
    # Агрегирует context (Analysis + Prediction + Pattern)
    # Использует 4-layer memory
    # Применяет strategy selection
    # Проверяет safety (Constitution)
    # Публикует decision
    await publish("decision.made", decision)
```

### Predictive Service Role

**Forecasting**

```python
subscriptions = [
    "execution.completed",
    "pattern.detected"
]

async def predict_scenario_outcomes(event):
    """Предсказывает результаты сценариев"""
    # ML-based prediction
    # Анализирует historical data
    # Предсказывает failure rate
    # Рекомендует actions
    await publish("prediction.created", prediction)
```

### Learning System Role

**Knowledge Accumulation**

```python
subscriptions = [
    "execution.completed",
    "scenario.improved"
]

async def learn_from_scenarios(event):
    """Учится на выполнениях сценариев"""
    # Обновляет knowledge base (RAG)
    # Сохраняет patterns
    # Улучшает competencies
```

### Community Intelligence Role

**Peer Knowledge**

```python
subscriptions = [
    "scenario.l4.generated"
]

async def enrich_with_community_wisdom(event):
    """Обогащает сценарии знаниями сообщества"""
    # Ищет похожие сценарии в community
    # Предлагает improvements
    # Публикует community feedback
    await publish("community.feedback", feedback)
```

---

## 📦 Database Schema

### PostgreSQL (scenario_intelligence schema)

```sql
-- Scenarios table
CREATE TABLE scenario_intelligence.scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id VARCHAR(255) UNIQUE NOT NULL,
    level INT NOT NULL CHECK (level IN (1, 2, 3, 4)),
    type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL,

    -- Content
    yaml_content JSONB NOT NULL,
    file_path TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),

    -- Quality
    quality_score FLOAT,
    execution_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    failure_count INT DEFAULT 0,

    -- Relations
    parent_scenario_id VARCHAR(255),
    related_scenarios JSONB,

    -- Learning
    learning_data JSONB DEFAULT '{}'::jsonb,

    -- Indexes
    INDEX idx_scenarios_level (level),
    INDEX idx_scenarios_type (type),
    INDEX idx_scenarios_status (status),
    INDEX idx_scenarios_version (version)
);

-- Executions table
CREATE TABLE scenario_intelligence.executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,

    -- Execution
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    execution_time_seconds FLOAT,

    -- Results
    result JSONB,
    error TEXT,
    metrics JSONB,

    -- Context
    executor VARCHAR(100),
    environment VARCHAR(50),

    -- Relations
    FOREIGN KEY (scenario_id) REFERENCES scenario_intelligence.scenarios(scenario_id),

    -- Indexes
    INDEX idx_executions_scenario (scenario_id),
    INDEX idx_executions_status (status),
    INDEX idx_executions_started (started_at)
);

-- Improvements table
CREATE TABLE scenario_intelligence.improvements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id VARCHAR(255) NOT NULL,
    old_version VARCHAR(20) NOT NULL,
    new_version VARCHAR(20) NOT NULL,

    -- Changes
    changes JSONB NOT NULL,
    reason TEXT,

    -- Approval
    recommended_by VARCHAR(100),
    approved_by VARCHAR(100),
    confidence FLOAT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    -- Relations
    FOREIGN KEY (scenario_id) REFERENCES scenario_intelligence.scenarios(scenario_id),

    -- Indexes
    INDEX idx_improvements_scenario (scenario_id),
    INDEX idx_improvements_created (created_at)
);

-- Archive table
CREATE TABLE scenario_intelligence.archive (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id VARCHAR(255) NOT NULL,
    version VARCHAR(20) NOT NULL,

    -- Content
    yaml_content JSONB NOT NULL,
    archive_path TEXT NOT NULL,

    -- Metadata
    archived_at TIMESTAMP DEFAULT NOW(),
    archived_by VARCHAR(100),
    reason TEXT,

    -- Indexes
    INDEX idx_archive_scenario (scenario_id),
    INDEX idx_archive_version (version)
);
```

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1)
1. ✅ Create Scenario Manager service
2. ✅ Implement Golden Standards (L1-L4 templates)
3. ✅ Setup PostgreSQL schema
4. ✅ Configure EventBus integration

### Phase 2: Generators (Week 2)
1. ✅ L1 Service Generator (46 scenarios)
2. ✅ L2 Subsystem Generator (11 scenarios)
3. ✅ L3 System Generator (19 scenarios)
4. ✅ L4 Workflow Generator (AI-powered)

### Phase 3: AI Office Integration (Week 3)
1. ✅ MIO Manager integration
2. ✅ Analytics Specialist integration
3. ✅ Project Agent integration
4. ✅ Orchestrator integration
5. ✅ DevOps Agent integration
6. ✅ DB Intelligence integration
7. ✅ Agent Router integration
8. ✅ AI Event Manager integration

### Phase 4: Intelligent Core Integration (Week 4)
1. ✅ AI Orchestration integration
2. ✅ Predictive Service integration
3. ✅ Learning System integration
4. ✅ Community Intelligence integration

### Phase 5: Continuous Improvement (Week 5)
1. ✅ Scenario improvement workflow
2. ✅ Archive system
3. ✅ Versioning system
4. ✅ Quality scoring

### Phase 6: Testing & Launch (Week 6)
1. ✅ Integration testing
2. ✅ Load testing
3. ✅ Documentation
4. ✅ Production deployment

---

## 📊 Success Metrics

### Generation Metrics
- **Generation Speed**: <1s per L1 scenario, <2s per L2, <5s per L3
- **Coverage**: 100% services, subsystems, functional systems covered
- **Quality Score**: >0.90 initial quality

### Improvement Metrics
- **Improvement Rate**: >20% scenarios improved based on executions
- **Version Evolution**: Average 3-5 versions per scenario
- **Failure Reduction**: >50% reduction in failure rate after improvements

### Integration Metrics
- **Event Latency**: <100ms event delivery
- **AI Office Response**: <5s from event to analysis
- **Decision Making**: <10s from analysis to decision

---

## 🎯 Next Steps

1. **Review this design** with team
2. **Create Scenario Manager** service (main orchestrator)
3. **Implement Golden Standards** (4 templates)
4. **Build L1 Generator** (initial 46 scenarios)
5. **Setup EventBus subscriptions** for all AI Office components
6. **Test end-to-end workflow** (generation → execution → improvement)

---

**Status**: 🎯 DESIGN COMPLETE - READY FOR IMPLEMENTATION
**Estimated Timeline**: 6 weeks
**Team**: AI Office + Intelligent Core + Platform Services
