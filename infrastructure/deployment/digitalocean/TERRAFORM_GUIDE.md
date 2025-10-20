# Terraform Deployment Guide for DigitalOcean Kubernetes

Complete guide for deploying DOKS cluster using Terraform with official DigitalOcean provider.

## Official Documentation

- **Terraform DigitalOcean Provider**: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs
- **Kubernetes Cluster Resource**: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs/resources/kubernetes_cluster
- **Terraform Best Practices**: https://www.terraform.io/docs/language/index.html

---

## Prerequisites

### Install Terraform

**macOS:**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Linux:**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

**Verify:**
```bash
terraform version
```

---

## Quick Start

### Step 1: Configure Variables

```bash
# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Minimum required variables:**
```hcl
do_token     = "dop_v1_your_token_here"
cluster_name = "bcm-platform-cluster"
region       = "nyc1"
```

### Step 2: Initialize Terraform

```bash
# Initialize Terraform and download provider
terraform init
```

**Expected output:**
```
Initializing the backend...
Initializing provider plugins...
- Finding digitalocean/digitalocean versions matching "~> 2.34.0"...
- Installing digitalocean/digitalocean v2.34.x...

Terraform has been successfully initialized!
```

### Step 3: Review Plan

```bash
# See what Terraform will create
terraform plan
```

This shows all resources that will be created:
- DigitalOcean Kubernetes cluster
- VPC network
- Container Registry (if enabled)
- Spaces bucket for backups (if enabled)
- 1-Click applications

### Step 4: Apply Configuration

```bash
# Create the infrastructure
terraform apply
```

**Review the plan and type `yes` to confirm.**

**Alternative (auto-approve):**
```bash
terraform apply -auto-approve
```

**Apply with specific variables:**
```bash
terraform apply \
  -var="cluster_name=my-cluster" \
  -var="region=sfo3" \
  -var="node_count=5"
```

### Step 5: Access Cluster

After successful deployment, Terraform outputs connection details:

```bash
# View outputs
terraform output

# Export kubeconfig
export KUBECONFIG=$(terraform output -raw kubeconfig_path)

# Or use doctl
terraform output -raw connection_command | bash
```

**Verify connection:**
```bash
kubectl get nodes
kubectl cluster-info
```

---

## Terraform Commands Reference

### Initialize and Validate

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format Terraform files
terraform fmt -recursive

# Check formatting
terraform fmt -check
```

### Plan and Apply

```bash
# Preview changes
terraform plan

# Save plan to file
terraform plan -out=tfplan

# Apply saved plan
terraform apply tfplan

# Apply with variable file
terraform apply -var-file="production.tfvars"

# Apply specific target
terraform apply -target=digitalocean_kubernetes_cluster.bcm_cluster
```

### Outputs and State

```bash
# Show all outputs
terraform output

# Show specific output
terraform output cluster_endpoint

# Show state
terraform show

# List resources in state
terraform state list

# Show specific resource
terraform state show digitalocean_kubernetes_cluster.bcm_cluster
```

### Destroy Resources

```bash
# Preview what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy

# Destroy with auto-approval
terraform destroy -auto-approve

# Destroy specific resource
terraform destroy -target=digitalocean_kubernetes_cluster.bcm_cluster
```

### Workspace Management

```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new production

# Switch workspace
terraform workspace select production

# Show current workspace
terraform workspace show
```

---

## Configuration Examples

### Basic Cluster

Minimal configuration for development:

```hcl
# terraform.tfvars
do_token                 = "dop_v1_your_token"
cluster_name             = "dev-cluster"
region                   = "nyc1"
node_size                = "s-2vcpu-4gb"
node_count               = 2
min_nodes                = 1
max_nodes                = 3
ha_control_plane         = false
create_container_registry = false
create_spaces_bucket     = false
environment              = "development"
```

### Production Cluster

Full configuration for production:

```hcl
# terraform.tfvars
do_token                  = "dop_v1_your_token"
cluster_name              = "bcm-production"
region                    = "nyc3"
k8s_version               = "1.28.2-do.0"
node_size                 = "s-4vcpu-8gb"
node_count                = 5
min_nodes                 = 3
max_nodes                 = 10
ha_control_plane          = true
auto_upgrade              = false
one_clicks                = ["ingress-nginx", "monitoring"]
create_container_registry = true
registry_subscription_tier = "professional"
create_spaces_bucket      = true
spaces_region             = "nyc3"
backup_retention_days     = 90
maintenance_day           = "sunday"
maintenance_hour          = "04:00"
environment               = "production"
tags                      = ["bcm-platform", "production", "critical"]
```

