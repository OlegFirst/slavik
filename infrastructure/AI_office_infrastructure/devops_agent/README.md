# DevOps Agent - AI Digital Colleague 🤖

**Autonomous DevOps AI for self-evolving infrastructure**

---

## Overview

DevOps Agent - это автономный AI-коллега, который:
- 🔍 **Непрерывно анализирует** кодовую базу и инфраструктуру
- 🛠️ **Автоматически исправляет** обнаруженные проблемы
- 📦 **Генерирует Docker** конфигурации для сервисов
- 🚀 **Мониторит развертывания** и управляет rollback
- 🧠 **Интегрирован с мозгом** (Workflow Intelligence) для принятия решений

---

## Quick Start

### Запуск полного анализа
```bash
python3 tools/devops-agent/agent.py --full-scan --report
```

### Сканирование только событий
```bash
python3 tools/devops-agent/agent.py --scan-events
```

### Сканирование контейнеров
```bash
python3 tools/devops-agent/agent.py --scan-containers
```

### Сканирование развертываний
```bash
python3 tools/devops-agent/agent.py --scan-deployments
```

### С автоматическим исправлением
```bash
python3 tools/devops-agent/agent.py --full-scan --auto-fix
```

---

## Architecture

### Components

```
tools/devops-agent/
├── agent.py                           # Main orchestrator
├── DEVOPS_AGENT_SPECIFICATION.md      # Detailed specification
├── analyzers/
│   ├── event_analyzer.py             # Event architecture analysis
│   ├── dockerfile_analyzer.py        # Dockerfile generation
│   └── deployment_analyzer.py        # Deployment & port monitoring
├── auto_remediation/
│   ├── event_fixer.py                # Auto-fix event issues
│   └── (more fixers...)
├── monitoring/
│   └── continuous_monitor.py         # Continuous monitoring
├── integrations/
│   └── workflow_intelligence.py      # Integration with мозг
└── workflows/
    └── devops_workflow.py            # Temporal workflow
```

### Integration Flow

```
┌─────────────────────────────────────────────────────────┐
│                  DevOps Agent Cycle                      │
└─────────────────────────────────────────────────────────┘

1. SCAN
   ├─> Event Architecture (publish/subscribe patterns)
   ├─> Container Configurations (Dockerfiles)
   └─> Deployment Status (health, ports)

2. ANALYZE (with AI)
   ├─> RAG Pipeline (knowledge retrieval)
   ├─> LLM Router (AI decision making)
   └─> Generate recommendations

3. FIX (if approved)
   ├─> Auto-generate missing code
   ├─> Create Dockerfiles
   └─> Resolve port conflicts

4. REPORT
   └─> Workflow Intelligence (мозг) via EventBus
```

---

## Features

### 1. Event Architecture Analysis
- Scans codebase for `publish()` and `subscribe()` calls
- Compares with AsyncAPI schema
- Detects gaps (missing publishers/subscribers)
- Suggests new events based on code patterns
- **Status**: ✅ Migrated from `tools/event_intelligence`

### 2. Dockerfile Generation
- Auto-detects service language (Python/Node/Go)
- Identifies framework (FastAPI/Flask/Express)
- Generates optimized multi-stage Dockerfiles
- Includes health checks and security best practices
- **Status**: ✅ New feature

### 3. Deployment Monitoring
- Scans port configurations
- Detects port conflicts
- Checks service health via `/health` endpoints
- Monitors Docker container status
- **Status**: ✅ New feature

### 4. Auto-Remediation
- Generates missing event publishers/subscribers
- Creates Dockerfiles for services without them
- Suggests port reassignments
- Dry-run mode for safety
- **Status**: ✅ Migrated + enhanced

---

## Integration with Platform

### Workflow Intelligence (мозг)

DevOps Agent reports to Workflow Intelligence for decision-making:

```python
# Example: Reporting infrastructure issues
await brain_client.report_infrastructure_analysis({
    "event_gaps": 121,
    "critical_issues": 4,
    "missing_dockerfiles": 3,
    "port_conflicts": 1,
    "recommendations": [...]
})

# Example: Requesting decision
decision = await brain_client.request_decision({
    "context": "port_conflict",
    "service1": "ai-event-manager",
    "service2": "workflow_intelligence",
    "port": 8050
})
```

### EventBus Communication

```python
# Publish infrastructure event
await eventbus.publish(
    "devops.infrastructure.analyzed",
    {
        "agent_id": "devops-agent",
        "findings": {...},
        "recommendations": [...]
    }
)
```

### Temporal Workflows

