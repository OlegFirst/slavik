# AI Agent Router v2.1 🚀

## Overview
**Production-Ready** intelligent AI request routing for BCM Platform with complete automation, observability, and protection layers.

## Version History
- **v1.0** (2025-10-04): Initial extraction (295 lines, ~50% potential)
- **v2.0** (2025-10-07): Enhanced with Circuit Breaker, Prometheus Metrics, Rate Limiting (750+ lines, ~85% potential)
- **v2.1** (2025-10-07): Full automation, integrations, reporting structure (4850+ lines, 100% potential) ✅

## ✨ Features

### Core Capabilities
- ✅ **Smart Routing** - Routes AI requests to appropriate microservices based on capability
- ✅ **Advanced Load Balancing** - Priority → Response Time → Current Load based selection
- ✅ **Health Monitoring** - Automatic health checks every 30s with auto-recovery
- ✅ **Request Analytics** - Tracking and analytics via Redis
- ✅ **Multi-Role Support** - 6 agent roles (Orchestrator, Processor, Assistant, Specialist, Bridge, Registry)

### Protection & Reliability
- ✅ **Circuit Breaker** - Protection from cascade failures with exponential backoff
- ✅ **Rate Limiting** - Token bucket algorithm (global: 1000 req/min, per-agent: configurable)
- ✅ **Graceful Degradation** - Automatic fallback when components unavailable
- ✅ **Auto-Recovery** - Health daemon attempts recovery for unhealthy agents

### Observability
- ✅ **Prometheus Metrics** - 18+ metrics exported at :9090/metrics
- ✅ **Grafana Dashboards** - Ready-to-use dashboards (8 panels)
- ✅ **Alert Rules** - 6 predefined alert rules
- ✅ **Structured Logging** - JSON logs with full context

### Automation
- ✅ **Temporal Workflows** - 4 production workflows (health monitoring, circuit breaker recovery, service discovery sync, metrics export)
- ✅ **GitHub Actions CI/CD** - Full pipeline (lint → test → security → build → deploy)
- ✅ **Docker Compose** - One-command deployment (router + redis + prometheus + grafana)
- ✅ **Health Daemon** - Background health checks and recovery

### Integrations
- ✅ **MIO Manager** - AgentRouterClient for easy integration
- ✅ **Service Discovery** - Dynamic agent registration via ServiceRegistry
- ✅ **Prometheus** - Metrics scraping every 10s
- ✅ **Grafana** - Real-time dashboards

## 🎯 Responsibility Sector

**AI Agent Router** is responsible for the **"AI Request Routing & Load Balancing"** sector.

### What It Does:
- Routes ALL AI requests to appropriate agents
- Balances load across agents
- Monitors agent health
- Protects from failures (circuit breaker + rate limiting)
- Exports metrics and analytics
- Integrates with service discovery

### What It DOES NOT Do:
- ❌ Business logic (done by AI agents)
- ❌ AI processing (done by AI agents)
- ❌ User authentication (done by API Gateway)
- ❌ Workflow orchestration (done by Temporal)
- ❌ Long-term storage (done by Supabase)

## 💾 Database

**Primary**: **Redis** (in-memory)
- Request analytics (last 1000)
- Agent statistics
- Circuit breaker state
- Rate limiter state

**Optional**: **PostgreSQL/Supabase** (for long-term analytics)
- Historical data
- Business intelligence
- Trend analysis

## 📊 SLIs/SLOs/SLAs

- **Routing Latency**: < 100ms (p95)
- **Success Rate**: > 99%
- **Availability**: 99.9%
- **Health Check Interval**: 30s
- **Metrics Export**: Every 10s
- **Service Discovery Sync**: Every 5 minutes

## 🚀 Quick Start

### Development (Docker Compose)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/agent-router

# Start full stack (router + redis + prometheus + grafana)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agent-router-metrics
```

**Services**:
- **Metrics**: http://localhost:9090/metrics
- **Health**: http://localhost:9090/health
- **Prometheus**: http://localhost:9091
- **Grafana**: http://localhost:3000 (admin/admin)
- **Redis**: localhost:6379

### Production (Temporal Workflows)

```python
from temporalio.client import Client
from temporal_workflows import start_all_workflows

