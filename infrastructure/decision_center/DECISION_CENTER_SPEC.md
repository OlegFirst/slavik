# Decision Center - Technical Specification

**Version:** 1.0.0
**Status:** Design
**Priority:** CRITICAL
**Timeline:** Week 1-2

---

## 🎯 Overview

Decision Center - центральный компонент governance layer, отвечающий за:
- Принятие решений на основе policies
- Эскалацию к человеку при необходимости
- Разрешение конфликтов приоритетов
- Audit logging всех решений (ISO 22301)
- Интеграцию с AI Intelligence Hub

---

## 🏗️ Architecture

### Component Structure

```
infrastructure/decision_center/
├── core/
│   ├── __init__.py
│   ├── decision_engine.py         # Основной движок принятия решений
│   ├── policy_engine.py           # Загрузка и валидация policies
│   ├── escalation_manager.py      # Управление эскалацией
│   └── audit_logger.py            # ISO 22301 compliant logging
│
├── api/
│   ├── __init__.py
│   ├── decision_api.py            # FastAPI endpoints
│   ├── models.py                  # Pydantic models
│   └── routes/
│       ├── decision.py            # Decision endpoints
│       ├── approval.py            # Manual approval endpoints
│       └── audit.py               # Audit log queries
│
├── integrations/
│   ├── __init__.py
│   ├── ai_intelligence_hub.py    # AI consultation
│   ├── infrastructure_coord.py    # Infrastructure coordination
│   ├── eventbus.py               # Event publishing
│   └── notification.py           # Email/Slack/SMS notifications
│
├── models/
│   ├── __init__.py
│   ├── decision.py               # Decision data models
│   ├── policy.py                 # Policy models
│   └── escalation.py             # Escalation models
│
├── utils/
│   ├── __init__.py
│   ├── context_builder.py        # System context aggregation
│   ├── priority_calculator.py    # Priority calculation
│   └── conflict_resolver.py      # Conflict resolution
│
├── tests/
│   ├── test_decision_engine.py
│   ├── test_escalation.py
│   └── test_policy_engine.py
│
├── policies.yaml                  # ✅ Already exists!
├── decision_center_api.py         # Main FastAPI app
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🔧 Core Components

### 1. Decision Engine

```python
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class DecisionType(Enum):
    """Типы решений"""
    AUTO_APPROVED = "auto_approved"      # Автоматически одобрено
    REQUIRES_APPROVAL = "requires_approval"  # Требует human approval
    ESCALATED = "escalated"              # Эскалировано к оператору
    AI_CONSULTED = "ai_consulted"        # Консультация с AI
    REJECTED = "rejected"                # Отклонено по политикам


