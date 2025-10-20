#!/bin/bash
#
# GKE Add-ons Installation Script
# Based on official Google Cloud and Kubernetes documentation
# Istio: https://cloud.google.com/kubernetes-engine/docs/tutorials/secure-services-istio
# Monitoring: Built-in GKE monitoring via Cloud Operations
#

set -e

# Load configuration
if [ -f "terraform.tfvars" ]; then
    source <(grep -v '^#' terraform.tfvars | sed 's/[[:space:]]*=[[:space:]]*/=/' | sed 's/^/export /')
fi

# Default values
PROJECT_ID="${project_id:-my-gcp-project}"
CLUSTER_NAME="${cluster_name:-bcm-platform-autopilot}"
REGION="${region:-us-central1}"
ISTIO_VERSION="${istio_version:-1.20.2}"

echo "========================================="
echo "Installing GKE Add-ons"
echo "========================================="
echo "Project ID: $PROJECT_ID"
echo "Cluster Name: $CLUSTER_NAME"
echo "Region: $REGION"
echo "========================================="

# Ensure kubectl is configured
echo "Verifying kubectl configuration..."
kubectl cluster-info > /dev/null 2>&1 || {
    echo "kubectl not configured. Running gke-configure.sh..."
    ./gke-configure.sh
}

echo ""
echo "========================================="
echo "1. Installing Istio Service Mesh"
echo "========================================="
echo "Reference: https://istio.io/latest/docs/setup/getting-started/"
echo ""

# Download Istio
if [ ! -d "istio-${ISTIO_VERSION}" ]; then
    echo "Downloading Istio ${ISTIO_VERSION}..."
    curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} sh -
else
    echo "Istio ${ISTIO_VERSION} already downloaded"
fi

cd istio-${ISTIO_VERSION}
export PATH=$PWD/bin:$PATH

# Install Istio using istioctl
# Reference: https://istio.io/latest/docs/setup/install/istioctl/
echo "Installing Istio with default profile..."
istioctl install --set profile=default -y

# Enable Istio injection for default namespace
echo "Enabling Istio sidecar injection for default namespace..."
kubectl label namespace default istio-injection=enabled --overwrite

cd ..

echo ""
echo "========================================="
echo "2. Configuring GKE Monitoring"
echo "========================================="
echo "Reference: https://cloud.google.com/kubernetes-engine/docs/how-to/monitoring"
echo ""

# GKE Autopilot includes Cloud Operations for GKE by default
# Verify monitoring is enabled
echo "Verifying Cloud Operations (Stackdriver) is enabled..."
gcloud container clusters describe "$CLUSTER_NAME" \
    --region="$REGION" \
    --format="value(monitoringService,loggingService)"

echo ""
echo "Cloud Operations features:"
echo "  - Cloud Monitoring (metrics)"
echo "  - Cloud Logging (logs)"
echo "  - Cloud Trace (distributed tracing)"
echo "  - Cloud Profiler (CPU/memory profiling)"
echo ""

echo "========================================="
echo "3. Installing Kubernetes Dashboard (Optional)"
echo "========================================="
echo "Reference: https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/"
echo ""

read -p "Install Kubernetes Dashboard? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Deploy Kubernetes Dashboard
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

    echo ""
    echo "Kubernetes Dashboard installed."
    echo "To access the dashboard:"
    echo "  1. Create an admin service account:"
    echo "     kubectl create serviceaccount dashboard-admin-sa"
    echo "     kubectl create clusterrolebinding dashboard-admin-sa --clusterrole=cluster-admin --serviceaccount=default:dashboard-admin-sa"
    echo "  2. Get the token:"
    echo "     kubectl create token dashboard-admin-sa"
    echo "  3. Start proxy:"
    echo "     kubectl proxy"
    echo "  4. Access at: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
    echo ""
fi

echo ""
echo "========================================="
echo "4. Verifying Installed Components"
echo "========================================="
echo ""

echo "Istio components:"
kubectl get pods -n istio-system
echo ""

echo "All namespaces:"
kubectl get namespaces
echo ""

echo "========================================="
echo "Add-ons Installation Complete!"
echo "========================================="
echo ""
echo "Installed components:"
echo "  ✓ Istio Service Mesh v${ISTIO_VERSION}"
echo "  ✓ Cloud Operations (built-in)"
echo "  ✓ Cloud Monitoring"
echo "  ✓ Cloud Logging"
echo ""
echo "Next steps:"
echo "  1. Deploy BCM Platform: ./gke-deploy-bcm.sh"
echo "  2. Configure Velero backups: See README.md"
echo ""
