# 🏢 AI Platform Service Catalog

**Updated**: 2025-10-11
**Version**: 2.0

---

## 🧠 AI Office Team (7 Specialists)

Intelligent AI-powered services for platform management and monitoring.

| # | Service | Port | Type | Responsibilities |
|---|---------|------|------|-----------------|
| 1 | **MIO Manager** | 8046 | Coordinator | Platform monitoring, orchestration, decision engine, EventBus coordination |
| 2 | **DB Intelligence** | 8051 | Database Expert | PostgreSQL/Redis monitoring, query optimization, connection pooling |
| 3 | **Analytics Specialist** | 8056 | Platform Analyst | Metrics discovery, dependency mapping, bottleneck detection, platform intelligence |
| 4 | **Agent Router** | 8057 | Router | Request routing, load balancing, circuit breaker |
| 5 | **DevOps Agent** | 8058 | ⭐ Infrastructure & Compliance | **Platform compliance (6 priorities)**, container analysis, event architecture, deployment monitoring, AI auto-remediation |
| 6 | **Project & Code Quality Agent** | 8060 | ⭐ Project Management + Code Analysis | Project/task management, **code security**, **quality analysis**, **testing coverage**, test generation, compliance checking (ISO 22301/27001/HIPAA), domain detection |
| 7 | **Orchestrator** | (varies) | System Orchestrator | Docker orchestration, service lifecycle management |

---

## ⭐ Recent Changes (2025-10-11)

### 1. DevOps Agent (8058) - EXPANDED

**Added**: Platform Compliance Toolkit (from archived project-manager)

**New Capabilities:**
- ✅ **Priority 1**: Port conflicts detection
- ✅ **Priority 2**: Metrics integration (Prometheus/Grafana)
- ✅ **Priority 3**: Database connections (PostgreSQL/Redis)
- ✅ **Priority 4**: KPI registration
- ✅ **Priority 5**: EventBus events monitoring
- ✅ **Priority 6**: Orchestrator control validation

**Integration:**
```python
# DevOps Agent now provides unified compliance + infrastructure
results = await devops_agent.run_compliance_checks()
results = await devops_agent.scan_infrastructure(scan_type="full")
```

---

### 2. Project & Code Quality Agent (8060) - RENAMED

**Previously**: Project Agent
**Now**: Project & Code Quality Agent

**Enhanced Capabilities:**
- Project Management: ✅ Projects, tasks, progress tracking
- **Code Quality**: ✅ Security scanning, quality analysis
- **Testing**: ✅ Coverage analysis, test generation (AI-powered)
- **Compliance**: ✅ ISO 22301, ISO 27001, HIPAA checks
- **AI**: ✅ Domain detection, test generation

**Who handles Testing?** → **Project & Code Quality Agent (8060)**

---

### 3. Archived

**project-manager** → `/infrastructure/_archive/tools-cleanup-2025-10-11/`
- Reason: Functions moved to DevOps Agent
- See: [ARCHIVED_REASON.md](/Users/MD/AI-Platform-ISO/_archive/tools-cleanup-2025-10-11/project-manager/ARCHIVED_REASON.md)

---

## 📊 Service Details

### DevOps Agent (8058)

**Full Name**: AI-Powered DevOps & Compliance Agent

**Capabilities:**
```yaml
capabilities:
  # Platform Compliance (NEW!)
  - platform_compliance_monitoring
  - port_conflict_detection
  - metrics_integration_validation
  - database_health_checking
  - kpi_registration_validation
  - eventbus_monitoring
  - orchestrator_control_validation

  # Infrastructure Analysis
  - deployment_monitoring
  - container_analysis
  - dockerfile_generation
  - event_architecture_scanning

  # AI & Automation
  - ai_powered_analysis
  - auto_remediation
  - predictive_monitoring
  - knowledge_learning
```

**API Endpoints:**
```python
POST /api/v1/compliance/check      # Run compliance checks
POST /api/v1/infrastructure/scan    # Scan infrastructure
POST /api/v1/remediation/apply      # Apply auto-fixes
GET  /api/v1/report                 # Get analysis report
```

---

### Project & Code Quality Agent (8060)

**Full Name**: Project Management & Code Quality Agent

**Capabilities:**
```yaml
capabilities:
  # Project Management
  - project_management
  - task_tracking
  - progress_reporting
  - assignment_management
  - status_tracking

  # Code Quality (NEW!)
  - code_security_scanning
  - code_quality_analysis
  - testing_coverage           # ⭐ Testing responsibility
  - test_generation            # AI-powered
  - compliance_checking        # ISO standards
  - domain_detection           # AI-powered
```

