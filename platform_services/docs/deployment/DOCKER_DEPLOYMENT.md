# Docker Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the BCM Platform using Docker and Docker Compose. Docker containerization ensures consistent deployments across development, staging, and production environments.

## Prerequisites

### Docker Installation

**Ubuntu/Debian:**
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

**RHEL/CentOS:**
```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker --version
```

**macOS:**
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Or use Homebrew
brew install --cask docker
```

### System Configuration

```bash
# Add user to docker group (avoid using sudo)
sudo usermod -aG docker $USER
newgrp docker

# Configure Docker daemon
sudo tee /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF

# Restart Docker
sudo systemctl restart docker
```

## Production Docker Compose Configuration

### Enhanced docker-compose.yml

Create a production-optimized `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database with production settings
  postgres:
    image: postgres:15-alpine
    container_name: bcm-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-bcm_platform}
      POSTGRES_USER: ${POSTGRES_USER:-bcm_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=en_US.UTF-8"
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "127.0.0.1:5432:5432"  # Bind to localhost only
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-databases.sh:/docker-entrypoint-initdb.d/init-databases.sh:ro
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-bcm_user} -d ${POSTGRES_DB:-bcm_platform}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - bcm-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    security_opt:
      - no-new-privileges:true
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Redis Cache with persistence
  redis:
    image: redis:7-alpine
    container_name: bcm-redis
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD:?REDIS_PASSWORD required}
      --maxmemory 1gb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
      --appendonly yes
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 20s
    networks:
      - bcm-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1.5G
        reservations:
          cpus: '0.5'
          memory: 512M
    security_opt:
      - no-new-privileges:true
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Planning Service
  planning-service:
    image: ${DOCKER_REGISTRY:-bcm}/planning-service:${VERSION:-latest}
    build:
      context: ./planning_service
      dockerfile: Dockerfile
      args:
        BUILD_DATE: ${BUILD_DATE}
        VCS_REF: ${VCS_REF}
        VERSION: ${VERSION:-1.0.0}
    container_name: planning-service
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-bcm_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-bcm_platform}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      EVENTBUS_URL: ${EVENTBUS_URL:-http://eventbus:8001}
      SERVICE_NAME: planning_service
      SERVICE_PORT: 8011
      JWT_PUBLIC_KEY: ${JWT_PUBLIC_KEY:?JWT_PUBLIC_KEY required}
      JWT_ALGORITHM: ${JWT_ALGORITHM:-RS256}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      ENVIRONMENT: ${ENVIRONMENT:-production}
    ports:
      - "127.0.0.1:8011:8011"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8011/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - bcm-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  # Plans Service
  plans-service:
    image: ${DOCKER_REGISTRY:-bcm}/plans-service:${VERSION:-latest}
    build:
      context: ./plans_service
      dockerfile: Dockerfile
      args:
        BUILD_DATE: ${BUILD_DATE}
        VCS_REF: ${VCS_REF}
        VERSION: ${VERSION:-1.0.0}
    container_name: plans-service
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-bcm_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-bcm_platform}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/1
      EVENTBUS_URL: ${EVENTBUS_URL:-http://eventbus:8001}
      SERVICE_NAME: plans_service
      SERVICE_PORT: 8023
      JWT_PUBLIC_KEY: ${JWT_PUBLIC_KEY}
      JWT_ALGORITHM: ${JWT_ALGORITHM:-RS256}
      PLANNING_SERVICE_URL: http://planning-service:8011
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      ENVIRONMENT: ${ENVIRONMENT:-production}
    ports:
      - "127.0.0.1:8023:8023"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      planning-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8023/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - bcm-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  # BIA Service
  bia-service:
    image: ${DOCKER_REGISTRY:-bcm}/bia-service:${VERSION:-latest}
    build:
      context: ./bia-service
      dockerfile: Dockerfile
    container_name: bia-service
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-bcm_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-bcm_platform}
      JWT_SECRET: ${JWT_SECRET:?JWT_SECRET required}
      SERVICE_PORT: 8012
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    ports:
      - "127.0.0.1:8012:8012"
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8012/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - bcm-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    security_opt:
      - no-new-privileges:true
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  # Compliance Service
  compliance-service:
    image: ${DOCKER_REGISTRY:-bcm}/compliance-service:${VERSION:-latest}
    build:
      context: ./compliance-service
      dockerfile: Dockerfile
    container_name: compliance-service
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-bcm_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-bcm_platform}
      JWT_SECRET: ${JWT_SECRET}
      SERVICE_PORT: 8014
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    ports:
      - "127.0.0.1:8014:8014"
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8014/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - bcm-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    security_opt:
      - no-new-privileges:true
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: bcm-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "127.0.0.1:9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./monitoring/alerts:/etc/prometheus/alerts:ro
      - prometheus_data:/prometheus
    networks:
      - bcm-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    security_opt:
      - no-new-privileges:true
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: bcm-grafana
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER:-admin}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD:?GRAFANA_ADMIN_PASSWORD required}
      GF_USERS_ALLOW_SIGN_UP: 'false'
      GF_SERVER_ROOT_URL: ${GRAFANA_ROOT_URL:-http://localhost:3000}
      GF_SMTP_ENABLED: ${SMTP_ENABLED:-false}
      GF_SMTP_HOST: ${SMTP_HOST}
      GF_SMTP_USER: ${SMTP_USERNAME}
      GF_SMTP_PASSWORD: ${SMTP_PASSWORD}
    ports:
      - "127.0.0.1:3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    depends_on:
      - prometheus
    networks:
      - bcm-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    security_opt:
      - no-new-privileges:true
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  bcm-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
```

## Image Building and Management

### Building Images

```bash
# Set version and build metadata
export VERSION=1.0.0
export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
export VCS_REF=$(git rev-parse --short HEAD)

# Build all images
docker compose -f docker-compose.prod.yml build

# Build specific service
docker compose -f docker-compose.prod.yml build planning-service

# Build with no cache (clean build)
docker compose -f docker-compose.prod.yml build --no-cache

# Build with parallel builds
docker compose -f docker-compose.prod.yml build --parallel
```

### Tagging Images

```bash
# Tag for version
docker tag bcm/planning-service:latest bcm/planning-service:1.0.0
docker tag bcm/planning-service:latest bcm/planning-service:1.0
docker tag bcm/planning-service:latest bcm/planning-service:stable

# Tag for registry
docker tag bcm/planning-service:1.0.0 registry.yourdomain.com/bcm/planning-service:1.0.0
```

### Pushing to Registry

```bash
# Login to registry
docker login registry.yourdomain.com

# Push images
docker push registry.yourdomain.com/bcm/planning-service:1.0.0
docker push registry.yourdomain.com/bcm/plans-service:1.0.0
docker push registry.yourdomain.com/bcm/bia-service:1.0.0
docker push registry.yourdomain.com/bcm/compliance-service:1.0.0

# Or push all with script
for service in planning-service plans-service bia-service compliance-service; do
    docker push registry.yourdomain.com/bcm/$service:1.0.0
done
```

## Container Orchestration

### Starting Services

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Start specific services
docker compose -f docker-compose.prod.yml up -d postgres redis

# Start with build
docker compose -f docker-compose.prod.yml up -d --build

# Scale service (if stateless)
docker compose -f docker-compose.prod.yml up -d --scale planning-service=3
```

### Stopping and Removing

```bash
# Stop all services
docker compose -f docker-compose.prod.yml stop

# Stop specific service
docker compose -f docker-compose.prod.yml stop planning-service

# Remove containers (keeps volumes)
docker compose -f docker-compose.prod.yml down

# Remove containers and volumes
docker compose -f docker-compose.prod.yml down -v

# Remove containers, volumes, and images
docker compose -f docker-compose.prod.yml down -v --rmi all
```

### Service Management

```bash
# Restart service
docker compose -f docker-compose.prod.yml restart planning-service

# View logs
docker compose -f docker-compose.prod.yml logs -f planning-service

# View logs for all services
docker compose -f docker-compose.prod.yml logs -f

# Execute command in container
docker compose -f docker-compose.prod.yml exec planning-service sh

# View service status
docker compose -f docker-compose.prod.yml ps

# View resource usage
docker stats
```

## Volume Management

### Data Persistence

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect platform-services_postgres_data

# Backup volume
docker run --rm -v platform-services_postgres_data:/data -v $(pwd)/backups:/backup \
    alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data

# Restore volume
docker run --rm -v platform-services_postgres_data:/data -v $(pwd)/backups:/backup \
    alpine tar xzf /backup/postgres_data_20241003.tar.gz -C /

# Remove unused volumes
docker volume prune
```

### Volume Drivers

For production, consider using volume drivers for distributed storage:

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=nfs-server.local,rw
      device: ":/path/to/postgres"
```

## Network Configuration

### Custom Networks

```yaml
networks:
  bcm-network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1

  external-network:
    external: true
    name: production-network
```

### Network Security

```bash
# Inspect network
docker network inspect bcm-network

# Connect container to network
docker network connect bcm-network my-container

# Disconnect container
docker network disconnect bcm-network my-container
```

## Resource Limits

### CPU and Memory Limits

Set in docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Maximum 2 CPU cores
      memory: 2G       # Maximum 2GB RAM
    reservations:
      cpus: '1.0'      # Reserve 1 CPU core
      memory: 1G       # Reserve 1GB RAM
```

### Monitoring Resources

```bash
# Real-time stats
docker stats

# Detailed container info
docker inspect planning-service | jq '.[0].HostConfig.Memory'

# Check resource usage over time
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## Health Checks

### Container Health

All services include health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8011/health"]
  interval: 30s      # Check every 30 seconds
  timeout: 10s       # Timeout after 10 seconds
  retries: 3         # Fail after 3 retries
  start_period: 60s  # Grace period on startup
```

### Health Check Script

```bash
#!/bin/bash
# check_health.sh

for container in planning-service plans-service bia-service compliance-service; do
    health=$(docker inspect --format='{{.State.Health.Status}}' $container)
    if [ "$health" != "healthy" ]; then
        echo "UNHEALTHY: $container is $health"
        docker logs --tail 50 $container
    else
        echo "HEALTHY: $container"
    fi
done
```

## Log Aggregation

### Centralized Logging

**Using ELK Stack:**

```yaml
# Add to docker-compose.prod.yml
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - bcm-network

  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    volumes:
      - ./monitoring/logstash/pipeline:/usr/share/logstash/pipeline:ro
    depends_on:
      - elasticsearch
    networks:
      - bcm-network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - bcm-network
```

**Log Collection:**

```bash
# Collect logs to JSON
docker logs planning-service --since 1h 2>&1 | \
    jq -R 'fromjson? // {message: .}' > planning_logs.json

# Stream logs to file
docker compose -f docker-compose.prod.yml logs -f > all_services.log
```

## Docker Security Best Practices

### Image Security

```dockerfile
# Use specific versions (not 'latest')
FROM python:3.11.5-slim

# Run as non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Use multi-stage builds
FROM python:3.11 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
CMD ["python", "app.py"]
```

### Runtime Security

```yaml
security_opt:
  - no-new-privileges:true  # Prevent privilege escalation
  - seccomp:unconfined      # Or use custom seccomp profile

read_only: true             # Read-only root filesystem
tmpfs:
  - /tmp                    # Allow writes to /tmp only

cap_drop:
  - ALL                     # Drop all capabilities
cap_add:
  - NET_BIND_SERVICE        # Add only necessary capabilities
```

### Secrets Management

```bash
# Create secret
echo "my_secret_password" | docker secret create postgres_password -

# Use in compose (Swarm mode)
services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password

secrets:
  postgres_password:
    external: true
```

## Production Deployment Workflow

### Complete Deployment

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting BCM Platform deployment..."

# 1. Pull latest code
git pull origin main

# 2. Build images
export VERSION=$(git describe --tags --always)
export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
export VCS_REF=$(git rev-parse --short HEAD)

docker compose -f docker-compose.prod.yml build

# 3. Stop old containers
docker compose -f docker-compose.prod.yml down

# 4. Start infrastructure services
docker compose -f docker-compose.prod.yml up -d postgres redis

# Wait for health checks
sleep 30

# 5. Run migrations (if needed)
docker compose -f docker-compose.prod.yml run --rm planning-service alembic upgrade head

# 6. Start application services
docker compose -f docker-compose.prod.yml up -d

# 7. Verify deployment
sleep 30
./docs/deployment/scripts/health_check.sh

echo "Deployment complete!"
```

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker logs planning-service

# Check events
docker events --since 1h

# Inspect container
docker inspect planning-service
```

**Port conflicts:**
```bash
# Find process using port
sudo lsof -i :8011
sudo netstat -tuln | grep 8011

# Kill process
sudo kill -9 <PID>
```

**Out of disk space:**
```bash
# Clean up unused resources
docker system prune -a --volumes

# Check disk usage
docker system df

# Remove specific items
docker volume rm $(docker volume ls -qf dangling=true)
docker image prune -a
```

## Related Documentation

- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Environment Configuration](./ENVIRONMENT_CONFIGURATION.md)
- [Kubernetes Deployment](./KUBERNETES_DEPLOYMENT.md)
- [Security Guide](./SECURITY_GUIDE.md)

---

**Last Updated:** 2024-10-03
**Document Owner:** Platform Engineering Team
