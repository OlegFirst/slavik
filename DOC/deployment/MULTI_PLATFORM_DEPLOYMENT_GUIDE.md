# BCM Platform - Multi-Platform Deployment Guide

**Version:** 3.0.0
**Last Updated:** October 21, 2025
**Status:** Production Ready ✅

---

## 📋 Overview

This guide covers deploying BCM Platform to **three different Kubernetes platforms**:

1. **Local Development** - minikube, kind, Docker Desktop
2. **Google Kubernetes Engine (GKE)** - Cloud production deployment
3. **DigitalOcean Kubernetes (DOKS)** - Alternative cloud deployment

All platforms are **fully configured** and **production-ready** with:
- ✅ One-command deployment
- ✅ Seamless context switching
- ✅ Unified management scripts
- ✅ CI/CD pipelines
- ✅ Disaster recovery

---

## 🎯 Quick Start (Choose Your Platform)

### Option 1: Local Development (Fastest)

```bash
# Setup (5 minutes)
./infrastructure/kubernetes/scripts/local-setup.sh minikube

# Deploy (3 minutes)
./infrastructure/kubernetes/scripts/local-deploy.sh

# Access
./infrastructure/kubernetes/scripts/port-forward-local.sh
# Open: http://localhost:8002/health
```

**Best for:** Development, testing, learning

---

### Option 2: Google Kubernetes Engine (Most Features)

```bash
# Setup (15 minutes)
cd infrastructure/deployment/gke
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your GCP project ID

# Deploy
./gke-create-cluster.sh
./gke-configure.sh
./gke-install-addons.sh
./gke-deploy-bcm.sh

# Access via LoadBalancer IP
kubectl get ingress -n bcm-platform
```

**Best for:** Production, enterprise, maximum features

---

### Option 3: DigitalOcean Kubernetes (Most Affordable)

```bash
# Setup (10 minutes)
cd infrastructure/deployment/digitalocean
export DIGITALOCEAN_ACCESS_TOKEN="your-do-token"

# Deploy
./do-create-cluster.sh
./do-configure.sh
./do-install-addons.sh
./do-deploy-bcm.sh

# Access via LoadBalancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

**Best for:** Cost-effective production, startups

---

## 🔄 Unified Deployment (All Platforms)

Use the **unified deployment script** for any platform:

```bash
# Local
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh local

# GKE
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh gke \
  --project my-gcp-project \
  --region us-central1

# DigitalOcean
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh digitalocean \
  --token $DO_TOKEN \
  --region nyc3
```

---

## 🔀 Context Switching (Seamless Platform Changes)

### Switch Between Clusters

```bash
# Interactive mode
./infrastructure/kubernetes/scripts/switch-context.sh

# Direct switch
./infrastructure/kubernetes/scripts/switch-context.sh minikube
./infrastructure/kubernetes/scripts/switch-context.sh gke_project_region_cluster
./infrastructure/kubernetes/scripts/switch-context.sh do-bcm-platform-prod

# Show current context
./infrastructure/kubernetes/scripts/switch-context.sh --current

# List all contexts
./infrastructure/kubernetes/scripts/switch-context.sh --list
```

### Create Shell Aliases (Recommended)

```bash
# Install aliases
./infrastructure/kubernetes/scripts/switch-context.sh --aliases

# Reload shell
source ~/.bashrc  # or source ~/.zshrc

