# План Координации: Снизу Вверх (Bottom-Up)
## Анализ Текущего Состояния + Поэтапное Проектирование

**Date:** 2025-10-09
**Approach:** Bottom-Up (Infrastructure → Core → Center → Program)
**Status:** Analysis + Design

---

## 🔍 ТЕКУЩЕЕ СОСТОЯНИЕ

### ЧТО УЖЕ ЕСТЬ:

| Компонент | Статус | Координация |
|-----------|--------|-------------|
| **EventBus** | ✅ 100% ready | ✅ Choreography готов (Redis Streams) |
| **infrastructure/orchestrator** | ✅ Ready | ✅ Unified Orchestrator (для AI Office tasks) |
| **intelligent-core/orchestration** | ⚠️ Существует, но СТАРЫЙ | ❌ Не интегрирован с EventBus |
| **ai-foundation** | ✅ Ready | ⚠️ Частично (140 событий найдено) |
| **expertise-center** | ✅ Ready | ⚠️ Частично (события есть, координации НЕТ) |
| **workflow_intelligence** | ✅ Ready | ⚠️ Частично (Temporal workflows isolate

d) |
| **platform-services** | ✅ Ready | ❌ Вообще нет координации |

### ГЛАВНАЯ ПРОБЛЕМА:

```
❌ Модули висят САМИ ПО СЕБЕ
❌ Нет операционного управления/координации
❌ Нет внутренней коммуникации между модулями
❌ EventBus 100% готов, но используется ЧАСТИЧНО (140 мест из 1000+)
```

---

## 🎯 УПУЩЕННЫЕ ЦИКЛЫ

Я описал ОДИН Virtuous Cycle (program level), но упустил:

### 1. Infrastructure Level Cycle (БАЗОВЫЙ)
```
Health Check → Failure Detection → Auto-Recovery →
Performance Metrics → Resource Optimization → REPEAT ♻️
```

### 2. Core Level Cycle (МОЗГ)
```
Data Collection → Pattern Detection → Model Training →
Prediction → Validation → Model Update → REPEAT ♻️
```

### 3. Center Level Cycle (ЭКСПЕРТИЗА)
```
Expert Analysis → Knowledge Extraction → Best Practice →
Application → Feedback → Refinement → REPEAT ♻️
```

### 4. Program Level Cycle (ПОЛЬЗОВАТЕЛИ)
```
User Action → Case Collection → Pattern Detection →
Material Generation → Knowledge Share → User Learning → REPEAT ♻️
```

### 5. Cross-Level Cycle (ИНТЕГРАЦИЯ)
```
Infrastructure Performance → Core Learning →
Center Expertise → Program Delivery →
User Feedback → Infrastructure Optimization → REPEAT ♻️
```

---

## 📐 4 УРОВНЯ КООРДИНАЦИИ (Bottom-Up)

### LEVEL 1: INFRASTRUCTURE (Фундамент)

**Что это:**
- EventBus, Database, Redis, API Gateway
- Базовая инфраструктура, на которой всё работает
- NO бизнес-логика, ТОЛЬКО техническая координация

**Координация:**
- **Choreography** (event-driven, decentralized)
- Health monitoring, auto-recovery, resource management
- Circuit breakers, fallbacks, retries

**Модули:**
- `/infrastructure/eventbus/`
- `/infrastructure/database/`
- `/infrastructure/gateway/`
- `/infrastructure/observability/`
- `/infrastructure/AI-office-infrastructure/orchestrator` (для инфраструктурных задач)

**Текущий статус:**
- ✅ EventBus готов (Redis Streams)
- ✅ Orchestrator готов (Infrastructure Executor)
- ❌ НЕТ координации между infrastructure компонентами
- ❌ НЕТ health monitoring cycle
- ❌ НЕТ auto-recovery механизмов

**Что нужно:**
1. Infrastructure Coordination Layer
2. Health Monitoring Cycle
3. Auto-Recovery Mechanism
4. Resource Optimization Cycle

