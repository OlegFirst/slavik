# BCM Platform Backend Architecture

## Overview

The BCM Platform backend is built using a microservices architecture with FastAPI services that integrate with external systems for business continuity management. The architecture consists of:

- **EventBus Service**: Central event management and message bus
- **BPMN Service**: Workflow engine for business continuity processes
- **LMS Adapter**: Integration with Learning Management Systems (Moodle, Open edX, Canvas)
- **TheHive Adapter**: Security incident and case management integration
- **Grafana Adapter**: KPI dashboards and metrics visualization
- **Authentication Service**: JWT-based authentication and multi-tenancy
- **Document Processor**: Document analysis and processing
- **Notification Service**: Multi-channel notifications
- **Orchestrator Service**: AI-powered workflow orchestration

## Service Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   Load Balancer │
│   (Vue.js)      │◄──►│   (nginx)        │◄──►│   (nginx)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────────────────────┐
        │                    Backend Services                        │
        │                                                           │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
        │  │ EventBus    │  │ Auth        │  │ BPMN        │      │
        │  │ Service     │  │ Service     │  │ Service     │      │
        │  │ :8001       │  │ :8005       │  │ :8005       │      │
        │  └─────────────┘  └─────────────┘  └─────────────┘      │
        │                                                           │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
        │  │ LMS         │  │ TheHive     │  │ Grafana     │      │
        │  │ Adapter     │  │ Adapter     │  │ Adapter     │      │
        │  │ :8006       │  │ :8007       │  │ :8008       │      │
        │  └─────────────┘  └─────────────┘  └─────────────┘      │
        └───────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────────────────────┐
        │                   Data Layer                              │
        │                                                           │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
        │  │ PostgreSQL  │  │ Redis       │  │ Supabase    │      │
        │  │ (Events)    │  │ (Cache)     │  │ (Primary)   │      │
        │  └─────────────┘  └─────────────┘  └─────────────┘      │
        └───────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────────────────────┐
        │                External Integrations                     │
        │                                                           │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
        │  │ Moodle/     │  │ TheHive     │  │ Grafana     │      │
        │  │ edX/Canvas  │  │ Instance    │  │ Instance    │      │
        │  └─────────────┘  └─────────────┘  └─────────────┘      │
        └───────────────────────────────────────────────────────────┘
