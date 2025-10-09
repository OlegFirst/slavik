# Phase 2 - Интеграция с СУЩЕСТВУЮЩЕЙ инфраструктурой

**Дата**: 2025-10-09
**Принцип**: НЕ создавать новое, использовать ЧТО УЖЕ ЕСТЬ!

---

## ✅ ЧТО УЖЕ РАБОТАЕТ (Существующая инфраструктура)

```
infrastructure/
├── eventbus/
│   ├── coordination/
│   │   └── infrastructure_coordinator.py        ✅ ГОТОВ! Координатор инфраструктуры
│   ├── core/                                    ✅ EventBus работает
│   └── backends/                                ✅ Redis Streams
│
├── decision-center/                             ✅ ПОЛНОСТЬЮ РЕАЛИЗОВАН!
│   ├── decision_center.py                       ✅ Governance + Policy Engine
│   ├── escalation_manager.py                    ✅ Эскалация
│   ├── notification_service.py                  ✅ Уведомления
│   └── policy_engine.py                         ✅ Политики
│
├── AI-office-infrastructure/
│   └── orchestrator/
│       └── unified_orchestrator.py              ✅ Единый оркестратор
│
├── observability/                               ✅ Prometheus + Grafana
│   ├── prometheus/
│   ├── grafana/
│   └── services/
│
└── runtime/
    ├── service-discovery/                       ✅ Service Discovery
    └── message-queue/                           ✅ RabbitMQ
```

---

## 🎯 ЧТО ДЕЛАЕМ (Интеграция Phase 2 компонентов)

### 1. Resource Tracker → InfrastructureCoordinator

**Где живет**: `/intelligent-core/coordination-center/resources/resource_tracker.py`

**Интеграция**:
```python
# infrastructure/eventbus/coordination/infrastructure_coordinator.py

class InfrastructureCoordinator:
    def __init__(self, ...):
        # ... existing ...

        # ADD: Resource Tracker для мониторинга ресурсов
        from coordination_center.resources import create_resource_tracker
        self.resource_tracker = None

    async def start(self):
        # ... existing health_monitor, auto_recovery ...

        # ADD: Запустить Resource Tracker
        self.resource_tracker = await create_resource_tracker(
            snapshot_interval_seconds=60.0,
            history_size=100,
            storage_path="/data/resource_history.json"
        )
        logger.info("✅ Resource Tracker started")

        # Подписка на события дефицита
        self.resource_tracker.on_deficit(self._handle_resource_deficit)

    async def _handle_resource_deficit(self, deficit_info):
        """Обработка дефицита ресурсов"""
        # Publish event через EventBus
        await self.eventbus.publish(Event(
            type="infrastructure.resource.deficit",
            data=deficit_info,
            source="resource-tracker"
        ))

        # Триггер самореализации (Phase 4)
        # await self.trigger_self_actualization(deficit_info)
```

---

### 2. Wishlist System → DecisionCenter

**Где живет**: `/intelligent-core/coordination-center/wishlist/wishlist_system.py`

