# BCM Platform System Integration Guide

## 🎯 Integration Architecture Overview

The BCM Platform follows a **microservices architecture** with **Odoo as the central hub** and specialized services for AI, simulation, and external integrations.

```mermaid
graph TB
    subgraph "Frontend Layer"
        VUE[Vue.js Portal<br/>:3002]
        REACT[React Admin<br/>:3001]
        ODOO_UI[Odoo Web UI<br/>:8069]
    end

    subgraph "API Gateway Layer"
        TRAEFIK[Traefik Reverse Proxy<br/>:80/:443]
        ODOO_API[Odoo REST API<br/>:8069/api]
    end

    subgraph "Business Logic Layer (Odoo Core)"
        BCM_CORE[bcm_core<br/>Foundation]
        BCM_SCENARIO[bcm_scenario_hub<br/>Scenarios]
        BCM_EXERCISE[bcm_exercise<br/>Exercises]
        BCM_BIA[bcm_bia<br/>Impact Analysis]
        BCM_INCIDENT[bcm_incident<br/>Incidents]
        BCM_COMMUNITY[bcm_community<br/>Forum Bridge]
    end

    subgraph "AI Services Layer"
        AI_ORCH[AI Orchestrator<br/>:8000]
        SCENARIO_AI[Scenario Orchestrator<br/>:8085]
        BIA_AI[BIA Engine<br/>:8082]
        DOC_AI[Document Processor<br/>:8083]
        COMP_AI[Compliance Checker<br/>:8084]
        UNIFIED_AI[Docker AI PoC<br/>:8090]
    end

    subgraph "Integration Services Layer"
        MCP[MCP Server<br/>:8087]
        EVENTBUS[EventBus<br/>:8001]
        NOTIFICATION[Notification Service<br/>:8002]
        BPMN[BPMN Service<br/>:8005]
    end

    subgraph "External Integration Layer"
        TEAMS[Microsoft Teams]
        SLACK[Slack Workspace]
        THEHIVE[TheHive Platform]
        NICS[NICS Platform]
        JAAMSIM[JaamSim Engine]
        GRAFANA[Grafana Monitoring]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>bcm_platform)]
        REDIS_DB[(Redis<br/>Cache & Sessions)]
        RMQ_DB[(RabbitMQ<br/>Message Queues)]
    end

    %% Frontend Connections
    VUE --> TRAEFIK
    REACT --> TRAEFIK
    ODOO_UI --> ODOO_API

    %% API Gateway Connections
    TRAEFIK --> ODOO_API
    ODOO_API --> BCM_CORE

    %% Business Logic Connections
    BCM_CORE --> BCM_SCENARIO
    BCM_CORE --> BCM_EXERCISE
    BCM_CORE --> BCM_BIA
    BCM_SCENARIO --> BCM_COMMUNITY
    BCM_EXERCISE --> BCM_BIA

    %% AI Service Connections
    SCENARIO_AI --> AI_ORCH
    BIA_AI --> AI_ORCH
    DOC_AI --> AI_ORCH
    COMP_AI --> AI_ORCH
    UNIFIED_AI --> AI_ORCH

    %% Integration Connections
    AI_ORCH --> MCP
    EVENTBUS --> NOTIFICATION
    EVENTBUS --> BPMN
    MCP --> BCM_CORE

    %% External Connections
    NOTIFICATION --> TEAMS
    NOTIFICATION --> SLACK
    EVENTBUS --> THEHIVE
    BPMN --> NICS
    BPMN --> JAAMSIM
    REDIS_DB --> GRAFANA

    %% Data Connections
    BCM_CORE --> PG
    AI_ORCH --> REDIS_DB
    EVENTBUS --> RMQ_DB

    %% Styling
    classDef frontend fill:#e1f5fe,stroke:#01579b
    classDef api fill:#f3e5f5,stroke:#4a148c
    classDef business fill:#e8f5e8,stroke:#1b5e20
    classDef ai fill:#fff3e0,stroke:#e65100
    classDef integration fill:#f1f8e9,stroke:#33691e
    classDef external fill:#ffebee,stroke:#b71c1c
    classDef data fill:#e3f2fd,stroke:#0d47a1

    class VUE,REACT,ODOO_UI frontend
    class TRAEFIK,ODOO_API api
    class BCM_CORE,BCM_SCENARIO,BCM_EXERCISE,BCM_BIA,BCM_INCIDENT,BCM_COMMUNITY business
    class AI_ORCH,SCENARIO_AI,BIA_AI,DOC_AI,COMP_AI,UNIFIED_AI ai
    class MCP,EVENTBUS,NOTIFICATION,BPMN integration
    class TEAMS,SLACK,THEHIVE,NICS,JAAMSIM,GRAFANA external
    class PG,REDIS_DB,RMQ_DB data
```

## 🔄 Integration Patterns

### **Pattern 1: AI-Enhanced Scenario Generation**

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Vue.js Frontend
    participant SO as Scenario Orchestrator
    participant AI as AI Orchestrator
    participant Odoo as Odoo BCM
    participant Community as Community Service

    User->>Frontend: Request new scenario
    Frontend->>SO: POST /scenarios/generate
    SO->>AI: Query for scenario content
    AI-->>SO: Generated content
    SO->>SO: Format to BCM structure
    SO->>Odoo: Save via REST API
    Odoo->>Community: Auto-create forum topic
    Community-->>Frontend: Real-time topic update
    Frontend-->>User: Scenario ready notification
