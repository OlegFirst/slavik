#!/usr/bin/env bash

################################################################################
# Smoke Tests for Production Deployment
#
# Runs comprehensive smoke tests after deployment
#
# Usage: ./smoke-tests.sh [--namespace <namespace>]
################################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="${1:-bcm-platform}"
TESTS_PASSED=0
TESTS_FAILED=0

log_test() { echo -e "${BLUE}[TEST]${NC} $*"; }
log_pass() { echo -e "${GREEN}[✓]${NC} $*"; ((TESTS_PASSED++)); }
log_fail() { echo -e "${RED}[✗]${NC} $*"; ((TESTS_FAILED++)); }

run_test() {
    local test_name="$1"
    local test_command="$2"

    log_test "$test_name"
    if eval "$test_command" &> /dev/null; then
        log_pass "$test_name"
        return 0
    else
        log_fail "$test_name"
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Smoke Tests - BCM Platform"
echo " Namespace: $NAMESPACE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: All pods running
log_test "Test 1: All pods in Running state"
FAILED_PODS=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null | wc -l | tr -d ' ')
if [[ "$FAILED_PODS" -eq 0 ]]; then
    RUNNING_PODS=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l | tr -d ' ')
    log_pass "All pods running ($RUNNING_PODS pods)"
else
    log_fail "$FAILED_PODS pod(s) not in Running state"
    kubectl get pods -n "$NAMESPACE" | grep -v "Running" || true
fi

# Test 2: No CrashLoopBackOff pods
log_test "Test 2: No CrashLoopBackOff pods"
CRASH_PODS=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers 2>/dev/null | grep "CrashLoopBackOff" | wc -l | tr -d ' ')
if [[ "$CRASH_PODS" -eq 0 ]]; then
    log_pass "No pods in CrashLoopBackOff"
else
    log_fail "$CRASH_PODS pod(s) in CrashLoopBackOff"
fi

