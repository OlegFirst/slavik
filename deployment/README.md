# Deployment Infrastructure

**Version:** 2.0.0  
**Purpose:** Enterprise Deployment & Orchestration  
**Last Updated:** 2025-10-08

---

## Overview

The Deployment Infrastructure provides comprehensive tools, configurations, and automation for deploying the AI-Platform-ISO system across various environments. It supports Docker, Kubernetes, and cloud-native deployments with full CI/CD integration.

### Key Components

1. **Docker Compose** - Local and development deployments
2. **Kubernetes Manifests** - Production-grade container orchestration
3. **Helm Charts** - Parameterized Kubernetes deployments
4. **CI/CD Pipelines** - Automated testing and deployment
5. **Infrastructure as Code** - Terraform configurations
6. **Monitoring & Observability** - Production monitoring setup
7. **Security & Secrets** - Secure configuration management
8. **Scaling & Auto-scaling** - Dynamic resource management

---

## Architecture

```
Deployment Infrastructure
│
├── Container Orchestration
│   ├── Docker Compose (Development)
│   ├── Kubernetes (Production)
│   └── Helm Charts (Parameterized)
│
├── CI/CD Automation
│   ├── GitHub Actions
│   ├── GitLab CI
│   └── Jenkins Pipelines
│
├── Infrastructure as Code
│   ├── Terraform (Cloud Resources)
│   ├── Ansible (Configuration)
│   └── CloudFormation (AWS)
│
├── Monitoring & Observability
│   ├── Prometheus
│   ├── Grafana
│   ├── ELK Stack
│   └── Jaeger (Tracing)
│
└── Security & Compliance
    ├── Secrets Management (Vault)
    ├── Network Policies
    ├── RBAC Configurations
    └── Security Scanning
```

---

## Directory Structure

```
deployment/
│
├── docker/
│   ├── docker-compose.yml                 # Main compose file
│   ├── docker-compose.dev.yml             # Development overrides
│   ├── docker-compose.prod.yml            # Production overrides
│   └── Dockerfiles/
│       ├── intelligent-core.Dockerfile
│       ├── platform-services.Dockerfile
│       └── infrastructure.Dockerfile
│
├── kubernetes/
│   ├── base/                              # Base configurations
│   │   ├── namespace.yaml
│   │   ├── configmaps/
│   │   ├── secrets/
│   │   └── services/
│   ├── intelligent-core/                  # AI modules
│   ├── platform-services/                 # BCM services
│   ├── infrastructure/                    # Infrastructure services
│   └── ingress/                           # Ingress configurations
│
├── helm/
│   ├── ai-platform/                       # Main Helm chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values.dev.yaml
│   │   ├── values.prod.yaml
│   │   └── templates/
│   └── dependencies/                      # Dependency charts
│
├── terraform/
│   ├── aws/                               # AWS infrastructure
│   ├── azure/                             # Azure infrastructure
│   ├── gcp/                               # GCP infrastructure
│   └── modules/                           # Reusable modules
│
├── ci-cd/
│   ├── github-actions/                    # GitHub workflows
│   ├── gitlab-ci/                         # GitLab pipelines
│   └── jenkins/                           # Jenkinsfiles
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   ├── rules/
│   │   └── alerts/
│   ├── grafana/
│   │   ├── dashboards/
│   │   └── datasources/
│   └── logging/
│       ├── elasticsearch/
│       ├── logstash/
│       └── kibana/
│
├── security/
│   ├── vault/                             # HashiCorp Vault
│   ├── network-policies/                  # K8s network policies
│   ├── rbac/                              # Role-based access
│   └── scanning/                          # Security scanning tools
│
└── scripts/
    ├── deploy.sh                          # Main deployment script
    ├── rollback.sh                        # Rollback script
    ├── scale.sh                           # Scaling script
    └── backup.sh                          # Backup script
```

---

## Quick Start

### Local Development (Docker Compose)

```bash
# Clone repository
git clone https://github.com/yourorg/AI-Platform-ISO.git
cd AI-Platform-ISO/deployment

# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production (Kubernetes)

```bash
# Apply base configurations
kubectl apply -f kubernetes/base/

# Deploy intelligent core
kubectl apply -f kubernetes/intelligent-core/

# Deploy platform services
kubectl apply -f kubernetes/platform-services/

# Deploy infrastructure
kubectl apply -f kubernetes/infrastructure/

# Check deployment status
kubectl get pods -n ai-platform

# Access services
kubectl port-forward -n ai-platform svc/gateway 8080:8080
```

### Helm Deployment

```bash
# Add Helm repository (if applicable)
helm repo add ai-platform https://charts.example.com/ai-platform

# Install with default values
helm install ai-platform ./helm/ai-platform

