# DEPLOYMENT GUIDE v3.0 - Digital Twin Standalone
## Enhanced with AnyLogic Pypeline and 30 Simulation Experiments

**Version**: 3.0.0  
**Date**: August 16, 2025  
**Target Environments**: Development, Staging, Production  
**Container Platform**: Docker  
**Language**: English

---

## OVERVIEW

This deployment guide covers the enhanced Digital Twin Standalone system v3.0 with AnyLogic Pypeline integration, 30 simulation experiments, and ML/AI capabilities.

### Architecture Components

1. **Main Application**: Digital Twin server (Port 3000)
2. **External Adapters**: 4 containerized simulation engines
3. **Database**: Supabase PostgreSQL
4. **ML/AI Pipeline**: Integrated with AnyLogic Pypeline
5. **Infrastructure**: Load balancer, monitoring, caching

---

## SYSTEM REQUIREMENTS

### Minimum Requirements
| Component | Development | Staging | Production |
|-----------|-------------|---------|------------|
| **CPU** | 4 cores | 8 cores | 16 cores |
| **Memory** | 8 GB | 16 GB | 32 GB |
| **Storage** | 50 GB SSD | 100 GB SSD | 500 GB SSD |
| **Network** | 100 Mbps | 1 Gbps | 1 Gbps |

### Enhanced Requirements for AnyLogic
| Component | Additional Requirement | Reason |
|-----------|----------------------|--------|
| **Memory** | +4 GB minimum | ML model training and hybrid simulations |
| **CPU** | Multi-core recommended | Parallel simulation execution |
| **Storage** | +20 GB | ML models, simulation results storage |
| **Python** | 3.11+ with ML libraries | AnyLogic Pypeline integration |

---

## PRE-DEPLOYMENT SETUP

### 1. Environment Preparation

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. System Configuration

```bash
# Create deployment directory
mkdir -p /opt/digital-twin-v3
cd /opt/digital-twin-v3

# Clone repository
git clone https://github.com/your-org/digital-twin-standalone.git .

# Set permissions
sudo chown -R $USER:$USER /opt/digital-twin-v3
```

### 3. Environment Variables Setup

Create `.env` file:

```env
# Application Configuration
NODE_ENV=production
PORT=3000
API_VERSION=3.0.0

# Database Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# External Adapters Configuration
SIMPY_ADAPTER_URL=http://simpy:7001/run
MESA_ADAPTER_URL=http://mesa:7002/run
EPINOW2_ADAPTER_URL=http://epinow2:7003/run
ANYLOGIC_ADAPTER_URL=http://anylogic:7004/run

# AnyLogic Pypeline Configuration
ANYLOGIC_PYTHONPATH=/app/python_scripts
ANYLOGIC_ML_MODELS_PATH=/app/models
ANYLOGIC_TEMP_DIR=/tmp/anylogic
ANYLOGIC_MEMORY_LIMIT=4GB
ANYLOGIC_TIMEOUT=600

# ML/AI Configuration
TENSORFLOW_VERSION=2.16.0
PYTORCH_VERSION=2.3.0
ENABLE_GPU=false
ML_MODEL_STORAGE=/data/ml_models

# Security Configuration
JWT_SECRET=your_jwt_secret_256_bits_minimum
ENCRYPTION_KEY=your_encryption_key
API_RATE_LIMIT=100
SIMULATION_RATE_LIMIT=10

# Monitoring Configuration
LOG_LEVEL=info
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30
```

---

## DOCKER DEPLOYMENT

### 1. Main Docker Compose Configuration

Create `docker-compose.v3.yml`:

```yaml
version: '3.8'

services:
  # Main Digital Twin Application
  digital-twin:
    build: .
    image: digital-twin:v3.0.0
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
    env_file:
      - .env
    depends_on:
      - redis
      - simpy
      - mesa
      - epinow2
      - anylogic
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - digital-twin-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - digital-twin-network

  # External Simulation Adapters
  simpy:
    build: ./external-adapters/seh_adapters/simpy-adapter
    image: seh-simpy:latest
    ports:
      - "7001:7001"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    networks:
      - digital-twin-network

  mesa:
    build: ./external-adapters/seh_adapters/mesa-adapter
    image: seh-mesa:latest
    ports:
      - "7002:7002"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    networks:
      - digital-twin-network

  epinow2:
    build: ./external-adapters/seh_adapters/epinow2-adapter
    image: seh-epinow2:latest
    ports:
      - "7003:7003"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    networks:
      - digital-twin-network

  # AnyLogic Pypeline (Enhanced)
  anylogic:
    build: ./external-adapters/anylogic-adapter/docker
    image: anylogic-pypeline:latest
    ports:
      - "7004:7004"
    environment:
      - PYTHONUNBUFFERED=1
      - ML_MODELS_PATH=/app/python_scripts
      - ANYLOGIC_MEMORY_LIMIT=4GB
      - TENSORFLOW_FORCE_GPU_ALLOW_GROWTH=true
    volumes:
      - anylogic_models:/app/models
      - anylogic_temp:/tmp/anylogic
    restart: unless-stopped
    networks:
      - digital-twin-network
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

  # Load Balancer (Production)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - digital-twin
    restart: unless-stopped
    networks:
      - digital-twin-network

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped
    networks:
      - digital-twin-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - digital-twin-network

volumes:
  redis_data:
  anylogic_models:
  anylogic_temp:
  prometheus_data:
  grafana_data:

networks:
  digital-twin-network:
    driver: bridge
```

