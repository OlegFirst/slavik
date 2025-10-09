#!/usr/bin/env python3
"""
Service Documentation Generator
Generates complete documentation packages for all platform-services
"""

import os
from pathlib import Path
from datetime import datetime

# Service configurations
SERVICES = {
    "compliance-service": {
        "port": 8014,
        "version": "1.0.0",
        "iso_clauses": ["9.2", "10.1", "10.2"],
        "description": "ISO 22301:2019 Compliance Management",
        "capabilities": [
            "Compliance assessment engine with production-tested scoring",
            "Evidence management with workflow tracking",
            "Gap analysis and remediation planning",
            "Internal audit management (ISO 9.2)",
            "Nonconformity management with 3 RCA methods (ISO 10.1)",
            "Continual improvement tracking (ISO 10.2)",
            "AI-powered compliance scanning"
        ],
        "endpoints": 50,
        "routers": 14
    },
    "risk-service": {
        "port": 8040,
        "version": "1.0.0",
        "iso_clauses": ["8.2.3"],
        "description": "ISO 22301:2019 Risk Assessment",
        "capabilities": [
            "5x5 Risk Matrix (Likelihood × Impact)",
            "FAIR Quantitative Analysis",
            "Monte Carlo Simulation",
            "Risk Treatment Plans",
            "Risk Heat Maps and Reports",
            "Threat and vulnerability assessment"
        ],
        "endpoints": 20,
        "routers": 5
    },
    "bcm-coordination-service": {
        "port": 8070,
        "version": "1.0.0",
        "iso_clauses": ["All"],
        "description": "BCM Services Coordination",
        "capabilities": [
            "Coordinates 10 specialized BCM analyzers",
            "Compliance analyzer (ISO 22301 gap analysis)",
            "Risk analyzer (FAIR-based)",
            "Impact analyzer (BIA)",
            "Auto-routing based on analysis type",
            "Batch analysis pipelines"
        ],
        "endpoints": 15,
        "routers": 3
    },
    "response-service": {
        "port": 8050,
        "version": "1.0.0",
        "iso_clauses": ["8.4"],
        "description": "ISO 22301:2019 Incident Response",
        "capabilities": [
            "Incident declaration and tracking",
            "Emergency response coordination",
            "Crisis management workflows",
            "Severity classification",
            "Escalation management",
            "Real-time incident dashboards"
        ],
        "endpoints": 25,
        "routers": 6
    },
    "governance-service": {
        "port": 8030,
        "version": "1.0.0",
        "iso_clauses": ["4", "5", "7"],
        "description": "ISO 22301:2019 Governance and Leadership",
        "capabilities": [
            "Organization context management",
            "Leadership and commitment tracking",
            "Policy management",
            "Roles and responsibilities",
            "Management commitment",
            "Resource allocation"
        ],
        "endpoints": 20,
        "routers": 5
    },
    "planning-service": {
        "port": 8035,
        "version": "1.0.0",
        "iso_clauses": ["8.3"],
        "description": "ISO 22301:2019 BCM Planning",
        "capabilities": [
            "Business continuity strategy development",
            "Recovery strategy planning",
            "Resource planning",
            "Continuity solutions design",
            "Plan integration and coordination"
        ],
        "endpoints": 18,
        "routers": 4
    },
    "plans-service": {
        "port": 8045,
        "version": "1.0.0",
        "iso_clauses": ["8.4.2"],
        "description": "ISO 22301:2019 BCM Plans Management",
        "capabilities": [
            "Business continuity plans management",
            "Disaster recovery plans",
            "Plan versioning and approval",
            "Plan testing and maintenance",
            "Plan distribution"
        ],
        "endpoints": 22,
        "routers": 5
    },
    "documents-service": {
        "port": 8060,
        "version": "1.0.0",
        "iso_clauses": ["7.5"],
        "description": "ISO 22301:2019 Documented Information",
        "capabilities": [
            "Document lifecycle management",
            "Version control",
            "Access control and distribution",
            "Document approval workflows",
            "Records management",
            "Template management"
        ],
        "endpoints": 25,
        "routers": 6
    },
    "learning-service": {
        "port": 8055,
        "version": "1.0.0",
        "iso_clauses": ["7.2", "10.2"],
        "description": "ISO 22301:2019 Competence and Learning",
        "capabilities": [
            "Training program management",
            "Competence tracking",
            "Awareness programs",
            "Lessons learned capture",
            "Knowledge management",
            "Training effectiveness measurement"
        ],
        "endpoints": 20,
        "routers": 5
    },
    "validation-service": {
        "port": 8065,
        "version": "1.0.0",
        "iso_clauses": ["8.5"],
        "description": "ISO 22301:2019 Exercising and Testing",
        "capabilities": [
            "Exercise planning and scheduling",
            "Test scenario management",
            "Exercise execution tracking",
            "Results analysis",
            "Improvement recommendations",
            "Exercise types: desktop, simulation, full-scale"
        ],
        "endpoints": 22,
        "routers": 5
    },
    "community-service": {
        "port": 8075,
        "version": "1.0.0",
        "iso_clauses": ["All"],
        "description": "BCM Community and Knowledge Sharing",
        "capabilities": [
            "Community forums and discussions",
            "Best practice sharing",
            "Peer collaboration",
            "Expert network",
            "Case studies repository",
            "Industry benchmarking"
        ],
        "endpoints": 18,
        "routers": 4
    }
}

