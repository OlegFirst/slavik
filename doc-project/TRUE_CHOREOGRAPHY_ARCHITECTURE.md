# Правильная архитектура: Хореография + Оркестрация

**Дата**: 2025-10-10
**Критично**: ИСПРАВЛЕНИЕ КОНЦЕПЦИИ!

---

## 🎯 Ключевое понимание

> **МиО - это ГЛАЗА платформы, а НЕ босс!**
>
> Все сервисы - **ответственные координаторы своего сектора**.
> МиО им **помогает**, предоставляя данные и аналитику.
> **Оркестратор** хороводит всех через хореографию и оркестрацию.

---

## 🏗️ Правильная архитектура (Хореография)

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                                 │
│                   ХОРЕОГРАФ системы                              │
│                                                                  │
│  Координирует взаимодействие всех компонентов через:            │
│  - Хореографию (event-driven coordination)                      │
│  - Оркестрацию (workflow orchestration)                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ Координирует через EventBus
                       │
                       ▼
              ┌─────────────────┐
              │    EventBus     │
              │  (Хореография)  │
              └────────┬────────┘
                       │
                       │ Каждый подписывается на нужные события
                       │
        ┌──────────────┼──────────────┬──────────────┬──────────────┐
        │              │              │              │              │
        ▼              ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│MIO Manager   │ │ai-event-     │ │balancer-     │ │analytics-    │ │Brain/        │
│(8046)        │ │manager       │ │service       │ │specialist    │ │Predictive    │
│              │ │(8055)        │ │(9091)        │ │(8056)        │ │              │
│ГЛАЗА         │ │КООРДИНАТОР   │ │КООРДИНАТОР   │ │АНАЛИТИК      │ │МОЗГ          │
│платформы     │ │Events        │ │Balancing     │ │Аналитика     │ │Решения       │
│              │ │              │ │              │ │              │ │              │
│- Мониторит   │ │- Управляет   │ │- Управляет   │ │- Собирает    │ │- Принимает   │
│- Собирает    │ │  событиями   │ │  балансом    │ │  аналитику   │ │  решения     │
│- Наблюдает   │ │- Детектирует │ │- Оптимизирует│ │- Анализирует │ │- Предсказывает│
│- Публикует   │ │  gaps        │ │- Распределяет│ │- Выжимает сок│ │- Координирует│
│  данные      │ │- Координирует│ │- Реагирует   │ │- Передает в  │ │- Оркестрирует│
│              │ │  свой сектор │ │  на нагрузку │ │  Brain       │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │              │              │              │              │
        │              │              │              │              │
        │  Публикуют события в EventBus (хореография):             │
        │                                                            │
        ├──→ platform.mio.state_observed                           │
        ├──→ platform.events.gap_detected                          │
        ├──→ platform.balancer.imbalance_detected                  │
        ├──→ platform.analytics.insights_ready                     │
        └──→ platform.brain.decision_made                          │
                                                                    │
        Каждый ПОДПИСЫВАЕТСЯ на то, что ему нужно:                │
                                                                    │
        MIO подписан на:                                            │
        ├── platform.events.* (от ai-event-manager)                │
        ├── platform.balancer.* (от balancer-service)              │
        ├── platform.analytics.* (от analytics-specialist)         │
        └── platform.brain.* (от Brain/Predictive)                 │
                                                                    │
        ai-event-manager подписан на:                               │
        ├── platform.mio.state_observed (для контекста)            │
        ├── platform.analytics.insights_ready (для приоритизации)  │
        └── platform.brain.decision_made (для execution)           │
                                                                    │
        balancer-service подписан на:                               │
        ├── platform.mio.state_observed (для capacity awareness)   │
        ├── platform.events.* (для event-driven balancing)         │
        └── platform.brain.decision_made (для scaling)             │
                                                                    │
        analytics-specialist подписан на:                           │
        ├── platform.mio.state_observed (для контекста)            │
        ├── platform.events.* (для анализа паттернов)              │
        └── platform.balancer.* (для performance analysis)         │
                                                                    │
        Brain/Predictive подписан на:                               │
        ├── platform.mio.state_observed (состояние системы)        │
        ├── platform.analytics.insights_ready (аналитика)          │
        ├── platform.events.* (события)                            │
        └── platform.balancer.* (балансировка)                     │