class DecisionOutcome(Enum):
    """Результаты решений"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    ESCALATED = "escalated"


@dataclass
class DecisionRequest:
    """Запрос на принятие решения"""
    request_id: str
    service: str                    # Какой сервис
    action: str                     # Что делать (restart, scale_up, failover)
    reason: str                     # Почему нужно
    priority: int                   # 1-5 (1 = critical)
    context: Dict[str, Any]         # System state, metrics, history
    requester: str                  # Кто запрашивает (infrastructure_coordinator)
    timestamp: datetime


@dataclass
class Decision:
    """Принятое решение"""
    decision_id: str
    request_id: str
    decision_type: DecisionType
    outcome: DecisionOutcome
    action: str
    justification: str              # Почему это решение
    decided_by: str                 # system/human/ai
    decided_at: datetime
    expires_at: Optional[datetime]   # TTL решения
    metadata: Dict[str, Any]


class DecisionEngine:
    """
    Основной движок принятия решений
    """

    def __init__(
        self,
        policy_engine: PolicyEngine,
        escalation_manager: EscalationManager,
        ai_hub: AIIntelligenceHub,
        audit_logger: AuditLogger
    ):
        self.policy_engine = policy_engine
        self.escalation_manager = escalation_manager
        self.ai_hub = ai_hub
        self.audit_logger = audit_logger

    async def make_decision(
        self,
        request: DecisionRequest
    ) -> Decision:
        """
        Принимает решение на основе policies и context
        """

        # 1. Загрузить политики для сервиса
        policies = self.policy_engine.get_policies(request.service)

        # 2. Проверить auto-approval rules
        if self._can_auto_approve(request, policies):
            decision = self._auto_approve(request, policies)

        # 3. Проверить нужна ли эскалация
        elif self._requires_escalation(request, policies):
            decision = await self.escalation_manager.escalate(request)

        # 4. Сложное решение → консультация с AI
        elif self._requires_ai_consultation(request):
            decision = await self._consult_ai(request, policies)

        # 5. Требует manual approval
        elif self._requires_manual_approval(request, policies):
            decision = await self._request_approval(request)

        # 6. Default: reject (безопасность превыше)
        else:
            decision = self._reject(request, "No matching policy")

        # 7. Audit logging (ISO 22301 requirement)
        await self.audit_logger.log_decision(decision, request, policies)

        # 8. Publish decision event
        await self._publish_decision_event(decision)

        return decision

    def _can_auto_approve(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> bool:
        """
        Проверяет можно ли автоматически одобрить
        """

        auto_approval = policies.get("auto_approval", {})

        # Restart всегда allowed (если не превышен лимит попыток)
        if request.action == "restart":
            attempts = request.context.get("recovery_attempts", 0)
            max_attempts = policies.get("max_auto_attempts", 3)
            return attempts < max_attempts

        # Failover allowed для standard services
        if request.action == "failover":
            return auto_approval.get("failover_allowed", True)

        # Scale down allowed (scale up требует approval)
        if request.action == "scale_down":
            return auto_approval.get("scale_down_requires_approval", False) is False

        return False

    def _requires_escalation(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> bool:
        """
        Проверяет нужна ли эскалация
        """

        # Critical services escalate immediately
        if policies.get("escalate_immediately", False):
            return True

        # Max attempts exceeded
        attempts = request.context.get("recovery_attempts", 0)
        max_attempts = policies.get("max_auto_attempts", 3)
        if attempts >= max_attempts:
            return True

        # Pattern detected (same failure repeatedly)
        if self._detect_failure_pattern(request):
            return True

        return False

    def _requires_ai_consultation(self, request: DecisionRequest) -> bool:
        """
        Проверяет нужна ли консультация с AI
        """

        complexity_indicators = [
            "unknown issue",
            "repeated failure",
            "root cause unclear",
            "performance degradation",
            "resource optimization"
        ]

        return any(
            indicator in request.reason.lower()
            for indicator in complexity_indicators
        )

    async def _consult_ai(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> Decision:
        """
        Консультация с AI Intelligence Hub
        """

        # Route to appropriate AI tier
        ai_response = await self.ai_hub.consult(
            problem=request.reason,
            context=request.context,
            service=request.service,
            action=request.action,
            complexity="medium"  # Can be calculated
        )

        # Parse AI recommendation
        if ai_response.confidence > 0.8:
            # High confidence → auto-approve with AI justification
            return Decision(
                decision_id=generate_id(),
                request_id=request.request_id,
                decision_type=DecisionType.AI_CONSULTED,
                outcome=DecisionOutcome.APPROVED,
                action=request.action,
                justification=ai_response.reasoning,
                decided_by="ai",
                decided_at=datetime.utcnow(),
                metadata={
                    "ai_model": ai_response.model_used,
                    "confidence": ai_response.confidence,
                    "tier": ai_response.tier
                }
            )
        else:
            # Low confidence → escalate to human
            return await self.escalation_manager.escalate(
                request,
                reason=f"AI confidence too low: {ai_response.confidence}"
            )

    async def _request_approval(self, request: DecisionRequest) -> Decision:
        """
        Запрос manual approval от оператора
        """

        # Create approval request
        approval_id = generate_id()

        # Notify operators
        await self._notify_operators(request, approval_id)

        # Return pending decision
        return Decision(
            decision_id=approval_id,
            request_id=request.request_id,
            decision_type=DecisionType.REQUIRES_APPROVAL,
            outcome=DecisionOutcome.PENDING,
            action=request.action,
            justification="Awaiting manual approval",
            decided_by="system",
            decided_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30),  # 30 min timeout
            metadata={"approval_id": approval_id}
        )
```

---

### 2. Policy Engine

```python
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class PolicyEngine:
    """
    Загружает и валидирует policies из YAML
    """

    def __init__(self, policy_file: str = "policies.yaml"):
        self.policy_file = Path(policy_file)
        self.policies: Optional[Dict[str, Any]] = None
        self.last_loaded: Optional[datetime] = None
        self.load_policies()

    def load_policies(self) -> None:
        """
        Загружает policies из YAML файла
        """
        try:
            with open(self.policy_file, 'r') as f:
                self.policies = yaml.safe_load(f)
            self.last_loaded = datetime.utcnow()
            self.validate_policies()
            logger.info(f"Policies loaded from {self.policy_file}")
        except Exception as e:
            logger.error(f"Failed to load policies: {e}")
            raise

    def validate_policies(self) -> None:
        """
        Валидирует структуру policies
        """
        required_sections = [
            "recovery",
            "escalation",
            "goals",
            "decision_rules"
        ]

        for section in required_sections:
            if section not in self.policies:
                raise ValueError(f"Missing required policy section: {section}")

    def get_policies(self, service: str) -> Dict[str, Any]:
        """
        Возвращает policies для конкретного сервиса
        """

        # Check if hot reload needed (file changed)
        if self._should_reload():
            self.load_policies()

        # Look for service-specific policies
        recovery_policies = self.policies.get("recovery", {})

        # Critical services
        critical = recovery_policies.get("critical_services", {})
        if service in critical:
            return {
                **recovery_policies.get("default", {}),
                **critical[service]
            }

        # Standard services
        standard = recovery_policies.get("standard_services", {})
        if service in standard:
            return {
                **recovery_policies.get("default", {}),
                **standard[service]
            }

        # Default policies
        return recovery_policies.get("default", {})

    def _should_reload(self) -> bool:
        """
        Проверяет нужно ли перезагрузить policies (hot reload)
        """
        if not self.last_loaded:
            return True

        file_mtime = datetime.fromtimestamp(
            self.policy_file.stat().st_mtime
        )

        return file_mtime > self.last_loaded

    def get_goal(self, goal_name: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает цель из policies
        """
        goals = self.policies.get("goals", {}).get("infrastructure", {})
        return goals.get(goal_name)

    def get_threshold(self, resource: str, level: str) -> int:
        """
        Возвращает threshold для ресурса
        """
        thresholds = self.policies.get("optimization", {}).get("thresholds", {})
        resource_thresholds = thresholds.get(resource, {})
        return resource_thresholds.get(level, 80)  # default 80%
