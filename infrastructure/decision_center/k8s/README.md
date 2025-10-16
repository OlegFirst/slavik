# Decision Center - Kubernetes Deployment

Kubernetes manifests for deploying Decision Center in production.

## Prerequisites

- Kubernetes cluster (v1.24+)
- `kubectl` configured
- Ingress controller (e.g., nginx-ingress)
- Metrics Server (for HPA)
- Persistent Volume provisioner

## Quick Start

### 1. Update Secrets

**IMPORTANT:** Before deployment, update secrets in `secret.yaml`:

```bash
# Edit secret.yaml and replace:
# - ANTHROPIC_API_KEY with your actual API key
# - POSTGRES_PASSWORD with a strong password
# - GRAFANA_PASSWORD with a secure password

vim k8s/secret.yaml
```

For production, use external secret management:
- Kubernetes Secrets encryption at rest
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

### 2. Deploy

```bash
# Apply manifests in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Or apply all at once
kubectl apply -f k8s/
```

### 3. Verify Deployment

```bash
# Check namespace
kubectl get all -n decision-center

# Check pods
kubectl get pods -n decision-center

# Check services
kubectl get svc -n decision-center

# Check logs
kubectl logs -n decision-center -l app=decision-center --tail=100
```

### 4. Access Services

**Internal (ClusterIP):**
```bash
# Port-forward to access Decision Center API
kubectl port-forward -n decision-center svc/decision-center-service 8080:8080

# Test
curl http://localhost:8080/health
```

**External (Ingress):**
```bash
# Update Ingress host in service.yaml
# Configure DNS: decision-center.example.com → Ingress IP

# Access
curl http://decision-center.example.com/health
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Ingress Controller              │
│    (decision-center.example.com)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Decision Center Service (ClusterIP) │
│              Port 8080                   │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌─────▼──────┐
│  Decision   │  │  Decision  │  ... (3-10 replicas via HPA)
│  Center     │  │  Center    │
│  Pod        │  │  Pod       │
└──────┬──────┘  └─────┬──────┘
       │                │
       └────────┬───────┘
                │
       ┌────────┴────────┐
       │                 │
┌──────▼──────┐  ┌──────▼──────┐
│  PostgreSQL │  │    Redis    │
│  StatefulSet│  │  StatefulSet│
└─────────────┘  └─────────────┘
```

## Components

### Decision Center
- **Deployment**: 3-10 replicas (auto-scaled via HPA)
- **Resources**: 256Mi-1Gi memory, 250m-1000m CPU
- **Probes**: Health checks on `/health`
- **Metrics**: Prometheus on `/metrics`

### PostgreSQL
- **StatefulSet**: 1 replica
- **Storage**: 10Gi PVC
- **Backup**: Configure pg_dump cronjob (see below)

### Redis
- **StatefulSet**: 1 replica
- **Storage**: 5Gi PVC
- **Persistence**: AOF enabled

### Horizontal Pod Autoscaler (HPA)
- **Min replicas**: 3
- **Max replicas**: 10
- **Target CPU**: 70%
- **Target Memory**: 80%

## Configuration

### Environment Variables

Edit `configmap.yaml`:
- `ENVIRONMENT`: production/staging/development
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR
- `AI_TIER*_ENABLED`: Enable/disable AI tiers
- `EVENTBUS_ENABLE_DEEP_AI`: Enable EventBus integration

### Policies

Edit policies in `deployment.yaml` → `policies-config` ConfigMap, or mount from external ConfigMap:

```yaml
volumes:
  - name: policies
    configMap:
      name: custom-policies-config
```

### Secrets

**Development:**
```bash
kubectl create secret generic decision-center-secrets \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-... \
  --from-literal=POSTGRES_PASSWORD=secure_password \
  -n decision-center
```

**Production:** Use external secret management (see `secret.yaml` for ExternalSecret example)

## Monitoring

### Prometheus

Deploy Prometheus (if not already):
```bash
# Using Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# Configure ServiceMonitor
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: decision-center
  namespace: decision-center
spec:
  selector:
    matchLabels:
      app: decision-center
  endpoints:
    - port: http
      path: /metrics
EOF
```

### Grafana

