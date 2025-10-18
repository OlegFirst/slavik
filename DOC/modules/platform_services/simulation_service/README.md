# Simulation & Modeling Service

**Type**: Platform Service
**Port**: 8095
**Status**: In Development
**Version**: 1.0.0

## Overview

The Simulation & Modeling Service is a comprehensive platform for business continuity management (BCM) simulations, exercises, and "what-if" analysis. It provides multi-engine simulation capabilities with deep integration into the AI-Platform-ISO ecosystem.

## Key Features

### 🎯 Core Capabilities

1. **Task Specification Generator** - AI-powered simulation specification creation
2. **Scenario Library** - Searchable repository with RAG-based search
3. **Multi-Engine Support** - JaamSim, SimPy, Monte Carlo, What-If analysis
4. **Real-time Visualization** - Interactive dashboards and 3D visualization
5. **Professional Reporting** - ISO 22301 compliant PDF/DOCX reports
6. **Knowledge Integration** - Automatic storage in Knowledge Center
7. **Community Sharing** - Contribution to Community Intelligence
8. **PDCA Integration** - Full Plan-Do-Check-Act cycle support

### 🔗 Platform Integrations

- **EventBus** - Platform-wide event choreography
- **AI Orchestrator** - Autonomous decision-making during simulations
- **Workflow Intelligence** - PDCA cycles and Case Library integration
- **Knowledge Center** - Best practices and lessons learned storage
- **Community Intelligence** - Scenario sharing and peer review
- **Predictive Journey** - Outcome forecasting and recommendations
- **AI Foundation** - RAG search, LLM generation, ML predictions
- **Digital Twin** (optional) - Real organization data for simulations

### 🎭 Dual Mode Operation

#### A. Internal Service (for Platform)
- Pre-workflow validation
- Infrastructure resilience testing
- Load testing and performance optimization
- Event choreography validation
- Priority queue optimization

#### B. External Service (for Users)
- BCM exercises and drills
- Training simulations
- Compliance testing
- "What-if" scenario analysis
- Strategic decision validation

## Architecture

```
Simulation Service (Port 8095)
├── Task Specification Generator
├── Scenario Library & Generator (AI-powered)
├── Multi-Engine Simulation
│   ├── JaamSim (Discrete Event Simulation)
│   ├── SimPy (Process Simulation)
│   ├── Monte Carlo (Statistical Analysis)
│   └── What-If Engine (Impact Analysis)
├── Real-time Visualization
├── Analytics & Reporting
└── Platform Integration Layer
    ├── EventBus Client
    ├── AI Orchestrator Client
    ├── Workflow Intelligence Client
    ├── Knowledge Center Client
    ├── Community Intelligence Client
    └── AI Foundation Client
```

## Technology Stack

### Backend
- **FastAPI** - REST API framework
- **SQLAlchemy** - ORM and database management
- **Pydantic** - Data validation
- **PostgreSQL** - Primary database
- **Redis** - Caching and real-time updates

### Simulation Engines
- **JaamSim** - Discrete event simulation
- **SimPy** - Process-based discrete-event simulation
- **NumPy/SciPy** - Statistical analysis
- **Pandas** - Data processing

### Visualization
- **Plotly Dash** - Interactive dashboards
- **WebSocket** - Real-time updates
- **Three.js** - 3D visualization

### Reporting
- **ReportLab** - PDF generation
- **python-docx** - DOCX generation
- **Jinja2** - Template rendering

### AI/ML
- **Integration with AI Foundation** for:
  - RAG (Retrieval Augmented Generation)
  - LLM (Large Language Models)
  - ML (Machine Learning models)

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker (optional)

### Local Development

```bash
# Clone repository
cd /Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start service
uvicorn main:app --host 0.0.0.0 --port 8095 --reload
```

### Docker Deployment

```bash
# Build image
docker build -t simulation-service:latest .

# Run container
docker run -p 8095:8095 --env-file .env simulation-service:latest

# Or use docker-compose
docker-compose up -d
```

## API Documentation

Once the service is running, access:
- **Swagger UI**: http://localhost:8095/docs
- **ReDoc**: http://localhost:8095/redoc

## Configuration

### Environment Variables

