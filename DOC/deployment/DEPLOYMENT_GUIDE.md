# Production Deployment Guide

**Document Type:** Deployment and Operations Guide
**Target Audience:** DevOps Engineers, System Administrators, Platform Operators
**Purpose:** Production deployment, configuration, and operations
**Version:** 1.0.0
**Last Updated:** 2025-10-09

---

## Overview

This guide provides comprehensive instructions for deploying AI-Platform-ISO to production environments. It covers infrastructure provisioning, service deployment, security hardening, monitoring configuration, and operational procedures.

**Deployment Options:**
- Cloud deployment (AWS, Azure, GCP)
- On-premises deployment
- Hybrid deployment
- Multi-region deployment for high availability

**Estimated Deployment Time:** 4-8 hours (depending on infrastructure complexity)

---

## Table of Contents

1. [Pre-Deployment Planning](#pre-deployment-planning)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Security Configuration](#security-configuration)
4. [Database Setup](#database-setup)
5. [Service Deployment](#service-deployment)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [High Availability Configuration](#high-availability-configuration)
8. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
9. [Performance Tuning](#performance-tuning)
10. [Operations and Maintenance](#operations-and-maintenance)

---

## Pre-Deployment Planning

### Capacity Planning

**Estimate Resource Requirements:**

**Small Deployment** (1-100 organizations, 500-1000 users)
- Compute: 8 vCPUs, 32 GB RAM
- Storage: 500 GB SSD
- Database: PostgreSQL (2 vCPU, 8 GB RAM, 100 GB storage)
- Estimated cost: USD 500-1000/month

**Medium Deployment** (100-500 organizations, 5000-10000 users)
- Compute: 32 vCPUs, 128 GB RAM (distributed across services)
- Storage: 2 TB SSD
- Database: PostgreSQL (8 vCPU, 32 GB RAM, 500 GB storage)
- Estimated cost: USD 2000-4000/month

**Large Deployment** (500+ organizations, 10000+ users)
- Compute: 64+ vCPUs, 256+ GB RAM (Kubernetes cluster)
- Storage: 5+ TB SSD
- Database: PostgreSQL (16+ vCPU, 64+ GB RAM, 1+ TB storage)
- Estimated cost: USD 5000-10000+/month

### Network Architecture

**Required Network Segments:**

1. **Public Zone**
   - API Gateway (HTTPS 443)
   - Web Application (HTTPS 443)
   - Load Balancer

2. **Application Zone** (Private)
   - Platform services
   - Intelligent core services
   - Application servers

3. **Data Zone** (Private)
   - PostgreSQL database
   - Redis cache
   - Vector database (Qdrant)

4. **Management Zone** (Restricted)
   - Monitoring (Prometheus, Grafana)
   - Logging infrastructure
   - Bastion hosts

### Compliance Requirements

**Security and Compliance:**
- SOC 2 Type II compliance
- GDPR compliance (for EU customers)
- ISO 27001 alignment
- Industry-specific requirements (HIPAA, FedRAMP, etc.)

**Data Residency:**
- Identify data residency requirements
- Plan multi-region deployment if needed
- Configure data sovereignty controls

---

## Infrastructure Requirements

### Cloud Infrastructure (AWS Example)

**Compute Resources:**

```yaml
# EC2 Instances or ECS/EKS for containerized deployment

API Gateway:
  Instance Type: t3.large (2 vCPU, 8 GB)
  Count: 2 (minimum for HA)
  Auto-scaling: Yes (2-10 instances)

Platform Services:
  Instance Type: t3.xlarge (4 vCPU, 16 GB)
  Count: 3 (minimum for HA)
  Auto-scaling: Yes (3-20 instances)

Intelligent Core:
  Instance Type: c5.2xlarge (8 vCPU, 16 GB)
  Count: 2 (minimum for HA)
  Auto-scaling: Yes (2-10 instances)
```

**Database:**

```yaml
Amazon RDS PostgreSQL:
  Instance Class: db.r5.2xlarge (8 vCPU, 64 GB)
  Storage: 500 GB GP3 SSD (min), auto-scaling enabled
  Multi-AZ: Yes (required for production)
  Backup Retention: 30 days
  Read Replicas: 2 (for read-heavy workloads)

Amazon ElastiCache Redis:
  Node Type: cache.r5.xlarge (4 vCPU, 26 GB)
  Number of Nodes: 3 (cluster mode enabled)
  Backup: Daily snapshots
```

**Storage:**

```yaml
Amazon S3:
  Bucket: ai-platform-iso-documents
  Versioning: Enabled
  Encryption: AES-256 (server-side)
  Lifecycle: Transition to Glacier after 90 days

Amazon EFS (for shared storage):
  Performance Mode: General Purpose
  Throughput Mode: Bursting
  Encryption: Enabled
```

**Networking:**

```yaml
VPC Configuration:
  CIDR: 10.0.0.0/16

Subnets:
  Public Subnets: 10.0.1.0/24, 10.0.2.0/24 (Multi-AZ)
  Private App Subnets: 10.0.10.0/24, 10.0.11.0/24 (Multi-AZ)
  Private Data Subnets: 10.0.20.0/24, 10.0.21.0/24 (Multi-AZ)

Load Balancer:
  Type: Application Load Balancer (ALB)
  Scheme: Internet-facing
  SSL/TLS: ACM certificate

NAT Gateway:
  Count: 2 (one per AZ for HA)
```

### Kubernetes Deployment (Recommended for Scale)

**Cluster Configuration:**

```yaml
# Amazon EKS / Azure AKS / Google GKE

Kubernetes Version: 1.28+

Node Pools:

  System Pool:
    Machine Type: t3.large
    Min Nodes: 2
    Max Nodes: 5
    Purpose: System components, monitoring

  Application Pool:
    Machine Type: t3.xlarge
    Min Nodes: 3
    Max Nodes: 20
    Purpose: Platform services
    Autoscaling: Enabled (CPU > 70%)

  AI Workload Pool:
    Machine Type: c5.2xlarge
    Min Nodes: 2
    Max Nodes: 10
    Purpose: AI Foundation, ML workloads
    Autoscaling: Enabled (CPU > 60%)
```

**Kubernetes Resources:**

```yaml
# Resource requests and limits per service

API Gateway:
  requests:
    cpu: "500m"
    memory: "1Gi"
  limits:
    cpu: "2000m"
    memory: "4Gi"
  replicas: 3

BIA Service:
  requests:
    cpu: "1000m"
    memory: "2Gi"
  limits:
    cpu: "4000m"
    memory: "8Gi"
  replicas: 3

AI Foundation:
  requests:
    cpu: "2000m"
    memory: "4Gi"
  limits:
    cpu: "8000m"
    memory: "16Gi"
  replicas: 2
```

---

## Security Configuration

### SSL/TLS Configuration

**Certificate Management:**

```bash
# Using Let's Encrypt (certbot)
sudo certbot certonly --standalone -d api.your-domain.com

# Or use AWS Certificate Manager (ACM)
aws acm request-certificate \
  --domain-name api.your-domain.com \
  --validation-method DNS \
  --subject-alternative-names "*.your-domain.com"

# Configure ALB to use certificate
# Update Target Group with HTTPS listener on port 443
```

**TLS Configuration (Minimum TLS 1.2):**

```nginx
# Nginx configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### Secrets Management

**AWS Secrets Manager:**

```bash
# Store API keys
aws secretsmanager create-secret \
  --name /ai-platform/production/anthropic-api-key \
  --secret-string "sk-ant-api03-xxxxx"

aws secretsmanager create-secret \
  --name /ai-platform/production/jwt-secret \
  --secret-string "$(openssl rand -base64 32)"

# Retrieve in application
aws secretsmanager get-secret-value \
  --secret-id /ai-platform/production/anthropic-api-key \
  --query SecretString --output text
```

**HashiCorp Vault (Alternative):**

```bash
# Enable KV secrets engine
vault secrets enable -path=ai-platform kv-v2

# Store secrets
vault kv put ai-platform/production/api-keys \
  anthropic_key="sk-ant-api03-xxxxx" \
  openai_key="sk-xxxxx"

# Grant policy to application
vault policy write ai-platform-app - <<EOF
path "ai-platform/data/production/*" {
  capabilities = ["read"]
}
EOF
```

### Network Security

**Security Groups (AWS) / Network Security Groups (Azure):**

```yaml
# API Gateway Security Group
Inbound Rules:
  - Port 443: 0.0.0.0/0 (HTTPS from internet)
  - Port 8000: Load Balancer SG (internal API)

Outbound Rules:
  - All traffic: 0.0.0.0/0

# Application Security Group
Inbound Rules:
  - Port 8001-8020: API Gateway SG
  - Port 22: Bastion SG (SSH)

Outbound Rules:
  - Port 5432: Database SG (PostgreSQL)
  - Port 6379: Redis SG
  - Port 443: 0.0.0.0/0 (outbound HTTPS)

# Database Security Group
Inbound Rules:
  - Port 5432: Application SG only

Outbound Rules:
  - None (or specific backup destinations)
```

**Web Application Firewall (WAF):**

```yaml
# AWS WAF rules
Rate Limiting:
  - Limit: 2000 requests per 5 minutes per IP

SQL Injection Protection:
  - AWS Managed Rule: SQLiMatchSet

XSS Protection:
  - AWS Managed Rule: XssMatchSet

Geographic Restrictions:
  - Allow: Specific countries (as needed)
  - Block: High-risk countries
```

### Application Security

**Authentication Configuration:**

```yaml
# .env.production
JWT_SECRET=<strong-random-string>  # Use Secrets Manager
JWT_ALGORITHM=RS256  # Use asymmetric keys for production
JWT_EXPIRATION_HOURS=1  # Shorter expiration
REFRESH_TOKEN_EXPIRATION_DAYS=30

# Enable MFA
MFA_ENABLED=true
MFA_METHODS=totp,sms

# Password policy
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true
PASSWORD_EXPIRATION_DAYS=90
```

**API Security:**

```yaml
# Rate limiting (per endpoint)
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# CORS configuration
CORS_ALLOWED_ORIGINS=https://app.your-domain.com,https://admin.your-domain.com
CORS_ALLOW_CREDENTIALS=true

# API key rotation
API_KEY_ROTATION_DAYS=90
```

---

## Database Setup

### PostgreSQL Configuration

**Production Database Setup:**

```sql
-- Create dedicated database
CREATE DATABASE ai_platform_prod;

-- Create application user
CREATE USER ai_platform_app WITH ENCRYPTED PASSWORD 'strong-password';

-- Grant privileges
GRANT CONNECT ON DATABASE ai_platform_prod TO ai_platform_app;
GRANT USAGE ON SCHEMA public TO ai_platform_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_platform_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_platform_app;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

**Performance Tuning:**

```ini
# postgresql.conf (for 64GB RAM server)

max_connections = 200
shared_buffers = 16GB
effective_cache_size = 48GB
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200  # For SSD
work_mem = 41MB  # (2GB / max_connections * 2)
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

**Backup Configuration:**

```bash
# Automated daily backups
0 2 * * * /usr/bin/pg_dump -U postgres ai_platform_prod | gzip > /backups/ai_platform_$(date +\%Y\%m\%d).sql.gz

# Weekly full backup with point-in-time recovery
0 3 * * 0 /usr/bin/pg_basebackup -D /backups/base_$(date +\%Y\%m\%d) -Ft -z -P

# Backup retention (delete backups older than 30 days)
find /backups -type f -mtime +30 -delete

# Test restore monthly
0 4 1 * * bash /scripts/test_restore.sh
```

### Redis Configuration

**Production Redis Setup:**

```ini
# redis.conf

# Network
bind 0.0.0.0
protected-mode yes
requirepass strong-redis-password
port 6379

# Memory
maxmemory 4gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfilename "appendonly.aof"

# Security
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 60
```

**Redis Cluster (for High Availability):**

```bash
# Create 6-node cluster (3 masters, 3 replicas)
redis-cli --cluster create \
  10.0.10.11:6379 \
  10.0.10.12:6379 \
  10.0.10.13:6379 \
  10.0.11.11:6379 \
  10.0.11.12:6379 \
  10.0.11.13:6379 \
  --cluster-replicas 1
```

---

## Service Deployment

### Deployment Order

Services must be deployed in the following order to satisfy dependencies:

```
1. Infrastructure Layer
   ├── PostgreSQL (external: RDS/Supabase)
   ├── Redis (external: ElastiCache or self-hosted cluster)
   └── Qdrant (external: Qdrant Cloud)

2. Foundation Services
   ├── EventBus
   ├── Service Discovery
   └── API Gateway (without routing initially)

3. Intelligent Core
   ├── AI Foundation
   ├── Workflow Engine
   ├── Expertise Center
   └── Learning System

4. Platform Services (parallel deployment possible)
   ├── BIA Service
   ├── Risk Service
   ├── Compliance Service
   ├── Planning Service
   └── Other services

5. Monitoring and Observability
   ├── Prometheus
   ├── Grafana
   └── Alert Manager

6. API Gateway (full routing enabled)
```

### Docker Compose Production Deployment

**Production docker-compose.yml:**

```yaml
version: '3.8'

services:
  api-gateway:
    image: ai-platform-iso/api-gateway:1.0.0
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  bia-service:
    image: ai-platform-iso/bia-service:1.0.0
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '1'
          memory: 2G
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Additional services...
```

### Kubernetes Deployment

**Deployment Manifests:**

```yaml
# api-gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: ai-platform-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
        version: v1.0.0
    spec:
      containers:
      - name: api-gateway
        image: ai-platform-iso/api-gateway:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ai-platform-secrets
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: ai-platform-secrets
              key: jwt-secret
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: ai-platform-prod
spec:
  selector:
    app: api-gateway
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Secrets Management:**

```yaml
# secrets.yaml (use with caution, better to use External Secrets Operator)
apiVersion: v1
kind: Secret
metadata:
  name: ai-platform-secrets
  namespace: ai-platform-prod
type: Opaque
stringData:
  database-url: postgresql://user:password@host:5432/database
  jwt-secret: your-jwt-secret
  anthropic-api-key: sk-ant-api03-xxxxx
```

**ConfigMap:**

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-platform-config
  namespace: ai-platform-prod
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  RATE_LIMIT_REQUESTS: "100"
  RATE_LIMIT_WINDOW_SECONDS: "60"
```

### Deployment Commands

```bash
# Docker Compose deployment
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes deployment
kubectl create namespace ai-platform-prod

# Apply secrets (use vault or external secrets in production)
kubectl apply -f k8s/secrets.yaml

# Apply configmaps
kubectl apply -f k8s/configmap.yaml

# Deploy services
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress/

# Verify deployment
kubectl get pods -n ai-platform-prod
kubectl get svc -n ai-platform-prod

# Check logs
kubectl logs -f deployment/api-gateway -n ai-platform-prod
```

---

## Monitoring and Observability

### Prometheus Configuration

**prometheus.yml:**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'ai-platform-prod'
    environment: 'production'

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'

  - job_name: 'bia-service'
    static_configs:
      - targets: ['bia-service:8001']

  - job_name: 'ai-foundation'
    static_configs:
      - targets: ['ai-foundation:8020']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'
```

**Alert Rules:**

```yaml
# /etc/prometheus/rules/platform-alerts.yml
groups:
  - name: platform_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: ServiceDown
        expr: up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"

      - alert: HighCPUUsage
        expr: process_cpu_usage > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.job }}"

      - alert: HighMemoryUsage
        expr: process_memory_usage_bytes / process_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: warning

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends > 180
        for: 5m
        labels:
          severity: warning
```

### Grafana Dashboards

**Configure Data Sources:**

```bash
# Add Prometheus data source via API
curl -X POST http://admin:admin@localhost:3001/api/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }'
```

**Import Pre-built Dashboards:**

- Platform Overview Dashboard (ID: custom-1000)
- Service Metrics Dashboard (ID: custom-1001)
- Database Performance (ID: custom-1002)
- AI Model Performance (ID: custom-1003)

### Logging Configuration

**Centralized Logging with ELK Stack:**

```yaml
# filebeat.yml
filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
          - logs_path:
              logs_path: "/var/lib/docker/containers/"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "ai-platform-logs-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"
```

---

## High Availability Configuration

### Load Balancer Setup

**AWS Application Load Balancer:**

```bash
# Create target group
aws elbv2 create-target-group \
  --name ai-platform-api-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx \
  --health-check-path /health \
  --health-check-interval-seconds 30

# Create load balancer
aws elbv2 create-load-balancer \
  --name ai-platform-alb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx \
  --scheme internet-facing

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

### Database Replication

**PostgreSQL Multi-AZ (AWS RDS):**

```bash
# Enable Multi-AZ
aws rds modify-db-instance \
  --db-instance-identifier ai-platform-prod \
  --multi-az \
  --apply-immediately

# Create read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier ai-platform-prod-replica-1 \
  --source-db-instance-identifier ai-platform-prod \
  --db-instance-class db.r5.xlarge
```

### Auto-Scaling Configuration

**Kubernetes Horizontal Pod Autoscaler:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: ai-platform-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
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

---

## Backup and Disaster Recovery

### Backup Strategy

**Database Backups:**

```bash
# Automated daily backups (RDS)
aws rds modify-db-instance \
  --db-instance-identifier ai-platform-prod \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00"

# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier ai-platform-prod \
  --db-snapshot-identifier ai-platform-manual-$(date +%Y%m%d)
```

**Application Data Backups:**

```bash
# Backup documents and files to S3
aws s3 sync /data/documents s3://ai-platform-backups/documents/ \
  --exclude "*.tmp" \
  --storage-class STANDARD_IA

# Backup configuration
aws s3 cp /etc/ai-platform/ s3://ai-platform-backups/config/ --recursive
```

### Disaster Recovery Plan

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 1 hour

**Recovery Procedures:**

```bash
# 1. Restore database from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-platform-prod-restored \
  --db-snapshot-identifier ai-platform-snapshot-20251009

# 2. Restore application data
aws s3 sync s3://ai-platform-backups/documents/ /data/documents/

# 3. Update DNS to point to recovery environment
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456 \
  --change-batch file://dns-change.json

# 4. Verify all services
kubectl get pods -n ai-platform-prod
curl https://api.your-domain.com/health
```

---

## Performance Tuning

### Application Optimization

**Caching Strategy:**

```python
# Configure Redis caching
CACHE_CONFIG = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {"max_connections": 50}
        },
        "KEY_PREFIX": "ai_platform",
        "TIMEOUT": 3600  # 1 hour default
    }
}
```

**Database Connection Pooling:**

```python
# SQLAlchemy connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Database Query Optimization

```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_bia_organization_id ON bia_analyses(organization_id);
CREATE INDEX idx_risk_status ON risk_assessments(status, created_at DESC);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM bia_analyses WHERE organization_id = 'org-123';

-- Update statistics
ANALYZE bia_analyses;
VACUUM ANALYZE;
```

---

## Operations and Maintenance

### Health Monitoring

**Automated Health Checks:**

```bash
#!/bin/bash
# health_check.sh

services=(
  "http://api-gateway:8000/health"
  "http://bia-service:8001/health"
  "http://ai-foundation:8020/health"
)

for service in "${services[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" $service)
  if [ $status -ne 200 ]; then
    echo "ALERT: Service $service returned $status"
    # Send alert via PagerDuty, Slack, etc.
  fi
done
```

### Maintenance Windows

**Planned Maintenance:**

1. Schedule during low-traffic periods (typically weekends)
2. Notify users 7 days in advance
3. Enable maintenance mode
4. Perform updates with blue-green deployment
5. Verify functionality
6. Disable maintenance mode

```bash
# Enable maintenance mode
kubectl set env deployment/api-gateway MAINTENANCE_MODE=true

# Perform updates
kubectl set image deployment/api-gateway api-gateway=ai-platform-iso/api-gateway:1.1.0

# Wait for rollout
kubectl rollout status deployment/api-gateway

# Disable maintenance mode
kubectl set env deployment/api-gateway MAINTENANCE_MODE=false
```

### Security Updates

**Regular Security Practices:**

```bash
# Weekly security scans
trivy image ai-platform-iso/api-gateway:latest

# Automated dependency updates (Dependabot, Renovate)
# Review and merge security patches within 24-48 hours

# Rotate secrets quarterly
aws secretsmanager update-secret \
  --secret-id /ai-platform/production/jwt-secret \
  --secret-string "$(openssl rand -base64 32)"
```

---

## Document Information

**Document Version:** 1.0.0
**Last Updated:** 2025-10-09
**Next Review:** 2025-11-09
**Maintained By:** Platform Operations Team
**Feedback:** devops@ai-platform-iso.com

---

**Production Readiness Checklist:**

- [ ] Infrastructure provisioned and configured
- [ ] SSL/TLS certificates installed
- [ ] Secrets management configured
- [ ] Database configured with backups
- [ ] Services deployed and health-checked
- [ ] Monitoring and alerting active
- [ ] High availability verified
- [ ] Disaster recovery plan tested
- [ ] Security hardening completed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Team trained on operations

For assistance with production deployment, contact the DevOps team.
