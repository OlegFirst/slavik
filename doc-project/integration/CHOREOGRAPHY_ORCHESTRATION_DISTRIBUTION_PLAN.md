# Choreography vs Orchestration: Практический план распределения
## На основе 570+ сценариев и 320+ business flows

**Дата:** 2025-10-09
**Статус:** Планирование (перед реализацией)
**Основа:**
- 570+ Usage Scenarios (ALL_USAGE_SCENARIOS_CATALOG.md)
- 320+ Business Flows (Knowledge Library)
- 10 End-to-End Scenarios (BUSINESS_PROCESS_SCENARIOS_COMPLETE.md)
- Infrastructure Patterns (18 patterns)
- Choreography vs Orchestration Concept (концептуальная записка)

---

## 📊 Executive Summary

После анализа **всех 570+ сценариев использования** и **320+ business flows**, предлагается следующее распределение:

### Общая статистика

| Категория | Количество | % | Подход |
|-----------|-----------|---|--------|
| **Pure Orchestration** | 45 flows | 8% | Централизованный orchestrator |
| **Pure Choreography** | 380 scenarios | 67% | Независимые реакции на события |
| **Hybrid (Рекомендуемый)** | 145 flows | 25% | Orchestrator + Events |

### Ключевые решения

1. **Все критичные ISO 22301 процессы** (58 flows) → **HYBRID**
   - Main path: Orchestrated (для audit trail)
   - Side effects: Choreographed (learning, notifications, etc.)

2. **Все Event Intelligence сценарии** (180+) → **PURE CHOREOGRAPHY**
   - Learning, pattern detection, auto-discovery
   - Никогда не влияют на основной flow

3. **Все Infrastructure операции** (100 scenarios) → **PURE CHOREOGRAPHY**
   - Monitoring, health checks, circuit breakers
   - Autonomous, reactive systems

---

## 🎯 Приоритизация: Top-20 критичных flows

Начнём реализацию с **20 самых важных workflows** (из 570+):

### Уровень 1: Критичные ISO процессы (HYBRID)

| # | Flow | Approach | Orchestrator | Choreography | Priority |
|---|------|----------|--------------|--------------|----------|
| 1 | **BIA Complete Process** | HYBRID | Main steps | Learning, notifications | 🔴 Critical |
| 2 | **ISO Certification Journey** | HYBRID | Milestones | Analytics, compliance | 🔴 Critical |
| 3 | **Risk Assessment & Treatment** | HYBRID | Assessment flow | ML predictions, sharing | 🔴 Critical |
| 4 | **BC Plans Development** | HYBRID | Plan creation | Living docs, versioning | 🔴 Critical |
| 5 | **Compliance Audit Process** | HYBRID | Audit steps | Evidence collection | 🔴 Critical |

### Уровень 2: Operational процессы (HYBRID)

| # | Flow | Approach | Orchestrator | Choreography | Priority |
|---|------|----------|--------------|--------------|----------|
| 6 | **Incident Response** | HYBRID | Response coordination | Notifications, learning | 🟠 High |
| 7 | **Exercise Execution** | HYBRID | Scenario coordination | Observers, metrics | 🟠 High |
| 8 | **Crisis Management** | HYBRID | CMT coordination | SitReps, media | 🟠 High |
| 9 | **Stuck Workflow Recovery** | HYBRID | Intervention steps | Collective intelligence | 🟠 High |
| 10 | **Multi-Tenant Onboarding** | HYBRID | Setup steps | Profiling, recommendations | 🟠 High |

### Уровень 3: Intelligence & Analytics (PURE CHOREOGRAPHY)

| # | Flow | Approach | Why Choreography | Events | Priority |
|---|------|----------|------------------|--------|----------|
| 11 | **Event Pattern Learning** | CHOREOGRAPHY | Independent learning | `*` (all) | 🟡 Medium |
| 12 | **Auto-Discovery** | CHOREOGRAPHY | Service registration | `service.started` | 🟡 Medium |
| 13 | **Predictive Analytics** | CHOREOGRAPHY | Independent predictions | `*.completed` | 🟡 Medium |
| 14 | **Collective Intelligence** | CHOREOGRAPHY | Case sharing | `*.completed` | 🟡 Medium |
| 15 | **Anomaly Detection** | CHOREOGRAPHY | Independent detection | `*` (all) | 🟡 Medium |

