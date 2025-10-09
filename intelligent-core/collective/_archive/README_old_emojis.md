# Collective Agent Networks

**Innovation Level:** Revolutionary
**Port:** 8032
**Purpose:** Organizations help each other through AI without revealing their identities

## Documentation

All technical documentation is located in the [`docs/`](docs/) folder:
- **[Technical Specification](docs/TECHNICAL_SPECIFICATION.md)** - Complete technical documentation
- **[Architecture](docs/ARCHITECTURE.md)** - Detailed architecture design
- **[Integration Guide](docs/INTEGRATION_COMPLETE.md)** - Integration with platform services
- **[MCP/Partisia Integration](docs/INTEGRATION_MCP_PARTISIA.md)** - Blockchain integration
- **[Analysis and Improvements](docs/ANALYSIS_AND_IMPROVEMENTS.md)** - Critical issues and recommendations

---

## 🎯 THE BREAKTHROUGH IDEA

**Problem:**
- Organization A stuck on BIA problem
- Organization B, C, D already solved it
- But they can't share (confidentiality!)

**Solution:**
- Create temporary **Collective Agent** from B, C, D's experience
- Agent helps A **without revealing** who B, C, D are
- **Full anonymity** + **collective wisdom**

**User Experience:**
```
User: "Struggling with supply chain dependencies in BIA"

Platform: "I've created a Collective Agent from 5 organizations
           that solved this challenge. Chat with it:"

Collective Agent: "Organizations that addressed supply chain
                   complexity typically started with Tier 1
                   suppliers. 3 out of 5 used dependency mapping
                   tools. The common pattern was..."

User: 🤯 "This is AMAZING! But who are these organizations?"

Platform: "That information is anonymous to protect privacy.
           But their collective wisdom is now yours."
```

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│         Collective Agent Networks System                 │
│                  (Port 8032)                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │     Stuck Organization Detector                  │  │
│  │  - No progress for 7+ days                       │  │
│  │  - Multiple validation failures                  │  │
│  │  - Low confidence in AI advice                   │  │
│  │  → Offer collective help                         │  │
│  └──────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │     Collective Agent Creator                     │  │
│  │  - Find orgs that solved problem                 │  │
│  │  - Extract approaches (anonymized)               │  │
│  │  - Create AI agent from synthesis                │  │
│  │  - Agent expires after 7 days                    │  │
│  └──────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │     Anonymous Chat Interface                     │  │
│  │  - User chats with collective agent              │  │
│  │  - Agent NEVER reveals source orgs               │  │
│  │  - Speaks as "organizations that..."            │  │
│  │  - Synthesizes across all experiences           │  │
│  └──────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │     Privacy-Preserving Metrics                   │  │
│  │  - Anonymized benchmarks                         │  │
│  │  - Minimum 5 orgs required                       │  │
│  │  - Aggregate statistics only                     │  │
│  │  - No outlier highlighting                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 PRIVACY ARCHITECTURE

### Multi-Layer Anonymization

```
Original Case:
{
    "org_name": "Memorial Hospital Seattle",
    "processes": [
        {"name": "Emergency Department", "criticality": 9.5}
    ],
    "author": "John Smith, BCM Manager"
}

↓ Layer 1: Organization Anonymization
{
    "org_type": "hospital_200-500_beds",
    "region": "pacific_northwest",
    "processes": [
        {"name": "Emergency Department", "criticality": 9.5}
    ]
}

↓ Layer 2: Aggregation (minimum 5 orgs)
{
    "pattern": "emergency_department_priority",
    "frequency": "4_out_of_5",
    "confidence": 0.8
}

↓ Layer 3: Collective Agent Synthesis
"Organizations that completed BIA typically prioritized
 emergency departments first (4 out of 5 cases)."
```

### Privacy Rules

**Rule 1: Minimum Threshold**
- Need **≥5 organizations** to create collective agent
- Prevents "this is probably Hospital X"

