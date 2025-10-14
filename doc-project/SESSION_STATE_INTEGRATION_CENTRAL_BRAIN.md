# Session State: Integration central-brain → ai-event-manager

**Дата**: 2025-10-10
**Задача**: Интеграция central-brain в ai-event-manager
**Статус**: 🚀 В ПРОЦЕССЕ
**Токены**: 9% осталось - КРИТИЧНО!

---

## 🎯 Что делаем

### Проблема (обнаружена пользователем):
1. **central-brain** (`/infrastructure/central-brain/`) - standalone CLI tool
   - Simple if-else rules (НЕ AI!)
   - НЕ координируется с системой
   - НЕ публикует в EventBus
   - Кому отчитывается? НИКОМУ!

2. **balancer-service** (`/infrastructure/balancer-service/`) - event-driven
   - Слушает EventBus ✅
   - НО НЕ знает о состоянии инфраструктуры ❌
   - НЕ знает о портах, БД, метриках ❌

### Решение: Интегрировать в ai-event-manager

**Почему ai-event-manager?**
- Уже hub для всех интеграций (EventBus, DevOps, GitHub, MIO Manager)
- Имеет IntegrationManager
- Event-driven architecture
- Синергия: Infrastructure State + Event Intelligence

---

## 📋 План действий (3-4 часа)

### Phase 1: Перенос в ai-event-manager (2 часа)

#### Шаг 1: Создать модуль monitoring
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager
mkdir -p monitoring
touch monitoring/__init__.py
touch monitoring/infrastructure_state.py
```

#### Шаг 2: Файл `monitoring/infrastructure_state.py`
**Что перенести из** `/infrastructure/central-brain/state_monitor.py`:
- `class SystemState` → `class InfrastructureState`
- `class CentralBrainStateMonitor` → `class InfrastructureStateMonitor`
- Methods:
  - `collect_state_from_project_manager()` (keep)
  - `update_state()` (ADD EventBus publishing)
  - `get_available_resources()` (keep)
  - `can_deploy_new_service()` (keep)
  - `suggest_scaling_strategy()` (ADD EventBus publishing)
  - `continuous_monitoring()` (keep)

**НОВОЕ - EventBus Publishing**:
```python
# После update_state():
await self.eventbus.publish(
    'platform.infrastructure.state_updated',
    {'state': state.__dict__, 'timestamp': ...}
)

# При critical issues:
await self.eventbus.publish(
    'platform.infrastructure.emergency',
    {'type': 'database_unavailable', 'severity': 'critical', ...}
)

# После suggest_strategy():
await self.eventbus.publish(
    'platform.infrastructure.strategy_recommended',
    {'strategy': strategy, ...}
)
```

#### Шаг 3: Обновить `integrations/__init__.py`
```python
from monitoring.infrastructure_state import InfrastructureStateMonitor

class IntegrationManager:
    def __init__(self, config):
        # ... existing ...
        self.infrastructure_monitor = None

    async def initialize_all(self):
        # ... existing ...

        # NEW:
        self.infrastructure_monitor = InfrastructureStateMonitor(
            eventbus=self.eventbus,
            project_manager_client=...  # TODO: create client
        )

        # Start monitoring
        asyncio.create_task(
            self.infrastructure_monitor.continuous_monitoring(interval=60)
        )
```

#### Шаг 4: Добавить API endpoints в `main.py`
```python
@app.get("/infrastructure/state")
@app.get("/infrastructure/resources")
@app.get("/infrastructure/strategy")
@app.post("/infrastructure/deployment-check")
```

---

### Phase 2: Интеграция balancer-service (1 час)

#### Обновить `/infrastructure/balancer-service/main.py`

**Новые подписки EventBus**:
```python
async def _subscribe_to_events(self):
    # ... existing ...

    # NEW:
    await self.eventbus.subscribe(
        'platform.infrastructure.state_updated',
        self._handle_infrastructure_state
    )
    await self.eventbus.subscribe(
        'platform.infrastructure.emergency',
        self._handle_infrastructure_emergency
    )
    await self.eventbus.subscribe(
        'platform.infrastructure.strategy_recommended',
        self._handle_strategy_recommendation
    )
