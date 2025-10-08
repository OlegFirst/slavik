# Intelligent Core - Dependency Graph

## Граф зависимостей модулей

### Визуализация

```
                    ┌──────────────────┐
                    │  ai-foundation   │ ◄── BASE LAYER
                    │  (No internal    │
                    │   dependencies)  │
                    └────────┬─────────┘
                             │
                             │ (used by)
        ┌────────────────────┼────────────────────┬───────────────┐
        │                    │                    │               │
        ▼                    ▼                    ▼               ▼
┌───────────────┐   ┌─────────────────┐  ┌──────────────┐  ┌─────────────┐
│  workflow_    │   │   expertise-    │  │ orchestration│  │  community_ │
│ intelligence  │   │    center       │  │ ai-orch.     │  │intelligence │
└───────┬───────┘   └────────┬────────┘  └──────┬───────┘  └──────┬──────┘
        │                    │                   │                 │
        │                    │                   │                 ▼
        │                    │                   │          ┌─────────────┐
        │                    │                   │          │ collective  │
        │                    │                   │          └─────────────┘
        │                    │                   │
        └────────┬───────────┴───────────────────┤
                 ▼                               │
         ┌──────────────┐                        │
         │  predictive  │                        │
         └──────────────┘                        │
                                                 ▼
                                    ┌────────────────────────┐
                                    │  coordination-center   │ ◄── TOP LEVEL
                                    │  (Integrates all)      │
                                    └────────────────────────┘
```

## Детальный граф с весами зависимостей

### Legend
- **Strong dependency** (⚡⚡⚡): критическая зависимость, без которой модуль не работает
- **Medium dependency** (⚡⚡): важная зависимость, функционал частично работает
- **Weak dependency** (⚡): опциональная зависимость, улучшение функционала

### Dependency Matrix

```
FROM ↓ / TO →        ai-fnd  wf-int  exp-ctr  ai-orch  comm-int  collective  predictive
──────────────────────────────────────────────────────────────────────────────────────────
ai-foundation         -        -        -        -        -          -           -
workflow_intl        ⚡⚡⚡      -        -        -        -          -           -
expertise-center     ⚡⚡⚡      -        -        -        -          -           -
ai-orchestration     ⚡⚡      ⚡       ⚡        -        -          -           -
community_intl       ⚡⚡      ⚡        -        -        -          -           -
collective           ⚡⚡       -        -        -       ⚡⚡         -           -
predictive           ⚡       ⚡⚡       -        -        -          -           -
coord-center         ⚡        ⚡       ⚡       ⚡⚡       ⚡          ⚡           ⚡
```

## Dependency Details

### ai-foundation (Level 0 - BASE)
```yaml
Internal Dependencies: None
External Dependencies:
  - anthropic: ⚡⚡⚡ (LLM provider)
  - openai: ⚡⚡⚡ (LLM provider)
  - qdrant-client: ⚡⚡⚡ (Vector DB)
  - scikit-learn: ⚡⚡ (ML models)
  - sentence-transformers: ⚡⚡ (Embeddings)

Used By:
  - workflow_intelligence: ⚡⚡⚡
  - expertise-center: ⚡⚡⚡
  - ai-orchestration: ⚡⚡
  - community_intelligence: ⚡⚡
  - collective: ⚡⚡
  - predictive: ⚡

Purpose: Core AI infrastructure for entire platform
```

### workflow_intelligence (Level 1)
```yaml
Internal Dependencies:
  - ai-foundation: ⚡⚡⚡ (RAG, LLM for ContextAdvisor)

External Dependencies:
  - sqlalchemy: ⚡⚡⚡ (Database)
  - fastapi: ⚡⚡ (Optional API)
  - redis: ⚡⚡ (Event bus - planned)

Used By:
  - platform-services/bia: ⚡⚡⚡
  - platform-services/risk: ⚡⚡⚡
  - ai-orchestration: ⚡ (monitoring)
  - community_intelligence: ⚡ (workflow events)
  - predictive: ⚡⚡ (case library)

Purpose: Make workflows intelligent with AI
```