**Rule 2: No Outlier Highlighting**
- Never say "one organization did Y differently"
- Prevents deduction by elimination

**Rule 3: Aggregate Statistics Only**
- "4 out of 5" not "80% including Hospital X"

**Rule 4: No Time Correlation**
- Can't track specific org over time

**Rule 5: Geographic Generalization**
- "Pacific Northwest" not "Seattle"

---

## 🤖 COLLECTIVE AGENT LIFECYCLE

### Phase 1: Creation (When User Stuck)

```python
# Stuck detected
detector.detect_stuck_organization(org_id)

# Find solvers
solvers = case_library.find_organizations_that_solved(
    problem_type="supply_chain_complexity",
    min_success_rate=0.8,
    min_count=5
)

# Create collective agent
agent = create_collective_agent(
    problem_type="supply_chain_complexity",
    approaches=anonymized_approaches,
    requesting_org_id=org_id
)

# Expires in 7 days
agent.expires_at = now() + timedelta(days=7)
```

### Phase 2: Chat (User Interacts)

```python
# User asks question
user_message = "How did you map Tier 2 supplier dependencies?"

# Agent responds (synthesized)
agent_response = """
Organizations that mapped Tier 2 dependencies typically started
with their Tier 1 suppliers and asked them to identify their
critical suppliers. 3 out of 5 used supplier questionnaires,
while 2 conducted workshops. The common challenge was incomplete
data, which they addressed by iterating and setting reasonable
boundaries (e.g., top 80% of spend).
"""
```

### Phase 3: Expiration (Cleanup)

```python
# After 7 days
if agent.expires_at < now():
    archive_conversation(agent.id)
    delete_collective_agent(agent.id)
```

---

## 📊 API ENDPOINTS

### Collective Agents

**Create Agent**
```bash
POST /api/v1/collective-agents/create
{
    "problem_type": "supply_chain_complexity",
    "min_orgs": 5
}

Response:
{
    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
    "source_org_count": 7,
    "expires_at": "2025-10-11T12:00:00"
}
```

**Chat with Agent**
```bash
POST /api/v1/collective-agents/{agent_id}/chat
{
    "message": "How did you map Tier 2 suppliers?"
}

Response:
{
    "message": "Organizations that addressed this...",
    "confidence": 0.85,
    "source_count": 7
}
```

**Get Active Agents**
```bash
GET /api/v1/collective-agents/active

Response:
[
    {
        "agent_id": "...",
        "problem_type": "supply_chain_complexity",
        "source_org_count": 7,
        "expires_at": "2025-10-11T12:00:00"
    }
]
```

### Stuck Detection

**Check if Stuck**
```bash
GET /api/v1/stuck-detection/check

Response:
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
            "title": "Get help from 7 organizations"
        }
    ]
}
```

---

## 🚀 DEPLOYMENT

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
export ANTHROPIC_API_KEY="sk-..."

# Run service
python main.py
```

Service runs on port **8032**

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## 💎 WHY THIS IS REVOLUTIONARY

### 1. **Solves Privacy Paradox**
- Want to share: ✅ (helps others)
- Can't share: ❌ (confidentiality)
- **Solution:** Anonymous collective wisdom

### 2. **Network Effects Without Risk**
- More orgs → more collective knowledge
- No competitive disadvantage
- Everyone benefits
- Incentive to contribute cases

### 3. **Small Orgs Get Big Org Wisdom**
- 50-person clinic learns from 500-bed hospitals
- Anonymously
- No consultant fees
- Instant access

### 4. **Unique Differentiation**
- No competitor does this
- Can't easily copy (requires trust + data)
- Becomes more valuable over time
- Creates moat

---

## 📈 USE CASES

### Use Case 1: Stuck on BIA

```
Scenario: Hospital struggling with dependency mapping for 2 weeks

Platform detects:
- Days in stage: 14 (threshold: 7)
- Progress: 0% in last week
- Confidence: Low

