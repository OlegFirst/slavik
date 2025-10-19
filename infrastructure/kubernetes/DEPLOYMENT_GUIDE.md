# BCM Platform - Kubernetes Deployment Guide

**Version:** 2.0.0
**Date:** 2025-10-19
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Deployment](#detailed-deployment)
4. [Configuration](#configuration)
5. [Monitoring Setup](#monitoring-setup)
6. [Troubleshooting](#troubleshooting)
7. [Scaling](#scaling)
8. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### Required Tools

- **kubectl** v1.28+
- **helm** v3.12+
- **docker** v24.0+
- **kubernetes cluster** v1.28+

### Cluster Requirements

- **Minimum Nodes:** 3
- **Node Resources (each):**
  - CPU: 4 cores
  - Memory: 16GB RAM
  - Storage: 50GB SSD

### Required Kubernetes Resources

- **Namespaces:**
  - `bcm-platform` (main application)
  - `monitoring` (Prometheus, Grafana)
  - `ingress-nginx` (Ingress controller)

- **Storage Classes:**
  - `fast-ssd` (for databases)
  - `standard` (for logs)

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/SEH-foundation/AI-Platform-ISO.git
cd AI-Platform-ISO/infrastructure/kubernetes
```

### 2. Create Namespace

```bash
kubectl create namespace bcm-platform
```

### 3. Deploy Secrets

```bash
# IMPORTANT: Replace placeholder values with real secrets!

kubectl create secret generic orchestration-secrets \
  --from-literal=database-url="postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB" \
  --from-literal=redis-url="redis://HOST:6379/0" \
  --from-literal=anthropic-api-key="YOUR_API_KEY" \
  --from-literal=jwt-secret-key="YOUR_JWT_SECRET" \
  --namespace=bcm-platform

kubectl create secret generic bcm-secrets \
  --from-literal=database-url="postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB" \
  --from-literal=redis-url="redis://HOST:6379/0" \
  --namespace=bcm-platform
```

### 4. Deploy ConfigMaps

```bash
kubectl apply -f configmaps/ --namespace=bcm-platform
```

### 5. Deploy Services

```bash
# Deploy orchestration layer
kubectl apply -f deployments/orchestration-deployment.yaml --namespace=bcm-platform

# Deploy BCM services
kubectl apply -f deployments/bcm-services/ --namespace=bcm-platform
```

### 6. Deploy Ingress

```bash
kubectl apply -f ingress/ --namespace=bcm-platform
```

### 7. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n bcm-platform

# Check services
kubectl get svc -n bcm-platform

# Check ingress
kubectl get ingress -n bcm-platform
```

---

## Detailed Deployment

### Step 1: Prepare Infrastructure

#### 1.1 Install Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.metrics.enabled=true \
  --set controller.podAnnotations."prometheus\.io/scrape"=true
```

#### 1.2 Install Cert-Manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

#### 1.3 Install Prometheus Operator

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### Step 2: Deploy Database (if not external)

```bash
# PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace bcm-platform \
  --set auth.username=bcm_user \
  --set auth.password=CHANGE_ME \
  --set auth.database=bcm_platform \
  --set primary.persistence.size=50Gi \
  --set primary.persistence.storageClass=fast-ssd

# Redis
helm install redis bitnami/redis \
  --namespace bcm-platform \
  --set auth.enabled=false \
  --set master.persistence.size=10Gi
```

### Step 3: Configure Secrets

#### Using Sealed Secrets (Recommended)

```bash
# Install sealed-secrets controller
helm install sealed-secrets sealed-secrets/sealed-secrets \
  --namespace kube-system

# Create sealed secret
kubeseal --format yaml \
  < secrets/orchestration-secrets.yaml \
  > secrets/orchestration-secrets-sealed.yaml

kubectl apply -f secrets/orchestration-secrets-sealed.yaml
```

#### Using External Secrets Operator (Alternative)

```bash
# Install external-secrets
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets-system \
  --create-namespace

# Configure secret store (Vault example)
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: bcm-platform
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "bcm-platform"
EOF

# Apply ExternalSecret
kubectl apply -f secrets/orchestration-secrets.yaml
```

### Step 4: Deploy Application

#### 4.1 Deploy Orchestration Layer

```bash
kubectl apply -f deployments/orchestration-deployment.yaml
```

#### 4.2 Deploy BCM Services (all 11)

Option A: Deploy all at once
```bash
for service in deployments/bcm-services/*.yaml; do
  kubectl apply -f "$service"
done
```

Option B: Deploy one by one
```bash
kubectl apply -f deployments/bcm-services/bia-service-deployment.yaml
kubectl apply -f deployments/bcm-services/risk-service-deployment.yaml
# ... etc
```

#### 4.3 Deploy Ingress

```bash
kubectl apply -f ingress/orchestration-ingress.yaml
```

### Step 5: Deploy Monitoring

#### 5.1 Deploy ServiceMonitors

```bash
kubectl apply -f monitoring/servicemonitors.yaml
```

#### 5.2 Deploy Grafana Dashboards

```bash
kubectl create configmap grafana-dashboard-platform-integration \
  --from-file=monitoring/grafana-platform-integration-dashboard.json \
  --namespace=monitoring

kubectl label configmap grafana-dashboard-platform-integration \
  grafana_dashboard=1 \
  --namespace=monitoring
```

---

## Configuration

### Environment-Specific Configuration

#### Staging

```yaml
# Override values for staging
replicas: 2
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

#### Production

```yaml
# Override values for production
replicas: 3
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Horizontal Pod Autoscaling

HPA is already configured in deployments. To adjust:

```bash
kubectl edit hpa orchestration-hpa -n bcm-platform
```

### Resource Quotas

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: bcm-platform-quota
  namespace: bcm-platform
spec:
  hard:
    requests.cpu: "50"
    requests.memory: 100Gi
    pods: "100"
EOF
```

---

## Monitoring Setup

### Access Grafana

```bash
# Get Grafana password
kubectl get secret --namespace monitoring kube-prometheus-stack-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward
kubectl port-forward -n monitoring \
  svc/kube-prometheus-stack-grafana 3000:80
```

Open: http://localhost:3000

### Access Prometheus

```bash
kubectl port-forward -n monitoring \
  svc/kube-prometheus-stack-prometheus 9090:9090
```

Open: http://localhost:9090

### Key Metrics to Monitor

1. **Intelligent Router:**
   - `intelligent_router_routing_time_ms` (target: < 20ms)
   - `intelligent_router_sla_compliance_rate` (target: > 0.95)

2. **Saga Engine:**
   - `saga_active_count`
   - `saga_success_rate` (target: > 0.95)

3. **Self-Aware Services:**
   - `self_aware_health_score` (target: > 0.7)
   - `self_aware_load_percent` (target: < 80%)

4. **System Health:**
   - `up{app="orchestration"}`
   - `up{component="bcm-service"}`

---

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Check pod events
kubectl describe pod POD_NAME -n bcm-platform

# Check logs
kubectl logs POD_NAME -n bcm-platform

# Check previous logs (if crashed)
kubectl logs POD_NAME -n bcm-platform --previous
```

#### 2. Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql -h postgres-service -U bcm_user -d bcm_platform
```

#### 3. Service Not Reachable

```bash
# Check service endpoints
kubectl get endpoints -n bcm-platform

# Test internal connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://orchestration-service:8002/health
```

#### 4. Ingress Not Working

```bash
# Check ingress
kubectl describe ingress orchestration-ingress -n bcm-platform

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### Debug Commands

```bash
# Get all resources in namespace
kubectl get all -n bcm-platform

# Get events
kubectl get events -n bcm-platform --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n bcm-platform
kubectl top nodes

# Get full pod YAML
kubectl get pod POD_NAME -n bcm-platform -o yaml
```

---

## Scaling

### Manual Scaling

```bash
# Scale orchestration
kubectl scale deployment orchestration-service \
  --replicas=5 -n bcm-platform

# Scale specific BCM service
kubectl scale deployment bia-service \
  --replicas=4 -n bcm-platform
```

### Auto-Scaling Configuration

HPA already configured. To modify:

```bash
kubectl edit hpa orchestration-hpa -n bcm-platform
```

### Cluster Autoscaling

If using cloud provider (GKE, EKS, AKS), enable cluster autoscaler:

```bash
# GKE example
gcloud container clusters update CLUSTER_NAME \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10
```

---

## Rollback Procedures

### Rollback Deployment

```bash
# Rollback orchestration
kubectl rollout undo deployment/orchestration-service -n bcm-platform

# Rollback to specific revision
kubectl rollout undo deployment/orchestration-service \
  --to-revision=2 -n bcm-platform

# Check rollout status
kubectl rollout status deployment/orchestration-service -n bcm-platform
```

### Rollback History

```bash
# View rollout history
kubectl rollout history deployment/orchestration-service -n bcm-platform

# View specific revision
kubectl rollout history deployment/orchestration-service \
  --revision=2 -n bcm-platform
```

---

## Health Checks

### Verify Deployment

```bash
#!/bin/bash
# health-check.sh

echo "🔍 Checking BCM Platform Health..."

# Check orchestration
ORCH_STATUS=$(kubectl get deployment orchestration-service -n bcm-platform -o jsonpath='{.status.availableReplicas}')
echo "Orchestration: $ORCH_STATUS replicas available"

# Check BCM services
BCM_SERVICES=$(kubectl get deployment -n bcm-platform -l component=bcm-service -o jsonpath='{.items[*].metadata.name}')
for service in $BCM_SERVICES; do
  REPLICAS=$(kubectl get deployment $service -n bcm-platform -o jsonpath='{.status.availableReplicas}')
  echo "$service: $REPLICAS replicas available"
done

# Check endpoints
ORCH_IP=$(kubectl get service orchestration-service -n bcm-platform -o jsonpath='{.spec.clusterIP}')
if curl -sf http://$ORCH_IP:8002/health > /dev/null; then
  echo "✅ Orchestration service health check passed"
else
  echo "❌ Orchestration service health check failed"
fi
```

---

## Maintenance

### Update Images

```bash
# Update orchestration image
kubectl set image deployment/orchestration-service \
  orchestration=ghcr.io/seh-foundation/ai-platform-iso/orchestration:v2.0.1 \
  -n bcm-platform

# Watch rollout
kubectl rollout status deployment/orchestration-service -n bcm-platform
```

### Backup

```bash
# Backup namespace resources
kubectl get all,configmap,secret -n bcm-platform -o yaml > bcm-platform-backup.yaml

# Backup database
kubectl exec -it postgres-0 -n bcm-platform -- \
  pg_dump -U bcm_user bcm_platform > backup.sql
```

---

## Security

### Network Policies

Network policies are included in deployment manifests.

### Pod Security Standards

```bash
kubectl label namespace bcm-platform \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

---

## Support

For issues or questions:
- **GitHub Issues:** https://github.com/SEH-foundation/AI-Platform-ISO/issues
- **Documentation:** https://docs.bcm-platform.io
- **Email:** support@seh-foundation.org

---

**Created:** 2025-10-19
**Author:** Claude Code
**Version:** 2.0.0
