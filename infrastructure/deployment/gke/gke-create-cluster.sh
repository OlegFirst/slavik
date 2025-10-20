#!/bin/bash
#
# GKE Autopilot Cluster Creation Script
# Based on: https://cloud.google.com/sdk/gcloud/reference/container/clusters/create-auto
# Documentation: https://cloud.google.com/kubernetes-engine/docs/how-to/creating-an-autopilot-cluster
#

set -e

# Load configuration
if [ -f "terraform.tfvars" ]; then
    source <(grep -v '^#' terraform.tfvars | sed 's/[[:space:]]*=[[:space:]]*/=/' | sed 's/^/export /')
fi

# Default values if not set in terraform.tfvars
PROJECT_ID="${project_id:-my-gcp-project}"
CLUSTER_NAME="${cluster_name:-bcm-platform-autopilot}"
REGION="${region:-us-central1}"
RELEASE_CHANNEL="${release_channel:-regular}"
NETWORK="${network:-default}"
SUBNETWORK="${subnetwork:-default}"

echo "========================================="
echo "Creating GKE Autopilot Cluster"
echo "========================================="
echo "Project ID: $PROJECT_ID"
echo "Cluster Name: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Release Channel: $RELEASE_CHANNEL"
echo "========================================="

# Set the default project
# Reference: https://cloud.google.com/sdk/gcloud/reference/config/set
gcloud config set project "$PROJECT_ID"

# Enable required APIs
# Reference: https://cloud.google.com/sdk/gcloud/reference/services/enable
echo "Enabling required Google Cloud APIs..."
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable cloudtrace.googleapis.com
gcloud services enable clouderrorreporting.googleapis.com
gcloud services enable cloudprofiler.googleapis.com

# Create GKE Autopilot cluster
# Reference: https://cloud.google.com/sdk/gcloud/reference/container/clusters/create-auto
echo "Creating GKE Autopilot cluster..."
gcloud container clusters create-auto "$CLUSTER_NAME" \
    --region="$REGION" \
    --release-channel="$RELEASE_CHANNEL" \
    --network="$NETWORK" \
    --subnetwork="$SUBNETWORK" \
    --enable-private-nodes \
    --enable-private-endpoint \
    --enable-master-authorized-networks \
    --master-authorized-networks=0.0.0.0/0 \
    --enable-autorepair \
    --enable-autoupgrade \
    --enable-stackdriver-kubernetes \
    --logging=SYSTEM,WORKLOAD \
    --monitoring=SYSTEM \
    --enable-cloud-logging \
    --enable-cloud-monitoring \
    --labels=environment=production,platform=bcm,managed-by=gcloud

echo "========================================="
echo "Cluster creation initiated successfully!"
echo "========================================="
echo ""
echo "To check cluster status, run:"
echo "  gcloud container clusters describe $CLUSTER_NAME --region=$REGION"
echo ""
echo "To get cluster credentials, run:"
echo "  ./gke-configure.sh"
echo ""
