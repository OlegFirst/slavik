# ФИНАЛЬНАЯ АРХИТЕКТУРА ПЛАТФОРМЫ - VARIANT 5

**Версия**: 5.0 Final
**Дата**: 2025-10-06
**Статус**: ✅ Ready for Implementation

---

## 🎯 EXECUTIVE SUMMARY

**Философия**: workflow_intelligence = "THE BRAIN" с унифицированными AI инструментами

**Ключевые решения:**
1. ✅ Variant 5 - sub-packages внутри workflow_intelligence
2. ✅ Унификация AI сервисов (RAG, ML, Learning)
3. ✅ Specialists + Analyzers (вместо organs) в BCM domain
4. ✅ platform-services остаются независимыми
5. ✅ Минимальные breaking changes (6 строк кода)

---

## 🏗️ АРХИТЕКТУРНЫЕ СЛОИ

```
┌─────────────────────────────────────────────────────────────┐
│                  WORKFLOW INTELLIGENCE                       │
│         🧠 THE BRAIN - Правила для всей платформы           │
│                                                              │
│  Core:          State Machine, Governance, Workflows        │
│  Services:      RAG, ML, Learning, Context, Case Library    │
│  Philosophy:    Managed Autonomy (Checkpoints + Creative)   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              EXPERTISE CENTER (AI Experts)                   │
│         🎓 Domain Plugins с AI специалистами                │
│                                                              │
│  Shared:        Base classes, Tools, LLM clients            │
│  Domains:       BCM, HR, Finance (swappable plugins)        │
│  Integration:   Specialists → Brain tools → Services        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 ORCHESTRATION LAYER                          │
│         🎯 AI Orchestration & Coordination                  │
│                                                              │
│  AI-Orchestration:    Decision engine, Memory, Safety       │
│  Coordination:        Intent parsing, API execution         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              PLATFORM SERVICES (Business Logic)              │
│         💼 Микросервисы с REST API                          │
│                                                              │
│  Services:      BIA, Risk, Planning, Compliance, etc.       │
│  Technology:    FastAPI, PostgreSQL, Docker                 │
│  Independence:  Отдельное развертывание                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE                             │
│         ⚙️ Database, Cache, EventBus, Auth                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 ПОЛНАЯ СТРУКТУРА ДИРЕКТОРИЙ

```
AI-Platform-ISO/
│
├─ intelligent-core/                           # ИНТЕЛЛЕКТУАЛЬНОЕ ЯДРО
│  │
│  ├─ workflow_intelligence/                   # 🧠 THE BRAIN
│  │  │
│  │  ├─ __init__.py                          # Main exports
│  │  ├─ README.md
│  │  │
│  │  ├─ core/                                # Brain Core (2,696 LOC)
│  │  │  ├─ __init__.py
│  │  │  ├─ engine.py                         # WorkflowEngine
│  │  │  ├─ state_machine.py                  # State Machine базовый
│  │  │  ├─ transitions.py                    # Управление переходами
│  │  │  ├─ validators.py                     # Валидация данных
│  │  │  ├─ context.py                        # Контекст для AI
│  │  │  ├─ events.py                         # Event publishing
│  │  │  │
│  │  │  └─ governance/                       # Managed Autonomy
│  │  │     ├─ __init__.py
│  │  │     ├─ rules_engine.py               # 13 правил безопасности
│  │  │     ├─ checkpoints.py                # 5 обязательных проверок
│  │  │     ├─ creative_zones.py             # 4 зоны свободы AI
│  │  │     └─ yaml_workflows.py             # YAML workflow loader
│  │  │
│  │  ├─ services/                            # AI Services (sub-packages)
│  │  │  │
│  │  │  ├─ rag/                             # RAG Service (1,368 LOC)
│  │  │  │  ├─ __init__.py                   # Export: RAGPipeline
│  │  │  │  ├─ pipeline.py                   # Main RAG pipeline
│  │  │  │  ├─ embeddings.py                 # Voyage/OpenAI embeddings
│  │  │  │  ├─ retrieval.py                  # Hybrid search (semantic + keyword)
│  │  │  │  ├─ reranker.py                   # Cohere reranker
│  │  │  │  └─ config.py                     # RAG configuration
│  │  │  │
│  │  │  ├─ ml/                              # ML Service (1,127 LOC)
│  │  │  │  ├─ __init__.py                   # Export: WorkflowPredictor, MLTrainer
│  │  │  │  ├─ predictive_models.py          # Random Forest + Gradient Boosting
│  │  │  │  ├─ training_pipeline.py          # ML training pipeline
│  │  │  │  ├─ anomaly_detector.py           # Statistical anomaly detection
│  │  │  │  └─ community_predictor.py        # ML from community cases
│  │  │  │
│  │  │  ├─ learning/                        # Self-Learning Service (619 LOC)
│  │  │  │  ├─ __init__.py                   # Export: SelfLearningEngine
│  │  │  │  ├─ self_learning_engine.py       # Main learning engine
│  │  │  │  ├─ pattern_extractor.py          # Extract patterns from cases
│  │  │  │  ├─ rule_generator.py             # Generate new rules
│  │  │  │  └─ improvement_tracker.py        # Track improvements
│  │  │  │
│  │  │  ├─ context/                         # Context Service (522 LOC)
│  │  │  │  ├─ __init__.py                   # Export: AIContextBuilder
│  │  │  │  ├─ context_builder.py            # Build AI context
│  │  │  │  ├─ context_aggregator.py         # Aggregate from multiple sources
│  │  │  │  ├─ prompt_builder.py             # Dynamic prompt building
│  │  │  │  └─ enricher.py                   # Context enrichment
│  │  │  │
│  │  │  ├─ case_library/                    # Case Library Service (750 LOC)
│  │  │  │  ├─ __init__.py                   # Export: CaseRepository
│  │  │  │  ├─ collector.py                  # Auto-collect successful workflows
│  │  │  │  ├─ repository.py                 # Store and search cases
│  │  │  │  ├─ analyzer.py                   # AI pattern analysis
│  │  │  │  ├─ search.py                     # Semantic search
│  │  │  │  ├─ models.py                     # Database models
│  │  │  │  └─ bridge.py                     # Community sync
│  │  │  │
│  │  │  ├─ journey/                         # Journey Prediction (687 LOC)
│  │  │  │  ├─ __init__.py                   # Export: JourneyPredictor
│  │  │  │  ├─ journey_predictor.py          # 90-day prediction
│  │  │  │  ├─ timeline_engine.py            # Timeline generation
│  │  │  │  └─ milestone_tracker.py          # Milestone tracking
│  │  │  │
│  │  │  └─ anomaly/                         # Anomaly Detection (529 LOC)
│  │  │     ├─ __init__.py                   # Export: StuckDetector
│  │  │     ├─ stuck_detector.py             # Workflow stagnation detection
│  │  │     ├─ anomaly_detector.py           # Statistical anomaly detection
│  │  │     └─ alerts.py                     # Alert generation
│  │  │
│  │  ├─ workflows/                           # Workflow Implementations
│  │  │  ├─ __init__.py
│  │  │  ├─ definitions/                     # YAML definitions
│  │  │  │  ├─ bia_process.yaml
│  │  │  │  ├─ risk_assessment.yaml
│  │  │  │  └─ planning_process.yaml
│  │  │  │
│  │  │  └─ implementations/                 # Python implementations
│  │  │     ├─ bia_workflow.py
│  │  │     ├─ risk_workflow.py
│  │  │     └─ planning_workflow.py
│  │  │
│  │  ├─ integration/                         # Adapters для внешних сервисов
│  │  │  ├─ __init__.py
│  │  │  ├─ eventbus_publisher.py            # EventBus integration
│  │  │  ├─ bia_adapter.py                   # BIA service adapter
│  │  │  └─ service_adapters.py              # Other service adapters
│  │  │
│  │  ├─ monitoring/                          # Metrics & Observability
│  │  │  ├─ __init__.py
│  │  │  └─ metrics.py                       # Prometheus metrics
│  │  │
│  │  └─ tests/                              # Comprehensive tests
│  │     ├─ test_state_machine.py
│  │     ├─ test_governance.py
│  │     ├─ test_rag.py
│  │     ├─ test_ml.py
│  │     └─ test_workflows.py
│  │
│  ├─ expertise-center/                       # 🎓 AI EXPERTISE CENTER
│  │  │
│  │  ├─ __init__.py
│  │  ├─ README.md
│  │  │
│  │  ├─ core/                               # Orchestration Core
│  │  │  ├─ __init__.py
│  │  │  ├─ chief_executive.py              # Main AI orchestrator
│  │  │  ├─ domain_loader.py                # Plugin loader
│  │  │  ├─ expert_registry.py              # Expert registry
│  │  │  └─ coordinator.py                  # Request coordination
│  │  │
│  │  ├─ shared/                             # Shared AI Infrastructure
│  │  │  │
│  │  │  ├─ base/                            # Base Classes
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ base_specialist.py           # BaseSpecialist (легковесный AI)
│  │  │  │  ├─ base_analyzer.py             # BaseAnalyzer (тяжелый AI)
│  │  │  │  └─ base_tool.py                 # BaseTool
│  │  │  │
│  │  │  ├─ tools/                           # Shared Tools (2,747 LOC)
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ bia_tools.py                 # BIA calculations
│  │  │  │  ├─ compliance_tools.py          # Compliance checks
│  │  │  │  ├─ strategic_tools.py           # Strategic planning
│  │  │  │  ├─ case_library_tool.py         # Case library access
│  │  │  │  └─ base_tool.py                 # Tool base class
│  │  │  │
│  │  │  └─ llm/                             # LLM Clients
│  │  │     ├─ __init__.py
│  │  │     ├─ llm_client.py                # Unified LLM client
│  │  │     ├─ anthropic_adapter.py         # Claude adapter
│  │  │     ├─ openai_adapter.py            # GPT adapter
│  │  │     └─ llm_router.py                # Model routing
│  │  │
│  │  └─ domains/                            # 🔌 DOMAIN PLUGINS
│  │     │
│  │     └─ bcm/                             # BCM Domain Plugin
│  │        │
│  │        ├─ __init__.py                   # BCMDomain class
│  │        ├─ README.md
│  │        │
│  │        ├─ specialists/                  # Специалисты (легковесные AI)
│  │        │  │                             # 13 специалистов total
│  │        │  ├─ __init__.py
│  │        │  │
│  │        │  ├─ bia_specialist.py          # BIA анализ
│  │        │  ├─ risk_analyst.py            # Risk assessment
│  │        │  ├─ project_manager.py         # Project management
│  │        │  ├─ incident_advisor.py        # Incident response
│  │        │  ├─ plan_generator.py          # Plan generation
│  │        │  ├─ compliance_copilot.py      # Compliance guidance
│  │        │  ├─ exercise_designer.py       # Exercise planning
│  │        │  ├─ compliance_auditor.py      # Compliance auditing
│  │        │  ├─ bcm_advisor.py             # General BCM advice
│  │        │  └─ strategic_planner.py       # Strategic planning
│  │        │
│  │        ├─ analyzers/                    # Анализаторы (тяжелые AI)
│  │        │  │                             # 10 анализаторов total
│  │        │  ├─ __init__.py
│  │        │  │
│  │        │  ├─ governance_analyzer.py     # Глубокий анализ governance
│  │        │  ├─ impact_analyzer.py         # Глубокий BIA анализ
│  │        │  ├─ risk_analyzer.py           # Глубокий risk анализ
│  │        │  ├─ compliance_analyzer.py     # Глубокий compliance анализ
│  │        │  ├─ emergency_analyzer.py      # Emergency response анализ
│  │        │  ├─ scenario_analyzer.py       # Scenario generation
│  │        │  ├─ performance_analyzer.py    # Performance metrics анализ
│  │        │  ├─ learning_analyzer.py       # Learning effectiveness
│  │        │  ├─ plan_analyzer.py           # Plan quality анализ
│  │        │  └─ lifecycle_analyzer.py      # PDCA lifecycle анализ
│  │        │
│  │        ├─ knowledge/                    # BCM Knowledge Base
│  │        │  ├─ iso_22301/                # ISO 22301:2019
│  │        │  ├─ bci_guidelines/           # BCI Good Practice
│  │        │  ├─ best_practices/           # Industry best practices
│  │        │  └─ templates/                # BCM templates
│  │        │
│  │        └─ services_config.py            # Service metadata
│  │
│  ├─ orchestration/                         # 🎯 ORCHESTRATION
│  │  │
│  │  ├─ ai-orchestration/                  # AI Decision Engine
│  │  │  ├─ orchestrator.py
│  │  │  ├─ decision_center/
│  │  │  ├─ distributed_memory/
│  │  │  ├─ safety_monitor/
│  │  │  └─ evolution_engine/
│  │  │
│  │  └─ coordination-center/               # API Coordination
│  │     ├─ intent_parser.py
│  │     ├─ api_executor.py
│  │     ├─ security_layer.py
│  │     └─ rollback_manager.py
│  │
│  └─ [other intelligent modules...]
│
├─ platform-services/                        # 💼 BUSINESS SERVICES
│  │
│  ├─ bia-service/                          # BIA REST API
│  │  ├─ main.py
│  │  ├─ config.py
│  │  ├─ api/routes.py
│  │  ├─ models/
│  │  ├─ services/business_logic.py
│  │  ├─ repositories/
│  │  ├─ events/
│  │  ├─ integration/
│  │  │  └─ ai_integration.py              # Calls expertise-center
│  │  └─ tests/
│  │
│  ├─ risk-service/                         # Risk REST API
│  ├─ governance-service/                   # Governance REST API
│  ├─ planning_service/                     # Planning REST API
│  ├─ plans_service/                        # Plans REST API
│  ├─ response-service/                     # Response REST API
│  ├─ compliance-service/                   # Compliance REST API
│  ├─ documents-service/                    # Documents REST API
│  ├─ validation-service/                   # Validation REST API
│  └─ learning-service/                     # Learning REST API
│
├─ infrastructure/                           # ⚙️ INFRASTRUCTURE
│  ├─ database/                             # PostgreSQL + migrations
│  ├─ eventbus/                             # Event streaming (FastAPI)
│  ├─ auth/                                 # Authentication
│  ├─ monitoring/                           # Prometheus + Grafana
│  ├─ observability/                        # Logging + Tracing
│  └─ message-queue/                        # RabbitMQ/Redis
│
├─ shared/                                   # 📚 SHARED LIBRARIES
│  ├─ auth/                                 # JWT, permissions, RLS
│  ├─ database/                             # Connection management
│  ├─ cache/                                # Redis caching
│  ├─ eventbus/                             # EventBus client
│  ├─ audit/                                # Audit logging
│  ├─ monitoring/                           # Health checks, metrics
│  └─ middleware/                           # Error handling, logging
│
└─ _archive/                                # 📦 ARCHIVED CODE
   ├─ ai_experts/                           # ← Moved to workflow_intelligence + expertise-center
   └─ ai-office/                            # ← Moved to expertise-center
