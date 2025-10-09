# 🏗️ AI-Platform-ISO: Концептуальное Разделение Архитектуры

**Version**: 1.0
**Date**: 2025-10-09
**Author**: Infrastructure Governance Team

---

## 🎯 ФИЛОСОФИЯ АРХИТЕКТУРЫ

### Главный Принцип: **Eat Your Own Dog Food**

> Мы создаем BCM платформу И применяем BCM на саму платформу.
>
> Это означает **двухуровневое разделение**:
> 1. **Программная функциональность** - что платформа делает ДЛЯ пользователей (7 user journeys)
> 2. **Системное функционирование** - как платформа управляет САМА СОБОЙ (BCM применяется на себя)

---

## 📊 ДВУХУРОВНЕВАЯ АРХИТЕКТУРА

```
┌─────────────────────────────────────────────────────────────┐
│         УРОВЕНЬ 1: ПРОГРАММНАЯ ФУНКЦИОНАЛЬНОСТЬ             │
│         (Product Features - что видят пользователи)         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  7 USER JOURNEYS:                                            │
│  ├─ Journey 1: Certification Path (Gap Analysis, Roadmap)   │
│  ├─ Journey 2: Auditor Tools (Client Management)            │
│  ├─ Journey 3: Learning Academy (Courses, AI Tutor)         │
│  ├─ Journey 4: Certified Courses (Auditor Verification)     │
│  ├─ Journey 5: Digital Twin (Organization Simulation)       │
│  ├─ Journey 6: Crisis Response (Emergency Portal)           │
│  └─ Journey 7: Auditor Certification (Self-Study)           │
│                                                               │
│  SERVICES (Business Logic):                                  │
│  ├─ BIA Service (8001) - Business Impact Analysis           │
│  ├─ Risk Service (8002) - Risk Management                   │
│  ├─ Planning Service (8004) - BC Plans                      │
│  ├─ Compliance Service (8005) - ISO tracking                │
│  ├─ Digital Twin (8082) - Simulation engine                 │
│  └─ AI Orchestrator (8000) - AI specialists                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ APIs, EventBus, Data
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         УРОВЕНЬ 2: СИСТЕМНОЕ ФУНКЦИОНИРОВАНИЕ               │
│         (Platform Operations - BCM на себя)                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  INFRASTRUCTURE GOVERNANCE (Phase 1.1):                      │
│  ├─ Infrastructure Coordinator (9092)                        │
│  │   ├─ Health Monitor (следит за всеми сервисами)         │
│  │   ├─ Auto-Recovery (автоматическое восстановление)       │
│  │   ├─ Resource Optimizer (оптимизация ресурсов)          │
│  │   └─ EventBus Management (координация)                   │
│  │                                                            │
│  ├─ Decision Center (9091) - Governance Layer                │
│  │   ├─ Policy Engine (policies.yaml - правила)            │
│  │   ├─ Escalation Manager (эскалация проблем)             │
│  │   ├─ Notification Service (уведомления)                  │
│  │   └─ Audit Logger (ISO 22301 compliance)                │
│  │                                                            │
│  ├─ System BCM Service (8050)                               │
│  │   ├─ Platform Health Score (общий health платформы)     │
│  │   ├─ BCM Cycles (PDCA на саму платформу)                │
│  │   ├─ Learning from Incidents (обучение на ошибках)      │
│  │   └─ Integration с AI Foundation                         │
│  │                                                            │
│  └─ Monitoring & Observability                              │
│      ├─ Prometheus (9090) - Metrics collection              │
│      ├─ Grafana (3000) - Visualization                      │
│      ├─ EventBus Stats - Real-time event monitoring        │
│      └─ Audit Trail - ISO compliance logs                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 КАК ЭТО РАБОТАЕТ ВМЕСТЕ

### Пример 1: Пользователь создает BIA

**Программная функциональность (Уровень 1)**:
```python
# Пользователь → Frontend → BIA Service (8001)
POST /api/bia/assessments
{
  "service_name": "Payment Processing",
  "criticality": "HIGH",
  "rto_hours": 4,
  "mtpd_hours": 8
}

# BIA Service обрабатывает запрос
# Сохраняет в БД
# Возвращает результат пользователю
```

**Системное функционирование (Уровень 2)**:
```python
# В это время Infrastructure Coordinator следит:

# Health Monitor проверяет BIA Service каждые 30 сек
health_check(service="bia_service", port=8001)
# → Status: HEALTHY, response_time: 45ms

