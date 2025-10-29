# Orchestrator Service Routes Inventory

## Service Information
- **Base URL**: http://localhost:8002
- **Framework**: FastAPI
- **Dependencies**: Redis (async pub/sub), EventBus, Odoo
- **AI Engine**: Rule-based with OpenAI/LangChain ready

## API Endpoints

### Health & Status
| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/health` | Service health check | `{"status": "healthy", "service": "orchestrator"}` |

### AI Recommendations
| Method | Path | Description | Request/Response |
|--------|------|-------------|------------------|
| POST | `/api/recommendations` | Get AI recommendations | Body: RecommendationRequest |

**RecommendationRequest Schema:**
```json
{
  "context": "string",
  "data": {},
  "tenant_id": "string",
  "user_id": "string"
}
```

**RecommendationResponse Schema:**
```json
{
  "recommendation": "string",
  "confidence": 0.85,
  "reasoning": "string",
  "alternatives": []
}
```

### Audit Management
| Method | Path | Description | Request/Response |
|--------|------|-------------|------------------|
| POST | `/api/audit/summarize` | Summarize audit evidence | Body: AuditSummaryRequest |

**AuditSummaryRequest Schema:**
```json
{
  "audit_id": "string",
  "evidence": [],
  "tenant_id": "string"
}
```

**AuditSummaryResponse Schema:**
```json
{
  "summary": "string",
  "findings": [],
  "recommendations": [],
  "capa_items": []
}
```

### AI Decision Management
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET | `/api/ai/decisions/pending` | Get pending decisions | Query: tenant_id |
| POST | `/api/ai/decisions/{decision_id}/approve` | Approve AI decision | Path: decision_id |
| POST | `/api/ai/decisions/{decision_id}/reject` | Reject AI decision | Path: decision_id |

**AIDecision Schema:**
```json
{
  "id": "string",
  "type": "bcp_generation|incident_response|audit_preparation",
  "title": "string",
  "description": "string",
  "recommendation": "string",
  "confidence": 0.92,
  "status": "pending|approved|rejected",
  "created_at": "datetime",
  "tenant_id": "string",
  "data": {}
}
```

### Odoo Integration
| Method | Path | Description | Actions |
|--------|------|-------------|---------|
| POST | `/api/callback/odoo` | Send results to Odoo | Actions: update_plan, update_incident, create_capa |

## Extended API (Workflow Management)

### Event Management
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/orchestrator/events/publish` | Publish event |
| GET | `/api/v1/orchestrator/events/{tenant_id}` | Get tenant events |
| GET | `/api/v1/orchestrator/events/{tenant_id}/stats` | Event statistics |

### Workflow Triggers
| Method | Path | Description | Triggers |
|--------|------|-------------|----------|
| POST | `/api/v1/orchestrator/workflows/bia/start` | Start BIA workflow | BIA analysis |
| POST | `/api/v1/orchestrator/workflows/incident/report` | Report incident | Response generation |
| POST | `/api/v1/orchestrator/workflows/audit/start` | Start audit | Preparation tasks |
| POST | `/api/v1/orchestrator/workflows/pdca/start` | Start PDCA cycle | Full cycle |

