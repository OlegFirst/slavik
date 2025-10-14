# План Интеграции: central-brain + balancer-service → Unified System

**Дата**: 2025-10-10
**Проблема**: Сервисы изолированы, нет синергии
**Решение**: Интеграция в единую event-driven систему

---

## 🎯 Текущая Проблема

### central-brain
- ❌ **Standalone CLI tool** - никуда не интегрирован
- ❌ **Simple rules** (if-else), НЕ AI
- ❌ **НЕ публикует** события в EventBus
- ❌ **НЕ координируется** с системой
- ❌ **Кому отчитывается?** НИКОМУ - просто print()

### balancer-service
- ✅ Подключен к EventBus
- ✅ Слушает события (imbalance_detected, resource_snapshot)
- ❌ **НЕ знает** о состоянии инфраструктуры (порты, БД, метрики)
- ❌ Логика в intelligent-core, но **координация слабая**

### Проблема координации
```
central-brain          balancer-service
     │                       │
     │                       │
     ▼                       ▼
  (никуда)              EventBus
                            │
                            ▼
                    intelligent-core/balancers
                            │
                            ▼
                    (принимает решения)
```

**Вопрос**: Кто знает о состоянии инфраструктуры? central-brain!
**Вопрос**: Кто принимает решения об балансировке? intelligent-core/balancers!
**Проблема**: Они НЕ общаются!

---

## ✅ Решение: 3 варианта интеграции

### Вариант 1: central-brain → ai-event-manager (РЕКОМЕНДУЮ ✅)

**Идея**: Перенести central-brain в ai-event-manager как **state monitoring module**

**Архитектура**:
```
┌─────────────────────────────────────────────────────────────┐
│  ai-event-manager (Port 8055)                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  IntegrationManager                                │     │
│  │  ├── EventBus (уже есть ✅)                        │     │
│  │  ├── DevOps Agent (уже есть ✅)                    │     │
│  │  ├── GitHub Integration (уже есть ✅)              │     │
│  │  ├── MIO Manager (уже есть ✅)                     │     │
│  │  └── Infrastructure State Monitor (NEW!) ⭐       │     │
│  │      └── central-brain logic                      │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Endpoints (NEW):                                           │
│  ├── GET  /infrastructure/state                            │
│  ├── GET  /infrastructure/resources                        │
│  ├── POST /infrastructure/strategy                         │
│  └── GET  /infrastructure/deployment-check                 │
│                                                              │
│  EventBus Publishing (NEW):                                │
│  ├── platform.infrastructure.state_updated                 │
│  ├── platform.infrastructure.resource_deficit              │
│  └── platform.infrastructure.strategy_recommended          │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ publishes events
                         ▼
                    ┌─────────┐
                    │ EventBus│
                    └─────────┘
                         │
                         │ subscribes
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  balancer-service (ИНТЕГРИРОВАН с ai-event-manager)         │
│  ├── Слушает: platform.infrastructure.state_updated        │
│  ├── Слушает: platform.bcm.imbalance_detected              │
│  ├── Слушает: platform.resources.snapshot                  │
│  └── Принимает решения с учётом ВСЕХ факторов              │
└─────────────────────────────────────────────────────────────┘
```

**Преимущества**:
- ✅ ai-event-manager уже имеет все интеграции
- ✅ EventBus уже подключен
- ✅ Синергия: state monitoring + event intelligence
- ✅ Единая точка мониторинга инфраструктуры
- ✅ balancer-service получает данные через EventBus

**Действия**:
1. Переместить `state_monitor.py` в `ai-event-manager/monitoring/infrastructure_state.py`
2. Добавить EventBus publishing для состояния
3. Добавить API endpoints в ai-event-manager
4. balancer-service подписывается на новые события

---

### Вариант 2: central-brain → balancer-service (АЛЬТЕРНАТИВА)

**Идея**: Встроить central-brain **внутрь** balancer-service

**Архитектура**:
```
┌─────────────────────────────────────────────────────────────┐
│  balancer-service (РАСШИРЕННЫЙ)                             │
│  ├── System Balancer (intelligent-core) ✅                  │
│  ├── 3D Balancer (intelligent-core) ✅                      │
│  ├── Infrastructure State Monitor (NEW!) ⭐                 │
│  │   └── central-brain logic                               │
│  └── EventBus Integration ✅                                │
│                                                              │
│  Решения на основе:                                         │
│  1. Imbalance events (от Survival Instinct)                 │
│  2. Resource snapshots (от Resource Tracker)                │
│  3. Infrastructure state (от встроенного central-brain)     │
└─────────────────────────────────────────────────────────────┘
```