# Если BIA Service падает:
# 1. Health Monitor публикует event: "bia_service.unhealthy"
# 2. Auto-Recovery получает event
# 3. Decision Center решает: можно ли авто-восстановить?
#    - Проверяет policy: bia_service.max_auto_attempts = 3
#    - Проверяет: это attempt #1? → YES
#    - Решение: APPROVE auto-recovery
# 4. Auto-Recovery выполняет: restart container
# 5. Escalation Manager НЕ активируется (т.к. успешно)
# 6. Audit Logger записывает: "bia_service auto-recovered successfully"
# 7. Notification Service уведомляет ops team: "BIA Service recovered"
```

---

### Пример 2: Критический инцидент - Database failure

**Программная функциональность (Уровень 1)**:
```python
# Пользователи видят: "Service temporarily unavailable"
# Все запросы к BIA/Risk/Planning services FAIL
# Frontend показывает: "We're experiencing issues, working on it"
```

**Системное функционирование (Уровень 2)**:
```python
# Infrastructure Coordinator реагирует:

# 1. Health Monitor детектит: database.unhealthy (consecutive_failures: 3)
event_publish("database.critical_failure")

# 2. Auto-Recovery запрашивает Decision Center:
decision, can_proceed = decision_center.decide_recovery_action(
    service_name="database",
    action_type="failover",
    current_attempt=1
)

# 3. Decision Center проверяет policy:
policy = policies['recovery']['by_service']['database']
# → priority: 1 (CRITICAL)
# → max_auto_attempts: 2
# → require_approval: TRUE  # ⚠️ Database failover requires approval!
# → escalate_immediately: FALSE

# Решение: ESCALATE (требуется человеческое одобрение)
decision.outcome = "ESCALATE"
decision.reasoning = "Database failover requires human approval per policy"

# 4. Escalation Manager активируется:
escalation = EscalationManager.create(
    service="database",
    level=2,  # Immediate escalation to on-call
    trigger="Critical service failure + approval required"
)

# 5. Notification Service отправляет:
# - Email → ops@ai-platform.com
# - Slack → #critical-alerts
# - SMS → on-call engineer

# 6. Admin Console показывает:
# - Active Escalation: "Database failure pending approval"
# - Approve/Reject buttons
# - Impact forecast: "All services affected, estimated 10min RTO"

# 7. Human operator видит в Governance Console:
# - Escalation #123: Database failover pending
# - Clicks "Approve"

# 8. Decision Center получает approval:
decision_center.approve_action(
    decision_id="decision-456",
    approved_by="admin@ai-platform.com"
)

# 9. Auto-Recovery выполняет: database failover
# 10. Health Monitor проверяет: database recovered? → YES
# 11. Escalation Manager закрывает эскалацию: RESOLVED
# 12. Audit Logger записывает полную цепочку событий (ISO compliance)
# 13. System BCM Service обучается на инциденте для future prevention
```

---

## 🎯 КЛЮЧЕВЫЕ РАЗЛИЧИЯ

### **Программная Функциональность** (Product):

**Цель**: Решать задачи ПОЛЬЗОВАТЕЛЕЙ
- Помочь организациям получить ISO сертификацию
- Дать аудиторам инструменты для работы
- Обучить специалистов BCM
- Моделировать кризисы
- Управлять активными кризисами

**Компоненты**:
- BIA Service - создает Business Impact Analysis ДЛЯ клиентов
- Risk Service - управляет рисками клиентов
- Digital Twin - моделирует организации клиентов
- AI Orchestrator - отвечает на вопросы клиентов
- Frontend UI - 7 user journeys

**Метрики успеха**:
- Сколько организаций получили сертификацию?
- Сколько аудиторов используют платформу?
- Сколько курсов пройдено?
- Revenue (MRR, ARR)

---

### **Системное Функционирование** (Operations):

**Цель**: Обеспечить РАБОТОСПОСОБНОСТЬ платформы
- Следить, чтобы все сервисы работали
- Автоматически восстанавливать при сбоях
- Оптимизировать ресурсы
- Эскалировать критичные проблемы
- Соблюдать ISO 22301 compliance для САМОЙ платформы

**Компоненты**:
- Infrastructure Coordinator - следит за ВСЕМИ сервисами
- Decision Center - принимает решения о recovery/optimization
- System BCM - применяет BCM на саму платформу
- Health Monitor - проверяет health всех сервисов
- Auto-Recovery - восстанавливает упавшие сервисы

**Метрики успеха**:
- Platform uptime (>99.9%)
- Recovery success rate (>90%)
- Mean time to recovery (MTTR < 5 min)
- Escalation count (чем меньше, тем лучше)
- Governance maturity score (70/100 → 100/100)

---

## 📐 АРХИТЕКТУРНЫЕ ПАТТЕРНЫ

### 1. **Separation of Concerns**

```
❌ ПЛОХО (mixed concerns):
BIA Service (8001)
├─ business_impact_analysis.py  # User functionality
├─ health_check.py              # Self-monitoring
└─ auto_recovery.py             # Self-healing

