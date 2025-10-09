# BCM Platform Services

ISO 22301:2019 Business Continuity Management Platform - Complete Service Suite

## 🏗️ Architecture

This platform implements ISO 22301:2019 Business Continuity Management System with full compliance features.

### Services

| Service | Port | ISO 22301 Clause | Description |
|---------|------|------------------|-------------|
| **Planning Service** | 8011 | 8.3 | Business Continuity Strategy development, Cost-Benefit Analysis |
| **Plans Service** | 8023 | 8.4 | Business Continuity Plans and Procedures management |
| **BIA Service** | 8012 | 8.2.2 | Business Impact Analysis with recovery objectives |
| **Compliance Service** | 8014 | 9.2, 10.1, 10.2 | Internal Audit, Nonconformity & Corrective Action, Continual Improvement |

### Infrastructure

- **PostgreSQL** (Port 5432) - Primary database with multi-tenant support
- **Redis** (Port 6379) - Caching and rate limiting
- **EventBus** (Port 8001) - Event-driven communication
- **RabbitMQ** (Port 5672) - Message queue for async workflows
- **Prometheus** (Port 9090) - Metrics collection
- **Grafana** (Port 3000) - Metrics visualization

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB RAM minimum
- Ports 3000, 5432, 5672, 6379, 8001, 8011, 8012, 8014, 8023, 9090 available

### Installation

1. **Clone and navigate to directory:**
   ```bash
   cd /Users/MD/AI-Platform-ISO/platform-services
   ```

2. **Start all services:**
   ```bash
   ./start.sh
   ```

3. **Check status:**
   ```bash
   ./status.sh
   ```

4. **View logs:**
   ```bash
   ./logs.sh [service-name]  # e.g., ./logs.sh planning-service
   ```

5. **Stop services:**
   ```bash
   ./stop.sh
   ```

## 📊 Access Points

### API Services
- **Planning Service API**: http://localhost:8011/docs
- **Plans Service API**: http://localhost:8023/docs
- **BIA Service API**: http://localhost:8012/docs
- **Compliance Service API**: http://localhost:8014/docs

### Health Checks
- Planning Service: http://localhost:8011/health
- Plans Service: http://localhost:8023/health
- BIA Service: http://localhost:8012/health
- Compliance Service: http://localhost:8014/health

### Monitoring
- **Grafana**: http://localhost:3000 (admin/admin)
  - BCM Services Overview dashboard
- **Prometheus**: http://localhost:9090
  - Metrics from both services

### Databases
- **PostgreSQL**: localhost:5432
  - User: `bcm_user`
  - Password: `bcm_dev_password_2024` (development)
  - Databases: `bcm_platform`, `planning`, `plans`

- **Redis**: localhost:6379

## 🔐 Security Features

### Authentication & Authorization
- JWT RS256 token validation
- Multi-layer tenant isolation
- Dev mode with X-Dev-User header (development only)

### Security Hardening
- CORS whitelisting
- Rate limiting (100 requests/60 seconds)
- Input validation with Pydantic v2
- SQL injection prevention via ORM
- Non-root container users

### Error Handling
- Centralized exception handling
- Safe error messages (no stack traces in production)
- Structured logging

## 📈 Key Features

### Planning Service (ISO 22301 Clause 8.3)

#### Business Continuity Strategies
- Multi-strategy types (preventive, detective, corrective, recovery)
- Cost-benefit analysis with NPV and payback period
- Resource planning and allocation
- Approval workflows

#### Financial Calculations
- **NPV (Net Present Value)** with proper discounting
- **Payback Period** with time value of money
- **ROI** calculations
- Support for 1-30 year timeframes

#### Validation
- 25+ Pydantic validators
- Business logic validation
- Financial constraint checking

### Plans Service (ISO 22301 Clause 8.4)

#### Business Continuity Plans
- Complete plan lifecycle management
- Version control
- Review and approval workflows
- Testing and exercise scheduling

#### Procedures
- Dependency management
- Circular dependency prevention (DFS algorithm)
- Topological sorting for execution order
- Resource requirements tracking

