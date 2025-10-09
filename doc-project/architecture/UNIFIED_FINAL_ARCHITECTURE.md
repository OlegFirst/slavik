# 🎯 ЕДИНАЯ ФИНАЛЬНАЯ АРХИТЕКТУРА

**Версия**: 6.0 Unified Final
**Дата**: 2025-10-06
**Статус**: ✅ Объединяет VARIANT 5 + CORRECTED_FINAL_ARCHITECTURE

---

## 📊 СРАВНЕНИЕ ДВУХ ПОДХОДОВ

### VARIANT 5 (FINAL_ARCHITECTURE_V5.md)

**Фокус**: workflow_intelligence как THE BRAIN с унифицированными AI сервисами

**Структура:**
```
workflow_intelligence/          # THE BRAIN + AI TOOLS
├─ core/
├─ services/                   # RAG, ML, Learning - внутри brain!
└─ workflows/

expertise-center/
├─ shared/                     # Base classes, tools, LLM
└─ domains/bcm/
   ├─ specialists/             # 13 специалистов (все в одной категории)
   ├─ analyzers/               # 10 анализаторов (переименованные organs)
   └─ knowledge/
```

**Ключевая идея**: AI tools (RAG, ML, Learning) - это инструменты МОЗГА

---

### CORRECTED_FINAL (CORRECTED_FINAL_ARCHITECTURE.md)

**Фокус**: expertise-center как главный координатор, 3-уровневая иерархия AI агентов

**Структура:**
```
expertise-center/               # ГЛАВНЫЙ КООРДИНАТОР
├─ shared/                     # RAG, ML, Learning - shared infrastructure!
│  ├─ rag/
│  ├─ ml/
│  └─ learning/
└─ domains/bcm/
   ├─ specialists/             # 3 стратегических (bcm_advisor, compliance_auditor, strategic_planner)
   ├─ colleagues/              # 7 тактических (bia_specialist, risk_analyst...)
   └─ organs/                  # 10 тяжелых AI (risk_advisor, impact_oracle...)

workflow_intelligence/          # THE BRAIN (не трогать!)
```

**Ключевая идея**: 3-уровневая иерархия AI агентов (strategic, tactical, heavy)

---

## 🎯 ОБЪЕДИНЕННАЯ АРХИТЕКТУРА (Best of Both)

### Принятые решения:

1. ✅ **workflow_intelligence** = THE BRAIN (core + governance)
2. ✅ **AI Services (RAG, ML, Learning)** - внутри workflow_intelligence/services/ (как в Variant 5)
   - **Почему**: Это инструменты МОЗГА, используются для workflow intelligence
3. ✅ **3-уровневая иерархия** AI агентов (как в CORRECTED)
   - **Specialists** = Стратегические (3 эксперта)
   - **Colleagues** = Тактические (7-10 помощников)
   - **Analyzers** = Тяжелые AI (10 анализаторов) - **НЕ organs!**
4. ✅ **expertise-center** = Domain plugin manager с BCM domain
5. ✅ **Naming**: Analyzers вместо Organs (профессиональнее)

---

## 📁 ФИНАЛЬНАЯ СТРУКТУРА (Unified)

