# Production Deployment Checklist

**Version:** 1.0.0
**Date:** 2025-10-20
**Status:** Production Ready

---

## 📋 Pre-Deployment Checklist

### Infrastructure Prerequisites

- [ ] **Kubernetes Cluster Ready**
  - [ ] Kubernetes v1.28+
  - [ ] 3+ nodes (production)
  - [ ] Node resources: 4 CPU, 16GB RAM, 50GB SSD per node
  - [ ] kubectl configured and connected
  - [ ] Cluster admin access verified

- [ ] **Storage Classes**
  - [ ] `fast-ssd` storage class available
  - [ ] `standard` storage class available
  - [ ] Dynamic provisioning enabled

- [ ] **Networking**
  - [ ] Ingress controller installed (nginx/traefik)
  - [ ] TLS certificates ready (Let's Encrypt or custom)
  - [ ] DNS records configured
  - [ ] Firewall rules configured

- [ ] **External Services**
  - [ ] PostgreSQL database ready (or helm chart ready)
  - [ ] Redis instance ready (or helm chart ready)
  - [ ] RabbitMQ ready (optional, for EventBus)
  - [ ] Container registry access (GHCR/Docker Hub)

### Security Prerequisites

- [ ] **Secrets Prepared**
  - [ ] Database credentials
  - [ ] Redis credentials
  - [ ] Anthropic API key
  - [ ] JWT secret key
  - [ ] TLS certificates
  - [ ] Docker registry credentials (if private)

- [ ] **Security Tools**
  - [ ] Sealed Secrets OR External Secrets Operator installed
  - [ ] RBAC policies reviewed
  - [ ] Network policies reviewed
  - [ ] Pod Security Standards configured

### Monitoring Prerequisites

- [ ] **Monitoring Stack**
  - [ ] Prometheus Operator installed
  - [ ] Grafana installed
  - [ ] AlertManager configured
  - [ ] Log aggregation ready (optional: Loki/ELK)

---

## 🚀 Deployment Steps

### Step 1: Validate Prerequisites

```bash
# Run pre-deployment validation
./infrastructure/kubernetes/scripts/validate-prerequisites.sh
```

**Expected output:**
- ✅ Cluster connectivity
- ✅ Required namespaces
- ✅ Storage classes
- ✅ Ingress controller
- ✅ Monitoring stack

### Step 2: Create Namespaces

```bash
# Create namespaces
kubectl create namespace bcm-platform --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Label namespaces
kubectl label namespace bcm-platform environment=production
kubectl label namespace bcm-platform managed-by=platform-integration
```

**Validation:**
```bash
kubectl get namespace bcm-platform -o yaml
```

### Step 3: Deploy Infrastructure Dependencies

#### Option A: External Database/Redis (Recommended for Production)

```bash
# Update secrets with external endpoints
kubectl create secret generic orchestration-secrets \
  --from-literal=database-url="postgresql+asyncpg://USER:PASSWORD@external-db.example.com:5432/bcm_platform" \
  --from-literal=redis-url="redis://external-redis.example.com:6379/0" \
  --from-literal=anthropic-api-key="YOUR_API_KEY" \
  --from-literal=jwt-secret-key="YOUR_JWT_SECRET" \
  --namespace=bcm-platform
```

#### Option B: Deploy with Helm (Testing/Staging)

```bash
# Deploy PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace bcm-platform \
  --set auth.username=bcm_user \
  --set auth.password=CHANGE_ME_PRODUCTION_PASSWORD \
  --set auth.database=bcm_platform \
  --set primary.persistence.size=50Gi \
  --set primary.persistence.storageClass=fast-ssd \
  --set metrics.enabled=true

# Deploy Redis
helm install redis bitnami/redis \
  --namespace bcm-platform \
  --set auth.enabled=true \
  --set auth.password=CHANGE_ME_REDIS_PASSWORD \
  --set master.persistence.size=10Gi \
  --set metrics.enabled=true

# Wait for databases
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n bcm-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n bcm-platform --timeout=300s
```

**Validation:**
```bash
kubectl get pods -n bcm-platform | grep -E "postgres|redis"
```

### Step 4: Deploy Secrets (Secure Method)

#### Using Sealed Secrets (Recommended)

```bash
# Install sealed-secrets controller
helm install sealed-secrets sealed-secrets/sealed-secrets \
  --namespace kube-system

# Create sealed secret
cat <<EOF | kubeseal -o yaml > orchestration-secrets-sealed.yaml
apiVersion: v1
kind: Secret
metadata:
  name: orchestration-secrets
  namespace: bcm-platform
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB"
  redis-url: "redis://HOST:6379/0"
  anthropic-api-key: "YOUR_KEY"
  jwt-secret-key: "YOUR_SECRET"
EOF

# Apply sealed secret
kubectl apply -f orchestration-secrets-sealed.yaml
```

**Validation:**
```bash
kubectl get secret orchestration-secrets -n bcm-platform
```

### Step 5: Deploy ConfigMaps

```bash
# Deploy all configmaps
kubectl apply -f infrastructure/kubernetes/configmaps/ --namespace=bcm-platform

# Verify
kubectl get configmap -n bcm-platform
```

**Expected ConfigMaps:**
- orchestration-config
- eventbus-config (if exists)
- monitoring-config (if exists)

### Step 6: Deploy Orchestration Layer

```bash
# Deploy orchestration
kubectl apply -f infrastructure/kubernetes/deployments/orchestration-deployment.yaml \
  --namespace=bcm-platform

# Watch deployment
kubectl rollout status deployment/orchestration-service -n bcm-platform
```

**Validation:**
```bash
# Check pods
kubectl get pods -n bcm-platform -l app=orchestration

# Check logs
kubectl logs -n bcm-platform -l app=orchestration --tail=50

# Check health endpoint
kubectl port-forward -n bcm-platform svc/orchestration-service 8002:8002
curl http://localhost:8002/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "platform_integration": {
    "enabled": true,
    "components": {
      "eventbus": "intelligent",
      "saga_engine": "enabled",
      "cqrs": "enabled"
    }
  }
}
```

### Step 7: Deploy BCM Services

```bash
# Deploy all BCM services
kubectl apply -f infrastructure/kubernetes/deployments/bcm-services/ \
  --namespace=bcm-platform

# Watch rollout
kubectl rollout status deployment -l component=bcm-service -n bcm-platform
```

**Validation:**
```bash
# Check all services running
kubectl get pods -n bcm-platform -l component=bcm-service

# Expected: 11 services, 2 replicas each = 22 pods total
kubectl get pods -n bcm-platform -l component=bcm-service --no-headers | wc -l
```

### Step 8: Deploy Ingress

```bash
# Deploy ingress
kubectl apply -f infrastructure/kubernetes/ingress/ --namespace=bcm-platform

# Check ingress
kubectl get ingress -n bcm-platform
kubectl describe ingress orchestration-ingress -n bcm-platform
```

**Validation:**
```bash
# Get ingress IP/hostname
kubectl get ingress orchestration-ingress -n bcm-platform \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Test external access
curl -k https://orchestration.bcm-platform.io/health
```

### Step 9: Deploy Monitoring

```bash
# Deploy ServiceMonitors
kubectl apply -f infrastructure/kubernetes/monitoring/servicemonitors.yaml

# Deploy Grafana dashboards
kubectl create configmap grafana-dashboard-platform-integration \
  --from-file=infrastructure/kubernetes/monitoring/grafana-platform-integration-dashboard.json \
  --namespace=monitoring

kubectl label configmap grafana-dashboard-platform-integration \
  grafana_dashboard=1 \
  --namespace=monitoring
```

**Validation:**
```bash
# Check ServiceMonitors
kubectl get servicemonitor -n bcm-platform

# Access Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80

# Login: admin / <get password>
kubectl get secret --namespace monitoring kube-prometheus-stack-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode
```

### Step 10: Run Smoke Tests

```bash
# Run automated smoke tests
./infrastructure/kubernetes/scripts/smoke-tests.sh

# Manual smoke tests
kubectl exec -it deployment/orchestration-service -n bcm-platform -- \
  python -m pytest test_platform_integration.py -v
```

**Expected Results:**
- ✅ All pods running
- ✅ All services healthy
- ✅ Ingress accessible
- ✅ Database connectivity
- ✅ Redis connectivity
- ✅ EventBus operational
- ✅ Saga Engine operational
- ✅ Metrics being collected

---

## ✅ Post-Deployment Validation

### Functional Tests

```bash
# 1. Test orchestration health
curl https://orchestration.bcm-platform.io/health

# 2. Test system status
curl https://orchestration.bcm-platform.io/api/v1/system/status

# 3. Test EventBus
curl -X POST https://orchestration.bcm-platform.io/api/v1/events/publish \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test.event", "data": {"test": true}}'

# 4. Test Saga execution
curl -X POST https://orchestration.bcm-platform.io/api/v1/sagas/execute \
  -H "Content-Type: application/json" \
  -d '{"saga_name": "create_bcm_program", "context": {}}'
```

### Performance Tests

```bash
# Load test (optional)
kubectl run load-test --rm -it --image=busybox --restart=Never -- \
  wget -O- http://orchestration-service.bcm-platform.svc:8002/health

# Metrics check
curl http://orchestration-service.bcm-platform.svc:8002/metrics | grep -E "intelligent_router|saga_"
```

### Monitoring Validation

- [ ] **Grafana Dashboards**
  - [ ] Platform Integration dashboard visible
  - [ ] All panels showing data
  - [ ] No "No Data" errors

- [ ] **Prometheus Alerts**
  - [ ] AlertManager receiving alerts
  - [ ] Alert rules loaded
  - [ ] Test alert fires correctly

- [ ] **Metrics Collection**
  - [ ] `intelligent_router_routing_time_ms` < 20ms
  - [ ] `intelligent_router_sla_compliance_rate` > 0.95
  - [ ] `saga_success_rate` > 0.95
  - [ ] `self_aware_health_score` > 0.7

---

## 🔥 Rollback Procedures

### Emergency Rollback

```bash
# Rollback orchestration
kubectl rollout undo deployment/orchestration-service -n bcm-platform

# Rollback all BCM services
kubectl rollout undo deployment -l component=bcm-service -n bcm-platform

# Check status
kubectl rollout status deployment/orchestration-service -n bcm-platform
```

### Partial Rollback (Single Service)

```bash
# Rollback specific service
kubectl rollout undo deployment/bia-service -n bcm-platform

# Rollback to specific revision
kubectl rollout history deployment/bia-service -n bcm-platform
kubectl rollout undo deployment/bia-service --to-revision=2 -n bcm-platform
```

### Complete Uninstall

```bash
# Delete all resources
kubectl delete namespace bcm-platform --wait=true

# Or selective delete
kubectl delete -f infrastructure/kubernetes/deployments/ -n bcm-platform
kubectl delete -f infrastructure/kubernetes/ingress/ -n bcm-platform
kubectl delete -f infrastructure/kubernetes/configmaps/ -n bcm-platform
```

---

## 📊 Success Criteria

### Deployment Success

- [x] All pods in `Running` state
- [x] 0 pods in `CrashLoopBackOff` or `Error`
- [x] All deployments at desired replica count
- [x] All services have endpoints
- [x] Ingress shows external IP/hostname
- [x] Health checks pass for all services

### Performance Criteria

- [x] Orchestration response time < 100ms (p95)
- [x] Intelligent Router latency < 20ms (p95)
- [x] Saga execution success rate > 95%
- [x] Pod CPU usage < 70%
- [x] Pod memory usage < 80%

### Monitoring Criteria

- [x] All ServiceMonitors active
- [x] Prometheus scraping metrics (0 errors)
- [x] Grafana dashboards populated
- [x] Alert rules active

---

## 🔒 Security Checklist

- [ ] All secrets encrypted (Sealed Secrets / External Secrets)
- [ ] No plain-text secrets in version control
- [ ] Network policies applied
- [ ] RBAC least-privilege enforced
- [ ] Pod Security Standards enforced
- [ ] TLS enabled for all ingress
- [ ] Container images signed (optional)
- [ ] Vulnerability scans passed

---

## 📝 Documentation Updates

- [ ] Update deployment timestamp in docs
- [ ] Document any deviations from standard procedure
- [ ] Update runbook with production URLs
- [ ] Record any issues encountered
- [ ] Update monitoring dashboard links

---

## 🎯 Next Steps After Deployment

1. **Monitor for 24 hours**
   - Watch Grafana dashboards
   - Check logs for errors
   - Monitor resource usage

2. **Run integration tests**
   - Test all BCM workflows
   - Verify cross-service communication
   - Test saga orchestration

3. **Performance tuning**
   - Adjust HPA settings if needed
   - Optimize resource limits
   - Fine-tune caching

4. **Documentation**
   - Document production configuration
   - Create runbook for operations
   - Train team on monitoring

5. **Backup validation**
   - Test database backup/restore
   - Verify disaster recovery procedures

---

**Deployment Completed:** _______________
**Deployed By:** _______________
**Verified By:** _______________
**Sign-off:** _______________

---

**Created:** 2025-10-20
**Author:** Claude Code
**Version:** 1.0.0
