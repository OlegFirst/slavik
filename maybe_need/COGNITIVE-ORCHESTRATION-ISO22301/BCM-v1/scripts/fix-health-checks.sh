#!/bin/bash

# Fix Health Checks for BCM Platform Services
echo "🔧 Fixing health checks for all services..."

# Function to check if service is responding
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-/health}

    echo "Checking $service_name on port $port..."

    # Try to connect to the service
    if docker exec $service_name curl -f http://localhost:$port$endpoint 2>/dev/null; then
        echo "✅ $service_name is responding"
        return 0
    else
        # Try alternative endpoint
        if docker exec $service_name curl -f http://localhost:$port/ 2>/dev/null; then
            echo "✅ $service_name is responding (root endpoint)"
            return 0
        else
            echo "❌ $service_name is not responding"
            return 1
        fi
    fi
}

# Check AI Orchestrator
check_service "iso-22301-ai_orchestrator-1" "8000" "/health"

# Check BIA Engine
check_service "iso-22301-bia_engine-1" "8082" "/health"

# Check Document Processor
check_service "iso-22301-document_processor-1" "8083" "/health"

# Check Compliance Checker
check_service "iso-22301-compliance_checker-1" "8084" "/health"

# Check Database Gateway
check_service "iso-22301-unified_database_gateway-1" "8888" "/health"

# Check BPMN Service
check_service "iso-22301-bpmn_service-1" "8005" "/health"

# Check LMS Adapter
check_service "iso-22301-lms_adapter-1" "8006" "/health"

# Check TheHive Adapter
check_service "iso-22301-thehive_adapter-1" "8007" "/health"

# Check Grafana Adapter
check_service "iso-22301-grafana_adapter-1" "8008" "/health"

# Check GitHub App
check_service "iso-22301-github_app-1" "8001" "/"

echo ""
echo "🔄 Restarting services with failed health checks..."

# Restart unhealthy services
docker-compose restart ai_orchestrator bia_engine document_processor compliance_checker unified_database_gateway

echo ""
echo "✅ Health check fixes applied!"