# BCM Platform - Comprehensive Technical Documentation for Frontend Developers

## Overview

The BCM (Business Continuity Management) Platform is a microservices-based architecture implementing ISO 22301 standards with advanced AI capabilities. The platform consists of 16+ specialized services orchestrated via Docker Compose, providing comprehensive business continuity management functionality.

## Architecture Summary

### Core Infrastructure
- **Database**: PostgreSQL 15 (primary), Redis (caching), RabbitMQ (messaging)
- **Authentication**: Keycloak SSO with JWT tokens
- **Container Orchestration**: Docker Compose
- **AI Integration**: Multi-provider AI ecosystem with specialized agents
- **Frontend Integration**: Vue.js frontend with REST API communication

### Service Categories
1. **AI Services** - Intelligent decision-making and automation
2. **Backend Services** - Core platform functionality
3. **Specialized Services** - Domain-specific business logic
4. **Adapter Services** - External system integrations
5. **Infrastructure Services** - Database, caching, messaging

---

## Service Catalog

### 🤖 AI Services

#### 1. AI Orchestrator
- **Port**: 8000
- **Purpose**: Central AI coordination and intelligent automation
- **Technology**: FastAPI + Python + Anthropic SDK
- **Key Features**:
  - Business process risk analysis
  - Incident classification using ML
  - Natural language query processing
  - AI-powered DevOps automation
  - GitHub Copilot integration

#### 2. AI Control Center
- **Port**: 8200
- **Purpose**: Digital BCM Organism management with 10 specialized AI organs
- **Technology**: Node.js + Express + WebSocket
- **Key Features**:
  - AI organ health monitoring
  - Token usage analytics
  - Multi-layer memory system (PostgreSQL, Redis, Supabase)
  - Anthropic Claude integration

### 🔧 Backend Services

#### 3. Authentication Service
- **Port**: 8005
- **Purpose**: JWT-based authentication and multi-tenancy
- **Technology**: FastAPI + SQLAlchemy + bcrypt
- **Database**: PostgreSQL (users, tenants, roles)

#### 4. EventBus Service
- **Port**: 8001
- **Purpose**: Event-driven communication between services
- **Technology**: FastAPI + Redis + PostgreSQL + WebSocket
- **Key Features**:
  - Event publishing with idempotency
  - Real-time event streaming (SSE/WebSocket)
  - Event history and analytics
  - Message validation and routing

### 🎯 Specialized Services

#### 5. BIA Engine (Business Impact Analysis)
- **Port**: 8082
- **Purpose**: Intelligent business impact analysis with ML optimization
- **Technology**: FastAPI + NumPy + scikit-learn
- **Key Features**:
  - RTO/RPO optimization algorithms
  - Financial impact modeling
  - Industry-specific calculations
  - Dependency analysis with cascading risk assessment

#### 6. Scenario Orchestrator
- **Port**: 8085
- **Purpose**: BCM scenario generation and learning system
- **Technology**: FastAPI + httpx
- **Key Features**:
  - AI-powered scenario generation
  - Exercise result accumulation
  - Performance learning and optimization
  - JaamSim integration for complex scenarios

#### 7. Compliance Checker
- **Port**: 8084
- **Purpose**: Automated compliance monitoring and validation
- **Technology**: FastAPI + rule engine

#### 8. Document Processor
- **Port**: 8083
- **Purpose**: Document analysis and processing
- **Technology**: FastAPI + NLP libraries

### 🔗 Adapter Services

#### 9. Grafana Adapter
- **Port**: 8006
- **Purpose**: KPI dashboards and metrics visualization
- **Technology**: FastAPI + Grafana API

#### 10. TheHive Adapter
- **Port**: 8007
- **Purpose**: Security incident management integration
- **Technology**: FastAPI + TheHive API

#### 11. LMS Adapter
- **Port**: 8008
- **Purpose**: Learning management system integration
- **Technology**: FastAPI + LMS APIs

### 🏗️ Infrastructure Services

#### 12. PostgreSQL
- **Port**: 5432
- **Databases**: bcm_platform, keycloak, bcm_events
- **Features**: Multi-database setup with health checks

