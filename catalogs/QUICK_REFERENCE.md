# Catalogs Quick Reference

**Last Updated**: 2025-10-12
**Status**: ✅ READY FOR SCENARIO GENERATION

---

## 📊 Platform Structure

```
46 Services
    ↓
11 Subsystems (technical, for deployment)
    ↓
19 Functional Systems (purpose-based, for business)
```

---

## 🗂️ Catalog Files

| File | What | Count |
|------|------|-------|
| `services/SERVICE_CATALOG_DETAILED.yaml` | All services | 46 |
| `subsystems/SUBSYSTEMS_CATALOG.yaml` | Technical subsystems | 11 |
| `systems/SYSTEMS_CATALOG.yaml` | Functional systems | 19 |

---

## 🏗️ 11 Subsystems (L2)

**For deployment and technical management:**

1. 💾 Database Infrastructure (4 services)
2. ⚡ Runtime Services (3 services)
3. 🚪 Gateway Layer (1 service)
4. 📊 Observability (2 services)
5. 📡 EventBus Core (1 service)
6. 🔒 Security (3 services)
7. 🤖 AI Office (7 services)
8. 📚 Shared Libraries (2 services)
9. 📋 Platform Services (11 services)
10. 🧠 Intelligent Core (12 services)
11. 🖥️ Interface Layer (3 services)

---

## 🚀 19 Functional Systems (L3)

**For business understanding and scenarios:**

### Foundation (7 systems)
1. 🚀 **Startup & Orchestration** - service-discovery, mio-manager, ai-orchestration
2. 🛡️ **Resilience & Failover** - event-intelligence, system-bcm-service
3. 🔒 **Security** - auth-service, vault
4. 📊 **Monitoring** - prometheus, grafana, mio-manager
5. 🔍 **Analytics** - analytics-specialist, community-intelligence
6. 💾 **Data Storage** - postgresql, redis, qdrant
7. 🌐 **API & Communication** - api-gateway, websocket, eventbus

### AI Intelligence (6 systems)
8. 📚 **Learning & Knowledge** - learning-service, ai-foundation
9. 🔮 **Predictive Intelligence** - predictive, analytics-specialist
10. 🤖 **AI Orchestration** - ai-orchestration, agent-router
11. 👥 **Community Intelligence** - community-intelligence, collective
12. 🧬 **Evolution** - event-intelligence, ai-orchestration
13. 🧠 **AI Foundation** - ai-foundation, qdrant, expertise-center

### Business & Operations (6 systems)
14. 📋 **BCM Business Logic** - bia, risk, plans, governance, compliance, response
15. ⚙️ **Workflow Management** - workflow-intelligence, workflow-engine
16. 📡 **Event-Driven Architecture** - eventbus, event-intelligence
17. 🔧 **DevOps & Infrastructure** - devops-agent, project-agent
18. ✅ **Testing & Validation** - validation-service, tests
19. 🖥️ **User Interface** - admin-panel, platform-ui (reserved)

---

## 🎯 Critical Services (Must Run)

| Port | Service | System |
|------|---------|--------|
| 5432 | PostgreSQL | Data Storage |
| 6379 | Redis | Data Storage |
| 8003 | EventBus | Event-Driven |
| 8000 | API Gateway | API & Communication |
| 8001 | Auth Service | Security |
| 8002 | MIO Manager | Startup & Orchestration |
| 8010 | Workflow Intelligence | Workflow Management |
| 8040 | AI Orchestration | AI Orchestration |
| 8500 | Service Discovery | Startup & Orchestration |

---

## 🔗 Integration Patterns

1. **All → DB Managers → PostgreSQL/Redis/Qdrant**
2. **Services ↔ EventBus → Async**
3. **External → Gateway → Service Discovery → Services**
4. **Services → Prometheus → Grafana**
5. **AI → Agent Router → Orchestration → Specialists**
6. **BCM → Workflow Intelligence → Temporal**
7. **UI ↔ WebSocket ↔ EventBus**
8. **AI → RAG → Qdrant**

---

## 📈 Statistics

- **Services**: 46 total (30 active, 4 deprecated)
- **Subsystems**: 11 (9 production, 1 reserved)
- **Systems**: 19 (17 production, 1 reserved, 1 planned)
- **Critical**: 7 systems, 8 subsystems

---

## 🚀 Deployment Order

1. **Foundation** → Data Storage, Event-Driven, API
2. **Security & Operations** → Security, Monitoring, Startup, Resilience
3. **AI Intelligence** → AI Foundation, Orchestration, Predictive, Learning
4. **Business** → BCM Logic, Workflows, Analytics
5. **Collaboration** → Community, Evolution, Testing
6. **Management** → DevOps, UI

---

## 📝 Scenario Generation Ready

Now ready to generate:
- **L1 Scenarios**: 46 (one per service)
- **L2 Scenarios**: 11 (one per subsystem)
- **L3 Scenarios**: 19 (one per functional system)
- **L4 Workflows**: User E2E workflows

---

## 🔍 Quick Find

**Find a service:**
```bash
grep -r "service_name" /Users/MD/AI-Platform-ISO/catalogs/services/
```

**Find a subsystem:**
```bash
grep -r "subsystem_id" /Users/MD/AI-Platform-ISO/catalogs/subsystems/
```

**Find a functional system:**
```bash
grep -r "system_id" /Users/MD/AI-Platform-ISO/catalogs/systems/
```

---

## 📚 Full Documentation

- `CATALOG_REBUILD_COMPLETE.md` - Complete rebuild summary
- `FUNCTIONAL_SYSTEMS_ANALYSIS.md` - Deep analysis (60KB)
- `FUNCTIONAL_SYSTEMS_QUICK_REF.md` - Quick reference (4.8KB)

---

**Architecture Approach**: FUNCTIONAL (purpose-based, not technology-based) ✅
