# BIA Service - Deployment Guide

**Version**: 1.0.0
**Date**: 2025-10-09

## Table of Contents

1. [Deployment Overview](#1-deployment-overview)
2. [Prerequisites](#2-prerequisites)
3. [Environment Configuration](#3-environment-configuration)
4. [Local Development Deployment](#4-local-development-deployment)
5. [Docker Deployment](#5-docker-deployment)
6. [Production Deployment](#6-production-deployment)
7. [Database Setup](#7-database-setup)
8. [Monitoring & Logging](#8-monitoring--logging)
9. [Troubleshooting](#9-troubleshooting)

## 1. Deployment Overview

### 1.1 Deployment Architecture

```
┌────────────────────────────────────────────────────────┐
│                  Production Environment                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Load Balancer│  │ Load Balancer│  │ Load Balancer│
│  │  (Nginx)     │  │  (Nginx)     │  │  (Nginx)     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         │                 │                  │         │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼──────┐ │
│  │ BIA Service  │  │ BIA Service  │  │ BIA Service │ │
│  │ Instance 1   │  │ Instance 2   │  │ Instance 3  │ │
│  │ Port 8012    │  │ Port 8012    │  │ Port 8012   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         │                 │                  │         │
│         └─────────────────┴──────────────────┘         │
│                           │                            │
│  ┌────────────────────────▼──────────────────────┐    │
│  │  Infrastructure Services                      │    │
│  │  - PostgreSQL (RDS/Managed)                  │    │
│  │  - Redis (ElastiCache/Managed)               │    │
│  │  - RabbitMQ (CloudAMQP/Managed)              │    │
│  └───────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
```

### 1.2 Deployment Options

| Environment | Method | Orchestration | Scale |
|-------------|--------|---------------|-------|
| Development | Local Python | None | 1 instance |
| Development | Docker Compose | Docker | 1-3 instances |
| Staging | Kubernetes | K8s | 2-5 instances |
| Production | Kubernetes | K8s | 3-10 instances |

## 2. Prerequisites

### 2.1 Software Requirements

**Required:**
- Python 3.11 or higher
- PostgreSQL 14+ (or SQLite for dev)
- Redis 7.0+
- RabbitMQ 3.12+ (if EventBus enabled)

**Optional:**
- Docker 24.0+
- Docker Compose 2.20+
- Kubernetes 1.27+
- Nginx (for load balancing)

### 2.2 System Requirements

**Minimum (Development):**
- CPU: 2 cores
- RAM: 2 GB
- Disk: 10 GB

**Recommended (Production per instance):**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB SSD

**Database:**
- CPU: 4+ cores
- RAM: 16 GB
- Disk: 100 GB SSD (IOPS 3000+)

## 3. Environment Configuration

### 3.1 Environment Variables

Create `.env` file:

```bash
# Service Configuration
BIA_SERVICE_PORT=8012
BIA_SERVICE_VERSION=1.0.0
BIA_LOG_LEVEL=INFO
BIA_DEBUG_MODE=false

# Database Configuration
DATABASE_URL=postgresql+asyncpg://bia_user:password@postgres:5432/bcm_platform
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=false

# Authentication
JWT_SECRET=<generate-strong-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Redis Cache
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=50

# EventBus Configuration
EVENTBUS_URL=amqp://guest:guest@rabbitmq:5672
FEATURE_EVENTBUS=true
EVENTBUS_TIMEOUT=30

# AI Services
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
AI_ENABLED=true
AI_ORCHESTRATOR_URL=http://ai-orchestration:8002

# Feature Flags
WHO_TIER_ENABLED=true
SUPPLY_CHAIN_ENABLED=true

# CORS Configuration
CORS_ENABLED=true
CORS_ORIGINS=https://app.example.com,https://admin.example.com
CORS_ALLOW_CREDENTIALS=true

# Monitoring
PROMETHEUS_ENABLED=true
SENTRY_DSN=<your-sentry-dsn>
```

### 3.2 Secrets Management

**Development:**
```bash
# Use .env file (git-ignored)
cp .env.example .env
# Edit .env with your values
```

**Production:**
```bash
# Use Kubernetes Secrets
kubectl create secret generic bia-service-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://...' \
  --from-literal=JWT_SECRET='...' \
  --from-literal=OPENAI_API_KEY='...'
```

## 4. Local Development Deployment

### 4.1 Python Virtual Environment

```bash
# Clone repository
git clone https://github.com/your-org/AI-Platform-ISO.git
cd AI-Platform-ISO/platform-services/bia-service

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="sqlite+aiosqlite:///./bia_dev.db"
export JWT_SECRET="dev-secret-key"
export REDIS_URL="redis://localhost:6379/0"

# Run database migrations (PostgreSQL only)
alembic upgrade head

# Start service
python main.py
```

Service available at: `http://localhost:8012`

### 4.2 Development with Hot Reload

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8012
```

## 5. Docker Deployment

### 5.1 Build Docker Image

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8012

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8012/health || exit 1

# Run application
CMD ["python", "main.py"]
```

**Build:**

```bash
docker build -t bia-service:1.0.0 .
```

### 5.2 Docker Compose Deployment

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  bia-service:
    image: bia-service:1.0.0
    container_name: bia-service
    ports:
      - "8012:8012"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/bcm_platform
      - REDIS_URL=redis://redis:6379/0
      - EVENTBUS_URL=amqp://guest:guest@rabbitmq:5672
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
      - rabbitmq
    networks:
      - bcm-network
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: postgres
    environment:
      - POSTGRES_DB=bcm_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - bcm-network

  redis:
    image: redis:7-alpine
    container_name: redis
    networks:
      - bcm-network
    volumes:
      - redis_data:/data

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - bcm-network
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

networks:
  bcm-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
```

**Run:**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bia-service

# Stop services
docker-compose down
```

## 6. Production Deployment

### 6.1 Kubernetes Deployment

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bia-service
  namespace: bcm-platform
  labels:
    app: bia-service
    version: "1.0.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bia-service
  template:
    metadata:
      labels:
        app: bia-service
        version: "1.0.0"
    spec:
      containers:
      - name: bia-service
        image: your-registry.io/bia-service:1.0.0
        ports:
        - containerPort: 8012
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bia-service-secrets
              key: DATABASE_URL
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: bia-service-secrets
              key: JWT_SECRET
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        - name: EVENTBUS_URL
          value: "amqp://guest:guest@rabbitmq-service:5672"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8012
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8012
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: bia-service
  namespace: bcm-platform
spec:
  selector:
    app: bia-service
  ports:
  - protocol: TCP
    port: 8012
    targetPort: 8012
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bia-service-hpa
  namespace: bcm-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bia-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Deploy:**

```bash
# Create namespace
kubectl create namespace bcm-platform

# Create secrets
kubectl apply -f secrets.yaml

# Deploy service
kubectl apply -f deployment.yaml

# Verify deployment
kubectl get pods -n bcm-platform
kubectl logs -f deployment/bia-service -n bcm-platform
```

### 6.2 Load Balancer Configuration

**Nginx configuration:**

```nginx
upstream bia_service {
    least_conn;
    server bia-service-1:8012 max_fails=3 fail_timeout=30s;
    server bia-service-2:8012 max_fails=3 fail_timeout=30s;
    server bia-service-3:8012 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name bia.example.com;

    location / {
        proxy_pass http://bia_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Health check
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }

    location /health {
        access_log off;
        proxy_pass http://bia_service;
    }
}
```

## 7. Database Setup

### 7.1 PostgreSQL Setup

**Create database and user:**

```sql
-- Create database
CREATE DATABASE bcm_platform;

-- Create user
CREATE USER bia_user WITH ENCRYPTED PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE bcm_platform TO bia_user;

-- Connect to database
\c bcm_platform

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO bia_user;
```

### 7.2 Run Migrations

```bash
# Install Alembic
pip install alembic

# Initialize migrations (first time only)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial BIA tables"

# Apply migrations
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### 7.3 Database Backup

```bash
# Backup
pg_dump -h postgres-host -U bia_user bcm_platform > bia_backup_$(date +%Y%m%d).sql

# Restore
psql -h postgres-host -U bia_user bcm_platform < bia_backup_20251009.sql
```

## 8. Monitoring & Logging

### 8.1 Prometheus Metrics

**Metrics endpoint:** `http://bia-service:8012/metrics`

**Key metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `bia_processes_total` - Total BIA processes
- `bia_processes_by_criticality` - Processes by criticality level
- `cache_hits_total` - Cache hits
- `cache_misses_total` - Cache misses

### 8.2 Logging Configuration

```python
# Production logging configuration
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/bia-service/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
})
```

### 8.3 Health Checks

**Liveness probe:**
```bash
curl http://localhost:8012/health
```

**Readiness probe:**
```bash
# Check all dependencies healthy
curl http://localhost:8012/health | jq '.cache.enabled && .features.eventbus'
```

## 9. Troubleshooting

### 9.1 Common Issues

**Issue: Service won't start**
```bash
# Check logs
docker logs bia-service
kubectl logs deployment/bia-service

# Common causes:
# - Database connection failure
# - Missing environment variables
# - Port already in use
```

**Issue: Database connection errors**
```bash
# Test database connection
psql -h postgres-host -U bia_user -d bcm_platform -c "SELECT 1;"

# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql+asyncpg://user:pass@host:port/db
```

**Issue: High memory usage**
```bash
# Check connection pool size
# Reduce DB_POOL_SIZE if needed
export DB_POOL_SIZE=10

# Monitor memory
docker stats bia-service
```

### 9.2 Performance Tuning

**Database connection pooling:**
```python
# Tune based on load
DB_POOL_SIZE=20  # Max connections per instance
DB_MAX_OVERFLOW=10  # Additional connections under load
```

**Cache configuration:**
```python
# Increase cache TTL for stable data
CACHE_TTL_PROCESS=600  # 10 minutes
CACHE_TTL_REPORT=1800  # 30 minutes
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-09
**Maintained By**: AI Platform Team
