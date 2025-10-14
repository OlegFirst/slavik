# Scenario Intelligence System

Система сценарного интеллекта - верхний слой координации в `intelligent-core`, который оркестрирует всю платформу через исполняемые сценарии.

## 🎯 Что это?

**Scenario Intelligence** = гибридная система управления поведением платформы, объединяющая лучшие практики из BPMN 2.0, Event Storming, ISO 22301, Google SRE, Netflix Chaos Engineering и AWS Well-Architected Framework.

### Три типа сценариев:

1. **System Scenarios** (тестирование системы) - Chaos, Security, Performance, Integration
2. **User Scenarios** (бизнес-процессы пользователей) - BIA, Risk Assessment, Incident Response, Compliance Workflows
3. **Behavioral Models** (правила и политики) - SOP, Политики безопасности, Compliance Policies

### 4-уровневая иерархия:

1. **Level 1 - Module** (модули): отдельные микросервисы и компоненты
2. **Level 2 - Subsystem** (подсистемы): группы модулей (AI Office, Platform Services)
3. **Level 3 - Inter-system** (межсистемные): взаимодействие между подсистемами
4. **Level 4 - User** (пользовательские): полные E2E workflows пользователей

## 🏗️ Архитектура

```
scenario-intelligence/
│
├─ engines/                    # Движки исполнения
│  ├─ scenario_engine.py      # Главный оркестратор
│  ├─ call_engine.py          # BPMN Call Activity
│  ├─ event_engine.py         # Event Storming Events
│  ├─ chaos_engine.py         # Netflix Chaos
│  └─ compliance_engine.py    # ISO Compliance
│
├─ storage/                    # Хранилище
│  ├─ registry.py             # Быстрый индекс (in-memory/PostgreSQL)
│  └─ rag_storage.py          # RAG с embeddings (Qdrant) [TODO]
│
├─ learning/                   # Обучение
│  ├─ scenario_learner.py     # Учится на выполнении
│  ├─ pattern_detector.py     # Находит паттерны [TODO]
│  ├─ predictor.py            # Предсказывает сценарии [TODO]
│  └─ auto_generator.py       # Генерирует сценарии [TODO]
│
├─ scenarios/                  # Сценарии (YAML)
│  ├─ level1-modules/         # Модульные (Vault, BIA Service, etc)
│  ├─ level2-subsystems/      # Подсистемные (AI Office, Platform Services)
│  ├─ level3-intersystem/     # Межсистемные (AI↔Platform, AI↔Infrastructure)
│  └─ level4-user/            # Пользовательские (E2E workflows)
│
├─ integration/                # Интеграции
│  ├─ db_integration.py       # PostgreSQL integration [TODO]
│  ├─ rag_integration.py      # Qdrant integration [TODO]
│  └─ eventbus_integration.py # EventBus integration [TODO]
│
├─ api/                        # REST API
│  └─ api.py                  # FastAPI endpoints
│
└─ tests/                      # Тесты [TODO: реорганизация]
   ├─ unit/
   ├─ integration/
   └─ e2e/
```

## 🚀 Быстрый старт

### 1. Тест системы:

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence
python3 test_scenario_system.py
```

### 2. Запуск API:

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence
python3 -m api.api
```

API будет доступен на `http://localhost:8090`

### 3. Использование в коде:

```python
from scenario_intelligence import ScenarioEngine, global_registry

# Зарегистрировать сценарий
await global_registry.register(scenario)

# Выполнить сценарий
engine = ScenarioEngine()
result = await engine.execute_scenario(scenario, context={...})

# Получить статистику
stats = await global_learner.get_statistics(scenario_id)
```

## 📝 Формат сценария

```yaml
scenario:
  # Metadata
  meta:
    id: "unique-id"
    version: "1.0.0"
    level: 1  # 1-4
    type: "functional"  # functional, chaos, security, workflow, etc
    pillar: "security"  # AWS Well-Architected pillar
    module: "vault"     # For level 1
    subsystem: "security"  # For level 2

  # Description
  description:
    title: "Название"
    summary: "Краткое описание"
    business_value: "Зачем нужно"

  # Behavior (Gherkin)
  behavior:
    feature: "Feature name"
    scenario: "Scenario name"
    given: ["precondition 1", "precondition 2"]
    when: ["action"]
    then: ["expected result 1", "expected result 2"]

  # Execution (SRE Runbook)
  execution:
    timeout: 30
    retry_policy:
      max_retries: 3
      backoff: exponential
    steps:
      - id: "step1"
        action: "service.method"
        params: {...}
        expect: {...}
        on_failure: "rollback"

  # Integration (BPMN + Event Storming)
  integration:
    calls:  # Синхронные вызовы (BPMN Call Activity)
      - scenario_id: "another-scenario"
        level: 1
        parallel: false
        input_mapping: {...}
        output_mapping: {...}

    events:  # Асинхронные события (Event Storming)
      emits:
        - event_type: "vault.secret.stored"
          aggregate: "secret"
      subscribes:
        - event_type: "user.authenticated"
          trigger_scenario: "vault-load-user-secrets"

  # Chaos (Netflix Chaos Engineering)
  chaos:
    hypothesis: "System handles vault unavailability gracefully"
    steady_state:
      metrics: [{name: "api_success_rate", threshold: 0.99}]
    actions:
      - type: "latency"
        target: "vault-service"
        duration: 5000
    rollout:
      phases: [{percentage: 10, duration: 60}]
    abort_conditions: [{metric: "error_rate", threshold: 0.05}]

  # Compliance (ISO 22301)
  compliance:
    iso_22301:
      clauses:
        - id: "7.5.3"
          name: "Control of documented information"
      evidence_generated:
        - type: "execution_log"
          retention: "7 years"
          format: "json"
```