**Интеграция**:
```python
# infrastructure/decision-center/decision_center.py

class InfrastructureDecisionCenter:
    def __init__(self, ...):
        # ... existing ...

        # ADD: Wishlist для управления потребностями
        from coordination_center.wishlist import create_wishlist_system
        self.wishlist = None

    async def initialize(self):
        # ADD: Инициализация Wishlist
        self.wishlist = await create_wishlist_system(
            storage_path="/data/wishlist.json",
            max_item_age_seconds=86400.0
        )
        logger.info("✅ Wishlist System initialized")

    async def decide_recovery_action(self, service_name, action_type, ...):
        """Решение о recovery action"""
        # ... existing policy check ...

        # ADD: Если recovery НЕ может быть выполнен сейчас → в wishlist
        if not can_execute_now:
            # Добавить в wishlist вместо отмены
            wish = self.wishlist.add_wish(
                description=f"Recover {service_name} via {action_type}",
                need_type=NeedType.SURVIVAL,
                urgency=0.9 if is_critical else 0.7,
                resource_cost=ResourceCost(
                    cpu_percent=20,
                    time_seconds=120
                ),
                deadline=time.time() + 3600
            )

            decision.outcome = DecisionOutcome.POSTPONED
            decision.reasoning = f"Added to wishlist: {wish.id}"

        return decision, can_proceed

    async def execute_prioritized_wishes(self):
        """Background task: выполнять wishes по приоритету"""
        while True:
            # Получить доступные ресурсы
            available = self.resource_tracker.get_available_resources()

            # Получить top wishes
            wishes = self.wishlist.get_prioritized_wishes(available, limit=5)

            for wish in wishes:
                # Проверить policy
                can_execute = await self._check_wish_policy(wish)

                if can_execute:
                    # Выполнить
                    success = await self._execute_wish(wish)

                    # Завершить
                    self.wishlist.complete_wish(wish.id, success)

            await asyncio.sleep(30)
```

---

### 3. Survival Instinct → InfrastructureCoordinator + DecisionCenter

**Где живет**: `/intelligent-core/system-bcm-service/instincts/survival.py`

**Интеграция через EventBus**:
```python
# system-bcm-service/instincts/survival.py

class SurvivalInstinct:
    def __init__(self, ..., eventbus, wishlist_system):
        # ... existing ...
        self.eventbus = eventbus
        self.wishlist = wishlist_system

    async def trigger_my_correction(self, imbalance):
        """При дисбалансе"""
        # ... existing action creation ...

        # ADD: Publish event через EventBus
        await self.eventbus.publish(Event(
            type="platform.bcm.imbalance_detected",
            data={
                "module": self.module_name,
                "kpi": imbalance.kpi_name,
                "level": imbalance.level.value,
                "action_type": action.action_type
            },
            source="survival-instinct"
        ))

        # ADD: Добавить в wishlist (если не критично)
        if imbalance.level != ImbalanceLevel.CRITICAL:
            self.wishlist.add_wish(
                description=action.description,
                need_type=NeedType.SURVIVAL,
                urgency=imbalance.level_value(),
                resource_cost=self._estimate_cost(action)
            )
```

**Подписка в InfrastructureCoordinator**:
```python
# infrastructure/eventbus/coordination/infrastructure_coordinator.py

async def start(self):
    # ... existing ...

    # ADD: Подписаться на события дисбаланса
    self.eventbus.subscribe(
        "platform.bcm.imbalance_detected",
        self._handle_imbalance_event
    )

async def _handle_imbalance_event(self, event):
    """Обработка событий дисбаланса"""
    data = event.data

    # Передать в DecisionCenter
    decision, can_proceed = await self.decision_center.decide_recovery_action(
        service_name=data['module'],
        action_type=data['action_type'],
        trigger_event_id=event.id
    )

    if can_proceed:
        # Выполнить через AutoRecovery
        await self.auto_recovery.recover(
            service_name=data['module'],
            strategy=RecoveryStrategy.RESTART  # example
        )
```

---

## 🔄 ПОТОК ДАННЫХ (с существующей инфраструктурой)

