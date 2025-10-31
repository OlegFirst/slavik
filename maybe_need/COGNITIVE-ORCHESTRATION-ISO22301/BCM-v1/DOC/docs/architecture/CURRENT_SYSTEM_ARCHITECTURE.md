# BCM Platform - Enhanced System Architecture (PHASE 1-5 Complete)

## 🏗️ System Overview

```mermaid
graph TD
    %% Frontend Layer
    FE1[Vue.js Web Portal<br/>:3002] --> API{API Gateway}
    FE2[React Admin Panel<br/>:3001] --> API
    FE3[Odoo Web Interface<br/>:8069] --> API

    %% API Gateway & Reverse Proxy
    API --> RP[Traefik Reverse Proxy<br/>:80/:443/:8888]
    RP --> ODOO[Odoo BCM Platform<br/>:8069]

    %% Core BCM Platform
    ODOO --> PG[(PostgreSQL<br/>bcm_platform DB<br/>:5432)]
    ODOO --> REDIS[(Redis Cache<br/>:6379)]
    ODOO --> RMQ[(RabbitMQ<br/>Message Queue<br/>:5672)]

    %% AI Services Layer
    AI1[AI Orchestrator<br/>:8000] --> ODOO
    AI2[Scenario Orchestrator<br/>:8085] --> AI1
    AI3[Docker AI PoC<br/>:8090] --> AI1
    AI4[BIA Engine<br/>:8082] --> REDIS
    AI5[Document Processor<br/>:8083] --> REDIS
    AI6[Compliance Checker<br/>:8084] --> REDIS

    %% Integration Layer
    INT1[MCP Server<br/>:8087] --> ODOO
    INT2[Exercise Simulators<br/>:8094] --> RMQ
    INT3[Governance Service<br/>:8014] --> PG
    INT4[Simulation Adapter<br/>:8012] --> RMQ

    %% Backend Services
    BE1[EventBus<br/>:8001] --> RMQ
    BE2[BPMN Service<br/>:8005] --> PG
    BE3[Notification Service<br/>:8002] --> REDIS
    BE4[GitHub App<br/>:8011] --> AI1

    %% External Integrations
    EXT1[Teams/Slack<br/>Webhooks] --> BE3
    EXT2[TheHive<br/>Security Cases] --> BE1
    EXT3[Grafana<br/>Monitoring] --> REDIS
    EXT4[Keycloak SSO<br/>:8080] --> ODOO

    %% Simulation Engines
    SIM1[JaamSim Engine<br/>VNC :5900] --> INT2
    SIM2[NICS Platform<br/>External] --> INT2

    %% Styling
    classDef frontend fill:#e1f5fe
    classDef core fill:#fff3e0
    classDef ai fill:#f3e5f5
    classDef integration fill:#e8f5e8
    classDef backend fill:#fff8e1
    classDef external fill:#ffebee
    classDef database fill:#e3f2fd

    class FE1,FE2,FE3 frontend
    class ODOO,PG,REDIS,RMQ core
    class AI1,AI2,AI3,AI4,AI5,AI6 ai
    class INT1,INT2,INT3,INT4 integration
    class BE1,BE2,BE3,BE4 backend
    class EXT1,EXT2,EXT3,EXT4,SIM2 external
    class PG,REDIS,RMQ database
```

## 🎯 Architecture Layers

### **Layer 1: Frontend (Presentation)**
- **Vue.js Web Portal** (`:3002`) - Main user interface
- **React Admin Panel** (`:3001`) - Administrative interface
- **Odoo Web Interface** (`:8069`) - Core BCM platform UI

### **Layer 2: Core BCM Platform (Business Logic)**
- **Odoo 18.0 CE** (`:8069`) - Main BCM application with 20+ modules
- **PostgreSQL** (`:5432`) - Primary database (bcm_platform)
- **Redis** (`:6379`) - Caching and session storage
- **RabbitMQ** (`:5672`) - Asynchronous message processing

### **Layer 3: AI Services (Intelligence)**
- **AI Orchestrator** (`:8000`) - Main AI coordination hub
- **Scenario Orchestrator** (`:8085`) - AI scenario generation
- **Docker AI PoC** (`:8090`) - Unified AI processing
- **Specialized AI Engines**: BIA (`:8082`), Document (`:8083`), Compliance (`:8084`)

### **Layer 4: Integration Services (Connectivity)**
- **MCP Server** (`:8087`) - Model Context Protocol for AI tools
- **Exercise Simulators** (`:8094`) - JaamSim + NICS bridge
- **Governance Service** (`:8014`) - Data policies and retention
- **Simulation Adapter** (`:8012`) - Simulation coordination

### **Layer 5: Backend Services (Operations)**
- **EventBus** (`:8001`) - Event coordination and routing
- **BPMN Service** (`:8005`) - Workflow execution engine
- **Notification Service** (`:8002`) - Multi-channel communications
- **GitHub App** (`:8011`) - Development integration

### **Layer 6: External Integrations (Ecosystem)**
- **Authentication**: Keycloak SSO (`:8080`)
- **Security**: TheHive incident management
- **Monitoring**: Grafana dashboards (`:3003`)
- **Communications**: Teams, Slack, SMS, PagerDuty
- **Simulation**: JaamSim (VNC `:5900`), External NICS Platform

