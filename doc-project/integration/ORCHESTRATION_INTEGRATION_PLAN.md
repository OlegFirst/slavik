# План Интеграции Оркестрации: Собираем Существующее
## Используем ЧТО ЕСТЬ + Дополняем Недостающее

**Date:** 2025-10-09
**Approach:** Integration, Not Reinvention
**Status:** Integration Ready

---

## ✅ ЧТО УЖЕ ЕСТЬ (Используем!)

### 1. **EventBus** (Infrastructure Level) - 100% ГОТОВ
**Location:** `/infrastructure/eventbus/`

**Что есть:**
- ✅ Clean interface (IEventBus)
- ✅ Redis Streams backend (production)
- ✅ Memory backend (testing)
- ✅ Event model (Event class)
- ✅ Wildcard subscriptions
- ✅ Consumer groups
- ✅ Retry logic
- ✅ Документация + примеры

**Паттерны:**
- Event Choreography
- Saga Pattern
- Event Sourcing
- Dead Letter Queue

**Что добавить:**
```python
# infrastructure/eventbus/coordination/
├── health_monitor.py         # Health Monitoring Cycle
├── auto_recovery.py          # Auto-Recovery для EventBus
└── resource_optimizer.py     # Resource Optimization
```

---

### 2. **AI Event Manager** (Infrastructure Level) - ГОТОВ
**Location:** `/infrastructure/AI-office-infrastructure/ai-event-manager/`

**Что есть:**
- ✅ FastAPI service (port 8055)
- ✅ REST API для управления событиями
- ✅ Integration с event_intelligence
- ✅ Recommendations endpoint
- ✅ Learning/feedback механизм
- ✅ Prometheus metrics

**Что добавить:**
- Auto-execution (с подтверждением)
- Webhook notifications
- Grafana dashboard integration

---

### 3. **event_intelligence** (Core Level) - БАЗОВАЯ РЕАЛИЗАЦИЯ
**Location:** `/intelligent-core/event_intelligence/`

**Что есть:**
- ✅ analyzer.py - Анализ событий
- ✅ learner.py - Обучение
- ✅ predictor.py - Предсказания
- ✅ knowledge_base.py - База знаний
- ✅ auto_discovery.py - Auto-discovery событий
- ✅ event_subscribers.py - Подписки (16 мест)
- ✅ code_healer.py - Автоматическое исправление

**Что добавить:**
```python
# intelligent-core/event_intelligence/coordination/
├── core_coordinator.py       # Координация RAG → ML → Learning
├── pattern_detector.py       # Pattern Detection Cycle
└── model_trainer.py          # Model Training Cycle
```

---

### 4. **Orchestration Docs** - УЖЕ ОПИСАНО!
**Location:** `/comprehensive-platform-docs/`

**Что есть:**
- ✅ `INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md` - Infrastructure паттерны
- ✅ `AI_ORCHESTRATION_CAPABILITIES.md` - AI Orchestrator (6-step cognitive loop)
- ✅ 570+ сценариев в comprehensive-platform-docs

**Архитектура AI Orchestrator:**
- 6-Step Cognitive Loop (Monitor → Understand → Decide → Act → Measure → Learn)
- 4-Layer Memory (Working → Short-term → Long-term → Procedural)
- 5 Action Types (AUTO_RESOLVE, DELEGATE, ESCALATE_HUMAN, WAIT_AND_MONITOR, EMERGENCY_STOP)

---

### 5. **intelligent-core/orchestration** - НУЖНО СОБРАТЬ
**Location:** `/intelligent-core/orchestration/`

**Что есть (снесено с разных версий):**
- ⚠️ `ai-orchestration/` - AI Orchestrator (из docs выше)
- ⚠️ `coordination-center/` - Coordination center
- ⚠️ `bcm-services-orchestrator/` - BCM services
- ⚠️ `task_queue/` - Task queue

**Статус:** Только начали собирать, затормозили

**Что нужно:**
1. Собрать в единую структуру
2. Интегрировать с EventBus
3. Подключить к event_intelligence
4. Добавить недостающие координаторы

---

### 6. **infrastructure/orchestrator** - СЫРОЙ, НО ГОТОВ
**Location:** `/infrastructure/AI-office-infrastructure/orchestrator/`

**Что есть:**
- ✅ `unified_orchestrator.py` - Unified Orchestrator (port 8090)
- ✅ Infrastructure Executor (deploy, restart, health)
- ✅ Event Executor (add publisher/subscriber, fix gaps)
- ✅ МиО Manager integration
- ⚠️ Code Executor (TODO)
- ⚠️ Database Executor (TODO)

**Роль:** Исполнитель для AI Office tasks (инфраструктурные задачи)

