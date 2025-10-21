# Intelligent Core - AI & Intelligence Layer

**Component**: Core AI & Intelligence Layer
**Status**: Production
**Version**: 2.1.0
**Last Updated**: 2025-10-21
**ISO Standards**: ISO/IEC 42001:2023, ISO/IEC 23894:2023, ISO 22301:2019

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Modules](#modules)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Integration Patterns](#integration-patterns)
- [Performance Benchmarks](#performance-benchmarks)
- [Standards Compliance](#standards-compliance)
- [Recent Changes](#recent-changes)

---

## 🎯 Overview

The **Intelligent Core** is the foundational AI and intelligence layer of the AI-Platform-ISO system. It provides enterprise-grade artificial intelligence, workflow orchestration, predictive analytics, and domain expertise capabilities that power all platform services.

### Key Capabilities

- **Machine Learning & AI**: Advanced LLM routing, RAG pipelines, embeddings, ML models
- **Workflow Orchestration**: BPMN 2.0 compliant workflow engine with state machines
- **Predictive Analytics**: Proactive recommendations and forecasting
- **Scenario Intelligence**: Simulation and what-if analysis
- **Knowledge Management**: Collective intelligence and knowledge sharing
- **Automated Healing**: Intelligent event analysis and self-recovery

### Important: BCM Domain Migration (October 2025)

**Note**: BCM tactical AI colleagues (BIA Specialist, Risk Analyst, Planning Coordinator, etc.) have been **migrated** to `/platform_services/bcm_domain/ai_colleagues/`.

The `expertise_center` now contains:
- **Strategic AI Experts** (`ai_experts/specialists/`) - Program-level BCM expertise
- **Backward compatibility symlink** (`ai_office/`) → Points to `bcm_domain/ai_colleagues/`

📖 See [BCM Domain Migration](../doc-project/BCM_DOMAIN_MIGRATION_COMPLETE.md) for details.

---

## 🏗️ Architecture

### System Layers

```mermaid
graph TB
    subgraph "AI Foundation Layer"
        AF[ai_foundation<br/>Core AI Services]
        WI[workflow_intelligence<br/>Orchestration]
        Pred[predictive<br/>Analytics]
        SI[scenario_intelligence<br/>Simulation]
    end

    subgraph "Orchestration Layer"
        Orch[orchestration<br/>Coordination]
        WE[workflow_engine<br/>BPMN Engine]
        Event[event_intelligence<br/>Event Analysis]
    end

    subgraph "Intelligence Layer"
        EC[expertise_center<br/>Strategic Experts]
        Coll[collective<br/>Collective Intelligence]
        Comm[community_intelligence<br/>Knowledge Sharing]
    end

    subgraph "Optimization Layer"
        WO[ai_workflow_optimizer<br/>ML Optimization]
    end

    subgraph "Platform Meta Layer"
        BCMS[system_bcm_service<br/>Self-BCM]
        Shared[shared<br/>Utilities]
    end

    AF --> WI
    WI --> WE
    Orch --> AF
    Orch --> WI
    EC --> AF
    Pred --> AF
    SI --> AF
    Event --> WI
    WO --> WI
    BCMS --> AF
```

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.11+ |
| **Database** | PostgreSQL | 14+ |
| **Cache** | Redis | 7+ |
| **Message Queue** | RabbitMQ | 3.12+ |
| **Vector DB** | Qdrant | Latest |
| **AI Models** | Anthropic Claude, OpenAI GPT | Latest |
| **Workflow Engine** | Custom BPMN 2.0 | 2.0 |

---

## 📦 Modules

### AI Foundation Layer (4 modules)

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [ai_foundation](./ai_foundation/README.md) | Core AI services: LLM routing, RAG, embeddings, ML models | 23,019 | ✅ Production |
| [workflow_intelligence](./workflow_intelligence/README.md) | Workflow orchestration, state machines, BPMN engine | 24,392 | ✅ Production |
| [predictive](./predictive/README.md) | Predictive analytics and proactive recommendations | 4,761 | ✅ Production |
| [scenario_intelligence](./scenario_intelligence/README.md) | Scenario generation, simulation, what-if analysis | 22,487 | ✅ Production |

### Orchestration Layer (3 modules)

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [orchestration](./orchestration/README.md) | Centralized AI service coordination and control | 25,171 | ✅ Production |
| [workflow_engine](./workflow_engine/README.md) | BPMN 2.0 compliant workflow execution engine | 6,361 | ✅ Production |
| [event_intelligence](./event_intelligence/README.md) | Intelligent event analysis and automated healing | 3,545 | ✅ Production |

### Intelligence Layer (3 modules)

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [expertise_center](./expertise_center/README.md) | Strategic AI experts and specialists (BCM Advisor, Security Expert) | 11,846 | ✅ Production |
| [collective](./collective/README.md) | Collective intelligence and privacy-preserving collaboration | 5,230 | ✅ Production |
| [community_intelligence](./community_intelligence/README.md) | Knowledge sharing and collaborative learning | 8,116 | ✅ Production |

### Optimization Layer (1 module)

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [ai_workflow_optimizer](./ai_workflow_optimizer/README.md) | ML-powered workflow optimization and tuning | 1,701 | ✅ Production |

### Platform Meta Layer (2 modules)

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [system_bcm_service](./system_bcm_service/README.md) | Platform self-BCM: Platform applies BCM to itself | ~5,000 | ✅ Production |
| [shared](./shared/README.md) | Shared utilities, models, and base classes | ~3,000 | ✅ Production |

---

## 📊 Total Metrics

| Metric | Value |
|--------|-------|
| **Total Modules** | 13 |
| **Total Lines of Code** | ~145,000 |
| **Python Files** | 550+ |
| **Total Classes** | 750+ |
| **Total Functions** | 2,500+ |
| **API Endpoints** | 400+ |
| **Test Coverage** | >80% |

*Metrics updated: 2025-10-21 (post BCM Domain migration)*

---

## 🚀 Installation

### Prerequisites

```bash
# Required
Python 3.11+
PostgreSQL 14+ (with JSONB support)
Redis 7+ (caching and state management)
RabbitMQ 3.12+ (event-driven architecture)
Qdrant (vector database for RAG)

# Optional but recommended
Docker 24+
Docker Compose 2+
```

### Quick Start

```bash
# Clone and navigate
cd /Users/MD/AI-Platform-ISO/intelligent_core

# Install all module dependencies
for module in */; do
    if [ -f "$module/requirements.txt" ]; then
        echo "Installing $module..."
        pip install -r "$module/requirements.txt"
    fi
done

# Initialize databases
python -m alembic upgrade head

# Start infrastructure services
docker-compose up -d postgres redis rabbitmq qdrant

# Run all services
python main.py
```

### Individual Module Setup

```bash
# Example: Set up ai_foundation only
cd ai_foundation
pip install -r requirements.txt
python -m pytest tests/ -v
python main.py
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in `intelligent_core/`:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_platform
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_platform
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_URL=amqp://user:pass@localhost:5672/
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672

# AI Services
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
CLAUDE_MODEL=claude-3-opus-20240229
GPT_MODEL=gpt-4-turbo-preview

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=optional_key

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
JWT_SECRET=your_jwt_secret_key
API_KEY_HASH=bcrypt_hashed_key
```

### Module-Specific Configuration

Each module has its own `config.py` or `settings.py`. See individual module READMEs for details.

---

## 👨‍💻 Development

### Running Tests

```bash
# Test all modules
pytest intelligent_core/ -v --cov=intelligent_core --cov-report=html

# Test specific module
pytest intelligent_core/ai_foundation/tests/ -v

# Test with coverage report
pytest --cov=intelligent_core --cov-report=term-missing

# Run integration tests
pytest intelligent_core/tests/integration/ -v -m integration
```

### Code Quality Standards

All modules follow strict quality requirements:

| Standard | Requirement | Tool |
|----------|------------|------|
| **Test Coverage** | ≥80% | pytest-cov |
| **Cyclomatic Complexity** | ≤15 | radon, mccabe |
| **Type Hints** | 100% public APIs | mypy |
| **Documentation** | Comprehensive docstrings | pydocstyle |
| **Code Style** | PEP 8 compliant | black, flake8, pylint |
| **Security** | No known vulnerabilities | bandit, safety |

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes and run quality checks
black intelligent_core/
flake8 intelligent_core/
mypy intelligent_core/
pytest intelligent_core/ -v

# 3. Commit with conventional commits
git commit -m "feat(ai_foundation): add new RAG pipeline"

# 4. Push and create PR
git push origin feature/your-feature
```

---

## 🔗 Integration Patterns

### Service-to-Service Communication

```python
from shared.clients import AIFoundationClient, WorkflowIntelligenceClient

# AI Foundation integration
ai_client = AIFoundationClient()
response = await ai_client.llm_route(
    prompt="Analyze this business impact",
    context={"domain": "bcm", "task": "bia"}
)

# Workflow Intelligence integration
wf_client = WorkflowIntelligenceClient()
workflow_id = await wf_client.start_workflow(
    workflow_type="bia",
    input_data={"process_id": "proc_123"}
)
```

### Event Bus Integration

```python
from infrastructure.eventbus import EventBus

# Subscribe to events
event_bus = EventBus()
await event_bus.subscribe(
    pattern="workflow.*.completed",
    handler=handle_workflow_completion
)

# Publish events
await event_bus.publish(
    event_type="ai.prediction.generated",
    payload={
        "prediction_id": "pred_123",
        "confidence": 0.95,
        "type": "risk_forecast"
    }
)
```

### RAG Pipeline Integration

```python
from ai_foundation.rag import RAGPipeline

# Initialize RAG pipeline
rag = RAGPipeline(
    collection_name="bcm_knowledge",
    embedding_model="text-embedding-3-large"
)

# Query knowledge base
results = await rag.query(
    question="What is RTO in BCM?",
    top_k=5,
    filter={"domain": "bcm"}
)
```

---

## ⚡ Performance Benchmarks

### Response Times (P95)

| Operation | P95 Latency | Notes |
|-----------|-------------|-------|
| **LLM Routing** | <50ms | Claude Opus, GPT-4 |
| **Workflow State Transition** | <50ms | BPMN engine |
| **Predictive Analytics** | <200ms | ML inference |
| **RAG Query** | <150ms | Vector similarity search |
| **Event Processing** | <10ms | RabbitMQ + Redis |

### Throughput

| Metric | Capacity |
|--------|----------|
| **Concurrent Workflows** | 1,000+ instances |
| **Events/Second** | 5,000+ |
| **LLM Requests/Minute** | 100+ |
| **RAG Queries/Second** | 50+ |

### Resource Usage

| Resource | Typical | Peak |
|----------|---------|------|
| **CPU** | 30% | 80% |
| **Memory** | 4GB | 8GB |
| **Database Connections** | 50 | 200 |
| **Redis Memory** | 1GB | 2GB |

---

## 📜 Standards Compliance

The Intelligent Core adheres to:

### ISO Standards

- **ISO/IEC 42001:2023** - AI Management System
- **ISO/IEC 23894:2023** - AI Risk Management
- **ISO/IEC 22989:2022** - AI Concepts and Terminology
- **ISO/IEC/IEEE 26514:2022** - Software Documentation
- **ISO/IEC/IEEE 42010:2011** - Architecture Description
- **ISO 22301:2019** - Business Continuity Management Systems

### Best Practices

- **Twelve-Factor App** methodology
- **SOLID** principles
- **Domain-Driven Design** (DDD)
- **Microservices** architecture
- **Event-Driven Architecture** (EDA)
- **Test-Driven Development** (TDD)

---

## 🔄 Recent Changes

### October 2025 - BCM Domain Migration & Enhancements

**Major Changes:**
- ✅ **BCM Migration**: Tactical AI colleagues moved to `/platform_services/bcm_domain/ai_colleagues/`
- ✅ **New Modules**: Added `scenario_intelligence` (22,487 LOC), `system_bcm_service` (~5,000 LOC), `shared` (~3,000 LOC)
- ✅ **Naming Fix**: Standardized module names (dashes → underscores)
- ✅ **Metrics Update**: 10 → 13 modules, 114K → 145K LOC
- ✅ **Documentation**: Comprehensive README overhaul

**Detailed Breakdown:**

| Change | Before | After | Impact |
|--------|--------|-------|--------|
| Total Modules | 10 | 13 | +3 modules |
| Total LOC | 114,142 | ~145,000 | +30,858 LOC |
| Python Files | 481 | 550+ | +69 files |
| Classes | 664 | 750+ | +86 classes |
| API Endpoints | 332 | 400+ | +68 endpoints |

**Module Changes:**
- ✅ `scenario_intelligence/` - NEW! Scenario generation and simulation
- ✅ `system_bcm_service/` - NEW! Platform self-BCM capabilities
- ✅ `shared/` - NEW! Common utilities for intelligent_core
- ✅ `expertise_center/ai_office/` - Now symlink to bcm_domain

**Migration Documentation:**
- 📖 [BCM Domain Migration Complete](../doc-project/BCM_DOMAIN_MIGRATION_COMPLETE.md)
- 📖 [Architecture Decision Records](../docs/adr/)

---

## 📚 Related Components

- [Platform Services](../platform_services/README.md) - Domain-specific business services (BCM, Risk, etc.)
- [Infrastructure](../infrastructure/README.md) - Platform infrastructure layer (Kubernetes, monitoring)
- [Interface](../interface/README.md) - User interface layer (frontend, APIs)
- [Documentation](../docs/README.md) - Architecture, ADRs, guides

---

## 📞 Support & Contributing

### Getting Help

- 📖 **Documentation**: `/docs/` directory
- 🐛 **Issue Tracker**: Internal GitLab
- 💬 **Slack**: #ai-platform-core channel
- 📧 **Email**: ai-platform-team@company.com

### Contributing

1. Read [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Follow [Code of Conduct](../CODE_OF_CONDUCT.md)
3. Submit PRs with comprehensive tests
4. Ensure ≥80% code coverage
5. Follow conventional commit messages

---

## 📄 License

**Proprietary** - AI-Platform-ISO
© 2025 Company Name. All rights reserved.

---

## 📊 Quick Reference

### Module Directory Structure

```
intelligent_core/
├── ai_foundation/          # Core AI services (23K LOC)
├── workflow_intelligence/  # Workflow orchestration (24K LOC)
├── predictive/             # Predictive analytics (5K LOC)
├── scenario_intelligence/  # Scenario simulation (22K LOC)
├── orchestration/          # Service coordination (25K LOC)
├── workflow_engine/        # BPMN engine (6K LOC)
├── event_intelligence/     # Event analysis (4K LOC)
├── expertise_center/       # Strategic AI experts (12K LOC)
├── collective/             # Collective intelligence (5K LOC)
├── community_intelligence/ # Knowledge sharing (8K LOC)
├── ai_workflow_optimizer/  # ML optimization (2K LOC)
├── system_bcm_service/     # Self-BCM (5K LOC)
├── shared/                 # Common utilities (3K LOC)
├── main.py                 # Entry point
├── docker-compose.yml      # Infrastructure
├── requirements.txt        # Dependencies
└── README.md              # This file
```

### Quick Commands

```bash
# Start all services
docker-compose up -d

# Run specific service
python -m ai_foundation.main

# Run tests
pytest intelligent_core/ -v

# Check code quality
black . && flake8 . && mypy .

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

**Last Updated**: 2025-10-21
**Maintainer**: AI Platform Team
**Version**: 2.1.0
**Status**: ✅ Production Ready

**Documentation Compliance**: ISO/IEC/IEEE 26514:2022 ✓
