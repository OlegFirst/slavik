# 🔄 Temporal Cloud + EventBus - Architecture Integration

**Version:** 1.0
**Date:** 2025-10-06
**Status:** ✅ Temporal Cloud Connected
**Part of:** FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md

---

## 📖 Overview

Этот документ описывает интеграцию **Temporal Cloud** (workflow orchestrator) и **EventBus** (RabbitMQ) в архитектуру AI-Powered BCM Platform.

**Ключевое решение:**
- ✅ **Temporal Cloud** = orchestration долгоживущих бизнес-процессов
- ✅ **EventBus (RabbitMQ)** = integration, notifications, real-time updates
- ✅ **Оба используются ВМЕСТЕ** (дополняют друг друга)

---

## 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     TEMPORAL CLOUD (SaaS)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ BIA Workflow │  │ Risk         │  │ Incident     │          │
│  │              │  │ Workflow     │  │ Response     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  Region: europe-west3.gcp.api.temporal.io:7233                  │
│  Namespace: ai-platform-iso-22301.r3gxp                         │
│  Auth: API Key + TLS                                            │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          │ gRPC (persistent workflows)
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│         WORKFLOW INTELLIGENCE ENGINE (intelligent-core/)         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Temporal Worker (Python 3.11 + temporalio SDK)        │    │
│  │  - Executes workflow code                              │    │
│  │  - Executes activities                                 │    │
│  │  - Publishes events to EventBus                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Workflows/   │  │ Activities/  │  │ Governance/  │          │
│  │ bia.py       │  │ bia_acts.py  │  │ rules.py     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Case Library (self-learning)                          │    │
│  │  - Auto-collect completed workflows                    │    │
│  │  - Store in PostgreSQL + Qdrant                        │    │
│  │  - AI learns patterns                                  │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          │ Publishes events
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                   EVENTBUS (RabbitMQ)                            │
│                                                                  │
│  Events: bia.started, bia.data_collected, bia.completed, etc.   │
│                                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Queue 1 │  │ Queue 2 │  │ Queue 3 │  │ Queue N │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          │ Subscribe to events
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                    PLATFORM SERVICES                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Notification  │  │Dashboard     │  │Risk Service  │          │
│  │Service       │  │Service       │  │              │          │
│  │              │  │              │  │              │          │
│  │@subscribe    │  │@subscribe    │  │@subscribe    │          │
│  │bia.completed │  │bia.progress  │  │bia.completed │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Audit Service │  │Metrics       │  │WebSocket     │          │
│  │              │  │Service       │  │Handler       │          │
│  │@subscribe    │  │@subscribe    │  │@subscribe    │          │
│  │*.completed   │  │*.*           │  │*.progress    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Division of Responsibilities

### Temporal Cloud - Orchestration

**Что делает:**
- ✅ Управляет **долгоживущими бизнес-процессами** (дни/недели)
- ✅ Сохраняет **persistent state** workflows
- ✅ Гарантирует **выполнение всех шагов** (exactly-once)
- ✅ **Human-in-the-loop** (wait for approvals)
- ✅ **Retry logic** при сбоях
- ✅ **Conditional logic** (if/else, loops)
- ✅ **Compensation/Rollback** (sagas pattern)

**Процессы через Temporal (~10-15 workflows):**
1. BIA Workflow (2-4 недели)
2. Risk Assessment Workflow (1-2 недели)
3. Incident Response Workflow (минуты-дни)
4. Compliance Audit Workflow (recurring, quarterly)
5. DR Testing Workflow (recurring, monthly)
6. Crisis Management Workflow
7. Supply Chain Risk Assessment
8. Training & Exercise Program (recurring)
9. BC Plan Update Workflow
10. Change Management Workflow

**Что НЕ делает:**
- ❌ Не для CRUD operations
- ❌ Не для real-time messaging
- ❌ Не для broadcasting (1→N)
- ❌ Не для stateless operations

---

### EventBus (RabbitMQ) - Integration

**Что делает:**
- ✅ **Fire-and-forget** notifications
- ✅ **Broadcasting** (1 event → N consumers)
- ✅ **Loose coupling** между сервисами
- ✅ **Real-time updates** для UI
- ✅ **Audit trail** (все события логируются)
- ✅ **Integration hooks** для новых сервисов

