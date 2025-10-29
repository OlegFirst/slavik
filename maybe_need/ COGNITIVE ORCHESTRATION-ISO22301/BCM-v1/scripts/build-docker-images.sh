#!/bin/bash

# Docker AI BCM Platform - Build and Push Script
# Builds all Docker images and pushes to registry

set -e

echo "🐳 Building Docker AI BCM Platform Images"
echo "========================================"

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

build_and_tag "ai-orchestrator" "services/ai_orchestrator/Dockerfile.docker-ai" "services/ai_orchestrator/"
build_and_tag "mcp-server" "docker-ai/mcp-server/Dockerfile" "docker-ai/mcp-server/"
build_and_tag "bia-engine" "services/bia_engine/Dockerfile" "services/bia_engine/"
build_and_tag "incident-agent" "services/ai/Dockerfile" "services/ai/"
build_and_tag "compliance-checker" "services/compliance_checker/Dockerfile" "services/compliance_checker/"
build_and_tag "document-processor" "services/document_processor/Dockerfile" "services/document_processor/"
build_and_tag "notification-service" "services/notification_service/Dockerfile" "services/notification_service/"
build_and_tag "github-app" "services/github_app/Dockerfile" "services/github_app/"

# Build specialized AI services
echo ""
echo "🤖 Building AI Services..."

build_and_tag "pdca-assistant" "services/ai/Dockerfile" "services/ai/"
build_and_tag "unified-ai" "services/docker-ai-poc/Dockerfile" "services/docker-ai-poc/"

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