```bash
# Service
PORT=8095
LOG_LEVEL=INFO
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/simulation_db
REDIS_URL=redis://localhost:6379

# Platform Integration
EVENTBUS_URL=http://localhost:8055
AI_ORCHESTRATOR_URL=http://localhost:8026
WORKFLOW_INTELLIGENCE_URL=http://localhost:8037
KNOWLEDGE_CENTER_URL=http://localhost:8038
COMMUNITY_INTELLIGENCE_URL=http://localhost:8030
PREDICTIVE_JOURNEY_URL=http://localhost:8031
AI_FOUNDATION_URL=http://localhost:8025
DIGITAL_TWIN_URL=http://localhost:8096
DIGITAL_TWIN_ENABLED=false

# Simulation Engines
JAAMSIM_PATH=/opt/jaamsim
SIMULATION_WORKING_DIR=/tmp/simulations

# AI/ML
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

## Usage Examples

### 1. Create and Run Simulation

```python
import httpx

# Create simulation specification
spec_request = {
    "goal": "Test BIA process resilience",
    "constraints": {
        "max_duration": "4 hours",
        "participants": 10,
        "complexity": "high"
    },
    "context": {
        "organization_type": "hospital",
        "size": "large"
    }
}

async with httpx.AsyncClient() as client:
    # Generate specification
    spec_response = await client.post(
        "http://localhost:8095/api/v1/specifications",
        json=spec_request
    )
    spec = spec_response.json()

    # Generate scenario
    scenario_response = await client.post(
        "http://localhost:8095/api/v1/scenarios/generate",
        json={"specification_id": spec["id"]}
    )
    scenario = scenario_response.json()

    # Create and start simulation
    sim_response = await client.post(
        "http://localhost:8095/api/v1/simulations",
        json={
            "specification_id": spec["id"],
            "scenario_id": scenario["id"],
            "engine": "jaamsim",
            "auto_start": True
        }
    )
    simulation = sim_response.json()

    print(f"Simulation started: {simulation['id']}")
```

### 2. Monitor Real-time Progress

```python
import asyncio
import websockets

async def monitor_simulation(simulation_id):
    uri = f"ws://localhost:8095/ws/simulations/{simulation_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Progress: {message}")

asyncio.run(monitor_simulation("sim_12345"))
```

### 3. Generate Report

```python
# Get simulation report
report_response = await client.post(
    f"http://localhost:8095/api/v1/reports/generate",
    json={
        "simulation_id": "sim_12345",
        "format": "pdf",
        "template": "iso_22301"
    }
)

report_url = report_response.json()["download_url"]
print(f"Report available: {report_url}")
```

## Project Structure

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# Coverage
pytest --cov=. --cov-report=html
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

## Monitoring

### Health Checks
- **Readiness**: `GET /health`
- **Liveness**: `GET /health/live`
- **Metrics**: `GET /metrics` (Prometheus format)

### Key Metrics
- `simulations_total` - Total simulations created
- `simulations_running` - Currently running simulations
- `simulations_completed` - Successfully completed
- `simulations_failed` - Failed simulations
- `simulation_duration_seconds` - Duration histogram
- `engine_usage` - Usage by engine type
- `integration_calls` - Platform integration calls

## Contributing

1. Create feature branch
2. Implement changes with tests
3. Ensure all tests pass
4. Submit pull request

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-12
**Maintainer**: AI Platform Team
**Status**: Phase 1 - Core Infrastructure (In Development)

## Roadmap

### Phase 1 (Week 1-2): Core Infrastructure ✅
- [x] Project structure
- [x] Database models
- [x] EventBus integration
- [ ] Core orchestrator
- [ ] Basic API endpoints

### Phase 2 (Week 2-3): Engine Integration
- [ ] Refactor JaamSim client
- [ ] Create SimPy engine
- [ ] Upgrade What-If engine
- [ ] Upgrade Monte Carlo engine

### Phase 3 (Week 3-4): New Components
- [ ] Task Specification Generator
- [ ] Visualization module
- [ ] Analytics & Reporting
- [ ] AI Foundation integration

### Phase 4 (Week 4-5): Platform Integration
- [ ] All platform clients
- [ ] Knowledge Center integration
- [ ] Community Intelligence integration
- [ ] End-to-end testing

### Phase 5 (Week 5-6): Production Ready
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation completion
- [ ] Deployment automation
