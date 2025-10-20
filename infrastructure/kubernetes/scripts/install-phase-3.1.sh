#!/usr/bin/env bash

################################################################################
# Phase 3.1 Installation Script
#
# Installs advanced production features:
# - Service Mesh (Istio)
# - GitOps (ArgoCD)
# - Distributed Tracing (Jaeger)
# - Disaster Recovery (Velero)
#
# Usage: ./install-phase-3.1.sh [--component <component>]
#
# Components: istio, argocd, jaeger, velero, all (default)
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

COMPONENT="${1:-all}"
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

install_istio() {
    log_step "Installing Istio Service Mesh"

    # Check if Istio is already installed
    if kubectl get namespace istio-system &> /dev/null; then
        log_warning "Istio already installed, skipping..."
        return
    fi

    # Download Istio
    log_info "Downloading Istio..."
    curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.20.0 sh -

    cd istio-1.20.0
    export PATH=$PWD/bin:$PATH

    # Install Istio with production profile
    log_info "Installing Istio with production profile..."
    istioctl install --set profile=production -y

    # Verify installation
    kubectl wait --for=condition=ready pod -l app=istiod -n istio-system --timeout=300s

    log_success "Istio installed successfully"

    # Enable sidecar injection for bcm-platform namespace
    log_info "Enabling sidecar injection for bcm-platform..."
    kubectl label namespace bcm-platform istio-injection=enabled --overwrite

    # Deploy Istio addons (Kiali, Jaeger, Prometheus, Grafana)
    log_info "Installing Istio observability addons..."
    kubectl apply -f samples/addons/kiali.yaml
    kubectl apply -f samples/addons/prometheus.yaml
    kubectl apply -f samples/addons/grafana.yaml
    kubectl apply -f samples/addons/jaeger.yaml

    cd ..

    log_success "Istio service mesh setup complete"
}

deploy_istio_configs() {
    log_step "Deploying Istio Configurations"

    if [[ ! -d "$K8S_DIR/istio" ]]; then
        log_error "Istio configuration directory not found"
        return 1
    fi

    # Deploy Gateway
    log_info "Deploying Istio Gateway..."
    kubectl apply -f "$K8S_DIR/istio/gateway.yaml"

    # Deploy VirtualServices
    log_info "Deploying VirtualServices..."
    kubectl apply -f "$K8S_DIR/istio/virtual-service-orchestration.yaml"

    # Deploy DestinationRules
    log_info "Deploying DestinationRules..."
    kubectl apply -f "$K8S_DIR/istio/destination-rule-orchestration.yaml"

    # Deploy Security policies
    log_info "Deploying Security policies..."
    kubectl apply -f "$K8S_DIR/istio/security.yaml"

    log_success "Istio configurations deployed"
}

install_argocd() {
    log_step "Installing ArgoCD"

    # Check if ArgoCD is already installed
    if kubectl get namespace argocd &> /dev/null; then
        log_warning "ArgoCD already installed, skipping..."
        return
    fi

    # Create namespace
    kubectl create namespace argocd

    # Install ArgoCD
    log_info "Installing ArgoCD..."
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

    # Wait for ArgoCD to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

    # Get initial admin password
    ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

    log_success "ArgoCD installed successfully"
    log_info "ArgoCD admin password: $ARGOCD_PASSWORD"
    log_info "Access ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
    log_info "Then open: https://localhost:8080"

    # Install ArgoCD CLI (optional)
    if ! command -v argocd &> /dev/null; then
        log_info "Installing ArgoCD CLI..."
        curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        chmod +x /usr/local/bin/argocd
    fi
}

deploy_argocd_apps() {
    log_step "Deploying ArgoCD Applications"

    if [[ ! -d "$K8S_DIR/argocd" ]]; then
        log_error "ArgoCD configuration directory not found"
        return 1
    fi

    # Deploy AppProject
    log_info "Creating ArgoCD Project..."
    kubectl apply -f "$K8S_DIR/argocd/project.yaml"

    # Deploy Applications
    log_info "Creating ArgoCD Applications..."
    kubectl apply -f "$K8S_DIR/argocd/application-bcm-platform.yaml"

    log_success "ArgoCD applications deployed"
    log_info "Check status: kubectl get applications -n argocd"
}

