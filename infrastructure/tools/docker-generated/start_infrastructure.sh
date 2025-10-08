#!/bin/bash
# Auto-generated startup script for AI Platform Infrastructure
# Usage: ./start_infrastructure.sh [layer]
#   layer: gateway|runtime|observability|integration|full

set -e

LAYER=${1:-full}
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 Starting AI Platform Infrastructure - Layer: $LAYER"
echo ""

# Check if .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "⚠️  .env file not found. Copying from template..."
    cp "$SCRIPT_DIR/.env.template" "$SCRIPT_DIR/.env"
    echo "⚠️  Please edit .env and set your actual values!"
    exit 1
fi

# Start the appropriate layer
case $LAYER in
    gateway)
        echo "📡 Starting Gateway layer..."
        docker-compose -f docker-compose.gateway.yml up -d
        ;;
    runtime)
        echo "⚡ Starting Runtime layer..."
        docker-compose -f docker-compose.runtime.yml up -d
        ;;
    observability)
        echo "👁️  Starting Observability layer..."
        docker-compose -f docker-compose.observability.yml up -d
        ;;
    integration)
        echo "🔗 Starting Integration layer..."
        docker-compose -f docker-compose.integration.yml up -d
        ;;
    full)
        echo "🌟 Starting all services..."
        docker-compose -f docker-compose.full.yml up -d
        ;;
    *)
        echo "❌ Unknown layer: $LAYER"
        echo "Valid layers: gateway, runtime, observability, integration, full"
        exit 1
        ;;
esac

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📊 Check status: docker-compose -f docker-compose.$LAYER.yml ps"
echo "📋 View logs: docker-compose -f docker-compose.$LAYER.yml logs -f"
echo "🛑 Stop services: ./stop_infrastructure.sh $LAYER"
