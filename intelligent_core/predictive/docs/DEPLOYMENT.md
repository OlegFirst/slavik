# Predictive Journey Service - Deployment Guide

**Document Version**: 1.0.0
**Last Updated**: 2025-10-09

## 1. Deployment Overview

This guide covers production deployment of the Predictive Journey Service across multiple environments using Docker, Kubernetes, and cloud platforms.

## 2. Prerequisites

### 2.1 Infrastructure Requirements

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| PostgreSQL | 15+ | Predictions storage (Supabase) |
| Redis | 7.0+ | EventBus messaging, caching |
| Python | 3.11+ | Runtime environment |
| Docker | 24+ | Containerization |
| Kubernetes | 1.27+ | Orchestration (optional) |

### 2.2 External Services

- **Supabase Account**: PostgreSQL database
- **Redis Instance**: EventBus and caching
- **SMTP Server**: Email delivery (via notification service)
- **Prometheus**: Metrics collection (optional)

### 2.3 Resource Requirements

**Minimum (Development)**:
- CPU: 250m (0.25 cores)
- Memory: 256Mi
- Storage: 1Gi

**Recommended (Production)**:
- CPU: 500m-1000m (0.5-1 cores)
- Memory: 512Mi-1Gi
- Storage: 5Gi

**Scaling**:
- 2-10 replicas based on load
- Auto-scaling at 70% CPU utilization

## 3. Docker Deployment

### 3.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8031

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8031/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8031"]
```

### 3.2 Build and Run

```bash
# Build image
docker build -t predictive-journey:1.0.0 .

# Tag for registry
docker tag predictive-journey:1.0.0 registry.example.com/predictive-journey:1.0.0

# Push to registry
docker push registry.example.com/predictive-journey:1.0.0

# Run container
docker run -d \
  --name predictive-journey \
  -p 8031:8031 \
  --env-file .env \
  --restart unless-stopped \
  registry.example.com/predictive-journey:1.0.0
```

### 3.3 Docker Compose

```yaml
version: '3.8'

services:
  predictive:
    image: registry.example.com/predictive-journey:1.0.0
    container_name: predictive-journey
    ports:
      - "8031:8031"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - REDIS_URL=redis://redis:6379
      - NOTIFICATION_SERVICE_URL=http://notification-service:8020
      - ENABLE_DAILY_DIGESTS=true
      - LOG_LEVEL=INFO
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8031/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

Run with:
```bash
docker-compose up -d
```

## 4. Kubernetes Deployment

### 4.1 Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: predictive-journey
  namespace: intelligent-core
  labels:
    app: predictive-journey
    component: intelligent-core
spec:
  replicas: 2
  selector:
    matchLabels:
      app: predictive-journey
  template:
    metadata:
      labels:
        app: predictive-journey
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8031"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: predictive-journey
        image: registry.example.com/predictive-journey:1.0.0
        ports:
        - containerPort: 8031
          name: http
        env:
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: predictive-secrets
              key: supabase-url
        - name: SUPABASE_KEY
          valueFrom:
            secretKeyRef:
              name: predictive-secrets
              key: supabase-key
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: NOTIFICATION_SERVICE_URL
          value: "http://notification-service:8020"
        - name: ENABLE_DAILY_DIGESTS
          value: "true"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8031
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8031
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: predictive-config
```

### 4.2 Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: predictive-service
  namespace: intelligent-core
  labels:
    app: predictive-journey
spec:
  type: ClusterIP
  ports:
  - port: 8031
    targetPort: 8031
    protocol: TCP
    name: http
  selector:
    app: predictive-journey
```

### 4.3 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: predictive-config
  namespace: intelligent-core
data:
  MIN_SIMILAR_ORGS: "3"
  TARGET_SIMILAR_ORGS: "50"
  MIN_CONFIDENCE: "0.7"
  MIN_PATTERN_FREQUENCY: "0.30"
  DAILY_DIGEST_HOUR: "8"
  CACHE_TTL_HOURS: "24"
```

### 4.4 Secret Manifest

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: predictive-secrets
  namespace: intelligent-core
type: Opaque
stringData:
  supabase-url: "https://your-project.supabase.co"
  supabase-key: "your-anon-key"
```

Apply with:
```bash
kubectl apply -f k8s/
```

### 4.5 Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: predictive-hpa
  namespace: intelligent-core
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: predictive-journey
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 5. Environment Configuration

### 5.1 Environment Variables

```bash
# Database (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Messaging (Required)
REDIS_URL=redis://localhost:6379

# Integrations (Required)
NOTIFICATION_SERVICE_URL=http://localhost:8020
CASE_LIBRARY_ENABLED=true

# Scheduler (Optional)
ENABLE_DAILY_DIGESTS=true
DAILY_DIGEST_HOUR=8

# Prediction Thresholds (Optional)
MIN_SIMILAR_ORGS=3
TARGET_SIMILAR_ORGS=50
MIN_CONFIDENCE=0.7
MIN_PATTERN_FREQUENCY=0.30

# Caching (Optional)
CACHE_TTL_HOURS=24

# Logging (Optional)
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Performance (Optional)
WORKERS=2
MAX_CONNECTIONS=100
TIMEOUT=30
```

