# AI Office Infrastructure Integration Map

**Created**: 2025-10-11
**Question**: "Связаны ли AI Office сервисы с Policy Engine и Balancer Service?"

---

## 🎯 Короткий ответ

**ДА! Связаны через EventBus** - единую шину событий.

**Архитектура**:
```
AI Office Infrastructure → EventBus ← Policy Engine
         ↓                              ↑
    Balancer Service ←──────────────────┘
```

---

## 📊 Полная карта интеграций

### 1. **AI Event Manager** ← Центральный узел

**Location**: `/infrastructure/AI-office-infrastructure/ai-event-manager/`

**Роль**: **UNIFIED MONITORING SYSTEM** - собирает данные от всех!

**Что делает**:
- 📊 Мониторит infrastructure state (порты, БД, метрики)
- 👀 Координируется с Resource Tracker (MIO Manager)
- 🔴 Публикует события в EventBus
- 🧠 Принимает стратегические решения

**Компонент**: `monitoring/infrastructure_state.py`

```python
class InfrastructureStateMonitor:
    """
    ЕДИНАЯ СИСТЕМА МОНИТОРИНГА для всей платформы

    Координация:
    1. Собирает данные из разных источников
    2. Объединяет в единое состояние
    3. Публикует в EventBus
    4. Принимает стратегические решения
    5. Отправляет рекомендации
    """
```

**Публикует события**:
- `platform.infrastructure.state_updated` (каждые 60s)
- `platform.infrastructure.emergency` (critical issues)
- `platform.infrastructure.strategy_recommended` (scaling strategy)
- `platform.infrastructure.resource_deficit` (low resources)
- `platform.infrastructure.service_unhealthy` (service down)

**Слушает события**:
- `platform.service.registered` (new service)
- `platform.service.unregistered` (service down)
- `platform.resources.snapshot` (from mio-manager)

**Упоминает в коде**:
```python
# infrastructure_state.py:12-15
"""
Публикует всё в EventBus для координации с:
- balancer-service ✅
- mio-manager ✅
- orchestrator ✅
- все остальные сервисы
"""
```

---

### 2. **Balancer Service** ← Получатель событий

**Location**: `/infrastructure/balancer-service/`

**Роль**: Orchestrates Phase 2 AI balancers (из `intelligent-core/ai-foundation/balancer/`)

**НЕ содержит**: Policy Engine импорты
**НЕ содержит**: Прямые импорты AI Office сервисов
**Связь**: **Только через EventBus** ✅

**Компоненты**:
1. System Balancer (МОЗГ ГЛОБАЛЬНЫЙ)
2. Impact Evidence Tracker (RATIONAL)
3. Predictive ROI Optimizer (INTUITIVE + PRAGMATIC)
4. Three-Dimensional Balancer (3D BALANCE)

**Подписки на события** (`main.py:136-177`):

```python
# От Survival Instinct
await self.eventbus.subscribe(
    'platform.bcm.imbalance_detected',
    self._handle_imbalance_event
)

# От Resource Tracker (MIO Manager)
await self.eventbus.subscribe(
    'platform.resources.snapshot',
    self._handle_resource_snapshot
)

await self.eventbus.subscribe(
    'platform.resources.deficit',
    self._handle_resource_deficit
)

# От AI Event Manager (Infrastructure State Monitor)
await self.eventbus.subscribe(
    'platform.infrastructure.state_updated',
    self._handle_infrastructure_state  # ← КРИТИЧНО!
)

await self.eventbus.subscribe(
    'platform.infrastructure.emergency',
    self._handle_infrastructure_emergency  # ← АВАРИИ!
)

await self.eventbus.subscribe(
    'platform.infrastructure.strategy_recommended',
    self._handle_strategy_recommendation  # ← СТРАТЕГИЯ!
)
```

**Как использует infrastructure state** (`main.py:247-293`):