**Что добавить:**
- Интеграция с Program-level orchestration
- Code Executor implementation
- Database Executor implementation

---

## 🔄 АРХИТЕКТУРА ИНТЕГРАЦИИ (4 Уровня)

```
┌─────────────────────────────────────────────────────────────────┐
│  LEVEL 4: PROGRAM ORCHESTRATION                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  intelligent-core/orchestration/                                │
│  ├── program_coordinator.py       ✅ СОЗДАТЬ                    │
│  ├── workflow_orchestrator.py     ✅ СОЗДАТЬ (use Temporal)     │
│  ├── virtuous_cycle.py            ✅ СОЗДАТЬ                    │
│  └── ai-orchestration/            ⚠️ СОБРАТЬ (из docs)          │
│      ├── orchestrator.py          (6-step cognitive loop)       │
│      ├── context_aggregator.py                                  │
│      ├── priority_engine.py                                     │
│      ├── strategy_selector.py                                   │
│      └── safety_monitor.py                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↕️ EventBus
┌─────────────────────────────────────────────────────────────────┐
│  LEVEL 3: CENTER COORDINATION                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  intelligent-core/expertise-center/coordination/                │
│  ├── expert_coordinator.py        ✅ СОЗДАТЬ                    │
│  │   └── Координация 12 Tactical Assistants                    │
│                                                                  │
│  intelligent-core/collective/coordination/                      │
│  ├── collective_cycle.py          ✅ СОЗДАТЬ                    │
│  │   └── Collective Intelligence (k=5)                          │
│                                                                  │
│  intelligent-core/community_intelligence/coordination/          │
│  └── community_learning.py        ✅ СОЗДАТЬ                    │
│      └── Learning от users                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↕️ EventBus
┌─────────────────────────────────────────────────────────────────┐
│  LEVEL 2: CORE COORDINATION (Мозг)                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  intelligent-core/event_intelligence/coordination/              │
│  ├── core_coordinator.py          ✅ СОЗДАТЬ                    │
│  │   └── RAG → ML → Learning Pipeline                          │
│  ├── pattern_detector.py          ✅ СОЗДАТЬ                    │
│  │   └── Pattern Detection Cycle                               │
│  └── model_trainer.py             ✅ СОЗДАТЬ                    │
│      └── Model Training Cycle (24h)                             │
│                                                                  │
│  intelligent-core/ai-foundation/coordination/                   │
│  └── ai_coordinator.py            ✅ СОЗДАТЬ                    │
│      └── Координация RAG + ML + LLM                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                         ↕️ EventBus
┌─────────────────────────────────────────────────────────────────┐
│  LEVEL 1: INFRASTRUCTURE COORDINATION                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  infrastructure/eventbus/                  ✅ ГОТОВ             │
│  ├── Core EventBus (Redis Streams)                              │
│  ├── Choreography patterns                                      │
│  └── coordination/                         ✅ ДОБАВИТЬ          │
│      ├── health_monitor.py                                      │
│      ├── auto_recovery.py                                       │
│      └── resource_optimizer.py                                  │
│                                                                  │
│  infrastructure/AI-office-infrastructure/                       │
│  ├── ai-event-manager/                     ✅ ГОТОВ             │
│  │   └── FastAPI service (port 8055)                            │
│  └── orchestrator/                         ⚠️ СЫРОЙ            │
│      ├── unified_orchestrator.py           (для AI Office)      │
│      └── executors/                        (Infrastructure)     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 ПЛАН ИНТЕГРАЦИИ (4 Фазы)

### PHASE 1: Infrastructure Integration (1 неделя)

**Цель:** Завершить Infrastructure Level coordination

**Tasks:**

1. **Дополнить EventBus координацией**
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/eventbus
mkdir coordination

# Создать 3 файла:
touch coordination/health_monitor.py      # Health Monitoring Cycle (30sec)
touch coordination/auto_recovery.py       # Auto-Recovery механизмы
touch coordination/resource_optimizer.py  # Resource Optimization (5min)
```

2. **Интегрировать с ai-event-manager**
```python
# ai-event-manager уже готов, только добавить:
# - Auto-execution (с подтверждением)
# - Webhook notifications
# - Grafana dashboard
```

3. **Подключить orchestrator к EventBus**
```python
# infrastructure/orchestrator/unified_orchestrator.py
# Добавить EventBus integration для координации
```

**Success Criteria:**
- ✅ Health Monitoring Cycle работает (30 sec)
- ✅ Auto-Recovery срабатывает при сбоях
- ✅ Resource Optimizer оптимизирует (5 min)

---

### PHASE 2: Core Integration (1-2 недели)

**Цель:** Завершить Core Level coordination (мозг)

**Tasks:**

