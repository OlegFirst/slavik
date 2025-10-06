# 🏗️ COMPLETE PLATFORM ARCHITECTURE

**AI-Powered BCM Platform - Full Architecture Map**

**Date:** 2025-10-05
**Version:** 3.0 (Complete)
**Status:** ✅ All Components Mapped

---

## 🎯 Executive Summary

Platform architecture with **4 clear layers** + **1 brain module** that defines all rules.

**Key Insight:**
- `workflow_intelligence` = **THE BRAIN** defining rules for entire platform
- Other modules work **WITHIN** those rules
- Domain plugins (BCM, HR, Finance) are **swappable** while keeping system functional

---

## 📊 4-Layer Architecture + Brain

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW INTELLIGENCE                     │
│          🧠 THE BRAIN - Defines Rules for Everyone          │
│                                                              │
│  • State Machine (workflow rules)                           │
│  • Case Library (learned patterns)                          │
│  • AI Advisor (context intelligence)                        │
│  • Governance (checkpoints vs creative zones)               │
│  • ML Predictor (success prediction)                        │
│                                                              │
│  Philosophy: "Managed Autonomy"                             │
│  - Strict rules at checkpoints                              │
│  - AI freedom in creative zones                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    (All layers follow brain rules)
                              ↓

┌─────────────────────────────────────────────────────────────┐
│ LAYER 0: INFRASTRUCTURE (Руки + Транспорт)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  coordination-center/          AI Orchestrator's hands      │
│  ├─ intent_parser.py           - Intent → API translator    │
│  ├─ api_executor.py            - Executes actions          │
│  ├─ security_layer.py          - Auth, RLS, audit          │
│  └─ rollback_manager.py        - Transaction safety        │
│                                                              │
│  /infrastructure/              Platform services            │
│  ├─ database/                  PostgreSQL + Redis           │
│  ├─ eventbus/                  Event streaming             │
│  ├─ auth/                      Authentication              │
│  ├─ observability/             Monitoring                  │
│  └─ message-queue/             RabbitMQ/Redis              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: PLATFORM CORE (Domain-Agnostic Systems)           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /platform-core/                                            │
│                                                              │
│  workflow/                     Unified Workflow Engine v2.0 │
│  ├─ bpmn_executor.py           - BPMN 2.0 orchestration    │
│  ├─ workflow_engine.py         - State management          │
│  ├─ iso22301_integration.py   - ISO standards             │
│  └─ ai_recommendations.py      - AI-powered suggestions    │
│     Status: ✅ Production (4,040 lines)                     │
│                                                              │
│  case-library/                 Self-Learning Repository     │
│  ├─ collector.py               - Collects successful cases │
│  ├─ repository.py              - Stores patterns           │
│  ├─ analyzer.py                - Extracts insights         │
│  └─ benchmarks.py              - Performance tracking      │
│                                                              │
│  learning-system/              Platform-Wide Learning       │
│  ├─ pattern_detector.py        - Detects patterns          │
│  ├─ competency_tracker.py      - Tracks skills            │
│  ├─ rule_generator.py          - Creates new rules         │
│  └─ gamification.py            - User engagement           │
│                                                              │
│  community_intelligence/       Peer Review & Knowledge      │
│  ├─ workflow_integration.py    - Workflow hooks            │
│  ├─ peer_review.py             - Expert validation         │
│  ├─ reputation.py              - Quality scoring           │
│  └─ case_library_sync.py       - Shares learnings         │
│                                                              │
│  collective/                   Anonymous Collective Wisdom  │
│  ├─ privacy_preserving.py      - Partisia Blockchain       │
│  ├─ aggregation.py             - Anonymous insights        │
│  └─ cross_org_learning.py      - Multi-org patterns        │
│                                                              │
│  digital_twin/                 BCM Digital Twin             │
│  ├─ queue_theory.py            - M/M/c simulation          │
│  ├─ ai_scenario_gen.py         - LLM scenarios             │
│  ├─ monte_carlo.py             - Risk simulation           │
│  └─ impact_passport.py         - BIA analysis              │
│     Status: ✅ Production (8 engines, 150+ tests)          │
│                                                              │
│  living-docs/                  Self-Evolving Documentation  │
│  ├─ doc_updater.py             - Auto-updates docs         │
│  ├─ knowledge_graph.py         - Semantic linking          │
│  └─ version_tracker.py         - Change tracking           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: AI INTELLIGENCE (AI Orchestration)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /ai-orchestration/            AI Orchestrator              │
│  ├─ orchestrator.py            - Main decision engine       │
│  ├─ decision_center/           - Context + Priority        │
│  │   ├─ context_aggregator.py  - Collects full context    │
│  │   ├─ priority_engine.py     - Assesses priority         │
│  │   ├─ strategy_selector.py   - Selects strategy          │
│  │   └─ delegation_manager.py  - Delegates tasks           │
│  │                                                           │
│  ├─ distributed_memory/        4-Layer Memory System        │
│  │   ├─ working_memory.py      - Redis (1 hour TTL)       │
│  │   ├─ short_term.py          - PostgreSQL (30 days)     │
│  │   ├─ long_term.py           - Case Library (permanent) │
│  │   └─ procedural.py          - ML Models (patterns)     │
│  │                                                           │
│  ├─ safety_monitor/            Safety-First Architecture    │
│  │   ├─ constitution.py        - Immutable rules           │
│  │   ├─ loop_detector.py       - Infinite loop prevention │
│  │   ├─ hallucination_detect.py - AI hallucination check  │
│  │   └─ control_monitor.py     - Loss of control prevention│
│  │                                                           │
│  └─ evolution_engine/          Self-Evolution (3 levels)    │
│      ├─ data_evolution.py      - Daily (automatic)         │
│      ├─ model_evolution.py     - Weekly (automatic)        │
│      └─ code_evolution.py      - Monthly (human review)    │
│                                                              │
│  /expertise-center/            Domain Expertise Manager     │
│  ├─ core/                                                   │
│  │   ├─ chief_executive.py     - Main AI orchestrator     │
│  │   ├─ domain_loader.py       - Plugin loader            │
│  │   └─ expert_registry.py     - Expert registry          │
│  │                                                           │
│  ├─ shared/                    AI Infrastructure (ALL)     │
│  │   ├─ rag/                   - RAG pipeline             │
│  │   │   ├─ hybrid_search.py   - Semantic + keyword       │
│  │   │   ├─ reranker.py        - Result re-ranking        │
│  │   │   └─ context_builder.py - Context assembly         │
│  │   │                                                      │
│  │   ├─ ml/                    - ML Models                │
│  │   │   ├─ random_forest.py   - Classification           │
│  │   │   ├─ gradient_boost.py  - Prediction               │
│  │   │   └─ anomaly_detect.py  - Outlier detection        │
│  │   │                                                      │
│  │   └─ learning/              - Self-learning             │
│  │       ├─ pattern_extract.py - Extract patterns          │
│  │       ├─ rule_generation.py - Generate rules            │
│  │       └─ improvement.py     - Continuous improvement    │
│  │                                                           │
│  └─ domains/                   🔌 DOMAIN PLUGINS           │
│      └─ bcm/                   (See Layer 3)               │
│                                                              │
│  /predictive/                  Journey Prediction           │
│  ├─ journey_predictor.py       - Predicts next 90 days    │
│  ├─ timeline_generator.py      - Creates timelines        │
│  └─ risk_forecaster.py         - Risk prediction          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: DOMAIN PLUGINS (Business Logic)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /expertise-center/domains/bcm/    BCM Plugin              │
│                                                              │
│  experts/                      BCM Experts (10)             │
│  ├─ bia_specialist.py          - BIA analysis              │
│  ├─ risk_analyst.py            - Risk management           │
│  ├─ planning_specialist.py     - Planning expert           │
│  ├─ incident_expert.py         - Incident management       │
│  ├─ exercise_designer.py       - Exercise planning         │
│  ├─ supply_chain_expert.py     - Supply chain             │
│  ├─ collective_expert.py       - Collective intelligence   │
│  ├─ documentation_expert.py    - Doc management            │
│  ├─ knowledge_manager.py       - Knowledge base            │
│  └─ predictive_analyst.py      - Predictive analysis       │
│                                                              │
│  tools/                        BCM Tools (~10)              │
│  ├─ bia_tool.py                - BIA calculations          │
│  ├─ dependency_mapper.py       - Dependency graphs         │
│  ├─ risk_assessment.py         - Risk scoring              │
│  ├─ mtpd_calculator.py         - MTPD/RTO calculations    │
│  └─ compliance_checker.py      - ISO 22301 validation     │
│                                                              │
│  organs/                       BCM Organs (Heavy AI)        │
│  ├─ bia_analyzer.py            - Deep BIA analysis         │
│  ├─ risk_modeler.py            - Risk modeling             │
│  ├─ plan_generator.py          - Plan generation           │
│  └─ exercise_simulator.py      - Exercise simulation       │
│                                                              │
│  knowledge/                    BCM Knowledge                │
│  ├─ iso_22301/                 - ISO 22301 standards       │
│  ├─ best_practices/            - Industry practices        │
│  └─ templates/                 - BCM templates             │
│                                                              │
│  services_config.py            Service Metadata Only        │
│  └─ BCM_SERVICES = {           (NOT actual service code)   │
│        "bia-service": {                                     │
│          "endpoint": "/api/bcm/bia",                        │
│          "experts": ["bia_specialist"],                     │
│        }                                                     │
│      }                                                       │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 🔌 PLUGIN INTERFACE                                   │ │
│  │                                                        │ │
│  │ class BCMDomain(BaseDomain):                          │ │
│  │     name = "bcm"                                       │ │
│  │     version = "1.0.0"                                  │ │
│  │                                                        │ │
│  │     def register(self, platform):                      │ │
│  │         """Platform injects shared services"""         │ │
│  │         self.rag = platform.get_rag()                  │ │
│  │         self.ml = platform.get_ml()                    │ │
│  │         self.learning = platform.get_learning()        │ │
│  │                                                        │ │
│  │     def get_experts(self):                             │ │
│  │         """Return BCM experts"""                       │ │
│  │         return [BIASpecialist, RiskAnalyst, ...]       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ACTUAL SERVICE IMPLEMENTATIONS                              │
│ (Stay in /platform-services/ - NOT moved!)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /platform-services/                                        │
│  ├─ bia-service/               BIA Service                  │
│  ├─ risk-service/              Risk Service                 │
│  ├─ planning-service/          Planning Service             │
│  ├─ incident-service/          Incident Service             │
│  └─ exercise-service/          Exercise Service             │
│                                                              │
│  These services:                                            │
│  ✅ Stay where they are                                     │
│  ✅ Independent deployment                                  │
│  ✅ Can be used by ANY domain plugin                        │
│  ✅ Domain only registers metadata (services_config.py)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 THE BRAIN: workflow_intelligence

