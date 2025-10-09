# 🤖 AI Experts - Unified Architecture

**Дата**: October 5, 2025
**Решение**: Создать единую архитектуру AI экспертов для всей платформы

---

## 🎯 Бизнес-Логика

### Принцип: 1 Модуль = 1 Эксперт

**У нас есть intelligent-core модули** → Каждому нужен свой AI эксперт

| № | Модуль | AI Expert | Специализация |
|---|--------|-----------|---------------|
| 1 | **workflow_intelligence** | BIA Specialist | Business Impact Analysis, RTO/RPO, dependencies |
| 2 | **workflow_intelligence** | Risk Analyst | Risk assessment, FAIR methodology, treatment |
| 3 | **workflow_intelligence** | Planning Specialist | BC strategies, recovery plans, procedures |
| 4 | **workflow_intelligence** | Incident Response Expert | Incident management, emergency response |
| 5 | **workflow_intelligence** | Exercise Designer | Exercise planning, scenarios, testing |
| 6 | **community_intelligence** | Compliance Auditor | ISO 22301 compliance, gap analysis, evidence |
| 7 | **collective** | Collective Wisdom Expert | Stuck detection, collective agent creation |
| 8 | **living-docs** | Documentation Expert | Content generation, personalization, learning |
| 9 | **knowledge** | Knowledge Manager | Learning patterns, self-learning, rules |
| 10 | **predictive** | Predictive Analyst | Forecasting, anomaly detection, trends |
| **+1** | **Координатор** | **Chief BCM Advisor** | Routing, orchestration, general consulting |

**Итого: 10 специалистов + 1 главный координатор = 11 AI экспертов**

---

## 🏗️ Единая Архитектура

### Где должны жить эксперты?

**РЕШЕНИЕ: `/intelligent-core/ai_experts/` - ЕДИНСТВЕННОЕ место для всех AI экспертов**

**Почему**:
- ✅ Единая архитектура
- ✅ Shared tools, RAG, ML
- ✅ Consistency
- ✅ Проще поддерживать
- ✅ Современная архитектура (tools + ML + learning)

### Что делать с ai-office?

**РЕШЕНИЕ: Мигрировать лучшее в ai_experts, остальное → archive**

**Что взять из ai-office**:
- ✅ RAG Pipeline (production-ready)
- ✅ Coordinator (routing logic)
- ✅ Detailed system prompts
- ✅ Meta Learning Engine
- ✅ AI Organs (как execution workers)

**Что НЕ нужно**:
- ❌ Дублирующие specialists
- ❌ Старая архитектура BaseAIColleague

---

## 📦 Новая Структура ai_experts

```
intelligent-core/ai_experts/
│
├── specialists/                    # 11 AI Experts
│   ├── __init__.py
│   ├── chief_bcm_advisor.py       # НОВЫЙ - главный координатор
│   ├── bia_specialist.py          # Migrate from ai-office
│   ├── risk_analyst.py            # Migrate from ai-office
│   ├── planning_specialist.py     # НОВЫЙ
│   ├── incident_expert.py         # Expand from ai-office
│   ├── exercise_designer.py       # Expand from ai-office
│   ├── compliance_auditor.py      # Already exists
│   ├── collective_expert.py       # НОВЫЙ
│   ├── documentation_expert.py    # НОВЫЙ
│   ├── knowledge_manager.py       # НОВЫЙ
│   └── predictive_analyst.py      # НОВЫЙ
│
├── base/                          # Base classes
│   ├── expert_agent.py           # Already exists
│   └── coordinator.py            # NEW - from ai-office
│
├── tools/                         # Already exists - 9 tools
│   ├── bia_tools.py              # ✅
│   ├── compliance_tools.py       # ✅
│   ├── strategic_tools.py        # ✅
│   ├── case_library_tool.py      # ✅
│   ├── risk_tools.py             # NEW
│   ├── planning_tools.py         # NEW
│   ├── incident_tools.py         # NEW
│   └── exercise_tools.py         # NEW
│
├── rag/                           # Merge from ai-office
│   ├── pipeline.py               # From ai-office (production)
│   ├── embeddings.py             # Already exists
│   ├── retrieval.py              # Already exists
│   ├── reranking.py              # Already exists
│   └── context_retriever.py      # From ai-office
│
├── ml/                            # Already exists
│   ├── predictive_models.py      # ✅
│   ├── anomaly_detection.py      # ✅
│   └── training_pipeline.py      # ✅
│
├── learning/                      # Already exists + from ai-office
│   ├── self_learning_engine.py   # ✅
│   ├── pattern_extractor.py      # ✅
│   ├── rule_generator.py         # ✅
│   └── meta_learning_engine.py   # From ai-office
│
├── organs/                        # From ai-office
│   ├── base_organ.py
│   ├── impact_oracle.py
│   ├── compliance_guardian.py
│   ├── risk_advisor.py
│   └── ... (10 organs)
│
├── api/                           # Public API
│   ├── experts.py                # FastAPI endpoints
│   └── coordinator.py            # Routing endpoint
│
├── main.py                        # FastAPI app (NEW)
├── config.py                      # Configuration
├── dependencies.py                # Dependency injection
└── requirements.txt
```

