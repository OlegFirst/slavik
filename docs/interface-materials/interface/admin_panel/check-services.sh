#!/bin/bash

echo "🔍 Checking BCM Platform Services..."
echo "===================================="

# Function to check if a port is open
check_port() {
    local port=$1
    local name=$2
    local url=$3
    
    if nc -z localhost $port 2>/dev/null; then
        echo "✅ $name - Port $port is OPEN"
        if [ ! -z "$url" ]; then
            echo "   URL: $url"
        fi
    else
        echo "❌ $name - Port $port is CLOSED"
    fi
}

echo ""
echo "Core BCM Services:"
check_port 8069 "Odoo BCM Core" "http://localhost:8069"
check_port 8000 "AI Orchestrator" "http://localhost:8000"
check_port 5432 "PostgreSQL" ""
check_port 6379 "Redis" ""

echo ""
echo "AI Services:"
check_port 8082 "BIA Engine" "http://localhost:8082"
check_port 8083 "Document Processor" "http://localhost:8083"
check_port 8001 "EventBus" "http://localhost:8001"

echo ""
echo "Monitoring Stack:"
check_port 3000 "Grafana" "http://localhost:3000"
check_port 9090 "Prometheus" "http://localhost:9090"
check_port 9093 "AlertManager" "http://localhost:9093"

echo ""
echo "Additional Services:"
check_port 8084 "Community Service" "http://localhost:8084"
check_port 8085 "Digital Twin" "http://localhost:8085"
check_port 8080 "Keycloak" "http://localhost:8080"

echo ""
echo "🎛️ Admin Panel will run on:"
echo "   http://localhost:3001"
echo ""
