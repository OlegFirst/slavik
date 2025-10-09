# Event Intelligence - Deployment Guide

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
PORT=8036
```

## Docker Deployment

```bash
# Build
docker build -t event_intelligence:latest .

# Run
docker run -p 8036:8036 --env-file .env event_intelligence:latest
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: event_intelligence
spec:
  replicas: 2
  selector:
    matchLabels:
      app: event_intelligence
  template:
    metadata:
      labels:
        app: event_intelligence
    spec:
      containers:
      - name: event_intelligence
        image: event_intelligence:latest
        ports:
        - containerPort: 8036
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