Action:
→ "We noticed you're working on dependency mapping.
   5 similar hospitals solved this challenge.
   Would you like help from their collective experience?"

User accepts:
→ Collective Agent created from 5 hospitals
→ User chats: "How did you identify indirect dependencies?"
→ Agent: "Organizations typically used stakeholder interviews..."

Result: User unstuck, continues BIA successfully
```

### Use Case 2: Benchmarking

```
User: "Is our BIA timeline normal?"

Platform:
→ Finds 12 similar healthcare orgs (anonymized)
→ Calculates statistics:
   - Mean: 45 days
   - Median: 42 days
   - Your estimate: 38 days
→ Shows: "Organizations similar to yours typically
          completed BIA in 42 days (median).
          Your timeline is faster than average."

Privacy preserved:
- Minimum 12 orgs (>>5)
- Aggregate stats only
- No org identification
```

### Use Case 3: Best Practice Discovery

```
User: "What's the best way to engage executives in BCM?"

Platform:
→ Finds 8 successful organizations
→ Creates Collective Agent from their approaches
→ User chats about executive engagement

Agent: "Organizations with strong executive sponsorship
        typically achieved it through business impact
        demonstrations. 5 out of 8 presented specific
        downtime cost scenarios. The common pattern was
        linking BCM to business objectives rather than
        compliance requirements..."

User learns from collective wisdom without knowing sources
```

---

## 🔍 STUCK ORGANIZATION DETECTION

### Detection Signals

```python
Signals:
- days_no_progress > 7: +3 points
- validation_failures > 5: +2 points
- avg_confidence < 0.6: +2 points
- repeated_questions > 3: +1 point
- repeated_doc_reviews > 5: +1 point
- frustration_score > 0.7: +2 points

Threshold: 4+ points = stuck
```

### What Happens When Stuck

1. **Detection:** Platform identifies stuck organization
2. **Analysis:** Finds similar organizations that solved it
3. **Check Privacy:** Ensure ≥5 organizations available
4. **Offer Help:** Notify user about collective agent option
5. **User Accepts:** Create collective agent
6. **Chat:** User gets help from collective wisdom
7. **Resolution:** Organization unstuck, continues successfully

---

## 🎨 UI MOCKUP

### Collective Agent Chat

```
┌─────────────────────────────────────────────────────┐
│ 🤝 Collective Intelligence Agent                    │
│    "Supply Chain Dependency Mapping"                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ This agent represents 5 healthcare organizations   │
│ that successfully solved this challenge.           │
│                                                     │
│ Source: Anonymous (privacy protected)              │
│ Expires: Oct 11, 2025                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ You: How did you map Tier 2 supplier dependencies? │
│                                                     │
│ Agent: Organizations that addressed this typically │
│        started with Tier 1 suppliers and asked     │
│        them to identify their critical suppliers.  │
│        3 out of 5 used supplier questionnaires...  │
│                                                     │
├─────────────────────────────────────────────────────┤
│ [Type your question...]                    [Send] │
└─────────────────────────────────────────────────────┘

💡 This agent will expire in 5 days
📊 Based on 5 organizations' collective experience
🔒 Fully anonymous - source organizations protected
```

---

## 📦 FILES

```
collective/
├── main.py                          # FastAPI application
├── config.py                        # Configuration
├── dependencies.py                  # Dependency injection
├── requirements.txt                 # Python dependencies
├── ARCHITECTURE.md                  # Detailed architecture
├── README.md                        # This file
│
├── services/
│   ├── collective_agent_service.py  # Agent creation & chat (550 lines)
│   ├── stuck_detector_service.py    # Stuck detection logic (500 lines)
│   └── anonymizer_service.py        # Privacy anonymization (450 lines)
│
├── api/
│   ├── collective_agents.py         # Agent endpoints
│   └── stuck_detection.py           # Detection endpoints
│
└── models/
    └── database.py                  # Database models
```

---

**Ready to build the future!** 🚀🤝✨