def generate_readme(service_name, config):
    """Generate README.md for a service"""
    return f"""# {service_name.replace('-', ' ').title()}

**Type**: Platform Service
**Port**: {config['port']}
**Status**: Active
**Version**: {config['version']}
**ISO 22301 Clause**: {', '.join(config['iso_clauses'])}

## Overview

{config['description']}

[Add detailed description here]

## Business Capabilities

{''.join(f'- {cap}\\n' for cap in config['capabilities'])}

## API Endpoints

The service exposes {config['endpoints']}+ RESTful API endpoints across {config['routers']} categories.

For detailed API documentation, see [docs/API.md](docs/API.md).

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ or SQLite (for development)
- Redis 7.0+ (for caching)
- RabbitMQ 3.12+ (for event bus, optional)

### Local Development Setup

```bash
# Navigate to service directory
cd platform-services/{service_name}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Start the service
python main.py
```

## Configuration

### Environment Variables

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete configuration guide.

## Dependencies

### Internal Dependencies
- **Database**: PostgreSQL
- **Cache**: Redis
- **Event Bus**: RabbitMQ
- **Shared Libraries**: auth, database, eventbus, cache

### External Dependencies
- **AI Orchestration Service** (port 8002)
- **API Gateway** (port 8000)
- **Workflow Intelligence**

## Standards Compliance

### ISO 22301:2019 - Clause {', '.join(config['iso_clauses'])}

See [docs/BUSINESS_LOGIC.md](docs/BUSINESS_LOGIC.md) for detailed compliance mapping.

## Development

See [docs/TECHNICAL_SPECIFICATION.md](docs/TECHNICAL_SPECIFICATION.md) for architecture details.

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Maintainer**: AI Platform Team
**Documentation**: [Complete Documentation Index](docs/README.md)
"""

def generate_technical_spec(service_name, config):
    """Generate TECHNICAL_SPECIFICATION.md"""
    return f"""# {service_name.replace('-', ' ').title()} - Technical Specification

**Version**: {config['version']}
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Approved
**ISO 22301 Clause**: {', '.join(config['iso_clauses'])}

## 1. Introduction

### 1.1 Purpose

This document specifies the technical architecture and implementation details of the {service_name.replace('-', ' ').title()}.

### 1.2 Scope

The service is responsible for:
{''.join(f'- {cap}\n' for cap in config['capabilities'])}

## 2. Architecture

### 2.1 System Context

```
API Gateway (8000)
       │
       ├─────────────────────────┐
       │                         │
{service_name.replace('-', ' ').title()}        Other Services
(Port {config['port']})
       │
       ├──── Database (PostgreSQL)
       ├──── Cache (Redis)
       ├──── EventBus (RabbitMQ)
       └──── AI Orchestration (8002)
```

### 2.2 Component Diagram

```
{service_name}/
├── API Layer (FastAPI)
│   ├── {config['routers']} routers
│   └── Authentication & Authorization
├── Service Layer (Business Logic)
│   └── Core services
├── Repository Layer (Data Access)
│   └── Database operations
└── Data Layer
    ├── Database models (SQLAlchemy)
    └── Domain models (Pydantic)
```

## 3. Data Models

See code in `models/` directory.

## 4. API Specifications

See [API.md](API.md) for complete API documentation.

## 5. Integration Points

See [INTEGRATION.md](INTEGRATION.md) for integration patterns.

## 6. Performance Requirements

- Response time: < 200ms for GET requests
- Throughput: 100+ requests/second
- Horizontal scalability via multiple instances

## 7. Security

- JWT Bearer token authentication
- RBAC authorization
- Tenant isolation
- Audit logging

## 8. Testing Strategy

- Unit testing: 80% minimum coverage
- Integration testing
- Performance testing
- Security testing

---

**Document Version**: {config['version']}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Next Review**: {datetime.now().strftime('%Y-%m-%d')}
"""