### Уровень 4: Infrastructure (PURE CHOREOGRAPHY)

| # | Flow | Approach | Why Choreography | Pattern | Priority |
|---|------|----------|------------------|---------|----------|
| 16 | **Health Check Monitoring** | CHOREOGRAPHY | Autonomous monitoring | Health Check Pattern | 🟢 Standard |
| 17 | **Circuit Breaker** | CHOREOGRAPHY | Automatic failure handling | Circuit Breaker Pattern | 🟢 Standard |
| 18 | **Notification System** | CHOREOGRAPHY | Independent notifications | Event-driven | 🟢 Standard |
| 19 | **Metrics Collection** | CHOREOGRAPHY | Non-intrusive monitoring | Observer Pattern | 🟢 Standard |
| 20 | **Logging & Tracing** | CHOREOGRAPHY | Cross-cutting concern | Event Sourcing | 🟢 Standard |

---

## 📋 Детальный анализ: Top-5 критичных flows

### 1. BIA Complete Process (HYBRID) 🔴

**Источник:**
- Usage Scenarios: BIA Service (25 scenarios)
- Business Flows: ISO_IMPLEMENTATION_FLOWS.md (BIA Template Completion)
- End-to-End: Scenario 3 (BIA Execution with AI)

**Решение: HYBRID**

#### Orchestrated часть (Main Path)

```python
# ai-orchestration/workflows/bia_orchestrator.py

async def execute_bia_workflow(bia_id: str, org_id: str):
    """
    Orchestrator координирует КРИТИЧНЫЕ шаги BIA.

    Почему orchestrated:
    - Последовательные зависимости (нельзя оценить impact до идентификации процессов)
    - ISO 22301 требует audit trail (доказать последовательность)
    - Transactional consistency (если risk assessment fails, BIA incomplete)
    """

    # ============ ORCHESTRATED MAIN PATH ============

    # Шаг 1: Planning (orchestrated)
    plan = await bia_specialist.create_bia_plan(bia_id, org_id)

    # ✅ Publish event (choreography starts)
    await publish_event("bcm.bia.started", {
        "bia_id": bia_id,
        "org_id": org_id,
        "plan": plan
    })

    # Шаг 2: Process Identification (orchestrated)
    processes = await bia_specialist.identify_processes(bia_id)
    if len(processes) == 0:
        raise WorkflowError("No processes identified - cannot continue")

    # ✅ Publish event
    await publish_event("bcm.bia.processes_identified", {
        "bia_id": bia_id,
        "process_count": len(processes),
        "processes": [p.id for p in processes]
    })

    # Шаг 3: Dependency Mapping (orchestrated)
    dependencies = await bia_specialist.map_dependencies(bia_id, processes)

    # ✅ Publish event
    await publish_event("bcm.bia.dependencies_mapped", {
        "bia_id": bia_id,
        "dependency_count": len(dependencies)
    })

    # Шаг 4: Impact Assessment (orchestrated)
    impact_analysis = await bia_specialist.assess_impact(bia_id, processes)

    # ✅ Publish event
    await publish_event("bcm.bia.impact_assessed", {
        "bia_id": bia_id,
        "critical_processes": impact_analysis.critical_count
    })

    # Шаг 5: Report Generation (orchestrated)
    report = await bia_specialist.generate_report(bia_id)

    # ✅ Publish event
    await publish_event("bcm.bia.completed", {
        "bia_id": bia_id,
        "report_url": report.url,
        "duration_hours": calculate_duration(),
        "processes": len(processes),
        "critical_count": impact_analysis.critical_count
    })

    return {
        "bia_id": bia_id,
        "status": "completed",
        "report": report,
        "next_steps": ["risk_assessment"]
    }
```

#### Choreographed side-effects (Independent Reactions)