**Location:** `/intelligent-core/workflow_intelligence/`

**Role:** Defines rules for ENTIRE platform - everyone works within these rules

### Components

```
workflow_intelligence/
├─ core/
│  ├─ workflow_engine.py        State machine executor
│  ├─ state_machine.py          State definitions
│  ├─ transitions.py            State transitions
│  └─ validators.py             Validation logic

├─ case_library/
│  ├─ collector.py              Collect successful workflows
│  ├─ repository.py             Store cases
│  ├─ analyzer.py               Extract patterns
│  └─ benchmarks.py             Performance metrics

├─ ai_advisor/
│  ├─ context_advisor.py        Context-aware intelligence
│  ├─ prompt_builder.py         Dynamic prompts
│  └─ recommendation_engine.py  AI suggestions

├─ governance/
│  ├─ rules_engine.py           Rule enforcement
│  ├─ safety_rails.py           Safety boundaries
│  ├─ creative_zones.py         AI freedom zones
│  └─ checkpoints.py            Mandatory validations

└─ ml/
   ├─ workflow_predictor.py     Success probability
   ├─ risk_detector.py          Risk identification
   └─ pattern_recognizer.py     Pattern detection
```

### Philosophy: Managed Autonomy

**Checkpoints (Strict Rules):**
- Data validation MUST pass
- Security checks CANNOT be bypassed
- Compliance rules are MANDATORY
- User permissions are ENFORCED

