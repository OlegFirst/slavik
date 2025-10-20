#!/bin/bash
#
# BCM Platform Deployment to GKE Script
# Deploys the BCM Platform services to Google Kubernetes Engine
#

set -e

# Load configuration
if [ -f "terraform.tfvars" ]; then
    source <(grep -v '^#' terraform.tfvars | sed 's/[[:space:]]*=[[:space:]]*/=/' | sed 's/^/export /')
fi

# Default values
PROJECT_ID="${project_id:-my-gcp-project}"
CLUSTER_NAME="${cluster_name:-bcm-platform-autopilot}"
REGION="${region:-us-central1}"
BCM_NAMESPACE="${bcm_namespace:-bcm-platform}"
KUBERNETES_MANIFESTS_DIR="${kubernetes_manifests_dir:-../../kubernetes}"

echo "========================================="
echo "Deploying BCM Platform to GKE"
echo "========================================="
echo "Project ID: $PROJECT_ID"
echo "Cluster Name: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Namespace: $BCM_NAMESPACE"
echo "========================================="

# Verify kubectl is configured
echo "Verifying kubectl configuration..."
kubectl cluster-info > /dev/null 2>&1 || {
    echo "Error: kubectl not configured. Run ./gke-configure.sh first"
    exit 1
}

# Verify we're connected to the correct cluster
CURRENT_CLUSTER=$(kubectl config current-context)
if [[ ! "$CURRENT_CLUSTER" =~ "$CLUSTER_NAME" ]]; then
    echo "Warning: Current context ($CURRENT_CLUSTER) doesn't match expected cluster ($CLUSTER_NAME)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

echo ""
echo "========================================="
echo "1. Creating BCM Namespace"
echo "========================================="
echo ""

# Create namespace
kubectl create namespace "$BCM_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Enable Istio injection for BCM namespace
kubectl label namespace "$BCM_NAMESPACE" istio-injection=enabled --overwrite

echo "Namespace '$BCM_NAMESPACE' created and configured"
echo ""

echo "========================================="
echo "2. Creating Secrets and ConfigMaps"
echo "========================================="
echo ""

# Create example secret for database credentials
# In production, use Google Secret Manager
# Reference: https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: bcm-database-credentials
  namespace: $BCM_NAMESPACE
type: Opaque
stringData:
  POSTGRES_USER: bcm_user
  POSTGRES_PASSWORD: CHANGE_ME_IN_PRODUCTION
  POSTGRES_DB: bcm_platform
  POSTGRES_HOST: postgresql.bcm-platform.svc.cluster.local
  POSTGRES_PORT: "5432"
EOF

echo "Database credentials secret created (update in production!)"
echo ""

echo "========================================="
echo "3. Deploying Kubernetes Manifests"
echo "========================================="
echo ""

# Check if Kubernetes manifests directory exists
if [ ! -d "$KUBERNETES_MANIFESTS_DIR" ]; then
    echo "Warning: Kubernetes manifests directory not found: $KUBERNETES_MANIFESTS_DIR"
    echo "Please ensure your Kubernetes manifests are in the correct location"
    echo ""

    # Create a minimal deployment example
    echo "Creating example deployment..."
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: bcm-platform
  namespace: $BCM_NAMESPACE
  labels:
    app: bcm-platform
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    name: http
  selector:
    app: bcm-platform
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bcm-platform
  namespace: $BCM_NAMESPACE
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bcm-platform
  template:
    metadata:
      labels:
        app: bcm-platform
        version: v1
    spec:
      containers:
      - name: bcm-platform
        image: gcr.io/$PROJECT_ID/bcm-platform:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: bcm-database-credentials
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: bcm-database-credentials
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: bcm-database-credentials
              key: POSTGRES_DB
        - name: POSTGRES_HOST
          valueFrom:
            secretKeyRef:
              name: bcm-database-credentials
              key: POSTGRES_HOST
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
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

    echo "Example deployment created"
else
    # Apply Kubernetes manifests from directory
    echo "Applying Kubernetes manifests from $KUBERNETES_MANIFESTS_DIR..."
    kubectl apply -f "$KUBERNETES_MANIFESTS_DIR" --namespace="$BCM_NAMESPACE" --recursive
fi

echo ""
echo "========================================="
echo "4. Verifying Deployment"
echo "========================================="
echo ""

echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment --all -n "$BCM_NAMESPACE" || true

echo ""
echo "Deployments status:"
kubectl get deployments -n "$BCM_NAMESPACE"
echo ""

echo "Pods status:"
kubectl get pods -n "$BCM_NAMESPACE"
echo ""

echo "Services status:"
kubectl get services -n "$BCM_NAMESPACE"
echo ""

echo "========================================="
echo "5. Getting Service Endpoints"
echo "========================================="
echo ""

echo "Waiting for LoadBalancer external IP..."
echo "This may take a few minutes..."
sleep 10

kubectl get services -n "$BCM_NAMESPACE" -o wide

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "To check the status of your deployment:"
echo "  kubectl get all -n $BCM_NAMESPACE"
echo ""
echo "To view logs:"
echo "  kubectl logs -n $BCM_NAMESPACE -l app=bcm-platform --tail=100"
echo ""
echo "To get LoadBalancer IP:"
echo "  kubectl get svc -n $BCM_NAMESPACE bcm-platform -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
echo ""
echo "To access the application:"
echo "  export BCM_IP=\$(kubectl get svc -n $BCM_NAMESPACE bcm-platform -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo "  echo \"BCM Platform available at: http://\$BCM_IP\""
echo ""
echo "Next steps:"
echo "  1. Set up Velero backups (see README.md)"
echo "  2. Configure monitoring and alerting"
echo "  3. Set up CI/CD pipelines"
echo ""