### 5.2 Configuration File (.env)

```bash
# Copy example
cp .env.example .env

# Edit with production values
nano .env
```

### 5.3 Secrets Management

**Using Kubernetes Secrets**:
```bash
# Create secret from file
kubectl create secret generic predictive-secrets \
  --from-file=supabase-url=./secrets/supabase-url.txt \
  --from-file=supabase-key=./secrets/supabase-key.txt \
  -n intelligent-core

# Or from literals
kubectl create secret generic predictive-secrets \
  --from-literal=supabase-url='https://...' \
  --from-literal=supabase-key='eyJ...' \
  -n intelligent-core
```

**Using HashiCorp Vault**:
```python
import hvac

# Connect to Vault
client = hvac.Client(url='http://vault:8200')
client.token = os.getenv('VAULT_TOKEN')

# Read secrets
secrets = client.secrets.kv.v2.read_secret_version(
    path='predictive-journey'
)

SUPABASE_URL = secrets['data']['data']['supabase_url']
SUPABASE_KEY = secrets['data']['data']['supabase_key']
```

## 6. Database Setup

### 6.1 Supabase Initialization

```sql
-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    predicted_data JSONB NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    horizon_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_predictions_org_type ON predictions(organization_id, prediction_type);
CREATE INDEX idx_predictions_created ON predictions(created_at DESC);
CREATE INDEX idx_predictions_expires ON predictions(expires_at) WHERE expires_at IS NOT NULL;

-- Create accuracy tracking table
CREATE TABLE IF NOT EXISTS prediction_accuracy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID REFERENCES predictions(id),
    predicted_date DATE NOT NULL,
    actual_date DATE,
    error_days INTEGER,
    was_accurate BOOLEAN,
    tracked_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_accuracy_prediction ON prediction_accuracy(prediction_id);

-- Create pattern cache table
CREATE TABLE IF NOT EXISTS pattern_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_key VARCHAR(200) UNIQUE NOT NULL,
    pattern_data JSONB NOT NULL,
    confidence FLOAT,
    sample_size INTEGER,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pattern_key ON pattern_cache(pattern_key);
```

### 6.2 Migration Script

```python
#!/usr/bin/env python3
"""Database migration script"""

import os
from supabase import create_client

def run_migration():
    """Run database migration"""
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

    # Read migration SQL
    with open('migrations/001_initial_schema.sql', 'r') as f:
        sql = f.read()

    # Execute migration
    result = supabase.rpc('execute_sql', {'sql': sql}).execute()

    print(f"Migration complete: {result}")

if __name__ == '__main__':
    run_migration()
```

## 7. Monitoring and Observability

### 7.1 Health Checks

```bash
# Liveness check
curl http://predictive-service:8031/health

# Expected response:
{
  "status": "healthy",
  "service": "predictive-journey",
  "version": "1.0.0",
  "checks": {
    "database": true,
    "eventbus": true,
    "case_library": true,
    "scheduler": true
  }
}
```

### 7.2 Prometheus Metrics

```yaml
# ServiceMonitor for Prometheus Operator
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: predictive-journey
  namespace: intelligent-core
spec:
  selector:
    matchLabels:
      app: predictive-journey
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

**Key Metrics**:
- `predictive_predictions_total` - Total predictions generated
- `predictive_confidence_avg` - Average confidence scores
- `predictive_similar_orgs_count` - Similar organizations found
- `predictive_daily_digests_sent` - Daily digest deliveries
- `predictive_event_publications` - EventBus publications
- `predictive_prediction_latency_seconds` - Prediction generation time
- `predictive_cache_hits_total` - Cache hit rate

### 7.3 Logging Configuration

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'service': 'predictive-journey',
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 7.4 Alerting Rules

```yaml
# Prometheus alerting rules
groups:
- name: predictive_journey
  interval: 30s
  rules:
  - alert: PredictiveLowConfidence
    expr: predictive_confidence_avg < 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Low prediction confidence"
      description: "Average confidence below 0.5 for 5 minutes"

  - alert: PredictiveHighLatency
    expr: histogram_quantile(0.95, predictive_prediction_latency_seconds) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High prediction latency"
      description: "95th percentile latency above 5 seconds"

  - alert: PredictiveServiceDown
    expr: up{job="predictive-journey"} == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Predictive service is down"
      description: "Service has been down for 2 minutes"
```

## 8. Scaling Strategies

### 8.1 Horizontal Scaling

```bash
# Manual scaling
kubectl scale deployment predictive-journey --replicas=5 -n intelligent-core

