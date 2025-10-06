# Orchestrator - Integration Specification

**Consolidation Target:** Unified orchestration module
**Sources:** 8 locations
**Total Code:** ~2000+ lines
**Priority:** High (максимальная распорошенность!)

---

## 🎯 PRIMARY FUNCTION

**Unified Platform Coordinator** - координация жизненного цикла ВСЕХ сервисов BCM Platform через 4 типа оркестрации:

1. **Platform Orchestration** - запуск/остановка/мониторинг инфраструктуры
2. **AI Orchestration** - координация AI агентов и моделей
3. **Scenario Orchestration** - генерация и управление сценариями учений
4. **Workflow Orchestration** - BPMN процессы (если есть)

---

## 📂 SOURCE ANALYSIS

### Source #1: `/services/platform-orchestrator/main.py` (300 lines)
**Функция:** Platform запуск и мониторинг

**Ключевые компоненты:**
- `ServiceGroup` class - группировка сервисов по уровням
- `PlatformOrchestrator` class - главный оркестратор
- Dependency-based startup (foundation → infrastructure → business → intelligence → applications)
- Docker management через python-docker
- Redis pub/sub для events
- PostgreSQL для platform status tracking
- Health monitoring с auto-restart

**Service Groups:**
```python
foundation = ['postgres', 'redis', 'rabbitmq']
infrastructure = ['eventbus', 'unified_database_gateway', 'unified_api_gateway']
business = ['odoo', 'bia_engine', 'compliance_checker', 'bpmn_service']
intelligence = ['ai_orchestrator', 'ai_control_center', 'digital_twin']
applications = ['admin_panel', 'web_portal', 'mobile_backend']
```

**Methods:**
- `connect_services()` - Redis + PostgreSQL connections
- `wait_for_dependencies()` - dependency resolution
- `start_group()` - group startup with health checks
- `initialize_database()` - DB schema creation
- `start_platform()` - full platform startup (main entry)
- `monitor_platform()` - continuous monitoring

### Source #2: `/services/ai_orchestrator/main.py` (1195 lines!)
**Функция:** AI coordination + DevOps automation + NLP

**Ключевые компоненты:**
- `BCMIntelligenceEngine` - business intelligence
  - `analyze_business_process_risk()` - RTO/RPO/criticality analysis
  - `classify_incident()` - AI incident classification
- `AIDevOpsEngine` - deployment orchestration
  - `orchestrate_deployment()` - AI-managed deployment
  - `_analyze_service_dependencies()` - dependency analysis
  - `_should_continue_deployment()` - smart failure handling
  - `_extract_lessons()` - learning from deployments
- `ClaudeProEngine` - Anthropic integration
  - `analyze_code_changes()` - code analysis
  - `generate_deployment_config()` - config generation
  - `create_intelligent_pr()` - auto PR creation
- `GitHubTokenManager` - GitHub auth
- `AIAgentRequest` routing - multi-agent coordination

**Endpoints:**
```
POST /analyze/process-risk
POST /analyze/incident
POST /nlp/query
POST /deployment/orchestrate
GET  /deployment/history
POST /claude/analyze-changes
POST /claude/generate-config
POST /ai/process
GET  /ai/agents/health
```

**Integrations:**
- Anthropic API (Claude models)
- Supabase (AI memory storage)
- GitHub (token exchange, PR creation)
- Redis (caching)
- EventBus (events)

### Source #3: `/services/scenario_orchestrator/main.py` (576 lines)
**Функция:** BCM scenario generation and learning

**Ключевые компоненты:**
- `ScenarioGenerationRequest` - scenario parameters
- `generate_ai_scenario()` - AI-powered scenario generation
- `ExerciseResult` - exercise completion tracking
- `ScenarioLearning` - accumulated learning data
- Experience accumulation system
- JaamSim configuration generation

**Endpoints:**
```
POST /scenarios/generate
GET  /scenarios/available
POST /learning/exercise-result
GET  /learning/scenario/{id}/insights
GET  /learning/dashboard
```

