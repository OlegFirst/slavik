# DigitalOcean Kubernetes Quick Start Guide

Get your BCM Platform running on DigitalOcean Kubernetes in under 30 minutes.

---

## Prerequisites Checklist

- [ ] DigitalOcean account (sign up at https://cloud.digitalocean.com)
- [ ] DigitalOcean API Token (create at https://cloud.digitalocean.com/account/api/tokens)
- [ ] Credit card added to DigitalOcean account
- [ ] Terminal/Command Line access

**Estimated Cost**: ~$150-200/month for production setup

---

## Option 1: Quick Deploy with Scripts (Recommended for Beginners)

### Step 1: Install Required Tools (5 minutes)

**macOS:**
```bash
# Install all tools at once
brew install doctl kubectl helm velero
```

**Linux (Ubuntu/Debian):**
```bash
# Install doctl
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.141.0/doctl-1.141.0-linux-amd64.tar.gz
tar xf ~/doctl-1.141.0-linux-amd64.tar.gz
sudo mv ~/doctl /usr/local/bin

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Velero
wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
tar -xvf velero-v1.12.0-linux-amd64.tar.gz
sudo mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/
```

**Verify installations:**
```bash
doctl version
kubectl version --client
helm version
velero version --client-only
```

### Step 2: Authenticate with DigitalOcean (2 minutes)

```bash
# Initialize doctl with your API token
doctl auth init

# When prompted, paste your DigitalOcean API token
# Get token from: https://cloud.digitalocean.com/account/api/tokens

# Verify authentication
doctl account get
```

### Step 3: Create Kubernetes Cluster (10-15 minutes)

```bash
# Navigate to deployment directory
cd infrastructure/deployment/digitalocean

# Make scripts executable
chmod +x *.sh

# Create cluster (default: 3 nodes, nyc1 region, HA control plane)
./do-create-cluster.sh

# Or customize with environment variables:
export CLUSTER_NAME="my-bcm-cluster"
export REGION="sfo3"
export NODE_SIZE="s-4vcpu-8gb"
export NODE_COUNT="3"
./do-create-cluster.sh
```

**Available Regions:**
- `nyc1`, `nyc3` - New York
- `sfo2`, `sfo3` - San Francisco
- `ams3` - Amsterdam
- `sgp1` - Singapore
- `lon1` - London
- `fra1` - Frankfurt
- `tor1` - Toronto
- `blr1` - Bangalore

**Wait for cluster creation** (typically 5-10 minutes)

### Step 4: Configure kubectl Access (1 minute)

```bash
# Configure kubectl to connect to your cluster
./do-configure.sh

# Verify connection
kubectl get nodes
```

You should see 3 nodes in "Ready" status.

### Step 5: Install Add-ons (5 minutes)

```bash
# Install ingress-nginx, cert-manager, and prepare Velero
./do-install-addons.sh
```

This installs:
- NGINX Ingress Controller (with DigitalOcean LoadBalancer)
- cert-manager (for TLS certificates)
- metrics-server (for resource metrics)
- Velero setup instructions (for backups)

### Step 6: Deploy BCM Platform (5 minutes)

```bash
# Prepare deployment
./do-deploy-bcm.sh

# Get LoadBalancer IP
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Update DNS
# Point your domain (e.g., bcm.example.com) to the LoadBalancer IP

# Deploy with Helm (after DNS is configured)
helm install bcm-platform ../../helm/bcm-platform \
  --namespace bcm-platform \
  --values values-digitalocean.yaml \
  --set postgresql.auth.password=YOUR_SECURE_PASSWORD \
  --set redis.auth.password=YOUR_SECURE_PASSWORD \
  --set rabbitmq.auth.password=YOUR_SECURE_PASSWORD \
  --timeout 10m \
  --wait
```

### Step 7: Verify Deployment

```bash
# Check pod status
kubectl get pods -n bcm-platform

# Check services
kubectl get svc -n bcm-platform

# Check ingress
kubectl get ingress -n bcm-platform

# View application logs
kubectl logs -n bcm-platform -l app=bcm-platform --tail=100
```

---

## Option 2: Quick Deploy with Terraform (Recommended for Advanced Users)

### Step 1: Install Tools (5 minutes)

**macOS:**
```bash
brew install terraform doctl kubectl helm
```

**Linux:**
```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install other tools (see Option 1)
```

### Step 2: Configure Terraform (3 minutes)

```bash
# Navigate to deployment directory
cd infrastructure/deployment/digitalocean

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

**Minimum configuration in terraform.tfvars:**
```hcl
do_token     = "dop_v1_your_token_here"
cluster_name = "bcm-platform-cluster"
region       = "nyc1"
```

### Step 3: Deploy with Terraform (10-15 minutes)

```bash
# Initialize Terraform
terraform init

# Preview what will be created
terraform plan

# Create infrastructure
terraform apply

# Type 'yes' when prompted
```

### Step 4: Connect to Cluster (1 minute)

```bash
# Export kubeconfig
export KUBECONFIG=$(terraform output -raw kubeconfig_path)

# Or use doctl
doctl kubernetes cluster kubeconfig save $(terraform output -raw cluster_name)

# Verify
kubectl get nodes
```

### Step 5: Continue from Option 1, Step 5

Follow steps 5-7 from Option 1 above.

---

## Quick Commands Reference

### Cluster Management

```bash
# List clusters
doctl kubernetes cluster list

# Get cluster info
doctl kubernetes cluster get bcm-platform-cluster

# Get LoadBalancer IP
kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Update kubeconfig
doctl kubernetes cluster kubeconfig save bcm-platform-cluster
```

### Application Management

```bash
# View all resources
kubectl get all -n bcm-platform

# View logs
kubectl logs -n bcm-platform -l app=bcm-platform --tail=100 -f

# Describe pod (for troubleshooting)
kubectl describe pod -n bcm-platform <pod-name>

# Execute command in pod
kubectl exec -it -n bcm-platform <pod-name> -- /bin/bash

# Port forward to service
kubectl port-forward -n bcm-platform svc/<service-name> 8080:80
```

### Backup Management (After Velero Setup)

```bash
# Create backup
velero backup create bcm-backup --include-namespaces bcm-platform --wait

# List backups
velero backup get

# Restore from backup
velero restore create --from-backup bcm-backup

# Schedule daily backups
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --ttl 720h \
  --include-namespaces bcm-platform
```

---

## DNS Configuration

### Option 1: DigitalOcean DNS (Easiest)

1. Go to https://cloud.digitalocean.com/networking/domains
2. Add your domain
3. Create an A record:
   - Hostname: `@` (or subdomain like `bcm`)
   - Will Direct to: `<LoadBalancer-IP>`
   - TTL: 3600

### Option 2: External DNS Provider

Add an A record with your DNS provider:
```
Type: A
Name: bcm (or @)
Value: <LoadBalancer-IP>
TTL: 3600
```

**Get LoadBalancer IP:**
```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

---

## Setup Velero Backups (Optional but Recommended)

### Quick Velero Setup

1. **Create DigitalOcean Space:**
   ```bash
   # Via web: https://cloud.digitalocean.com/spaces
   # Or CLI:
   doctl compute space create bcm-velero-backups --region nyc3
   ```

2. **Get Spaces Access Keys:**
   - Go to https://cloud.digitalocean.com/account/api/tokens
   - Navigate to "Spaces Keys"
   - Click "Generate New Key"
   - Save the Access Key ID and Secret Key

3. **Create credentials file:**
   ```bash
   cat > credentials-velero <<EOF
   [default]
   aws_access_key_id=YOUR_ACCESS_KEY_ID
   aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
   EOF
   ```

4. **Install Velero:**
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

5. **Create backup schedule:**
   ```bash
   velero schedule create daily-backup \
     --schedule="0 2 * * *" \
     --ttl 720h \
     --include-namespaces bcm-platform
   ```

---

## Troubleshooting Quick Fixes

### Cluster Creation Fails

```bash
# Check account status
doctl account get

# Verify region availability
doctl kubernetes options regions

# Check quota limits
doctl compute droplet list
```

### Can't Connect to Cluster

```bash
# Re-download kubeconfig
doctl kubernetes cluster kubeconfig save bcm-platform-cluster --overwrite

# Verify context
kubectl config get-contexts

# Test connection
kubectl cluster-info
```

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n bcm-platform

# Describe pod for errors
kubectl describe pod -n bcm-platform <pod-name>

# View logs
kubectl logs -n bcm-platform <pod-name>

# Check node resources
kubectl describe nodes
```

### LoadBalancer IP Pending

```bash
# Wait 2-5 minutes, then check again
kubectl get svc -n ingress-nginx

# Check DigitalOcean LoadBalancer
doctl compute load-balancer list

# Describe service for events
kubectl describe svc -n ingress-nginx ingress-nginx-controller
```

### Certificate Not Issued

```bash
# Check cert-manager pods
kubectl get pods -n cert-manager

# Describe certificate
kubectl describe certificate -n bcm-platform bcm-platform-tls

# Check ClusterIssuer
kubectl describe clusterissuer letsencrypt-prod

# View cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

---

## Cost Breakdown

### Minimal Setup (~$90/month)
- 2x s-2vcpu-4gb nodes: $48
- 1x LoadBalancer: $12
- Block Storage (20GB): $2
- Spaces (250GB): $5
- Container Registry (Basic): $20
- **Total: ~$87/month**

### Recommended Production (~$180/month)
- 3x s-4vcpu-8gb nodes: $144
- HA Control Plane: Free
- 1x LoadBalancer: $12
- Block Storage (50GB): $5
- Spaces (500GB): $5
- Container Registry (Basic): $20
- **Total: ~$186/month**

### High Availability (~$350/month)
- 5x s-4vcpu-8gb nodes: $240
- HA Control Plane: Free
- 2x LoadBalancer: $24
- Block Storage (100GB): $10
- Spaces (1TB): $10
- Container Registry (Professional): $60
- **Total: ~$344/month**

**Note**: Prices as of October 2025. Check current pricing at https://www.digitalocean.com/pricing

---

## Next Steps

After successful deployment:

1. **Configure TLS Certificates**
   - Update email in ClusterIssuer
   - Verify certificate issuance

2. **Set Up Monitoring**
   - Access Grafana dashboards
   - Configure alerts

3. **Configure Backups**
   - Test Velero backups
   - Set up backup schedules

4. **Security Hardening**
   - Enable Pod Security Standards
   - Configure Network Policies
   - Set up RBAC

5. **CI/CD Integration**
   - Connect deployment pipeline
   - Configure auto-deployment

6. **Performance Tuning**
   - Configure HPA
   - Set resource limits
   - Enable cluster autoscaling

---

## Getting Help

- **README**: Full documentation in `README.md`
- **Terraform Guide**: Infrastructure as code guide in `TERRAFORM_GUIDE.md`
- **Official Docs**: https://docs.digitalocean.com/products/kubernetes/
- **Community**: https://www.digitalocean.com/community/
- **Support**: https://cloud.digitalocean.com/support/tickets

---

## Clean Up (Destroy Everything)

**WARNING: This will delete all resources and data!**

### Using Scripts:
```bash
doctl kubernetes cluster delete bcm-platform-cluster
```

### Using Terraform:
```bash
terraform destroy
```

**Before destroying:**
1. Backup all important data
2. Export configurations
3. Download logs and metrics
4. Verify backups are stored in Spaces

---

**Congratulations!** Your BCM Platform should now be running on DigitalOcean Kubernetes.

Access your application at: https://your-domain.com

**Last Updated**: 2025-10-21
