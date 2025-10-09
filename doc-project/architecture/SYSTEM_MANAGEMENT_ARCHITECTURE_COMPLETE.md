# Полная Архитектура Системы Управления
## Самообучающаяся BCM Платформа

**Date:** 2025-10-09
**Version:** 1.0 - Complete Design
**Status:** Implementation Ready

---

## 🎯 МИССИЯ

Создать **самообучающуюся интеллектуальную систему**, которая становится **экспертом BCM** через:

1. **ПРОЖИВАНИЕ BCM на себе** (практика, не теория)
2. **ОБУЧЕНИЕ от 3 групп пользователей** (консультанты, организации, доноры)
3. **ЭВОЛЮЦИЮ через код** (pattern detection → code generation)
4. **ОРКЕСТРАЦИЮ взаимодействия** (virtuous cycle)

---

## 🏗️ ДВЕ ЦЕЛИ + АРХИТЕКТУРА

### ЦЕЛЬ 1: УСТОЙЧИВОСТЬ СИСТЕМЫ (System Level)

**Концепт:** Система применяет BCM на СЕБЕ

#### 1.1 BIA для Процессов Системы

**Критичные процессы платформы:**

| Процесс | RTO | RPO | Зависимости | Приоритет |
|---------|-----|-----|-------------|-----------|
| **EventBus** | 30 sec | 0 | Redis Streams | CRITICAL |
| **API Gateway** | 1 min | 0 | None (stateless) | CRITICAL |
| **PostgreSQL** | 5 min | 1 min | Supabase | CRITICAL |
| **AI Foundation** | 2 min | 0 | Anthropic/OpenAI, Qdrant | HIGH |
| **Expertise Center** | 3 min | 0 | AI Foundation | HIGH |
| **Workflow Intelligence** | 5 min | 5 min | PostgreSQL, EventBus | MEDIUM |
| **Monitoring** | 10 min | 5 min | Prometheus, Grafana | MEDIUM |

**Orchestration для BIA системы:**

```python
# intelligent-core/orchestration/system_bia.py

class SystemBIAOrchestrator:
    """Orchestrates BIA для процессов самой системы"""

    async def run_system_bia(self):
        """Запускает BIA для всех процессов системы"""

        # Step 1: Identify critical processes
        processes = await self.identify_system_processes()

        # Step 2: Assess dependencies
        for process in processes:
            dependencies = await self.map_dependencies(process)
            await publish_event("system.bia.dependencies_mapped", {
                "process": process.name,
                "dependencies": dependencies
            })

        # Step 3: Define RTO/RPO
        for process in processes:
            rto_rpo = await self.calculate_rto_rpo(process)
            await publish_event("system.bia.rto_defined", {
                "process": process.name,
                "rto": rto_rpo["rto"],
                "rpo": rto_rpo["rpo"]
            })

        # Step 4: Create recovery strategies
        for process in processes:
            strategy = await self.design_recovery_strategy(process)
            await publish_event("system.bia.strategy_created", {
                "process": process.name,
                "strategy": strategy
            })

        return {
            "status": "completed",
            "processes_analyzed": len(processes),
            "critical_count": sum(1 for p in processes if p.priority == "CRITICAL")
        }
```

**Choreography для реакций:**

```python
# intelligent-core/event_intelligence/system_subscribers.py

@subscribe_to("system.bia.dependencies_mapped")
async def learn_from_system_bia(event: Event):
    """Event Intelligence учится из системного BIA"""

    # Записываем паттерн зависимостей
    await knowledge_graph.add_dependency(
        from_process=event.data["process"],
        to_processes=event.data["dependencies"]
    )

    # Детектим circular dependencies
    if await detect_circular_dependency(event.data["process"]):
        await publish_event("system.risk.circular_dependency", {
            "process": event.data["process"],
            "severity": "high"
        })
```

---

#### 1.2 Risk Assessment для Системы

**Риски системы:**

| Риск | Вероятность | Impact | Приоритет | Mitigation |
|------|-------------|--------|-----------|------------|
| **Redis down** | Medium | Critical | P1 | Fallback to in-memory queue |
| **PostgreSQL overload** | High | High | P1 | Connection pooling, query optimization |
| **API rate limits (OpenAI)** | High | Medium | P2 | LLM Router (fallback to Anthropic) |
| **Qdrant slow queries** | Medium | Medium | P2 | Caching, index optimization |
| **Memory leak** | Low | High | P2 | Auto-restart on threshold |
| **DDoS attack** | Low | Critical | P1 | Rate limiting, WAF |

