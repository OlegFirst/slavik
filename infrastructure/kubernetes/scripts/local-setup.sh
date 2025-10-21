#!/usr/bin/env bash

################################################################################
# Local Kubernetes Setup Script
#
# Sets up local Kubernetes cluster for BCM Platform development and testing
# Supports: minikube, kind, Docker Desktop
#
# Usage: ./local-setup.sh [minikube|kind|docker-desktop]
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PLATFORM="${1:-minikube}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

log_info() { echo -e "${BLUE}ℹ${NC} $*"; }
log_success() { echo -e "${GREEN}✅${NC} $*"; }
log_warning() { echo -e "${YELLOW}⚠️${NC}  $*"; }
log_error() { echo -e "${RED}❌${NC} $*"; }
log_step() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▶${NC} $*"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

check_dependencies() {
    log_step "Checking Dependencies"

    local all_ok=true

    # Check kubectl
    if command -v kubectl &> /dev/null; then
        log_success "kubectl: $(kubectl version --client -o json | grep -o '"gitVersion":"[^"]*"' | cut -d'"' -f4)"
    else
        log_error "kubectl not found. Install: brew install kubectl"
        all_ok=false
    fi

    # Check Docker
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null; then
            log_success "Docker: running"
        else
            log_error "Docker daemon not running. Start Docker Desktop"
            all_ok=false
        fi
    else
        log_error "Docker not found. Install: https://www.docker.com/products/docker-desktop"
        all_ok=false
    fi

    # Check Helm
    if command -v helm &> /dev/null; then
        log_success "Helm: $(helm version --short)"
    else
        log_warning "Helm not found. Installing..."
        brew install helm || curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi

    if [[ "$all_ok" == false ]]; then
        log_error "Missing dependencies. Please install them and try again."
        exit 1
    fi
}

setup_minikube() {
    log_step "Setting up Minikube"

    # Check if minikube is installed
    if ! command -v minikube &> /dev/null; then
        log_info "Installing minikube..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install minikube
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
            sudo install minikube-linux-amd64 /usr/local/bin/minikube
        fi
    fi

    # Check if cluster already exists
    if minikube status &> /dev/null; then
        log_warning "Minikube cluster already running"
        read -p "Delete and recreate? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            minikube delete
        else
            log_info "Using existing cluster"
            return
        fi
    fi

    # Start minikube with BCM Platform requirements
    log_info "Starting minikube cluster..."
    minikube start \
        --cpus=4 \
        --memory=8192 \
        --disk-size=40gb \
        --kubernetes-version=v1.28.0 \
        --driver=docker \
        --addons=ingress,metrics-server,storage-provisioner

    # Enable Istio addon (if available)
    if minikube addons list | grep -q istio; then
        log_info "Enabling Istio addon..."
        minikube addons enable istio
    fi

    log_success "Minikube cluster ready"
}

setup_kind() {
    log_step "Setting up kind (Kubernetes in Docker)"

    # Check if kind is installed
    if ! command -v kind &> /dev/null; then
        log_info "Installing kind..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install kind
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
            chmod +x ./kind
            sudo mv ./kind /usr/local/bin/kind
        fi
    fi

    # Check if cluster already exists
    if kind get clusters | grep -q bcm-platform; then
        log_warning "kind cluster 'bcm-platform' already exists"
        read -p "Delete and recreate? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kind delete cluster --name bcm-platform
        else
            log_info "Using existing cluster"
            kubectl config use-context kind-bcm-platform
            return
        fi
    fi

    # Create kind cluster with custom config
    log_info "Creating kind cluster..."
    cat <<EOF | kind create cluster --name bcm-platform --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
- role: worker
EOF

    # Install nginx ingress controller
    log_info "Installing nginx ingress controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

    # Wait for ingress controller
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=90s

    # Install metrics-server
    log_info "Installing metrics-server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

    # Patch metrics-server for kind
    kubectl patch deployment metrics-server -n kube-system --type=json -p='[
        {
            "op": "add",
            "path": "/spec/template/spec/containers/0/args/-",
            "value": "--kubelet-insecure-tls"
        }
    ]'

    log_success "kind cluster ready"
}

