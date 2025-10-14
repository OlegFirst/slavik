#!/usr/bin/env python3
"""
Batch documentation generator for intelligent-core modules
Generates professional documentation for all modules
"""

import os
from pathlib import Path

# Module configurations
MODULES = {
    'community_intelligence': {
        'port': 8030,
        'description': 'Community-driven knowledge creation through peer review and reputation',
        'features': [
            'Auto-contribution from workflow completions',
            'Peer review system with quality scoring',
            'Reputation economy with gamification',
            'Case library with semantic search',
            'Smart anonymization',
        ],
        'iso_clauses': ['9.1', '10.2', 'A.17'],
        'skip': ['TECHNICAL_SPECIFICATION.md']  # Already exists
    },
    'learning-system': {
        'port': 8033,
        'description': 'Adaptive learning system for organizational knowledge management',
        'features': [
            'Knowledge graph construction',
            'Lesson learned capture',
            'Training recommendation engine',
            'Competency tracking',
            'Learning path optimization',
        ],
        'iso_clauses': ['7.2', '7.3', '9.1', 'A.17'],
        'skip': ['TECHNICAL_SPECIFICATION.md']  # Already exists
    },
    'knowledge-system': {
        'port': 8034,
        'description': 'Centralized knowledge management and retrieval system',
        'features': [
            'Document management',
            'Knowledge base indexing',
            'Full-text and semantic search',
            'Version control',
            'Access control',
        ],
        'iso_clauses': ['7.5', 'A.17'],
        'skip': []
    },
    'workflow-engine': {
        'port': 8035,
        'description': 'BCM workflow orchestration and state management',
        'features': [
            'Workflow definition and execution',
            'State machine implementation',
            'Transition validation',
            'Progress tracking',
            'Checkpoint management',
        ],
        'iso_clauses': ['8.1', '8.2', '8.3', '8.4'],
        'skip': []
    },
    'event_intelligence': {
        'port': 8036,
        'description': 'Event pattern detection and predictive analytics',
        'features': [
            'Event pattern learning',
            'Anomaly detection',
            'Auto-discovery of services',
            'Gap prediction',
            'Code healing',
        ],
        'iso_clauses': ['9.1', '10.1'],
        'skip': []
    },
    'orchestration': {
        'port': 8037,
        'description': 'Cross-module orchestration and coordination',
        'features': [
            'Multi-service coordination',
            'Saga pattern implementation',
            'Distributed transaction management',
            'Service mesh integration',
            'Circuit breaker patterns',
        ],
        'iso_clauses': ['8.1', '8.5'],
        'skip': []
    },
    'ai_workflow_optimizer': {
        'port': 8038,
        'description': 'AI-powered workflow optimization and recommendations',
        'features': [
            'Workflow performance analysis',
            'Bottleneck detection',
            'Resource optimization',
            'Path recommendation',
            'Efficiency scoring',
        ],
        'iso_clauses': ['9.1', '9.3', '10.2'],
        'skip': []
    },
    'shared': {
        'port': None,
        'description': 'Shared utilities and common components',
        'features': [
            'EventBus client',
            'Database clients',
            'Authentication utilities',
            'Logging framework',
            'Configuration management',
        ],
        'iso_clauses': ['N/A'],
        'skip': []
    },
    'wrappers': {
        'port': None,
        'description': 'Service wrappers for external integrations',
        'features': [
            'External service adapters',
            'Protocol translation',
            'Rate limiting',
            'Circuit breakers',
            'Retry logic',
        ],
        'iso_clauses': ['N/A'],
        'skip': []
    },
}

def create_architecture_doc(module_name, config):
    """Generate ARCHITECTURE.md"""
    port_info = f"**Port**: {config['port']}\n" if config['port'] else ""

    content = f"""# {module_name.replace('-', ' ').replace('_', ' ').title()} - Architecture

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Overview

{config['description'].capitalize()}.

{port_info}
## Components

### Core Components

"""
    for feature in config['features']:
        content += f"- **{feature.split(':')[0] if ':' in feature else feature}**\n"

    content += """
## Technology Stack

- Python 3.11+
- FastAPI (if service)
- PostgreSQL (Supabase)
- Redis (EventBus)

## Integration Points

### Internal Dependencies

- `shared.database` - Database client
- `shared.eventbus` - Event messaging
- `ai_foundation` - AI capabilities

### External Dependencies

- Supabase PostgreSQL
- Redis
- Prometheus (metrics)

## Data Flow

```
Request → API Layer → Business Logic → Data Layer → Response
           ↓
      Event Publishing
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
- Review Date: 2025-10-09
"""
    return content

