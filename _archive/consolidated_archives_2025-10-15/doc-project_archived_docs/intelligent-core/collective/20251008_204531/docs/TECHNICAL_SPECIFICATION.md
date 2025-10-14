# Collective Agent Networks - Technical Specification

**Version:** 1.0.0
**Port:** 8032
**Status:** Production Ready

---

## Overview

Collective Agent Networks enables anonymous collaboration between organizations by creating temporary AI agents synthesized from multiple organizations' successful experiences. Organizations get collective wisdom without revealing identities.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│         Collective Agent Networks                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Services Layer:                                    │
│  ├── Stuck Detector Service                        │
│  ├── Collective Agent Service                      │
│  ├── Anonymizer Service                            │
│  ├── Case Library Bridge                           │
│  └── LLM Client (Anthropic)                        │
│                                                     │
│  API Layer:                                         │
│  ├── /collective-agents/*                          │
│  └── /stuck-detection/*                            │
│                                                     │
│  Data Layer:                                        │
│  ├── PostgreSQL (collective_agents, conversations) │
│  └── Case Library Integration                      │
└─────────────────────────────────────────────────────┘
```

---

## Core Services

### 1. Stuck Detector Service

**Purpose:** Detect when organizations need help

**Detection Signals:**
```python
signals = {
    'days_no_progress': {
        'threshold': 7,
        'weight': 3
    },
    'validation_failures': {
        'threshold': 5,
        'weight': 2
    },
    'avg_confidence': {
        'threshold': 0.6,
        'weight': 2
    },
    'repeated_questions': {
        'threshold': 3,
        'weight': 1
    },
    'frustration_score': {
        'threshold': 0.7,
        'weight': 2
    }
}

# Stuck if total score >= 4
```

**API:**
```python
GET /api/v1/stuck-detection/check
Response: {
    "is_stuck": bool,
    "stuck_score": int,
    "signals": {...},
    "recommendations": [...]
}
```

---

### 2. Collective Agent Service

**Purpose:** Create and manage temporary AI agents from collective wisdom

**Agent Creation Flow:**
```python
1. User stuck (detected or manual request)
2. Find organizations that solved problem
   - min_orgs = 5 (k-anonymity)
   - success_rate >= 0.8
   - similar context (industry, size)
3. Extract anonymized approaches
4. Create AI agent with synthesized knowledge
5. Set expiration (7 days)
6. Return agent_id to user
```

**Agent Structure:**
```python
{
    "agent_id": UUID,
    "problem_type": str,  # e.g. "supply_chain_complexity"
    "source_org_count": int,  # Never reveal specific orgs
    "created_at": timestamp,
    "expires_at": timestamp,  # +7 days
    "conversation_history": [...],
    "privacy_level": "k-anonymous"  # k >= 5
}
```

**Chat Flow:**
```python
POST /api/v1/collective-agents/{agent_id}/chat
Request: {"message": "How did you map Tier 2 suppliers?"}

Processing:
1. Retrieve agent context
2. Synthesize from source experiences
3. Generate response (NEVER reveal source orgs)
4. Store in conversation history
5. Return collective wisdom

Response: {
    "message": "Organizations that addressed this...",
    "confidence": 0.85,
    "source_count": 7  # Count, not identities!
}
```

---

### 3. Anonymizer Service

**Purpose:** Multi-layer privacy-preserving anonymization

**Layer 1: Organization Anonymization**
```python
def anonymize_organization(case):
    return {
        "org_type": generalize_org_type(case['org_name']),
        "size_category": categorize_size(case['size']),
        "region": generalize_region(case['location']),
        "industry": case['industry'],
        # Remove:
        # - org_name
        # - author name
        # - specific dates
        # - any PII
    }
```

**Layer 2: Aggregation**
```python
def aggregate_approaches(cases):
    if len(cases) < 5:
        raise InsufficientDataError("Need >= 5 orgs for k-anonymity")

    patterns = extract_patterns(cases)

    return {
        "common_approaches": [
            {
                "approach": "stakeholder_interviews",
                "frequency": "5_out_of_7",  # Vague counts
                "effectiveness": 0.85
            }
        ],
        "challenges": [...],
        "success_factors": [...]
    }
```

**Layer 3: Synthesis**
```python
def synthesize_collective_wisdom(patterns):
    # AI generates natural language
    # NEVER mentions specific organizations
    # Uses phrases like:
    # - "Organizations that..."
    # - "Most organizations..."
    # - "The common pattern was..."

    return llm.generate(
        prompt=create_synthesis_prompt(patterns),
        instructions=PRIVACY_INSTRUCTIONS
    )

PRIVACY_INSTRUCTIONS = """
CRITICAL: NEVER reveal source organizations.
Speak in aggregate terms:
- "5 out of 7 organizations..."
- "The common approach was..."
- "Organizations typically..."

NEVER say:
- "Hospital X did..."
- "One organization uniquely..."
- Anything that could identify specific org
"""
```

---

## Privacy Architecture

### K-Anonymity Guarantee

**Minimum Threshold:**
- Require >= 5 organizations for any collective agent
- Prevents "this is probably Organization X"

**Implementation:**
```python
class CollectiveAgentCreator:
    def __init__(self):
        self.k_anonymity = 5  # Minimum organizations

    async def create_agent(self, problem_type: str):
        # Find organizations
        solvers = await self.find_solvers(problem_type)

        if len(solvers) < self.k_anonymity:
            raise InsufficientDataError(
                f"Need >= {self.k_anonymity} organizations "
                f"(found {len(solvers)})"
            )

        # Proceed with creation
        ...
```

### No Outlier Highlighting

**Rule:** Never highlight what 1 org did differently

**Bad Example (revealing):**
```
"4 organizations used interviews,
 but one organization used automated tools"
→ User might deduce which org was different
```

**Good Example (privacy-preserving):**
```
"Organizations used a mix of approaches:
 stakeholder interviews (most common),
 and automated dependency mapping tools"
→ No way to identify specific org
```

### Geographic Generalization

**Mapping:**
```python
REGION_GENERALIZATION = {
    "Seattle": "Pacific Northwest",
    "Portland": "Pacific Northwest",
    "San Francisco": "West Coast",
    "Los Angeles": "West Coast",
    "Boston": "Northeast",
    # Never reveal city-level
}
```

---

## Database Schema

```sql
-- Collective Agents
CREATE TABLE collective_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_type TEXT NOT NULL,
    source_org_count INT NOT NULL,  -- Count only, not IDs!
    created_for_org_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    privacy_level TEXT DEFAULT 'k-anonymous',
    status TEXT DEFAULT 'active'  -- active, expired, archived
);

-- Conversations (stored for quality improvement)
CREATE TABLE agent_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES collective_agents(id),
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Stuck Detection Logs
CREATE TABLE stuck_detection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL,
    stuck_score INT NOT NULL,
    signals JSONB NOT NULL,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    action_taken TEXT  -- offered_help, agent_created, ignored
);
```

---

## API Reference

### Collective Agents

#### Create Agent
```http
POST /api/v1/collective-agents/create
Content-Type: application/json

{
    "problem_type": "supply_chain_complexity",
    "min_orgs": 5,
    "context": {
        "industry": "healthcare",
        "size": "200-500"
    }
}

Response 201:
{
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "source_org_count": 7,
    "expires_at": "2025-10-12T12:00:00Z",
    "problem_type": "supply_chain_complexity"
}

Response 400:
{
    "error": "insufficient_data",
    "message": "Need >= 5 organizations (found 3)"
}
```

#### Chat with Agent
```http
POST /api/v1/collective-agents/{agent_id}/chat
Content-Type: application/json

{
    "message": "How did you map Tier 2 supplier dependencies?"
}

Response 200:
{
    "message": "Organizations that addressed this typically...",
    "confidence": 0.85,
    "source_count": 7
}

Response 404:
{
    "error": "agent_not_found",
    "message": "Agent expired or does not exist"
}
```

#### Get Active Agents
```http
GET /api/v1/collective-agents/active

Response 200:
[
    {
        "agent_id": "...",
        "problem_type": "supply_chain_complexity",
        "source_org_count": 7,
        "created_at": "2025-10-05T12:00:00Z",
        "expires_at": "2025-10-12T12:00:00Z"
    }
]
```

### Stuck Detection

#### Check if Stuck
```http
GET /api/v1/stuck-detection/check?org_id={org_id}

Response 200:
{
    "is_stuck": true,
    "stuck_score": 5,
    "signals": {
        "days_no_progress": 10,
        "validation_failures": 7,
        "avg_confidence": 0.45
    },
    "recommendations": [
        {
            "type": "collective_agent",
            "title": "Get help from 7 organizations",
            "problem_type": "supply_chain_complexity"
        }
    ]
}
```

---

## Configuration

```python
# config.py
class Settings(BaseSettings):
    # Service
    PORT: int = 8032
    DEBUG: bool = False

    # Privacy
    K_ANONYMITY: int = 5  # Minimum organizations
    MAX_RISK_SCORE: float = 0.2  # Privacy risk threshold
    AGENT_EXPIRATION_DAYS: int = 7

    # Database
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # AI
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # Integration
    CASE_LIBRARY_URL: str = "http://localhost:8032"

    # Stuck Detection
    STUCK_DETECTION_THRESHOLD: int = 4
    STUCK_CHECK_INTERVAL_HOURS: int = 24

    class Config:
        env_file = ".env"
```

---

## Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export DATABASE_URL="postgresql://..."
export ANTHROPIC_API_KEY="sk-..."

# Run
python main.py
# → http://localhost:8032
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
ANTHROPIC_API_KEY=sk-xxx

# Optional
PORT=8032
K_ANONYMITY=5
AGENT_EXPIRATION_DAYS=7
STUCK_DETECTION_THRESHOLD=4
```

---

## Metrics & Monitoring

**Key Metrics:**
- Active collective agents count
- Agent creation success rate
- Average source org count per agent
- Stuck organizations detected
- Privacy violations (should be 0!)
- Agent expiration rate

**Privacy Monitoring:**
- Ensure all agents have >= k sources
- Monitor for outlier highlighting attempts
- Check geographic generalization compliance

---

## Security Considerations

**Privacy Threats:**
1. **Re-identification:** Mitigated by k-anonymity (>= 5 orgs)
2. **Outlier highlighting:** Prevented by aggregation rules
3. **Time correlation:** No timestamps in responses
4. **Deduction by elimination:** Geographic generalization

**Countermeasures:**
- Strict k-anonymity enforcement
- LLM instructions for privacy
- Multi-layer anonymization
- Agent expiration (limit exposure)

---

**Status:** ✅ Production Ready with strong privacy guarantees