```

---

### 3. Escalation Manager

```python
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class EscalationLevel(Enum):
    """Уровни эскалации"""
    L1_OPERATOR = "l1_operator"          # Дежурный оператор
    L2_ENGINEER = "l2_engineer"          # Инженер
    L3_ARCHITECT = "l3_architect"        # Архитектор
    L4_MANAGEMENT = "l4_management"      # Менеджмент


@dataclass
class EscalationRequest:
    """Запрос на эскалацию"""
    escalation_id: str
    original_request: DecisionRequest
    escalation_level: EscalationLevel
    reason: str
    urgency: int  # 1-5
    assigned_to: Optional[str]
    created_at: datetime
    responded_at: Optional[datetime]
    resolution: Optional[str]


class EscalationManager:
    """
    Управляет эскалацией к человеку
    """

    def __init__(
        self,
        policy_engine: PolicyEngine,
        notification_service: NotificationService,
        audit_logger: AuditLogger
    ):
        self.policy_engine = policy_engine
        self.notification_service = notification_service
        self.audit_logger = audit_logger
        self.active_escalations: Dict[str, EscalationRequest] = {}

    async def escalate(
        self,
        request: DecisionRequest,
        reason: Optional[str] = None
    ) -> Decision:
        """
        Эскалирует решение к человеку
        """

        # Determine escalation level
        level = self._determine_escalation_level(request)

        # Create escalation request
        escalation = EscalationRequest(
            escalation_id=generate_id(),
            original_request=request,
            escalation_level=level,
            reason=reason or f"Max attempts exceeded for {request.service}",
            urgency=self._calculate_urgency(request),
            assigned_to=None,
            created_at=datetime.utcnow(),
            responded_at=None,
            resolution=None
        )

        # Store active escalation
        self.active_escalations[escalation.escalation_id] = escalation

        # Notify appropriate personnel
        await self._notify_escalation(escalation)

        # Audit log
        await self.audit_logger.log_escalation(escalation)

        # Return escalated decision
        return Decision(
            decision_id=escalation.escalation_id,
            request_id=request.request_id,
            decision_type=DecisionType.ESCALATED,
            outcome=DecisionOutcome.ESCALATED,
            action=request.action,
            justification=f"Escalated to {level.value}: {escalation.reason}",
            decided_by="system",
            decided_at=datetime.utcnow(),
            metadata={
                "escalation_id": escalation.escalation_id,
                "escalation_level": level.value,
                "urgency": escalation.urgency
            }
        )

    def _determine_escalation_level(
        self,
        request: DecisionRequest
    ) -> EscalationLevel:
        """
        Определяет уровень эскалации
        """

        # Critical services → L2 engineer immediately
        policies = self.policy_engine.get_policies(request.service)
        if policies.get("priority", 3) == 1:
            return EscalationLevel.L2_ENGINEER

        # Pattern detected → L2 engineer
        if self._detect_failure_pattern(request):
            return EscalationLevel.L2_ENGINEER

        # Default → L1 operator
        return EscalationLevel.L1_OPERATOR

    def _calculate_urgency(self, request: DecisionRequest) -> int:
        """
        Рассчитывает urgency (1-5, 1 = most urgent)
        """

        # Critical service = urgency 1
        if request.priority == 1:
            return 1

        # RTO/RPO violations
        policies = self.policy_engine.get_policies(request.service)
        rto = policies.get("rto", 300)
        downtime = request.context.get("downtime_seconds", 0)

        if downtime > rto:
            return 1  # RTO violated!
        elif downtime > rto * 0.8:
            return 2  # Close to RTO
        else:
            return 3  # Still within RTO

    async def _notify_escalation(self, escalation: EscalationRequest) -> None:
        """
        Отправляет уведомления об эскалации
        """

        # Get notification channels from policies
        policies = self.policy_engine.get_policies(
            escalation.original_request.service
        )
        channels = policies.get("notification_channels", ["email"])
        recipients = policies.get("notify_recipients", [])

        # Prepare message
        message = self._format_escalation_message(escalation)

        # Send via all channels
        for channel in channels:
            if channel == "email":
                await self.notification_service.send_email(
                    recipients=recipients,
                    subject=f"🚨 Escalation: {escalation.original_request.service}",
                    body=message
                )
            elif channel == "slack":
                await self.notification_service.send_slack(
                    message=message,
                    urgency=escalation.urgency
                )
            elif channel == "sms":
                await self.notification_service.send_sms(
                    recipients=recipients,
                    message=message[:160]  # SMS limit
                )

    async def respond_to_escalation(
        self,
        escalation_id: str,
        response: str,
        approved: bool,
        responder: str
    ) -> Decision:
        """
        Оператор отвечает на эскалацию
        """

        escalation = self.active_escalations.get(escalation_id)
        if not escalation:
            raise ValueError(f"Escalation {escalation_id} not found")

        # Update escalation
        escalation.responded_at = datetime.utcnow()
        escalation.resolution = response
        escalation.assigned_to = responder

        # Create decision
        decision = Decision(
            decision_id=generate_id(),
            request_id=escalation.original_request.request_id,
            decision_type=DecisionType.ESCALATED,
            outcome=DecisionOutcome.APPROVED if approved else DecisionOutcome.REJECTED,
            action=escalation.original_request.action,
            justification=f"Human decision by {responder}: {response}",
            decided_by=responder,
            decided_at=datetime.utcnow(),
            metadata={
                "escalation_id": escalation_id,
                "escalation_level": escalation.escalation_level.value
            }
        )

        # Audit log
        await self.audit_logger.log_decision(
            decision,
            escalation.original_request,
            {}
        )

        # Remove from active
        del self.active_escalations[escalation_id]

        return decision