```

**Новые обработчики**:
```python
async def _handle_infrastructure_state(self, event: dict):
    state = event['data']['state']
    self.infrastructure_state = state

    # Check capacity before balancing
    if not state['postgres_available']:
        # Conservative balancing
        pass

async def _handle_infrastructure_emergency(self, event: dict):
    # IMMEDIATELY adjust balancing
    pass
```

---

### Phase 3: Cleanup (15 мин)

```bash
# Archive old central-brain
cd /Users/MD/AI-Platform-ISO/infrastructure
mkdir -p _archive-deprecated-2025-10-10/
mv central-brain/ _archive-deprecated-2025-10-10/central-brain-migrated-to-ai-event-manager/

# Create README in archive
cat > _archive-deprecated-2025-10-10/central-brain-migrated-to-ai-event-manager/README.md << 'EOF'
# Central Brain - MIGRATED

**Дата**: 2025-10-10
**Новое расположение**:
`/infrastructure/AI-office-infrastructure/ai-event-manager/monitoring/infrastructure_state.py`

Интегрирован в ai-event-manager с EventBus publishing.
EOF
```

---

## 📚 Обновление документации

### 1. Создать новый документ
**Файл**: `/doc-project/INFRASTRUCTURE_STATE_INTEGRATION.md`
**Содержание**:
- Архитектура интеграции
- EventBus events schema
- API endpoints
- Примеры использования

### 2. Обновить каталог
**Файл**: `/infrastructure/AI-office-infrastructure/ai-event-manager/README.md`
**Добавить**:
- Infrastructure State Monitoring (NEW!)
- Events: platform.infrastructure.*
- Endpoints: /infrastructure/*

### 3. Обновить balancer-service
**Файл**: `/infrastructure/balancer-service/README.md`
**Добавить**:
- Integration with Infrastructure State
- New EventBus subscriptions

### 4. Обновить главный каталог
**Файл**: `/doc/INDEX.md` или создать `/doc-project/SERVICES_CATALOG_2025-10-10.md`
**Отметить**:
- ❌ central-brain (deprecated → migrated to ai-event-manager)
- ✅ ai-event-manager (UPDATED: + Infrastructure State)
- ✅ balancer-service (UPDATED: + Infrastructure awareness)

---

## 🔧 Технические детали

### EventBus Events (NEW)

```typescript
// platform.infrastructure.state_updated
{
  event: "platform.infrastructure.state_updated",
  data: {
    state: {
      timestamp: "2025-10-10T12:00:00",
      ports_available: 50,
      ports_used: 30,
      prometheus_available: true,
      grafana_available: true,
      postgres_available: true,
      redis_available: true,
      services_with_metrics: 18,
      services_with_db: 20,
      total_services: 24,
      monitoring_coverage: 0.75,
      database_coverage: 0.83
    },
    timestamp: "2025-10-10T12:00:00"
  },
  priority: "normal"
}

// platform.infrastructure.emergency
{
  event: "platform.infrastructure.emergency",
  data: {
    type: "database_unavailable" | "monitoring_down" | "resource_exhausted",
    severity: "critical" | "high" | "medium",
    state: { ... },
    message: "PostgreSQL недоступен"
  },
  priority: "high"
}

// platform.infrastructure.strategy_recommended
{
  event: "platform.infrastructure.strategy_recommended",
  data: {
    strategy: "emergency" | "monitoring_recovery" | "improve_monitoring" | "maintain",
    priority: "critical" | "high" | "medium" | "low",
    action: "Восстановить критичные БД немедленно",
    reason: "Критичные базы данных недоступны"
  },
  priority: "normal"
}
```

### API Endpoints (NEW)

```http
GET /infrastructure/state
Response: { status: "success", state: { ... } }

GET /infrastructure/resources
Response: {
  status: "success",
  resources: {
    available: true,
    monitoring_coverage: 0.75,
    database_coverage: 0.83,
    system_healthy: true
  }
}

