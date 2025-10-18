# Governance Gap - Action Plan
**Created:** 2025-10-15
**Status:** Assigned to another Claude instance
**Priority:** CRITICAL for production

---

## Executive Summary

Infrastructure Level (Phase 1) технически готов на 100%, но имеет **критический governance gap** с maturity 20/100. Перед production развёртыванием необходимо реализовать минимальный governance layer.

---

## Critical Issues

### 1. No Decision Center ❌
- Infrastructure Coordinator принимает решения автоматически
- Никому не подотчётен
- Нет human approval
- Нет escalation

### 2. Hardcoded Goals ❌
- MAX_ATTEMPTS = 3 (откуда?)
- THRESHOLD = 80% (почему?)
- Нет policy engine
- Нет business alignment

### 3. Weak AI Integration ❌
- Не использует AI Orchestrator
- Не консультируется с Expertise Center
- Не использует Predictive Intelligence
- Работает изолированно

### 4. No Escalation ❌
- Auto-Recovery может зацикливаться
- Нет механизма остановки
- Нет notification на критичные ситуации

### 5. Reactive, Not Proactive ❌
- Только реагирует на проблемы
- Не предсказывает
- Не предотвращает

---

## Governance Maturity Assessment

```
Decision Making:        ████░░░░░░ 20/100  ❌
Accountability:         ██░░░░░░░░ 10/100  ❌
Goal Management:        ███░░░░░░░ 15/100  ❌
Policy Compliance:      ███░░░░░░░ 25/100  ❌
AI Integration:         ████░░░░░░ 40/100  ⚠️
Escalation:             ░░░░░░░░░░  0/100  ❌
Conflict Resolution:    ░░░░░░░░░░  0/100  ❌

Overall Maturity:       ███░░░░░░░ 20/100  ❌ CRITICAL
```

---

## Action Plan

### Phase 1.1: Minimal Governance (URGENT - 1-2 days)

**Goal:** Make system safe for production

#### Task 1.1.1: Minimal Decision Center (2-3 hours)
**File:** `/infrastructure/decision_center/minimal_decision_center.py`

**Features:**
- Escalation после max_attempts
- Manual approval для critical services
- Basic decision logging
- Integration with Infrastructure Coordinator

**Implementation:**
```python
class MinimalDecisionCenter:
    """
    Minimal Decision Center для Phase 1.1
    Обеспечивает базовое управление и escalation
    """

    async def decide_recovery_action(
        self,
        service: str,
        health_status: HealthStatus,
        attempts: int,
        history: RecoveryHistory
    ) -> RecoveryDecision:
        """
        Принимает решение о recovery action

        Rules:
        1. If attempts >= max_attempts → ESCALATE
        2. If critical service → NOTIFY immediately
        3. If manual approval required → WAIT for approval
        """

        policy = await self.policy_engine.get_policy(service)

        # Rule 1: Max attempts exceeded
        if attempts >= policy.max_attempts:
            return await self.escalate(
                service=service,
                reason="max_attempts_exceeded",
                attempts=attempts,
                notify=["ops_team", "on_call"]
            )

        # Rule 2: Critical service
        if policy.is_critical and attempts >= policy.escalate_after:
            await self.notify_immediately(service, health_status)

        # Rule 3: Manual approval
        if policy.require_approval and attempts > 0:
            return await self.wait_for_approval(service, action)

        # Allow auto-recovery
        return RecoveryDecision(
            action="proceed",
            approved_by="decision_center",
            reason="within_policy"
        )
```

#### Task 1.1.2: Escalation Mechanism (1 hour)
**File:** `/infrastructure/eventbus/coordination/escalation_manager.py`

**Features:**
- Escalation rules
- Notification routing
- Escalation tracking
- Integration with Auto-Recovery

**Implementation:**
```python
class EscalationManager:
    """
    Управление escalation для Infrastructure Level
    """

    async def escalate(
        self,
        service: str,
        reason: str,
        severity: str,
        context: dict
    ) -> EscalationTicket:
        """
        Создаёт escalation ticket и уведомляет
        """

        ticket = EscalationTicket(
            id=generate_id(),
            service=service,
            reason=reason,
            severity=severity,
            context=context,
            created_at=now(),
            status="open"
        )

        # Save to database
        await self.db.save_escalation(ticket)

        # Notify appropriate channels
        await self.notify(ticket)

        # Publish event
        await self.eventbus.publish(Event(
            type="infrastructure.escalation.created",
            data=ticket.dict()
        ))

        return ticket

    async def notify(self, ticket: EscalationTicket):
        """
        Отправляет уведомления
        """

        if ticket.severity == "critical":
            # Immediate notification: SMS, phone, PagerDuty
            await self.notify_on_call(ticket)
            await self.notify_slack(ticket, urgent=True)
        elif ticket.severity == "high":
            # Slack + Email
            await self.notify_slack(ticket)
            await self.notify_email(ticket)
        else:
            # Email only
            await self.notify_email(ticket)
```