```

---

## 🎓 КЛЮЧЕВЫЕ КОНЦЕПЦИИ

### 1. Specialists vs Analyzers

**SPECIALISTS (Специалисты)** - Легковесные AI агенты
- **Назначение**: Быстрые ответы, конкретная экспертиза
- **Характеристики**:
  - 1-2 LLM calls обычно
  - Использует готовые инструменты (tools)
  - Быстрое время ответа (<5 секунд)
  - Стандартные промпты
- **Примеры**: BIA Specialist, Risk Analyst, Compliance Copilot
- **Когда использовать**: Рутинные задачи, стандартные вопросы, быстрые советы

**ANALYZERS (Анализаторы)** - Тяжелые AI системы
- **Назначение**: Глубокий анализ, комплексное мышление
- **Характеристики**:
  - 5-10+ LLM calls
  - Chain of thought reasoning
  - Долгое время ответа (30-60+ секунд)
  - Многоступенчатый анализ
- **Примеры**: Impact Analyzer, Risk Analyzer, Compliance Analyzer
- **Когда использовать**: Сложные решения, стратегический анализ, критические оценки

**Почему "Analyzers" вместо "Organs":**
- ✅ Понятнее на русском и английском
- ✅ Отражает назначение (глубокий анализ)
- ✅ Согласуется с Specialists
- ✅ Профессиональное название

---

## 🔄 REQUEST FLOW

### Пример: "Провести BIA анализ для процесса платежей"

```
1. USER REQUEST
   ↓
   POST /api/v1/bcm/bia/analyze
   {
     "process": "payment_processing",
     "use_ai": true,
     "deep_analysis": true
   }

