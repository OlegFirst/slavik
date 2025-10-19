#!/usr/bin/env bash
# Generate Kubernetes deployment manifests for all 11 BCM services

set -e

# Service configurations: name|port|iso-clause|description
SERVICES=(
    "bia-service|8020|8.2.2|Business Impact Analysis"
    "risk-service|8040|8.2.3|Risk Assessment"
    "compliance-service|8030|All|Compliance Management"
    "planning-service|8050|8.3|BCM Planning"
    "governance-service|8060|5.1-5.3|Governance"
    "plans-service|8070|8.4|Plan Management"
    "response-service|8080|8.4.3|Incident Response"
    "documents-service|8090|7.5|Document Management"
    "validation-service|8100|8.5|Validation & Testing"
    "learning-service|8110|7.2-7.3|Training & Awareness"
    "simulation-service|8130|8.5|Simulation & Exercises"
)

OUTPUT_DIR="./deployments/bcm-services"
mkdir -p "$OUTPUT_DIR"

for service_config in "${SERVICES[@]}"; do
    IFS='|' read -r service port iso_clause description <<< "$service_config"

    cat > "$OUTPUT_DIR/${service}-deployment.yaml" <<EOF
# ${description} Service Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${service}
  namespace: bcm-platform
  labels:
    app: ${service}
    component: bcm-service
    platform: bcm
    iso-clause: "${iso_clause}"
  annotations:
    description: "${description}"
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: ${service}
  template:
    metadata:
      labels:
        app: ${service}
        component: bcm-service
        platform: bcm
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "${port}"
        prometheus.io/path: "/metrics"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      initContainers:
      - name: wait-for-database
        image: busybox:1.36
        command: ['sh', '-c', 'until nc -z postgres-service 5432; do echo waiting for database; sleep 2; done;']

      containers:
      - name: ${service%-service}
        image: ghcr.io/seh-foundation/ai-platform-iso/${service}:v2.0.0
        imagePullPolicy: Always

        ports:
        - name: http
          containerPort: ${port}
          protocol: TCP

        env:
        - name: PORT
          value: "${port}"
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"

        # Database
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bcm-secrets
              key: database-url

        # Redis
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: bcm-secrets
              key: redis-url

        # Platform Integration
        - name: PLATFORM_INTEGRATION_ENABLED
          value: "true"

        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        startupProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30

        volumeMounts:
        - name: logs
          mountPath: /app/logs

      volumes:
      - name: logs
        emptyDir: {}

      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - ${service}
              topologyKey: kubernetes.io/hostname

---
apiVersion: v1
kind: Service
metadata:
  name: ${service}
  namespace: bcm-platform
  labels:
    app: ${service}
    component: bcm-service
spec:
  type: ClusterIP
  ports:
  - name: http
    port: ${port}
    targetPort: http
    protocol: TCP
  selector:
    app: ${service}
  sessionAffinity: ClientIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ${service}-hpa
  namespace: bcm-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ${service}
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
EOF

    echo "✅ Generated ${service}-deployment.yaml"
done

echo ""
echo "🎉 All BCM service deployments generated!"
echo "📁 Location: $OUTPUT_DIR"