**Преимущества**:
- ✅ Всё в одном месте
- ✅ Быстрые решения (нет EventBus latency)
- ✅ Логика балансировки + инфраструктура вместе

**Недостатки**:
- ❌ balancer-service становится "толстым"
- ❌ Нет переиспользования в других сервисах
- ❌ ai-event-manager не знает о состоянии инфраструктуры

---

### Вариант 3: central-brain → EventBus-driven service (НОВЫЙ СЕРВИС)

**Идея**: Сделать central-brain **полноценным event-driven сервисом**

**Архитектура**:
```
┌─────────────────────────────────────────────────────────────┐
│  infrastructure-state-service (NEW SERVICE)                 │
│  ├── State Monitor (central-brain logic)                    │
│  ├── EventBus Publisher                                     │
│  └── REST API                                               │
│                                                              │
│  Publishes:                                                 │
│  ├── platform.infrastructure.state_updated (every 60s)      │
│  ├── platform.infrastructure.emergency (critical)           │
│  └── platform.infrastructure.strategy (recommendations)     │
│                                                              │
│  Subscribes:                                                │
│  ├── platform.service.registered (new service)              │
│  └── platform.service.unregistered (service down)           │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ EventBus
                         ▼
              ┌──────────────────────┐
              │  ai-event-manager    │
              │  balancer-service    │
              │  mio-manager         │
              │  orchestrator        │
              └──────────────────────┘
```

**Преимущества**:
- ✅ Полноценный event-driven сервис
- ✅ Все могут подписаться на состояние
- ✅ Separation of concerns

**Недостатки**:
- ❌ Ещё один сервис для поддержки
- ❌ Дублирование функционала с ai-event-manager

---

## 🏆 Рекомендация: Вариант 1

**Интегрировать central-brain в ai-event-manager**

### Почему?

1. **ai-event-manager уже hub для координации**:
   - EventBus ✅
   - DevOps Agent ✅
   - GitHub Integration ✅
   - MIO Manager ✅
   - + Infrastructure State = COMPLETE

2. **Синергия с event intelligence**:
   - Event gaps detection + Infrastructure state = Smart decisions
   - AI recommendations + Infrastructure capacity = Realistic plans

3. **Единая точка мониторинга**:
   - Events ✅
   - Infrastructure ✅
   - Resources ✅
   - Services ✅

4. **balancer-service остаётся focused**:
   - Только балансировка
   - Получает данные через EventBus
   - Не раздувается

---

## 📋 Implementation Plan - Вариант 1

### Phase 1: Перенос central-brain в ai-event-manager (2 часа)

**Шаг 1**: Создать модуль infrastructure monitoring
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager

mkdir -p monitoring
touch monitoring/__init__.py
touch monitoring/infrastructure_state.py
```

**Шаг 2**: Перенести логику state_monitor.py
```python
# monitoring/infrastructure_state.py
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class InfrastructureState:
    """Infrastructure state (от central-brain)"""
    timestamp: datetime
    ports_available: int
    ports_used: int
    prometheus_available: bool
    # ... all fields from central-brain

