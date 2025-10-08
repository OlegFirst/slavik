# Intelligent Core - Complete Layer Documentation

## Обзор слоя

**Intelligent Core** - это интеллектуальный слой AI-Platform-ISO, предоставляющий AI/ML функциональность для всей платформы.

### Ключевые характеристики
- **583 Python файлов** (исключая venv и архивы)
- **9 активных модулей**
- **Архитектура**: Модульная, plugin-based, event-driven
- **AI Stack**: RAG + LLM + ML + Self-Learning
- **Статус**: Production-ready с TODO списками

## Все модули intelligent-core

```
intelligent-core/
├── ai-foundation/                ⭐ Core AI Infrastructure
├── workflow_intelligence/        ⭐ Self-Learning Workflow Engine
├── expertise-center/             ⭐ Domain AI Experts (Plugin Architecture)
├── orchestration/
│   ├── ai-orchestration/         ⭐ Autonomous Decision-Making Brain
│   ├── coordination-center/      📋 Command Interpreter & Execution
│   └── bcm-services-orchestrator/ 📋 BCM Services Coordinator
├── collective/                   🤝 Collective Agent Networks
├── community_intelligence/       👥 Community Contributions & Reputation
├── predictive/                   🔮 Journey Prediction & Forecasting
├── workflow-engine/              🔄 BPMN Workflow Engine
└── ai_workflow_optimizer/        ⚡ Workflow Optimization Service
```

**Легенда:**
- ⭐ = Ключевой модуль (critical path)
- 🤝 = Коллективный интеллект
- 👥 = Сообщество
- 🔮 = Предиктивная аналитика
- 🔄 = Workflow execution
- ⚡ = Оптимизация
- 📋 = Оркестрация

## Архитектура слоя

### Высокоуровневая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                     INTELLIGENT CORE                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              AI FOUNDATION (Base Layer)                    │ │
│  │  ┌─────────┐ ┌────────┐ ┌──────┐ ┌─────────┐ ┌─────────┐ │ │
│  │  │   RAG   │ │  LLM   │ │  ML  │ │Learning │ │ Context │ │ │
│  │  │Pipeline │ │ Router │ │Models│ │ Engine  │ │ Builder │ │ │
│  │  └─────────┘ └────────┘ └──────┘ └─────────┘ └─────────┘ │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │ (Used by all modules)                │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │         INTELLIGENT MODULES LAYER                    │      │
│  │                                                       │      │
│  │  ┌─────────────────┐  ┌──────────────────────────┐  │      │
│  │  │   Workflow      │  │   Expertise Center       │  │      │
│  │  │ Intelligence    │  │  (Domain AI Experts)     │  │      │
│  │  │                 │  │                          │  │      │
│  │  │ • State Machine │  │ • Specialists (3)        │  │      │
│  │  │ • Case Library  │  │ • Tactical Assist. (12)  │  │      │
│  │  │ • AI Advisor    │  │ • Analyzers (10)         │  │      │
│  │  │ • Governance    │  │ • Plugin Architecture    │  │      │
│  │  └─────────────────┘  └──────────────────────────┘  │      │
│  │                                                       │      │
│  │  ┌─────────────────┐  ┌──────────────────────────┐  │      │
│  │  │   Community     │  │   Collective             │  │      │
│  │  │ Intelligence    │  │   (Agent Networks)       │  │      │
│  │  │                 │  │                          │  │      │
│  │  │ • Contributions │  │ • Anonymous Wisdom       │  │      │
│  │  │ • Peer Review   │  │ • K-Anonymity            │  │      │
│  │  │ • Reputation    │  │ • Stuck Detection        │  │      │
│  │  │ • Living Docs   │  │ • MCP/Partisia           │  │      │
│  │  └─────────────────┘  └──────────────────────────┘  │      │
│  │                                                       │      │
│  │  ┌─────────────────┐  ┌──────────────────────────┐  │      │
│  │  │   Predictive    │  │   Workflow Engine        │  │      │
│  │  │   (Journey)     │  │   (BPMN)                 │  │      │
│  │  └─────────────────┘  └──────────────────────────┘  │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         ORCHESTRATION LAYER (Top Level)                  │  │
│  │                                                           │  │
│  │  ┌──────────────────┐  ┌─────────────────────────┐      │  │
│  │  │  AI Orchestrator │  │  Coordination Center    │      │  │
│  │  │  (The Brain)     │  │  (Command Execution)    │      │  │
│  │  │                  │  │                         │      │  │
│  │  │ • Context Agg.   │  │ • Command Interpreter   │      │  │
│  │  │ • Priority       │  │ • Security Layer        │      │  │
│  │  │ • Safety         │  │ • Execution Tracker     │      │  │
│  │  │ • Evolution      │  │                         │      │  │
│  │  │ • 4-Layer Memory │  │                         │      │  │
│  │  └──────────────────┘  └─────────────────────────┘      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          ▲
                          │
                Uses by platform-services