**Learning System:**
- Exercise result collection
- Pattern extraction (successful/failed elements)
- AI-powered improvement recommendations
- Dashboard with effectiveness metrics

**Integrations:**
- AI Orchestrator (NLP queries)
- Odoo BCM Scenario Hub
- JaamSim (simulation configs)

### Source #4: `/services/deployer/main.py` (224 lines)
**Функция:** Simple deployment without AI

**ВАЖНО:** Это ДУБЛИКАТ platform-orchestrator! Удалить или merge.

**Компоненты:**
- `BCMDeployer` class
- `start_service()` - docker-compose up
- `check_service_health()` - health checks
- `restart_service()` - auto-restart
- `deploy_platform()` - sequential deployment
- `monitor_services()` - continuous monitoring

**Endpoints:**
```
POST /deploy
GET  /status
POST /restart/{service_name}
POST /monitoring/start
POST /monitoring/stop
```

**Разница с platform-orchestrator:**
- Проще (без Redis/Postgres)
- Меньше функционала
- Тот же самый service_order
- **РЕШЕНИЕ:** MERGE в platform orchestrator

### Source #5-8: Backend/Odoo copies
**Статус:** Требуется проверка в следующем чтении

---

## 🔗 EXTERNAL INTEGRATIONS

### 1. Docker
- **Usage:** Service lifecycle management
- **Methods:** `docker.from_env()`, `containers.get()`, `docker-compose up/down`

### 2. EventBus
- **Usage:** Platform events pub/sub
- **Events Published:**
  - `platform.ready`
  - `group.{name}.ready`
  - `service.failed`
  - `deployment.completed`
- **Events Subscribed:** (TBD - need to check other services)

### 3. Redis
- **Usage:**
  - Platform events channel
  - Service status caching
  - AI memory (Supabase alternative)
- **Clients:** `redis.asyncio`, `redis.from_url()`

### 4. PostgreSQL
- **Usage:**
  - Platform status tracking
  - Deployment history
  - Service registry
- **Tables:**
  - `platform_status`
  - `platform_events`
  - `deployment_history` (AI orchestrator)

### 5. Anthropic API
- **Usage:** Claude models for code analysis
- **Endpoints:**
  - `POST /v1/messages` - Claude chat
- **Models:** `claude-3-5-sonnet-20241022`

### 6. Supabase
- **Usage:** AI knowledge base
- **Tables:**
  - `ai_knowledge` - accumulated learning
  - `github_events` - GitHub integration events
  - `deployment_stats` - deployment analytics

### 7. GitHub
- **Usage:**
  - Token exchange (GitHub JWT → internal token)
  - Auto PR creation
  - Workflow integration
- **APIs:** GitHub REST API v3

### 8. Odoo
- **Usage:**
  - BCM Scenario Hub integration
  - Module calls to orchestrator
- **Endpoints:**
  - `POST /api/v1/bcm_scenario` - save scenarios

### 9. AI Agents (from ai_agent_router.py)
- **Capabilities:**
  - PDCA analysis
  - BIA analysis
  - Document processing
  - Compliance checks
  - Workflow orchestration
  - GitHub integration
  - Decision support
  - Context awareness

---

## 🏗️ CONSOLIDATED ARCHITECTURE

