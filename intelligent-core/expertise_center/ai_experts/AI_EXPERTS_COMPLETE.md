# ✅ AI EXPERTS & ML SUBSYSTEM - АРХИТЕКТУРА

## 🎯 Обзор

Гибридная AI/ML подсистема с managed autonomy для BCM платформы.

**Философия:** Одна foundation model (Claude) + Specialized Agents + RAG + ML Predictions

---

## 📦 Компоненты

### 1. AI Expert Agents (3 специалиста)

#### BCM Advisor
- **Роль:** Помощь с BIA, планированием, стратегией
- **Tools:** BIA Analysis, Dependency Mapper, Case Search
- **Expertise:** Business impact analysis, recovery strategies
- **Temperature:** 0.3 (factual)

#### Compliance Auditor
- **Роль:** Проверка соответствия ISO 22301
- **Tools:** Compliance Check, Gap Analysis, Evidence Validator
- **Expertise:** Clause-by-clause compliance, audit prep
- **Temperature:** 0.2 (very factual)

#### Strategic Planner
- **Роль:** Долгосрочное планирование BCM программы
- **Tools:** Timeline Predictor, Resource Planner, Maturity Assessment
- **Expertise:** Roadmap development, budgeting, executive communication
- **Temperature:** 0.4 (strategic thinking)

---

### 2. RAG Pipeline

**Sources:**
1. Knowledge Graph (ISO standards, clauses)
2. Case Library (successful cases, patterns)
3. Community Annotations (practical interpretations)

**Process:**
```
Query → Embeddings → Hybrid Search → Re-rank → Top-K chunks
```

**Hybrid Search:**
- Semantic (vector similarity)
- Keyword (BM25-like)
- Filtered (industry, module)
- Re-ranked (recency + relevance + source priority)

---

### 3. ML Models

#### Workflow Predictor
**Predicts:**
- Stage duration (Random Forest Regressor)
- Stuck probability (Gradient Boosting Classifier)
- Expert help needed (Gradient Boosting Classifier)
- Total completion time

**Training Data:** Historical completed workflows (min 50 cases)

**Features:**
- Org context (industry, size, maturity)
- Stage info (current stage, total stages)
- Historical patterns (AI usage, challenges)

**Accuracy Target:** R² > 0.7 for duration, Accuracy > 0.75 for classification

---

### 4. Self-Learning Engine

**Learning Flow:**
```
Workflow Completed
  ↓
Auto-collect (anonymized)
  ↓
Extract patterns (ML)
  ↓
Update benchmarks
  ↓
IF pattern frequency > 10 AND success > 80%
  ↓
Suggest new rule (human approval)
```

**Supervised Elements:**
- Peer review for case quality
- Human approval for new rules
- Admin oversight for pattern → rule

---

## 📁 Структура файлов

```
intelligent-core/ai_experts/
├── __init__.py
├── requirements.txt
├── AI_EXPERTS_COMPLETE.md         # This file
│
├── base/
│   ├── __init__.py
│   └── expert_agent.py             # Base ExpertAgent class
│
├── specialists/
│   ├── __init__.py
│   ├── bcm_advisor.py              # BCM Advisor agent
│   ├── compliance_auditor.py       # Compliance Auditor agent
│   └── strategic_planner.py        # Strategic Planner agent
│
├── tools/
│   ├── __init__.py
│   ├── base_tool.py                # BaseTool class
│   ├── bia_tools.py                # BIA Analysis, Dependency Mapper
│   ├── compliance_tools.py         # Compliance Check, Gap Analysis
│   ├── strategic_tools.py          # Timeline Predictor, Resource Planner
│   └── case_library_tool.py        # Case Search tool
│
├── ml/
│   ├── __init__.py
│   ├── predictive_models.py        # WorkflowPredictor (Random Forest + GB)
│   ├── anomaly_detection.py        # Anomaly detection models
│   └── training_pipeline.py        # Training orchestration
│
├── rag/
│   ├── __init__.py
│   ├── pipeline.py                 # RAGPipeline main class
│   ├── embeddings.py               # Embedding generation
│   ├── retrieval.py                # Hybrid search implementation
│   └── reranking.py                # Re-ranking logic
│
├── learning/
│   ├── __init__.py
│   ├── self_learning_engine.py     # Auto-learning from workflows
│   ├── pattern_extractor.py        # ML pattern extraction
│   └── rule_generator.py           # Rule proposal generation
│
├── api/
│   ├── __init__.py
│   └── routes.py                   # FastAPI endpoints
│
├── tests/
│   ├── __init__.py
│   ├── test_expert_agents.py
│   ├── test_rag_pipeline.py
│   ├── test_ml_models.py
│   └── conftest.py
│
└── examples/
    ├── __init__.py
    ├── basic_usage.py              # Basic expert usage
    └── ml_training.py              # ML model training example
```

---

## 🔧 Core Components Implementation

### Expert Agent Base Class