#### 13. Redis
- **Port**: 6379
- **Purpose**: Caching, session storage, real-time messaging

#### 14. RabbitMQ
- **Port**: 5672 (AMQP), 15672 (Management)
- **Purpose**: Asynchronous message queuing

#### 15. Keycloak
- **Port**: 8080
- **Purpose**: SSO authentication and authorization

#### 16. Odoo BCM Platform
- **Port**: 8069
- **Purpose**: Main business logic and web interface
- **Technology**: Odoo 18.0 with custom BCM modules

---

## API Reference Guide

### Authentication Flow

All API calls require JWT authentication (except health checks and login).

#### Login Endpoint
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "tenant_domain": "company.bcm"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "user_001",
    "email": "user@example.com",
    "full_name": "John Doe",
    "tenant_id": "tenant_001",
    "roles": ["user", "bcm_analyst"]
  },
  "tenant": {
    "id": "tenant_001",
    "name": "ACME Corporation",
    "domain": "company.bcm",
    "plan": "enterprise"
  }
}
```

#### Authentication Headers
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### AI Orchestrator API

#### Risk Analysis
```http
POST /analyze/process-risk
Authorization: Bearer <token>
Content-Type: application/json

{
  "id": 1,
  "name": "Customer Service Process",
  "criticality": 4,
  "rto_hours": 2,
  "rpo_hours": 1,
  "dependencies": [2, 3],
  "resources_required": ["staff", "phones", "crm_system"]
}
```

**Response:**
```json
{
  "status": "success",
  "process_id": 1,
  "analysis": {
    "risk_score": 12.5,
    "risk_level": "high",
    "factors": {
      "criticality_impact": 8,
      "dependency_impact": 1.0,
      "rto_impact": 3.5
    },
    "recommendations": [
      "Develop detailed recovery plan",
      "Define alternative resources",
      "Conduct plan testing"
    ],
    "estimated_downtime_cost": 4000
  },
  "generated_at": "2024-09-16T10:30:00Z"
}
```

#### Incident Classification
```http
POST /analyze/incident
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Database Server Outage",
  "description": "Primary database server is unresponsive, causing system-wide issues",
  "category": "technology",
  "severity": "high",
  "affected_processes": [1, 2, 5]
}
```

**Response:**
```json
{
  "status": "success",
  "incident_id": null,
  "classification": {
    "predicted_category": "technology",
    "original_category": "technology",
    "confidence": 0.95,
    "category_scores": {
      "technology": 3,
      "operational": 1
    },
    "recommended_actions": [
      "Run system diagnostics",
      "Switch to backup systems",
      "Contact technical specialists"
    ],
    "estimated_resolution_time": 6
  },
  "generated_at": "2024-09-16T10:30:00Z"
}
```

#### Natural Language Processing
```http
POST /nlp/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is the risk level for our payment processing system?",
  "context": {
    "use_anthropic": true
  },
  "user_role": "governance_brain"
}
```

**Response:**
```json
{
  "query": "What is the risk level for our payment processing system?",
  "intent": "risk_inquiry",
  "response": "I can help analyze payment processing risks. Please provide the process ID for detailed analysis.",
  "actions": ["request_process_id", "show_risk_analysis_form"],
  "model_used": "anthropic_claude_sonnet"
}
```

### EventBus API

#### Publish Event
```http
POST /api/events/publish
Authorization: Bearer <token>
Content-Type: application/json

{
  "event_type": "bcm.bia.completed",
  "tenant_id": "tenant_001",
  "data": {
    "bia_id": 1,
    "rto": 4,
    "rpo": 2,
    "critical_processes": [1, 2, 3]
  },
  "user_id": "user_123",
  "correlation_id": "flow_456",
  "event_id": "evt_789"
}
```

**Response:**
```json
{
  "id": 123,
  "event_type": "bcm.bia.completed",
  "tenant_id": "tenant_001",
  "data": {
    "bia_id": 1,
    "rto": 4,
    "rpo": 2,
    "critical_processes": [1, 2, 3]
  },
  "user_id": "user_123",
  "correlation_id": "flow_456",
  "metadata": {},
  "created_at": "2024-09-16T10:30:00Z",
  "status": "published"
}
```

#### Event Stream (SSE)
```http
GET /api/events/stream?tenant_id=tenant_001
Authorization: Bearer <token>
Accept: text/event-stream
```

**Response Stream:**
```
data: {"id": 123, "event_type": "bcm.incident.reported", "data": {...}}

