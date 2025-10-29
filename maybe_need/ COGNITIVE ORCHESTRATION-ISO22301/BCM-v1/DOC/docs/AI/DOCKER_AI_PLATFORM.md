# Docker AI Native BCM Platform

## 🌟 Overview

The BCM Platform has been enhanced with Docker AI native capabilities, providing enterprise-grade AI orchestration for Business Continuity Management. This implementation leverages cutting-edge Docker AI technologies including Model Runner, MCP Protocol, and Docker Offload.

## 🏗️ Architecture

### Core Components

```
🧠 Docker Model Runner (8088)  ← Local LLM inference (OpenAI compatible)
🔌 MCP Gateway (8089)          ← Model Context Protocol for tool integration
🛠️ BCM MCP Server (8087)       ← BCM-specific tools and APIs
🤖 AI Orchestrator Native      ← Enhanced orchestrator with Docker AI
🎯 Specialized BCM Agents       ← Domain-specific AI agents
🔍 Agent Registry (8099)       ← Service discovery and monitoring
```

### AI Agent Specialization

- **BIA Agent**: Business Impact Analysis with GPU acceleration
- **Incident Agent**: Automated response with TheHive/Grafana MCP integration
- **Compliance Agent**: ISO 22301 knowledge base and gap analysis

## 🚀 Quick Start

### Prerequisites

- Docker Desktop with AI features enabled
- 8GB+ RAM recommended
- GPU support optional (NVIDIA Docker for acceleration)

### 1. Basic Infrastructure Test

```bash
# Test core infrastructure
docker-compose -f docker-compose.docker-ai.yml up -d postgres redis rabbitmq

# Verify services
docker-compose -f docker-compose.docker-ai.yml ps
```

### 2. Start Docker AI Services

```bash
# Start Docker Model Runner (downloads ~3GB AI models)
docker-compose -f docker-compose.docker-ai.yml up -d model-runner

# Start MCP integration
docker-compose -f docker-compose.docker-ai.yml up -d mcp-gateway bcm-mcp-server

# Start AI orchestrator
docker-compose -f docker-compose.docker-ai.yml up -d ai-orchestrator-native
```

### 3. Deploy Specialized Agents

```bash
# Start BCM AI agents
docker-compose -f docker-compose.docker-ai.yml up -d bia-agent incident-agent compliance-agent

# Start agent registry
docker-compose -f docker-compose.docker-ai.yml up -d agent-registry
```

### 4. Full Platform Deployment

```bash
# Run comprehensive integration test
./tests/integration/test-docker-ai.sh
```

## 🔧 Configuration

### Environment Variables

Create `.env` file with the following configuration:

```env
# Database
DB_PASSWORD=postgres123
KEYCLOAK_DB_PASSWORD=keycloak123
KEYCLOAK_ADMIN_PASSWORD=admin123

# Message Queue
RABBITMQ_PASSWORD=bcm123

# Docker AI Configuration
GPU_ENABLED=false                    # Set to true if GPU available
GPU_OFFLOAD_ENABLED=false           # Enable Docker Offload
DOCKER_OFFLOAD_ENDPOINT=             # Cloud GPU endpoint

# Optional integrations
GITHUB_APP_ID=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

### GPU Acceleration

For GPU-enabled inference:

1. Install NVIDIA Docker support
2. Set `GPU_ENABLED=true` in `.env`
3. Configure Docker Offload for cloud GPU acceleration

## 📡 API Endpoints

### Docker Model Runner (Local LLM)

```bash
# List available models
curl http://localhost:8088/v1/models

# Chat completion (OpenAI compatible)
curl -X POST http://localhost:8088/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Analyze BCM risk scenario"}],
    "max_tokens": 100
  }'
```

### MCP Tools Integration

```bash
# List available BCM tools
curl http://localhost:8087/mcp/tools/list

# Execute BCM process analysis
curl -X POST http://localhost:8087/mcp/tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "bcm_process_list",
    "parameters": {"tenant_id": "org_123"}
  }'

# Incident classification
curl -X POST http://localhost:8087/mcp/tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "bcm_incident_classify",
    "parameters": {"incident_description": "Database server failure"}
  }'
