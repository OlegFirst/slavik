# BCM Platform API Endpoints Export

## Экспорт всех API эндпоинтов

### Core BCM Endpoints

#### Authentication & Authorization
```http
POST   /api/v1/auth/login
POST   /api/v1/auth/logout  
POST   /api/v1/auth/refresh
GET    /api/v1/auth/profile
PUT    /api/v1/auth/profile
POST   /api/v1/auth/change-password
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
GET    /api/v1/auth/permissions
```

#### BCM Core Management
```http
GET    /api/v1/bcm/core/status
GET    /api/v1/bcm/core/health
GET    /api/v1/bcm/core/version
GET    /api/v1/bcm/core/client-context
POST   /api/v1/bcm/core/client-context
PUT    /api/v1/bcm/core/client-context
POST   /api/v1/bcm/core/validate
GET    /api/v1/bcm/core/tags
POST   /api/v1/bcm/core/tags
PUT    /api/v1/bcm/core/tags/{id}
DELETE /api/v1/bcm/core/tags/{id}
```

### Business Impact Analysis (BIA) API

#### Business Processes
```http
GET    /api/v1/bcm/bia/processes
POST   /api/v1/bcm/bia/processes
GET    /api/v1/bcm/bia/processes/{id}
PUT    /api/v1/bcm/bia/processes/{id}
DELETE /api/v1/bcm/bia/processes/{id}
POST   /api/v1/bcm/bia/processes/bulk-create
PUT    /api/v1/bcm/bia/processes/bulk-update
DELETE /api/v1/bcm/bia/processes/bulk-delete
GET    /api/v1/bcm/bia/processes/{id}/dependencies
POST   /api/v1/bcm/bia/processes/{id}/dependencies
```

#### BIA Assessments
```http
GET    /api/v1/bcm/bia/assessments
POST   /api/v1/bcm/bia/assessments
GET    /api/v1/bcm/bia/assessments/{id}
PUT    /api/v1/bcm/bia/assessments/{id}
DELETE /api/v1/bcm/bia/assessments/{id}
POST   /api/v1/bcm/bia/assessments/{id}/start
POST   /api/v1/bcm/bia/assessments/{id}/complete
POST   /api/v1/bcm/bia/assessments/{id}/approve
GET    /api/v1/bcm/bia/assessments/{id}/report
```

#### Impact Analysis
```http
POST   /api/v1/bcm/bia/calculate-impact
POST   /api/v1/bcm/bia/optimize-rto-rpo
POST   /api/v1/bcm/bia/dependency-analysis
GET    /api/v1/bcm/bia/impact-matrix
GET    /api/v1/bcm/bia/criticality-dashboard
POST   /api/v1/bcm/bia/scenario-analysis
```

### Risk Management API

#### Risk Register
```http
GET    /api/v1/bcm/risk/risks
POST   /api/v1/bcm/risk/risks
GET    /api/v1/bcm/risk/risks/{id}
PUT    /api/v1/bcm/risk/risks/{id}
DELETE /api/v1/bcm/risk/risks/{id}
POST   /api/v1/bcm/risk/risks/{id}/archive
GET    /api/v1/bcm/risk/risks/{id}/history
POST   /api/v1/bcm/risk/risks/import
GET    /api/v1/bcm/risk/risks/export
```

#### Risk Assessments
```http
GET    /api/v1/bcm/risk/assessments
POST   /api/v1/bcm/risk/assessments
GET    /api/v1/bcm/risk/assessments/{id}
PUT    /api/v1/bcm/risk/assessments/{id}
DELETE /api/v1/bcm/risk/assessments/{id}
POST   /api/v1/bcm/risk/assessments/{id}/approve
GET    /api/v1/bcm/risk/assessments/{id}/report
```

#### Risk Analysis
```http
POST   /api/v1/bcm/risk/calculate-score
GET    /api/v1/bcm/risk/matrix-analysis
POST   /api/v1/bcm/risk/trend-analysis
POST   /api/v1/bcm/risk/scenario-modeling
POST   /api/v1/bcm/risk/ai-assessment
GET    /api/v1/bcm/risk/correlations
POST   /api/v1/bcm/risk/monte-carlo
```

#### Risk Treatment
```http
GET    /api/v1/bcm/risk/treatments
POST   /api/v1/bcm/risk/treatments
GET    /api/v1/bcm/risk/treatments/{id}
PUT    /api/v1/bcm/risk/treatments/{id}
DELETE /api/v1/bcm/risk/treatments/{id}
POST   /api/v1/bcm/risk/treatments/{id}/complete
GET    /api/v1/bcm/risk/treatments/effectiveness
```

### Incident Management API

