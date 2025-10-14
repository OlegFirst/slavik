# BIA Service - Business Impact Analysis

**Type**: Platform Service
**Port**: 8012
**Status**: Active
**Version**: 1.0.0
**ISO 22301 Clause**: 8.2.2 - Business Impact Analysis

## Overview

The BIA Service provides comprehensive Business Impact Analysis capabilities aligned with ISO 22301:2019 Clause 8.2.2 requirements. It enables organizations to identify critical business processes, assess their impact during disruptions, and define appropriate recovery objectives (RTO, RPO, MTPD).

This service combines traditional BIA methodology with AI-powered intelligence to suggest recovery objectives and discover process dependencies automatically.

## Business Capabilities

The BIA Service delivers the following business value:

- **Critical Process Identification**: Automated criticality scoring with WHO tier classification for healthcare organizations
- **Recovery Objectives Definition**: Define and validate RTO (Recovery Time Objective), RPO (Recovery Point Objective), and MTPD (Maximum Tolerable Period of Disruption)
- **Financial Impact Assessment**: Multi-period financial impact analysis from 1 hour to 1 month
- **Dependency Mapping**: Comprehensive upstream/downstream process, technology, and supplier dependencies
- **AI-Powered Analysis**: Intelligent RTO/RPO suggestions based on criticality, industry benchmarks, and historical data
- **Supply Chain BCM**: Critical supplier management and supply chain risk assessment
- **Multi-Industry Support**: Healthcare (WHO tiers), Financial Services, Manufacturing, IT, Retail, and more

## API Endpoints

The service exposes 16 RESTful API endpoints across multiple categories:

### Process Management
- POST /api/bia/processes - Create BIA process
- GET /api/bia/processes - List processes with filtering
- GET /api/bia/processes/{id} - Get process details
- PUT /api/bia/processes/{id} - Update process
- DELETE /api/bia/processes/{id} - Delete process
- POST /api/bia/processes/{id}/complete - Mark as completed

### AI-Powered Analysis
- POST /api/bia/processes/{id}/suggest-rto - AI RTO/RPO/MTPD suggestions
- POST /api/bia/processes/{id}/discover-dependencies - AI dependency discovery

### Bulk Operations
- POST /api/bia/processes/bulk - Bulk create processes
- PATCH /api/bia/processes/bulk - Bulk update processes
- DELETE /api/bia/processes/bulk - Bulk delete processes
- POST /api/bia/processes/bulk/validate - Validate before import

### Reporting
- GET /api/bia/reports/summary - Executive summary report
- GET /api/bia/reports/critical-processes - Critical processes report
- GET /api/bia/reports/dependencies - Dependencies mapping report

### Health & Monitoring
- GET /health - Health check endpoint
- GET /metrics/cache - Cache performance metrics
- GET /api/compliance/check - ISO 22301 compliance status

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
cd platform-services/bia-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy from .env.example)
cp .env.example .env

# Run database migrations (if using PostgreSQL)
alembic upgrade head

# Start the service
python main.py
```

The service will start on port 8012 by default.

### Docker Deployment

```bash
# Build Docker image
docker build -t bia-service:latest .

# Run with Docker Compose
docker-compose up bia-service
```

## Configuration

### Environment Variables

```bash
# Service Configuration
BIA_SERVICE_PORT=8012
BIA_SERVICE_VERSION=1.0.0
BIA_LOG_LEVEL=INFO

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
FEATURE_EVENTBUS=true

# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AI_ENABLED=true

# Feature Flags
WHO_TIER_ENABLED=true
SUPPLY_CHAIN_ENABLED=true

# CORS Configuration
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Event Subscriptions

The BIA Service subscribes to the following EventBus topics:

- `governance.organization.created` - Auto-create BIA template for new organizations
- `risk.critical_risk_identified` - Link critical risks to BIA processes

## Dependencies

### Internal Dependencies

- **Database**: PostgreSQL (tables: bia_processes, bia_dependencies, bia_impacts)
- **Cache**: Redis (for high-performance caching)
- **Event Bus**: RabbitMQ via infrastructure/eventbus service
- **Shared Libraries**:
  - shared/database - Database connection management
  - shared/auth - JWT authentication and RBAC
  - shared/eventbus - Event publishing/subscribing
  - shared/cache - Redis caching layer

### External Dependencies

- **AI Orchestration Service** (port 8002) - For AI-powered RTO suggestions and dependency discovery
- **API Gateway** (port 8000) - For external API access
- **Workflow Intelligence** - For audit logging and compliance checking

### Python Package Dependencies

Key dependencies include:
- FastAPI 0.104.1
- SQLAlchemy 2.0+ (async support)
- Pydantic 2.5+
- asyncpg (PostgreSQL driver)
- redis-py (Redis client)
- aio-pika (RabbitMQ async client)

See `requirements.txt` for complete list.

## Standards Compliance

### ISO 22301:2019 - Clause 8.2.2 Requirements

This service implements all mandatory requirements from ISO 22301:2019 Clause 8.2.2 (Business Impact Analysis):

**Criticality Assessment** (8.2.2.a)
- Five-level criticality classification (CRITICAL, HIGH, MEDIUM, LOW, NEGLIGIBLE)
- Automated criticality scoring based on multiple factors
- WHO Essential Services tier classification for healthcare (Tier 1-4)

**Recovery Objectives** (8.2.2.b)
- RTO (Recovery Time Objective) in hours
- RPO (Recovery Point Objective) in hours
- MTPD (Maximum Tolerable Period of Disruption) in hours
- Peak period analysis with different RTOs

**Resource Requirements** (8.2.2.c)
- Personnel requirements (minimum staff levels)
- Facilities and equipment
- Technology and systems
- Information and data
- Materials and supplies

**Dependency Identification** (8.2.2.d)
- Upstream/downstream process dependencies
- Technology dependencies with criticality rating
- Supplier dependencies
- External service dependencies

**Impact Analysis** (8.2.2.e)
- Financial impact (multi-period: 1h, 4h, 8h, 24h, 1 week, 1 month)
- Operational impact
- Reputational impact (5 levels)
- Regulatory impact (5 levels)
- Patient safety impact (healthcare-specific, 5 levels)

**Additional Features**
- Alternative procedures documentation
- Legal/regulatory compliance tracking
- Recovery strategies per process
- Integration with risk assessments

## Development

### Project Structure

```
bia-service/
├── api/                    # API routes (thin layer)
├── database/              # Database connection and models
├── models/                # Domain models and enums
├── repositories/          # Data access layer
├── services/              # Business logic
├── utils/                 # Utility functions
├── docs/                  # Documentation
├── tests/                 # Unit and integration tests
├── config.py              # Service configuration
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_bia_service.py
```

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-09
**Maintainer**: AI Platform Team
**Documentation**: [Complete Documentation Index](docs/README.md)