```

## Core Services

### 1. EventBus Service (Port 8001)

**Purpose**: Central event management system for all BCM modules

**Features**:
- Event publishing and subscription
- Event history and auditing
- Real-time event streaming (SSE & WebSocket)
- Event validation and correlation
- Multi-tenant event isolation

**Key Endpoints**:
```
POST   /api/events/publish          - Publish new event
GET    /api/events/history          - Retrieve event history
GET    /api/events/stream           - SSE event stream
GET    /api/events/stats            - Event statistics
POST   /api/events/validate         - Validate event structure
WS     /api/events/ws               - WebSocket event stream
```

**Event Types**:
- `bcm.bia.started` / `bcm.bia.completed`
- `bcm.plan.generated` / `bcm.plan.approved`
- `bcm.incident.opened` / `bcm.incident.resolved`
- `bcm.training.completed`
- `bcm.exercise.completed`
- `bcm.kpi.calculated`

### 2. BPMN Service (Port 8005)

**Purpose**: Workflow engine for business continuity processes

**Features**:
- BPMN 2.0 process deployment and execution
- Process instance management
- Task assignment and completion
- Event-driven workflow triggers
- Process monitoring and analytics

**Key Endpoints**:
```
POST   /api/bpmn/processes          - Deploy BPMN process
GET    /api/bpmn/processes          - List processes
POST   /api/bpmn/processes/{id}/start - Start process instance
GET    /api/bpmn/instances          - List process instances
GET    /api/bpmn/tasks              - List tasks
POST   /api/bpmn/tasks/{id}/complete - Complete task
```

**Mock Endpoints**:
```
GET    /api/bpmn/mock/processes     - Mock process data
GET    /api/bpmn/mock/instances     - Mock instance data
GET    /api/bpmn/mock/tasks         - Mock task data
GET    /api/bpmn/mock/templates     - BCM workflow templates
POST   /api/bpmn/mock/deploy-demo-process - Deploy demo process
```

### 3. LMS Adapter (Port 8006)

**Purpose**: Multi-LMS integration for training and competency management

**Supported LMS Types**:
- **Moodle**: Web services API integration
- **Open edX**: OAuth2 and REST API
- **Canvas**: REST API with bearer token

**Features**:
- Multi-LMS configuration management
- Course catalog synchronization
- User enrollment management
- Progress tracking and reporting
- Competency matrix management
- Learning analytics

**Key Endpoints**:
```
POST   /api/lms/configs             - Add LMS configuration
GET    /api/lms/{config_id}/courses - Get courses
POST   /api/lms/{config_id}/courses/{course_id}/enroll - Enroll user
GET    /api/lms/{config_id}/users/{email}/enrollments - User enrollments
GET    /api/lms/{config_id}/courses/{course_id}/launch - Launch course (SSO)
```

**Mock Endpoints**:
```
GET    /api/lms/mock/configs        - Mock LMS configurations
GET    /api/lms/mock/courses        - Mock course data
GET    /api/lms/mock/enrollments    - Mock enrollment data
GET    /api/lms/mock/training-paths - Training curricula
GET    /api/lms/mock/competency-matrix - BCM competency matrix
GET    /api/lms/mock/analytics      - Learning analytics
```

### 4. TheHive Adapter (Port 8007)

**Purpose**: Security incident and case management integration

**Features**:
- Case management with severity classification
- Alert processing and promotion
- Observable management (IOCs)
- Task assignment and tracking
- BCM-specific incident workflows
- Integration with security tools

**Key Endpoints**:
```
POST   /api/thehive/configs         - Add TheHive configuration
POST   /api/thehive/{config_id}/cases - Create case
GET    /api/thehive/{config_id}/cases - List cases
POST   /api/thehive/{config_id}/alerts - Create alert
POST   /api/thehive/{config_id}/alerts/{id}/promote - Promote to case
POST   /api/thehive/{config_id}/bcm/incident - Create BCM incident
```

**Mock Endpoints**:
```
GET    /api/thehive/mock/configs    - Mock TheHive configurations
GET    /api/thehive/mock/cases      - Mock case data
GET    /api/thehive/mock/alerts     - Mock alert data
GET    /api/thehive/mock/templates  - BCM case templates
GET    /api/thehive/mock/metrics    - Incident metrics
```

### 5. Grafana Adapter (Port 8008)

**Purpose**: KPI dashboards and metrics visualization

**Features**:
- Dashboard management and automation
- Data source configuration
- BCM KPI tracking and visualization
- Annotation management for key events
- Alert rule management
- PDF report generation (Enterprise)

**Key Endpoints**:
```
POST   /api/grafana/configs         - Add Grafana configuration
GET    /api/grafana/{config_id}/dashboards - List dashboards
POST   /api/grafana/{config_id}/dashboards - Create dashboard
GET    /api/grafana/{config_id}/datasources - List data sources
POST   /api/grafana/{config_id}/bcm/overview - Create BCM overview dashboard
POST   /api/grafana/{config_id}/kpi/sync - Sync KPIs to annotations
```

**Mock Endpoints**:
```
GET    /api/grafana/mock/kpis       - Mock BCM KPI data
GET    /api/grafana/mock/dashboards - Mock dashboard configs
GET    /api/grafana/mock/incident-metrics - Incident metrics
GET    /api/grafana/mock/training-metrics - Training metrics
GET    /api/grafana/mock/exercise-metrics - Exercise metrics
```

## Event-Driven Architecture

### Event Flow Pattern

```
┌─────────────┐    Event     ┌─────────────┐    Process    ┌─────────────┐
│   Service   │─────────────►│  EventBus   │──────────────►│  Handlers   │
│  (Publisher)│              │   Service   │               │(Subscribers)│
└─────────────┘              └─────────────┘               └─────────────┘
                                    │
                                    ▼
                             ┌─────────────┐
                             │  Event      │
                             │  History    │
                             │ (Database)  │
                             └─────────────┘
