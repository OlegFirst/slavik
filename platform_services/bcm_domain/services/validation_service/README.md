# Validation Service

ISO 22301 Clauses 8.5, 9.1, 9.2, 9.3, 10 - Validation & Continuous Improvement

## Overview

The Validation Service manages:
- **Exercise Management** (ISO 8.5): BC plan testing and exercising
- **Performance Monitoring** (ISO 9.1): KPI tracking and measurement
- **Internal Audits** (ISO 9.2): Audit planning, execution, and findings
- **Management Reviews** (ISO 9.3): Strategic BCMS reviews
- **CAPA & Improvement** (ISO 10): Corrective and preventive actions

## Architecture

4-Tier Architecture:
```
validation/
├── api/              # API Layer (FastAPI routes, schemas)
├── services/         # Service Layer (business logic)
├── repositories/     # Repository Layer (data access)
├── workflows/        # Workflow Layer (state machines)
├── models/           # Domain & Database models
├── events/           # Event publishing/subscription
├── tasks/            # Background tasks (Celery)
├── config.py         # Configuration management
└── main.py           # FastAPI application entry point
```

## Setup

### 1. Install Dependencies

```bash
cd /Users/MD/AI-Platform-ISO/services/validation
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Initialize Database

```bash
# Run database migrations
alembic upgrade head
```

### 4. Run Service

```bash
# Development mode
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8022
```

### 5. Run Celery Worker (for background tasks)

```bash
# Start Celery worker
celery -A tasks.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A tasks.celery_app beat --loglevel=info
```

## API Endpoints

### Exercise Management
- `POST /api/validation/exercises` - Create exercise
- `GET /api/validation/exercises` - List exercises
- `GET /api/validation/exercises/{id}` - Get exercise
- `POST /api/validation/exercises/{id}/start` - Start exercise
- `POST /api/validation/exercises/{id}/complete` - Complete exercise
- `POST /api/validation/exercises/{id}/observations` - Add observation

### KPI Management
- `POST /api/validation/kpis` - Create KPI
- `GET /api/validation/kpis` - List KPIs
- `GET /api/validation/kpis/{id}` - Get KPI
- `POST /api/validation/kpis/{id}/measure` - Record measurement
- `GET /api/validation/kpis/{id}/trend` - Get trend analysis
- `GET /api/validation/kpis/dashboard` - Get KPI dashboard

### Internal Audits
- `POST /api/validation/audits` - Create audit
- `GET /api/validation/audits` - List audits
- `POST /api/validation/audits/{id}/findings` - Add finding
- `GET /api/validation/audits/{id}/report` - Generate audit report

### CAPA
- `POST /api/validation/capa` - Create CAPA
- `GET /api/validation/capa` - List CAPAs
- `PATCH /api/validation/capa/{id}` - Update CAPA
- `POST /api/validation/capa/{id}/verify` - Verify CAPA

### Management Reviews
- `POST /api/validation/management-reviews` - Create review
- `GET /api/validation/management-reviews` - List reviews
- `GET /api/validation/management-reviews/{id}/prepare` - Auto-prepare review data

## Features

### KPI Auto-Collection
- Automatic KPI data collection from BCM modules
- Configurable collection intervals
- Multiple collection methods (manual, automated, calculated)

### KPI Alerting
- Real-time threshold monitoring
- Email notifications for critical/warning breaches
- Auto-resolution when KPIs recover

### Workflow State Machines
- Exercise workflow: planned → scheduled → in_progress → completed → reviewed
- Audit workflow: planned → in_progress → fieldwork_complete → reported → closed
- CAPA workflow: open → in_progress → implemented → verified → closed

### Event-Driven Integration
- Publishes events: exercise.completed, kpi.alert, audit.finding, capa.closed
- Subscribes to: governance.*, plans.*, incidents.*

## Development

### Running Tests
```bash
pytest tests/ -v --cov=.
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## Migration Notes

This service was migrated from:
- **Source**: `/Users/MD/ISO-22301—копия/services/SERVICES/BCM/validation/`
- **Destination**: `/Users/MD/AI-Platform-ISO/services/validation/`

**Key Changes**:
- Migrated from monolithic main.py (2168 lines) to 4-tier architecture
- Removed mock/stub implementations
- Connected to real infrastructure (EventBus, Orchestrator)
- Preserved all business logic and workflows
- Maintained backward compatibility with API contracts

## License

Proprietary - Internal BCM Platform