2. API GATEWAY
   ↓
   Route to platform-services/bia-service (port 8011)

3. BIA SERVICE (platform-services/bia-service)
   ↓
   async def analyze_bia(request):
       # 1. Workflow Intelligence (проверка правил)
       workflow = await brain.get_workflow("bia")
       if not workflow.governance.is_allowed(request):
           raise PermissionError()

       # 2. Database операции
       bia = await db.create_bia(request.org_id)

       # 3. AI анализ (если запрошен)
       if request.use_ai:
           # Get specialist from expertise-center
           specialist = await get_specialist("bcm", "bia_specialist")
           ai_insights = await specialist.analyze(request.data)

           # Deep analysis (если запрошен)
           if request.deep_analysis:
               analyzer = await get_analyzer("bcm", "impact_analyzer")
               deep_insights = await analyzer.analyze(request.data)
               ai_insights.merge(deep_insights)

           bia.ai_insights = ai_insights

       # 4. Save & publish event
       await db.save(bia)
       await eventbus.publish("bia.completed", bia)

       return bia

4. EXPERTISE-CENTER (expertise-center/domains/bcm)
   ↓
   # BIA Specialist (quick analysis)
   class BIASpecialist(BaseSpecialist):
       async def analyze(self, data):
           # 1. Check workflow state
           workflow = await self.brain.get_workflow("bia")

           # 2. Use RAG (from brain)
           similar_cases = await self.brain.services.rag.search(
               query=f"BIA for {data['process']}",
               top_k=5
           )

           # 3. Use ML (from brain)
           criticality = await self.brain.services.ml.predict(
               model="criticality",
               data=data
           )

           # 4. Use Tools (from shared)
           bia_calc = await self.tools.bia_calculator.calculate(data)

           # 5. Generate advice (1 LLM call)
           advice = await self.llm.generate(
               prompt=self._build_prompt(data, similar_cases, criticality),
               model="claude-3-5-sonnet"
           )

           return {
               "criticality": criticality,
               "calculations": bia_calc,
               "similar_cases": similar_cases,
               "advice": advice
           }