**Creative Zones (AI Freedom):**
- Generate recommendations
- Suggest optimizations
- Predict outcomes
- Learn from patterns

### How Others Use It

```python
# BCM Expert uses workflow intelligence rules
from workflow_intelligence import WorkflowEngine, Governance

class BIASpecialist(BaseExpert):
    async def handle_request(self, query, context):
        # 1. Check governance rules (defined by brain)
        if not Governance.is_allowed("bia_analysis", context):
            return {"error": "Not allowed by governance"}

        # 2. Use workflow engine (brain's state machine)
        workflow = await WorkflowEngine.get_workflow("bia", context)

        # 3. Work within creative zone
        ai_analysis = await self._analyze_with_ai(query)

        # 4. Validate at checkpoint (brain's rules)
        if not workflow.validate_checkpoint("analysis_complete"):
            return {"error": "Checkpoint validation failed"}

        return ai_analysis
```

---

## 🔄 Complete Request Flow

### Example: "Calculate BIA for payment processing"

```
1. USER REQUEST
   ↓
   "Calculate BIA for payment processing"

2. LAYER 0: coordination-center
   ↓
   • Parse intent: {"action": "calculate_bia", "target": "payment_processing"}
   • Check security: User has permission?
   • Prepare context

3. WORKFLOW INTELLIGENCE (THE BRAIN)
   ↓
   • Check governance: BIA analysis allowed?
   • Load workflow rules: "bia_analysis" workflow
   • Identify checkpoints: [validation, approval, documentation]
   • Identify creative zones: [data_collection, analysis, recommendations]

4. LAYER 2: expertise-center/chief_executive
   ↓
   • Analyze query: domain="bcm", expertise="bia"
   • Get expert: BCM BIA Specialist
   • Load shared tools: RAG, ML, Learning

5. LAYER 3: domains/bcm/experts/bia_specialist
   ↓
   • Use BIA Tool (structured calculation)
   • Use RAG (find similar cases from case library)
   • Use ML (predict criticality)
   • Delegate to BIA Organ (deep LLM analysis)

6. LAYER 1: platform-core services
   ↓
   • Case Library: Find similar BIA cases
   • Digital Twin: Run M/M/c queue simulation
   • Learning System: Record this analysis for future
   • Community Intelligence: Share anonymized insights

7. WORKFLOW INTELLIGENCE (CHECKPOINTS)
   ↓
   • Checkpoint 1: Data validation ✅
   • Creative Zone: AI generates insights
   • Checkpoint 2: Compliance check ✅
   • Creative Zone: Recommendations
   • Checkpoint 3: Human approval ✅

8. LAYER 2: ai-orchestration (safety validation)
   ↓
   • Constitution check: Rules followed? ✅
   • Loop detection: Not infinite loop? ✅
   • Hallucination check: Data is real? ✅
   • Control monitor: Within scope? ✅

9. LAYER 0: coordination-center
   ↓
   • Execute API calls to platform-services/bia-service
   • Log to audit trail
   • Return result to user

10. RESULT
    ↓
    {
      "success": true,
      "bia_analysis": {...},
      "criticality": "high",
      "mtpd": "4 hours",
      "confidence": 0.92,
      "recommendations": [...],
      "case_stored": true
    }
```