**Events публикуемые workflows:**
```
bia.started                 → NotificationService, Dashboard
bia.kickoff_completed       → AuditLog, Metrics
bia.data_collected          → Dashboard (progress update)
bia.analysis_completed      → RiskService (trigger update)
bia.completed               → NotificationService, AuditLog, RiskService

incident.detected           → AlertService, LogService, StatusPage
incident.escalated          → ManagementNotification, AuditLog
incident.resolved           → AllClearNotification, StatusPage

compliance.audit_started    → NotificationService, AuditLog
compliance.issues_found     → RemediationWorkflow (trigger)
compliance.audit_completed  → RegulatoryReporting, AuditLog
```

**Что НЕ делает:**
- ❌ Не управляет state workflows
- ❌ Не гарантирует порядок шагов
- ❌ Не имеет retry logic для processes
- ❌ Не для долгоживущих процессов

---

## 🔄 Integration Pattern: Temporal + EventBus

**Паттерн использования:**

```python
# ✅ ПРАВИЛЬНО: Temporal orchestrates + EventBus integrates

@workflow.defn
class BIAWorkflow:
    """Temporal управляет процессом BIA"""

    @workflow.run
    async def run(self, org_id: str) -> BIAResult:
        # ═════════════════════════════════════════════════════
        # TEMPORAL: Orchestration (persistent state)
        # ═════════════════════════════════════════════════════

        # Stage 1: Kickoff Meeting
        kickoff = await workflow.execute_activity(
            kickoff_meeting,
            org_id,
            start_to_close_timeout=timedelta(days=2)
        )

        # ─────────────────────────────────────────────────────
        # EVENTBUS: Notification (fire-and-forget)
        # ─────────────────────────────────────────────────────
        await workflow.execute_activity(
            publish_event,
            "bia.kickoff_completed",
            {"org_id": org_id, "stage": "kickoff"}
        )

        # ═════════════════════════════════════════════════════
        # TEMPORAL: Data Collection (AI-powered)
        # ═════════════════════════════════════════════════════
        data = await workflow.execute_activity(
            collect_data_with_ai,
            org_id,
            start_to_close_timeout=timedelta(days=5)
        )

        # ─────────────────────────────────────────────────────
        # EVENTBUS: Progress Update (real-time for UI)
        # ─────────────────────────────────────────────────────
        await workflow.execute_activity(
            publish_event,
            "bia.data_collected",
            {"org_id": org_id, "progress": "40%"}
        )

        # ═════════════════════════════════════════════════════
        # TEMPORAL: Analysis (AI + Governance)
        # ═════════════════════════════════════════════════════
        analysis = await workflow.execute_activity(
            analyze_data,
            data,
            start_to_close_timeout=timedelta(days=3)
        )

        # Governance Checkpoint
        governance = await workflow.execute_activity(
            governance_checkpoint,
            analysis
        )

        if governance.requires_human:
            # TEMPORAL: Wait for human approval (может дни!)
            await workflow.wait_condition(lambda: self.human_approved)
            final_analysis = self.human_decision
        else:
            # TEMPORAL: Creative Zone - AI decides
            final_analysis = analysis

        # ─────────────────────────────────────────────────────
        # EVENTBUS: Analysis Complete (trigger RiskService)
        # ─────────────────────────────────────────────────────
        await workflow.execute_activity(
            publish_event,
            "bia.analysis_completed",
            final_analysis
        )

        # ═════════════════════════════════════════════════════
        # TEMPORAL: Generate Report
        # ═════════════════════════════════════════════════════
        report = await workflow.execute_activity(
            generate_report,
            final_analysis
        )

        # ═════════════════════════════════════════════════════
        # TEMPORAL: Publish to Case Library (learning)
        # ═════════════════════════════════════════════════════
        await workflow.execute_activity(
            publish_to_case_library,
            {
                "workflow_id": workflow.info().workflow_id,
                "org_id": org_id,
                "result": report,
                "duration": workflow.now() - workflow.info().start_time
            }
        )

        # ─────────────────────────────────────────────────────
        # EVENTBUS: BIA Completed (notify all stakeholders)
        # ─────────────────────────────────────────────────────
        await workflow.execute_activity(
            publish_event,
            "bia.completed",
            {"org_id": org_id, "report_id": report.id}
        )

        return report


# ═════════════════════════════════════════════════════════════════
# EVENTBUS: Consumers (independent services)
# ═════════════════════════════════════════════════════════════════

# Notification Service
@eventbus.subscribe("bia.completed")
async def send_bia_completion_notification(event):
    """Send email/SMS to stakeholders"""
    await notification_service.send(
        recipients=event["stakeholders"],
        template="bia_completed",
        data=event
    )

# Dashboard Service
@eventbus.subscribe("bia.data_collected")
async def update_dashboard(event):
    """Real-time progress update on dashboard"""
    await websocket.broadcast({
        "type": "bia_progress",
        "org_id": event["org_id"],
        "progress": event["progress"]
    })

# Risk Service
@eventbus.subscribe("bia.completed")
async def trigger_risk_update(event):
    """BIA completed → update risk assessment"""
    await risk_service.update_from_bia(
        org_id=event["org_id"],
        bia_report_id=event["report_id"]
    )

# Audit Log Service
@eventbus.subscribe("bia.*")  # All BIA events
async def log_bia_event(event):
    """Log all BIA events for compliance"""
    await audit_log.record({
        "event_type": event.routing_key,
        "timestamp": datetime.utcnow(),
        "data": event
    })

# Metrics Service
@eventbus.subscribe("*.completed")  # All completion events
async def update_metrics(event):
    """Update completion metrics"""
    await metrics.increment(f"{event.routing_key}.count")
```

