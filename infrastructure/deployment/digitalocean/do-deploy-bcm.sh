#!/bin/bash
#
# Deploy BCM Platform to DigitalOcean Kubernetes
# Based on official Kubernetes and Helm best practices
#

set -e

# Configuration variables
CLUSTER_NAME="${CLUSTER_NAME:-bcm-platform-cluster}"
NAMESPACE="${NAMESPACE:-bcm-platform}"
HELM_RELEASE_NAME="${HELM_RELEASE_NAME:-bcm-platform}"
HELM_CHART_PATH="${HELM_CHART_PATH:-../../helm/bcm-platform}"
VALUES_FILE="${VALUES_FILE:-values-digitalocean.yaml}"
INGRESS_HOST="${INGRESS_HOST:-bcm.example.com}"
STORAGE_CLASS="${STORAGE_CLASS:-do-block-storage}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploy BCM Platform to DOKS${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: helm is not installed${NC}"
    exit 1
fi

# Verify cluster connection
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Not connected to Kubernetes cluster${NC}"
    echo "Please run ./do-configure.sh first"
    exit 1
fi

echo -e "${YELLOW}Step 1: Verifying cluster readiness...${NC}"
echo ""

# Get cluster nodes
echo "Cluster nodes:"
kubectl get nodes
echo ""

# Check if ingress-nginx is installed
if ! kubectl get namespace ingress-nginx &> /dev/null; then
    echo -e "${RED}Error: ingress-nginx not found${NC}"
    echo "Please run ./do-install-addons.sh first"
    exit 1
fi

# Get LoadBalancer IP
echo "Waiting for LoadBalancer IP to be assigned..."
EXTERNAL_IP=""
TIMEOUT=300
ELAPSED=0

while [ -z "$EXTERNAL_IP" ] && [ $ELAPSED -lt $TIMEOUT ]; do
    EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")

    if [ -z "$EXTERNAL_IP" ]; then
        echo "Waiting for LoadBalancer IP... (${ELAPSED}s)"
        sleep 5
        ELAPSED=$((ELAPSED + 5))
    fi
done

if [ -z "$EXTERNAL_IP" ]; then
    echo -e "${RED}Warning: LoadBalancer IP not assigned yet${NC}"
    echo "You may need to wait longer or check ingress-nginx service"
else
    echo -e "${GREEN}LoadBalancer IP: $EXTERNAL_IP${NC}"
    echo ""
    echo "Configure your DNS:"
    echo "  $INGRESS_HOST A $EXTERNAL_IP"
fi
echo ""

echo -e "${YELLOW}Step 2: Creating namespace...${NC}"
echo ""

if kubectl get namespace $NAMESPACE &> /dev/null; then
    echo -e "${GREEN}✓ Namespace $NAMESPACE already exists${NC}"
else
    kubectl create namespace $NAMESPACE
    echo -e "${GREEN}✓ Namespace $NAMESPACE created${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Creating DigitalOcean-specific values file...${NC}"
echo ""

cat > $VALUES_FILE <<EOF
# BCM Platform values for DigitalOcean Kubernetes
# Generated on $(date)

global:
  environment: production
  domain: $INGRESS_HOST
  storageClass: $STORAGE_CLASS

# Ingress configuration for DigitalOcean LoadBalancer
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: $INGRESS_HOST
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: bcm-platform-tls
      hosts:
        - $INGRESS_HOST

# Storage configuration using DigitalOcean Block Storage
persistence:
  storageClass: $STORAGE_CLASS
  size: 20Gi

# PostgreSQL configuration
postgresql:
  enabled: true
  auth:
    database: bcm_platform
    username: bcm_user
    # Set password via --set postgresql.auth.password=<password>
  primary:
    persistence:
      enabled: true
      storageClass: $STORAGE_CLASS
      size: 20Gi
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

# Redis configuration
redis:
  enabled: true
  master:
    persistence:
      enabled: true
      storageClass: $STORAGE_CLASS
      size: 8Gi
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "250m"

# RabbitMQ configuration
rabbitmq:
  enabled: true
  persistence:
    enabled: true
    storageClass: $STORAGE_CLASS
    size: 8Gi
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

# DigitalOcean-specific resource configurations
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

# Autoscaling (compatible with DOKS)
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

# Monitoring integration
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
  prometheusRule:
    enabled: true

