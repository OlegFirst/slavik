# Intelligent Core

**Component**: Core AI & Intelligence Layer
**Status**: Active
**Version**: 2.1.0
**Last Updated**: 2025-10-19

## Overview

The Intelligent Core represents the foundational AI and intelligence layer of the AI-Platform-ISO system. This layer provides enterprise-grade artificial intelligence, workflow orchestration, predictive analytics, and domain expertise capabilities that power all platform services.

The Intelligent Core implements a comprehensive suite of AI services including machine learning, natural language processing, knowledge management, workflow automation, and collaborative intelligence. All modules adhere to ISO/IEC AI standards and provide standardized interfaces for service integration.

### Important: BCM Domain Migration (October 2025)

**Note:** The BCM tactical AI colleagues (BIA Specialist, Risk Analyst, etc.) have been **migrated** to `/platform_services/bcm_domain/ai_colleagues/`.

The `expertise_center` now contains only:
- **Strategic AI Experts** (`ai_experts/specialists/`) - Program-level BCM expertise
- **Backward compatibility symlink** (`ai_office/`) - Points to `bcm_domain/ai_colleagues/`

See [BCM Domain Migration](../docs/bcm-domain-migration.md) for details.

## Architecture

### Layer Components

```mermaid
graph TB
    subgraph "AI Foundation Layer"
        AF[ai-foundation]
        WI[workflow_intelligence]
        Pred[predictive]
    end

    subgraph "Orchestration Layer"
        Orch[orchestration]
        WE[workflow-engine]
        Event[event_intelligence]
    end

    subgraph "Intelligence Layer"
        EC[expertise-center]
        Coll[collective]
        Comm[community_intelligence]
    end

    subgraph "Optimization Layer"
        WO[ai_workflow_optimizer]
    end

    AF --> WI
    WI --> WE
    Orch --> AF
    Orch --> WI
    EC --> AF
    Pred --> AF
    Event --> WI
    WO --> WI
```

## Modules

### AI Foundation Layer

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [ai_foundation](./ai_foundation/README.md) | Core AI services: LLM routing, RAG, embeddings, ML | 23,019 | ✅ Active |
| [workflow_intelligence](./workflow_intelligence/README.md) | Workflow orchestration, state machines, BPMN engine | 24,392 | ✅ Active |
| [predictive](./predictive/README.md) | Predictive analytics and proactive recommendations | 4,761 | ✅ Active |
| [scenario_intelligence](./scenario_intelligence/README.md) | Scenario generation, simulation, and what-if analysis | 22,487 | ✅ Active |

### Orchestration Layer

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [orchestration](./orchestration/README.md) | Centralized AI service coordination and control | 25,171 | ✅ Active |
| [workflow_engine](./workflow_engine/README.md) | BPMN 2.0 compliant workflow execution engine | 6,361 | ✅ Active |
| [event_intelligence](./event_intelligence/README.md) | Intelligent event analysis and automated healing | 3,545 | ✅ Active |

### Intelligence Layer

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [expertise_center](./expertise_center/README.md) | Strategic AI experts and specialists (BCM Advisor, etc.) | 11,846 | ✅ Active |
| [collective](./collective/README.md) | Collective intelligence and privacy-preserving collaboration | 5,230 | ✅ Active |
| [community_intelligence](./community_intelligence/README.md) | Knowledge sharing and collaborative learning | 8,116 | ✅ Active |

### Optimization Layer

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [ai_workflow_optimizer](./ai_workflow_optimizer/README.md) | ML-powered workflow optimization | 1,701 | ✅ Active |

### Platform Meta Layer

| Module | Description | LOC | Status |
|--------|-------------|-----|--------|
| [system_bcm_service](./system_bcm_service/README.md) | Platform self-BCM: Platform applies BCM to itself | ~5,000 | ✅ Active |
| [shared](./shared/README.md) | Shared utilities, models, and base classes for intelligent_core | ~3,000 | ✅ Active |

## Total Metrics

