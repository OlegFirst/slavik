# 🏆 КОМБИНИРОВАННАЯ ФИНАЛЬНАЯ АРХИТЕКТУРА

**Версия:** 6.0 (Combined Best)
**Дата:** 2025-10-06
**Статус:** ✅ Финал (V5 + Claude улучшения)

---

## 🎯 ЧТО БЕРЕМ

### Из V5 (FINAL_ARCHITECTURE_V5.md):
✅ **Specialists/Analyzers** - отличное разделение
✅ **Plugin architecture** - expertise-center с domains
✅ **Managed Autonomy** - checkpoints + creative zones
✅ **Minimal breaking changes** - только 6 строк кода
✅ **Migration plan** - конкретный и реалистичный

### Из моего предложения (CORRECTED_FINAL_ARCHITECTURE.md):
✅ **ai-infrastructure** - отдельный слой для AI инструментов
✅ **workflow_intelligence остается focused** - только workflow logic
✅ **Автономность** - expertise-center НЕ зависит от workflow
✅ **4-уровневая иерархия** - ясное разделение слоев

---

## 🏗️ ФИНАЛЬНАЯ СТРУКТУРА

```
intelligent-core/
│
├── 🧠 workflow_intelligence/              THE BRAIN (Workflow Engine)
│   │                                      Focused: ТОЛЬКО workflow logic
│   ├── core/
│   │   ├── engine.py                      WorkflowEngine
│   │   ├── state_machine.py               State Machine
│   │   ├── transitions.py                 Transitions
│   │   ├── validators.py                  Validators
│   │   ├── context.py                     Workflow context
│   │   └── governance/                    Managed Autonomy
│   │       ├── rules_engine.py            13 safety rules
│   │       ├── checkpoints.py             Mandatory checks
│   │       └── creative_zones.py          AI freedom zones
│   │
│   ├── workflows/                         Workflow definitions
│   │   ├── definitions/                   YAML workflows
│   │   └── implementations/               Python implementations
│   │
│   ├── integration/                       Service adapters
│   │   ├── eventbus_publisher.py
│   │   └── service_adapters.py
│   │
│   └── monitoring/                        Metrics
│       └── metrics.py                     Prometheus metrics
│
├── 🔧 ai-infrastructure/                  AI FOUNDATION (Shared AI)
│   │                                      Используется ВСЕМИ
│   ├── rag/                               ✅ ONE RAG Pipeline
│   │   ├── __init__.py
│   │   ├── pipeline.py                    Main RAG
│   │   ├── embeddings.py                  Voyage/OpenAI
│   │   ├── retrieval.py                   Hybrid search
│   │   └── reranker.py                    Cohere reranker
│   │
│   ├── ml/                                ✅ ONE ML Engine
│   │   ├── __init__.py
│   │   ├── predictive_models.py           RF + GB
│   │   ├── training_pipeline.py           ML training
│   │   └── anomaly_detector.py            Anomaly detection
│   │
│   ├── learning/                          ✅ ONE Self-Learning
│   │   ├── __init__.py
│   │   ├── self_learning_engine.py        Learning engine
│   │   ├── pattern_extractor.py           Pattern extraction
│   │   └── rule_generator.py              Rule generation
│   │
│   ├── context/                           Context Services
│   │   ├── __init__.py
│   │   ├── context_builder.py             AI context builder
│   │   ├── context_aggregator.py          Multi-source aggregation
│   │   └── prompt_builder.py              Dynamic prompts
│   │
│   ├── case_library/                      Case Repository
│   │   ├── __init__.py
│   │   ├── collector.py                   Auto-collect cases
│   │   ├── repository.py                  Store & search
│   │   ├── analyzer.py                    Pattern analysis
│   │   └── bridge.py                      Community sync
│   │
│   ├── journey/                           Journey Prediction
│   │   ├── __init__.py
│   │   ├── journey_predictor.py           90-day prediction
│   │   └── timeline_engine.py             Timeline generation
│   │
│   └── anomaly/                           Anomaly Detection
│       ├── __init__.py
│       ├── stuck_detector.py              Workflow stuck detection
│       └── alerts.py                      Alert generation
│
├── 🎓 expertise-center/                   DOMAIN PLUGINS (AI Experts)
│   │
│   ├── core/
│   │   ├── chief_executive.py             Main AI orchestrator
│   │   ├── domain_loader.py               Plugin loader
│   │   ├── expert_registry.py             Expert registry
│   │   └── coordinator.py                 Request coordination
│   │
│   ├── shared/                            Shared for all domains
│   │   ├── base/
│   │   │   ├── base_specialist.py         ✅ Specialists (легкие AI)
│   │   │   ├── base_analyzer.py           ✅ Analyzers (тяжелые AI)
│   │   │   └── base_tool.py               Tool base class
│   │   │
│   │   ├── tools/                         Domain-agnostic tools
│   │   │   ├── bia_tools.py
│   │   │   ├── compliance_tools.py
│   │   │   ├── strategic_tools.py
│   │   │   └── case_library_tool.py
│   │   │
│   │   └── llm/                           LLM Clients
│   │       ├── llm_client.py              Unified client
│   │       ├── anthropic_adapter.py       Claude
│   │       ├── openai_adapter.py          GPT
│   │       └── llm_router.py              Model routing
│   │
│   └── domains/                           🔌 DOMAIN PLUGINS
│       │
│       └── bcm/                           BCM Plugin
│           ├── __init__.py                BCMDomain class
│           │
│           ├── specialists/               10 Specialists (легкие)
│           │   ├── bia_specialist.py
│           │   ├── risk_analyst.py
│           │   ├── compliance_copilot.py
│           │   ├── project_manager.py
│           │   ├── incident_advisor.py
│           │   ├── plan_generator.py
│           │   ├── exercise_designer.py
│           │   ├── compliance_auditor.py
│           │   ├── bcm_advisor.py
│           │   └── strategic_planner.py
│           │
│           ├── analyzers/                 10 Analyzers (тяжелые)
│           │   ├── impact_analyzer.py
│           │   ├── risk_analyzer.py
│           │   ├── compliance_analyzer.py
│           │   ├── governance_analyzer.py
│           │   ├── emergency_analyzer.py
│           │   ├── scenario_analyzer.py
│           │   ├── performance_analyzer.py
│           │   ├── learning_analyzer.py
│           │   ├── plan_analyzer.py
│           │   └── lifecycle_analyzer.py
│           │
│           ├── knowledge/                 BCM Knowledge
│           │   ├── iso_22301/
│           │   ├── bci_guidelines/
│           │   └── best_practices/
│           │
│           └── services_config.py         Metadata only
│
├── 🎯 orchestration/                      ORCHESTRATION LAYER
│   ├── ai-orchestration/                  AI Decision Engine
│   └── coordination-center/               API Coordination
│
└── 🔧 ai-tools/                           AI UTILITIES
    ├── workflow-optimizer/                ML optimization
    └── agent-router/                      Request routing
```

