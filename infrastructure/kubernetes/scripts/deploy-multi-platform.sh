#!/usr/bin/env bash

################################################################################
# BCM Platform - Multi-Platform Unified Deployment Script
#
# Deploys BCM Platform to any Kubernetes cluster:
# - local (minikube/kind/docker-desktop)
# - gke (Google Kubernetes Engine)
# - digitalocean (DigitalOcean Kubernetes)
#
# Usage: ./deploy-multi-platform.sh <platform> [options]
#
# Examples:
#   ./deploy-multi-platform.sh local
#   ./deploy-multi-platform.sh gke --project my-gcp-project
#   ./deploy-multi-platform.sh digitalocean --token $DO_TOKEN
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INFRA_DIR="$(cd "$K8S_DIR/.." && pwd)"

# Default values
PLATFORM="${1:-}"
NAMESPACE="bcm-platform"
ENVIRONMENT="production"
SKIP_TESTS=false
DRY_RUN=false

log_info() { echo -e "${BLUE}ℹ${NC} $*"; }
log_success() { echo -e "${GREEN}✅${NC} $*"; }
log_warning() { echo -e "${YELLOW}⚠️${NC}  $*"; }
log_error() { echo -e "${RED}❌${NC} $*"; }
log_step() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▶${NC} $*"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

show_help() {
    cat <<EOF
BCM Platform - Multi-Platform Deployment Script

USAGE:
    ./deploy-multi-platform.sh <platform> [options]

PLATFORMS:
    local           Deploy to local Kubernetes (minikube/kind/docker-desktop)
    gke             Deploy to Google Kubernetes Engine
    digitalocean    Deploy to DigitalOcean Kubernetes
    do              Alias for digitalocean

OPTIONS:
    -h, --help                Show this help message
    -n, --namespace NAME      Kubernetes namespace (default: bcm-platform)
    -e, --environment ENV     Environment (production/staging, default: production)
    --skip-tests              Skip smoke tests after deployment
    --dry-run                 Show what would be deployed without deploying

PLATFORM-SPECIFIC OPTIONS:

    GKE:
        --project ID          GCP Project ID
        --region REGION       GCP Region (default: us-central1)
        --cluster NAME        Cluster name (default: bcm-platform-prod)

    DigitalOcean:
        --token TOKEN         DigitalOcean API token
        --region REGION       DO Region (default: nyc3)
        --cluster NAME        Cluster name (default: bcm-platform-prod)

    Local:
        --minimal             Deploy minimal set of services
        --skip-monitoring     Skip monitoring stack

EXAMPLES:
    # Local deployment
    ./deploy-multi-platform.sh local

    # GKE deployment
    ./deploy-multi-platform.sh gke --project my-gcp-project --region us-central1

    # DigitalOcean deployment
    ./deploy-multi-platform.sh digitalocean --token \$DO_TOKEN --region nyc3

    # Dry run
    ./deploy-multi-platform.sh gke --project my-project --dry-run

EOF
}

parse_arguments() {
    if [[ -z "$PLATFORM" ]]; then
        log_error "Platform not specified"
        show_help
        exit 1
    fi

    # Normalize platform name
    case "$PLATFORM" in
        do)
            PLATFORM="digitalocean"
            ;;
    esac

    shift # Remove platform argument

    # Parse remaining arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -n|--namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --project)
                GCP_PROJECT="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --cluster)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            --token)
                DO_TOKEN="$2"
                shift 2
                ;;
            --minimal)
                MINIMAL=true
                shift
                ;;
            --skip-monitoring)
                SKIP_MONITORING=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

validate_platform() {
    log_step "Validating Platform: $PLATFORM"

    case "$PLATFORM" in
        local)
            validate_local
            ;;
        gke)
            validate_gke
            ;;
        digitalocean)
            validate_digitalocean
            ;;
        *)
            log_error "Unknown platform: $PLATFORM"
            log_info "Valid platforms: local, gke, digitalocean"
            exit 1
            ;;
    esac

    log_success "Platform validation complete"
}

