# Docker Compose Usage Guide

## Profiles

This Docker Compose uses **profiles** to control which services start:

### Available Profiles:

1. **`dev`** - All services for development
2. **`prod`** - Production services only (no dev tools)
3. **`core`** - Only core AI modules (ai-foundation, workflow-intelligence, expertise-center)
4. **`platform`** - Only platform services (BIA, Risk, Compliance, etc.)
5. **`observability`** - Only monitoring stack (Prometheus, Grafana, etc.)

## Usage Examples

### Start everything (development):
```bash
docker-compose --profile dev up -d
```

### Start only core modules:
```bash
docker-compose --profile core up -d
```

### Start core + observability:
```bash
docker-compose --profile core --profile observability up -d
```

### Production deployment:
```bash
docker-compose --profile prod up -d
```

### Only monitoring stack:
```bash
docker-compose --profile observability up -d
```

## Networks

All services are in `bcm-network` (172.20.0.0/16)

Service-to-service communication:
```python
# From one service to another
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get('http://ai-foundation:9001/health')
```

## Volumes

Persistent volumes for:
- Database services
- Prometheus (metrics data)
- Grafana (dashboards)

## Health Checks

All services have health checks. Check status:
```bash
docker-compose ps
```

## Logs

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-foundation

# Last 100 lines
docker-compose logs --tail=100
```

## Stop Services

```bash
# Stop all
docker-compose down

# Stop but keep volumes
docker-compose down -v

# Stop specific profile
docker-compose --profile observability down
```

## Resource Limits

Services have resource limits:
- AI services: 2 CPU, 4GB RAM
- Gateway: 1 CPU, 2GB RAM
- Other: 0.5 CPU, 1GB RAM

Adjust in docker-compose.improved.yml if needed.