---

## 🎯 КЛЮЧЕВЫЕ ПРИНЦИПЫ

### 1. Разделение Ответственности (Single Responsibility)

**workflow_intelligence:**
- ✅ ТОЛЬКО workflow logic
- ✅ State machine, transitions, governance
- ✅ Workflow definitions
- ❌ НЕТ RAG/ML/Learning (это не workflow!)

**ai-infrastructure:**
- ✅ Shared AI инструменты
- ✅ RAG, ML, Learning, Context, Case Library
- ✅ Используется ВСЕМИ (workflow, specialists, analyzers)
- ❌ НЕТ domain logic

**expertise-center:**
- ✅ Domain plugins (BCM, HR, Finance...)
- ✅ Specialists + Analyzers
- ✅ Использует ai-infrastructure
- ❌ НЕТ собственной AI инфраструктуры

### 2. Dependency Flow (правильные зависимости)

```
expertise-center → ai-infrastructure
workflow_intelligence → ai-infrastructure
orchestration → ai-infrastructure + expertise-center

НО: ai-infrastructure НЕ зависит ни от кого!
```

### 3. Naming Clarity (ясные названия)

- ✅ **workflow_intelligence** = workflow engine (понятно!)
- ✅ **ai-infrastructure** = AI tools (понятно!)
- ✅ **expertise-center** = domain experts (понятно!)
- ✅ **specialists** = легкие AI (понятно!)
- ✅ **analyzers** = тяжелые AI (понятно!)

---