#### Advanced Features
- **Procedure Dependency Validator**: Prevents circular dependencies
- **N+1 Query Prevention**: Eager loading with SQLAlchemy
- **Resource Allocation**: Track resources across plans and procedures

### BIA Service (ISO 22301 Clause 8.2.2)

#### Business Impact Analysis
- Process criticality assessment (CRITICAL, HIGH, MEDIUM, LOW)
- Recovery objectives: RTO, RPO, MTPD
- Financial impact analysis over time
- WHO Essential Services tier classification

#### ISO 22301 Compliance Fields (19 fields)
- Recovery strategies documentation
- Resource requirements (personnel, facilities, technology, information)
- Legal and regulatory requirements tracking
- Upstream/downstream process dependencies
- External service provider management

#### Business Validations
- Recovery objectives validation (RPO ≤ RTO ≤ MTPD)
- Criticality-based RTO limits enforcement
- Financial impact timeline consistency
- Essential service tier validation

### Compliance Service (ISO 22301 Clauses 9.2, 10.1, 10.2)

#### Internal Audit (Clause 9.2)
- Audit planning and scheduling
- Evidence collection and verification
- Finding assessment (major/minor)
- Gap analysis

#### Nonconformity & Corrective Action (Clause 10.1)
- Nonconformity logging and categorization
- **Root Cause Analysis** with 3 methods:
  - **5 Whys** - Sequential questioning technique
  - **Fishbone Diagram** - 6M categorization (Man, Machine, Method, Material, Measurement, Environment)
  - **Fault Tree Analysis** - Logic tree with AND/OR gates
- Corrective action planning and tracking
- Effectiveness verification

#### Continual Improvement (Clause 10.2)
- Improvement initiative tracking
- Metrics and KPI monitoring
- Change history with field-level tracking
- Audit trail for all operations

#### Advanced Features
- **RCA Templates**: Auto-extract root causes, probability calculations
- **Workflow Validators**: 68 edge case validations across 5 workflows
- **Audit Trail**: ISO-compliant activity logging with user context
- **Change History**: DeepDiff-based field-level tracking

## 🧪 Testing

### Unit Tests
- **Planning Service**: 127 tests
- **Plans Service**: 95 tests
- **BIA Service**: 45+ tests
- **Compliance Service**: 60+ tests
- **Total Coverage**: 85%+

Run tests:
```bash
# Planning Service
cd planning_service
PYTHONPATH=/Users/MD/AI-Platform-ISO/platform-services/planning_service:$PYTHONPATH python3 -m pytest tests/ -v

# Plans Service
cd plans_service
PYTHONPATH=/Users/MD/AI-Platform-ISO/platform-services/plans_service:$PYTHONPATH python3 -m pytest tests/ -v

# BIA Service
cd bia-service
PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH python3 -m pytest tests/ -v

# Compliance Service
cd compliance-service
PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH python3 -m pytest tests/ -v
```

## 📊 Monitoring & Metrics

### Prometheus Metrics

**HTTP Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Concurrent requests

**Business Metrics:**
- `planning_service_strategies_created_total`
- `planning_service_cost_benefit_calculations_total`
- `plans_service_plans_created_total`
- `plans_service_procedure_validations_total`
- `bia_service_processes_created_total`
- `bia_service_impact_assessments_total`
- `compliance_service_audits_created_total`
- `compliance_service_nonconformities_total`
- `compliance_service_rca_analyses_total`

**Infrastructure Metrics:**
- `database_connections_active`
- `eventbus_messages_published_total`
- `audit_log_entries_total`
- `change_history_records_total`

### Grafana Dashboards

Pre-configured dashboards:
- BCM Services Overview
- Request rates and error rates
- Latency percentiles (p50, p95, p99)
- Business metrics

## 🗄️ Database Schema

### Planning Service Tables
- `strategies` - Business continuity strategies
- `strategy_resources` - Resource allocations
- `cost_benefit_analyses` - Financial analyses