# Connect to Temporal
client = await Client.connect("localhost:7233")

# Start all workflows
await start_all_workflows(
    temporal_client=client,
    router_config={
        "redis_url": "redis://redis:6379/0",
        "enable_circuit_breaker": True,
        "enable_metrics": True,
        "rate_limit": 1000
    }
)
```

### Usage from Code

```python
# Simple routing via MIO Manager integration
from mio_manager.integrations.agent_router_client import route_ai_request

result = await route_ai_request(
    capability="bia",
    request_data={"organization_id": "123"}
)

# Advanced usage
from agent_router import AIAgentRouter, AgentCapability

router = AIAgentRouter(
    redis_url="redis://localhost:6379/0",
    enable_circuit_breaker=True,
    enable_metrics=True,
    rate_limit=1000
)

result = await router.route_request(
    capability=AgentCapability.BIA_ANALYSIS,
    request_data={"organization": "Acme Corp"},
    context={"user_id": "123", "priority": "high"}
)
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  MIO Manager (Central Entry Point)                         │
│  ↓ Uses AgentRouterClient                                  │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  AI Agent Router v2.1                                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Global Rate Limiter (1000 req/min)                │ │
│  │  2. Find Capable Agents (by capability + health)      │ │
│  │  3. Advanced Load Balancing (priority→time→load)      │ │
│  │  4. Circuit Breaker Protection                        │ │
│  │  5. Execute Request                                   │ │
│  │  6. Update Metrics + Analytics                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   [Orchestrator] [Processor]  [Assistant]
   ai_orchestrator unified_ai  pdca_assistant

Monitoring Stack:
  Prometheus (scrapes :9090/metrics every 10s)
       ↓
  Grafana (dashboards + alerts)
       ↓
  Platform Admins
