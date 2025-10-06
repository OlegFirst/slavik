# Risk Office - Complete BCM Risk Management Module

## Architecture

Risk Office is a **modular BCM service** that integrates all AI components:

```
┌─────────────────────────────────────────────────────────┐
│                    RiskService                          │
│                  (Main Orchestrator)                    │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ RiskWorkflow │ │  RiskExpert  │ │RiskSpecialist│
│  (workflow_  │ │ (business    │ │ (dialogue)   │
│intelligence) │ │  logic)      │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        │         ┌─────┴─────┐         │
        │         ▼           ▼         │
        │   ┌──────────┐ ┌──────────┐  │
        │   │RiskOrgan │ │RiskTools │  │
        │   │  (LLM)   │ │   (DB)   │  │
        │   └──────────┘ └──────────┘  │
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
                  ┌──────────┐
                  │ EventBus │
                  └──────────┘
```

## Features

- **Guided Risk Workflow**: NOT_STARTED → IDENTIFY_RISKS → ANALYZE_LIKELIHOOD → CALCULATE_IMPACT → FAIR_ANALYSIS → TREATMENT_PLANNING → COMPLETED
- **FAIR Methodology**: TEF × LM = ALE (Factor Analysis of Information Risk)
- **AI-Powered Analysis**: LLM-based risk identification, likelihood, impact, and treatment recommendations
- **Industry Benchmarks**: Uses Case Library for similar cases and benchmarks
- **Event-Driven**: Publishes events to EventBus for inter-office communication
- **Conversational + Direct API**: Chat interface for users, direct API for programmatic access

## Quick Start

### 1. Initialize Service

```python
from bcm_offices.risk import RiskService

service = RiskService(
    db_session=supabase_client,
    llm_router=llm_router,
    event_bus=event_bus,
    org_context={
        'org_id': 'org_123',
        'industry': 'fintech',
        'size': 'medium',
        'revenue': 50_000_000,
        'risk_appetite': 'medium',
        'risk_budget': 500_000
    }
)
```

### 2. Chat Interface (Conversational)

```python
# User asks in natural language
response = await service.chat(
    message="Help me identify risks for our payment processing system",
    context={
        'process_id': 'proc_payment_123'
    }
)

print(response['message'])
# ✅ Identified 7 risks for the process.

print(response['next_step'])
# Would you like to analyze the likelihood of these risks?

# Continue conversation
response = await service.chat(
    message="Yes, analyze likelihood",
    context={
        'process_id': 'proc_payment_123'
    }
)
```

### 3. Direct API (Programmatic)

```python
# Step 1: Identify risks
result = await service.identify_risks(
    process_id='proc_payment_123',
    user_input="Payment processing in fintech"
)

risk_ids = result['risk_ids']
# ['risk_001', 'risk_002', 'risk_003', ...]

# Step 2: Analyze likelihood
likelihood = await service.analyze_likelihood(risk_ids)

# Step 3: Calculate impact
impact = await service.calculate_impact(risk_ids)

# Step 4: FAIR analysis
fair = await service.fair_analysis(risk_ids)

print(f"Total ALE: ${fair['total_ale']:,.2f}")
# Total ALE: $1,250,000.00

# Step 5: Plan treatments
treatments = await service.plan_treatments(risk_ids)

for risk_id, treatment in treatments['treatments'].items():
    print(f"{risk_id}: {treatment['treatment_type']} - {treatment['priority']}")
# risk_001: reduce - critical
# risk_002: accept - low
# risk_003: transfer - high
```

## Workflow Stages

### 1. NOT_STARTED → IDENTIFY_RISKS

**Requirements**: Start workflow

**Actions**:
- Identify business process to analyze
- AI suggests risks based on process type, industry, dependencies

**Output**: List of identified risks with threat, vulnerability, category

---

### 2. IDENTIFY_RISKS → ANALYZE_LIKELIHOOD

**Requirements**: Minimum 1 risk identified

**Validation**:
- Each risk must have: description, threat, vulnerability

**Actions**:
- Analyze likelihood (1-5 score)
- Estimate frequency (per year/month/week/day)

**Output**: Likelihood scores with reasoning and confidence

---

### 3. ANALYZE_LIKELIHOOD → CALCULATE_IMPACT

**Requirements**: Likelihood scores for all risks

**Validation**:
- Likelihood score must be 1-5

**Actions**:
- Calculate impact across 4 dimensions:
  - Financial (0-100)
  - Operational (0-100)
  - Reputational (0-100)
  - Regulatory (0-100)