**Integration with Auto-Recovery:**
```python
# In auto_recovery.py:

async def _execute_recovery(self, service_name: str, strategy: str):
    attempts = self.recovery_history.get(service_name, 0)

    # Check with Decision Center
    decision = await self.decision_center.decide_recovery_action(
        service=service_name,
        health_status=current_status,
        attempts=attempts,
        history=self.history[service_name]
    )

    if decision.action == "escalate":
        logger.warning(f"Escalating {service_name} recovery to human")
        return  # STOP auto-recovery

    if decision.action == "wait_approval":
        logger.info(f"Waiting for manual approval for {service_name}")
        return  # WAIT

    # Proceed with recovery
    # ... existing code ...
```

#### Task 1.1.3: Policy Configuration (1 hour)
**File:** `/infrastructure/governance/policies.yaml`

**Content:**
```yaml
infrastructure_policies:
  version: "1.0"
  updated: "2025-10-15"
  approved_by: "CTO"

  recovery:
    default:
      max_auto_attempts: 3
      escalate_after: 2
      require_approval: false
      backoff_multiplier: 2
      max_backoff_seconds: 300

    critical_services:
      database:
        priority: 1
        rto_seconds: 120
        max_auto_attempts: 2
        escalate_after: 1
        require_approval: true
        escalation_severity: "critical"
        reason: "ISO 22301 Clause 8.4 - Critical data service"

      eventbus:
        priority: 1
        rto_seconds: 60
        max_auto_attempts: 3
        escalate_after: 2
        escalation_severity: "critical"
        reason: "Core infrastructure component"

      api_gateway:
        priority: 2
        rto_seconds: 180
        max_auto_attempts: 3
        escalate_after: 2
        escalation_severity: "high"

      redis:
        priority: 2
        rto_seconds: 120
        max_auto_attempts: 3
        escalate_after: 2

      rag_pipeline:
        priority: 3
        rto_seconds: 300
        max_auto_attempts: 2
        escalate_after: 1

  optimization:
    thresholds:
      cpu_high: 80
      cpu_critical: 90
      memory_high: 85
      memory_critical: 95
      disk_high: 80
      disk_critical: 90

    actions:
      preventive_threshold: 75  # Действовать до проблемы
      reactive_threshold: 90    # Реагировать на проблему

    schedule:
      optimization_cycle_minutes: 5
      off_hours_start: "22:00"
      off_hours_end: "06:00"
      prefer_off_hours: true

  notifications:
    slack:
      enabled: true
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channels:
        critical: "#infrastructure-alerts"
        high: "#infrastructure-alerts"
        medium: "#infrastructure-monitoring"

    email:
      enabled: true
      smtp_server: "${SMTP_SERVER}"
      recipients:
        critical: ["ops-team@company.com", "on-call@company.com"]
        high: ["ops-team@company.com"]

    pagerduty:
      enabled: true
      api_key: "${PAGERDUTY_API_KEY}"
      service_id: "${PAGERDUTY_SERVICE_ID}"
      escalation_policy: "infrastructure-oncall"

  compliance:
    audit_all_decisions: true
    log_retention_days: 90
    iso_22301_compliance: true
    require_approval_after_hours: false
```

**Policy Engine:**
```python
# File: /infrastructure/governance/policy_engine.py

class PolicyEngine:
    """
    Загружает и применяет политики
    """

    def __init__(self, config_path: str):
        self.policies = self._load_policies(config_path)

    def _load_policies(self, path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    async def get_policy(self, service: str) -> ServicePolicy:
        """
        Возвращает политику для сервиса
        """

        # Check critical services first
        if service in self.policies['recovery']['critical_services']:
            return ServicePolicy(
                **self.policies['recovery']['critical_services'][service],
                is_critical=True
            )

        # Use default policy
        return ServicePolicy(
            **self.policies['recovery']['default'],
            is_critical=False
        )

    async def reload_policies(self):
        """
        Hot reload политик
        """
        self.policies = self._load_policies(self.config_path)
        logger.info("Policies reloaded")
```

#### Task 1.1.4: Enhanced Audit Logging (2 hours)
**File:** `/infrastructure/governance/audit_logger.py`

**Features:**
- Логирование всех решений
- Structured logging (JSON)
- PostgreSQL storage
- Retention policy (90 days)
- ISO 22301 compliance fields