---

### LEVEL 2: CORE (Мозг)

**Что это:**
- `ai-foundation` - RAG, ML, Learning, LLM Router
- "Мозг" системы - обработка данных, learning, predictions
- NO domain expertise, ТОЛЬКО AI infrastructure

**Координация:**
- **Choreography** для data flows (события между AI компонентами)
- **Internal Orchestration** для сложных ML pipelines

**Модули:**
- `/intelligent-core/ai-foundation/`
  - `rag/` - RAG Pipeline
  - `ml/` - ML Models
  - `learning/` - Self-Learning
  - `llm/` - LLM Router
  - `learning-knowledge/` - Knowledge Management

**Текущий статус:**
- ✅ Компоненты существуют
- ⚠️ Частичная интеграция с EventBus (140 событий)
- ❌ НЕТ координации между RAG → ML → Learning
- ❌ НЕТ learning cycle
- ❌ НЕТ feedback loop между компонентами

**Что нужно:**
1. Core Coordination Layer (внутри ai-foundation)
2. ML Training Cycle
3. RAG → ML → Learning Pipeline
4. Feedback Loop для model improvement

---

### LEVEL 3: CENTER (Экспертиза)

**Что это:**
- `expertise-center` - 12 Tactical Assistants
- `collective` - Collective Intelligence
- `community_intelligence` - Learning от users
- Domain expertise (BCM knowledge)

**Координация:**
- **Hybrid:**
  - Choreography для событий (learning from users)
  - Orchestration для expert workflows (BIA, Risk Assessment)

**Модули:**
- `/intelligent-core/expertise-center/`
  - `ai_experts/` - 12 Tactical Assistants
  - `domain_knowledge/` - BCM knowledge
- `/intelligent-core/collective/`
- `/intelligent-core/community_intelligence/`

**Текущий статус:**
- ✅ 12 Tactical Assistants существуют
- ✅ Collective Intelligence framework есть
- ❌ НЕТ координации между assistants
- ❌ НЕТ learning loop от community
- ❌ НЕТ collective intelligence cycle

**Что нужно:**
1. Center Coordination Layer
2. Expert Collaboration Mechanism (12 assistants работают вместе)
3. Community Learning Cycle
4. Collective Intelligence Cycle (k=5)

---

### LEVEL 4: PROGRAM (Программные потоки)

**Что это:**
- `platform-services/` - 12 бизнес-сервисов (BIA, Risk, Planning, etc.)
- `workflow_intelligence` - Orchestration workflows
- User-facing business logic

**Координация:**
- **Hybrid:**
  - Orchestration для critical workflows (BIA, ISO Journey)
  - Choreography для side-effects (notifications, logging, learning)

**Модули:**
- `/platform-services/*` (12 services)
- `/intelligent-core/workflow_intelligence/`
- `/intelligent-core/orchestration/` (program-level orchestration)

**Текущий статус:**
- ✅ 12 platform services существуют
- ✅ workflow_intelligence с Temporal workflows
- ⚠️ intelligent-core/orchestration СТАРЫЙ (не интегрирован)
- ❌ НЕТ координации между platform-services
- ❌ НЕТ end-to-end workflows
- ❌ НЕТ virtuous cycle для users

**Что нужно:**
1. Program Coordination Layer
2. End-to-End Workflow Orchestration
3. User Learning Cycle
4. Virtuous Cycle (3 user groups)

---

## 🔄 ПОЭТАПНЫЙ ПЛАН (Bottom-Up)

### PHASE 1: INFRASTRUCTURE COORDINATION (Фундамент) ⬅️ НАЧИНАЕМ ЗДЕСЬ

**Цель:** Обеспечить базовую устойчивость и координацию инфраструктуры

#### Task 1.1: Infrastructure Health Monitoring Cycle

