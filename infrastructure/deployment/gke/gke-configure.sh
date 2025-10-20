#!/bin/bash
#
# GKE Cluster kubectl Configuration Script
# Based on: https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials
# Documentation: https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl
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

echo "========================================="
echo "Configuring kubectl for GKE Cluster"
echo "========================================="
echo "Project ID: $PROJECT_ID"
echo "Cluster Name: $CLUSTER_NAME"
echo "Region: $REGION"
echo "========================================="

# Set the default project
gcloud config set project "$PROJECT_ID"

# Install gke-gcloud-auth-plugin if not already installed
# Reference: https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl
echo "Checking for gke-gcloud-auth-plugin..."
if ! command -v gke-gcloud-auth-plugin &> /dev/null; then
    echo "Installing gke-gcloud-auth-plugin..."
    gcloud components install gke-gcloud-auth-plugin
else
    echo "gke-gcloud-auth-plugin is already installed"
fi

# Get cluster credentials and configure kubectl
# Reference: https://cloud.google.com/sdk/gcloud/reference/container/clusters/get-credentials
echo "Fetching cluster credentials..."
gcloud container clusters get-credentials "$CLUSTER_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID"

echo ""
echo "========================================="
echo "kubectl configured successfully!"
echo "========================================="
echo ""

# Verify connection
echo "Verifying cluster connection..."
kubectl cluster-info
echo ""
kubectl get nodes
echo ""

echo "Current kubectl context:"
kubectl config current-context
echo ""

echo "To view cluster details:"
echo "  kubectl cluster-info"
echo "  kubectl get nodes"
echo "  kubectl get namespaces"
echo ""
