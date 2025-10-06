# 🧠 AI Office

**7 Specialized AI Colleagues for Interactive BCM Assistance**

Port: **8032**

---

## Overview

The AI Office service provides **interactive AI colleagues** with PDCA framework, RAG capabilities, and conversational intelligence. Each colleague specializes in a specific BCM domain, providing guided assistance through Plan-Do-Check-Act workflows.

**Architecture Note:**
- **AI Organs** (10 specialized units) have been migrated to [ai-orchestration/muscles/ai_organs/](../ai-orchestration/muscles/ai_organs/)
- **AI Colleagues** (7 interactive assistants) remain in this service
- **Super-Orchestrator** orchestrates both Organs and Colleagues

See [AI_OFFICE_INTEGRATION.md](../ai-orchestration/AI_OFFICE_INTEGRATION.md) for full architecture.

### The 7 AI Colleagues

| Colleague | Specialty | Features |
|-----------|-----------|----------|
| **Compliance Copilot** | ISO 22301 Compliance | Standards interpretation, gap analysis, audit preparation |
| **Project Manager AI** | BCM Projects | Timeline planning, resource allocation, milestone tracking |
| **Risk Analyst AI** | Risk Management | Risk assessment, mitigation strategies, scenario analysis |
| **BIA Specialist AI** | Business Impact Analysis | Criticality assessment, dependency mapping, RTO/RPO |
| **Plan Generator AI** | BCM Planning | Plan creation, template generation, documentation |
| **Incident Advisor AI** | Incident Response | Crisis guidance, escalation procedures, communication |
| **Exercise Designer AI** | BCM Exercises | Tabletop design, scenario creation, evaluation criteria |

**Each colleague provides:**
- 🔄 **PDCA Framework** - Plan-Do-Check-Act guided workflows
- 🧠 **RAG Capabilities** - Context-aware answers from knowledge base
- 💬 **Conversation Tracking** - Maintains context across interactions
- 🎯 **Action Suggestions** - Recommends next best actions
- 📊 **Progress Tracking** - Monitors PDCA phase progress

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure LLM Provider

Choose one:

**Anthropic Claude (Recommended):**
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

**OpenAI GPT:**
```bash
export OPENAI_API_KEY="your-api-key"
```

**Ollama (Local):**
```bash
ollama pull llama3.2
# No API key needed
```

### 3. Start Service

```bash
python main.py
```

Service runs on `http://localhost:8032`

---

## API Usage

### Individual Organ

```bash
curl -X POST http://localhost:8032/api/ai/organs/risk-advisor \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "twin_id": 1,
      "organization_state": {"name": "Acme Corp"},
      "known_risks": ["Supply chain disruption"]
    }
  }'
```

### Full Analysis

```bash
curl -X POST http://localhost:8032/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "twin_id": 1,
    "analysis_type": "comprehensive"
  }'
```

**Analysis Types:**
- `comprehensive` - Full BCM analysis (5 organs)
- `risk` - Risk-focused (3 organs)
- `compliance` - Standards compliance (2 organs)
- `planning` - Plan development (3 organs)
- `emergency` - Crisis response (3 organs)
- `training` - Learning & development (3 organs)

---

## Architecture

```
ai-intelligence/
├── main.py
├── requirements.txt
├── api/
│   ├── ai_router.py        # Full analysis
│   ├── organ_router.py     # Individual organs
│   └── insight_router.py   # Insights management
├── organs/
│   ├── base_organ.py
│   ├── governance_brain.py
│   ├── emergency_response.py
│   ├── impact_oracle.py
│   ├── scenario_creator.py
│   ├── risk_advisor.py
│   ├── compliance_guardian.py
│   ├── performance_analyst.py
│   ├── learning_coach.py
│   ├── plan_generator.py
│   └── lifecycle_monitor.py
├── llm/
│   └── llm_router.py       # LLM provider routing
└── models/
    └── ai_models.py        # Database models
```

---

## Integration

### Digital Twin (Port 8030)
- Organization state
- Dependencies
- Health metrics

### Domain Intelligence (Port 8020)
- Industry benchmarks
- Standard requirements
- Threat intelligence

### Learning System (Port 8033)
- Exercise patterns
- Competency data

---

## Database

**Schema:** `ai_intelligence`

**Tables:**
- `analysis_sessions` - Full analysis records
- `organ_results` - Individual organ outputs
- `insights` - Actionable insights with acknowledgement tracking

---

## LLM Configuration

**Provider Priority:**
1. Anthropic Claude (`claude-3-5-sonnet-20241022`)
2. OpenAI GPT (`gpt-4-turbo-preview`)
3. Ollama (`llama3.2`)

**Temperature Settings (by organ):**
- Emergency Response: 0.3 (precise)
- Compliance Guardian: 0.4 (accurate)
- Impact Oracle: 0.4 (data-driven)
- Scenario Creator: 0.7 (creative)

---

## Development

### Adding a New Organ

```python
from base_organ import BaseAIOrgan

class MyOrgan(BaseAIOrgan):
    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="My Organ",
            emoji="🎯",
            llm_router=llm_router
        )

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass
```

---

## Monitoring

```bash
# Health check
curl http://localhost:8032/health

# List organs
curl http://localhost:8032/api/ai/organs/organs

# Analysis types
curl http://localhost:8032/api/ai/analysis-types
```

---

## License

Part of ISO-22301 BCM Intelligence Platform