---

## 🎯 Архитектура Экспертов

### Base Class: ExpertAgent

```python
# base/expert_agent.py (уже существует, улучшить)

class ExpertAgent:
    """
    Base class для всех AI экспертов

    Все эксперты:
    - Используют tools (Anthropic tool calling)
    - Имеют RAG pipeline для контекста
    - Используют ML predictions
    - Self-learning от паттернов
    - Могут делегировать Organs
    """

    def __init__(
        self,
        name: str,
        role_description: str,
        knowledge_sources: List,
        tools: List[BaseTool],
        organs: Dict[str, BaseOrgan] = None,  # NEW
        temperature: float = 0.3
    ):
        self.name = name
        self.role = role_description
        self.knowledge_sources = knowledge_sources
        self.tools = tools
        self.organs = organs or {}  # NEW - execution workers
        self.temperature = temperature

        # Components
        self.rag_pipeline = None  # Injected
        self.ml_predictor = None  # Injected

    async def advise(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point для консультации

        Workflow:
        1. Analyze intent
        2. Use appropriate tools
        3. Delegate to organs if needed
        4. RAG for qualitative context
        5. ML predictions if applicable
        6. Synthesize response
        """

        # 1. Tool calling
        tool_results = await self._use_tools(query, context)

        # 2. Organ execution (if needed)
        organ_results = await self._delegate_to_organs(tool_results, context)

        # 3. RAG context
        rag_context = await self._get_rag_context(query, context)

        # 4. ML predictions
        predictions = await self._get_ml_predictions(context)

        # 5. Synthesize
        response = await self._synthesize_response(
            query=query,
            tool_results=tool_results,
            organ_results=organ_results,
            rag_context=rag_context,
            predictions=predictions
        )

        return response

    async def _use_tools(self, query, context):
        """Execute relevant tools"""
        # Tool calling logic
        pass

    async def _delegate_to_organs(self, tool_results, context):
        """Delegate heavy computations to organs"""
        # Organ delegation logic
        pass

    async def _get_rag_context(self, query, context):
        """Get RAG context"""
        return await self.rag_pipeline.process_query(query, context)

    async def _get_ml_predictions(self, context):
        """Get ML predictions if applicable"""
        if self.ml_predictor:
            return await self.ml_predictor.predict(context)
        return None

    async def _synthesize_response(self, **components):
        """Synthesize final response"""
        # Combine all components into coherent response
        pass
```

---

## 🤖 Примеры Специалистов

### 1. BIA Specialist (Migrate from ai-office)

