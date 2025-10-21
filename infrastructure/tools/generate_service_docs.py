#!/usr/bin/env python3
"""
Professional service documentation generator
ISO/IEC/IEEE 26514:2022 compliant
"""

import json
import sys
from pathlib import Path
from datetime import datetime

SERVICE_DESCRIPTIONS = {
    "validation-service": "The Validation Service provides comprehensive validation capabilities for business continuity processes, including KPI monitoring, alert management, and continuous process improvement. It implements automated validation workflows with real-time metrics collection and threshold-based alerting.",

    "documents-service": "The Documents Service manages the complete lifecycle of business continuity documentation, including policy documents, procedures, plans, and templates. It implements version control, approval workflows, access control, and document generation capabilities.",

    "governance-service": "The Governance Service implements organizational governance frameworks for business continuity management, including stakeholder management, decision-making processes, and organizational context analysis. It provides tools for governance structure definition and accountability tracking.",

    "response-service": "The Response Service manages the complete incident and emergency response lifecycle from detection through resolution and post-incident review. It implements response plan activation, team coordination, escalation workflows, and lessons learned capture.",

    "bia-service": "The BIA Service provides Business Impact Analysis capabilities including criticality assessment, dependency mapping, and recovery time objective determination. It implements comprehensive analysis workflows with AI-powered recommendations.",

    "risk-service": "The Risk Service implements comprehensive risk management including risk identification, assessment, treatment planning, and monitoring. It provides risk matrices, heat maps, and integration with mitigation workflows.",

    "compliance-service": "The Compliance Service manages regulatory compliance and standards adherence including gap analysis, audit management, and certification tracking. It implements compliance monitoring with automated evidence collection.",

    "bcm-coordination-service": "The BCM Coordination Service provides centralized coordination for all business continuity management activities. It orchestrates interactions between BIA, risk, compliance, and response services, ensuring consistent BCM program execution.",

    "community-service": "The Community Service enables knowledge sharing, collaboration, and best practice exchange among BCM practitioners. It implements community features including forums, knowledge bases, and peer review capabilities.",

    "learning-service": "The Learning Service provides training, awareness, and competency development for business continuity management. It implements learning paths, assessments, certification tracking, and skills gap analysis.",

    "planning_service": "The Planning Service manages business continuity planning processes including plan development, maintenance, and testing. It implements structured planning workflows with template management and version control.",

    "plans_service": "The Plans Service provides centralized repository and management for all business continuity plans. It implements plan storage, retrieval, distribution, and activation workflows with role-based access control."
}

def generate_service_readme(service_name: str, section: str) -> str:
    """Generate professional service README"""

    scan_file = Path(f"/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/devops-agent/reports-generated/modules/{service_name}_scan.json")

    if not scan_file.exists():
        print(f"️  Scan file not found: {scan_file}")
        print(f"   Using minimal template for {service_name}")
        metrics = {"loc": 0, "python_files": 0, "classes": 0, "functions": 0, "endpoints": 0, "dependencies": 0}
    else:
        with open(scan_file) as f:
            data = json.load(f)
        metrics = data.get('metrics', {})

    title = service_name.replace('-', ' ').replace('_', ' ').title()
    description = SERVICE_DESCRIPTIONS.get(service_name, f"The {title} provides core business continuity management functionality.")

    readme = f"""# {title}

**Type**: Platform Service
**Domain**: Business Continuity Management
**Status**: Active
**Version**: 2.0.0

## Overview

{description}

## Metrics

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | {metrics.get('loc', 0):,} |
| **Python Files** | {metrics.get('python_files', 0)} |
| **Classes** | {metrics.get('classes', 0)} |
| **Functions** | {metrics.get('functions', 0)} |
| **API Endpoints** | {metrics.get('endpoints', 0)} |
| **Dependencies** | {metrics.get('dependencies', 0)} |

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
cd platform-services/{service_name}

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
pytest tests/ --cov={service_name.replace('-', '_')} --cov-report=html
```

## Integration

### Event Bus Integration

The service publishes and subscribes to platform events:

```python
from infrastructure.eventbus import EventBus

# Subscribe to events
await event_bus.subscribe(
    pattern="{service_name.split('-')[0]}.*",
    handler=handle_event
)
```

### Workflow Intelligence Integration

Integrates with workflow intelligence for process orchestration:

```python
from intelligent_core.ai_foundation import WorkflowIntelligenceClient

client = WorkflowIntelligenceClient()
await client.start_workflow(type="{service_name.split('-')[0]}")
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

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Maintainer**: AI Platform Team
"""

    return readme

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate-service-docs.py <service_name> <section>")
        sys.exit(1)

    service_name = sys.argv[1]
    section = sys.argv[2]

    readme_content = generate_service_readme(service_name, section)

    output_path = Path(f"/Users/MD/AI-Platform-ISO/{section}/{service_name}/README.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(readme_content)

    print(f" Generated: {output_path}")
    print(f"   Size: {len(readme_content)} characters")

if __name__ == "__main__":
    main()
