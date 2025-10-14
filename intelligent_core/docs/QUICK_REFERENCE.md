# INTELLIGENT CORE - QUICK REFERENCE

**Version:** 2.0.0 | **Updated:** 2025-10-08

---

## 🎯 Quick Overview

The Intelligent Core is the "brain" of the AI-Platform-ISO system with **12 core modules** providing AI, orchestration, workflow management, expertise, and predictive capabilities.

**Total:** 114,142 LOC | 481 Python files | 332+ API endpoints | 664 classes

---

## 🔌 Service Ports & Status

| Port | Service | Status | Purpose |
|------|---------|--------|---------|
| **8030** | ai-orchestration | ✅ Running | Main orchestration & decision-making |
| **8031** | predictive | ✅ Running | Predictive analytics & proactive recommendations |
| **8032** | collective | ✅ Running | Privacy-preserving collective intelligence |
| **8034** | coordination-center | 🟡 Active | Intent-to-API translation layer |
| **8035** | expertise-center | 🟡 Active | 22 AI experts & analyzers |
| **8036** | workflow-engine | 🟡 Active | BPMN workflow execution |
| **8037** | workflow_intelligence | 🟡 Active | Main workflow orchestrator (THE BRAIN) |
| **8038** | ai_workflow_optimizer | ✅ Running | ML-powered workflow optimization |
| **8039** | event_intelligence | 🟡 Active | Event analysis & auto-discovery |
| **8040** | ai-foundation | 🟡 Active | Core AI services (LLM, RAG, ML) |
| **8030** | community_intelligence | ⚠️ Conflict | Community knowledge & peer review |

**Legend:** ✅ Running | 🟡 Active (ready for deployment) | ⚠️ Needs attention

---

## 🏗️ Architecture Layers

### Layer 1: Foundation
- **ai-foundation** (8040) - LLM, RAG, embeddings, ML
- **shared** - Platform client, event bus

### Layer 2: Intelligence & Orchestration
- **workflow_intelligence** (8037) - THE BRAIN - workflow orchestration, BPMN, state machines
- **ai_workflow_optimizer** (8038) - ML optimization
- **event_intelligence** (8039) - Event analysis, auto-discovery
- **orchestration** → **ai-orchestration** (8030) - Decision-making, memory, safety
- **orchestration** → **coordination-center** (8034) - Intent translation
- **workflow-engine** (8036) - BPMN execution

### Layer 3: Domain Expertise & Collaboration
- **expertise-center** (8035) - 12 tactical assistants + 10 strategic analyzers
- **community_intelligence** (8030) - Peer review, reputation, case library
- **collective** (8032) - Anonymous collaboration

### Layer 4: Predictive
- **predictive** (8031) - Journey prediction, proactive recommendations

---

## ⚡ Key Services Quick Start

### ai-foundation (Core AI)
```bash
# Port: 8040
# Start service
cd intelligent-core/ai-foundation
python main.py

# Key endpoints
POST /api/v1/llm/route        # Route LLM requests
POST /api/v1/rag/query        # RAG query
GET /health
```

**Dependencies:** PostgreSQL, Redis, Qdrant, Anthropic/OpenAI API keys

---

### workflow_intelligence (THE BRAIN)
```bash
# Port: 8037
# Start service
cd intelligent-core/workflow_intelligence
python main.py

# Key endpoints
POST /api/v1/workflow/start   # Start workflow
POST /cases/add                # Add to case library
POST /analyze                  # ML analysis
GET /health
```

**Dependencies:** PostgreSQL, Redis, RabbitMQ, Temporal, ai-foundation

---

### ai-orchestration (Main Orchestrator)
```bash
# Port: 8030
# Start service
cd intelligent-core/orchestration/ai-orchestration
python main.py

# Key endpoints
GET /api/v1/system/status      # System status
POST /api/v1/ai/agent/process  # AI agent routing
GET /api/v1/ai/decisions       # List decisions
GET /health
```

**Dependencies:** Redis, PostgreSQL, RabbitMQ, all platform services

---