validate_local() {
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Local Kubernetes cluster not running"
        log_info "Run: ./infrastructure/kubernetes/scripts/local-setup.sh"
        exit 1
    fi

    local context=$(kubectl config current-context)
    if [[ ! "$context" =~ (minikube|kind|docker-desktop) ]]; then
        log_warning "Current context '$context' doesn't look like a local cluster"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

validate_gke() {
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found"
        log_info "Install: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    if [[ -z "${GCP_PROJECT:-}" ]]; then
        log_error "GCP Project ID required for GKE deployment"
        log_info "Use: --project YOUR_PROJECT_ID"
        exit 1
    fi

    # Set defaults
    REGION="${REGION:-us-central1}"
    CLUSTER_NAME="${CLUSTER_NAME:-bcm-platform-prod}"
}

validate_digitalocean() {
    if ! command -v doctl &> /dev/null; then
        log_error "doctl CLI not found"
        log_info "Install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi

    if [[ -z "${DO_TOKEN:-}" ]]; then
        log_error "DigitalOcean API token required"
        log_info "Use: --token YOUR_DO_TOKEN"
        log_info "Get token: https://cloud.digitalocean.com/account/api/tokens"
        exit 1
    fi

    # Set defaults
    REGION="${REGION:-nyc3}"
    CLUSTER_NAME="${CLUSTER_NAME:-bcm-platform-prod}"
}

deploy_to_platform() {
    log_step "Deploying to Platform: $PLATFORM"

    if [[ "$DRY_RUN" == true ]]; then
        log_warning "DRY RUN MODE - No changes will be made"
        show_deployment_plan
        return
    fi

    case "$PLATFORM" in
        local)
            deploy_local
            ;;
        gke)
            deploy_gke
            ;;
        digitalocean)
            deploy_digitalocean
            ;;
    esac

    log_success "Deployment complete"
}

deploy_local() {
    log_info "Deploying to local Kubernetes cluster"

    local deploy_script="$SCRIPT_DIR/local-deploy.sh"
    local args=()

    [[ "${SKIP_MONITORING:-false}" == true ]] && args+=(--skip-monitoring)
    [[ "${MINIMAL:-false}" == true ]] && args+=(--minimal)

    if [[ -x "$deploy_script" ]]; then
        "$deploy_script" "${args[@]}"
    else
        log_error "Local deployment script not found: $deploy_script"
        exit 1
    fi
}

deploy_gke() {
    log_info "Deploying to Google Kubernetes Engine"
    log_info "Project: $GCP_PROJECT"
    log_info "Region: $REGION"
    log_info "Cluster: $CLUSTER_NAME"

    local gke_dir="$INFRA_DIR/deployment/gke"

    if [[ ! -d "$gke_dir" ]]; then
        log_error "GKE deployment directory not found: $gke_dir"
        exit 1
    fi

    # Set GCP project
    gcloud config set project "$GCP_PROJECT"

    # Check if cluster exists
    if gcloud container clusters list --region="$REGION" --filter="name=$CLUSTER_NAME" --format="value(name)" | grep -q "$CLUSTER_NAME"; then
        log_info "Cluster $CLUSTER_NAME already exists"
    else
        log_info "Creating GKE cluster..."
        cd "$gke_dir"
        ./gke-create-cluster.sh
    fi

    # Configure kubectl
    log_info "Configuring kubectl..."
    cd "$gke_dir"
    ./gke-configure.sh

    # Install addons
    log_info "Installing addons..."
    ./gke-install-addons.sh

    # Deploy BCM Platform
    log_info "Deploying BCM Platform..."
    ./gke-deploy-bcm.sh
}

deploy_digitalocean() {
    log_info "Deploying to DigitalOcean Kubernetes"
    log_info "Region: $REGION"
    log_info "Cluster: $CLUSTER_NAME"

    local do_dir="$INFRA_DIR/deployment/digitalocean"

    if [[ ! -d "$do_dir" ]]; then
        log_error "DigitalOcean deployment directory not found: $do_dir"
        exit 1
    fi

    # Authenticate with DigitalOcean
    export DIGITALOCEAN_ACCESS_TOKEN="$DO_TOKEN"
    doctl auth init --access-token "$DO_TOKEN"

    # Check if cluster exists
    if doctl kubernetes cluster list --format Name --no-header | grep -q "^$CLUSTER_NAME$"; then
        log_info "Cluster $CLUSTER_NAME already exists"
    else
        log_info "Creating DigitalOcean Kubernetes cluster..."
        cd "$do_dir"
        ./do-create-cluster.sh
    fi

    # Configure kubectl
    log_info "Configuring kubectl..."
    cd "$do_dir"
    ./do-configure.sh

    # Install addons
    log_info "Installing addons..."
    ./do-install-addons.sh

    # Deploy BCM Platform
    log_info "Deploying BCM Platform..."
    ./do-deploy-bcm.sh
}