---

## 🎯 Two Request Paths

### Fast Path (2 hops) - Simple CRUD

```
User → coordination-center → platform-services
      (Layer 0)              (Services)

Example: "Get BIA record #123"
- No AI needed
- Direct database query
- Fast response
```

### Smart Path (4 hops) - AI Reasoning

```
User → coordination-center → expertise-center → domain expert → platform-services
      (Layer 0)              (Layer 2)          (Layer 3)       (Services)

Example: "Calculate BIA for payment processing"
- Needs AI reasoning
- Uses workflow intelligence rules
- Learns from experience
- Full orchestration
```

**Auto-detection:**
```python
class ChiefExecutiveAI:
    def _is_simple_crud(self, query):
        crud_keywords = ["get", "list", "show", "retrieve", "fetch"]
        return any(kw in query.lower() for kw in crud_keywords)

    async def handle_request(self, query, context):
        if self._is_simple_crud(query):
            return await self._fast_path(query, context)
        else:
            return await self._smart_path(query, context)
```

---

## 🔌 Plugin Architecture

### How BCM Works as Plugin

**1. Domain Registration:**
```python
# expertise-center/domains/bcm/__init__.py

from expertise_center.shared.base import BaseDomain

class BCMDomain(BaseDomain):
    name = "bcm"
    version = "1.0.0"
    description = "Business Continuity Management"

    def register(self, platform):
        """Platform injects shared services"""
        self.rag = platform.get_rag()
        self.ml = platform.get_ml()
        self.learning = platform.get_learning()
        self.workflow_intelligence = platform.get_workflow_intelligence()

    def get_experts(self):
        """Return BCM experts"""
        from .experts import (
            BIASpecialist, RiskAnalyst, PlanningSpecialist,
            IncidentExpert, ExerciseDesigner, SupplyChainExpert,
            CollectiveExpert, DocumentationExpert, KnowledgeManager,
            PredictiveAnalyst
        )
        return [
            BIASpecialist, RiskAnalyst, PlanningSpecialist,
            IncidentExpert, ExerciseDesigner, SupplyChainExpert,
            CollectiveExpert, DocumentationExpert, KnowledgeManager,
            PredictiveAnalyst
        ]

    def get_tools(self):
        """Return BCM tools"""
        from .tools import (
            BIATool, DependencyMapper, RiskAssessment,
            MTPDCalculator, ComplianceChecker
        )
        return [
            BIATool, DependencyMapper, RiskAssessment,
            MTPDCalculator, ComplianceChecker
        ]

    def get_organs(self):
        """Return BCM organs (heavy AI)"""
        from .organs import (
            BIAAnalyzer, RiskModeler, PlanGenerator, ExerciseSimulator
        )
        return [
            BIAAnalyzer, RiskModeler, PlanGenerator, ExerciseSimulator
        ]

    def get_services_metadata(self):
        """Return service metadata (NOT actual code)"""
        from .services_config import BCM_SERVICES
        return BCM_SERVICES
```

