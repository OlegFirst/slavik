# Learning System - Deployment Guide

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
PORT=8033
```

## Docker Deployment

```bash
# Build
docker build -t learning-system:latest .

# Run
docker run -p 8033:8033 --env-file .env learning-system:latest
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: learning-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: learning-system
  template:
    metadata:
      labels:
        app: learning-system
    spec:
      containers:
      - name: learning-system
        image: learning-system:latest
        ports:
        - containerPort: 8033
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
