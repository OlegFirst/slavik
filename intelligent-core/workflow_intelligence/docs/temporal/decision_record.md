# ADR-001: Temporal Cloud + EventBus для оркестрации процессов

**Status:** ✅ Accepted
**Date:** 2025-10-06
**Deciders:** Architecture Team
**Related:** TEMPORAL_EVENTBUS_ARCHITECTURE.md, FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md

---

## Context

AI-Powered BCM Platform требует оркестрации сложных бизнес-процессов (BIA, Risk Assessment, Incident Response, Compliance Audit, etc.). Эти процессы характеризуются:

- **Долгая продолжительность:** долгоживущие
- **Human-in-the-loop:** необходимость approvals от stakeholders
- **Критичность:** процессы не могут быть потеряны при сбоях
- **Multi-stage:** последовательность шагов с условной логикой
- **External dependencies:** интеграция с внешними API
- **Learning:** необходимость сохранения и анализа выполненных процессов

Одновременно платформа нуждается в:
- **Inter-service communication:** взаимодействие между микросервисами
- **Real-time updates:** уведомления для UI
- **Notifications:** email/SMS/push уведомления
- **Audit trail:** логирование всех событий
- **Loose coupling:** независимое развитие сервисов

---

## Decision

**Решение:** Использовать **ОБА** инструмента:

### 1. Temporal Cloud - для workflow orchestration

**Для чего:**
- ✅ Долгоживущие бизнес-процессы (BIA, Risk, Incident Response, etc.)
- ✅ Persistent state management
- ✅ Human approvals (wait conditions)
- ✅ Retry logic при сбоях
- ✅ Governance checkpoints
- ✅ Case Library (self-learning)

**~10-15 core workflows:**
1. BIA Workflow
2. Risk Assessment Workflow
3. Incident Response Workflow
4. Compliance Audit Workflow (recurring)
5. DR Testing Workflow (recurring)
6. Crisis Management Workflow
7. Supply Chain Risk Assessment
8. Training & Exercise Program (recurring)
9. BC Plan Update Workflow
10. Change Management Workflow

### 2. EventBus (RabbitMQ) - для integration

**Для чего:**
- ✅ Inter-service communication
- ✅ Fire-and-forget notifications
- ✅ Broadcasting (1 → N consumers)
- ✅ Real-time updates для UI
- ✅ Audit trail
- ✅ Loose coupling между сервисами

**Events публикуемые workflows:**
- `bia.started`, `bia.data_collected`, `bia.completed`
- `incident.detected`, `incident.escalated`, `incident.resolved`
- `compliance.audit_started`, `compliance.audit_completed`
- etc.

### 3. Integration Pattern

**Temporal orchestrates + EventBus integrates:**

```python
@workflow.defn
class BIAWorkflow:
    @workflow.run
    async def run(self, org_id: str):
        # Temporal: orchestration
        data = await workflow.execute_activity(collect_data, org_id)

        # EventBus: notification (via activity)
        await workflow.execute_activity(
            publish_event,
            "bia.data_collected",
            {"org_id": org_id, "progress": "40%"}
        )

        # Temporal: analysis
        analysis = await workflow.execute_activity(analyze_data, data)

        # EventBus: trigger other services
        await workflow.execute_activity(
            publish_event,
            "bia.analysis_completed",
            analysis
        )
```

**Consumers (independent services):**

```python
# Notification Service
@eventbus.subscribe("bia.completed")
async def send_notification(event):
    await email_service.send(event)

# Dashboard Service
@eventbus.subscribe("bia.data_collected")
async def update_dashboard(event):
    await websocket.broadcast(event)
```

---

## Alternatives Considered

### Alternative 1: ❌ Только Temporal (без EventBus)

**Pros:**
- Единый инструмент
- Меньше complexity
- Все в Temporal UI

**Cons:**
- ❌ **Дорого:** каждый notification = activity execution = cost
- ❌ **Tight coupling:** Temporal workflow должен знать обо ВСЕХ consumers
- ❌ **Сложность добавления новых consumers:** нужно изменять workflow code
- ❌ **Real-time updates проблематичны:** Temporal не для low-latency messaging
- ❌ **Broadcasting сложен:** нужно явно вызывать каждый consumer

