# Phase 3.1 - Advanced Production Features

**Version:** 1.0.0
**Date:** 2025-10-20
**Status:** Design Complete, Implementation In Progress

---

## 📋 Overview

Phase 3.1 extends the basic production deployment (Phase 3) with enterprise-grade features:

1. **Service Mesh (Istio)** - Advanced traffic management, security, observability
2. **GitOps (ArgoCD)** - Declarative, automated deployment management
3. **Disaster Recovery** - Multi-region, backup/restore, failover
4. **Distributed Tracing (Jaeger)** - End-to-end request tracing
5. **Advanced Monitoring** - Custom dashboards, SLO/SLI tracking
6. **Cost Optimization** - Resource optimization, auto-scaling tuning

---

## 🕸️ 1. Service Mesh Architecture (Istio)

### Why Service Mesh?

**Problems Solved:**
- Complex microservice communication
- Service-to-service security
- Traffic management and routing
- Observability across services
- Resilience (retries, circuit breaking, timeouts)

**Istio Benefits:**
- Zero-trust security (mTLS between services)
- Advanced traffic control (canary, A/B testing)
- Distributed tracing integration
- Automatic metrics collection
- Policy enforcement

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Istio Control Plane                      │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Istiod  │  │  Pilot    │  │ Citadel  │  │  Galley  │  │
│  └──────────┘  └───────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                       Data Plane                             │
│                                                              │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────┐│
│  │ Orchestration │     │  BIA Service  │     │   Risk    ││
│  │   Service     │     │               │     │  Service  ││
│  │ ┌───────────┐ │     │ ┌───────────┐ │     │┌─────────┐││
│  │ │    App    │ │     │ │    App    │ │     ││   App   │││
│  │ └───────────┘ │     │ └───────────┘ │     │└─────────┘││
│  │ ┌───────────┐ │     │ ┌───────────┐ │     │┌─────────┐││
│  │ │Envoy Proxy│ │────▶│ │Envoy Proxy│ │────▶││Envoy Prx│││
│  │ └───────────┘ │mTLS │ └───────────┘ │mTLS │└─────────┘││
│  └───────────────┘     └───────────────┘     └───────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step 1: Install Istio

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install Istio with demo profile (for testing)
istioctl install --set profile=demo -y

# Or production profile
istioctl install --set profile=production \
  --set values.gateways.istio-ingressgateway.type=LoadBalancer \
  --set values.pilot.resources.requests.memory=1Gi \
  --set values.pilot.resources.requests.cpu=500m

# Verify installation
kubectl get pods -n istio-system
```

#### Step 2: Enable Sidecar Injection

```bash
# Label namespace for auto-injection
kubectl label namespace bcm-platform istio-injection=enabled

# Restart pods to inject sidecars
kubectl rollout restart deployment -n bcm-platform
```

#### Step 3: Deploy Istio Resources

**VirtualService for Traffic Routing:**

```yaml
# infrastructure/kubernetes/istio/virtual-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: orchestration-vs
  namespace: bcm-platform
spec:
  hosts:
  - orchestration.bcm-platform.io
  gateways:
  - orchestration-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1
    route:
    - destination:
        host: orchestration-service
        port:
          number: 8002
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure
    timeout: 10s
  - match:
    - uri:
        prefix: /health
    route:
    - destination:
        host: orchestration-service
        port:
          number: 8002
```

**DestinationRule for Load Balancing:**

```yaml
# infrastructure/kubernetes/istio/destination-rule.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: orchestration-dr
  namespace: bcm-platform
spec:
  host: orchestration-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_REQUEST
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

**Gateway for Ingress:**

```yaml
# infrastructure/kubernetes/istio/gateway.yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: orchestration-gateway
  namespace: bcm-platform
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: orchestration-tls
    hosts:
    - orchestration.bcm-platform.io
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - orchestration.bcm-platform.io
    tls:
      httpsRedirect: true
```

#### Step 4: Enable mTLS

```yaml
# infrastructure/kubernetes/istio/peer-authentication.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: bcm-platform
spec:
  mtls:
    mode: STRICT  # Enforce mTLS for all services
```

#### Step 5: Traffic Management - Canary Deployment

```yaml
# infrastructure/kubernetes/istio/canary-virtual-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: orchestration-canary
  namespace: bcm-platform
spec:
  hosts:
  - orchestration-service
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: orchestration-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: orchestration-service
        subset: v1
      weight: 90  # 90% to stable version
    - destination:
        host: orchestration-service
        subset: v2
      weight: 10  # 10% to canary
```

### Observability with Istio