### expertise-center (AI Experts)
```bash
# Port: 8035
# Start service
cd intelligent-core/expertise-center/service
python main.py

# 12 Tactical Assistants + 10 Strategic Analyzers
# Key endpoints
GET /expertise/assistants      # List all
POST /expertise/analyze        # Request analysis
GET /health
```

**Dependencies:** ai-foundation, PostgreSQL, Qdrant

---

### predictive (Proactive Intelligence)
```bash
# Port: 8031
# Start service
cd intelligent-core/predictive
python main.py

# Key endpoints
GET /api/v1/predictions/journey/{org_id}
GET /api/v1/predictions/recommendations/{org_id}
GET /health
```

**Dependencies:** workflow_intelligence, community_intelligence, notification-service

---

## 🔗 Critical Integrations

### 1. Platform Client (Shared)
```python
from shared.platform_client import get_platform_client

# Access all services
client = await get_platform_client()
await client.ai.ask("question")
await client.experts.query_expert("bia_specialist", "query")
await client.workflows.search_cases({"module": "bia"})
```

### 2. EventBus (Shared)
```python
from shared.eventbus import get_eventbus

# Publish event
eventbus = get_eventbus()
await eventbus.publish("workflow.completed", {"id": "123"})

# Subscribe
await eventbus.subscribe("workflow.*", handler_function)
```

### 3. AI Foundation Integration
```python
# All experts now inherit from ai-foundation
from ai_foundation import AIFoundation

class MyExpert(AIFoundation):
    # Automatic RAG, LLM, embeddings access
    pass
```

---

## 📊 Integration Matrix

| Service | Depends On | Used By |
|---------|-----------|---------|
| ai-foundation | None | All |
| workflow_intelligence | ai-foundation | optimizer, community, predictive |
| ai-orchestration | All services | All |
| expertise-center | ai-foundation | optimizer, orchestration |
| community_intelligence | ai-foundation, workflows | collective, predictive |
| predictive | workflows, community | orchestration |

---

## 🚀 Common Operations

### Start All Services Locally
```bash
# 1. Start dependencies
docker-compose up -d postgres redis rabbitmq qdrant

# 2. Start foundation
cd intelligent-core/ai-foundation && python main.py &

# 3. Start workflow intelligence
cd intelligent-core/workflow_intelligence && python main.py &

# 4. Start orchestration
cd intelligent-core/orchestration/ai-orchestration && python main.py &

# 5. Start expertise center
cd intelligent-core/expertise-center/service && python main.py &

# 6. Start predictive
cd intelligent-core/predictive && python main.py &
```

### Check Service Health
```bash
# Check all services
for port in 8030 8031 8032 8034 8035 8036 8037 8038 8039 8040; do
  echo "Port $port:"
  curl -s http://localhost:$port/health | jq
done
```

### View Metrics
```bash
# Prometheus metrics for any service
curl http://localhost:8037/metrics
```

---

## 🔧 Configuration

### Environment Variables (Common)
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://user:pass@localhost:5672/

# AI Services
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key

# Vector DB
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8037

