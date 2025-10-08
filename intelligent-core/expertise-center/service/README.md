# Expertise Center Service

**Standalone FastAPI service providing REST API access to BCM Experts and Analyzers**

## 🎯 Overview

Expertise Center Service is an API gateway that provides access to:
- **12 Tactical Assistants** (BCM AI Experts)
- **10 Strategic Analyzers**

### Port: `8035`

---

## 🚀 Quick Start

```bash
# Start the service
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise-center/service
python3 standalone_main.py

# Or with nohup
nohup python3 standalone_main.py > /tmp/expertise_center_service.log 2>&1 &

# Check health
curl http://localhost:8035/health
```

---

## 📋 Available Experts

### Tactical Assistants (12)

1. **BIA Specialist AI** - Business Impact Analysis & RTO/RPO
2. **Risk Analyst AI** - Risk Assessment & Treatment Planning
3. **Compliance Copilot AI** - ISO 22301 Compliance & Gap Analysis
4. **Incident Advisor AI** - Incident Response & Crisis Management
5. **Plan Generator AI** - BCM Plan Development & Maintenance
6. **Exercise Designer AI** - BCM Exercise & Testing Design
7. **Project Manager AI** - BCM Program Management
8. **Documents Specialist AI** - BCM Documentation & Templates
9. **Governance Specialist AI** - BCM Governance & Leadership
10. **Learning Specialist AI** - BCM Training & Awareness
11. **Validation Specialist AI** - BCM Validation & Verification
12. **Community Specialist AI** - BCM Community Building

### Strategic Analyzers (10)

1. **Compliance Analyzer** - ISO 22301 Compliance Analysis
2. **Risk Analyzer** - Risk Impact Analysis
3. **Governance Analyzer** - BCM Governance Analysis
4. **Lifecycle Analyzer** - BCM Lifecycle Analysis
5. **Learning Analyzer** - Learning & Training Analysis
6. **Performance Analyzer** - BCM Performance Analysis
7. **Emergency Analyzer** - Emergency Response Analysis
8. **Impact Analyzer** - Business Impact Analysis
9. **Plan Analyzer** - BCM Plan Analysis
10. **Scenario Analyzer** - BCM Scenario Analysis

---

## 🔌 API Endpoints

### Core Endpoints

```bash
# Health check
GET /health
GET /expertise/health

# Service info
GET /
GET /expertise/info

# API documentation
GET /docs          # Swagger UI
GET /redoc         # ReDoc
```

### Tactical Assistants

```bash
# BIA Specialist
POST /expertise/tactical/bia/analyze

# Risk Analyst
POST /expertise/tactical/risk/assess

# Compliance Copilot
POST /expertise/tactical/compliance/check

# ... (all 12 experts available)
```

### Analyzers

```bash
# Compliance Analyzer
POST /expertise/analyzers/compliance/analyze

# Risk Analyzer
POST /expertise/analyzers/risk/analyze

# Governance Analyzer
POST /expertise/analyzers/governance/analyze

# ... (all 10 analyzers available)
```

### Generic Query Endpoint

```bash
POST /expertise/query
{
  "expert_type": "bia_specialist",
  "query": "What are critical processes for healthcare?",
  "context": {"industry": "healthcare"},
  "organization_id": "org123"
}
```

---

## 💡 Usage Examples

### Health Check

```bash
curl http://localhost:8035/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "expertise-center-service",
  "version": "1.0.0"
}
```

### Get Available Experts

```bash
curl http://localhost:8035/expertise/info
```

**Response:**
```json
{
  "tactical_assistants": [
    {
      "id": "bia_specialist",
      "name": "BIA Specialist AI",
      "specialty": "Business Impact Analysis"
    },
    ...
  ],
  "analyzers": [
    {
      "id": "compliance",
      "name": "Compliance Analyzer"
    },
    ...
  ],
  "total_experts": 12,
  "total_analyzers": 10,
  "status": "available"
}
```

### Query BIA Specialist

```bash
curl -X POST http://localhost:8035/expertise/tactical/bia/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze impact of email system outage",
    "context": {
      "industry": "finance",
      "organization_size": "medium"
    }
  }'
```

### Query Risk Analyzer

```bash
curl -X POST http://localhost:8035/expertise/analyzers/risk/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "threats": ["ransomware", "ddos"],
      "vulnerabilities": ["unpatched_systems"],
      "assets": ["customer_database"]
    },
    "context": {
      "industry": "healthcare"
    }
  }'
```