```

## 📊 Prometheus Metrics (18+)

### Request Metrics
- `ai_router_requests_total{capability, agent, status}` - Total requests
- `ai_router_request_duration_seconds{capability, agent}` - Request duration histogram
- `ai_router_fallback_total{capability}` - Fallback routing attempts
- `ai_router_errors_total{type}` - Errors by type
- `ai_router_no_agents_available_total` - No agents available events

### Agent Health Metrics
- `ai_router_agent_health{agent, role}` - Agent health status (1=healthy, 0=unhealthy)
- `ai_router_agent_response_time_seconds{agent}` - Agent response time histogram
- `ai_router_agent_load{agent}` - Current agent load

### Circuit Breaker Metrics
- `ai_router_circuit_breaker_state{agent}` - Circuit state (0=closed, 1=open, 2=half_open)
- `ai_router_circuit_breaker_failures_total{agent}` - Circuit failures

### Capability Metrics
- `ai_router_capability_requests_total{capability}` - Requests by capability
- `ai_router_capability_success_rate{capability}` - Success rate by capability

## 🔄 Temporal Workflows

### 1. AgentHealthMonitoringWorkflow
**Frequency**: Every 30 seconds
**Purpose**: Monitor all agents, send alerts if < 50% healthy

### 2. CircuitBreakerRecoveryWorkflow
**Frequency**: On-demand (triggered by open circuit breaker)
**Purpose**: Attempt recovery with exponential backoff, reset on success

### 3. ServiceDiscoverySyncWorkflow
**Frequency**: Every 5 minutes
**Purpose**: Sync with Service Registry, discover new agents, remove missing

### 4. MetricsExportWorkflow
**Frequency**: Every 1 minute
**Purpose**: Aggregate and export metrics, push to Pushgateway (optional)

## 🔗 Integration Points

### Required
- **Redis** - Request logging, analytics storage
- **AI Agents** - ai_orchestrator, unified_ai, pdca_assistant, github_app, document_ai

### Optional
- **Prometheus** - Metrics scraping
- **Grafana** - Visualization
- **Service Registry** - Dynamic agent registration
- **Temporal** - Workflow automation
- **MIO Manager** - Central coordination

## 📚 Documentation

### Core Documentation
- **README.md** (this file) - Overview and quick start
- **WORKFLOW_SPECIFICATION.md** - Job description, SLAs, workflows (500+ lines)
- **REPORTING_STRUCTURE.md** - Reporting hierarchy, metrics, dashboards

### Archive (Historical)
- **_archive/docs-history/ANALYSIS.md** - Initial analysis
- **_archive/docs-history/ENHANCEMENT_v2.0_COMPLETE.md** - v2.0 milestone
- **_archive/docs-history/INTEGRATION_COMPLETE.md** - Integration milestone
- **_archive/docs-history/AUTOMATION_COMPLETE.md** - Automation milestone

## 🎯 Statistics

| Metric | v1.0 | v2.0 | v2.1 (Final) |
|--------|------|------|--------------|
| **Lines of Code** | 295 | 750+ | 4850+ |
| **Files** | 2 | 8 | 16 |
| **Features** | 5 | 10 | 15+ |
| **Automation** | 0% | 0% | 100% ✅ |
| **Integration** | 0 | 0 | 4 ✅ |
| **Workflows** | 0 | 0 | 4 ✅ |
| **Metrics** | 0 | 18+ | 18+ ✅ |
| **Potential** | ~50% | ~85% | **100%** ✅ |

## ✅ Production Readiness Checklist

### Functionality
- ✅ Smart routing with load balancing
- ✅ Circuit breaker protection
- ✅ Rate limiting
- ✅ Health monitoring with auto-recovery
- ✅ Metrics export (Prometheus)
- ✅ Service discovery integration
- ✅ Graceful degradation

### Observability
- ✅ Structured logging (JSON)
- ✅ Prometheus metrics (18+)
- ✅ Health checks (30s interval)
- ✅ Analytics (Redis, last 1000)
- ✅ Grafana dashboards (ready)

### Reliability
- ✅ Circuit breaker (auto-recovery)
- ✅ Rate limiting (overload protection)
- ✅ Fallback routing
- ✅ Health daemon (background checks)
- ✅ Exponential backoff

### Automation
- ✅ Temporal workflows (4 workflows)
- ✅ GitHub Actions CI/CD
- ✅ Docker Compose (one-command)
- ✅ Automated testing
- ✅ Automated deployment

### Integration
- ✅ MIO Manager client
- ✅ Service Registry integration
- ✅ Prometheus integration
- ✅ Temporal integration
- ✅ Redis integration

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended for Dev/Test)
```bash
docker-compose up -d
```
**Pros**: Fastest, easiest, includes full monitoring stack

### Option 2: Kubernetes (Recommended for Production)
```bash
kubectl apply -f k8s/agent-router/
```
**Pros**: Scalable, high availability, cloud-native

### Option 3: Temporal Workflows (Recommended for Automation)
```python
await start_all_workflows(client, router_config)
```
**Pros**: Durable, fault-tolerant, long-running

### Option 4: GitHub Actions CI/CD
```bash
git push origin main
```
**Pros**: Automated testing, deployment, rollback

## 📈 Future Enhancements (Optional v3.0)

### If Needed:
1. **Distributed Tracing** (OpenTelemetry) - Full request tracing
2. **Request Caching** - Intelligent deduplication
3. **A/B Testing** - Traffic splitting, canary deployments
4. **Predictive Routing** - ML-based agent selection
5. **WebSocket Support** - Real-time streaming

## 📞 Support

For issues or questions:
- Check documentation in `WORKFLOW_SPECIFICATION.md`
- Review metrics at http://localhost:9091 (Prometheus)
- Check dashboards at http://localhost:3000 (Grafana)
- View logs: `docker-compose logs -f agent-router-metrics`

## 📄 License

Part of BCM Platform AI Infrastructure

---

**Status**: ✅ **PRODUCTION-READY** 🚀

**AI Agent Router v2.1** - Complete, automated, and ready to serve as the central nervous system for all AI requests!