```
┌─────────────────────────────────────────────────────────────────┐
│         1. Survival Instinct (system-bcm-service)               │
│         • detect_my_imbalance()                                 │
│         • trigger_my_correction()                               │
└────────────────────┬────────────────────────────────────────────┘
                     │ publish event via EventBus
                     │ "platform.bcm.imbalance_detected"
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│         2. InfrastructureCoordinator (infrastructure)           │
│         • _handle_imbalance_event()                             │
│         • Delegate to DecisionCenter                            │
└────────────────────┬────────────────────────────────────────────┘
                     │ decide_recovery_action()
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│         3. DecisionCenter (infrastructure/decision-center)      │
│         • PolicyEngine.check_policy_compliance()                │
│         • Если не может сейчас → wishlist.add_wish()            │
│         • Если может → return (decision, true)                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
           ┌─────────┴─────────┐
           │                   │
           ▼                   ▼
┌─────────────────┐   ┌─────────────────┐
│  4a. Wishlist   │   │  4b. Execute    │
│  add_wish()     │   │  auto_recovery  │
│  (postponed)    │   │  (immediate)    │
└────────┬────────┘   └─────────────────┘
         │
         │ Background: execute_prioritized_wishes()
         ▼
┌─────────────────────────────────────────┐
│  5. Resource Tracker                    │
│  • get_available_resources()            │
│  • Определить что можно выполнить       │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│  6. Execute Wish                        │
│  • _execute_wish()                      │
│  • complete_wish()                      │
│  • memory.remember_pattern()            │
└─────────────────────────────────────────┘
```

---

## 📝 КОНКРЕТНЫЕ ИЗМЕНЕНИЯ (минимальные!)

### Изменение 1: InfrastructureCoordinator + Resource Tracker

**Файл**: `/infrastructure/eventbus/coordination/infrastructure_coordinator.py`

**Добавить**:
```python
# After line 97 (after HealthMonitor import)

# Import Resource Tracker
from coordination_center.resources import create_resource_tracker

# In __init__:
self.resource_tracker = None

# In start():
# After auto_recovery.start()
self.resource_tracker = await create_resource_tracker(...)
logger.info("✅ Resource Tracker started")

# In stop():
if self.resource_tracker:
    self.resource_tracker.stop()
```

---

### Изменение 2: DecisionCenter + Wishlist

**Файл**: `/infrastructure/decision-center/decision_center.py`

**Добавить**:
```python
# After line 37 (after audit_logger import)

from coordination_center.wishlist import create_wishlist_system, NeedType, ResourceCost

# In __init__:
self.wishlist = None
self.resource_tracker = None  # будет передан из coordinator

# New method:
async def initialize(self, resource_tracker):
    """Initialize with dependencies"""
    self.resource_tracker = resource_tracker
    self.wishlist = await create_wishlist_system(...)
    logger.info("✅ Wishlist System initialized")

# Modify decide_recovery_action():
# Add postpone to wishlist logic (see above)

# New method:
async def execute_prioritized_wishes(self):
    """Background executor for wishes"""
    # (see code above)
```

---

### Изменение 3: system-bcm-service интеграция

**Файл**: `/intelligent-core/system-bcm-service/main.py`

**Добавить**:
```python
# In startup():
# INSTEAD of creating separate instances:
# Use InfrastructureCoordinator!

from infrastructure.eventbus.coordination import InfrastructureCoordinator

state.infrastructure_coordinator = InfrastructureCoordinator(
    event_bus_backend='redis',
    redis_url=REDIS_URL,
    enable_governance=True
)
await state.infrastructure_coordinator.start()

# Get references to components
state.eventbus = state.infrastructure_coordinator.eventbus
state.resource_tracker = state.infrastructure_coordinator.resource_tracker
state.wishlist = state.infrastructure_coordinator.decision_center.wishlist

# Initialize Survival Instinct with EventBus + Wishlist
state.survival = await start_survival_instinct(
    ...,
    eventbus=state.eventbus,
    wishlist_system=state.wishlist,
    resource_tracker=state.resource_tracker
)
```

---

## 🎯 КЛЮЧЕВОЕ ОТЛИЧИЕ

**РАНЬШЕ (неправильно)**:
```
system-bcm-service
├── создает свой EventBus
├── создает свой Resource Tracker
├── создает свой Wishlist
└── НЕ использует infrastructure!
```