**Создать:**
```python
# infrastructure/coordination/health_monitor.py

class InfrastructureHealthMonitor:
    """Мониторит здоровье всей инфраструктуры"""

    async def run_health_cycle(self):
        """Постоянный цикл health monitoring"""

        while True:
            # Check all infrastructure components
            redis_health = await self.check_redis()
            db_health = await self.check_database()
            gateway_health = await self.check_gateway()

            # Publish health status
            await publish_event("infrastructure.health.checked", {
                "redis": redis_health,
                "database": db_health,
                "gateway": gateway_health,
                "timestamp": datetime.now()
            })

            # Wait 30 seconds
            await asyncio.sleep(30)
```

**Choreography для реакций:**
```python
# infrastructure/observability/health_subscribers.py

@subscribe_to("infrastructure.health.checked")
async def record_health_metrics(event: Event):
    """Записывает health metrics в Prometheus"""
    await prometheus.record("infrastructure_redis_health", event.data["redis"]["status"])
    await prometheus.record("infrastructure_db_health", event.data["database"]["status"])

@subscribe_to("infrastructure.health.checked")
async def trigger_recovery_if_needed(event: Event):
    """Триггерит recovery если что-то упало"""
    if event.data["redis"]["status"] == "down":
        await publish_event("infrastructure.redis.failed", {})

    if event.data["database"]["status"] == "degraded":
        await publish_event("infrastructure.database.degraded", {})
```

---

#### Task 1.2: Auto-Recovery Mechanism

**Создать:**
```python
# infrastructure/coordination/auto_recovery.py

@subscribe_to("infrastructure.redis.failed")
async def recover_redis(event: Event):
    """Auto-recovery для Redis"""

    logger.warning("🚨 Redis FAILED - starting recovery")

    # Step 1: Activate fallback (in-memory queue)
    await activate_in_memory_queue()

    # Step 2: Try reconnection (every 10 sec, max 6 tries)
    for attempt in range(6):
        await asyncio.sleep(10)
        if await try_reconnect_redis():
            logger.info("✅ Redis RECOVERED")
            await deactivate_in_memory_queue()
            await publish_event("infrastructure.redis.recovered", {
                "recovery_time": attempt * 10
            })
            return

    # Step 3: If failed after 60sec → alert
    await publish_event("infrastructure.redis.recovery_failed", {
        "alert": "Manual intervention required"
    })


@subscribe_to("infrastructure.database.degraded")
async def optimize_database(event: Event):
    """Auto-optimization для degraded Database"""

    logger.warning("⚠️ Database DEGRADED - optimizing")

    # Kill long queries
    await kill_long_queries(threshold_sec=30)

    # Scale down connection pool
    await scale_connection_pool(target=20)

    # Enable read-only mode temporarily
    await enable_readonly_mode(duration_sec=60)

    # Wait for recovery
    await asyncio.sleep(60)

    # Restore
    await disable_readonly_mode()
    await scale_connection_pool(target=40)

    await publish_event("infrastructure.database.optimized", {})
```

---

#### Task 1.3: Resource Optimization Cycle

**Создать:**
```python
# infrastructure/coordination/resource_optimizer.py

class ResourceOptimizer:
    """Оптимизирует использование ресурсов"""

    async def run_optimization_cycle(self):
        """Цикл оптимизации (каждые 5 минут)"""

        while True:
            # Collect resource metrics
            metrics = await self.collect_resource_metrics()

            # Analyze
            recommendations = await self.analyze_resource_usage(metrics)

            # Publish recommendations
            await publish_event("infrastructure.resources.analyzed", {
                "cpu_usage": metrics["cpu"],
                "memory_usage": metrics["memory"],
                "db_connections": metrics["db_conn"],
                "recommendations": recommendations
            })

            # Wait 5 minutes
            await asyncio.sleep(300)


@subscribe_to("infrastructure.resources.analyzed")
async def apply_optimizations(event: Event):
    """Применяет оптимизации автоматически"""

    for recommendation in event.data["recommendations"]:
        if recommendation["auto_apply"]:
            if recommendation["type"] == "scale_down_connections":
                await scale_connection_pool(recommendation["target_size"])

            elif recommendation["type"] == "enable_caching":
                await enable_redis_caching(recommendation["cache_keys"])

            logger.info(f"✅ Applied: {recommendation['type']}")
```