**Пример проблемы:**

```python
# ❌ ПЛОХО: Temporal для всего
@workflow.defn
class BIAWorkflow:
    @workflow.run
    async def run(self, org_id: str):
        # ... workflow logic ...

        # Нужно явно вызвать КАЖДЫЙ consumer
        await workflow.execute_activity(send_email_notification)
        await workflow.execute_activity(send_sms_notification)
        await workflow.execute_activity(update_dashboard)
        await workflow.execute_activity(log_to_audit)
        await workflow.execute_activity(update_metrics)
        await workflow.execute_activity(notify_slack)
        # ... добавился новый consumer? Меняем workflow!

        # Cost: 6+ activities на каждый BIA workflow
        # Tight coupling: workflow знает обо всех consumers
```

**Verdict:** ❌ Rejected - дорого и tight coupling

---

### Alternative 2: ❌ Только EventBus (без Temporal)

**Pros:**
- Дешево
- Loose coupling
- Простой broadcasting

**Cons:**
- ❌ **Нет persistent state:** при крэше процесс потерян
- ❌ **Нет orchestration:** сложно управлять последовательностью шагов
- ❌ **Нет human approvals:** EventBus не умеет ждать
- ❌ **Нет retry logic для процессов:** только для отдельных messages
- ❌ **Нет visibility:** сложно понять где процесс сейчас

**Пример проблемы:**

```python
# ❌ ПЛОХО: EventBus для долгого процесса
# Day 1: Start BIA
await eventbus.publish("bia.start", {"org_id": org_id})

# Service A (listener)
@eventbus.subscribe("bia.start")
async def on_bia_start(event):
    data = await collect_data(event["org_id"])
    await eventbus.publish("bia.data_collected", data)

# Service B (listener)
@eventbus.subscribe("bia.data_collected")
async def on_data_collected(event):
    analysis = await analyze(event["data"])
    await eventbus.publish("bia.analysis_done", analysis)

# 🔥 ПРОБЛЕМЫ:
# 1. Сервис A упал после collect_data → процесс потерян
# 2. Где state? Как понять на каком этапе BIA?
# 3. Approval от человека? Нет механизма
# 4. Retry если external API failed? Нет
# 5. История выполнения? Только logs
```

**Verdict:** ❌ Rejected - нет orchestration и reliability

---

### Alternative 3: ❌ Custom orchestrator на EventBus

**Idea:** Написать свой orchestrator поверх EventBus (saga pattern вручную)

**Pros:**
- Контроль над implementation
- Использует EventBus

**Cons:**
- ❌ **Reinventing the wheel:** Temporal уже реализует все это
- ❌ **Complexity:** нужно реализовать state management, retry logic, timeouts, etc.
- ❌ **Maintenance:** свой код нужно поддерживать
- ❌ **No UI:** нужно писать свой dashboard
- ❌ **Testing:** нужно тестировать edge cases (crashing, timeouts, etc.)
- ❌ **Time to market:** месяцы разработки вместо быстрой интеграции

**Estimate:**
- Temporal integration: быстрая интеграция
- Custom orchestrator: 2-3 месяца + ongoing maintenance

**Verdict:** ❌ Rejected - не имеет смысла reinventing the wheel

---

### Alternative 4: ✅ Temporal + EventBus ВМЕСТЕ

**Pros:**
- ✅ **Best of both worlds:** orchestration + integration
- ✅ **Temporal:** reliability, state management, orchestration
- ✅ **EventBus:** loose coupling, broadcasting, real-time
- ✅ **Cost-effective:** Temporal только для core processes (~10-15)
- ✅ **Flexible:** легко добавлять новых consumers
- ✅ **Visibility:** Temporal UI + Event logs
- ✅ **Proven pattern:** используется в production (Uber, Netflix, etc.)

**Cons:**
- ⚠️ **Два инструмента:** нужно поддерживать оба
- ⚠️ **Complexity:** integration layer между ними

**Mitigation:**
- Integration layer простой (activity `publish_event`)
- Оба инструмента managed (Temporal Cloud, CloudAMQP)
- Четкое разделение ответственности

**Verdict:** ✅ **ACCEPTED** - оптимальный баланс

---