### expertise-center (Level 1)
```yaml
Internal Dependencies:
  - ai-foundation: ⚡⚡⚡ (RAG, LLM, ML for all experts)
  - ai-foundation/learning-knowledge: ⚡⚡ (Domain knowledge)

External Dependencies:
  - None (inherits from ai-foundation)

Used By:
  - platform-services/*: ⚡⚡ (AI expert assistance)
  - workflow_intelligence: ⚡ (optional expert advice)
  - ai-orchestration: ⚡ (delegation to experts)

Purpose: Domain-specific AI experts (BCM, ISMS, etc)
```

### ai-orchestration (Level 2)
```yaml
Internal Dependencies:
  - ai-foundation: ⚡⚡ (LLM Router for decisions)
  - workflow_intelligence: ⚡ (workflow monitoring)
  - expertise-center: ⚡ (delegation to experts)

External Dependencies:
  - redis: ⚡⚡⚡ (Memory storage)
  - sqlalchemy: ⚡⚡ (Decision storage)

Used By:
  - coordination-center: ⚡⚡⚡ (command execution)
  - platform-services: ⚡ (autonomous operations)

Purpose: Autonomous decision-making brain
```

### community_intelligence (Level 1)
```yaml
Internal Dependencies:
  - ai-foundation: ⚡⚡ (RAG for semantic search)
  - workflow_intelligence: ⚡ (listens to workflow.completed events)

External Dependencies:
  - sqlalchemy: ⚡⚡⚡ (Database)
  - fastapi: ⚡⚡⚡ (REST API)

Used By:
  - collective: ⚡⚡ (case library for agents)
  - platform-services: ⚡⚡ (contributions, reputation)

Purpose: Community contributions, peer review, reputation
```

### collective (Level 2)
```yaml
Internal Dependencies:
  - ai-foundation: ⚡⚡ (LLM for agent responses)
  - community_intelligence: ⚡⚡ (case library access)

External Dependencies:
  - sqlalchemy: ⚡⚡⚡ (Database)
  - fastapi: ⚡⚡⚡ (REST API)

Used By:
  - platform-services: ⚡⚡ (collective wisdom)

Purpose: Anonymous collective agent networks
```

### predictive (Level 2)
```yaml
Internal Dependencies:
  - workflow_intelligence: ⚡⚡ (case library for predictions)
  - ai-foundation: ⚡ (ML models)

External Dependencies:
  - sqlalchemy: ⚡⚡⚡ (Database)
  - fastapi: ⚡⚡⚡ (REST API)

Used By:
  - platform-services: ⚡⚡ (journey predictions)

Purpose: Predictive analytics, journey forecasting
```

### coordination-center (Level 3 - TOP)
```yaml
Internal Dependencies:
  - ALL modules: ⚡ to ⚡⚡ (integrates entire platform)
  - ai-orchestration: ⚡⚡⚡ (command execution)

External Dependencies:
  - fastapi: ⚡⚡⚡ (REST API)

Used By:
  - External systems (command interface)

Purpose: Unified command & execution center
```

## Circular Dependencies

### Analysis: ✅ No circular dependencies detected

All dependencies are **unidirectional** (top-down):
- Level 0 (ai-foundation) has no dependencies
- Level 1 modules depend only on Level 0
- Level 2 modules depend on Level 0 and Level 1
- Level 3 (coordination-center) depends on all

## Shared Dependencies (External)

### Critical (all modules)
```
PostgreSQL: ⚡⚡⚡
Redis: ⚡⚡⚡
FastAPI: ⚡⚡⚡
Pydantic: ⚡⚡⚡
SQLAlchemy: ⚡⚡⚡
```

### AI Stack (via ai-foundation)
```
Anthropic: ⚡⚡⚡
OpenAI: ⚡⚡⚡
Qdrant: ⚡⚡⚡
scikit-learn: ⚡⚡
```

## Import Paths

### From platform-services
```python
# Base AI
from ai_foundation import RAGPipeline, LLMRouter

# Workflows
from workflow_intelligence import initialize
workflow, advisor = await initialize("bia", StateMachine, db)

# Experts
from expertise_center import ChiefExecutive
chief = ChiefExecutive()
result = await chief.ask_colleague("bia_specialist", "task")

# Orchestration
from intelligent_core.ai_orchestration import AIOrchestrator
orchestrator = AIOrchestrator()
```