**2. Platform Loads Plugin:**
```python
# expertise-center/core/domain_loader.py

class DomainLoader:
    def load_domain(self, domain_name: str):
        """Load domain plugin"""
        # Import domain
        domain_module = importlib.import_module(f"expertise_center.domains.{domain_name}")
        domain_class = domain_module.get_domain_class()

        # Instantiate
        domain = domain_class()

        # Inject platform services
        domain.register(platform=self.platform)

        # Register experts
        for expert_class in domain.get_experts():
            self.registry.register_expert(
                domain=domain_name,
                expertise=expert_class.__name__,
                expert_class=expert_class,
                capabilities=expert_class.capabilities,
                tools=expert_class.tools
            )

        return domain
```

**3. Expert Uses Platform Services:**
```python
# expertise-center/domains/bcm/experts/bia_specialist.py

class BIASpecialist:
    capabilities = ["business_impact_analysis", "criticality_assessment"]
    tools = ["BIATool", "DependencyMapper"]

    def __init__(self, platform_services):
        # Injected by platform
        self.rag = platform_services.rag
        self.ml = platform_services.ml
        self.learning = platform_services.learning
        self.workflow_intelligence = platform_services.workflow_intelligence

    async def handle(self, query, context):
        # 1. Check workflow rules (from brain)
        workflow = await self.workflow_intelligence.get_workflow("bia", context)

        # 2. Use RAG to find similar cases
        similar_cases = await self.rag.search(query, top_k=5)

        # 3. Use ML to predict criticality
        criticality = await self.ml.predict("criticality", context)

        # 4. Perform BIA analysis
        bia_result = await self._analyze_bia(query, context, similar_cases, criticality)

        # 5. Store in learning system
        await self.learning.record_case({
            "query": query,
            "result": bia_result,
            "success": True
        })

        # 6. Return result
        return bia_result
```