```python
# specialists/bia_specialist.py

from ..base.expert_agent import ExpertAgent
from ..tools.bia_tools import BIAAnalysisTool, DependencyMapperTool, ImpactCalculatorTool
from ..organs.impact_oracle import ImpactOracle

class BIASpecialist(ExpertAgent):
    """
    Business Impact Analysis Expert

    Specializes in:
    - Critical process identification
    - RTO/RPO determination
    - Dependency mapping
    - Impact assessment
    """

    def __init__(self, case_library, knowledge_graph):
        # Tools
        tools = [
            BIAAnalysisTool(workflow_engine=None),
            DependencyMapperTool(case_library),
            ImpactCalculatorTool()
        ]

        # Organs (heavy computation)
        organs = {
            'impact_oracle': ImpactOracle()
        }

        super().__init__(
            name="BIA Specialist",
            role_description="Business Impact Analysis expert specializing in RTO/RPO and criticality assessment",
            knowledge_sources=[knowledge_graph, case_library],
            tools=tools,
            organs=organs,
            temperature=0.3
        )

    def _specialization(self) -> str:
        return """business impact analysis, RTO/RPO determination, and process criticality.

You excel at:
- Identifying critical business processes
- Calculating recovery time objectives (RTOs)
- Determining recovery point objectives (RPOs)
- Mapping dependencies and interdependencies
- Quantifying financial, operational, and reputational impacts
- Using tier-based criticality assessment

Your approach:
- Start with business needs, not technology
- Consider regulatory requirements
- Use real-world benchmarks from case library
- Be realistic about recovery objectives
- Focus on quantifiable impacts
"""
```

### 2. Chief BCM Advisor (НОВЫЙ - Координатор)

```python
# specialists/chief_bcm_advisor.py

from ..base.expert_agent import ExpertAgent

class ChiefBCMAdvisor(ExpertAgent):
    """
    Chief BCM Advisor - главный координатор

    Responsibilities:
    - Route queries to appropriate specialist
    - High-level strategic advice
    - Cross-module orchestration
    - General BCM consulting
    """

    def __init__(self, specialists: Dict[str, ExpertAgent], knowledge_graph):
        self.specialists = specialists  # All 10 specialists

        super().__init__(
            name="Chief BCM Advisor",
            role_description="Senior BCM consultant and coordinator",
            knowledge_sources=[knowledge_graph],
            tools=[],  # Uses specialists as "tools"
            temperature=0.5  # More creative for strategic advice
        )

    async def advise(self, query: str, context: Dict[str, Any]):
        """
        Route query or provide strategic advice

        Workflow:
        1. Analyze intent
        2. Decide: route to specialist OR handle directly
        3. If routing: delegate to specialist
        4. If handling: provide high-level strategic advice
        """

        # Analyze intent
        intent = await self._analyze_intent(query, context)

        # Route to specialist
        if intent.specialist_needed:
            specialist = self.specialists[intent.specialist_type]
            return await specialist.advise(query, context)

        # Handle strategically
        else:
            return await self._provide_strategic_advice(query, context)

    async def _analyze_intent(self, query, context):
        """Determine which specialist or handle directly"""
        # Intent analysis logic
        # Returns: {specialist_needed: bool, specialist_type: str}
        pass

    async def _provide_strategic_advice(self, query, context):
        """High-level strategic consulting"""
        # RAG + general knowledge
        pass
```

### 3. Collective Wisdom Expert (НОВЫЙ)

```python
# specialists/collective_expert.py

from ..base.expert_agent import ExpertAgent

class CollectiveWisdomExpert(ExpertAgent):
    """
    Collective Wisdom Expert

    Specializes in:
    - Stuck detection
    - Collective agent creation
    - Privacy-preserving help
    - K-anonymity guarantees
    """

    def __init__(self, case_library, analytics_client):
        tools = [
            StuckDetectionTool(analytics_client),
            CollectiveAgentTool(case_library)
        ]

        super().__init__(
            name="Collective Wisdom Expert",
            role_description="Expert in collective intelligence and privacy-preserving help",
            knowledge_sources=[case_library],
            tools=tools,
            temperature=0.4
        )
```

---

## 📋 Migration Plan

### Phase 1: Foundation (Week 1)

1. **Create base/coordinator.py** - migrate from ai-office
2. **Enhance base/expert_agent.py** - add organs support
3. **Create main.py** - FastAPI app for ai_experts

### Phase 2: Migrate Specialists (Week 2)

4. **Migrate BIA Specialist** - from ai-office to ai_experts
5. **Migrate Risk Analyst** - from ai-office to ai_experts
6. **Migrate Compliance Auditor** - merge versions
7. **Create Chief BCM Advisor** - new coordinator

### Phase 3: Expand Specialists (Week 3)