### Within intelligent-core
```python
# ai-foundation imports nothing from intelligent-core

# workflow_intelligence
from ai_foundation import RAGPipeline, LLMRouter

# expertise-center
from ai_foundation import RAGPipeline, LLMRouter, ContextBuilder

# ai-orchestration
from ai_foundation import LLMRouter
from intelligent_core.workflow_intelligence import WorkflowEngine  # optional
from intelligent_core.expertise_center import ChiefExecutive  # optional

# community_intelligence
from ai_foundation import RAGPipeline
from workflow_intelligence import event_bus

# collective
from ai_foundation import LLMRouter
from community_intelligence import CaseLibraryBridge

# predictive
from ai_foundation import PredictiveModel
from workflow_intelligence.case_library import CaseRepository
```

## Dependency Installation Order

### Development
```bash
# 1. Base layer (no dependencies)
cd ai-foundation && pip install -r requirements.txt

# 2. Level 1 (depend on ai-foundation only)
cd workflow_intelligence && pip install -r requirements.txt
cd expertise-center  # (uses ai-foundation requirements)
cd community_intelligence && pip install -r requirements.txt

# 3. Level 2 (depend on Level 0 + Level 1)
cd orchestration/ai-orchestration && pip install -r requirements.txt
cd collective && pip install -r requirements.txt
cd predictive && pip install -r requirements.txt

# 4. Level 3 (integrates all)
cd orchestration/coordination-center && pip install -r requirements.txt
```

### Production (Docker)
```dockerfile
# Stage 1: ai-foundation
FROM python:3.11-slim AS ai-foundation
COPY ai-foundation/requirements.txt .
RUN pip install -r requirements.txt

# Stage 2: other modules
FROM ai-foundation AS intelligent-core
COPY . .
RUN pip install -r workflow_intelligence/requirements.txt
RUN pip install -r expertise-center/requirements.txt
# ... etc
```

## Breaking Changes Impact

### If ai-foundation changes:
```
Impact: ⚡⚡⚡ CRITICAL
Affected modules:
  - workflow_intelligence (breaks ContextAdvisor)
  - expertise-center (breaks all experts)
  - ai-orchestration (breaks LLM decisions)
  - community_intelligence (breaks semantic search)
  - collective (breaks agent responses)
  - predictive (breaks ML predictions)

Mitigation:
  - Semantic versioning
  - Deprecation warnings
  - Compatibility layer
```

### If workflow_intelligence changes:
```
Impact: ⚡⚡ HIGH
Affected modules:
  - platform-services/bia, risk, etc (breaks workflows)
  - community_intelligence (breaks event listening)
  - predictive (breaks case library access)

Mitigation:
  - Stable API contract
  - Event schema versioning
```

### If expertise-center changes:
```
Impact: ⚡ MEDIUM
Affected modules:
  - platform-services (breaks AI assistance)

Mitigation:
  - Plugin versioning
  - Backward compatible base classes
```

## Dependency Health

### ai-foundation dependencies
```
✅ anthropic: actively maintained
✅ openai: actively maintained
✅ qdrant-client: actively maintained
✅ scikit-learn: stable, mature
⚠️ voyageai: newer, less proven
```

### Shared infrastructure
```
✅ PostgreSQL: mature, stable
✅ Redis: mature, stable
✅ FastAPI: actively maintained
✅ SQLAlchemy 2.0: just migrated, stable
```

## Recommendations

### For New Modules
1. **Always** import from ai-foundation for AI capabilities
2. **Never** create circular dependencies
3. **Use** event bus for loose coupling
4. **Follow** dependency levels (don't skip layers)

### For Refactoring
1. Keep ai-foundation stable (it's the foundation)
2. Version public APIs
3. Deprecate gracefully
4. Test dependency chains

### For Deployment
1. Deploy ai-foundation first
2. Then Level 1 modules
3. Then Level 2 modules
4. Finally coordination-center

---

**Generated**: 2025-10-07
**Analyzer**: Claude-Analyst-1
**Status**: ✅ Comprehensive