```bash
# Install Kiali (service mesh observability)
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/kiali.yaml

# Install Jaeger (tracing)
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/jaeger.yaml

# Install Prometheus (metrics)
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/prometheus.yaml

# Install Grafana (dashboards)
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/grafana.yaml

# Access Kiali dashboard
istioctl dashboard kiali
```

---

## 🔄 2. GitOps with ArgoCD

### Why GitOps?

**Benefits:**
- Declarative deployment (Git as single source of truth)
- Automated sync between Git and cluster
- Easy rollback (Git revert)
- Audit trail (Git history)
- Multi-cluster management
- Self-healing deployments

### Architecture

```
┌──────────────┐
│  Git Repo    │ ← Developer pushes changes
│  (manifests) │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   ArgoCD     │ ← Monitors Git, syncs to cluster
│  Controller  │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  Kubernetes  │ ← Desired state applied
│   Cluster    │
└──────────────┘
```

### Implementation

#### Step 1: Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access at https://localhost:8080
# Username: admin
# Password: <from above>
```

#### Step 2: Configure Git Repository

```yaml
# infrastructure/kubernetes/argocd/repository.yaml
apiVersion: v1
kind: Secret
metadata:
  name: bcm-platform-repo
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: https://github.com/SEH-foundation/AI-Platform-ISO.git
  password: <GITHUB_TOKEN>
  username: not-used
```

#### Step 3: Create ArgoCD Application

```yaml
# infrastructure/kubernetes/argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: bcm-platform
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/SEH-foundation/AI-Platform-ISO.git
    targetRevision: main
    path: infrastructure/kubernetes/deployments

  destination:
    server: https://kubernetes.default.svc
    namespace: bcm-platform

  syncPolicy:
    automated:
      prune: true      # Delete resources not in Git
      selfHeal: true   # Auto-sync if manual changes detected
      allowEmpty: false

    syncOptions:
    - CreateNamespace=true

    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas  # Ignore HPA-managed replicas
```

#### Step 4: Deploy Application

```bash
# Apply ArgoCD application
kubectl apply -f infrastructure/kubernetes/argocd/application.yaml

# Check sync status
argocd app get bcm-platform

# Manual sync (if not automated)
argocd app sync bcm-platform

# View sync history
argocd app history bcm-platform
```

### GitOps Workflow

```
1. Developer commits changes to Git
   ↓
2. ArgoCD detects changes (every 3 minutes)
   ↓
3. ArgoCD compares Git state vs Cluster state
   ↓
4. If different, ArgoCD syncs (applies changes)
   ↓
5. Kubernetes applies new manifests
   ↓
6. ArgoCD reports sync status
```

### Multi-Environment Strategy

```yaml
# environments/staging/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: bcm-platform-staging

replicas:
- name: orchestration-service
  count: 2

images:
- name: orchestration
  newTag: staging-latest

configMapGenerator:
- name: environment-config
  literals:
  - ENVIRONMENT=staging
  - LOG_LEVEL=DEBUG
```

```yaml
# environments/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: bcm-platform

replicas:
- name: orchestration-service
  count: 3

images:
- name: orchestration
  newTag: v2.0.0

configMapGenerator:
- name: environment-config
  literals:
  - ENVIRONMENT=production
  - LOG_LEVEL=INFO
```

---

## 🌍 3. Disaster Recovery

### DR Strategy

**RTO (Recovery Time Objective):** 1 hour
**RPO (Recovery Point Objective):** 15 minutes

### Multi-Region Architecture

```
┌─────────────────────────────────────────────┐
│           Global Load Balancer              │
│         (DNS-based or Anycast)              │
└──────────┬──────────────────┬───────────────┘
           │                  │
     ┌─────▼─────┐      ┌────▼──────┐
     │  Region 1 │      │  Region 2 │
     │  PRIMARY  │◀────▶│  STANDBY  │
     └───────────┘ Sync └───────────┘

     ┌───────────┐      ┌───────────┐
     │ K8s       │      │ K8s       │
     │ Cluster   │      │ Cluster   │
     └───────────┘      └───────────┘

     ┌───────────┐      ┌───────────┐
     │ PostgreSQL│──────│PostgreSQL │
     │ Primary   │Replic│ Replica   │
     └───────────┘ation └───────────┘
```

### Implementation

#### Database Replication

```yaml
# PostgreSQL streaming replication
# Primary database
postgresql:
  primary:
    configuration:
      wal_level: replica
      max_wal_senders: 10
      wal_keep_size: 256MB
      synchronous_commit: on
      synchronous_standby_names: '*'

# Standby database
postgresql:
  standby:
    configuration:
      hot_standby: on
      primary_conninfo: 'host=primary-db.region1 port=5432 user=replicator password=xxx'
      restore_command: 'cp /archive/%f %p'
