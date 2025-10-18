# Enhanced Decision Center - Usage Examples

## Overview

Enhanced `InfrastructureDecisionCenter` теперь поддерживает:
- ✅ **AI Hub integration** (optional) - AI-ассистируемые решения
- ✅ **Prometheus metrics** (optional) - мониторинг решений
- ✅ **Backward compatible** - работает как прежде без новых параметров

---

## Example 1: Basic Usage (Unchanged)

```python
from infrastructure.policy_engine import InfrastructureDecisionCenter

# Создать как прежде - без AI, без metrics
decision_center = InfrastructureDecisionCenter()

# Использовать как прежде
decision, can_proceed = await decision_center.decide_recovery_action(
    service_name="api-gateway",
    action_type="restart",
    current_attempt=1
)

print(f"Decision: {decision.outcome.value}, Can proceed: {can_proceed}")
```

**Результат:** Работает точно так же, как старая версия.

---

## Example 2: With AI Hub (Enhanced)

```python
from infrastructure.policy_engine import InfrastructureDecisionCenter
from infrastructure.decision_center.integrations.ai_hub import AIIntelligenceHub

# Создать AI Hub
ai_hub = AIIntelligenceHub(
    tier1_enabled=False,
    tier2_enabled=False,
    tier3_enabled=True,  # Быстрый tier
    tier4_enabled=False
)

# Создать Decision Center с AI
decision_center = InfrastructureDecisionCenter(
    ai_hub=ai_hub  # Add AI consultation
)

# Использовать как прежде
decision, can_proceed = await decision_center.decide_recovery_action(
    service_name="database",
    action_type="restart",
    current_attempt=3  # AI consultation для attempt >= 2
)

# Проверить AI involvement
if decision.parameters.get('ai_enhanced'):
    print(f"🧠 AI assisted decision:")
    print(f"   Confidence: {decision.parameters['ai_confidence']:.2f}")
    print(f"   Model: {decision.parameters['ai_model']}")
```

**Результат:**
- Для attempt 1: работает как обычно
- Для attempt >= 2: консультируется с AI Hub
- AI recommendation учитывается в решении

---

## Example 3: With Prometheus Metrics (Enhanced)

```python
from infrastructure.policy_engine import InfrastructureDecisionCenter
from prometheus_client import start_http_server

# Start Prometheus metrics server
start_http_server(9090)

# Создать Decision Center с metrics
decision_center = InfrastructureDecisionCenter(
    enable_metrics=True  # Enable Prometheus
)

# Использовать как обычно
decision, can_proceed = await decision_center.decide_recovery_action(
    service_name="cache-service",
    action_type="restart",
    current_attempt=1
)

# Metrics автоматически экспортируются на :9090/metrics
```

**Prometheus Metrics:**
```
# Decision counters
decision_center_decisions_total{outcome="approved",service="cache-service",action_type="restart"} 1

# Decision duration
decision_center_decision_duration_seconds_sum{service="cache-service",action_type="restart"} 0.045
decision_center_decision_duration_seconds_count{service="cache-service",action_type="restart"} 1

# Escalations
decision_center_escalations_total{severity="high",service="database"} 2

# AI consultations
decision_center_ai_consultations_total{confidence_level="high"} 5

# Pending approvals
decision_center_pending_approvals 3
```

---

## Example 4: Full Enhanced Setup (AI + Metrics + EventBus)

```python
from infrastructure.policy_engine import InfrastructureDecisionCenter
from infrastructure.decision_center.integrations.ai_hub import AIIntelligenceHub
from infrastructure.eventbus import create_eventbus
from prometheus_client import start_http_server

# Start Prometheus
start_http_server(9090)

# Create AI Hub
ai_hub = AIIntelligenceHub(tier3_enabled=True)

# Create EventBus
eventbus = create_eventbus('redis')
await eventbus.connect()

# Create fully enhanced Decision Center
decision_center = InfrastructureDecisionCenter(
    ai_hub=ai_hub,              # AI consultation
    enable_metrics=True,        # Prometheus metrics
    eventbus=eventbus           # Event publishing
)

# Use it
decision, can_proceed = await decision_center.decide_recovery_action(
    service_name="payment-service",
    action_type="restart",
    current_attempt=2
)

print(f"✅ Decision: {decision.outcome.value}")
print(f"🧠 AI enhanced: {decision.parameters.get('ai_enhanced', False)}")

# Get stats
stats = await decision_center.get_stats()
print(f"📊 Total decisions: {stats['total_decisions']}")
print(f"🧠 AI consultations: {stats['ai_consultations']}")
print(f"✨ AI enhanced decisions: {stats['ai_enhanced_decisions']}")
```

