#!/usr/bin/env bash

################################################################################
# Prerequisites Validation Script
#
# Validates that all prerequisites are met before deploying to Kubernetes
#
# Usage: ./validate-prerequisites.sh [--namespace <namespace>]
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="${1:-bcm-platform}"
ERRORS=0
WARNINGS=0

log_check() { echo -e "${BLUE}[CHECK]${NC} $*"; }
log_pass() { echo -e "${GREEN}[✓]${NC} $*"; }
log_fail() { echo -e "${RED}[✗]${NC} $*"; ((ERRORS++)); }
log_warn() { echo -e "${YELLOW}[!]${NC} $*"; ((WARNINGS++)); }

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Prerequisites Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. kubectl
log_check "Checking kubectl..."
if command -v kubectl &> /dev/null; then
    log_pass "kubectl found: $(kubectl version --client --short 2>/dev/null | head -1)"
else
    log_fail "kubectl not installed"
fi

# 2. helm
log_check "Checking helm..."
if command -v helm &> /dev/null; then
    log_pass "helm found: $(helm version --short)"
else
    log_warn "helm not installed (optional)"
fi

# 3. Cluster connectivity
log_check "Checking cluster connectivity..."
if kubectl cluster-info &> /dev/null; then
    log_pass "Connected to cluster: $(kubectl config current-context)"
else
    log_fail "Cannot connect to Kubernetes cluster"
fi

# 4. Cluster version
log_check "Checking Kubernetes version..."
K8S_VERSION=$(kubectl version -o json 2>/dev/null | grep -o '"gitVersion":"v[^"]*"' | head -1 | cut -d'"' -f4 | sed 's/v//')
if [[ -n "$K8S_VERSION" ]]; then
    MAJOR=$(echo "$K8S_VERSION" | cut -d'.' -f1)
    MINOR=$(echo "$K8S_VERSION" | cut -d'.' -f2)
    if [[ "$MAJOR" -ge 1 ]] && [[ "$MINOR" -ge 28 ]]; then
        log_pass "Kubernetes version: v$K8S_VERSION (>= v1.28)"
    else
        log_warn "Kubernetes version: v$K8S_VERSION (recommended >= v1.28)"
    fi
else
    log_warn "Could not determine Kubernetes version"
fi

# 5. Node resources
log_check "Checking node resources..."
NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l | tr -d ' ')
if [[ "$NODE_COUNT" -ge 3 ]]; then
    log_pass "Node count: $NODE_COUNT (>= 3)"
else
    log_warn "Node count: $NODE_COUNT (recommended >= 3 for production)"
fi

# 6. Storage classes
log_check "Checking storage classes..."
if kubectl get storageclass &> /dev/null; then
    SC_COUNT=$(kubectl get storageclass --no-headers | wc -l | tr -d ' ')
    log_pass "Storage classes found: $SC_COUNT"
    if kubectl get storageclass fast-ssd &> /dev/null; then
        log_pass "fast-ssd storage class exists"
    else
        log_warn "fast-ssd storage class not found (can use default)"
    fi
else
    log_fail "No storage classes found"
fi

# 7. Ingress controller
log_check "Checking ingress controller..."
if kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx &> /dev/null 2>&1; then
    log_pass "Nginx ingress controller found"
elif kubectl get pods -n kube-system -l app=traefik &> /dev/null 2>&1; then
    log_pass "Traefik ingress controller found"
else
    log_warn "No ingress controller found (install nginx-ingress or traefik)"
fi

# 8. Monitoring stack
log_check "Checking monitoring stack..."
if kubectl get namespace monitoring &> /dev/null; then
    log_pass "Monitoring namespace exists"
    if kubectl get prometheus -n monitoring &> /dev/null 2>&1; then
        log_pass "Prometheus found"
    else
        log_warn "Prometheus not found (install kube-prometheus-stack)"
    fi
else
    log_warn "Monitoring namespace not found"
fi

# 9. Namespace
log_check "Checking namespace $NAMESPACE..."
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    log_pass "Namespace $NAMESPACE exists"
else
    log_warn "Namespace $NAMESPACE does not exist (will be created)"
fi

# 10. Secrets
if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    log_check "Checking secrets in $NAMESPACE..."
    if kubectl get secret orchestration-secrets -n "$NAMESPACE" &> /dev/null; then
        log_pass "orchestration-secrets found"
    else
        log_warn "orchestration-secrets not found (must be created before deployment)"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [[ "$ERRORS" -eq 0 ]] && [[ "$WARNINGS" -eq 0 ]]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    exit 0
elif [[ "$ERRORS" -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  Validation passed with $WARNINGS warning(s)${NC}"
    echo "   You can proceed, but review warnings above"
    exit 0
else
    echo -e "${RED}❌ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo "   Fix errors before deploying"
    exit 1
fi