```

#### Backup Strategy

```yaml
# infrastructure/kubernetes/backup/velero-backup.yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: bcm-platform-backup
  namespace: velero
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  template:
    includedNamespaces:
    - bcm-platform
    includedResources:
    - '*'
    excludedResources:
    - events
    - events.events.k8s.io
    storageLocation: default
    volumeSnapshotLocations:
    - default
    ttl: 720h  # 30 days retention
```

#### Velero Installation

```bash
# Install Velero CLI
wget https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/velero-v1.12.0-linux-amd64.tar.gz
tar -xvf velero-v1.12.0-linux-amd64.tar.gz
sudo mv velero-v1.12.0-linux-amd64/velero /usr/local/bin/

# Install Velero server (AWS example)
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket bcm-platform-backups \
  --backup-location-config region=us-east-1 \
  --snapshot-location-config region=us-east-1 \
  --secret-file ./credentials-velero

# Create backup
velero backup create bcm-platform-manual --include-namespaces bcm-platform

# List backups
velero backup get

# Restore from backup
velero restore create --from-backup bcm-platform-manual
```

#### Failover Procedure

```bash
#!/bin/bash
# failover.sh - Failover to DR site

# 1. Promote standby database to primary
kubectl exec -n bcm-platform postgres-standby-0 -- \
  pg_ctl promote -D /var/lib/postgresql/data

# 2. Update DNS to point to DR site
# (Use your DNS provider's CLI or API)

# 3. Scale up DR cluster
kubectl scale deployment --all --replicas=3 -n bcm-platform

# 4. Verify health
kubectl get pods -n bcm-platform
./infrastructure/kubernetes/scripts/smoke-tests.sh

# 5. Monitor
kubectl logs -f -n bcm-platform -l app=orchestration
```

---

## 🔍 4. Distributed Tracing (Jaeger)

### Architecture

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│   Client   │────▶│Orchestration│────▶│BIA Service │
└────────────┘     └─────┬──────┘     └─────┬──────┘
                         │                   │
                         ▼                   ▼
                    ┌─────────────────────────────┐
                    │      Jaeger Collector       │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────┐
                    │     Jaeger Storage          │
                    │  (Elasticsearch/Cassandra)  │
                    └────────────┬────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────┐
                    │       Jaeger Query UI       │
                    └─────────────────────────────┘
```

### Implementation

#### Step 1: Install Jaeger Operator

```bash
# Install Jaeger Operator
kubectl create namespace observability
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability
```

#### Step 2: Deploy Jaeger Instance

```yaml
# infrastructure/kubernetes/tracing/jaeger.yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: bcm-platform-jaeger
  namespace: observability
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
        index-prefix: jaeger
  ingress:
    enabled: true
    hosts:
    - jaeger.bcm-platform.io
  ui:
    options:
      dependencies:
        menuEnabled: true
      tracking:
        gaID: UA-000000-2
```

#### Step 3: Instrument Applications

**Python (OpenTelemetry):**

```python
# Add to orchestration service
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Configure tracer
resource = Resource(attributes={
    "service.name": "orchestration-service",
    "service.version": "2.0.0"
})

provider = TracerProvider(resource=resource)
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent.observability",
    agent_port=6831,
)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Manual tracing
tracer = trace.get_tracer(__name__)

@app.post("/api/v1/sagas/execute")
async def execute_saga(saga_request: SagaRequest):
    with tracer.start_as_current_span("execute_saga") as span:
        span.set_attribute("saga.name", saga_request.saga_name)
        span.set_attribute("saga.context", str(saga_request.context))

        result = await saga_orchestrator.execute(saga_request)

        span.set_attribute("saga.result", result.status)
        return result
```

#### Step 4: View Traces

```bash
# Access Jaeger UI
kubectl port-forward -n observability svc/bcm-platform-jaeger-query 16686:16686

# Open http://localhost:16686
```

---

## 📊 5. Advanced Monitoring & SLO/SLI

### Service Level Objectives (SLOs)

**Orchestration Service:**
- **Availability:** 99.9% (43 minutes downtime/month)
- **Latency:** 95% of requests < 100ms
- **Error Rate:** < 0.1%

**Intelligent Router:**
- **Routing Latency:** 95% < 20ms
- **SLA Compliance:** > 95%

### SLO Monitoring