## 🔧 Движки

### 1. Scenario Engine (главный)
- Оркестрирует все остальные движки
- Выполняет сценарии любого типа/уровня
- Координирует Call/Event/Chaos/Compliance engines

### 2. Call Engine (BPMN)
- Синхронные вызовы других сценариев
- Параллельные/последовательные
- Input/output mapping
- Timeout и error handling

### 3. Event Engine (Event Storming)
- Асинхронные события (pub/sub)
- Подписки и автозапуск сценариев
- Domain Events, Commands, Policies
- Aggregates для контекста

### 4. Chaos Engine (Netflix)
- Chaos experiments
- Progressive rollout
- Hypothesis testing
- Steady state verification
- Abort conditions

### 5. Compliance Engine (ISO)
- Проверки compliance
- Генерация evidence
- Retention policies
- Clause mapping

## 📊 Обучение

**Learner** автоматически:
- Записывает каждое выполнение
- Собирает статистику (success rate, duration)
- Находит паттерны использования [TODO]
- Предсказывает следующие сценарии [TODO]
- Генерирует новые сценарии из шаблонов [TODO]

## 🌐 API Endpoints

```
GET  /health                                    # Health check
POST /scenarios/execute                         # Выполнить сценарий
POST /scenarios/register                        # Зарегистрировать сценарий
GET  /scenarios/{scenario_id}                   # Получить сценарий
GET  /scenarios                                 # Поиск сценариев (фильтры)
GET  /scenarios/statistics                      # Общая статистика
GET  /scenarios/{scenario_id}/statistics        # Статистика сценария
GET  /scenarios/{scenario_id}/executions        # История выполнений
```

## 📚 Примеры сценариев

### Level 1 (Module): Vault Store Secret
`scenarios/level1-modules/vault/functional/store-secret.v1.0.0.yaml`

Демонстрирует:
- Функциональное тестирование модуля
- ISO 22301 compliance
- Event emission
- Evidence generation

### Level 4 (User): BIA Complete Workflow
`scenarios/level4-user/workflows/bia-complete-workflow.v1.0.0.yaml`

Демонстрирует:
- E2E пользовательский workflow
- Call Activity (вызов Level 3 сценария)
- Multi-service orchestration
- Business process compliance

## ✅ Что реализовано

### Движки (Engines):
- ✅ **Scenario Engine** (главный оркестратор) - координирует все движки
- ✅ **Call Engine** (BPMN Call Activity) - синхронные вызовы сценариев
- ✅ **Event Engine** (Event Storming) - асинхронные события pub/sub
- ✅ **Chaos Engine** (Netflix) - chaos experiments с hypothesis testing
- ✅ **Compliance Engine** (ISO) - проверки compliance и генерация evidence

### Хранилище (Storage):
- ✅ **Registry** (быстрый индекс) - мульти-индексный поиск сценариев (in-memory)

### Обучение (Learning):
- ✅ **Learner** (обучение на выполнении) - сбор статистики и паттернов

### API:
- ✅ **REST API** (FastAPI) - 8 эндпоинтов для управления

### Тесты:
- ✅ **test_scenario_system.py** - комплексное тестирование всех компонентов

### Сценарии:
- ✅ **2 эталонных сценария** (Level 1, Level 4)

## 🔗 Интеграция с платформой

### Текущая интеграция:
- ✅ **Standalone** - работает независимо с in-memory хранилищем
- ✅ **REST API** - доступен для всех сервисов на порту 8090

### Планируемая интеграция:

#### База данных:
- 🔄 **PostgreSQL** (schema: `scenario_intelligence`) - персистентное хранилище
  - Таблицы: `scenarios`, `executions`, `statistics`, `patterns`
  - Миграция: `infrastructure/database/migrations/scenario_intelligence_schema.sql`

#### RAG:
- 🔄 **Qdrant** (collection: `scenarios`) - семантический поиск сценариев
  - Embeddings для поиска похожих сценариев
  - Интеграция с `intelligent-core/ai-foundation/rag`

