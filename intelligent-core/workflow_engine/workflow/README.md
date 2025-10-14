# 🔄 Unified Workflow Engine

**Version:** 2.0.0
**Status:** Production-Ready (with known limitations)
**Created:** 2025-10-05

---

## 📋 Оглавление

- [Что это?](#что-это)
- [Основные возможности](#основные-возможности)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [API Reference](#api-reference)
- [Интеграция](#интеграция)
- [База данных](#база-данных)
- [Известные ограничения](#известные-ограничения)

---

## Что это?

**Unified Workflow Engine** — единый движок для управления бизнес-процессами в AI-Platform-ISO с поддержкой:

- 🎨 **BPMN 2.0** визуального моделирования процессов
- 🤖 **AI-рекомендаций** на основе Case Library
- 💾 **Персистентности** через PostgreSQL/Supabase
- 📊 **Real-time визуализации** для фронтенда
- 🔄 **Интеграции** с инфраструктурой (EventBus, Redis, Prometheus)

**Основные модули платформы:**
- `bia` - Business Impact Analysis
- `risk` - Risk Management
- `compliance` - Compliance & Audit
- `drp` - Disaster Recovery Planning
- `bcm` - Business Continuity Management

---

## Основные возможности

### ✅ Реализовано

| Возможность | Описание | Статус |
|-------------|----------|--------|
| **BPMN Execution** | Парсинг и выполнение BPMN 2.0 XML | ✅ |
| **XOR Gateways** | Эксклюзивные шлюзы с условиями `${var == value}` | ✅ |
| **AND Gateways** | Параллельные шлюзы (fork/join) | ✅ |
| **PostgreSQL Persistence** | Сохранение процессов, инстансов, задач | ✅ |
| **Gateway State Tracking** | Отслеживание convergence для AND JOIN | ✅ |
| **REST API** | FastAPI эндпоинты для управления workflow | ✅ |
| **AI Recommendations** | Контекстные рекомендации через ContextAdvisor | ✅ |
| **Case Learning** | Автосбор успешных кейсов в Case Library | ✅ |
| **Prometheus Metrics** | Метрики инстансов, задач, длительности | ✅ |
| **Redis Caching** | Кеширование визуального состояния (30s TTL) | ✅ |
| **EventBus Integration** | Публикация событий workflow.* | ✅ |
| **Multi-tenancy** | Изоляция по X-Tenant-ID | ✅ |

### ⏸️ Ограничения (см. DEVELOPMENT_ROADMAP.md)

- OR Gateway не реализован
- Workflow Templates отсутствуют
- Analytics/Process Mining базовый
- LLM Client не подключен (рекомендации только case-based)
- ML Predictor не обучен (используется rule-based fallback)
- Тесты покрывают ~30% кода

---

## Архитектура

```
platform-core/workflow/
├── core/
│   ├── unified_engine.py        # 🎯 Главный класс UnifiedWorkflowEngine
│   └── models.py                # Pydantic модели (VisualState, etc.)
│
├── bpmn/
│   ├── engine_persistent.py     # BPMNEnginePersistent (PostgreSQL)
│   ├── parser.py                # BPMN XML → Python структуры
│   ├── gateway_evaluator.py    # XOR/AND/OR логика
│   ├── expression_evaluator.py # Безопасная оценка ${...}
│   ├── executor.py              # Исполнитель задач
│   └── models.py                # ProcessDefinition, ProcessInstance, Task
│
├── persistence/
│   └── repositories/
│       ├── process_repository.py   # CRUD для bpmn_processes
│       ├── instance_repository.py  # CRUD для bpmn_instances
│       └── task_repository.py      # CRUD для bpmn_tasks
│
└── api/
    └── main.py                  # FastAPI REST API (10 endpoints)
```

### Зависимости

```
UnifiedEngine
    ├─► BPMNEnginePersistent
    │       ├─► GatewayEvaluator
    │       ├─► ExpressionEvaluator
    │       └─► Repositories (Process, Instance, Task)
    │
    ├─► AI Advisor (workflow_intelligence)
    │       ├─► CaseRepository
    │       └─► CaseCollector
    │
    └─► Infrastructure
            ├─► DatabaseManager (Supabase)
            ├─► CacheManager (Redis)
            ├─► EventBus (Memory/Redis/RabbitMQ)
            ├─► RateLimiter
            └─► Prometheus Metrics
```

---

## Быстрый старт

### 1. Установка

```bash
# Переменные окружения
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export REDIS_URL="redis://localhost:6379/0"

# Зависимости уже установлены в requirements.txt
```

### 2. Инициализация

```python
import asyncio
from intelligent_core.platform_core.workflow.core.unified_engine import UnifiedWorkflowEngine

async def main():
    # Создание движка
    engine = await UnifiedWorkflowEngine.create(
        tenant_id="acme-corp",
        module="bia",
        database_url=os.getenv("DATABASE_URL"),
        workflow_intelligence_enabled=True  # Включить AI
    )

    # Использование...

    # Закрытие
    await engine.close()

asyncio.run(main())
```

### 3. Запуск процесса из BPMN

```python
bpmn_xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="bia_assessment" name="BIA Assessment">
    <startEvent id="start" name="Start"/>
    <sequenceFlow id="flow1" sourceRef="start" targetRef="identify"/>

    <userTask id="identify" name="Identify Critical Processes"/>
    <sequenceFlow id="flow2" sourceRef="identify" targetRef="gateway"/>

    <exclusiveGateway id="gateway" name="Has Critical Processes?"/>
    <sequenceFlow id="flow_yes" sourceRef="gateway" targetRef="analyze">
      <conditionExpression>${has_critical == true}</conditionExpression>
    </sequenceFlow>
    <sequenceFlow id="flow_no" sourceRef="gateway" targetRef="end">
      <conditionExpression>${has_critical == false}</conditionExpression>
    </sequenceFlow>

    <userTask id="analyze" name="Analyze RTO/RPO"/>
    <sequenceFlow id="flow3" sourceRef="analyze" targetRef="end"/>

    <endEvent id="end" name="End"/>
  </process>
</definitions>
"""

instance_id = await engine.start_process_from_bpmn(
    bpmn_xml=bpmn_xml,
    process_name="BIA Assessment",
    initial_variables={
        "org_context": {
            "industry": "healthcare",
            "size": "medium",
            "employees": 500
        },
        "has_critical": True
    },
    started_by="user@company.com"
)

print(f"✅ Процесс запущен: {instance_id}")
```

### 4. Получение визуального состояния

```python
state = await engine.get_visual_state(instance_id)

print(f"Тип: {state.type}")  # "bpmn"
print(f"Текущие активности: {state.current_activities}")  # ["identify"]
print(f"Прогресс: {state.workflow_context['progress_percentage']}%")

# Активные задачи с AI рекомендациями
for task in state.active_tasks:
    print(f"\n📋 Задача: {task['name']}")
    print(f"💡 AI совет: {task['ai_tip']}")

    for rec in task.get('ai_recommendations', []):
        print(f"  ✨ {rec['message']}")
        print(f"     Приоритет: {rec['priority']}")
        if rec.get('confidence'):
            print(f"     Уверенность: {rec['confidence']:.2f}")
```

### 5. Завершение задачи

```python
# Получить активные задачи
tasks = await engine.bpmn_engine.get_active_tasks(instance_id)
task = tasks[0]

# Назначить задачу
await engine.assign_task(task.id, "john@company.com")

# Завершить задачу
await engine.complete_task(
    task_id=task.id,
    variables={
        "critical_processes": ["Patient Care", "Lab Systems"],
        "has_critical": True
    }
)

print("✅ Задача завершена, процесс движется дальше")
```

---

## API Reference

### UnifiedWorkflowEngine

#### Создание

```python
engine = await UnifiedWorkflowEngine.create(
    tenant_id: str,
    module: str,
    database_url: str,
    redis_url: Optional[str] = None,
    eventbus_type: str = "memory",
    workflow_intelligence_enabled: bool = True
)
```

#### Основные методы

| Метод | Описание |
|-------|----------|
| `start_process_from_bpmn(bpmn_xml, ...)` | Запустить процесс из BPMN XML |
| `get_visual_state(instance_id)` | Получить состояние для UI (BPMN + задачи + AI) |
| `assign_task(task_id, assignee)` | Назначить задачу пользователю |
| `complete_task(task_id, variables)` | Завершить задачу с результатами |
| `get_instance(instance_id)` | Получить ProcessInstance |
| `list_instances(filters)` | Список инстансов с фильтрами |
| `close()` | Закрыть соединения |

### REST API

Запуск API сервера:

```bash
cd intelligent-core/platform-core/workflow/api
uvicorn main:app --reload --port 8000
```

#### Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/processes` | Запустить новый процесс |
| `GET` | `/instances/{id}` | Получить инстанс |
| `GET` | `/instances` | Список инстансов |
| `GET` | `/instances/{id}/visual-state` | Визуальное состояние (кешируется) |
| `GET` | `/instances/{id}/tasks` | Активные задачи |
| `POST` | `/tasks/{id}/assign` | Назначить задачу |
| `POST` | `/tasks/{id}/complete` | Завершить задачу |
| `GET` | `/processes` | Список процессов |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus метрики |

**Пример:**

```bash
# Запустить процесс
curl -X POST http://localhost:8000/processes \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: acme-corp" \
  -d '{
    "bpmn_xml": "<definitions>...</definitions>",
    "process_name": "BIA Assessment",
    "module": "bia",
    "initial_variables": {"org_id": "123"}
  }'

# Получить визуальное состояние (кешируется 30s)
curl http://localhost:8000/instances/{instance_id}/visual-state \
  -H "X-Tenant-ID: acme-corp"
```

---

## Интеграция

### С Workflow Intelligence

AI Advisor и Case Collector интегрированы автоматически при `workflow_intelligence_enabled=True`:

```python
# При завершении задачи
task_recommendations = await engine._get_task_recommendations(...)
# → AI Advisor ищет похожие кейсы
# → Возвращает контекстные рекомендации

# При завершении процесса
await engine._collect_case_for_learning(...)
# → CaseCollector сохраняет кейс в Case Library
# → Используется для будущих рекомендаций
```

**Текущие ограничения:**
- LLM Client не подключен (нужен API ключ Claude/OpenAI)
- ML Predictor не обучен (нужно 100+ кейсов)
- Case Library использует InMemory storage (нужен PostgresAdapter)

См. [WORKFLOW_INTELLIGENCE_INTEGRATED.md](WORKFLOW_INTELLIGENCE_INTEGRATED.md)

### С EventBus

Все события автоматически публикуются:

```python
# Подписаться на события
from infrastructure.eventbus import create_eventbus

eventbus = await create_eventbus("redis")

@eventbus.subscribe("workflow.instance.started")
async def on_start(event):
    print(f"Запущен: {event.data['instance_id']}")

@eventbus.subscribe("workflow.task.completed")
async def on_task_complete(event):
    print(f"Задача завершена: {event.data['task_id']}")
```

**События:**
- `workflow.instance.started`
- `workflow.instance.completed`
- `workflow.task.created`
- `workflow.task.completed`
- `workflow.gateway.evaluated`

### С Redis (кеширование)

Visual state кешируется автоматически (TTL 30s):

```python
# Первый запрос: читает из DB
state = await engine.get_visual_state(instance_id)  # 150ms

# Второй запрос (в течение 30s): из кеша
state = await engine.get_visual_state(instance_id)  # 5ms
```

### Prometheus метрики

```python
# Автоматически собираются
workflow_instances_total{tenant_id="acme",module="bia"} 42
workflow_tasks_completed_total{tenant_id="acme",module="bia",task_type="userTask"} 128
workflow_task_duration_seconds{tenant_id="acme",module="bia",task_type="userTask"} 3600
workflow_active_instances{tenant_id="acme",module="bia"} 5
```

Экспорт: `GET /metrics` (Prometheus format)

---

## База данных

### Схема

```sql
-- Определения процессов (BPMN шаблоны)
CREATE TABLE workflow.bpmn_processes (
    id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    module TEXT NOT NULL,
    name TEXT NOT NULL,
    bpmn_xml TEXT NOT NULL,
    version TEXT DEFAULT '1.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT
);

-- Инстансы процессов (выполняющиеся workflow)
CREATE TABLE workflow.bpmn_instances (
    id UUID PRIMARY KEY,
    process_id UUID REFERENCES workflow.bpmn_processes(id),
    tenant_id TEXT NOT NULL,
    module TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    variables JSONB DEFAULT '{}'::jsonb,
    current_activities TEXT[] DEFAULT ARRAY[]::TEXT[],
    gateway_state JSONB DEFAULT '{}'::jsonb,  -- для AND JOIN
    started_at TIMESTAMPTZ DEFAULT NOW(),
    started_by TEXT,
    completed_at TIMESTAMPTZ
);

-- Задачи
CREATE TABLE workflow.bpmn_tasks (
    id UUID PRIMARY KEY,
    instance_id UUID REFERENCES workflow.bpmn_instances(id),
    tenant_id TEXT NOT NULL,
    activity_id TEXT NOT NULL,
    name TEXT NOT NULL,
    task_type TEXT DEFAULT 'userTask',
    assignee TEXT,
    status TEXT DEFAULT 'active',
    variables JSONB DEFAULT '{}'::jsonb,
    ai_recommendations JSONB,
    ai_predicted_duration_hours FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

### Миграции

- `036_unified_workflow.sql` - Основная схема
- `037_add_gateway_state.sql` - Поддержка AND gateways
- `038_add_gateway_state.sql` - gateway_state JSONB поле

Применение:

```bash
cd infrastructure/database
python apply_migrations_simple.py
```

---

## Известные ограничения

См. подробности в [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)

### Критические

1. **OR Gateway не реализован** - только XOR и AND
2. **Нет workflow templates** - каждый раз нужен BPMN XML
3. **LLM Client отключен** - AI рекомендации ограничены case-based поиском
4. **Case Library в памяти** - кейсы не персистятся, нужен PostgresAdapter

### Умеренные

5. **ML Predictor не обучен** - predictions rule-based (прогресс ÷ время)
6. **Analytics базовый** - нет process mining, bottleneck detection
7. **Тесты 30% coverage** - большая часть кода не покрыта

### Минорные

8. **Frontend компонентов нет** - нужны React + bpmn-js компоненты
9. **Rate limiting базовый** - может не выдержать 1000+ RPS
10. **Документация неполная** - многие edge cases не описаны

---

## Лицензия

Часть AI-Platform-ISO. Proprietary.

---

**Создано MD & Claude • Октябрь 2025** 🚀