GET /infrastructure/strategy
Response: {
  status: "success",
  strategy: {
    strategy: "maintain",
    priority: "low",
    action: "Поддерживать текущее состояние",
    reason: "Система работает в штатном режиме"
  }
}

POST /infrastructure/deployment-check
Body: { service_name: "new-service", requires_db: true, requires_metrics: true }
Response: { can_deploy: true, reason: "Все необходимые ресурсы доступны" }
```

---

## ✅ Checklist

### Phase 1: ai-event-manager
- [ ] Создать `monitoring/__init__.py`
- [ ] Создать `monitoring/infrastructure_state.py`
- [ ] Перенести `InfrastructureState` dataclass
- [ ] Перенести `InfrastructureStateMonitor` class
- [ ] Добавить EventBus publishing в `update_state()`
- [ ] Добавить EventBus publishing в `suggest_strategy()`
- [ ] Добавить emergency event publishing
- [ ] Обновить `IntegrationManager` в `integrations/__init__.py`
- [ ] Добавить 4 API endpoints в `main.py`
- [ ] Тесты

### Phase 2: balancer-service
- [ ] Добавить 3 новые подписки EventBus
- [ ] Создать `_handle_infrastructure_state()`
- [ ] Создать `_handle_infrastructure_emergency()`
- [ ] Создать `_handle_strategy_recommendation()`
- [ ] Использовать `self.infrastructure_state` в балансировке
- [ ] Тесты

### Phase 3: Cleanup & Docs
- [ ] Архивировать `/infrastructure/central-brain/`
- [ ] Создать README в архиве
- [ ] Обновить `/infrastructure/AI-office-infrastructure/ai-event-manager/README.md`
- [ ] Обновить `/infrastructure/balancer-service/README.md`
- [ ] Создать `/doc-project/INFRASTRUCTURE_STATE_INTEGRATION.md`
- [ ] Обновить главный каталог сервисов
- [ ] Проверить что всё работает

---

## 🚨 Важные замечания

1. **Project Manager Client**:
   - central-brain импортирует напрямую из `infrastructure/tools/project-manager`
   - В ai-event-manager нужно создать client или использовать прямой импорт

2. **EventBus Priority**:
   - `platform.infrastructure.emergency` → priority="high"
   - `platform.infrastructure.state_updated` → priority="normal"
   - `platform.infrastructure.strategy_recommended` → priority="normal"

3. **Monitoring Interval**:
   - Default: 60 seconds
   - Configurable через IntegrationManager config

4. **Backward Compatibility**:
   - Старый central-brain будет в архиве
   - Можно восстановить если нужно
   - Но рекомендуется использовать новую интеграцию

---

## 📊 Результат (ожидаемый)

### До:
```
central-brain (standalone)     balancer-service (isolated)
     │                               │
     ▼                               ▼
  (никуда)                       EventBus
                                     │
                                     ▼
                              intelligent-core
```

### После:
```
┌──────────────────────────────────────────────────────┐
│  ai-event-manager (Hub)                              │
│  ├── Event Intelligence ✅                           │
│  ├── Infrastructure State Monitor ✅ (NEW!)          │
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
│service ✅   │ │manager   │ │ator      │
└─────────────┘ └──────────┘ └──────────┘
```

---

## 🔄 Следующая сессия (при восстановлении контекста)

**Прочитать**:
1. Этот файл (`SESSION_STATE_INTEGRATION_CENTRAL_BRAIN.md`)
2. `/doc-project/INTEGRATION_PLAN_CENTRAL_BRAIN_BALANCER.md` (детальный план)
3. `/doc-project/CENTRAL_BRAIN_BALANCER_ANALYSIS.md` (первичный анализ)

**Действия**:
1. Проверить checklist выше
2. Продолжить с невыполненных пунктов
3. Обновить документацию
4. Протестировать интеграцию

**Команда для проверки статуса**:
```bash
ls -la /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager/monitoring/
ls -la /Users/MD/AI-Platform-ISO/infrastructure/central-brain/  # должно быть в архиве
```

---

**Сохранено**: 2025-10-10
**Автор**: Claude (Integration Session)
**Статус**: 🚀 Ready to implement
**Timeline**: 3-4 часа