```

### **Pattern 2: Exercise Workflow Execution**

```mermaid
sequenceDiagram
    participant User
    participant Odoo as Odoo BCM
    participant BPMN as BPMN Service
    participant EventBus
    participant Notification as Notification Service
    participant Simulators as Exercise Simulators

    User->>Odoo: Apply scenario to organization
    Odoo->>BPMN: Create workflow instance
    BPMN->>EventBus: Publish exercise.started
    EventBus->>Notification: Send participant alerts
    EventBus->>Simulators: Initialize simulation
    Simulators->>JaamSim: Start discrete simulation
    JaamSim-->>Simulators: Simulation metrics
    Simulators->>EventBus: Publish metrics update
    EventBus->>Odoo: Update exercise progress
    Odoo-->>User: Real-time exercise dashboard
```

### **Pattern 3: Community Knowledge Creation**

```mermaid
sequenceDiagram
    participant User
    participant Odoo as Odoo BCM
    participant Community as Community Service
    participant AI as AI Orchestrator
    participant Knowledge as Knowledge Base

    User->>Odoo: Publish new scenario
    Odoo->>Community: Auto-create forum topic
    Community->>User: Notification of new discussion
    User->>Community: Participate in discussion
    Community->>AI: Analyze discussion content
    AI->>Knowledge: Generate best practices article
    Knowledge->>Odoo: Link article to scenario
    Odoo-->>User: Enhanced scenario with community insights
```

## 🔧 Critical Integration Points

### **1. Odoo ↔ AI Services**
```yaml
Integration Method: REST API + MCP Protocol
Data Flow: Bidirectional
Key Endpoints:
  - Odoo → AI: /api/v1/ai/analyze
  - AI → Odoo: /api/v1/scenarios, /api/v1/incidents
Security: API key authentication
Error Handling: Circuit breaker pattern with fallbacks
```

### **2. EventBus ↔ All Services**
```yaml
Integration Method: RabbitMQ messaging
Message Format: JSON with standardized schema
Event Categories:
  - bcm.scenario.* (created, published, applied)
  - bcm.exercise.* (started, completed, failed)
  - bcm.incident.* (detected, escalated, resolved)
  - system.* (health, performance, errors)
```

### **3. Frontend ↔ Backend**
```yaml
Vue.js Portal:
  - Axios HTTP client for API calls
  - WebSocket connection for real-time updates
  - State management via Vuex
  - Authentication via Keycloak integration

React Admin:
  - REST API integration with Odoo
  - Real-time dashboard updates
  - Role-based access control
  - Administrative functions
```

## 🛡️ Security Integration

### **Authentication Flow**
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Keycloak
    participant Odoo
    participant Services

    User->>Frontend: Login request
    Frontend->>Keycloak: Authenticate
    Keycloak-->>Frontend: JWT token
    Frontend->>Odoo: API call with token
    Odoo->>Keycloak: Validate token
    Keycloak-->>Odoo: Token valid + user info
    Odoo->>Services: Forward request with context
    Services-->>Odoo: Processed response
    Odoo-->>Frontend: Final response
    Frontend-->>User: Authenticated session
```

### **Authorization Model**
```yaml
Keycloak Realm: bcm-platform
Client: odoo-bcm

Security Groups:
  - BCM User: Basic access to scenarios and exercises
  - BCM Manager: Full module access + management
  - BCM Admin: System administration + configuration
  - Scenario Reviewer: Scenario moderation and approval
  - Exercise Facilitator: Exercise execution and monitoring

Multi-Tenant Security:
  - Company-based data isolation
  - Role inheritance within company hierarchy
  - Cross-company collaboration controls
```

## 📊 Performance Integration

### **Monitoring Stack**
```mermaid
graph LR
    SERVICES[All Services] --> HEALTH[Health Checks]
    SERVICES --> METRICS[Application Metrics]
    HEALTH --> GRAFANA[Grafana Dashboard]
    METRICS --> GRAFANA
    GRAFANA --> ALERTS[Alert Rules]
    ALERTS --> NOTIFICATION[Notification Service]
    NOTIFICATION --> TEAMS[Teams/Slack/PagerDuty]
```

### **Key Metrics Monitored**
- **Service Health**: Uptime, response times, error rates
- **AI Performance**: Model inference times, accuracy scores
- **Database Performance**: Query times, connection pools
- **Exercise Metrics**: Participation rates, completion times
- **User Engagement**: Scenario usage, community activity

## 🚀 Deployment Integration

### **Container Orchestration**
```yaml
Platform: Docker Compose
Orchestration: Single docker-compose.yml
Service Discovery: Docker internal DNS
Load Balancing: Traefik reverse proxy
Health Monitoring: Built-in Docker health checks
```

### **Data Persistence**
```yaml
Primary Storage: PostgreSQL with Docker volumes
Cache Storage: Redis with persistence enabled
File Storage: Docker volumes for uploads and logs
Backup Strategy: Automated database backups
```

### **Scaling Strategy**
```yaml
Horizontal Scaling:
  - AI services can run multiple instances
  - EventBus supports load distribution
  - Notification service scales independently

Vertical Scaling:
  - PostgreSQL optimized for BCM workloads
  - Redis configured for high throughput
  - AI services with memory optimization
```

---

**This guide provides the complete integration foundation for understanding, maintaining, and extending the BCM Platform ecosystem.**