**Orchestration для Risk Assessment:**

```python
# intelligent-core/orchestration/system_risk.py

class SystemRiskOrchestrator:
    """Orchestrates Risk Assessment для системы"""

    async def run_system_risk_assessment(self):
        """Оценивает риски системы"""

        # Step 1: Identify risks
        risks = await self.identify_system_risks()

        # Step 2: Assess probability & impact
        for risk in risks:
            assessment = await self.assess_risk(risk)
            await publish_event("system.risk.assessed", {
                "risk_id": risk.id,
                "probability": assessment["probability"],
                "impact": assessment["impact"],
                "priority": assessment["priority"]
            })

        # Step 3: Design mitigation
        for risk in risks:
            if risk.priority in ["P1", "P2"]:
                mitigation = await self.design_mitigation(risk)
                await publish_event("system.risk.mitigation_designed", {
                    "risk_id": risk.id,
                    "mitigation": mitigation
                })

        # Step 4: Implement controls
        for risk in risks:
            if risk.priority == "P1":
                await self.implement_control(risk)
                await publish_event("system.risk.control_implemented", {
                    "risk_id": risk.id,
                    "control": risk.control
                })

        return {"status": "completed", "risks_assessed": len(risks)}
```

**Choreography для автоматических mitigation:**

```python
# infrastructure/observability/risk_handlers.py

@subscribe_to("system.risk.assessed")
async def auto_implement_mitigation(event: Event):
    """Автоматически применяет mitigation для известных рисков"""

    risk_id = event.data["risk_id"]

    if risk_id == "redis_down":
        # Активируем fallback
        await activate_fallback_queue()
        await publish_event("system.mitigation.activated", {
            "risk_id": risk_id,
            "action": "fallback_queue_activated"
        })

    elif risk_id == "postgresql_overload":
        # Увеличиваем connection pool
        await scale_connection_pool(target_size=50)
        await publish_event("system.mitigation.activated", {
            "risk_id": risk_id,
            "action": "connection_pool_scaled"
        })
```

---

#### 1.3 Recovery Plans для Системы

**Recovery strategies:**

**Scenario 1: EventBus Down (Redis Streams unavailable)**

```python
# infrastructure/eventbus/recovery.py

class EventBusRecoveryPlan:
    """Recovery plan для EventBus failures"""

    async def detect_failure(self):
        """Детектит failure EventBus"""
        try:
            await redis.ping()
            return False  # Healthy
        except ConnectionError:
            await publish_alert("EventBus DOWN - activating recovery")
            return True  # Failed

    async def recover(self):
        """Восстанавливает EventBus"""

        # Step 1: Activate fallback (in-memory queue)
        await self.activate_in_memory_queue()
        logger.warning("⚠️ EventBus DOWN - using in-memory fallback")

        # Step 2: Buffer events
        buffered_events = []
        async for event in self.in_memory_queue:
            buffered_events.append(event)

        # Step 3: Attempt reconnection (every 10 sec)
        while not await self.try_reconnect():
            await asyncio.sleep(10)

        # Step 4: Replay buffered events
        logger.info("✅ EventBus RECOVERED - replaying buffered events")
        for event in buffered_events:
            await publish_event(event.name, event.data)

        # Step 5: Switch back to Redis
        await self.deactivate_in_memory_queue()
        logger.info("✅ EventBus fully recovered")
```

**Scenario 2: PostgreSQL Overload**

```python
# infrastructure/database/recovery.py

class DatabaseRecoveryPlan:
    """Recovery plan для Database overload"""

    async def detect_overload(self):
        """Детектит перегрузку DB"""
        metrics = await self.get_db_metrics()

        if metrics["active_connections"] > 80:  # 80% threshold
            return True
        if metrics["query_latency_p95"] > 1000:  # 1 sec
            return True
        return False

    async def recover(self):
        """Восстанавливает DB performance"""

        # Step 1: Kill long-running queries
        long_queries = await self.find_long_queries(threshold_sec=30)
        for query in long_queries:
            await self.kill_query(query.pid)
            logger.warning(f"Killed long query: {query.query[:100]}")

        # Step 2: Scale connection pool DOWN (reduce pressure)
        await self.scale_connection_pool(target_size=20)

        # Step 3: Enable read-only mode for non-critical endpoints
        await self.enable_readonly_mode()

        # Step 4: Clear cache (might have stale data)
        await redis.flushdb()

        # Step 5: Wait for recovery
        await asyncio.sleep(60)

        # Step 6: Gradually restore
        await self.disable_readonly_mode()
        await self.scale_connection_pool(target_size=40)

        logger.info("✅ Database recovered from overload")
```