### Plans Service Tables
- `plans` - Business continuity plans
- `procedures` - Procedures with dependencies
- `plan_resources` - Resource allocations
- `plan_exercises` - Testing and exercises

### BIA Service Tables
- `bia_processes` - Business processes with ISO 22301 fields
- `bia_assessments` - Impact assessments and recovery objectives
- `bia_resources` - Resource requirements tracking

### Compliance Service Tables
- `audits` - Internal audit management
- `audit_evidence` - Evidence collection
- `audit_findings` - Findings and gaps
- `nonconformities` - NC tracking with RCA templates
- `corrective_actions` - CA planning and verification
- `improvements` - Continual improvement initiatives

### Shared Tables
- `audit_logs` - Audit trail for all operations
- `change_history` - Field-level change tracking

### Indexes
- 25+ composite indexes for optimal query performance
- Tenant isolation indexes
- Foreign key indexes
- Workflow state indexes

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://bcm_user:password@postgres:5432/bcm_platform

# JWT Authentication
JWT_PUBLIC_KEY=PLACEHOLDER_DEV_MODE
JWT_ALGORITHM=RS256

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

See `.env.example` for full configuration.

## 🐳 Docker Commands

### View all containers:
```bash
docker-compose ps
```

### Restart a service:
```bash
docker-compose restart planning-service
```

### View logs:
```bash
docker-compose logs -f planning-service
docker-compose logs -f plans-service
docker-compose logs -f bia-service
docker-compose logs -f compliance-service
```

### Access database:
```bash
docker-compose exec postgres psql -U bcm_user -d bcm_platform
```

### Access Redis:
```bash
docker-compose exec redis redis-cli
```

### Rebuild after code changes:
```bash
docker-compose up -d --build planning-service
docker-compose up -d --build plans-service
docker-compose up -d --build bia-service
docker-compose up -d --build compliance-service
```

## 📁 Project Structure

```
platform-services/
├── planning_service/           # ISO 22301 Clause 8.3
│   ├── api/                    # FastAPI routes
│   ├── auth/                   # JWT authentication
│   ├── database/               # Database layer
│   ├── domain/                 # Business logic
│   ├── models/                 # Pydantic models
│   ├── repositories/           # Data access
│   ├── services/               # Business services
│   ├── tests/                  # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
├── plans_service/              # ISO 22301 Clause 8.4
│   ├── api/
│   ├── auth/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── bia-service/                # ISO 22301 Clause 8.2.2
│   ├── api/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── tests/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── compliance-service/         # ISO 22301 Clauses 9.2, 10.1, 10.2
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── workflows/
│   ├── tests/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── monitoring/                 # Prometheus & Grafana
│   ├── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       └── datasources/
├── scripts/
│   └── init-databases.sh       # DB initialization
├── docker-compose.yml
├── .env
├── start.sh
├── stop.sh
├── logs.sh
└── status.sh
```

## 🔍 Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker info

# Check logs
./logs.sh

# Rebuild everything
docker-compose down -v
./start.sh
```

### Database connection errors
```bash
# Check PostgreSQL is ready
docker-compose exec postgres pg_isready -U bcm_user

# View database logs
docker-compose logs postgres
```

### Port already in use
```bash
# Find what's using the port
lsof -i :8011  # or :8023, :5432, etc.

# Kill the process or change port in docker-compose.yml
```

## 📚 API Documentation

Interactive API documentation available at:
- Planning Service: http://localhost:8011/docs
- Plans Service: http://localhost:8023/docs

### Example API Calls

**Create Strategy:**
```bash
curl -X POST http://localhost:8011/api/v1/strategies \
  -H "Content-Type: application/json" \
  -H "X-Dev-User: user123|tenant456|admin" \
  -d '{
    "name": "Primary Data Center Recovery",
    "strategy_type": "recovery",
    "description": "Recovery strategy for primary DC failure",
    "implementation_timeframe": "immediate"
  }'
