# BCM Platform - Quick Start Guide

## 🎯 Quick Setup (3-5 minutes)

### Prerequisites

- Python 3.11+
- Anthropic API key
- (Optional) Docker & Docker Compose for full stack

---

## Option 1: Quick Test (No Docker)

### 1. Setup Environment

```bash
# Clone repository (or you're already in it)
cd AI-Platform-ISO

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy template
cp .env.template .env

# Edit .env and add your ANTHROPIC_API_KEY
nano .env  # or use any editor
```

### 3. Generate Test Data

```bash
# Generate seed data
python scripts/seed_data_generator.py --output data/seed/

# This creates:
# - data/seed/bia_cases.json (50 cases)
# - data/seed/risk_cases.json (30 cases)
# - data/seed/planning_cases.json (20 cases)
# - data/seed/annotations.json (100 annotations)
# - data/seed/benchmarks.json
```

### 4. Test Individual Modules

```bash
# Test Community Intelligence
cd intelligent-core/community_intelligence
python -m pytest tests/ -v

# Test Collective Agents
cd ../collective
python -m pytest tests/ -v

# Test Workflow Intelligence
cd ../workflow_intelligence
python -m pytest tests/ -v
```

---

## Option 2: Full Stack with Docker (Recommended)

### 1. Setup

```bash
# Copy environment template
cp .env.template .env

# Add your ANTHROPIC_API_KEY to .env
nano .env
```

### 2. Run Quick Start

```bash
# Make script executable
chmod +x quickstart.sh

# Run it!
./quickstart.sh
```

This will:
1. Generate seed data (50 BIA cases, 30 Risk cases, 20 Planning cases)
2. Start infrastructure (Postgres, Redis, Neo4j)
3. Run database migrations
4. Load seed data
5. Start all services
6. Run integration test

### 3. Access the Platform

After ~3-5 minutes, you'll have:

- **Main API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **AI Orchestrator**: http://localhost:8001
- **Grafana**: http://localhost:3000 (admin/admin)
- **MLflow**: http://localhost:5000
- **Neo4j Browser**: http://localhost:7474 (neo4j/neo4j_password)

---

## Manual Setup (Step by Step)

If you prefer manual control:

```bash
# 1. Generate seed data
python scripts/seed_data_generator.py --output data/seed/

# 2. Start databases
docker-compose up -d postgres redis neo4j

# 3. Wait for databases
sleep 10

# 4. Run migrations
python infrastructure/database/apply_migrations_simple.py

# 5. Start services
docker-compose up -d

# 6. Check status
docker-compose ps
```

---

## Verify Installation

### 1. Check API Docs

Open http://localhost:8000/docs

You should see FastAPI interactive documentation.

### 2. Test Community Intelligence

```bash
curl http://localhost:8003/api/v1/contributions
```

### 3. Test Collective Agents

```bash
curl http://localhost:8032/api/v1/collective-agents/active
```

### 4. Run Integration Tests

```bash
python scripts/end_to_end_integration.py
```

---

## Troubleshooting

### Services not starting

```bash
# Check logs
docker-compose logs <service-name>

# Common services: postgres, redis, neo4j, intelligent-core
docker-compose logs postgres
```

### Database connection issues

```bash
# Restart database
docker-compose restart postgres

# Check if it's healthy
docker-compose ps postgres

# Connect to database manually
docker-compose exec postgres psql -U bcm_user -d bcm_platform
```

### Port already in use

```bash
# Find what's using the port
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### Reset everything

```bash
# Warning: This deletes all data!
docker-compose down -v

# Then run quickstart again
./quickstart.sh
```

---

## Module-Specific Testing

### Test Community Intelligence

```bash
cd intelligent-core/community_intelligence

# Run service
python main.py

# In another terminal
curl http://localhost:8003/health
```

### Test Collective Agents

```bash
cd intelligent-core/collective

# Run service
python main.py

# Test stuck detection
curl -X POST http://localhost:8032/api/v1/stuck-detection/check \
  -H "Content-Type: application/json" \
  -d '{"org_id": "test-org-123", "module": "bia"}'
```

### Test Workflow Intelligence

```bash
cd intelligent-core/workflow_intelligence

# Run tests
python -m pytest tests/ -v

# Run example
python examples/basic_bia_workflow.py
```

---

## Development Workflow

### 1. Make changes

Edit code in your preferred IDE.

### 2. Run tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_specific.py -v
```

### 3. Reload services

```bash
# If using Docker
docker-compose restart <service-name>

# If running locally
# Just restart the Python process (auto-reload is enabled)
```

---

## Data Generation Options

### Generate more data

```bash
python scripts/seed_data_generator.py \
    --bia-cases 100 \
    --risk-cases 50 \
    --planning-cases 30 \
    --annotations 200 \
    --output data/seed/
```

### Generate industry-specific data

Edit `scripts/seed_data_generator.py` and add your industry to the `self.industries` dict.

---

## Next Steps

1. **Explore API**: http://localhost:8000/docs
2. **Read Architecture**: [ARCHITECTURE_VISION.md](ARCHITECTURE_VISION.md)
3. **Check Modules**:
   - [Community Intelligence](intelligent-core/community_intelligence/INTEGRATION_COMPLETE.md)
   - [Collective Agents](intelligent-core/collective/INTEGRATION_COMPLETE.md)
   - [Workflow Intelligence](intelligent-core/workflow_intelligence/WORKFLOW_INTELLIGENCE_COMPLETE.md)

---

## Getting Help

- Check logs: `docker-compose logs -f`
- View service status: `docker-compose ps`
- Inspect database: `docker-compose exec postgres psql -U bcm_user -d bcm_platform`
- Review documentation in `docs/` folder

---

## Stopping the Platform

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes all data!)
docker-compose down -v
```

---

**🎉 You're all set! Start exploring the AI-Powered BCM Platform.**