```
orchestrator/
├── core/                          # Shared orchestration logic
│   ├── base_orchestrator.py      # Base class для всех
│   ├── service_registry.py       # Service discovery & registry
│   ├── health_monitor.py         # Health checks & monitoring
│   ├── event_coordinator.py      # EventBus coordination
│   └── docker_manager.py         # Docker API wrapper
│
├── platform/                      # Platform orchestration
│   ├── platform_orchestrator.py  # From source #1
│   ├── service_groups.py         # ServiceGroup logic
│   └── deployment_manager.py     # From source #4 (merge)
│
├── ai/                            # AI orchestration
│   ├── ai_orchestrator.py        # Main AI coordinator
│   ├── intelligence_engine.py    # BCMIntelligenceEngine (from #2)
│   ├── devops_engine.py          # AIDevOpsEngine (from #2)
│   ├── claude_engine.py          # ClaudeProEngine (from #2)
│   ├── agent_router.py           # Multi-agent routing (from #2)
│   └── model_selector.py         # Model selection logic
│
├── scenario/                      # Scenario orchestration
│   ├── scenario_orchestrator.py  # From source #3
│   ├── generator.py              # Scenario generation
│   ├── learning_engine.py        # Exercise learning system
│   └── jaamsim_config.py         # JaamSim configs
│
├── workflow/                      # Workflow orchestration (future)
│   ├── bpmn_orchestrator.py      # BPMN workflows
│   └── task_scheduler.py         # Task scheduling
│
├── control_center/                # Unified control
│   ├── unified_controller.py     # Master controller
│   ├── dashboard_api.py          # Management dashboard
│   └── monitoring_dashboard.py   # Monitoring UI data
│
├── integrations/                  # External integrations
│   ├── eventbus.py               # EventBus client
│   ├── docker_client.py          # Docker wrapper
│   ├── redis_client.py           # Redis client
│   ├── postgres_client.py        # PostgreSQL client
│   ├── anthropic_client.py       # Claude API client
│   ├── supabase_client.py        # Supabase client
│   ├── github_client.py          # GitHub API client
│   └── odoo_client.py            # Odoo integration
│
├── api/                           # REST API
│   ├── platform_routes.py        # Platform endpoints
│   ├── ai_routes.py              # AI endpoints
│   ├── scenario_routes.py        # Scenario endpoints
│   ├── deployment_routes.py      # Deployment endpoints
│   └── monitoring_routes.py      # Monitoring endpoints
│
├── models/                        # Data models
│   ├── platform_models.py        # Platform entities
│   ├── ai_models.py              # AI entities
│   ├── scenario_models.py        # Scenario entities
│   └── deployment_models.py      # Deployment entities
│
├── config/
│   └── settings.py               # Configuration
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── main.py                        # FastAPI app entry
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 📊 CONSOLIDATION STRATEGY

### Phase 1: Foundation (core/)
- Extract common logic from all sources
- Create base classes
- Implement service registry
- Build health monitoring

### Phase 2: Platform Orchestration
- Copy from source #1 (platform-orchestrator)
- Merge source #4 (deployer) - deployment logic only
- Add EventBus publishing
- Database tracking

### Phase 3: AI Orchestration
- Copy from source #2 (ai_orchestrator)
- Split into submodules (intelligence, devops, claude, agents)
- Keep all AI features
- Maintain Anthropic integration

### Phase 4: Scenario Orchestration
- Copy from source #3 (scenario_orchestrator)
- Keep learning system
- Integrate with AI orchestrator
- JaamSim support

### Phase 5: Control Center
- Create unified controller
- Dashboard API
- Monitoring endpoints
- Cross-orchestrator coordination

### Phase 6: Integration Layer
- External service clients
- Error handling
- Retry logic
- Circuit breakers

---

## ❌ WHAT TO DELETE

1. **Source #4 (deployer)** - merge into platform orchestrator, then delete
2. **Backend copies** - (check sources #5-8, likely duplicates)
3. **Odoo service copies** - keep Odoo integration, delete service duplicates

---

## 🔄 EVENT FLOWS

### Platform Startup Flow
```
1. unified_controller.start_all()
2. platform_orchestrator.start_platform()
3. For each service group:
   a. wait_for_dependencies()
   b. start_group()
   c. Publish "group.{name}.ready"
4. Publish "platform.ready"
5. Start monitoring
```

### AI Deployment Flow
```
1. POST /deployment/orchestrate
2. ai_devops.orchestrate_deployment()
3. _analyze_service_dependencies() - AI ordering
4. For each service:
   a. _deploy_service()
   b. _health_check()
   c. If failure: _should_continue_deployment() - AI decision