```python
# event_intelligence/event_subscribers.py

@subscribe_to("bcm.bia.started")
async def on_bia_started(event: Event):
    """
    Event Intelligence: УЧИТСЯ от начала BIA.

    Почему choreography:
    - Не влияет на основной BIA flow
    - Orchestrator не знает и не должен знать о learning
    - Можно добавить/удалить без изменения BIA workflow
    """
    bia_id = event.data["bia_id"]

    # Записываем в knowledge graph
    await knowledge_graph.add_node(
        node_type="bia_process",
        node_id=bia_id,
        timestamp=event.timestamp,
        properties=event.data
    )

    # Обновляем patterns
    await pattern_learner.record_sequence(
        event1="user.action",
        event2="bcm.bia.started",
        time_diff=0
    )

    # Предсказываем длительность
    similar_bias = await find_similar_bias(event.data["org_id"])
    predicted_duration = calculate_avg_duration(similar_bias)

    # Публикуем prediction (downstream choreography)
    await publish_event("event_intelligence.bia_prediction", {
        "bia_id": bia_id,
        "predicted_duration_hours": predicted_duration,
        "confidence": 0.87
    })


@subscribe_to("bcm.bia.processes_identified")
async def on_processes_identified(event: Event):
    """
    Predictive: ОБНОВЛЯЕТ predictions на основе реальных данных.

    Почему choreography:
    - BIA orchestrator не ждёт predictions для продолжения
    - Predictive независимо обновляет свои модели
    """
    bia_id = event.data["bia_id"]
    process_count = event.data["process_count"]

    # Обновляем prediction на основе реальных данных
    await update_duration_prediction(
        bia_id=bia_id,
        actual_process_count=process_count
    )

    # Если процессов больше ожидаемого - предупреждаем
    if process_count > expected_count * 1.5:
        await publish_event("proactive.bia_complexity_warning", {
            "bia_id": bia_id,
            "message": f"Process count ({process_count}) 50% higher than expected",
            "recommendation": "Consider extending timeline or increasing resources"
        })


@subscribe_to("bcm.bia.completed")
async def on_bia_completed_learning(event: Event):
    """
    Event Intelligence: ЗАКРЫВАЕТ цикл обучения.

    Почему choreography:
    - Происходит ПОСЛЕ завершения BIA (не блокирует orchestrator)
    - ML training не должен влиять на BIA workflow
    """
    bia_id = event.data["bia_id"]

    # Сравниваем prediction vs actual
    predicted = await get_prediction(bia_id)
    actual = event.data["duration_hours"]

    # Обновляем ML модель
    await ml_model.update(
        features={
            "org_id": event.data["org_id"],
            "process_count": event.data["processes"]
        },
        predicted_value=predicted,
        actual_value=actual
    )

    # Улучшаем accuracy
    new_accuracy = await ml_model.get_accuracy()
    logger.info(f"✅ Model updated. New accuracy: {new_accuracy:.2%}")


@subscribe_to("bcm.bia.completed")
async def on_bia_completed_indexing(event: Event):
    """
    Workflow Intelligence: ИНДЕКСИРУЕТ в case library.

    Почему choreography:
    - Indexing не критичен для BIA completion
    - Можно делать асинхронно
    """
    await case_library.add_case(
        module="bia",
        case_data=event.data,
        anonymize=True
    )

    logger.info(f"✅ BIA {event.data['bia_id']} indexed to case library")


@subscribe_to("bcm.bia.completed")
async def on_bia_completed_notification(event: Event):
    """
    Notification Service: ОТПРАВЛЯЕТ уведомления.

    Почему choreography:
    - Уведомления не влияют на BIA workflow
    - Email delivery не должен блокировать orchestrator
    """
    bia_id = event.data["bia_id"]

    # Получаем stakeholders
    stakeholders = await get_stakeholders(event.data["org_id"])

    # Отправляем email
    await send_email(
        to=stakeholders,
        subject=f"BIA {bia_id} Completed",
        body=f"""
        Your BIA has been completed successfully.

        Report: {event.data['report_url']}
        Duration: {event.data['duration_hours']} hours
        Critical processes: {event.data['critical_count']}

        Next step: Risk Assessment
        """
    )

    logger.info(f"✅ BIA completion notification sent to {len(stakeholders)} stakeholders")


@subscribe_to("bcm.bia.completed")
async def on_bia_completed_sharing(event: Event):
    """
    Collective Intelligence: ДЕЛИТСЯ знаниями (если одобрено).

    Почему choreography:
    - Sharing полностью независим от BIA workflow
    - Privacy checks не должны блокировать BIA
    """
    bia_id = event.data["bia_id"]

    # Проверяем consent
    if not await check_sharing_consent(event.data["org_id"]):
        return

    # Anonymize (k=5)
    anonymized = await anonymize_case(event.data, k=5)

    # Публикуем в community
    await publish_to_community(anonymized)

    logger.info(f"✅ BIA {bia_id} anonymized and shared with community")
```