show_deployment_plan() {
    cat <<EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DRY RUN - Deployment Plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Platform:       $PLATFORM
Namespace:      $NAMESPACE
Environment:    $ENVIRONMENT

EOF

    case "$PLATFORM" in
        gke)
            cat <<EOF
GCP Project:    $GCP_PROJECT
Region:         $REGION
Cluster:        $CLUSTER_NAME

Steps:
  1. Create/verify GKE Autopilot cluster
  2. Configure kubectl access
  3. Install Istio service mesh
  4. Install monitoring addons
  5. Deploy orchestration service
  6. Deploy BCM services
  7. Configure Velero backups
  8. Run smoke tests

EOF
            ;;
        digitalocean)
            cat <<EOF
Region:         $REGION
Cluster:        $CLUSTER_NAME

Steps:
  1. Create/verify DOKS cluster
  2. Configure kubectl access
  3. Install ingress-nginx (1-Click)
  4. Install cert-manager
  5. Deploy orchestration service
  6. Deploy BCM services
  7. Configure Velero backups
  8. Run smoke tests

EOF
            ;;
        local)
            cat <<EOF
Context:        $(kubectl config current-context 2>/dev/null || echo "N/A")

Steps:
  1. Verify local cluster
  2. Create namespace
  3. Deploy infrastructure (PostgreSQL, Redis)
  4. Deploy orchestration service
  5. Deploy BCM services
  6. Run smoke tests

EOF
            ;;
    esac

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

run_smoke_tests() {
    if [[ "$SKIP_TESTS" == true ]]; then
        log_info "Skipping smoke tests (--skip-tests)"
        return
    fi

    log_step "Running Smoke Tests"

    local test_script="$SCRIPT_DIR/smoke-tests.sh"
    if [[ -x "$test_script" ]]; then
        "$test_script" "$NAMESPACE" || log_warning "Some smoke tests failed"
    else
        log_warning "Smoke test script not found: $test_script"
    fi
}

print_summary() {
    log_step "Deployment Summary"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  BCM Platform Deployed Successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    log_success "Platform: $PLATFORM"
    log_success "Namespace: $NAMESPACE"
    log_success "Context: $(kubectl config current-context)"

    echo ""
    log_info "Deployed Pods:"
    kubectl get pods -n "$NAMESPACE"

    echo ""
    log_info "Services:"
    kubectl get services -n "$NAMESPACE"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Next Steps"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    case "$PLATFORM" in
        local)
            echo "1. Start port forwards:"
            echo "   ./infrastructure/kubernetes/scripts/port-forward-local.sh"
            echo ""
            echo "2. Access Orchestration API:"
            echo "   http://localhost:8002/health"
            ;;
        gke)
            echo "1. Get external IP:"
            echo "   kubectl get ingress -n $NAMESPACE"
            echo ""
            echo "2. Set up DNS pointing to the LoadBalancer IP"
            echo ""
            echo "3. Access Grafana:"
            echo "   kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80"
            ;;
        digitalocean)
            echo "1. Get LoadBalancer IP:"
            echo "   kubectl get svc ingress-nginx-controller -n ingress-nginx"
            echo ""
            echo "2. Set up DNS pointing to the LoadBalancer IP"
            echo ""
            echo "3. Configure TLS certificates (Let's Encrypt)"
            ;;
    esac

    echo ""
    echo "4. View logs:"
    echo "   kubectl logs -n $NAMESPACE deployment/orchestration-service -f"
    echo ""
}

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  BCM Platform - Multi-Platform Deployment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    parse_arguments "$@"
    validate_platform
    deploy_to_platform

    if [[ "$DRY_RUN" == false ]]; then
        run_smoke_tests
        print_summary
    fi

    echo ""
    log_success "All done!"
    echo ""
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}⚠️${NC}  Deployment interrupted by user"; exit 130' INT

main "$@"