# Kill process
kill -9 <PID>
```

### Service Won't Start
```bash
# Check logs
tail -f intelligent-core/*/logs/service.log

# Check dependencies
docker ps  # Verify postgres, redis, rabbitmq running
```

### Import Errors
```bash
# Add to PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH

# Or install in development mode
pip install -e .
```

---

## 📝 Key Endpoints by Use Case

### Workflow Management
```bash
# Start workflow
POST http://localhost:8037/api/v1/workflow/start
{"workflow_type": "bia", "org_id": "123"}

# Check status
GET http://localhost:8037/api/v1/workflow/{id}/status

# Optimize workflow
POST http://localhost:8038/api/v1/optimize/performance
{"processId": "proc_001"}
```

### AI Analysis
```bash
# Ask AI
POST http://localhost:8040/api/v1/llm/route
{"prompt": "Analyze this BIA", "context": {...}}

# RAG query
POST http://localhost:8040/api/v1/rag/query
{"question": "What are ISO 22301 requirements?"}

# Expert analysis
POST http://localhost:8035/expertise/analyze
{"type": "bia_specialist", "data": {...}}
```

### Predictive Intelligence
```bash
# Predict journey
GET http://localhost:8031/api/v1/predictions/journey/org_123

# Get recommendations
GET http://localhost:8031/api/v1/predictions/recommendations/org_123

# Forecast expert demand
GET http://localhost:8031/api/v1/predictions/expert-demand
```

### Community Intelligence
```bash
# Search cases
POST http://localhost:8030/api/v1/community/clauses/search
{"query": "BIA best practices"}

# Get guidance
GET http://localhost:8030/api/v1/community/guidance/clause_4.1

# Predict timeline
POST http://localhost:8030/api/v1/community/timeline/predict
{"org_id": "123", "horizon_months": 12}
```

---

## 🎓 Module Responsibility Summary

### ai-foundation
**Responsibility:** Provide core AI capabilities (LLM, RAG, ML) to all services
**Key Feature:** Multi-provider LLM routing, RAG pipeline, embeddings

### workflow_intelligence
**Responsibility:** THE BRAIN - orchestrate all workflows with BPMN engine
**Key Feature:** 7 workflow types, case library, ML-powered recommendations

### ai-orchestration
**Responsibility:** Central decision-making and service coordination
**Key Feature:** 4-layer memory, safety constraints, self-evolution

### expertise-center
**Responsibility:** Provide 22 domain experts for BCM guidance
**Key Feature:** 12 tactical assistants + 10 strategic analyzers

### predictive
**Responsibility:** Predict organization journey and provide proactive recommendations
**Key Feature:** 90-day timeline prediction, daily proactive digests

### community_intelligence
**Responsibility:** Community-driven knowledge creation with peer review
**Key Feature:** 3-reviewer peer review, reputation system, AI synthesis

### collective
**Responsibility:** Privacy-preserving anonymous collaboration
**Key Feature:** Collective agents from 5+ organizations, k-anonymity

### ai_workflow_optimizer
**Responsibility:** ML-powered workflow optimization
**Key Feature:** Performance prediction, bottleneck detection, anomaly detection

### event_intelligence
**Responsibility:** Event analysis, pattern learning, auto-discovery
**Key Feature:** Service auto-discovery, event prediction, self-healing

### coordination-center
**Responsibility:** Translate AI intents to API calls
**Key Feature:** Human-in-the-loop, execution tracking, rollback

### workflow-engine
**Responsibility:** BPMN 2.0 workflow execution engine
**Key Feature:** Expression evaluation, gateway logic, state persistence

---

## 📚 Documentation Locations

- **Main Catalog:** `/intelligent-core/INTELLIGENT_CORE_COMPLETE_CATALOG.md`
- **Quick Reference:** `/intelligent-core/QUICK_REFERENCE.md` (this file)
- **Integration Map:** `/intelligent-core/INTEGRATION_MAP.md`
- **Module READMEs:** `/intelligent-core/{module}/README.md`
- **API Docs:** `http://localhost:{port}/docs` (OpenAPI)

---

## 🔥 Known Issues

1. **Port Conflict:** community_intelligence config conflict (8030 vs 8031)
2. **TODO:** workflow_intelligence case library implementation incomplete
3. **TODO:** Temporal workflow engine configuration needed
4. **TODO:** Qdrant vector DB setup required
5. **Missing:** Some EventBus subscriptions not implemented

See main catalog for detailed issue list and recommendations.

---

## 💡 Pro Tips

1. **Use Platform Client:** Simplifies inter-service communication
2. **Check EventBus:** Most services communicate via events
3. **Monitor Metrics:** All services expose `/metrics` endpoint
4. **Read Module README:** Each module has detailed documentation
5. **Test Integration:** Use `/health` endpoints to verify connectivity

---

## 📞 Support

**Team:** AI Platform Team
**Updated:** 2025-10-08
**Review:** Quarterly

For detailed information, see:
- Full catalog: `INTELLIGENT_CORE_COMPLETE_CATALOG.md`
- Integration map: `INTEGRATION_MAP.md`
- Module-specific READMEs in each directory