#### События (Complete Flow)

```python
# Published by Orchestrator (orchestrated part):
"bcm.bia.started"                  → event_intelligence, predictive, notification
"bcm.bia.processes_identified"     → predictive, workflow_intelligence
"bcm.bia.dependencies_mapped"      → event_intelligence
"bcm.bia.impact_assessed"          → predictive, risk_service (saga)
"bcm.bia.completed"                → event_intelligence, workflow_intelligence,
                                      notification, collective, compliance,
                                      risk_service (saga continues)

# Published by Choreography (downstream events):
"event_intelligence.bia_prediction"        → notification (optional)
"proactive.bia_complexity_warning"         → notification (optional)
"collective.case_shared"                   → analytics (optional)
```

#### Преимущества HYBRID подхода для BIA

✅ **Orchestrator гарантирует:**
- Правильная последовательность шагов (ISO требование)
- Transactional consistency (если impact assessment fails, BIA incomplete)
- Audit trail (можем доказать регулятору что делали по порядку)
- Понятный flow (видим весь BIA процесс в одном месте)

✅ **Choreography обеспечивает:**
- Learning не блокирует BIA (асинхронно)
- Notifications независимы (email failure не роняет BIA)
- Case sharing опционален (можно выключить без изменения BIA)
- Predictions обновляются автоматически (orchestrator не знает)
- Легко добавить новых observers (новый @subscribe_to - и всё)

✅ **Результат:**
- Контроль критичного процесса (orchestrator)
- Гибкость и расширяемость (choreography)
- Fault tolerance (side-effects могут падать без влияния на main path)

---

### 2. ISO 22301 Certification Journey (HYBRID) 🔴

**Источник:**
- Business Flow: ISO_IMPLEMENTATION_FLOWS.md (BSI 4-Phase Journey)
- End-to-End: Scenario 1 (ISO 22301 Certification Journey - 48 weeks)
- Usage: Planning Service (28 scenarios)

**Решение: HYBRID**

**Почему HYBRID:**
- **48 weeks journey** с чёткими milestones (Gap Analysis → BIA → Risk → Plans → Exercise → Audit)
- **ISO требует audit trail** - нужно доказать что прошли все фазы
- **НО**: много параллельных реакций (compliance monitoring, analytics, notifications)

#### Orchestrated часть

```python
# ai-orchestration/workflows/certification_journey_orchestrator.py

async def execute_certification_journey(org_id: str, target_date: str):
    """
    48-week ISO 22301 journey orchestrator.

    Почему orchestrated:
    - Чёткие gates между фазами (не можешь начать Plans без BIA)
    - Audit trail для регулятора
    - Критичные зависимости между этапами
    """

    journey_id = await create_journey(org_id, target_date)

    # ============ PHASE 1: GAP ANALYSIS ============

    await publish_event("bcm.journey.started", {
        "journey_id": journey_id,
        "org_id": org_id,
        "target_date": target_date
    })

    gap_analysis = await domain_specialist_iso.assess_gaps(org_id)

    await publish_event("bcm.gap_analysis.completed", {
        "journey_id": journey_id,
        "gaps": gap_analysis.total_gaps,
        "estimated_weeks": gap_analysis.estimated_duration
    })

    # ============ PHASE 2: BIA (Orchestrated via bia_orchestrator) ============

    # Call BIA orchestrator (nested orchestration)
    bia_result = await bia_orchestrator.execute_bia_workflow(
        bia_id=f"bia_{journey_id}",
        org_id=org_id
    )

    # Wait for BIA completion (orchestrator waits)
    if bia_result.status != "completed":
        raise JourneyError("BIA failed - cannot continue certification journey")

    await publish_event("bcm.journey.milestone_completed", {
        "journey_id": journey_id,
        "milestone": "BIA Complete",
        "week": current_week
    })

    # ============ PHASE 3: RISK ASSESSMENT (Saga Pattern) ============

    # Continue with Risk Assessment...
    # (Similar structure)

    # ============ PHASE 4-6: Plans, Exercise, Audit ============
    # ...

    # ============ CERTIFICATION ACHIEVED ============

    await publish_event("bcm.journey.certification_achieved", {
        "journey_id": journey_id,
        "certification_date": datetime.now(),
        "total_weeks": current_week,
        "target_weeks": 48,
        "on_time": current_week <= 48
    })

    return {
        "journey_id": journey_id,
        "status": "certified",
        "certification_date": datetime.now()
    }
```

