# Decision Center - AI-Driven Governance for Infrastructure Automation

**Version:** 1.0.0-MVP
**Status:** Production-ready MVP
**ISO Compliance:** ISO 22301 (BCMS)

## Overview

Decision Center is the governance layer for the AI-Driven ISO Platform, providing intelligent decision-making for infrastructure automation. It prevents infinite recovery loops, enforces policies, and ensures human oversight when needed.

### Key Features

- **Policy-Based Decisions**: YAML-configured policies with hot reload
- **Multi-Level Escalation**: L1 (Operator) → L2 (Engineer) → L3 (Architect) → L4 (Management)
- **AI Integration**: Multi-tier AI consultation (MVP: stub with heuristics, Phase 2: real AI)
- **Audit Logging**: ISO 22301 compliant audit trail with 90-day retention
- **Prometheus Metrics**: Comprehensive observability
- **FastAPI REST API**: Clean, well-documented API

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           Infrastructure Coordinator                │
│       (Requests approval for actions)               │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ POST /api/v1/decisions
                  ▼
┌─────────────────────────────────────────────────────┐
│              Decision Center API                    │
│                 (FastAPI)                           │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│            Decision Engine                          │
│                                                     │
│  ┌──────────────────────────────────────────┐     │
│  │ 1. Can auto-approve?                     │     │
│  │    ✓ restart (within max_attempts)       │     │
│  │    ✓ failover                            │     │
│  │    ✓ scale_down                          │     │
│  └──────────────────────────────────────────┘     │
│                  │                                 │
│  ┌──────────────────────────────────────────┐     │
│  │ 2. Requires escalation?                  │     │
│  │    ✓ max_attempts exceeded               │     │
│  │    ✓ critical services                   │     │
│  │    ✓ RTO violation imminent              │     │
│  └──────────────────────────────────────────┘     │
│                  │                                 │
│  ┌──────────────────────────────────────────┐     │
│  │ 3. Requires AI consultation?             │     │
│  │    ✓ unknown issues                      │     │
│  │    ✓ performance degradation             │     │
│  │    ✓ complex patterns                    │     │
│  └──────────────────────────────────────────┘     │
│                  │                                 │
│  ┌──────────────────────────────────────────┐     │
│  │ 4. Requires manual approval?             │     │
│  │    ✓ scale_up                            │     │
│  │    ✓ configuration changes               │     │
│  └──────────────────────────────────────────┘     │
│                  │                                 │
│  ┌──────────────────────────────────────────┐     │
│  │ 5. Default: REJECT (safe fallback)       │     │
│  └──────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌────────────────────┐
│  Escalation     │  │  Audit Logger      │
│  Manager        │  │  (ISO 22301)       │
└─────────────────┘  └────────────────────┘
```

## Components

### 1. Decision Engine (`core/decision_engine.py`)
Main decision-making logic. Evaluates policies and makes decisions.

**Key Methods:**
- `make_decision(request)` - Main entry point
- `_can_auto_approve()` - Check if action can be auto-approved
- `_requires_escalation()` - Check if escalation needed
- `_requires_ai_consultation()` - Check if AI needed
- `_requires_manual_approval()` - Check if manual approval needed

### 2. Policy Engine (`core/policy_engine.py`)
Loads and validates policies from `policies.yaml`.

**Features:**
- Hot reload (no restart needed)
- Policy validation
- Service-specific + default policies
- Critical vs standard services

### 3. Escalation Manager (`core/escalation_manager.py`)
Manages escalation to human operators.

**Escalation Levels:**
- **L1 Operator**: Standard operations
- **L2 Engineer**: Technical issues, repeated failures
- **L3 Architect**: Critical services, architectural changes
- **L4 Management**: Business impact, SLA violations

### 4. Audit Logger (`utils/audit_logger.py`)
ISO 22301 compliant audit logging.

**Features:**
- Immutable append-only logs
- 90-day retention
- JSON format (JSONL)
- Daily rotation

### 5. AI Intelligence Hub (`integrations/ai_hub.py`)
AI consultation integration (MVP: stub, Phase 2: real AI).

**Multi-Tier Architecture (Phase 2):**
- **Tier 1 Strategic**: GPT-4, Claude Opus ($$$, 5-15s)
- **Tier 2 Operational**: Claude Sonnet, GPT-4-mini ($$, 2-5s)
- **Tier 3 Quick**: GPT-3.5, Gemini Pro ($, <1s)
- **Tier 4 Custom**: Fine-tuned model (Free, <500ms)

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

### Configuration

1. **Policies**: Edit `policies.yaml` to configure service policies
2. **Environment Variables**:
   ```bash
   DECISION_CENTER_LOG_DIR=/var/log/decision_center
   DECISION_CENTER_RETENTION_DAYS=90
   DECISION_CENTER_POLICY_FILE=policies.yaml
   ```

## Running

### Development

```bash
cd infrastructure/decision_center
python -m api.main
```

Server runs on `http://localhost:8080`