---

## 🏗️ Architecture

```
expertise-center/
├── domains/                    # Expert implementations
│   └── bcm/
│       ├── tactical_assistants/  # 12 experts
│       └── analyzers/            # 10 analyzers
├── shared/                     # Shared utilities
│   └── base/
│       ├── base_tactical_assistant.py
│       └── assistant_context.py
└── service/                    # API Service (THIS)
    ├── api/
    │   ├── routes.py          # Main router
    │   ├── tactical.py        # Tactical endpoints
    │   └── analyzers.py       # Analyzer endpoints
    ├── config.py              # Configuration
    ├── main.py                # Full version (with imports)
    └── standalone_main.py     # Standalone version ✅
```

---

## ⚙️ Configuration

Environment variables:

```bash
# Service
EXPERTISE_CENTER_PORT=8035
EXPERTISE_CENTER_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO

# Dependencies (optional)
AI_FOUNDATION_URL=http://localhost:8040
KNOWLEDGE_BASE_URL=http://localhost:8040

# EventBus (optional)
EVENTBUS_ENABLED=false
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5673
```

---

## 📊 Integration

### With AI Orchestration

```python
import httpx

async def query_expert(expert_type: str, query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8035/expertise/query",
            json={
                "expert_type": expert_type,
                "query": query
            }
        )
        return response.json()

# Usage
result = await query_expert("bia_specialist", "Analyze critical processes")
```

### With Workflow Engine

```yaml
# BPMN task
- id: consult_expert
  type: serviceTask
  implementation: http
  endpoint: http://localhost:8035/expertise/tactical/bia/analyze
  method: POST
```

---

## 🔧 Development

### Run in Development Mode

```bash
cd service
python3 standalone_main.py
```

### Run with Auto-reload

```bash
uvicorn standalone_main:app --host 0.0.0.0 --port 8035 --reload
```

### View Logs

```bash
tail -f /tmp/expertise_center_service.log
```

### Check Process

```bash
lsof -i :8035
ps aux | grep standalone_main
```

---

## 🧪 Testing

```bash
# Health check
curl http://localhost:8035/health

# Get experts info
curl http://localhost:8035/expertise/info | python3 -m json.tool

# Test BIA endpoint
curl -X POST http://localhost:8035/expertise/tactical/bia/analyze \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'

# Test Compliance Analyzer
curl -X POST http://localhost:8035/expertise/analyzers/compliance/analyze \
  -H "Content-Type: application/json" \
  -d '{"data":{"standard":"ISO22301"}}'
```

---

## 📝 Current Status

### ✅ Completed

- [x] FastAPI service created
- [x] 12 Tactical Assistant endpoints
- [x] 10 Analyzer endpoints
- [x] Health checks
- [x] Swagger documentation
- [x] Service running on port 8035
- [x] Basic testing passed

### 🔄 In Progress

- [ ] Full expert integration (currently gateway mode)
- [ ] RAG pipeline integration
- [ ] LLM router integration
- [ ] Context enrichment

### 📋 Future Enhancements

- [ ] Authentication & authorization
- [ ] Rate limiting
- [ ] Caching
- [ ] Metrics & monitoring
- [ ] Advanced error handling
- [ ] WebSocket support for streaming

---

## 📚 Documentation

- **Swagger UI**: http://localhost:8035/docs
- **ReDoc**: http://localhost:8035/redoc
- **OpenAPI JSON**: http://localhost:8035/openapi.json

---

## 🐛 Troubleshooting

### Service won't start

```bash
# Check if port is occupied
lsof -i :8035

# Kill old process
kill $(lsof -t -i :8035)

# Restart
python3 standalone_main.py
```

### Import errors

```bash
# Ensure PYTHONPATH includes intelligent-core
export PYTHONPATH=/Users/MD/AI-Platform-ISO/intelligent-core:/Users/MD/AI-Platform-ISO
python3 standalone_main.py
```

### Experts not responding

Check that expert classes are properly imported in `tactical.py` and `analyzers.py`

---

## 📞 Support

For issues or questions:
1. Check logs: `/tmp/expertise_center_service.log`
2. View Swagger docs: http://localhost:8035/docs
3. Check service status: `curl http://localhost:8035/health`

---

**Created:** 2025-10-08
**Version:** 1.0.0
**Status:** ✅ Production Ready (Gateway Mode)