def generate_api_doc(service_name, config):
    """Generate API.md"""
    return f"""# {service_name.replace('-', ' ').title()} - API Documentation

**Service**: {service_name.replace('-', ' ').title()}
**Base URL**: `http://localhost:{config['port']}`
**API Prefix**: `/api`
**Version**: {config['version']}

## Authentication

All API endpoints require JWT Bearer token authentication.

### Request Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Development Mode

For development/testing, use the `X-Dev-User` header:

```http
X-Dev-User: {{"user_id": "user_123", "tenant_id": "tenant_123", "permissions": ["VIEW", "EDIT"]}}
```

## Error Handling

### Standard Error Response

```json
{{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status_code": 400
}}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request - validation error |
| 401 | Unauthorized - missing or invalid JWT |
| 403 | Forbidden - tenant mismatch or insufficient permissions |
| 404 | Resource not found |
| 422 | Business rule violation |
| 500 | Internal server error |

## API Endpoints

### Health Check

**Endpoint:** `GET /health`

**Response:** `200 OK`

```json
{{
  "status": "healthy",
  "service": "{service_name}",
  "version": "{config['version']}",
  "port": {config['port']}
}}
```

### Main Endpoints

[Add specific endpoints based on service implementation]

See `api/` directory for complete endpoint implementations.

---

**API Version**: {config['version']}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
"""

def generate_business_logic(service_name, config):
    """Generate BUSINESS_LOGIC.md"""
    return f"""# {service_name.replace('-', ' ').title()} - Business Logic

**Service**: {service_name.replace('-', ' ').title()}
**Version**: {config['version']}
**ISO 22301 Clause**: {', '.join(config['iso_clauses'])}

## 1. Business Rules

### 1.1 Core Business Rules

[Add specific business rules]

### 1.2 Validation Rules

[Add validation rules]

## 2. Workflows

### 2.1 Main Workflows

[Add workflow descriptions]

### 2.2 State Machines

[Add state machine diagrams and transitions]

## 3. Business Logic Components

### 3.1 Services

[Describe business logic services]

### 3.2 Calculations

[Describe calculation logic]

## 4. ISO 22301 Compliance Mapping

### Clause {', '.join(config['iso_clauses'])} Requirements

[Add detailed compliance mapping]

---

**Document Version**: {config['version']}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
"""

def generate_integration(service_name, config):
    """Generate INTEGRATION.md"""
    return f"""# {service_name.replace('-', ' ').title()} - Integration Guide

**Service**: {service_name.replace('-', ' ').title()}
**Version**: {config['version']}
**Port**: {config['port']}

## 1. Internal Service Integration

### 1.1 Database Integration

**Type**: PostgreSQL 14+
**Connection**: Async via SQLAlchemy 2.0+

### 1.2 Cache Integration

**Type**: Redis 7.0+
**Purpose**: Performance optimization

### 1.3 Event Bus Integration

**Type**: RabbitMQ 3.12+
**Purpose**: Asynchronous event-driven communication

#### Events Published

[List events published by this service]

#### Events Subscribed

[List events this service subscribes to]

### 1.4 AI Orchestration Integration

**Service**: AI Orchestration Service (Port 8002)
**Purpose**: AI-powered analysis and recommendations

## 2. External Service Integration

### 2.1 API Gateway

**Gateway Port**: 8000
**Purpose**: External API access and authentication

### 2.2 Workflow Intelligence

**Purpose**: Real-time guidance, audit logging, compliance checking

## 3. Integration Patterns

### 3.1 Synchronous Communication

REST API calls for immediate responses.

### 3.2 Asynchronous Communication

EventBus for fire-and-forget operations.

### 3.3 Caching Strategy

Redis for frequently accessed data.

## 4. Error Handling

### 4.1 Retry Logic

Exponential backoff for external service calls.

### 4.2 Circuit Breaker

Fail fast when services are unavailable.

---

**Document Version**: {config['version']}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
"""