---

## Example 5: Integration with Infrastructure Coordinator (Backward Compatible)

```python
# In infrastructure_coordinator.py

class InfrastructureCoordinator:
    def __init__(self, eventbus, config):
        # Option A: Simple (как прежде)
        self.decision_center = InfrastructureDecisionCenter()

        # Option B: Enhanced with AI
        from infrastructure.decision_center.integrations.ai_hub import AIIntelligenceHub
        self.decision_center = InfrastructureDecisionCenter(
            ai_hub=AIIntelligenceHub(tier3_enabled=True),
            enable_metrics=True,
            eventbus=eventbus
        )

    async def handle_service_failure(self, service_name, failure_type):
        # Use как прежде - API unchanged
        decision, can_proceed = await self.decision_center.decide_recovery_action(
            service_name=service_name,
            action_type="restart",
            current_attempt=self.recovery_attempts.get(service_name, 0) + 1
        )

        if can_proceed:
            await self.execute_recovery(service_name, "restart")
```

**Результат:** Infrastructure Coordinator работает без изменений, но получает AI enhancement и metrics бесплатно.

---

## Comparison: OLD vs Enhanced

### OLD (все еще работает):
```python
decision_center = InfrastructureDecisionCenter()
```
- ✅ Policy engine
- ✅ Audit logging
- ✅ Escalation workflow
- ✅ Approval workflow
- ❌ No AI
- ❌ No Prometheus metrics

### Enhanced (опционально):
```python
decision_center = InfrastructureDecisionCenter(
    ai_hub=AIIntelligenceHub(...),
    enable_metrics=True
)
```
- ✅ Policy engine
- ✅ Audit logging
- ✅ Escalation workflow
- ✅ Approval workflow
- ✅ **AI consultation** (для сложных случаев)
- ✅ **Prometheus metrics** (для мониторинга)
- ✅ **Backward compatible** (можно не использовать)

---

## When AI Consultation Happens

AI Hub консультируется автоматически когда:
1. **Multiple attempts**: `current_attempt >= 2`
2. **Escalation required**: Policy требует escalation
3. **Uncertain cases**: Policy compliance unclear

**Fallback:** Если AI Hub недоступен, решение принимается по policy как обычно.

---

## Migration Path

### Phase 1: No changes (current)
```python
# Infrastructure Coordinator uses OLD Decision Center
decision_center = InfrastructureDecisionCenter()
```

### Phase 2: Add AI (optional)
```python
# Add AI Hub, but everything else unchanged
decision_center = InfrastructureDecisionCenter(
    ai_hub=AIIntelligenceHub(tier3_enabled=True)
)
```

### Phase 3: Add Metrics (optional)
```python
# Add metrics for monitoring
decision_center = InfrastructureDecisionCenter(
    ai_hub=AIIntelligenceHub(tier3_enabled=True),
    enable_metrics=True
)
```

### Phase 4: Full integration
```python
# All features enabled
decision_center = InfrastructureDecisionCenter(
    ai_hub=AIIntelligenceHub(...),
    enable_metrics=True,
    eventbus=create_eventbus('redis'),
    db_session_factory=get_db_session_factory()
)
```

---

## Summary

**Key Points:**
- ✅ **Backward compatible** - работает как прежде
- ✅ **Optional enhancements** - AI и metrics опциональны
- ✅ **No breaking changes** - существующий код работает
- ✅ **Gradual adoption** - можно добавлять постепенно

**Next Steps:**
1. Infrastructure Coordinator продолжает работать как прежде
2. Можно добавить AI Hub когда будет готов
3. Можно добавить metrics для мониторинга
4. Можно создать REST API wrapper (следующий шаг)
