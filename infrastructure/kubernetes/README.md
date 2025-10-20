# BCM Platform - Kubernetes Infrastructure

**Version:** 2.0.0
**Status:** Production Ready ✅

---

## 📋 Quick Start

### Prerequisites

- Kubernetes cluster v1.28+
- kubectl configured
- Helm 3.x (optional)
- 3+ nodes with 4 CPU, 16GB RAM each

### Deploy to Kubernetes

```bash
# 1. Validate prerequisites
./infrastructure/kubernetes/scripts/validate-prerequisites.sh

# 2. Deploy to production
./infrastructure/kubernetes/scripts/deploy-production.sh \
  --environment production \
  --namespace bcm-platform

# 3. Run smoke tests
./infrastructure/kubernetes/scripts/smoke-tests.sh bcm-platform

# 4. Access services
kubectl get ingress -n bcm-platform
```

---

## 📂 Directory Structure

```
infrastructure/kubernetes/
├── README.md                          # This file
├── DEPLOYMENT_GUIDE.md                # Detailed deployment guide
├── PRODUCTION_DEPLOYMENT_CHECKLIST.md # Production checklist
├── PHASE_3.1_ADVANCED_FEATURES.md     # Phase 3.1 documentation
│
├── deployments/                       # Kubernetes deployments
│   ├── orchestration-deployment.yaml  # Orchestration layer
│   └── bcm-services/                  # 11 BCM service deployments
│       ├── bia-service-deployment.yaml
│       ├── risk-service-deployment.yaml
│       └── ... (9 more services)
│
├── configmaps/                        # ConfigMaps
│   └── orchestration-configmap.yaml
│
├── secrets/                           # Secret templates (sealed)
│   └── orchestration-secrets.yaml
│
├── ingress/                           # Ingress resources
│   └── orchestration-ingress.yaml
│
├── monitoring/                        # Monitoring configs
│   ├── servicemonitors.yaml           # Prometheus ServiceMonitors
│   └── grafana-platform-integration-dashboard.json
│
├── istio/                             # Service Mesh (Phase 3.1)
│   ├── gateway.yaml                   # Istio Gateway
│   ├── virtual-service-orchestration.yaml
│   ├── destination-rule-orchestration.yaml
│   └── security.yaml                  # mTLS & AuthZ policies
│
├── argocd/                            # GitOps (Phase 3.1)
│   ├── project.yaml                   # ArgoCD Project
│   └── application-bcm-platform.yaml  # ArgoCD Applications
│
├── tracing/                           # Distributed Tracing (Phase 3.1)
│   └── jaeger.yaml
│
├── backup/                            # Disaster Recovery (Phase 3.1)
│   └── velero-backup.yaml
│
└── scripts/                           # Automation scripts
    ├── deploy-production.sh           # Main deployment script
    ├── validate-prerequisites.sh      # Prerequisites check
    ├── smoke-tests.sh                 # Smoke testing
    ├── generate-bcm-deployments.sh    # Generate BCM service deployments
    └── install-phase-3.1.sh           # Install Phase 3.1 features
```

---

## 🚀 Deployment Options

### Option 1: Quick Deployment (Automated)

```bash
# Full automated deployment
./infrastructure/kubernetes/scripts/deploy-production.sh \
  --environment production \
  --namespace bcm-platform

# Watch deployment progress
kubectl get pods -n bcm-platform -w
```

### Option 2: Manual Deployment (Step-by-Step)

Follow the comprehensive guide:

```bash
cat infrastructure/kubernetes/DEPLOYMENT_GUIDE.md
cat infrastructure/kubernetes/PRODUCTION_DEPLOYMENT_CHECKLIST.md
```

**Steps:**
1. Create namespace
2. Deploy secrets
3. Deploy ConfigMaps
4. Deploy orchestration layer
5. Deploy BCM services
6. Deploy ingress
7. Deploy monitoring
8. Run smoke tests

### Option 3: GitOps Deployment (ArgoCD)

```bash
# Install ArgoCD (Phase 3.1)
./infrastructure/kubernetes/scripts/install-phase-3.1.sh argocd

# Deploy applications
kubectl apply -f infrastructure/kubernetes/argocd/project.yaml
kubectl apply -f infrastructure/kubernetes/argocd/application-bcm-platform.yaml

# ArgoCD will automatically sync from Git
argocd app sync bcm-platform
```

---

## 📊 What Gets Deployed

### Core Platform (Phase 3)

**Orchestration Layer:**
- Orchestration Service (3 replicas)
- HPA (auto-scaling 3-10 replicas)
- Service, Ingress, ConfigMaps

**11 BCM Services:**
- BIA Service (8020)
- Risk Service (8040)
- Compliance Service (8030)
- Planning Service (8050)
- Governance Service (8060)
- Plans Service (8070)
- Response Service (8080)
- Documents Service (8090)
- Validation Service (8100)
- Learning Service (8110)
- Simulation Service (8120)

