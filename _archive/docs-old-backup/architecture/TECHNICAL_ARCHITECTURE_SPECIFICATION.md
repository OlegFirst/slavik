# 🏗️ Technical Architecture Specification
## AI-Powered BCM Platform - intelligent-core

**Version**: 2.0
**Date**: 2025-10-07
**Status**: Production Architecture
**Classification**: Technical Specification

---

## 📋 Document Information

### Purpose
Definitive technical specification for the intelligent-core layer of the AI-Powered BCM Platform, defining architecture, components, interfaces, and integration patterns for all 9 production modules.

### Audience
- Software Architects
- Backend Engineers
- DevOps Engineers
- QA Engineers
- Technical Leads

### Related Documents
- [Testing Specification](TESTING_SPECIFICATION.md)
- [API Documentation](api/)
- [Deployment Guide](deployment/)
- [Strategic Concept](STRATEGIC_PROJECT_CONCEPT.md)

---

## 🎯 Executive Summary

### System Overview
The **intelligent-core** is the AI intelligence layer of the BCM Platform, providing:
- Workflow orchestration and state management
- AI/ML infrastructure (RAG, LLM, ML models)
- Domain expertise (26 specialized AI agents)
- Autonomous decision-making and orchestration
- Community-driven knowledge and collective intelligence
- **Self-evolution capabilities** (platform that improves itself)

### Architecture Principles
1. **Layered Architecture** - Clear separation of concerns
2. **Microservices** - Independent, scalable modules
3. **Event-Driven** - Asynchronous communication via EventBus
4. **AI-First** - Intelligence embedded at every layer
5. **Self-Learning** - Platform learns from usage
6. **Privacy-by-Design** - GDPR compliant from the ground up

### Key Metrics
- **Modules**: 9 production modules
- **Python Files**: ~580 files
- **Lines of Code**: ~85,000 LOC
- **AI Agents**: 26 specialized agents
- **ML Models**: 8+ trained models
- **API Endpoints**: 100+ REST endpoints

---

## 📐 Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 5: Human Interface                  │
│                  (Web App, API Gateway, CLI)                 │
├─────────────────────────────────────────────────────────────┤
│                Layer 4: Platform Services                    │
│   (BIA, Risk, Compliance, Documents, Plans, Learning...)    │
├─────────────────────────────────────────────────────────────┤
│              Layer 3: INTELLIGENT-CORE ⭐                    │
│  ┌───────────────────────────────────────────────────┐     │
│  │ 1. workflow_intelligence (THE BRAIN)              │     │
│  │ 2. ai-foundation (RAG, ML, LLM)                   │     │
│  │ 3. orchestration (Autonomous AI)                  │     │
│  │ 4. expertise-center (26 AI Agents)                │     │
│  │ 5. collective (Collective Intelligence)           │     │
│  │ 6. community_intelligence (Community Knowledge)   │     │
│  │ 7. predictive (Journey Prediction)                │     │
│  │ 8. workflow-engine (BPMN Orchestration)           │     │
│  │ 9. ai_workflow_optimizer (Self-Evolution)         │     │
│  └───────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│                   Layer 2: Shared Libraries                  │
│        (Auth, Database, Cache, EventBus, Utils)             │
├─────────────────────────────────────────────────────────────┤
│                  Layer 1: Infrastructure                     │
│   (PostgreSQL, Redis, Qdrant, Temporal, RabbitMQ)          │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Rules
- ✅ Higher layers depend on lower layers
- ❌ No circular dependencies
- ✅ Modules communicate via EventBus
- ✅ Shared libraries for common functionality

---

## 🧠 Module 1: workflow_intelligence

### Overview
**Purpose**: Core workflow engine and state management (THE BRAIN)
**Location**: `intelligent-core/workflow_intelligence/`
**Files**: ~100 Python files
**LOC**: ~12,000

### Responsibilities
- Workflow state machine management
- Multi-tenancy with Row-Level Security (RLS)
- AI context generation for decision-making
- Case library (learn from completed workflows)
- Temporal workflow orchestration
- Event publishing for platform-wide coordination

### Architecture

```
workflow_intelligence/
├── core/
│   ├── engine.py                    # WorkflowEngine (main orchestrator)
│   ├── state_machine.py             # State transitions
│   ├── validators.py                # Business rules validation
│   └── context.py                   # AI context generation
├── storage/
│   ├── postgres_adapter.py          # PostgreSQL with RLS
│   └── rls_context.py               # Multi-tenancy security
├── case_library/
│   ├── collector.py                 # Collect completed workflows
│   ├── repository.py                # Store cases
│   └── analyzer.py                  # Extract patterns
├── temporal_workflows/
│   ├── bia_workflow.py              # BIA Temporal workflow
│   ├── risk_workflow.py             # Risk assessment workflow
│   └── planning_workflow.py         # Planning workflow
├── integration/
│   ├── ai_context_builder.py        # Build context for AI
│   └── learning_knowledge_client.py # Integration with knowledge
└── monitoring/
    └── metrics.py                   # Prometheus metrics
```

