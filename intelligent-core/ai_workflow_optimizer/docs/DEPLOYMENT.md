# Ai Workflow Optimizer - Deployment Guide

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
PORT=8038
```

## Docker Deployment

```bash
# Build
docker build -t ai_workflow_optimizer:latest .

# Run
docker run -p 8038:8038 --env-file .env ai_workflow_optimizer:latest
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai_workflow_optimizer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai_workflow_optimizer
  template:
    metadata:
      labels:
        app: ai_workflow_optimizer
    spec:
      containers:
      - name: ai_workflow_optimizer
        image: ai_workflow_optimizer:latest
        ports:
        - containerPort: 8038
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
