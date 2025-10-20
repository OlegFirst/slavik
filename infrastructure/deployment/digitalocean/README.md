# DigitalOcean Kubernetes (DOKS) Deployment Guide

Complete deployment setup for BCM Platform on DigitalOcean Kubernetes using **official doctl SDK**.

## Official Documentation References

- **doctl Kubernetes Reference**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/
- **DOKS Product Docs**: https://docs.digitalocean.com/products/kubernetes/
- **Cluster Creation**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/create/
- **Connect to Cluster**: https://docs.digitalocean.com/products/kubernetes/how-to/connect-to-cluster/
- **1-Click Apps**: https://docs.digitalocean.com/products/kubernetes/how-to/manage-1click-apps/
- **Velero Plugin**: https://github.com/digitalocean/velero-plugin
- **DOKS Starter Kit**: https://github.com/digitalocean/Kubernetes-Starter-Kit-Developers

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Deployment Scripts](#deployment-scripts)
4. [Official doctl Commands](#official-doctl-commands)
5. [Velero Backup Setup](#velero-backup-setup)
6. [Monitoring and Management](#monitoring-and-management)
7. [Cost Optimization](#cost-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

Install the following tools before deployment:

#### 1. doctl (DigitalOcean CLI)

**macOS:**
```bash
brew install doctl
```

**Linux:**
```bash
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.141.0/doctl-1.141.0-linux-amd64.tar.gz
tar xf ~/doctl-1.141.0-linux-amd64.tar.gz
sudo mv ~/doctl /usr/local/bin
```

**Verify Installation:**
```bash
doctl version
```

**Official Installation Guide**: https://docs.digitalocean.com/reference/doctl/how-to/install/

#### 2. kubectl (Kubernetes CLI)

**macOS:**
```bash
brew install kubectl
```

**Linux:**
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

**Verify:**
```bash
kubectl version --client
```

#### 3. Helm (Package Manager)

**macOS:**
```bash
brew install helm
```

**Linux:**
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Verify:**
```bash
helm version
```

#### 4. Velero CLI (Backup Tool)

**macOS:**
```bash
brew install velero
```

**Linux:**
```bash
wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
tar -xvf velero-v1.12.0-linux-amd64.tar.gz
sudo mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/
```

**Verify:**
```bash
velero version --client-only
```

---

## Installation Steps

### Step 1: Authenticate doctl

```bash
# Initialize doctl with your DigitalOcean API token
doctl auth init

# Verify authentication
doctl account get

# List authentication contexts
doctl auth list
```

**Get API Token**: https://cloud.digitalocean.com/account/api/tokens

**Official Guide**: https://docs.digitalocean.com/reference/doctl/how-to/install/#step-3-initialize-doctl

### Step 2: Check Available Options

Before creating a cluster, review available options:

```bash
# List available Kubernetes versions
doctl kubernetes options versions

# List available regions
doctl kubernetes options regions

# List available node sizes (Droplet types)
doctl kubernetes options sizes

# List available 1-Click applications
doctl kubernetes 1-click list
```

**Reference**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/options/

### Step 3: Configure Environment Variables

Copy and edit the example configuration:

```bash
# Copy Terraform variables example
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Required variables:**
- `do_token` - Your DigitalOcean API token
- `cluster_name` - Name for your cluster
- `region` - DigitalOcean region (e.g., nyc1, sfo3)
- `node_size` - Droplet size (e.g., s-4vcpu-8gb)

### Step 4: Create Kubernetes Cluster

Make script executable and run:

```bash
chmod +x do-create-cluster.sh
./do-create-cluster.sh
```

**Or manually with environment variables:**

```bash
export CLUSTER_NAME="bcm-platform-cluster"
export REGION="nyc1"
export NODE_SIZE="s-4vcpu-8gb"
export NODE_COUNT="3"
export HA_CONTROL_PLANE="true"
export ONE_CLICKS="ingress-nginx,monitoring"

./do-create-cluster.sh
```

**This script uses the official command:**
```bash
doctl kubernetes cluster create $CLUSTER_NAME \
  --region $REGION \
  --size $NODE_SIZE \
  --count $NODE_COUNT \
  --ha \
  --1-clicks ingress-nginx,monitoring
```

**Reference**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/create/

### Step 5: Configure kubectl Access

```bash
chmod +x do-configure.sh
./do-configure.sh
```

**This script uses the official command:**
```bash
doctl kubernetes cluster kubeconfig save $CLUSTER_NAME
```

**What this does:**
- Downloads cluster kubeconfig
- Merges with `~/.kube/config`
- Sets current context to the new cluster
- Configures authentication automatically

**Reference**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/kubeconfig/save/

**Manual verification:**
```bash
# View cluster info
kubectl cluster-info

# List nodes
kubectl get nodes

# View current context
kubectl config current-context

# Display kubeconfig
doctl kubernetes cluster kubeconfig show $CLUSTER_NAME
```

### Step 6: Install Add-ons

```bash
chmod +x do-install-addons.sh
./do-install-addons.sh
```

**Components installed:**
- **ingress-nginx** - NGINX Ingress Controller with LoadBalancer
- **cert-manager** - TLS certificate management
- **metrics-server** - Resource metrics
- **Velero** - Backup and disaster recovery (manual setup)

**Reference**: https://docs.digitalocean.com/products/kubernetes/how-to/manage-1click-apps/

### Step 7: Deploy BCM Platform

```bash
chmod +x do-deploy-bcm.sh
./do-deploy-bcm.sh
```

This script:
1. Verifies cluster readiness
2. Gets LoadBalancer external IP
3. Creates namespace
4. Generates DigitalOcean-specific values file
5. Provides deployment commands

**Then deploy with Helm:**
```bash
helm install bcm-platform ../../helm/bcm-platform \
  --namespace bcm-platform \
  --values values-digitalocean.yaml \
  --set postgresql.auth.password=<secure-password> \
  --set redis.auth.password=<secure-password> \
  --set rabbitmq.auth.password=<secure-password> \
  --timeout 10m \
  --wait
```

---

## Deployment Scripts

### do-create-cluster.sh

Creates a DigitalOcean Kubernetes cluster with specified configuration.

**Environment Variables:**
- `CLUSTER_NAME` - Cluster name (default: bcm-platform-cluster)
- `REGION` - DigitalOcean region (default: nyc1)
- `K8S_VERSION` - Kubernetes version (default: latest)
- `NODE_SIZE` - Node size (default: s-4vcpu-8gb)
- `NODE_COUNT` - Number of nodes (default: 3)
- `HA_CONTROL_PLANE` - Enable HA control plane (default: true)
- `AUTO_UPGRADE` - Enable auto-upgrades (default: false)
- `TAGS` - Comma-separated tags
- `ONE_CLICKS` - 1-Click apps to install

### do-configure.sh

Configures kubectl to connect to the DOKS cluster.

**Environment Variables:**
- `CLUSTER_NAME` - Cluster name
- `KUBECONFIG_PATH` - Path to kubeconfig file

### do-install-addons.sh

Installs monitoring, ingress, cert-manager, and Velero.

**Environment Variables:**
- `CLUSTER_NAME` - Cluster name
- `INSTALL_CERT_MANAGER` - Install cert-manager (default: true)
- `INSTALL_VELERO` - Install Velero (default: true)
- `DO_SPACES_BUCKET` - Spaces bucket for backups
- `DO_SPACES_REGION` - Spaces region

### do-deploy-bcm.sh

Prepares and deploys the BCM Platform.

**Environment Variables:**
- `NAMESPACE` - Kubernetes namespace (default: bcm-platform)
- `HELM_RELEASE_NAME` - Helm release name
- `HELM_CHART_PATH` - Path to Helm chart
- `INGRESS_HOST` - Hostname for ingress

---

## Official doctl Commands

### Cluster Management

```bash
# Create cluster with HA control plane and 1-Click apps
doctl kubernetes cluster create my-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --size s-4vcpu-8gb \
  --count 3 \
  --ha \
  --1-clicks ingress-nginx,monitoring

# List clusters
doctl kubernetes cluster list

# Get cluster details
doctl kubernetes cluster get <cluster-name>

# Update cluster (add tags, enable auto-upgrade)
doctl kubernetes cluster update <cluster-name> \
  --auto-upgrade=true \
  --tag production

# Delete cluster
doctl kubernetes cluster delete <cluster-name>
```

**Reference**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/

### Node Pool Management

```bash
# List node pools
doctl kubernetes cluster node-pool list <cluster-name>

# Create additional node pool
doctl kubernetes cluster node-pool create <cluster-name> \
  --name high-memory-pool \
  --size s-8vcpu-16gb \
  --count 2 \
  --auto-scale \
  --min-nodes 2 \
  --max-nodes 5

# Resize node pool
doctl kubernetes cluster node-pool update <cluster-name> <pool-id> \
  --count 4

# Delete node pool
doctl kubernetes cluster node-pool delete <cluster-name> <pool-id>
```

**Reference**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/node-pool/

### Kubeconfig Management

```bash
# Save kubeconfig and set as current context
doctl kubernetes cluster kubeconfig save <cluster-name>

# Display kubeconfig
doctl kubernetes cluster kubeconfig show <cluster-name>

# Remove kubeconfig from local config
doctl kubernetes cluster kubeconfig remove <cluster-name>
```

**Reference**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/kubeconfig/

### 1-Click Applications

```bash
# List available 1-Click apps
doctl kubernetes 1-click list

# Install 1-Click app on existing cluster
doctl kubernetes 1-click install <cluster-name> \
  --1-clicks ingress-nginx

# Install multiple apps
doctl kubernetes 1-click install <cluster-name> \
  --1-clicks ingress-nginx,monitoring,cert-manager
```

**Reference**: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/1-click/

### Registry Management

```bash
# Create container registry
doctl registry create <registry-name>

# Login to registry
doctl registry login

# Get registry info
doctl registry get

# Configure cluster to use registry
doctl kubernetes cluster registry add <cluster-name> <registry-name>
```

**Reference**: https://docs.digitalocean.com/reference/doctl/reference/registry/

---

## Velero Backup Setup

### Official Velero Configuration for DigitalOcean Spaces

**References:**
- https://github.com/digitalocean/velero-plugin
- https://www.digitalocean.com/community/tutorials/how-to-back-up-and-restore-a-kubernetes-cluster-on-digitalocean-using-velero
- https://github.com/digitalocean/Kubernetes-Starter-Kit-Developers/blob/main/05-setup-backup-restore/velero.md

### Step 1: Create DigitalOcean Space

```bash
# Via DigitalOcean CLI
doctl compute space create bcm-velero-backups \
  --region nyc3

# Or via web console
# https://cloud.digitalocean.com/spaces
```

### Step 2: Create Spaces Access Keys

1. Navigate to https://cloud.digitalocean.com/account/api/tokens
2. Go to "Spaces Keys" section
3. Click "Generate New Key"
4. Save the Access Key ID and Secret Key

### Step 3: Create Credentials File

```bash
# Copy example file
cp credentials-velero.example credentials-velero

# Edit with your actual keys
nano credentials-velero
```

**Format:**
```ini
[default]
aws_access_key_id=DO00XXXXXXXXXXXXX
aws_secret_access_key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Install Velero with DigitalOcean Plugin

**Official command from DigitalOcean documentation:**

```bash
velero install \
  --provider velero.io/aws \
  --plugins velero/velero-plugin-for-aws:v1.10.0,digitalocean/velero-plugin:v1.1.0 \
  --bucket bcm-velero-backups \
  --secret-file=./credentials-velero \
  --backup-location-config region=nyc3,s3ForcePathStyle=true,s3Url=https://nyc3.digitaloceanspaces.com \
  --snapshot-location-config region=nyc3 \
  --use-node-agent=true \
  --use-volume-snapshots=true \
  --features=EnableCSI \
  --wait
```

**Parameters explained:**
- `--provider velero.io/aws` - DigitalOcean Spaces uses S3-compatible API
- `--plugins` - AWS plugin for S3 compatibility + DigitalOcean plugin for volume snapshots
- `--bucket` - Your DigitalOcean Space name
- `--backup-location-config` - Space region and S3 URL
- `--use-node-agent` - Enable File System Backup (formerly Restic)
- `--use-volume-snapshots` - Enable DigitalOcean volume snapshots
- `--features=EnableCSI` - Enable CSI snapshot support

**Region Options:**
- `nyc3` - New York 3
- `sfo3` - San Francisco 3
- `sgp1` - Singapore 1
- `fra1` - Frankfurt 1
- `ams3` - Amsterdam 3

### Step 5: Verify Velero Installation

```bash
# Check Velero deployment
kubectl get deployment -n velero

# Check Velero pods
kubectl get pods -n velero

# Verify backup location
velero backup-location get

# Verify snapshot location
velero snapshot-location get
```

### Step 6: Create Backup Schedules

**Daily full cluster backup:**
```bash
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --ttl 720h0m0s \
  --include-namespaces='*'
```

**Hourly BCM Platform namespace backup:**
```bash
velero schedule create hourly-bcm-backup \
  --schedule="0 * * * *" \
  --ttl 168h0m0s \
  --include-namespaces bcm-platform
```

**Weekly backup with volume snapshots:**
```bash
velero schedule create weekly-full-backup \
  --schedule="0 3 * * 0" \
  --ttl 2160h0m0s \
  --snapshot-volumes=true \
  --include-namespaces='*'
```

### Step 7: Test Backup and Restore

**Create on-demand backup:**
```bash
velero backup create test-backup \
  --include-namespaces bcm-platform \
  --wait
```

**Check backup status:**
```bash
velero backup describe test-backup
velero backup logs test-backup
```

**List backups:**
```bash
velero backup get
```

**Restore from backup:**
```bash
velero restore create --from-backup test-backup
```

**Restore specific namespace:**
```bash
velero restore create test-restore \
  --from-backup daily-backup-20240101120000 \
  --include-namespaces bcm-platform
```

### Step 8: Monitor Backups

```bash
# View backup schedules
velero schedule get

# Describe schedule
velero schedule describe daily-backup

# Check backup completion status
velero backup get

# View restore operations
velero restore get
```

**Reference**: https://velero.io/docs/main/backup-reference/

---

## Monitoring and Management

### Access NGINX Ingress Controller LoadBalancer

```bash
# Get LoadBalancer external IP
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Get LoadBalancer details
doctl compute load-balancer list
```

### Access Monitoring Stack (if installed)

The monitoring 1-Click app installs Prometheus and Grafana:

```bash
# Check monitoring namespace
kubectl get pods -n monitoring

# Access Grafana (port-forward)
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80

# Default credentials (change immediately):
# Username: admin
# Password: prom-operator
```

**Reference**: https://docs.digitalocean.com/products/kubernetes/how-to/monitor-cluster-prometheus-operator/

### View Cluster Metrics

```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods -A

# Get cluster events
kubectl get events -A --sort-by='.lastTimestamp'
```

### View Cluster Logs

```bash
# DigitalOcean provides cluster audit logs
doctl kubernetes cluster logs <cluster-name>

# View specific pod logs
kubectl logs -n bcm-platform <pod-name> --tail=100 -f

# View logs from all pods in deployment
kubectl logs -n bcm-platform -l app=bcm-platform --tail=100
```

### Scale Applications

```bash
# Scale deployment
kubectl scale deployment -n bcm-platform <deployment-name> --replicas=5

# View horizontal pod autoscalers
kubectl get hpa -n bcm-platform

# Describe HPA
kubectl describe hpa -n bcm-platform <hpa-name>
```

### Cluster Upgrades

```bash
# Check available upgrades
doctl kubernetes options versions

# Upgrade cluster
doctl kubernetes cluster upgrade <cluster-name> \
  --version <new-version>

# Upgrade with confirmation
doctl kubernetes cluster upgrade <cluster-name> \
  --version 1.28.2-do.0 \
  --yes
```

**Reference**: https://docs.digitalocean.com/products/kubernetes/how-to/upgrade-cluster/

---

## Cost Optimization

### Understanding DOKS Pricing

**Control Plane**: Free (fully managed by DigitalOcean)

**Worker Nodes**: Standard Droplet pricing
- `s-2vcpu-4gb`: $24/month
- `s-4vcpu-8gb`: $48/month
- `s-8vcpu-16gb`: $96/month

**Load Balancer**: $12/month per LB

**Block Storage**: $0.10/GB/month

**Spaces (Backup)**: $5/month (250GB included)

**Reference**: https://www.digitalocean.com/pricing/kubernetes

### Cost-Saving Tips

1. **Use Autoscaling**: Scale down during off-peak hours
   ```bash
   kubectl autoscale deployment -n bcm-platform <app> \
     --min=2 --max=10 --cpu-percent=80
   ```

2. **Right-size nodes**: Monitor resource usage and adjust node sizes

3. **Use spot instances**: DigitalOcean doesn't have spot instances, but use smaller nodes with autoscaling

4. **Clean up unused resources**:
   ```bash
   # Delete unused PVCs
   kubectl get pvc -A
   kubectl delete pvc <unused-pvc>

   # Delete old deployments
   kubectl delete deployment <old-deployment>
   ```

5. **Set resource limits**: Prevent resource waste
   ```yaml
   resources:
     requests:
       memory: "256Mi"
       cpu: "250m"
     limits:
       memory: "512Mi"
       cpu: "500m"
   ```

---

## Troubleshooting

### Common Issues

#### 1. Cluster Creation Fails

```bash
# Check doctl authentication
doctl account get

# Verify quota limits
doctl compute droplet list

# Check region capacity
doctl kubernetes options regions
```

#### 2. Unable to Connect to Cluster

```bash
# Re-download kubeconfig
doctl kubernetes cluster kubeconfig save <cluster-name> --overwrite

# Verify context
kubectl config get-contexts

# Switch context if needed
kubectl config use-context do-<region>-<cluster-name>
```

#### 3. Pods Not Starting

```bash
# Describe pod for events
kubectl describe pod -n <namespace> <pod-name>

# Check pod logs
kubectl logs -n <namespace> <pod-name>

# Check resource constraints
kubectl get nodes
kubectl describe node <node-name>
```

#### 4. LoadBalancer External IP Pending

```bash
# Check service
kubectl get svc -n ingress-nginx

# Describe service for events
kubectl describe svc -n ingress-nginx ingress-nginx-controller

# Check DigitalOcean LoadBalancer
doctl compute load-balancer list

# Typical wait time: 2-5 minutes
```

#### 5. Velero Backup Fails

```bash
# Check Velero logs
kubectl logs -n velero deployment/velero

# Verify credentials
kubectl get secret -n velero cloud-credentials -o yaml

# Check backup location
velero backup-location get

# Test Spaces connectivity
velero backup create test --wait
velero backup describe test --details
```

#### 6. Certificate Issues

```bash
# Check cert-manager pods
kubectl get pods -n cert-manager

# Describe certificate
kubectl describe certificate -n bcm-platform bcm-platform-tls

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Verify ClusterIssuer
kubectl get clusterissuer
kubectl describe clusterissuer letsencrypt-prod
```

### Get Help

**DigitalOcean Support:**
- Documentation: https://docs.digitalocean.com/products/kubernetes/
- Community: https://www.digitalocean.com/community/
- Support Tickets: https://cloud.digitalocean.com/support/tickets

**doctl Issues:**
- GitHub: https://github.com/digitalocean/doctl/issues

**Kubernetes Issues:**
- Kubernetes Docs: https://kubernetes.io/docs/
- Kubectl Reference: https://kubernetes.io/docs/reference/kubectl/

---

## Next Steps

After successful deployment:

1. **Configure DNS**: Point your domain to LoadBalancer IP
2. **Set up TLS**: Verify Let's Encrypt certificates are issued
3. **Configure Monitoring**: Set up alerts and dashboards
4. **Test Backups**: Verify Velero backups are working
5. **Security Hardening**:
   - Enable Pod Security Standards
   - Configure Network Policies
   - Set up RBAC
6. **CI/CD Integration**: Connect your deployment pipeline
7. **Performance Testing**: Load test your application
8. **Documentation**: Document your specific configuration

---

## Additional Resources

### Official DigitalOcean Documentation
- **DOKS Overview**: https://docs.digitalocean.com/products/kubernetes/
- **doctl Reference**: https://docs.digitalocean.com/reference/doctl/
- **Kubernetes Starter Kit**: https://github.com/digitalocean/Kubernetes-Starter-Kit-Developers
- **DOKS Best Practices**: https://docs.digitalocean.com/products/kubernetes/resources/best-practices/

### Community Tutorials
- **DOKS Setup Guide**: https://www.digitalocean.com/community/developer-center/how-to-set-up-a-digitalocean-managed-kubernetes-cluster-doks
- **Velero Backup Tutorial**: https://www.digitalocean.com/community/tutorials/how-to-back-up-and-restore-a-kubernetes-cluster-on-digitalocean-using-velero
- **Operational Readiness**: https://docs.digitalocean.com/products/kubernetes/getting-started/operational-readiness/

### Tools and Plugins
- **doctl GitHub**: https://github.com/digitalocean/doctl
- **Velero Plugin**: https://github.com/digitalocean/velero-plugin
- **Marketplace Apps**: https://marketplace.digitalocean.com/category/kubernetes

---

## Support

For issues with this deployment setup:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review DigitalOcean documentation
3. Check official doctl issues: https://github.com/digitalocean/doctl/issues
4. Contact DigitalOcean support

---

**Last Updated**: 2025-10-21
**doctl Version**: v1.141.0
**Kubernetes Version**: 1.28.2-do.0 (latest stable)
