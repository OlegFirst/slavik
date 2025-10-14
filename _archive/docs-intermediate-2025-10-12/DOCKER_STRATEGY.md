# Docker Containerization Strategy

**Date:** 2025-10-11
**Purpose:** Production-ready containerization для Railway/Cloud deployment
**Architect:** DevOps Agent + Project Agent

---

## 🎯 Architecture Analysis

### Текущая Архитектура (52 сервиса):

```
┌─────────────────────────────────────────────────────────────┐
│                    AI-POWERED BCM PLATFORM                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │ Platform Services│  │ Intelligent Core │              │
│  │    (9 services)  │  │   (12 services)  │              │
│  └──────────────────┘  └──────────────────┘              │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │  Infrastructure  │  │   AI Office      │              │
│  │   (8 services)   │  │   (6 services)   │              │
│  └──────────────────┘  └──────────────────┘              │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │    Interfaces    │  │   Integrations   │              │
│  │   (3 services)   │  │   (3 services)   │              │
│  └──────────────────┘  └──────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Containerization Strategy

### Принцип: **Microservices with Logical Grouping**

Не монолит, но и не 52 контейнера! Группируем по:
1. **Функциональности** (что делает)
2. **Зависимостям** (shared dependencies)
3. **Scale требованиям** (кто масштабируется вместе)
4. **Deployment частоте** (кто деплоится вместе)

---

## 📦 Container Groups (12 контейнеров)

### Group 1: **Gateway** (1 container)
```
gateway-container:
  - API Gateway (8000)
  - Rate Limiting
  - Authentication
  - Routing
```
**Rationale:** Entry point, separate для security isolation

### Group 2: **Platform Services** (1 container)
```
platform-services-container:
  - BIA Service (8012)
  - Risk Service (8026)
  - Compliance Service (8014)
  - Governance Service (8025)
  - Planning Service (8011)
  - Plans Service (8023)
  - Response Service (8027)
  - Learning Service (8021)
  - Documents Service (8022)
```
**Rationale:**
- Shared dependencies (FastAPI, SQLAlchemy, same DB)
- Similar resource requirements
- Deploy together (business logic)

### Group 3: **Intelligent Core** (1 container)
```
intelligent-core-container:
  - AI Orchestration (8002)
  - Workflow Intelligence (8028)
  - Community Intelligence (8030)
  - Predictive Service (8031)
  - Event Intelligence (8032)
  - Collective (8034)
  - AI Workflow Optimizer (8038)
```
**Rationale:**
- AI/ML dependencies (heavy)
- Shared models
- Scale together

### Group 4: **Expertise Center** (1 container)
```
expertise-container:
  - Expertise Center (8029) - 14 AI specialists
  - Coordination Center (8033)
```
**Rationale:**
- Specialized AI agents
- Resource-intensive
- Independent scaling

### Group 5: **EventBus** (1 container)
```
eventbus-container:
  - EventBus (8001)
  - Message Queue
  - Event routing
```
**Rationale:**
- Critical infrastructure
- Separate for reliability
- Independent scaling

### Group 6: **AI Office Infrastructure** (1 container)
```
ai-office-container:
  - MIO Manager (8057)
  - Agent Router (8059)
  - Project Agent (8060)
  - DevOps Agent (8058)
  - Analytics Specialist (8056)
  - AI Event Manager (8055)
```
**Rationale:**
- Internal tooling
- Shared orchestration logic
- Lower resource requirements

### Group 7: **Monitoring Stack** (1 container)
```
monitoring-container:
  - Prometheus (9090)
  - Monitoring Backend (8050)
  - Service Catalog (8052)
  - Metrics Exporters
```
**Rationale:**
- Observability system
- Self-contained
- Volume for metrics data

### Group 8: **Database Services** (1 container)
```
db-services-container:
  - DB Intelligence (8051)
  - DB Migration Runner
  - Connection Pool Manager
```
**Rationale:**
- Database tooling
- Separate от main DB (external Supabase)

### Group 9: **Security** (1 container)
```
security-container:
  - Auth Service (8081)
  - Secrets Manager (8084)
  - JWT Handler
```
**Rationale:**
- Security-critical
- Isolated for compliance
- Audit logging

### Group 10: **Runtime Services** (1 container)
```
runtime-container:
  - Realtime WebSocket (8082)
  - Message Queue (8085)
  - Service Discovery (8086)
```
**Rationale:**
- Runtime infrastructure
- Shared dependencies (asyncio)

### Group 11: **Interfaces** (1 container)
```
interfaces-container:
  - Admin Panel (3000)
  - User Portal (3001)
  - Control Center (3002)
```
**Rationale:**
- Frontend apps (React/Vue)
- Static builds + nginx
- CDN-ready

### Group 12: **Integrations** (1 container)
```
integrations-container:
  - GitHub Integration (8087)
  - MCP Server (8088)
  - Partisia Contracts (8089)