data: {"type": "heartbeat", "timestamp": "2024-09-16T10:30:00Z"}

data: {"id": 124, "event_type": "bcm.plan.generated", "data": {...}}
```

### BIA Engine API

#### Comprehensive BIA Analysis
```http
POST /compute
Authorization: Bearer <token>
Content-Type: application/json

{
  "processes": [
    {
      "id": 1,
      "name": "Payment Processing",
      "industry": "financial",
      "criticality": "critical",
      "annual_revenue_impact": 5000000,
      "peak_concurrent_users": 1000,
      "dependencies": [2, 3],
      "compliance_requirements": ["PCI-DSS", "SOX"],
      "staff_count": 25
    }
  ],
  "analysis_period_days": 365,
  "risk_tolerance": 0.05,
  "budget_constraint": 100000
}
```

**Response:**
```json
{
  "status": "success",
  "summary": {
    "total_processes_analyzed": 1,
    "critical_processes": 1,
    "total_annual_risk_exposure": 125000.0,
    "average_rto_hours": 0.5,
    "dependency_analysis": {
      "dependency_analysis": {
        "1": {
          "cascade_risk_score": 12.5,
          "dependency_depth": 2,
          "impact_breadth": 0,
          "critical_path": true
        }
      },
      "critical_path_processes": [1],
      "total_processes": 1,
      "highly_interconnected": [],
      "recommendations": [
        "Prioritize protection of high cascade risk processes: 1"
      ]
    }
  },
  "detailed_results": [
    {
      "process_id": 1,
      "process_name": "Payment Processing",
      "industry": "financial",
      "criticality": "critical",
      "optimization": {
        "optimized_rto_hours": 0.5,
        "optimized_rpo_minutes": 3.75,
        "mtpd_hours": 0.75,
        "confidence_score": 0.925,
        "estimated_improvement_cost": 7500.0
      },
      "financial_impact": {
        "24_hour_downtime": {
          "direct_revenue_loss": 1369863.01,
          "reputation_damage": 1232876.71,
          "regulatory_penalty": 273972.60,
          "productivity_loss": 1200.0,
          "opportunity_cost": 205479.45,
          "total_financial_impact": 3083391.77
        }
      }
    }
  ]
}
```

### Scenario Orchestrator API

#### Generate AI Scenario
```http
POST /scenarios/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "category": "cyber",
  "complexity": 4,
  "duration_hours": 6,
  "participants": 15,
  "affected_systems": ["email", "crm", "payment_gateway"],
  "custom_objectives": [
    "Test incident response procedures",
    "Evaluate communication protocols"
  ],
  "organization_context": "Financial services company"
}
```

**Response:**
```json
{
  "status": "success",
  "scenario_id": "ai_20240916_103000",
  "title": "Cyber BCM Exercise Scenario",
  "file_path": "/app/generated_scenarios/scenario_ai_20240916_103000.json",
  "ai_generated": true,
  "created_at": "2024-09-16T10:30:00Z",
  "note": "Scenario saved locally. Odoo integration in Phase 2."
}
```

#### Submit Exercise Results
```http
POST /learning/exercise-result
Authorization: Bearer <token>
Content-Type: application/json

