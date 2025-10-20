#!/usr/bin/env bash

################################################################################
# Production Deployment Script for BCM Platform
#
# This script automates the deployment of Platform Integration (Graceful Choreography)
# to a production Kubernetes cluster.
#
# Usage:
#   ./deploy-production.sh [options]
#
# Options:
#   --environment <env>    Deployment environment (staging|production)
#   --namespace <ns>       Kubernetes namespace (default: bcm-platform)
#   --skip-deps           Skip infrastructure dependencies
#   --dry-run             Show what would be deployed without applying
#   --help                Show this help message
#
# Prerequisites:
#   - kubectl configured and connected to cluster
#   - Helm 3.x installed
#   - Cluster admin access
#   - Secrets prepared
#
# Version: 1.0.0
# Date: 2025-10-20
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default configuration
ENVIRONMENT="${ENVIRONMENT:-staging}"
NAMESPACE="${NAMESPACE:-bcm-platform}"
SKIP_DEPS=false
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$K8S_DIR/../.." && pwd)"

################################################################################
# Functions
################################################################################

log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✅${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC}  $*"
}

log_error() {
    echo -e "${RED}❌${NC} $*"
}

log_step() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▶${NC} $*"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

show_help() {
    head -n 30 "$0" | tail -n +3 | sed 's/^# //'
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                ;;
        esac
    done
}