```python
async def _handle_infrastructure_state(self, event: dict):
    """
    Infrastructure-aware balancing decisions based on:
    - Database availability
    - Monitoring coverage
    - Port availability
    - Resource capacity
    """
    state = event['data']['state']
    self.infrastructure_state = state  # ← Сохраняет!

    # Проверки:
    if state.get('cpu_usage') > 0.85:
        # Conservative balancing

    if not state.get('postgres_available'):
        # Halt new resource allocations

    if state.get('monitoring_coverage') < 0.5:
        # Limited visibility mode
```

**Реагирует на аварии** (`main.py:295-340`):

```python
async def _handle_infrastructure_emergency(self, event: dict):
    """IMMEDIATELY adjust balancing strategy"""

    if emergency['type'] == 'database_unavailable':
        # Stop aggressive resource allocations
        # Switch to emergency mode

    elif emergency['type'] == 'resource_exhausted':
        # Trigger immediate resource optimization
        # Prioritize resource freeing

    elif emergency['type'] == 'monitoring_unavailable':
        # Use conservative balancing without metrics
```

---

### 3. **Policy Engine** ← Governance layer

**Location**: `/infrastructure/policy-engine/`

**Роль**: YAML-based infrastructure governance

**НЕ содержит**: Прямые импорты AI Office сервисов
**Связь**: **Через PolicyAwareOrchestrator** (AI Orchestration)

**Определяет политики для сервисов** (`policies.yaml:93-201`):

```yaml
# Policy Engine знает про AI Office сервисы!
workflow_intelligence:
  priority: 2  # High
  rto_seconds: 180
  max_auto_attempts: 3
  recovery_strategy: "restart"

expertise_center:
  priority: 3  # Medium
  rto_seconds: 300

mio_manager:  # ← AI Office!
  priority: 2  # High
  rto_seconds: 120
  recovery_strategy: "restart"
  notify_teams: ["ops", "platform"]

monitoring:
  priority: 1  # Critical
  rto_seconds: 90
  escalate_immediately: true
```

**Упоминания AI Office** (из grep):
- ✅ `policies.yaml`: mio_manager policy
- ✅ `README.md`: Integration examples
- ✅ Архивные документы Phase 1.1

**Как интегрируется**:

```
AI Office Service (сбой)
    ↓
AI Orchestrator (обнаруживает)
    ↓
PolicyAwareOrchestrator (проверяет)
    ↓
Policy Engine (валидирует действия)
    ↓
Decision: Allowed/Escalate
```

---

## 🔗 Интеграционная архитектура

### Схема взаимодействия

```
┌─────────────────────────────────────────────────────────────┐
│                        EventBus (Redis)                      │
│                    Единая шина событий                       │
└─────────────────────────────────────────────────────────────┘
         ↑                 ↑                 ↑
         │                 │                 │
    ┌────┴────┐       ┌────┴────┐      ┌────┴────┐
    │   AI    │       │ Balancer│      │  Policy │
    │  Event  │       │ Service │      │  Engine │
    │ Manager │       │         │      │    ↕    │
    └─────────┘       └─────────┘      │  AI     │
         ↑                                 Orch   │
         │                              └─────────┘
    ┌────┴────────────────┐
    │  AI Office Infra    │
    ├─────────────────────┤
    │ • orchestrator      │
    │ • mio-manager       │
    │ • analytics         │
    │ • db-intelligence   │
    │ • devops-agent      │
    │ • agent-router      │
    └─────────────────────┘
```

### Поток событий

**1. Service Health Check**:
```
MIO Manager (Resource Tracker)
    → publish: platform.resources.snapshot
        → AI Event Manager (получает)
        → Infrastructure State Monitor (обрабатывает)
            → publish: platform.infrastructure.state_updated
                → Balancer Service (получает)
                → Adjusts balancing strategy
```

**2. Emergency Detection**:
```
AI Event Manager (обнаруживает PostgreSQL down)
    → publish: platform.infrastructure.emergency
        {type: 'database_unavailable', resource: 'postgres'}
            → Balancer Service (получает)
                → Switches to emergency mode
                → Halts new allocations
```

**3. Scaling Strategy**:
```
AI Event Manager (видит CPU > 85%)
    → InfrastructureStateMonitor.suggest_scaling_strategy()
        → strategy = 'scale_resources'
            → publish: platform.infrastructure.strategy_recommended
                → Balancer Service (получает)
                    → Enables aggressive optimization
```