# Install with custom values
helm install ai-platform ./helm/ai-platform \
  -f helm/ai-platform/values.prod.yaml \
  --namespace ai-platform \
  --create-namespace

# Upgrade deployment
helm upgrade ai-platform ./helm/ai-platform

# Rollback
helm rollback ai-platform 1
```

---

## Deployment Strategies

### 1. Blue-Green Deployment

```bash
# Deploy green environment
kubectl apply -f kubernetes/blue-green/green/

# Test green environment
./scripts/test-environment.sh green

# Switch traffic to green
kubectl patch service gateway -p '{"spec":{"selector":{"version":"green"}}}'

# Remove blue environment
kubectl delete -f kubernetes/blue-green/blue/
```

### 2. Canary Deployment

```bash
# Deploy canary version (10% traffic)
kubectl apply -f kubernetes/canary/canary-10.yaml

# Monitor canary metrics
./scripts/monitor-canary.sh

# Increase canary traffic (50%)
kubectl apply -f kubernetes/canary/canary-50.yaml

# Complete rollout (100%)
kubectl apply -f kubernetes/canary/canary-100.yaml
```

### 3. Rolling Update

```bash
# Update deployment with rolling strategy
kubectl set image deployment/bia-service \
  bia-service=bia-service:v2.0.0 \
  --record

# Monitor rollout
kubectl rollout status deployment/bia-service

# Rollback if needed
kubectl rollout undo deployment/bia-service
```

---

## Environment Configuration

### Development Environment

**Characteristics:**
- Local Docker Compose
- Hot-reloading enabled
- Debug logging
- Minimal resources
- Mock external services

**Configuration:**
```yaml
# docker-compose.dev.yml
services:
  bia-service:
    build:
      context: ../platform-services/bia-service
      dockerfile: Dockerfile.dev
    volumes:
      - ../platform-services/bia-service:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    ports:
      - "8001:8001"
```

### Staging Environment

**Characteristics:**
- Kubernetes cluster
- Production-like configuration
- Real external services
- Performance testing
- Security scanning

**Configuration:**
```yaml
# helm/ai-platform/values.staging.yaml
replicaCount: 2
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
```

### Production Environment

**Characteristics:**
- Multi-zone Kubernetes
- High availability
- Auto-scaling
- Full monitoring
- Disaster recovery

**Configuration:**
```yaml
# helm/ai-platform/values.prod.yaml
replicaCount: 3
resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 2000m
    memory: 4Gi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
persistence:
  enabled: true
  size: 100Gi
```

---

## CI/CD Pipelines

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy AI Platform

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build images
        run: |
          docker build -t ai-platform/bia-service:${{ github.sha }} \
            platform-services/bia-service
      - name: Push to registry
        run: |
          docker push ai-platform/bia-service:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/bia-service \
            bia-service=ai-platform/bia-service:${{ github.sha }}
```

---

## Infrastructure as Code

### Terraform (AWS Example)

```hcl
# terraform/aws/main.tf
module "eks_cluster" {
  source = "./modules/eks"
  
  cluster_name    = "ai-platform-prod"
  cluster_version = "1.28"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  
  node_groups = {
    general = {
      desired_capacity = 3
      max_capacity     = 10
      min_capacity     = 2
      instance_types   = ["t3.xlarge"]
    }
    ai_workloads = {
      desired_capacity = 2
      max_capacity     = 5
      min_capacity     = 1
      instance_types   = ["g4dn.xlarge"]  # GPU instances
    }
  }
}

module "rds" {
  source = "./modules/rds"
  
  identifier     = "ai-platform-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.large"
  
  allocated_storage = 100
  storage_encrypted = true
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets
}
```

---

## Monitoring & Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Platform Services
  - job_name: 'bia-service'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: bia-service
  
  # Intelligent Core
  - job_name: 'ai-foundation'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: ai-foundation

rule_files:
  - 'rules/*.yml'
  - 'alerts/*.yml'
```

### Grafana Dashboards

Pre-configured dashboards available:
- **Platform Overview** - System-wide metrics
- **Service Performance** - Individual service metrics
- **AI Model Performance** - ML model metrics
- **Infrastructure Health** - Kubernetes cluster health
- **Business Metrics** - BCM-specific KPIs

---

## Security

### Secrets Management (Vault)

```bash
# Initialize Vault
vault operator init
vault operator unseal

# Store secrets
vault kv put secret/ai-platform/database \
  host=postgres.example.com \
  username=admin \
  password=secure_password

# Inject secrets into Kubernetes
kubectl create secret generic database-credentials \
  --from-literal=host=$(vault kv get -field=host secret/ai-platform/database) \
  --from-literal=username=$(vault kv get -field=username secret/ai-platform/database) \
  --from-literal=password=$(vault kv get -field=password secret/ai-platform/database)
```

### Network Policies

```yaml
# security/network-policies/bia-service-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bia-service-policy
  namespace: ai-platform