### 2. Enhanced Dockerfile for Main Application

```dockerfile
FROM node:18-alpine

# Install system dependencies for ML integration
RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    python3-dev

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp

# Set permissions
RUN chmod +x /app/scripts/*.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "run", "start:production"]
```

---

## DEPLOYMENT PROCEDURES

### 1. Development Environment

```bash
# Quick start for development
git clone https://github.com/your-org/digital-twin-standalone.git
cd digital-twin-standalone

# Install dependencies
npm install

# Setup environment
cp .env.example .env.development
# Edit .env.development with your configuration

# Start development servers
npm run dev:all

# Verify all 30 experiments
curl http://localhost:3000/api/impact/simulations/experiments
```

### 2. Staging Environment

```bash
# Deploy to staging
cd /opt/digital-twin-v3

# Build all images
docker-compose -f docker-compose.v3.yml build

# Start staging environment
docker-compose -f docker-compose.v3.yml up -d

# Verify deployment
./scripts/health-check.sh staging

# Run integration tests
./scripts/test-all-experiments.sh
```

### 3. Production Environment

```bash
# Production deployment with zero downtime
cd /opt/digital-twin-v3

# Pre-deployment checks
./scripts/pre-deployment-checks.sh

# Backup current state
./scripts/backup-production.sh

# Deploy new version
docker-compose -f docker-compose.v3.yml pull
docker-compose -f docker-compose.v3.yml up -d --no-deps digital-twin

# Verify health
./scripts/health-check.sh production

# Run smoke tests
./scripts/smoke-tests.sh

# Monitor for 10 minutes
./scripts/monitor-deployment.sh 600
```

---

## ANYLOGIC PYPELINE SETUP

### 1. AnyLogic Container Configuration

```dockerfile
# AnyLogic Pypeline Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python ML libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy AnyLogic integration code
COPY api_server/ ./api_server/
COPY anylogic-model/ ./anylogic-model/
COPY python_scripts/ ./python_scripts/

# Create directories for models and temp files
RUN mkdir -p /app/models /tmp/anylogic

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:7004/health || exit 1

EXPOSE 7004

# Start AnyLogic Pypeline server
CMD ["python", "api_server/app.py"]
```

### 2. ML Models Setup

```bash
# Setup ML models for AnyLogic
mkdir -p /opt/digital-twin-v3/ml-models

# Download pre-trained models (if available)
./scripts/download-ml-models.sh

# Or train models from scratch
docker exec anylogic python python_scripts/train_models.py
```

---

## MONITORING AND LOGGING

### 1. Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'digital-twin'
    static_configs:
      - targets: ['digital-twin:3000']
    metrics_path: '/metrics'

  - job_name: 'anylogic-pypeline'
    static_configs:
      - targets: ['anylogic:7004']
    metrics_path: '/metrics'

  - job_name: 'external-adapters'
    static_configs:
      - targets: 
        - 'simpy:7001'
        - 'mesa:7002'
        - 'epinow2:7003'
```

### 2. Grafana Dashboards

```bash
# Import pre-configured dashboards
curl -X POST \
  http://admin:admin123@localhost:3001/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/dashboards/digital-twin-v3.json
```

### 3. Log Aggregation

```yaml
# Add to docker-compose.v3.yml
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

---

## BACKUP AND RECOVERY

### 1. Database Backup

```bash
#!/bin/bash
# scripts/backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/digital-twin-v3"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup Supabase database
pg_dump $SUPABASE_CONNECTION_STRING > $BACKUP_DIR/database_$DATE.sql

# Backup ML models
tar -czf $BACKUP_DIR/ml_models_$DATE.tar.gz /app/models/

# Backup configuration
cp .env $BACKUP_DIR/env_$DATE.bak

echo "Backup completed: $BACKUP_DIR"
```

### 2. Restore Procedure