### Production

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8080 --workers 4
```

### Docker (Future)

```bash
docker run -p 8080:8080 \
  -v /path/to/policies.yaml:/app/policies.yaml \
  -v /var/log/decision_center:/var/log/decision_center \
  decision-center:latest
```

## API Endpoints

### Core Endpoints

#### `POST /api/v1/decisions`
Request a decision

**Request:**
```json
{
  "service": "database",
  "action": "restart",
  "reason": "High memory usage detected",
  "priority": 2,
  "context": {
    "recovery_attempts": 1,
    "downtime_seconds": 120,
    "memory_usage_percent": 95
  },
  "requester": "infrastructure_coordinator"
}
```

**Response:**
```json
{
  "decision_id": "uuid",
  "request_id": "uuid",
  "decision_type": "auto_approved",
  "outcome": "approved",
  "action": "restart",
  "justification": "Auto-approved by policy: restart within limits. Attempts: 1/3",
  "decided_by": "system",
  "decided_at": "2024-01-15T10:30:45Z",
  "expires_at": null,
  "metadata": {
    "policy_version": "1.0",
    "auto_approval_rule": "restart_allowed"
  }
}
```

#### `GET /api/v1/escalations`
List active escalations

#### `POST /api/v1/escalations/{id}/respond`
Respond to escalation

**Request:**
```json
{
  "approved": true,
  "operator": "john.doe@company.com",
  "resolution": "Approved restart after reviewing metrics"
}
```

#### `GET /api/v1/policies/{service}`
Get service policies

#### `POST /api/v1/policies/reload`
Reload policies (hot reload)

#### `GET /api/v1/audit/history/{service}`
Get decision history

#### `GET /metrics`
Prometheus metrics

## Metrics

Decision Center exposes Prometheus metrics at `/metrics`:

### Decision Metrics
- `decision_center_decisions_total` - Total decisions by service, action, type, outcome
- `decision_center_decision_latency_seconds` - Decision latency

### Escalation Metrics
- `decision_center_escalations_total` - Total escalations by level, urgency
- `decision_center_escalation_response_time_seconds` - Response time
- `decision_center_active_escalations` - Active escalations by level

### AI Metrics
- `decision_center_ai_consultations_total` - AI consultations by tier
- `decision_center_ai_consultation_latency_seconds` - AI latency
- `decision_center_ai_confidence` - AI confidence scores

### Audit Metrics
- `decision_center_audit_logs_written_total` - Audit logs written
- `decision_center_audit_log_write_errors_total` - Audit errors

## Policies Configuration

Edit `policies.yaml` to configure decision policies.

### Example Policy

```yaml
critical_services:
  database:
    max_auto_attempts: 2
    rto: 300  # seconds
    rpo: 3600  # seconds
    escalate_immediately: false
    critical: true
    auto_approval:
      failover_allowed: true
      scale_up_requires_approval: true
      scale_down_requires_approval: false
      configuration_change_requires_approval: true