#### EventBus:
- 🔄 **EventBus** - публикация событий при выполнении
  - `scenario.execution.started`
  - `scenario.execution.completed`
  - `scenario.execution.failed`
  - `scenario.pattern.detected`
  - `scenario.learning.updated`

#### AI Platform:
- 🔄 **AI Orchestrator** (`intelligent-core/orchestration/ai-orchestration`)
  - Выполнение AI-задач в сценариях
  - Интеграция с decision center
- 🔄 **Workflow Intelligence** (`intelligent-core/workflow_intelligence`)
  - Оркестрация бизнес-процессов через сценарии
  - Temporal workflows
- 🔄 **Learning System** (`intelligent-core/ai-foundation/learning-knowledge`)
  - Обучение на результатах выполнения
  - Pattern detection

#### Service Discovery:
- 🔄 **Service Discovery** (`infrastructure/runtime/service-discovery`)
  - Регистрация как сервис `scenario-intelligence:8090`
  - Health checks

## 🔮 Roadmap

### Phase 1: Персистентность и RAG (в разработке)
- 🔄 **PostgreSQL Schema** - создание таблиц для персистентности
- 🔄 **Database Integration** - подключение к PostgreSQL
- 🔄 **RAG Storage** (Qdrant) - хранение с embeddings для семантического поиска
- 🔄 **EventBus Integration** - публикация событий выполнения

### Phase 2: Продвинутое обучение
- 🔄 **Pattern Detector** - автоматическое определение паттернов использования
- 🔄 **Predictor** - предсказание следующих сценариев на основе истории
- 🔄 **Auto-Generator** - автогенерация новых сценариев из шаблонов

### Phase 3: Библиотека сценариев
- 🔄 **20-30 эталонных сценариев** для всех уровней:
  - Level 1: все критические модули
  - Level 2: основные подсистемы
  - Level 3: ключевые интеграции
  - Level 4: основные пользовательские workflows

### Phase 4: Расширенные возможности
- 📋 **Визуальный редактор** сценариев (UI)
- 📋 **Scenario versioning** и rollback
- 📋 **A/B тестирование** сценариев
- 📋 **Scenario templates** библиотека
- 📋 **Distributed execution** - выполнение на нескольких нодах
- 📋 **Real-time monitoring** - live dashboard выполнения

## 🧪 Тестирование

### Текущие тесты:
```bash
# Основной тест
python3 test_scenario_system.py
```

### Планируемая структура:
```
tests/
├─ unit/                      # Модульные тесты
│  ├─ test_engines.py
│  ├─ test_registry.py
│  └─ test_learner.py
├─ integration/               # Интеграционные тесты
│  ├─ test_db_integration.py
│  ├─ test_rag_integration.py
│  └─ test_eventbus.py
└─ e2e/                       # End-to-end тесты
   ├─ test_full_workflow.py
   └─ test_chaos_scenarios.py
```

## 📖 Документация

См. также:
- [FULL_IMPLEMENTATION_ARCHITECTURE.md](FULL_IMPLEMENTATION_ARCHITECTURE.md) - Полная архитектура
- [HYBRID_ARCHITECTURE_DESIGN.md](HYBRID_ARCHITECTURE_DESIGN.md) - Гибридный дизайн
- [EXPERT_REVIEW.md](EXPERT_REVIEW.md) - Экспертная оценка
- [SCENARIO_SDL.md](SCENARIO_SDL.md) - Scenario Definition Language [TODO]

## 🎬 Статус тестирования

```
======================================================================
✅ ALL TESTS PASSED!
======================================================================

Final Statistics:
  Total scenarios: 2
  By level: {1: 1, 4: 1}
  By type: {'functional': 1, 'workflow': 1}

Test Coverage:
  ✅ Scenario Engine - OK
  ✅ Call Engine - OK
  ✅ Event Engine - OK
  ✅ Chaos Engine - OK
  ✅ Compliance Engine - OK
  ✅ Registry - OK
  ✅ Learner - OK
  ✅ API Endpoints - OK
```

## 📊 Метрики и KPI

### Текущие метрики:
- **Total scenarios**: количество зарегистрированных сценариев
- **Success rate**: процент успешных выполнений
- **Average duration**: среднее время выполнения
- **Executions count**: количество выполнений

### Планируемые метрики:
- **Pattern coverage**: покрытие обнаруженными паттернами
- **Prediction accuracy**: точность предсказаний
- **Auto-generation rate**: количество автогенерированных сценариев
- **Compliance score**: уровень соответствия ISO 22301

## 🚀 Система готова к использованию!

**Текущий статус**: ✅ MVP готов, работает standalone

**Следующие шаги**: Интеграция с PostgreSQL и EventBus (см. Roadmap Phase 1)