```

---

## 🔌 API Endpoints

### Decision API

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Decision Center API", version="1.0.0")


class DecisionRequestAPI(BaseModel):
    service: str
    action: str
    reason: str
    priority: int
    context: Dict[str, Any]
    requester: str


class ApprovalResponseAPI(BaseModel):
    escalation_id: str
    approved: bool
    response: str
    responder: str


@app.post("/decision/evaluate")
async def evaluate_decision(
    request: DecisionRequestAPI,
    decision_engine: DecisionEngine = Depends(get_decision_engine)
):
    """
    Принимает решение на основе policies
    """
    decision_request = DecisionRequest(**request.dict())
    decision = await decision_engine.make_decision(decision_request)

    return {
        "decision_id": decision.decision_id,
        "outcome": decision.outcome.value,
        "action": decision.action,
        "justification": decision.justification,
        "decided_by": decision.decided_by
    }


@app.post("/decision/approve")
async def approve_decision(
    approval: ApprovalResponseAPI,
    escalation_manager: EscalationManager = Depends(get_escalation_manager)
):
    """
    Оператор одобряет/отклоняет эскалацию
    """
    decision = await escalation_manager.respond_to_escalation(
        escalation_id=approval.escalation_id,
        response=approval.response,
        approved=approval.approved,
        responder=approval.responder
    )

    return {
        "decision_id": decision.decision_id,
        "outcome": decision.outcome.value
    }


@app.get("/decision/status/{decision_id}")
async def get_decision_status(
    decision_id: str,
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """
    Получить статус решения
    """
    decision = await audit_logger.get_decision(decision_id)

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    return decision


@app.get("/escalations/active")
async def get_active_escalations(
    escalation_manager: EscalationManager = Depends(get_escalation_manager)
):
    """
    Список активных эскалаций
    """
    return {
        "escalations": [
            {
                "escalation_id": e.escalation_id,
                "service": e.original_request.service,
                "action": e.original_request.action,
                "reason": e.reason,
                "urgency": e.urgency,
                "created_at": e.created_at.isoformat()
            }
            for e in escalation_manager.active_escalations.values()
        ]
    }


@app.get("/audit/decisions")
async def query_audit_log(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service: Optional[str] = None,
    outcome: Optional[str] = None,
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """
    Запрос audit log (ISO 22301 compliance)
    """
    decisions = await audit_logger.query_decisions(
        start_date=start_date,
        end_date=end_date,
        service=service,
        outcome=outcome
    )

    return {"decisions": decisions}
```

