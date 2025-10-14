# Expertise Center Service - Deployment Guide

## Overview

Expertise Center Service provides REST API access to:
- **12 Tactical Assistants** (BIA, Risk, Compliance, etc.)
- **10 Strategic Analyzers** (Compliance, Risk, Governance, etc.)
- **Multi-Expert Collaboration**
- **Knowledge Base Integration**

**Port:** 8035
**Version:** 1.0.0
**Status:** Production Ready ✅

---

## Quick Start

### 1. Local Development

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise-center/service

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run service
python main.py
```

Service will start on http://localhost:8035

### 2. Docker Deployment

```bash
# Build image
docker build -t expertise-center:latest -f Dockerfile ../..

# Run container
docker run -d \
  --name expertise-center \
  -p 8035:8035 \
  -e AI_FOUNDATION_URL=http://ai-foundation:8040 \
  expertise-center:latest
```

### 3. Docker Compose

```bash
# Start with dependencies
docker-compose up -d

# Start standalone
docker-compose up expertise-center
```

---

## API Endpoints

### Health & Info

```bash
# Health check
GET /health

# Service info
GET /expertise/info

# List all experts
GET /expertise/experts

# Get specific expert
GET /expertise/experts/{expert_id}
```

### Tactical Assistants

```bash
# BIA Specialist
POST /expertise/tactical/bia/analyze

# Risk Analyst
POST /expertise/tactical/risk/assess

# Compliance Copilot
POST /expertise/tactical/compliance/check

# Incident Advisor
POST /expertise/tactical/incident/advise

# Plan Generator
POST /expertise/tactical/plan/generate

# Exercise Designer
POST /expertise/tactical/exercise/design

# Project Manager
POST /expertise/tactical/project/manage

# Documents Specialist
POST /expertise/tactical/documents/create

# Governance Specialist
POST /expertise/tactical/governance/analyze

# Learning Specialist
POST /expertise/tactical/learning/design

# Validation Specialist
POST /expertise/tactical/validation/validate

# Community Specialist
POST /expertise/tactical/community/engage
```

### Strategic Analyzers

```bash
# Compliance Analyzer
POST /expertise/analyzers/compliance/analyze

# Risk Analyzer
POST /expertise/analyzers/risk/analyze

# Governance Analyzer
POST /expertise/analyzers/governance/analyze

# Lifecycle Analyzer
POST /expertise/analyzers/lifecycle/analyze

# Learning Analyzer
POST /expertise/analyzers/learning/analyze

# Performance Analyzer
POST /expertise/analyzers/performance/analyze

# Emergency Analyzer
POST /expertise/analyzers/emergency/analyze

# Impact Analyzer
POST /expertise/analyzers/impact/analyze

# Plan Analyzer
POST /expertise/analyzers/plan/analyze

# Scenario Analyzer
POST /expertise/analyzers/scenario/analyze
```

### Generic Expert Query

```bash
POST /expertise/query
{
  "expert_type": "bia_specialist",
  "query": "What are critical processes for healthcare?",
  "context": {"industry": "healthcare"},
  "organization_id": "org_123"
}
```

---

## Temporal Workflows

Expertise Center integrates with Temporal for durable workflows:

```python
from workflow_intelligence.temporal_workflows import ExpertiseWorkflow

# Single expert query
await client.execute_workflow(
    ExpertiseWorkflow.run,
    {
        "workflow_type": "single_expert",
        "expert_type": "bia_specialist",
        "query": "Analyze critical processes",
        "organization_id": "org_123"
    },
    id="expertise-single-001",
    task_queue="expertise-tasks"
)

# Multi-expert collaboration
await client.execute_workflow(
    ExpertiseWorkflow.run,
    {
        "workflow_type": "multi_expert",
        "experts": ["bia_specialist", "risk_analyst", "compliance_copilot"],
        "query": "Comprehensive BCM assessment",
        "organization_id": "org_123"
    },
    id="expertise-multi-001",
    task_queue="expertise-tasks"
)

# Expert + Analyzer
await client.execute_workflow(
    ExpertiseWorkflow.run,
    {
        "workflow_type": "expert_analyzer",
        "expert_type": "risk_analyst",
        "analyzer_type": "compliance_analyzer",
        "query": "Risk assessment with compliance check",
        "organization_id": "org_123"
    },
    id="expertise-analyzer-001",
    task_queue="expertise-tasks"
)

# Full analysis
await client.execute_workflow(
    ExpertiseWorkflow.run,
    {
        "workflow_type": "full_analysis",
        "experts": ["bia_specialist", "risk_analyst"],
        "analyzers": ["compliance_analyzer", "governance_analyzer"],
        "query": "Complete BCM program assessment",
        "organization_id": "org_123"
    },
    id="expertise-full-001",
    task_queue="expertise-tasks"
)
```

**Workflow Features:**
- ✅ Durable execution (survives restarts)
- ✅ Automatic retries
- ✅ Multi-expert collaboration
- ✅ Knowledge validation
- ✅ Actionable recommendations
- ✅ Progress tracking

---

## Configuration

### Environment Variables

```bash
# Service
EXPERTISE_CENTER_PORT=8035
EXPERTISE_CENTER_HOST=0.0.0.0
LOG_LEVEL=INFO
WORKERS=1