**Scenario 3: LLM API Rate Limits**

```python
# intelligent-core/ai-foundation/llm/recovery.py

class LLMRecoveryPlan:
    """Recovery plan для LLM API rate limits"""

    async def detect_rate_limit(self, provider: str):
        """Детектит rate limit"""
        try:
            response = await self.call_llm(provider, test_prompt="Hello")
            return False
        except RateLimitError:
            return True

    async def recover(self, provider: str):
        """Переключается на альтернативный LLM"""

        # Step 1: Switch to fallback provider
        if provider == "anthropic":
            fallback = "openai"
        else:
            fallback = "anthropic"

        logger.warning(f"⚠️ {provider} rate limited - switching to {fallback}")
        await self.set_primary_provider(fallback)

        # Step 2: Queue requests for original provider
        await self.queue_for_retry(provider, delay_minutes=5)

        # Step 3: Notify monitoring
        await publish_event("system.recovery.llm_switched", {
            "from": provider,
            "to": fallback,
            "reason": "rate_limit"
        })

        return {"status": "recovered", "using": fallback}
```

---

#### 1.4 Chaos Engineering (Тестирование Recovery)

**Намеренные сбои для тестирования:**

```python
# infrastructure/chaos/chaos_monkey.py

class ChaosMonkey:
    """Намеренно создает сбои для тестирования recovery"""

    async def run_chaos_test(self, scenario: str):
        """Запускает chaos test"""

        logger.warning(f"🐒 Chaos Monkey: Starting {scenario} test")

        if scenario == "redis_down":
            # Останавливаем Redis на 30 секунд
            await self.stop_redis()
            await asyncio.sleep(30)
            await self.start_redis()

            # Проверяем: восстановился ли EventBus?
            assert await self.check_eventbus_health()
            logger.info("✅ Chaos test PASSED: EventBus recovered")

        elif scenario == "db_overload":
            # Генерируем 1000 heavy queries
            await self.generate_heavy_load(queries=1000)

            # Проверяем: сработал ли auto-recovery?
            await asyncio.sleep(60)
            assert await self.check_db_latency() < 500  # ms
            logger.info("✅ Chaos test PASSED: DB recovered from overload")

        elif scenario == "llm_rate_limit":
            # Симулируем rate limit
            await self.block_anthropic_api()

            # Проверяем: переключился ли на OpenAI?
            assert await self.get_active_llm() == "openai"
            logger.info("✅ Chaos test PASSED: LLM switched to fallback")

        return {"test": scenario, "status": "PASSED"}
```

**Choreography для learning from chaos:**

```python
# intelligent-core/event_intelligence/chaos_subscribers.py

@subscribe_to("chaos.test.completed")
async def learn_from_chaos(event: Event):
    """Учится из chaos tests"""

    # Записываем: сколько времени заняло recovery
    recovery_time = event.data["recovery_time_seconds"]

    await knowledge_graph.add_fact(
        fact_type="recovery_performance",
        scenario=event.data["scenario"],
        recovery_time=recovery_time,
        rto_target=event.data["rto_target"],
        passed=recovery_time < event.data["rto_target"]
    )

    # Если recovery НЕ прошел в RTO → создать improvement task
    if recovery_time >= event.data["rto_target"]:
        await workflow_intelligence.create_task({
            "type": "improve_recovery",
            "scenario": event.data["scenario"],
            "current_time": recovery_time,
            "target_time": event.data["rto_target"],
            "priority": "high"
        })
```

---

### ЦЕЛЬ 2: СТАТЬ ЭКСПЕРТОМ BCM (Program Level)

**Концепт:** Система учится от 3 групп пользователей

#### 2.1 Обучение от КОНСУЛЬТАНТОВ

**Что консультанты дают:**
- Методологии (как правильно делать BIA)
- Best practices (ISO 22301, NIST)
- Экспертные оценки (quality review)
- Инструменты (чеклисты, шаблоны)

