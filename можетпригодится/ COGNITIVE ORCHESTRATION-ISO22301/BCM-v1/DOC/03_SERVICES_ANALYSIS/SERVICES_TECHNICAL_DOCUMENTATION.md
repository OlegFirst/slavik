# ISO-22301 BCM Platform - Services Technical Documentation

**Version:** 2.0.0
**Last Updated:** 2025-09-28
**Platform:** Digital BCM Organism with 10 AI Organs
**Architecture:** Microservices-based with Event-Driven Communication

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Platform Architecture Overview](#platform-architecture-overview)
3. [Services Catalog](#services-catalog)
4. [AI & Intelligence Services](#ai--intelligence-services)
5. [Core BCM Services](#core-bcm-services)
6. [Integration & Communication Services](#integration--communication-services)
7. [Infrastructure & Support Services](#infrastructure--support-services)
8. [Service Dependencies Matrix](#service-dependencies-matrix)
9. [Deployment Status & Health](#deployment-status--health)
10. [API Endpoints Reference](#api-endpoints-reference)
11. [Configuration & Environment Variables](#configuration--environment-variables)
12. [Development Guidelines](#development-guidelines)

---

## Executive Summary

The ISO-22301 BCM Platform is a comprehensive, AI-powered Business Continuity Management system comprising **32 microservices** organized into 4 architectural layers:

- **AI & Intelligence Layer** (10 services): AI orchestration, machine learning, natural language processing
- **Core BCM Layer** (8 services): Business impact analysis, scenario management, compliance checking
- **Integration Layer** (6 services): External system adapters, event bus, API gateway
- **Infrastructure Layer** (8 services): Databases, messaging, monitoring, authentication

**Key Technologies:**
- **Backend:** Python (FastAPI, Flask), Node.js (Express)
- **Databases:** PostgreSQL 15, MongoDB, Redis 7
- **Messaging:** RabbitMQ, Redis Pub/Sub
- **AI/ML:** Anthropic Claude, Local LLMs, Supabase Vector Store
- **Orchestration:** Docker Compose, Kubernetes-ready

---

## Platform Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI & INTELLIGENCE LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│  ai_orchestrator  │  ai_consultant  │  ai_control_center        │
│  ai_workflow_optimizer  │  docker-ai  │  docker-ai-poc          │
│  scenario_orchestrator  │  digital-twin-engine                  │
│  digital-twin-platform  │  knowledge-base                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CORE BCM LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  bia_engine  │  compliance_checker  │  document_processor       │
│  bcm_content_training_bridge  │  process_mining_service         │
│  notification_service  │  monitoring_service                    │
│  template_library  │  document_management                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INTEGRATION LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  unified_api_gateway  │  unified_control_center                 │
│  unified_database_gateway  │  crm_bridge  │  github_app         │
│  community  │  realtime_websocket                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  postgres  │  redis  │  rabbitmq  │  keycloak  │  grafana      │
│  mailhog  │  traefik  │  deployer                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Services Catalog

### Quick Reference Table

| Service Name | Type | Port | Technology | Status | Docker Compose |
|-------------|------|------|------------|--------|----------------|
| ai_orchestrator | AI Core | 8000 | FastAPI/Python | Active | ✅ |
| ai_consultant | AI Agent | - | Python | Development | ❌ |
| ai_control_center | AI Dashboard | - | Node.js | Development | ❌ |
| ai_workflow_optimizer | AI Optimization | - | Python | Development | ❌ |
| bia_engine | BCM Core | 8082 | FastAPI/Python | Active | ✅ |
| scenario_orchestrator | BCM Core | 8085 | FastAPI/Python | Active | ✅ |
| compliance_checker | BCM Core | 8084 | FastAPI/Python | Active | ✅ |
| document_processor | BCM Core | 8083 | FastAPI/Python | Active | ✅ |
| notification_service | Support | 8002 | FastAPI/Python | Active | ✅ |
| github_app | Integration | 8011 | FastAPI/Python | Active | ✅ |
| deployer | DevOps | 8009 | FastAPI/Python | Active | ✅ |
| unified_api_gateway | Integration | - | Python | Development | ❌ |
| unified_control_center | Integration | - | Python | Development | ❌ |
| unified_database_gateway | Integration | - | Python | Development | ❌ |
| digital-twin-platform | Simulation | - | Node.js | Development | ❌ |
| digital-twin-engine | Simulation | - | Node.js | Development | ❌ |
| docker-ai | AI Service | 8090 | Python | Active | ✅ |
| docker-ai-poc | AI PoC | - | Python | Development | ❌ |
| knowledge-base | Knowledge Mgmt | - | TypeScript | Library | ❌ |
| bcm_content_training_bridge | Training | - | Python | Development | ❌ |
| community | Community | - | Python | Development | ❌ |
| crm_bridge | Integration | - | Python | Development | ❌ |
| monitoring_service | Infrastructure | - | Python | Development | ❌ |
| process_mining_service | Analytics | - | Python | Development | ❌ |
| template_library | Support | - | Docker | Development | ❌ |
| document_management | Support | - | Python | Development | ❌ |
| realtime_websocket | Communication | - | Python | Development | ❌ |
| vscode-extension | Developer Tool | - | TypeScript | Development | ❌ |

---

## AI & Intelligence Services

### 1. AI Orchestrator Service

**Service Name:** `ai_orchestrator`
**Technology Stack:** FastAPI, Python 3.11+, Redis, RabbitMQ, Supabase
**Port:** 8000
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
Central AI coordination hub for the BCM Platform. Orchestrates all AI-powered operations including risk analysis, incident classification, natural language processing, and intelligent DevOps automation.

#### Key Features
- **Risk Analysis Engine:** ML-based business process risk assessment
- **Incident Classification:** Automatic categorization using NLP
- **Natural Language Interface:** Chat-based BCM queries
- **AI DevOps Orchestration:** Intelligent deployment planning and execution
- **Claude Pro Integration:** Advanced AI capabilities via Anthropic API
- **GitHub Copilot Authentication:** Token management for developer tools
- **Supabase AI Memory:** Long-term learning and knowledge accumulation

#### API Endpoints

```
POST /analyze/process-risk        - Analyze business process risks
POST /analyze/incident            - Classify and analyze incidents
POST /nlp/query                   - Natural language query processing
POST /deployment/orchestrate      - AI-driven deployment orchestration
GET  /deployment/history          - View deployment history
POST /deployment/learn            - Manual AI learning feedback
POST /auth/token-exchange         - GitHub JWT to internal token
POST /auth/refresh-token          - Refresh expired token
POST /claude/analyze-changes      - Claude code analysis
POST /claude/generate-config      - Generate deployment configs
POST /claude/analyze-deployment   - Analyze deployment results
POST /claude/create-pr            - Create intelligent PRs
POST /ai/process                  - Route to specialized AI agents
GET  /ai/agents/health            - Check all AI agents health
GET  /ai/agents/analytics         - Get AI agent metrics
GET  /health                      - Service health check
```

#### Configuration

**Environment Variables:**
```bash
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://bcm:bcm123@rabbitmq:5672/
ODOO_URL=http://odoo:8069
GITHUB_APP_ID=<github-app-id>
GITHUB_CLIENT_ID=<github-client-id>
GITHUB_CLIENT_SECRET=<github-client-secret>
GITHUB_WEBHOOK_SECRET=<webhook-secret>
GITHUB_PRIVATE_KEY=<private-key-pem>
SUPABASE_URL=https://mvzlkpzakzlmmxyjjtvr.supabase.co
SUPABASE_KEY=<supabase-anon-key>
ANTHROPIC_API_KEY=<anthropic-api-key>
```

#### Dependencies
- **Internal:** Redis, RabbitMQ
- **External:** Supabase, Anthropic API, GitHub API
- **Python Packages:** `fastapi>=0.104.1`, `uvicorn[standard]>=0.24.0`, `pydantic>=2.11.7`, `redis>=5.0.1`, `pika>=1.3.2`, `httpx>=0.26.0`, `supabase>=2.18.1`

#### Integration Points
- **Odoo BCM Modules:** Risk data synchronization
- **GitHub App:** Webhook processing and Copilot integration
- **BIA Engine:** Business impact analysis coordination
- **Scenario Orchestrator:** Scenario generation intelligence
- **Document Processor:** Document analysis routing

#### Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "ai_orchestrator",
  "version": "2.0.0-ai-agents",
  "ai_agents_enabled": true,
  "ai_agents": {
    "total": 10,
    "healthy": 10
  },
  "timestamp": "2025-09-28T12:00:00"
}
```

#### Architectural Role
**Primary Intelligence Hub** - Coordinates all AI operations across the platform, routes requests to specialized agents, maintains AI memory, and provides intelligent automation for DevOps workflows.

---

### 2. BIA Engine (Business Impact Analysis)

**Service Name:** `bia_engine`
**Technology Stack:** FastAPI, Python 3.11+, NumPy
**Port:** 8082
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
Intelligent Business Impact Analysis engine with ML-powered RTO/RPO optimization, financial impact modeling, and process dependency analysis.

#### Key Features
- **Intelligent RTO/RPO Optimization:** ML algorithms for recovery objectives
- **Financial Impact Modeling:** Industry-specific calculations (Healthcare, Financial, IT, Manufacturing, Retail, etc.)
- **Dependency Analysis:** Cascade risk and critical path identification
- **Industry Coefficients:** Sector-specific multipliers for accurate analysis
- **Compliance Integration:** Regulatory penalty estimation

#### Industry Support
- **Financial Services:** High regulatory impact, 2-hour RTO baseline
- **Healthcare:** Critical operations, 1-hour RTO baseline
- **Manufacturing:** Operational continuity, 8-hour RTO baseline
- **IT Services:** High availability, 1-hour RTO baseline
- **Retail:** Customer-facing, 4-hour RTO baseline

#### API Endpoints

```
POST /compute                     - Comprehensive BIA analysis
POST /optimize/single-process     - Optimize individual process
GET  /health                      - Service health check
GET  /                           - Service information
```

#### Key Data Models

**BusinessProcess:**
```python
{
  "id": int,
  "name": str,
  "industry": "financial|healthcare|manufacturing|it_services|retail",
  "criticality": "critical|high|medium|low",
  "annual_revenue_impact": float,
  "peak_concurrent_users": int,
  "dependencies": [int],
  "compliance_requirements": [str],
  "staff_count": int
}
```

**BIA Response:**
```json
{
  "status": "success",
  "summary": {
    "total_processes_analyzed": 10,
    "critical_processes": 3,
    "total_annual_risk_exposure": 1250000.50,
    "average_rto_hours": 4.5,
    "dependency_analysis": {...}
  },
  "detailed_results": [...]
}
```

#### Configuration

**Environment Variables:**
```bash
DATABASE_URL=postgresql://odoo:postgres123@postgres:5432/bcm_platform
REDIS_URL=redis://redis:6379/1
RABBITMQ_URL=amqp://bcm:bcm123@rabbitmq:5672/
PORT=8082
```

#### Dependencies
- **Internal:** PostgreSQL, Redis, RabbitMQ
- **Python Packages:** `fastapi>=0.104.1`, `numpy>=1.24.0`, `pydantic>=2.11.7`

#### Integration Points
- **AI Orchestrator:** Risk analysis coordination
- **Odoo BCM Modules:** Process data synchronization
- **Compliance Checker:** Regulatory requirement validation

#### Architectural Role
**Core BCM Intelligence** - Provides sophisticated business impact analysis with industry-specific calculations and ML-optimized recovery objectives.

---

### 3. Scenario Orchestrator

**Service Name:** `scenario_orchestrator`
**Technology Stack:** FastAPI, Python 3.11+, httpx
**Port:** 8085
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
AI-powered BCM scenario generation, management, and continuous learning system. Generates realistic exercise scenarios, accumulates experience from past exercises, and improves scenario effectiveness over time.

#### Key Features
- **AI Scenario Generation:** Automated creation of BCM exercise scenarios
- **JaamSim Integration:** Discrete event simulation for complex scenarios
- **Experience Accumulation:** Learning from exercise results
- **Scenario Optimization:** AI-powered improvement recommendations
- **Multi-Category Support:** Epidemic, blackout, cyber, supply chain, natural disaster, terrorism
- **Learning Dashboard:** Platform-wide effectiveness tracking

#### Scenario Categories
1. **Epidemic:** Pandemic/outbreak scenarios
2. **Blackout:** Power infrastructure failures
3. **Cyber:** Cybersecurity incidents
4. **Supply Chain:** Logistics disruptions
5. **Natural Disaster:** Earthquakes, floods, hurricanes
6. **Terrorism:** Security threats

#### API Endpoints

```
POST /scenarios/generate              - Generate AI-powered scenario
GET  /scenarios/available             - List available scenarios
POST /learning/exercise-result        - Submit exercise results for learning
GET  /learning/scenario/{id}/insights - Get accumulated learning insights
GET  /learning/dashboard              - Platform-wide learning metrics
GET  /health                          - Service health check
```

#### Key Data Models

**ScenarioGenerationRequest:**
```python
{
  "category": "epidemic|blackout|cyber|supply|natural|terrorism",
  "complexity": 1-5,
  "duration_hours": 4,
  "participants": 10,
  "affected_systems": [str],
  "custom_objectives": [str],
  "organization_context": str
}
```

**ExerciseResult:**
```python
{
  "exercise_id": str,
  "scenario_id": str,
  "duration_actual_hours": float,
  "participants_count": int,
  "success_metrics": dict,
  "participant_feedback": [dict],
  "simulation_metrics": dict,
  "lessons_learned": [str],
  "effectiveness_score": 0-10
}
```

#### Configuration

**Environment Variables:**
```bash
REDIS_URL=redis://redis:6379/2
AI_ORCHESTRATOR_URL=http://ai_orchestrator:8000
PORT=8085
```

#### Dependencies
- **Internal:** Redis, AI Orchestrator
- **External:** JaamSim (for complex simulations)
- **Python Packages:** `fastapi>=0.104.1`, `httpx>=0.26.0`

#### Integration Points
- **AI Orchestrator:** NLP-based scenario generation
- **Odoo BCM Scenario Hub:** Scenario storage and management
- **Exercise Simulators Bridge:** JaamSim integration for complex scenarios

#### Learning System

The service implements a sophisticated learning system:

1. **Experience Collection:** Gathers data from completed exercises
2. **Pattern Recognition:** Identifies successful elements and common issues
3. **AI-Powered Recommendations:** Generates improvement suggestions after 3+ exercises
4. **Continuous Optimization:** Adapts scenarios based on accumulated knowledge

#### Architectural Role
**Scenario Intelligence Center** - Generates, manages, and continuously improves BCM exercise scenarios using AI and accumulated experience.

---

### 4. Document Processor

**Service Name:** `document_processor`
**Technology Stack:** FastAPI, Python 3.11+
**Port:** 8083
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
AI-powered document intelligence service for BCM documentation processing, analysis, and compliance verification.

#### Key Features
- **Intelligent Document Parsing:** Extract structure and content
- **Compliance Verification:** ISO 22301 requirement checking
- **Document Classification:** Automatic categorization
- **Content Analysis:** Key information extraction

#### API Endpoints

```
POST /process/document            - Process BCM document
POST /analyze/compliance          - Check ISO 22301 compliance
GET  /health                      - Service health check
```

#### Configuration

**Environment Variables:**
```bash
REDIS_URL=redis://redis:6379/3
RABBITMQ_URL=amqp://bcm:bcm123@rabbitmq:5672/
PORT=8083
```

#### Dependencies
- **Internal:** Redis, RabbitMQ
- **Python Packages:** `fastapi>=0.104.1`, `python-multipart>=0.0.18`

#### Architectural Role
**Document Intelligence** - Provides AI-powered document processing and analysis for BCM documentation.

---

### 5. Compliance Checker

**Service Name:** `compliance_checker`
**Technology Stack:** FastAPI, Python 3.11+
**Port:** 8084
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
Automated ISO 22301:2019 compliance verification and continuous monitoring service.

#### Key Features
- **ISO 22301 Verification:** Automated compliance checking
- **Continuous Monitoring:** Real-time compliance tracking
- **Gap Analysis:** Identify compliance gaps
- **Remediation Recommendations:** AI-powered improvement suggestions

#### API Endpoints

```
POST /check/compliance            - Verify ISO 22301 compliance
GET  /check/requirements          - List ISO 22301 requirements
POST /analyze/gaps                - Identify compliance gaps
GET  /health                      - Service health check
```

#### Configuration

**Environment Variables:**
```bash
REDIS_URL=redis://redis:6379/4
RABBITMQ_URL=amqp://bcm:bcm123@rabbitmq:5672/
PORT=8084
```

#### Dependencies
- **Internal:** Redis, RabbitMQ, Knowledge Base
- **Python Packages:** `fastapi>=0.104.1`

#### Integration Points
- **Knowledge Base:** ISO 22301 requirements library
- **Odoo BCM Modules:** Compliance status synchronization

#### Architectural Role
**Compliance Guardian AI Organ** - Automated continuous monitoring and verification of ISO 22301 compliance.

---

### 6. Docker AI Service

**Service Name:** `unified_ai_service` (docker-ai)
**Technology Stack:** Python 3.11+, FastAPI
**Port:** 8090
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
Unified AI service providing local LLM capabilities with Docker Desktop AI integration.

#### Key Features
- **Local LLM Integration:** Docker Desktop AI models
- **OpenAI-Compatible API:** Standard interface
- **Multi-Model Support:** Multiple model selection
- **BCM Enterprise Routing:** Intelligent model selection for tasks

#### Model Configuration

```yaml
Models Available:
  - gemma3:latest (Primary, 2.3GB)
  - smollm2:135M (Fast, 100MB)
  - mistral:latest (Business, 4.1GB)
  - deepseek-r1-distill-llama:latest (Analysis, 4.6GB)
  - deepcoder-preview:latest (Code, 8.4GB)
```

#### API Endpoints

```
POST /v1/chat/completions         - OpenAI-compatible chat
POST /v1/completions              - OpenAI-compatible completion
GET  /v1/models                   - List available models
GET  /health                      - Service health check
```

#### Configuration

**Environment Variables:**
```bash
REDIS_URL=redis://redis:6379/1
AI_ORCHESTRATOR_URL=http://ai_orchestrator:8000
PORT=8090
MODEL_NAME=gemma3:latest
FAST_MODEL=smollm2:135M-Q4_K_M
BUSINESS_MODEL=mistral:latest
ANALYSIS_MODEL=deepseek-r1-distill-llama:latest
CODE_MODEL=deepcoder-preview:latest
```

#### Dependencies
- **Internal:** Redis, AI Orchestrator
- **External:** Docker Desktop AI
- **Python Packages:** `fastapi>=0.104.1`, `httpx>=0.26.0`

#### Architectural Role
**Local AI Provider** - Provides on-premise AI capabilities without external API dependencies.

---

### 7. Digital Twin Platform

**Service Name:** `digital-twin-platform`
**Technology Stack:** Node.js, Express, TypeScript
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Standalone Digital Twin Module for NPO organizations with simulation capabilities.

#### Key Features
- **Organizational Modeling:** Digital representation of organization structure
- **Process Simulation:** Business process modeling and simulation
- **Resource Management:** Digital resource tracking
- **Scenario Testing:** Test BCM scenarios in digital environment
- **MCP Server Integration:** Model Context Protocol for AI integration

#### Technology Stack

**Core Dependencies:**
```json
{
  "express": "^4.21.2",
  "mongodb": "^6.18.0",
  "pg": "^8.16.3",
  "ioredis": "^5.7.0",
  "@supabase/supabase-js": "^2.55.0",
  "@modelcontextprotocol/sdk": "^1.17.3",
  "winston": "^3.11.0",
  "zod": "^3.25.76"
}
```

#### External Adapters

1. **AnyLogic Adapter:** Enterprise simulation integration
2. **MESA Adapter:** Agent-based modeling (Python)
3. **SimPy Adapter:** Process-based simulation (Python)
4. **EpiNow2 Adapter:** Epidemiological forecasting (R)

#### Scripts

```bash
npm start                 # Start main server
npm run dev              # Development mode with watch
npm run web              # Web server mode
npm run mcp:start        # Start MCP server
npm run test             # Run tests
npm run test:coverage    # Coverage report
```

#### Configuration

**Environment Variables:**
```bash
MONGODB_URL=<mongodb-connection-string>
POSTGRES_URL=<postgres-connection-string>
REDIS_URL=redis://redis:6379/0
SUPABASE_URL=<supabase-url>
SUPABASE_KEY=<supabase-key>
```

#### Architectural Role
**Simulation Engine** - Provides digital twin capabilities for organizational modeling and scenario simulation.

---

### 8. Digital Twin Engine

**Service Name:** `digital-twin-engine`
**Technology Stack:** Node.js
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Core simulation engine for digital twin operations.

#### Key Features
- **Real-time Simulation:** Live organizational state modeling
- **Event Processing:** Handle organizational events
- **State Management:** Track digital twin state

#### Architectural Role
**Simulation Core** - Core engine for digital twin simulation operations.

---

### 9. Knowledge Base

**Service Name:** `knowledge-base`
**Technology Stack:** TypeScript, React Hooks
**Port:** Not exposed (Library)
**Docker Status:** ❌ Library module

#### Purpose
Unified source of truth for ISO 22301:2019 standard requirements, processes, controls, and compliance utilities.

#### Key Features
- **ISO 22301 Standard Library:** Complete requirements catalog
- **Module Compliance Matrix:** Map requirements to BCM modules
- **React Hooks:** Easy integration in frontend components
- **Compliance Analysis:** Automated gap analysis
- **Template Library:** Policy, procedure, and plan templates

#### Structure

```
knowledge-base/
├── iso-22301-standard.ts      # Core standard definitions
├── complete-requirements.ts   # Full requirements set
├── hooks.ts                   # React hooks
├── utils.ts                   # Utility functions
└── templates/                 # Document templates
```

#### React Hooks

```typescript
useModuleRequirements(moduleName)    // Get requirements for module
useComplianceAnalysis(moduleName)    // Analyze compliance status
useComplianceGaps()                  // Get compliance gaps
useImplementationRoadmap()           // Get implementation phases
```

#### API (TypeScript)

```typescript
ISO22301KnowledgeBase.getRequirementsByModule(moduleName)
ISO22301KnowledgeBase.validateModuleCompliance(moduleName)
ISO22301KnowledgeBase.getComplianceGaps()
ISO22301KnowledgeBase.getImplementationRoadmap()
ISO22301KnowledgeBase.getRequirementById(requirementId)
```

#### ISO 22301 Coverage

| Section | Title | BCM Modules |
|---------|-------|-------------|
| 4 | Context of the organization | bcm_context |
| 5 | Leadership | bcm_governance |
| 6 | Planning | bcm_risk_management, bcm_bia |
| 7 | Support | bcm_training, bcm_resources |
| 8 | Operation | bcm_plans, bcm_incident_management |
| 9 | Performance evaluation | bcm_audit, bcm_monitoring |
| 10 | Improvement | bcm_improvement |

#### Architectural Role
**Knowledge Repository** - Central repository for ISO 22301 knowledge, requirements, and compliance utilities.

---

### 10. AI Control Center

**Service Name:** `ai_control_center`
**Technology Stack:** Node.js, React
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Central dashboard for monitoring and controlling all AI services across the BCM Platform.

#### Key Features
- **AI Agent Monitoring:** Real-time status of all AI agents
- **Performance Metrics:** AI operation analytics
- **Model Management:** LLM model selection and configuration
- **Alert System:** AI anomaly detection and alerts

#### Dependencies
```json
{
  "@supabase/supabase-js": "^2.55.0",
  "axios": "^1.12.2",
  "ioredis": "^5.7.0",
  "winston": "^3.11.0"
}
```

#### Architectural Role
**AI Operations Dashboard** - Centralized monitoring and control for AI infrastructure.

---

## Core BCM Services

### 11. Notification Service

**Service Name:** `notification_service`
**Technology Stack:** FastAPI, Python 3.11+
**Port:** 8002
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
Multi-channel notification service for BCM alerts, incidents, and communications.

#### Key Features
- **Multi-Channel Support:** Email, SMS, Push notifications
- **Template Management:** Notification templates
- **Priority Routing:** Urgent vs standard notifications
- **Delivery Tracking:** Status and confirmation tracking

#### API Endpoints

```
POST /notify/email                - Send email notification
POST /notify/sms                  - Send SMS notification
POST /notify/push                 - Send push notification
POST /notify/broadcast            - Broadcast to multiple channels
GET  /status/{notification_id}    - Check notification status
GET  /health                      - Service health check
```

#### Configuration

**Environment Variables:**
```bash
REDIS_URL=redis://redis:6379/2
RABBITMQ_URL=amqp://bcm:bcm123@rabbitmq:5672/
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<smtp-username>
SMTP_PASSWORD=<smtp-password>
```

#### Dependencies
- **Internal:** Redis, RabbitMQ
- **External:** SMTP server, SMS gateway
- **Python Packages:** `fastapi>=0.104.1`, `aiosmtplib>=2.0.0`

#### Architectural Role
**Communication Hub** - Handles all outbound notifications for incidents, alerts, and BCM communications.

---

### 12. Monitoring Service

**Service Name:** `monitoring_service`
**Technology Stack:** Python 3.11+
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Platform-wide health monitoring and metrics collection.

#### Key Features
- **Service Health Monitoring:** Track all microservices
- **Metrics Collection:** Performance and usage metrics
- **Alerting:** Automated alerts for issues
- **Dashboard Integration:** Grafana/Prometheus integration

#### Architectural Role
**Platform Monitor** - Continuous health and performance monitoring.

---

### 13. Process Mining Service

**Service Name:** `process_mining_service`
**Technology Stack:** Python 3.11+
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Business process mining and analysis for BCM optimization.

#### Key Features
- **Process Discovery:** Automatic process mapping
- **Bottleneck Detection:** Identify process inefficiencies
- **Compliance Mining:** Process compliance verification
- **Performance Analysis:** Process execution metrics

#### Architectural Role
**Process Intelligence** - Analyzes business processes for optimization and compliance.

---

### 14. BCM Content Training Bridge

**Service Name:** `bcm_content_training_bridge`
**Technology Stack:** Python 3.11+, Odoo ORM
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Bridge between BCM content management and training systems.

#### Key Features
- **Training Content Sync:** Synchronize BCM and training content
- **Course Management:** BCM training course integration
- **Progress Tracking:** Training completion monitoring
- **Certification Management:** BCM certification tracking

#### Architectural Role
**Training Integration** - Connects BCM operations with learning management systems.

---

### 15. Community Service

**Service Name:** `community`
**Technology Stack:** Python 3.11+, FastAPI
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
BCM community marketplace and knowledge sharing platform.

#### Key Features
- **Module Marketplace:** Share and download BCM modules
- **Template Exchange:** Community templates
- **Best Practices:** Shared knowledge base
- **Discussion Forums:** Community collaboration

#### Architectural Role
**Community Platform** - Enables BCM community collaboration and resource sharing.

---

### 16. Template Library

**Service Name:** `template_library`
**Technology Stack:** Docker
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Centralized repository for BCM document templates.

#### Key Features
- **Template Management:** Store and version templates
- **Category Organization:** Templates by type (policies, procedures, plans)
- **ISO 22301 Compliance:** Pre-built compliant templates
- **Customization:** Template customization engine

#### Architectural Role
**Template Repository** - Centralized storage and management of BCM templates.

---

### 17. Document Management

**Service Name:** `document_management`
**Technology Stack:** Python 3.11+
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Comprehensive BCM document lifecycle management.

#### Key Features
- **Version Control:** Document versioning
- **Access Control:** Role-based permissions
- **Audit Trail:** Document change tracking
- **Search:** Full-text document search

#### Architectural Role
**Document Lifecycle** - Manages BCM document creation, storage, and lifecycle.

---

## Integration & Communication Services

### 18. Unified API Gateway

**Service Name:** `unified_api_gateway`
**Technology Stack:** Python 3.11+, FastAPI
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Single entry point for all BCM Platform APIs with routing, authentication, and rate limiting.

#### Key Features
- **API Routing:** Intelligent request routing
- **Authentication:** JWT token validation
- **Rate Limiting:** API throttling
- **API Versioning:** Support for multiple API versions
- **Request Logging:** Comprehensive request logging

#### Planned Endpoints

```
/api/v1/*                         - Version 1 APIs
/api/v2/*                         - Version 2 APIs (future)
GET /api/health                   - Gateway health
GET /api/docs                     - API documentation
```

#### Architectural Role
**API Gateway** - Single entry point and traffic management for all APIs.

---

### 19. Unified Control Center

**Service Name:** `unified_control_center`
**Technology Stack:** Python 3.11+
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Centralized control plane for platform-wide operations and management.

#### Key Features
- **Service Orchestration:** Manage microservices
- **Configuration Management:** Centralized config
- **Deployment Control:** Deployment orchestration
- **Monitoring Dashboard:** Platform overview

#### Architectural Role
**Control Plane** - Centralized platform management and orchestration.

---

### 20. Unified Database Gateway

**Service Name:** `unified_database_gateway`
**Technology Stack:** Python 3.11+, SQLAlchemy
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Unified data access layer providing abstraction over multiple databases.

#### Key Features
- **Multi-Database Support:** PostgreSQL, MongoDB, Redis
- **Query Abstraction:** Unified query interface
- **Connection Pooling:** Optimized connections
- **Data Migration:** Schema management

#### Architectural Role
**Data Access Layer** - Unified interface for all database operations.

---

### 21. CRM Bridge

**Service Name:** `crm_bridge`
**Technology Stack:** Python 3.11+, FastAPI
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Integration bridge between BCM Platform and CRM systems.

#### Key Features
- **CRM Synchronization:** Two-way data sync
- **Contact Management:** CRM contact integration
- **Incident Notifications:** CRM-based alerting
- **Customer Communication:** CRM communication tracking

#### Supported CRMs
- Salesforce
- HubSpot
- Microsoft Dynamics
- Odoo CRM (native)

#### Architectural Role
**CRM Integration** - Connects BCM operations with customer relationship management.

---

### 22. GitHub App

**Service Name:** `github_app`
**Technology Stack:** FastAPI, Python 3.11+
**Port:** 8011
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
GitHub App for webhooks, Copilot Extension integration, and repository automation.

#### Key Features
- **Webhook Processing:** GitHub events handling
- **Copilot Extension:** AI-powered developer assistance
- **Repository Automation:** Automated PR creation and management
- **Code Analysis:** AI-powered code review
- **Deployment Automation:** CI/CD integration

#### API Endpoints

```
POST /webhooks/github             - GitHub webhook handler
GET  /auth/callback               - OAuth callback
POST /copilot/query               - Copilot extension query
GET  /health                      - Service health check
```

#### Configuration

**Environment Variables:**
```bash
GITHUB_APP_ID=<github-app-id>
GITHUB_CLIENT_ID=<client-id>
GITHUB_CLIENT_SECRET=<client-secret>
GITHUB_WEBHOOK_SECRET=<webhook-secret>
GITHUB_PRIVATE_KEY=<private-key-pem>
SUPABASE_URL=<supabase-url>
SUPABASE_KEY=<supabase-key>
AI_ORCHESTRATOR_URL=http://ai_orchestrator:8000
```

#### Dependencies
- **Internal:** AI Orchestrator, Supabase
- **External:** GitHub API
- **Python Packages:** `fastapi>=0.104.1`, `httpx>=0.26.0`, `pyjwt>=2.8.0`

#### Integration Points
- **AI Orchestrator:** AI-powered code analysis
- **Supabase:** Webhook event storage
- **GitHub API:** Repository operations

#### Architectural Role
**Developer Integration** - Connects development workflow with BCM Platform intelligence.

---

### 23. Deployer Service

**Service Name:** `deployer`
**Technology Stack:** FastAPI, Python 3.11+, Docker SDK
**Port:** 8009
**Docker Status:** ✅ Active in docker-compose.yml

#### Purpose
Automated deployment orchestration service for BCM Platform services.

#### Key Features
- **Docker Deployment:** Container orchestration
- **Health Monitoring:** Post-deployment health checks
- **Rollback Support:** Automatic rollback on failure
- **Deployment History:** Track all deployments
- **Status Reporting:** Real-time deployment status

#### API Endpoints

```
POST /deploy/service              - Deploy a service
POST /deploy/rollback             - Rollback deployment
GET  /deploy/status/{id}          - Check deployment status
GET  /deploy/history              - Deployment history
GET  /health                      - Service health check
```

#### Configuration

**Environment Variables:**
```bash
DOCKER_HOST=unix:///var/run/docker.sock
POSTGRES_URL=postgresql://odoo:postgres123@postgres:5432/bcm_platform
REDIS_URL=redis://redis:6379/0
```

#### Dependencies
- **Internal:** PostgreSQL, Redis, Docker socket
- **Python Packages:** `fastapi>=0.104.1`, `docker>=7.0.0`

#### Volume Mounts
```yaml
volumes:
  - ./services/deployer:/app
  - /var/run/docker.sock:/var/run/docker.sock  # Docker control
```

#### Architectural Role
**Deployment Automation** - Handles automated service deployment and orchestration.

---

### 24. Realtime WebSocket

**Service Name:** `realtime_websocket`
**Technology Stack:** Python 3.11+, WebSockets
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
Real-time bidirectional communication for live updates and notifications.

#### Key Features
- **WebSocket Server:** Real-time connections
- **Pub/Sub Integration:** Redis-based messaging
- **Room Management:** Group communications
- **Connection Management:** Handle client connections

#### Architectural Role
**Real-time Communication** - Provides WebSocket-based real-time updates.

---

### 25. AI Workflow Optimizer

**Service Name:** `ai_workflow_optimizer`
**Technology Stack:** Python 3.11+
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
AI-powered workflow analysis and optimization for BCM processes.

#### Key Features
- **Workflow Analysis:** Identify bottlenecks
- **AI Optimization:** Suggest improvements
- **Automation Opportunities:** Identify automation potential
- **Performance Prediction:** Predict workflow outcomes

#### Architectural Role
**Workflow Intelligence** - Analyzes and optimizes BCM workflows using AI.

---

### 26. AI Consultant

**Service Name:** `ai-consultant`
**Technology Stack:** Python 3.11+
**Port:** Not exposed
**Docker Status:** ❌ Development mode

#### Purpose
AI-powered BCM consulting assistant providing expert guidance.

#### Key Features
- **Expert Consultation:** AI-powered BCM advice
- **Best Practices:** Industry best practices recommendations
- **Problem Solving:** Guided problem resolution
- **Documentation:** Automated documentation assistance

#### Architectural Role
**AI Consultant** - Provides intelligent BCM consulting and guidance.

---

### 27. VSCode Extension

**Service Name:** `vscode-extension`
**Technology Stack:** TypeScript, VSCode Extension API
**Port:** Not exposed
**Docker Status:** ❌ Developer tool

#### Purpose
VSCode extension for BCM Platform development with AI assistance.

#### Key Features
- **Code Completion:** BCM-aware code completion
- **Module Templates:** Quick module scaffolding
- **Documentation:** Inline documentation
- **AI Assistance:** Integrated AI help

#### Architectural Role
**Developer Tool** - Enhances developer experience for BCM Platform development.

---

## Infrastructure & Support Services

### Infrastructure Services (Managed via Docker Compose)

#### 28. PostgreSQL Database

**Service Name:** `postgres`
**Technology:** PostgreSQL 15 Alpine
**Port:** 5432
**Docker Status:** ✅ Active

**Purpose:** Primary relational database for BCM Platform data.

**Configuration:**
```yaml
POSTGRES_DB: bcm_platform
POSTGRES_USER: odoo
POSTGRES_PASSWORD: postgres123
POSTGRES_MULTIPLE_DATABASES: keycloak
```

**Volumes:**
- `postgres_data:/var/lib/postgresql/data`
- `./core/database/seeds:/docker-entrypoint-initdb.d/`

**Health Check:**
```bash
pg_isready -U odoo
```

---

#### 29. Redis Cache

**Service Name:** `redis`
**Technology:** Redis 7 Alpine
**Port:** 6379
**Docker Status:** ✅ Active

**Purpose:** In-memory cache and message broker for high-performance operations.

**Volumes:**
- `redis_data:/data`

**Health Check:**
```bash
redis-cli ping
```

**Usage:**
- Database 0: AI Orchestrator
- Database 1: BIA Engine
- Database 2: Notification Service
- Database 3: Document Processor
- Database 4: Compliance Checker

---

#### 30. RabbitMQ

**Service Name:** `rabbitmq`
**Technology:** RabbitMQ 3 Management Alpine
**Ports:** 5672 (AMQP), 15672 (Management UI)
**Docker Status:** ✅ Active

**Purpose:** Message queue for asynchronous service communication.

**Configuration:**
```yaml
RABBITMQ_DEFAULT_USER: bcm
RABBITMQ_DEFAULT_PASS: bcm123
```

**Management UI:** http://localhost:15672

**Volumes:**
- `rabbitmq_data:/var/lib/rabbitmq`

---

#### 31. Keycloak SSO

**Service Name:** `keycloak`
**Technology:** Keycloak 23.0.0
**Port:** 8080
**Docker Status:** ✅ Active

**Purpose:** Single Sign-On (SSO) and identity management for BCM Platform.

**Configuration:**
```yaml
KC_DB: postgres
KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
KEYCLOAK_ADMIN: admin
KEYCLOAK_ADMIN_PASSWORD: <admin-password>
```

**Realms:**
- `bcm-platform`: Main BCM realm

**Clients:**
- `odoo-bcm`: Odoo integration client

**Admin Console:** http://localhost:8080/admin

---

#### 32. Grafana

**Service Name:** `grafana`
**Technology:** Grafana Latest
**Port:** 3003
**Docker Status:** ✅ Active

**Purpose:** Platform monitoring and visualization dashboard.

**Configuration:**
```yaml
GF_SECURITY_ADMIN_PASSWORD: admin123
GF_USERS_ALLOW_SIGN_UP: false
GF_INSTALL_PLUGINS: redis-datasource,prometheus
```

**Dashboard:** http://localhost:3003

**Data Sources:**
- Redis metrics
- Prometheus metrics (future)

**Volumes:**
- `grafana_data:/var/lib/grafana`
- `./monitoring/grafana-dashboard.json:/etc/grafana/provisioning/dashboards/bcm-dashboard.json`

---

## Service Dependencies Matrix

### Critical Dependencies (Must be running first)

| Service | Depends On | Critical |
|---------|-----------|----------|
| postgres | - | YES |
| redis | - | YES |
| rabbitmq | - | YES |
| keycloak | postgres | YES |

### AI Services Dependencies

| Service | Depends On | Optional |
|---------|-----------|----------|
| ai_orchestrator | redis, rabbitmq | NO |
| bia_engine | redis, rabbitmq, postgres | NO |
| scenario_orchestrator | redis, ai_orchestrator | NO |
| document_processor | redis, rabbitmq | NO |
| compliance_checker | redis, rabbitmq | NO |
| docker-ai | redis, ai_orchestrator | YES |

### Integration Services Dependencies

| Service | Depends On | Optional |
|---------|-----------|----------|
| github_app | ai_orchestrator, supabase | YES |
| deployer | postgres, redis, docker | NO |
| notification_service | redis, rabbitmq | NO |

### Dependency Graph

```
postgres ─┐
redis ────┼──> keycloak ──> odoo ──> web_portal
rabbitmq ─┘         │
                    │
                    ├──> ai_orchestrator ──┬──> bia_engine
                    │                      ├──> scenario_orchestrator
                    │                      ├──> document_processor
                    │                      ├──> compliance_checker
                    │                      └──> github_app
                    │
                    └──> notification_service
                         deployer
                         monitoring_service
```

---

## Deployment Status & Health

### Currently Active in Docker Compose

✅ **Infrastructure (5 services)**
- postgres
- redis
- rabbitmq
- keycloak
- grafana

✅ **Core BCM (7 services)**
- odoo
- ai_orchestrator
- bia_engine
- scenario_orchestrator
- document_processor
- compliance_checker
- notification_service

✅ **Integration (3 services)**
- github_app
- deployer
- docker-ai (unified_ai_service)

✅ **Backend Adapters (4 services)**
- eventbus
- bpmn_service
- lms_adapter
- thehive_adapter
- grafana_adapter

✅ **Frontend (3 services)**
- web_portal
- admin_panel
- web_portal_v2

✅ **Support (3 services)**
- mailhog
- traefik
- pdca_assistant

**Total Active:** 25 services

### Development Mode Services

❌ **AI & Intelligence (5 services)**
- ai-consultant
- ai_control_center
- ai_workflow_optimizer
- digital-twin-platform
- digital-twin-engine

❌ **Core BCM (7 services)**
- bcm_content_training_bridge
- community
- monitoring_service
- process_mining_service
- template_library
- document_management
- realtime_websocket

❌ **Integration (3 services)**
- unified_api_gateway
- unified_control_center
- unified_database_gateway
- crm_bridge

❌ **Developer Tools (1 service)**
- vscode-extension

**Total Development:** 16 services

---

## API Endpoints Reference

### Service Port Mapping

| Service | Internal Port | External Port | Protocol |
|---------|--------------|---------------|----------|
| ai_orchestrator | 8000 | 8000 | HTTP |
| bia_engine | 8082 | 8082 | HTTP |
| scenario_orchestrator | 8085 | 8085 | HTTP |
| document_processor | 8083 | 8083 | HTTP |
| compliance_checker | 8084 | 8084 | HTTP |
| notification_service | 8000 | 8002 | HTTP |
| github_app | 8001 | 8011 | HTTP |
| deployer | 8002 | 8009 | HTTP |
| docker-ai | 8090 | 8090 | HTTP |
| odoo | 8069 | 8069 | HTTP |
| postgres | 5432 | 5432 | TCP |
| redis | 6379 | 6379 | TCP |
| rabbitmq | 5672 | 5672 | AMQP |
| rabbitmq (mgmt) | 15672 | 15672 | HTTP |
| keycloak | 8080 | 8080 | HTTP |
| grafana | 3000 | 3003 | HTTP |
| mailhog | 8025 | 8025 | HTTP |
| traefik | 8080 | 8888 | HTTP |
| web_portal | 80 | 3000 | HTTP |
| admin_panel | 3001 | 3001 | HTTP |
| web_portal_v2 | 5173 | 5173 | HTTP |

### Base URLs (Development)

```bash
# AI Services
AI_ORCHESTRATOR_URL=http://localhost:8000
BIA_ENGINE_URL=http://localhost:8082
SCENARIO_ORCHESTRATOR_URL=http://localhost:8085
DOCUMENT_PROCESSOR_URL=http://localhost:8083
COMPLIANCE_CHECKER_URL=http://localhost:8084

# Core Services
ODOO_URL=http://localhost:8069
NOTIFICATION_SERVICE_URL=http://localhost:8002

# Integration Services
GITHUB_APP_URL=http://localhost:8011
DEPLOYER_URL=http://localhost:8009

# Infrastructure
POSTGRES_URL=postgresql://odoo:postgres123@localhost:5432/bcm_platform
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://bcm:bcm123@localhost:5672/
KEYCLOAK_URL=http://localhost:8080
```

---

## Configuration & Environment Variables

### Global Platform Configuration

**Required for all services:**
```bash
# Database
POSTGRES_DB=bcm_platform
POSTGRES_USER=odoo
POSTGRES_PASSWORD=postgres123
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=bcm
RABBITMQ_PASSWORD=bcm123

# Platform
BCM_MODE=production
BCM_VERSION=18.0.1.0.0
```

### AI Services Configuration

```bash
# Anthropic API
ANTHROPIC_API_KEY=<your-anthropic-key>

# Supabase
SUPABASE_URL=https://mvzlkpzakzlmmxyjjtvr.supabase.co
SUPABASE_KEY=<your-supabase-anon-key>

# GitHub App
GITHUB_APP_ID=<app-id>
GITHUB_CLIENT_ID=<client-id>
GITHUB_CLIENT_SECRET=<client-secret>
GITHUB_WEBHOOK_SECRET=<webhook-secret>
GITHUB_PRIVATE_KEY=<private-key-pem>
```

### Security Configuration

```bash
# Keycloak
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=<strong-password>
KEYCLOAK_DB_PASSWORD=<strong-password>
KEYCLOAK_CLIENT_SECRET=<client-secret>

# JWT
JWT_SECRET_KEY=<strong-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8
```

### External Integrations

```bash
# Frontend URL
FRONTEND_URL=https://iso-22301-theta.vercel.app

# CORS Origins
CORS_ORIGINS=https://iso-22301-theta.vercel.app,https://94a0f440b3da.ngrok-free.app

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<smtp-username>
SMTP_PASSWORD=<smtp-password>
EMAIL_FROM=bcm-platform@localhost

# Monitoring
GRAFANA_PASSWORD=admin123
```

### Docker Compose .env Template

```bash
# Database Passwords
DB_PASSWORD=postgres123
KEYCLOAK_DB_PASSWORD=keycloak123
RABBITMQ_PASSWORD=bcm123

# Admin Passwords
KEYCLOAK_ADMIN_PASSWORD=admin123
GRAFANA_PASSWORD=admin123

# AI Services
ANTHROPIC_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=

# GitHub Integration
GITHUB_APP_ID=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_WEBHOOK_SECRET=
GITHUB_PRIVATE_KEY=

# Optional: MongoDB
MONGODB_URL=
MONGODB_DATABASE=

# Optional: GPU
GPU_ENABLED=false
```

---

## Development Guidelines

### Service Development Best Practices

1. **Health Check Endpoint:** Every service MUST have `/health` endpoint
2. **Logging:** Use structured logging with appropriate levels
3. **Error Handling:** Implement comprehensive error handling
4. **Documentation:** OpenAPI/Swagger documentation for all APIs
5. **Testing:** Unit tests and integration tests
6. **Dependencies:** Explicit dependency declaration in requirements.txt or package.json

### Adding New Service

**Step 1: Create Service Directory**
```bash
mkdir -p services/my_new_service
cd services/my_new_service
```

**Step 2: Create Service Files**
```bash
# Python Service
touch main.py requirements.txt Dockerfile

# Node.js Service
npm init -y
touch index.js Dockerfile
```

**Step 3: Implement Health Check**
```python
# Python (FastAPI)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "my_new_service",
        "version": "1.0.0"
    }
```

**Step 4: Add to Docker Compose**
```yaml
my_new_service:
  build:
    context: ./services/my_new_service
    dockerfile: Dockerfile
  depends_on:
    - redis
    - rabbitmq
  environment:
    - REDIS_URL=redis://redis:6379/0
    - RABBITMQ_URL=amqp://bcm:${RABBITMQ_PASSWORD}@rabbitmq:5672/
  ports:
    - "8099:8000"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Testing Services

**Test Individual Service:**
```bash
# Start dependencies
docker-compose up -d postgres redis rabbitmq

# Test service
cd services/my_service
python -m pytest tests/

# Test API
curl http://localhost:8000/health
```

**Integration Testing:**
```bash
# Start all services
docker-compose up -d

# Run integration tests
python scripts/integration_tests.py
```

### Service Communication Patterns

**1. Synchronous HTTP:**
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://ai_orchestrator:8000/analyze/process-risk",
        json={"process_id": 123}
    )
```

**2. Asynchronous Messaging (RabbitMQ):**
```python
import pika

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://bcm:bcm123@rabbitmq:5672/")
)
channel = connection.channel()
channel.queue_declare(queue='bcm_events')
channel.basic_publish(
    exchange='',
    routing_key='bcm_events',
    body=json.dumps(event_data)
)
```

**3. Pub/Sub (Redis):**
```python
import redis

r = redis.from_url("redis://redis:6379/0")
r.publish('bcm_channel', json.dumps(message))
```

### Monitoring and Observability

**Metrics to Track:**
- Request count
- Response times
- Error rates
- Resource usage (CPU, memory)
- Queue depths (RabbitMQ)

**Logging Standards:**
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log structure
logger.info(f"Processing request", extra={
    "service": "ai_orchestrator",
    "endpoint": "/analyze/process-risk",
    "request_id": request_id,
    "duration_ms": duration
})
```

---

## Appendix: Service Quick Reference

### Python Services (FastAPI)
- ai_orchestrator
- bia_engine
- scenario_orchestrator
- document_processor
- compliance_checker
- notification_service
- github_app
- deployer
- docker-ai

### Node.js Services
- digital-twin-platform
- digital-twin-engine
- ai_control_center
- knowledge-base (TypeScript library)

### Infrastructure Services
- postgres (PostgreSQL 15)
- redis (Redis 7)
- rabbitmq (RabbitMQ 3)
- keycloak (Keycloak 23)
- grafana (Grafana latest)

### Development Status
- **Active:** 25 services
- **Development:** 16 services
- **Total:** 41 services

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-09-28 | Technical Documentation Team | Initial comprehensive documentation |

---

**END OF DOCUMENT**