**Implementation:**
```python
class AuditLogger:
    """
    Audit logging для compliance (ISO 22301)
    """

    async def log_decision(self, decision: Decision):
        """
        Логирует решение Decision Center
        """

        audit_record = {
            "id": generate_id(),
            "timestamp": now(),
            "type": "decision",
            "service": decision.service,
            "action": decision.action,
            "reason": decision.reason,
            "decided_by": decision.decided_by,  # "system" or "human"
            "context": decision.context,
            "policy_reference": decision.policy_reference,
            "iso_clause": decision.iso_clause,
            "result": None,  # Filled later
            "duration_ms": None
        }

        await self.db.insert("audit_log", audit_record)

        # Also publish event for real-time monitoring
        await self.eventbus.publish(Event(
            type="infrastructure.audit.decision_logged",
            data=audit_record
        ))

    async def log_recovery_action(self, action: RecoveryAction):
        """
        Логирует recovery action
        """

        audit_record = {
            "id": generate_id(),
            "timestamp": now(),
            "type": "recovery_action",
            "service": action.service,
            "strategy": action.strategy,
            "attempt": action.attempt,
            "max_attempts": action.max_attempts,
            "backoff_seconds": action.backoff_seconds,
            "result": action.result,  # "success", "failure", "escalated"
            "duration_ms": action.duration_ms,
            "error_message": action.error_message,
            "decided_by": action.decided_by
        }

        await self.db.insert("audit_log", audit_record)

    async def log_escalation(self, escalation: EscalationTicket):
        """
        Логирует escalation
        """

        audit_record = {
            "id": generate_id(),
            "timestamp": now(),
            "type": "escalation",
            "service": escalation.service,
            "reason": escalation.reason,
            "severity": escalation.severity,
            "context": escalation.context,
            "notified": escalation.notified,
            "status": escalation.status,
            "resolved_at": None,
            "resolved_by": None
        }

        await self.db.insert("audit_log", audit_record)
```

**Database Schema:**
```sql
-- File: /infrastructure/database/migrations/019_audit_log.sql

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    type VARCHAR(50) NOT NULL,  -- 'decision', 'recovery_action', 'escalation'
    service VARCHAR(100) NOT NULL,
    action VARCHAR(50),
    reason TEXT,
    decided_by VARCHAR(50),  -- 'system', 'human', 'decision_center'
    context JSONB,
    policy_reference VARCHAR(200),
    iso_clause VARCHAR(50),
    result VARCHAR(50),
    duration_ms INTEGER,
    severity VARCHAR(20),
    error_message TEXT,

    -- Indexes for queries
    INDEX idx_audit_timestamp (timestamp DESC),
    INDEX idx_audit_service (service),
    INDEX idx_audit_type (type)
);

-- Retention policy (90 days)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM audit_log
    WHERE timestamp < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (run daily)
-- Requires pg_cron extension
SELECT cron.schedule('cleanup-audit-logs', '0 2 * * *', 'SELECT cleanup_old_audit_logs()');
```

---

### Phase 1.5: AI Integration (IMPORTANT - 3-5 days)

**Goal:** Utilize existing AI capabilities

#### Task 1.5.1: AI Orchestrator Integration (2 days)
- Infrastructure → publishes complex problems
- AI Orchestrator → analyzes and decides
- Infrastructure → executes decisions

#### Task 1.5.2: Expertise Center Consultation (1 day)
- Database problems → Database Specialist
- Performance issues → Performance Specialist
- Security alerts → Security Specialist

#### Task 1.5.3: Predictive Integration (1 day)
- Predictive Intelligence → forecasts problems
- Infrastructure → preventive actions
- Proactive optimization

#### Task 1.5.4: Workflow Intelligence (1 day)
- Complex recovery → Temporal workflows
- Rollback mechanisms
- Saga patterns for distributed recovery

---

## Success Criteria

### Phase 1.1 (Minimal Governance)
- [ ] Decision Center implemented
- [ ] Escalation mechanism working
- [ ] Policies loaded from YAML
- [ ] Audit logging to PostgreSQL
- [ ] Manual approval for critical services
- [ ] No infinite recovery loops
- [ ] Notifications working (Slack, Email)
- [ ] ISO 22301 compliance fields present

### Phase 1.5 (AI Integration)
- [ ] AI Orchestrator receives infrastructure events
- [ ] Expertise Center consulted for complex issues
- [ ] Predictive Intelligence forecasting problems
- [ ] Workflow Intelligence handling complex recovery
- [ ] Cross-level integration working

---

## Timeline

```
Week 1:
├─ Day 1-2: Phase 1.1 (Minimal Governance)
│   ├─ Decision Center
│   ├─ Escalation
│   ├─ Policy Engine
│   └─ Audit Logging
│
└─ Day 3-7: Phase 1.5 (AI Integration)
    ├─ AI Orchestrator Integration
    ├─ Expertise Center Consultation
    ├─ Predictive Integration
    └─ Workflow Intelligence
```

---

## Risk Mitigation

**Risk 1:** Auto-Recovery infinite loops
- **Mitigation:** Escalation after max_attempts ✅
- **Status:** Addressed in Phase 1.1

**Risk 2:** No human oversight
- **Mitigation:** Manual approval for critical services ✅
- **Status:** Addressed in Phase 1.1

**Risk 3:** Hardcoded policies
- **Mitigation:** YAML configuration ✅
- **Status:** Addressed in Phase 1.1

**Risk 4:** No compliance audit trail
- **Mitigation:** Enhanced audit logging ✅
- **Status:** Addressed in Phase 1.1

---

## Notes

- **Assigned to:** Another Claude instance (as of 2025-10-15)
- **Priority:** CRITICAL - blocks production deployment
- **Dependencies:** None (can start immediately)
- **Estimated effort:** 6-8 days total (Phase 1.1 + 1.5)

---

**Status:** 📋 PLANNED - Ready to implement
**Next Action:** Start with Task 1.1.1 (Minimal Decision Center)
