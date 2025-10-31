#!/bin/bash

# Docker AI BCM Platform - Build and Push Script
# Builds all Docker images and pushes to registry

set -e

echo "🐳 Building Complete BCM Platform Images (84+ Components)"
echo "========================================================"
echo "📦 Building all services:"
echo "   • 🏗️  Core Services (5)"
echo "   • 🤖 AI Services (9)"
echo "   • ⚙️  Backend Services (4)"
echo "   • 🔌 Adapter Services (3)"
echo "   • 🔗 Integration Services (5)"
echo "   • 🖥️  Frontend Applications (6)"
echo "   • 🏢 Odoo BCM Modules (20)"
echo ""

# Configuration
REGISTRY=${DOCKER_REGISTRY:-"ghcr.io/seh-foundation/iso-22301"}
VERSION=${VERSION:-"latest"}
BUILD_TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "📋 Build Configuration:"
echo "• Registry: $REGISTRY"
echo "• Version: $VERSION"
echo "• Build ID: $BUILD_TIMESTAMP"

# Function to build and tag image
build_and_tag() {
    local service_name=$1
    local dockerfile_path=$2
    local context_path=$3

    # Check if Dockerfile exists
    if [ ! -f "$dockerfile_path" ]; then
        echo "⚠️  Skipping $service_name - Dockerfile not found: $dockerfile_path"
        return 0
    fi

    # Check if context path exists
    if [ ! -d "$context_path" ]; then
        echo "⚠️  Skipping $service_name - Context path not found: $context_path"
        return 0
    fi

    echo ""
    echo "🔧 Building $service_name..."

    docker build \
        -f "$dockerfile_path" \
        -t "$REGISTRY/bcm-$service_name:$VERSION" \
        -t "$REGISTRY/bcm-$service_name:$BUILD_TIMESTAMP" \
        "$context_path"

    echo "✅ Built $service_name"
}

# Build core services
echo ""
echo "🏗️  Building Core Services..."

build_and_tag "ai-orchestrator" "services/ai_orchestrator/Dockerfile" "services/ai_orchestrator/"
build_and_tag "ai-control-center" "services/ai_control_center/Dockerfile" "services/ai_control_center/"
build_and_tag "unified-database-gateway" "services/unified_database_gateway/Dockerfile" "services/unified_database_gateway/"
build_and_tag "unified-api-gateway" "services/unified_api_gateway/Dockerfile" "services/unified_api_gateway/"
build_and_tag "crm-bridge" "services/crm_bridge/Dockerfile" "services/crm_bridge/"

# Build AI services
echo ""
echo "🤖 Building AI Services..."

build_and_tag "bia-engine" "services/bia_engine/Dockerfile" "services/bia_engine/"
build_and_tag "document-processor" "services/document_processor/Dockerfile" "services/document_processor/"
build_and_tag "ai-consultant" "services/ai-consultant/Dockerfile" "services/ai-consultant/"
build_and_tag "ai-workflow-optimizer" "services/ai_workflow_optimizer/Dockerfile" "services/ai_workflow_optimizer/"
build_and_tag "process-mining-service" "services/process_mining_service/Dockerfile" "services/process_mining_service/"
build_and_tag "document-management" "services/document_management/Dockerfile" "services/document_management/"
build_and_tag "knowledge-base" "services/knowledge-base/Dockerfile" "services/knowledge-base/"
build_and_tag "scenario-orchestrator" "services/scenario_orchestrator/Dockerfile" "services/scenario_orchestrator/"
build_and_tag "github-app" "services/github_app/Dockerfile" "services/github_app/"

# Build backend services
echo ""
echo "⚙️  Building Backend Services..."

build_and_tag "notification-service" "services/notification_service/Dockerfile" "services/notification_service/"
build_and_tag "monitoring-service" "services/monitoring_service/Dockerfile" "services/monitoring_service/"
build_and_tag "realtime-websocket" "services/realtime_websocket/Dockerfile" "services/realtime_websocket/"
build_and_tag "deployer" "services/deployer/Dockerfile" "services/deployer/"

# Build adapter services
echo ""
echo "🔌 Building Adapter Services..."

build_and_tag "document-processor-adapter" "adapters/document-processor/Dockerfile" "adapters/document-processor/"
build_and_tag "thehive-adapter" "adapters/thehive/Dockerfile" "adapters/thehive/"
build_and_tag "simulation-adapter" "adapters/simulation/Dockerfile" "adapters/simulation/"

# Build integration services
echo ""
echo "🔗 Building Integration Services..."

build_and_tag "mcp-server" "integrations/mcp-server/Dockerfile" "integrations/mcp-server/"
build_and_tag "exercise-simulators" "integrations/exercise_simulators/Dockerfile.bridge" "integrations/exercise_simulators/"
build_and_tag "governance-service" "integrations/governance/Dockerfile" "integrations/governance/"
build_and_tag "thehive-integration" "integrations/thehive/Dockerfile.bridge" "integrations/thehive/"
build_and_tag "moodle-integration" "integrations/moodle/Dockerfile.bridge" "integrations/moodle/"

# Build frontend applications
echo ""
echo "🖥️  Building Frontend Applications..."

build_and_tag "admin-panel" "frontend/admin_panel/Dockerfile" "frontend/admin_panel/"
build_and_tag "admin-panel3" "frontend/admin_panel3/Dockerfile" "frontend/admin_panel3/"
build_and_tag "unified-bcm-platform" "frontend/unified-bcm-platform/Dockerfile" "frontend/unified-bcm-platform/"
build_and_tag "bcm-marketplace" "frontend/bcm-marketplace/Dockerfile" "frontend/bcm-marketplace/"
build_and_tag "web-portal-enhanced" "frontend/web_portal_enhanced/Dockerfile" "frontend/web_portal_enhanced/"
build_and_tag "digital-twin-platform" "services/digital-twin-platform/Dockerfile" "services/digital-twin-platform/"

# Show built images
echo ""
echo "📦 Built Images:"
docker images | grep "$REGISTRY/bcm-" | head -10

# Optional: Push to registry
if [ "$PUSH_IMAGES" = "true" ]; then
    echo ""
    echo "🚀 Pushing to registry..."

    for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep "$REGISTRY/bcm-"); do
        echo "⬆️  Pushing $image..."
        docker push "$image"
    done

    echo "✅ All images pushed to $REGISTRY"
else
    echo ""
    echo "💡 To push images to registry, run:"
    echo "   PUSH_IMAGES=true ./build-docker-images.sh"
fi

echo ""
echo "🎉 Docker AI BCM Platform build complete!"
echo "Images available at: $REGISTRY"