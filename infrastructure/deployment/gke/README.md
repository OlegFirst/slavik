# GKE Deployment Guide for BCM Platform

Complete deployment setup for BCM Platform on Google Kubernetes Engine (GKE) using official Google Cloud SDK (gcloud).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Velero Backup Setup](#velero-backup-setup)
- [Monitoring and Operations](#monitoring-and-operations)
- [Troubleshooting](#troubleshooting)
- [References](#references)

---

## Prerequisites

### Required Tools

1. **Google Cloud SDK (gcloud CLI)**
   - Installation: https://cloud.google.com/sdk/docs/install
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Linux
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL

   # Windows
   # Download from https://cloud.google.com/sdk/docs/install
   ```

2. **kubectl**
   - Installation: https://kubernetes.io/docs/tasks/tools/
   ```bash
   # Install via gcloud
   gcloud components install kubectl

   # Or via package manager
   # macOS: brew install kubectl
   # Linux: snap install kubectl --classic
   ```

3. **gke-gcloud-auth-plugin**
   ```bash
   gcloud components install gke-gcloud-auth-plugin
   ```

4. **Velero CLI** (for backups)
   - Installation: https://velero.io/docs/main/basic-install/
   ```bash
   # macOS
   brew install velero

   # Linux
   wget https://github.com/vmware-tanzu/velero/releases/latest/download/velero-linux-amd64.tar.gz
   tar -xvf velero-linux-amd64.tar.gz
   sudo mv velero-linux-amd64/velero /usr/local/bin/
   ```

### Google Cloud Setup

1. **Create a GCP Project**
   - Go to: https://console.cloud.google.com/
   - Create a new project or select an existing one
   - Note your Project ID

2. **Enable Billing**
   - Ensure billing is enabled: https://console.cloud.google.com/billing

3. **Authenticate with gcloud**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Set Default Region (Optional)**
   ```bash
   gcloud config set compute/region us-central1
   gcloud config set compute/zone us-central1-a
   ```

---

## Quick Start

### 1. Configure Your Deployment

Copy the example configuration file and update with your values:

```bash
cd infrastructure/deployment/gke
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set at minimum:
- `project_id` - Your GCP Project ID
- `cluster_name` - Desired cluster name
- `region` - GCP region for deployment

### 2. Create GKE Cluster

```bash
chmod +x *.sh
./gke-create-cluster.sh
```

This creates a GKE Autopilot cluster with:
- Autopilot mode (Google-managed nodes)
- Private nodes and endpoints
- Cloud Operations (monitoring & logging)
- Auto-scaling and auto-upgrade enabled

**Official Reference:** https://cloud.google.com/sdk/gcloud/reference/container/clusters/create-auto

### 3. Configure kubectl Access

```bash
./gke-configure.sh
```

**Official Reference:** https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials

### 4. Install Add-ons

```bash
./gke-install-addons.sh
```

Installs:
- Istio Service Mesh
- Verifies Cloud Operations (built-in)
- Optional: Kubernetes Dashboard

**Istio Reference:** https://istio.io/latest/docs/setup/getting-started/

### 5. Deploy BCM Platform

```bash
./gke-deploy-bcm.sh
```

Deploys the BCM Platform to your GKE cluster.

### 6. Setup Velero Backups

```bash
./velero-setup.sh
```

**Velero Reference:** https://velero.io/docs/main/gcp-config/

---

## Detailed Setup

### Step 1: Create GKE Autopilot Cluster

The `gke-create-cluster.sh` script uses the following official gcloud command:

```bash
gcloud container clusters create-auto CLUSTER_NAME \
    --region=REGION \
    --release-channel=RELEASE_CHANNEL \
    --network=NETWORK \
    --subnetwork=SUBNETWORK \
    --enable-private-nodes \
    --enable-private-endpoint \
    --enable-master-authorized-networks \
    --enable-stackdriver-kubernetes \
    --logging=SYSTEM,WORKLOAD \
    --monitoring=SYSTEM
```

**Key Features:**

- **Autopilot Mode**: Google manages nodes, scaling, security
- **Private Cluster**: Enhanced security with private nodes
- **Cloud Operations**: Built-in monitoring and logging
- **Auto-upgrade**: Automatic Kubernetes version updates
- **Release Channels**:
  - `rapid` - Latest features, weekly updates
  - `regular` - Balanced stability/features (default)
  - `stable` - Maximum stability, less frequent updates

**Official Documentation:**
- Command Reference: https://cloud.google.com/sdk/gcloud/reference/container/clusters/create-auto
- Autopilot Overview: https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview
- Creating Autopilot Clusters: https://cloud.google.com/kubernetes-engine/docs/how-to/creating-an-autopilot-cluster

### Step 2: Configure kubectl Access

The `gke-configure.sh` script uses:

```bash
gcloud container clusters get-credentials CLUSTER_NAME \
    --region=REGION \
    --project=PROJECT_ID
```

This command:
1. Fetches cluster credentials
2. Updates your `~/.kube/config`
3. Configures authentication
4. Sets the current kubectl context

**Official Documentation:**
- Command Reference: https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials
- Cluster Access: https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl

### Step 3: Install Istio Service Mesh

The `gke-install-addons.sh` script downloads and installs Istio:

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.20.2 sh -

# Install Istio
istioctl install --set profile=default -y

# Enable sidecar injection
kubectl label namespace default istio-injection=enabled
```

**Istio Profiles:**
- `default` - Production ready, recommended for most deployments
- `demo` - Development/testing with additional features
- `minimal` - Minimal control plane components
- `remote` - Multicluster mesh deployments

**Official Documentation:**
- Istio on GKE: https://istio.io/latest/docs/setup/platform-setup/gke/
- Istio Installation: https://istio.io/latest/docs/setup/install/istioctl/
- GKE Istio Tutorial: https://cloud.google.com/kubernetes-engine/docs/tutorials/secure-services-istio

### Step 4: Cloud Operations (Monitoring & Logging)

GKE Autopilot includes Cloud Operations by default:

- **Cloud Monitoring** - Metrics, dashboards, alerts
- **Cloud Logging** - Centralized log management
- **Cloud Trace** - Distributed tracing
- **Cloud Profiler** - CPU/memory profiling

View your cluster's monitoring:
```bash
# Get monitoring service
gcloud container clusters describe CLUSTER_NAME \
    --region=REGION \
    --format="value(monitoringService)"

# Access Cloud Console
# Monitoring: https://console.cloud.google.com/monitoring
# Logging: https://console.cloud.google.com/logs
```

**Official Documentation:**
- Cloud Operations for GKE: https://cloud.google.com/kubernetes-engine/docs/how-to/monitoring
- Cloud Monitoring: https://cloud.google.com/monitoring/docs
- Cloud Logging: https://cloud.google.com/logging/docs

### Step 5: Deploy BCM Platform

The `gke-deploy-bcm.sh` script:

1. Creates BCM namespace
2. Enables Istio injection
3. Creates secrets and ConfigMaps
4. Deploys Kubernetes manifests
5. Exposes services via LoadBalancer

**Key Kubernetes Resources:**

```yaml
# Namespace with Istio injection
apiVersion: v1
kind: Namespace
metadata:
  name: bcm-platform
  labels:
    istio-injection: enabled

# Deployment with resource requests
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bcm-platform
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: bcm-platform
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Official Documentation:**
- Kubernetes Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- GKE Workloads: https://cloud.google.com/kubernetes-engine/docs/how-to/deploying-workloads

---

## Velero Backup Setup

### Overview

Velero provides disaster recovery for Kubernetes clusters by backing up cluster resources and persistent volumes to Google Cloud Storage.

**Official Reference:** https://velero.io/docs/main/gcp-config/

### Setup Steps

The `velero-setup.sh` script automates:

1. **Create GCS Bucket**
   ```bash
   gsutil mb -p PROJECT_ID -l REGION gs://BUCKET_NAME/
   gsutil versioning set on gs://BUCKET_NAME/
   ```

2. **Create Service Account**
   ```bash
   gcloud iam service-accounts create velero \
       --display-name "Velero service account"
   ```

3. **Create Custom IAM Role**

   Required permissions:
   - `compute.disks.get`
   - `compute.disks.create`
   - `compute.disks.createSnapshot`
   - `compute.snapshots.get`
   - `compute.snapshots.create`
   - `compute.snapshots.useReadOnly`
   - `compute.snapshots.delete`
   - `compute.zones.get`

   ```bash
   gcloud iam roles create velero.server \
       --project=PROJECT_ID \
       --file=velero-role.yaml
   ```

4. **Bind IAM Roles**
   ```bash
   # Bind custom role
   gcloud projects add-iam-policy-binding PROJECT_ID \
       --member=serviceAccount:velero@PROJECT_ID.iam.gserviceaccount.com \
       --role=projects/PROJECT_ID/roles/velero.server

   # Grant bucket access
   gsutil iam ch serviceAccount:velero@PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://BUCKET_NAME
   ```

5. **Create Service Account Key**
   ```bash
   gcloud iam service-accounts keys create credentials-velero.json \
       --iam-account=velero@PROJECT_ID.iam.gserviceaccount.com
   ```

6. **Install Velero**
   ```bash
   velero install \
       --provider gcp \
       --plugins velero/velero-plugin-for-gcp:v1.9.0 \
       --bucket BUCKET_NAME \
       --secret-file ./credentials-velero.json \
       --use-volume-snapshots=true
   ```

7. **Create Backup Schedule**
   ```bash
   velero schedule create bcm-platform-daily \
       --schedule="0 2 * * *" \
       --ttl "30d" \
       --include-namespaces=bcm-platform
   ```

### Velero Operations

#### Create Manual Backup
```bash
velero backup create bcm-backup-$(date +%Y%m%d-%H%M%S) \
    --include-namespaces bcm-platform
```

#### List Backups
```bash
velero backup get
```

#### Describe Backup
```bash
velero backup describe BACKUP_NAME --details
```

#### Restore from Backup
```bash
velero restore create --from-backup BACKUP_NAME
```

#### Monitor Backup
```bash
velero backup logs BACKUP_NAME
```

#### Delete Old Backups
```bash
velero backup delete BACKUP_NAME
```

**Official Documentation:**
- Velero Documentation: https://velero.io/docs/
- GCP Plugin: https://github.com/vmware-tanzu/velero-plugin-for-gcp
- Backup Reference: https://velero.io/docs/main/backup-reference/

---

## Monitoring and Operations

### Cloud Console Access

- **GKE Dashboard**: https://console.cloud.google.com/kubernetes/list
- **Cloud Monitoring**: https://console.cloud.google.com/monitoring
- **Cloud Logging**: https://console.cloud.google.com/logs
- **Cloud Trace**: https://console.cloud.google.com/traces
- **Cloud Storage (Backups)**: https://console.cloud.google.com/storage

### kubectl Commands

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes
kubectl top nodes

# Workloads
kubectl get all -n bcm-platform
kubectl get pods -n bcm-platform -o wide
kubectl top pods -n bcm-platform

# Services and endpoints
kubectl get services -n bcm-platform
kubectl get ingress -n bcm-platform

# Logs
kubectl logs -n bcm-platform -l app=bcm-platform --tail=100
kubectl logs -n bcm-platform POD_NAME --follow

# Events
kubectl get events -n bcm-platform --sort-by='.lastTimestamp'

# Resource usage
kubectl describe node NODE_NAME
kubectl describe pod -n bcm-platform POD_NAME
```

### gcloud Commands

```bash
# Cluster status
gcloud container clusters describe CLUSTER_NAME --region=REGION

# List clusters
gcloud container clusters list

# Resize cluster (not applicable to Autopilot)
# Autopilot auto-scales automatically

# Get credentials
gcloud container clusters get-credentials CLUSTER_NAME --region=REGION

# Update cluster
gcloud container clusters update CLUSTER_NAME --region=REGION

# Delete cluster
gcloud container clusters delete CLUSTER_NAME --region=REGION
```

### Istio Commands

```bash
# Check Istio installation
istioctl version
istioctl verify-install

# Analyze configuration
istioctl analyze -n bcm-platform

# View proxy configuration
istioctl proxy-config cluster POD_NAME -n bcm-platform

# Dashboard
istioctl dashboard kiali
istioctl dashboard prometheus
istioctl dashboard grafana
```

---

## Troubleshooting

### Common Issues

#### 1. gcloud Not Authenticated
```bash
# Error: (gcloud.container.clusters.create-auto) There was a problem refreshing your current auth tokens
gcloud auth login
gcloud auth application-default login
```

#### 2. kubectl Connection Issues
```bash
# Re-fetch credentials
gcloud container clusters get-credentials CLUSTER_NAME --region=REGION

# Verify current context
kubectl config current-context
kubectl config get-contexts

# Switch context
kubectl config use-context CONTEXT_NAME
```

#### 3. API Not Enabled
```bash
# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable monitoring.googleapis.com
```

#### 4. Insufficient Permissions
```bash
# Check current permissions
gcloud projects get-iam-policy PROJECT_ID

# Required roles for cluster creation:
# - roles/container.admin
# - roles/iam.serviceAccountUser
```

#### 5. Pods Not Starting (Autopilot)
```bash
# Check events
kubectl get events -n bcm-platform --sort-by='.lastTimestamp'

# Describe pod
kubectl describe pod POD_NAME -n bcm-platform

# Common Autopilot issues:
# - Resource requests not specified (required in Autopilot)
# - Invalid resource requests
# - SecurityContext violations
```

#### 6. Velero Backup Failures
```bash
# Check Velero logs
kubectl logs -n velero deployment/velero

# Describe backup
velero backup describe BACKUP_NAME --details

# Check service account permissions
gcloud projects get-iam-policy PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:velero@*"
```

### Debug Commands

```bash
# View cluster details
gcloud container clusters describe CLUSTER_NAME --region=REGION

# Check node pool status
kubectl get nodes -o wide

# View pod resource usage
kubectl top pods -n bcm-platform

# Check persistent volumes
kubectl get pv
kubectl get pvc -n bcm-platform

# View service endpoints
kubectl get endpoints -n bcm-platform

# Network troubleshooting
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- /bin/bash
```

### Logs and Monitoring

```bash
# View logs in Cloud Logging
gcloud logging read "resource.type=k8s_cluster AND resource.labels.cluster_name=CLUSTER_NAME" \
    --limit 50 \
    --format json

# View metrics in Cloud Monitoring
gcloud monitoring time-series list \
    --filter='resource.type="k8s_cluster" AND resource.labels.cluster_name="CLUSTER_NAME"'

# Export logs to file
kubectl logs -n bcm-platform POD_NAME > pod.log
```

---

## Cost Optimization

### GKE Autopilot Pricing

- **Autopilot charges** for vCPU, memory, and ephemeral storage requested by pods
- No charge for cluster management fee
- Includes OS, monitoring, logging at no extra cost

**Pricing Reference:** https://cloud.google.com/kubernetes-engine/pricing#autopilot_mode

### Cost Optimization Tips

1. **Right-size resource requests**
   ```yaml
   resources:
     requests:
       cpu: "100m"      # Start small
       memory: "128Mi"
   ```

2. **Use Spot VMs** (when available for Autopilot)
   ```bash
   # Currently limited in Autopilot, but check:
   gcloud container clusters describe CLUSTER_NAME --region=REGION
   ```

3. **Delete unused resources**
   ```bash
   kubectl delete deployment UNUSED_DEPLOYMENT -n bcm-platform
   kubectl delete service UNUSED_SERVICE -n bcm-platform
   ```

4. **Monitor costs**
   - Cloud Billing Reports: https://console.cloud.google.com/billing
   - Set up budget alerts

5. **Use Cloud Storage Lifecycle Policies**
   ```bash
   # For Velero backup bucket
   gsutil lifecycle set lifecycle.json gs://BUCKET_NAME
   ```

---

## Security Best Practices

### 1. Private Cluster
Already configured in scripts:
- Private nodes (no public IPs)
- Private endpoint (control plane not publicly accessible)
- Authorized networks for control plane access

### 2. Workload Identity
Enable Workload Identity for pod-to-GCP authentication:
```bash
gcloud container clusters update CLUSTER_NAME \
    --region=REGION \
    --workload-pool=PROJECT_ID.svc.id.goog
```

**Reference:** https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity

### 3. Secret Management
Use Google Secret Manager instead of Kubernetes Secrets:
```bash
gcloud secrets create bcm-database-password --data-file=-
```

**Reference:** https://cloud.google.com/secret-manager/docs

### 4. Network Policies
Enable network policies for pod-to-pod communication control:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bcm-network-policy
  namespace: bcm-platform
spec:
  podSelector:
    matchLabels:
      app: bcm-platform
  policyTypes:
  - Ingress
  - Egress
```

### 5. Binary Authorization
Enforce only signed container images:
```bash
gcloud container clusters update CLUSTER_NAME \
    --region=REGION \
    --enable-binauthz
```

**Reference:** https://cloud.google.com/binary-authorization/docs

---

## References

### Official Google Cloud Documentation

- **GKE Documentation**: https://cloud.google.com/kubernetes-engine/docs
- **gcloud SDK Reference**: https://cloud.google.com/sdk/gcloud/reference
- **GKE Autopilot**: https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview
- **Cloud Operations**: https://cloud.google.com/kubernetes-engine/docs/how-to/monitoring

### Official Command References

- **gcloud container clusters create-auto**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/create-auto
- **gcloud container clusters get-credentials**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials
- **gcloud services enable**: https://cloud.google.com/sdk/gcloud/reference/services/enable

### Third-Party Tools

- **Istio Documentation**: https://istio.io/latest/docs/
- **Velero Documentation**: https://velero.io/docs/
- **Kubernetes Documentation**: https://kubernetes.io/docs/

### Guides and Tutorials

- **Creating Autopilot Clusters**: https://cloud.google.com/kubernetes-engine/docs/how-to/creating-an-autopilot-cluster
- **Cluster Access**: https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl
- **Istio on GKE Tutorial**: https://cloud.google.com/kubernetes-engine/docs/tutorials/secure-services-istio
- **Velero GCP Setup**: https://velero.io/docs/main/gcp-config/

---

## Next Steps

After completing the deployment:

1. **Configure DNS** - Point your domain to the LoadBalancer IP
2. **Setup SSL/TLS** - Configure HTTPS with Google-managed certificates
3. **Configure Monitoring** - Set up custom dashboards and alerts
4. **Setup CI/CD** - Integrate with Cloud Build or GitHub Actions
5. **Test Backups** - Perform a test restore from Velero backup
6. **Security Hardening** - Implement all security best practices
7. **Performance Tuning** - Optimize resource requests based on usage

---

## Support

For issues and questions:

- **GKE Issues**: https://cloud.google.com/kubernetes-engine/docs/support
- **gcloud CLI**: https://cloud.google.com/sdk/docs/troubleshooting
- **Istio**: https://istio.io/latest/docs/ops/common-problems/
- **Velero**: https://velero.io/docs/main/troubleshooting/

---

## License

This deployment configuration follows Google Cloud's terms of service and Kubernetes open-source license.