```

## Граф зависимостей модулей

### Базовый слой
```
ai-foundation
    └── (no dependencies within intelligent-core)
        └── External: anthropic, openai, qdrant, scikit-learn
```

### Зависимости между модулями

```
workflow_intelligence
    └── uses: ai-foundation (RAG, LLM)

expertise-center
    └── uses: ai-foundation (RAG, LLM, ML)
    └── uses: ai-foundation/learning-knowledge

orchestration/ai-orchestration
    └── uses: ai-foundation (LLM Router)
    └── integrates: workflow_intelligence, expertise-center

community_intelligence
    └── uses: ai-foundation (RAG for semantic search)
    └── listens: workflow_intelligence events

collective
    └── uses: community_intelligence (case library)
    └── uses: ai-foundation (LLM for agents)

predictive
    └── uses: workflow_intelligence (case library)
    └── uses: ai-foundation (ML models)

orchestration/coordination-center
    └── integrates: all modules (command execution)

workflow-engine
    └── independent (BPMN execution)
```

### Dependency Graph (Text)

```
                    ai-foundation (BASE)
                          │
        ┌─────────────────┼─────────────────┬──────────────┐
        ▼                 ▼                 ▼              ▼
  workflow_intl    expertise-center   orchestration   community_intl
        │                 │                 │              │
        │                 │                 ▼              ▼
        │                 │         ai-orchestration   collective
        │                 │                 │
        └─────────┬───────┴─────────────────┤
                  ▼                         │
              predictive                    │
                                            ▼
                                  coordination-center
                                      (TOP LEVEL)
```

## Все модули - Краткое описание

### 1. ai-foundation ⭐
**Назначение**: Core AI Infrastructure
**Компоненты**:
- RAG Pipeline (RAGPipeline, KnowledgeSourceManager)
- LLM Router (Anthropic, OpenAI, Ollama)
- ML Models (Predictive, Anomaly Detection)
- Learning Engine (Self-learning, Pattern extraction)
- Context Builder

**API**: `RAGPipeline`, `LLMRouter`, `PredictiveModel`
**Status**: ✅ Production-ready
**Детали**: См. `ai-foundation/MODULE_ANALYSIS.md`

### 2. workflow_intelligence ⭐
**Назначение**: Self-Learning Workflow Engine
**Компоненты**:
- WorkflowEngine (universal state machine wrapper)
- Case Library (learning from success)
- ContextAdvisor (AI-powered advice)
- Governance (YAML workflows, rules, checkpoints)
- Event Bus (workflow events)

**API**: `initialize()`, `WorkflowEngine`, `ContextAdvisor`
**Status**: ⚠️ Development (storage needs reimplementation)
**Детали**: См. `workflow_intelligence/MODULE_ANALYSIS.md`

### 3. expertise-center ⭐
**Назначение**: Domain AI Experts (Plugin Architecture)
**Компоненты**:
- ChiefExecutive (orchestrator)
- ExpertRegistry (plugin registry)
- DomainLoader (dynamic loading)
- BCM Domain:
  - Specialists (3): BCMAdvisor, ComplianceAuditor, StrategicPlanner
  - Tactical Assistants (12): BIA, Risk, Compliance, etc.
  - Analyzers (10): Heavy AI analysis

**API**: `ChiefExecutive`, `query_specialist()`, `ask_colleague()`
**Status**: ✅ Production-ready (base), individual experts need completion
**Детали**: См. `expertise-center/MODULE_ANALYSIS.md`

### 4. orchestration/ai-orchestration ⭐
**Назначение**: Autonomous Decision-Making Brain
**Компоненты**:
- AIOrchestrator (main brain)
- DecisionCenter (context, priority, strategy)
- DistributedMemory (4-layer: working, short, long, procedural)
- SafetyMonitor (constitution, loops, hallucinations)
- EvolutionEngine (self-improvement)

**API**: `AIOrchestrator`, `decide()`, `execute()`
**Status**: ✅ Production-ready
**Детали**: См. `orchestration/ai-orchestration/` docs

### 5. community_intelligence 👥
**Назначение**: Community Contributions & Reputation
**Компоненты**:
- ContributionService (case contributions)
- PeerReviewService (review system)
- ReputationEngine (multi-dimensional reputation)
- LivingDocumentationService (AI + community synthesis)
- PredictiveTimelineService

**API**: `ContributionService`, `ReputationEngine`
**Status**: ✅ Production-ready
**Port**: 8031

### 6. collective 🤝
**Назначение**: Collective Agent Networks (Anonymous Wisdom)
**Компоненты**:
- CollectiveAgentService (agent creation)
- StuckDetectorService (stuck workflow detection)
- AnonymizerService (k-anonymity)
- MCP/Partisia Integration (blockchain privacy)

**API**: `/collective-agents/create`, `/stuck-detection/analyze`
**Status**: ✅ Production-ready
**Port**: 8032
**Privacy**: K-anonymity (min 5 orgs), multi-layer anonymization

### 7. predictive 🔮
**Назначение**: Journey Prediction & Forecasting
**Компоненты**:
- JourneyPredictor (90-day journey prediction)
- DemandForecaster (expert demand forecasting)
- ProactiveRecommendations

**API**: `/predictions/journey`, `/predictions/certification-timeline`
**Status**: ⚠️ Has critical bugs (see ANALYSIS_AND_IMPROVEMENTS.md)
**Port**: 8033

### 8. workflow-engine 🔄
**Назначение**: BPMN Workflow Engine
**Компоненты**:
- BPMN parser and executor
- Gateway support (exclusive, parallel, inclusive)
- REST API integration

**API**: REST API for workflow execution
**Status**: ✅ Complete

### 9. orchestration/coordination-center 📋
**Назначение**: Command Interpreter & Execution
**Компоненты**:
- CommandInterpreter
- ExecutionTracker
- SecurityLayer

**API**: `/execute`, `/status`
**Status**: ✅ Production-ready
**Port**: 8050

## Внешние зависимости (pip)

### AI/ML Stack
```
# LLM Providers
anthropic>=0.25.0
openai>=1.30.0