## 🔄 REQUEST FLOW

### Сценарий: "Провести глубокий BIA анализ"

```
1. USER REQUEST
   ↓
   POST /api/v1/bcm/bia/analyze
   { "process": "payment", "deep_analysis": true }

2. platform-services/bia-service
   ↓
   async def analyze_bia(request):
       # A. Workflow check (workflow_intelligence)
       workflow = await brain.get_workflow("bia")
       await workflow.governance.validate(request)

       # B. Database operations
       bia = await db.create_bia(request)

       # C. AI Analysis (expertise-center)
       if request.use_ai:
           # Get specialist
           specialist = await get_specialist("bcm", "bia_specialist")
           insights = await specialist.analyze(request.data)

           # Deep analysis
           if request.deep_analysis:
               analyzer = await get_analyzer("bcm", "impact_analyzer")
               deep = await analyzer.analyze(request.data)
               insights.merge(deep)

           bia.ai_insights = insights

       # D. Store in case library (ai-infrastructure)
       await ai_infra.case_library.store_case(bia)

       return bia

3. expertise-center/domains/bcm/specialists/bia_specialist
   ↓
   class BIASpecialist(BaseSpecialist):
       async def analyze(self, data):
           # Uses ai-infrastructure (не workflow!)

           # RAG search
           similar = await ai_infra.rag.search(
               f"BIA for {data['process']}"
           )

           # ML prediction
           criticality = await ai_infra.ml.predict(
               model="criticality", data=data
           )

           # Context builder
           context = await ai_infra.context.build(
               data, similar, criticality
           )

           # LLM call (1-2 calls)
           advice = await self.llm.generate(
               prompt=self._build_prompt(context)
           )

           return {
               "criticality": criticality,
               "similar_cases": similar,
               "advice": advice
           }

4. expertise-center/domains/bcm/analyzers/impact_analyzer
   ↓
   class ImpactAnalyzer(BaseAnalyzer):
       async def analyze(self, data):
           # Multi-step deep analysis (5-10 LLM calls)
           # Also uses ai-infrastructure

           # Step 1: Identify factors
           factors = await self.llm.chain_of_thought(...)

           # Step 2-6: Analyze each
           analyses = []
           for factor in factors:
               analysis = await self.llm.deep_analyze(factor)

               # Use RAG for each factor
               context = await ai_infra.rag.search(factor)
               analysis.enrich(context)

               analyses.append(analysis)

           # Step 7: Cross-impact
           cross = await self.llm.analyze_interactions(analyses)

           # Step 8: Synthesis
           synthesis = await self.llm.synthesize(...)

           # Step 9: Recommendations
           recommendations = await self.llm.recommend(synthesis)

           # Step 10: Confidence
           confidence = await self.llm.assess_confidence(...)

           return {
               "factors": factors,
               "analyses": analyses,
               "synthesis": synthesis,
               "recommendations": recommendations,
               "confidence": confidence
           }

5. RESULT
   ↓
   {
     "bia_id": "bia_123",
     "criticality": "high",
     "mtpd": "4 hours",
     "ai_insights": {
       "specialist": {...},      # Quick (1-2 LLM calls)
       "analyzer": {...}          # Deep (10 LLM calls)
     },
     "confidence": 0.92,
     "stored_in_case_library": true
   }
```

---

## 📦 IMPORT PATTERNS

### Workflow Intelligence (Workflow logic)

```python
# Import workflow engine
from workflow_intelligence.core import WorkflowEngine, StateMachine
from workflow_intelligence.core.governance import Governance

# Use workflow
workflow = WorkflowEngine(workflow_id="bia_123", workflow_type="bia")
await workflow.governance.validate(request)
```

### AI Infrastructure (AI tools)

```python
# Import AI tools
from ai_infrastructure.rag import RAGPipeline
from ai_infrastructure.ml import WorkflowPredictor
from ai_infrastructure.learning import SelfLearningEngine
from ai_infrastructure.context import AIContextBuilder
from ai_infrastructure.case_library import CaseRepository

# Use RAG
rag = RAGPipeline()
results = await rag.search("BIA for payment processing", top_k=5)

# Use ML
predictor = WorkflowPredictor()
criticality = await predictor.predict(data)

# Use Case Library
cases = CaseRepository()
similar = await cases.find_similar(query)
```