---

## 🚀 Adding New Domain (Example: HR)

**1. Create domain structure:**
```bash
mkdir -p expertise-center/domains/hr/{experts,tools,organs,knowledge}
```

**2. Create domain class:**
```python
# expertise-center/domains/hr/__init__.py

class HRDomain(BaseDomain):
    name = "hr"
    version = "1.0.0"
    description = "Human Resources Management"

    def get_experts(self):
        from .experts import RecruitmentSpecialist, TrainingManager
        return [RecruitmentSpecialist, TrainingManager]

    def get_services_metadata(self):
        return {
            "recruitment-service": {
                "endpoint": "/api/hr/recruitment",
                "experts": ["recruitment_specialist"]
            }
        }
```

**3. Create expert:**
```python
# expertise-center/domains/hr/experts/recruitment_specialist.py

class RecruitmentSpecialist:
    capabilities = ["candidate_screening", "interview_scheduling"]

    async def handle(self, query, context):
        # Uses same platform services (RAG, ML, Learning)
        # Uses same workflow intelligence rules
        # But HR-specific logic
        return {"success": True}
```

**4. Load domain:**
```python
# Platform automatically loads
domain_loader.load_domain("hr")

# Now available:
# - hr.recruitment_specialist
# - hr.training_manager
```

**Benefits:**
- ✅ BCM code untouched
- ✅ Same platform services
- ✅ Same workflow rules
- ✅ Independent domain logic

---

## 📊 Key Architectural Decisions

### ✅ Decision 1: Services Stay in /platform-services/

**Rationale:**
- Independent deployment
- Docker compose unchanged
- Can be used by multiple domains
- Domain only registers metadata

### ✅ Decision 2: workflow_intelligence is THE BRAIN

**Rationale:**
- Defines rules for ALL domains
- Everyone works within these rules
- Managed autonomy (strict checkpoints + creative zones)
- Self-learning from all domain experiences

### ✅ Decision 3: ai-orchestration for Safety

**Rationale:**
- 4-layer memory system (working, short-term, long-term, procedural)
- Safety-first (constitution, loops, hallucinations, control)
- Self-evolution (data, model, code)
- Decision-making with context aggregation

### ✅ Decision 4: expertise-center as Plugin Manager

**Rationale:**
- Domain plugins are swappable
- Shared AI infrastructure (RAG, ML, Learning)
- Auto-discovery of experts
- Central registry

### ✅ Decision 5: 2 Paths (Fast + Smart)

**Rationale:**
- Simple CRUD doesn't need AI overhead (2 hops)
- Complex reasoning uses full stack (4 hops)
- Auto-detection based on query
- Performance optimization

---

## 🎯 Integration Points

### workflow_intelligence ↔ All Layers

```python
# Layer 0 (coordination-center) checks workflow rules
await workflow_intelligence.check_governance(action, context)

# Layer 1 (platform-core) uses workflow engine
workflow = await workflow_intelligence.get_workflow(module, context)

# Layer 2 (expertise-center) follows workflow rules
is_allowed = await workflow_intelligence.validate_checkpoint(step)

# Layer 3 (domain experts) work in creative zones
zone = await workflow_intelligence.get_creative_zone(task)
```

### ai-orchestration ↔ All Decisions

```python
# All AI decisions go through orchestrator
decision = await orchestrator.decide(situation, tenant_id)

# Safety validation
if not decision.safety_approved:
    return {"error": "Safety validation failed"}

# Execution
result = await orchestrator.execute(decision)

# Learning
await orchestrator.memory.store(decision, result)
```

### expertise-center ↔ Domains

```python
# Load domain
domain = loader.load_domain("bcm")

# Get expert
expert_class = registry.get_expert("bcm", "bia")

# Instantiate with platform services
expert = expert_class(platform_services={
    "rag": shared_rag,
    "ml": shared_ml,
    "learning": shared_learning,
    "workflow_intelligence": workflow_intelligence
})

# Handle request
result = await expert.handle(query, context)
```

