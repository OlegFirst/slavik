# Shared - Deployment Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7.0+
- Docker 24+ (optional)

## Environment Variables

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Messaging
REDIS_URL=redis://localhost:6379

# Service Configuration
LOG_LEVEL=INFO
```

## Docker Deployment

```bash
# Build
docker build -t shared:latest .

# Run
docker run -p 8000:8000 --env-file .env shared:latest
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shared
spec:
  replicas: 2
  selector:
    matchLabels:
      app: shared
  template:
    metadata:
      labels:
        app: shared
    spec:
      containers:
      - name: shared
        image: shared:latest
        ports:
        - containerPort: 8000
```

## Health Checks

- Liveness: `GET /health`
- Readiness: `GET /health`

## Monitoring

- Prometheus metrics: `GET /metrics`
- Grafana dashboards available

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
