# 🔍 Analytics Specialist AI

**Platform Intelligence Expert - AI Colleague #6 in AI Office**

> Цифровой коллега, который анализирует экосистему платформы, выявляет проблемы, и предоставляет интеллектуальные insights для принятия решений.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Workflows](#workflows)
- [Integration](#integration)
  - [Platform Client Integration ✨ NEW](#platform-client-integration--new-in-v110)
- [Development](#development)
- [Deployment](#deployment)

---

## 📚 Documentation

- **[PLATFORM_CLIENT_INTEGRATION.md](./PLATFORM_CLIENT_INTEGRATION.md)** - Platform Client integration guide (v1.1.0)
- **[INTEGRATION_STATUS.md](./INTEGRATION_STATUS.md)** - Integration coverage & test results
- **[АВТОМАТИЧЕСКАЯ_ИНТЕГРАЦИЯ_ГОТОВО.md](./АВТОМАТИЧЕСКАЯ_ИНТЕГРАЦИЯ_ГОТОВО.md)** - Russian summary
- **[CHANGES_SUMMARY.md](./CHANGES_SUMMARY.md)** - All changes in v1.1.0
- **[HOW_TO_INTEGRATE.md](../../../intelligent-core/shared/HOW_TO_INTEGRATE.md)** - Universal integration guide

---

## 🎯 Overview

**Analytics Specialist** - 6-й AI Colleague в AI Office, специализирующийся на анализе платформы и генерации insights.

### Key Responsibilities

- ✅ **Platform Health Analysis** - Анализ здоровья платформы (процессы, метрики, зависимости)
- ✅ **Bottleneck Detection** - Обнаружение узких мест в workflows
- ✅ **Dependency Analysis** - Анализ зависимостей и конфликтов между сервисами
- ✅ **Incident Investigation** - Расследование инцидентов и поиск root cause
- ✅ **MIO Manager Integration** - Отчетность и координация через МиО Manager
- ✅ **AI Orchestrator Support** - Предоставление контекста для принятия решений

### Competency Levels

Analytics Specialist растет от junior до expert, получая новые инструменты:

| Level | Tools | Capabilities |
|-------|-------|--------------|
| **Junior** | process_analytics, metrics_discovery | Basic process mining, metrics coverage |
| **Middle** | + dependency_mapper, discover_services | Platform-wide analysis, dependency conflicts |
| **Senior** | + predictive, optimizer, ast_analyzer | ML predictions, code quality analysis |
| **Expert** | + all tools | Digital twin foundation, real-time intelligence |

**Current Level:** `junior` (configurable via `COMPETENCY_LEVEL`)

---

## ✨ Features

### Core Analytics

- 🔍 **Process Mining** - Analyze workflow executions, detect bottlenecks and deviations
- 📊 **Metrics Intelligence** - Discover and analyze Prometheus metrics coverage
- 🔗 **Dependency Mapping** - Map service dependencies, detect conflicts and circular deps
- 🎯 **Health Scoring** - Calculate overall platform health score (0-100)
- 📈 **Trend Analysis** - Track platform health trends over time

### Automated Workflows

- ⏰ **Daily Health Check** - Automated daily platform analysis (09:00 by default)
- 🔄 **Continuous Improvement** - Hourly scan for improvement opportunities
- 🚨 **Incident Investigation** - On-demand incident root cause analysis
- 📤 **Auto-Reporting** - Automatic reporting to MIO Manager

### Integrations

**Platform "Brains" (via platform_client):** ✨ NEW in v1.1.0
- 🧠 **AI Foundation** (port 8040) - RAG Pipeline, LLM Router, Embeddings
- 🎓 **Expertise Center** (port 8035) - 12 Tactical Assistants + 10 Analyzers
- 📚 **Workflow Intelligence** (port 8037) - Case Library + ML Analysis

**Analytics-Specific Clients:**
- 👔 **MIO Manager** (port 8046) - Coordination and task delegation
- 🧠 **AI Orchestrator** (port 8004) - Decision-making context provider
- 📊 **Process Analytics** (port 8780) - Process mining data source
- 🔮 **Predictive Service** (port 8033) - ML predictions (middle+)
- 🤝 **Collective AI** (port 8032) - Collective intelligence (senior+)
- 🌍 **Community Intelligence** (port 8031) - Knowledge sharing

**Integration Coverage:** 9/12 (75%) - [See Integration Status](./INTEGRATION_STATUS.md)

---

## 🏗️ Architecture

```
analytics-specialist/
├── config/             Configuration
│   └── settings.py     Environment settings
│
├── models/             Data models (Pydantic)
│   └── analytics_models.py
│
├── clients/            External service clients
│   ├── process_analytics_client.py    Process Analytics integration
│   └── mio_manager_client.py          MIO Manager integration
│
├── tools/              Analysis tools (wrappers for /tools/analyzers)
│   ├── metrics_discovery_tool.py      Metrics discovery
│   └── dependency_mapper_tool.py      Dependency analysis
│
├── core/               Core analytics engine
│   └── analytics_core.py               Main orchestrator
│
├── workflows/          Automated workflows
│   ├── daily_health_check.py          Daily health check
│   └── incident_investigation.py      Incident investigation
│
├── api/                REST API
│   └── routes.py       FastAPI routes
│
└── main.py             FastAPI application
```

### Data Flow

```
1. Analytics Specialist analyzes platform
      ↓
2. Generates insights & recommendations
      ↓
3. Reports to MIO Manager
      ↓
4. MIO Manager coordinates actions
      ↓
5. Orchestrator executes fixes
      ↓
6. Analytics Specialist verifies impact
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching)
- Access to:
  - MIO Manager (port 8046)
  - Process Analytics (port 8780)
  - AI Orchestrator (port 8004)

### Installation

```bash
# Clone repository (if needed)
cd infrastructure/AI-office-infrastructure/analytics-specialist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Configuration

Edit `.env`:

```bash
# Service
ANALYTICS_PORT=8051
COMPETENCY_LEVEL=junior

# AI Office Infrastructure
MIO_MANAGER_URL=http://localhost:8046

# Analytics Services
PROCESS_ANALYTICS_URL=http://localhost:8780

# Tools
PROJECT_ROOT=/Users/MD/AI-Platform-ISO
TOOLS_ANALYZERS_PATH=/Users/MD/AI-Platform-ISO/infrastructure/tools/analyzers

# Workflows
DAILY_HEALTH_CHECK_ENABLED=true
CONTINUOUS_IMPROVEMENT_ENABLED=true
```

### Run Service

```bash
# Development mode (with auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8051 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8051 --workers 4
```

### Verify Service

```bash
# Health check
curl http://localhost:8051/health

# Service status
curl http://localhost:8051/api/v1/analytics/status

# Root endpoint
curl http://localhost:8051/
```

---

## 📚 API Documentation

### Interactive Docs

Once service is running:
- **Swagger UI:** http://localhost:8051/docs
- **ReDoc:** http://localhost:8051/redoc

### Key Endpoints

#### Health & Status

```bash
# Health check
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "competency_level": "junior",
  "available_tools": ["metrics_discovery", "dependency_mapper"],
  "uptime_seconds": 12345.67
}
```

```bash
# Detailed status
GET /api/v1/analytics/status

Response:
{
  "service": "analytics-specialist",
  "status": "healthy",
  "competency_level": "junior",
  "integrations": {
    "process_analytics": "healthy",
    "mio_manager": "healthy"
  },
  "tools": {...}
}
```

#### Analysis

```bash
# Platform health analysis
POST /api/v1/analytics/analyze
Content-Type: application/json

{
  "analysis_type": "platform_health",
  "requester": "ai-orchestrator"
}

Response:
{
  "status": "success",
  "report_id": "report_20251008_100000",
  "health_score": 78.5,
  "summary": "Found: 3 bottlenecks, 2 conflicts. 5 recommendations provided.",
  "total_insights": 5,
  "critical_insights": 0,
  "recommendations": 5,
  "report": {...}
}
```

```bash
# Get platform insights (for AI Orchestrator)
GET /api/v1/analytics/insights

Response:
{
  "health_score": 78.5,
  "critical_insights": [...],
  "recommendations": [...],
  "last_analysis_at": "2025-10-08T10:00:00Z",
  "competency_level": "junior"
}
```

#### Workflows

```bash
# Trigger daily health check
POST /api/v1/workflows/daily-health-check

Response:
{
  "status": "triggered",
  "workflow": "daily_health_check",
  "message": "Workflow started in background",
  "triggered_at": "2025-10-08T10:00:00Z"
}
```

```bash
# Investigate incident
POST /api/v1/workflows/investigate-incident
Content-Type: application/json

{
  "incident_id": "inc_001",
  "incident_details": {
    "type": "service_outage",
    "affected_service": "workflow_intelligence"
  }
}

Response:
{
  "status": "success",
  "incident_id": "inc_001",
  "root_cause": {...},
  "prevention_plan": [...],
  "insights_generated": 3
}
```

---

## ⚙️  Workflows

### Daily Health Check

**Trigger:** Automated daily at 09:00 (configurable)

**What it does:**
1. Analyzes platform health (processes, metrics, dependencies)
2. Generates insights and recommendations
3. Reports to MIO Manager
4. If critical issues found → Requests task delegation

**Configuration:**
```bash
DAILY_HEALTH_CHECK_ENABLED=true
DAILY_HEALTH_CHECK_TIME=09:00
```

**Manual trigger:**
```bash
curl -X POST http://localhost:8051/api/v1/workflows/daily-health-check
```

---

### Continuous Improvement

**Trigger:** Automated hourly (configurable)

**What it does:**
1. Scans for improvement opportunities
2. Focuses on low/medium severity issues
3. Reports only if > 5 opportunities found

**Configuration:**
```bash
CONTINUOUS_IMPROVEMENT_ENABLED=true
CONTINUOUS_IMPROVEMENT_INTERVAL=3600  # 1 hour in seconds
```

---

### Incident Investigation

**Trigger:** On-demand (manual or automated)

**What it does:**
1. Analyzes incident context
2. Finds similar historical incidents
3. Identifies root cause
4. Generates prevention plan
5. Reports to MIO Manager

**Example:**
```bash
curl -X POST http://localhost:8051/api/v1/workflows/investigate-incident \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "inc_001",
    "incident_details": {
      "type": "service_outage",
      "affected_service": "workflow_intelligence"
    }
  }'
```

---

## 🔗 Integration

### Platform Client Integration ✨ NEW in v1.1.0

Analytics Specialist uses **automatic integration** with 3 key platform "brains" via `intelligent-core/shared/platform_client.py`:

```python
from shared.platform_client import get_platform_client

# Automatic integration - one line!
platform = get_platform_client()

# Now you have access to:
# 1. AI Foundation (RAG, LLM, Embeddings)
knowledge = await platform.ai.search_knowledge("How to detect bottlenecks?")
ai_analysis = await platform.ai.ask("Analyze this anomaly", context={...})

# 2. Expertise Center (12 Tactical Assistants)
bia_result = await platform.experts.bia_analysis({"process_id": "P-123"})
risk_result = await platform.experts.risk_assessment({...})

# 3. Workflow Intelligence (Case Library)
case_id = await platform.workflows.add_case(case_data, module="analytics")
similar_cases = await platform.workflows.search_cases({"tags": ["bottleneck"]})
```

**Benefits:**
- ✅ Automatic connection to platform "brains"
- ✅ No manual client configuration
- ✅ Unified standard across all services
- ✅ Built-in health monitoring
- ✅ Graceful degradation

**Learn More:**
- [Platform Client Integration Guide](./PLATFORM_CLIENT_INTEGRATION.md)
- [Integration Status & Coverage](./INTEGRATION_STATUS.md)
- [How to Integrate (Universal Guide)](../../../intelligent-core/shared/HOW_TO_INTEGRATE.md)

---

### With MIO Manager

Analytics Specialist reports insights to МиО Manager:

```python
from clients import MIOManagerClient, report_daily_health_check

mio = MIOManagerClient()

# Report daily health check
await report_daily_health_check(
    mio_client=mio,
    health_score=78.5,
    critical_issues=[...],
    recommendations=[...]
)

# Request task delegation
await mio.delegate_task({
    "title": "Fix critical bottlenecks",
    "priority": "high",
    "actions": [...]
})
```

---

### With AI Orchestrator

AI Orchestrator queries Analytics Specialist for context:

```python
# AI Orchestrator side
import httpx

async def get_platform_insights():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8051/api/v1/analytics/insights"
        )
        insights = response.json()

    # Use insights in decision-making
    if insights["health_score"] < 70:
        # Take action based on critical insights
        ...
```

---

### With Process Analytics

Analytics Specialist queries Process Analytics for data:

```python
from clients import ProcessAnalyticsClient

pa = ProcessAnalyticsClient()

# Get bottlenecks
bottlenecks = await pa.detect_bottlenecks("bia_workflow")

# Get comprehensive analysis
analysis = await pa.comprehensive_analysis("bia_workflow")
```

---

## 🛠️ Development

### Project Structure

```
analytics-specialist/
├── config/             ✅ Configuration
├── models/             ✅ Data models (complete Pydantic models)
├── clients/            ✅ External service clients
├── tools/              ✅ Analysis tools (wrappers)
├── core/               ✅ Core analytics engine
├── workflows/          ✅ Automated workflows
├── api/                ✅ REST API
├── main.py             ✅ FastAPI application
├── requirements.txt    ✅ Python dependencies
├── Dockerfile          ✅ Docker image
├── .env.example        ✅ Environment template
└── README.md           ✅ This file
```

### Adding New Tools

1. Create tool wrapper in `tools/`:

```python
# tools/new_tool.py
class NewAnalysisTool:
    def __init__(self):
        self.name = "new_tool"
        self.description = "What it does"
        self.competency_required = "senior"  # junior|middle|senior|expert

    async def analyze(self):
        # Implementation
        return {...}
```

2. Add to `core/analytics_core.py`:

```python
def _initialize_tools(self):
    tools = {}

    # ...existing tools...

    # Add new tool for senior+
    if self.competency in [CompetencyLevel.SENIOR, CompetencyLevel.EXPERT]:
        tools["new_tool"] = NewAnalysisTool()

    return tools
```

3. Use in analysis workflows.

---

### Adding New Workflows

1. Create workflow in `workflows/`:

```python
# workflows/new_workflow.py
async def new_workflow():
    """New automated workflow"""
    core = AnalyticsCore()
    await core.initialize()

    # Do analysis
    result = await core.analyze_something()

    # Report to MIO
    await core.report_to_mio(result)

    return {"status": "success"}
```

2. Add route in `api/routes.py`:

```python
@workflow_router.post("/new-workflow")
async def trigger_new_workflow():
    background_tasks.add_task(new_workflow)
    return {"status": "triggered"}
```

3. Schedule in `main.py` if needed.

---

### Testing

```bash
# Run tests (when implemented)
pytest tests/

# Test specific module
pytest tests/test_core.py

# With coverage
pytest --cov=. tests/
```

---

## 🐳 Deployment

### Docker

```bash
# Build image
docker build -t analytics-specialist:1.0.0 .

# Run container
docker run -d \
  --name analytics-specialist \
  -p 8051:8051 \
  -e COMPETENCY_LEVEL=junior \
  -e MIO_MANAGER_URL=http://mio-manager:8046 \
  -e PROCESS_ANALYTICS_URL=http://process-analytics:8780 \
  analytics-specialist:1.0.0

# Check logs
docker logs -f analytics-specialist

# Stop
docker stop analytics-specialist
```

### Docker Compose

Add to `docker-compose.yml`:

```yaml
services:
  analytics-specialist:
    build: ./infrastructure/AI-office-infrastructure/analytics-specialist
    container_name: analytics-specialist
    ports:
      - "8051:8051"
    environment:
      - COMPETENCY_LEVEL=junior
      - MIO_MANAGER_URL=http://mio-manager:8046
      - PROCESS_ANALYTICS_URL=http://process-analytics:8780
      - DAILY_HEALTH_CHECK_ENABLED=true
      - CONTINUOUS_IMPROVEMENT_ENABLED=true
    depends_on:
      - mio-manager
      - process-analytics
      - redis
    networks:
      - ai-office-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8051/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 📊 Monitoring

### Health Metrics

Analytics Specialist exposes `/health` endpoint for monitoring:

```bash
# Check health
curl http://localhost:8051/health

# Prometheus metrics (TODO)
curl http://localhost:8051/metrics
```

### Logging

Logs are output to stdout in JSON format:

```json
{
  "timestamp": "2025-10-08T10:00:00Z",
  "level": "INFO",
  "service": "analytics-specialist",
  "message": "Daily health check complete",
  "health_score": 78.5,
  "insights": 5
}
```

---

## 🤝 Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Document all public methods
- Add examples in docstrings

### Commit Messages

```
feat(core): Add dependency conflict detection
fix(workflows): Fix daily health check scheduling
docs(readme): Update API documentation
```

---

## 📝 License

Part of AI-Platform-ISO project.

---

## 🆘 Support

### Troubleshooting

**Issue:** Service won't start
```bash
# Check logs
docker logs analytics-specialist

# Verify dependencies
curl http://localhost:8046/health  # MIO Manager
curl http://localhost:8780/health  # Process Analytics
```

**Issue:** No insights generated
```bash
# Check Process Analytics has data
curl http://localhost:8780/api/v1/process-mining/processes

# Manually trigger analysis
curl -X POST http://localhost:8051/api/v1/analytics/analyze \
  -H "Content-Type: application/json" \
  -d '{"analysis_type": "platform_health", "requester": "manual"}'
```

**Issue:** Tools not available
```bash
# Check tools path
echo $TOOLS_ANALYZERS_PATH

# Verify tools exist
ls -la /Users/MD/AI-Platform-ISO/infrastructure/tools/analyzers/

# Check service status
curl http://localhost:8051/api/v1/analytics/status
```

---

## 🎯 Roadmap

### Version 1.0 (Released - 2025-10-05)
- ✅ Junior competency (process mining + metrics)
- ✅ MIO Manager integration
- ✅ Daily health check workflow
- ✅ Incident investigation workflow

### Version 1.1 (Current - 2025-10-08) ✨
- ✅ **Platform Client Integration** - Automatic connection to 3 "brains"
- ✅ **AI Foundation** - RAG, LLM, Embeddings
- ✅ **Expertise Center** - 12 Tactical Assistants
- ✅ **Workflow Intelligence** - Case Library + ML
- ✅ **Enhanced Health Monitoring** - 9/12 integrations tracked
- ✅ **Competency-based unlocking** - Predictive (middle+), Collective (senior+)
- ✅ **Comprehensive documentation** - 5 guides, automated tests

### Version 1.2 (Next - Planned)
- [ ] **Learning System Integration** - Analytics → Learning feedback loop
- [ ] **Knowledge Library** - Long-term storage of insights
- [ ] **Workflow Intelligence Logging** - Full execution tracking
- [ ] Middle competency activation (+ dependency analysis)
- [ ] Grafana dashboard

### Version 2.0 (Future)
- [ ] Senior competency (+ all advanced tools)
- [ ] Digital twin data collection
- [ ] User journey analytics
- [ ] Self-improving recommendations
- [ ] 100% platform integration coverage

---

## 📞 Contact

For questions or issues:
- Create GitHub issue
- Contact AI Office team

---

**Built with ❤️  by AI Platform ISO Team**

**Analytics Specialist AI - Making the platform smarter, one insight at a time! 🔍🧠**