**Как система учится:**

```python
# intelligent-core/community_intelligence/consultant_learning.py

@subscribe_to("consultant.completed_audit")
async def learn_from_consultant_audit(event: Event):
    """Учится из audit проведенного консультантом"""

    audit_data = event.data

    # Консультант оценил BIA plan на 8/10
    # Что он отметил как хорошо, что как плохо?

    quality_feedback = audit_data["quality_assessment"]

    # Детектим паттерны ХОРОШЕГО BIA
    if quality_feedback["score"] >= 8:
        good_patterns = await extract_patterns(audit_data["bia_plan"])

        # Сохраняем как "gold standard"
        await knowledge_graph.add_best_practice(
            domain="bia",
            patterns=good_patterns,
            source="expert_consultant",
            confidence=0.9
        )

    # Детектим паттерны ПЛОХОГО BIA
    if quality_feedback["score"] <= 5:
        bad_patterns = await extract_patterns(audit_data["bia_plan"])

        # Сохраняем как "anti-pattern"
        await knowledge_graph.add_anti_pattern(
            domain="bia",
            patterns=bad_patterns,
            issues=quality_feedback["issues"]
        )

    # Обновляем ML model для quality prediction
    await ml_quality_predictor.train(
        input=audit_data["bia_plan"],
        target_score=quality_feedback["score"]
    )

    await publish_event("system.learning.consultant_audit_processed", {
        "audit_id": audit_data["audit_id"],
        "learned_patterns": len(good_patterns) + len(bad_patterns)
    })
```

**Virtuous Cycle для консультантов:**

```
Консультант использует platform для клиента
↓
Консультант оценивает качество BIA (8/10)
↓
Система учится: что = хорошо, что = плохо
↓
Система улучшает свои AI recommendations
↓
Следующий BIA (другой организации) = лучше качество
↓
Консультант видит: platform помогает → использует чаще
↓
LOOP ♻️
```

---

#### 2.2 Обучение от ОРГАНИЗАЦИЙ

**Что организации дают:**
- Real-world кейсы (что работает на практике)
- Edge cases (ситуации не из учебника)
- Контекст (культурные особенности, ограничения)
- Feedback (что полезно, что нет)

**Collective Intelligence (k=5 anonymization):**

```python
# intelligent-core/collective/collective_agent.py

class CollectiveAgent:
    """Синтезирует опыт 5+ организаций (анонимно)"""

    async def create_collective_intelligence(self, domain: str, context: dict):
        """Создает Collective Agent для группы организаций"""

        # Находим 5+ организаций с похожим контекстом
        similar_orgs = await self.find_similar_orgs(
            domain=domain,  # "HIV program"
            context=context,  # {"location": "West Africa", "size": "small"}
            minimum=5
        )

        if len(similar_orgs) < 5:
            return None  # Не достаточно для k=5 privacy

        # Anonymize & aggregate
        aggregated_data = []
        for org in similar_orgs:
            # Удаляем все identifiable data
            anonymous_case = await self.anonymize(org.bia_data)
            aggregated_data.append(anonymous_case)

        # Детектим паттерны из 5+ кейсов
        patterns = await self.detect_patterns(aggregated_data)

        # Создаем Collective Agent
        agent = {
            "id": f"collective_{domain}_{hash(context)}",
            "domain": domain,
            "context": context,
            "org_count": len(similar_orgs),
            "patterns": patterns,
            "created_at": datetime.now()
        }

        # Сохраняем в Qdrant
        await qdrant.upsert(
            collection="collective_agents",
            documents=[{
                "id": agent["id"],
                "text": f"Collective intelligence from {len(similar_orgs)} {domain} organizations",
                "metadata": agent
            }]
        )

        return agent


@subscribe_to("organization.completed_bia")
async def update_collective_intelligence(event: Event):
    """Обновляет Collective Intelligence при завершении BIA"""

    org_data = event.data

    # Добавляем кейс в collective pool
    await collective_pool.add_case(
        domain=org_data["domain"],
        context=org_data["context"],
        bia_data=org_data["bia_plan"]
    )

    # Проверяем: достигли ли k=5 для этого контекста?
    count = await collective_pool.count_cases(
        domain=org_data["domain"],
        context=org_data["context"]
    )

    if count >= 5:
        # Создаем/обновляем Collective Agent
        agent = await CollectiveAgent().create_collective_intelligence(
            domain=org_data["domain"],
            context=org_data["context"]
        )

        await publish_event("collective.agent.updated", {
            "agent_id": agent["id"],
            "org_count": count,
            "patterns_detected": len(agent["patterns"])
        })
```