1. **Создать Core Coordinator**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/event_intelligence
mkdir coordination

touch coordination/core_coordinator.py    # RAG → ML → Learning Pipeline
touch coordination/pattern_detector.py    # Pattern Detection
touch coordination/model_trainer.py       # Model Training Cycle
```

2. **Интегрировать ai-foundation**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation
mkdir coordination

touch coordination/ai_coordinator.py      # RAG + ML + LLM координация
```

3. **Подключить к EventBus**
```python
# Все координаторы используют EventBus для choreography
# Подписываются на события и публикуют результаты
```

**Success Criteria:**
- ✅ RAG → ML → Learning Pipeline работает end-to-end
- ✅ Pattern Detector детектирует паттерны
- ✅ Model Trainer переобучает models каждые 24h

---

### PHASE 3: Center Integration (1-2 недели)

**Цель:** Координация экспертизы (expertise-center, collective, community)

**Tasks:**

1. **Expert Coordinator**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise-center
mkdir coordination

touch coordination/expert_coordinator.py  # Координация 12 Tactical Assistants
```

2. **Collective Intelligence Cycle**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/collective
mkdir coordination

touch coordination/collective_cycle.py    # k=5 anonymization + collective agents
```

3. **Community Learning**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/community_intelligence
mkdir coordination

touch coordination/community_learning.py  # Learning от users
```

**Success Criteria:**
- ✅ 12 Tactical Assistants работают вместе
- ✅ Collective Agents обновляются (7 days)
- ✅ Community learning loop работает

---

### PHASE 4: Program Integration (2-3 недели)

**Цель:** Program-level orchestration + Virtuous Cycle

**Tasks:**

1. **Собрать intelligent-core/orchestration**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration

# Собрать из разных версий:
# 1. ai-orchestration/ (6-step cognitive loop из docs)
# 2. Интегрировать с EventBus
# 3. Подключить к Temporal workflows
```

2. **Program Coordinator**
```python
# intelligent-core/orchestration/program_coordinator.py
# End-to-end workflow orchestration
# Использует Temporal + EventBus
```

3. **Virtuous Cycle**
```python
# intelligent-core/orchestration/virtuous_cycle.py
# 3 user groups → learning → materials → code improvements
```

**Success Criteria:**
- ✅ End-to-end BIA journey работает
- ✅ Virtuous Cycle генерирует материалы (7 days)
- ✅ 3 user groups получают value

---

## 🔧 КОНКРЕТНЫЕ ЗАДАЧИ

### Task 1: EventBus Health Monitoring (Priority 1)

**File:** `infrastructure/eventbus/coordination/health_monitor.py`

```python
"""
EventBus Health Monitoring Cycle

Запускается каждые 30 секунд, проверяет:
- Redis connection
- Consumer groups health
- Event processing rate
- Dead letter queue size
"""

import asyncio
from datetime import datetime
from infrastructure.eventbus import create_eventbus_from_env, Event

class EventBusHealthMonitor:
    def __init__(self):
        self.bus = create_eventbus_from_env()

    async def run_health_cycle(self):
        """Постоянный цикл health monitoring"""
        while True:
            # Check Redis
            redis_health = await self.check_redis()

            # Check consumer groups
            groups_health = await self.check_consumer_groups()

            # Check event rate
            event_rate = await self.get_event_processing_rate()

            # Publish health status
            await self.bus.publish(Event.create(
                event_type="infrastructure.eventbus.health_checked",
                data={
                    "redis": redis_health,
                    "consumer_groups": groups_health,
                    "event_rate": event_rate,
                    "timestamp": datetime.now().isoformat()
                },
                source="eventbus-health-monitor",
                tenant_id="system"
            ))

            # Wait 30 seconds
            await asyncio.sleep(30)

    async def check_redis(self):
        """Check Redis connection"""
        try:
            # Redis ping
            stats = await self.bus.get_stats()
            return {"status": "healthy", "stats": stats}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def check_consumer_groups(self):
        """Check all consumer groups"""
        # Implementation
        pass

    async def get_event_processing_rate(self):
        """Get events/second"""
        # Implementation
        pass
```

---

### Task 2: Core Coordinator (Priority 2)

**File:** `intelligent-core/event_intelligence/coordination/core_coordinator.py`