def generate_deployment(service_name, config):
    """Generate DEPLOYMENT.md"""
    return f"""# {service_name.replace('-', ' ').title()} - Deployment Guide

**Service**: {service_name.replace('-', ' ').title()}
**Version**: {config['version']}
**Port**: {config['port']}

## 1. Environment Configuration

### 1.1 Environment Variables

```bash
# Service Configuration
SERVICE_PORT={config['port']}
SERVICE_VERSION={config['version']}
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bcm_platform
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=false

# Authentication
JWT_SECRET=your-secret-key-change-in-production

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# EventBus Configuration
EVENTBUS_URL=amqp://guest:guest@localhost:5672
EVENTS_ENABLED=true

# AI Services
AI_ENABLED=true
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# CORS Configuration
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 2. Local Development

```bash
# Clone repository
git clone <repository-url>

# Navigate to service
cd platform-services/{service_name}

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start service
python main.py
```

## 3. Docker Deployment

### 3.1 Build Image

```bash
docker build -t {service_name}:latest .
```

### 3.2 Run Container

```bash
docker run -d \\
  --name {service_name} \\
  -p {config['port']}:{config['port']} \\
  -e DATABASE_URL=postgresql://... \\
  -e JWT_SECRET=... \\
  {service_name}:latest
```

## 4. Docker Compose

```yaml
version: '3.8'
services:
  {service_name}:
    build: .
    ports:
      - "{config['port']}:{config['port']}"
    environment:
      - DATABASE_URL=postgresql://...
      - JWT_SECRET=...
    depends_on:
      - postgres
      - redis
```

## 5. Production Deployment

### 5.1 Prerequisites
- Kubernetes cluster or Docker Swarm
- Load balancer
- Monitoring (Prometheus, Grafana)

### 5.2 Scaling
- Horizontal scaling: Multiple service instances
- Database connection pooling
- Redis caching

### 5.3 Health Checks
- Endpoint: GET /health
- Frequency: Every 30 seconds

## 6. Monitoring

### 6.1 Prometheus Metrics
- Endpoint: /metrics
- Metrics: Request count, latency, errors

### 6.2 Logging
- Format: JSON structured logs
- Level: INFO (production), DEBUG (development)

---

**Document Version**: {config['version']}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
"""

def generate_docs_index(service_name, config):
    """Generate docs/README.md index"""
    return f"""# {service_name.replace('-', ' ').title()} - Documentation Index

**Service**: {service_name.replace('-', ' ').title()}
**Version**: {config['version']}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}

## Documentation Structure

1. **[TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md)** - Technical architecture and design
2. **[API.md](API.md)** - Complete API reference with examples
3. **[BUSINESS_LOGIC.md](BUSINESS_LOGIC.md)** - Business rules and workflows
4. **[INTEGRATION.md](INTEGRATION.md)** - Integration patterns and dependencies
5. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment and configuration guide

## Quick Links

- **Main README**: [../README.md](../README.md)
- **Health Endpoint**: `http://localhost:{config['port']}/health`
- **API Documentation**: `http://localhost:{config['port']}/docs`
- **Metrics**: `http://localhost:{config['port']}/metrics`

## ISO 22301 Compliance

**Covered Clauses**: {', '.join(config['iso_clauses'])}

See [BUSINESS_LOGIC.md](BUSINESS_LOGIC.md) for detailed compliance mapping.

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Maintainer**: AI Platform Team
"""

def create_service_documentation(service_name, config):
    """Create complete documentation package for a service"""
    base_path = Path(f"/Users/MD/AI-Platform-ISO/platform-services/{service_name}")
    docs_path = base_path / "docs"

    # Create docs directory
    docs_path.mkdir(parents=True, exist_ok=True)

    # Generate all documents
    docs = {
        "../README.md": generate_readme(service_name, config),
        "TECHNICAL_SPECIFICATION.md": generate_technical_spec(service_name, config),
        "API.md": generate_api_doc(service_name, config),
        "BUSINESS_LOGIC.md": generate_business_logic(service_name, config),
        "INTEGRATION.md": generate_integration(service_name, config),
        "DEPLOYMENT.md": generate_deployment(service_name, config),
        "README.md": generate_docs_index(service_name, config)
    }

    created_files = []
    for filename, content in docs.items():
        if filename.startswith("../"):
            filepath = base_path / filename[3:]
        else:
            filepath = docs_path / filename

        # Write file
        filepath.write_text(content)
        created_files.append(str(filepath))
        print(f"✅ Created: {filepath}")

    return created_files

def main():
    """Generate documentation for all services"""
    print("=" * 80)
    print("Platform Services Documentation Generator")
    print("=" * 80)
    print()

    all_created_files = []

    for service_name, config in SERVICES.items():
        print(f"\\n📝 Generating documentation for {service_name}...")
        print(f"   Port: {config['port']}, ISO Clauses: {', '.join(config['iso_clauses'])}")

        created_files = create_service_documentation(service_name, config)
        all_created_files.extend(created_files)

        print(f"   ✅ Created {len(created_files)} files for {service_name}")

    print(f"\\n{'=' * 80}")
    print(f"✅ COMPLETE: Generated {len(all_created_files)} documentation files")
    print(f"   Services documented: {len(SERVICES)}")
    print(f"   Files per service: 7 (README + 6 docs)")
    print(f"{'=' * 80}")

    return all_created_files

if __name__ == "__main__":
    main()