---

### PHASE 2: CORE COORDINATION (Мозг)

**Цель:** Координация AI компонентов внутри ai-foundation

#### Task 2.1: RAG → ML → Learning Pipeline

**Создать:**
```python
# intelligent-core/ai-foundation/coordination/core_coordinator.py

class CoreCoordinator:
    """Координирует RAG → ML → Learning pipeline"""

    async def run_learning_pipeline(self, query: str, user_feedback: dict):
        """Pipeline: RAG → LLM → User Feedback → ML Learning"""

        # Step 1: RAG retrieval
        rag_results = await rag_pipeline.search(query)

        # Step 2: LLM generation
        llm_response = await llm_router.generate(
            prompt=query,
            context=rag_results
        )

        # Step 3: User feedback
        # (user rates response 1-5, provides corrections)

        # Step 4: Learning
        await publish_event("core.learning.feedback_received", {
            "query": query,
            "rag_results": rag_results,
            "llm_response": llm_response,
            "user_rating": user_feedback["rating"],
            "user_correction": user_feedback.get("correction")
        })

        return llm_response


@subscribe_to("core.learning.feedback_received")
async def update_ml_models(event: Event):
    """Обновляет ML models на основе feedback"""

    # If rating < 3 → bad response
    if event.data["user_rating"] < 3:
        # Analyze: почему RAG retrieval был плохой?
        await rag_quality_analyzer.analyze_failure(
            query=event.data["query"],
            retrieved=event.data["rag_results"],
            expected=event.data["user_correction"]
        )

        # Update retrieval model
        await rag_ml_model.train_on_failure(
            query=event.data["query"],
            bad_results=event.data["rag_results"],
            correct_result=event.data["user_correction"]
        )

    # If rating >= 4 → good response
    elif event.data["user_rating"] >= 4:
        # Reinforce this pattern
        await rag_ml_model.train_on_success(
            query=event.data["query"],
            good_results=event.data["rag_results"]
        )
```

---

#### Task 2.2: Model Training Cycle

**Создать:**
```python
# intelligent-core/ai-foundation/learning/training_cycle.py

class ModelTrainingCycle:
    """Периодическое переобучение ML models"""

    async def run_training_cycle(self):
        """Цикл: каждые 24 часа переобучаем models"""

        while True:
            # Collect training data за последние 24 часа
            training_data = await self.collect_training_data(hours=24)

            if len(training_data) >= 100:  # Minimum 100 samples
                # Retrain models
                await publish_event("core.training.started", {
                    "data_count": len(training_data)
                })

                results = await self.retrain_all_models(training_data)

                await publish_event("core.training.completed", {
                    "models_updated": results["models"],
                    "accuracy_improvement": results["accuracy_delta"]
                })

            # Wait 24 hours
            await asyncio.sleep(86400)
```

---

### PHASE 3: CENTER COORDINATION (Экспертиза)

**Цель:** Координация между 12 Tactical Assistants + Collective Intelligence

#### Task 3.1: Expert Collaboration Mechanism