### High-Performance Cluster

For compute-intensive workloads:

```hcl
# terraform.tfvars
node_size  = "c-8vcpu-16gb"  # CPU-optimized
node_count = 5
min_nodes  = 3
max_nodes  = 15
```

### Multi-Region Setup

Deploy to multiple regions using workspaces:

```bash
# Create production workspace
terraform workspace new production
terraform apply -var-file="production.tfvars" -var="region=nyc3"

# Create DR workspace
terraform workspace new disaster-recovery
terraform apply -var-file="production.tfvars" -var="region=sfo3"
```

---

## Advanced Configuration

### Custom Node Pool

Add additional node pools:

```hcl
# Add to main.tf
resource "digitalocean_kubernetes_node_pool" "high_memory" {
  cluster_id = digitalocean_kubernetes_cluster.bcm_cluster.id
  name       = "high-memory-pool"
  size       = "m-8vcpu-64gb"
  node_count = 2
  auto_scale = true
  min_nodes  = 1
  max_nodes  = 5

  labels = {
    workload = "memory-intensive"
  }

  taint {
    key    = "workloadType"
    value  = "memory"
    effect = "NoSchedule"
  }
}
```

### Remote State Backend

Store state in DigitalOcean Spaces:

```hcl
# backend.tf
terraform {
  backend "s3" {
    endpoint                    = "nyc3.digitaloceanspaces.com"
    region                      = "us-east-1" # DigitalOcean Spaces uses us-east-1
    bucket                      = "terraform-state-bcm"
    key                         = "kubernetes/terraform.tfstate"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
  }
}
```

**Initialize with backend:**
```bash
export AWS_ACCESS_KEY_ID="DO_SPACES_KEY"
export AWS_SECRET_ACCESS_KEY="DO_SPACES_SECRET"
terraform init
```

### Module Usage

Create reusable module:

```hcl
# modules/doks-cluster/main.tf
module "doks_cluster" {
  source = "./modules/doks-cluster"

  cluster_name     = "app-cluster"
  region           = "nyc1"
  node_size        = "s-4vcpu-8gb"
  node_count       = 3
  ha_control_plane = true
}
```

---

## State Management

### Import Existing Resources

Import existing cluster created via doctl:

```bash
# Get cluster ID
doctl kubernetes cluster list --format ID,Name

# Import cluster
terraform import digitalocean_kubernetes_cluster.bcm_cluster <cluster-id>
```

### Move Resources

```bash
# Move resource in state
terraform state mv \
  digitalocean_kubernetes_cluster.old_name \
  digitalocean_kubernetes_cluster.new_name

# Remove resource from state (without destroying)
terraform state rm digitalocean_kubernetes_cluster.bcm_cluster
```

### State Locking

For team collaboration, enable state locking:

```hcl
terraform {
  backend "s3" {
    endpoint = "nyc3.digitaloceanspaces.com"
    bucket   = "terraform-state"
    key      = "doks/terraform.tfstate"

    # Use DynamoDB-compatible lock table
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/terraform.yml
name: Terraform Deploy

on:
  push:
    branches: [main]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        env:
          DIGITALOCEAN_TOKEN: ${{ secrets.DO_TOKEN }}
        run: terraform init

      - name: Terraform Plan
        env:
          TF_VAR_do_token: ${{ secrets.DO_TOKEN }}
        run: terraform plan -out=tfplan

      - name: Terraform Apply
        env:
          TF_VAR_do_token: ${{ secrets.DO_TOKEN }}
        run: terraform apply -auto-approve tfplan
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - plan
  - apply

terraform-validate:
  stage: validate
  script:
    - terraform init -backend=false
    - terraform validate
    - terraform fmt -check

terraform-plan:
  stage: plan
  script:
    - terraform init
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - tfplan

terraform-apply:
  stage: apply
  script:
    - terraform apply -auto-approve tfplan
  when: manual
  only:
    - main
```

---

## Security Best Practices

### Secrets Management

**Never commit secrets to Git!**

