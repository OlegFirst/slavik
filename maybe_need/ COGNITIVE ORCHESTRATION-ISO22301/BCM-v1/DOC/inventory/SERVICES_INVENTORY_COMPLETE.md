# BCM Platform Services Inventory - Complete Reference

## 📊 Service Overview Dashboard

| Service Name | Port | Status | Health | Dependencies | Function |
|-------------|------|--------|---------|-------------|----------|
| **Core Platform** |||||
| Odoo BCM Platform | 8069 | ✅ Running | ⚠️ Unhealthy | postgres, redis | Main BCM application |
| PostgreSQL | 5432 | ✅ Running | ✅ Healthy | - | Primary database |
| Redis | 6379 | ✅ Running | ✅ Healthy | - | Cache & sessions |
| RabbitMQ | 5672 | ✅ Running | ✅ Healthy | - | Message queue |
| **AI Services** |||||
| AI Orchestrator | 8000 | ✅ Running | ⚠️ Unhealthy | redis, rabbitmq | Main AI coordination |
| Scenario Orchestrator | 8085 | ✅ Running | ✅ Healthy | ai_orchestrator | AI scenario generation |
| Docker AI PoC | 8090 | ✅ Running | ✅ Healthy | ai_orchestrator | Unified AI processing |
| BIA Engine | 8082 | ✅ Running | ⚠️ Unhealthy | redis, rabbitmq | ML Business Impact Analysis |
| Document Processor | 8083 | ✅ Running | ⚠️ Unhealthy | redis, rabbitmq | AI document intelligence |
| Compliance Checker | 8084 | ✅ Running | ⚠️ Unhealthy | redis, rabbitmq | ISO 22301 automation |
| **Integration Services** |||||
| MCP Server | 8087 | ✅ Running | ✅ Healthy | odoo, postgres | AI tool integration |
| EventBus | 8001 | ✅ Running | ✅ Healthy | rabbitmq | Event coordination |
| Notification Service | 8002 | ✅ Running | ✅ Healthy | redis | Multi-channel alerts |
| **Backend Services** |||||
| BPMN Service | 8005 | ✅ Running | ⚠️ Unhealthy | postgres, eventbus | Workflow execution |
| Deployer | 8009 | ✅ Running | ✅ Healthy | postgres, redis | Deployment automation |
| GitHub App | 8011 | ✅ Running | ⚠️ Unhealthy | ai_orchestrator | Development integration |
| **Adapters** |||||
| LMS Adapter | 8006 | ✅ Running | ⚠️ Unhealthy | eventbus | Learning management |
| TheHive Adapter | 8007 | ✅ Running | ✅ Healthy | eventbus | Security incidents |
| Grafana Adapter | 8008 | ✅ Running | ⚠️ Unhealthy | eventbus | Monitoring bridge |
| **Frontend** |||||
| Web Portal | 3002 | ✅ Running | ⚠️ Unhealthy | odoo, backend APIs | Vue.js main interface |
| Admin Panel | 3001 | ✅ Running | ✅ Healthy | odoo | React admin interface |
| **Infrastructure** |||||
| Traefik Proxy | 80/443/8888 | ✅ Running | ✅ Healthy | - | Reverse proxy & SSL |
| Grafana | 3003 | ✅ Running | ✅ Healthy | redis | Monitoring dashboard |
| MailHog | 1025/8025 | ✅ Running | ✅ Healthy | - | Email testing |

## 🔍 Service Detail Breakdown

### **🎯 AI Services Cluster**

#### **AI Orchestrator** (:8000)
```yaml
Location: /services/ai_orchestrator/main.py
Function: Central AI coordination hub
Capabilities:
  - Risk analysis and assessment
  - Incident classification automation
  - Recovery planning assistance
  - Natural language query processing
  - BIA automation support

API Endpoints:
  - POST /analyze/process-risk
  - POST /analyze/incident
  - POST /nlp/query
  - GET /health

Dependencies:
  - Redis for caching AI context
  - RabbitMQ for async AI processing
  - Supabase for AI memory storage

Current Issues:
  - Health check failing (needs investigation)
  - NLP responses basic (needs enhancement)
```

#### **Scenario Orchestrator** (:8085)
```yaml
Location: /services/scenario_orchestrator/main.py
Function: AI-powered scenario generation
Capabilities:
  - Dynamic scenario creation
  - Multi-category scenario support
  - JaamSim configuration generation
  - Integration with AI Orchestrator

API Endpoints:
  - POST /scenarios/generate
  - GET /scenarios/available
  - GET /health

Current State:
  - ✅ Working: AI generation pipeline
  - ✅ Working: Local scenario storage
  - 📋 Pending: Odoo integration
  - 📋 Pending: Frontend connection

Generated Scenario Categories:
  - epidemic, blackout, cyber, supply
  - natural, terrorism, financial, other
```

#### **Docker AI PoC** (:8090)
```yaml
Location: /services/docker-ai/unified_ai_service.py
Function: Unified AI service combining multiple AI capabilities
Features:
  - Multi-service AI processing
  - Agent-based architecture
  - Docker AI native integration

Current Implementation:
  - ✅ Service running and healthy
  - ✅ Health endpoint responding
  - 📋 Needs: Integration with other AI services
  - 📋 Needs: Specific AI agent functionality
```

---

### **🔗 Integration Services Cluster**

