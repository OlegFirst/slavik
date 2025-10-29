#!/bin/bash

# 🚀 BCM Docker AI Quick Deploy Script
# Supports: Railway, Render, DigitalOcean, Google Cloud Run, Local

set -e

echo "🤖 BCM Docker AI Quick Deploy"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_IMAGE="maxde4/bcm-ai-unified:latest"
ODOO_IMAGE="maxde4/seh-foundation-iso-22301:latest"

show_menu() {
    echo ""
    echo "Select deployment target:"
    echo "1) Local Docker (recommended for testing)"
    echo "2) Railway (fastest cloud deploy)"
    echo "3) Render (free tier available)"
    echo "4) DigitalOcean App Platform"
    echo "5) Google Cloud Run"
    echo "6) Docker Compose (full stack locally)"
    echo "7) Update all deployed instances"
    echo "0) Exit"
    echo ""
}

deploy_local() {
    echo -e "${BLUE}🐳 Deploying locally...${NC}"

    # Pull latest images
    docker pull $DOCKER_IMAGE
    docker pull $ODOO_IMAGE

    # Stop existing containers
    docker stop bcm-ai-local bcm-odoo-local 2>/dev/null || true
    docker rm bcm-ai-local bcm-odoo-local 2>/dev/null || true

    # Start AI service
    docker run -d \
        --name bcm-ai-local \
        -p 8000:8000 \
        --restart unless-stopped \
        $DOCKER_IMAGE

    # Start Odoo service
    docker run -d \
        --name bcm-odoo-local \
        -p 8069:8069 \
        --restart unless-stopped \
        $ODOO_IMAGE

    echo -e "${GREEN}✅ Local deployment completed!${NC}"
    echo "🔗 AI Service: http://localhost:8000"
    echo "🔗 Odoo BCM: http://localhost:8069"
}

deploy_railway() {
    echo -e "${BLUE}🚂 Deploying to Railway...${NC}"

    if [ -z "$RAILWAY_TOKEN" ]; then
        echo -e "${RED}❌ RAILWAY_TOKEN environment variable not set${NC}"
        echo "Get your token from: https://railway.app/account/tokens"
        return 1
    fi

    # Deploy using Railway CLI or API
    if command -v railway &> /dev/null; then
        railway login --token $RAILWAY_TOKEN
        railway up --detach
    else
        # API deployment
        curl -X POST \
            -H "Authorization: Bearer $RAILWAY_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"image\": \"$DOCKER_IMAGE\"}" \
            https://backboard.railway.app/v2/deploy
    fi

    echo -e "${GREEN}✅ Railway deployment initiated!${NC}"
}

deploy_render() {
    echo -e "${BLUE}🎨 Deploying to Render...${NC}"

    if [ -z "$RENDER_API_KEY" ]; then
        echo -e "${RED}❌ RENDER_API_KEY environment variable not set${NC}"
        echo "Get your API key from: https://dashboard.render.com/account/api-keys"
        return 1
    fi

    curl -X POST \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"serviceId\": \"$RENDER_SERVICE_ID\", \"imageName\": \"$DOCKER_IMAGE\"}" \
        https://api.render.com/v1/services/deploys

    echo -e "${GREEN}✅ Render deployment initiated!${NC}"
}

deploy_digitalocean() {
    echo -e "${BLUE}🌊 Deploying to DigitalOcean...${NC}"

    if [ -z "$DO_API_TOKEN" ]; then
        echo -e "${RED}❌ DO_API_TOKEN environment variable not set${NC}"
        return 1
    fi

    # Use doctl if available
    if command -v doctl &> /dev/null; then
        doctl apps create-deployment $DO_APP_ID
    else
        echo "Install doctl CLI: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    fi

    echo -e "${GREEN}✅ DigitalOcean deployment initiated!${NC}"
}

deploy_gcp() {
    echo -e "${BLUE}☁️ Deploying to Google Cloud Run...${NC}"

    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not installed${NC}"
        echo "Install from: https://cloud.google.com/sdk/docs/install"
        return 1
    fi

    # Deploy AI service
    gcloud run deploy bcm-ai-unified \
        --image=$DOCKER_IMAGE \
        --platform=managed \
        --region=us-central1 \
        --allow-unauthenticated \
        --port=8000

    # Deploy Odoo service
    gcloud run deploy bcm-odoo \
        --image=$ODOO_IMAGE \
        --platform=managed \
        --region=us-central1 \
        --allow-unauthenticated \
        --port=8069

    echo -e "${GREEN}✅ Google Cloud Run deployment completed!${NC}"
}

deploy_compose() {
    echo -e "${BLUE}🐳 Deploying full stack with Docker Compose...${NC}"

    # Pull latest images first
    docker pull $DOCKER_IMAGE
    docker pull $ODOO_IMAGE

    # Update docker-compose.yml with latest images
    sed -i.bak "s|image: bcm-ai-unified:.*|image: $DOCKER_IMAGE|g" docker-compose.yml
    sed -i.bak "s|image: maxde4/seh-foundation-iso-22301:.*|image: $ODOO_IMAGE|g" docker-compose.yml

    # Deploy with compose
    docker-compose down
    docker-compose up -d

    echo -e "${GREEN}✅ Docker Compose deployment completed!${NC}"
    echo "🔗 Services starting at:"
    echo "   - AI Service: http://localhost:8000"
    echo "   - Odoo BCM: http://localhost:8069"
    echo "   - Redis: localhost:6379"
    echo "   - PostgreSQL: localhost:5432"
}

update_all() {
    echo -e "${YELLOW}🔄 Updating all deployed instances...${NC}"

    echo "Pulling latest images..."
    docker pull $DOCKER_IMAGE
    docker pull $ODOO_IMAGE

    # Update local if running
    if docker ps | grep -q bcm-ai-local; then
        echo "Updating local deployment..."
        deploy_local
    fi

    # Update cloud deployments if tokens are available
    [ ! -z "$RAILWAY_TOKEN" ] && deploy_railway
    [ ! -z "$RENDER_API_KEY" ] && deploy_render
    [ ! -z "$DO_API_TOKEN" ] && deploy_digitalocean

    echo -e "${GREEN}✅ All updates completed!${NC}"
}

# Main script
while true; do
    show_menu
    read -p "Enter your choice [0-7]: " choice

    case $choice in
        1) deploy_local ;;
        2) deploy_railway ;;
        3) deploy_render ;;
        4) deploy_digitalocean ;;
        5) deploy_gcp ;;
        6) deploy_compose ;;
        7) update_all ;;
        0) echo "👋 Goodbye!"; exit 0 ;;
        *) echo -e "${RED}❌ Invalid option. Please try again.${NC}" ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
done