**Создать:**
```python
# intelligent-core/expertise-center/coordination/expert_coordinator.py

class ExpertCoordinator:
    """Координирует работу 12 Tactical Assistants"""

    async def collaborate_on_bia(self, org_id: str):
        """Несколько экспертов работают вместе над BIA"""

        # Step 1: BIA Specialist создает plan
        bia_plan = await bia_specialist.create_bia_plan(org_id)

        await publish_event("center.bia.plan_created", {
            "org_id": org_id,
            "bia_plan": bia_plan
        })

        # Step 2: Risk Analyst оценивает риски
        # (реагирует на событие)

        # Step 3: Compliance Auditor проверяет соответствие ISO
        # (реагирует на событие)

        # Step 4: Training Specialist создает обучающие материалы
        # (реагирует на событие)

        return bia_plan


@subscribe_to("center.bia.plan_created")
async def risk_analyst_reviews_bia(event: Event):
    """Risk Analyst проверяет BIA plan на риски"""

    bia_plan = event.data["bia_plan"]

    # Analyze risks
    risks = await risk_analyst.analyze_bia_risks(bia_plan)

    await publish_event("center.bia.risks_identified", {
        "org_id": event.data["org_id"],
        "risks": risks
    })


@subscribe_to("center.bia.plan_created")
async def compliance_auditor_checks_iso(event: Event):
    """Compliance Auditor проверяет ISO 22301 compliance"""

    bia_plan = event.data["bia_plan"]

    # Check compliance
    compliance = await compliance_auditor.check_iso22301(bia_plan)

    await publish_event("center.bia.compliance_checked", {
        "org_id": event.data["org_id"],
        "compliance_score": compliance["score"],
        "gaps": compliance["gaps"]
    })
```

---

#### Task 3.2: Collective Intelligence Cycle

**Создать:**
```python
# intelligent-core/collective/coordination/collective_cycle.py

class CollectiveCycle:
    """Цикл Collective Intelligence"""

    async def run_collective_cycle(self):
        """Каждые 7 дней обновляем Collective Agents"""

        while True:
            # Collect all new cases за последние 7 дней
            new_cases = await self.collect_new_cases(days=7)

            # Group by context (HIV program, rural clinic, etc.)
            grouped = await self.group_by_context(new_cases)

            for context, cases in grouped.items():
                if len(cases) >= 5:  # k=5 minimum
                    # Update or create Collective Agent
                    agent = await self.update_collective_agent(context, cases)

                    await publish_event("collective.agent.updated", {
                        "context": context,
                        "case_count": len(cases),
                        "patterns_detected": len(agent["patterns"])
                    })

            # Wait 7 days
            await asyncio.sleep(7 * 86400)
```

---

### PHASE 4: PROGRAM COORDINATION (Программные потоки)

**Цель:** End-to-end workflow orchestration для пользователей

#### Task 4.1: Workflow Orchestration

**Использовать existing:**
- `intelligent-core/orchestration/` (ОБНОВИТЬ, интегрировать с EventBus)
- `workflow_intelligence/workflows/temporal/` (Temporal workflows)

**Создать:**
```python
# intelligent-core/orchestration/coordination/program_coordinator.py

class ProgramCoordinator:
    """Координирует program-level workflows"""

    async def orchestrate_bia_journey(self, org_id: str):
        """Orchestrates полный BIA journey"""

        # Step 1: Start BIA (platform-services/bia-service)
        bia = await bia_service.start_bia(org_id)

        await publish_event("program.bia.started", {
            "org_id": org_id,
            "bia_id": bia["bia_id"]
        })

        # Step 2: Wait for completion
        # (Temporal workflow handles this)

        # Step 3: Generate materials
        # (Choreography - multiple services react)

        return bia


# Choreography для side-effects

@subscribe_to("program.bia.completed")
async def save_to_case_library(event: Event):
    """Case Library сохраняет кейс"""
    await case_library.add_case(event.data["bia_plan"])


@subscribe_to("program.bia.completed")
async def update_collective(event: Event):
    """Collective Intelligence обновляется"""
    await collective.add_to_pool(event.data["bia_plan"])


@subscribe_to("program.bia.completed")
async def notify_donor(event: Event):
    """Donor видит прогресс"""
    await donor_dashboard.update_progress(event.data["org_id"])


@subscribe_to("program.bia.completed")
async def generate_learning_materials(event: Event):
    """Автоматически создаются обучающие материалы"""
    materials = await material_generator.generate_from_case(event.data["bia_plan"])
    await publish_event("program.materials.generated", {
        "materials": materials
    })
```