**Virtuous Cycle для организаций:**

```
Organization A завершает BIA
↓
Система anonymizes & добавляет в collective pool
↓
5+ organizations → создается Collective Agent
↓
Organization B (stuck) запрашивает помощь
↓
Collective Agent: "В 80% HIV clinics critical process = cold chain"
↓
Organization B: "Точно! Не подумал. Спасибо."
↓
Organization B завершает BIA → добавляется в pool
↓
Collective Agent УМНЕЕ (теперь 6 org вместо 5)
↓
LOOP ♻️
```

---

#### 2.3 Обучение от ДОНОРОВ

**Что доноры дают:**
- Impact metrics (что важно измерять)
- Priorities (какие org приоритетны)
- ROI expectations (что = успех)
- Feedback (какие dashboards нужны)

**Impact Dashboard Learning:**

```python
# platform-services/monitoring/donor_dashboard.py

class DonorDashboard:
    """Dashboard для доноров с learning механизмом"""

    async def render_dashboard(self, donor_id: str, program_id: str):
        """Рендерит dashboard И учится что донор смотрит"""

        # Рендерим стандартный dashboard
        dashboard = await self.generate_dashboard(program_id)

        # Логируем: что донор просматривает
        await self.log_view(
            donor_id=donor_id,
            program_id=program_id,
            timestamp=datetime.now()
        )

        return dashboard


@subscribe_to("donor.dashboard.viewed")
async def learn_from_donor_view(event: Event):
    """Учится из просмотров donor dashboards"""

    # Донор смотрел dashboard 10 раз за месяц
    # Какие metrics он drill-down чаще всего?

    view_data = event.data

    # Получаем историю просмотров этого донора
    history = await get_donor_view_history(
        donor_id=view_data["donor_id"],
        days=30
    )

    # Детектим паттерны: что важно для донора
    important_metrics = await detect_important_metrics(history)

    # important_metrics = ["% orgs completed BIA", "Avg RTO improvement"]

    # Обновляем dashboard config для этого донора
    await update_dashboard_config(
        donor_id=view_data["donor_id"],
        priority_metrics=important_metrics
    )

    # Обучаем ML: что показывать на dashboard
    await ml_dashboard_optimizer.train(
        donor_preferences=important_metrics,
        donor_type=view_data["donor_type"]  # "foundation", "government", etc.
    )


@subscribe_to("donor.requested_custom_metric")
async def add_custom_metric_to_platform(event: Event):
    """Донор запросил custom metric → добавляем в tracking"""

    custom_metric = event.data["metric"]

    # Донор хочет видеть: "% staff trained on BCM"

    # Добавляем tracking для этого metric
    await metrics_registry.add_metric(
        name=custom_metric["name"],
        description=custom_metric["description"],
        calculation=custom_metric["formula"],
        requested_by=event.data["donor_id"]
    )

    # Начинаем собирать этот metric для ВСЕХ programs
    await start_tracking_metric(custom_metric)

    # Система УЧИТСЯ: этот metric важен → добавляем в платформу
    await publish_event("system.learning.new_metric_added", {
        "metric": custom_metric["name"],
        "source": "donor_request"
    })
```

**Virtuous Cycle для доноров:**

```
Donor смотрит impact dashboard
↓
Система логирует: какие metrics важны
↓
Donor запрашивает custom metric ("% staff trained")
↓
Система добавляет tracking этого metric
↓
Все organizations теперь tracked по этому metric
↓
Donor видит новый metric на dashboard
↓
Donor доволен → финансирует больше org
↓
Система УМНЕЕ (знает что важно измерять)
↓
LOOP ♻️
```

---

## 🔄 VIRTUOUS CYCLE INTEGRATION

**Полный цикл самообучения:**