## 🔄 Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant ODOO as Odoo BCM
    participant AI as AI Orchestrator
    participant SO as Scenario Orchestrator
    participant DB as PostgreSQL

    %% AI Scenario Generation Flow
    U->>FE: Request new scenario
    FE->>SO: POST /scenarios/generate
    SO->>AI: Query AI for scenario content
    AI-->>SO: Generated scenario data
    SO->>SO: Format & structure data
    SO->>ODOO: Save via REST API
    ODOO->>DB: Store in bcm.scenario
    DB-->>ODOO: Confirm save
    ODOO-->>SO: Return scenario ID
    SO-->>FE: Scenario created response
    FE-->>U: Display new scenario

    %% Exercise Execution Flow
    U->>ODOO: Apply scenario to organization
    ODOO->>BPMN: Create workflow instance
    BPMN->>EventBus: Notify exercise start
    EventBus->>Notification: Send alerts
    Notification->>Teams: Notify participants
    EventBus->>Simulators: Initialize simulation
    Simulators->>JaamSim: Start discrete event simulation
```

## 📊 Service Dependencies

```mermaid
graph LR
    %% Core Dependencies
    PG[(PostgreSQL)] --> ODOO[Odoo BCM]
    REDIS[(Redis)] --> ODOO
    RMQ[(RabbitMQ)] --> EventBus[EventBus]

    %% AI Layer Dependencies
    ODOO --> AI_ORCH[AI Orchestrator]
    AI_ORCH --> SCENARIO_ORCH[Scenario Orchestrator]
    REDIS --> BIA[BIA Engine]
    REDIS --> DOC[Document Processor]
    REDIS --> COMP[Compliance Checker]

    %% Integration Dependencies
    EventBus --> BPMN[BPMN Service]
    EventBus --> NOTIF[Notification Service]
    PG --> GOVERNANCE[Governance Service]
    RMQ --> SIMULATORS[Exercise Simulators]

    %% External Dependencies
    NOTIF --> TEAMS[Teams/Slack]
    BPMN --> WORKFLOWS[Workflow Engine]
    SIMULATORS --> JAAMSIM[JaamSim Engine]
    ODOO --> KEYCLOAK[Keycloak SSO]

    %% Styling
    classDef core fill:#bbdefb
    classDef ai fill:#e1bee7
    classDef integration fill:#c8e6c9
    classDef external fill:#ffcdd2

    class PG,REDIS,RMQ,ODOO core
    class AI_ORCH,SCENARIO_ORCH,BIA,DOC,COMP ai
    class EventBus,BPMN,NOTIF,GOVERNANCE,SIMULATORS integration
    class TEAMS,WORKFLOWS,JAAMSIM,KEYCLOAK external
```

## 📈 Component Interaction Matrix

| Service | Port | Dependencies | Provides | Status |
|---------|------|-------------|----------|---------|
| **Odoo BCM Platform** | 8069 | postgres, redis | Core BCM functionality | ✅ Healthy |
| **AI Orchestrator** | 8000 | redis, rabbitmq | AI coordination | ✅ Healthy |
| **Scenario Orchestrator** | 8085 | ai_orchestrator | AI scenario generation | ✅ Healthy |
| **Docker AI PoC** | 8090 | ai_orchestrator | Unified AI processing | ✅ Healthy |
| **MCP Server** | 8087 | odoo, postgres | AI tool integration | ✅ Healthy |
| **EventBus** | 8001 | rabbitmq | Event coordination | ✅ Healthy |
| **BPMN Service** | 8005 | postgres, eventbus | Workflow execution | ⚠️ Unhealthy |
| **Notification Service** | 8002 | redis | Multi-channel alerts | ✅ Healthy |
| **Exercise Simulators** | 8094 | rabbitmq, jaamsim | Simulation bridge | 📋 Not deployed |
| **Governance Service** | 8014 | postgres | Data governance | 📋 Not deployed |

## 🔧 Configuration Overview

### **Environment Variables**
```bash
# Core Platform
DB_PASSWORD=postgres123
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://bcm:bcm123@rabbitmq:5672/

# AI Integration
AI_ORCHESTRATOR_URL=http://ai_orchestrator:8000
MODEL_RUNNER_URL=http://model_runner:8088
MCP_SERVER_URL=http://bcm_mcp_server:8087

# External Services
FRONTEND_URL=https://iso-22301-theta.vercel.app
KEYCLOAK_URL=http://keycloak:8080
TEAMS_WEBHOOK_URL=${TEAMS_WEBHOOK_URL}
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
```

### **Network Architecture**
- **Internal Network**: Docker bridge network for service communication
- **External Access**: Traefik reverse proxy with SSL termination
- **Database Access**: PostgreSQL with connection pooling
- **Cache Layer**: Redis with multiple DB indexes for different services

## 🎯 Critical Integration Points

### **AI Pipeline**
```
User Request → Scenario Orchestrator → AI Orchestrator → Local LLM → Generated Content
```

### **Exercise Execution**
```
Scenario Application → BPMN Workflow → Task Assignment → Notification → Simulation
```

### **Community Interaction**
```
Scenario Publication → Forum Topic Creation → Discussion → Knowledge Base → Best Practices
```

---

**Next: Detailed component documentation with implementation specifics**