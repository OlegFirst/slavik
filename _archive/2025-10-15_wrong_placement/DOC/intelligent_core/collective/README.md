# Collective Intelligence Agent Networks

**Type**: Core Module
**Domain**: Intelligent-Core
**Status**: Active
**Version**: 1.0.0
**Port**: 8034

## Overview

Collective Intelligence Agent Networks enables privacy-preserving knowledge sharing across organizations by creating temporary AI agents synthesized from anonymized experiences of multiple organizations that successfully solved similar challenges. The module implements k-anonymity principles (minimum k=5) to ensure complete organizational privacy while enabling collective wisdom transfer.

This module transforms individual organizational struggles into collective learning opportunities, allowing organizations to benefit from proven solutions without compromising confidentiality or competitive information.

## Architecture

### Core Components

1. **Stuck Organization Detector** - Identifies organizations requiring assistance based on progress metrics
2. **Collective Agent Creator** - Synthesizes anonymous collective wisdom agents from successful cases
3. **Privacy-Preserving Anonymizer** - Multi-layer anonymization with k-anonymity guarantees
4. **Agent Chat Interface** - Conversational interface maintaining source anonymity
5. **Case Library Integration** - Connects to community intelligence for solver identification

### Key Features

- **Automatic Stuck Detection**: 7-day progress monitoring with multi-signal scoring
- **k-anonymity Guarantee**: Minimum 5 organizations required for agent creation
- **Multi-Layer Anonymization**: 4-layer privacy protection (organization, journey, pattern, metrics)
- **Temporary Agents**: 7-day lifespan with automatic expiration and cleanup
- **Aggregate Statistics**: Statistical framing without source attribution
- **Success-Driven Selection**: 80%+ success rate requirement for source cases

## Technical Architecture

```
Collective Intelligence (Port 8034)
├── Stuck Detection
│   ├── Progress Monitoring
│   ├── Signal Aggregation (6 signals)
│   ├── Scoring Engine (threshold: 4+)
│   └── Recommendation Generator
│
├── Collective Agent Creation
│   ├── Case Library Query (min 5 cases)
│   ├── Success Rate Validation (≥80%)
│   ├── Multi-Layer Anonymization
│   ├── Pattern Synthesis
│   └── LLM Agent Configuration
│
├── Privacy System
│   ├── Organization Anonymization
│   ├── Journey Anonymization
│   ├── Pattern Anonymization
│   ├── Metric Anonymization
│   └── Re-identification Risk Scoring
│
└── Chat Interface
    ├── Agent Session Management
    ├── Message Processing
    ├── Statistical Framing
    └── Source Protection
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (for case library access)
- Redis 6+ (for session management)
- Anthropic API key (for agent LLM)

### Setup

```bash
# Navigate to module directory
cd intelligent-core/collective

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm_platform
REDIS_URL=redis://localhost:6379

# AI Foundation
ANTHROPIC_API_KEY=your_api_key
AI_FOUNDATION_URL=http://localhost:8025

# EventBus
EVENTBUS_URL=http://localhost:8001

# Privacy Settings
MIN_ORGS_FOR_AGENT=5  # k-anonymity threshold
MAX_RISK_SCORE=0.3    # Re-identification risk threshold
AGENT_EXPIRY_DAYS=7   # Agent lifespan
```

## Usage

### Starting the Service

```bash
# Run service
python -m collective.main

# Or with uvicorn
uvicorn collective.main:app --host 0.0.0.0 --port 8034
```

The service will start on `http://localhost:8034`

### API Documentation

Interactive API documentation:
- **Swagger UI**: http://localhost:8034/docs
- **ReDoc**: http://localhost:8034/redoc

### Example Usage

**Check if Organization is Stuck**
```bash
curl http://localhost:8034/api/v1/stuck-detection/check?module=bia
```

**Create Collective Agent**
```bash
curl -X POST http://localhost:8034/api/v1/collective-agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "problem_type": "supply_chain_complexity",
    "min_orgs": 5
  }'
```