**Output**: Impact scores with reasoning

---

### 4. CALCULATE_IMPACT → FAIR_ANALYSIS

**Requirements**: Impact scores for all risks

**Validation**:
- Must have all 4 impact types

**Actions**:
- Calculate FAIR metrics:
  - **TEF** (Threat Event Frequency): events per year
  - **LM** (Loss Magnitude): $ per event
  - **ALE** (Annual Loss Expectancy): TEF × LM

**Output**: FAIR metrics with total ALE

---

### 5. FAIR_ANALYSIS → TREATMENT_PLANNING

**Requirements**: FAIR metrics for all risks

**Validation**:
- TEF × LM must equal ALE

**Actions**:
- Recommend treatments:
  - **REDUCE**: Implement controls (if cost < ALE)
  - **ACCEPT**: Live with risk (if ALE < risk appetite)
  - **TRANSFER**: Insurance, outsourcing (if ALE high but unpredictable)
  - **AVOID**: Eliminate activity (if ALE unacceptable)

**Output**: Treatment plans with actions, cost, expected reduction

---

### 6. TREATMENT_PLANNING → REVIEW_RESULTS

**Requirements**: Treatment plans for all risks

**Validation**:
- Treatment type must be: reduce, accept, transfer, avoid
- Must have actions, priority

**Actions**:
- Review all results
- Option to go back to IDENTIFY_RISKS (loop)

**Output**: Complete risk assessment report

---

### 7. REVIEW_RESULTS → COMPLETED

**Requirements**: Review completed

**Actions**:
- Workflow completed
- Results saved to Case Library for learning

**Output**: Assessment complete

---

## Integration with Existing Infrastructure

### Extends `workflow_intelligence`

```python
from workflow_intelligence.core.state_machine import StateMachine

class RiskWorkflow(StateMachine):
    # Inherits:
    # - State transitions with validation
    # - Rollback capability
    # - Audit trail
    # - Event publishing
    pass
```

### Uses `AIContextBuilder`

```python
from workflow_intelligence.integration.ai_context_builder import AIContextBuilder

# Builds full context for AI:
context = await ai_context_builder.build_full_context(org_context, user_message)

# Returns:
{
    "workflow": {...},         # Current workflow state
    "similar_cases": [...],    # From Case Library
    "benchmarks": {...},       # Industry benchmarks
    "comparison": {...},       # Compare to similar orgs
    "trending": [...]          # Common patterns
}
```

### Migrates from `/ai-orchestration/muscles/ai_organs/`

```python
# OLD: risk_advisor.py (standalone LLM organ)
from ai_organs.risk_advisor import RiskAdvisor

# NEW: Integrated into Risk Office
from bcm_offices.risk import RiskOrgan
```

### Uses `/ai_experts/` patterns

```python
# Follows existing Expert pattern:
# - ExpertAgent base class
# - Tools for DB operations
# - RAG pipeline for knowledge retrieval
```

## Event-Driven Integration

### Published Events

```python
# When risks identified
event_bus.publish(
    topic='risk.assessment.risks_identified',
    data={
        'assessment_id': 'assess_123',
        'process_id': 'proc_123',
        'risks_count': 7,
        'risk_ids': ['risk_001', ...]
    }
)

# When FAIR analysis completed
event_bus.publish(
    topic='risk.assessment.fair_completed',
    data={
        'assessment_id': 'assess_123',
        'total_ale': 1250000.0,
        'high_priority_count': 3
    }
)
```

### Subscribed Events

```python
# Auto-trigger risk assessment when critical process created
event_bus.subscribe(
    topic='bia.process.created',
    handler=service._on_process_created
)

# Re-evaluate treatments when risk appetite changes
event_bus.subscribe(
    topic='governance.policy.updated',
    handler=service._on_policy_updated
)
```

## Database Schema

### Tables Used

- `bia.processes` - Business processes (from BIA Office)
- `risk.assessments` - Risk assessments
- `risk.identified_risks` - Identified risks
- `risk.likelihood_scores` - Likelihood analysis
- `risk.impact_assessments` - Impact scores
- `risk.fair_metrics` - FAIR metrics (TEF, LM, ALE)
- `risk.treatments` - Treatment plans

### Example Queries