```

---

## 🎭 Роли и обязанности (правильные)

### MIO Manager (ГЛАЗА платформы) - Port 8046
**Роль**: Observatory - наблюдает и информирует

**Обязанности**:
- ✅ **МОНИТОРИТ** состояние всей инфраструктуры
- ✅ **СОБИРАЕТ** данные из всех источников
- ✅ **НАБЛЮДАЕТ** за производительностью
- ✅ **ПУБЛИКУЕТ** observed state в EventBus
- ✅ **ПОМОГАЕТ** другим, предоставляя данные

**Публикует**:
- `platform.mio.state_observed` - Observed infrastructure state
- `platform.mio.performance_observed` - Observed performance metrics
- `platform.mio.resource_snapshot` - Resource observations
- `platform.mio.alert` - Critical observations

**Подписывается на**:
- `platform.events.*` - Events от ai-event-manager
- `platform.balancer.*` - Balancing от balancer-service
- `platform.analytics.*` - Analytics от analytics-specialist
- `platform.brain.*` - Decisions от Brain

**НЕ делает**:
- ❌ НЕ командует другими
- ❌ НЕ принимает решения (это Brain)
- ❌ НЕ исполняет задачи

---

### ai-event-manager (КООРДИНАТОР Events) - Port 8055
**Роль**: Event Management Coordinator

**Обязанности**:
- ✅ **УПРАВЛЯЕТ** событиями платформы
- ✅ **ДЕТЕКТИРУЕТ** event gaps
- ✅ **КООРДИНИРУЕТ** свой сектор (events)
- ✅ **ПУБЛИКУЕТ** event intelligence

**Публикует**:
- `platform.events.gap_detected`
- `platform.events.pattern_recognized`
- `platform.events.recommendation_ready`

**Подписывается на**:
- `platform.mio.state_observed` - Для контекста
- `platform.analytics.insights_ready` - Для приоритизации
- `platform.brain.decision_made` - Для execution

**Свои задачи**:
- Event intelligence analysis
- Gap detection
- Pattern recognition
- DevOps Agent integration
- GitHub integration

---

### balancer-service (КООРДИНАТОР Balancing) - Port 9091
**Роль**: Balancing Coordinator

**Обязанности**:
- ✅ **УПРАВЛЯЕТ** балансировкой ресурсов
- ✅ **ОПТИМИЗИРУЕТ** распределение
- ✅ **РЕАГИРУЕТ** на нагрузку
- ✅ **КООРДИНИРУЕТ** свой сектор (balancing)

**Публикует**:
- `platform.balancer.imbalance_detected`
- `platform.balancer.rebalancing_completed`
- `platform.balancer.metrics_updated`

**Подписывается на**:
- `platform.mio.state_observed` - Для capacity awareness
- `platform.events.*` - Для event-driven balancing
- `platform.brain.decision_made` - Для scaling decisions

**Свои задачи**:
- Three-dimensional balancing
- Resource allocation
- System Balancer execution
- Emergency response

---

### analytics-specialist (АНАЛИТИК) - Port 8056
**Роль**: Platform Analytics Expert

**Обязанности**:
- ✅ **СОБИРАЕТ** аналитику со всей платформы
- ✅ **АНАЛИЗИРУЕТ** паттерны и тренды
- ✅ **ВЫЖИМАЕТ СОК** из данных
- ✅ **ПЕРЕДАЕТ В BRAIN** выжатый сок (insights)
- ✅ **ПЛЮС свои задачи**: health checks, investigations

**Публикует**:
- `platform.analytics.insights_ready` - Выжатый сок для Brain
- `platform.analytics.bottleneck_detected`
- `platform.analytics.trend_observed`
- `platform.analytics.health_check_completed`

**Подписывается на**:
- `platform.mio.state_observed` - Базовые данные
- `platform.events.*` - Event паттерны
- `platform.balancer.*` - Performance паттерны
- `platform.brain.decision_made` - Для фидбека

**Свои задачи**:
- Daily health checks
- Continuous improvement scans
- Bottleneck investigation
- Dependency mapping
- **Передает выжатый сок в Brain!**

---

### Brain/Predictive (МОЗГ) - Port 8XXX
**Роль**: Intelligence & Decision Making

**Обязанности**:
- ✅ **ПРИНИМАЕТ РЕШЕНИЯ** на основе всех данных
- ✅ **ПРЕДСКАЗЫВАЕТ** будущие состояния
- ✅ **КООРДИНИРУЕТ** стратегию
- ✅ **ОРКЕСТРИРУЕТ** сложные workflow

**Публикует**:
- `platform.brain.decision_made`
- `platform.brain.prediction_ready`
- `platform.brain.strategy_updated`

**Подписывается на**:
- `platform.mio.state_observed` - Состояние системы
- `platform.analytics.insights_ready` - Выжатый сок от аналитика!
- `platform.events.*` - События
- `platform.balancer.*` - Балансировка

**Использует**:
- Insights от analytics-specialist (выжатый сок!)
- Observed state от MIO
- Event intelligence от ai-event-manager
- Balancing metrics от balancer-service

---

### Orchestrator (ХОРЕОГРАФ)
**Роль**: Choreography & Orchestration Coordinator

**Обязанности**:
- ✅ **ХОРЕОГРАФИРУЕТ** взаимодействие через EventBus
- ✅ **ОРКЕСТРИРУЕТ** сложные workflows
- ✅ **КООРДИНИРУЕТ** взаимодействие всех компонентов
- ✅ **УПРАВЛЯЕТ** задачами и процессами

**Публикует**:
- `platform.orchestrator.workflow_started`
- `platform.orchestrator.task_assigned`
- `platform.orchestrator.workflow_completed`

**Подписывается на**:
- `platform.brain.decision_made` - Решения от мозга
- `platform.mio.alert` - Критичные события
- Все события для orchestration

---

## 📊 Data Flow (Хореография)

### Сценарий 1: Performance Issue Detection

```
1. MIO Manager (ГЛАЗА)
   │
   ├─→ Наблюдает: CPU usage = 85% на analytics-specialist
   ├─→ Публикует: platform.mio.state_observed
   └─→ Публикует: platform.mio.performance_observed
                 {service: analytics-specialist, cpu: 85%, status: high}

