#!/bin/bash
#
# DigitalOcean Kubernetes Configuration Script
# Based on official doctl SDK documentation
# Reference: https://docs.digitalocean.com/products/kubernetes/how-to/connect-to-cluster/
#

set -e

# Configuration variables
CLUSTER_NAME="${CLUSTER_NAME:-bcm-platform-cluster}"
KUBECONFIG_PATH="${KUBECONFIG_PATH:-$HOME/.kube/config}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Configure kubectl for DOKS Cluster${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}Error: doctl is not installed${NC}"
    echo "Please install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if doctl is authenticated
if ! doctl auth list &> /dev/null; then
    echo -e "${RED}Error: doctl is not authenticated${NC}"
    echo "Please run: doctl auth init"
    exit 1
fi

echo -e "${YELLOW}Step 1: Listing available clusters...${NC}"
echo ""
# Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/list/
doctl kubernetes cluster list
echo ""

echo -e "${YELLOW}Step 2: Downloading cluster kubeconfig...${NC}"
echo "Cluster: $CLUSTER_NAME"
echo "Kubeconfig path: $KUBECONFIG_PATH"
echo ""

# Save kubeconfig for the cluster
# Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/kubeconfig/save/
# This command downloads the kubeconfig, merges it with existing config, and sets the context
echo -e "${GREEN}Executing: doctl kubernetes cluster kubeconfig save $CLUSTER_NAME${NC}"
doctl kubernetes cluster kubeconfig save $CLUSTER_NAME

echo ""
echo -e "${GREEN}✓ Kubeconfig saved successfully!${NC}"
echo ""

echo -e "${YELLOW}Step 3: Verifying cluster connection...${NC}"
echo ""

# Get current context
CURRENT_CONTEXT=$(kubectl config current-context)
echo "Current context: $CURRENT_CONTEXT"
echo ""

# Display cluster info
echo "Cluster Info:"
kubectl cluster-info
echo ""

echo -e "${YELLOW}Step 4: Checking cluster nodes...${NC}"
echo ""
kubectl get nodes -o wide
echo ""

echo -e "${YELLOW}Step 5: Checking system pods...${NC}"
echo ""
kubectl get pods -n kube-system
echo ""

echo -e "${YELLOW}Step 6: Checking 1-Click Apps installation...${NC}"
echo ""

# Check if ingress-nginx is installed
if kubectl get namespace ingress-nginx &> /dev/null; then
    echo -e "${GREEN}✓ ingress-nginx namespace found${NC}"
    kubectl get pods -n ingress-nginx
    echo ""
    echo "Ingress Controller LoadBalancer:"
    kubectl get svc -n ingress-nginx
else
    echo -e "${YELLOW}⚠ ingress-nginx not found (may still be installing)${NC}"
fi
echo ""

# Check if monitoring stack is installed
if kubectl get namespace monitoring &> /dev/null; then
    echo -e "${GREEN}✓ monitoring namespace found${NC}"
    kubectl get pods -n monitoring
else
    echo -e "${YELLOW}⚠ monitoring namespace not found (may still be installing)${NC}"
fi
echo ""

echo -e "${YELLOW}Step 7: Checking available storage classes...${NC}"
echo ""
kubectl get storageclass
echo ""

echo -e "${YELLOW}Step 8: Getting cluster credentials information...${NC}"
echo ""
# Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/kubeconfig/show/
doctl kubernetes cluster kubeconfig show $CLUSTER_NAME
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}kubectl configured successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Cluster context: $CURRENT_CONTEXT"
echo ""
echo "Useful commands:"
echo "  kubectl get nodes                  - View cluster nodes"
echo "  kubectl get pods -A                - View all pods"
echo "  kubectl get svc -A                 - View all services"
echo "  doctl kubernetes cluster get $CLUSTER_NAME - View cluster details"
echo ""
echo "Next steps:"
echo "1. Run ./do-install-addons.sh to install additional monitoring and backup tools"
echo "2. Run ./do-deploy-bcm.sh to deploy the BCM Platform"
echo ""