**4. Policy Validation** (через AI Orchestration):
```
MIO Manager (сбой)
    → AI Orchestrator (обнаруживает)
        → PolicyAwareOrchestrator (проверяет)
            → Policy Engine.get_recovery_policy('mio_manager')
                → {priority: 2, rto: 120s, strategy: 'restart'}
                    → Decision: Auto-restart allowed
```

---

## 📋 Проверка компонентов

### AI Office Infrastructure

| Сервис | Main.py | EventBus | Balancer связь | Policy связь |
|--------|---------|----------|----------------|--------------|
| **ai-event-manager** | ✅ | ✅ Публикует | ✅ Прямая (publish) | ⚠️ Косвенная (AI Orch) |
| **mio-manager** | ✅ | ✅ Subscriber | ✅ Через события | ✅ Policy defined |
| **orchestrator** | ✅ | Вероятно | ⚠️ Косвенная | ✅ PolicyAware |
| **analytics-specialist** | ✅ | Вероятно | ⚠️ Нет данных | ❓ |
| **db-intelligence** | ✅ | Вероятно | ⚠️ Нет данных | ❓ |
| **devops-agent** | ✅ | Вероятно | ⚠️ Нет данных | ❓ |
| **agent-router** | ✅ router.py | ⚠️ Не найдено | ❓ | ❓ |

### Infrastructure Core

| Компонент | Связь с AI Office | Тип связи |
|-----------|-------------------|-----------|
| **policy-engine** | ✅ mio_manager policy | YAML config |
| **balancer-service** | ✅ EventBus subscriber | Events |
| **balancer-service** | ✅ infrastructure_state | Runtime state |

---

## 🔍 Детали найденных связей

### 1. AI Event Manager → Balancer Service

**Файл**: `ai-event-manager/monitoring/infrastructure_state.py`

**Связь**: Публикует события, которые Balancer Service слушает

```python
# ai-event-manager публикует:
await self.eventbus.publish(
    'platform.infrastructure.state_updated',
    {
        'state': asdict(state),
        'timestamp': state.timestamp.isoformat()
    }
)

# balancer-service слушает:
await self.eventbus.subscribe(
    'platform.infrastructure.state_updated',
    self._handle_infrastructure_state
)
```

**Данные в событии**:
- `ports_available`, `ports_used`
- `prometheus_available`, `grafana_available`
- `postgres_available`, `redis_available`
- `total_services`, `healthy_services`
- `cpu_usage`, `memory_usage`, `disk_usage`
- `monitoring_coverage`, `database_coverage`

**Как Balancer использует**:
- Сохраняет в `self.infrastructure_state`
- Переключается на conservative mode при высоком CPU
- Останавливает allocations при недоступной БД
- Использует limited visibility mode при низком monitoring coverage

---

### 2. Policy Engine → MIO Manager

**Файл**: `policy-engine/policies.yaml:113-121`

```yaml
mio_manager:
  priority: 2  # High
  rto_seconds: 120  # 2 minutes
  max_auto_attempts: 3
  escalate_immediately: false
  recovery_strategy: "restart"
  notify_teams: ["ops", "platform"]
  require_approval: false
```

**Связь**: Определяет правила восстановления MIO Manager

**Использование**:
1. AI Orchestrator обнаруживает сбой MIO Manager
2. PolicyAwareOrchestrator читает эту policy
3. Проверяет: RTO = 120s, можно 3 попытки auto-restart
4. Принимает решение: Auto-resolve или Escalate

---

### 3. Balancer Service ← Infrastructure emergencies

**Файл**: `balancer-service/main.py:295-340`

**События от AI Event Manager**:

```python
# PostgreSQL down
{
  'type': 'database_unavailable',
  'resource': 'postgres',
  'severity': 'critical'
}
→ Balancer: "Halt new resource allocations"

# CPU exhausted
{
  'type': 'resource_exhausted',
  'resource': 'cpu',
  'severity': 'high',
  'usage': 0.95
}
→ Balancer: "Trigger immediate resource optimization"

# Prometheus down
{
  'type': 'monitoring_unavailable',
  'resource': 'prometheus',
  'severity': 'high'
}
→ Balancer: "Use conservative balancing without metrics"
```

