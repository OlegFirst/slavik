#!/bin/bash
# Health check script for all services

echo "🏥 Checking service health..."
echo ""

docker-compose -f docker-compose.full.yml ps

echo ""
echo "Detailed health checks:"
echo ""

for container in $(docker-compose -f docker-compose.full.yml ps -q); do
    name=$(docker inspect --format='{{.Name}}' $container | sed 's/^\///')
    health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no healthcheck")
    status=$(docker inspect --format='{{.State.Status}}' $container)

    if [ "$status" = "running" ]; then
        if [ "$health" = "healthy" ]; then
            echo "✅ $name - $status ($health)"
        elif [ "$health" = "no healthcheck" ]; then
            echo "⚪ $name - $status (no healthcheck)"
        else
            echo "⚠️  $name - $status ($health)"
        fi
    else
        echo "❌ $name - $status"
    fi
done