5. IMPACT ANALYZER (deep analysis if requested)
   ↓
   class ImpactAnalyzer(BaseAnalyzer):
       async def analyze(self, data):
           # Multi-step deep analysis (5-10 LLM calls)

           # Step 1: Identify critical factors (LLM call 1)
           factors = await self.llm.chain_of_thought(
               "Identify all critical impact factors",
               data
           )

           # Step 2: Analyze each factor (LLM calls 2-6)
           analyses = []
           for factor in factors:
               analysis = await self.llm.deep_analyze(factor)
               analyses.append(analysis)

           # Step 3: Cross-impact analysis (LLM call 7)
           cross_impacts = await self.llm.analyze_interactions(analyses)

           # Step 4: Synthesize findings (LLM call 8)
           synthesis = await self.llm.synthesize(
               analyses + cross_impacts
           )

           # Step 5: Generate recommendations (LLM call 9)
           recommendations = await self.llm.recommend(synthesis)

           # Step 6: Confidence assessment (LLM call 10)
           confidence = await self.llm.assess_confidence(
               synthesis, recommendations
           )

           return {
               "factors": factors,
               "analyses": analyses,
               "cross_impacts": cross_impacts,
               "synthesis": synthesis,
               "recommendations": recommendations,
               "confidence": confidence,
               "reasoning_chain": self.get_reasoning_chain()
           }