8. **Expand Planning Specialist** - from minimal to full
9. **Expand Incident Expert** - from minimal to full
10. **Expand Exercise Designer** - from minimal to full
11. **Create Collective Expert** - new
12. **Create Documentation Expert** - new
13. **Create Knowledge Manager** - new
14. **Create Predictive Analyst** - new

### Phase 4: Integration (Week 4)

15. **Integrate RAG Pipeline** - production version from ai-office
16. **Integrate Organs** - execution workers from ai-office
17. **Integrate Meta Learning** - from ai-office
18. **Create API endpoints** - FastAPI routes
19. **Testing** - integration tests
20. **Archive ai-office** - move to _archive/

---

## 🎯 API Design

### Expert Consultation Endpoint

```python
# api/experts.py

@router.post("/experts/{expert_type}/advise")
async def consult_expert(
    expert_type: str,
    request: ConsultationRequest,
    expert: ExpertAgent = Depends(get_expert)
):
    """
    Consult specific expert

    expert_type:
    - bia
    - risk
    - planning
    - incident
    - exercise
    - compliance
    - collective
    - documentation
    - knowledge
    - predictive
    - chief (coordinator)
    """

    response = await expert.advise(
        query=request.query,
        context=request.context
    )

    return response
```

### Coordinator Auto-Routing

```python
@router.post("/advise")
async def auto_route_query(
    request: ConsultationRequest,
    coordinator: ChiefBCMAdvisor = Depends(get_chief_advisor)
):
    """
    Auto-route query to appropriate expert

    Coordinator analyzes intent and routes
    """

    response = await coordinator.advise(
        query=request.query,
        context=request.context
    )

    return response
```

---

## ✅ Benefits of Unified Architecture

### 1. Consistency
- ✅ All experts use same base class
- ✅ Same tools framework
- ✅ Same ML predictions
- ✅ Same RAG pipeline

### 2. Reusability
- ✅ Shared tools across experts
- ✅ Shared organs (execution workers)
- ✅ Shared learning engine
- ✅ Shared knowledge sources

### 3. Scalability
- ✅ Easy to add new expert
- ✅ Easy to add new tool
- ✅ Easy to add new organ
- ✅ Modular architecture

### 4. Maintainability
- ✅ One place for all experts
- ✅ Clear structure
- ✅ No duplication
- ✅ Easy to update

### 5. Business Alignment
- ✅ 1 module = 1 expert (clear mapping)
- ✅ Chief coordinator (management structure)
- ✅ Scalable (add expert = add specialist)

---

## 🚀 Next Steps

### Immediate (This Week)

1. ✅ **Create AI_EXPERTS_UNIFIED_ARCHITECTURE.md** (done)
2. ⏳ **Decision**: Approve unified architecture
3. ⏳ **Create base/coordinator.py**
4. ⏳ **Create specialists/chief_bcm_advisor.py**
5. ⏳ **Migrate BIA Specialist** (proof of concept)

### Short-term (2-4 weeks)

6. ⏳ **Migrate all ai-office specialists**
7. ⏳ **Create new specialists** (Collective, Documentation, etc.)
8. ⏳ **Integrate Organs**
9. ⏳ **Create API endpoints**
10. ⏳ **Testing**

### Long-term (1-2 months)

11. ⏳ **Archive ai-office**
12. ⏳ **Documentation**
13. ⏳ **Performance optimization**
14. ⏳ **Advanced features**

---

## 📊 Summary

**Текущая ситуация**:
- ai-office: 7 colleagues (старая архитектура)
- ai_experts: 3 specialists (новая архитектура)
- **Дублирование и confusion**

**Решение**:
- ✅ **Единое место**: ai_experts
- ✅ **11 экспертов**: 10 специалистов + 1 координатор
- ✅ **1 модуль = 1 эксперт**: бизнес-логика
- ✅ **Лучшее из обоих**: tools + RAG + ML + organs
- ✅ **Миграция**: ai-office → ai_experts → archive

**Преимущества**:
- ✅ Consistency
- ✅ Scalability
- ✅ Business alignment
- ✅ No duplication
- ✅ Modern architecture

---

**Generated**: October 5, 2025
**Purpose**: Unified AI Experts Architecture
**Status**: ✅ Ready for implementation