{
  "exercise_id": "ex_001",
  "scenario_id": "ai_20240916_103000",
  "template_id": "tpl_cyber_001",
  "exercise_type": "full_scale",
  "duration_actual_hours": 5.5,
  "participants_count": 15,
  "success_metrics": {
    "response_time_minutes": 12,
    "communication_effectiveness": 8.5,
    "recovery_time_hours": 4.2
  },
  "participant_feedback": [
    {
      "participant_id": "p_001",
      "rating": 8,
      "comment": "Realistic scenario, good communication flow"
    }
  ],
  "effectiveness_score": 8.2,
  "lessons_learned": [
    "Need faster initial response",
    "Communication protocols work well"
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "exercise_id": "ex_001",
  "scenario_learning_updated": true,
  "total_scenario_uses": 3,
  "avg_effectiveness": 7.8
}
```

### AI Control Center API

#### Organism Health Check
```http
GET /api/organism/health
Authorization: Bearer <token>
```

**Response:**
```json
{
  "organism": {
    "name": "Digital BCM Organism",
    "overall_health": 0.92,
    "status": "healthy",
    "consciousness_level": "active",
    "organs_count": 10
  },
  "organs": {
    "governance_brain": {
      "name": "Governance Brain",
      "status": "healthy",
      "provider": "anthropic",
      "personality": "wise_ruler",
      "health_score": 0.95,
      "last_check": "2024-09-16T10:30:00Z"
    },
    "emergency_response": {
      "name": "Emergency Response",
      "status": "healthy",
      "provider": "local",
      "personality": "emergency_responder",
      "health_score": 0.88
    }
  },
  "timestamp": "2024-09-16T10:30:00Z"
}
```

---

## WebSocket Events

### EventBus WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8001/api/events/ws?tenant_id=tenant_001');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);

  if (data.type === 'heartbeat') {
    console.log('Heartbeat received');
  } else {
    // Handle business event
    console.log('Event received:', data);
  }
};
```

**Event Types:**
- `bcm.bia.started` - BIA analysis initiated
- `bcm.bia.completed` - BIA analysis finished
- `bcm.incident.reported` - New incident reported
- `bcm.plan.generated` - Recovery plan generated
- `bcm.exercise.completed` - Training exercise finished

---

## Service Dependencies

### Dependency Map
```
Frontend (Vue.js)
    ↓
Odoo BCM Platform (Port 8069)
    ↓
┌─ AI Orchestrator (8000) ── Anthropic API
├─ AI Control Center (8200) ── Supabase
├─ Auth Service (8005) ──────── PostgreSQL
├─ EventBus (8001) ─────────── Redis + PostgreSQL
├─ BIA Engine (8082)
├─ Scenario Orchestrator (8085)
├─ Compliance Checker (8084)
├─ Document Processor (8083)
├─ Grafana Adapter (8006) ──── Grafana API
├─ TheHive Adapter (8007) ──── TheHive API
└─ LMS Adapter (8008) ────────── LMS APIs
    ↓
Infrastructure Layer:
├─ PostgreSQL (5432)
├─ Redis (6379)
├─ RabbitMQ (5672)
└─ Keycloak (8080)
```

### Service Start Order
1. **Infrastructure** (PostgreSQL, Redis, RabbitMQ)
2. **Authentication** (Keycloak, Auth Service)
3. **Core Services** (EventBus, AI Orchestrator)
4. **Specialized Services** (BIA Engine, Scenario Orchestrator)
5. **Adapters** (Grafana, TheHive, LMS)
6. **Main Platform** (Odoo BCM)
7. **Frontend** (Vue.js Portal)

---

## Configuration and Deployment

### Environment Variables

#### AI Orchestrator
```bash
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://bcm:bcm123@rabbitmq:5672/
ANTHROPIC_API_KEY=sk-ant-xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx
GITHUB_APP_ID=123456
```

#### Auth Service
```bash
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
POSTGRES_URL=postgresql://odoo:postgres123@postgres/bcm_platform
```

#### EventBus
```bash
REDIS_URL=redis://redis:6379
POSTGRES_URL=postgresql://bcm:bcm_password@postgres/bcm_events
CORS_ORIGINS=http://localhost:8081,http://localhost:8069
```

### Docker Compose Services

```yaml
# Key service configurations
services:
  ai_orchestrator:
    build: ./services/ai_orchestrator
    ports: ["8000:8000"]
    depends_on: [redis, rabbitmq]

  eventbus:
    build: ./backend/eventbus
    ports: ["8001:8001"]
    depends_on: [postgres, redis]

  bia_engine:
    build: ./services/bia_engine
    ports: ["8082:8082"]

  odoo:
    image: maxde4/seh-foundation-iso-22301:latest
    ports: ["8069:8069"]
    depends_on: [postgres, redis]
```

### Health Check Endpoints

All services provide health checks at `/health`:

```http
GET /health
```

**Standard Response:**
```json
{
  "status": "healthy",
  "service": "service_name",
  "version": "1.0.0",
  "timestamp": "2024-09-16T10:30:00Z"
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error description",
  "status_code": 500,
  "timestamp": "2024-09-16T10:30:00Z",
  "path": "/api/endpoint",
  "correlation_id": "req_123456"
}
```

### Common HTTP Status Codes
- **200** - Success
- **201** - Created
- **400** - Bad Request (validation error)
- **401** - Unauthorized (invalid/missing token)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **422** - Unprocessable Entity (business logic error)
- **500** - Internal Server Error
- **503** - Service Unavailable (health check failed)

### Rate Limiting
- Default: 100 requests/minute per token
- AI services: 10 requests/minute for complex operations
- Headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## Integration Patterns

### Event-Driven Architecture
```javascript
// Publishing events
await fetch('/api/events/publish', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    event_type: 'bcm.bia.started',
    tenant_id: 'tenant_001',
    data: { bia_id: 1, process_id: 5 }
  })
});

// Listening to events (SSE)
const eventSource = new EventSource('/api/events/stream?tenant_id=tenant_001');
eventSource.onmessage = function(event) {
  const eventData = JSON.parse(event.data);
  handleBCMEvent(eventData);
};
```

### AI Integration Pattern
```javascript
// AI-powered analysis
const analyzeRisk = async (processData) => {
  const response = await fetch('/analyze/process-risk', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(processData)
  });

  if (response.ok) {
    const analysis = await response.json();
    return analysis.analysis;
  }
  throw new Error('Analysis failed');
};
```

### Multi-tenancy Pattern
```javascript
// All API calls automatically scope to user's tenant
// Token contains tenant_id for automatic filtering
const headers = {
  'Authorization': `Bearer ${userToken}`, // Contains tenant context
  'Content-Type': 'application/json'
};
```

---

## Development Guidelines

### API Best Practices
1. **Always include Authorization header** for protected endpoints
2. **Handle async operations** - AI analysis can take 30-60 seconds
3. **Implement retry logic** for external service calls
4. **Use correlation IDs** for request tracing
5. **Subscribe to relevant events** for real-time updates

### Frontend Integration Tips
1. **Cache authentication tokens** with automatic refresh
2. **Implement WebSocket reconnection** for event streams
3. **Show loading states** for AI operations
4. **Handle tenant switching** if multi-tenant UI
5. **Use optimistic updates** where appropriate

### Testing Endpoints
```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8082/health

# Authentication
curl -X POST http://localhost:8005/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bcm.local","password":"admin123"}'

# AI Analysis (requires auth token)
curl -X POST http://localhost:8000/analyze/process-risk \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id":1,"name":"Test Process","criticality":3}'
```

---

## Monitoring and Observability

### Key Metrics to Monitor
- **Response times** for each service
- **Error rates** by endpoint
- **AI token usage** and costs
- **Event processing** throughput
- **Database connection** pools
- **Memory usage** for AI services

### Logging Format
```json
{
  "timestamp": "2024-09-16T10:30:00Z",
  "level": "INFO",
  "service": "ai_orchestrator",
  "message": "Risk analysis completed",
  "correlation_id": "req_123456",
  "user_id": "user_001",
  "tenant_id": "tenant_001",
  "duration_ms": 1250
}
```

### Health Check Dashboard
The AI Control Center provides a comprehensive health dashboard at `/api/organism/health` showing the status of all AI organs and system components.

---

This comprehensive documentation provides frontend developers with all necessary information to integrate with the BCM Platform's microservices architecture, including API specifications, authentication flows, event patterns, and best practices for building robust BCM applications.