**Chat with Collective Agent**
```bash
curl -X POST http://localhost:8034/api/v1/collective-agents/{agent_id}/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How did you map Tier 2 supplier dependencies?"
  }'
```

## API Reference

See [API.md](API.md) for complete API documentation.

### Stuck Detection Endpoints

```
GET  /api/v1/stuck-detection/check              # Check stuck status
POST /api/v1/stuck-detection/accept-help        # Accept collective help
GET  /api/v1/stuck-detection/signals/{org_id}   # Get stuck signals
```

### Collective Agent Endpoints

```
POST /api/v1/collective-agents/create           # Create agent
POST /api/v1/collective-agents/{id}/chat        # Chat with agent
GET  /api/v1/collective-agents/{id}             # Get agent details
GET  /api/v1/collective-agents/active           # List active agents
DELETE /api/v1/collective-agents/{id}           # Expire agent early
```

### Privacy Endpoints

```
POST /api/v1/privacy/anonymize                  # Test anonymization
POST /api/v1/privacy/risk-score                 # Calculate risk score
GET  /api/v1/privacy/stats                      # Privacy statistics
```

## Dependencies

### Internal Dependencies

- `shared.event_bus` - Event publishing and subscription
- `shared.database` - Database connection management
- `ai-foundation` - LLM routing for agent conversations
- `community_intelligence.case_library` - Case repository access

### External Dependencies

- **Anthropic Claude** (3.5+) - Agent conversation LLM
- **FastAPI** (0.100.0+) - API framework
- **SQLAlchemy** (2.0+) - Database ORM
- **Pydantic** (2.0+) - Data validation
- **httpx** - Async HTTP client

## Stuck Detection

### Detection Signals (6 Total)

1. **Days No Progress** (threshold: 7 days) - +3 points
2. **Validation Failures** (threshold: 5 failures) - +2 points
3. **Low AI Confidence** (avg < 0.6) - +2 points
4. **Repeated Questions** (threshold: 3 repeats) - +1 point
5. **Document Review Cycles** (threshold: 5 cycles) - +1 point
6. **Frustration Score** (score > 0.7) - +2 points

### Stuck Scoring

- **Score 0-3**: On track
- **Score 4-6**: Stuck, collective help recommended
- **Score 7+**: Seriously stuck, immediate intervention

## Privacy Architecture

### k-anonymity Implementation

**Requirement**: Minimum 5 organizations with similar problem solutions

**Guarantee**: Individual organizations cannot be identified from agent responses

**Validation**: Automated check before agent creation

### Multi-Layer Anonymization

**Layer 1: Organization Anonymization**
- Remove: Names, locations, specific employee counts, department terms
- Keep: Industry category, size category, region, maturity level

**Layer 2: Journey Anonymization**
- Remove: Specific dates, exact durations, tool names
- Keep: Quarter/year, duration categories, tool categories

**Layer 3: Pattern Anonymization**
- Remove: Person names, specific products, organization terms
- Keep: General approaches, method descriptions, pattern structures

**Layer 4: Metric Anonymization**
- Round values to prevent fingerprinting
- Use ranges instead of exact values
- Maintain relative comparisons

### Re-identification Risk Scoring

```python
risk_score = (
    k_anonymity_factor +
    unique_attributes_factor +
    specific_metrics_factor +
    temporal_proximity_factor
) / 4

# Safe if risk_score ≤ 0.3
```

## Collective Agent Lifecycle

### Phase 1: Creation

1. Organization detected as stuck (score ≥ 4)
2. Platform queries case library for solvers (min 5, success rate ≥80%)
3. Multi-layer anonymization applied to all source cases
4. Risk score calculated and validated (≤0.3)
5. LLM agent configured with anonymized collective knowledge
6. Agent activated with 7-day expiration

### Phase 2: Interaction

1. User submits questions via chat interface
2. Agent responds using statistical framing ("5 out of 7 organizations...")
3. Source attribution strictly prevented by system prompts
4. All conversations logged for privacy audit
5. Agent maintains consistency across conversation

### Phase 3: Expiration

