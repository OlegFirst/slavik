# Functional Systems Quick Reference


**Full Analysis:** `/Users/MD/AI-Platform-ISO/catalogs/FUNCTIONAL_SYSTEMS_ANALYSIS.md`

**Total Services:** 45

**Active Services:** 30


---


## 19 Functional Systems


🚀 **Система запуска и оркестрации**

   - Key services: `service-discovery, mio-manager, ai-orchestration`



🛡️ **Система отказоустойчивости**

   - Key services: `event-intelligence, system-bcm-service, circuit-breakers`



🔒 **Система безопасности**

   - Key services: `auth-service, vault, api-gateway`



📊 **Система мониторинга**

   - Key services: `prometheus, grafana, mio-manager, db-intelligence`



🔍 **Система аналитики**

   - Key services: `analytics-specialist, community-intelligence`



💾 **Система хранения данных**

   - Key services: `postgresql, redis, qdrant`



🌐 **API и коммуникации**

   - Key services: `api-gateway, websocket, message-queue, eventbus`



📚 **Система обучения**

   - Key services: `learning-service, ai-foundation, expertise-center`



🔮 **Система предсказаний**

   - Key services: `predictive, analytics-specialist`



🤖 **AI Оркестрация**

   - Key services: `ai-orchestration, agent-router, collective`



👥 **Коллективный AI**

   - Key services: `community-intelligence, collective, expertise-center`



🧬 **Система эволюции**

   - Key services: `event-intelligence, self-learning`



📋 **BCM Business Logic**

   - Key services: `bia, risk, plans, governance, compliance, response`



⚙️ **Workflow Management**

   - Key services: `workflow-intelligence, workflow-engine`



📡 **Event-Driven Architecture**

   - Key services: `eventbus, event-intelligence, websocket`



🧠 **AI Foundation**

   - Key services: `ai-foundation, qdrant, RAG, embeddings`



🔧 **DevOps & Infrastructure**

   - Key services: `devops-agent, project-agent, service-discovery`



✅ **Testing & Validation**

   - Key services: `validation-service, tests, exercises, audit`



🖥️ **User Interface Layer**

   - Key services: `admin-panel, platform-ui, mcp-interface`



---


## 11 Technical Categories


💾 **Database Infrastructure** - 4 services

   - PostgreSQL, Redis, Qdrant, DB Managers



⚡ **Runtime Services** - 3 services

   - Service Discovery, WebSocket, Message Queue



🚪 **Gateway Layer** - 1 service

   - API Gateway



📊 **Observability** - 2 services

   - Prometheus, Grafana



📡 **EventBus Core** - 1 service

   - EventBus



🔒 **Security** - 2 services

   - Auth Service, Vault



🤖 **AI Office** - 6 services

   - MIO, DB Intelligence, Analytics, DevOps, Project, Router



📚 **Shared Libraries** - 2 services

   - Shared, Tests



📋 **Platform Services** - 10 services

   - Planning, BIA, Learning, Validation, Plans, Documents, Governance, Compliance, Risk, Response



🧠 **Intelligent Core** - 12 services

   - Workflow Intelligence, AI Foundation, Expertise, Community, Workflow Engine, AI Orchestration, Event Intelligence, Predictive, Coordination, Collective, Optimizer, System BCM



🖥️ **Interface Layer** - 3 services

   - MCP, Admin Panel, Platform UI



---


## Critical Services (Must Run)


| Port | Service | Purpose |

|------|---------|---------|

| `postgresql:5432` | Database | All data storage |

| `redis:6379` | Cache | Sessions, rate limiting, registry |

| `eventbus:8003` | Events | Async communication |

| `service-discovery:8500` | Registry | Service coordination |

| `api-gateway:8000` | Gateway | External API entry |

| `auth-service:8001` | Auth | Authentication & authorization |

| `mio-manager:8002` | Coordinator | Platform orchestration |

| `workflow-intelligence:8010` | Workflows | Process orchestration |

| `ai-orchestration:8040` | AI Brain | AI coordination |


---


## Integration Patterns


1. **All → Database Managers → PostgreSQL/Redis/Qdrant**

2. **Services ↔ EventBus → Async communication**

3. **External → API Gateway → Service Discovery → Services**

4. **Services /metrics → Prometheus → Grafana**

5. **AI tasks → Agent Router → AI Orchestration → Specialists**

6. **BCM → Workflow Intelligence → Temporal → Execution**

7. **UI ↔ WebSocket ↔ EventBus → Live updates**

8. **AI → RAG → Qdrant → Context retrieval**


---


## Deployment Status


- ✅ **Production (23)**: Fully deployed and operational

- ✅ **Running (3)**: Currently active

- 🟢 **Active (14)**: In use

- 🟡 **Configured (1)**: Set up but not fully deployed

- 📋 **Planned (2)**: Future implementation

- ⚪ **Reserved (3)**: Reserved for future


---


*For detailed analysis, see `/Users/MD/AI-Platform-ISO/catalogs/FUNCTIONAL_SYSTEMS_ANALYSIS.md`*