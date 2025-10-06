# Plans Service - Business Continuity Plans & Procedures

**Service:** `plans_service`
**Port:** `8023`
**ISO 22301:** Clause 8.4
**BCI Practice:** PP5 (Enabling Solutions)

## Overview

Plans Service manages business continuity plans, procedures, resources, and plan lifecycle. This service implements ISO 22301 Clause 8.4 requirements for BC plans and procedures.

## Architecture

```
plans_service/
├── config.py                   # Configuration
├── main.py                     # FastAPI app
├── database.py                 # Database connection
├── dependencies.py             # Dependency injection
├── models/
│   ├── domain.py              # Pydantic models
│   └── database.py            # SQLAlchemy models (8 models)
├── api/
│   └── routes.py              # API endpoints (25+)
├── services/
│   └── plan_service.py        # Business logic
├── repositories/
│   └── plan_repository.py     # Data access layer
├── workflows/
│   ├── plan_lifecycle.py      # Plan workflow
│   └── review_workflow.py     # Review workflow
└── requirements.txt
```

## Database Models

### Plan (Main)
- Plan identification and classification
- ISO 8.4.4 content (objectives, scope, triggers)
- Recovery objectives (RTO/RPO/MTPD)
- Team assignments
- Approval workflow
- Review scheduling

### Procedure
- Procedure sequencing
- Step-by-step procedures
- Dependencies and prerequisites
- Resource requirements
- Success criteria

### PlanResource
- Resource classification (7 types)
- Availability requirements
- Criticality levels
- Alternative resources

### ContactList
- Contact information
- Call tree structure
- List types (internal, external, emergency, etc.)

### PlanActivation
- Activation tracking
- Performance metrics
- RTO achievement
- Effectiveness ratings

### PlanReview
- Review tracking
- Findings and recommendations
- Action items
- Approval workflow

### CommunicationTemplate
- Template library
- Variable substitution
- Approval requirements

### PlanTemplate
- Plan templates
- Reusable structures
- Global/tenant templates

## Workflows

### Plan Lifecycle
```
DRAFT → UNDER_REVIEW → APPROVED → ACTIVE → ARCHIVED
  ↓         ↓           ↓          ↓
 edit     reject      activate  deactivate
```

### Review Workflow
- Scheduled reviews
- Post-exercise reviews
- Post-incident reviews
- Organizational change reviews

## API Endpoints

### Plan Management (10 endpoints)
- `POST /api/plans/plans` - Create plan
- `GET /api/plans/plans` - List plans
- `GET /api/plans/plans/{id}` - Get plan
- `PUT /api/plans/plans/{id}` - Update plan
- `DELETE /api/plans/plans/{id}` - Archive plan
- `POST /api/plans/plans/{id}/submit-review` - Submit for review
- `POST /api/plans/plans/{id}/approve` - Approve plan
- `POST /api/plans/plans/{id}/activate` - Activate plan
- `GET /api/plans/plans/{id}/workflow` - Get workflow status

### Procedure Management (4 endpoints)
- `POST /api/plans/plans/{id}/procedures` - Add procedure
- `GET /api/plans/plans/{id}/procedures` - List procedures
- `PUT /api/plans/plans/{id}/procedures/{proc_id}` - Update procedure
- `DELETE /api/plans/plans/{id}/procedures/{proc_id}` - Delete procedure

### Resource Management (2 endpoints)
- `POST /api/plans/plans/{id}/resources` - Add resource
- `GET /api/plans/plans/{id}/resources` - List resources

### Contact Lists (2 endpoints)
- `POST /api/plans/contact-lists` - Create contact list
- `GET /api/plans/contact-lists` - List contact lists

### Plan Activation (2 endpoints)
- `POST /api/plans/plans/{id}/activate-real` - Activate for incident
- `GET /api/plans/activations` - List activations

### Plan Reviews (2 endpoints)
- `POST /api/plans/plans/{id}/reviews` - Create review
- `GET /api/plans/plans/{id}/reviews` - List reviews

**Total:** 25+ endpoints

## Integration

### With Planning Service
- Links to approved strategies
- Strategy implementation via plans

### With BIA Service
- Plans based on BIA results
- RTO/RPO from BIA analysis

### With Risk Service
- Plans based on risk assessments
- Risk mitigation through plans

### With Incident Service
- Plan activation during incidents
- Incident response integration

### With Exercise Service
- Plan testing and validation
- Post-exercise reviews

## ISO 22301 Compliance

### Clause 8.4.1 - General
- ✅ BC plans established and documented
- ✅ Plans based on BIA and risk assessment
- ✅ Plans define recovery strategies

### Clause 8.4.2 - Incident Response Structure
- ✅ Roles and responsibilities defined
- ✅ Authority to act specified
- ✅ Incident response process

### Clause 8.4.3 - Warning and Communication
- ✅ Contact lists with call trees
- ✅ Communication templates
- ✅ Stakeholder notification procedures

### Clause 8.4.4 - BC Plans and Procedures
- ✅ Activation triggers and criteria
- ✅ Response and recovery procedures
- ✅ Communication requirements
- ✅ Resource requirements
- ✅ External dependencies
- ✅ Recovery priorities
- ✅ Return to normal procedures

## Running the Service

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://bcm:bcm@localhost:5432/bcm"
export EVENTBUS_URL="http://localhost:8001"
export ORCHESTRATOR_URL="http://localhost:8002"

# Run service
python -m plans_service.main
```

### Docker
```bash
docker build -t plans_service .
docker run -p 8023:8023 plans_service
```

## Configuration

Key settings in `config.py`:
- `SERVICE_PORT`: 8023
- `DATABASE_URL`: PostgreSQL connection
- `EVENTBUS_URL`: EventBus service
- `ORCHESTRATOR_URL`: Orchestrator service
- `PLANNING_SERVICE_URL`: Planning service (strategies)
- `BIA_SERVICE_URL`: BIA service
- `RISK_SERVICE_URL`: Risk service
- `INCIDENT_SERVICE_URL`: Incident service

## License

Internal - Company Use Only