---

## 🎯 Integration Points

### 1. Infrastructure Coordinator Integration

```python
# infrastructure/eventbus/coordination/infrastructure_coordinator.py

async def handle_health_event(self, event: Event):
    """
    При health проблеме → спросить Decision Center
    """

    if event.event_type == "infrastructure.health.degraded":
        # Request decision from Decision Center
        decision = await self.decision_center_client.evaluate_decision(
            service=event.data["service_name"],
            action="restart",  # or "failover", "scale_up"
            reason=f"Health check failed: {event.data['reason']}",
            priority=self._get_service_priority(event.data["service_name"]),
            context={
                "health_status": event.data["status"],
                "recovery_attempts": self._get_recovery_attempts(event.data["service_name"]),
                "downtime_seconds": event.data.get("downtime", 0),
                "recent_events": self._get_recent_events(event.data["service_name"])
            },
            requester="infrastructure_coordinator"
        )

        # Execute decision
        if decision["outcome"] == "approved":
            await self.auto_recovery.recover_service(
                service_name=event.data["service_name"],
                strategy=decision["action"]
            )
        elif decision["outcome"] == "escalated":
            logger.warning(
                f"Decision escalated for {event.data['service_name']}: "
                f"{decision['justification']}"
            )
            # Wait for human approval...
```