# Vector DB
qdrant-client>=1.8.0

# Embeddings
sentence-transformers>=2.5.0
voyageai>=0.2.0

# ML
scikit-learn>=1.4.0
numpy>=1.26.0
pandas>=2.2.0
```

### Web Framework
```
fastapi>=0.104.0
pydantic>=2.0.0
uvicorn>=0.24.0
```

### Database
```
sqlalchemy>=2.0.0
asyncpg>=0.28.0
alembic>=1.12.0
```

### Infrastructure
```
redis>=5.0.0
celery>=5.3.0
```

## API карта (Все публичные API)

### AI Foundation
```python
from ai_foundation import RAGPipeline, LLMRouter

# RAG
pipeline = RAGPipeline()
results = await pipeline.retrieve(query="...")
context = await pipeline.build_context(query="...")

# LLM
llm = LLMRouter()
response = await llm.query(
    system_prompt="...",
    user_prompt="...",
    task_type="strategic_analysis"
)
```

### Workflow Intelligence
```python
from workflow_intelligence import initialize

workflow, advisor = await initialize(
    module="bia",
    existing_state_machine=BIAWorkflowEngine,
    db_manager=db_manager
)

# Start workflow
context = await workflow.start(workflow_id="bia_001")

# Execute action
context = await workflow.execute_action(
    workflow_id="bia_001",
    action="identify_process"
)

# Get AI advice
hint = await advisor.get_contextual_hint(context)
```

### Expertise Center
```python
from expertise_center import ChiefExecutive

chief = ChiefExecutive()
await chief.initialize(domains=['bcm'])

# Strategic specialist
result = await chief.query_specialist(
    specialist_id="bcm_advisor",
    context={...},
    query="Strategic question"
)

# Tactical assistant
result = await chief.ask_colleague(
    colleague_id="bia_specialist",
    task="Help me identify critical processes"
)
```

### AI Orchestrator
```python
from intelligent_core.ai_orchestration import AIOrchestrator

orchestrator = AIOrchestrator()
await orchestrator.initialize()