---

## 📊 Data Flow Example: BIA Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User starts BIA                                              │
│    POST /api/bia/start                                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. API Gateway → Temporal Client                                │
│    client.start_workflow(BIAWorkflow, org_id)                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Temporal Cloud starts workflow                               │
│    Workflow ID: bia-org123-2025-10-06                           │
│    State: RUNNING                                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Temporal Worker executes activities                          │
│    Activity: kickoff_meeting                                    │
│    Duration: 2 hours                                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Activity publishes event to EventBus                         │
│    publish_event("bia.kickoff_completed", {...})                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ├──────────────┬──────────────┬──────────────┐
                     ▼              ▼              ▼              ▼
          ┌───────────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────┐
          │Notification   │ │Dashboard    │ │AuditLog  │ │Metrics   │
          │Service        │ │Service      │ │Service   │ │Service   │
          │               │ │             │ │          │ │          │
          │Send email     │ │Update UI    │ │Log event │ │Increment │
          └───────────────┘ └─────────────┘ └──────────┘ └──────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Workflow continues: collect_data_with_ai                     │
│    Duration: 5 days                                             │
│    State persisted in Temporal Cloud                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Data collected → publish event                               │
│    publish_event("bia.data_collected", {progress: "40%"})       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ Dashboard Service   │
          │ (WebSocket update)  │
          │ UI shows 40% done   │
          └─────────────────────┘
                     │
                     ▼
         ... continues for 2-4 weeks ...
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ FINAL: BIA Completed                                            │
│    - Temporal: Report generated, Case Library updated           │
│    - EventBus: "bia.completed" → all subscribers notified       │
│    - State: COMPLETED                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Temporal Cloud
- **Provider:** Temporal Technologies (SaaS)
- **Region:** europe-west3 (GCP)
- **Namespace:** ai-platform-iso-22301.r3gxp
- **Address:** europe-west3.gcp.api.temporal.io:7233
- **Auth:** API Key + TLS
- **SDK:** temporalio[opentelemetry]==1.18.1 (Python)
- **Python:** 3.11.13

### EventBus (RabbitMQ)
- **Provider:** CloudAMQP / Self-hosted
- **Protocol:** AMQP 0.9.1
- **Client:** aio-pika (Python async)
- **Patterns:** Pub/Sub, Topic Exchange
- **Persistence:** Messages persisted to disk

### Integration Layer
- **Location:** `shared/eventbus/`
- **Files:**
  - `client.py` - EventBus client
  - `publisher.py` - Event publisher
  - `subscriber.py` - Event subscriber decorators
  - `schemas.py` - Event schemas

---

## 📁 Code Structure

