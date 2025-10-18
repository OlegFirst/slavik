# BCM AI Colleagues

**9 Intelligent AI Assistants for Business Continuity Management**

---

## 📋 Overview

BCM AI Colleagues are specialized AI assistants that help with Business Continuity Management tasks. Each colleague has deep expertise in their domain and uses RAG, LLM, and ML capabilities from `intelligent_core/ai_foundation`.

---

## 🤖 Available Colleagues

### 1. BIA Specialist AI
**Specialty:** Business Impact Analysis

**Capabilities:**
- RTO/RPO determination
- Critical process identification
- Dependency mapping
- Impact assessment (financial, operational, reputational)
- MTD/MBCO calculations

**Example:**
```python
from platform_services.bcm_domain.ai_colleagues import BIASpecialistAI

bia_ai = BIASpecialistAI(rag_pipeline=rag, config={})
response = await bia_ai.process_message(
    "What should be the RTO for our payment processing system?"
)
```

### 2. Risk Analyst AI
**Specialty:** Risk Assessment & Management

**Capabilities:**
- Risk identification
- Threat assessment
- Vulnerability analysis
- Risk scoring and prioritization
- Mitigation recommendations

### 3. Compliance Copilot
**Specialty:** ISO 22301:2019 Compliance

**Capabilities:**
- Gap analysis
- Clause interpretation
- Compliance assessment
- Audit preparation
- Standard mapping (ISO 22301 ↔ BCI GPG)

### 4. Exercise Designer AI
**Specialty:** BC Exercise Planning

**Capabilities:**
- Tabletop exercise design
- Full-scale drill planning
- Scenario development
- Exercise objectives
- Participant role assignment

### 5. Incident Advisor AI
**Specialty:** Incident Response & Recovery

**Capabilities:**
- Incident classification
- Response coordination
- Recovery prioritization
- Communication planning
- Post-incident review

### 6. Plan Generator AI
**Specialty:** BC Plan Development

**Capabilities:**
- Business Continuity Plan creation
- Recovery procedure development
- Plan structure (ISO 22301 compliant)
- Template generation
- Plan review and improvement

### 7. Project Manager AI
**Specialty:** BCM Project Management

**Capabilities:**
- BCM program roadmap
- Task breakdown and scheduling
- Resource allocation
- Progress tracking
- Stakeholder management

### 8. Project Intelligence AI
**Specialty:** BCM Analytics & Reporting

**Capabilities:**
- BCM maturity assessment
- KPI tracking and reporting
- Trend analysis
- Dashboard creation
- Executive summaries

---

## 🎯 Colleague Coordinator

**Auto-routing to appropriate colleague:**

```python
from platform_services.bcm_domain.ai_colleagues import ColleagueCoordinator

# Initialize all colleagues
coordinator = ColleagueCoordinator(
    rag_pipeline=rag,
    colleagues={
        "bia_specialist": bia_ai,
        "risk_analyst": risk_ai,
        "compliance_copilot": compliance_ai,
        # ... other colleagues
    }
)

# Auto-routes based on query intent
response = await coordinator.route_query(
    "Help me determine RTO for critical processes"
)
# → Routes to BIA Specialist

response = await coordinator.route_query(
    "What are the requirements for ISO 22301 Clause 8.2?"
)
# → Routes to Compliance Copilot
```

---

## 🏗️ Architecture

### Base Class: `BaseAIColleague`

All colleagues extend `BaseAIColleague`:

```python
class BaseAIColleague:
    """Base class for all AI colleagues"""

    def __init__(self, name: str, specialty: str, rag_pipeline: RAGPipeline, config: dict):
        self.name = name
        self.specialty = specialty
        self.rag = rag_pipeline
        self.config = config

    async def process_message(self, message: str, context: AssistantContext) -> AssistantMessage:
        """Process user message and return response"""
        pass

    def _build_system_prompt(self, context: AssistantContext) -> str:
        """Build colleague-specific system prompt"""
        pass
```

### Integration with AI Foundation

```python
from intelligent_core.ai_foundation import RAGPipeline, LLMRouter

# Colleagues use:
# 1. RAG for knowledge retrieval
knowledge = await self.rag.retrieve(query, top_k=5)

# 2. LLM for text generation
response = await self.llm.generate(
    prompt=system_prompt + user_query,
    context=knowledge
)

# 3. Intent analysis for routing
intent = await self.intent_analyzer.analyze(query)
```

---

## 📊 Usage Patterns

### Pattern 1: Direct Colleague Usage

```python
# Use specific colleague directly
bia_ai = BIASpecialistAI(rag_pipeline=rag, config={})
response = await bia_ai.process_message("Determine RTO for process X")
```

### Pattern 2: Coordinator Auto-Routing

```python
# Let coordinator choose appropriate colleague
coordinator = ColleagueCoordinator(rag, colleagues={...})
response = await coordinator.route_query("Any BCM question")
```

### Pattern 3: Multi-Colleague Workflow

```python
# Complex workflow using multiple colleagues
# Step 1: BIA determines criticality
bia_result = await bia_ai.analyze_process(process_id)

# Step 2: Risk Analyst assesses threats
risk_result = await risk_ai.assess_risks(
    process_id=process_id,
    rto=bia_result.rto
)

# Step 3: Plan Generator creates recovery plan
plan = await plan_generator.generate_plan(
    process_id=process_id,
    bia=bia_result,
    risks=risk_result
)
```

---

## 🔌 Integration Points

### With BCM Services

Colleagues integrate with BCM services via HTTP:

```python
# BIA Specialist → BIA Service (8012)
bia_service_url = "http://localhost:8012"
bia_result = await httpx.post(
    f"{bia_service_url}/api/bia/analyze",
    json={"process_id": process_id}
)

# Use service result to enhance AI response
ai_response = await bia_ai.enhance_with_service_data(
    user_query=query,
    service_data=bia_result.json()
)
```

### With EventBus

```python
# Publish colleague consultations to EventBus
await eventbus.publish(
    event_type="bcm.colleague.consultation",
    data={
        "colleague": "bia_specialist",
        "query": query,
        "response": response
    }
)
```

---

## 📝 Configuration

Each colleague accepts configuration:

```python
config = {
    "model": "claude-sonnet-3.5",     # LLM model
    "temperature": 0.7,               # Creativity level
    "max_tokens": 2000,               # Response length
    "rag_top_k": 5,                   # RAG results
    "use_cache": True,                # Enable caching
}

colleague = BIASpecialistAI(rag_pipeline=rag, config=config)
```

---

## 🧪 Testing

```python
# Unit test example
import pytest
from platform_services.bcm_domain.ai_colleagues import BIASpecialistAI

@pytest.fixture
async def bia_ai():
    rag = RAGPipeline(config={...})
    return BIASpecialistAI(rag_pipeline=rag, config={})

@pytest.mark.asyncio
async def test_rto_determination(bia_ai):
    response = await bia_ai.process_message(
        "Determine RTO for payment processing"
    )
    assert "RTO" in response.message
    assert "hours" in response.message.lower()
```

---

## 📚 Documentation

- **Architecture**: See `base/base_colleague.py` for base implementation
- **Coordinator**: See `coordinator/colleague_coordinator.py` for routing logic
- **Examples**: See individual colleague directories for usage examples

---

## 🔄 Migration Notes

**Migrated from:** `intelligent_core/expertise_center/ai_office/ВСМ-colleagues/`
**New location:** `platform_services/bcm_domain/ai_colleagues/`

**Backward compatibility:** Symlink at old location points to new location

---

**Version:** 1.0.0
**Colleagues:** 8 active
**ISO Compliance:** ISO 22301:2019