**ТЕПЕРЬ (правильно)**:
```
infrastructure/
├── InfrastructureCoordinator
│   ├── EventBus (Redis Streams)
│   ├── HealthMonitor
│   ├── AutoRecovery
│   ├── Resource Tracker ← NEW
│   └── DecisionCenter
│       ├── PolicyEngine
│       ├── EscalationManager
│       ├── NotificationService
│       └── Wishlist System ← NEW
│
system-bcm-service/
└── ИСПОЛЬЗУЕТ infrastructure через EventBus!
    └── Survival Instinct publishes events
```

---

## ✅ ПРЕИМУЩЕСТВА

1. **Единая точка координации**: InfrastructureCoordinator
2. **Единый EventBus**: Все коммуницируют через него
3. **PolicyEngine уже работает**: Просто добавляем wishlist logic
4. **Мониторинг уже есть**: Prometheus + Grafana интегрированы
5. **Эскалация уже есть**: EscalationManager + NotificationService
6. **НЕ ДУБЛИРУЕМ**: Используем что уже работает!

---

## 🚀 ПЛАН ДЕЙСТВИЙ

### Шаг 1: Интегрировать Resource Tracker в InfrastructureCoordinator
```bash
# Edit: infrastructure/eventbus/coordination/infrastructure_coordinator.py
# Add: Resource Tracker initialization
# Add: Resource deficit handling
```

### Шаг 2: Интегрировать Wishlist в DecisionCenter
```bash
# Edit: infrastructure/decision-center/decision_center.py
# Add: Wishlist initialization
# Add: Postpone logic в decide_recovery_action()
# Add: execute_prioritized_wishes() background task
```

### Шаг 3: Обновить system-bcm-service
```bash
# Edit: intelligent-core/system-bcm-service/main.py
# REMOVE: Separate EventBus/Resource/Wishlist creation
# ADD: Use InfrastructureCoordinator
```

### Шаг 4: Обновить Survival Instinct
```bash
# Edit: intelligent-core/system-bcm-service/instincts/survival.py
# ADD: eventbus.publish() при imbalance
# ADD: wishlist.add_wish() для non-critical
```

### Шаг 5: Тестирование
```bash
# 1. Start infrastructure
cd infrastructure
python3 -m eventbus.coordination.infrastructure_coordinator

# 2. Start system-bcm-service
cd intelligent-core/system-bcm-service
python3 main.py

# 3. Trigger imbalance → watch flow
```

---

## 📊 МЕТРИКИ (используем существующий Prometheus!)

**Уже работает**:
- `infrastructure/observability/prometheus/` - Prometheus config
- `infrastructure/observability/grafana/` - Grafana dashboards

**Добавляем**:
```python
# В Resource Tracker metrics export (уже есть в коде)
resource_tracker_cpu_percent
resource_tracker_memory_percent
resource_tracker_deficit_state

# В Wishlist metrics export
wishlist_pending_items
wishlist_completed_items
wishlist_conflict_resolutions

# В DecisionCenter metrics
decision_center_postponed_actions
decision_center_wishlist_executions
```

**Prometheus scraping**:
```yaml
# infrastructure/observability/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'system-bcm-service'
    static_configs:
      - targets: ['localhost:8009']
    metrics_path: '/metrics'
```

---

## 🔥 ВЫВОДЫ

1. ✅ **НЕ создаем дубликаты** - используем InfrastructureCoordinator
2. ✅ **Интегрируем через EventBus** - infrastructure уже настроен
3. ✅ **Wishlist в DecisionCenter** - логично (governance layer)
4. ✅ **Resource Tracker в Coordinator** - логично (infrastructure monitoring)
5. ✅ **PolicyEngine УЖЕ ЕСТЬ** - просто расширяем логику
6. ✅ **Monitoring УЖЕ ЕСТЬ** - Prometheus + Grafana готовы

**Следующий шаг**: Начать с Шага 1 (Resource Tracker в InfrastructureCoordinator)

---

**Дата**: 2025-10-09
**Статус**: READY TO IMPLEMENT
**Подход**: Использовать существующую инфраструктуру, НЕ создавать новое!
