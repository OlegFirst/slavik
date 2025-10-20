#!/bin/bash
#
# DigitalOcean Kubernetes Add-ons Installation Script
# Based on official DigitalOcean documentation
# Reference: https://docs.digitalocean.com/products/kubernetes/how-to/manage-1click-apps/
#

set -e

# Configuration variables
CLUSTER_NAME="${CLUSTER_NAME:-bcm-platform-cluster}"
INSTALL_CERT_MANAGER="${INSTALL_CERT_MANAGER:-true}"
INSTALL_VELERO="${INSTALL_VELERO:-true}"
DO_SPACES_BUCKET="${DO_SPACES_BUCKET:-bcm-velero-backups}"
DO_SPACES_REGION="${DO_SPACES_REGION:-nyc3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Install DOKS Add-ons and Tools${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: helm is not installed${NC}"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Verify cluster connection
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Not connected to Kubernetes cluster${NC}"
    echo "Please run ./do-configure.sh first"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking existing 1-Click Apps...${NC}"
echo ""

# Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/1-click/list/
echo "Installed 1-Click Apps:"
doctl kubernetes 1-click list
echo ""

echo -e "${YELLOW}Step 2: Verifying ingress-nginx installation...${NC}"
echo ""

if kubectl get namespace ingress-nginx &> /dev/null; then
    echo -e "${GREEN}✓ ingress-nginx is installed${NC}"
    echo ""
    echo "Waiting for ingress-nginx pods to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s || echo -e "${YELLOW}⚠ Some pods may still be initializing${NC}"

    echo ""
    echo "Ingress Controller Status:"
    kubectl get pods -n ingress-nginx
    echo ""
    echo "LoadBalancer External IP:"
    kubectl get svc -n ingress-nginx ingress-nginx-controller
else
    echo -e "${YELLOW}⚠ ingress-nginx not found${NC}"
    echo "Installing ingress-nginx using 1-Click App..."
    # Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/1-click/install/
    doctl kubernetes 1-click install $CLUSTER_NAME --1-clicks ingress-nginx

    echo "Waiting for installation to complete (this may take a few minutes)..."
    sleep 30
fi
echo ""

echo -e "${YELLOW}Step 3: Verifying monitoring stack...${NC}"
echo ""

if kubectl get namespace monitoring &> /dev/null; then
    echo -e "${GREEN}✓ monitoring stack is installed${NC}"
    kubectl get pods -n monitoring
else
    echo -e "${YELLOW}⚠ monitoring stack not found${NC}"
    echo "Note: You can install monitoring using 1-Click App via DigitalOcean UI"
    echo "Reference: https://docs.digitalocean.com/products/kubernetes/how-to/manage-1click-apps/"
fi
echo ""

if [ "$INSTALL_CERT_MANAGER" = "true" ]; then
    echo -e "${YELLOW}Step 4: Installing cert-manager for TLS certificates...${NC}"
    echo ""

    if kubectl get namespace cert-manager &> /dev/null; then
        echo -e "${GREEN}✓ cert-manager already installed${NC}"
    else
        echo "Installing cert-manager using Helm..."
        # Reference: https://cert-manager.io/docs/installation/helm/

        # Add Jetstack Helm repository
        helm repo add jetstack https://charts.jetstack.io
        helm repo update

        # Install cert-manager
        helm install cert-manager jetstack/cert-manager \
            --namespace cert-manager \
            --create-namespace \
            --version v1.13.0 \
            --set installCRDs=true

        echo "Waiting for cert-manager pods to be ready..."
        kubectl wait --namespace cert-manager \
            --for=condition=ready pod \
            --all \
            --timeout=300s || echo -e "${YELLOW}⚠ Some pods may still be initializing${NC}"

        echo ""
        echo -e "${GREEN}✓ cert-manager installed successfully${NC}"
    fi

    echo ""
    kubectl get pods -n cert-manager
    echo ""
fi

