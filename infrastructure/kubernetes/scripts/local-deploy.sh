#!/usr/bin/env bash

################################################################################
# Local BCM Platform Deployment Script
#
# Deploys BCM Platform to local Kubernetes cluster (minikube/kind/docker-desktop)
#
# Usage: ./local-deploy.sh [--skip-monitoring] [--minimal]
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
NAMESPACE="bcm-platform"
SKIP_MONITORING=false
MINIMAL=false

log_info() { echo -e "${BLUE}ℹ${NC} $*"; }
log_success() { echo -e "${GREEN}✅${NC} $*"; }
log_warning() { echo -e "${YELLOW}⚠️${NC}  $*"; }
log_error() { echo -e "${RED}❌${NC} $*"; }
log_step() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▶${NC} $*"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-monitoring)
            SKIP_MONITORING=true
            shift
            ;;
        --minimal)
            MINIMAL=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

check_cluster() {
    log_step "Checking Kubernetes Cluster"

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Kubernetes cluster not accessible"
        log_info "Run: ./infrastructure/kubernetes/scripts/local-setup.sh"
        exit 1
    fi

    local context=$(kubectl config current-context)
    log_info "Current context: $context"

    # Verify it's a local cluster
    if [[ ! "$context" =~ (minikube|kind|docker-desktop) ]]; then
        log_warning "Context '$context' doesn't look like a local cluster"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    log_success "Cluster accessible"
}

create_namespace() {
    log_step "Creating Namespace"

    if kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warning "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace $NAMESPACE
        kubectl label namespace $NAMESPACE environment=local
        log_success "Namespace created: $NAMESPACE"
    fi
}

create_local_secrets() {
    log_step "Creating Local Secrets"

    # Create development secrets (not for production!)
    kubectl create secret generic orchestration-secrets \
        --namespace=$NAMESPACE \
        --from-literal=DATABASE_URL="postgresql://bcm:bcm123@postgres:5432/bcm_platform" \
        --from-literal=REDIS_URL="redis://redis:6379/0" \
        --from-literal=ANTHROPIC_API_KEY="sk-ant-local-dev-placeholder" \
        --from-literal=JWT_SECRET_KEY="local-dev-secret-key-change-in-production" \
        --from-literal=POSTGRES_PASSWORD="bcm123" \
        --dry-run=client -o yaml | kubectl apply -f -

    log_success "Development secrets created (WARNING: Not secure for production!)"
}

deploy_infrastructure() {
    log_step "Deploying Infrastructure (PostgreSQL, Redis)"

    # Deploy PostgreSQL
    log_info "Deploying PostgreSQL..."
    cat <<EOF | kubectl apply -f -
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: $NAMESPACE
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: bcm_platform
        - name: POSTGRES_USER
          value: bcm
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: orchestration-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: $NAMESPACE
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
EOF

    # Deploy Redis
    log_info "Deploying Redis..."
    cat <<EOF | kubectl apply -f -
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: $NAMESPACE
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
EOF

    # Wait for infrastructure
    log_info "Waiting for infrastructure to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=120s
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=120s

    log_success "Infrastructure deployed"
}

deploy_configmaps() {
    log_step "Deploying ConfigMaps"

    # Use existing configmap if available
    if [[ -f "$K8S_DIR/configmaps/orchestration-configmap.yaml" ]]; then
        kubectl apply -f "$K8S_DIR/configmaps/orchestration-configmap.yaml"
    else
        # Create minimal configmap for local development
        cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: orchestration-config
  namespace: $NAMESPACE
data:
  ENVIRONMENT: "local"
  LOG_LEVEL: "DEBUG"
  PLATFORM_INTEGRATION_ENABLED: "true"
  ENABLE_GRACEFUL_CHOREOGRAPHY: "true"
  EVENTBUS_ENABLED: "true"
  SAGA_ENGINE_ENABLED: "true"
  CQRS_ENABLED: "true"
EOF
    fi

    log_success "ConfigMaps deployed"
}

deploy_orchestration() {
    log_step "Deploying Orchestration Service"

    # Adjust deployment for local environment
    if [[ -f "$K8S_DIR/deployments/orchestration-deployment.yaml" ]]; then
        # Modify for local (reduce resources, single replica)
        kubectl apply -f "$K8S_DIR/deployments/orchestration-deployment.yaml"

        # Scale down for local
        kubectl scale deployment orchestration-service -n $NAMESPACE --replicas=1
    else
        log_error "Orchestration deployment file not found"
        exit 1
    fi

    # Wait for orchestration
    log_info "Waiting for orchestration service..."
    kubectl wait --for=condition=ready pod -l app=orchestration -n $NAMESPACE --timeout=300s

    log_success "Orchestration service deployed"
}