## Decision Rationale

### Why Temporal + EventBus?

**1. Cost optimization:**
- Temporal: только ~10-15 core workflows (~1000 executions/month)
- EventBus: тысячи events/day (cheap)
- **Result:** $200-500/month вместо $2000-3000/month (если все через Temporal)

**2. Reliability где критично:**
- BIA долгоживущий процесс → НЕ может быть потерян → **Temporal**
- Email notification → fire-and-forget → **EventBus**

**3. Flexibility:**
- Добавить новый notification consumer → просто subscribe к event
- Не нужно менять workflow code

**4. Performance:**
- Temporal: для долгих процессов (latency не критична)
- EventBus: для real-time updates (low latency)

**5. Proven pattern:**
- Airbnb, Uber, Netflix используют такой же pattern
- Best practices от индустрии

---

## Implementation Plan

### Phase 0: ✅ DONE (2-3 часа)
- [x] Temporal Cloud setup
- [x] Connection tested
- [x] Sample workflow executed

### Phase 1: Infrastructure (4-6 часов)
- [ ] RabbitMQ setup (CloudAMQP / self-hosted)
- [ ] EventBus client library (`shared/eventbus/`)
- [ ] Integration: Temporal activity → EventBus publish

### Phase 2: Workflow Intelligence Engine 
- [ ] Phase 2.1: Core Workflow Engine (BIA Workflow на Temporal)
- [ ] Phase 2.2: Case Library (self-learning)
- [ ] Phase 2.3: Governance System
- [ ] Phase 2.4: Production testing

### Phase 3: Platform Services 
- [ ] EventBus consumers в каждом сервисе
- [ ] Notification Service (subscribe to *.completed)
- [ ] Dashboard Service (subscribe to *.progress)
- [ ] Audit Service (subscribe to *.*)

---

## Consequences

### Positive:

**✅ Reliability:**
- Temporal гарантирует выполнение critical processes
- State persisted в Temporal Cloud

**✅ Scalability:**
- Temporal Workers масштабируются горизонтально
- EventBus consumers масштабируются независимо

**✅ Flexibility:**
- Новые consumers добавляются через EventBus
- Workflow logic не меняется

**✅ Visibility:**
- Temporal UI - полная история workflows
- RabbitMQ Management UI - мониторинг очередей
- Audit trail через EventBus events

**✅ Learning:**
- Case Library собирает все завершенные workflows
- AI learns from patterns

**✅ Cost-effective:**
- Temporal только для core processes (~$200-500/month)
- EventBus дешевый (managed или self-hosted)

### Negative:

**⚠️ Operational complexity:**
- Два инструмента требуют мониторинга
- **Mitigation:** Оба managed services

**⚠️ Integration layer:**
- Нужен код для публикации events из Temporal
- **Mitigation:** Простая activity `publish_event`

**⚠️ Learning curve:**
- Команда должна понимать оба инструмента
- **Mitigation:** Документация + training

---

## Related Documents

- [TEMPORAL_EVENTBUS_ARCHITECTURE.md](TEMPORAL_EVENTBUS_ARCHITECTURE.md) - Architecture integration
- [TEMPORAL_INTEGRATION_STRATEGY.md](../intelligent-core/workflow_intelligence/TEMPORAL_INTEGRATION_STRATEGY.md) - Temporal guide
- [PROCESSES_MAPPING.md](../intelligent-core/workflow_intelligence/PROCESSES_MAPPING.md) - Process mapping
- [CORRECT_SETUP_WITH_TEMPORAL.md](CORRECT_SETUP_WITH_TEMPORAL.md) - Setup guide

---

## References

**Industry patterns:**
- Uber: "Building Uber's Fulfillment Platform with Cadence (Temporal predecessor)"
- Netflix: "Conductor vs Temporal for workflow orchestration"
- Airbnb: "Event-Driven Architecture at Airbnb"

**Documentation:**
- Temporal Docs: https://docs.temporal.io
- RabbitMQ Patterns: https://www.rabbitmq.com/getstarted.html

---

**Last Updated:** 2025-10-06
**Status:** ✅ Accepted and Implemented (Temporal Cloud connected)
**Next:** Phase 2 - Workflow Intelligence Engine development
