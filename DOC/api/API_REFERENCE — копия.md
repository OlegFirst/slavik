# Platform Services - API Reference

**Last Updated:** 2025-10-08
**Total API Endpoints:** 735+
**API Version:** v1
**Protocol:** REST (HTTP/HTTPS)
**Format:** JSON
**Authentication:** JWT (RS256)
**Documentation:** OpenAPI/Swagger (auto-generated)

---

## Quick Access

All services provide interactive API documentation at:
```
http://localhost:{PORT}/docs
```

### Core BCM Services
- [Planning Service](#1-planning-service-api) - http://localhost:8011/docs
- [BIA Service](#2-bia-service-api) - http://localhost:8012/docs
- [Governance Service](#3-governance-service-api) - http://localhost:8013/docs
- [Compliance Service](#4-compliance-service-api) - http://localhost:8014/docs
- [Learning Service](#5-learning-service-api) - http://localhost:8021/docs
- [Validation Service](#6-validation-service-api) - http://localhost:8022/docs
- [Plans Service](#7-plans-service-api) - http://localhost:8023/docs
- [Documents Service](#8-documents-service-api) - http://localhost:8024/docs
- [Risk Service](#9-risk-service-api) - http://localhost:8040/docs
- [Response Service](#10-response-service-api) - http://localhost:8041/docs

### Intelligence Services
- [Learning Service](#5-learning-service-api) - http://localhost:8021/docs
- [Living Docs](#11-living-docs-api) - http://localhost:8034/docs
- [BCM Coordination](#12-bcm-coordination-api) - http://localhost:8070/docs

---

## Authentication

### Development Mode
For development, use the `X-Dev-User` header:

```bash
curl -X GET http://localhost:8011/api/v1/strategies \
  -H "X-Dev-User: user123|tenant456|admin"
```

### Production Mode
JWT Bearer token required:

```bash
curl -X GET http://localhost:8011/api/v1/strategies \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### JWT Token Structure
```json
{
  "user_id": "uuid",
  "tenant_id": "uuid",
  "role": "admin|user|viewer",
  "exp": 1234567890
}
```

---

## Common Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Common Headers

### Request Headers
```
Content-Type: application/json
Authorization: Bearer {token}
X-Request-ID: {uuid}  (optional, for tracing)
X-Tenant-ID: {uuid}   (optional, overrides JWT tenant)
```

### Response Headers
```
Content-Type: application/json
X-Request-ID: {uuid}
X-Response-Time: {milliseconds}
```

---

## Pagination

All list endpoints support pagination:

### Query Parameters
```
?page=1
&page_size=20
&sort_by=created_at
&sort_order=desc
```

### Response Format
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

---

## 1. Planning Service API

**Base URL:** `http://localhost:8011/api/v1`
**ISO Clause:** 8.3
**Total Endpoints:** 20+

### Health & Monitoring

**GET /health**
```bash
curl http://localhost:8011/health
```
Response:
```json
{
  "status": "healthy",
  "service": "planning-service",
  "version": "2.0.0",
  "timestamp": "2025-10-08T10:00:00Z"
}
```

**GET /metrics**
Prometheus metrics endpoint

---

### Strategies

**POST /strategies**
Create a new business continuity strategy

Request:
```json
{
  "name": "Primary Data Center Recovery",
  "strategy_type": "recovery",
  "description": "Recovery strategy for primary DC failure",
  "implementation_timeframe": "immediate"
}
```

Response (201):
```json
{
  "id": "uuid",
  "name": "Primary Data Center Recovery",
  "strategy_type": "recovery",
  "description": "Recovery strategy for primary DC failure",
  "implementation_timeframe": "immediate",
  "approval_status": "pending",
  "created_at": "2025-10-08T10:00:00Z",
  "updated_at": "2025-10-08T10:00:00Z"
}
```

**GET /strategies**
List all strategies (paginated)

Query Parameters:
- `page` (int, default: 1)
- `page_size` (int, default: 20)
- `strategy_type` (string, optional)
- `approval_status` (string, optional)

**GET /strategies/{id}**
Get strategy details

**PUT /strategies/{id}**
Update strategy

**DELETE /strategies/{id}**
Delete strategy (soft delete)

**POST /strategies/{id}/approve**
Approve strategy

**POST /strategies/{id}/reject**
Reject strategy

---

### Cost-Benefit Analysis

**POST /strategies/{id}/cost-benefit**
Perform cost-benefit analysis

Request:
```json
{
  "initial_investment": 100000,
  "annual_costs": 20000,
  "annual_benefits": 50000,
  "analysis_years": 5,
  "discount_rate": 0.1
}
```

Response:
```json
{
  "id": "uuid",
  "strategy_id": "uuid",
  "npv": 45678.90,
  "roi": 0.45,
  "payback_period_years": 2.5,
  "analysis_summary": "Positive NPV, recommended for approval"
}
```

**GET /strategies/{id}/cost-benefit**
Get cost-benefit analysis results

---

### Resource Allocation

**POST /strategies/{id}/resources**
Add resource allocation

**GET /strategies/{id}/resources**
List resources for strategy

**PUT /resources/{id}**
Update resource allocation

**DELETE /resources/{id}**
Remove resource allocation

---

## 2. BIA Service API

**Base URL:** `http://localhost:8012/api/v1`
**ISO Clause:** 8.2.2
**Total Endpoints:** 31

### BIA Processes

**POST /bia**
Create BIA process

Request:
```json
{
  "process_name": "Payment Processing",
  "process_owner": "Finance Department",
  "criticality": "CRITICAL",
  "rto_hours": 2,
  "rpo_hours": 1,
  "mtpd_hours": 4,
  "recovery_strategy": "Hot site failover",
  "upstream_processes": ["Order Management"],
  "downstream_processes": ["Settlement", "Reconciliation"]
}
```

Validation:
- `rpo_hours <= rto_hours <= mtpd_hours`
- `criticality` in [CRITICAL, HIGH, MEDIUM, LOW]

**GET /bia**
List BIA processes

**GET /bia/{id}**
Get BIA process details

**PUT /bia/{id}**
Update BIA process

**DELETE /bia/{id}**
Delete BIA process

**GET /bia/criticality/{level}**
Filter by criticality level

---

### Assessments

**POST /bia/{id}/assessment**
Create impact assessment

Request:
```json
{
  "assessment_date": "2025-10-08",
  "financial_impact_1h": 10000,
  "financial_impact_4h": 50000,
  "financial_impact_24h": 200000,
  "financial_impact_1week": 1000000,
  "operational_impact": "Complete service disruption",
  "reputational_impact": "High customer dissatisfaction",
  "regulatory_impact": "Potential regulatory fines"
}
```

**GET /bia/{id}/assessments**
List assessments for process

---

### Dependencies

**POST /bia/{id}/dependencies**
Add process dependency

**GET /bia/{id}/dependencies**
Get dependency map

**GET /bia/dependency-graph**
Get full dependency graph (for visualization)

---

### Resources

**POST /bia/{id}/resources**
Add resource requirement

Request:
```json
{
  "resource_type": "PERSONNEL",
  "resource_name": "Senior Database Administrator",
  "quantity_required": 2,
  "criticality": "CRITICAL"
}
```

**GET /bia/{id}/resources**
List resource requirements

---

## 3. Governance Service API

**Base URL:** `http://localhost:8013/api/v1`
**ISO Clauses:** 4, 5
**Total Endpoints:** 46

### Policies

**POST /governance/policies**
Create governance policy

**GET /governance/policies**
List policies

**GET /governance/policies/{id}**
Get policy details

**PUT /governance/policies/{id}**
Update policy

**POST /governance/policies/{id}/approve**
Approve policy

**POST /governance/policies/{id}/review**
Schedule policy review

---

### Stakeholders

**POST /governance/stakeholders**
Register stakeholder

Request:
```json
{
  "stakeholder_name": "Board of Directors",
  "stakeholder_type": "INTERNAL",
  "influence": "HIGH",
  "interest": "HIGH",
  "communication_frequency": "MONTHLY",
  "contact_details": {...}
}
```

**GET /governance/stakeholders**
List stakeholders

**POST /governance/stakeholders/{id}/communication**
Log stakeholder communication

---

### Organizational Context

**POST /governance/context**
Define organizational context

**GET /governance/context**
Get current context

**PUT /governance/context/{id}**
Update context analysis

---

## 4. Compliance Service API

**Base URL:** `http://localhost:8014/api/v1`
**ISO Clauses:** 9.2, 10.1, 10.2
**Total Endpoints:** 95

### Audits

**POST /audits**
Create audit plan

Request:
```json
{
  "audit_title": "ISO 22301 Internal Audit Q1 2025",
  "audit_type": "INTERNAL",
  "audit_scope": "Clauses 4-10",
  "clauses_covered": ["4.1", "4.2", "5.1", "5.2"],
  "planned_start_date": "2025-01-15",
  "planned_end_date": "2025-01-30",
  "lead_auditor": "user-uuid"
}
```

**GET /audits**
List audits

**GET /audits/{id}**
Get audit details

**PUT /audits/{id}**
Update audit

**POST /audits/{id}/start**
Start audit execution

**POST /audits/{id}/complete**
Complete audit

---

### Audit Findings

**POST /audits/{id}/findings**
Add audit finding

Request:
```json
{
  "finding_title": "Incomplete BIA Documentation",
  "finding_description": "3 critical processes lack recovery strategies",
  "severity": "MAJOR",
  "iso_clause": "8.2.2",
  "evidence": "Review of BIA register",
  "recommendation": "Complete recovery strategies within 30 days"
}
```

**GET /audits/{id}/findings**
List findings for audit

**PUT /findings/{id}**
Update finding

**POST /findings/{id}/close**
Close finding

---

### Nonconformities

**POST /nonconformities**
Log nonconformity

Request:
```json
{
  "title": "Backup Failed",
  "description": "Daily backup process failed for 3 consecutive days",
  "nc_type": "MAJOR",
  "rca_method": "5_WHYS",
  "rca_template": {
    "problem_statement": "Backup process failed",
    "why_1": "Storage was full",
    "why_2": "Retention policy not enforced",
    "why_3": "No automated cleanup configured",
    "why_4": "Initial setup was manual",
    "why_5": "Lack of proper documentation"
  },
  "detected_date": "2025-10-08",
  "area_affected": "IT Infrastructure"
}
```

RCA Methods:
- `5_WHYS` - Sequential questioning
- `FISHBONE` - 6M categorization
- `FAULT_TREE` - Logic tree analysis

**GET /nonconformities**
List nonconformities

**GET /nonconformities/{id}**
Get nonconformity details

**PUT /nonconformities/{id}**
Update nonconformity

---

### Corrective Actions

**POST /nonconformities/{id}/corrective-actions**
Create corrective action

**GET /nonconformities/{id}/corrective-actions**
List corrective actions

**POST /corrective-actions/{id}/verify**
Verify effectiveness

---

### Improvements

**POST /improvements**
Create improvement initiative

**GET /improvements**
List improvements

**POST /improvements/{id}/kpi**
Add KPI tracking

**GET /improvements/{id}/progress**
Get improvement progress

---

## 5. Learning Service API

**Base URL:** `http://localhost:8021/api/v1`
**ISO Clauses:** 7.2, 7.3
**Total Endpoints:** 34

### Training Programs

**POST /training/programs**
Create training program

**GET /training/programs**
List programs

**POST /training/programs/{id}/enroll**
Enroll user in program

---

### Assessments

**GET /training/assessments/{id}**
Get assessment

**POST /training/assessments/{id}/submit**
Submit assessment answers

**GET /training/assessments/{id}/results**
Get assessment results

---

### Certifications

**POST /certifications**
Issue certification

**GET /certifications/{id}**
Get certification details

**POST /certifications/{id}/renew**
Renew certification

---

## 6. Validation Service API

**Base URL:** `http://localhost:8022/api/v1`
**ISO Clauses:** 8.5, 9.1-9.3, 10
**Total Endpoints:** 49

### KPIs

**POST /validation/kpis**
Define KPI

Request:
```json
{
  "kpi_name": "Recovery Time Achievement",
  "kpi_description": "Percentage of incidents resolved within RTO",
  "target_value": 95,
  "measurement_unit": "PERCENTAGE",
  "measurement_frequency": "MONTHLY"
}
```

**GET /validation/kpis**
List KPIs

**POST /validation/kpis/{id}/metric**
Record metric data point

---

### Alerts

**POST /validation/alerts**
Configure alert

**GET /validation/alerts**
List alerts

**POST /validation/alerts/{id}/trigger**
Manually trigger alert

---

## 7. Plans Service API

**Base URL:** `http://localhost:8023/api/v1`
**ISO Clause:** 8.4
**Total Endpoints:** 32

### Plans

**POST /plans**
Create business continuity plan

Request:
```json
{
  "plan_name": "IT Disaster Recovery Plan",
  "plan_type": "RECOVERY",
  "scope": "IT Infrastructure",
  "version": "1.0"
}
```

**GET /plans**
List plans

**GET /plans/{id}**
Get plan details

**PUT /plans/{id}**
Update plan

**POST /plans/{id}/activate**
Activate plan

**POST /plans/{id}/version**
Create new version

---

### Procedures

**POST /plans/{id}/procedures**
Add procedure to plan

Request:
```json
{
  "procedure_name": "Restore Database from Backup",
  "procedure_steps": [
    "Identify latest backup",
    "Verify backup integrity",
    "Restore to staging environment",
    "Run validation tests",
    "Promote to production"
  ],
  "execution_order": 1,
  "depends_on_procedures": []  // UUIDs of prerequisite procedures
}
```

Validation:
- Circular dependency prevention (DFS algorithm)
- Topological sorting for execution order

**GET /plans/{id}/procedures**
List procedures

**GET /plans/{id}/execution-order**
Get optimal execution order (topological sort)

---

### Exercises

**POST /plans/{id}/exercises**
Schedule exercise

**GET /plans/{id}/exercises**
List exercises

**POST /exercises/{id}/complete**
Complete exercise and capture results

---

## 8. Documents Service API

**Base URL:** `http://localhost:8024/api/v1`
**ISO Clause:** 7.5
**Total Endpoints:** 30

### Documents

**POST /documents**
Upload document (multipart/form-data)

**GET /documents**
List documents

**GET /documents/{id}**
Get document metadata

**GET /documents/{id}/download**
Download document file

**PUT /documents/{id}**
Update document metadata

**DELETE /documents/{id}**
Delete document (soft delete)

---

### Versions

**GET /documents/{id}/versions**
List document versions

**GET /documents/{id}/versions/{version}**
Get specific version

**POST /documents/{id}/restore/{version}**
Restore to previous version

---

### Approvals

**POST /documents/{id}/submit-approval**
Submit for approval

**POST /documents/{id}/approve**
Approve document

**POST /documents/{id}/reject**
Reject document

---

### Search

**POST /documents/search**
Full-text search

Request:
```json
{
  "query": "business continuity",
  "filters": {
    "document_type": "POLICY",
    "approval_status": "APPROVED"
  }
}
```

---

## 9. Risk Service API

**Base URL:** `http://localhost:8040/api/v1/risk`
**ISO Clause:** 8.2.3
**Total Endpoints:** 29

### Risks

**POST /risks**
Create risk

Request:
```json
{
  "risk_title": "Data Center Flood",
  "risk_description": "Flooding risk to primary data center",
  "risk_category": "NATURAL_DISASTER",
  "inherent_likelihood": 3,
  "inherent_impact": 5
}
```

Auto-calculated:
- `inherent_risk_score` = likelihood × impact
- `risk_level` = CRITICAL (>=20), HIGH (15-19), MEDIUM (8-14), LOW (<8)

**GET /risks**
List risks

**GET /risks/{id}**
Get risk details

**PUT /risks/{id}**
Update risk

---

### Assessments

**POST /risks/{id}/assess**
Perform risk assessment

Request:
```json
{
  "assessment_date": "2025-10-08",
  "fair_analysis": {
    "loss_event_frequency": {...},
    "loss_magnitude": {...}
  },
  "monte_carlo_iterations": 10000
}
```

**GET /risks/{id}/assessments**
List assessments

---

### Treatments

**POST /risks/{id}/treatments**
Create treatment plan

**GET /risks/{id}/treatments**
List treatments

---

### Controls

**POST /risks/{id}/controls**
Add risk control

**GET /risks/{id}/controls**
List controls

**POST /controls/{id}/test**
Record control test

---

## 10. Response Service API

**Base URL:** `http://localhost:8041/api/v1/response`
**ISO Clause:** 8.4.5
**Total Endpoints:** 38

### Incidents

**POST /incidents**
Create incident

Request:
```json
{
  "incident_title": "Email System Outage",
  "incident_description": "Complete email system unavailable",
  "severity": "CRITICAL",
  "detected_at": "2025-10-08T09:00:00Z",
  "detected_by": "user-uuid"
}
```

Severity levels:
- CRITICAL: Response time 15 minutes
- HIGH: Response time 60 minutes
- MEDIUM: Response time 120 minutes
- LOW: Response time 240 minutes

**GET /incidents**
List incidents

**GET /incidents/{id}**
Get incident details

**PUT /incidents/{id}**
Update incident

**POST /incidents/{id}/resolve**
Resolve incident

---

### Timeline

**POST /incidents/{id}/timeline**
Add timeline entry

**GET /incidents/{id}/timeline**
Get incident timeline

---

### Escalations

**POST /incidents/{id}/escalate**
Escalate incident

**GET /incidents/{id}/escalations**
Get escalation history

---

### Communications

**POST /incidents/{id}/communications**
Log communication

**GET /incidents/{id}/communications**
Get communication log

---

### Lessons Learned

**POST /incidents/{id}/lessons-learned**
Capture lessons learned

**GET /incidents/{id}/lessons-learned**
Get lessons learned

---

## 11. Living Docs API

**Base URL:** `http://localhost:8034`
**Total Endpoints:** 10

### Documentation

**GET /**
Root documentation

**GET /health**
Health check

**GET /gaps**
Identified documentation gaps

**GET /improvements**
Auto-improvements

**GET /journey/{goal}**
Personalized learning journey

**POST /examples/generate**
Generate AI examples

**POST /feedback**
Submit user feedback

---

## 12. BCM Coordination API

**Base URL:** `http://localhost:8070`
**Total Endpoints:** TBD

### Coordination

**GET /health**
Health check

**POST /coordinate**
Coordinate analyzers

---

## Event-Driven APIs

All services publish events to EventBus. Subscribe to events for real-time updates.

### Event Patterns

```javascript
// Subscribe to all BIA events
eventBus.subscribe('bia.*', handleBIAEvent)

// Subscribe to specific event
eventBus.subscribe('risk.critical', handleCriticalRisk)

// Publish event
eventBus.publish('compliance.audit.completed', {audit_id: 'uuid'})
```

### Common Events

**BIA Service**
- `bia.created`
- `bia.updated`
- `bia.assessment.completed`

**Risk Service**
- `risk.created`
- `risk.assessed`
- `risk.critical` (auto-escalate)

**Compliance Service**
- `compliance.audit.started`
- `compliance.audit.completed`
- `compliance.nonconformity.created`

**Response Service**
- `incident.created`
- `incident.escalated`
- `incident.resolved`

---

## WebSocket APIs

### Real-Time Updates

Connect to WebSocket for real-time incident updates:

```javascript
const ws = new WebSocket('ws://localhost:8041/ws/incidents/{incident_id}')

ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  console.log('Incident update:', update)
}
```

---

## Rate Limiting

All APIs implement rate limiting:

```
Rate Limit: 100 requests per 60 seconds
Rate Limit Headers:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1234567890
```

When rate limit exceeded:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "rto_hours",
      "reason": "Must be less than mtpd_hours"
    },
    "request_id": "uuid"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 422 | Input validation failed |
| NOT_FOUND | 404 | Resource not found |
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Insufficient permissions |
| CONFLICT | 409 | Resource conflict |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

---

## API Testing

### Using cURL

```bash
# Create BIA process
curl -X POST http://localhost:8012/api/v1/bia \
  -H "Content-Type: application/json" \
  -H "X-Dev-User: user123|tenant456|admin" \
  -d '{
    "process_name": "Payment Processing",
    "process_owner": "Finance",
    "criticality": "CRITICAL",
    "rto_hours": 2,
    "rpo_hours": 1,
    "mtpd_hours": 4
  }'
```

### Using Python

```python
import httpx

client = httpx.AsyncClient()

response = await client.post(
    "http://localhost:8012/api/v1/bia",
    headers={
        "Content-Type": "application/json",
        "X-Dev-User": "user123|tenant456|admin"
    },
    json={
        "process_name": "Payment Processing",
        "process_owner": "Finance",
        "criticality": "CRITICAL",
        "rto_hours": 2,
        "rpo_hours": 1,
        "mtpd_hours": 4
    }
)

print(response.json())
```

---

## API Versioning

Current version: **v1**

Future versions will use URL versioning:
- `/api/v1/...` - Current
- `/api/v2/...` - Future

Version deprecation policy:
- 6 months notice before deprecation
- 12 months support for deprecated versions

---

## OpenAPI Specification

All services provide OpenAPI 3.0 specifications:

```bash
# Get OpenAPI spec
curl http://localhost:8011/openapi.json

# Interactive documentation
open http://localhost:8011/docs

# ReDoc format
open http://localhost:8011/redoc
```

---

## SDK & Client Libraries

### Python SDK (Future)

```python
from bcm_platform import BCMClient

client = BCMClient(
    base_url="http://localhost",
    api_key="your-api-key"
)

# Create BIA process
bia = await client.bia.create({
    "process_name": "Payment Processing",
    "criticality": "CRITICAL"
})

# Create risk
risk = await client.risk.create({
    "risk_title": "Data Center Flood",
    "inherent_likelihood": 3,
    "inherent_impact": 5
})
```

---

**Document Version:** 1.0.0
**Maintained By:** API Platform Team
**Related Documents:**
- [Platform Services Catalog](./PLATFORM_SERVICES_COMPLETE_CATALOG.md)
- [Port Allocation](./PORT_ALLOCATION.md)
- [Database Schema Map](./DATABASE_SCHEMA_MAP.md)
