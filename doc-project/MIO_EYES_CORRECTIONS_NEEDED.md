# МиО Manager - Исправления для роли ГЛАЗА (EYES)

## Текущая ситуация

### ✅ Что уже есть и работает правильно:

1. **Infrastructure State Monitor** (`monitoring/infrastructure_state.py`)
   - Собирает состояние инфраструктуры
   - Уже есть! (421 строк)

2. **Performance Evaluator** (`monitoring/performance_evaluator.py`)
   - Оценивает производительность сервисов
   - Уже есть! (421 строк)

3. **SmartScheduler** (`scheduler/smart_scheduler.py`)
   - Управляет всеми циклами анализа
   - Огромный файл (1442 строки!)
   - Уже делает многое из того что нужно

4. **Automation Toolkit** (`integrations/automation_toolkit.py`)
   - Автоматизация discovery и setup

5. **Все интеграционные клиенты**
   - EventBus, Brain, Predictive, Optimizer, etc.
   - Уже созданы!

### ❌ Что НЕ РАБОТАЕТ (критичные проблемы):

#### Проблема 1: Prometheus регистрация - РУЧНАЯ
- `/infrastructure/observability/config/prometheus/prometheus.yml` - все hardcoded
- 40+ сервисов прописаны вручную
- Нет автоматической регистрации новых сервисов
- Нет проверки coverage (кто зарегистрирован, кто нет)

#### Проблема 2: МиО НЕ наблюдает за метриками coverage
- МиО не проверяет: все ли сервисы мониторятся?
- МиО не проверяет: отчитываются ли сервисы?
- МиО не публикует observations о coverage в EventBus

#### Проблема 3: Неправильная хореография в EventBus
Сейчас МиО местами КОМАНДУЕТ вместо того чтобы НАБЛЮДАТЬ:
- `brain.escalate_problem()` - МиО командует мозгу что делать ❌
- `brain.send_alert()` - МиО командует мозгу ❌
- `brain.publish_report()` - Это OK, но должно быть через EventBus ⚠️

**Правильная хореография:**
```
МиО (ГЛАЗА) → наблюдает и публикует observations в EventBus
EventBus → доставляет observations всем подписчикам
Brain (МОЗГ) → подписывается на observations, анализирует, ПРИНИМАЕТ РЕШЕНИЯ
ai-event-manager → подписывается на observations, координирует events
DevOps Agent → подписывается на observations, может автоматически исправлять
```

## 🎯 Что нужно исправить

### 1. Добавить Metrics Coverage Observer в МиО

**Файл**: `/mio-manager/monitoring/metrics_coverage_observer.py` (УЖЕ СОЗДАН!)

**Задача:**
- Наблюдает Service Discovery vs Prometheus targets
- Публикует: `platform.mio.metrics_coverage_observed`
- Публикует: `platform.mio.metrics_coverage_issue_observed` (если < 90%)

**Интеграция в SmartScheduler:**
```python
# Добавить новый цикл в SmartScheduler
async def _observe_metrics_coverage(self):
    """Наблюдение за metrics coverage (каждые 5 минут)"""
    observation = await self.metrics_coverage_observer.observe_coverage()
    await self.metrics_coverage_observer.publish_observation(observation)
```

### 2. Добавить Metrics Health Checker в МиО

**Файл**: `/mio-manager/monitoring/metrics_health_checker.py` (НУЖНО СОЗДАТЬ)

**Задача:**
- Проверяет доступность metrics endpoints
- Проверяет актуальность метрик (last scrape time)
- Проверяет scrape errors
- Публикует: `platform.mio.metrics_health_observed`

**Интеграция в SmartScheduler:**
```python
# Добавить новый цикл
async def _check_metrics_health(self):
    """Проверка health метрик (каждую минуту)"""
    health = await self.metrics_health_checker.check_all_endpoints()
    await self.metrics_health_checker.publish_health_observation(health)
```

### 3. Добавить Metrics Registration Automator

**Файл**: `/mio-manager/automation/metrics_registration_automator.py` (НУЖНО СОЗДАТЬ)

**Задача:**
- Слушает `platform.service.registered` от Service Discovery
- Автоматически создает Prometheus job config (file-based SD)
- Обновляет `/etc/prometheus/sd_configs/services.json`
- Публикует: `platform.mio.service_monitoring_enabled`