```

### AI Agent Orchestration

```bash
# Route to specialized agents
curl -X POST http://localhost:8000/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "bia",
    "data": {"business_process": "customer_support"},
    "context": {"priority": "high"}
  }'

# Check agent health
curl http://localhost:8000/ai/agents/health

# Get analytics
curl http://localhost:8000/ai/agents/analytics
```

## 🛠️ MCP Tools Available

### Process Management
- `bcm_process_list` - List business processes with criticality
- `bcm_process_analyze` - BIA/Risk/Dependency analysis

### Incident Management
- `bcm_incident_create` - Create incident records
- `bcm_incident_classify` - AI-powered incident classification

### Risk Assessment
- `bcm_risk_assessment` - Process risk evaluation
- `bcm_compliance_check` - ISO 22301 compliance verification

### PDCA Cycle
- `bcm_pdca_suggest` - Next best action recommendations
- `bcm_audit_evidence` - Gather audit evidence

### Integration Tools
- `bcm_odoo_query` - Direct Odoo database queries
- `bcm_keycloak_auth` - Authentication and authorization
- `bcm_redis_cache` - Cache and session management

## 🔍 Monitoring & Analytics

### Health Monitoring

- **Service Health**: `http://localhost:8000/ai/agents/health`
- **Agent Analytics**: `http://localhost:8000/ai/agents/analytics`
- **MCP Server Status**: `http://localhost:8087/health`
- **Model Runner**: `http://localhost:8088/v1/models`

### Performance Metrics

The platform tracks:
- Agent response times
- Request distribution
- Success/failure rates
- Load balancing effectiveness
- GPU utilization (if enabled)

## 🚀 Docker AI Features

### Local LLM Inference
- OpenAI-compatible API
- Multiple model support
- CPU/GPU acceleration
- Secure local processing

### MCP Protocol Integration
- Standardized tool integration
- Secure API access
- Extensible tool registry
- Enterprise authentication

### Agent Specialization
- Domain-specific expertise
- Intelligent routing
- Load balancing
- Failover support

### Enterprise Security
- Local data processing
- Secure tool integration
- Role-based access control
- Audit trail logging

## 📋 Testing

### Integration Tests

```bash
# Full platform test
./tests/integration/test-docker-ai.sh

# Basic agent test
./tests/integration/test-ai-agents.sh
```

### Unit Tests

```bash
# MCP server tests
cd docker-ai/mcp-server && python -m pytest

# AI orchestrator tests
cd services/ai_orchestrator && python -m pytest
```

### Performance Tests

```bash
# Load testing (coming soon)
./tests/performance/load-test.sh
```

## 🔧 Development

### Adding New MCP Tools

1. Define tool in `docker-ai/mcp-server/server.yaml`
2. Implement in `docker-ai/mcp-server/main.py`
3. Register in MCP gateway
4. Test with integration suite

### Creating New AI Agents

1. Create agent directory in `services/ai/`
2. Implement agent logic with MCP integration
3. Add to `docker-compose.docker-ai.yml`
4. Update agent registry configuration

### Contributing

1. Follow Docker AI best practices
2. Implement MCP protocol standards
3. Add comprehensive tests
4. Update documentation

## 🎯 Roadmap

### Phase 1 (Completed)
- ✅ Docker Model Runner integration
- ✅ MCP Protocol implementation
- ✅ Specialized BCM agents
- ✅ Agent orchestration system

### Phase 2 (In Progress)
- 🔄 Docker Offload GPU acceleration
- 🔄 Advanced MCP tool registry
- 🔄 Multi-model LLM support
- 🔄 Enterprise security hardening

### Phase 3 (Planned)
- 📋 Multi-cloud deployment
- 📋 Advanced analytics dashboard
- 📋 Custom model fine-tuning
- 📋 Enterprise SSO integration

## 📞 Support

For technical support and questions:
- GitHub Issues: [BCM Platform Issues](https://github.com/seh-foundation/iso-22301/issues)
- Documentation: See `docs/` directory
- Docker AI Docs: [Docker AI Documentation](https://docs.docker.com/guides/agentic-ai/)

---

**🎉 The BCM Platform is now Docker AI native and ready for enterprise deployment!**