```

### Event Correlation

Events can be correlated using `correlation_id` to track complete workflows:

```json
{
  "event_type": "bcm.incident.opened",
  "tenant_id": "tenant_001",
  "correlation_id": "incident_workflow_12345",
  "data": {
    "incident_id": "INC-2024-001",
    "severity": "HIGH"
  }
}
```

## Integration Patterns

### 1. Adapter Pattern

Each external system integration follows a consistent adapter pattern:

```python
class ExternalSystemAdapter(ABC):
    @abstractmethod
    async def authenticate(self) -> bool: pass
    
    @abstractmethod
    async def get_data(self) -> List[Data]: pass
    
    @abstractmethod
    async def create_resource(self, resource: Resource) -> Resource: pass
```

### 2. Configuration Management

All adapters support dynamic configuration:

```python
class AdapterConfig(BaseModel):
    id: str
    name: str
    base_url: HttpUrl
    api_key: str
    tenant_id: str
    is_active: bool = True
    settings: Dict[str, Any] = {}
```

### 3. Event Publishing

Standardized event publishing across all services:

```python
async def publish_event(self, event_type: str, tenant_id: str, data: Dict[str, Any]):
    async with httpx.AsyncClient() as client:
        await client.post(f"{EVENTBUS_URL}/api/events/publish", json={
            "event_type": event_type,
            "tenant_id": tenant_id,
            "data": data
        })
```

## Data Models

### Common Model Patterns

All services follow consistent data modeling:

```python
class BaseModel(PydanticBaseModel):
    id: Optional[str] = None
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
```

### Multi-tenancy

All services implement multi-tenant isolation:

- Database level: `tenant_id` column in all tables
- API level: Tenant validation in all endpoints
- Event level: Tenant-specific event channels

## Security

### Authentication

- JWT-based authentication with RS256 signing
- Token validation middleware across all services
- Role-based access control (RBAC)

### Authorization

- Tenant-based resource isolation
- Role-based endpoint access
- Service-to-service authentication

### Data Protection

- Encrypted sensitive data storage
- Audit logging for all data access
- GDPR compliance features

## Monitoring and Observability

### Health Checks

All services expose health endpoints:
```
GET /health - Service health status
```

### Metrics

- Prometheus metrics exposure
- Custom BCM KPIs
- Performance monitoring

### Logging

- Structured logging with correlation IDs
- Centralized log aggregation
- Error tracking and alerting

## Deployment

### Docker Services

Each service has a dedicated Dockerfile:

```yaml
services:
  eventbus:
    build: ./backend/eventbus
    ports: ["8001:8001"]
    environment:
      - POSTGRES_URL=postgresql://...
      - REDIS_URL=redis://...
      
  bpmn-service:
    build: ./backend/bpmn_service
    ports: ["8005:8005"]
    depends_on: [eventbus]
```

### Environment Configuration

Services use environment variables for configuration:

```bash
# Database
POSTGRES_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379

# Services
EVENTBUS_URL=http://eventbus:8001
CORS_ORIGINS=http://localhost:8081,http://localhost:8069

# External Systems
GRAFANA_URL=https://grafana.company.com
MOODLE_URL=https://moodle.company.com
```

## Testing Strategy

### Unit Tests

- Service-specific unit tests
- Mock external dependencies
- Coverage requirements: >80%

### Integration Tests

- Cross-service integration testing
- EventBus message flow verification
- External system mocking

### End-to-End Tests

- Complete workflow testing
- User journey validation
- Performance testing

### Mock Data

Comprehensive mock data for testing:

- `mock_data.py` in each service
- Realistic BCM scenarios
- Performance test data sets

## API Documentation

All services expose OpenAPI documentation:
- Interactive Swagger UI at `/docs`
- OpenAPI schema at `/openapi.json`
- Redoc documentation at `/redoc`

## Performance Considerations

### Scalability

- Horizontal scaling supported
- Stateless service design
- Database connection pooling
- Redis caching layer

### Optimization

- Async/await throughout
- Database query optimization
- Connection pooling
- Response caching

### Monitoring

- Response time monitoring
- Throughput measurement
- Error rate tracking
- Resource utilization metrics