### 2. AI Intelligence Hub Integration

```python
# intelligent_core/ai_intelligence_hub/ai_router.py

async def consult(
    self,
    problem: str,
    context: Dict[str, Any],
    service: str,
    action: str,
    complexity: str = "medium"
) -> AIResponse:
    """
    Decision Center консультируется с AI
    """

    # Route to appropriate tier
    tier = self._route_to_tier(complexity, context)

    # Get AI response
    if tier == ModelTier.TIER_1:
        response = await self.tier1_client.analyze(
            prompt=self._format_prompt(problem, context),
            model="gpt-4"
        )
    elif tier == ModelTier.TIER_2:
        response = await self.tier2_client.analyze(
            prompt=self._format_prompt(problem, context),
            model="claude-3-sonnet"
        )

    # Parse and return
    return AIResponse(
        recommendation=response.recommendation,
        reasoning=response.reasoning,
        confidence=response.confidence,
        model_used=response.model,
        tier=tier.value
    )
```

---

## 📊 Monitoring & Metrics

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Decision metrics
decisions_total = Counter(
    'decision_center_decisions_total',
    'Total decisions made',
    ['service', 'action', 'outcome', 'decided_by']
)

decision_latency = Histogram(
    'decision_center_decision_latency_seconds',
    'Decision latency',
    ['service', 'decision_type']
)

# Escalation metrics
escalations_total = Counter(
    'decision_center_escalations_total',
    'Total escalations',
    ['service', 'level', 'reason']
)

escalation_response_time = Histogram(
    'decision_center_escalation_response_seconds',
    'Time to respond to escalation'
)

# AI consultation metrics
ai_consultations_total = Counter(
    'decision_center_ai_consultations_total',
    'AI consultations',
    ['tier', 'outcome']
)

ai_consultation_cost = Counter(
    'decision_center_ai_cost_dollars',
    'AI consultation cost',
    ['tier', 'model']
)
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/test_decision_engine.py

def test_auto_approve_restart():
    """Auto-approve restart within max_attempts"""
    decision = decision_engine.make_decision(
        service="redis",
        action="restart",
        recovery_attempts=2,  # < max_attempts (3)
        priority=2
    )
    assert decision.outcome == DecisionOutcome.APPROVED
    assert decision.decision_type == DecisionType.AUTO_APPROVED


def test_escalate_after_max_attempts():
    """Escalate after max_attempts exceeded"""
    decision = decision_engine.make_decision(
        service="redis",
        action="restart",
        recovery_attempts=3,  # >= max_attempts (3)
        priority=2
    )
    assert decision.outcome == DecisionOutcome.ESCALATED
    assert decision.decision_type == DecisionType.ESCALATED


def test_critical_service_immediate_escalation():
    """Critical service escalates immediately"""
    decision = decision_engine.make_decision(
        service="database",  # Critical service
        action="restart",
        recovery_attempts=0,
        priority=1
    )
    assert decision.outcome == DecisionOutcome.ESCALATED
```

---

## 📅 Implementation Timeline

### Week 1: Core Components (MVP)
- Day 1-2: Decision Engine + Policy Engine
- Day 3-4: Escalation Manager + Audit Logger
- Day 5: API endpoints
- Day 6-7: Testing + Integration with Infrastructure Coordinator

### Week 2: AI Integration & Production Ready
- Day 8-9: AI Intelligence Hub integration
- Day 10-11: Notification service (Email/Slack)
- Day 12: Monitoring & metrics
- Day 13-14: Documentation + Production deployment

---

## ✅ Acceptance Criteria

- [ ] Decision Engine делает решения на основе policies.yaml
- [ ] Escalation работает после max_attempts
- [ ] Manual approval workflow функционален
- [ ] Audit logging ISO 22301 compliant (90 days retention)
- [ ] Integration с Infrastructure Coordinator работает
- [ ] AI consultation работает для complex decisions
- [ ] Prometheus metrics экспортируются
- [ ] API endpoints протестированы
- [ ] Documentation готова

---

**Ready to implement?** 🚀