# Backup annotations for Velero
podAnnotations:
  backup.velero.io/backup-volumes: data

EOF

echo -e "${GREEN}✓ Values file created: $VALUES_FILE${NC}"
echo ""

echo -e "${YELLOW}Step 4: Checking if Helm chart exists...${NC}"
echo ""

if [ ! -d "$HELM_CHART_PATH" ]; then
    echo -e "${YELLOW}⚠ Helm chart not found at: $HELM_CHART_PATH${NC}"
    echo "Please ensure the BCM Platform Helm chart exists"
    echo "You may need to adjust HELM_CHART_PATH variable"
    echo ""
    echo "Continuing with deployment preparation..."
    echo ""
else
    echo -e "${GREEN}✓ Helm chart found${NC}"
    echo ""

    echo -e "${YELLOW}Step 5: Validating Helm chart...${NC}"
    echo ""
    helm lint $HELM_CHART_PATH -f $VALUES_FILE || echo -e "${YELLOW}⚠ Helm lint warnings (review above)${NC}"
    echo ""
fi

echo -e "${YELLOW}Step 6: Deployment options...${NC}"
echo ""
echo "To deploy the BCM Platform, you have two options:"
echo ""
echo "Option 1: Deploy with Helm (recommended)"
echo "==========================================="
echo ""
echo -e "${GREEN}helm install $HELM_RELEASE_NAME $HELM_CHART_PATH \\${NC}"
echo -e "${GREEN}  --namespace $NAMESPACE \\${NC}"
echo -e "${GREEN}  --values $VALUES_FILE \\${NC}"
echo -e "${GREEN}  --set postgresql.auth.password=<secure-password> \\${NC}"
echo -e "${GREEN}  --set redis.auth.password=<secure-password> \\${NC}"
echo -e "${GREEN}  --set rabbitmq.auth.password=<secure-password> \\${NC}"
echo -e "${GREEN}  --timeout 10m \\${NC}"
echo -e "${GREEN}  --wait${NC}"
echo ""
echo "Option 2: Deploy from Docker images (if using docker-compose setup)"
echo "======================================================================"
echo ""
echo "Build and push images to DigitalOcean Container Registry:"
echo -e "${GREEN}doctl registry login${NC}"
echo -e "${GREEN}docker-compose -f docker-compose.prod.yml build${NC}"
echo -e "${GREEN}docker-compose -f docker-compose.prod.yml push${NC}"
echo ""

echo -e "${YELLOW}Step 7: Post-deployment verification commands...${NC}"
echo ""
echo "After deployment, verify with:"
echo ""
echo "  # Check pod status"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "  # Check services"
echo "  kubectl get svc -n $NAMESPACE"
echo ""
echo "  # Check ingress"
echo "  kubectl get ingress -n $NAMESPACE"
echo ""
echo "  # View logs"
echo "  kubectl logs -n $NAMESPACE -l app=bcm-platform --tail=100"
echo ""
echo "  # Check Helm release status"
echo "  helm status $HELM_RELEASE_NAME -n $NAMESPACE"
echo ""

echo -e "${YELLOW}Step 8: Setting up TLS certificates...${NC}"
echo ""

if kubectl get namespace cert-manager &> /dev/null; then
    echo "Creating Let's Encrypt ClusterIssuer..."

    cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com  # CHANGE THIS
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

    echo ""
    echo -e "${GREEN}✓ ClusterIssuer created${NC}"
    echo -e "${YELLOW}⚠ Remember to update the email address in the ClusterIssuer${NC}"
else
    echo -e "${YELLOW}⚠ cert-manager not found. Install it with ./do-install-addons.sh${NC}"
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment preparation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Summary:"
echo "  Namespace: $NAMESPACE"
echo "  Helm Release: $HELM_RELEASE_NAME"
echo "  Ingress Host: $INGRESS_HOST"
if [ -n "$EXTERNAL_IP" ]; then
    echo "  LoadBalancer IP: $EXTERNAL_IP"
fi
echo "  Values File: $VALUES_FILE"
echo ""
echo "Next steps:"
echo "1. Update DNS: Point $INGRESS_HOST to $EXTERNAL_IP"
echo "2. Update email in ClusterIssuer for Let's Encrypt"
echo "3. Run the Helm install command shown above"
echo "4. Set up Velero backup schedules"
echo "5. Configure monitoring and alerts"
echo ""