---

## 📁 Complete Directory Structure

```
AI-Platform-ISO/
├─ infrastructure/                      Layer 0: Infrastructure
│  ├─ database/                         PostgreSQL + migrations
│  ├─ eventbus/                         Event streaming
│  ├─ auth/                             Authentication
│  ├─ observability/                    Monitoring
│  └─ message-queue/                    RabbitMQ/Redis
│
├─ intelligent-core/                    Core Intelligence
│  │
│  ├─ workflow_intelligence/            🧠 THE BRAIN (Rules Engine)
│  │  ├─ core/                          State machine + workflows
│  │  ├─ case_library/                  Self-learning repository
│  │  ├─ ai_advisor/                    Context-aware AI
│  │  ├─ governance/                    Checkpoints + creative zones
│  │  └─ ml/                            Workflow prediction
│  │
│  ├─ coordination-center/              Layer 0: Executor
│  │  ├─ intent_parser.py               Intent → API translator
│  │  ├─ api_executor.py                Executes actions
│  │  └─ security_layer.py              Auth, RLS, audit
│  │
│  ├─ platform-core/                    Layer 1: Domain-Agnostic
│  │  ├─ workflow/                      Unified Workflow v2.0
│  │  ├─ case-library/                  Case repository
│  │  ├─ learning-system/               Platform learning
│  │  ├─ community_intelligence/        Peer review
│  │  ├─ collective/                    Anonymous wisdom
│  │  ├─ digital_twin/                  BCM twin
│  │  └─ living-docs/                   Self-evolving docs
│  │
│  ├─ ai-orchestration/                 Layer 2: AI Orchestrator
│  │  ├─ orchestrator.py                Main decision engine
│  │  ├─ decision_center/               Context + Priority
│  │  ├─ distributed_memory/            4-layer memory
│  │  ├─ safety_monitor/                Safety-first
│  │  └─ evolution_engine/              Self-evolution
│  │
│  ├─ expertise-center/                 Layer 2: Domain Plugins
│  │  ├─ core/
│  │  │  ├─ chief_executive.py          AI orchestrator
│  │  │  ├─ domain_loader.py            Plugin loader
│  │  │  └─ expert_registry.py          Expert registry
│  │  │
│  │  ├─ shared/                        AI Infrastructure
│  │  │  ├─ rag/                        RAG pipeline
│  │  │  ├─ ml/                         ML models
│  │  │  └─ learning/                   Self-learning
│  │  │
│  │  └─ domains/                       🔌 PLUGINS
│  │      └─ bcm/                       BCM Plugin (Layer 3)
│  │          ├─ experts/               10 BCM experts
│  │          ├─ tools/                 BCM tools
│  │          ├─ organs/                Heavy AI analyzers
│  │          ├─ knowledge/             ISO 22301, templates
│  │          └─ services_config.py     Metadata only
│  │
│  ├─ predictive/                       Journey prediction
│  │
│  └─ ai_platform/                      DEPRECATED (reference only)
│
└─ platform-services/                   Actual Service Code
   ├─ bia-service/                      BIA calculations
   ├─ risk-service/                     Risk management
   ├─ planning-service/                 Planning
   ├─ incident-service/                 Incidents
   └─ exercise-service/                 Exercises
      (These stay here - independent deployment)
```

---

## 🎓 Understanding the Architecture

### Key Concepts

**1. The Brain (workflow_intelligence)**
- Defines rules for EVERYONE
- Managed autonomy philosophy
- Self-learning case library
- Checkpoints (strict) vs Creative Zones (freedom)

**2. The Orchestrator (ai-orchestration)**
- Makes decisions with full context
- 4-layer memory system
- Safety-first architecture
- Self-evolution capabilities

**3. The Plugin System (expertise-center)**
- Domain plugins are swappable
- Shared AI infrastructure (RAG, ML, Learning)
- Auto-discovery and registration
- Platform injects services

**4. The Services (platform-services)**
- Stay where they are
- Independent deployment
- Domain-agnostic implementation
- Metadata registered by domain plugins