```
**Rationale:**
- External integrations
- Optional components
- Independent failure domain

---

## 🗂️ Shared Volumes

### Volume 1: **Database** (External - Supabase)
```yaml
# No volume - external cloud DB
DATABASE_URL: postgresql://...@supabase.com
```

### Volume 2: **Redis Cache**
```yaml
redis-data:
  type: volume
  persist: true
  backup: false
```

### Volume 3: **Logs**
```yaml
platform-logs:
  type: volume
  persist: true
  mount:
    - /var/log/platform
  retention: 7 days
```

### Volume 4: **Metrics**
```yaml
prometheus-data:
  type: volume
  persist: true
  backup: true
  mount:
    - /prometheus
  retention: 30 days
```

### Volume 5: **Uploads/Documents**
```yaml
platform-uploads:
  type: volume
  persist: true
  backup: true
  mount:
    - /data/uploads
```

### Volume 6: **ML Models**
```yaml
ml-models:
  type: volume
  persist: true
  readonly: true
  mount:
    - /models
```

---

## 📋 Docker Compose Structure

```yaml
version: '3.8'

# 12 service containers
services:
  gateway:
    build: ./infrastructure/gateway
    ports: ["8000:8000"]
    depends_on: [platform-services, eventbus]

  platform-services:
    build: ./platform-services
    ports: ["8011-8027:8011-8027"]
    depends_on: [eventbus, redis]
    volumes:
      - platform-logs:/var/log
      - platform-uploads:/data/uploads

  intelligent-core:
    build: ./intelligent-core
    ports: ["8002:8002", "8028-8038:8028-8038"]
    depends_on: [eventbus, redis]
    volumes:
      - ml-models:/models:ro
      - platform-logs:/var/log

  expertise-center:
    build: ./intelligent-core/expertise
    ports: ["8029:8029", "8033:8033"]
    depends_on: [eventbus]

  eventbus:
    build: ./infrastructure/runtime/eventbus
    ports: ["8001:8001"]
    volumes:
      - eventbus-data:/data

  ai-office:
    build: ./infrastructure/AI-office-infrastructure
    ports: ["8055-8060:8055-8060"]
    depends_on: [eventbus]

  monitoring:
    build: ./infrastructure/observability
    ports: ["9090:9090", "8050:8050"]
    volumes:
      - prometheus-data:/prometheus
      - monitoring-logs:/var/log

  db-services:
    build: ./infrastructure/database-services
    ports: ["8051:8051"]
    environment:
      DATABASE_URL: ${DATABASE_URL}

  security:
    build: ./infrastructure/security
    ports: ["8081:8081", "8084:8084"]
    volumes:
      - secrets-data:/secrets

  runtime:
    build: ./infrastructure/runtime
    ports: ["8082:8082", "8085-8086:8085-8086"]
    depends_on: [redis]

  interfaces:
    build: ./interface
    ports: ["3000-3002:3000-3002"]
    depends_on: [gateway]

  integrations:
    build: ./infrastructure/integration
    ports: ["8087-8089:8087-8089"]
    depends_on: [eventbus]

# External services
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes:
      - redis-data:/data

# Volumes
volumes:
  redis-data:
  platform-logs:
  prometheus-data:
  platform-uploads:
  ml-models:
  eventbus-data:
  monitoring-logs:
  secrets-data:
```

---

## 🏗️ Dockerfile Templates

### Template 1: **Python FastAPI Service**

```dockerfile
# platform-services/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8012/health || exit 1

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports (8011-8027)
EXPOSE 8011 8012 8013 8014 8015 8016 8017 8018 8019 8020 8021 8022 8023 8024 8025 8026 8027

# Start command (supervisor runs all services)
CMD ["python", "start_all_services.py"]
```

### Template 2: **AI/ML Service**

```dockerfile
# intelligent-core/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies for ML
RUN apt-get update && apt-get install -y \
    gcc g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python ML dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy models (if bundled)
COPY models/ /models/

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

# Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /models
USER appuser

EXPOSE 8002 8028 8029 8030 8031 8032 8033 8034 8038

CMD ["python", "start_intelligent_core.py"]
```

### Template 3: **Node.js Frontend**

```dockerfile
# interface/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -q --spider http://localhost:3000 || exit 1

EXPOSE 3000 3001 3002

CMD ["nginx", "-g", "daemon off;"]
```

### Template 4: **Monitoring Stack**

```dockerfile
# infrastructure/observability/Dockerfile
FROM prom/prometheus:latest AS prometheus

FROM python:3.11-slim

WORKDIR /app

# Install Prometheus
COPY --from=prometheus /bin/prometheus /usr/local/bin/
COPY --from=prometheus /etc/prometheus /etc/prometheus

# Install Python monitoring services
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /prometheus && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /prometheus /app

USER appuser