# Use aliases
k8s-local     # Switch to local
k8s-gke       # Switch to GKE
k8s-do        # Switch to DigitalOcean
k8s-current   # Show current
bcm-status    # Check BCM Platform status
bcm-health    # Check orchestration health
bcm-logs      # Follow logs
```

---

## 📊 Platform Comparison

| Feature | Local | GKE | DigitalOcean |
|---------|-------|-----|--------------|
| **Setup Time** | 5 min | 15 min | 10 min |
| **Cost/Month** | $0 | $240-400 | $120-200 |
| **Production Ready** | ❌ | ✅✅✅ | ✅✅ |
| **Istio Service Mesh** | ⚠️ Manual | ✅ Native | ⚠️ Manual |
| **Auto-scaling** | ❌ | ✅ Autopilot | ✅ HPA |
| **Monitoring** | ⚠️ Optional | ✅ Cloud Ops | ✅ Prometheus |
| **Backups** | ❌ | ✅ Velero+GCS | ✅ Velero+Spaces |
| **Multi-region** | ❌ | ✅ | ⚠️ Manual |
| **SLA** | N/A | 99.95% | 99.95% |
| **Best For** | Dev/Test | Enterprise | Startups |

---

## 🏗️ Architecture by Platform

### Local Architecture

```
┌─────────────────────────────────────────┐
│  Local Machine (Docker Desktop/VM)     │
├─────────────────────────────────────────┤
│  minikube / kind / docker-desktop      │
│  ├─ bcm-platform namespace             │
│  │  ├─ PostgreSQL (1 pod)              │
│  │  ├─ Redis (1 pod)                   │
│  │  ├─ Orchestration Service (1 pod)  │
│  │  └─ BCM Services (3 pods)           │
│  └─ Port-forward to localhost:8002     │
└─────────────────────────────────────────┘
```

**Features:**
- Single-node cluster
- Minimal resources (4 CPU, 8GB RAM)
- Port-forwarding for access
- No external LoadBalancer

---

### GKE Architecture

```
┌─────────────────────────────────────────────────────┐
│  Google Cloud Platform                              │
├─────────────────────────────────────────────────────┤
│  GKE Autopilot Cluster (Multi-zone HA)            │
│  ├─ Istio Service Mesh                             │
│  │  ├─ Ingress Gateway (LoadBalancer)             │
│  │  ├─ mTLS between all services                  │
│  │  └─ Circuit breaking, retries                  │
│  ├─ bcm-platform namespace                         │
│  │  ├─ Orchestration (3-10 pods, HPA)            │
│  │  └─ BCM Services (2-5 pods each, HPA)         │
│  ├─ Cloud Operations (Monitoring/Logging)          │
│  ├─ Cloud Storage (Velero backups)                │
│  └─ Cloud Armor (DDoS protection)                  │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Multi-zone HA control plane
- Auto-scaling nodes (Autopilot)
- Native Istio integration
- Cloud Operations monitoring
- Automated backups to GCS
- 99.95% SLA

---

### DigitalOcean Architecture

```
┌─────────────────────────────────────────────────────┐
│  DigitalOcean Cloud                                 │
├─────────────────────────────────────────────────────┤
│  DOKS Cluster (HA control plane)                   │
│  ├─ ingress-nginx (LoadBalancer)                   │
│  ├─ cert-manager (Let's Encrypt TLS)               │
│  ├─ bcm-platform namespace                         │
│  │  ├─ Orchestration (3-10 pods, HPA)            │
│  │  └─ BCM Services (2-5 pods each, HPA)         │
│  ├─ Prometheus + Grafana (Monitoring)             │
│  ├─ DigitalOcean Spaces (Velero backups)          │
│  └─ DigitalOcean Container Registry               │
└─────────────────────────────────────────────────────┘
```

**Features:**
- HA control plane (free)
- Auto-scaling worker nodes
- LoadBalancer ($12/month)
- Prometheus/Grafana monitoring
- Velero backups to Spaces
- 99.95% SLA

---

## 📂 Directory Structure

```
AI-Platform-ISO/
├── infrastructure/
│   ├── kubernetes/                    # Kubernetes manifests
│   │   ├── scripts/
│   │   │   ├── local-setup.sh        # Local cluster setup
│   │   │   ├── local-deploy.sh       # Local deployment
│   │   │   ├── deploy-multi-platform.sh  # ✨ Unified deployment
│   │   │   ├── switch-context.sh     # ✨ Context switcher
│   │   │   ├── deploy-production.sh  # Production deploy
│   │   │   ├── smoke-tests.sh        # Smoke tests
│   │   │   └── port-forward-local.sh # Port forwarding
│   │   ├── deployments/              # K8s deployments
│   │   ├── configmaps/               # ConfigMaps
│   │   ├── secrets/                  # Secret templates
│   │   ├── monitoring/               # ServiceMonitors
│   │   ├── istio/                    # Istio configs
│   │   └── argocd/                   # GitOps configs
│   │
│   ├── deployment/                    # ✨ Platform-specific deployments
│   │   ├── gke/                      # ✨ GKE deployment (14 files)
│   │   │   ├── README.md
│   │   │   ├── QUICK_START.md
│   │   │   ├── gke-create-cluster.sh
│   │   │   ├── gke-configure.sh
│   │   │   ├── gke-install-addons.sh
│   │   │   ├── gke-deploy-bcm.sh
│   │   │   ├── velero-setup.sh
│   │   │   └── terraform.tfvars.example
│   │   │
│   │   └── digitalocean/             # ✨ DigitalOcean deployment (15 files)
│   │       ├── README.md
│   │       ├── QUICKSTART.md
│   │       ├── do-create-cluster.sh
│   │       ├── do-configure.sh
│   │       ├── do-install-addons.sh
│   │       ├── do-deploy-bcm.sh
│   │       ├── main.tf               # Terraform config
│   │       └── terraform.tfvars.example
│   │
│   └── terraform/
│       └── gke/                       # GKE Terraform modules
│           └── main.tf
│
├── .github/
│   └── workflows/
│       └── deploy-multi-platform.yml  # ✨ Multi-platform CI/CD
│
└── MULTI_PLATFORM_DEPLOYMENT_GUIDE.md  # ✨ This file
```

