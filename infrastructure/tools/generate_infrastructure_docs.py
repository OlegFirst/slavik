#!/usr/bin/env python3
"""
Professional infrastructure documentation generator
ISO/IEC/IEEE 26514:2022 compliant
"""

import json
import sys
from pathlib import Path
from datetime import datetime

INFRASTRUCTURE_DESCRIPTIONS = {
    "database": "The Database infrastructure provides PostgreSQL database management with Supabase integration, migration management, and database connection pooling. It implements RLS (Row Level Security) policies, automated migrations, and comprehensive database monitoring.",

    "eventbus": "The Event Bus infrastructure provides asynchronous event-driven communication across all platform services. It implements publish-subscribe patterns using RabbitMQ, with support for event routing, dead letter queues, and message persistence.",

    "observability": "The Observability infrastructure provides comprehensive monitoring, logging, and tracing capabilities using Prometheus, Grafana, and Loki. It implements centralized metrics collection, alerting, and distributed tracing for platform-wide visibility.",

    "tools": "The Tools infrastructure provides development and operational utilities including code analyzers, documentation generators, deployment scripts, and automation tools. It implements quality assurance, testing utilities, and DevOps automation.",

    "security": "The Security infrastructure provides authentication, authorization, API gateway, and secrets management. It implements JWT token handling, rate limiting, audit logging, and secure credential storage.",

    "AI-office-infrastructure": "The AI Office Infrastructure provides DevOps automation, project analysis agents, and intelligent monitoring capabilities. It implements automated code quality checks, deployment management, and AI-powered operational insights.",

    "gateway": "The Gateway infrastructure provides API gateway functionality with routing, load balancing, authentication middleware, and rate limiting. It implements service discovery, health checking, and centralized request/response handling.",

    "runtime": "The Runtime infrastructure provides shared runtime services including configuration management, dependency injection, and service lifecycle management. It implements initialization patterns and graceful shutdown handling.",

    "deployment": "The Deployment infrastructure provides containerization, orchestration, and CI/CD pipeline management. It implements Docker configurations, Kubernetes manifests, and automated deployment workflows.",

    "integration": "The Integration infrastructure provides external system integrations including third-party APIs, webhooks, and data synchronization. It implements adapter patterns and integration testing utilities.",

    "scripts": "The Scripts infrastructure provides operational automation scripts for deployment, maintenance, backup, and recovery operations. It implements Shell, Python, and infrastructure-as-code utilities.",

    "infrastructure": "The Infrastructure core provides shared infrastructure patterns, base classes, and common utilities used across all infrastructure components. It implements reusable infrastructure abstractions."
}

def generate_infrastructure_readme(component_name: str, section: str) -> str:
    """Generate professional infrastructure README"""

    scan_file = Path(f"/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/devops-agent/reports-generated/modules/{component_name}_scan.json")

    if not scan_file.exists():
        print(f"️  Scan file not found: {scan_file}")
        print(f"   Using minimal template for {component_name}")
        metrics = {"loc": 0, "python_files": 0, "classes": 0, "functions": 0, "endpoints": 0, "dependencies": 0}
    else:
        with open(scan_file) as f:
            data = json.load(f)
        metrics = data.get('metrics', {})

    title = component_name.replace('-', ' ').replace('_', ' ').title()
    description = INFRASTRUCTURE_DESCRIPTIONS.get(component_name, f"The {title} infrastructure component provides core platform infrastructure capabilities.")

    readme = f"""# {title}

**Type**: Infrastructure Component
**Domain**: Platform Infrastructure
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
| **Configuration Files** | {len(metrics.get('config_files', []))} |

## Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized components)
- Access to platform configuration

### Setup

```bash
cd infrastructure/{component_name}

# Install dependencies (if applicable)
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Initialize component
./setup.sh
```

## Configuration

Infrastructure components are configured through environment variables and configuration files. Refer to component-specific documentation for detailed configuration options.

## Testing

```bash
# Run infrastructure tests
pytest tests/ -v

# Run integration tests
pytest tests/integration/ -v
```

## Standards Compliance

This infrastructure component adheres to:

- **ISO/IEC 27001:2022** - Information security management
- **ISO/IEC/IEEE 26514:2022** - Software documentation
- **Infrastructure as Code best practices**
- **Twelve-Factor App methodology**

## Related Components

- [Intelligent Core](../../intelligent-core/README.md) - AI and intelligence layer
- [Platform Services](../../platform-services/README.md) - Business services
- [Infrastructure Overview](../README.md) - Infrastructure layer overview

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Maintainer**: Platform Infrastructure Team
"""

    return readme

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate-infrastructure-docs.py <component_name> <section>")
        sys.exit(1)

    component_name = sys.argv[1]
    section = sys.argv[2]

    readme_content = generate_infrastructure_readme(component_name, section)

    output_path = Path(f"/Users/MD/AI-Platform-ISO/{section}/{component_name}/README.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(readme_content)

    print(f" Generated: {output_path}")
    print(f"   Size: {len(readme_content)} characters")

if __name__ == "__main__":
    main()