# Test 3: Orchestration health endpoint
log_test "Test 3: Orchestration health endpoint"
ORCH_POD=$(kubectl get pod -n "$NAMESPACE" -l app=orchestration -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [[ -n "$ORCH_POD" ]]; then
    if kubectl exec -n "$NAMESPACE" "$ORCH_POD" -- curl -sf http://localhost:8002/health > /dev/null 2>&1; then
        log_pass "Orchestration health check passed"
    else
        log_fail "Orchestration health check failed"
    fi
else
    log_fail "Orchestration pod not found"
fi

# Test 4: Orchestration system status
log_test "Test 4: Orchestration system status endpoint"
if [[ -n "$ORCH_POD" ]]; then
    if kubectl exec -n "$NAMESPACE" "$ORCH_POD" -- curl -sf http://localhost:8002/api/v1/system/status > /dev/null 2>&1; then
        log_pass "System status endpoint accessible"
    else
        log_fail "System status endpoint failed"
    fi
else
    log_fail "Cannot test - orchestration pod not found"
fi

# Test 5: All services have endpoints
log_test "Test 5: All services have endpoints"
SERVICES_WITHOUT_ENDPOINTS=0
while IFS= read -r svc; do
    if ! kubectl get endpoints "$svc" -n "$NAMESPACE" -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null | grep -q "."; then
        ((SERVICES_WITHOUT_ENDPOINTS++))
    fi
done < <(kubectl get svc -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

if [[ "$SERVICES_WITHOUT_ENDPOINTS" -eq 0 ]]; then
    log_pass "All services have endpoints"
else
    log_fail "$SERVICES_WITHOUT_ENDPOINTS service(s) have no endpoints"
fi

# Test 6: Deployments at desired replica count
log_test "Test 6: Deployments at desired replica count"
DEPLOYMENTS_NOT_READY=0
while IFS= read -r deploy; do
    DESIRED=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
    READY=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
    if [[ "$DESIRED" != "$READY" ]]; then
        ((DEPLOYMENTS_NOT_READY++))
    fi
done < <(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

if [[ "$DEPLOYMENTS_NOT_READY" -eq 0 ]]; then
    log_pass "All deployments at desired replica count"
else
    log_fail "$DEPLOYMENTS_NOT_READY deployment(s) not at desired replica count"
fi

# Test 7: Ingress has external IP/hostname
log_test "Test 7: Ingress has external IP"
INGRESS_IP=$(kubectl get ingress orchestration-ingress -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
INGRESS_HOST=$(kubectl get ingress orchestration-ingress -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")

if [[ -n "$INGRESS_IP" ]] || [[ -n "$INGRESS_HOST" ]]; then
    log_pass "Ingress has external address: ${INGRESS_IP}${INGRESS_HOST}"
else
    log_fail "Ingress has no external address (may be pending)"
fi

# Test 8: HPA configured
log_test "Test 8: HPA configured"
HPA_COUNT=$(kubectl get hpa -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l | tr -d ' ')
if [[ "$HPA_COUNT" -gt 0 ]]; then
    log_pass "$HPA_COUNT HPA(s) configured"
else
    log_fail "No HPAs found"
fi

# Test 9: ServiceMonitors deployed
log_test "Test 9: ServiceMonitors deployed"
SM_COUNT=$(kubectl get servicemonitor -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l | tr -d ' ')
if [[ "$SM_COUNT" -gt 0 ]]; then
    log_pass "$SM_COUNT ServiceMonitor(s) deployed"
else
    log_fail "No ServiceMonitors found"
fi

# Test 10: Metrics endpoint responding
log_test "Test 10: Metrics endpoint responding"
if [[ -n "$ORCH_POD" ]]; then
    if kubectl exec -n "$NAMESPACE" "$ORCH_POD" -- curl -sf http://localhost:9090/metrics | head -1 > /dev/null 2>&1; then
        log_pass "Metrics endpoint responding"
    else
        log_fail "Metrics endpoint not responding"
    fi
else
    log_fail "Cannot test - orchestration pod not found"
fi

# Test 11: No recent pod restarts
log_test "Test 11: No excessive pod restarts"
HIGH_RESTART_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | awk '$4 > 5 {print $1}' | wc -l | tr -d ' ')
if [[ "$HIGH_RESTART_PODS" -eq 0 ]]; then
    log_pass "No pods with excessive restarts (>5)"
else
    log_fail "$HIGH_RESTART_PODS pod(s) have >5 restarts"
fi

# Test 12: Resource limits configured
log_test "Test 12: Resource limits configured"
PODS_WITHOUT_LIMITS=$(kubectl get pods -n "$NAMESPACE" -o json 2>/dev/null | \
    jq '[.items[].spec.containers[] | select(.resources.limits == null)] | length')
if [[ "$PODS_WITHOUT_LIMITS" -eq 0 ]]; then
    log_pass "All pods have resource limits"
else
    log_fail "$PODS_WITHOUT_LIMITS container(s) without resource limits"
fi

# Test 13: Liveness probes configured
log_test "Test 13: Liveness probes configured"
PODS_WITHOUT_LIVENESS=$(kubectl get pods -n "$NAMESPACE" -o json 2>/dev/null | \
    jq '[.items[].spec.containers[] | select(.livenessProbe == null)] | length')
if [[ "$PODS_WITHOUT_LIVENESS" -eq 0 ]]; then
    log_pass "All pods have liveness probes"
else
    log_fail "$PODS_WITHOUT_LIVENESS container(s) without liveness probes"
fi

# Test 14: Readiness probes configured
log_test "Test 14: Readiness probes configured"
PODS_WITHOUT_READINESS=$(kubectl get pods -n "$NAMESPACE" -o json 2>/dev/null | \
    jq '[.items[].spec.containers[] | select(.readinessProbe == null)] | length')
if [[ "$PODS_WITHOUT_READINESS" -eq 0 ]]; then
    log_pass "All pods have readiness probes"
else
    log_fail "$PODS_WITHOUT_READINESS container(s) without readiness probes"
fi

# Test 15: Platform Integration components
if [[ -n "$ORCH_POD" ]]; then
    log_test "Test 15: Platform Integration components active"

    # Try to get status and check for platform_integration key
    STATUS_OUTPUT=$(kubectl exec -n "$NAMESPACE" "$ORCH_POD" -- curl -sf http://localhost:8002/api/v1/system/status 2>/dev/null || echo "{}")

    if echo "$STATUS_OUTPUT" | grep -q "platform_integration"; then
        log_pass "Platform Integration components detected"

        # Check individual components if possible
        if echo "$STATUS_OUTPUT" | grep -q "eventbus"; then
            log_pass "  - EventBus active"
        fi
        if echo "$STATUS_OUTPUT" | grep -q "saga"; then
            log_pass "  - Saga Engine active"
        fi
        if echo "$STATUS_OUTPUT" | grep -q "cqrs"; then
            log_pass "  - CQRS active"
        fi
    else
        log_fail "Platform Integration components not detected in status"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
SUCCESS_RATE=$(( TESTS_PASSED * 100 / TOTAL_TESTS ))

echo "Tests passed: $TESTS_PASSED/$TOTAL_TESTS ($SUCCESS_RATE%)"
echo ""

if [[ "$TESTS_FAILED" -eq 0 ]]; then
    echo -e "${GREEN}✅ All smoke tests passed!${NC}"
    echo ""
    echo "Deployment is healthy and ready for use."
    exit 0
else
    echo -e "${RED}❌ $TESTS_FAILED test(s) failed${NC}"
    echo ""
    echo "Please review the failed tests above and troubleshoot."
    echo ""
    echo "Troubleshooting commands:"
    echo "  kubectl get pods -n $NAMESPACE"
    echo "  kubectl logs -n $NAMESPACE -l app=orchestration"
    echo "  kubectl describe pod <pod-name> -n $NAMESPACE"
    exit 1
fi