setup_docker_desktop() {
    log_step "Setting up Docker Desktop Kubernetes"

    # Check if Docker Desktop K8s is enabled
    if ! kubectl config get-contexts | grep -q docker-desktop; then
        log_error "Docker Desktop Kubernetes not enabled"
        log_info "Enable it in: Docker Desktop → Settings → Kubernetes → Enable Kubernetes"
        exit 1
    fi

    # Switch to docker-desktop context
    kubectl config use-context docker-desktop

    # Install nginx ingress
    log_info "Installing nginx ingress controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

    # Wait for ingress controller
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=90s

    log_success "Docker Desktop Kubernetes ready"
}

install_monitoring() {
    log_step "Installing Monitoring Stack (Optional)"

    read -p "Install Prometheus + Grafana? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping monitoring stack"
        return
    fi

    # Add Prometheus Helm repo
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

    # Install kube-prometheus-stack
    log_info "Installing kube-prometheus-stack..."
    helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
        --set grafana.adminPassword=admin \
        --wait

    log_success "Monitoring stack installed"
    log_info "Grafana credentials: admin/admin"
    log_info "Access: kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80"
}

verify_cluster() {
    log_step "Verifying Cluster"

    log_info "Cluster info:"
    kubectl cluster-info

    echo ""
    log_info "Nodes:"
    kubectl get nodes

    echo ""
    log_info "Namespaces:"
    kubectl get namespaces

    echo ""
    log_info "Storage classes:"
    kubectl get storageclass

    # Test cluster functionality
    log_info "Testing cluster..."
    kubectl run test-pod --image=nginx --rm -it --restart=Never -- echo "Cluster is working!" || true
}

save_cluster_info() {
    log_step "Saving Cluster Information"

    local info_file="$K8S_DIR/LOCAL_CLUSTER_INFO.txt"

    cat > "$info_file" <<EOF
BCM Platform - Local Kubernetes Cluster
========================================

Platform: $PLATFORM
Created: $(date)
Kubernetes Version: $(kubectl version --short 2>/dev/null | grep Server || echo "Unknown")

Current Context:
$(kubectl config current-context)

Cluster Info:
$(kubectl cluster-info)

Nodes:
$(kubectl get nodes)

Important Commands:
-------------------

# Switch to this cluster
kubectl config use-context $(kubectl config current-context)

# Deploy BCM Platform
./infrastructure/kubernetes/scripts/local-deploy.sh

# Access services locally
kubectl port-forward -n bcm-platform svc/orchestration-service 8002:8002

# Stop cluster (minikube)
minikube stop

# Start cluster (minikube)
minikube start

# Delete cluster
$( [[ "$PLATFORM" == "minikube" ]] && echo "minikube delete" || echo "kind delete cluster --name bcm-platform" )

# View logs
kubectl logs -n bcm-platform deployment/orchestration-service -f

Monitoring:
-----------
# Access Grafana (if installed)
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80
# Username: admin, Password: admin

# Access Prometheus
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090

Next Steps:
-----------
1. Deploy BCM Platform: ./infrastructure/kubernetes/scripts/local-deploy.sh
2. Access services via port-forward
3. Run tests: ./infrastructure/kubernetes/scripts/smoke-tests.sh bcm-platform

EOF

    cat "$info_file"
    log_success "Cluster info saved to: $info_file"
}

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  BCM Platform - Local Kubernetes Setup"
    echo "  Platform: $PLATFORM"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_dependencies

    case "$PLATFORM" in
        minikube)
            setup_minikube
            ;;
        kind)
            setup_kind
            ;;
        docker-desktop)
            setup_docker_desktop
            ;;
        *)
            log_error "Unknown platform: $PLATFORM"
            log_info "Valid platforms: minikube, kind, docker-desktop"
            exit 1
            ;;
    esac

    verify_cluster
    install_monitoring
    save_cluster_info

    echo ""
    log_success "Local Kubernetes cluster ready!"
    echo ""
    log_info "Next steps:"
    echo "  1. Deploy BCM Platform:"
    echo "     ./infrastructure/kubernetes/scripts/local-deploy.sh"
    echo ""
    echo "  2. Access orchestration service:"
    echo "     kubectl port-forward -n bcm-platform svc/orchestration-service 8002:8002"
    echo ""
    echo "  3. Run smoke tests:"
    echo "     ./infrastructure/kubernetes/scripts/smoke-tests.sh bcm-platform"
    echo ""
}

main "$@"