---

## 🎯 Выводы

### ✅ Что связано:

1. **AI Event Manager ↔ Balancer Service**
   - **Тип**: EventBus (асинхронные события)
   - **События**: infrastructure.state_updated, emergency, strategy
   - **Направление**: AI Event Manager → Balancer Service
   - **Статус**: ✅ Полностью интегрировано

2. **Policy Engine ↔ MIO Manager**
   - **Тип**: YAML configuration
   - **Файл**: policies.yaml (mio_manager section)
   - **Направление**: Policy Engine → AI Orchestrator → MIO Manager
   - **Статус**: ✅ Policy defined

3. **Policy Engine ↔ AI Orchestration**
   - **Тип**: PolicyAwareOrchestrator
   - **Файл**: `intelligent-core/orchestration/ai-orchestration/policy_aware_orchestrator.py`
   - **Направление**: Двусторонняя (AI проверяет policy)
   - **Статус**: ✅ Production ready

### ⚠️ Что НЕ связано напрямую:

1. **Orchestrator, Analytics, DB-Intelligence, DevOps, Agent Router**
   - НЕ найдено прямых импортов Policy Engine
   - НЕ найдено прямых импортов Balancer Service
   - **Связь**: Вероятно через EventBus (нужна проверка)

2. **Policy Engine ↔ Balancer Service**
   - НЕТ прямых импортов
   - **Связь**: Косвенная через AI Orchestration
   - Balancer Service использует infrastructure state (от AI Event Manager)
   - Policy Engine валидирует recovery actions (через AI Orchestrator)

### 📊 Паттерн интеграции:

**Event-Driven Architecture**:
- ✅ Loose coupling (нет прямых зависимостей)
- ✅ EventBus как единая шина
- ✅ Асинхронная коммуникация
- ✅ Scalable и resilient

**Governance Layer**:
- ✅ Policy Engine = Правила (YAML)
- ✅ AI Orchestration = Исполнение (validates against policies)
- ✅ AI Office Services = Исполнители (follow orchestrator)

---

## 🔧 Рекомендации

### 1. Добавить EventBus регистрацию во все AI Office сервисы

```python
# В каждом main.py AI Office сервиса:
from infrastructure.runtime.service_discovery.eventbus_integration import (
    publish_service_started,
    publish_service_heartbeat
)

async def startup():
    await publish_service_started(
        eventbus=eventbus,
        service_name="orchestrator",  # или другой сервис
        orchestrator="ai-office",
        port=8059
    )
```

### 2. Добавить policies для недостающих сервисов

В `policies.yaml` добавить:

```yaml
# orchestrator
orchestrator:
  priority: 2  # High
  rto_seconds: 120
  recovery_strategy: "restart"

# analytics-specialist
analytics_specialist:
  priority: 3  # Medium
  rto_seconds: 180
  recovery_strategy: "restart"

# db-intelligence
db_intelligence:
  priority: 2  # High
  rto_seconds: 120
  recovery_strategy: "restart"

# devops-agent
devops_agent:
  priority: 3  # Medium
  rto_seconds: 240
  recovery_strategy: "restart"

# agent-router
agent_router:
  priority: 2  # High
  rto_seconds: 120
  recovery_strategy: "restart"
```

### 3. Документировать EventBus события для каждого сервиса

Создать `EVENTS.md` для каждого AI Office сервиса с:
- События которые публикует
- События на которые подписан
- Формат данных

---

## 📚 Связанные документы

1. `SERVICE_REGISTRATION_SYSTEM.md` - System service discovery
2. `SERVICE_DISCOVERY_CATALOG_INTEGRATION.md` - Service Catalog integration
3. `infrastructure/policy-engine/README.md` - Policy Engine docs
4. `infrastructure/balancer-service/README.md` - Balancer Service docs

---

**Status**: ✅ Анализ завершён
**Confidence**: 95% (проверены ключевые компоненты)
**Связь найдена**: EventBus + Policy Engine
**Паттерн**: Event-Driven + Governance Layer
