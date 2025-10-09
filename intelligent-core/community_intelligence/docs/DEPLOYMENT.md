# Community Intelligence - Deployment Guide

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
PORT=8030
```

## Docker Deployment

```bash
# Build
docker build -t community_intelligence:latest .

# Run
docker run -p 8030:8030 --env-file .env community_intelligence:latest
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: community_intelligence
spec:
  replicas: 2
  selector:
    matchLabels:
      app: community_intelligence
  template:
    metadata:
      labels:
        app: community_intelligence
    spec:
      containers:
      - name: community_intelligence
        image: community_intelligence:latest
        ports:
        - containerPort: 8030
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