```

### Policy Fields

- **max_auto_attempts**: Max automatic restart attempts before escalation
- **rto**: Recovery Time Objective (seconds)
- **rpo**: Recovery Point Objective (seconds)
- **escalate_immediately**: Skip auto-approval, escalate immediately
- **critical**: Mark as critical service
- **auto_approval**: Auto-approval rules for actions

## Integration with Infrastructure Coordinator

Infrastructure Coordinator calls Decision Center before executing any action:

```python
# Infrastructure Coordinator pseudocode
async def restart_service(service_name):
    # 1. Request decision
    decision = await decision_center.request_decision(
        service=service_name,
        action="restart",
        reason="High memory usage",
        priority=2,
        context={
            "recovery_attempts": self.recovery_attempts,
            "downtime_seconds": self.downtime,
            "memory_usage_percent": 95
        }
    )

    # 2. Check outcome
    if decision.outcome == "approved":
        # Execute restart
        await self.execute_restart(service_name)

    elif decision.outcome == "pending":
        # Wait for manual approval
        await self.wait_for_approval(decision.decision_id)

    elif decision.outcome == "escalated":
        # Escalated to operator, wait
        logger.warning(f"Decision escalated: {decision.justification}")

    elif decision.outcome == "rejected":
        # Don't execute, log reason
        logger.error(f"Decision rejected: {decision.justification}")
```

## Testing

### Run Tests

```bash
pytest tests/ -v
```

### Example Test

```python
import pytest
from models.decision import DecisionRequest
from core.decision_engine import DecisionEngine
from core.policy_engine import PolicyEngine

@pytest.mark.asyncio
async def test_auto_approve_restart():
    # Setup
    policy_engine = PolicyEngine()
    decision_engine = DecisionEngine(policy_engine)

    # Request
    request = DecisionRequest.create(
        service="redis",
        action="restart",
        reason="High memory",
        context={"recovery_attempts": 1}
    )

    # Execute
    decision = await decision_engine.make_decision(request)

    # Assert
    assert decision.outcome.value == "approved"
    assert decision.decision_type.value == "auto_approved"
```

## Audit Logs

Audit logs are written to `/var/log/decision_center/audit-YYYY-MM-DD.jsonl`

### Example Audit Log Entry

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "event": "decision_made",
  "decision_id": "uuid",
  "request_id": "uuid",
  "service": "database",
  "action": "restart",
  "decision_type": "auto_approved",
  "outcome": "approved",
  "decided_by": "system",
  "justification": "Auto-approved by policy...",
  "priority": 2,
  "requester": "infrastructure_coordinator",
  "context": {...},
  "policies_applied": {...},
  "metadata": {...}
}
```

## Troubleshooting

### Decision Rejected Unexpectedly

1. Check policies: `GET /api/v1/policies/{service}`
2. Check audit logs: `GET /api/v1/audit/history/{service}`
3. Review decision justification

### Escalations Not Working

1. Check active escalations: `GET /api/v1/escalations`
2. Verify notification handler configured
3. Check escalation logs in audit trail

### Policy Changes Not Applied

1. Reload policies: `POST /api/v1/policies/reload`
2. Check validation errors in logs
3. Verify `policies.yaml` syntax

## Future Enhancements (Phase 2)

1. **Real AI Integration**
   - OpenAI API integration
   - Anthropic Claude integration
   - Local LLM support
   - Custom model training

2. **Database Storage**
   - PostgreSQL for decisions, escalations, audit logs
   - Query optimization
   - Historical analytics

3. **Notification System**
   - Email notifications
   - Slack integration
   - SMS alerts
   - PagerDuty integration

4. **UI Dashboard**
   - Real-time decision monitoring
   - Escalation management UI
   - Policy editor
   - Analytics dashboards

5. **Advanced Features**
   - A/B testing for policies
   - Machine learning for policy optimization
   - Cost optimization algorithms
   - RTO/RPO prediction

## Contributing

Decision Center is part of the AI-Driven ISO Platform.

For questions or issues, contact the platform team.

## License

Proprietary - Internal Use Only