#### Incident Operations
```http
GET    /api/v1/bcm/incident/incidents
POST   /api/v1/bcm/incident/incidents
GET    /api/v1/bcm/incident/incidents/{id}
PUT    /api/v1/bcm/incident/incidents/{id}
DELETE /api/v1/bcm/incident/incidents/{id}
POST   /api/v1/bcm/incident/report
PUT    /api/v1/bcm/incident/{id}/status
POST   /api/v1/bcm/incident/{id}/escalate
POST   /api/v1/bcm/incident/{id}/assign
POST   /api/v1/bcm/incident/{id}/close
```

#### Incident Response
```http
GET    /api/v1/bcm/incident/{id}/responses
POST   /api/v1/bcm/incident/{id}/responses
PUT    /api/v1/bcm/incident/responses/{id}
DELETE /api/v1/bcm/incident/responses/{id}
POST   /api/v1/bcm/incident/{id}/timeline
GET    /api/v1/bcm/incident/{id}/impact-assessment
POST   /api/v1/bcm/incident/{id}/lessons-learned
```

#### Crisis Management
```http
POST   /api/v1/bcm/crisis/activate
GET    /api/v1/bcm/crisis/status-board
POST   /api/v1/bcm/crisis/team-notification
GET    /api/v1/bcm/crisis/team-status
POST   /api/v1/bcm/crisis/communications
GET    /api/v1/bcm/crisis/media-monitoring
POST   /api/v1/bcm/crisis/stakeholder-updates
```

### Plans Management API

#### Plan Operations
```http
GET    /api/v1/bcm/plans/plans
POST   /api/v1/bcm/plans/plans
GET    /api/v1/bcm/plans/plans/{id}
PUT    /api/v1/bcm/plans/plans/{id}
DELETE /api/v1/bcm/plans/plans/{id}
POST   /api/v1/bcm/plans/{id}/activate
POST   /api/v1/bcm/plans/{id}/deactivate
GET    /api/v1/bcm/plans/{id}/status
POST   /api/v1/bcm/plans/{id}/test
GET    /api/v1/bcm/plans/{id}/test-results
```

#### Plan Steps
```http
GET    /api/v1/bcm/plans/{id}/steps
POST   /api/v1/bcm/plans/{id}/steps
PUT    /api/v1/bcm/plans/steps/{id}
DELETE /api/v1/bcm/plans/steps/{id}
POST   /api/v1/bcm/plans/steps/{id}/complete
POST   /api/v1/bcm/plans/steps/{id}/skip
GET    /api/v1/bcm/plans/{id}/execution-status
```

#### Plan Templates
```http
GET    /api/v1/bcm/plans/templates
POST   /api/v1/bcm/plans/templates
GET    /api/v1/bcm/plans/templates/{id}
PUT    /api/v1/bcm/plans/templates/{id}
DELETE /api/v1/bcm/plans/templates/{id}
POST   /api/v1/bcm/plans/templates/{id}/apply
```

### AI & Analytics API

#### AI Analysis Services
```http
POST   /api/v1/bcm/ai/trigger-analysis
GET    /api/v1/bcm/ai/analysis/{id}/status
GET    /api/v1/bcm/ai/analysis/{id}/results
DELETE /api/v1/bcm/ai/analysis/{id}
GET    /api/v1/bcm/ai/analysis/history
POST   /api/v1/bcm/ai/model/retrain
GET    /api/v1/bcm/ai/model/performance
GET    /api/v1/bcm/ai/health-check
```

#### Predictive Analytics
```http
POST   /api/v1/bcm/ai/predict-incidents
POST   /api/v1/bcm/ai/predict-risks
POST   /api/v1/bcm/ai/forecast-trends
POST   /api/v1/bcm/ai/anomaly-detection
GET    /api/v1/bcm/ai/predictions/{id}
POST   /api/v1/bcm/ai/recommendations
```

### Portal & Self-Service API

#### Portal Dashboard
```http
GET    /api/v1/bcm/portal/dashboard
POST   /api/v1/bcm/portal/dashboard/customize
GET    /api/v1/bcm/portal/widgets
POST   /api/v1/bcm/portal/widgets
PUT    /api/v1/bcm/portal/widgets/{id}
DELETE /api/v1/bcm/portal/widgets/{id}
```

#### AI Assistant
```http
POST   /api/v1/bcm/portal/ai-chat
GET    /api/v1/bcm/portal/ai-chat/history
DELETE /api/v1/bcm/portal/ai-chat/history
POST   /api/v1/bcm/portal/ai-recommendations
GET    /api/v1/bcm/portal/ai-insights
```