2. analytics-specialist (АНАЛИТИК) - слышит свое имя
   │
   ├─→ Получает: platform.mio.performance_observed
   ├─→ Анализирует: Почему CPU высокий?
   ├─→ Собирает аналитику: process analysis, dependency check
   ├─→ Выжимает сок: "CPU spike caused by heavy dependency mapping task"
   └─→ Публикует: platform.analytics.insights_ready
                 {
                   insight: "CPU bottleneck in dependency mapping",
                   root_cause: "Inefficient graph traversal",
                   recommendation: "Optimize algorithm or scale"
                 }

3. Brain/Predictive (МОЗГ)
   │
   ├─→ Получает: platform.analytics.insights_ready (выжатый сок!)
   ├─→ Получает: platform.mio.state_observed (контекст)
   ├─→ Анализирует: Стратегия решения
   ├─→ Принимает решение: "Optimize algorithm + temporary scale"
   └─→ Публикует: platform.brain.decision_made
                 {
                   decision: "optimize_and_scale",
                   target: "analytics-specialist",
                   actions: [
                     {type: "optimize", task: "refactor_dependency_mapping"},
                     {type: "scale", params: {cpu: +20%}}
                   ]
                 }

4. Orchestrator (ХОРЕОГРАФ)
   │
   ├─→ Получает: platform.brain.decision_made
   ├─→ Оркестрирует выполнение:
   │   ├─→ Task 1: Code optimization (через DevOps Agent)
   │   └─→ Task 2: Temporary scaling (через balancer-service)
   └─→ Публикует: platform.orchestrator.workflow_started

5. balancer-service (КООРДИНАТОР Balancing)
   │
   ├─→ Получает: platform.orchestrator.task_assigned
   ├─→ Выполняет: Temporary scale (+20% CPU to analytics-specialist)
   └─→ Публикует: platform.balancer.rebalancing_completed