```sql
-- Get all risks for a process
SELECT r.*, l.score as likelihood, i.financial, i.operational, f.ale
FROM risk.identified_risks r
LEFT JOIN risk.likelihood_scores l ON r.id = l.risk_id
LEFT JOIN risk.impact_assessments i ON r.id = i.risk_id
LEFT JOIN risk.fair_metrics f ON r.id = f.risk_id
WHERE r.process_id = 'proc_123';

-- Get total ALE for organization
SELECT SUM(f.ale) as total_ale
FROM risk.fair_metrics f
JOIN risk.identified_risks r ON f.risk_id = r.id
WHERE r.assessment_id IN (
    SELECT id FROM risk.assessments WHERE org_id = 'org_123'
);
```

## Case Library Learning

Risk Office automatically records successful workflows to Case Library:

```python
# When workflow completes, records:
await case_repository.record_case({
    "industry": "fintech",
    "module": "risk",
    "action_type": "identify_risks",
    "context": {
        "process_type": "payment_processing",
        "process_criticality": "critical"
    },
    "result": {
        "risks_count": 7,
        "categories": ["operational", "technology", "compliance"]
    },
    "success": True
})

# Future assessments use this for benchmarks:
similar_cases = await case_repository.search(
    industry="fintech",
    module="risk",
    action_type="identify_risks",
    limit=5
)
```

## API Reference

### RiskService

#### `chat(message, context, history=None)`

Conversational interface for risk management.

**Args**:
- `message` (str): User message in natural language
- `context` (dict): Context with `process_id`, `org_context`, etc
- `history` (list, optional): Conversation history

**Returns**: Conversational response with action results

---

#### `identify_risks(process_id, user_input=None)`

Identify risks for a business process.

**Args**:
- `process_id` (str): Process to analyze
- `user_input` (str, optional): User description

**Returns**: Dict with `risk_ids`, `recommendations`, `workflow_state`

---

#### `analyze_likelihood(risk_ids)`

Analyze likelihood for identified risks.

**Returns**: Dict with `likelihood_scores`, `recommendations`, `workflow_state`

---

#### `calculate_impact(risk_ids)`

Calculate impact across 4 dimensions.

**Returns**: Dict with `impact_scores`, `recommendations`, `workflow_state`

---

#### `fair_analysis(risk_ids)`

Perform FAIR analysis (TEF × LM = ALE).

**Returns**: Dict with `fair_metrics`, `total_ale`, `recommendations`, `workflow_state`

---

#### `plan_treatments(risk_ids)`

Plan risk treatments (reduce, accept, transfer, avoid).

**Returns**: Dict with `treatments`, `recommendations`, `workflow_state`

---

#### `get_workflow_status()`

Get current workflow status.

**Returns**: Dict with `current_stage`, `available_actions`, `gaps`, `metadata`

---

#### `health_check()`

Check service health.

**Returns**: Dict with component health status

---

## Testing

```python
import pytest
from bcm_offices.risk import RiskService

@pytest.fixture
async def risk_service(supabase_client, llm_router):
    return RiskService(
        db_session=supabase_client,
        llm_router=llm_router,
        org_context={'industry': 'fintech', 'size': 'medium'}
    )

async def test_risk_workflow(risk_service):
    # Identify risks
    result = await risk_service.identify_risks('proc_123')
    assert result['success'] == True
    assert len(result['risk_ids']) > 0

    # Analyze likelihood
    likelihood = await risk_service.analyze_likelihood(result['risk_ids'])
    assert likelihood['success'] == True

    # Calculate impact
    impact = await risk_service.calculate_impact(result['risk_ids'])
    assert impact['success'] == True

    # FAIR analysis
    fair = await risk_service.fair_analysis(result['risk_ids'])
    assert fair['success'] == True
    assert fair['total_ale'] > 0

    # Plan treatments
    treatments = await risk_service.plan_treatments(result['risk_ids'])
    assert treatments['success'] == True
```

## Next Steps

### Create Remaining 9 Offices

Use Risk Office as template:

1. **BIA Office** - Business Impact Analysis
2. **Compliance Office** - ISO 22301 compliance
3. **Governance Office** - Policies and procedures
4. **Emergency Office** - Incident response
5. **Planning Office** - BCP/DRP/IRP planning
6. **Performance Office** - KPIs and monitoring
7. **Learning Office** - Training and exercises
8. **Scenario Office** - Scenario generation
9. **Lifecycle Office** - Continuous improvement

Each office follows same pattern:
- Workflow (extends StateMachine)
- Expert (business logic)
- Specialist (dialogue)
- Organ (LLM)
- Tools (DB)
- Service (orchestrator)