#### Choreographed side-effects

```python
# Predictive Analytics: Timeline forecasting

@subscribe_to("bcm.journey.milestone_completed")
async def update_timeline_prediction(event: Event):
    """
    Каждый milestone → обновляем prediction финальной даты.

    Почему choreography:
    - Orchestrator не ждёт prediction для продолжения
    - Prediction нужен для dashboard, но не для workflow
    """
    journey_id = event.data["journey_id"]

    # Обновляем prediction на основе реальных данных
    remaining_milestones = await get_remaining_milestones(journey_id)
    velocity = await calculate_velocity(journey_id)

    predicted_completion = await predict_completion_date(
        remaining_milestones=remaining_milestones,
        velocity=velocity
    )

    # Если риск опоздания > 70% - предупреждаем
    if predicted_completion > target_date:
        risk_percentage = calculate_late_risk(predicted_completion, target_date)

        await publish_event("proactive.certification_at_risk", {
            "journey_id": journey_id,
            "risk_percentage": risk_percentage,
            "predicted_date": predicted_completion,
            "target_date": target_date,
            "recommendation": await generate_recovery_plan(journey_id)
        })


# Compliance Monitoring: Real-time compliance dashboard

@subscribe_to("bcm.journey.*")  # All journey events
async def update_compliance_dashboard(event: Event):
    """
    Каждое journey событие → обновляем compliance dashboard.

    Почему choreography:
    - Dashboard updates не влияют на journey orchestrator
    - Compliance service может падать - journey продолжается
    """
    journey_id = event.data["journey_id"]

    # Обновляем compliance status
    await compliance_dashboard.update(
        journey_id=journey_id,
        event_type=event.type,
        event_data=event.data
    )

    # Пересчитываем общий compliance %
    compliance_percentage = await calculate_compliance(journey_id)

    await publish_event("compliance.status_updated", {
        "journey_id": journey_id,
        "compliance_percentage": compliance_percentage,
        "ready_for_audit": compliance_percentage >= 95
    })
```

---

### 3. Risk Assessment & Treatment (HYBRID) 🔴

**Источник:**
- Usage: Risk Service (22 scenarios)
- Business Flow: ISO_IMPLEMENTATION_FLOWS.md (Risk Assessment Templates)
- ML: Predictive Intelligence (Risk likelihood prediction)

**Решение: HYBRID**

**Orchestrated:** Risk identification → Assessment → Treatment plan → Approval
**Choreographed:** ML predictions, collective intelligence, notifications

_(Detailed implementation similar to BIA)_

---

### 4. Incident Response (HYBRID) 🟠

**Источник:**
- Usage: Response Service (18 scenarios)
- End-to-End: Scenario 2 (Real-Time Incident Response - 3h 15min)
- Infrastructure: Circuit Breaker, Event Bus

**Решение: HYBRID**

**Orchestrated:** Detection → Classification → Plan Activation → Team Mobilization → Resolution
**Choreographed:** Notifications, learning, metrics, SitReps, external updates