class InfrastructureStateMonitor:
    """
    Infrastructure State Monitor

    Monitors infrastructure and publishes state to EventBus.
    Based on central-brain logic.
    """

    def __init__(self, eventbus, project_manager_client):
        self.eventbus = eventbus
        self.project_manager = project_manager_client
        self.current_state: Optional[InfrastructureState] = None

    async def update_state(self):
        """Collect state and publish to EventBus"""
        # Get state from project manager
        state_data = await self.project_manager.get_system_state()

        # Transform to InfrastructureState
        state = InfrastructureState(...)

        self.current_state = state

        # PUBLISH to EventBus (NEW!)
        await self.eventbus.publish(
            'platform.infrastructure.state_updated',
            {
                'state': state.__dict__,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority='normal'
        )

        # Check for critical issues
        if not state.postgres_available or not state.redis_available:
            await self.eventbus.publish(
                'platform.infrastructure.emergency',
                {
                    'type': 'database_unavailable',
                    'severity': 'critical',
                    'state': state.__dict__
                },
                priority='high'
            )

    async def suggest_strategy(self) -> Dict:
        """Suggest scaling strategy (от central-brain)"""
        # Same logic as central-brain
        ...

        # PUBLISH strategy to EventBus (NEW!)
        await self.eventbus.publish(
            'platform.infrastructure.strategy_recommended',
            {
                'strategy': strategy,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority='normal'
        )

        return strategy

    async def continuous_monitoring(self, interval: int = 60):
        """Continuous monitoring with EventBus publishing"""
        while True:
            await self.update_state()
            await self.suggest_strategy()
            await asyncio.sleep(interval)
```

**Шаг 3**: Добавить в IntegrationManager
```python
# integrations/__init__.py
from monitoring.infrastructure_state import InfrastructureStateMonitor

class IntegrationManager:
    def __init__(self, config):
        # ... existing code ...
        self.infrastructure_monitor = None

    async def initialize_all(self):
        # ... existing integrations ...

        # Initialize Infrastructure State Monitor
        self.infrastructure_monitor = InfrastructureStateMonitor(
            eventbus=self.eventbus,
            project_manager_client=self.project_manager  # NEW CLIENT
        )

        # Start continuous monitoring
        asyncio.create_task(
            self.infrastructure_monitor.continuous_monitoring(interval=60)
        )
```

**Шаг 4**: Добавить API endpoints
```python
# main.py
@app.get("/infrastructure/state")
async def get_infrastructure_state():
    """Get current infrastructure state"""
    if not integration_manager or not integration_manager.infrastructure_monitor:
        raise HTTPException(status_code=503, detail="Monitor not available")

    state = integration_manager.infrastructure_monitor.current_state
    return {
        "status": "success",
        "state": state.__dict__ if state else None
    }

@app.get("/infrastructure/resources")
async def get_available_resources():
    """Get available resources"""
    monitor = integration_manager.infrastructure_monitor
    resources = monitor.get_available_resources()
    return {
        "status": "success",
        "resources": resources
    }

@app.get("/infrastructure/strategy")
async def get_scaling_strategy():
    """Get recommended scaling strategy"""
    monitor = integration_manager.infrastructure_monitor
    strategy = await monitor.suggest_strategy()
    return {
        "status": "success",
        "strategy": strategy
    }

@app.post("/infrastructure/deployment-check")
async def check_deployment(service_name: str, requires_db: bool = True, requires_metrics: bool = True):
    """Check if service can be deployed"""
    monitor = integration_manager.infrastructure_monitor
    can_deploy, reason = monitor.can_deploy_new_service(
        service_name=service_name,
        requires_db=requires_db,
        requires_metrics=requires_metrics
    )
    return {
        "can_deploy": can_deploy,
        "reason": reason
    }
```

---

### Phase 2: Интеграция balancer-service (1 час)

**Шаг 1**: Подписаться на новые события
```python
# balancer-service/main.py
async def _subscribe_to_events(self):
    # ... existing subscriptions ...

    # NEW: Subscribe to infrastructure state
    await self.eventbus.subscribe(
        'platform.infrastructure.state_updated',
        self._handle_infrastructure_state
    )

    # NEW: Subscribe to infrastructure emergency
    await self.eventbus.subscribe(
        'platform.infrastructure.emergency',
        self._handle_infrastructure_emergency
    )

    # NEW: Subscribe to strategy recommendations
    await self.eventbus.subscribe(
        'platform.infrastructure.strategy_recommended',
        self._handle_strategy_recommendation
    )

async def _handle_infrastructure_state(self, event: dict):
    """Handle infrastructure state update"""
    state = event['data']['state']

    # Check if critical resources unavailable
    if not state['postgres_available'] or not state['redis_available']:
        self.logger.warning(
            "Critical infrastructure issue detected",
            postgres=state['postgres_available'],
            redis=state['redis_available']
        )

        # Trigger conservative balancing
        # (avoid aggressive resource allocation)

    # Store state for balancing decisions
    self.infrastructure_state = state

async def _handle_infrastructure_emergency(self, event: dict):
    """Handle infrastructure emergency"""
    emergency_type = event['data']['type']

    if emergency_type == 'database_unavailable':
        # IMMEDIATELY adjust balancing
        # - Stop aggressive allocations
        # - Preserve existing resources
        # - Alert System Balancer
        pass
```

**Шаг 2**: Использовать infrastructure state в балансировке
```python
# balancer-service/main.py
async def _handle_imbalance_event(self, event: dict):
    """Handle imbalance with infrastructure awareness"""

    # Check infrastructure capacity FIRST
    if hasattr(self, 'infrastructure_state'):
        infra = self.infrastructure_state

        # If low monitoring coverage, don't allocate aggressively
        if infra['monitoring_coverage'] < 0.5:
            self.logger.warning(
                "Low monitoring coverage - conservative balancing"
            )
            # Use conservative strategy

        # If DB under pressure, avoid DB-heavy allocations
        if infra['database_coverage'] > 0.9:
            self.logger.warning(
                "DB capacity near limit - avoid DB allocations"
            )

    # Proceed with balancing decision
    # ... existing code ...
```

---

### Phase 3: Архивирование старого central-brain (15 минут)

```bash
# Переместить в архив
cd /Users/MD/AI-Platform-ISO/infrastructure
mkdir -p _archive-deprecated-2025-10-10/
mv central-brain/ _archive-deprecated-2025-10-10/central-brain-migrated-to-ai-event-manager/

# Создать README
cat > _archive-deprecated-2025-10-10/central-brain-migrated-to-ai-event-manager/README.md << 'EOF'
# Central Brain - MIGRATED

**Дата архивации**: 2025-10-10
**Причина**: Интегрирован в ai-event-manager

## Новое расположение

`/infrastructure/AI-office-infrastructure/ai-event-manager/monitoring/infrastructure_state.py`

## Что изменилось

1. ✅ Интегрирован в ai-event-manager
2. ✅ Публикует события в EventBus
3. ✅ API endpoints добавлены
4. ✅ balancer-service теперь получает infrastructure state

## Восстановление

Не рекомендуется. Используйте новую интеграцию.
EOF
```

---

## 📊 Результат

### До интеграции:
```
central-brain (standalone)     balancer-service (isolated)
     │                               │
     ▼                               ▼
  (никуда)                       EventBus
                                     │
                                     ▼
                              intelligent-core
```

### После интеграции:
```
┌──────────────────────────────────────────────────────┐
│  ai-event-manager (Hub)                              │
│  ├── Event Intelligence ✅                           │
│  ├── Infrastructure State Monitor ✅ (ex central-brain)
│  └── EventBus Publisher ✅                           │
└─────────────────────┬────────────────────────────────┘
                      │
                      │ Events:
                      │ - platform.infrastructure.state_updated
                      │ - platform.infrastructure.emergency
                      │ - platform.infrastructure.strategy_recommended
                      ▼
              ┌────────────────┐
              │    EventBus    │
              └───────┬────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐
│balancer-    │ │mio-      │ │orchestr- │
│service      │ │manager   │ │ator      │
└─────────────┘ └──────────┘ └──────────┘
```

### Преимущества:
- ✅ **Синергия**: Infrastructure state + Event intelligence = Smart platform
- ✅ **Event-driven**: Все через EventBus
- ✅ **Reusability**: Все сервисы получают infrastructure state
- ✅ **No duplication**: Один источник истины для infrastructure
- ✅ **Smart balancing**: balancer-service учитывает infrastructure capacity

---

## ✅ Checklist выполнения

### Phase 1: ai-event-manager integration
- [ ] Создать `monitoring/infrastructure_state.py`
- [ ] Перенести логику из `central-brain/state_monitor.py`
- [ ] Добавить EventBus publishing
- [ ] Добавить API endpoints
- [ ] Интегрировать в IntegrationManager
- [ ] Тесты

### Phase 2: balancer-service integration
- [ ] Подписаться на `platform.infrastructure.*` события
- [ ] Обработчики событий
- [ ] Использовать infrastructure state в балансировке
- [ ] Тесты

### Phase 3: Cleanup
- [ ] Архивировать `/infrastructure/central-brain/`
- [ ] Обновить документацию
- [ ] Проверить, что всё работает

---

## 🚀 Timeline

**Total**: 3-4 часа

- Phase 1: 2 часа
- Phase 2: 1 час
- Phase 3: 15 минут
- Testing: 45 минут

---

**Готово к началу?** Начнём с Phase 1!