6. WORKFLOW INTELLIGENCE (brain checks)
   ↓
   # Governance validation
   await workflow.governance.validate_checkpoint("analysis_complete")

   # Case Library (learning)
   await workflow.services.case_library.store_case({
       "workflow": "bia",
       "success": True,
       "data": bia,
       "ai_insights": ai_insights
   })

7. RESULT TO USER
   ↓
   {
     "success": true,
     "bia_id": "bia_123",
     "criticality": "high",
     "mtpd": "4 hours",
     "ai_insights": {
       "specialist_advice": {...},      # Quick analysis
       "deep_analysis": {...}            # Deep analysis (if requested)
     },
     "confidence": 0.92,
     "similar_cases": [...],
     "stored_in_case_library": true
   }
```

---

## 🎯 USAGE EXAMPLES

### Import Patterns

**Brain Core:**
```python
# Import workflow engine
from workflow_intelligence.core import WorkflowEngine, StateMachine
from workflow_intelligence.core.governance import Governance

# Create workflow
workflow = WorkflowEngine(workflow_id="bia_123", workflow_type="bia")
```

**Brain Services (AI Tools):**
```python
# Import specific services
from workflow_intelligence.services.rag import RAGPipeline
from workflow_intelligence.services.ml import WorkflowPredictor
from workflow_intelligence.services.learning import SelfLearningEngine
from workflow_intelligence.services.context import AIContextBuilder
from workflow_intelligence.services.case_library import CaseRepository

# Use RAG
rag = RAGPipeline()
results = await rag.search("BIA for payment processing", top_k=5)

# Use ML
predictor = WorkflowPredictor()
success_prob = await predictor.predict(workflow_data)

# Use Case Library
cases = CaseRepository()
similar = await cases.find_similar(query, org_context)
```

**Expertise Center (AI Experts):**
```python
# Import specialists
from expertise_center.domains.bcm.specialists import (
    BIASpecialist,
    RiskAnalyst,
    ComplianceCopilot
)