```yaml
# infrastructure/kubernetes/monitoring/slo-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: slo-rules
  namespace: bcm-platform
spec:
  groups:
  - name: slo
    interval: 30s
    rules:
    # Availability SLO
    - record: slo:availability:ratio
      expr: |
        sum(rate(http_requests_total{job="orchestration",code!~"5.."}[5m]))
        /
        sum(rate(http_requests_total{job="orchestration"}[5m]))

    # Latency SLO
    - record: slo:latency:p95
      expr: |
        histogram_quantile(0.95,
          sum(rate(http_request_duration_seconds_bucket{job="orchestration"}[5m])) by (le)
        )

    # Error budget (30 day window)
    - record: slo:error_budget:30d
      expr: |
        1 - (
          (1 - slo:availability:ratio)
          /
          (1 - 0.999)  # Target 99.9%
        )

    # Alert on error budget burn
    - alert: ErrorBudgetBurn
      expr: slo:error_budget:30d < 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Error budget burning too fast"
        description: "Only {{ $value }}% of error budget remaining"
```

### Custom Dashboards

See `infrastructure/kubernetes/monitoring/grafana-slo-dashboard.json`

---

## 💰 6. Cost Optimization

### Resource Right-Sizing

```bash
# Analyze resource usage
kubectl top pods -n bcm-platform --containers

# Identify over-provisioned pods
kubectl get pods -n bcm-platform -o json | \
  jq '.items[] | {
    name: .metadata.name,
    cpu_request: .spec.containers[0].resources.requests.cpu,
    cpu_limit: .spec.containers[0].resources.limits.cpu,
    mem_request: .spec.containers[0].resources.requests.memory,
    mem_limit: .spec.containers[0].resources.limits.memory
  }'
```

### Vertical Pod Autoscaler

```yaml
# infrastructure/kubernetes/autoscaling/vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: orchestration-vpa
  namespace: bcm-platform
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orchestration-service
  updatePolicy:
    updateMode: "Auto"  # or "Recreate" or "Initial"
  resourcePolicy:
    containerPolicies:
    - containerName: orchestration
      minAllowed:
        cpu: 250m
        memory: 256Mi
      maxAllowed:
        cpu: 2000m
        memory: 2Gi
```

### Cluster Autoscaler

```bash
# Enable cluster autoscaler (GKE example)
gcloud container clusters update bcm-platform-cluster \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --zone us-central1-a
```

### Cost Monitoring

```yaml
# infrastructure/kubernetes/monitoring/cost-dashboard.yaml
# Use kubecost or similar tool

# Install kubecost
helm install kubecost kubecost/cost-analyzer \
  --namespace kubecost \
  --create-namespace \
  --set prometheus.server.global.external_labels.cluster_id=bcm-platform
```

---

## 🚀 Deployment Roadmap

### Phase 3.1.1: Service Mesh (Week 1-2)
- [x] Architecture design
- [ ] Install Istio
- [ ] Configure VirtualServices & DestinationRules
- [ ] Enable mTLS
- [ ] Deploy Kiali for observability
- [ ] Test canary deployments

### Phase 3.1.2: GitOps (Week 3)
- [x] Architecture design
- [ ] Install ArgoCD
- [ ] Configure Git repository
- [ ] Create ArgoCD applications
- [ ] Setup multi-environment (staging/prod)
- [ ] Test automated sync

### Phase 3.1.3: Disaster Recovery (Week 4)
- [x] Architecture design
- [ ] Setup multi-region clusters
- [ ] Configure database replication
- [ ] Install Velero for backups
- [ ] Create backup schedules
- [ ] Test failover procedure

### Phase 3.1.4: Distributed Tracing (Week 5)
- [x] Architecture design
- [ ] Install Jaeger
- [ ] Instrument applications
- [ ] Configure trace sampling
- [ ] Create trace-based dashboards
- [ ] Test end-to-end tracing

### Phase 3.1.5: Advanced Monitoring (Week 6)
- [x] Architecture design
- [ ] Define SLOs/SLIs
- [ ] Create SLO monitoring rules
- [ ] Deploy custom Grafana dashboards
- [ ] Setup alerting based on SLOs
- [ ] Test alert workflows

### Phase 3.1.6: Cost Optimization (Week 7)
- [x] Architecture design
- [ ] Analyze current resource usage
- [ ] Deploy VPA
- [ ] Configure cluster autoscaler
- [ ] Install kubecost
- [ ] Implement cost alerts

---

## 📚 References

- **Istio:** https://istio.io/latest/docs/
- **ArgoCD:** https://argo-cd.readthedocs.io/
- **Velero:** https://velero.io/docs/
- **Jaeger:** https://www.jaegertracing.io/docs/
- **OpenTelemetry:** https://opentelemetry.io/docs/
- **SLO/SLI:** https://sre.google/sre-book/service-level-objectives/

---

**Created:** 2025-10-20
**Author:** Claude Code
**Version:** 1.0.0