```bash
#!/bin/bash
# scripts/restore-database.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

# Stop services
docker-compose -f docker-compose.v3.yml stop

# Restore database
psql $SUPABASE_CONNECTION_STRING < $BACKUP_FILE

# Restore ML models
tar -xzf ml_models_*.tar.gz -C /

# Restart services
docker-compose -f docker-compose.v3.yml start

echo "Restore completed"
```

---

## SCALING AND PERFORMANCE

### 1. Horizontal Scaling

```yaml
# Production scaling configuration
services:
  digital-twin:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  anylogic:
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 6G
          cpus: '3.0'
```

### 2. Load Balancer Configuration

```nginx
# nginx.conf
upstream digital_twin_backend {
    server digital-twin:3000;
    # Add more servers for scaling
    # server digital-twin-2:3000;
    # server digital-twin-3:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://digital_twin_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/impact/simulations/run {
        proxy_pass http://digital_twin_backend;
        proxy_read_timeout 600s;  # Extended for long simulations
    }
}
```

---

## TROUBLESHOOTING

### 1. Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **AnyLogic Memory Error** | Out of memory during ML training | Increase memory limit, reduce model complexity |
| **Simulation Timeout** | Experiments timeout after 10 minutes | Check resource allocation, optimize models |
| **Adapter Connection Failed** | External adapters unreachable | Verify network connectivity, restart containers |
| **ML Model Training Failed** | Python errors in AnyLogic container | Check dependencies, validate input data |

### 2. Health Check Scripts

```bash
#!/bin/bash
# scripts/health-check.sh

echo "Checking Digital Twin v3.0 Health..."

# Main application
curl -f http://localhost:3000/api/health || echo "[ERROR] Main app failed"

# External adapters
curl -f http://localhost:7001/health || echo "[ERROR] SimPy failed"
curl -f http://localhost:7002/health || echo "[ERROR] Mesa failed"
curl -f http://localhost:7003/health || echo "[ERROR] EpiNow2 failed"
curl -f http://localhost:7004/health || echo "[ERROR] AnyLogic failed"

# Test 30 experiments
EXPERIMENT_COUNT=$(curl -s http://localhost:3000/api/impact/simulations/experiments | jq '.count')
if [ "$EXPERIMENT_COUNT" -eq 30 ]; then
    echo "[OK] All 30 experiments available"
else
    echo "[ERROR] Only $EXPERIMENT_COUNT experiments available"
fi

echo "Health check completed"
```

---

## SECURITY CONSIDERATIONS

### 1. Container Security

```yaml
# Security-hardened configuration
services:
  digital-twin:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp
```

### 2. Network Security

```bash
# Firewall configuration
sudo ufw allow 22/tcp          # SSH
sudo ufw allow 80/tcp          # HTTP
sudo ufw allow 443/tcp         # HTTPS
sudo ufw allow 3000/tcp        # Digital Twin (internal)
sudo ufw deny 7001:7004/tcp    # Block external adapter ports
sudo ufw enable
```

---

## MAINTENANCE PROCEDURES

### 1. Regular Maintenance Tasks

```bash
#!/bin/bash
# scripts/weekly-maintenance.sh

# Update ML models
docker exec anylogic python python_scripts/retrain_models.py

# Clean up old simulation results
docker exec digital-twin npm run cleanup:old-simulations

# Update container images
docker-compose -f docker-compose.v3.yml pull

# Restart services if needed
docker-compose -f docker-compose.v3.yml restart

# Run health checks
./scripts/health-check.sh

echo "Weekly maintenance completed"
```

### 2. Performance Optimization

```bash
#!/bin/bash
# scripts/optimize-performance.sh

# Clear Redis cache
docker exec redis redis-cli FLUSHALL

# Optimize AnyLogic models
docker exec anylogic python python_scripts/optimize_models.py

# Clean temporary files
docker exec digital-twin npm run cleanup:temp

# Restart for fresh state
docker-compose -f docker-compose.v3.yml restart digital-twin anylogic

echo "Performance optimization completed"
```

---

## APPENDICES

### Appendix A: Port Mapping
| Service | Port | Purpose |
|---------|------|---------|
| Digital Twin | 3000 | Main application |
| SimPy | 7001 | Discrete event simulation |
| Mesa | 7002 | Agent-based modeling |
| EpiNow2 | 7003 | Epidemiological modeling |
| AnyLogic | 7004 | Hybrid simulation with ML |
| Redis | 6379 | Caching |
| Nginx | 80/443 | Load balancer |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Monitoring dashboard |

### Appendix B: Environment Variables Reference
Complete list of environment variables with descriptions and examples.

### Appendix C: API Endpoints Quick Reference
Quick reference for all 30 experiment endpoints and their parameters.

---

**Document Information:**
- Version: 3.0.0
- Last Updated: August 16, 2025
- Maintainer: DevOps and Development Teams
- Next Review: November 16, 2025