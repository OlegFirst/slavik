# Response Module

**ISO 22301:2019 Clause 8.4 - Incident Response**

Complete incident response management module for BCM Platform.

## Overview

The Response module provides comprehensive incident response capabilities including:

- **Incident Management**: Create, track, and manage incidents
- **Response Actions**: Define and track response actions
- **Response Teams**: Manage incident response teams
- **Communications**: Track all incident communications
- **Timeline**: Chronological incident timeline
- **Recovery Metrics**: RTO/RPO tracking and validation
- **Escalation**: Automatic and manual incident escalation
- **Reporting**: Comprehensive incident reports
- **Dashboard**: Real-time incident analytics

## Architecture

```
response/
├── api/
│   ├── __init__.py
│   └── routes.py          # All 15+ API endpoints
├── models/
│   ├── __init__.py
│   ├── domain.py          # Pydantic models
│   └── database.py        # SQLAlchemy models
├── services/
│   ├── __init__.py
│   └── business_logic.py  # ResponseService
├── repositories/
│   ├── __init__.py
│   └── repository.py      # ResponseRepository
├── events/
│   ├── __init__.py
│   ├── publishers.py      # Event publishers
│   └── subscribers.py     # Event subscribers
├── config.py              # Configuration
├── main.py                # FastAPI application
└── requirements.txt       # Dependencies
```

## Features

### 1. Incident Management
- Create and track incidents
- Multiple severity levels (low, medium, high, critical)
- Multiple incident types (security breach, system failure, etc.)
- Status tracking (detected → investigating → contained → resolved → closed)
- Root cause analysis
- Lessons learned documentation

### 2. Response Actions
- Add response actions to incidents
- Priority-based action management
- Action assignment and tracking
- Action status tracking
- Dependencies and checklists

### 3. Response Teams
- Create response teams
- Team member roles (incident manager, technical lead, etc.)
- Team activation criteria
- Escalation procedures

### 4. Communications
- Track all incident communications
- Multiple communication types (email, phone, SMS, etc.)
- Stakeholder notifications
- Communication history

### 5. Timeline
- Automatic timeline generation
- Track all incident events
- Actor tracking
- Event metadata

### 6. Recovery Metrics
- RTO (Recovery Time Objective) tracking
- RPO (Recovery Point Objective) tracking
- Compliance validation
- Service-specific metrics

### 7. Reporting & Analytics
- Comprehensive incident reports
- Dashboard with statistics
- Organization-level metrics (MTTR, MTBF)
- Compliance reporting

## API Endpoints

### Incident Endpoints
- `POST /api/v1/response/incidents` - Create incident
- `GET /api/v1/response/incidents` - List incidents
- `GET /api/v1/response/incidents/{id}` - Get incident
- `PUT /api/v1/response/incidents/{id}` - Update incident
- `PATCH /api/v1/response/incidents/{id}/status` - Change status
- `POST /api/v1/response/incidents/{id}/resolve` - Resolve incident
- `POST /api/v1/response/incidents/{id}/escalate` - Escalate incident

### Response Actions Endpoints
- `POST /api/v1/response/incidents/{id}/actions` - Add action
- `GET /api/v1/response/incidents/{id}/actions` - List actions
- `PUT /api/v1/response/actions/{id}` - Update action

### Response Team Endpoints
- `POST /api/v1/response/incidents/{id}/team` - Assign team
- `GET /api/v1/response/incidents/{id}/team` - Get team
- `POST /api/v1/response/organizations/{org_id}/teams` - Create team
- `GET /api/v1/response/organizations/{org_id}/teams` - List teams

### Communication Endpoints
- `POST /api/v1/response/incidents/{id}/communications` - Log communication
- `GET /api/v1/response/incidents/{id}/communications` - List communications

### Timeline Endpoints
- `GET /api/v1/response/incidents/{id}/timeline` - Get timeline

### Metrics Endpoints
- `POST /api/v1/response/incidents/{id}/metrics` - Add metrics
- `PUT /api/v1/response/metrics/{id}` - Update metrics
- `GET /api/v1/response/incidents/{id}/metrics` - Get metrics

### Reporting Endpoints
- `GET /api/v1/response/incidents/{id}/report` - Generate report
- `GET /api/v1/response/organizations/{org_id}/dashboard` - Dashboard
- `GET /api/v1/response/organizations/{org_id}/metrics` - Org metrics

