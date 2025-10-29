#!/bin/bash

# Setup Grafana Dashboards for BCM Platform

echo "🔧 Setting up Grafana dashboards..."

GRAFANA_URL="http://localhost:3003"
GRAFANA_USER="admin"
GRAFANA_PASS="admin"

# Wait for Grafana to be ready
echo "⏳ Waiting for Grafana to be ready..."
sleep 5

# Create BCM datasource (if needed)
echo "📊 Creating BCM datasource..."
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -d '{
    "name": "BCM Platform",
    "type": "prometheus",
    "url": "http://localhost:9090",
    "access": "proxy",
    "isDefault": true
  }' \
  "${GRAFANA_URL}/api/datasources" 2>/dev/null || echo "⚠️ Datasource may already exist"

# Import BCM Overview Dashboard
echo "📈 Importing BCM Overview Dashboard..."
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -d @/Users/MD/ISO-22301/monitoring/grafana-bcm-dashboard.json \
  "${GRAFANA_URL}/api/dashboards/db" 2>/dev/null

# Import Services Dashboard
echo "🔧 Importing Services Dashboard..."
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -d @/Users/MD/ISO-22301/monitoring/grafana-services-dashboard.json \
  "${GRAFANA_URL}/api/dashboards/db" 2>/dev/null

# Import Performance Dashboard
echo "⚡ Importing Performance Dashboard..."
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${GRAFANA_USER}:${GRAFANA_PASS}" \
  -d @/Users/MD/ISO-22301/monitoring/grafana-performance-dashboard.json \
  "${GRAFANA_URL}/api/dashboards/db" 2>/dev/null

echo "✅ Grafana dashboards setup complete!"
echo "🌐 Access Grafana at: ${GRAFANA_URL}"
echo "🔐 Login: ${GRAFANA_USER} / ${GRAFANA_PASS}"
echo ""
echo "📊 Available Dashboards:"
echo "  - BCM Platform Overview"
echo "  - BCM Services Monitoring"
echo "  - BCM Performance Metrics"