**API Endpoints:**
```python
# Project Management
POST /projects                      # Create project
GET  /projects                      # List projects
POST /tasks                         # Create task

# Code Quality (CLI + API)
POST /api/v1/scan/security         # Security scan
POST /api/v1/scan/quality          # Quality analysis
POST /api/v1/scan/testing          # ⭐ Testing coverage
POST /api/v1/generate/tests        # AI test generation
POST /api/v1/compliance/check      # ISO compliance
```

**CLI:**
```bash
project-agent scan --module security
project-agent scan --module quality
project-agent scan --module testing        # ⭐ Testing
project-agent generate-tests
project-agent detect-domain
```

---

## 🔧 Runtime Services

| Service | Port | Type | Responsibilities |
|---------|------|------|-----------------|
| **Service Discovery** | 8500 | Registry | Unified Catalog + Runtime Registry, health tracking, EventBus integration |
| **EventBus** | 6379 | Message Broker | Redis-based event bus for real-time coordination |
| **Realtime WebSocket** | 8004 | WebSocket | Real-time updates for UI |
| **Message Queue** | (varies) | Queue | Async task processing |

---

## 🔒 Security Services

| Service | Port | Type | Responsibilities |
|---------|------|------|-----------------|
| **Secrets Manager** | (internal) | Security | Centralized secrets management |
| **Auth** | (internal) | Authentication | JWT-based authentication |

---

## 🗄️ Database Services

| Service | Port | Type | Responsibilities |
|---------|------|------|-----------------|
| **PostgreSQL** | 5432 | Database | Primary database |
| **Redis** | 6379 | Cache | Caching & EventBus backend |

---

## 📊 Observability

| Service | Port | Type | Responsibilities |
|---------|------|------|-----------------|
| **Prometheus** | 9090 | Metrics | Metrics collection & storage |
| **Grafana** | 3000 | Visualization | Metrics dashboards |

---

## 🎯 Integration Patterns

### MIO Manager → DevOps Agent (Compliance)

```python
# MIO Manager uses DevOps Agent for compliance checks
from devops_agent.tools import ComplianceRunner

runner = ComplianceRunner()
state = await runner.run_all_checks()

# Or via DevOps Agent API
import httpx
response = await httpx.post("http://devops-agent:8058/api/v1/compliance/check")
```

### Any Service → Project & Code Quality Agent (Testing)

```python
# Request test coverage analysis
import httpx

response = await httpx.post(
    "http://project-agent:8060/api/v1/scan/testing",
    json={"project_path": "/path/to/project"}
)

coverage = response.json()
# {
#   "coverage": {"python": 85.5, "javascript": 72.3},
#   "test_files": [...],
#   "summary": {"average_coverage": 78.9, "status": "OK"}
# }
```

---

## 📋 Service Dependencies

### DevOps Agent (8058)
**Depends on:**
- EventBus (for publishing results)
- AI Foundation (RAG + LLM for analysis)
- Workflow Intelligence (for decision approval)

**Used by:**
- MIO Manager (compliance monitoring)
- Orchestrator (infrastructure validation)

### Project & Code Quality Agent (8060)
**Depends on:**
- EventBus (for coordination)
- MIO Manager (for orchestration)

**Used by:**
- Developers (code analysis, test generation)
- DevOps Agent (CI/CD quality checks)
- MIO Manager (quality monitoring)

---

## 🚀 Quick Start

### Start AI Office Services

```bash
# MIO Manager (Coordinator)
cd /infrastructure/AI-office-infrastructure/mio-manager
python main.py

# DevOps Agent (Infrastructure & Compliance)
cd /infrastructure/AI-office-infrastructure/devops-agent
python main.py

# Project & Code Quality Agent (Testing & Quality)
cd /infrastructure/AI-office-infrastructure/project-agent
python main.py

# Other specialists...
```

### Verify Health

```bash
# Check all AI Office services
curl http://localhost:8046/health  # MIO Manager
curl http://localhost:8051/health  # DB Intelligence
curl http://localhost:8056/health  # Analytics Specialist
curl http://localhost:8057/health  # Agent Router
curl http://localhost:8058/health  # DevOps Agent
curl http://localhost:8060/health  # Project & Code Quality Agent
```

---

## 📚 Documentation

- [DevOps Agent Specification](/infrastructure/AI-office-infrastructure/devops-agent/DEVOPS_AGENT_SPECIFICATION.md)
- [Project Agent README](/infrastructure/AI-office-infrastructure/project-agent/README.md)
- [MIO Manager Architecture](/infrastructure/AI-office-infrastructure/mio-manager/docs/AI_MIO_MANAGER_ARCHITECTURE.md)
- [Final Integration Strategy](/doc-project/FINAL_INTEGRATION_STRATEGY.md)

---

**Maintained by**: AI Office Team
**Last Updated**: 2025-10-11
**Status**: Production Ready ✅