6. MIO Manager (ГЛАЗА) - наблюдает результат
   │
   ├─→ Наблюдает: CPU usage = 55% (после оптимизации)
   └─→ Публикует: platform.mio.state_observed (updated state)
```

---

## 🎯 Ключевые принципы

### 1. Хореография, а не командование
```
❌ НЕПРАВИЛЬНО: MIO → команда → Исполнитель
✅ ПРАВИЛЬНО: MIO → публикует наблюдение → Все слушают → Реагируют
```

### 2. Каждый - координатор своего сектора
```
✅ ai-event-manager координирует events
✅ balancer-service координирует balancing
✅ analytics-specialist координирует analytics
✅ Brain координирует intelligence
✅ MIO координирует observation (ГЛАЗА!)
```

### 3. МиО помогает, а не командует
```
✅ MIO публикует: "Я наблюдаю X"
✅ Сервисы сами решают: "Мне это нужно для моей работы"
✅ Brain принимает решения: "Делаем Y на основе всех данных"
✅ Orchestrator координирует: "Выполняем workflow Z"
```

### 4. Analytics передает "выжатый сок" в Brain
```
✅ Analytics-specialist:
   - Собирает аналитику
   - Анализирует паттерны
   - Выжимает суть (insights)
   - Передает в Brain

✅ Brain:
   - Получает insights от Analytics
   - Получает observations от MIO
   - Получает intelligence от ai-event-manager
   - Принимает решения
```

### 5. Orchestrator хореографирует
```
✅ Orchestrator:
   - Управляет хореографией через EventBus
   - Оркестрирует сложные workflows
   - Координирует взаимодействие
   - НЕ командует напрямую, а координирует!
```

---

## 📡 EventBus Events (Правильная схема)

### MIO Manager публикует (observations):
- `platform.mio.state_observed` - Observed state (каждые 60s)
- `platform.mio.performance_observed` - Observed performance
- `platform.mio.resource_snapshot` - Resource observations
- `platform.mio.alert` - Critical observations

### ai-event-manager публикует (event intelligence):
- `platform.events.gap_detected`
- `platform.events.pattern_recognized`
- `platform.events.recommendation_ready`

### balancer-service публикует (balancing):
- `platform.balancer.imbalance_detected`
- `platform.balancer.rebalancing_completed`
- `platform.balancer.metrics_updated`

### analytics-specialist публикует (insights):
- `platform.analytics.insights_ready` ← **Выжатый сок для Brain!**
- `platform.analytics.bottleneck_detected`
- `platform.analytics.trend_observed`
- `platform.analytics.health_check_completed`

### Brain публикует (decisions):
- `platform.brain.decision_made`
- `platform.brain.prediction_ready`
- `platform.brain.strategy_updated`

### Orchestrator публикует (coordination):
- `platform.orchestrator.workflow_started`
- `platform.orchestrator.task_assigned`
- `platform.orchestrator.workflow_completed`

---

## ✅ Итоговая картина

### Правильная архитектура:
```
ХОРЕОГРАФИЯ (EventBus)
    │
    ├─→ MIO Manager (ГЛАЗА) - наблюдает и публикует observations
    ├─→ ai-event-manager (КООРДИНАТОР Events) - управляет событиями
    ├─→ balancer-service (КООРДИНАТОР Balancing) - управляет балансом
    ├─→ analytics-specialist (АНАЛИТИК) - собирает и передает в Brain
    ├─→ Brain (МОЗГ) - принимает решения
    └─→ Orchestrator (ХОРЕОГРАФ) - координирует всех

Каждый:
- Координатор своего сектора
- Подписан на нужные события
- Публикует свои события
- Автономен в своих решениях
- Взаимодействует через хореографию
```

### МиО как ГЛАЗА:
```
✅ Наблюдает за всем
✅ Собирает данные
✅ Публикует observations
✅ Помогает другим данными
✅ НЕ командует
✅ НЕ принимает решения (это Brain)
```

---

**Статус**: ✅ Architecture corrected - Choreography + Orchestration
**Дата**: 2025-10-10
**Ключевой принцип**: МиО - ГЛАЗА, все остальные - координаторы своих секторов