# Import analyzers
from expertise_center.domains.bcm.analyzers import (
    ImpactAnalyzer,
    RiskAnalyzer,
    ComplianceAnalyzer
)

# Use specialist (quick)
specialist = BIASpecialist()
quick_insights = await specialist.analyze(data)

# Use analyzer (deep)
analyzer = ImpactAnalyzer()
deep_insights = await analyzer.analyze(data)
```

**Flexibility:**
```python
# Option 1: Import only what you need
from workflow_intelligence.services.rag import RAGPipeline

# Option 2: Import brain core
from workflow_intelligence.core import WorkflowEngine

# Option 3: Import everything
from workflow_intelligence import *
```

---

## 📊 COMPONENT DISTRIBUTION

### workflow_intelligence/ (THE BRAIN)

**Что здесь:**
- ✅ Brain Core (engine, state machine, governance)
- ✅ AI Services (RAG, ML, Learning, Context, Case Library)
- ✅ Workflow Definitions (YAML + Python)
- ✅ Integration adapters

**Откуда взято:**
- `core/` - оригинальный код workflow_intelligence
- `services/rag/` - из ai_experts/rag + ai-office/core/rag (merge)
- `services/ml/` - из ai_experts/ml + community_intelligence/ml (merge)
- `services/learning/` - из ai_experts/learning + ai-office/core/learning (merge)
- `services/context/` - оригинальный ai_advisor (переименован)
- `services/case_library/` - оригинальный code (перемещен в services)
- `services/journey/` - из predictive/services/journey_predictor
- `services/anomaly/` - из collective/services/stuck_detector

**LOC**: ~7,500 (включая services)

---

### expertise-center/ (AI EXPERTISE)

**Что здесь:**
- ✅ Shared infrastructure (base classes, tools, LLM clients)
- ✅ Domain plugins (BCM, future: HR, Finance)
- ✅ Specialists (легковесные AI агенты)
- ✅ Analyzers (тяжелые AI анализаторы)

**Откуда взято:**
- `shared/base/` - из ai_experts/base + ai-office/base (merge)
- `shared/tools/` - из ai_experts/tools
- `shared/llm/` - из ai-office/llm
- `domains/bcm/specialists/` - из ai-office/ВСМ-colleagues + ai_experts/specialists (13 total)
- `domains/bcm/analyzers/` - из ai-office/organs (переименовано, 10 total)
- `domains/bcm/knowledge/` - из ai_experts/knowledge

**LOC**: ~15,000+

---

### platform-services/ (BUSINESS LOGIC)

**Что здесь:**
- ✅ FastAPI микросервисы
- ✅ Business logic
- ✅ Database операции
- ✅ REST API endpoints
- ✅ Event publishing/subscribing

**Откуда взято:**
- ✅ ОСТАЕТСЯ КАК ЕСТЬ! Не перемещается!

**LOC**: ~50,000+ (10 сервисов)

---

## 🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ

### workflow_intelligence/__init__.py

```python
"""
Workflow Intelligence - THE BRAIN

Main exports for easy access.
"""

# Core
from .core.engine import WorkflowEngine
from .core.state_machine import StateMachine
from .core.governance import Governance, RulesEngine

# Services (optional - can import directly from submodules)
from .services.rag import RAGPipeline
from .services.ml import WorkflowPredictor
from .services.learning import SelfLearningEngine
from .services.context import AIContextBuilder
from .services.case_library import CaseRepository

__all__ = [
    # Core
    'WorkflowEngine',
    'StateMachine',
    'Governance',
    'RulesEngine',

    # Services
    'RAGPipeline',
    'WorkflowPredictor',
    'SelfLearningEngine',
    'AIContextBuilder',
    'CaseRepository',
]

__version__ = '5.0.0'
```

### expertise_center/__init__.py

```python
"""
Expertise Center - AI Expertise Plugin System

Manages domain plugins with AI specialists and analyzers.
"""

from .core.chief_executive import ChiefExecutiveAI
from .core.domain_loader import DomainLoader
from .core.expert_registry import ExpertRegistry

# Shared
from .shared.base import BaseSpecialist, BaseAnalyzer, BaseTool
from .shared.llm import LLMClient

__all__ = [
    'ChiefExecutiveAI',
    'DomainLoader',
    'ExpertRegistry',
    'BaseSpecialist',
    'BaseAnalyzer',
    'BaseTool',
    'LLMClient',
]