# Make autonomous decision
decision = await orchestrator.decide(situation)
result = await orchestrator.execute(decision)
```

### Community Intelligence (REST)
```
POST /contributions/submit
POST /reviews/submit
GET  /reputation/{user_id}
GET  /cases/search
```

### Collective (REST)
```
POST /collective-agents/create
GET  /collective-agents/{agent_id}
POST /stuck-detection/analyze
```

### Predictive (REST)
```
GET  /predictions/journey/{user_id}
GET  /predictions/certification-timeline/{user_id}
POST /predictions/proactive-recommendations/{user_id}
```

## Как запустить

### Prerequisites
```bash
# Python 3.11+
python --version

# PostgreSQL 14+
psql --version

# Redis 7+
redis-server --version

# Qdrant (vector DB)
docker run -p 6333:6333 qdrant/qdrant
```

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/bcm_platform

# Redis
REDIS_URL=redis://localhost:6379

# Vector DB
QDRANT_URL=http://localhost:6333

# Services
COMMUNITY_INTELLIGENCE_URL=http://localhost:8031
COLLECTIVE_URL=http://localhost:8032
PREDICTIVE_URL=http://localhost:8033
COORDINATION_CENTER_URL=http://localhost:8050
EOF
```

### Installation (Development)
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core

# Install ai-foundation first (base dependency)
cd ai-foundation
pip install -r requirements.txt

# Install workflow_intelligence
cd ../workflow_intelligence
pip install -r requirements.txt

# Install expertise-center
cd ../expertise-center
# Uses ai-foundation (already installed)

# Install services
cd ../community_intelligence
pip install -r requirements.txt

cd ../collective
pip install -r requirements.txt

cd ../predictive
pip install -r requirements.txt
```

### Run Services

**Community Intelligence:**
```bash
cd community_intelligence
uvicorn main:app --host 0.0.0.0 --port 8031
```

**Collective:**
```bash
cd collective
uvicorn main:app --host 0.0.0.0 --port 8032
```

**Predictive:**
```bash
cd predictive
uvicorn main:app --host 0.0.0.0 --port 8033
```

**Coordination Center:**
```bash
cd orchestration/coordination-center
uvicorn main:app --host 0.0.0.0 --port 8050
```

### Python Library Usage

```python
# In platform-services or other modules
from ai_foundation import RAGPipeline, LLMRouter
from workflow_intelligence import initialize
from expertise_center import ChiefExecutive

# Initialize
rag = RAGPipeline()
llm = LLMRouter()
chief = ChiefExecutive()

# Use AI capabilities
results = await rag.retrieve(query="...")
response = await llm.query(system_prompt="...", user_prompt="...")
advice = await chief.ask_colleague("bia_specialist", "task")
```

## Интеграции с другими слоями

### Platform Services Integration

```python
# In platform-services/bia/
from workflow_intelligence import initialize
from expertise_center import ChiefExecutive

# Initialize workflow intelligence
workflow, advisor = await initialize("bia", BIAWorkflowEngine, db_manager)

# Get AI assistance
chief = ChiefExecutive()
hint = await chief.ask_colleague("bia_specialist", "Suggest RTO")
```

### Infrastructure Integration

```python
# Event Bus integration
from shared.eventbus import EventBusClient