# AI Foundation
AI_FOUNDATION_URL=http://localhost:8040
KNOWLEDGE_BASE_URL=http://localhost:8040

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/expertise_center

# EventBus (optional)
EVENTBUS_ENABLED=false
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5673

# CORS
CORS_ORIGINS=*

# Monitoring
PROMETHEUS_ENABLED=true
OPENTELEMETRY_ENABLED=true

# AI Models
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key

# Performance
MAX_CONCURRENT_QUERIES=10
QUERY_TIMEOUT=30
CACHE_TTL=300
```

---

## Monitoring

### Prometheus Metrics

Available at: http://localhost:8035/metrics

Key metrics:
- `expertise_queries_total` - Total queries processed
- `expertise_query_duration_seconds` - Query latency
- `expertise_expert_invocations_total` - Expert usage
- `expertise_analyzer_runs_total` - Analyzer usage
- `expertise_errors_total` - Error count

### Health Checks

```bash
# Basic health
curl http://localhost:8035/health

# Detailed status
curl http://localhost:8035/expertise/info
```

---

## Integration

### From AI Orchestrator

```python
from intelligent_core.orchestration.ai_orchestration.orchestrator import AIOrchestrator

orchestrator = AIOrchestrator()

# Query expert
result = await orchestrator.execute_task({
    "type": "expertise_query",
    "expert": "bia_specialist",
    "query": "Identify critical processes",
    "organization_id": "org_123"
})
```

### From Other Services

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8035/expertise/query",
        json={
            "expert_type": "compliance_copilot",
            "query": "Check ISO 22301 compliance",
            "context": {"standard": "iso22301"}
        }
    )
    result = response.json()
```

---

## Testing

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise-center/service
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=service --cov-report=html

# Test specific endpoint
pytest tests/test_tactical.py::test_bia_specialist -v
```

---

## Troubleshooting

### Import Errors

If you see import errors:

```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO/intelligent-core:$PYTHONPATH

# Or add to .env
PYTHONPATH=/Users/MD/AI-Platform-ISO/intelligent-core
```

### AI Foundation Connection

Ensure AI Foundation is running:

```bash
# Check AI Foundation
curl http://localhost:8040/health

# Update URL in .env
AI_FOUNDATION_URL=http://localhost:8040
```

### Port Conflicts

If port 8035 is in use:

```bash
# Change port in .env
EXPERTISE_CENTER_PORT=8036

# Or use environment variable
EXPERTISE_CENTER_PORT=8036 python main.py
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│     Expertise Center Service (8035)     │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   REST API (FastAPI)             │  │
│  │   - /expertise/tactical/*        │  │
│  │   - /expertise/analyzers/*       │  │
│  │   - /expertise/query             │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   12 Tactical Assistants         │  │
│  │   - BIA Specialist               │  │
│  │   - Risk Analyst                 │  │
│  │   - Compliance Copilot           │  │
│  │   - ... (9 more)                 │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   10 Strategic Analyzers         │  │
│  │   - Compliance Analyzer          │  │
│  │   - Risk Analyzer                │  │
│  │   - Governance Analyzer          │  │
│  │   - ... (7 more)                 │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      AI Foundation (8040)               │
│      - RAG Pipeline                     │
│      - LLM Router                       │
│      - Embeddings                       │
│      - Knowledge Base                   │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│   Temporal Workflows                    │
│   - ExpertiseWorkflow                   │
│   - Single/Multi Expert                 │
│   - Expert + Analyzer                   │
│   - Full Analysis                       │
└─────────────────────────────────────────┘
```

---

## Next Steps

1. **Start Service:**
   ```bash
   cd service
   python main.py
   ```

2. **Test API:**
   ```bash
   curl http://localhost:8035/health
   curl http://localhost:8035/expertise/info
   ```

3. **Query Expert:**
   ```bash
   curl -X POST http://localhost:8035/expertise/query \
     -H "Content-Type: application/json" \
     -d '{
       "expert_type": "bia_specialist",
       "query": "What are critical processes?",
       "context": {"industry": "healthcare"}
     }'
   ```

4. **View Documentation:**
   - Swagger: http://localhost:8035/docs
   - ReDoc: http://localhost:8035/redoc

---

## Support

**Issues:** Report at GitHub Issues
**Documentation:** See `/docs` endpoint
**Status:** Production Ready ✅

---

**Last Updated:** 2025-10-08
**Version:** 1.0.0
**Maintainer:** BCM Platform Team