## Configuration

Configuration is managed via environment variables:

```bash
# Service Configuration
SERVICE_NAME=response
SERVICE_VERSION=1.0.0
HOST=0.0.0.0
PORT=8041

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
DB_SCHEMA=response

# ISO Configuration
ISO_STANDARD=ISO 22301:2019
ISO_CLAUSE=8.4
DEFAULT_RTO_HOURS=4.0
DEFAULT_RPO_HOURS=1.0

# Features
AUTO_ESCALATE_CRITICAL=true
REQUIRE_ROOT_CAUSE_ON_RESOLVE=true

# Event Bus (optional)
EVENT_BUS_ENABLED=false
EVENT_BUS_TYPE=memory

# Logging
LOG_LEVEL=INFO
LOG_JSON=false
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (create `.env` file)

3. Run database migrations:
```bash
# TODO: Alembic migrations
```

4. Start the service:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8041 --reload
```

## Database Schema

The module uses the `response` schema with the following tables:

- `incidents` - Main incident records
- `response_actions` - Response actions
- `response_teams` - Response teams
- `response_team_members` - Team members
- `communication_logs` - Communication tracking
- `incident_timeline` - Event timeline
- `recovery_metrics` - RTO/RPO metrics

## ISO 22301:2019 Compliance

This module implements **ISO 22301:2019 Clause 8.4 - Incident response**:

### 8.4.1 General
- Incident response structure and procedures
- Response team management
- Communication protocols

### 8.4.2 Incident escalation
- Automatic escalation for critical incidents
- Escalation procedures
- Stakeholder notifications

### 8.4.3 Incident response structure
- Structured incident management
- Response actions tracking
- Team coordination

### 8.4.4 Recovery time and point objectives
- RTO/RPO tracking
- Compliance validation
- Service-level metrics

### 8.4.5 Incident analysis
- Root cause analysis
- Lessons learned
- Comprehensive reporting

## Event-Driven Integration

The module publishes and subscribes to events:

### Published Events
- `response.incident.created`
- `response.incident.updated`
- `response.incident.status_changed`
- `response.incident.resolved`
- `response.incident.closed`
- `response.incident.escalated`
- `response.stakeholder.notification`
- `response.metrics.updated`
- `response.compliance.violation`

### Subscribed Events
- `risk.assessment.high_risk_detected`
- `risk.assessment.critical_risk`
- `impact.analysis.high_impact`
- `recovery.failure`
- `recovery.rto_exceeded`
- `recovery.rpo_exceeded`
- `monitoring.alert.critical`
- `monitoring.system_down`

## Health Checks

- `/health` - Full health check with components
- `/ready` - Readiness probe (Kubernetes)
- `/live` - Liveness probe (Kubernetes)

## API Documentation

- Swagger UI: `http://localhost:8041/docs`
- ReDoc: `http://localhost:8041/redoc`
- OpenAPI JSON: `http://localhost:8041/openapi.json`

## Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=response --cov-report=html
```

## Development

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Running in Development
```bash
# With auto-reload
uvicorn main:app --reload --port 8041

# With debug logging
LOG_LEVEL=DEBUG uvicorn main:app --reload --port 8041
```

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8041"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: response-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: response-service
  template:
    metadata:
      labels:
        app: response-service
    spec:
      containers:
      - name: response-service
        image: response-service:latest
        ports:
        - containerPort: 8041
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        livenessProbe:
          httpGet:
            path: /live
            port: 8041
        readinessProbe:
          httpGet:
            path: /ready
            port: 8041
```

## Monitoring

The service exposes metrics for monitoring:

- Request rates
- Response times
- Error rates
- Database connection pool
- Active incidents
- Resolution times

## Security

- Multi-tenancy: `organization_id` based isolation
- API authentication (configure in production)
- Input validation via Pydantic
- SQL injection protection via SQLAlchemy
- CORS configuration
- Rate limiting (optional)

## Support

For issues or questions:
- Check API documentation: `/docs`
- Review logs: `LOG_LEVEL=DEBUG`
- Check database health: `/health`

## License

Proprietary - BCM Platform

## Version

1.0.0

## Changelog

### 1.0.0 (2025-10-03)
- Initial release
- Full ISO 22301:2019 Clause 8.4 implementation
- All 15+ API endpoints
- Complete CRUD operations
- Event-driven integration
- Dashboard and reporting