```bash
# Start DevOps workflow via Temporal
temporal workflow start \
    --type DevOpsAgentWorkflow \
    --task-queue devops-queue \
    --input '{"scan_type": "full", "auto_fix": false}'
```

---

## Temporal Workflows

### 1. DevOpsAgentWorkflow
Main workflow for infrastructure management:
- Scans infrastructure
- AI analysis
- Auto-remediation (if approved)
- Reports to мозг

### 2. DevOpsWeeklyDeepScan
Scheduled weekly scan (Monday 03:00):
- Full infrastructure analysis
- Dockerfile generation
- Port conflict detection
- Comprehensive reporting

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/devops_agent.yml
name: DevOps Agent - Infrastructure Check

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 3 * * 1'  # Monday 03:00

jobs:
  infrastructure-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run DevOps Agent
        run: |
          python3 tools/devops-agent/agent.py --full-scan

      - name: Check Critical Issues
        run: |
          python3 tools/devops-agent/agent.py --validate --fail-on-critical
```

---

## Metrics & Monitoring

### Prometheus Metrics

```prometheus
# DevOps Agent Metrics
devops_agent_scans_total               # Total scans performed
devops_agent_issues_detected           # Issues found
devops_agent_auto_fixes_applied        # Auto-fixes applied
devops_agent_dockerfiles_generated     # Dockerfiles generated
devops_agent_port_conflicts_detected   # Port conflicts found
```

### Grafana Dashboard

Key panels:
1. Infrastructure Health Score
2. Event Architecture Coverage
3. Auto-Fix Success Rate
4. Port Usage Map
5. Deployment Health

---

## Examples

### Example 1: Find Missing Dockerfiles

```python
from tools.devops_agent.analyzers.dockerfile_analyzer import DockerfileAnalyzer

analyzer = DockerfileAnalyzer("/Users/MD/AI-Platform-ISO")
missing = analyzer.find_missing_dockerfiles()

for service in missing:
    print(f"Service: {service.name}")
    print(f"  Language: {service.language}")
    print(f"  Framework: {service.framework}")
    print(f"  Suggested Dockerfile:")
    print(analyzer.generate_dockerfile(service))
```

### Example 2: Detect Port Conflicts

```python
from tools.devops_agent.analyzers.deployment_analyzer import DeploymentAnalyzer

analyzer = DeploymentAnalyzer("/Users/MD/AI-Platform-ISO")
conflicts = analyzer.detect_port_conflicts()

for conflict in conflicts:
    print(f"⚠️  Port {conflict.port}: {conflict.service1} vs {conflict.service2}")

    # Get suggestion for new port
    new_port = analyzer.suggest_available_port()
    print(f"   Suggested port: {new_port}")
```

### Example 3: Full Cycle with Brain Integration

```python
from tools.devops_agent.agent import DevOpsAgent

agent = DevOpsAgent("/Users/MD/AI-Platform-ISO")
await agent.initialize()

# Run full cycle
result = await agent.run_full_cycle()

print(f"Status: {result['status']}")
print(f"Issues found: {result['scan_results'].get('total_issues', 0)}")
print(f"Recommendations: {len(result['ai_analysis'].get('ai_recommendations', []))}")
```

---

## Migration from tools/event_intelligence

Old structure → New structure:
- `event_intelligence_system.py` → `analyzers/event_analyzer.py`
- `auto_fixer.py` → `auto_remediation/event_fixer.py`
- `continuous_monitor.py` → `monitoring/continuous_monitor.py`

**All existing functionality preserved + new DevOps features added!**

---

## Roadmap

### Phase 1: Foundation ✅
- [x] Event architecture analysis
- [x] Auto-remediation
- [x] Continuous monitoring

### Phase 2: DevOps Expansion ✅
- [x] Dockerfile generation
- [x] Deployment monitoring
- [x] Port management
- [x] Integration with Workflow Intelligence

### Phase 3: Advanced (In Progress)
- [ ] AI-powered infrastructure optimization
- [ ] Predictive deployment failure detection
- [ ] Auto-scaling recommendations
- [ ] Security vulnerability scanning

---

## Documentation

- [DEVOPS_AGENT_SPECIFICATION.md](./DEVOPS_AGENT_SPECIFICATION.md) - Detailed specification
- [Workflow Intelligence Integration](../../intelligent-core/workflow_intelligence/README.md)
- [Temporal Workflows Guide](../../intelligent-core/workflow_intelligence/temporal_workflows/README.md)

---

**Built with ❤️ for autonomous, self-evolving platforms**
