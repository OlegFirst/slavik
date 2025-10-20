#!/bin/bash
#
# DigitalOcean Kubernetes Cluster Creation Script
# Based on official doctl SDK documentation
# Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/create/
#

set -e

# Configuration variables
CLUSTER_NAME="${CLUSTER_NAME:-bcm-platform-cluster}"
REGION="${REGION:-nyc1}"
K8S_VERSION="${K8S_VERSION:-}"  # Empty means latest version
NODE_SIZE="${NODE_SIZE:-s-4vcpu-8gb}"
NODE_COUNT="${NODE_COUNT:-3}"
NODE_POOL_NAME="${NODE_POOL_NAME:-worker-pool}"
VPC_UUID="${VPC_UUID:-}"  # Optional: Specify VPC UUID if needed
HA_CONTROL_PLANE="${HA_CONTROL_PLANE:-true}"
AUTO_UPGRADE="${AUTO_UPGRADE:-false}"
TAGS="${TAGS:-bcm-platform,production}"
ONE_CLICKS="${ONE_CLICKS:-ingress-nginx,monitoring}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}DigitalOcean Kubernetes Cluster Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}Error: doctl is not installed${NC}"
    echo "Please install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if doctl is authenticated
if ! doctl auth list &> /dev/null; then
    echo -e "${RED}Error: doctl is not authenticated${NC}"
    echo "Please run: doctl auth init"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking available Kubernetes versions...${NC}"
echo ""
# Command reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/options/versions/
doctl kubernetes options versions
echo ""

if [ -z "$K8S_VERSION" ]; then
    echo -e "${YELLOW}Using latest Kubernetes version (no --version flag)${NC}"
else
    echo -e "${YELLOW}Using Kubernetes version: $K8S_VERSION${NC}"
fi
echo ""

echo -e "${YELLOW}Step 2: Checking available regions...${NC}"
echo ""
# Command reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/options/regions/
doctl kubernetes options regions
echo ""

echo -e "${YELLOW}Step 3: Checking available node sizes...${NC}"
echo ""
# Command reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/options/sizes/
doctl kubernetes options sizes
echo ""

echo -e "${YELLOW}Step 4: Creating DigitalOcean Kubernetes cluster...${NC}"
echo "Cluster Name: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Node Size: $NODE_SIZE"
echo "Node Count: $NODE_COUNT"
echo "HA Control Plane: $HA_CONTROL_PLANE"
echo "Auto Upgrade: $AUTO_UPGRADE"
echo "Tags: $TAGS"
echo "1-Click Apps: $ONE_CLICKS"
echo ""

# Build the create command based on official documentation
# Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/create/
CREATE_CMD="doctl kubernetes cluster create $CLUSTER_NAME \
  --region $REGION \
  --size $NODE_SIZE \
  --count $NODE_COUNT \
  --tag $TAGS"

# Add optional version flag if specified
if [ -n "$K8S_VERSION" ]; then
    CREATE_CMD="$CREATE_CMD --version $K8S_VERSION"
fi

# Add HA control plane if enabled
if [ "$HA_CONTROL_PLANE" = "true" ]; then
    CREATE_CMD="$CREATE_CMD --ha"
fi

# Add auto-upgrade if enabled
if [ "$AUTO_UPGRADE" = "true" ]; then
    CREATE_CMD="$CREATE_CMD --auto-upgrade"
fi

# Add VPC if specified
if [ -n "$VPC_UUID" ]; then
    CREATE_CMD="$CREATE_CMD --vpc-uuid $VPC_UUID"
fi

# Add 1-click applications if specified
if [ -n "$ONE_CLICKS" ]; then
    CREATE_CMD="$CREATE_CMD --1-clicks $ONE_CLICKS"
fi

# Execute the create command
echo -e "${GREEN}Executing: $CREATE_CMD${NC}"
echo ""
eval $CREATE_CMD

echo ""
echo -e "${GREEN}✓ Cluster creation initiated successfully!${NC}"
echo ""

echo -e "${YELLOW}Step 5: Waiting for cluster to be ready...${NC}"
echo "This may take several minutes..."
echo ""

# Wait for cluster to be running
# Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/get/
MAX_WAIT=600  # 10 minutes
ELAPSED=0
INTERVAL=10

while [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS=$(doctl kubernetes cluster get $CLUSTER_NAME --format Status --no-header 2>/dev/null || echo "unknown")

    if [ "$STATUS" = "running" ]; then
        echo -e "${GREEN}✓ Cluster is running!${NC}"
        break
    fi

    echo "Current status: $STATUS (waited ${ELAPSED}s)"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo -e "${RED}Error: Cluster did not become ready within $MAX_WAIT seconds${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 6: Retrieving cluster information...${NC}"
echo ""
# Reference: https://docs.digitalocean.com/reference/doctl/reference/kubernetes/cluster/get/
doctl kubernetes cluster get $CLUSTER_NAME

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cluster created successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Run ./do-configure.sh to configure kubectl access"
echo "2. Run ./do-install-addons.sh to install monitoring and tools"
echo "3. Run ./do-deploy-bcm.sh to deploy the BCM Platform"
echo ""