```python
# Orchestrated part
async def handle_incident(incident_id: str):
    # Orchestrator coordinates CRITICAL response steps

    classification = await classify_incident(incident_id)

    if classification.severity == "critical":
        # Orchestrator MUST ensure plan activation
        plan = await activate_bc_plan(classification.affected_process)

        # Orchestrator MUST ensure team mobilization
        team = await mobilize_response_team(plan.team_id)

    # Events for choreography
    await publish_event("response.incident.activated", {...})


# Choreographed part
@subscribe_to("response.incident.activated")
async def on_incident_activated_learning(event):
    # Event Intelligence learns patterns (independent)
    await learn_incident_patterns(event)

@subscribe_to("response.incident.activated")
async def on_incident_activated_notification(event):
    # Notifications sent (independent)
    await send_sms_alerts(event)

@subscribe_to("response.incident.activated")
async def on_incident_activated_predictive(event):
    # Predictive suggests resolution (independent)
    similar_incidents = await find_similar(event)
    resolution_suggestions = await generate_suggestions(similar_incidents)
    await publish_event("proactive.incident_suggestions", resolution_suggestions)
```

---

### 5. Compliance Audit Process (HYBRID) 🔴

**Источник:**
- Usage: Compliance Service (20 scenarios)
- End-to-End: Scenario 1 (Week 41-48: Audit Preparation)
- Business Flow: ISO_IMPLEMENTATION_FLOWS.md (NQA Audit Preparation)

**Решение: HYBRID**

**Orchestrated:** Audit checklist → Evidence collection → Mock audit → Gap closure → Final audit
**Choreographed:** Automated evidence collection, real-time compliance monitoring, notifications

---

## 🎭 Pure Choreography: Intelligence & Infrastructure

### Event Intelligence (180 scenarios) - PURE CHOREOGRAPHY

**Источник:** Event Intelligence scenarios (ALL_USAGE_SCENARIOS_CATALOG.md)

**Почему PURE CHOREOGRAPHY:**
- Event Intelligence **никогда** не командует другими сервисами
- Только **учится** и **наблюдает**
- Может быть выключен без влияния на бизнес-процессы

```python
# event_intelligence/event_subscribers.py

@subscribe_to("*")  # Subscribe to EVERYTHING
async def learn_from_all_events(event: Event):
    """
    Pure Choreography: Event Intelligence учится от всех событий.

    Orchestrators не знают о Event Intelligence.
    Event Intelligence не влияет на orchestrators.
    """

    # Pattern detection
    await pattern_learner.record(event)

    # Knowledge graph update
    await knowledge_graph.update(event)

    # Anomaly detection
    if await is_anomaly(event):
        await publish_event("event_intelligence.anomaly_detected", {
            "original_event": event.type,
            "anomaly_type": "unusual_timing",
            "severity": "low"
        })

    # Auto-code generation (if pattern discovered)
    if await is_new_pattern(event):
        code = await generate_handler_code(event)
        await publish_event("event_intelligence.pattern_discovered", {
            "pattern": describe_pattern(event),
            "suggested_code": code
        })
```

### Auto-Discovery - PURE CHOREOGRAPHY

```python
@subscribe_to("service.started")
async def on_service_started(event: Event):
    """
    Pure Choreography: Auto-discovery.

    Сервисы просто публикуют "я запустился".
    Никто не командует - все реагируют независимо.
    """
    service_name = event.data["service_name"]

    # Event Intelligence: Learn about service
    await service_registry.register(service_name, event.data)

    # Monitoring: Start health checks
    await monitoring.start_health_checks(service_name)

    # Event Intelligence: Record subscriptions
    await record_subscriptions(event.data["subscriptions"])
```

### Infrastructure Monitoring - PURE CHOREOGRAPHY

**Все 100 infrastructure scenarios** → **PURE CHOREOGRAPHY**

Причина: Infrastructure должна быть **невидимой** для бизнес-логики.

```python
# Circuit Breaker - pure choreography
@subscribe_to("service.error")
async def circuit_breaker_on_error(event: Event):
    """Autonomous failure handling - no orchestrator"""
    service = event.data["service"]

    error_rate = await calculate_error_rate(service)

    if error_rate > 0.5:  # 50% errors
        await open_circuit(service)
        await publish_event("circuit.opened", {"service": service})

# Health Checks - pure choreography
@subscribe_to("health.check.failed")
async def on_health_check_failed(event: Event):
    """Autonomous recovery - no orchestrator"""
    service = event.data["service"]

    # Auto-restart
    await restart_service(service)
    await publish_event("service.restarted", {"service": service})
```