#### **MCP Server** (:8087)
```yaml
Location: /integrations/mcp-server/main.py
Function: Model Context Protocol for AI tool integration
Available Tools:
  - odoo: Direct Odoo API access
  - postgres: Database queries
  - redis: Cache operations
  - grafana: Monitoring data
  - thehive: Security context

Configuration:
  MCP_TOOLS: "odoo,keycloak,postgres,redis,grafana,thehive"
  ODOO_URL: "http://odoo:8069"
  POSTGRES_URL: "postgresql://odoo:password@postgres:5432/bcm_platform"

Current State:
  - ✅ Healthy and responding
  - ✅ Tool integration working
  - 📋 Needs: AI model connections
```

#### **Exercise Simulators Bridge** (:8094)
```yaml
Location: /integrations/exercise_simulators/bridge_service.py
Function: Unified API for JaamSim and NICS integration
Capabilities:
  - JaamSim discrete event simulation
  - NICS incident command integration
  - Real-time exercise monitoring
  - WebSocket participant updates

Simulation Engines:
  - JaamSim: Java-based discrete event simulation
  - NICS: Next Generation Incident Command System
  - Templates: IT failure, supply chain, cyber incidents

Current State:
  - 📋 Container configured but not deployed
  - ✅ JaamSim templates ready
  - ✅ NICS client code implemented
  - 📋 Needs: Service deployment and testing
```

---

### **🔧 Backend Services Cluster**

#### **EventBus** (:8001)
```yaml
Location: /backend/eventbus/main.py
Function: Central event coordination and routing
Features:
  - Asynchronous event processing
  - Service-to-service communication
  - Event logging and audit trail
  - Multi-tenant event isolation

Event Types:
  - Scenario events (created, published, applied)
  - Exercise events (started, completed, failed)
  - Incident events (detected, escalated, resolved)
  - System events (health, performance, errors)

Integration Points:
  - All backend services publish events
  - Notification service subscribes to alerts
  - BPMN service subscribes to workflow triggers
```

#### **BPMN Service** (:8005)
```yaml
Location: /backend/bpmn_service/main.py
Function: BPMN 2.0 workflow execution engine
Features:
  - Process definition management
  - Process instance execution
  - User task assignment and tracking
  - Process variable management

BPMN Capabilities:
  - User tasks for human interaction
  - Service tasks for automated operations
  - Gateways for conditional logic
  - Error handling and compensation

Current Issues:
  - Health check failing
  - Integration with bcm_exercise needed
  - Workflow templates not deployed
```

#### **Notification Service** (:8002)
```yaml
Location: /services/notification_service/main.py
Function: Multi-channel notification system
Channels Supported:
  - Email (SMTP)
  - Microsoft Teams (Webhooks)
  - Slack (Webhooks)
  - SMS (Twilio)
  - PagerDuty (API)

Features:
  - Template-based notifications
  - Escalation rules and routing
  - Delivery status tracking
  - Multi-language support

Current State:
  - ✅ Service healthy and running
  - ✅ External integration code ready
  - 📋 Needs: Webhook configuration
  - 📋 Needs: Integration testing
```

---

## 🌐 External Integration Points

### **Authentication & Security**
```mermaid
graph LR
    USER[User] --> KEYCLOAK[Keycloak SSO<br/>:8080]
    KEYCLOAK --> ODOO[Odoo BCM]
    ODOO --> THEHIVE[TheHive<br/>Security Cases]
    THEHIVE --> ADAPTER[TheHive Adapter<br/>:8007]
    ADAPTER --> EVENTBUS[EventBus]
```

### **Monitoring & Analytics**
```mermaid
graph LR
    SERVICES[All Services] --> METRICS[Metrics Collection]
    METRICS --> GRAFANA[Grafana<br/>:3003]
    GRAFANA --> DASHBOARDS[BCM Dashboards]
    DASHBOARDS --> ALERTS[Alert Rules]
    ALERTS --> NOTIFICATION[Notification Service]
```

### **Development Integration**
```mermaid
graph LR
    GITHUB[GitHub Repository] --> WEBHOOK[GitHub Webhooks]
    WEBHOOK --> GITHUB_APP[GitHub App<br/>:8011]
    GITHUB_APP --> AI_ORCH[AI Orchestrator]
    AI_ORCH --> SUPABASE[Supabase AI Memory]
```

## 📋 Service Health Summary

### **✅ Fully Operational (9 services)**
- PostgreSQL, Redis, RabbitMQ
- MCP Server, EventBus, Notification Service
- Scenario Orchestrator, Docker AI PoC, Deployer

### **⚠️ Running but Unhealthy (8 services)**
- AI Orchestrator, BIA Engine, Document Processor
- Compliance Checker, BPMN Service, GitHub App
- Web Portal, Odoo Platform

### **📋 Configured but Not Deployed (4 services)**
- Exercise Simulators Bridge
- Governance Service
- Simulation Adapter
- JaamSim Engine

## 🎯 Documentation Priorities

1. **Fix unhealthy services** - Debug and resolve health check issues
2. **Deploy missing services** - Complete simulation and governance services
3. **Integration testing** - End-to-end workflow validation
4. **Performance optimization** - Service response time improvements
5. **Security hardening** - Production security configuration

---

**Complete service inventory with current operational status and integration requirements documented.**