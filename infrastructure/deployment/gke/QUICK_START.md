# GKE Deployment - Quick Start Guide

5-minute setup guide for deploying BCM Platform on Google Kubernetes Engine.

## Prerequisites Check

```bash
# Verify gcloud is installed
gcloud version

# Verify kubectl is installed
kubectl version --client

# Verify you're authenticated
gcloud auth list

# Verify your project is set
gcloud config get-value project
```

## Step-by-Step Deployment

### 1. Configure (2 minutes)

```bash
cd infrastructure/deployment/gke

# Copy and edit configuration
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Update project_id, cluster_name, region
```

**Minimum required changes in terraform.tfvars:**
- `project_id = "your-gcp-project-id"`

### 2. Create Cluster (10-15 minutes)

```bash
./gke-create-cluster.sh
```

**What this does:**
- Enables required GCP APIs
- Creates GKE Autopilot cluster
- Configures private networking
- Enables monitoring & logging

**Wait for completion** - GKE cluster creation takes 10-15 minutes.

### 3. Configure kubectl (1 minute)

```bash
./gke-configure.sh
```

**Verify it worked:**
```bash
kubectl get nodes
kubectl cluster-info
```

### 4. Install Add-ons (5 minutes)

```bash
./gke-install-addons.sh
```

**What this installs:**
- Istio Service Mesh v1.20.2
- Verifies Cloud Operations
- Optional: Kubernetes Dashboard

### 5. Deploy BCM Platform (2 minutes)

```bash
./gke-deploy-bcm.sh
```

**Check deployment status:**
```bash
kubectl get pods -n bcm-platform
kubectl get services -n bcm-platform
```

### 6. Setup Backups (5 minutes)

```bash
./velero-setup.sh
```

**Verify backups:**
```bash
velero backup get
velero schedule get
```

## Get Application URL

```bash
# Get LoadBalancer IP
kubectl get svc -n bcm-platform bcm-platform -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Or use this one-liner
export BCM_IP=$(kubectl get svc -n bcm-platform bcm-platform -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "BCM Platform: http://$BCM_IP"
```

## Verify Everything Works

```bash
# Check cluster health
kubectl get nodes
kubectl get pods --all-namespaces

# Check BCM Platform
kubectl get all -n bcm-platform

# Check Istio
kubectl get pods -n istio-system

# Check Velero
velero version
velero backup get
```

## Common Commands

```bash
# View logs
kubectl logs -n bcm-platform -l app=bcm-platform --tail=50

# Scale deployment (Autopilot auto-scales, but you can set replicas)
kubectl scale deployment/bcm-platform -n bcm-platform --replicas=5

# Update deployment
kubectl set image deployment/bcm-platform bcm-platform=gcr.io/PROJECT_ID/bcm-platform:v2 -n bcm-platform

# Create manual backup
velero backup create manual-backup-$(date +%Y%m%d) --include-namespaces bcm-platform

# Port forward for local testing
kubectl port-forward -n bcm-platform svc/bcm-platform 8080:80
```

## Troubleshooting

### Cluster creation fails
```bash
# Check API status
gcloud services list --enabled | grep container

# Check quotas
gcloud compute project-info describe --project=PROJECT_ID

# View detailed error
gcloud container clusters describe CLUSTER_NAME --region=REGION
```

### Pods not starting
```bash
# Check events
kubectl get events -n bcm-platform --sort-by='.lastTimestamp'

# Describe pod
kubectl describe pod POD_NAME -n bcm-platform

# View logs
kubectl logs POD_NAME -n bcm-platform
```

### Can't connect to cluster
```bash
# Re-fetch credentials
gcloud container clusters get-credentials CLUSTER_NAME --region=REGION

# Check context
kubectl config current-context
```

## Clean Up (Delete Everything)

⚠️ **WARNING:** This will delete your cluster and all data!

```bash
# Delete cluster
gcloud container clusters delete CLUSTER_NAME --region=REGION

# Delete Velero backup bucket (optional)
gsutil -m rm -r gs://BUCKET_NAME

# Delete service account (optional)
gcloud iam service-accounts delete velero@PROJECT_ID.iam.gserviceaccount.com
```

## Cost Estimation

**GKE Autopilot Pricing** (approximate):
- Small deployment (3 pods, 1 CPU, 2GB RAM): ~$50-100/month
- Medium deployment (10 pods, 5 CPU, 10GB RAM): ~$200-400/month
- Large deployment (50 pods, 20 CPU, 40GB RAM): ~$800-1500/month

**Additional costs:**
- Cloud Storage (backups): ~$0.02/GB/month
- Network egress: Variable
- Cloud Operations: Included

**Calculate your costs:** https://cloud.google.com/products/calculator

## Next Steps

1. ✅ Cluster running
2. ✅ Application deployed
3. ✅ Backups configured

**Now:**
- [ ] Configure custom domain and SSL
- [ ] Set up monitoring alerts
- [ ] Configure CI/CD pipeline
- [ ] Security hardening
- [ ] Performance optimization

## Getting Help

- **Documentation**: See `README.md` for detailed information
- **GKE Docs**: https://cloud.google.com/kubernetes-engine/docs
- **Kubernetes Docs**: https://kubernetes.io/docs
- **Istio Docs**: https://istio.io/latest/docs
- **Velero Docs**: https://velero.io/docs