check_prerequisites() {
    log_step "Checking Prerequisites"

    local all_ok=true

    # Check kubectl
    if command -v kubectl &> /dev/null; then
        log_success "kubectl installed: $(kubectl version --client --short 2>/dev/null || echo 'unknown')"
    else
        log_error "kubectl not found"
        all_ok=false
    fi

    # Check helm
    if command -v helm &> /dev/null; then
        log_success "helm installed: $(helm version --short)"
    else
        log_error "helm not found"
        all_ok=false
    fi

    # Check cluster connectivity
    if kubectl cluster-info &> /dev/null; then
        log_success "Cluster connectivity OK"
        kubectl cluster-info | head -1
    else
        log_error "Cannot connect to Kubernetes cluster"
        all_ok=false
    fi

    # Check cluster version
    local k8s_version
    k8s_version=$(kubectl version -o json 2>/dev/null | grep -o '"gitVersion":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [[ -n "$k8s_version" ]]; then
        log_success "Kubernetes version: $k8s_version"
    else
        log_warning "Could not determine Kubernetes version"
    fi

    # Check required directories
    if [[ -d "$K8S_DIR/deployments" ]]; then
        log_success "Deployment manifests found"
    else
        log_error "Deployment manifests not found at $K8S_DIR/deployments"
        all_ok=false
    fi

    if [[ "$all_ok" == false ]]; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    log_success "All prerequisites satisfied"
}

confirm_deployment() {
    log_step "Deployment Configuration"

    echo "  Environment:  $ENVIRONMENT"
    echo "  Namespace:    $NAMESPACE"
    echo "  Skip Deps:    $SKIP_DEPS"
    echo "  Dry Run:      $DRY_RUN"
    echo "  K8s Context:  $(kubectl config current-context)"
    echo ""

    if [[ "$DRY_RUN" == false ]]; then
        read -rp "Proceed with deployment? (yes/no): " confirm
        if [[ "$confirm" != "yes" ]]; then
            log_warning "Deployment cancelled by user"
            exit 0
        fi
    else
        log_info "DRY RUN MODE - No changes will be applied"
    fi
}

apply_manifest() {
    local manifest="$1"
    local description="${2:-manifest}"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Would apply $description"
        kubectl apply -f "$manifest" --namespace="$NAMESPACE" --dry-run=client
    else
        log_info "Applying $description..."
        kubectl apply -f "$manifest" --namespace="$NAMESPACE"
    fi
}

create_namespace() {
    log_step "Creating Namespace"

    if [[ "$DRY_RUN" == false ]]; then
        kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
        kubectl label namespace "$NAMESPACE" environment="$ENVIRONMENT" --overwrite
        kubectl label namespace "$NAMESPACE" managed-by=platform-integration --overwrite
    else
        log_info "DRY RUN: Would create namespace $NAMESPACE"
    fi

    log_success "Namespace ready: $NAMESPACE"
}

deploy_infrastructure() {
    if [[ "$SKIP_DEPS" == true ]]; then
        log_warning "Skipping infrastructure dependencies (--skip-deps)"
        return
    fi

    log_step "Deploying Infrastructure Dependencies"

    log_info "Note: For production, use external PostgreSQL and Redis"
    log_info "      For testing, you can deploy with Helm (see DEPLOYMENT_GUIDE.md)"

    # Check if postgres exists
    if kubectl get statefulset postgres -n "$NAMESPACE" &> /dev/null; then
        log_success "PostgreSQL already deployed"
    else
        log_warning "PostgreSQL not found - deploy manually or with Helm"
    fi

    # Check if redis exists
    if kubectl get statefulset redis-master -n "$NAMESPACE" &> /dev/null; then
        log_success "Redis already deployed"
    else
        log_warning "Redis not found - deploy manually or with Helm"
    fi
}

deploy_secrets() {
    log_step "Deploying Secrets"

    # Check if secrets exist
    if kubectl get secret orchestration-secrets -n "$NAMESPACE" &> /dev/null; then
        log_success "orchestration-secrets already exists"
    else
        log_error "orchestration-secrets not found!"
        log_info "Create secrets before deploying:"
        log_info "  kubectl create secret generic orchestration-secrets \\"
        log_info "    --from-literal=database-url=\"postgresql+asyncpg://...\" \\"
        log_info "    --from-literal=redis-url=\"redis://...\" \\"
        log_info "    --from-literal=anthropic-api-key=\"...\" \\"
        log_info "    --from-literal=jwt-secret-key=\"...\" \\"
        log_info "    --namespace=$NAMESPACE"

        if [[ "$DRY_RUN" == false ]]; then
            exit 1
        fi
    fi

    if kubectl get secret bcm-secrets -n "$NAMESPACE" &> /dev/null; then
        log_success "bcm-secrets already exists"
    else
        log_warning "bcm-secrets not found - will be created from orchestration-secrets"

        if [[ "$DRY_RUN" == false ]]; then
            # Copy orchestration-secrets to bcm-secrets
            kubectl get secret orchestration-secrets -n "$NAMESPACE" -o yaml | \
                sed "s/name: orchestration-secrets/name: bcm-secrets/" | \
                kubectl apply -f -
            log_success "bcm-secrets created"
        fi
    fi
}

deploy_configmaps() {
    log_step "Deploying ConfigMaps"

    local configmap_dir="$K8S_DIR/configmaps"

    if [[ -d "$configmap_dir" ]]; then
        for cm_file in "$configmap_dir"/*.yaml; do
            if [[ -f "$cm_file" ]]; then
                local cm_name=$(basename "$cm_file" .yaml)
                apply_manifest "$cm_file" "ConfigMap: $cm_name"
            fi
        done
        log_success "ConfigMaps deployed"
    else
        log_warning "ConfigMaps directory not found: $configmap_dir"
    fi
}

deploy_orchestration() {
    log_step "Deploying Orchestration Layer"

    local orch_manifest="$K8S_DIR/deployments/orchestration-deployment.yaml"

    if [[ -f "$orch_manifest" ]]; then
        apply_manifest "$orch_manifest" "Orchestration Service"

        if [[ "$DRY_RUN" == false ]]; then
            log_info "Waiting for orchestration deployment to be ready..."
            kubectl rollout status deployment/orchestration-service -n "$NAMESPACE" --timeout=300s
            log_success "Orchestration layer deployed successfully"
        fi
    else
        log_error "Orchestration manifest not found: $orch_manifest"
        exit 1
    fi
}

deploy_bcm_services() {
    log_step "Deploying BCM Services"

    local bcm_dir="$K8S_DIR/deployments/bcm-services"

    if [[ -d "$bcm_dir" ]]; then
        local service_count=0

        for service_file in "$bcm_dir"/*.yaml; do
            if [[ -f "$service_file" ]]; then
                local service_name=$(basename "$service_file" .yaml | sed 's/-deployment//')
                apply_manifest "$service_file" "BCM Service: $service_name"
                ((service_count++))
            fi
        done

        if [[ "$DRY_RUN" == false ]]; then
            log_info "Waiting for BCM services to be ready..."
            kubectl rollout status deployment -l component=bcm-service -n "$NAMESPACE" --timeout=600s
            log_success "$service_count BCM services deployed successfully"
        else
            log_info "DRY RUN: Would deploy $service_count BCM services"
        fi
    else
        log_error "BCM services directory not found: $bcm_dir"
        exit 1
    fi
}

deploy_ingress() {
    log_step "Deploying Ingress"

    local ingress_dir="$K8S_DIR/ingress"

    if [[ -d "$ingress_dir" ]]; then
        for ingress_file in "$ingress_dir"/*.yaml; do
            if [[ -f "$ingress_file" ]]; then
                local ingress_name=$(basename "$ingress_file" .yaml)
                apply_manifest "$ingress_file" "Ingress: $ingress_name"
            fi
        done

        if [[ "$DRY_RUN" == false ]]; then
            sleep 5
            log_info "Ingress status:"
            kubectl get ingress -n "$NAMESPACE"
        fi

        log_success "Ingress deployed"
    else
        log_warning "Ingress directory not found: $ingress_dir"
    fi
}

deploy_monitoring() {
    log_step "Deploying Monitoring"

    local monitoring_dir="$K8S_DIR/monitoring"

    if [[ -d "$monitoring_dir" ]]; then
        # Deploy ServiceMonitors
        if [[ -f "$monitoring_dir/servicemonitors.yaml" ]]; then
            apply_manifest "$monitoring_dir/servicemonitors.yaml" "ServiceMonitors"
        fi

        # Deploy Grafana dashboard
        if [[ -f "$monitoring_dir/grafana-platform-integration-dashboard.json" ]] && [[ "$DRY_RUN" == false ]]; then
            log_info "Creating Grafana dashboard ConfigMap..."
            kubectl create configmap grafana-dashboard-platform-integration \
                --from-file="$monitoring_dir/grafana-platform-integration-dashboard.json" \
                --namespace=monitoring \
                --dry-run=client -o yaml | kubectl apply -f -

            kubectl label configmap grafana-dashboard-platform-integration \
                grafana_dashboard=1 \
                --namespace=monitoring \
                --overwrite
        fi

        log_success "Monitoring deployed"
    else
        log_warning "Monitoring directory not found: $monitoring_dir"
    fi
}

run_smoke_tests() {
    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN: Skipping smoke tests"
        return
    fi

    log_step "Running Smoke Tests"

    # Wait a bit for services to stabilize
    sleep 10

    # Test 1: Check pod status
    log_info "Test 1: Checking pod status..."
    local failed_pods
    failed_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null | wc -l)

    if [[ "$failed_pods" -eq 0 ]]; then
        log_success "All pods running"
    else
        log_error "$failed_pods pod(s) not in Running state"
        kubectl get pods -n "$NAMESPACE" | grep -v "Running"
    fi

    # Test 2: Check orchestration health
    log_info "Test 2: Checking orchestration health..."
    local orch_pod
    orch_pod=$(kubectl get pod -n "$NAMESPACE" -l app=orchestration -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [[ -n "$orch_pod" ]]; then
        if kubectl exec -n "$NAMESPACE" "$orch_pod" -- curl -sf http://localhost:8002/health > /dev/null 2>&1; then
            log_success "Orchestration health check passed"
        else
            log_error "Orchestration health check failed"
        fi
    else
        log_error "Orchestration pod not found"
    fi

    # Test 3: Check service endpoints
    log_info "Test 3: Checking service endpoints..."
    local services_without_endpoints=0

    while IFS= read -r svc; do
        if ! kubectl get endpoints "$svc" -n "$NAMESPACE" -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null | grep -q "."; then
            log_warning "Service $svc has no endpoints"
            ((services_without_endpoints++))
        fi
    done < <(kubectl get svc -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

    if [[ "$services_without_endpoints" -eq 0 ]]; then
        log_success "All services have endpoints"
    else
        log_warning "$services_without_endpoints service(s) have no endpoints"
    fi

    # Test 4: Check HPA status
    log_info "Test 4: Checking HPA status..."
    local hpa_count
    hpa_count=$(kubectl get hpa -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)

    if [[ "$hpa_count" -gt 0 ]]; then
        log_success "$hpa_count HPA(s) configured"
    else
        log_warning "No HPAs found"
    fi

    log_success "Smoke tests completed"
}

show_deployment_info() {
    log_step "Deployment Information"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "DRY RUN completed - no changes were applied"
        return
    fi

    echo "Namespace: $NAMESPACE"
    echo ""

    echo "Pods:"
    kubectl get pods -n "$NAMESPACE" -o wide
    echo ""

    echo "Services:"
    kubectl get svc -n "$NAMESPACE"
    echo ""

    echo "Ingress:"
    kubectl get ingress -n "$NAMESPACE"
    echo ""

    # Get ingress URL
    local ingress_ip
    ingress_ip=$(kubectl get ingress orchestration-ingress -n "$NAMESPACE" \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

    if [[ "$ingress_ip" != "pending" ]] && [[ -n "$ingress_ip" ]]; then
        echo "Access URLs:"
        echo "  Health:  http://$ingress_ip/health"
        echo "  Status:  http://$ingress_ip/api/v1/system/status"
        echo "  Metrics: http://$ingress_ip/metrics"
    else
        log_info "Ingress IP pending - check later with:"
        log_info "  kubectl get ingress orchestration-ingress -n $NAMESPACE"
    fi

    echo ""
    log_success "Deployment completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "  1. Monitor pods: kubectl get pods -n $NAMESPACE -w"
    echo "  2. Check logs: kubectl logs -n $NAMESPACE -l app=orchestration"
    echo "  3. Access Grafana dashboard: kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80"
    echo "  4. Run integration tests"
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse command line arguments
    parse_args "$@"

    # Print banner
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  BCM Platform - Production Deployment Script"
    echo "  Version: 1.0.0"
    echo "  Environment: $ENVIRONMENT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Run deployment steps
    check_prerequisites
    confirm_deployment
    create_namespace
    deploy_infrastructure
    deploy_secrets
    deploy_configmaps
    deploy_orchestration
    deploy_bcm_services
    deploy_ingress
    deploy_monitoring
    run_smoke_tests
    show_deployment_info
}

# Run main function
main "$@"