```

**Create Plan:**
```bash
curl -X POST http://localhost:8023/api/v1/plans \
  -H "Content-Type: application/json" \
  -H "X-Dev-User: user123|tenant456|admin" \
  -d '{
    "plan_name": "IT Disaster Recovery Plan",
    "plan_type": "recovery",
    "scope": "IT Infrastructure"
  }'
```

**Create BIA Process:**
```bash
curl -X POST http://localhost:8012/api/v1/bia \
  -H "Content-Type: application/json" \
  -H "X-Dev-User: user123|tenant456|admin" \
  -d '{
    "process_name": "Payment Processing",
    "process_owner": "Finance Department",
    "criticality": "CRITICAL",
    "rto_hours": 2,
    "rpo_hours": 1,
    "mtpd_hours": 4
  }'
```

**Create Nonconformity with RCA:**
```bash
curl -X POST http://localhost:8014/api/v1/nonconformities \
  -H "Content-Type: application/json" \
  -H "X-Dev-User: user123|tenant456|admin" \
  -d '{
    "title": "Backup Failed",
    "description": "Daily backup process failed",
    "nc_type": "major",
    "rca_method": "5_whys",
    "rca_template": {
      "problem_statement": "Backup process failed",
      "why_1": "Storage was full",
      "why_2": "Retention policy not enforced",
      "why_3": "No automated cleanup configured",
      "why_4": "Initial setup was manual",
      "why_5": "Lack of proper documentation"
    }
  }'
```

## 🎯 ISO 22301:2019 Compliance

### Clause 8.2.2 - Business Impact Analysis (BIA Service)
✅ Process criticality assessment
✅ Recovery time objectives (RTO)
✅ Recovery point objectives (RPO)
✅ Maximum tolerable period of disruption (MTPD)
✅ Financial impact analysis
✅ Recovery strategies documentation
✅ Resource requirements (personnel, facilities, technology, information)
✅ Upstream/downstream dependencies
✅ Legal and regulatory requirements

### Clause 8.3 - Business Continuity Strategies (Planning Service)
✅ Resource requirements determination
✅ Protection and mitigation strategies
✅ Recovery time objectives (RTO)
✅ Recovery point objectives (RPO)
✅ Cost-benefit analysis
✅ Resource allocation

### Clause 8.4 - Business Continuity Plans and Procedures (Plans Service)
✅ Documented procedures
✅ Resource requirements
✅ Dependencies management
✅ Testing and exercising
✅ Version control
✅ Review and approval

### Clause 9.2 - Internal Audit (Compliance Service)
✅ Audit planning and scheduling
✅ Evidence collection and verification
✅ Finding assessment and categorization
✅ Gap analysis
✅ Audit trail logging

### Clause 10.1 - Nonconformity and Corrective Action (Compliance Service)
✅ Nonconformity logging and categorization
✅ Root cause analysis (5 Whys, Fishbone, Fault Tree)
✅ Corrective action planning
✅ Effectiveness verification
✅ Change history tracking

### Clause 10.2 - Continual Improvement (Compliance Service)
✅ Improvement initiative tracking
✅ Metrics and KPI monitoring
✅ Field-level change tracking
✅ Audit trail for all operations

## 🚧 Production Deployment

### Before Production

1. **Update JWT keys:**
   ```bash
   # Generate RSA key pair
   ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key
   # Update JWT_PUBLIC_KEY in .env
   ```

2. **Change passwords:**
   - PostgreSQL: `POSTGRES_PASSWORD`
   - Grafana: `GRAFANA_ADMIN_PASSWORD`

3. **Configure CORS:**
   - Update `ALLOWED_ORIGINS` with production domains

4. **Disable dev mode:**
   ```bash
   ALLOW_DEV_MODE=false
   DEBUG=false
   ENVIRONMENT=production
   ```

5. **Setup SSL/TLS:**
   - Configure reverse proxy (nginx/traefik)
   - Add SSL certificates

6. **Backup strategy:**
   - PostgreSQL backups
   - Volume backups

## 📝 License

Proprietary - BCM Platform

## 👥 Support

For issues, questions, or contributions, contact the development team.