__version__ = '5.0.0'
```

### expertise_center/domains/bcm/__init__.py

```python
"""
BCM Domain Plugin

Provides BCM specialists, analyzers, and knowledge.
"""

from expertise_center.shared.base import BaseDomain

class BCMDomain(BaseDomain):
    """BCM Domain Plugin"""

    name = "bcm"
    version = "1.0.0"
    description = "Business Continuity Management"

    def register(self, platform):
        """Platform injects shared services"""
        # Get brain services
        self.brain = platform.get_brain()
        self.rag = self.brain.services.rag
        self.ml = self.brain.services.ml
        self.learning = self.brain.services.learning

        # Get shared tools
        self.tools = platform.get_tools()
        self.llm = platform.get_llm()

    def get_specialists(self):
        """Return BCM specialists (легковесные AI)"""
        from .specialists import (
            BIASpecialist,
            RiskAnalyst,
            ProjectManager,
            IncidentAdvisor,
            PlanGenerator,
            ComplianceCopilot,
            ExerciseDesigner,
            ComplianceAuditor,
            BCMAdvisor,
            StrategicPlanner
        )
        return [
            BIASpecialist,
            RiskAnalyst,
            ProjectManager,
            IncidentAdvisor,
            PlanGenerator,
            ComplianceCopilot,
            ExerciseDesigner,
            ComplianceAuditor,
            BCMAdvisor,
            StrategicPlanner
        ]

    def get_analyzers(self):
        """Return BCM analyzers (тяжелые AI)"""
        from .analyzers import (
            GovernanceAnalyzer,
            ImpactAnalyzer,
            RiskAnalyzer,
            ComplianceAnalyzer,
            EmergencyAnalyzer,
            ScenarioAnalyzer,
            PerformanceAnalyzer,
            LearningAnalyzer,
            PlanAnalyzer,
            LifecycleAnalyzer
        )
        return [
            GovernanceAnalyzer,
            ImpactAnalyzer,
            RiskAnalyzer,
            ComplianceAnalyzer,
            EmergencyAnalyzer,
            ScenarioAnalyzer,
            PerformanceAnalyzer,
            LearningAnalyzer,
            PlanAnalyzer,
            LifecycleAnalyzer
        ]

    def get_services_metadata(self):
        """Return service metadata (NOT actual code)"""
        from .services_config import BCM_SERVICES
        return BCM_SERVICES
```

---

## 🚀 MIGRATION PLAN

### Phase 1: Подготовка (НЕ ЛОМАЕТ!)

```bash
# 1. Создать expertise-center структуру
mkdir -p intelligent-core/expertise-center/{core,shared,domains}
mkdir -p intelligent-core/expertise-center/shared/{base,tools,llm}
mkdir -p intelligent-core/expertise-center/domains/bcm/{specialists,analyzers,knowledge}