spec:
  podSelector:
    matchLabels:
      app: bia-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: gateway
    ports:
    - protocol: TCP
      port: 8001
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

---

## Scaling

### Horizontal Pod Autoscaler

```yaml
# kubernetes/platform-services/bia-service-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bia-service-hpa
  namespace: ai-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bia-service
  minReplicas: 2
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

---

## Backup & Recovery

### Database Backup

```bash
# scripts/backup.sh
#!/bin/bash

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# PostgreSQL backup
kubectl exec -n ai-platform postgres-0 -- \
  pg_dump -U postgres ai_platform > \
  ${BACKUP_DIR}/postgres_${TIMESTAMP}.sql

# Upload to S3
aws s3 cp ${BACKUP_DIR}/postgres_${TIMESTAMP}.sql \
  s3://ai-platform-backups/postgres/

# Rotate old backups (keep last 30 days)
find ${BACKUP_DIR} -name "postgres_*.sql" -mtime +30 -delete
```

### Disaster Recovery

```bash
# scripts/restore.sh
#!/bin/bash

BACKUP_FILE=$1

# Download from S3
aws s3 cp s3://ai-platform-backups/postgres/${BACKUP_FILE} \
  /tmp/${BACKUP_FILE}

# Restore database
kubectl exec -n ai-platform postgres-0 -- \
  psql -U postgres -d ai_platform < /tmp/${BACKUP_FILE}

echo "Database restored from ${BACKUP_FILE}"
```

---

## Troubleshooting

### Common Issues

**Issue:** Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n ai-platform

# Check logs
kubectl logs <pod-name> -n ai-platform

# Check events
kubectl get events -n ai-platform --sort-by='.lastTimestamp'
```

**Issue:** Service unreachable

```bash
# Check service
kubectl get svc -n ai-platform

# Check endpoints
kubectl get endpoints -n ai-platform

# Test connectivity
kubectl run test-pod --image=busybox -it --rm -- \
  wget -O- http://bia-service:8001/health
```

**Issue:** High resource usage

```bash
# Check resource usage
kubectl top pods -n ai-platform

# Check HPA status
kubectl get hpa -n ai-platform

# Scale manually if needed
kubectl scale deployment/bia-service --replicas=5 -n ai-platform
```

---

## Maintenance

### Rolling Restart

```bash
# Restart all services
kubectl rollout restart deployment -n ai-platform

# Restart specific service
kubectl rollout restart deployment/bia-service -n ai-platform
```

### Version Upgrade

```bash
# Update Helm chart
helm upgrade ai-platform ./helm/ai-platform \
  --set image.tag=v2.1.0 \
  --namespace ai-platform

# Monitor upgrade
kubectl rollout status deployment -n ai-platform
```

---

## Performance Tuning

### Resource Optimization

```yaml
# Optimized resource allocation
resources:
  requests:
    cpu: 1000m      # Minimum guaranteed
    memory: 2Gi     # Minimum guaranteed
  limits:
    cpu: 2000m      # Maximum allowed
    memory: 4Gi     # Maximum allowed

# Pod priority
priorityClassName: high-priority

# Pod disruption budget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: bia-service-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: bia-service
```

---

## Cost Optimization

### Resource Right-Sizing

```bash
# Analyze resource usage
kubectl top pods -n ai-platform

# Recommendations
./scripts/resource-recommendations.sh

# Apply optimized configurations
kubectl apply -f kubernetes/optimized/
```

### Auto-Scaling Policies

```yaml
# Cost-effective auto-scaling
autoscaling:
  enabled: true
  minReplicas: 2              # Minimum for availability
  maxReplicas: 5              # Cap to control costs
  targetCPUUtilizationPercentage: 75  # Higher threshold
  scaleDownStabilization: 600  # Wait 10 min before scaling down
```

---

## Compliance & Auditing

### Audit Logging

```yaml
# Enable Kubernetes audit logging
apiVersion: v1
kind: Policy
rules:
  - level: Metadata
    resources:
    - group: ""
      resources: ["secrets", "configmaps"]
  - level: Request
    verbs: ["create", "update", "patch", "delete"]
```

### Compliance Checks

```bash
# Run CIS Kubernetes benchmark
./scripts/cis-benchmark.sh

# Security scanning
trivy image ai-platform/bia-service:latest

# Policy compliance
opa test security/policies/
```

---

## Related Documentation

- [Infrastructure Overview](../infrastructure/README.md)
- [Platform Services](../platform-services/README.md)
- [Intelligent Core](../intelligent-core/README.md)
- [Monitoring Guide](./monitoring/README.md)
- [Security Guide](./security/README.md)

---

**Maintained By:** DevOps & Infrastructure Team  
**Contact:** devops@example.com  
**Documentation Version:** 1.0.0