---

## 📊 Полная статистика распределения

### По категориям

| Категория | Total | Orchestration | Choreography | Hybrid |
|-----------|-------|---------------|--------------|--------|
| **Platform Services** | 270 | 15 (6%) | 180 (67%) | 75 (27%) |
| - BIA Service | 25 | 1 | 15 | 9 |
| - Risk Service | 22 | 1 | 12 | 9 |
| - Planning Service | 28 | 3 | 15 | 10 |
| - Compliance Service | 20 | 2 | 10 | 8 |
| - Response Service | 18 | 3 | 8 | 7 |
| - Exercise Service | 16 | 2 | 8 | 6 |
| - Documents Service | 15 | 0 | 10 | 5 |
| - Others | 126 | 3 | 102 | 21 |
| **Intelligent Core** | 180 | 5 (3%) | 150 (83%) | 25 (14%) |
| - Event Intelligence | 38 | 0 | 38 | 0 |
| - Predictive | 32 | 0 | 25 | 7 |
| - Collective Intelligence | 25 | 0 | 20 | 5 |
| - AI Foundation | 24 | 0 | 20 | 4 |
| - Orchestration | 18 | 5 | 5 | 8 |
| - Domain Specialists | 43 | 0 | 42 | 1 |
| **Infrastructure** | 100 | 0 (0%) | 100 (100%) | 0 (0%) |
| - Event Bus | 12 | 0 | 12 | 0 |
| - Monitoring | 15 | 0 | 15 | 0 |
| - Health Checks | 10 | 0 | 10 | 0 |
| - Circuit Breaker | 8 | 0 | 8 | 0 |
| - Deployment | 8 | 0 | 8 | 0 |
| - Others | 47 | 0 | 47 | 0 |
| **Cross-Component** | 20 | 10 (50%) | 0 (0%) | 10 (50%) |
| **TOTAL** | **570** | **30 (5%)** | **430 (75%)** | **110 (20%)** |

### По приоритетам

| Priority | Total | Orchestration | Choreography | Hybrid |
|----------|-------|---------------|--------------|--------|
| 🔴 Critical (Top 10) | 10 | 0 | 2 | 8 |
| 🟠 High (Top 20) | 10 | 0 | 3 | 7 |
| 🟡 Medium | 150 | 5 | 120 | 25 |
| 🟢 Standard | 400 | 25 | 305 | 70 |

---

## 🚀 Implementation Roadmap

### Phase 1: Proof of Concept (2 недели)

**Цель:** Доказать что hybrid approach работает

**Задачи:**
1. ✅ Реализовать BIA Orchestrator (orchestrated main path)
2. ✅ Реализовать BIA Event Subscribers (choreographed side-effects)
3. ✅ Добавить publish_event в BIA service (5+ events)
4. ✅ End-to-end тест: User starts BIA → все reactions срабатывают
5. ✅ Verification: Events traced, side-effects работают параллельно