**✨ = New in v3.0.0**

---

## 🚀 Deployment Scenarios

### Scenario 1: Local Development Only

```bash
# Day 1: Setup
./infrastructure/kubernetes/scripts/local-setup.sh minikube
./infrastructure/kubernetes/scripts/local-deploy.sh

# Daily workflow
./infrastructure/kubernetes/scripts/port-forward-local.sh &
curl http://localhost:8002/health

# Cleanup
kubectl delete namespace bcm-platform
minikube stop
```

**Use when:** Developing features, testing locally

---

### Scenario 2: Local + Cloud Staging

```bash
# Local development
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh local

# Deploy to cloud staging
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh digitalocean \
  --token $DO_TOKEN \
  --environment staging

# Switch between them
./infrastructure/kubernetes/scripts/switch-context.sh minikube       # Local
./infrastructure/kubernetes/scripts/switch-context.sh do-staging     # Cloud
```

**Use when:** Need to test cloud features before production

---

### Scenario 3: Multi-Cloud Production (Recommended)

```bash
# Primary production: GKE
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh gke \
  --project prod-project \
  --region us-central1

# Backup production: DigitalOcean
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh digitalocean \
  --token $DO_TOKEN \
  --region nyc3

# Manage both
k8s-gke && bcm-status       # Check GKE
k8s-do && bcm-status        # Check DO
```

**Use when:** Need high availability, disaster recovery, geographic distribution

---

## 🔐 Secrets Management

### Local Development

```bash
# Local secrets (auto-generated, NOT secure)
kubectl get secret orchestration-secrets -n bcm-platform -o yaml
```

### GKE Production

```bash
# Use Google Secret Manager
gcloud secrets create anthropic-api-key --data-file=-
kubectl create secret generic orchestration-secrets \
  --from-literal=ANTHROPIC_API_KEY="$(gcloud secrets versions access latest --secret=anthropic-api-key)"
```

### DigitalOcean Production

```bash
# Use External Secrets Operator or Sealed Secrets
# See: infrastructure/deployment/digitalocean/README.md
```

---

## 📈 Monitoring & Observability

### Local

```bash
# Access Grafana (if installed)
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
# Open: http://localhost:3000 (admin/admin)
```

### GKE

```bash
# Cloud Monitoring (built-in)
# Open: https://console.cloud.google.com/monitoring

# Or port-forward Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
```

### DigitalOcean

```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

---

## 💰 Cost Comparison

### Local Development: **$0/month**

- Runs on your laptop/desktop
- No cloud costs
- Limited by local resources

---

### GKE Production: **$240-400/month**

**Breakdown:**
- GKE Autopilot compute: $180-300/month
- Cloud Storage (backups): $5/month
- Load Balancer: $18/month
- Network egress: $10-50/month
- Monitoring: Included

**Optimization:**
- Use Preemptible nodes: -60% cost
- Use committed use discounts: -30% cost
- Right-size workloads: -20% cost

**Reduced cost:** ~$150/month with optimizations

---

### DigitalOcean: **$120-200/month**

**Breakdown:**
- 3x s-4vcpu-8gb nodes: $144/month
- HA control plane: Free
- Load Balancer: $12/month
- Block Storage: $5/month
- Spaces (backups): $5/month
- Container Registry: $20/month

**Optimization:**
- Use smaller nodes: -40% cost
- Scale down non-peak: -20% cost

**Reduced cost:** ~$90/month with optimizations

---

## 🔄 CI/CD Integration

### GitHub Actions (Included)

```bash
# File: .github/workflows/deploy-multi-platform.yml

# Manual trigger
gh workflow run deploy-multi-platform.yml \
  -f platform=gke \
  -f environment=production

# Automatic on push to main
git push origin main  # Auto-deploys to both platforms
```

### GitLab CI (Template)

```yaml
# .gitlab-ci.yml
deploy-gke:
  stage: deploy
  script:
    - ./infrastructure/kubernetes/scripts/deploy-multi-platform.sh gke --project $GCP_PROJECT
  only:
    - main

deploy-do:
  stage: deploy
  script:
    - ./infrastructure/kubernetes/scripts/deploy-multi-platform.sh digitalocean --token $DO_TOKEN
  only:
    - main
```

---

## 🆘 Troubleshooting

### Issue: Context switching fails

```bash
# Verify contexts exist
kubectl config get-contexts

# Manually switch
kubectl config use-context <context-name>

# Verify connection
kubectl cluster-info
```

---

### Issue: Local cluster not accessible

```bash
# Restart minikube
minikube stop
minikube start