1. After 7 days, agent automatically expires
2. Conversation archived (anonymized)
3. Agent deleted from active pool
4. Statistics captured for effectiveness measurement

## Standards Compliance

### Privacy Standards

- **k-anonymity**: Minimum k=5 for all collective agents
- **GDPR**: No personally identifiable information in agent data
- **Data Minimization**: Only essential anonymized patterns stored
- **Right to Erasure**: Source organizations can request removal

### ISO 22301 Integration

- **Clause 7.4**: Knowledge management via collective wisdom
- **Clause 10.2**: Continuous improvement through shared learning
- **Confidentiality**: Maintains organizational confidentiality while sharing knowledge

## Performance

### Benchmarks

- **Stuck Detection**: <100ms (P95)
- **Agent Creation**: <5s (includes case query + anonymization)
- **Chat Response**: <2s (Claude Sonnet 3.5)
- **Risk Scoring**: <200ms (P95)

### Scalability

- **Concurrent Agents**: 1000+ active agents supported
- **Agent Pool**: Redis-backed session management
- **Case Library**: Indexed PostgreSQL queries
- **LLM**: Anthropic API rate limits apply

## Monitoring

### Health Checks

```bash
# Service health
curl http://localhost:8034/health

# Detailed metrics
curl http://localhost:8034/health/detailed
```

### Metrics

Prometheus metrics at `/metrics`:

- `collective_agents_created_total` - Total agents created
- `collective_agents_active` - Currently active agents
- `collective_chat_messages_total` - Total chat messages processed
- `collective_stuck_detections_total` - Stuck organizations detected
- `collective_privacy_violations_total` - Privacy violations detected

### Logging

```
2025-10-09 12:00:00 - collective - INFO - Stuck detected: org_id=abc123, score=5
2025-10-09 12:01:00 - collective - INFO - Agent created: agent_id=xyz789, sources=7
2025-10-09 12:02:00 - collective - INFO - Chat message: agent_id=xyz789, message_count=3
```

## Use Cases

### Use Case 1: BIA Dependency Mapping Struggle

```
Scenario: Organization stuck for 14 days on supply chain mapping
Detection: Score = 6 (days:3, failures:2, confidence:2)
Action: Create collective agent from 7 healthcare organizations
Result: User learns phased approach, completes mapping in 3 days
Privacy: Source organizations never revealed
```

### Use Case 2: Executive Engagement Challenge

```
Scenario: Organization struggling to secure executive sponsorship
Detection: Repeated questions on same topic
Action: Agent synthesizes 8 successful executive engagement patterns
Result: Statistical guidance ("5 out of 8 used business impact demos")
Privacy: No individual organization's approach identified
```

### Use Case 3: Benchmarking Progress

```
Scenario: User asks "Is my BIA timeline normal?"
Response: Collective agent shows anonymized aggregate statistics
Data: 12 similar organizations, median 42 days, your 38 days
Privacy: Minimum 12 orgs (>>5), aggregate stats only
```

## Documentation

### Technical Documentation

- [Technical Specification](docs/TECHNICAL_SPECIFICATION.md) - Complete specifications
- [Architecture](docs/ARCHITECTURE.md) - Detailed architecture design
- [Integration Guide](docs/INTEGRATION_COMPLETE.md) - Platform integration
- [Privacy Implementation](docs/PRIVACY.md) - Privacy architecture details

## Troubleshooting

### Agent Creation Fails (Insufficient Cases)

```
Error: "Need minimum 5 organizations, found 3"
Solution: Expand search criteria or wait for more case submissions
```

### High Privacy Risk Score

```
Error: "Risk score 0.42 exceeds threshold 0.3"
Solution: Increase anonymization level or require more source organizations
```

### Agent Not Responding

```
Check: Agent expiration (7-day limit)
Check: LLM API availability (Anthropic)
Check: Agent session in Redis
```

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-09
**Maintainer**: AI Platform Team
**Contact**: Technical support via internal channels

---

## Quick Links

- **Service Health**: http://localhost:8034/health
- **API Docs**: http://localhost:8034/docs
- **Metrics**: http://localhost:8034/metrics