✅ ХОРОШО (separated):
BIA Service (8001)
└─ business_impact_analysis.py  # ТОЛЬКО user functionality

Infrastructure Coordinator (9092)
├─ health_monitor.py            # Следит за BIA Service
└─ auto_recovery.py             # Восстанавливает BIA Service
```

### 2. **Event-Driven Coordination**

```python
# Сервисы НЕ знают об Infrastructure Coordinator
# Coordinator СЛУШАЕТ события от всех сервисов

# BIA Service просто работает:
def create_bia_assessment(data):
    # Business logic
    assessment = Assessment.create(data)

    # Publish domain event (не для infrastructure, а для других services)
    eventbus.publish("bia.assessment.created", assessment)

    return assessment

# Infrastructure Coordinator слушает ВСЕ события:
eventbus.subscribe("*.unhealthy", auto_recovery.handle_failure)
eventbus.subscribe("*.critical", escalation_manager.handle_critical)
eventbus.subscribe("*.recovery.success", system_bcm.learn_from_incident)
```

### 3. **Policy-Driven Governance**

```yaml
# policies.yaml - ЕДИНЫЙ источник правил

# Программная функциональность использует:
bia_workflows:
  validation:
    min_rto_minutes: 15
    max_rto_hours: 48
    require_dependencies: true

# Системное функционирование использует:
recovery:
  by_service:
    bia_service:
      priority: 3  # Medium
      rto_seconds: 240  # 4 minutes
      max_auto_attempts: 3
      recovery_strategy: "restart"
```

### 4. **Recursive BCM Application**

```
Уровень 0: Клиенты используют платформу для BCM
           ↓
Уровень 1: Платформа предоставляет BCM функциональность
           ├─ BIA Service (создает BIA для клиентов)
           ├─ Risk Service (управляет рисками клиентов)
           └─ Digital Twin (моделирует кризисы клиентов)
           ↓
Уровень 2: Платформа применяет BCM на САМУ СЕБЯ
           ├─ System BCM создает BIA для ПЛАТФОРМЫ
           ├─ Decision Center управляет рисками ПЛАТФОРМЫ
           └─ Infrastructure Coordinator восстанавливает ПЛАТФОРМУ
           ↓
Рекурсия: System BCM service тоже может упасть!
          → Infrastructure Coordinator восстанавливает System BCM
          → Decision Center решает как восстанавливать
          → Escalation Manager эскалирует если не получается
```

---

## 🏢 ОРГАНИЗАЦИОННАЯ СТРУКТУРА

### **Команды разработки**

#### Product Team (Программная функциональность)
**Фокус**: User journeys, business logic, UX

**Зоны ответственности**:
- 7 user journeys
- BIA/Risk/Planning services
- Digital Twin simulator
- AI Orchestrator
- Frontend UI

**Метрики**:
- User satisfaction (NPS)
- Feature adoption
- Revenue growth
- Time to certification

---

#### Platform Team (Системное функционирование)
**Фокус**: Reliability, observability, governance

**Зоны ответственности**:
- Infrastructure Coordinator
- Decision Center
- System BCM
- Monitoring & Alerting
- EventBus management

**Метрики**:
- Platform uptime (SLA)
- MTTR (Mean Time To Recovery)
- Incident count
- Governance maturity score

---

### **Shared Ownership**

```
EventBus:
├─ Product Team: использует для domain events (bia.created, risk.updated)
└─ Platform Team: использует для infrastructure events (service.unhealthy)

Policies (policies.yaml):
├─ Product Team: добавляет business rules (workflow validation, BIA thresholds)
└─ Platform Team: добавляет operations rules (recovery strategies, escalation)

Observability:
├─ Product Team: business metrics (assessments created, plans generated)
└─ Platform Team: infrastructure metrics (service health, response times)
```

---

## 🎯 GOVERNANCE MODEL

### **Who decides what?**

#### Product Decisions (Program Level)
**Decision Makers**: Product Manager, CTO, Business Stakeholders

**Decisions**:
- Which user journeys to build?
- What features to prioritize?
- Pricing model
- AI model selection (Claude vs GPT)
- User experience

**Input**: User feedback, market research, revenue impact

---

#### Platform Decisions (Infrastructure Level)
**Decision Makers**: Decision Center (automated) + Platform Team (escalation)

**Decisions**:
- Should we auto-recover this service?
- Is resource optimization needed?
- Escalate to human?
- Which recovery strategy?

**Input**: Policies (policies.yaml), health metrics, historical data

**Escalation Path**:
1. **Auto-decision** (Decision Center): 80% of cases
2. **Ops team approval**: 15% (critical services)
3. **CTO approval**: 5% (platform-wide impact)

---

## 📊 INTEGRATION POINTS

### **How do levels interact?**

#### 1. **Monitoring Integration**

```python
# Product service exposes health endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "dependencies": {
            "database": check_db(),
            "redis": check_redis()
        },
        "metrics": {
            "active_sessions": get_active_sessions(),
            "queue_depth": get_queue_depth()
        }
    }