5. _extract_lessons() - learning
6. _suggest_improvements() - AI recommendations
7. Optional: _create_improvement_pr() - auto PR
```

### Scenario Generation Flow
```
1. POST /scenarios/generate
2. generate_ai_scenario()
3. Query AI Orchestrator NLP
4. Format response to markdown
5. Generate JaamSim config (if complex)
6. Save to Odoo BCM Scenario Hub
7. Return scenario_id
```

### Exercise Learning Flow
```
1. POST /learning/exercise-result
2. collect_exercise_result()
3. Update scenario_learning_db
4. Extract patterns from feedback
5. If enough data: _generate_scenario_improvements()
6. _notify_ai_orchestrator_learning()
7. Update dashboard metrics
```

---

## 🚨 CRITICAL DEPENDENCIES

### Startup Order (from source #1):
```
Level 1: foundation (postgres, redis, rabbitmq)
Level 2: infrastructure (eventbus, gateways)
Level 3: business + intelligence (parallel)
Level 4: applications
```

### Service Dependencies:
- **All services** depend on EventBus
- **AI features** depend on Redis + Supabase (optional)
- **Platform orchestrator** depends on Docker socket
- **Scenario orchestrator** depends on AI orchestrator

---

## 📝 ENDPOINTS SUMMARY

### Platform Orchestration (20+ endpoints)
```
GET  /health
GET  /
POST /deploy
GET  /status
POST /restart/{service}
POST /monitoring/start
POST /monitoring/stop
GET  /services
GET  /services/{name}/health
GET  /services/{name}/logs
```

### AI Orchestration (30+ endpoints)
```
POST /analyze/process-risk
POST /analyze/incident
POST /nlp/query
POST /deployment/orchestrate
GET  /deployment/history
POST /deployment/learn
POST /claude/analyze-changes
POST /claude/generate-config
POST /claude/analyze-deployment
POST /claude/create-pr
POST /claude/learn-from-workflow
POST /auth/token-exchange
POST /auth/refresh-token
POST /ai/process
GET  /ai/agents/health
GET  /ai/agents/analytics
```

### Scenario Orchestration (10+ endpoints)
```
POST /scenarios/generate
GET  /scenarios/available
POST /learning/exercise-result
GET  /learning/scenario/{id}/insights
GET  /learning/dashboard
GET  /api/v1/scenarios/status
```

**Total:** ~60 endpoints to consolidate!

---

## 💡 KEY DECISIONS

### 1. Architecture Pattern
**Choice:** Layered + Modular
- Core layer - shared logic
- Specialized orchestrators - domain logic
- Control center - coordination
- Integration layer - external services

### 2. Base Class Strategy
**Choice:** Single `BaseOrchestrator` class
```python
class BaseOrchestrator:
    registry: ServiceRegistry
    eventbus: EventBusClient
    health_monitor: HealthMonitor

    async def start()
    async def stop()
    async def get_status()
```

### 3. AI Integration
**Choice:** Keep ALL AI features from source #2
- Intelligence engine (risk, incident analysis)
- DevOps automation
- Claude integration
- Agent routing
- Learning system

### 4. Deployment Strategy
**Choice:** Merge deployer (#4) into platform orchestrator
- Keep simple deployment logic
- Add AI deployment as separate mode
- Unified monitoring

### 5. Learning System
**Choice:** Centralize in scenario orchestrator
- Exercise results
- Pattern extraction
- Improvement recommendations
- Cross-service learning notifications

---

## ✅ SUCCESS CRITERIA

- [ ] All 60 endpoints functional
- [ ] Docker management working
- [ ] EventBus integration active
- [ ] Health monitoring running
- [ ] AI features preserved
- [ ] Scenario generation working
- [ ] Learning system active
- [ ] Dashboard accessible
- [ ] No service duplicates
- [ ] Clean separation of concerns

---

**Ready for CODE_INVENTORY.md creation!** 🚀