**Monitoring:**
- 6 Prometheus ServiceMonitors
- 15 Alert Rules
- Grafana Dashboard (Platform Integration)

**Total Resources:** 49 Kubernetes resources

### Advanced Features (Phase 3.1)

**Service Mesh (Istio):**
- Istio Gateway
- VirtualServices (traffic routing)
- DestinationRules (load balancing, circuit breaking)
- PeerAuthentication (mTLS)
- AuthorizationPolicies (RBAC)

**GitOps (ArgoCD):**
- ArgoCD Project
- 6 ArgoCD Applications
- Automated sync from Git
- Multi-environment support

**Distributed Tracing (Jaeger):**
- Jaeger Operator
- Jaeger instance
- OpenTelemetry instrumentation

**Disaster Recovery (Velero):**
- Velero CLI
- Backup schedules
- Restore procedures

---

## 🔧 Configuration

### Environment Variables

See `.env.example` and `COMPREHENSIVE_.env.example` for all configuration options.

**Critical Variables:**
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `ANTHROPIC_API_KEY` - AI API key
- `JWT_SECRET_KEY` - JWT signing key
- `PLATFORM_INTEGRATION_ENABLED=true` - Enable Graceful Choreography

### Resource Limits

**Orchestration Service:**
- Requests: 512Mi RAM, 500m CPU
- Limits: 2Gi RAM, 2000m CPU
- Replicas: 3-10 (HPA)

**BCM Services (each):**
- Requests: 256Mi RAM, 250m CPU
- Limits: 1Gi RAM, 1000m CPU
- Replicas: 2-5 (HPA)

### Customization

Edit deployments before applying:
```bash
# Edit orchestration deployment
vim infrastructure/kubernetes/deployments/orchestration-deployment.yaml

# Regenerate BCM service deployments
./infrastructure/kubernetes/scripts/generate-bcm-deployments.sh
```

---

## 📈 Monitoring & Observability

### Access Grafana Dashboard

```bash
# Get Grafana password
kubectl get secret --namespace monitoring kube-prometheus-stack-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80

# Open http://localhost:3000
# Dashboard: "Platform Integration"
```

### Access Prometheus

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090
# Open http://localhost:9090
```

### Key Metrics

**Platform Integration Metrics:**
- `intelligent_router_routing_time_ms` (target: < 20ms)
- `intelligent_router_sla_compliance_rate` (target: > 0.95)
- `saga_active_count`
- `saga_success_rate` (target: > 0.95)
- `self_aware_health_score` (target: > 0.7)
- `cqrs_query_cache_hit_rate`

**System Metrics:**
- `up{app="orchestration"}`
- `up{component="bcm-service"}`
- `container_cpu_usage_seconds_total`
- `container_memory_working_set_bytes`

---

## 🕸️ Phase 3.1: Advanced Features

### Install All Phase 3.1 Components

```bash
# Install everything
./infrastructure/kubernetes/scripts/install-phase-3.1.sh all

# Or install individually
./infrastructure/kubernetes/scripts/install-phase-3.1.sh istio
./infrastructure/kubernetes/scripts/install-phase-3.1.sh argocd
./infrastructure/kubernetes/scripts/install-phase-3.1.sh jaeger
./infrastructure/kubernetes/scripts/install-phase-3.1.sh velero
```

### Service Mesh (Istio)

**Benefits:**
- Zero-trust security (mTLS)
- Advanced traffic management
- Canary deployments
- Circuit breaking
- Rate limiting

**Access Kiali (Service Mesh UI):**
```bash
istioctl dashboard kiali
# Open http://localhost:20001
```

### GitOps (ArgoCD)

**Benefits:**
- Git as single source of truth
- Automated sync
- Easy rollback
- Audit trail

**Access ArgoCD UI:**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open https://localhost:8080
# Username: admin
# Password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Distributed Tracing (Jaeger)

**Benefits:**
- End-to-end request tracing
- Performance bottleneck identification
- Service dependency mapping

**Access Jaeger UI:**
```bash
kubectl port-forward -n observability svc/jaeger-query 16686:16686
# Open http://localhost:16686
```

### Disaster Recovery (Velero)

**Benefits:**
- Automated backups
- Multi-region replication
- Fast recovery (RTO: 1 hour, RPO: 15 minutes)

**Create Backup:**
```bash
velero backup create bcm-platform-backup --include-namespaces bcm-platform
velero backup get
```

**Restore:**
```bash
velero restore create --from-backup bcm-platform-backup
```

---

## 🔒 Security

### mTLS Enabled

All service-to-service communication encrypted with mutual TLS via Istio.

### RBAC

Authorization policies control access between services.

### Network Policies

Firewall rules isolate services.

### Secret Management

Use **Sealed Secrets** or **External Secrets Operator** for production:

```bash
# Option A: Sealed Secrets
helm install sealed-secrets sealed-secrets/sealed-secrets --namespace kube-system
kubeseal --format yaml < secret.yaml > sealed-secret.yaml
kubectl apply -f sealed-secret.yaml

