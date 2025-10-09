# Workflow Intelligence Engine

**Type**: Core Module
**Domain**: Intelligent-Core
**Status**: Active
**Version**: 1.0.0
**Port**: 8037

## Overview

The Workflow Intelligence Engine is the cognitive backbone of the AI-Platform-ISO system, providing intelligent workflow orchestration, case-based reasoning, and machine learning-powered recommendations for Business Continuity Management workflows. It combines Temporal Cloud for durable workflow execution with advanced pattern learning and cross-module knowledge transfer.

The module serves as the central intelligence layer for all BCM workflows, enabling organizations to benefit from collective wisdom while maintaining privacy and ensuring compliance with ISO 22301 standards.

## Architecture

### Core Components

1. **Temporal Workflow Engine** - Durable workflow orchestration using Temporal Cloud
2. **Case Library** - Searchable repository of anonymized workflow executions
3. **State Machine** - Flexible workflow state management with governance controls
4. **Cross-Module Learning** - ML-powered pattern transfer between BCM modules
5. **Benchmarking System** - Performance comparison against similar organizations

### Key Features

- **Durable Workflows**: Resilient execution with automatic recovery
- **Case-Based Reasoning**: Learn from similar organizations' successful approaches
- **Pattern Recognition**: Identify and recommend proven strategies
- **Progress Tracking**: Real-time workflow state and progress monitoring
- **Quality Assurance**: Governance checkpoints and creative zones
- **ML Recommendations**: Data-driven guidance based on historical outcomes

## Technical Architecture

```
Workflow Intelligence Engine (Port 8037)
├── Temporal Cloud Integration
│   ├── Workflow Definitions (YAML-based)
│   ├── Activity Execution
│   ├── State Persistence
│   └── Event Handling
│
├── Case Library
│   ├── PostgreSQL Storage
│   ├── Vector Similarity Search (Qdrant)
│   ├── Anonymization Layer
│   └── Benchmark Calculation
│
├── Governance System
│   ├── Rule Engine
│   ├── Checkpoint Validators
│   ├── Creative Zones
│   └── Compliance Tracking
│
└── Machine Learning
    ├── Cross-Module Learning
    ├── Success Pattern Extraction
    ├── Benchmark Analytics
    └── Trend Detection
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Temporal Cloud account

### Setup

```bash
# Navigate to module directory
cd intelligent-core/workflow_intelligence

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Temporal Cloud credentials and database URLs
```

### Environment Variables

```bash
# Temporal Cloud
TEMPORAL_API_KEY=your_api_key_here
TEMPORAL_NAMESPACE=your_namespace
TEMPORAL_ADDRESS=region.gcp.api.temporal.io:7233

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm_platform
REDIS_URL=redis://localhost:6379

# EventBus
EVENTBUS_URL=http://localhost:8001

# AI Foundation
AI_FOUNDATION_URL=http://localhost:8025
```

## Usage

### Starting the Service

```bash
# Activate virtual environment
source venv/bin/activate

# Run service
python main.py
```

The service will start on `http://localhost:8037`

### API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8037/docs
- **ReDoc**: http://localhost:8037/redoc

### Running Temporal Workflows

```bash
# Start Temporal worker
cd temporal_workflows
python worker.py

# Execute workflow
python run_workflow.py --workflow-type bia --org-id <org_id>
```

## API Reference

### Core Endpoints

See [docs/API.md](docs/API.md) for complete API documentation.

**Case Library**
```
POST   /api/v1/cases                    # Add case
GET    /api/v1/cases/search             # Search cases
GET    /api/v1/cases/{case_id}          # Get case details
GET    /api/v1/cases/similar            # Find similar cases
```

**Workflow Management**
```
POST   /api/v1/workflows                # Create workflow
GET    /api/v1/workflows/{workflow_id}  # Get workflow state
POST   /api/v1/workflows/{id}/transition # Execute transition
```

**Benchmarking**
```
GET    /api/v1/benchmarks               # Get benchmarks
POST   /api/v1/benchmarks/compare       # Compare performance
```

**Cross-Module Learning**
```
GET    /api/v1/ml/patterns              # Get learned patterns
POST   /api/v1/ml/insights              # Get cross-module insights
```

## Dependencies

### Internal Dependencies

- `shared.event_bus` - Event publishing and subscription
- `shared.database` - Database connection management
- `ai-foundation` - LLM routing and RAG capabilities

### External Dependencies

- **Temporal SDK** (1.18.1+) - Workflow orchestration
- **FastAPI** (0.100.0+) - API framework
- **SQLAlchemy** (2.0+) - Database ORM
- **Qdrant Client** - Vector similarity search
- **Pydantic** (2.0+) - Data validation

