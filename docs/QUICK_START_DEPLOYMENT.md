# BCM Platform - Quick Start Deployment

**Choose your platform and get started in minutes!**

---

## 🚀 Option 1: Local Development (5 minutes)

Perfect for testing and development on your laptop.

```bash
# 1. Setup local Kubernetes
./infrastructure/kubernetes/scripts/local-setup.sh minikube

# 2. Deploy BCM Platform
./infrastructure/kubernetes/scripts/local-deploy.sh

# 3. Access the platform
./infrastructure/kubernetes/scripts/port-forward-local.sh &

# 4. Test health endpoint
curl http://localhost:8002/health
```

**Done!** BCM Platform is running locally.

**Cost:** $0/month

---

## ☁️ Option 2: Google Cloud (GKE) - 15 minutes

Best for production with maximum features.

```bash
# 1. Configure
cd infrastructure/deployment/gke
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Add your GCP project ID

# 2. Deploy everything
./gke-create-cluster.sh      # Creates cluster (10 min)
./gke-configure.sh           # Configures kubectl
./gke-install-addons.sh      # Installs Istio, monitoring
./gke-deploy-bcm.sh          # Deploys BCM Platform

# 3. Get access URL
kubectl get ingress -n bcm-platform
```

**Done!** Production-ready BCM Platform on GKE.

**Cost:** ~$240/month (optimized ~$150/month)

---

## 🌊 Option 3: DigitalOcean (10 minutes)

Most affordable cloud option, perfect for startups.

```bash
# 1. Get DigitalOcean token
# https://cloud.digitalocean.com/account/api/tokens

# 2. Deploy everything
cd infrastructure/deployment/digitalocean
export DIGITALOCEAN_ACCESS_TOKEN="your-token-here"

./do-create-cluster.sh       # Creates cluster (8 min)
./do-configure.sh            # Configures kubectl
./do-install-addons.sh       # Installs ingress, cert-manager
./do-deploy-bcm.sh           # Deploys BCM Platform

# 3. Get LoadBalancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

**Done!** Production BCM Platform on DigitalOcean.

**Cost:** ~$120/month (optimized ~$90/month)

---

## 🔄 Unified Deployment (Any Platform)

Use ONE command for any platform:

```bash
# Local
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh local

# GKE
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh gke \
  --project my-gcp-project

# DigitalOcean
./infrastructure/kubernetes/scripts/deploy-multi-platform.sh digitalocean \
  --token $DO_TOKEN
```

---

## 🔀 Switch Between Platforms

```bash
# Interactive menu
./infrastructure/kubernetes/scripts/switch-context.sh

# Direct switch
./infrastructure/kubernetes/scripts/switch-context.sh minikube
./infrastructure/kubernetes/scripts/switch-context.sh gke_project_region_cluster
./infrastructure/kubernetes/scripts/switch-context.sh do-bcm-platform

# Install shell aliases
./infrastructure/kubernetes/scripts/switch-context.sh --aliases
source ~/.bashrc  # or ~/.zshrc

# Use aliases
k8s-local      # Switch to local
k8s-gke        # Switch to GKE
k8s-do         # Switch to DigitalOcean
bcm-status     # Check status
bcm-logs       # View logs
```

---

## 📊 Platform Comparison

| | Local | GKE | DigitalOcean |
|---|---|---|---|
| **Time** | 5 min | 15 min | 10 min |
| **Cost** | $0 | $240/mo | $120/mo |
| **Production** | ❌ | ✅✅✅ | ✅✅ |
| **Best For** | Dev/Test | Enterprise | Startups |

---

## ✅ Verify Deployment

```bash
# Check pods
kubectl get pods -n bcm-platform

# Run smoke tests
./infrastructure/kubernetes/scripts/smoke-tests.sh bcm-platform

# Check health
kubectl exec -n bcm-platform deployment/orchestration-service -- \
  curl -f http://localhost:8002/health
```

---

## 📚 Full Documentation

- **Complete Guide:** [MULTI_PLATFORM_DEPLOYMENT_GUIDE.md](infrastructure/MULTI_PLATFORM_DEPLOYMENT_GUIDE.md)
- **GKE Guide:** [infrastructure/deployment/gke/README.md](infrastructure/deployment/gke/README.md)
- **DigitalOcean Guide:** [infrastructure/deployment/digitalocean/README.md](infrastructure/deployment/digitalocean/README.md)
- **Kubernetes Docs:** [infrastructure/kubernetes/README.md](infrastructure/kubernetes/README.md)

---

## 🆘 Quick Troubleshooting

### Pods not starting?
```bash
kubectl describe pod -n bcm-platform <pod-name>
kubectl logs -n bcm-platform <pod-name>
```

### Context issues?
```bash
kubectl config get-contexts
kubectl config use-context <context-name>
```

### Need to start over?
```bash
# Local
kubectl delete namespace bcm-platform
minikube delete

# Cloud
kubectl delete namespace bcm-platform
# (cluster remains, just redeploy)
```

---

## 🎯 What's Next?

1. **Deploy** using one of the options above
2. **Verify** with smoke tests
3. **Explore** the platform via API or UI
4. **Monitor** with Grafana/Prometheus
5. **Set up CI/CD** (GitHub Actions included)

---

**Ready? Pick your platform above and deploy! 🚀**

**Questions?** Check the [Full Guide](infrastructure/MULTI_PLATFORM_DEPLOYMENT_GUIDE.md)