# Infrastructure Coordinator calls it
health_monitor.register_service(
    name="bia_service",
    url="http://localhost:8001/health",
    interval=30  # seconds
)
```

#### 2. **Policy Integration**

```yaml
# policies.yaml влияет на ОБА уровня

# Program Level: BIA validation
bia_workflows:
  validation:
    min_rto_minutes: 15  # Product team decision

# Infrastructure Level: BIA service recovery
recovery:
  by_service:
    bia_service:
      rto_seconds: 240  # Platform team decision
```

#### 3. **Event Integration**

```python
# Domain events (Product) → Infrastructure events (Platform)

# Product: BIA Service publishes
eventbus.publish("bia.assessment.completed", {...})

# Platform: System BCM learns from this
@eventbus.subscribe("bia.assessment.*")
def learn_from_bia_patterns(event):
    # Analyze: are we creating too many assessments? (high load)
    # Decide: should we scale up?
    # Apply: auto-scaling recommendation
```

---

## 🚀 DEVELOPMENT WORKFLOW

### **Product Feature Development**

```bash
# Developer adds new feature: "Generate BIA Report"

# Step 1: Implement business logic
# File: platform-services/bia-service/report_generator.py
def generate_bia_report(assessment_id):
    # Business logic
    report = create_pdf_report(assessment_id)

    # Publish domain event
    eventbus.publish("bia.report.generated", {
        "assessment_id": assessment_id,
        "report_url": report.url
    })

    return report

# Step 2: Platform Team AUTOMATICALLY gets monitoring
# → Infrastructure Coordinator automatically monitors BIA service
# → No extra code needed!

# Step 3: Add policy if needed
# File: infrastructure/decision-center/policies.yaml
bia_workflows:
  report_generation:
    max_generation_time_minutes: 5
    timeout_action: "alert_ops_team"
```

### **Platform Feature Development**

```bash
# Platform engineer improves auto-recovery

# Step 1: Implement new recovery strategy
# File: infrastructure/eventbus/coordination/auto_recovery.py
async def _execute_recovery_circuit_breaker(self, service_name):
    # New strategy: circuit breaker pattern
    # Half-open state → probe → full recovery

# Step 2: Add policy
# File: infrastructure/decision-center/policies.yaml
recovery:
  by_service:
    api_gateway:
      recovery_strategy: "circuit_breaker"  # NEW strategy

# Step 3: Test with ANY service
# → Works with BIA/Risk/Planning automatically
# → No changes needed in product services!
```

---

## 🎯 NEXT STEPS

### **Immediate (Week 1-2)**

✅ **COMPLETED**:
- [x] Infrastructure Coordinator UI integration
- [x] Decision Center REST API
- [x] Governance Console component
- [x] EventBus management UI

⏳ **IN PROGRESS**:
- [ ] Deploy Prometheus & Grafana dashboards
- [ ] Integrate policies from ai-foundation/workflow_intelligence
- [ ] Create System BCM dashboard

### **Short-term (Month 1-2)**

- [ ] Implement Phase 1.5: AI-assisted decision making
  - Decision Center → ai-foundation integration
  - RAG-based recovery recommendations
  - ML-based RTO prediction

- [ ] Complete observability stack
  - EventCatalog for event visualization
  - Audit trail viewer
  - Real-time escalation notifications

### **Long-term (Month 3-6)**

- [ ] Recursive BCM maturity
  - System BCM score: 70/100 → 90/100
  - Full automation: 80% → 95%
  - Zero manual escalations for routine incidents

- [ ] Platform self-optimization
  - ML-based capacity planning
  - Predictive failure detection
  - Auto-scaling based on AI predictions

---

## 📚 RELATED DOCUMENTS

- [7_USER_JOURNEYS_PLATFORM_ARCHITECTURE.md](/interface/7_USER_JOURNEYS_PLATFORM_ARCHITECTURE.md) - Product (Уровень 1)
- [PHASE_1.1_GOVERNANCE_COMPLETE.md](/infrastructure/decision-center/PHASE_1.1_GOVERNANCE_COMPLETE.md) - Platform (Уровень 2)
- [policies.yaml](/infrastructure/decision-center/policies.yaml) - Unified governance policies

---

**Ключевой вывод**:

> Мы создаем **платформу-которая-ест-свою-еду**.
>
> Программная функциональность (7 journeys) дает клиентам BCM инструменты.
> Системное функционирование (Infrastructure Coordinator) применяет BCM на саму платформу.
>
> Это делает нас ЭКСПЕРТАМИ, потому что мы сами живем по BCM принципам.

**Документ готов! 🚀**