### Key Components

#### WorkflowEngine
```python
class WorkflowEngine:
    """
    Core workflow orchestration engine

    Manages:
    - State transitions
    - Event publishing
    - Context generation for AI
    - Gap analysis and validation
    """

    async def start(
        self,
        module: str,
        tenant_id: str,
        user_id: str,
        initial_data: Dict
    ) -> str:
        """Start new workflow instance"""

    async def execute_action(
        self,
        workflow_id: str,
        action: str,
        tenant_id: str,
        user_id: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """Execute workflow action"""

    async def get_context(
        self,
        workflow_id: str,
        tenant_id: str
    ) -> Dict:
        """Get AI context for decision-making"""
```

#### PostgresStorageAdapter (RLS-enabled)
```python
class PostgresStorageAdapter:
    """
    PostgreSQL storage with Row-Level Security

    Security:
    - Multi-tenancy isolation via RLS
    - Prevents cross-tenant data access
    - Admin override support
    """

    async def create_workflow(
        self,
        tenant_id: str,
        module: str,
        data: Dict
    ) -> str:
        """Create workflow with RLS context"""

    async def get_workflow(
        self,
        workflow_id: str,
        tenant_id: str
    ) -> Dict:
        """Get workflow (RLS enforced)"""
```

### Database Schema

**workflow_contexts** table:
```sql
CREATE TABLE workflow_intelligence.workflow_contexts (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    module VARCHAR(50) NOT NULL,
    current_stage VARCHAR(50),
    data JSONB,
    available_actions TEXT[],
    gaps JSONB[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE workflow_intelligence.workflow_contexts ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON workflow_intelligence.workflow_contexts
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

### Integration Points
- **EventBus**: Publishes workflow events
- **ai-foundation**: Gets AI context and recommendations
- **Temporal**: Orchestrates long-running workflows
- **platform-services**: Consumed by BIA, Risk, Planning services

### API Endpoints
- `POST /api/v1/workflows/{module}/start` - Start workflow
- `POST /api/v1/workflows/{id}/actions/{action}` - Execute action
- `GET /api/v1/workflows/{id}/context` - Get AI context
- `GET /api/v1/workflows/{id}` - Get workflow state

---

## 🤖 Module 2: ai-foundation

### Overview
**Purpose**: AI infrastructure (RAG, ML, LLM, Learning)
**Location**: `intelligent-core/ai-foundation/`
**Files**: ~50 Python files
**LOC**: ~8,500

### Responsibilities
- RAG (Retrieval-Augmented Generation) pipeline
- Multi-provider LLM routing (Anthropic, OpenAI)
- ML models (prediction, anomaly detection)
- Self-learning from platform usage
- Knowledge indexing and retrieval

### Architecture

```
ai-foundation/
├── rag/
│   ├── pipeline.py                  # Main RAG orchestration
│   ├── embeddings.py                # Voyage/OpenAI embeddings
│   ├── retrieval.py                 # Hybrid search
│   ├── reranking.py                 # Cohere reranking
│   └── qdrant_client.py             # Vector DB client
├── llm/
│   ├── llm_router.py                # Multi-provider routing
│   ├── anthropic_adapter.py         # Claude integration
│   └── openai_adapter.py            # GPT integration
├── ml/
│   ├── predictive_models.py         # RandomForest, Gradient Boosting
│   ├── anomaly_detector.py          # Isolation Forest
│   └── training_pipeline.py         # Model training
├── learning/
│   ├── self_learning_engine.py      # Platform learning
│   ├── pattern_extractor.py         # Extract patterns
│   └── rule_generator.py            # Generate rules
├── context/
│   ├── context_builder.py           # Build AI context
│   └── prompt_builder.py            # Construct prompts
└── learning-knowledge/               # Knowledge management
    ├── knowledge/                    # Standards (ISO, BCI, WHO)
    ├── learning/                     # Learning engines
    └── api/                          # Knowledge API (port 8030)