#### Self-Service Operations
```http
GET    /api/v1/bcm/portal/self-service/menu
POST   /api/v1/bcm/portal/self-service/action
GET    /api/v1/bcm/portal/notifications
PUT    /api/v1/bcm/portal/notifications/{id}/read
DELETE /api/v1/bcm/portal/notifications/{id}
POST   /api/v1/bcm/portal/settings
GET    /api/v1/bcm/portal/settings
```

### Reporting & Analytics API

#### Report Generation
```http
GET    /api/v1/bcm/reports/templates
POST   /api/v1/bcm/reports/generate
GET    /api/v1/bcm/reports/{id}/status
GET    /api/v1/bcm/reports/{id}/download
DELETE /api/v1/bcm/reports/{id}
POST   /api/v1/bcm/reports/schedule
GET    /api/v1/bcm/reports/scheduled
PUT    /api/v1/bcm/reports/scheduled/{id}
DELETE /api/v1/bcm/reports/scheduled/{id}
```

#### KPI & Metrics
```http
GET    /api/v1/bcm/kpi/definitions
POST   /api/v1/bcm/kpi/definitions
PUT    /api/v1/bcm/kpi/definitions/{id}
DELETE /api/v1/bcm/kpi/definitions/{id}
GET    /api/v1/bcm/kpi/measurements
POST   /api/v1/bcm/kpi/measurements
GET    /api/v1/bcm/kpi/dashboard
GET    /api/v1/bcm/kpi/trends
```

### Exercise & Training API

#### Exercise Management
```http
GET    /api/v1/bcm/exercise/exercises
POST   /api/v1/bcm/exercise/exercises
GET    /api/v1/bcm/exercise/exercises/{id}
PUT    /api/v1/bcm/exercise/exercises/{id}
DELETE /api/v1/bcm/exercise/exercises/{id}
POST   /api/v1/bcm/exercise/{id}/start
POST   /api/v1/bcm/exercise/{id}/complete
GET    /api/v1/bcm/exercise/{id}/results
```

#### Training Programs
```http
GET    /api/v1/bcm/training/programs
POST   /api/v1/bcm/training/programs
GET    /api/v1/bcm/training/programs/{id}
PUT    /api/v1/bcm/training/programs/{id}
DELETE /api/v1/bcm/training/programs/{id}
POST   /api/v1/bcm/training/{id}/enroll
GET    /api/v1/bcm/training/{id}/progress
POST   /api/v1/bcm/training/{id}/complete
```

### Governance & Compliance API

#### Audit Management
```http
GET    /api/v1/bcm/audit/plans
POST   /api/v1/bcm/audit/plans
GET    /api/v1/bcm/audit/plans/{id}
PUT    /api/v1/bcm/audit/plans/{id}
DELETE /api/v1/bcm/audit/plans/{id}
POST   /api/v1/bcm/audit/{id}/start
GET    /api/v1/bcm/audit/findings
POST   /api/v1/bcm/audit/findings
PUT    /api/v1/bcm/audit/findings/{id}
```

#### Compliance Monitoring
```http
GET    /api/v1/bcm/compliance/frameworks
GET    /api/v1/bcm/compliance/status
POST   /api/v1/bcm/compliance/assessment
GET    /api/v1/bcm/compliance/gaps
POST   /api/v1/bcm/compliance/remediation
GET    /api/v1/bcm/compliance/reports
```

### Client Management API

#### Client Operations
```http
GET    /api/v1/bcm/clients/clients
POST   /api/v1/bcm/clients/clients
GET    /api/v1/bcm/clients/clients/{id}
PUT    /api/v1/bcm/clients/clients/{id}
DELETE /api/v1/bcm/clients/clients/{id}
POST   /api/v1/bcm/clients/{id}/onboard
POST   /api/v1/bcm/clients/{id}/offboard
GET    /api/v1/bcm/clients/{id}/configuration
PUT    /api/v1/bcm/clients/{id}/configuration
```

### Configuration API

#### System Configuration
```http
GET    /api/v1/bcm/config/settings
PUT    /api/v1/bcm/config/settings
GET    /api/v1/bcm/config/parameters
PUT    /api/v1/bcm/config/parameters/{key}
GET    /api/v1/bcm/config/integrations
POST   /api/v1/bcm/config/integrations
PUT    /api/v1/bcm/config/integrations/{id}
DELETE /api/v1/bcm/config/integrations/{id}
```

### Scenario Hub API

#### Scenario Marketplace
```http
GET    /api/v1/bcm/scenarios/marketplace
GET    /api/v1/bcm/scenarios/templates
POST   /api/v1/bcm/scenarios/templates
GET    /api/v1/bcm/scenarios/templates/{id}
PUT    /api/v1/bcm/scenarios/templates/{id}
DELETE /api/v1/bcm/scenarios/templates/{id}
POST   /api/v1/bcm/scenarios/templates/{id}/apply
POST   /api/v1/bcm/scenarios/templates/{id}/rate
GET    /api/v1/bcm/scenarios/categories
```