### AI Orchestration
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/orchestrator/ai/decisions/{tenant_id}` | Decision history |
| GET | `/api/v1/orchestrator/ai/decisions/{tenant_id}/pending` | Pending approvals |
| POST | `/api/v1/orchestrator/ai/decisions/approve` | Approve/reject decisions |
| GET | `/api/v1/orchestrator/ai/rules` | Get orchestration rules |

## Event Handlers

### Subscribed Events
The orchestrator listens to `bcm.*` pattern via Redis pub/sub:

| Event Type | Handler | Auto-Trigger |
|------------|---------|--------------|
| `bcm.bia.completed` | `handle_bia_completed()` | BCP generation |
| `bcm.incident.opened` | `handle_incident_opened()` | Response checklist |
| `bcm.incident.reported` | `handle_incident_opened()` | Response checklist |
| `bcm.audit.initiated` | `handle_audit_initiated()` | Preparation recommendations |
| `bcm.training.scheduled` | `handle_training_scheduled()` | Training materials |
| `bcm.plan.draft_requested` | - | Plan draft generation |
| `bcm.kpi.calculated` | - | KPI recommendations |

## Orchestration Rules

### Predefined Rules (5 active)
1. **auto_generate_bcp** 
   - Trigger: BIA completion
   - Confidence: 0.92
   - Action: Generate BCP from BIA

2. **incident_response**
   - Trigger: High/critical incidents
   - Confidence: 0.88
   - Action: Generate response checklist

3. **schedule_overdue_exercise**
   - Trigger: >90 days since last exercise
   - Confidence: 0.85
   - Action: Schedule exercise

4. **compliance_analysis**
   - Trigger: Audit completion
   - Confidence: 0.87
   - Action: Analyze compliance gaps

5. **schedule_training**
   - Trigger: Plan approval
   - Confidence: 0.83
   - Action: Schedule training

## External Service Calls

### Odoo Integration
Base URL: `ODOO_URL` environment variable

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/bcm/plan/generate_from_bia` | POST | Generate BCP from BIA |
| `/bcm/incident/update_checklist` | POST | Update incident checklist |
| `/bcm/plan/update` | POST | Update plan |
| `/bcm/incident/update` | POST | Update incident |
| `/bcm/capa/create` | POST | Create CAPA |

### EventBus Integration
Base URL: `EVENTBUS_URL` environment variable

| Event Published | When |
|-----------------|------|
| `bcm.ai.decision.created` | New AI decision |
| `bcm.ai.decision.approved` | Decision approved |
| `bcm.ai.decision.rejected` | Decision rejected |
| `bcm.incident.checklist_generated` | Checklist created |
| `bcm.plan.draft_generated` | Plan draft ready |
| `bcm.kpi.recommendations` | KPI recommendations |

## AI Decision Logic

### Decision Types & Confidence
- **BCP Generation**: 0.92 confidence
- **Incident Response**: 0.88 confidence
- **Audit Preparation**: 0.85 confidence

### Context-Aware Logic
1. **BIA Context**: Prioritize RTO < 4 hours
2. **Incident Context**: Activate response team
3. **Audit Context**: Prepare documentation
4. **Default**: Review BCM status

### KPI Thresholds
- BIA Coverage < 80% → Trigger analysis
- Plans up-to-date < 70% → Trigger review
- CAPA on-time < 85% → Trigger escalation

## Background Tasks

### Async Processing
- Decision execution after approval
- Event publishing to EventBus
- Odoo callback execution
- Redis pub/sub monitoring

### Workflow States
- Decisions tracked in `pending_decisions` dict
- Event correlation via `correlation_id`
- Audit trail for all AI decisions

## Configuration

### Environment Variables
- `REDIS_URL` - Default: redis://localhost:6379
- `EVENTBUS_URL` - Default: http://localhost:8001
- `ODOO_URL` - Default: http://localhost:8069
- `OPENAI_API_KEY` - For LLM integration (optional)
- `CORS_ORIGINS` - Default: http://localhost:8081,http://localhost:8069

### Dependencies
- FastAPI 0.104.1
- Redis 5.0.1
- Pydantic 2.5.0
- HTTPX 0.25.2
- OpenAI 1.3.0 (configured)
- LangChain 0.0.340 (configured)

## PDCA Workflow

### Cycle Management
- **PLAN**: Context import → BIA → Planning
- **DO**: Implementation → Training → Exercises
- **CHECK**: Monitoring → Audits → KPIs
- **ACT**: Management review → Improvements

### Workflow Integration
- Event-driven state transitions
- Automatic next-step recommendations
- Progress tracking per tenant