```

### Key Components

#### RAGPipeline
```python
class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline

    Features:
    - Document ingestion and chunking
    - Embedding generation (Voyage AI, OpenAI)
    - Hybrid search (vector + keyword)
    - Reranking for relevance (Cohere)
    """

    async def ingest_documents(
        self,
        documents: List[Document],
        collection: str
    ):
        """Ingest and index documents"""

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Document]:
        """Retrieve relevant documents"""

    async def retrieve_with_reranking(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Document]:
        """Retrieve and rerank for best results"""
```

#### LLMRouter
```python
class LLMRouter:
    """
    Multi-provider LLM routing

    Providers:
    - Anthropic (Claude 3.5 Sonnet)
    - OpenAI (GPT-4)

    Features:
    - Automatic fallback
    - Cost optimization
    - Rate limit handling
    """

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """Generate LLM response"""

    async def generate_with_fallback(
        self,
        prompt: str,
        primary_provider: str = "anthropic"
    ) -> Dict:
        """Generate with automatic fallback"""
```

### Vector Database (Qdrant)

**Collections**:
- `iso_standards` - ISO 22301, 27001, etc.
- `bci_guidelines` - BCI Good Practice Guidelines
- `workflow_cases` - Completed workflow patterns
- `community_knowledge` - Community contributions

**Vector Dimensions**: 1024 (Voyage AI embeddings)

### Integration Points
- **Qdrant**: Vector storage and search
- **Voyage AI**: Embeddings API
- **Anthropic/OpenAI**: LLM APIs
- **PostgreSQL**: Knowledge and learning data

---

## 🎯 Module 3: orchestration

### Overview
**Purpose**: Autonomous AI orchestration and decision-making
**Location**: `intelligent-core/orchestration/`
**Files**: ~80 Python files
**LOC**: ~10,500

### Responsibilities
- Autonomous decision-making (AI brain)
- Context aggregation from entire platform
- Task delegation to specialists
- 4-layer memory system
- Safety validation and monitoring

### Architecture

```
orchestration/
├── ai-orchestration/                # Main orchestrator
│   ├── orchestrator.py              # Core decision loop
│   ├── decision_center/
│   │   ├── context_aggregator.py    # Gather platform context
│   │   ├── priority_engine.py       # Calculate priority
│   │   ├── strategy_selector.py     # Select strategy
│   │   └── delegation_manager.py    # Delegate to specialists
│   ├── memory/
│   │   ├── working_memory.py        # Current context
│   │   ├── short_term_memory.py     # Recent events
│   │   ├── long_term_memory.py      # Historical patterns
│   │   ├── procedural_memory.py     # Learned strategies
│   │   └── distributed_memory.py    # Unified interface
│   ├── safety/
│   │   └── safety_monitor.py        # Safety validation
│   └── evolution/
│       └── evolution_engine.py      # Self-improvement
└── coordination-center/              # Intent-based routing
    └── api/routes.py                # API coordination
```

### Key Components

#### AIOrchestrator
```python
class AIOrchestrator:
    """
    Autonomous AI orchestration

    Capabilities:
    - Platform-wide context awareness
    - Autonomous decision-making
    - Task delegation
    - Safety validation
    - Self-learning
    """

    async def decide(self) -> Decision:
        """
        Make autonomous decision

        Process:
        1. Aggregate context
        2. Calculate priority
        3. Select strategy
        4. Validate safety
        5. Return decision
        """

    async def execute(self, decision: Decision):
        """Execute decision (delegate or auto-resolve)"""
```

#### DistributedMemory (4-layer system)
```python
class DistributedMemory:
    """
    4-layer memory system

    Layers:
    1. Working Memory - Current context (Redis)
    2. Short-term Memory - Recent events (Redis)
    3. Long-term Memory - Historical patterns (PostgreSQL)
    4. Procedural Memory - Learned strategies (PostgreSQL)
    """

    async def store(
        self,
        layer: MemoryLayer,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """Store in memory layer"""

    async def recall(
        self,
        layer: MemoryLayer,
        query: str
    ) -> List[Dict]:
        """Recall from memory"""
```

### Decision Flow

```
1. CONTEXT AGGREGATION
   ├─ Active workflows
   ├─ Stuck workflows
   ├─ Recent events
   ├─ User requests
   └─ Platform metrics

2. PRIORITY CALCULATION
   ├─ Urgency score
   ├─ Impact score
   └─ Resource availability

3. STRATEGY SELECTION
   ├─ Retrieve similar situations
   ├─ Evaluate strategies
   └─ Select best approach

4. SAFETY VALIDATION
   ├─ Check for loops
   ├─ Validate constraints
   └─ Prevent hallucinations

5. DECISION EXECUTION
   ├─ Delegate to specialist
   ├─ Auto-resolve
   └─ Wait for human
```

### Integration Points
- **Supabase**: Context aggregation (workflows, processes, risks)
- **Redis**: Working and short-term memory
- **EventBus**: Task delegation events
- **expertise-center**: Delegate to AI agents

---

## 🎓 Module 4: expertise-center

### Overview
**Purpose**: 26 specialized AI agents for BCM domains
**Location**: `intelligent-core/expertise-center/`
**Files**: ~150 Python files
**LOC**: ~18,500

### Responsibilities
- Domain expertise for BCM, Risk, Compliance
- 10 heavy analyzers (deep analysis)
- 3 strategic specialists (expert advice)
- 13 tactical assistants (conversational)

### Architecture

```
expertise-center/
├── shared/base/
│   ├── base_analyzer.py             # Heavy AI analysis (10 types)
│   ├── base_specialist.py           # Expert agents (3 types)
│   └── base_tactical_assistant.py   # Conversational (13 types)
├── domains/bcm/
│   ├── analyzers/                   # 10 BCM analyzers
│   │   ├── impact_analyzer.py       # BIA predictions
│   │   ├── risk_analyzer.py         # Risk assessment
│   │   ├── compliance_analyzer.py   # ISO 22301 compliance
│   │   ├── governance_analyzer.py   # Governance analysis
│   │   ├── emergency_analyzer.py    # Emergency response
│   │   ├── scenario_analyzer.py     # Scenario testing
│   │   ├── performance_analyzer.py  # Performance metrics
│   │   ├── learning_analyzer.py     # Training effectiveness
│   │   ├── plan_analyzer.py         # Plan quality
│   │   └── lifecycle_analyzer.py    # BCM lifecycle
│   ├── specialists/                 # 3 strategic specialists
│   │   ├── bcm_advisor.py           # Strategic BCM advice
│   │   ├── compliance_auditor.py    # Compliance auditing
│   │   └── strategic_planner.py     # Strategic planning
│   └── tactical_assistants/         # 13 conversational assistants
│       ├── bia_specialist.py
│       ├── risk_analyst.py
│       ├── incident_advisor.py
│       ├── plan_generator.py
│       ├── exercise_designer.py
│       ├── compliance_copilot.py
│       ├── governance_specialist.py
│       ├── learning_specialist.py
│       ├── documents_specialist.py
│       ├── validation_specialist.py
│       ├── community_specialist.py
│       ├── project_manager.py
│       └── response_specialist.py
└── core/
    └── coordinator.py               # Agent coordination
```

### Base Classes

#### BaseAnalyzer
```python
class BaseAnalyzer(ABC):
    """
    Base class for heavy AI analyzers

    Integrations:
    - RAG: Knowledge retrieval
    - LLM: Deep analysis
    - ML: Predictions
    - Knowledge: Standards and guidelines
    """

    def __init__(self, config: Config):
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.predictor = PredictiveModel()
        self.anomaly_detector = AnomalyDetector()
        self.knowledge = LearningKnowledgeAdapter()

    @abstractmethod
    async def analyze(self, context: Dict) -> AnalysisResult:
        """Perform deep analysis"""

    @abstractmethod
    async def extract_insights(self, data: Dict) -> List[Insight]:
        """Extract actionable insights"""
```

### Agent Types

**Analyzers** (Heavy AI processing):
- Input: Complex business data
- Processing: RAG + LLM + ML
- Output: Detailed analysis report
- Execution Time: 5-30 seconds

**Specialists** (Expert advice):
- Input: Strategic questions
- Processing: RAG + LLM
- Output: Expert recommendations
- Execution Time: 3-10 seconds

**Tactical Assistants** (Conversational):
- Input: User questions (chat)
- Processing: RAG + LLM
- Output: Conversational responses
- Execution Time: 1-5 seconds

### Integration Points
- **ai-foundation**: RAG, LLM, ML services
- **workflow_intelligence**: Workflow context
- **orchestration**: Delegation from orchestrator

---

## 🤝 Module 5: collective

### Overview
**Purpose**: Privacy-preserving collective intelligence
**Location**: `intelligent-core/collective/`
**Files**: ~20 Python files
**LOC**: ~3,200
**Port**: 8032

### Responsibilities
- Create collective AI agents from ≥5 organizations
- Anonymize sensitive data (GDPR compliant)
- Enforce k-anonymity (privacy guarantee)
- Detect stuck workflows
- Temporary agent lifecycle (7 days)

### Architecture

```
collective/
├── services/
│   ├── collective_agent_service.py  # Agent creation & chat
│   ├── anonymizer.py                # Privacy protection
│   ├── k_anonymity_validator.py     # K-anonymity enforcement
│   └── stuck_detection_service.py   # Detect stuck workflows
├── models/
│   └── database.py                  # CollectiveAgent, messages
├── api/
│   ├── collective_agents.py         # Agent endpoints
│   └── stuck_detection.py           # Stuck workflow API
└── config.py
```

### Key Components

#### CollectiveAgentService
```python
class CollectiveAgentService:
    """
    Create collective AI agents from anonymized cases

    Privacy Guarantees:
    - Minimum 5 organizations (k=5)
    - All PII removed
    - No reverse engineering possible
    - GDPR compliant
    """

    async def create_collective_agent(
        self,
        query: Dict,
        tenant_id: str
    ) -> CollectiveAgent:
        """
        Create collective agent

        Requirements:
        - ≥5 organizations match query
        - Cases anonymized
        - K-anonymity validated
        """

    async def chat(
        self,
        agent_id: str,
        message: str,
        tenant_id: str
    ) -> str:
        """Chat with collective agent"""
```

#### Anonymizer
```python
class Anonymizer:
    """
    Privacy-preserving anonymization

    Removes:
    - Organization names
    - Contact information
    - IP addresses
    - Identifiers
    - Dates (generalized)
    """

    def anonymize_case(self, case: Dict) -> Dict:
        """Anonymize workflow case"""

    def verify_anonymization(self, case: Dict) -> bool:
        """Verify no PII remains"""
```

### Privacy Model

**K-Anonymity**: Each record indistinguishable from ≥k-1 others
```
Minimum k = 5 organizations required

Example:
Query: "Healthcare, medium-sized, BIA workflow"
Result: Cases from 8 organizations (k=8) ✅

Query: "Finance, large, specific region"
Result: Only 3 organizations found (k=3) ❌ REJECTED
```

### Integration Points
- **workflow_intelligence**: Case library (anonymized cases)
- **LLM**: Chat with collective agent
- **EventBus**: Stuck workflow notifications

### API Endpoints
- `POST /api/v1/collective/create` - Create collective agent
- `POST /api/v1/collective/{id}/chat` - Chat with agent
- `GET /api/v1/collective/stuck-workflows` - Detect stuck workflows

---

## 🌐 Module 6: community_intelligence

### Overview
**Purpose**: Community-driven knowledge creation
**Location**: `intelligent-core/community_intelligence/`
**Files**: ~40 Python files
**LOC**: ~5,800
**Port**: 8030

### Responsibilities
- Peer review workflow
- Reputation system (gamification)
- Contribution management
- Living documentation
- Community case library

### Architecture

```
community_intelligence/
├── services/
│   ├── contribution_service.py      # Submit/approve contributions
│   ├── peer_review_service.py       # Multi-reviewer workflow
│   ├── reputation_engine.py         # Reputation scoring
│   ├── anonymizer.py                # Privacy protection
│   ├── case_library_bridge.py       # Bridge to workflow_intelligence
│   ├── workflow_completion_handler.py # EventBus subscriber
│   └── living_docs.py               # Dynamic documentation
├── api/
│   └── routes.py                    # Unified router
├── events/
│   └── subscribers.py               # EventBus subscribers
└── models/
    └── database.py                  # Contributions, reviews, reputation
```

### Peer Review Workflow

```
1. SUBMIT CONTRIBUTION
   ├─ Author submits case/document
   ├─ Initial validation
   └─ Status: Draft

2. PEER REVIEW
   ├─ Assign reviewers (≥2)
   ├─ Reviews submitted
   └─ Calculate consensus

3. DECISION
   ├─ Approved (≥66% agreement)
   ├─ Rejected (majority disagree)
   └─ Revision Requested

4. PUBLISH
   ├─ Add to community library
   ├─ Update reputation scores
   └─ Notify community
```

### Reputation System

**Scoring**:
```python
reputation_score = (
    contributions_approved * 10 +
    reviews_completed * 5 +
    helpful_votes * 2 +
    tenure_months * 1
)
```

**Badges**:
- 🥉 Contributor (10+ contributions)
- 🥈 Expert (50+ contributions, 4.5+ rating)
- 🥇 Master (100+ contributions, 4.8+ rating)

### Integration Points
- **workflow_intelligence**: Workflow completion events
- **EventBus**: workflow.completed subscription
- **LLM**: Content generation and summarization

---

## 🔮 Module 7: predictive

### Overview
**Purpose**: Journey prediction and proactive recommendations
**Location**: `intelligent-core/predictive/`
**Files**: ~15 Python files
**LOC**: ~2,400
**Port**: 8031

### Responsibilities
- Predict next workflow steps
- Generate proactive recommendations
- Forecast demand
- Daily digest emails (8 AM)

### Architecture

```
predictive/
├── services/
│   ├── journey_predictor.py         # Predict next steps
│   ├── proactive_recommendations.py # Generate recommendations
│   └── demand_forecaster.py         # Forecast future needs
├── scheduler/
│   └── daily_digests.py             # Daily email digests (8 AM)
└── api/
    └── predictions.py               # Prediction endpoints
```

### Journey Prediction

**Input**: Current workflow state + historical patterns
**Output**: Predicted next 3-5 steps with probabilities

```python
{
    "workflow_id": "wf-123",
    "current_step": "data_collection",
    "predictions": [
        {"step": "analysis", "probability": 0.85, "days_until": 3},
        {"step": "review", "probability": 0.78, "days_until": 7},
        {"step": "approval", "probability": 0.65, "days_until": 10}
    ]
}
```

### Integration Points
- **workflow_intelligence**: Case library (historical data)
- **Notification Service**: Daily digests

---

## 🔄 Module 8: workflow-engine

### Overview
**Purpose**: BPMN 2.0 visual process orchestration
**Location**: `intelligent-core/workflow-engine/`
**Files**: 22 Python files
**LOC**: ~4,500

### Responsibilities
- BPMN 2.0 XML parsing
- Visual process execution
- Gateway evaluation (XOR, AND, OR)
- Integration with workflow_intelligence
- PostgreSQL persistence

### Architecture

```
workflow-engine/
├── workflow/
│   ├── core/
│   │   └── unified_engine.py        # BPMN + Workflow Intelligence
│   ├── bpmn/
│   │   ├── parser.py                # Parse BPMN XML
│   │   ├── engine.py                # Execute BPMN
│   │   ├── engine_persistent.py     # PostgreSQL backend
│   │   ├── gateway_evaluator.py     # Gateway logic
│   │   └── expression_evaluator.py  # Expression evaluation
│   ├── persistence/
│   │   ├── database.py              # Database manager
│   │   └── repositories/            # Process, instance, task repos
│   ├── api/
│   │   └── main.py                  # FastAPI endpoints
│   └── visualization/
│       └── state_visualizer.py      # Visual state rendering
```

### BPMN Support

**Supported Elements**:
- ✅ Start Event
- ✅ End Event
- ✅ User Task
- ✅ Service Task
- ✅ Exclusive Gateway (XOR)
- ✅ Parallel Gateway (AND)
- ✅ Inclusive Gateway (OR)
- ✅ Sequence Flows
- ✅ Conditions

**Example BPMN**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="bia_process">
    <startEvent id="start"/>
    <userTask id="collect_data" name="Collect BIA Data"/>
    <exclusiveGateway id="gateway1"/>
    <userTask id="detailed_analysis" name="Detailed Analysis"/>
    <userTask id="quick_analysis" name="Quick Analysis"/>
    <endEvent id="end"/>

    <sequenceFlow sourceRef="start" targetRef="collect_data"/>
    <sequenceFlow sourceRef="collect_data" targetRef="gateway1"/>
    <sequenceFlow sourceRef="gateway1" targetRef="detailed_analysis">
      <conditionExpression>complexity == "high"</conditionExpression>
    </sequenceFlow>
    <sequenceFlow sourceRef="gateway1" targetRef="quick_analysis">
      <conditionExpression>complexity == "low"</conditionExpression>
    </sequenceFlow>
  </process>
</definitions>
```

### Integration Points
- **workflow_intelligence**: Unified engine integration
- **PostgreSQL**: Process and instance persistence
- **EventBus**: BPMN events

---

## 🤖 Module 9: ai_workflow_optimizer

### Overview
**Purpose**: Platform self-evolution via ML analysis
**Location**: `intelligent-core/ai_workflow_optimizer/`
**Files**: 1 file (946 lines!)
**LOC**: 946
**Port**: 8006

### Responsibilities
- **CRITICAL**: Platform analyzes itself
- ML-powered optimization detection
- Performance prediction
- Bottleneck detection
- Anomaly detection
- Generate technical specs for improvements
- **Future**: Integration with "Laboratory" for code generation

### Architecture

```
ai_workflow_optimizer/
└── main.py                          # Complete service (946 LOC)
    ├── WorkflowOptimizerService     # ML analysis
    ├── ML Models (3):
    │   ├── PerformancePredictor     # RandomForest
    │   ├── BottleneckDetector       # Classifier
    │   └── AnomalyDetector          # Isolation Forest
    ├── Database Models:
    │   ├── ProcessExecution
    │   ├── OptimizationPrediction
    │   └── MLModel
    └── API Endpoints (8)
```

### Self-Evolution Cycle

```
┌───────────────────────────────────────────────────┐
│         PLATFORM SELF-EVOLUTION CYCLE             │
├───────────────────────────────────────────────────┤
│                                                   │
│  1. MONITORING                                    │
│     └─ Orchestrator collects platform metrics    │
│                                                   │
│  2. ANALYSIS (ai_workflow_optimizer)              │
│     ├─ Performance prediction                     │
│     ├─ Bottleneck detection                       │
│     └─ Anomaly detection                          │
│                                                   │
│  3. OPTIMIZATION NEED DETECTED                    │
│     └─ Generate technical specification (ТЗ)     │
│                                                   │
│  4. LABORATORY (Future - Not Yet Implemented)     │
│     ├─ AI specialists receive ТЗ                  │
│     ├─ Generate code implementation               │
│     └─ Run automated tests                        │
│                                                   │
│  5. ADMIN REVIEW                                  │
│     ├─ Platform admin reviews changes            │
│     ├─ Test in staging                            │
│     └─ Approve integration                        │
│                                                   │
│  6. SELF-UPDATE                                   │
│     ├─ Deploy new code                            │
│     ├─ Monitor impact                             │
│     └─ Platform evolved! 🎉                       │
│                                                   │
└───────────────────────────────────────────────────┘
```

### ML Models

#### 1. Performance Predictor (RandomForest)
```python
Features: [complexity, resource_count, stakeholder_count, step_count]
Target: execution_time_minutes
Accuracy: ~85%

Usage:
{
    "process_id": "proc-123",
    "complexity": "medium",
    "resource_count": 5,
    "stakeholder_count": 10,
    "step_count": 8
}
→ Predicted: 67.5 minutes
```

#### 2. Bottleneck Detector (Classifier)
```python
Features: [complexity, resources, stakeholders, steps, success_rate]
Target: is_bottleneck (binary)
Accuracy: ~82%

Output:
{
    "bottleneck_probability": 0.73,
    "severity": "high",
    "bottlenecks": [
        {"type": "resource_shortage", "impact": 0.8},
        {"type": "communication_overhead", "impact": 0.6}
    ]
}
```

#### 3. Anomaly Detector (Isolation Forest)
```python
Features: [execution_time, resources, stakeholders, steps, success_rate]
Contamination: 10%
Accuracy: ~85%

Output:
{
    "is_anomaly": true,
    "risk_level": "high",
    "anomalies": [
        {"type": "execution_time_anomaly", "severity": "high"}
    ]
}
```

### Integration Points
- **PostgreSQL**: Store predictions and models
- **orchestration**: Provide optimization insights
- **Future Laboratory**: Code generation

### API Endpoints
- `POST /api/v1/optimize/performance` - Performance optimization
- `GET /api/v1/analyze/bottlenecks/{id}` - Bottleneck analysis
- `GET /api/v1/optimize/resources/{id}` - Resource optimization
- `GET /api/v1/detect/anomalies/{id}` - Anomaly detection
- `POST /api/v1/models/retrain` - Retrain ML models
- `GET /api/v1/models/status` - Model status

---

## 🔗 Integration Architecture

### EventBus Communication

**Events Published**:
```
workflow.started         → workflow_intelligence
workflow.completed       → community_intelligence, collective
workflow.stuck           → collective (stuck detection)
task.delegated           → orchestration → expertise-center
case.created             → community_intelligence
contribution.approved    → community_intelligence
```

**Event Format**:
```python
{
    "event_type": "workflow.completed",
    "timestamp": "2025-10-07T10:30:00Z",
    "tenant_id": "tenant-123",
    "data": {
        "workflow_id": "wf-456",
        "module": "planning",
        "duration_days": 14,
        "success": true
    }
}
```

### Database Architecture

**Schemas**:
- `workflow_intelligence.*` - Workflows, cases
- `community_intelligence.*` - Contributions, reviews
- `orchestration.*` - Decisions, memory
- `collective.*` - Collective agents
- `predictive.*` - Predictions
- `ai_optimizer.*` - ML models, predictions

**RLS (Row-Level Security)**:
- Enforced on all tenant-specific tables
- `current_setting('app.current_tenant')::UUID`
- Prevents cross-tenant data access

### API Gateway Routing

```
/api/v1/workflows/*          → workflow_intelligence
/api/v1/analysis/*           → expertise-center (analyzers)
/api/v1/advice/*             → expertise-center (specialists)
/api/v1/assist/*             → expertise-center (assistants)
/api/v1/collective/*         → collective
/api/v1/community/*          → community_intelligence
/api/v1/predictions/*        → predictive
/api/v1/bpmn/*               → workflow-engine
/api/v1/optimize/*           → ai_workflow_optimizer
/api/v1/orchestrator/*       → orchestration
```

---

## 📊 Performance Specifications

### Response Time Targets

| Operation | Target | Max |
|-----------|--------|-----|
| Workflow start | < 200ms | 500ms |
| Workflow action | < 300ms | 1s |
| RAG retrieval | < 100ms | 300ms |
| LLM generation | < 3s | 10s |
| Analyzer (heavy) | < 10s | 30s |
| ML prediction | < 500ms | 2s |

### Throughput Targets

| Service | Target TPS | Max TPS |
|---------|-----------|---------|
| workflow_intelligence | 100 | 500 |
| ai-foundation (RAG) | 50 | 200 |
| expertise-center | 20 | 100 |
| orchestration | 10 | 50 |

### Resource Limits

**Memory**:
- workflow_intelligence: 2GB
- ai-foundation: 4GB (embeddings cache)
- orchestration: 1GB
- expertise-center: 3GB
- ai_workflow_optimizer: 2GB (ML models)

**CPU**:
- Most services: 2 cores
- ai-foundation: 4 cores (embeddings)
- ai_workflow_optimizer: 4 cores (ML training)

---

## 🔒 Security Specifications

### Authentication
- **JWT tokens** (RS256)
- **Access tokens**: 15 min expiry
- **Refresh tokens**: 7 days
- **Token rotation**: Automatic

### Authorization
- **RBAC** (Role-Based Access Control)
- **Tenant isolation** (RLS)
- **Permission model**: Resource-based

### Data Protection
- **Encryption at rest**: AES-256
- **Encryption in transit**: TLS 1.3
- **PII anonymization**: GDPR compliant
- **K-anonymity**: k≥5 for collective intelligence

### Security Monitoring
- **SQL injection prevention**: Parameterized queries
- **XSS prevention**: Input sanitization
- **Rate limiting**: 100 req/min per user
- **Audit logging**: All sensitive operations

---

## 🚀 Deployment Architecture

### Container Configuration

**Docker Images**:
```yaml
workflow_intelligence:
  image: ai-bcm/workflow-intelligence:latest
  ports: [8001]
  replicas: 3

ai-foundation:
  image: ai-bcm/ai-foundation:latest
  ports: [8002]
  replicas: 2

orchestration:
  image: ai-bcm/orchestration:latest
  ports: [8003]
  replicas: 2

expertise-center:
  image: ai-bcm/expertise-center:latest
  ports: [8004]
  replicas: 3

collective:
  image: ai-bcm/collective:latest
  ports: [8032]
  replicas: 2

community_intelligence:
  image: ai-bcm/community-intelligence:latest
  ports: [8030]
  replicas: 2

predictive:
  image: ai-bcm/predictive:latest
  ports: [8031]
  replicas: 1

workflow-engine:
  image: ai-bcm/workflow-engine:latest
  ports: [8005]
  replicas: 2

ai_workflow_optimizer:
  image: ai-bcm/ai-workflow-optimizer:latest
  ports: [8006]
  replicas: 1
```

### Infrastructure Dependencies

**Required Services**:
- PostgreSQL 15+ (with pgvector extension)
- Redis 7+
- Qdrant (vector database)
- RabbitMQ 3.12+ (EventBus)
- Temporal Cloud (workflow orchestration)

**Optional Services**:
- Prometheus (metrics)
- Grafana (dashboards)
- Jaeger (tracing)
- Elasticsearch (logs)

---

## 📚 Appendix

### A. Technology Stack

**Core**:
- Python 3.11+
- FastAPI 0.109+
- SQLAlchemy 2.0+
- Pydantic 2.5+

**AI/ML**:
- Anthropic SDK (Claude)
- OpenAI SDK (GPT)
- LangChain 0.1+
- scikit-learn 1.3+
- Voyage AI (embeddings)

**Databases**:
- PostgreSQL 15+ (with pgvector)
- Qdrant (vectors)
- Redis 7+

**Orchestration**:
- Temporal Cloud
- RabbitMQ

### B. Glossary

**BCM**: Business Continuity Management
**BIA**: Business Impact Analysis
**RAG**: Retrieval-Augmented Generation
**LLM**: Large Language Model
**RLS**: Row-Level Security
**BPMN**: Business Process Model and Notation
**k-anonymity**: Privacy model (k≥5 organizations)

### C. References

- [Testing Specification](TESTING_SPECIFICATION.md)
- [BPMN 2.0 Specification](https://www.omg.org/spec/BPMN/2.0/)
- [ISO 22301:2019](https://www.iso.org/standard/75106.html)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Temporal Documentation](https://docs.temporal.io/)

---

**Document Version**: 2.0
**Last Updated**: 2025-10-07
**Next Review**: 2025-12-07
**Owner**: Architecture Team
**Status**: Production Ready