install_jaeger() {
    log_step "Installing Jaeger (Distributed Tracing)"

    # Check if observability namespace exists
    if ! kubectl get namespace observability &> /dev/null; then
        kubectl create namespace observability
    fi

    # Install Jaeger Operator
    log_info "Installing Jaeger Operator..."
    kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability

    # Wait for operator
    kubectl wait --for=condition=ready pod -l name=jaeger-operator -n observability --timeout=300s

    log_success "Jaeger Operator installed"
    log_info "Deploy Jaeger instance: kubectl apply -f infrastructure/kubernetes/tracing/jaeger.yaml"
}

install_velero() {
    log_step "Installing Velero (Backup & Disaster Recovery)"

    # Check if Velero CLI is installed
    if ! command -v velero &> /dev/null; then
        log_info "Installing Velero CLI..."
        wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
        tar -xvf velero-v1.12.0-linux-amd64.tar.gz
        sudo mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/
        rm -rf velero-v1.12.0-linux-amd64*
    fi

    log_warning "Velero server installation requires cloud provider credentials"
    log_info "For AWS: velero install --provider aws --plugins velero/velero-plugin-for-aws:v1.8.0 --bucket <bucket> --secret-file ./credentials-velero"
    log_info "For GCP: velero install --provider gcp --plugins velero/velero-plugin-for-gcp:v1.8.0 --bucket <bucket> --secret-file ./credentials-velero"
    log_info "For Azure: velero install --provider azure --plugins velero/velero-plugin-for-microsoft-azure:v1.8.0 --bucket <bucket> --secret-file ./credentials-velero"

    log_success "Velero CLI installed"
}

verify_installation() {
    log_step "Verifying Installation"

    local all_ok=true

    # Check Istio
    if kubectl get namespace istio-system &> /dev/null; then
        log_success "Istio: installed"
    else
        log_warning "Istio: not installed"
        all_ok=false
    fi

    # Check ArgoCD
    if kubectl get namespace argocd &> /dev/null; then
        log_success "ArgoCD: installed"
    else
        log_warning "ArgoCD: not installed"
        all_ok=false
    fi

    # Check Jaeger
    if kubectl get namespace observability &> /dev/null; then
        log_success "Jaeger: installed"
    else
        log_warning "Jaeger: not installed"
        all_ok=false
    fi

    # Check Velero
    if command -v velero &> /dev/null; then
        log_success "Velero CLI: installed"
    else
        log_warning "Velero CLI: not installed"
        all_ok=false
    fi

    if [[ "$all_ok" == true ]]; then
        log_success "All Phase 3.1 components verified"
    else
        log_warning "Some components are missing"
    fi
}

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Phase 3.1 Installation - Advanced Production Features"
    echo "  Component: $COMPONENT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    case "$COMPONENT" in
        istio)
            install_istio
            deploy_istio_configs
            ;;
        argocd)
            install_argocd
            deploy_argocd_apps
            ;;
        jaeger)
            install_jaeger
            ;;
        velero)
            install_velero
            ;;
        all)
            install_istio
            deploy_istio_configs
            install_argocd
            deploy_argocd_apps
            install_jaeger
            install_velero
            verify_installation
            ;;
        *)
            log_error "Unknown component: $COMPONENT"
            log_info "Valid components: istio, argocd, jaeger, velero, all"
            exit 1
            ;;
    esac

    echo ""
    log_success "Phase 3.1 installation complete!"
    echo ""
    log_info "Next steps:"
    echo "  1. Access Kiali: istioctl dashboard kiali"
    echo "  2. Access ArgoCD: kubectl port-forward svc/argocd-server -n argocd 8080:443"
    echo "  3. Access Jaeger: kubectl port-forward -n observability svc/jaeger-query 16686:16686"
    echo "  4. Configure Velero backups"
}

main "$@"