### Expertise Center (Domain experts)

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

# Use specialist
specialist = BIASpecialist()
specialist.inject_infrastructure(ai_infra)  # Inject ai-infrastructure
insights = await specialist.analyze(data)

# Use analyzer
analyzer = ImpactAnalyzer()
analyzer.inject_infrastructure(ai_infra)  # Inject ai-infrastructure
deep = await analyzer.analyze(data)
```

---

## 🎓 SPECIALIST vs ANALYZER (Из V5)

### SPECIALIST (Легковесный AI)

**Характеристики:**
- 1-2 LLM calls
- Быстрый ответ (<5 сек)
- Использует готовые tools
- Стандартные промпты

**Когда:**
- Рутинные задачи
- Стандартные вопросы
- Быстрые советы
- Guided workflows

**Примеры:**
- BIA Specialist - расчет BIA
- Risk Analyst - базовый risk assessment
- Compliance Copilot - проверка соответствия

### ANALYZER (Тяжелый AI)

**Характеристики:**
- 5-10+ LLM calls
- Chain of thought reasoning
- Долгий ответ (30-60+ сек)
- Многоступенчатый анализ

**Когда:**
- Сложные решения
- Стратегический анализ
- Критические оценки
- Глубокое понимание

**Примеры:**
- Impact Analyzer - глубокий BIA анализ
- Risk Analyzer - FAIR quantitative
- Compliance Analyzer - полный audit

---

## 🚀 MIGRATION PLAN

### Phase 1: Создать ai-infrastructure (3-4 часа)

```bash
# 1. Структура
mkdir -p intelligent-core/ai-infrastructure/{rag,ml,learning,context,case_library,journey,anomaly}

# 2. Копировать (НЕ перемещать!)
# RAG (merge ai_experts + ai-office)
cp -r intelligent-core/ai_experts/rag/* intelligent-core/ai-infrastructure/rag/
cp intelligent-core/ai-office/core/rag/* intelligent-core/ai-infrastructure/rag/

# ML (merge ai_experts + community)
cp -r intelligent-core/ai_experts/ml/* intelligent-core/ai-infrastructure/ml/
cp intelligent-core/community_intelligence/ml/* intelligent-core/ai-infrastructure/ml/

# Learning (merge ai_experts + ai-office)
cp -r intelligent-core/ai_experts/learning/* intelligent-core/ai-infrastructure/learning/
cp intelligent-core/ai-office/core/learning/* intelligent-core/ai-infrastructure/learning/

# Context (from workflow_intelligence)
cp -r intelligent-core/workflow_intelligence/integration/ai_context_builder.py \
  intelligent-core/ai-infrastructure/context/context_builder.py

# Case Library (from workflow_intelligence)
cp -r intelligent-core/workflow_intelligence/core/case_library/* \
  intelligent-core/ai-infrastructure/case_library/

# Journey (from predictive)
cp -r intelligent-core/predictive/services/journey_predictor.py \
  intelligent-core/ai-infrastructure/journey/

# Anomaly (from collective)
cp -r intelligent-core/collective/services/stuck_detector.py \
  intelligent-core/ai-infrastructure/anomaly/

# 3. Create __init__.py for all
touch intelligent-core/ai-infrastructure/{rag,ml,learning,context,case_library,journey,anomaly}/__init__.py
```

### Phase 2: Создать expertise-center (2-3 часа)

```bash
# 1. Структура
mkdir -p intelligent-core/expertise-center/{core,shared,domains}
mkdir -p intelligent-core/expertise-center/shared/{base,tools,llm}
mkdir -p intelligent-core/expertise-center/domains/bcm/{specialists,analyzers,knowledge}

# 2. Shared
cp -r intelligent-core/ai_experts/base/* intelligent-core/expertise-center/shared/base/
cp -r intelligent-core/ai_experts/tools/* intelligent-core/expertise-center/shared/tools/
cp -r intelligent-core/ai-office/llm/* intelligent-core/expertise-center/shared/llm/

# 3. BCM Specialists
cp -r intelligent-core/ai-office/ВСМ-colleagues/* \
  intelligent-core/expertise-center/domains/bcm/specialists/
cp intelligent-core/ai_experts/specialists/* \
  intelligent-core/expertise-center/domains/bcm/specialists/

# 4. BCM Analyzers (rename from organs)
cp intelligent-core/ai-office/organs/* \
  intelligent-core/expertise-center/domains/bcm/analyzers/
# Переименовать: organ.py → analyzer.py

# 5. Knowledge
cp -r intelligent-core/ai_experts/knowledge/* \
  intelligent-core/expertise-center/domains/bcm/knowledge/
```

### Phase 3: Обновить импорты (2-3 часа)

**Обновить 8-10 файлов:**

```python
# 1. platform-services/*/integration/ai_integration.py
# OLD:
from workflow_intelligence.integration.ai_context_builder import AIContextBuilder
from workflow_intelligence.core.case_library import CaseRepository