---

#### Task 4.2: Virtuous Cycle для 3 групп пользователей

**Создать:**
```python
# intelligent-core/orchestration/coordination/virtuous_cycle.py

class VirtuousCycleCoordinator:
    """Координирует Virtuous Cycle для 3 user groups"""

    async def run_virtuous_cycle(self):
        """Запускает полный цикл раз в 7 дней"""

        while True:
            # Phase 1: Collect from 3 groups
            consultant_data = await self.collect_consultant_insights()
            org_data = await self.collect_org_cases()
            donor_data = await self.collect_donor_feedback()

            # Phase 2: Detect patterns
            patterns = await self.detect_patterns(consultant_data, org_data, donor_data)

            await publish_event("program.patterns.detected", {
                "patterns": patterns
            })

            # Phase 3: Generate materials
            # (Choreography - material_generator reacts)

            # Phase 4: Share knowledge
            # (Choreography - knowledge_library reacts)

            # Phase 5: Improve code
            # (Choreography - code_improver reacts)

            # Wait 7 days
            await asyncio.sleep(7 * 86400)
```

---

## 🎯 IMPLEMENTATION PRIORITY

### Priority 1: Infrastructure Coordination (PHASE 1) ⭐⭐⭐⭐⭐
**Почему первое:** Без устойчивой инфраструктуры всё остальное бесполезно

**Tasks:**
1. Health Monitoring Cycle
2. Auto-Recovery Mechanism
3. Resource Optimization Cycle

**Timeline:** 1-2 недели

---

### Priority 2: Core Coordination (PHASE 2) ⭐⭐⭐⭐
**Почему второе:** Мозг должен работать координированно

**Tasks:**
1. RAG → ML → Learning Pipeline
2. Model Training Cycle
3. Feedback Loop

**Timeline:** 2-3 недели

---

### Priority 3: Center Coordination (PHASE 3) ⭐⭐⭐
**Почему третье:** Экспертиза строится на устойчивом мозге

**Tasks:**
1. Expert Collaboration Mechanism
2. Collective Intelligence Cycle
3. Community Learning Loop

**Timeline:** 2-3 недели

---

### Priority 4: Program Coordination (PHASE 4) ⭐⭐
**Почему последнее:** Пользовательские flows зависят от всех предыдущих уровней

**Tasks:**
1. Workflow Orchestration
2. Virtuous Cycle
3. End-to-End Integration

**Timeline:** 3-4 недели

---

## ✅ SUCCESS CRITERIA

**Phase 1:**
- ✅ Infrastructure health cycle работает (30sec intervals)
- ✅ Auto-recovery срабатывает при сбоях
- ✅ Resource optimization оптимизирует каждые 5 минут

**Phase 2:**
- ✅ RAG → ML pipeline работает end-to-end
- ✅ Models переобучаются каждые 24 часа
- ✅ Accuracy улучшается с каждым циклом

**Phase 3:**
- ✅ 12 Tactical Assistants работают вместе
- ✅ Collective Agents обновляются каждые 7 дней
- ✅ Community learning loop функционирует

**Phase 4:**
- ✅ End-to-end BIA journey работает
- ✅ Virtuous Cycle генерирует материалы каждые 7 дней
- ✅ 3 user groups получают value

---

## 🚀 NEXT STEPS

1. ✅ **Утвердить подход** (Bottom-Up правильный?)
2. ✅ **Начать с Phase 1** (Infrastructure Coordination)
3. Создать координаторы для каждого уровня
4. Интегрировать с существующим EventBus
5. Тестировать каждый цикл отдельно
6. Интегрировать циклы между уровнями

---

**Status:** Ready to start Phase 1
**Awaiting:** Confirmation of approach