```
intelligent-core/workflow_intelligence/
├── README.md
├── TEMPORAL_INTEGRATION_STRATEGY.md
├── PROCESSES_MAPPING.md
│
├── workflows/                      # Temporal Workflows
│   ├── bia_workflow.py
│   ├── risk_workflow.py
│   ├── incident_workflow.py
│   └── compliance_workflow.py
│
├── activities/                     # Temporal Activities
│   ├── bia_activities.py
│   ├── risk_activities.py
│   └── common_activities.py
│
├── core/
│   ├── governance/                 # Governance System
│   │   ├── rules_engine.py
│   │   ├── checkpoints.py
│   │   └── creative_zones.py
│   │
│   └── case_library/               # Self-Learning
│       ├── collector.py
│       ├── repository.py
│       └── search.py
│
├── temporal_config.py              # Temporal Client config
├── temporal_worker.py              # Worker startup
└── test_temporal_connection.py    # Connection test

shared/eventbus/
├── __init__.py
├── client.py                       # EventBus connection
├── publisher.py                    # publish_event()
├── subscriber.py                   # @subscribe decorator
└── schemas.py                      # Event schemas

infrastructure/eventbus/
├── docker-compose.yml              # RabbitMQ setup
├── config/
│   └── rabbitmq.conf
└── init/
    └── setup_exchanges.sh
```

---

## 🔄 Deployment Architecture

### Temporal Worker Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  temporal-worker:
    build:
      context: ./intelligent-core/workflow_intelligence
      dockerfile: Dockerfile
    environment:
      - TEMPORAL_API_KEY=${TEMPORAL_API_KEY}
      - TEMPORAL_NAMESPACE=${TEMPORAL_NAMESPACE}
      - TEMPORAL_ADDRESS=${TEMPORAL_ADDRESS}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
      - rabbitmq
    restart: always
    healthcheck:
      test: ["CMD", "python", "-c", "import temporalio"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### RabbitMQ Deployment

```yaml
  rabbitmq:
    image: rabbitmq:3.12-management
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Management UI
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    restart: always
```

---

## 🎯 Benefits of This Architecture

### 1. **Reliability**
- ✅ Temporal гарантирует выполнение workflows (даже при крашах)
- ✅ EventBus персистирует события (не теряются при сбоях)
- ✅ Retry logic на обоих уровнях

### 2. **Scalability**
- ✅ Temporal Workers масштабируются горизонтально
- ✅ EventBus consumers независимо масштабируются
- ✅ Loose coupling → добавление новых сервисов без изменений

### 3. **Visibility**
- ✅ Temporal UI - полная история workflows
- ✅ RabbitMQ Management - мониторинг очередей
- ✅ Audit trail через EventBus

### 4. **Flexibility**
- ✅ Новые consumers подключаются через EventBus
- ✅ Workflow logic изменяется без затрагивания consumers
- ✅ Governance rules применяются централизованно

### 5. **Learning**
- ✅ Case Library собирает все workflows
- ✅ AI learns from completed workflows
- ✅ Continuous improvement

---

## 📚 Documentation References

**Temporal:**
- [TEMPORAL_INTEGRATION_STRATEGY.md](../intelligent-core/workflow_intelligence/TEMPORAL_INTEGRATION_STRATEGY.md) - Full Temporal guide
- [PROCESSES_MAPPING.md](../intelligent-core/workflow_intelligence/PROCESSES_MAPPING.md) - Which processes use Temporal
- [README.md](../intelligent-core/workflow_intelligence/README.md) - Quick start

**EventBus:**
- [shared/eventbus/README.md](../shared/eventbus/README.md) - EventBus integration guide
- [infrastructure/eventbus/README.md](../infrastructure/eventbus/README.md) - RabbitMQ setup

**Architecture:**
- [FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md](./FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md) - Main architecture doc
- [CORRECT_SETUP_WITH_TEMPORAL.md](./CORRECT_SETUP_WITH_TEMPORAL.md) - Setup algorithm

---

## ✅ Current Status

- [x] Temporal Cloud настроен
- [x] Connection tested
- [x] Sample workflow executed
- [x] Documentation created
- [ ] **Next:** Phase 2 - Workflow Intelligence Engine development (8-12 дней)

---

**Last Updated:** 2025-10-06
**Status:** ✅ Architecture Approved