```
AI-Platform-ISO/
│
├─ intelligent-core/
│  │
│  ├─ workflow_intelligence/                   # 🧠 THE BRAIN
│  │  │
│  │  ├─ __init__.py
│  │  ├─ README.md
│  │  │
│  │  ├─ core/                                # Brain Core Logic
│  │  │  ├─ __init__.py
│  │  │  ├─ engine.py                         # WorkflowEngine
│  │  │  ├─ state_machine.py                  # State Machine
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
│  │  ├─ services/                            # AI Tools (Brain Instruments)
│  │  │  │                                    # ← Из ai_experts + ai-office/core
│  │  │  ├─ rag/                             # RAG Service (1,368 LOC)
│  │  │  │  ├─ __init__.py                   # Export: RAGPipeline
│  │  │  │  ├─ pipeline.py
│  │  │  │  ├─ embeddings.py
│  │  │  │  ├─ retrieval.py
│  │  │  │  ├─ reranker.py
│  │  │  │  └─ config.py
│  │  │  │
│  │  │  ├─ ml/                              # ML Service (1,127 LOC)
│  │  │  │  ├─ __init__.py                   # Export: WorkflowPredictor
│  │  │  │  ├─ predictive_models.py
│  │  │  │  ├─ training_pipeline.py
│  │  │  │  ├─ anomaly_detector.py
│  │  │  │  └─ community_predictor.py
│  │  │  │
│  │  │  ├─ learning/                        # Self-Learning (619 LOC)
│  │  │  │  ├─ __init__.py                   # Export: SelfLearningEngine
│  │  │  │  ├─ self_learning_engine.py
│  │  │  │  ├─ pattern_extractor.py
│  │  │  │  ├─ rule_generator.py
│  │  │  │  └─ improvement_tracker.py
│  │  │  │
│  │  │  ├─ context/                         # Context Service (522 LOC)
│  │  │  │  ├─ __init__.py                   # Export: AIContextBuilder
│  │  │  │  ├─ context_builder.py
│  │  │  │  ├─ context_aggregator.py
│  │  │  │  ├─ prompt_builder.py
│  │  │  │  └─ enricher.py
│  │  │  │
│  │  │  ├─ case_library/                    # Case Library (750 LOC)
│  │  │  │  ├─ __init__.py                   # Export: CaseRepository
│  │  │  │  ├─ collector.py
│  │  │  │  ├─ repository.py
│  │  │  │  ├─ analyzer.py
│  │  │  │  ├─ search.py
│  │  │  │  ├─ models.py
│  │  │  │  └─ bridge.py
│  │  │  │
│  │  │  ├─ journey/                         # Journey Prediction (687 LOC)
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ journey_predictor.py
│  │  │  │  ├─ timeline_engine.py
│  │  │  │  └─ milestone_tracker.py
│  │  │  │
│  │  │  └─ anomaly/                         # Anomaly Detection (529 LOC)
│  │  │     ├─ __init__.py
│  │  │     ├─ stuck_detector.py
│  │  │     ├─ anomaly_detector.py
│  │  │     └─ alerts.py
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
│  │  ├─ integration/                         # Service Adapters
│  │  │  ├─ __init__.py
│  │  │  ├─ eventbus_publisher.py
│  │  │  ├─ bia_adapter.py
│  │  │  └─ service_adapters.py
│  │  │
│  │  ├─ monitoring/
│  │  │  ├─ __init__.py
│  │  │  └─ metrics.py
│  │  │
│  │  └─ tests/
│  │
│  ├─ expertise-center/                       # 🎓 DOMAIN PLUGIN MANAGER
│  │  │
│  │  ├─ __init__.py
│  │  ├─ README.md
│  │  │
│  │  ├─ core/                               # Plugin Manager Core
│  │  │  ├─ __init__.py
│  │  │  ├─ chief_executive.py              # Main AI orchestrator & router
│  │  │  ├─ domain_loader.py                # Plugin loader
│  │  │  ├─ expert_registry.py              # Expert registry
│  │  │  └─ coordinator.py                  # Request coordination
│  │  │
│  │  ├─ shared/                             # Shared Infrastructure
│  │  │  │                                   # (НЕ AI services! Только base classes + tools)
│  │  │  ├─ base/                            # Base Classes
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ base_specialist.py           # Strategic AI (high-level)
│  │  │  │  ├─ base_colleague.py            # Tactical AI (operational)
│  │  │  │  ├─ base_analyzer.py             # Heavy AI (deep analysis)
│  │  │  │  ├─ base_tool.py                 # Tool base class
│  │  │  │  └─ base_domain.py               # Domain plugin base
│  │  │  │
│  │  │  ├─ tools/                           # Shared Tools (2,747 LOC)
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ bia_tools.py
│  │  │  │  ├─ compliance_tools.py
│  │  │  │  ├─ strategic_tools.py
│  │  │  │  ├─ case_library_tool.py
│  │  │  │  └─ base_tool.py
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
│  │        ├─ specialists/                  # 🎯 Strategic Experts (3)
│  │        │  │                             # High-level, strategic planning
│  │        │  ├─ __init__.py
│  │        │  ├─ bcm_advisor.py            # General BCM strategy
│  │        │  ├─ compliance_auditor.py     # Compliance strategy
│  │        │  └─ strategic_planner.py      # Long-term planning
│  │        │
│  │        ├─ colleagues/                   # 💬 Tactical Assistants (7-10)
│  │        │  │                             # Operational tasks, guided workflows
│  │        │  ├─ __init__.py
│  │        │  ├─ bia_specialist.py         # BIA operational tasks
│  │        │  ├─ risk_analyst.py           # Risk operational tasks
│  │        │  ├─ project_manager.py        # Project coordination
│  │        │  ├─ incident_advisor.py       # Incident response guidance
│  │        │  ├─ plan_generator.py         # Plan creation assistance
│  │        │  ├─ compliance_copilot.py     # Compliance guidance
│  │        │  └─ exercise_designer.py      # Exercise planning
│  │        │
│  │        ├─ analyzers/                    # 🧠 Heavy AI Analyzers (10)
│  │        │  │                             # Deep analysis, complex reasoning
│  │        │  ├─ __init__.py
│  │        │  ├─ governance_analyzer.py    # Deep governance analysis
│  │        │  ├─ impact_analyzer.py        # Deep BIA analysis
│  │        │  ├─ risk_analyzer.py          # Deep risk analysis (FAIR, Monte Carlo)
│  │        │  ├─ compliance_analyzer.py    # Deep compliance analysis
│  │        │  ├─ emergency_analyzer.py     # Emergency response analysis
│  │        │  ├─ scenario_analyzer.py      # Scenario generation
│  │        │  ├─ performance_analyzer.py   # Performance metrics analysis
│  │        │  ├─ learning_analyzer.py      # Learning effectiveness
│  │        │  ├─ plan_analyzer.py          # Plan quality analysis
│  │        │  └─ lifecycle_analyzer.py     # PDCA lifecycle analysis
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
│  ├─ bia-service/
│  ├─ risk-service/
│  ├─ governance-service/
│  ├─ planning_service/
│  ├─ plans_service/
│  ├─ response-service/
│  ├─ compliance-service/
│  ├─ documents-service/
│  ├─ validation-service/
│  └─ learning-service/
│
├─ infrastructure/                           # ⚙️ INFRASTRUCTURE
│  ├─ database/
│  ├─ eventbus/
│  ├─ auth/
│  ├─ monitoring/
│  └─ observability/
│
└─ _archive/                                # 📦 ARCHIVED
   ├─ ai_experts/
   └─ ai-office/
```