def create_business_logic_doc(module_name, config):
    """Generate BUSINESS_LOGIC.md"""
    content = f"""# {module_name.replace('-', ' ').replace('_', ' ').title()} - Business Logic

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Business Overview

{config['description'].capitalize()}.

## Key Business Functions

"""
    for feature in config['features']:
        content += f"### {feature}\n\n"
        content += f"Business logic for {feature.lower()}.\n\n"

    content += """
## Business Rules

1. Data validation requirements
2. Authorization and access control
3. Business process compliance
4. Error handling and recovery

## Success Metrics

- Performance KPIs
- User satisfaction
- System reliability
- Compliance adherence

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
"""
    return content

def create_api_doc(module_name, config):
    """Generate API.md"""
    port_info = f"`http://localhost:{config['port']}`" if config['port'] else "N/A (library module)"

    content = f"""# {module_name.replace('-', ' ').replace('_', ' ').title()} - API Reference

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Base URL

{port_info}

## Authentication

Bearer token (JWT) required for all endpoints.

```
Authorization: Bearer <token>
```

## Endpoints

### Health Check

```
GET /health
```

Response:
```json
{{
  "status": "healthy",
  "version": "1.0.0"
}}
```

## Error Responses

Standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
"""
    return content

def create_integration_doc(module_name, config):
    """Generate INTEGRATION.md"""
    content = f"""# {module_name.replace('-', ' ').replace('_', ' ').title()} - Integration Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Integration Overview

Integration patterns and dependencies for {module_name}.

## Internal Dependencies

### Database Integration

```python
from shared.database import get_db

db = await get_db()
```

### EventBus Integration

```python
from shared.eventbus import get_eventbus_client

eventbus = get_eventbus_client()
await eventbus.publish('event.type', {{'data': 'value'}})
```

## External Integrations

- Supabase PostgreSQL
- Redis EventBus
- Prometheus metrics

## Event Patterns

### Published Events

List of events published by this module.

### Subscribed Events

List of events this module subscribes to.

## Integration Testing

```python
import pytest

@pytest.mark.asyncio
async def test_integration():
    # Test integration
    pass
```

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
"""
    return content

def create_deployment_doc(module_name, config):
    """Generate DEPLOYMENT.md"""
    content = f"""# {module_name.replace('-', ' ').replace('_', ' ').title()} - Deployment Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7.0+
- Docker 24+ (optional)

## Environment Variables

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Messaging
REDIS_URL=redis://localhost:6379

# Service Configuration
LOG_LEVEL=INFO
"""

    if config['port']:
        content += f"PORT={config['port']}\n"

    content += """```

## Docker Deployment

```bash
# Build
docker build -t {module_name}:latest .

# Run
docker run -p {port}:{port} --env-file .env {module_name}:latest
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {module_name}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {module_name}
  template:
    metadata:
      labels:
        app: {module_name}
    spec:
      containers:
      - name: {module_name}
        image: {module_name}:latest
        ports:
        - containerPort: {port}
```

## Health Checks

- Liveness: `GET /health`
- Readiness: `GET /health`

## Monitoring

- Prometheus metrics: `GET /metrics`
- Grafana dashboards available

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
""".format(module_name=module_name, port=config['port'] or 8000)

    return content

def main():
    """Generate documentation for all modules"""
    base_path = Path(__file__).parent

    for module_name, config in MODULES.items():
        print(f"\n=== Generating docs for {module_name} ===")
        module_path = base_path / module_name
        docs_path = module_path / 'docs'
        docs_path.mkdir(exist_ok=True)

        # Generate each document type
        docs_to_create = {
            'ARCHITECTURE.md': create_architecture_doc,
            'BUSINESS_LOGIC.md': create_business_logic_doc,
            'API.md': create_api_doc,
            'INTEGRATION.md': create_integration_doc,
            'DEPLOYMENT.md': create_deployment_doc,
        }

        for doc_name, generator_func in docs_to_create.items():
            if doc_name in config.get('skip', []):
                print(f"  Skipping {doc_name} (already exists)")
                continue

            doc_path = docs_path / doc_name
            if not doc_path.exists():
                content = generator_func(module_name, config)
                doc_path.write_text(content)
                print(f"  Created {doc_name}")
            else:
                print(f"  Skipped {doc_name} (exists)")

    print("\n✅ Documentation generation complete!")

if __name__ == '__main__':
    main()