```python
"""
Core Coordinator: RAG → ML → Learning Pipeline

Координирует:
1. RAG Pipeline (ai-foundation/rag)
2. ML Models (ai-foundation/ml)
3. Learning (ai-foundation/learning)
4. Event Intelligence (event_intelligence)
"""

from infrastructure.eventbus import create_eventbus_from_env, Event

class CoreCoordinator:
    def __init__(self):
        self.bus = create_eventbus_from_env()

    async def setup_subscriptions(self):
        """Setup event subscriptions"""

        # When user gives feedback → trigger learning
        await self.bus.subscribe(
            "core.user.feedback_received",
            self.handle_feedback
        )

        # When new data collected → trigger training
        await self.bus.subscribe(
            "core.data.collected",
            self.handle_new_data
        )

    async def handle_feedback(self, event: Event):
        """Handle user feedback on AI responses"""

        feedback = event.data

        # If bad feedback → analyze why
        if feedback["rating"] < 3:
            # Analyze RAG failure
            await self.analyze_rag_failure(feedback)

            # Update ML model
            await self.update_ml_model(feedback)

        # Publish learning event
        await self.bus.publish(Event.create(
            event_type="core.learning.completed",
            data={"feedback_id": feedback["id"]},
            source="core-coordinator",
            tenant_id=event.tenant_id
        ))

    async def analyze_rag_failure(self, feedback):
        """Analyze why RAG retrieval failed"""
        # Implementation with ai-foundation/rag
        pass

    async def update_ml_model(self, feedback):
        """Update ML model with feedback"""
        # Implementation with ai-foundation/ml
        pass
```

---

### Task 3: AI Orchestrator Integration (Priority 3)

**File:** `intelligent-core/orchestration/ai-orchestration/orchestrator.py`

**Используем из comprehensive-platform-docs:**
- 6-Step Cognitive Loop (уже описано)
- Context Aggregator (уже описан)
- Priority Engine (уже описан)
- Strategy Selector (уже описан)
- Safety Monitor (уже описан)

**Что добавить:**
- EventBus integration
- Интеграция с Temporal workflows
- Подключение к expertise-center

```python
"""
AI Orchestrator - 6-Step Cognitive Loop

Based on: /comprehensive-platform-docs/AI_ORCHESTRATION_CAPABILITIES.md

Steps:
1. MONITOR - Context Aggregation
2. UNDERSTAND - Priority Assessment
3. DECIDE - Strategy Selection
4. ACT - Action Execution
5. MEASURE - Safety Validation
6. LEARN - Continuous Improvement
"""

from infrastructure.eventbus import create_eventbus_from_env, Event

class AIOrchestrator:
    def __init__(self):
        self.bus = create_eventbus_from_env()

    async def orchestrate(self, situation):
        """Run 6-step cognitive loop"""

        # Step 1: MONITOR
        context = await self.context_aggregator.aggregate(situation)

        # Step 2: UNDERSTAND
        priority = await self.priority_engine.assess(situation, context)

        # Step 3: DECIDE
        strategy = await self.strategy_selector.select(situation, context, priority)

        # Step 4: ACT (через EventBus!)
        await self.bus.publish(Event.create(
            event_type="orchestration.action.execute",
            data={
                "action_type": strategy.action_type,
                "strategy": strategy.to_dict(),
                "priority": priority
            },
            source="ai-orchestrator",
            tenant_id=situation.tenant_id
        ))

        # Step 5: MEASURE
        # (Choreography - safety_monitor подписывается и валидирует)

        # Step 6: LEARN
        # (Choreography - learner подписывается и обучается)

        return strategy
```

---

## ✅ SUCCESS CRITERIA (По Фазам)

### Phase 1 Success:
- ✅ EventBus Health Monitoring работает (30 sec loop)
- ✅ Auto-Recovery срабатывает при Redis failure
- ✅ Resource Optimizer работает (5 min loop)
- ✅ ai-event-manager интегрирован

### Phase 2 Success:
- ✅ Core Coordinator работает (RAG → ML → Learning)
- ✅ Pattern Detector детектирует паттерны
- ✅ Model Trainer переобучает (24h cycle)
- ✅ event_intelligence + ai-foundation интегрированы

### Phase 3 Success:
- ✅ Expert Coordinator (12 assistants collaborate)
- ✅ Collective Intelligence Cycle (k=5, 7 days)
- ✅ Community Learning Loop работает

### Phase 4 Success:
- ✅ AI Orchestrator работает (6-step loop)
- ✅ Program Coordinator (end-to-end workflows)
- ✅ Virtuous Cycle (3 user groups, 7 days)
- ✅ Полная интеграция всех 4 уровней

---

## 🚀 NEXT STEPS

1. **Подтвердить подход** - Правильно ли понял что собирать?
2. **Начать с Phase 1** - Infrastructure Integration (самое важное)
3. **Использовать существующее** - Не изобретать заново
4. **Интегрировать через EventBus** - Choreography для всего

---

**Status:** Ready to Start Integration
**Priority:** Phase 1 (Infrastructure) → Phase 2 (Core) → Phase 3 (Center) → Phase 4 (Program)