```python
# intelligent-core/orchestration/virtuous_cycle_orchestrator.py

class VirtuousCycleOrchestrator:
    """Orchestrates полный цикл самообучения"""

    async def run_cycle(self):
        """Запускает один полный цикл"""

        logger.info("🔄 Starting Virtuous Cycle")

        # PHASE 1: Collect data from 3 user groups

        # From consultants
        consultant_data = await self.collect_consultant_insights()
        await publish_event("cycle.phase1.consultant_data_collected", {
            "audits": len(consultant_data)
        })

        # From organizations
        org_data = await self.collect_org_cases()
        await publish_event("cycle.phase1.org_data_collected", {
            "cases": len(org_data)
        })

        # From donors
        donor_data = await self.collect_donor_feedback()
        await publish_event("cycle.phase1.donor_data_collected", {
            "feedback_count": len(donor_data)
        })

        # PHASE 2: Detect patterns (AI analysis)

        patterns = await self.detect_patterns_from_all_sources(
            consultant_data=consultant_data,
            org_data=org_data,
            donor_data=donor_data
        )

        await publish_event("cycle.phase2.patterns_detected", {
            "patterns_count": len(patterns)
        })

        # PHASE 3: Generate learning materials

        materials = []
        for pattern in patterns:
            # Auto-create case study, training, exercise
            material = await self.generate_learning_material(pattern)
            materials.append(material)

        await publish_event("cycle.phase3.materials_generated", {
            "materials_count": len(materials)
        })

        # PHASE 4: Share knowledge

        # Publish to knowledge library
        for material in materials:
            await knowledge_library.publish(material)

        # Update collective intelligence
        await collective_intelligence.update_from_materials(materials)

        # Notify users
        await notification_service.notify_new_materials(materials)

        await publish_event("cycle.phase4.knowledge_shared", {
            "users_notified": await get_active_user_count()
        })

        # PHASE 5: Improve system code

        code_improvements = []
        for pattern in patterns:
            # Generate code from pattern
            improvement = await code_generator.generate_from_pattern(pattern)
            code_improvements.append(improvement)

        # Apply auto-fixable improvements
        applied = 0
        for improvement in code_improvements:
            if improvement["auto_fixable"]:
                await code_improver.apply(improvement)
                applied += 1

        await publish_event("cycle.phase5.code_improved", {
            "improvements_applied": applied
        })

        # PHASE 6: Measure impact

        impact = await self.measure_cycle_impact()

        await publish_event("cycle.completed", {
            "cycle_id": generate_cycle_id(),
            "patterns_detected": len(patterns),
            "materials_generated": len(materials),
            "code_improvements": applied,
            "impact": impact
        })

        logger.info(f"✅ Virtuous Cycle completed: {len(patterns)} patterns, {len(materials)} materials, {applied} improvements")

        return {
            "status": "completed",
            "next_cycle_scheduled": datetime.now() + timedelta(days=7)
        }
```

**Choreography для непрерывного learning:**

```python
# intelligent-core/event_intelligence/learning_subscribers.py

@subscribe_to("cycle.phase2.patterns_detected")
async def update_ml_models(event: Event):
    """Обновляет ML models когда детектированы новые паттерны"""

    patterns = event.data["patterns"]

    for pattern in patterns:
        # Обновляем соответствующую ML model
        if pattern["domain"] == "bia":
            await bia_ml_model.train_on_pattern(pattern)
        elif pattern["domain"] == "risk":
            await risk_ml_model.train_on_pattern(pattern)

    await publish_event("system.ml.models_updated", {
        "models_count": len(patterns)
    })


@subscribe_to("cycle.completed")
async def schedule_next_cycle(event: Event):
    """Планирует следующий цикл"""

    next_cycle_time = event.data["next_cycle_scheduled"]

    # Ждем 7 дней
    delay_seconds = (next_cycle_time - datetime.now()).total_seconds()
    await asyncio.sleep(delay_seconds)

    # Запускаем новый цикл
    await publish_event("cycle.trigger", {
        "reason": "scheduled",
        "previous_cycle": event.data["cycle_id"]
    })
```

---

## 🎭 CHOREOGRAPHY vs ORCHESTRATION DISTRIBUTION

### System Level (Устойчивость) = CHOREOGRAPHY

**Почему choreography:**
- Resilience (нет single point of failure)
- Fault isolation (сбой одного не роняет всех)
- Scalability (легко добавлять сервисы)

**Примеры:**