| Metric | Value |
|--------|-------|
| **Total Modules** | 13 |
| **Total Lines of Code** | ~145,000 |
| **Python Files** | 550+ |
| **Total Classes** | 750+ |
| **Total Functions** | 2,500+ |
| **API Endpoints** | 400+ |

**Note:** Metrics updated 2025-10-19 after BCM Domain migration

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with JSONB support
- Redis 7+ for caching and state management
- RabbitMQ 3.12+ for event-driven architecture
- Qdrant vector database for RAG pipelines

### Setup All Modules

```bash
cd intelligent-core

# Install all dependencies
for module in */; do
    if [ -f "$module/requirements.txt" ]; then
        echo "Installing $module..."
        pip install -r "$module/requirements.txt"
    fi
done

# Initialize databases
python -m alembic upgrade head

# Start core services
docker-compose up -d
```

## Configuration

Core environment variables shared across modules:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://user:pass@localhost:5672/

# AI Services
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

## Development

### Running Tests

```bash
# Test all modules
pytest intelligent-core/ -v --cov=intelligent-core

# Test specific module
pytest intelligent-core/ai-foundation/tests/ -v
```

### Code Quality

All modules follow strict quality standards:

- Test coverage: ≥80%
- Complexity: ≤15 cyclomatic complexity
- Type hints: Required for all public APIs
- Documentation: Comprehensive docstrings

## Integration Patterns

### Service-to-Service Communication

```python
from shared.clients import AIFoundationClient, WorkflowIntelligenceClient

# AI Foundation integration
ai_client = AIFoundationClient()
response = await ai_client.llm_route(prompt="...")

# Workflow Intelligence integration
wf_client = WorkflowIntelligenceClient()
workflow_id = await wf_client.start_workflow(type="bia")
```

### Event Bus Integration

```python
from infrastructure.eventbus import EventBus

# Subscribe to events
await event_bus.subscribe(
    pattern="workflow.*.completed",
    handler=handle_workflow_completion
)

# Publish events
await event_bus.publish(
    event_type="ai.prediction.generated",
    payload={"prediction_id": "pred_123"}
)
```

## Performance Benchmarks

- **AI Foundation LLM Routing**: <50ms (P95)
- **Workflow State Transitions**: <50ms (P95)
- **Predictive Analytics**: <200ms (P95)
- **Concurrent Workflows**: 1000+ simultaneous instances
- **Event Processing**: 5000+ events/second

## Standards Compliance

The Intelligent Core adheres to:

- **ISO/IEC 42001:2023** - AI Management System
- **ISO/IEC 23894:2023** - AI Risk Management
- **ISO/IEC 22989:2022** - AI Concepts and Terminology
- **ISO/IEC/IEEE 26514:2022** - Software documentation
- **ISO/IEC/IEEE 42010:2011** - Architecture description
- **ISO 22301:2019** - Business Continuity Management Systems

## Related Components

- [Platform Services](../platform-services/README.md) - Domain-specific business services
- [Infrastructure](../infrastructure/README.md) - Platform infrastructure layer
- [Interface](../interface/README.md) - User interface layer

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-19
**Maintainer**: AI Platform Team
**Documentation Status**: Professional standards compliant (ISO/IEC/IEEE 26514:2022)

## Recent Changes

### October 2025 - BCM Domain Migration
- ✅ BCM tactical AI colleagues migrated to `/platform_services/bcm_domain/`
- ✅ Added `scenario_intelligence` module (22,487 LOC)
- ✅ Added `system_bcm_service` (platform self-BCM)
- ✅ Added `shared` module for intelligent_core utilities
- ✅ Fixed naming: `ai-foundation` → `ai_foundation`, `workflow-engine` → `workflow_engine`
- ✅ Total modules: 10 → 13
- ✅ Total LOC: 114K → 145K

See full migration report: [BCM Domain Migration Complete](../doc-project/BCM_DOMAIN_MIGRATION_COMPLETE.md)
