# Decision Center - Developer Guide

Complete guide for developers integrating with Decision Center.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [API Integration](#api-integration)
4. [Adding New Services](#adding-new-services)
5. [Custom Policies](#custom-policies)
6. [EventBus Integration](#eventbus-integration)
7. [Testing](#testing)
8. [Development Workflow](#development-workflow)
9. [Architecture Deep Dive](#architecture-deep-dive)

---

## Overview

### What is Decision Center?

Decision Center is an AI-driven decision-making engine that automates infrastructure operations while maintaining safety through:

- **Multi-tier AI consultation** (Claude Opus/Sonnet/Haiku)
- **Policy-based guardrails**
- **Multi-level escalation** (L1-L4)
- **Deep AI integration** (via EventBus to AI Orchestrator)
- **Audit trail** for compliance

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Application                         │
│         (Infrastructure Coordinator, Monitoring)            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST /api/v1/decisions
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Decision Center API                       │
│  ┌───────────┐  ┌──────────┐  ┌────────────┐  ┌─────────┐ │
│  │ Decision  │→ │ Policy   │→ │ AI Hub     │→ │Escalate │ │
│  │ Engine    │  │ Engine   │  │ (Tiers 1-3)│  │ Manager │ │
│  └───────────┘  └──────────┘  └────────────┘  └─────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ EventBus (optional deep AI)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 AI Orchestrator (Intelligent Core)          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ Multi-Expert│  │ Predictive  │  │ Learning from    │   │
│  │ Consultation│  │ Intelligence│  │ Outcomes         │   │
│  └─────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

1. **Request Decision** - POST to `/api/v1/decisions`
2. **Respond to Escalation** - POST to `/api/v1/escalations/{id}/respond`
3. **Monitor Status** - GET `/health`, `/metrics`
4. **Manage Policies** - GET/POST `/api/v1/policies/*`

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (for local development)
- Access to Decision Center API
- API credentials (if authentication enabled)

### Local Development Setup

**1. Clone and Setup**

```bash
cd infrastructure/decision_center

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

**2. Start Dependencies (Docker)**

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Wait for services to be ready
docker-compose ps
```

**3. Run Decision Center**

```bash
# Run directly
uvicorn api.main:app --reload --port 8080

# Or via Docker
docker-compose up decision-center
```

**4. Verify**

```bash
curl http://localhost:8080/health

# Expected:
{
  "status": "healthy",
  "version": "1.0.0-mvp",
  "components": {...}
}
```

---

## API Integration

### Making a Decision Request

**Basic Request:**

```python
import httpx

async def request_decision():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://decision-center:8080/api/v1/decisions",
            json={
                "service": "database",
                "action": "restart",
                "reason": "High memory usage detected (95%)",
                "priority": 2,  # 1=critical, 5=low
                "context": {
                    "memory_percent": 95,
                    "cpu_percent": 45,
                    "recovery_attempts": 1,
                    "downtime_seconds": 120
                },
                "requester": "infrastructure_coordinator"
            }
        )

        decision = response.json()
        print(f"Decision: {decision['outcome']}")
        print(f"Justification: {decision['justification']}")

        return decision
```

**Response Structure:**

```json
{
  "decision_id": "dec_abc123",
  "request_id": "req_xyz789",
  "decision_type": "automated",
  "outcome": "approved",
  "action": "restart",
  "justification": "High memory usage (95%) detected. AI confidence: 0.92. Restart approved to restore service health.",
  "decided_by": "ai_tier2_sonnet",
  "decided_at": "2025-10-16T10:30:00Z",
  "expires_at": "2025-10-16T11:30:00Z",
  "metadata": {
    "ai_confidence": 0.92,
    "policy_matched": true,
    "consultation_time_ms": 234
  }
}
```

**Outcome Values:**

- `approved` - Action is safe, proceed
- `rejected` - Action is unsafe, do not proceed
- `escalated` - Human review required, wait for operator response

### Handling Escalations

**When `outcome == "escalated"`:**

```python
async def handle_escalation(decision):
    escalation_id = decision['metadata']['escalation_id']

    # Poll for resolution
    while True:
        response = await client.get(
            f"http://decision-center:8080/api/v1/escalations/{escalation_id}"
        )
        escalation = response.json()

        if escalation['status'] == 'resolved':
            # Operator approved or rejected
            print(f"Operator decision: {escalation['resolution']}")
            return escalation['approved']

        # Wait before polling again
        await asyncio.sleep(30)
```

**Better: Use Webhooks (Future)**

```python
# Register webhook for escalation updates
await client.post(
    "http://decision-center:8080/api/v1/webhooks",
    json={
        "event": "escalation.resolved",
        "url": "https://your-service/webhook/escalation"
    }
)
```

### Error Handling

```python
async def request_decision_with_retry():
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = await client.post(
                "http://decision-center:8080/api/v1/decisions",
                json={...},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                # Decision Center unavailable, use fallback
                return fallback_decision()
            elif e.response.status_code == 400:
                # Bad request, fix and retry
                raise
            else:
                # Retry on 500s
                await asyncio.sleep(2 ** attempt)

        except httpx.TimeoutException:
            # Decision Center slow, retry
            await asyncio.sleep(2 ** attempt)

    # All retries failed, use fallback
    return fallback_decision()
```

---

## Adding New Services

### Step 1: Define Service Policy

Create or update `policies.yaml`:

```yaml
services:
  my-new-service:
    # Basic settings
    auto_approve: true
    confidence_threshold: 0.80
    max_recovery_attempts: 3

    # Allowed actions
    allowed_actions:
      - restart
      - scale_up
      - scale_down
      - rollback

    # Blocked actions (safety)
    blocked_actions:
      - delete
      - destroy
      - drop_data

    # Escalation triggers
    escalation_triggers:
      - type: repeated_failure
        threshold: 2
        window_minutes: 30
      - type: downtime
        threshold_minutes: 10
      - type: data_risk
        severity: any

    # Constraints
    constraints:
      max_downtime_minutes: 15
      requires_backup: true
      rto_minutes: 5
      rpo_minutes: 0

    # Metadata
    criticality: high  # low, medium, high, critical
    owner: team-backend
    runbook_url: https://wiki.company.com/runbooks/my-service
```

### Step 2: Reload Policies

```bash
curl -X POST http://decision-center:8080/api/v1/policies/reload
```

### Step 3: Test Decision Request

```python
decision = await request_decision(
    service="my-new-service",
    action="restart",
    reason="Test decision for new service",
    context={"test": True}
)

assert decision['outcome'] in ['approved', 'rejected', 'escalated']
```

### Step 4: Monitor Behavior

Check Grafana dashboard for:
- Decision approval rate
- Escalation frequency
- AI confidence scores

Adjust policy if needed.

---

## Custom Policies

### Policy Components

**1. Auto-Approve Settings**

```yaml
auto_approve: true  # Enable automatic approvals
confidence_threshold: 0.85  # AI must be 85%+ confident
```

**2. Action Control**

```yaml
allowed_actions:
  - restart      # Safe, non-destructive
  - scale_up     # Adds resources
  - scale_down   # Removes resources (if safe)
  - rollback     # Reverts to previous version

blocked_actions:
  - delete       # Destructive
  - drop_database  # Data loss
```

**3. Escalation Rules**

```yaml
escalation_triggers:
  # Repeated failures
  - type: repeated_failure
    threshold: 2           # After 2 failures
    window_minutes: 30     # Within 30 minutes
    escalation_level: L2   # Skip to L2

  # Extended downtime
  - type: downtime
    threshold_minutes: 10  # 10 minutes down
    escalation_level: L3   # Critical

  # Data risk
  - type: data_risk
    severity: high         # Any high data risk
    escalation_level: L4   # Security team
```

**4. Constraints**

```yaml
constraints:
  max_downtime_minutes: 15  # RTO target
  requires_backup: true     # Must have backup before action
  rto_minutes: 5            # Recovery time objective
  rpo_minutes: 0            # Recovery point objective (no data loss)
```

### Advanced Policy Patterns

**Pattern 1: Canary Deployment Safety**

```yaml
canary-service:
  auto_approve: true
  confidence_threshold: 0.90  # Higher bar

  allowed_actions:
    - deploy_canary
    - promote_canary
    - rollback_canary

  constraints:
    canary_percentage_max: 10  # Max 10% traffic to canary
    rollback_on_error_rate: 0.01  # Rollback if 1% errors
```

**Pattern 2: Database Schema Migrations**

```yaml
database-migrations:
  auto_approve: false  # Always escalate

  escalation_triggers:
    - type: schema_change
      always_escalate: true
      assigned_to: dba-team

  constraints:
    requires_backup: true
    requires_dry_run: true
    maintenance_window_only: true
```

**Pattern 3: Multi-Region Failover**

```yaml
global-load-balancer:
  auto_approve: true
  confidence_threshold: 0.95

  allowed_actions:
    - failover_region
    - drain_traffic

  escalation_triggers:
    - type: multi_region_impact
      regions_affected: 2
      escalation_level: L4

  constraints:
    max_concurrent_failovers: 1
    cooldown_minutes: 60
```

---

## EventBus Integration

### Deep AI Integration Architecture

When EventBus is enabled, Decision Center publishes consultation requests to AI Orchestrator for deeper analysis:

```
Decision Center → EventBus → AI Orchestrator
                            ↓
                     Multi-Expert Consultation
                     - Database Specialist
                     - Performance Expert
                     - Security Specialist
                     - BCM Consultant
                            ↓
                     Predictive Intelligence
                     - Failure forecasting
                     - Pattern detection
                     - RTO/RPO risk
                            ↓
                EventBus → Decision Center
```

### Subscribing to Decision Events

**Your service can subscribe to decision events:**

```python
from infrastructure.eventbus import create_eventbus, Event

async def main():
    # Connect to EventBus
    eventbus = create_eventbus('redis')
    await eventbus.connect()

    # Subscribe to decision events
    async def handle_decision(event: Event):
        data = event.data
        print(f"Decision made for {data['service']}: {data['outcome']}")

        # Your logic here
        if data['outcome'] == 'approved':
            await execute_action(data['service'], data['action'])

    await eventbus.subscribe(
        'infrastructure.decision.made',
        handle_decision
    )

    # Keep running
    await asyncio.sleep(3600)
```

### Publishing Custom Events

**Notify Decision Center of action outcomes:**

```python
# After executing approved action
await eventbus.publish(Event.create(
    event_type='infrastructure.action.completed',
    data={
        'decision_id': decision['decision_id'],
        'service': 'database',
        'action': 'restart',
        'success': True,
        'duration_seconds': 45,
        'metrics': {
            'memory_after': 60,
            'cpu_after': 30
        }
    },
    tenant_id='default'
))
```

**This enables AI learning from outcomes.**

---

## Testing

### Unit Tests

```python
import pytest
from decision_center.core.decision_engine import DecisionEngine
from decision_center.models.decision import DecisionRequest

@pytest.mark.asyncio
async def test_auto_approve_restart():
    """Test auto-approval of database restart with high memory"""

    # Setup
    engine = DecisionEngine(...)

    # Create request
    request = DecisionRequest.create(
        service="database",
        action="restart",
        reason="High memory usage",
        priority=2,
        context={
            "memory_percent": 95,
            "recovery_attempts": 0
        }
    )

    # Make decision
    decision = await engine.make_decision(request)

    # Assert
    assert decision.outcome == DecisionOutcome.APPROVED
    assert decision.decided_by.startswith("ai_tier")
    assert decision.metadata['ai_confidence'] > 0.80
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_decision_api_e2e():
    """End-to-end test of decision API"""

    async with httpx.AsyncClient() as client:
        # Request decision
        response = await client.post(
            "http://localhost:8080/api/v1/decisions",
            json={
                "service": "database",
                "action": "restart",
                "reason": "Test",
                "context": {"test": True}
            }
        )

        assert response.status_code == 200
        decision = response.json()

        assert decision['outcome'] in ['approved', 'rejected', 'escalated']
        assert 'decision_id' in decision
        assert 'justification' in decision
```

### Load Testing

```python
import asyncio
from locust import HttpUser, task, between

class DecisionCenterUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def request_decision(self):
        self.client.post(
            "/api/v1/decisions",
            json={
                "service": "test-service",
                "action": "restart",
                "reason": "Load test",
                "context": {}
            }
        )
```

Run:
```bash
locust -f load_test.py --host=http://decision-center:8080
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_decision_engine.py::test_auto_approve_restart -v

# Run with coverage
pytest tests/ --cov=decision_center --cov-report=html

# Run E2E tests
pytest tests/test_api_manual.py -v -s
```

---

## Development Workflow

### Making Changes

**1. Create Feature Branch**

```bash
git checkout -b feature/add-new-policy
```

**2. Make Changes**

```python
# Edit code
vim decision_center/core/decision_engine.py

# Update tests
vim tests/test_decision_engine.py
```

**3. Run Tests Locally**

```bash
# Unit tests
pytest tests/ -v

# Lint
flake8 decision_center/

# Type check
mypy decision_center/
```

**4. Test in Docker**

```bash
# Build image
docker-compose build decision-center

# Run
docker-compose up decision-center

# Test
curl http://localhost:8080/health
```

**5. Commit and Push**

```bash
git add .
git commit -m "feat: Add new escalation policy for schema changes"
git push origin feature/add-new-policy
```

**6. Create Pull Request**

- Include tests
- Update documentation
- Get review from team

### Debugging

**Local Debugging:**

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Run with debugger
python -m pdb api/main.py
```

**Remote Debugging (K8s):**

```bash
# Port-forward Decision Center
kubectl port-forward -n decision-center pod/decision-center-xxx 8080:8080

# Attach debugger
# Use IDE remote debugging (VS Code, PyCharm)
```

**Verbose Logging:**

```bash
# Set LOG_LEVEL=DEBUG in .env
LOG_LEVEL=DEBUG uvicorn api.main:app --reload
```

---

## Architecture Deep Dive

### Decision Flow

```
1. Request arrives at /api/v1/decisions
   ↓
2. DecisionEngine.make_decision()
   ↓
3. PolicyEngine.check_policy()
   - Load service policies
   - Check allowed/blocked actions
   - Validate constraints
   ↓
4. AIHub.consult() [if EventBus disabled]
   OR
   EventBus → AI Orchestrator [if EventBus enabled]
   ↓
5. Decision outcome:
   - APPROVED → AuditLogger → Response
   - REJECTED → AuditLogger → Response
   - ESCALATED → EscalationManager → Response
   ↓
6. Metrics updated (Prometheus)
```

### Component Responsibilities

**DecisionEngine:**
- Orchestrates decision-making flow
- Enforces business logic
- Manages decision lifecycle

**PolicyEngine:**
- Loads and validates policies
- Checks action permissions
- Applies constraints

**AIHub:**
- Routes to appropriate AI tier
- Handles fallback to heuristics
- Manages API calls to Anthropic

**EscalationManager:**
- Creates escalation records
- Tracks SLA timers
- Notifies operators

**AuditLogger:**
- Logs all decisions
- Provides audit trail
- Enables analytics

### Data Models

**DecisionRequest:**
```python
@dataclass
class DecisionRequest:
    request_id: str
    service: str
    action: str
    reason: str
    priority: int  # 1-5
    context: Dict[str, Any]
    requester: str
    created_at: datetime
```

**Decision:**
```python
@dataclass
class Decision:
    decision_id: str
    request_id: str
    decision_type: DecisionType  # automated, manual, policy
    outcome: DecisionOutcome  # approved, rejected, escalated
    action: str
    justification: str
    decided_by: str
    decided_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]
```

### Extension Points

**Custom AI Provider:**

```python
class CustomAIProvider:
    async def consult(self, prompt: str, context: Dict) -> AIResponse:
        # Your custom AI logic
        pass

# Register
ai_hub = AIIntelligenceHub(
    custom_provider=CustomAIProvider()
)
```

**Custom Escalation Handler:**

```python
class SlackEscalationHandler:
    async def notify(self, escalation: Escalation):
        # Send to Slack
        await slack_client.post_message(
            channel="#ops-escalations",
            text=f"Escalation {escalation.escalation_id}: {escalation.reason}"
        )

# Register
escalation_manager.add_handler(SlackEscalationHandler())
```

**Custom Metrics:**

```python
from prometheus_client import Counter

custom_metric = Counter(
    'custom_decisions_total',
    'Custom decision metric',
    ['service', 'result']
)

# Use in decision flow
custom_metric.labels(service=service, result=outcome).inc()
```

---

## Best Practices

### API Integration

1. **Always handle escalations**: Don't assume instant approval
2. **Implement retries**: Decision Center may be temporarily unavailable
3. **Provide rich context**: More context = better AI decisions
4. **Monitor decision patterns**: Track approval/rejection rates
5. **Use appropriate priorities**: P1 for critical, P5 for routine

### Policy Design

1. **Start conservative**: Lower confidence thresholds initially
2. **Monitor and adjust**: Review decision patterns weekly
3. **Document reasoning**: Add comments explaining policy choices
4. **Version control**: Commit policy changes to git
5. **Test before production**: Validate policies in staging

### Testing

1. **Test all outcomes**: Approved, rejected, escalated
2. **Test error cases**: API failures, timeouts, invalid data
3. **Load test**: Ensure system handles peak load
4. **Integration test**: Test full flow end-to-end
5. **Monitor in production**: Use canary deployments

---

## Troubleshooting

### Common Issues

**Issue: All decisions escalate**
- Check AI API key is set correctly
- Verify Anthropic API is reachable
- Check confidence thresholds in policies

**Issue: Decisions too slow**
- Check AI API latency in metrics
- Verify database connection pool
- Review EventBus performance

**Issue: Policies not loading**
- Check `policies.yaml` syntax (valid YAML)
- Verify file path in configuration
- Check logs for policy parse errors

### Getting Help

- **Documentation**: `/docs` folder
- **API Docs**: http://decision-center:8080/docs
- **Slack**: #decision-center-dev
- **Issues**: GitHub Issues

---

## Resources

- [Operator Runbook](runbooks/OPERATOR_RUNBOOK.md)
- [API Reference](INTEGRATION_GUIDE.md)
- [Architecture](DECISION_CENTER_SPEC.md)
- [AI Integration](AI_INTEGRATION_README.md)

**Document Version:** 1.0
**Last Updated:** 2025-10-16
**Maintained by:** Infrastructure Team