Use environment variables:
```bash
export TF_VAR_do_token="your_token"
export TF_VAR_spaces_access_key="your_key"
export TF_VAR_spaces_secret_key="your_secret"

terraform apply
```

Or use secret management tools:
```bash
# HashiCorp Vault
terraform plan -var="do_token=$(vault read -field=token secret/do/api)"

# AWS Secrets Manager
terraform plan -var="do_token=$(aws secretsmanager get-secret-value --secret-id do-token --query SecretString --output text)"
```

### State Encryption

Always encrypt state files:

```hcl
terraform {
  backend "s3" {
    encrypt = true
  }
}
```

### Resource Tagging

Implement consistent tagging:

```hcl
locals {
  common_tags = [
    "terraform-managed",
    "environment:${var.environment}",
    "cost-center:engineering",
    "project:bcm-platform"
  ]
}

resource "digitalocean_kubernetes_cluster" "bcm_cluster" {
  tags = concat(var.tags, local.common_tags)
}
```

---

## Troubleshooting

### Common Issues

#### 1. Provider Authentication Error

```
Error: Error creating kubernetes cluster: GET https://api.digitalocean.com/v2/kubernetes/clusters: 401 unable to authenticate you
```

**Solution:**
```bash
# Verify token is set
echo $TF_VAR_do_token

# Or set in tfvars file
echo 'do_token = "dop_v1_your_token"' >> terraform.tfvars
```

#### 2. State Lock Error

```
Error: Error acquiring the state lock
```

**Solution:**
```bash
# Force unlock (use with caution)
terraform force-unlock <lock-id>
```

#### 3. Resource Already Exists

```
Error: Error creating kubernetes cluster: already exists
```

**Solution:**
```bash
# Import existing resource
terraform import digitalocean_kubernetes_cluster.bcm_cluster <cluster-id>
```

#### 4. Version Conflict

```
Error: Unsupported Kubernetes version
```

**Solution:**
```bash
# List available versions
doctl kubernetes options versions

# Update variable
terraform apply -var="k8s_version=1.28.2-do.0"
```

### Debug Mode

Enable detailed logging:

```bash
# Set log level
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform.log

# Run command
terraform apply

# Review logs
cat terraform.log
```

---

## Maintenance

### Update Cluster

```bash
# Update Kubernetes version
terraform apply -var="k8s_version=1.29.0-do.0"

# Scale node pool
terraform apply -var="node_count=5"

# Enable auto-upgrade
terraform apply -var="auto_upgrade=true"
```

### Backup State

```bash
# Create state backup
terraform state pull > terraform.tfstate.backup

# Restore from backup
terraform state push terraform.tfstate.backup
```

### Refresh State

```bash
# Update state with real infrastructure
terraform refresh

# Or during plan
terraform plan -refresh=true
```

---

## Clean Up

### Destroy Resources

**WARNING: This will delete all resources!**

```bash
# Preview destruction
terraform plan -destroy

# Destroy with confirmation
terraform destroy

# Auto-approve destruction
terraform destroy -auto-approve

# Destroy specific resource only
terraform destroy -target=digitalocean_spaces_bucket.velero_backups
```

### Preserve Specific Resources

Remove from state before destroy:

```bash
# Remove from state (keeps resource in DigitalOcean)
terraform state rm digitalocean_kubernetes_cluster.bcm_cluster

# Now destroy won't affect it
terraform destroy
```

---

## Additional Resources

### Official Documentation
- **Terraform DigitalOcean Provider**: https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs
- **Terraform Language**: https://www.terraform.io/language
- **Terraform CLI**: https://www.terraform.io/cli

### Community Resources
- **DigitalOcean Community**: https://www.digitalocean.com/community/tutorials
- **Terraform Discuss**: https://discuss.hashicorp.com/c/terraform-core
- **Example Configurations**: https://github.com/digitalocean/terraform-provider-digitalocean/tree/main/examples

### Tools
- **tfenv** - Terraform version manager: https://github.com/tfutils/tfenv
- **terraform-docs** - Generate documentation: https://terraform-docs.io/
- **tflint** - Linter for Terraform: https://github.com/terraform-linters/tflint
- **checkov** - Security scanner: https://www.checkov.io/

---

**Last Updated**: 2025-10-21
**Terraform Version**: 1.6.0+
**Provider Version**: 2.34.0+