**Хореография:**
```
Service Discovery → публикует: platform.service.registered
МиО Automator → слушает event, автоматически добавляет в Prometheus SD
МиО Automator → публикует: platform.mio.service_monitoring_enabled
```

### 4. Исправить EventBus хореографию в SmartScheduler

**Что менять:**

#### ❌ СЕЙЧАС (неправильно - МиО командует):
```python
# SmartScheduler._escalate_critical_failure()
await self.brain.escalate_problem(...)  # МиО командует мозгу

# SmartScheduler._hourly_devops_monitoring()
await self.brain.send_alert(...)  # МиО командует мозгу
```

#### ✅ ДОЛЖНО БЫТЬ (правильно - МиО наблюдает и публикует):
```python
# SmartScheduler._escalate_critical_failure()
await self.eventbus.publish(
    'platform.mio.critical_failure_observed',
    {
        'services': critical_failures,
        'severity': 'critical',
        'observation': 'Multiple critical services are down',
        'recommendation': 'Immediate investigation required'
    },
    priority='critical'
)
# Brain подписан на этот event и САМ ПРИМЕТ РЕШЕНИЕ что делать

# SmartScheduler._hourly_devops_monitoring()
await self.eventbus.publish(
    'platform.mio.event_gaps_observed',
    {
        'total_gaps': total_gaps,
        'critical_gaps': critical_gaps,
        'observation': 'Critical event architecture gaps detected',
        'recommendation': 'Review event architecture'
    },
    priority='high'
)
# Brain/DevOps Agent подписаны и САМ решают что делать
```

### 5. Обновить main.py МиО Manager

**Добавить новые компоненты:**
```python
# Global instances
metrics_coverage_observer = None
metrics_health_checker = None
metrics_registration_automator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global metrics_coverage_observer, metrics_health_checker, metrics_registration_automator

    # Initialize Metrics Coverage Observer
    metrics_coverage_observer = MetricsCoverageObserver(
        eventbus=eventbus_client,
        service_discovery_url=settings.SERVICE_DISCOVERY_URL,
        prometheus_url=settings.PROMETHEUS_URL
    )
    logger.info("   👀 Metrics Coverage Observer initialized")

    # Initialize Metrics Health Checker
    metrics_health_checker = MetricsHealthChecker(
        eventbus=eventbus_client,
        prometheus_url=settings.PROMETHEUS_URL
    )
    logger.info("   👀 Metrics Health Checker initialized")

    # Initialize Metrics Registration Automator
    metrics_registration_automator = MetricsRegistrationAutomator(
        eventbus=eventbus_client,
        prometheus_sd_file='/etc/prometheus/sd_configs/services.json'
    )
    await metrics_registration_automator.start()
    logger.info("   🔧 Metrics Registration Automator started")

    # Pass to SmartScheduler
    smart_scheduler = SmartScheduler(
        ...,
        metrics_coverage_observer=metrics_coverage_observer,
        metrics_health_checker=metrics_health_checker
    )
```

## 📋 План действий (приоритет)

### PHASE 1: Наблюдение (1-2 дня) ← СНАЧАЛА!

1. ✅ **Metrics Coverage Observer** - УЖЕ СОЗДАН!
   - Уже создан: `/mio-manager/monitoring/metrics_coverage_observer.py`
   - Нужно: Интегрировать в SmartScheduler

2. ⏳ **Metrics Health Checker** - СОЗДАТЬ
   - Создать: `/mio-manager/monitoring/metrics_health_checker.py`
   - Интегрировать в SmartScheduler

3. ⏳ **Добавить циклы в SmartScheduler**
   - Metrics Coverage Cycle (каждые 5 минут)
   - Metrics Health Cycle (каждую минуту)

4. ⏳ **Обновить main.py**
   - Инициализировать новые компоненты
   - Передать в SmartScheduler

### PHASE 2: Исправить хореографию (1 день)

5. ⏳ **Исправить EventBus events в SmartScheduler**
   - Заменить `brain.escalate_problem()` на `eventbus.publish('platform.mio.critical_failure_observed')`
   - Заменить `brain.send_alert()` на `eventbus.publish('platform.mio.*_observed')`
   - Заменить `brain.publish_report()` на `eventbus.publish('platform.mio.report_ready')`

6. ⏳ **Обновить ai-event-manager**
   - Подписаться на `platform.mio.*_observed` events
   - Координировать responses