# Or recreate kind cluster
kind delete cluster --name bcm-platform
./infrastructure/kubernetes/scripts/local-setup.sh kind
```

---

### Issue: GKE deployment fails

```bash
# Check authentication
gcloud auth list
gcloud config set project <project-id>

# Check cluster status
gcloud container clusters list
gcloud container clusters describe <cluster-name> --region <region>

# Get fresh credentials
gcloud container clusters get-credentials <cluster-name> --region <region>
```

---

### Issue: DigitalOcean deployment fails

```bash
# Re-authenticate
doctl auth init

# Check cluster status
doctl kubernetes cluster list
doctl kubernetes cluster get <cluster-name>

# Get fresh credentials
doctl kubernetes cluster kubeconfig save <cluster-name>
```

---

## 📚 Documentation Index

### Quick References
- **This Guide** - Multi-platform overview (you are here)
- [Local Development](kubernetes/scripts/local-setup.sh) - Local setup script
- [Unified Deployment](kubernetes/scripts/deploy-multi-platform.sh) - Multi-platform script
- [Context Switcher](kubernetes/scripts/switch-context.sh) - Context management

### Platform-Specific Guides
- [GKE Complete Guide](deployment/gke/README.md) - 828 lines, comprehensive
- [GKE Quick Start](deployment/gke/QUICK_START.md) - 5-minute guide
- [DigitalOcean Complete Guide](deployment/digitalocean/README.md) - 828 lines
- [DigitalOcean Quick Start](deployment/digitalocean/QUICKSTART.md) - 30-minute guide

### Advanced Topics
- [Phase 3.1 Features](kubernetes/PHASE_3.1_ADVANCED_FEATURES.md) - Istio, ArgoCD, Velero
- [Production Checklist](kubernetes/PRODUCTION_DEPLOYMENT_CHECKLIST.md) - Pre-flight checks
- [Terraform Guide](deployment/digitalocean/TERRAFORM_GUIDE.md) - Infrastructure as Code

---

## 🎯 Next Steps

### For New Users

1. **Start local:**
   ```bash
   ./infrastructure/kubernetes/scripts/local-setup.sh minikube
   ./infrastructure/kubernetes/scripts/local-deploy.sh
   ```

2. **Learn context switching:**
   ```bash
   ./infrastructure/kubernetes/scripts/switch-context.sh --aliases
   ```

3. **Choose cloud platform:**
   - Budget-conscious → DigitalOcean
   - Enterprise features → GKE

---

### For Production Deployment

1. **Review** [Production Checklist](kubernetes/PRODUCTION_DEPLOYMENT_CHECKLIST.md)

2. **Choose platform** and deploy:
   ```bash
   # GKE
   cd infrastructure/deployment/gke
   ./gke-create-cluster.sh

   # OR DigitalOcean
   cd infrastructure/deployment/digitalocean
   ./do-create-cluster.sh
   ```

3. **Set up monitoring** (included in deployment)

4. **Configure backups:**
   ```bash
   # GKE
   ./velero-setup.sh

   # DigitalOcean
   # Follow instructions in deployment/digitalocean/README.md
   ```

5. **Set up CI/CD** - GitHub Actions already configured

---

### For Multi-Cloud Setup

1. **Deploy to GKE** (primary)
2. **Deploy to DigitalOcean** (backup)
3. **Set up DNS** with failover
4. **Configure Velero** cross-region backups
5. **Test disaster recovery**

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] All pods running: `kubectl get pods -n bcm-platform`
- [ ] Services have endpoints: `kubectl get svc -n bcm-platform`
- [ ] Health checks passing: `kubectl get pods -n bcm-platform | grep Running`
- [ ] Smoke tests passing: `./infrastructure/kubernetes/scripts/smoke-tests.sh bcm-platform`
- [ ] Monitoring accessible
- [ ] Backups configured (production only)
- [ ] Context switching works: `./infrastructure/kubernetes/scripts/switch-context.sh --list`

---

## 🤝 Support

### Documentation
- Local: [local-setup.sh](kubernetes/scripts/local-setup.sh)
- GKE: [deployment/gke/README.md](deployment/gke/README.md)
- DigitalOcean: [deployment/digitalocean/README.md](deployment/digitalocean/README.md)

### Official Support
- **GKE**: https://cloud.google.com/kubernetes-engine/docs/support
- **DigitalOcean**: https://docs.digitalocean.com/products/kubernetes/
- **Kubernetes**: https://kubernetes.io/docs/

---

**Created:** October 21, 2025
**Author:** Claude Code
**Version:** 3.0.0 - Multi-Platform Support
**License:** SEH Foundation

---

*Ready for deployment to any platform! 🚀*
