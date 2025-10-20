#!/bin/bash
#
# Velero Backup System Setup for GKE
# Based on: https://velero.io/docs/main/gcp-config/
# Reference: https://github.com/vmware-tanzu/velero-plugin-for-gcp
#

set -e

# Load configuration
if [ -f "terraform.tfvars" ]; then
    source <(grep -v '^#' terraform.tfvars | sed 's/[[:space:]]*=[[:space:]]*/=/' | sed 's/^/export /')
fi

# Default values
PROJECT_ID="${project_id:-my-gcp-project}"
BUCKET="${velero_backup_bucket:-bcm-platform-velero-backups}"
REGION="${region:-us-central1}"
BACKUP_SCHEDULE="${velero_backup_schedule:-0 2 * * *}"
RETENTION_DAYS="${velero_backup_retention_days:-30}"
SERVICE_ACCOUNT_NAME="velero"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "========================================="
echo "Setting up Velero for GKE Backups"
echo "========================================="
echo "Project ID: $PROJECT_ID"
echo "Bucket: $BUCKET"
echo "Region: $REGION"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "========================================="

# Check if Velero CLI is installed
if ! command -v velero &> /dev/null; then
    echo "Error: Velero CLI not found"
    echo "Please install Velero CLI first:"
    echo "  macOS: brew install velero"
    echo "  Linux: https://velero.io/docs/main/basic-install/"
    exit 1
fi

echo ""
echo "========================================="
echo "1. Creating GCS Bucket for Backups"
echo "========================================="
echo ""

# Create GCS bucket
# Reference: https://cloud.google.com/storage/docs/creating-buckets
if gsutil ls -b gs://$BUCKET 2>/dev/null; then
    echo "Bucket gs://$BUCKET already exists"
else
    echo "Creating bucket gs://$BUCKET..."
    gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET/

    # Enable object versioning
    gsutil versioning set on gs://$BUCKET/

    echo "Bucket created successfully"
fi

echo ""
echo "========================================="
echo "2. Creating Service Account"
echo "========================================="
echo ""

# Create service account for Velero
# Reference: https://cloud.google.com/iam/docs/creating-managing-service-accounts
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL 2>/dev/null; then
    echo "Service account $SERVICE_ACCOUNT_EMAIL already exists"
else
    echo "Creating service account..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name "Velero service account" \
        --project=$PROJECT_ID

    echo "Service account created"
fi

echo ""
echo "========================================="
echo "3. Creating Custom IAM Role"
echo "========================================="
echo ""

# Create custom role with required permissions
# Reference: https://velero.io/docs/main/gcp-config/
ROLE_NAME="velero.server"
ROLE_TITLE="Velero Server"

cat > velero-role.yaml <<EOF
title: "$ROLE_TITLE"
description: "Velero server role with required permissions for backup and restore"
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
- storage.objects.create
- storage.objects.delete
- storage.objects.get
- storage.objects.list
EOF

# Create or update the role
if gcloud iam roles describe $ROLE_NAME --project=$PROJECT_ID 2>/dev/null; then
    echo "Updating existing custom role..."
    gcloud iam roles update $ROLE_NAME \
        --project=$PROJECT_ID \
        --file=velero-role.yaml
else
    echo "Creating custom IAM role..."
    gcloud iam roles create $ROLE_NAME \
        --project=$PROJECT_ID \
        --file=velero-role.yaml
fi

rm velero-role.yaml

echo ""
echo "========================================="
echo "4. Binding IAM Roles"
echo "========================================="
echo ""

# Bind custom role to service account
echo "Binding custom Velero role to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
    --role=projects/$PROJECT_ID/roles/$ROLE_NAME

# Grant objectAdmin role on the bucket
# Reference: https://cloud.google.com/storage/docs/access-control/using-iam-permissions
echo "Granting objectAdmin role on bucket..."
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT_EMAIL:objectAdmin gs://$BUCKET

echo ""
echo "========================================="
echo "5. Creating Service Account Key"
echo "========================================="
echo ""

KEY_FILE="credentials-velero.json"

if [ -f "$KEY_FILE" ]; then
    echo "Key file $KEY_FILE already exists"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing key file"
    else
        echo "Creating new service account key..."
        gcloud iam service-accounts keys create $KEY_FILE \
            --iam-account=$SERVICE_ACCOUNT_EMAIL
        echo "Key created: $KEY_FILE"
    fi
else
    echo "Creating service account key..."
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account=$SERVICE_ACCOUNT_EMAIL
    echo "Key created: $KEY_FILE"
fi

echo ""
echo "========================================="
echo "6. Installing Velero in Kubernetes"
echo "========================================="
echo ""

# Verify kubectl is configured
kubectl cluster-info > /dev/null 2>&1 || {
    echo "Error: kubectl not configured. Run ./gke-configure.sh first"
    exit 1
}

# Install Velero
# Reference: https://velero.io/docs/main/basic-install/
echo "Installing Velero..."
velero install \
    --provider gcp \
    --plugins velero/velero-plugin-for-gcp:v1.9.0 \
    --bucket $BUCKET \
    --secret-file ./$KEY_FILE \
    --use-volume-snapshots=true \
    --snapshot-location-config snapshotLocation=us-central1 \
    --backup-location-config serviceAccount=$SERVICE_ACCOUNT_EMAIL

echo ""
echo "Waiting for Velero deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/velero -n velero

echo ""
echo "========================================="
echo "7. Creating Backup Schedule"
echo "========================================="
echo ""

# Create a daily backup schedule
echo "Creating backup schedule..."
velero schedule create bcm-platform-daily \
    --schedule="$BACKUP_SCHEDULE" \
    --ttl "${RETENTION_DAYS}d" \
    --include-namespaces=bcm-platform,default

echo ""
echo "========================================="
echo "8. Verifying Installation"
echo "========================================="
echo ""

echo "Velero version:"
velero version

echo ""
echo "Velero backup locations:"
velero backup-location get

echo ""
echo "Velero snapshot locations:"
velero snapshot-location get

echo ""
echo "Velero schedules:"
velero schedule get

echo ""
echo "========================================="
echo "Velero Setup Complete!"
echo "========================================="
echo ""
echo "Configuration:"
echo "  Bucket: gs://$BUCKET"
echo "  Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "  Backup Schedule: $BACKUP_SCHEDULE"
echo "  Retention: $RETENTION_DAYS days"
echo ""
echo "Common Velero commands:"
echo "  # Create a manual backup"
echo "  velero backup create <backup-name> --include-namespaces bcm-platform"
echo ""
echo "  # List backups"
echo "  velero backup get"
echo ""
echo "  # Describe a backup"
echo "  velero backup describe <backup-name>"
echo ""
echo "  # Restore from backup"
echo "  velero restore create --from-backup <backup-name>"
echo ""
echo "  # Delete a backup"
echo "  velero backup delete <backup-name>"
echo ""
echo "IMPORTANT: Keep the credentials file secure!"
echo "  File: $KEY_FILE"
echo ""