event_bus = EventBusClient(backend='redis')
await event_bus.publish(Event(
    event_type="workflow.completed",
    data={...}
))
```

### External Services

- **Monitoring**: Prometheus metrics exposed by all services
- **Logging**: Centralized logging to infrastructure/monitoring
- **Secrets**: Vault integration for API keys

## Критичные проблемы (по модулям)

### ai-foundation (P0)
- [ ] Vector DB Connection Management - connection pool
- [ ] Error Handling - retry logic for LLM calls
- [ ] Rate Limiting - API call rate limiting

### workflow_intelligence (P0)
- [ ] **Reimplement PostgreSQL Storage** - был удален из-за SQLAlchemy issues
- [ ] Production Database Schema - Alembic migrations
- [ ] Event Bus → Redis - заменить in-memory

### predictive (P0)
- [ ] **Database session management** - критичный баг
- [ ] **Seed data generator** - нет тестовых данных
- [ ] Error handling - нет retry logic

### collective (P1)
- [ ] Agent expiration job - автоматическая очистка
- [ ] MCP/Partisia full integration

### community_intelligence (P1)
- [ ] Living Docs AI synthesis - не полностью реализовано

## Метрики и Мониторинг

### Текущее состояние
- Базовые health endpoints есть у всех сервисов
- Prometheus metrics частично реализованы
- Distributed tracing не реализовано

### Рекомендуемые метрики

**AI Foundation:**
- RAG retrieval latency
- LLM token usage
- Cache hit rate
- Error rates по провайдерам

**Workflow Intelligence:**
- Workflow duration
- Action execution time
- AI advice acceptance rate
- Case library growth

**Expertise Center:**
- Expert query latency
- Expert utilization
- Token usage per expert
- User satisfaction

**Services:**
- Request latency (p50, p95, p99)
- Error rates
- Active connections
- Queue depths

## Production Deployment Notes

### Resource Requirements

**Minimum:**
- 8GB RAM (для ML models + vector DB)
- 4 CPU cores
- 100GB SSD (для PostgreSQL + vector indices)

**Recommended:**
- 16GB RAM
- 8 CPU cores
- 200GB SSD

### Scaling Strategy

**Horizontal Scaling:**
- All services stateless (кроме databases)
- Load balancer перед сервисами
- Redis для shared state

**Vertical Scaling:**
- Vector DB (Qdrant) - нужен RAM для индексов
- ML inference - нужен CPU/GPU

### High Availability

**Database:**
- PostgreSQL master-replica
- Redis cluster
- Qdrant cluster (для production)

**Services:**
- Минимум 2 replicas каждого сервиса
- Health checks + auto-restart
- Circuit breakers

## Security

### Implemented
- ✅ RLS (Row Level Security) готов
- ✅ SQL Injection protection
- ✅ Input validation (Pydantic)
- ✅ K-anonymity в Collective

### TODO
- [ ] API authentication (JWT)
- [ ] Rate limiting
- [ ] Encryption at rest
- [ ] Audit logging
- [ ] GDPR compliance

## Тестирование

### Test Coverage
- **ai-foundation**: ~60% (unit tests)
- **workflow_intelligence**: ~70% (unit + security)
- **expertise-center**: ~30% (base classes only)
- **orchestration**: ~50% (core only)
- **services**: ~40% (basic tests)

### Missing Tests
- [ ] End-to-end integration tests
- [ ] Load/performance tests
- [ ] Chaos engineering tests
- [ ] AI quality tests

## Следующие шаги (Priority)

### Phase 1: Production Readiness (P0)
1. Fix workflow_intelligence storage (PostgreSQL)
2. Fix predictive session management
3. Add error handling + retry logic
4. Add API authentication

### Phase 2: Observability (P1)
1. Prometheus metrics для всех сервисов
2. Distributed tracing (Jaeger)
3. Centralized logging
4. Alerting rules

### Phase 3: Optimization (P2)
1. Caching strategy (Redis)
2. Query optimization
3. Cost optimization (LLM usage)
4. Performance tuning

### Phase 4: Features (P2)
1. New domains в expertise-center
2. Multi-expert coordination
3. Advanced analytics
4. Mobile API

## Документация по модулям

### Детальная документация
- **ai-foundation**: `ai-foundation/MODULE_ANALYSIS.md`
- **workflow_intelligence**: `workflow_intelligence/MODULE_ANALYSIS.md`
- **expertise-center**: `expertise-center/MODULE_ANALYSIS.md`
- **predictive**: `predictive/docs/ANALYSIS_AND_IMPROVEMENTS.md`
- **ai-orchestration**: `orchestration/ai-orchestration/README.md`
- **collective**: `collective/docs/`
- **community_intelligence**: `community_intelligence/docs/`

### Architecture Decisions
- Модульная архитектура для изоляции доменов
- Plugin architecture для expertise-center
- Event-driven для loose coupling
- ai-foundation как shared base layer
- YAML для governance (non-developers могут редактировать)

## Контакты и Support

**Основная документация**: `/doc-project/`
**Архитектура проекта**: `/doc-project/FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md`
**Knowledge System**: `/doc-project/KNOWLEDGE_SYSTEM_IMPLEMENTATION_COMPLETE.md`

---

**Версия**: 1.0.0
**Последнее обновление**: 2025-10-07
**Общий статус**: ⚠️ 70% Production-ready, 30% needs work
**Анализ выполнен**: Claude-Analyst-1

## Statistics

- **Total Python Files**: 583
- **Active Modules**: 9
- **REST Services**: 4 (ports 8031, 8032, 8033, 8050)
- **AI Experts**: 25 (3 specialists + 12 tactical + 10 analyzers)
- **Lines of Code**: ~50,000+ (estimated)
- **Test Coverage**: ~50% average