### File & Document Management

#### File Operations
```http
POST   /api/v1/bcm/files/upload
GET    /api/v1/bcm/files/{id}
DELETE /api/v1/bcm/files/{id}
GET    /api/v1/bcm/files/{id}/preview
GET    /api/v1/bcm/files/{id}/download
POST   /api/v1/bcm/files/{id}/share
GET    /api/v1/bcm/files/search
```

#### Document Templates
```http
GET    /api/v1/bcm/templates/documents
POST   /api/v1/bcm/templates/documents
GET    /api/v1/bcm/templates/documents/{id}
PUT    /api/v1/bcm/templates/documents/{id}
DELETE /api/v1/bcm/templates/documents/{id}
POST   /api/v1/bcm/templates/documents/{id}/generate
```

### Notification & Communication API

#### Notification Management
```http
GET    /api/v1/bcm/notifications
POST   /api/v1/bcm/notifications
PUT    /api/v1/bcm/notifications/{id}/read
DELETE /api/v1/bcm/notifications/{id}
POST   /api/v1/bcm/notifications/settings
GET    /api/v1/bcm/notifications/settings
GET    /api/v1/bcm/notifications/templates
POST   /api/v1/bcm/notifications/templates
```

#### Communication Channels
```http
GET    /api/v1/bcm/communications/channels
POST   /api/v1/bcm/communications/channels
PUT    /api/v1/bcm/communications/channels/{id}
DELETE /api/v1/bcm/communications/channels/{id}
POST   /api/v1/bcm/communications/send
GET    /api/v1/bcm/communications/history
```

---

## HTTP Status Codes

### Success Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted for processing
- `204 No Content` - Successful request with no content to return

### Client Error Codes
- `400 Bad Request` - Invalid request syntax or parameters
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Request conflicts with current state
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded

### Server Error Codes
- `500 Internal Server Error` - Server error
- `502 Bad Gateway` - Invalid response from upstream server
- `503 Service Unavailable` - Service temporarily unavailable
- `504 Gateway Timeout` - Upstream server timeout

---

## Common Query Parameters

### Pagination
- `limit` - Number of items per page (default: 20, max: 100)
- `offset` - Number of items to skip
- `page` - Page number (alternative to offset)

### Filtering
- `filter` - General filter parameter (JSON object)
- `search` - Text search parameter
- `status` - Filter by status
- `date_from` - Filter from date (ISO 8601)
- `date_to` - Filter to date (ISO 8601)

### Sorting
- `sort` - Sort field name
- `order` - Sort order (asc/desc)

### Fields
- `fields` - Comma-separated list of fields to include
- `exclude` - Comma-separated list of fields to exclude
- `expand` - Comma-separated list of related objects to include

### Format
- `format` - Response format (json/xml/csv)
- `download` - Force download (true/false)

---

## Rate Limiting Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999  
X-RateLimit-Reset: 1642691400
X-RateLimit-Window: 3600
```

## Security Headers

```http
X-Client-ID: client-uuid-here
Authorization: Bearer jwt-token-here
X-Request-ID: unique-request-id
X-API-Version: 1.0
```

## WebSocket Endpoints

### Real-time Notifications
```
wss://api.bcm-platform.com/ws/notifications
wss://api.bcm-platform.com/ws/incidents
wss://api.bcm-platform.com/ws/plans
wss://api.bcm-platform.com/ws/ai-analysis
```

### Event Types
- `incident.created`
- `incident.updated`
- `incident.escalated`
- `plan.activated`
- `plan.completed`
- `ai.analysis.complete`
- `notification.new`

---

## Batch Operations

### Bulk Endpoints
```http
POST   /api/v1/bcm/*/bulk-create
PUT    /api/v1/bcm/*/bulk-update
DELETE /api/v1/bcm/*/bulk-delete
POST   /api/v1/bcm/*/bulk-import
GET    /api/v1/bcm/*/bulk-export
```

### Batch Request Format
```json
{
  "operations": [
    {
      "method": "POST",
      "path": "/api/v1/bcm/bia/processes",
      "body": {...}
    },
    {
      "method": "PUT", 
      "path": "/api/v1/bcm/bia/processes/123",
      "body": {...}
    }
  ]
}
```

---

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:
```
GET /api/v1/docs/openapi.json
GET /api/v1/docs/swagger.yaml
```

Interactive API documentation:
```
GET /api/v1/docs/
GET /api/v1/redoc/
```