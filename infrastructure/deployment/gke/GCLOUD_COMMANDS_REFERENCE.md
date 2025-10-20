# Google Cloud SDK (gcloud) Commands Reference

Complete reference of all official gcloud commands used in this GKE deployment.

## Table of Contents

- [Authentication & Configuration](#authentication--configuration)
- [GKE Cluster Management](#gke-cluster-management)
- [API Management](#api-management)
- [IAM & Service Accounts](#iam--service-accounts)
- [Cloud Storage](#cloud-storage)
- [Monitoring & Logging](#monitoring--logging)
- [kubectl Integration](#kubectl-integration)

---

## Authentication & Configuration

### Authenticate to Google Cloud

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/auth/login

```bash
# Interactive browser-based authentication
gcloud auth login

# Application default credentials (for tools/libraries)
gcloud auth application-default login

# List authenticated accounts
gcloud auth list

# Set active account
gcloud config set account ACCOUNT_EMAIL
```

### Project Configuration

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/config/set

```bash
# Set default project
gcloud config set project PROJECT_ID

# Set default region
gcloud config set compute/region REGION

# Set default zone
gcloud config set compute/zone ZONE

# View all configuration
gcloud config list

# View specific configuration
gcloud config get-value project
gcloud config get-value compute/region
```

---

## GKE Cluster Management

### Create Autopilot Cluster

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/create-auto

**Full Command Syntax**:
```bash
gcloud container clusters create-auto CLUSTER_NAME \
    --region=REGION \
    [--release-channel=RELEASE_CHANNEL] \
    [--network=NETWORK] \
    [--subnetwork=SUBNETWORK] \
    [--enable-private-nodes] \
    [--enable-private-endpoint] \
    [--enable-master-authorized-networks] \
    [--master-authorized-networks=CIDR] \
    [--enable-stackdriver-kubernetes] \
    [--logging=LOGGING_COMPONENTS] \
    [--monitoring=MONITORING_COMPONENTS] \
    [--labels=KEY=VALUE,...] \
    [--async] \
    [--cluster-version=VERSION]
```

**Example**:
```bash
gcloud container clusters create-auto bcm-platform-autopilot \
    --region=us-central1 \
    --release-channel=regular \
    --network=default \
    --subnetwork=default \
    --enable-private-nodes \
    --enable-private-endpoint \
    --enable-master-authorized-networks \
    --master-authorized-networks=0.0.0.0/0 \
    --enable-stackdriver-kubernetes \
    --logging=SYSTEM,WORKLOAD \
    --monitoring=SYSTEM \
    --labels=environment=production,platform=bcm
```

**Parameters Explained**:

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `CLUSTER_NAME` | Name of the cluster | Yes | - |
| `--region` | Compute region for cluster | Yes | - |
| `--release-channel` | Release channel (rapid/regular/stable) | No | regular |
| `--network` | VPC network to use | No | default |
| `--subnetwork` | Subnet to use | No | default |
| `--enable-private-nodes` | Use private IP addresses for nodes | No | false |
| `--enable-private-endpoint` | Make control plane private | No | false |
| `--enable-master-authorized-networks` | Restrict control plane access | No | false |
| `--master-authorized-networks` | CIDR blocks for control plane access | No | - |
| `--logging` | Logging components (SYSTEM,WORKLOAD) | No | SYSTEM |
| `--monitoring` | Monitoring components | No | SYSTEM |
| `--labels` | Resource labels (key=value pairs) | No | - |

### Describe Cluster

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/describe

```bash
# Basic cluster description
gcloud container clusters describe CLUSTER_NAME \
    --region=REGION

# Get specific fields
gcloud container clusters describe CLUSTER_NAME \
    --region=REGION \
    --format="value(status)"

# Get monitoring/logging services
gcloud container clusters describe CLUSTER_NAME \
    --region=REGION \
    --format="value(monitoringService,loggingService)"

# Output as JSON
gcloud container clusters describe CLUSTER_NAME \
    --region=REGION \
    --format=json
```

### List Clusters

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/list

```bash
# List all clusters
gcloud container clusters list

# List clusters in specific region
gcloud container clusters list --region=REGION

# Format output
gcloud container clusters list --format="table(name,location,status,currentNodeCount)"
```

### Update Cluster

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/update

```bash
# Update cluster configuration
gcloud container clusters update CLUSTER_NAME \
    --region=REGION

# Enable workload identity
gcloud container clusters update CLUSTER_NAME \
    --region=REGION \
    --workload-pool=PROJECT_ID.svc.id.goog

# Update master authorized networks
gcloud container clusters update CLUSTER_NAME \
    --region=REGION \
    --enable-master-authorized-networks \
    --master-authorized-networks=CIDR
```

### Delete Cluster

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/delete

```bash
# Delete cluster
gcloud container clusters delete CLUSTER_NAME \
    --region=REGION

# Delete without confirmation prompt
gcloud container clusters delete CLUSTER_NAME \
    --region=REGION \
    --quiet
```

### Get Cluster Credentials

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials

```bash
# Get credentials and configure kubectl
gcloud container clusters get-credentials CLUSTER_NAME \
    --region=REGION

# Get credentials for specific project
gcloud container clusters get-credentials CLUSTER_NAME \
    --region=REGION \
    --project=PROJECT_ID

# Use internal IP for control plane access
gcloud container clusters get-credentials CLUSTER_NAME \
    --region=REGION \
    --internal-ip
```

---

## API Management

### Enable APIs

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/services/enable

```bash
# Enable single API
gcloud services enable container.googleapis.com

# Enable multiple APIs
gcloud services enable \
    container.googleapis.com \
    compute.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudtrace.googleapis.com \
    clouderrorreporting.googleapis.com \
    cloudprofiler.googleapis.com
```

### List Enabled APIs

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/services/list

```bash
# List all enabled services
gcloud services list --enabled

# Filter by name
gcloud services list --enabled | grep container

# Show disabled services
gcloud services list --available
```

---

## IAM & Service Accounts

### Create Service Account

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/create

```bash
# Create service account
gcloud iam service-accounts create SERVICE_ACCOUNT_NAME \
    --display-name="DISPLAY_NAME" \
    --description="DESCRIPTION"

# Example for Velero
gcloud iam service-accounts create velero \
    --display-name="Velero service account" \
    --description="Service account for Velero backup system"
```

### Describe Service Account

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/describe

```bash
# Describe service account
gcloud iam service-accounts describe SERVICE_ACCOUNT_EMAIL

# Example
gcloud iam service-accounts describe velero@PROJECT_ID.iam.gserviceaccount.com
```

### List Service Accounts

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/list

```bash
# List all service accounts
gcloud iam service-accounts list

# Filter by name
gcloud iam service-accounts list --filter="email:velero*"
```

### Create Custom IAM Role

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/iam/roles/create

```bash
# Create custom role from YAML file
gcloud iam roles create ROLE_NAME \
    --project=PROJECT_ID \
    --file=ROLE_FILE.yaml

# Example role YAML file:
cat > velero-role.yaml <<EOF
title: "Velero Server"
description: "Velero server role"
stage: "GA"
includedPermissions:
- compute.disks.get
- compute.disks.create
- compute.disks.createSnapshot
- compute.snapshots.get
- compute.snapshots.create
- compute.snapshots.useReadOnly
- compute.snapshots.delete
- compute.zones.get
EOF

gcloud iam roles create velero.server \
    --project=PROJECT_ID \
    --file=velero-role.yaml
```

### Update Custom IAM Role

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/iam/roles/update

```bash
# Update custom role
gcloud iam roles update ROLE_NAME \
    --project=PROJECT_ID \
    --file=ROLE_FILE.yaml
```

### Add IAM Policy Binding

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/projects/add-iam-policy-binding

```bash
# Bind role to service account
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=serviceAccount:SERVICE_ACCOUNT_EMAIL \
    --role=ROLE

# Example for Velero
gcloud projects add-iam-policy-binding my-project \
    --member=serviceAccount:velero@my-project.iam.gserviceaccount.com \
    --role=projects/my-project/roles/velero.server
```

### Create Service Account Key

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/keys/create

```bash
# Create JSON key file
gcloud iam service-accounts keys create KEY_FILE.json \
    --iam-account=SERVICE_ACCOUNT_EMAIL

# Example
gcloud iam service-accounts keys create credentials-velero.json \
    --iam-account=velero@PROJECT_ID.iam.gserviceaccount.com
```

### List Service Account Keys

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts/keys/list

```bash
# List keys for service account
gcloud iam service-accounts keys list \
    --iam-account=SERVICE_ACCOUNT_EMAIL
```

---

## Cloud Storage

### Create Bucket

**Official Reference**: https://cloud.google.com/storage/docs/gsutil/commands/mb

```bash
# Create bucket using gsutil
gsutil mb -p PROJECT_ID -l REGION gs://BUCKET_NAME/

# Example
gsutil mb -p my-project -l us-central1 gs://bcm-platform-velero-backups/
```

### List Buckets

**Official Reference**: https://cloud.google.com/storage/docs/gsutil/commands/ls

```bash
# List all buckets
gsutil ls

# List with details
gsutil ls -L -b gs://BUCKET_NAME/

# List bucket contents
gsutil ls gs://BUCKET_NAME/
```

### Enable Versioning

**Official Reference**: https://cloud.google.com/storage/docs/gsutil/commands/versioning

```bash
# Enable versioning on bucket
gsutil versioning set on gs://BUCKET_NAME/

# Check versioning status
gsutil versioning get gs://BUCKET_NAME/
```

### Set IAM Policy on Bucket

**Official Reference**: https://cloud.google.com/storage/docs/gsutil/commands/iam

```bash
# Grant objectAdmin role to service account
gsutil iam ch serviceAccount:SERVICE_ACCOUNT_EMAIL:objectAdmin gs://BUCKET_NAME

# Example
gsutil iam ch serviceAccount:velero@my-project.iam.gserviceaccount.com:objectAdmin gs://bcm-platform-velero-backups/

# View bucket IAM policy
gsutil iam get gs://BUCKET_NAME
```

### Delete Bucket

**Official Reference**: https://cloud.google.com/storage/docs/gsutil/commands/rm

```bash
# Delete bucket and all contents
gsutil -m rm -r gs://BUCKET_NAME/
```

---

## Monitoring & Logging

### View Logs

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/logging/read

```bash
# Read recent logs
gcloud logging read "resource.type=k8s_cluster" \
    --limit=50 \
    --format=json

# Filter by cluster
gcloud logging read "resource.type=k8s_cluster AND resource.labels.cluster_name=CLUSTER_NAME" \
    --limit=50

# Filter by time
gcloud logging read "resource.type=k8s_cluster" \
    --freshness=1h \
    --format=json

# Filter by severity
gcloud logging read "resource.type=k8s_cluster AND severity>=ERROR" \
    --limit=50
```

### List Metrics

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/monitoring/time-series/list

```bash
# List time series
gcloud monitoring time-series list \
    --filter='resource.type="k8s_cluster"' \
    --format=json

# Filter by cluster
gcloud monitoring time-series list \
    --filter='resource.type="k8s_cluster" AND resource.labels.cluster_name="CLUSTER_NAME"'
```

---

## kubectl Integration

### Install kubectl

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/components/install

```bash
# Install kubectl component
gcloud components install kubectl

# Install gke-gcloud-auth-plugin
gcloud components install gke-gcloud-auth-plugin

# Update all components
gcloud components update
```

### List Components

**Official Reference**: https://cloud.google.com/sdk/gcloud/reference/components/list

```bash
# List all components
gcloud components list

# List installed components only
gcloud components list --only-local-state
```

---

## Additional Useful Commands

### Get Project Information

```bash
# Get current project ID
gcloud config get-value project

# Get project information
gcloud projects describe PROJECT_ID

# List all projects
gcloud projects list
```

### Check Quotas

```bash
# Get compute quotas
gcloud compute project-info describe --project=PROJECT_ID

# Get region-specific quotas
gcloud compute regions describe REGION
```

### Version Information

```bash
# gcloud SDK version
gcloud version

# Components versions
gcloud components list
```

---

## Common Flag Patterns

### Output Formatting

```bash
# JSON output
--format=json

# YAML output
--format=yaml

# Table output
--format="table(field1,field2,field3)"

# Get specific value
--format="value(fieldName)"

# CSV output
--format=csv
```

### Filtering

```bash
# Filter by field
--filter="fieldName=value"

# Multiple conditions
--filter="field1=value1 AND field2=value2"

# OR condition
--filter="field1=value1 OR field1=value2"

# Greater than / Less than
--filter="fieldName>=100"
```

### Async Operations

```bash
# Run command asynchronously
--async

# Don't wait for operation to complete
gcloud container clusters create-auto CLUSTER_NAME \
    --region=REGION \
    --async
```

### Quiet Mode

```bash
# Skip confirmation prompts
--quiet
# or
-q

# Example
gcloud container clusters delete CLUSTER_NAME --region=REGION --quiet
```

---

## Official Documentation Links

### Main References
- **gcloud SDK Documentation**: https://cloud.google.com/sdk/gcloud/reference
- **GKE Documentation**: https://cloud.google.com/kubernetes-engine/docs
- **Cloud Storage (gsutil)**: https://cloud.google.com/storage/docs/gsutil

### Command-Specific
- **create-auto**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/create-auto
- **get-credentials**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials
- **describe**: https://cloud.google.com/sdk/gcloud/reference/container/clusters/describe
- **services enable**: https://cloud.google.com/sdk/gcloud/reference/services/enable
- **iam service-accounts**: https://cloud.google.com/sdk/gcloud/reference/iam/service-accounts

### Installation & Setup
- **Install gcloud SDK**: https://cloud.google.com/sdk/docs/install
- **Initializing gcloud**: https://cloud.google.com/sdk/docs/initializing
- **Authorizing gcloud**: https://cloud.google.com/sdk/docs/authorizing

---

## Notes

- All commands in this reference are from official Google Cloud SDK documentation
- Command syntax and flags are current as of October 2025
- Always check `gcloud help COMMAND` for the most up-to-date information
- Use `gcloud version` to verify your SDK version
- Update SDK regularly with `gcloud components update`

---

**Last Updated**: October 21, 2025
**SDK Version Tested**: Google Cloud SDK 500.0.0+
**Documentation Source**: https://cloud.google.com/sdk/gcloud/reference