7. ⏳ **Обновить analytics-specialist**
   - Подписаться на `platform.mio.*_observed`
   - Собирать аналитику
   - Передавать insights в Brain через `platform.analytics.insights_ready`

### PHASE 3: Автоматизация регистрации (2 дня)

8. ⏳ **Metrics Registration Automator** - СОЗДАТЬ
   - Создать: `/mio-manager/automation/metrics_registration_automator.py`
   - Слушает `platform.service.registered`
   - Автоматически обновляет Prometheus SD JSON

9. ⏳ **Обновить Service Discovery**
   - Публиковать `platform.service.registered` при регистрации
   - Интеграция с EventBus

10. ⏳ **Мигрировать Prometheus на file-based SD**
    - Изменить `prometheus.yml`
    - Создать `/etc/prometheus/sd_configs/services.json`
    - Мигрировать существующие 40+ сервисов

## 🎯 Правильная архитектура (после исправлений)

### МиО Manager = ГЛАЗА (Observatory)

```
МиО Manager (ГЛАЗА)
│
├── 1. Infrastructure State Monitor (уже есть!)
│   └─ Публикует: platform.mio.state_observed
│
├── 2. Performance Evaluator (уже есть!)
│   └─ Публикует: platform.mio.performance_observed
│
├── 3. Metrics Coverage Observer (УЖЕ СОЗДАН!)
│   ├─ Наблюдает: Service Discovery vs Prometheus
│   └─ Публикует: platform.mio.metrics_coverage_observed
│
├── 4. Metrics Health Checker (НУЖНО СОЗДАТЬ)
│   ├─ Проверяет: доступность endpoints, scrape errors
│   └─ Публикует: platform.mio.metrics_health_observed
│
├── 5. Metrics Registration Automator (НУЖНО СОЗДАТЬ)
│   ├─ Слушает: platform.service.registered
│   ├─ Автоматизирует: регистрацию в Prometheus
│   └─ Публикует: platform.mio.service_monitoring_enabled
│
├── 6. SmartScheduler (уже есть!)
│   ├─ Управляет всеми observation cycles
│   ├─ ИСПРАВИТЬ: EventBus хореографию
│   └─ Публикует observations (НЕ командует!)
│
└── 7. EventBus Integration
    └─ ВСЕ публикации через EventBus!
        НЕ прямые вызовы brain.escalate_problem() и т.д.
```

### Хореография после исправлений:

```
1. МиО (ГЛАЗА) → наблюдает систему
   └─ Публикует: platform.mio.*_observed (observations)

2. EventBus → доставляет observations всем подписчикам

3. Brain (МОЗГ) → подписан на platform.mio.*_observed
   ├─ Анализирует observations
   ├─ ПРИНИМАЕТ РЕШЕНИЯ
   └─ Публикует: platform.brain.decision_made

4. ai-event-manager → подписан на platform.mio.*_observed
   ├─ Координирует event responses
   └─ Может escalate critical issues

5. analytics-specialist → подписан на platform.mio.*_observed
   ├─ Собирает аналитику
   ├─ Анализирует trends
   └─ Публикует: platform.analytics.insights_ready → Brain

6. DevOps Agent → подписан на platform.mio.*_observed
   ├─ Может автоматически исправлять проблемы
   └─ Публикует: platform.devops.action_completed

7. balancer-service → подписан на platform.mio.performance_observed
   ├─ Реагирует на performance issues
   └─ Публикует: platform.balancer.rebalanced
```

## ✅ Успех после исправлений

После всех исправлений:

1. ✅ **МиО = ГЛАЗА** (наблюдает, НЕ командует)
2. ✅ **Brain = МОЗГ** (принимает решения)
3. ✅ **Хореография** (event-driven, autonomous services)
4. ✅ **Автоматическая регистрация** в Prometheus
5. ✅ **Постоянное наблюдение** за metrics coverage
6. ✅ **Autonomous coordinators** (каждый сервис координирует свой сектор)

---

## 🚀 Следующий шаг

**СНАЧАЛА**: Создать Metrics Health Checker, затем интегрировать оба observer'а в SmartScheduler и обновить main.py.

**ПОТОМ**: Исправить хореографию EventBus в SmartScheduler.

**В КОНЦЕ**: Автоматизация регистрации через Metrics Registration Automator.