### How It All Works Together

```
User: "Calculate BIA for payment processing"
  ↓
coordination-center: Parse intent, check security
  ↓
workflow_intelligence: Check governance, load workflow rules
  ↓
expertise-center/chief: Analyze query → domain="bcm", expertise="bia"
  ↓
expertise-center/registry: Get BIASpecialist expert
  ↓
domains/bcm/bia_specialist:
  - Use workflow rules (from brain)
  - Use RAG (shared)
  - Use ML (shared)
  - Use BIA Tool (BCM-specific)
  - Delegate to BIA Organ (heavy AI)
  ↓
platform-core services:
  - Case Library: Find similar cases
  - Digital Twin: Run simulation
  - Learning System: Record this case
  ↓
workflow_intelligence: Validate checkpoints
  ↓
ai-orchestration: Safety validation
  ↓
coordination-center: Execute API calls, audit trail
  ↓
Result to user
```

---

## ✅ Migration Path

### From Current State to This Architecture

**Phase 1: Foundation (Week 1)**
- ✅ workflow_intelligence already exists (THE BRAIN)
- ✅ platform-core created
- ✅ expertise-center created
- ✅ ai-orchestration already exists

**Phase 2: Move BCM to Plugin (Week 2)**
- Move `/intelligent-core/ai-office/` → `/expertise-center/domains/bcm/`
- Split colleagues → experts, organs → organs
- Create `services_config.py` (metadata)
- Keep services in `/platform-services/` (NO move)

**Phase 3: Integration (Week 3)**
- Connect expertise-center with workflow_intelligence
- Connect ai-orchestration with all layers
- Implement 2-path system (fast + smart)
- Test full flow end-to-end

**Phase 4: Verification (Week 4)**
- Test BCM plugin works
- Test domain swappability (add HR test domain)
- Performance testing (2-hop vs 4-hop)
- Documentation complete

---

## 📊 Metrics & Monitoring

### System Metrics

```python
# Get full platform status
status = await platform.get_status()

{
  "workflow_intelligence": {
    "total_workflows": 1247,
    "active_workflows": 89,
    "case_library_size": 3421,
    "learning_patterns": 156
  },
  "ai_orchestration": {
    "total_decisions": 8934,
    "safety_blocks": 12,
    "avg_confidence": 0.87,
    "memory_usage": {
      "working": "512MB",
      "short_term": "2.3GB",
      "long_term": "45GB",
      "procedural": "890MB"
    }
  },
  "expertise_center": {
    "loaded_domains": ["bcm"],
    "total_experts": 10,
    "total_requests": 5621,
    "avg_response_time": "1.2s"
  },
  "platform_services": {
    "bia_service": {"status": "healthy", "uptime": "99.9%"},
    "risk_service": {"status": "healthy", "uptime": "99.8%"}
  }
}
```

---

## 🎯 Summary

### What Makes This Architecture Special

1. **Brain-First:** workflow_intelligence defines rules, everyone follows
2. **Safety-First:** ai-orchestration ensures no runaway AI
3. **Plugin Architecture:** Domains are swappable, platform is stable
4. **Managed Autonomy:** Strict checkpoints + AI creative zones
5. **Self-Learning:** Case library + learning system + evolution engine
6. **Performance:** 2 paths (fast CRUD, smart AI)
7. **Clean Separation:** 4 layers with clear responsibilities

### Key Files

| Component | Location | Role |
|-----------|----------|------|
| **THE BRAIN** | `/intelligent-core/workflow_intelligence/` | Rules engine |
| **Orchestrator** | `/intelligent-core/ai-orchestration/` | AI decision maker |
| **Plugin Manager** | `/intelligent-core/expertise-center/` | Domain loader |
| **BCM Plugin** | `/expertise-center/domains/bcm/` | BCM business logic |
| **Platform Core** | `/intelligent-core/platform-core/` | Domain-agnostic |
| **Services** | `/platform-services/` | Actual implementations |

---

**Version:** 3.0 (Complete)
**Date:** 2025-10-05
**Status:** ✅ All Components Mapped
**Next:** Implementation Plan