# NEW:
from ai_infrastructure.context import AIContextBuilder
from ai_infrastructure.case_library import CaseRepository

# 2. bcm_offices/risk/ai/expert.py
# OLD:
from workflow_intelligence.integration.ai_context_builder import AIContextBuilder

# NEW:
from ai_infrastructure.context import AIContextBuilder

# 3. predictive/integration/dependencies.py
# OLD:
from workflow_intelligence.case_library.repository import CaseRepository

# NEW:
from ai_infrastructure.case_library import CaseRepository

# 4. Все specialists/analyzers
# Добавить injection:
class BIASpecialist(BaseSpecialist):
    def inject_infrastructure(self, ai_infra):
        self.rag = ai_infra.rag
        self.ml = ai_infra.ml
        self.learning = ai_infra.learning
        self.context = ai_infra.context
        self.case_library = ai_infra.case_library
```

### Phase 4: Создать __init__.py (1 час)

```python
# ai-infrastructure/__init__.py
"""
AI Infrastructure - Shared AI Tools

Provides RAG, ML, Learning, and other AI services for the entire platform.
"""

from .rag import RAGPipeline
from .ml import WorkflowPredictor, MLTrainer
from .learning import SelfLearningEngine
from .context import AIContextBuilder
from .case_library import CaseRepository
from .journey import JourneyPredictor
from .anomaly import StuckDetector

__all__ = [
    'RAGPipeline',
    'WorkflowPredictor',
    'MLTrainer',
    'SelfLearningEngine',
    'AIContextBuilder',
    'CaseRepository',
    'JourneyPredictor',
    'StuckDetector',
]

# expertise-center/__init__.py
"""
Expertise Center - Domain Plugin System

Manages domain plugins with specialists and analyzers.
"""

from .core import ChiefExecutiveAI, DomainLoader, ExpertRegistry
from .shared.base import BaseSpecialist, BaseAnalyzer

__all__ = [
    'ChiefExecutiveAI',
    'DomainLoader',
    'ExpertRegistry',
    'BaseSpecialist',
    'BaseAnalyzer',
]
```

### Phase 5: Тестирование (2-3 часа)

```bash
# Unit tests
pytest intelligent-core/ai-infrastructure/tests/ -v
pytest intelligent-core/expertise-center/tests/ -v
pytest intelligent-core/workflow_intelligence/tests/ -v

# Integration tests
pytest platform-services/bia-service/tests/ -v
pytest platform-services/risk-service/tests/ -v