# 2. Создать workflow_intelligence/services структуру
mkdir -p intelligent-core/workflow_intelligence/services/{rag,ml,learning,context,case_library,journey,anomaly}
```

### Phase 2: Копирование кода (НЕ перемещение!)

```bash
# AI tools → workflow_intelligence/services/
cp -r intelligent-core/ai_experts/rag/* intelligent-core/workflow_intelligence/services/rag/
cp -r intelligent-core/ai_experts/ml/* intelligent-core/workflow_intelligence/services/ml/
cp -r intelligent-core/ai_experts/learning/* intelligent-core/workflow_intelligence/services/learning/

# Specialists → expertise-center/domains/bcm/specialists/
cp -r intelligent-core/ai-office/ВСМ-colleagues/* intelligent-core/expertise-center/domains/bcm/specialists/
cp intelligent-core/ai_experts/specialists/* intelligent-core/expertise-center/domains/bcm/specialists/

# Analyzers (organs) → expertise-center/domains/bcm/analyzers/
cp intelligent-core/ai-office/organs/* intelligent-core/expertise-center/domains/bcm/analyzers/

# Base classes → expertise-center/shared/base/
cp intelligent-core/ai_experts/base/* intelligent-core/expertise-center/shared/base/
cp intelligent-core/ai-office/base/* intelligent-core/expertise-center/shared/base/

# Tools → expertise-center/shared/tools/
cp -r intelligent-core/ai_experts/tools/* intelligent-core/expertise-center/shared/tools/

# Knowledge → expertise-center/domains/bcm/knowledge/
cp -r intelligent-core/ai_experts/knowledge/* intelligent-core/expertise-center/domains/bcm/knowledge/
```

### Phase 3: Создать __init__.py для всех sub-packages

```bash
# Create __init__.py files
touch intelligent-core/workflow_intelligence/services/{rag,ml,learning,context,case_library,journey,anomaly}/__init__.py
touch intelligent-core/expertise-center/domains/bcm/{specialists,analyzers}/__init__.py
```

### Phase 4: Обновить импорты (6 файлов)

```python
# bcm_offices/risk/ai/expert.py
# До:
from workflow_intelligence.integration.ai_context_builder import AIContextBuilder
from workflow_intelligence.core.case_library.repository import CaseLibraryRepository

# После:
from workflow_intelligence.services.context import AIContextBuilder
from workflow_intelligence.services.case_library import CaseRepository

# predictive/integration/dependencies.py
# До:
from workflow_intelligence.case_library.repository import CaseRepository

# После:
from workflow_intelligence.services.case_library import CaseRepository
```

### Phase 5: Тестирование

```bash
# Test imports
python3 -m pytest intelligent-core/workflow_intelligence/tests/
python3 -m pytest intelligent-core/expertise-center/tests/

# Test services
python3 -m pytest platform-services/bia-service/tests/
python3 -m pytest platform-services/risk-service/tests/
```

### Phase 6: Архивирование старого кода

```bash
# После успешных тестов
mv intelligent-core/ai_experts _archive/ai_experts
mv intelligent-core/ai-office _archive/ai-office
```

---

## ✅ ПРЕИМУЩЕСТВА ФИНАЛЬНОЙ АРХИТЕКТУРЫ

### 1. Ясность и логичность

**До:**
- ❌ ai_experts - часть brain или нет?
- ❌ ai-office - что это? BCM или platform?
- ❌ organs - что это значит?

**После:**
- ✅ workflow_intelligence = Brain + AI Tools (понятно!)
- ✅ expertise-center = AI Experts по доменам (понятно!)
- ✅ specialists = быстрые AI, analyzers = глубокие AI (понятно!)
- ✅ platform-services = бизнес логика (понятно!)

### 2. Убирает дублирование

- ✅ RAG: 3 реализации → 1 unified
- ✅ ML: 2 реализации → 1 unified
- ✅ Learning: 2 реализации → 1 unified
- ✅ Base classes: 2 места → 1 место
- ✅ ~6,000 LOC удалено

### 3. Гибкость использования

```python
# Import только то что нужно
from workflow_intelligence.services.rag import RAGPipeline

# Import всё из brain
from workflow_intelligence import *

# Import специалиста
from expertise_center.domains.bcm.specialists import BIASpecialist

# Import анализатора
from expertise_center.domains.bcm.analyzers import ImpactAnalyzer
```

### 4. Managed Autonomy сохранена

- ✅ Governance rules - те же
- ✅ Checkpoints - те же
- ✅ Creative zones - те же
- ✅ Философия - та же

### 5. Plugin architecture

```python
# Легко добавить новый домен
class HRDomain(BaseDomain):
    name = "hr"

    def get_specialists(self):
        return [RecruitmentSpecialist, TrainingManager]

# Platform автоматически загрузит
domain_loader.load_domain("hr")
```

### 6. Naming clarity

- ✅ Specialists - понятно на русском и английском
- ✅ Analyzers - понятно что делают (глубокий анализ)
- ✅ Нет странных "organs"

---

## 📊 SUMMARY

**Что изменилось:**
1. ✅ ai_experts → workflow_intelligence/services + expertise-center/shared
2. ✅ ai-office → expertise-center/domains/bcm
3. ✅ organs → analyzers (переименовано)
4. ✅ platform-services → ОСТАЮТСЯ КАК ЕСТЬ

**Что НЕ изменилось:**
1. ✅ Brain core (workflow_intelligence/core)
2. ✅ Governance philosophy
3. ✅ Platform services
4. ✅ Infrastructure

**Breaking changes:**
- Минимальные: 6 строк кода в 4 файлах

**Timeline:**
- Phase 1-3: 4-6 часов (создание структуры + копирование)
- Phase 4-5: 2-3 часа (обновление импортов + тесты)
- Phase 6: 1 час (архивирование)
- **TOTAL: 7-10 часов**

**Выгода:**
- Унифицированная архитектура
- Убрано ~6,000 LOC дублей
- Ясная структура для всех
- Готово к масштабированию

---

**Версия**: 5.0 Final
**Статус**: ✅ Ready for Implementation
**Следующий шаг**: Начать миграцию Phase 1?