```python
# base/expert_agent.py

class ExpertAgent:
    """
    Base class для AI экспертов

    Специализация через:
    - System prompt (роль эксперта)
    - RAG context (релевантные знания)
    - Tools (специфичные возможности)
    """

    def __init__(
        self,
        name: str,
        role_description: str,
        knowledge_sources: list,
        tools: list
    ):
        self.name = name
        self.role = role_description
        self.rag_pipeline = RAGPipeline(knowledge_sources)
        self.tools = {tool.name: tool for tool in tools}
        self.llm = AnthropicClient()

    async def advise(self, query: str, context: dict) -> str:
        # 1. RAG retrieval
        # 2. Build prompt
        # 3. Generate with tools
        # 4. Execute tool calls
        pass
```

### Tool System

```python
# tools/base_tool.py

class BaseTool(ABC):
    """Base class for AI expert tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool logic"""
        pass

    def to_anthropic_tool(self) -> dict:
        """Convert to Anthropic tool format"""
        pass
```

### ML Predictor

```python
# ml/predictive_models.py

class WorkflowPredictor:
    """ML predictor for workflow journey"""

    def __init__(self, case_library):
        self.duration_model = RandomForestRegressor(n_estimators=100)
        self.stuck_model = GradientBoostingClassifier()

    async def predict_journey(
        self,
        org_context: dict,
        current_state: str,
        current_progress: dict
    ) -> dict:
        # Predict timeline, risks, help needs
        pass
```

### RAG Pipeline

```python
# rag/pipeline.py

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline"""

    async def retrieve(
        self,
        query: str,
        context: dict,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        # 1. Generate embeddings
        # 2. Hybrid search (vector + keyword)
        # 3. Re-rank by relevance
        # 4. Return top-k
        pass
```

---

## 🚀 Quick Start

### 1. Installation

```bash
cd intelligent-core/ai_experts
pip install -r requirements.txt
```

### 2. Basic Usage

```python
from ai_experts import BCMAdvisor, RAGPipeline

# Initialize BCM Advisor
advisor = BCMAdvisor(
    case_library=case_lib,
    knowledge_graph=kg
)

# Get advice
response = await advisor.advise(
    query="How should I identify critical processes for healthcare org?",
    context={
        'industry': 'healthcare',
        'size': 'medium',
        'current_stage': 'identify_processes'
    }
)

print(response)
```

### 3. ML Training

```python
from ai_experts.ml import WorkflowPredictor

# Initialize predictor
predictor = WorkflowPredictor(case_library)

# Train on historical data
accuracy = await predictor.train()

# Predict journey
timeline = await predictor.predict_journey(
    org_context={'industry': 'healthcare', 'size': 'medium'},
    current_state='identify_processes',
    current_progress={}
)
```

---

## 🎯 Key Features

### 1. Managed Autonomy
- AI operates within Creative Zones
- Tools enable capabilities
- Rules enforce constraints
- Human approval for critical decisions

### 2. Hybrid Learning
- Automatic case collection
- ML pattern extraction
- Supervised rule generation
- Federated knowledge aggregation

### 3. Contextual Intelligence
- RAG retrieves relevant knowledge
- Industry-specific insights
- Real case examples
- Standards compliance

### 4. Predictive Capabilities
- Timeline forecasting
- Risk prediction
- Resource planning
- Expert help forecasting

---

## 📊 Performance Targets

### RAG Pipeline
- Retrieval latency: < 200ms
- Relevance@5: > 0.85
- Context quality score: > 0.8

### ML Models
- Duration prediction R²: > 0.7
- Stuck prediction accuracy: > 0.75
- Training time: < 5 min (50-100 cases)

### Expert Agents
- Response latency: < 3s (simple), < 10s (complex with tools)
- Tool execution success: > 95%
- User satisfaction: > 4.2/5

---

## 🔌 Integration Points

### With Workflow Intelligence
```python
# Expert advice during workflow
workflow = BIAWorkflowEngine(org_id)
context = workflow.get_context()

advice = await bcm_advisor.advise(
    query=user_question,
    context=context
)
```

### With Case Library
```python
# Auto-learning from completions
@eventbus.subscribe('workflow.completed')
async def learn_from_completion(event):
    await learning_engine.learn_from_workflow_completion(
        event.data.workflow_case
    )
```

### With Community Intelligence
```python
# Synthesize living documentation
annotations = await community.get_annotations(clause_id)
cases = await case_library.find_cases_for_clause(clause_id)

guidance = await rag_pipeline.synthesize(
    official_text=kg.get_clause(clause_id),
    community_input=annotations,
    real_cases=cases
)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest intelligent-core/ai_experts/tests/ -v

# Test specific component
pytest intelligent-core/ai_experts/tests/test_expert_agents.py

# With coverage
pytest --cov=ai_experts
```

---

## 📖 Documentation

- **AI_EXPERTS_COMPLETE.md** - This file (architecture overview)
- **API_REFERENCE.md** - API documentation
- **INTEGRATION_GUIDE.md** - Integration instructions
- **ML_MODELS.md** - ML models documentation

---

## ✅ Status

**Architecture:** ✅ Complete
**Implementation:** In Progress
**Testing:** Pending
**Documentation:** ✅ Complete

---

**Ready for implementation! 🚀**

_AI Experts & ML Subsystem v1.0.0_
_AI-Platform-ISO © 2025_