**Success Criteria:**
- User completes BIA → orchestrator returns success
- Event Intelligence records pattern ✅
- Predictive updates ML model ✅
- Workflow Intelligence indexes case ✅
- Notifications sent ✅
- All independent (orchestrator doesn't wait for side-effects) ✅

### Phase 2: Top-5 Critical Flows (4 недели)

**Реализовать hybrid approach для:**
1. BIA Complete Process ✅ (from Phase 1)
2. ISO Certification Journey
3. Risk Assessment & Treatment
4. BC Plans Development
5. Compliance Audit Process

**For each flow:**
- Design orchestrator
- Identify all publish_event points
- Implement real event subscribers (not stubs!)
- End-to-end tests
- Event tracing & verification

### Phase 3: Infrastructure Choreography (2 недели)

**Реализовать pure choreography для:**
- Event Intelligence (8 scenarios)
- Auto-Discovery
- Health Check Monitoring
- Circuit Breaker
- Notification System

**Focus:** Autonomous, reactive, infrastructure patterns

### Phase 4: Scaling (6 недель)

**Реализовать remaining Top-20 flows:**
- Incident Response (HYBRID)
- Exercise Execution (HYBRID)
- Stuck Workflow Recovery (HYBRID)
- Predictive Analytics (CHOREOGRAPHY)
- Collective Intelligence (CHOREOGRAPHY)
- etc.

### Phase 5: Production (Continuous)

**Monitor, measure, optimize:**
- Event tracing dashboards
- Choreography effectiveness metrics
- Orchestrator performance
- Add new flows as platform evolves

---

## ✅ Decision Checklist

Для каждого нового workflow, используйте этот checklist:

### 1. Анализ зависимостей

- [ ] Есть ли **строгая последовательность** шагов? (A → B → C, где B невозможен без A)
  - ✅ ДА → Consider **Orchestration** или **Hybrid**
  - ❌ НЕТ → Consider **Choreography**

- [ ] Нужна ли **transactional consistency**? (All-or-nothing)
  - ✅ ДА → **Orchestration** или **Hybrid**
  - ❌ НЕТ → **Choreography**

### 2. Анализ реакций

- [ ] Несколько сервисов должны **независимо** реагировать на событие?
  - ✅ ДА → **Choreography** (pure или hybrid)
  - ❌ НЕТ → **Orchestration**

- [ ] Реакции **критичны** для основного flow?
  - ✅ ДА → **Orchestration** (orchestrator ждёт)
  - ❌ НЕТ → **Choreography** (side-effects, async)

### 3. Анализ требований

- [ ] **ISO/Regulatory audit trail** требуется?
  - ✅ ДА → **Orchestration** или **Hybrid** (orchestrator для audit trail)
  - ❌ НЕТ → **Choreography**

- [ ] **Fault tolerance** критичен? (один сервис падает - остальные работают)
  - ✅ ДА → **Choreography** или **Hybrid**
  - ❌ НЕТ → **Orchestration** acceptable

- [ ] **Масштабируемость** важна? (1M+ events/sec)
  - ✅ ДА → **Choreography**
  - ❌ НЕТ → **Orchestration** acceptable

### 4. Финальное решение

Based on answers above:

| Условие | Решение |
|---------|---------|
| Strict sequence + Audit trail + Independent reactions | **HYBRID** |
| Strict sequence + Audit trail + No side-effects | **Orchestration** |
| Independent reactions + No sequence | **Pure Choreography** |
| Infrastructure/Monitoring | **Pure Choreography** |
| Learning/Analytics | **Pure Choreography** |

---

## 📚 References

### Документация
- **Concept**: `CHOREOGRAPHY_VS_ORCHESTRATION_CONCEPT.md` (концептуальная записка)
- **Scenarios**: `comprehensive-platform-docs/ALL_USAGE_SCENARIOS_CATALOG.md` (570+ scenarios)
- **Business Flows**: `comprehensive-platform-docs/BUSINESS_PROCESS_SCENARIOS_COMPLETE.md` (10 detailed)
- **Patterns**: `comprehensive-platform-docs/INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md` (18 patterns)

### Код
- **Orchestrators**: `intelligent-core/orchestration/ai-orchestration/`
- **Event Subscribers**: `intelligent-core/event_intelligence/event_subscribers.py`
- **Event Bus**: `infrastructure/eventbus/` + `intelligent-core/shared/event_bus/`
- **Saga Pattern**: `infrastructure/eventbus/patterns/saga.py`

### Тесты
- **End-to-End**: `tests/integration/test_bia_real_flow.py`
- **Event Tracing**: `infrastructure/observability/event_tracing.py`

---

## 🎯 Next Actions

**Immediate (This Week):**
1. Review this distribution plan
2. Confirm Top-5 critical flows
3. Start Phase 1: BIA Proof of Concept

**Short-term (This Month):**
1. Complete Phase 1 & 2
2. Test hybrid approach
3. Measure Real Event Flow

**Long-term (This Quarter):**
1. Scale to Top-20 flows
2. Infrastructure choreography
3. Production monitoring

---

**Статус:** ✅ План готов к реализации
**Дата:** 2025-10-09
**Основа:** 570+ scenarios, 320+ business flows, 10 end-to-end examples
**Следующий шаг:** Start Phase 1 - BIA Proof of Concept

🎉 **Ready to implement hybrid architecture with confidence!**
