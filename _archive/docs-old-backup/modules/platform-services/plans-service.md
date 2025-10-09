# Plans Service

**Type**: Platform Service
**Domain**: Business Continuity Management
**Status**: Active
**Version**: 2.0.0

## Overview

The Plans Service provides centralized repository and management for all business continuity plans. It implements plan storage, retrieval, distribution, and activation workflows with role-based access control.

## Metrics

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | 8,612 |
| **Python Files** | 38 |
| **Classes** | 79 |
| **Functions** | 28 |
| **API Endpoints** | 32 |
| **Dependencies** | 64 |

## API Reference

### Health & Monitoring

**`GET /health`**
Service health check endpoint.

**`GET /metrics`**
Prometheus metrics endpoint.

See service-specific API documentation for complete endpoint reference.

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- RabbitMQ 3.12+

### Setup

```bash
cd platform-services/plans_service

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with service configuration

# Initialize database
python -m alembic upgrade head

# Start service
python main.py
```

## Configuration

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://user:pass@localhost:5672/

# Service Port
SERVICE_PORT=8000
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=plans_service --cov-report=html
```

## Integration

### Event Bus Integration

The service publishes and subscribes to platform events:

```python
from infrastructure.eventbus import EventBus

# Subscribe to events
await event_bus.subscribe(
    pattern="plans_service.*",
    handler=handle_event
)
```

### Workflow Intelligence Integration

Integrates with workflow intelligence for process orchestration:

```python
from ai_foundation import WorkflowIntelligenceClient

client = WorkflowIntelligenceClient()
await client.start_workflow(type="plans_service")
```

## Standards Compliance

This service adheres to:

- **ISO 22301:2019** - Business Continuity Management Systems
- **ISO/IEC/IEEE 26514:2022** - Software documentation
- **ISO/IEC 27001:2022** - Information security management (where applicable)

## Related Services

- [ai-foundation](../../intelligent-core/ai-foundation/README.md) - AI services
- [workflow_intelligence](../../intelligent-core/workflow_intelligence/README.md) - Workflow orchestration

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-08
**Maintainer**: AI Platform Team