---

## 🎯 КЛЮЧЕВЫЕ РЕШЕНИЯ

### 1. Где AI Services (RAG, ML, Learning)?

**✅ РЕШЕНИЕ: В workflow_intelligence/services/**

**Почему:**
- RAG, ML, Learning - это **инструменты МОЗГА**
- Они используются для workflow intelligence (предсказание, анализ паттернов, case library)
- Brain управляет workflow → Brain нужны AI tools для этого
- Согласуется с концепцией "THE BRAIN" из оригинальной архитектуры

**Использование:**
```python
# Brain использует свои инструменты
from workflow_intelligence.services.rag import RAGPipeline
from workflow_intelligence.services.ml import WorkflowPredictor

# Specialists/Colleagues/Analyzers ТОЖЕ используют brain tools
class BIASpecialist(BaseColleague):
    async def analyze(self, data):
        # Используем RAG из brain
        similar = await self.brain.services.rag.search(data)
        # Используем ML из brain
        prediction = await self.brain.services.ml.predict(data)
```

---

### 2. Три уровня AI агентов

**✅ ИЕРАРХИЯ:**

#### SPECIALISTS (Стратегические эксперты) - 3 эксперта

**Из:** ai_experts/specialists/

**Кто:**
- `bcm_advisor.py` - Общая BCM стратегия
- `compliance_auditor.py` - Compliance стратегия
- `strategic_planner.py` - Долгосрочное планирование

**Для чего:**
- Strategic planning
- Policy recommendations
- High-level advisory
- Long-term roadmaps
- Industry benchmarking

**Характеристики:**
- Широкий охват (вся организация)
- Стратегический уровень (3-5 лет)
- Используют: Knowledge Graph, Case Library, Industry Benchmarks
- LLM calls: 2-3 (умеренно)

**Пример запроса:**
```
"How should we structure our BCM program for healthcare industry?"
"What's the best compliance strategy for ISO 22301 + HIPAA?"
"Create a 3-year BCM roadmap for our organization"
```

---

#### COLLEAGUES (Тактические помощники) - 7-10 помощников

**Из:** ai-office/ВСМ-colleagues/

**Кто:**
- `bia_specialist.py` - BIA процесс
- `risk_analyst.py` - Risk assessment
- `project_manager.py` - Проект менеджмент
- `incident_advisor.py` - Инциденты
- `plan_generator.py` - Создание планов
- `compliance_copilot.py` - Compliance guidance
- `exercise_designer.py` - Упражнения

**Для чего:**
- Operational tasks
- Guided workflows (PDCA)
- Conversational interface
- Step-by-step assistance
- Daily operational support

**Характеристики:**
- Узкий фокус (одна задача)
- Тактический уровень (текущие операции)
- Диалоговый интерфейс
- PDCA guided workflow
- Используют: RAG, Tools, могут делегировать к Analyzers
- LLM calls: 1-2 (быстро)

**Пример запроса:**
```
"Help me calculate BIA for payment processing system"
"Guide me through risk assessment for new office"
"Create incident response plan step by step"
```

---

#### ANALYZERS (Тяжелые анализаторы) - 10 анализаторов

**Из:** ai-office/organs/ (переименовано!)

**Почему "Analyzers" вместо "Organs":**
- ✅ Понятнее (анализаторы = делают анализ)
- ✅ Профессиональнее
- ✅ Согласуется с Specialists/Colleagues
- ✅ Отражает назначение (глубокий анализ)

**Кто:**
- `governance_analyzer.py` - Глубокий governance анализ
- `impact_analyzer.py` - Глубокий BIA анализ
- `risk_analyzer.py` - Глубокий risk анализ (FAIR, Monte Carlo)
- `compliance_analyzer.py` - Глубокий compliance анализ
- `emergency_analyzer.py` - Emergency response анализ
- `scenario_analyzer.py` - Scenario generation
- `performance_analyzer.py` - Performance анализ
- `learning_analyzer.py` - Learning effectiveness
- `plan_analyzer.py` - Plan quality анализ
- `lifecycle_analyzer.py` - PDCA lifecycle анализ

**Для чего:**
- Deep AI analysis
- Complex generation (50+ pages documents)
- Heavy LLM processing
- Multi-step reasoning
- Quantitative modeling

**Характеристики:**
- Глубокий анализ
- Долгое выполнение (30-60+ секунд)
- Множественные LLM calls (5-10+)
- Chain of thought reasoning
- Используют: Full LLM power + RAG + ML + Simulation
- LLM calls: 5-10+ (медленно, но глубоко)

**Пример задачи:**
```
"Perform deep FAIR risk analysis with Monte Carlo simulation"
"Generate comprehensive BCM plan (50+ pages) for healthcare"
"Analyze organization's BCM maturity level across all PDCA cycles"
"Create complex crisis scenario with 10+ interdependencies"
```

---

## 🔄 REQUEST FLOW EXAMPLES

### Сценарий 1: Стратегический запрос

```
USER: "How should I structure BCM program for healthcare with ISO 22301 + HIPAA?"
  ↓
API GATEWAY (port 8001)
  ↓
expertise-center/core/chief_executive.py
  - Анализ: domain=bcm, type=strategic, complexity=high
  - Решение: Specialist (bcm_advisor)
  ↓
domains/bcm/specialists/bcm_advisor.py
  async def handle(query, context):
      # 1. Get knowledge (ISO 22301 + HIPAA)
      knowledge = await self.knowledge.get("iso_22301", "hipaa")

      # 2. Search similar cases
      similar = await self.brain.services.rag.search(
          "healthcare BCM program ISO HIPAA"
      )

      # 3. Industry benchmarks
      benchmarks = await self.tools.industry_benchmarks.get("healthcare")

      # 4. LLM strategic analysis (2-3 calls)
      strategy = await self.llm.strategic_plan(
          knowledge, similar, benchmarks, context
      )

      return strategy
  ↓
RESULT:
{
  "strategy": {
    "structure": "3-tier BCM program aligned with ISO 22301",
    "hipaa_integration": "Specific controls for PHI protection",
    "timeline": "18-month implementation roadmap",
    "resources": "Team structure + budget estimates"
  },
  "case_studies": [...],
  "recommendations": [...]
}
```

---

### Сценарий 2: Тактическая задача (простая)

```
USER: "Calculate BIA for payment processing system"
  ↓
API GATEWAY
  ↓
expertise-center/core/chief_executive.py
  - Анализ: domain=bcm, type=tactical, complexity=low
  - Решение: Colleague (bia_specialist)
  ↓
domains/bcm/colleagues/bia_specialist.py
  async def handle(query, context):
      # 1. Guided workflow (PDCA)
      workflow = await self.brain.get_workflow("bia")

      # 2. Search similar BIA
      similar = await self.brain.services.rag.search(
          "BIA payment processing"
      )

      # 3. Use tools (calculations)
      bia_calc = await self.tools.bia_calculator.calculate(context)

      # 4. LLM advice (1 call - fast)
      advice = await self.llm.generate_advice(
          similar, bia_calc, workflow
      )

      return {
          "calculations": bia_calc,
          "advice": advice,
          "next_steps": workflow.get_next_steps()
      }
  ↓
RESULT:
{
  "criticality": "high",
  "mtpd": "4 hours",
  "rto": "2 hours",
  "rpo": "30 minutes",
  "financial_impact": "$500K/day",
  "advice": "Payment processing is critical...",
  "similar_cases": [...],
  "next_steps": ["Analyze dependencies", "Assess impact", ...]
}
```

---

### Сценарий 3: Тактическая задача (сложная - делегирование)

```
USER: "Perform deep FAIR risk analysis with Monte Carlo simulation for ransomware"
  ↓
API GATEWAY
  ↓
expertise-center/core/chief_executive.py
  - Анализ: domain=bcm, type=tactical, complexity=high
  - Решение: Colleague (risk_analyst) → delegation to Analyzer
  ↓
domains/bcm/colleagues/risk_analyst.py
  async def handle(query, context):
      # Colleague понимает: нужен глубокий анализ
      # Делегирует к Analyzer

      analyzer = await self.get_analyzer("risk_analyzer")
      deep_analysis = await analyzer.analyze(query, context)

      # Colleague оборачивает результат для пользователя
      return {
          "summary": self._create_summary(deep_analysis),
          "deep_analysis": deep_analysis,
          "recommendations": self._create_recommendations(deep_analysis)
      }
  ↓
domains/bcm/analyzers/risk_analyzer.py
  async def analyze(query, context):
      # Multi-step deep analysis (10+ LLM calls)

      # Step 1: Threat modeling (LLM call 1)
      threats = await self.llm.identify_threats(query)

      # Step 2: FAIR decomposition (LLM call 2-3)
      fair = await self.llm.fair_decomposition(threats)

      # Step 3: Для каждого threat - анализ (LLM calls 4-8)
      analyses = []
      for threat in threats:
          loss_magnitude = await self.llm.estimate_loss(threat)
          frequency = await self.llm.estimate_frequency(threat)
          analyses.append({threat, loss_magnitude, frequency})

      # Step 4: Monte Carlo simulation (не LLM - Python)
      simulation = await self.simulate_monte_carlo(analyses, iterations=10000)

      # Step 5: Synthesis (LLM call 9)
      synthesis = await self.llm.synthesize(analyses, simulation)

      # Step 6: Recommendations (LLM call 10)
      recommendations = await self.llm.recommend(synthesis)

      return {
          "threats": threats,
          "fair_analysis": fair,
          "analyses": analyses,
          "monte_carlo": simulation,
          "synthesis": synthesis,
          "recommendations": recommendations,
          "confidence": 0.87
      }
  ↓
RESULT:
{
  "summary": "Ransomware risk: High (ALE $2.3M)",
  "deep_analysis": {
    "threats": [...],
    "fair_analysis": {...},
    "monte_carlo": {
      "ale_mean": "$2.3M",
      "ale_p90": "$5.1M",
      "probability_distribution": [...]
    }
  },
  "recommendations": [
    "Implement offline backups",
    "Segmentation of critical systems",
    ...
  ]
}
```

---

## 🎓 NAMING DECISION: Analyzers vs Organs

### Почему "Analyzers"?

**❌ Organs** (старое название):
- Непонятно на русском ("органы"? какие органы?)
- Метафора не очевидна
- Звучит странно в бизнес-контексте

**✅ Analyzers** (новое название):
- ✅ Понятно: "анализаторы" = делают глубокий анализ
- ✅ Профессионально: business-friendly термин
- ✅ Согласуется: Specialists, Colleagues, Analyzers - логичная иерархия
- ✅ Отражает назначение: deep analysis, complex reasoning

**Сравнение терминологии:**

| Уровень | Старое | Новое | Почему лучше |
|---------|--------|-------|--------------|
| Strategic | Specialists | Specialists | ✅ Без изменений |
| Tactical | Colleagues | Colleagues | ✅ Без изменений |
| Heavy AI | **Organs** ❌ | **Analyzers** ✅ | Профессиональнее, понятнее |

---

## 📊 COMPONENT DISTRIBUTION TABLE

| Компонент | Текущее место | Новое место | Категория |
|-----------|---------------|-------------|-----------|
| **RAG** | ai_experts/rag + ai-office/core/rag | workflow_intelligence/services/rag/ | Brain Tool |
| **ML** | ai_experts/ml + community/ml | workflow_intelligence/services/ml/ | Brain Tool |
| **Learning** | ai_experts/learning + ai-office/learning | workflow_intelligence/services/learning/ | Brain Tool |
| **Context** | workflow_intelligence/ai_advisor | workflow_intelligence/services/context/ | Brain Tool |
| **Case Library** | workflow_intelligence/case_library | workflow_intelligence/services/case_library/ | Brain Tool |
| **Journey** | predictive/services | workflow_intelligence/services/journey/ | Brain Tool |
| **Anomaly** | collective/services | workflow_intelligence/services/anomaly/ | Brain Tool |
| **Base Classes** | ai_experts/base + ai-office/base | expertise-center/shared/base/ | Shared |
| **Tools** | ai_experts/tools | expertise-center/shared/tools/ | Shared |
| **LLM Clients** | ai-office/llm | expertise-center/shared/llm/ | Shared |
| **BCM Advisor** | ai_experts/specialists/bcm_advisor | expertise-center/domains/bcm/specialists/ | Specialist |
| **Compliance Auditor** | ai_experts/specialists/compliance_auditor | expertise-center/domains/bcm/specialists/ | Specialist |
| **Strategic Planner** | ai_experts/specialists/strategic_planner | expertise-center/domains/bcm/specialists/ | Specialist |
| **BIA Specialist** | ai-office/ВСМ-colleagues/bia_specialist | expertise-center/domains/bcm/colleagues/ | Colleague |
| **Risk Analyst** | ai-office/ВСМ-colleagues/risk_analyst | expertise-center/domains/bcm/colleagues/ | Colleague |
| **Project Manager** | ai-office/ВСМ-colleagues/project_manager | expertise-center/domains/bcm/colleagues/ | Colleague |
| **Incident Advisor** | ai-office/ВСМ-colleagues/incident_advisor | expertise-center/domains/bcm/colleagues/ | Colleague |
| **Plan Generator** | ai-office/ВСМ-colleagues/plan_generator | expertise-center/domains/bcm/colleagues/ | Colleague |
| **Compliance Copilot** | ai-office/ВСМ-colleagues/compliance_copilot | expertise-center/domains/bcm/colleagues/ | Colleague |
| **Exercise Designer** | ai-office/ВСМ-colleagues/exercise_designer | expertise-center/domains/bcm/colleagues/ | Colleague |
| **Governance Analyzer** | ai-office/organs/governance_brain | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Impact Analyzer** | ai-office/organs/impact_oracle | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Risk Analyzer** | ai-office/organs/risk_advisor | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Compliance Analyzer** | ai-office/organs/compliance_guardian | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Emergency Analyzer** | ai-office/organs/emergency_response | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Scenario Analyzer** | ai-office/organs/scenario_creator | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Performance Analyzer** | ai-office/organs/performance_analyst | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Learning Analyzer** | ai-office/organs/learning_coach | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Plan Analyzer** | ai-office/organs/plan_generator | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Lifecycle Analyzer** | ai-office/organs/lifecycle_monitor | expertise-center/domains/bcm/analyzers/ | Analyzer |
| **Knowledge** | ai_experts/knowledge | expertise-center/domains/bcm/knowledge/ | BCM Domain |

---

## ✅ ПРЕИМУЩЕСТВА UNIFIED ARCHITECTURE

### 1. Best of Both Worlds

**Из Variant 5:**
- ✅ AI Services (RAG, ML, Learning) - инструменты мозга
- ✅ workflow_intelligence = THE BRAIN концепция
- ✅ Sub-packages для независимого импорта
- ✅ Убирает дублирование

**Из CORRECTED_FINAL:**
- ✅ 3-уровневая иерархия AI агентов (strategic, tactical, heavy)
- ✅ Четкое разделение: Specialists, Colleagues, Analyzers
- ✅ expertise-center как plugin manager
- ✅ Логичная группировка по назначению

### 2. Ясная архитектура

**Brain (workflow_intelligence):**
- Core = State machine + Governance
- Services = AI tools (RAG, ML, Learning, etc)

**Expertise (expertise-center):**
- Shared = Base classes + Tools + LLM
- Domains = BCM (specialists + colleagues + analyzers)

**Services (platform-services):**
- Business logic + Database + REST API

### 3. Понятный naming

- **Specialists** = Strategic (3) - стратегия, политики, долгосрочное планирование
- **Colleagues** = Tactical (7-10) - операционные задачи, диалог, PDCA workflows
- **Analyzers** = Heavy AI (10) - глубокий анализ, генерация, моделирование

### 4. Scalability

```python
# Легко добавить новый домен
class HRDomain(BaseDomain):
    def get_specialists(self):
        return [HRStrategicAdvisor, TalentStrategist]

    def get_colleagues(self):
        return [RecruitmentAssistant, OnboardingGuide]

    def get_analyzers(self):
        return [TalentAnalyzer, CultureAnalyzer]
```

---

## 🚀 MIGRATION PLAN

### Phase 1: Создать структуру (4-6 часов)

```bash
# 1. workflow_intelligence/services
mkdir -p intelligent-core/workflow_intelligence/services/{rag,ml,learning,context,case_library,journey,anomaly}

# 2. expertise-center
mkdir -p intelligent-core/expertise-center/{core,shared,domains}
mkdir -p intelligent-core/expertise-center/shared/{base,tools,llm}
mkdir -p intelligent-core/expertise-center/domains/bcm/{specialists,colleagues,analyzers,knowledge}
```

### Phase 2: Копировать код (4-6 часов)

```bash
# AI services → workflow_intelligence/services/
cp -r intelligent-core/ai_experts/rag/* intelligent-core/workflow_intelligence/services/rag/
cp -r intelligent-core/ai_experts/ml/* intelligent-core/workflow_intelligence/services/ml/
cp -r intelligent-core/ai_experts/learning/* intelligent-core/workflow_intelligence/services/learning/

# Base classes → expertise-center/shared/
cp -r intelligent-core/ai_experts/base/* intelligent-core/expertise-center/shared/base/
cp -r intelligent-core/ai-office/base/* intelligent-core/expertise-center/shared/base/

# Tools → expertise-center/shared/tools/
cp -r intelligent-core/ai_experts/tools/* intelligent-core/expertise-center/shared/tools/

# LLM → expertise-center/shared/llm/
cp -r intelligent-core/ai-office/llm/* intelligent-core/expertise-center/shared/llm/

# Specialists (3) → expertise-center/domains/bcm/specialists/
cp intelligent-core/ai_experts/specialists/* intelligent-core/expertise-center/domains/bcm/specialists/

# Colleagues (7) → expertise-center/domains/bcm/colleagues/
cp -r intelligent-core/ai-office/ВСМ-colleagues/* intelligent-core/expertise-center/domains/bcm/colleagues/

# Analyzers (10) → expertise-center/domains/bcm/analyzers/
cp intelligent-core/ai-office/organs/* intelligent-core/expertise-center/domains/bcm/analyzers/

# Knowledge → expertise-center/domains/bcm/knowledge/
cp -r intelligent-core/ai_experts/knowledge/* intelligent-core/expertise-center/domains/bcm/knowledge/
```

### Phase 3: Создать __init__.py (2 часа)

```bash
# Create all __init__.py files with proper exports
# (см. примеры выше в technical details)
```

### Phase 4: Обновить импорты (2-3 часа)

**6 файлов для обновления** (минимальные breaking changes):

1. `bcm_offices/risk/ai/expert.py` (2 строки)
2. `predictive/integration/dependencies.py` (1 строка)
3. `collective/services/case_library.py` (1 блок - уже готов к failure)

### Phase 5: Тестирование (2-3 часа)

```bash
# Test brain services
pytest intelligent-core/workflow_intelligence/tests/

# Test expertise center
pytest intelligent-core/expertise-center/tests/

# Test platform services
pytest platform-services/*/tests/
```

### Phase 6: Архивирование (1 час)

```bash
mv intelligent-core/ai_experts _archive/ai_experts
mv intelligent-core/ai-office _archive/ai-office
```

**TOTAL TIME: 15-21 часов (~2-3 рабочих дня)**

---

## 📊 SUMMARY

**Что объединили:**
1. ✅ AI Services в workflow_intelligence/services/ (из Variant 5)
2. ✅ 3-уровневая иерархия AI агентов (из CORRECTED_FINAL)
3. ✅ Analyzers вместо Organs (улучшенный naming)
4. ✅ expertise-center как plugin manager (из обоих)

**Что получили:**
- Единая согласованная архитектура
- Понятная структура для всех
- Минимальные breaking changes
- Готовность к масштабированию

**Breaking changes:**
- 6 строк кода в 4 файлах

**LOC removed:**
- ~6,000 LOC дублирующегося кода

**Timeline:**
- 2-3 рабочих дня (15-21 час)

---

**Версия**: 6.0 Unified Final
**Статус**: ✅ Ready for Implementation
**Согласовано**: Объединяет Variant 5 + CORRECTED_FINAL_ARCHITECTURE
**Следующий шаг**: Начать миграцию?
