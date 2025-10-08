#!/bin/bash
# Auto-generated stop script for AI Platform Infrastructure

set -e

LAYER=${1:-full}
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🛑 Stopping AI Platform Infrastructure - Layer: $LAYER"

case $LAYER in
    gateway|runtime|observability|integration|full)
        docker-compose -f "docker-compose.$LAYER.yml" down
        ;;
    all)
        echo "🛑 Stopping all layers..."
        for layer in gateway runtime observability integration full; do
            if [ -f "docker-compose.$layer.yml" ]; then
                docker-compose -f "docker-compose.$layer.yml" down 2>/dev/null || true
            fi
        done
        ;;
    *)
        echo "❌ Unknown layer: $LAYER"
        exit 1
        ;;
esac

echo "✅ Services stopped successfully!"