# Option B: External Secrets (Vault)
kubectl apply -f infrastructure/kubernetes/secrets/orchestration-secrets.yaml
```

---

## 🧪 Testing

### Smoke Tests

```bash
./infrastructure/kubernetes/scripts/smoke-tests.sh bcm-platform
```

**Tests:**
- All pods running
- No CrashLoopBackOff
- Health endpoints responding
- Services have endpoints
- HPA configured
- Metrics collecting

### Integration Tests

```bash
# Test orchestration health
kubectl exec -n bcm-platform deployment/orchestration-service -- \
  curl -f http://localhost:8002/health

# Test Platform Integration
kubectl exec -n bcm-platform deployment/orchestration-service -- \
  python -m pytest test_platform_integration.py -v
```

### Load Testing

```bash
# Simple load test
kubectl run load-test --rm -it --image=busybox --restart=Never -- \
  sh -c "while true; do wget -O- http://orchestration-service.bcm-platform.svc:8002/health; sleep 1; done"
```

---

## 🔄 CI/CD Integration

### GitHub Actions

Workflows provided in `.github/workflows/`:

1. **test-orchestration.yml** - Run tests on push
2. **build-and-push.yml** - Build Docker images
3. **deploy-kubernetes.yml** - Deploy to K8s

**Trigger deployment:**
```bash
# Via GitHub UI: Actions → Deploy to Kubernetes → Run workflow

# Or via gh CLI
gh workflow run deploy-kubernetes.yml \
  -f environment=production \
  -f version=v2.0.0
```

### ArgoCD Integration

ArgoCD automatically syncs from Git every 3 minutes.

**Manual sync:**
```bash
argocd app sync bcm-platform
argocd app sync --all
```

---

## 📊 Scaling

### Manual Scaling

```bash
# Scale orchestration
kubectl scale deployment orchestration-service --replicas=5 -n bcm-platform

# Scale specific BCM service
kubectl scale deployment bia-service --replicas=4 -n bcm-platform
```

### Auto-Scaling (HPA)

HPA already configured for all deployments:
- Min: 2-3 replicas
- Max: 5-10 replicas
- Target CPU: 70%

### Cluster Auto-Scaling

Enable on cloud provider:
```bash
# GKE
gcloud container clusters update CLUSTER --enable-autoscaling --min-nodes 3 --max-nodes 10

# EKS
eksctl scale nodegroup --cluster=CLUSTER --nodes=3 --nodes-min=3 --nodes-max=10 ng-1

# AKS
az aks update --resource-group RG --name CLUSTER --enable-cluster-autoscaler --min-count 3 --max-count 10
```

---

## 🛠️ Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
kubectl describe pod POD_NAME -n bcm-platform
kubectl logs POD_NAME -n bcm-platform
kubectl logs POD_NAME -n bcm-platform --previous  # Previous instance logs
```

#### Service Not Reachable

```bash
kubectl get endpoints -n bcm-platform
kubectl exec -it deployment/orchestration-service -n bcm-platform -- \
  curl http://bia-service:8020/health
```

#### Ingress Not Working

```bash
kubectl describe ingress orchestration-ingress -n bcm-platform
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### Debug Commands

```bash
# Get all resources
kubectl get all -n bcm-platform

# Check events
kubectl get events -n bcm-platform --sort-by='.lastTimestamp'

# Resource usage
kubectl top pods -n bcm-platform
kubectl top nodes

# Exec into pod
kubectl exec -it deployment/orchestration-service -n bcm-platform -- /bin/sh
```

---

## 📚 Documentation

- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Production Checklist:** `PRODUCTION_DEPLOYMENT_CHECKLIST.md`
- **Phase 3.1 Features:** `PHASE_3.1_ADVANCED_FEATURES.md`
- **Service Catalog:** `../../SERVICE_CATALOG_DETAILED.yaml`
- **Environment Variables:** `../../COMPREHENSIVE_.env.example`

---

## 🤝 Support

**Issues:** https://github.com/SEH-foundation/AI-Platform-ISO/issues
**Documentation:** https://seh-foundation.github.io/AI-Platform-ISO/
**Email:** support@seh-foundation.org

---

## 📝 Version History

**v2.0.0 (2025-10-20)**
- ✅ Phase 3 complete - Basic production deployment
- ✅ Phase 3.1 complete - Advanced features (Istio, ArgoCD, Jaeger, Velero)
- ✅ 49 Kubernetes resources
- ✅ 4 automation scripts
- ✅ Full documentation

**v1.0.0 (2025-10-19)**
- Initial production deployment infrastructure

---

**Created:** 2025-10-20
**Author:** Claude Code
**License:** SEH Foundation