## Standards Compliance

### ISO 22301:2019 Integration

- **Clause 8.2**: Risk assessment workflow integration
- **Clause 8.3**: Business continuity strategies via workflow patterns
- **Clause 9.1**: Monitoring and measurement through case analytics
- **Clause 10.2**: Continuous improvement via pattern learning

### Data Privacy

- **Anonymization**: All case data anonymized before storage
- **k-anonymity**: Minimum 5 similar cases required for benchmarking
- **GDPR Compliance**: No personally identifiable information stored

## Development

### Project Structure

```
workflow_intelligence/
├── api/                    # API endpoints
├── case_library/           # Case storage and retrieval
├── core/                   # Core workflow engine
│   ├── state_machine.py   # State management
│   └── workflow_engine.py # Workflow execution
├── governance/             # Rules and checkpoints
├── integration/            # External system integration
├── ml/                     # Machine learning components
│   └── cross_module_learning.py
├── monitoring/             # Health checks and metrics
├── storage/                # Database models
├── temporal_workflows/     # Temporal workflow definitions
├── docs/                   # Technical documentation
├── tests/                  # Test suite
├── main.py                # Service entry point
└── requirements.txt       # Python dependencies
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test module
pytest tests/test_case_library.py
```

### Code Quality

```bash
# Format code
black .

# Lint
pylint **/*.py

# Type checking
mypy .
```

## Monitoring

### Health Checks

```bash
# Service health
curl http://localhost:8037/health

# Detailed status
curl http://localhost:8037/health/detailed
```

### Metrics

Prometheus metrics exposed at `/metrics`:

- `workflow_intelligence_cases_total` - Total cases in library
- `workflow_intelligence_workflows_active` - Active workflows
- `workflow_intelligence_ml_predictions_total` - ML predictions made
- `workflow_intelligence_benchmark_requests_total` - Benchmark requests

### Logging

Structured logging to stdout:
```
2025-10-09 12:00:00 - workflow_intelligence - INFO - Service started on port 8037
2025-10-09 12:01:15 - workflow_intelligence - INFO - Case added: case_id=abc123
```

## Performance

### Benchmarks

- **Case Search**: <200ms (P95)
- **Similarity Matching**: <1s (P95)
- **Workflow Transition**: <100ms (P95)
- **ML Inference**: <500ms (P95)

### Scalability

- **Horizontal Scaling**: Supported via stateless API design
- **Database**: Connection pooling (10-20 connections)
- **Cache**: Redis for frequently accessed data
- **Temporal**: Cloud-managed workflow scalability

## Troubleshooting

### Common Issues

**Temporal Connection Failed**
```bash
# Verify credentials
echo $TEMPORAL_API_KEY

# Test connection
python test_temporal_connection.py
```

**Database Migration Issues**
```bash
# Check migration status
psql $DATABASE_URL -c "SELECT * FROM alembic_version;"

# Apply migrations manually
psql $DATABASE_URL -f migrations/001_workflow_intelligence.sql
```

**Case Search Returns No Results**
```bash
# Verify data exists
psql $DATABASE_URL -c "SELECT COUNT(*) FROM workflow_cases;"

# Check vector index
# Ensure Qdrant is running and indexed
```

## Documentation

### Technical Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System architecture and design
- [Technical Specification](docs/TECHNICAL_SPECIFICATION.md) - Detailed specifications
- [API Reference](docs/API.md) - Complete API documentation
- [Integration Guide](docs/INTEGRATION.md) - Integration with other services
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions

### Additional Resources

- [Temporal Cloud Setup](TEMPORAL_SETUP_COMPLETE.md) - Temporal configuration
- [Migration Guide](docs/IMPORT_MIGRATION_GUIDE.md) - SQLAlchemy migration notes
- [Instrumentation Guide](docs/INSTRUMENTATION_COMPLETE_GUIDE.md) - Observability setup

## Contributing

### Development Workflow

1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure all tests pass (`pytest`)
4. Submit pull request with description
5. Code review and approval
6. Merge to `main`

### Coding Standards

- **Style**: PEP 8 compliance
- **Documentation**: Docstrings for all public functions
- **Testing**: Minimum 80% code coverage
- **Type Hints**: Required for all function signatures

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-09
**Maintainer**: AI Platform Team
**Contact**: Technical support via internal channels

---

## Quick Links

- **Temporal Cloud Dashboard**: https://cloud.temporal.io
- **Service Health**: http://localhost:8037/health
- **API Docs**: http://localhost:8037/docs
- **Metrics**: http://localhost:8037/metrics