EXPOSE 9090 8050 8052

# Supervisor to run both Prometheus and monitoring-backend
CMD ["supervisord", "-c", "/app/supervisord.conf"]
```

---

## 🚀 Railway Deployment Strategy

### railway.json (Project Config)

```json
{
  "version": 2,
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Service Group 1: **Core Platform** (Critical)
```yaml
# railway-core.yaml
services:
  gateway:
    source: infrastructure/gateway
    plan: pro  # $20/month
    replicas: 2
    resources:
      cpu: 1
      memory: 1GB

  platform-services:
    source: platform-services
    plan: pro
    replicas: 2
    resources:
      cpu: 2
      memory: 2GB
    env:
      DATABASE_URL: ${{secrets.DATABASE_URL}}
      REDIS_URL: ${{services.redis.connectionString}}

  eventbus:
    source: infrastructure/runtime/eventbus
    plan: pro
    replicas: 2
    resources:
      cpu: 1
      memory: 512MB
```

### Service Group 2: **AI/ML** (High Resources)
```yaml
# railway-ai.yaml
services:
  intelligent-core:
    source: intelligent-core
    plan: pro  # или hobby+
    replicas: 1
    resources:
      cpu: 4
      memory: 4GB
    env:
      ML_MODEL_PATH: /models
      EVENTBUS_URL: ${{services.eventbus.url}}
```

### Service Group 3: **Observability** (Low Priority)
```yaml
# railway-monitoring.yaml
services:
  monitoring:
    source: infrastructure/observability
    plan: hobby  # $5/month
    replicas: 1
    resources:
      cpu: 0.5
      memory: 512MB
    volumes:
      - prometheus-data:/prometheus
```

---

## 🔧 Build Scripts

### build_all.sh
```bash
#!/bin/bash
# Build all Docker images

set -e

echo "🏗️  Building all containers..."

# Core services
docker build -t bcm-platform/gateway:latest ./infrastructure/gateway
docker build -t bcm-platform/platform-services:latest ./platform-services
docker build -t bcm-platform/intelligent-core:latest ./intelligent-core
docker build -t bcm-platform/eventbus:latest ./infrastructure/runtime/eventbus

# Support services
docker build -t bcm-platform/monitoring:latest ./infrastructure/observability
docker build -t bcm-platform/security:latest ./infrastructure/security
docker build -t bcm-platform/interfaces:latest ./interface

echo "✅ All images built successfully!"

# Tag for Railway
echo "🏷️  Tagging for Railway..."
docker tag bcm-platform/gateway:latest registry.railway.app/bcm-platform/gateway:latest

echo "✅ Ready for deployment!"
```

### deploy_railway.sh
```bash
#!/bin/bash
# Deploy to Railway

set -e

echo "🚀 Deploying to Railway..."

# Login
railway login

# Deploy each service
railway up --service gateway
railway up --service platform-services
railway up --service intelligent-core
railway up --service eventbus

echo "✅ Deployment complete!"
```

---

## 📊 Resource Planning

### Production Resources:

| Container | CPU | Memory | Storage | Cost/month |
|-----------|-----|--------|---------|------------|
| Gateway | 1 | 1GB | - | $20 |
| Platform Services | 2 | 2GB | 10GB | $40 |
| Intelligent Core | 4 | 4GB | 20GB | $80 |
| Expertise Center | 2 | 2GB | 5GB | $40 |
| EventBus | 1 | 512MB | 5GB | $20 |
| AI Office | 1 | 1GB | - | $20 |
| Monitoring | 0.5 | 512MB | 10GB | $10 |
| DB Services | 0.5 | 512MB | - | $10 |
| Security | 1 | 512MB | 1GB | $20 |
| Runtime | 1 | 512MB | - | $20 |
| Interfaces | 0.5 | 256MB | - | $10 |
| Integrations | 0.5 | 256MB | - | $10 |
| **Total** | **15** | **13GB** | **51GB** | **$300** |

---

## 🎯 Next Steps

### Phase 1: Core Containers (Week 1)
- [ ] Create Dockerfiles для 12 групп
- [ ] docker-compose.yml для local dev
- [ ] Test local deployment
- [ ] CI/CD pipeline

### Phase 2: Railway Setup (Week 2)
- [ ] Railway project setup
- [ ] Secrets configuration
- [ ] Deploy core services
- [ ] Test production

### Phase 3: Optimization (Week 3)
- [ ] Multi-stage builds
- [ ] Image size optimization
- [ ] Health checks tuning
- [ ] Auto-scaling

### Phase 4: Monitoring (Week 4)
- [ ] Prometheus in container
- [ ] Grafana dashboards
- [ ] Alerts setup
- [ ] Log aggregation

---

**Prepared by:** DevOps Agent (8058) + Project Agent (8060)
**Status:** READY FOR IMPLEMENTATION
**Next:** Create Dockerfiles