# Import tests
python3 -c "from ai_infrastructure import RAGPipeline; print('✅ ai-infrastructure OK')"
python3 -c "from expertise_center import ChiefExecutiveAI; print('✅ expertise-center OK')"
python3 -c "from workflow_intelligence.core import WorkflowEngine; print('✅ workflow OK')"
```

### Phase 6: Архивирование (1 час)

```bash
# После успешных тестов
mv intelligent-core/ai_experts _archive/ai_experts_v1
mv intelligent-core/ai-office _archive/ai-office_v1
mv intelligent-core/bcm_offices _archive/bcm_offices_v1
```

---

## ✅ ПРЕИМУЩЕСТВА КОМБИНИРОВАННОЙ АРХИТЕКТУРЫ

### 1. Best of Both Worlds

**Из V5:**
- ✅ Specialists/Analyzers (отличное разделение)
- ✅ Plugin architecture (BCM как domain)
- ✅ Minimal breaking changes
- ✅ Managed Autonomy сохранена

**Из моего:**
- ✅ ai-infrastructure (четкий AI слой)
- ✅ workflow_intelligence focused (только workflow)
- ✅ Автономность (expertise НЕ зависит от workflow)
- ✅ Single Responsibility (каждый слой = одна роль)

### 2. Ясная Архитектура

```
workflow_intelligence     = Workflow Logic      (state machine, governance)
ai-infrastructure         = AI Tools            (RAG, ML, Learning)
expertise-center          = Domain Experts      (specialists, analyzers)
platform-services         = Business Services   (REST API, CRUD)
```

**Каждый знает свою роль!**

### 3. Правильные Зависимости

```
Level 4: platform-services → expertise-center, workflow_intelligence, ai-infrastructure
Level 3: expertise-center → ai-infrastructure
Level 2: workflow_intelligence → ai-infrastructure
Level 1: ai-infrastructure (независим!)
```

**Нет circular dependencies!**

### 4. Гибкость Использования

```python
# Можно использовать отдельно:
from ai_infrastructure.rag import RAGPipeline  # Только RAG

# Можно использовать вместе:
from ai_infrastructure import *  # Все AI tools

# Можно использовать с workflow:
from workflow_intelligence.core import WorkflowEngine
workflow = WorkflowEngine()
rag = RAGPipeline()  # Они независимы!
```

### 5. Легко Масштабировать

```python
# Добавить новый AI tool
ai-infrastructure/
└── vector_db/  # NEW!
    ├── __init__.py
    └── vector_client.py

# Добавить новый домен
expertise-center/domains/
└── hr/  # NEW!
    ├── specialists/
    └── analyzers/
```

---

## 📊 СРАВНЕНИЕ ВАРИАНТОВ

| Аспект | V5 | Мой вариант | **Комбинированный** |
|--------|----|--------------|--------------------|
| **workflow_intelligence** | Раздут (core + services) | Focused (только core) | ✅ **Focused (только core)** |
| **AI инструменты** | В workflow/services | В ai-foundation | ✅ **В ai-infrastructure** |
| **Specialists/Analyzers** | ✅ Да | Да | ✅ **Да (из V5)** |
| **Plugin architecture** | ✅ Да | Да | ✅ **Да (из V5)** |
| **Breaking changes** | ✅ 6 строк | ~15 строк | ✅ **8-10 строк** |
| **Migration time** | ✅ 7-10 часов | 12-15 часов | ✅ **10-12 часов** |
| **Clarity** | 7/10 | 9/10 | ✅ **9/10** |
| **Scalability** | 7/10 | 9/10 | ✅ **9/10** |
| **Autonomy** | 6/10 | 9/10 | ✅ **9/10** |

---

## 🎯 ИТОГОВОЕ РЕШЕНИЕ

### Структура:

```
intelligent-core/
├── workflow_intelligence/      🧠 Workflow Logic (focused!)
├── ai-infrastructure/          🔧 AI Tools (RAG, ML, Learning)
├── expertise-center/           🎓 Domain Plugins (BCM, HR...)
└── orchestration/              🎯 Orchestration Layer
```

### Принципы:

1. ✅ **Single Responsibility** - каждый модуль = одна роль
2. ✅ **Dependency Inversion** - ai-infrastructure независим
3. ✅ **Plugin Architecture** - domains как plugins
4. ✅ **Specialists/Analyzers** - ясное разделение AI
5. ✅ **Minimal Changes** - 8-10 строк кода

### Timeline:

- Phase 1: ai-infrastructure (3-4 часа)
- Phase 2: expertise-center (2-3 часа)
- Phase 3: Update imports (2-3 часа)
- Phase 4: Create __init__.py (1 час)
- Phase 5: Testing (2-3 часа)
- Phase 6: Archive (1 час)

**TOTAL: 10-12 часов**

### Выгода:

- ✅ Ясная архитектура (каждый знает роль)
- ✅ Правильные зависимости (no circular)
- ✅ Легко масштабировать (new domains, new tools)
- ✅ Specialists/Analyzers (из V5)
- ✅ Minimal breaking changes
- ✅ ~6,000 LOC дублей удалено

---

**Версия:** 6.0 (Combined Best)
**Статус:** ✅ Финальное решение
**Следующий шаг:** Начинаем миграцию?