# Auto-scaling (via HPA)
kubectl autoscale deployment predictive-journey \
  --min=2 --max=10 --cpu-percent=70 \
  -n intelligent-core
```

### 8.2 Vertical Scaling

```yaml
# Increase resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### 8.3 Caching Optimization

```python
# Increase cache TTL for stable predictions
CACHE_CONFIG = {
    'journey_prediction': {
        'ttl': 86400 * 2,  # 48 hours
    },
    'certification_forecast': {
        'ttl': 604800 * 2,  # 14 days
    }
}
```

## 9. Backup and Recovery

### 9.1 Database Backup

```bash
# Backup predictions table (via Supabase)
# Enable daily automated backups in Supabase dashboard

# Manual backup
pg_dump -h your-project.supabase.co \
  -U postgres \
  -t predictions \
  -t prediction_accuracy \
  -t pattern_cache \
  > backup_$(date +%Y%m%d).sql
```

### 9.2 Redis Backup

```bash
# Enable Redis persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"

# Manual backup
redis-cli SAVE
cp /var/lib/redis/dump.rdb /backup/redis_$(date +%Y%m%d).rdb
```

### 9.3 Disaster Recovery

```bash
# Restore database
psql -h your-project.supabase.co \
  -U postgres \
  < backup_20251009.sql

# Restore Redis
redis-cli FLUSHALL
redis-cli --rdb /backup/redis_20251009.rdb
```

## 10. Security Hardening

### 10.1 Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: predictive-network-policy
  namespace: intelligent-core
spec:
  podSelector:
    matchLabels:
      app: predictive-journey
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8031
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - podSelector:
        matchLabels:
          app: notification-service
    ports:
    - protocol: TCP
      port: 8020
```

### 10.2 Pod Security

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: predictive-journey
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
  - name: predictive-journey
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

### 10.3 Secret Rotation

```bash
# Rotate Supabase key
# 1. Generate new key in Supabase dashboard
# 2. Update Kubernetes secret
kubectl create secret generic predictive-secrets \
  --from-literal=supabase-key='new-key' \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Restart deployment
kubectl rollout restart deployment/predictive-journey -n intelligent-core
```

## 11. Troubleshooting

### 11.1 Service Won't Start

```bash
# Check logs
kubectl logs -f deployment/predictive-journey -n intelligent-core

# Check events
kubectl get events -n intelligent-core --sort-by='.lastTimestamp'

# Common issues:
# - Missing secrets: Check SUPABASE_URL, SUPABASE_KEY
# - Redis unavailable: Check REDIS_URL connectivity
# - Port conflict: Verify port 8031 is available
```

### 11.2 High Memory Usage

```bash
# Check current usage
kubectl top pod -n intelligent-core -l app=predictive-journey

# Increase limits
kubectl set resources deployment/predictive-journey \
  --limits=memory=1Gi -n intelligent-core

# Enable memory profiling
python -m memory_profiler main.py
```

### 11.3 Predictions Not Generating

```bash
# Check case library connectivity
curl http://workflow-intelligence:8030/health

# Check EventBus
redis-cli -u $REDIS_URL PING

# Check logs for errors
kubectl logs -f deployment/predictive-journey | grep ERROR
```

## 12. Rollback Procedures

```bash
# View deployment history
kubectl rollout history deployment/predictive-journey -n intelligent-core

# Rollback to previous version
kubectl rollout undo deployment/predictive-journey -n intelligent-core

# Rollback to specific revision
kubectl rollout undo deployment/predictive-journey \
  --to-revision=2 -n intelligent-core

# Verify rollback
kubectl rollout status deployment/predictive-journey -n intelligent-core
```

## 13. Performance Tuning

### 13.1 Database Optimization

```sql
-- Add indexes for frequent queries
CREATE INDEX CONCURRENTLY idx_predictions_org_created
ON predictions(organization_id, created_at DESC);

-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM predictions
WHERE organization_id = 'uuid'
AND prediction_type = 'journey'
ORDER BY created_at DESC
LIMIT 1;
```

### 13.2 Caching Strategy

```python
# Warm cache on startup
async def warm_cache():
    """Pre-load frequently accessed predictions"""
    active_orgs = await get_active_organizations()

    for org in active_orgs:
        prediction = await generate_journey_prediction(org.id)
        await cache.set(f'prediction:journey:{org.id}', prediction, ttl=86400)
```

### 13.3 Connection Pooling

```python
from supabase import create_client

# Configure connection pool
supabase = create_client(
    url=SUPABASE_URL,
    key=SUPABASE_KEY,
    options={
        'db': {
            'pool_size': 20,
            'max_overflow': 10,
            'pool_timeout': 30
        }
    }
)
```

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
- Review Date: 2025-10-09
- Next Review: 2026-01-09
- Classification: Internal Use Only