```python
# Service health monitoring - CHOREOGRAPHY

@subscribe_to("service.health.check")
async def report_my_health(event: Event):
    """Каждый сервис сам отвечает на health check"""
    health = await check_my_health()
    await publish_event("service.health.report", {
        "service": "bia-service",
        "status": health["status"],
        "uptime": health["uptime"]
    })

# Auto-recovery - CHOREOGRAPHY

@subscribe_to("service.failed")
async def trigger_recovery(event: Event):
    """Каждый сервис сам триггерит recovery"""
    if event.data["service"] == "my-service":
        await self_recover()
        await publish_event("service.recovered", {
            "service": "my-service",
            "recovery_time": recovery_time
        })

# Resource management - CHOREOGRAPHY

@subscribe_to("system.load.high")
async def scale_down_my_resources(event: Event):
    """Каждый сервис сам управляет ресурсами"""
    await reduce_connection_pool()
    await enable_caching()
    await publish_event("service.scaled_down", {
        "service": "my-service"
    })
```

---

### Program Level (Экспертиза) = HYBRID

**Orchestration** для критических workflows (строгий порядок):

```python
# BIA Process - ORCHESTRATION (main path)

class BIAOrchestrator:
    async def run_bia_workflow(self, org_id: str):
        # Step 1: Planning
        plan = await bia_specialist.create_plan(org_id)
        await publish_event("bcm.bia.planning_complete", {...})

        # Step 2: Data Collection
        data = await bia_specialist.collect_data(org_id)
        await publish_event("bcm.bia.data_collected", {...})

        # Step 3: Analysis
        analysis = await bia_specialist.analyze(data)
        await publish_event("bcm.bia.analysis_complete", {...})

        # Step 4: Reporting
        report = await bia_specialist.generate_report(analysis)
        await publish_event("bcm.bia.completed", {...})

        return report
```

**Choreography** для side-effects (независимые реакции):

```python
# Side-effects - CHOREOGRAPHY

@subscribe_to("bcm.bia.completed")
async def save_to_case_library(event: Event):
    """Case Library сохраняет кейс"""
    await case_library.add_case(event.data["bia_plan"])

@subscribe_to("bcm.bia.completed")
async def update_collective_intelligence(event: Event):
    """Collective Intelligence обновляется"""
    await collective.add_to_pool(event.data["bia_plan"])

@subscribe_to("bcm.bia.completed")
async def learn_patterns(event: Event):
    """Event Intelligence учится"""
    await event_intelligence.detect_patterns(event.data["bia_plan"])

@subscribe_to("bcm.bia.completed")
async def notify_donor(event: Event):
    """Notification уведомляет донора"""
    await notification.send_to_donor(event.data["org_id"], "BIA completed")
```

---

## 📊 CONCRETE ARCHITECTURE

### Модули и их Роли:

| Модуль | Уровень | Роль | Choreography/Orchestration |
|--------|---------|------|----------------------------|
| **EventBus** | System | Координация событий | Choreography backbone |
| **Orchestrator** | System + Program | Критические workflows | Orchestration engine |
| **ai-foundation** | Program | Мозг (RAG, ML, Learning) | Choreography (events) |
| **expertise-center** | Program | 12 Tactical Assistants | Orchestration (internal) |
| **collective** | Program | Collective Intelligence | Choreography (events) |
| **community_intelligence** | Program | Learning от users | Choreography (events) |
| **workflow_intelligence** | Program | Case Library + ML | Hybrid |
| **analytics-specialist** | System | Анализ платформы | Choreography (events) |
| **monitoring** | System | Observability | Choreography (events) |

---

## 🚀 IMPLEMENTATION PLAN

### Phase 1: System Level (Устойчивость)
- [ ] BIA для процессов системы
- [ ] Risk Assessment для системы
- [ ] Recovery Plans для системы
- [ ] Chaos Engineering tests

### Phase 2: Program Level (Обучение от 3 групп)
- [ ] Consultant learning loop
- [ ] Organization learning loop (Collective Intelligence)
- [ ] Donor learning loop (Impact dashboards)

### Phase 3: Virtuous Cycle
- [ ] Полный цикл orchestration
- [ ] Auto-generation learning materials
- [ ] Code improvements from patterns

### Phase 4: Integration
- [ ] EventBus 100% integration (DONE ✅)
- [ ] Choreography subscribers для всех событий
- [ ] Orchestrator для критических workflows

---

**Status:** Architecture Complete - Ready for Implementation
**Next:** Start Phase 1 (System Level BIA)