Import dashboard from `monitoring/grafana/dashboards/decision-center.json`

## Scaling

### Manual Scaling
```bash
# Scale deployment
kubectl scale deployment decision-center --replicas=5 -n decision-center

# Scale PostgreSQL (not recommended - use replication instead)
kubectl scale statefulset postgres --replicas=1 -n decision-center
```

### Auto-scaling (HPA)
Automatically scales based on CPU/Memory (configured in `hpa.yaml`)

### Database High Availability

For production, consider:
1. **PostgreSQL HA**: Patroni, Stolon, or managed service (RDS, Cloud SQL)
2. **Redis HA**: Redis Sentinel or Redis Cluster
3. **Backups**: Automated backups with retention

## Backup & Recovery

### PostgreSQL Backup

Create a CronJob for automated backups:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: decision-center
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:15-alpine
              command:
                - /bin/sh
                - -c
                - |
                  pg_dump -h postgres-service -U decision_center decision_center \
                    | gzip > /backup/backup-$(date +%Y%m%d-%H%M%S).sql.gz
              env:
                - name: PGPASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: decision-center-secrets
                      key: POSTGRES_PASSWORD
              volumeMounts:
                - name: backup-storage
                  mountPath: /backup
          restartPolicy: OnFailure
          volumes:
            - name: backup-storage
              persistentVolumeClaim:
                claimName: postgres-backup-pvc
```

### Redis Backup

Redis AOF is enabled. To create manual snapshot:
```bash
kubectl exec -n decision-center redis-0 -- redis-cli BGSAVE
```

## Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n decision-center
kubectl describe pod <pod-name> -n decision-center
```

### View Logs
```bash
# Decision Center logs
kubectl logs -n decision-center -l app=decision-center --tail=100 -f

# PostgreSQL logs
kubectl logs -n decision-center postgres-0 --tail=100

# Redis logs
kubectl logs -n decision-center redis-0 --tail=100
```

### Debug Container
```bash
kubectl exec -it -n decision-center <pod-name> -- /bin/sh
```

### Health Check
```bash
# Port-forward
kubectl port-forward -n decision-center svc/decision-center-service 8080:8080

# Test
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/ai/status
```

### Common Issues

**Pods not starting:**
- Check secrets are created: `kubectl get secrets -n decision-center`
- Check ConfigMaps: `kubectl get cm -n decision-center`
- Check PVC binding: `kubectl get pvc -n decision-center`

**Database connection errors:**
- Verify PostgreSQL is running: `kubectl get pods -n decision-center | grep postgres`
- Check PostgreSQL logs: `kubectl logs -n decision-center postgres-0`
- Test connection: `kubectl exec -it postgres-0 -n decision-center -- psql -U decision_center`

**AI integration errors:**
- Verify ANTHROPIC_API_KEY is set correctly
- Check Decision Center logs for API errors
- Test AI status: `curl http://localhost:8080/api/v1/ai/status`

## Security Considerations

1. **Secrets Management**
   - Use external secret management (Vault, AWS Secrets Manager)
   - Enable Kubernetes secrets encryption at rest
   - Rotate secrets regularly

2. **Network Policies**
   - Restrict traffic between pods
   - Allow only necessary ingress/egress

3. **RBAC**
   - Use least privilege for ServiceAccounts
   - Implement Pod Security Standards

4. **TLS/SSL**
   - Enable TLS for Ingress (cert-manager + Let's Encrypt)
   - Use TLS for database connections

5. **Image Security**
   - Use private registry
   - Scan images for vulnerabilities
   - Use specific image tags (not `latest`)

## Production Checklist

- [ ] Update all secrets in `secret.yaml`
- [ ] Configure external secret management
- [ ] Set up database backups
- [ ] Configure monitoring and alerting
- [ ] Enable TLS/SSL for Ingress
- [ ] Implement Network Policies
- [ ] Configure log aggregation
- [ ] Test disaster recovery procedures
- [ ] Document runbooks for operators
- [ ] Load test the system
- [ ] Set up CI/CD pipeline

## Resources

- [Decision Center Documentation](../README.md)
- [API Documentation](../INTEGRATION_GUIDE.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Operator](https://prometheus-operator.dev/)