if [ "$INSTALL_VELERO" = "true" ]; then
    echo -e "${YELLOW}Step 5: Installing Velero for backup and disaster recovery...${NC}"
    echo ""

    if kubectl get namespace velero &> /dev/null; then
        echo -e "${GREEN}✓ Velero already installed${NC}"
        kubectl get pods -n velero
    else
        echo "Setting up Velero for DigitalOcean Spaces..."
        echo ""

        # Check if Velero CLI is installed
        if ! command -v velero &> /dev/null; then
            echo -e "${RED}Error: Velero CLI is not installed${NC}"
            echo "Please install Velero CLI:"
            echo "  macOS: brew install velero"
            echo "  Linux: https://velero.io/docs/main/basic-install/"
            echo ""
            echo "After installing Velero CLI, run this script again."
            echo ""
        else
            echo "Velero CLI found. Please ensure you have:"
            echo "1. Created a DigitalOcean Space: $DO_SPACES_BUCKET"
            echo "2. Created credentials-velero file with your Spaces access keys"
            echo ""
            echo "To install Velero, run the following command manually:"
            echo ""
            echo -e "${GREEN}velero install \\${NC}"
            echo -e "${GREEN}  --provider velero.io/aws \\${NC}"
            echo -e "${GREEN}  --plugins velero/velero-plugin-for-aws:v1.10.0,digitalocean/velero-plugin:v1.1.0 \\${NC}"
            echo -e "${GREEN}  --bucket $DO_SPACES_BUCKET \\${NC}"
            echo -e "${GREEN}  --secret-file=./credentials-velero \\${NC}"
            echo -e "${GREEN}  --backup-location-config region=$DO_SPACES_REGION,s3ForcePathStyle=true,s3Url=https://${DO_SPACES_REGION}.digitaloceanspaces.com \\${NC}"
            echo -e "${GREEN}  --snapshot-location-config region=$DO_SPACES_REGION \\${NC}"
            echo -e "${GREEN}  --use-node-agent=true \\${NC}"
            echo -e "${GREEN}  --use-volume-snapshots=true \\${NC}"
            echo -e "${GREEN}  --features=EnableCSI \\${NC}"
            echo -e "${GREEN}  --wait${NC}"
            echo ""
            echo "Reference: https://github.com/digitalocean/velero-plugin"
            echo ""
        fi
    fi
    echo ""
fi

echo -e "${YELLOW}Step 6: Installing metrics-server (if not present)...${NC}"
echo ""

if kubectl get deployment metrics-server -n kube-system &> /dev/null; then
    echo -e "${GREEN}✓ metrics-server already installed${NC}"
else
    echo "Installing metrics-server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

    echo "Waiting for metrics-server to be ready..."
    sleep 10
    kubectl wait --namespace kube-system \
        --for=condition=ready pod \
        --selector=k8s-app=metrics-server \
        --timeout=120s || echo -e "${YELLOW}⚠ metrics-server may still be initializing${NC}"
fi

kubectl get deployment metrics-server -n kube-system
echo ""

echo -e "${YELLOW}Step 7: Summary of installed add-ons...${NC}"
echo ""

echo "Namespaces:"
kubectl get namespaces
echo ""

echo "Storage Classes:"
kubectl get storageclass
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Add-ons installation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Installed components:"
echo "  ✓ ingress-nginx (LoadBalancer)"
echo "  ✓ metrics-server (resource metrics)"
if [ "$INSTALL_CERT_MANAGER" = "true" ] && kubectl get namespace cert-manager &> /dev/null; then
    echo "  ✓ cert-manager (TLS certificates)"
fi
if [ "$INSTALL_VELERO" = "true" ] && kubectl get namespace velero &> /dev/null; then
    echo "  ✓ Velero (backup and disaster recovery)"
fi
echo ""
echo "Next steps:"
echo "1. Configure TLS certificates with cert-manager"
echo "2. Set up Velero backup schedules (if installed)"
echo "3. Run ./do-deploy-bcm.sh to deploy the BCM Platform"
echo ""
