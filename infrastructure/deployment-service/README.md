# BCM Deployment Service

**Extracted from:** `/intelligent-core/tools/deployer/` (Oct 4, 2025)
**Status:** Production-ready
**Lines of code:** 223

## What it does
Simple and reliable deployment service for managing BCM platform infrastructure. Orchestrates Docker containers, manages service health checks, and provides deployment automation without AI complexity.

## Integration points
- Docker Engine: Direct container orchestration
- Docker Compose: Service orchestration and configuration
- Health Checks: HTTP endpoint monitoring with auto-restart
- Database: PostgreSQL connection for deployment tracking

## Dependencies
- FastAPI (web framework)
- Docker SDK for Python
- Requests (HTTP client)
- Standard Python libraries

## Key Features
- Service deployment orchestration
- Health monitoring and auto-restart
- Docker-compose based configuration
- Deployment state tracking
- RESTful API for deployment operations

## How to run
```bash
# Build the service
docker build -t bcm-deployer .

# Run standalone
python main.py

# Or via docker-compose
docker-compose up deployer
```

## API Endpoints
- `GET /health` - Service health check
- `POST /deploy` - Deploy services
- `GET /status` - Deployment status
- `POST /restart` - Restart services