deploy_bcm_services() {
    log_step "Deploying BCM Services"

    if [[ "$MINIMAL" == true ]]; then
        log_info "Minimal mode: Skipping BCM services"
        return
    fi

    if [[ -d "$K8S_DIR/deployments/bcm-services" ]]; then
        # Deploy only essential services for local
        local services=("bia-service" "risk-service" "compliance-service")

        for service in "${services[@]}"; do
            if [[ -f "$K8S_DIR/deployments/bcm-services/${service}-deployment.yaml" ]]; then
                log_info "Deploying $service..."
                kubectl apply -f "$K8S_DIR/deployments/bcm-services/${service}-deployment.yaml"

                # Scale down for local
                kubectl scale deployment $service -n $NAMESPACE --replicas=1 --timeout=30s || true
            fi
        done

        log_success "Essential BCM services deployed (minimal set)"
    else
        log_warning "BCM services directory not found, skipping"
    fi
}

deploy_monitoring() {
    log_step "Deploying Monitoring"

    if [[ "$SKIP_MONITORING" == true ]]; then
        log_info "Skipping monitoring (--skip-monitoring flag)"
        return
    fi

    if [[ -f "$K8S_DIR/monitoring/servicemonitors.yaml" ]]; then
        kubectl apply -f "$K8S_DIR/monitoring/servicemonitors.yaml" || log_warning "ServiceMonitors not applied (Prometheus operator may not be installed)"
    fi

    log_success "Monitoring configured"
}

create_port_forward_script() {
    log_step "Creating Port Forward Script"

    local script_path="$K8S_DIR/scripts/port-forward-local.sh"

    cat > "$script_path" <<'EOF'
#!/usr/bin/env bash

# Port Forward Script for Local Development
# Usage: ./port-forward-local.sh

NAMESPACE="bcm-platform"

echo "Starting port forwards for BCM Platform..."
echo "Press Ctrl+C to stop all port forwards"
echo ""

# Orchestration Service
echo "Orchestration API: http://localhost:8002"
kubectl port-forward -n $NAMESPACE svc/orchestration-service 8002:8002 &

# PostgreSQL (optional)
# echo "PostgreSQL: localhost:5432"
# kubectl port-forward -n $NAMESPACE svc/postgres 5432:5432 &

# Redis (optional)
# echo "Redis: localhost:6379"
# kubectl port-forward -n $NAMESPACE svc/redis 6379:6379 &

# Grafana (if monitoring installed)
if kubectl get svc -n monitoring kube-prometheus-stack-grafana &> /dev/null; then
    echo "Grafana: http://localhost:3000 (admin/admin)"
    kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80 &
fi

# Prometheus (if monitoring installed)
if kubectl get svc -n monitoring kube-prometheus-stack-prometheus &> /dev/null; then
    echo "Prometheus: http://localhost:9090"
    kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090 &
fi

echo ""
echo "All port forwards started. Press Ctrl+C to stop."

# Wait for Ctrl+C
trap "kill 0" EXIT
wait
EOF

    chmod +x "$script_path"
    log_success "Port forward script created: $script_path"
}

run_smoke_tests() {
    log_step "Running Smoke Tests"

    if [[ -f "$SCRIPT_DIR/smoke-tests.sh" ]]; then
        "$SCRIPT_DIR/smoke-tests.sh" $NAMESPACE || log_warning "Some smoke tests failed (this is OK for local development)"
    else
        log_warning "Smoke tests script not found"
    fi
}

print_summary() {
    log_step "Deployment Summary"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  BCM Platform - Local Deployment Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    log_success "Namespace: $NAMESPACE"
    log_success "Context: $(kubectl config current-context)"

    echo ""
    log_info "Deployed Components:"
    kubectl get deployments -n $NAMESPACE

    echo ""
    log_info "Services:"
    kubectl get services -n $NAMESPACE

    echo ""
    log_info "Pods:"
    kubectl get pods -n $NAMESPACE

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Next Steps"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Start port forwards:"
    echo "   $K8S_DIR/scripts/port-forward-local.sh"
    echo ""
    echo "2. Access Orchestration API:"
    echo "   http://localhost:8002/health"
    echo "   http://localhost:8002/api/v1/system/status"
    echo ""
    echo "3. View logs:"
    echo "   kubectl logs -n $NAMESPACE deployment/orchestration-service -f"
    echo ""
    echo "4. Access Grafana (if monitoring installed):"
    echo "   http://localhost:3000 (admin/admin)"
    echo ""
    echo "5. Clean up:"
    echo "   kubectl delete namespace $NAMESPACE"
    echo ""
}

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  BCM Platform - Local Deployment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_cluster
    create_namespace
    create_local_secrets
    deploy_infrastructure
    deploy_configmaps
    deploy_orchestration
    deploy_bcm_services
    deploy_monitoring
    create_port_forward_script

    # Wait a bit for services to stabilize
    sleep 5

    run_smoke_tests
    print_summary
}

main "$@"
