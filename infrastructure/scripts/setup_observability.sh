#!/bin/bash

# Full observability stack setup for AI Platform
# Интегрирует с tools для автоматического discovery сервисов

set -e

echo "📊 Setting up Observability Stack"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

cd infrastructure/observability

# Step 1: Create bcm-network if not exists
echo -e "${BLUE}[1/8]${NC} Creating Docker networks..."
docker network create bcm-network 2>/dev/null || echo "  bcm-network already exists"
docker network create monitoring-network 2>/dev/null || echo "  monitoring-network already exists"
echo -e "${GREEN}✅${NC} Networks ready"

# Step 2: Create necessary directories
echo -e "${BLUE}[2/8]${NC} Creating directories..."
mkdir -p config/prometheus/sd_configs
mkdir -p config/grafana/dashboards
mkdir -p config/alertmanager/templates
mkdir -p logs/prometheus
mkdir -p logs/grafana
mkdir -p logs/loki
echo -e "${GREEN}✅${NC} Directories created"

# Step 3: Generate service discovery configs using tools
echo -e "${BLUE}[3/8]${NC} Generating service discovery configs..."

# Use module_scanner to discover services
if [ -f "../../tools/analyzers/module_scanner.py" ]; then
    python3 ../../tools/analyzers/module_scanner.py \
        ../../intelligent-core/ai-foundation \
        ../../intelligent-core/workflow_intelligence \
        ../../intelligent-core/expertise-center \
        > config/prometheus/sd_configs/core_modules.json 2>/dev/null || true
fi

# Create service discovery for 3 core modules
cat > config/prometheus/sd_configs/core_modules_static.json << 'EOF'
[
  {
    "targets": ["localhost:9001"],
    "labels": {
      "job": "ai-foundation",
      "service": "ai-foundation",
      "tier": "core",
      "component": "rag-ml-learning"
    }
  },
  {
    "targets": ["localhost:9002"],
    "labels": {
      "job": "workflow-intelligence",
      "service": "workflow-intelligence",
      "tier": "core",
      "component": "orchestration"
    }
  },
  {
    "targets": ["localhost:9003"],
    "labels": {
      "job": "expertise-center",
      "service": "expertise-center",
      "tier": "core",
      "component": "domain-experts"
    }
  }
]
EOF

echo -e "${GREEN}✅${NC} Service discovery configs generated"

# Step 4: Update Prometheus config to include SD
echo -e "${BLUE}[4/8]${NC} Updating Prometheus configuration..."

# Backup existing config
cp config/prometheus/prometheus.yml config/prometheus/prometheus.yml.backup 2>/dev/null || true

# Add file_sd_configs to prometheus.yml if not exists
cat >> config/prometheus/prometheus.yml << 'EOF'

  # Auto-discovered core modules
  - job_name: 'core-modules'
    file_sd_configs:
      - files:
          - '/etc/prometheus/sd_configs/core_modules_static.json'
        refresh_interval: 30s
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
EOF

echo -e "${GREEN}✅${NC} Prometheus config updated"

# Step 5: Create alert rules for core modules
echo -e "${BLUE}[5/8]${NC} Creating alert rules..."

cat > config/prometheus/rules/core_modules.yml << 'EOF'
groups:
  - name: core_modules
    interval: 30s
    rules:
      # ai-foundation alerts
      - alert: AIFoundationDown
        expr: up{job="ai-foundation"} == 0
        for: 2m
        labels:
          severity: critical
          component: ai-foundation
        annotations:
          summary: "AI Foundation service is down"
          description: "AI Foundation (RAG/ML/Learning) has been down for 2 minutes"

      - alert: AIFoundationHighLatency
        expr: http_request_duration_seconds{job="ai-foundation",quantile="0.95"} > 5
        for: 5m
        labels:
          severity: warning
          component: ai-foundation
        annotations:
          summary: "AI Foundation high latency"
          description: "95th percentile latency is {{ $value }}s"

      # workflow-intelligence alerts
      - alert: WorkflowEngineDown
        expr: up{job="workflow-intelligence"} == 0
        for: 2m
        labels:
          severity: critical
          component: workflow-intelligence
        annotations:
          summary: "Workflow Intelligence engine is down"
          description: "Workflow orchestration engine has been down for 2 minutes"

      - alert: WorkflowExecutionFailed
        expr: rate(workflow_executions_failed_total{job="workflow-intelligence"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
          component: workflow-intelligence
        annotations:
          summary: "High workflow failure rate"
          description: "Workflow failure rate: {{ $value | humanizePercentage }}"

      # expertise-center alerts
      - alert: ExpertiseCenterDown
        expr: up{job="expertise-center"} == 0
        for: 2m
        labels:
          severity: critical
          component: expertise-center
        annotations:
          summary: "Expertise Center is down"
          description: "Domain experts service has been down for 2 minutes"

      - alert: ExpertResponseSlow
        expr: avg(expert_query_duration_seconds{job="expertise-center"}) > 10
        for: 5m
        labels:
          severity: warning
          component: expertise-center
        annotations:
          summary: "Expert responses are slow"
          description: "Average response time: {{ $value }}s"

      # Cross-module integration alerts
      - alert: CoreModulesCommunicationFailure
        expr: sum(rate(http_requests_failed_total{job=~"ai-foundation|workflow-intelligence|expertise-center"}[5m])) > 10
        for: 3m
        labels:
          severity: critical
          component: integration
        annotations:
          summary: "Core modules communication failure"
          description: "High rate of failed requests between core modules"
EOF

echo -e "${GREEN}✅${NC} Alert rules created"

# Step 6: Create Grafana dashboards for core modules
echo -e "${BLUE}[6/8]${NC} Creating Grafana dashboards..."

# ai-foundation dashboard
cat > config/grafana/dashboards/ai-foundation.json << 'EOF'
{
  "dashboard": {
    "title": "AI Foundation Monitoring",
    "tags": ["ai-foundation", "rag", "ml", "learning"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Service Status",
        "type": "stat",
        "targets": [{
          "expr": "up{job=\"ai-foundation\"}",
          "refId": "A"
        }]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [{
          "expr": "rate(http_requests_total{job=\"ai-foundation\"}[5m])",
          "legendFormat": "{{method}} {{endpoint}}",
          "refId": "A"
        }]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=\"ai-foundation\"}[5m]))",
          "legendFormat": "{{endpoint}}",
          "refId": "A"
        }]
      },
      {
        "title": "RAG Query Performance",
        "type": "graph",
        "targets": [{
          "expr": "rate(rag_queries_total{job=\"ai-foundation\"}[5m])",
          "legendFormat": "{{collection}}",
          "refId": "A"
        }]
      },
      {
        "title": "LLM API Calls",
        "type": "graph",
        "targets": [{
          "expr": "rate(llm_api_calls_total{job=\"ai-foundation\"}[5m])",
          "legendFormat": "{{provider}} {{model}}",
          "refId": "A"
        }]
      },
      {
        "title": "Learning Events",
        "type": "graph",
        "targets": [{
          "expr": "rate(learning_events_total{job=\"ai-foundation\"}[5m])",
          "legendFormat": "{{event_type}}",
          "refId": "A"
        }]
      }
    ]
  }
}
EOF

echo -e "${GREEN}✅${NC} Dashboards created"

# Step 7: Start observability stack
echo -e "${BLUE}[7/8]${NC} Starting observability stack..."

docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services
echo "  Waiting for services to start..."
sleep 15

echo -e "${GREEN}✅${NC} Observability stack started"

# Step 8: Verify all services
echo -e "${BLUE}[8/8]${NC} Verifying services..."

services=(
    "prometheus:9090"
    "grafana:3000"
    "alertmanager:9093"
    "node-exporter:9100"
    "cadvisor:8080"
    "loki:3100"
)

all_healthy=true

for service_port in "${services[@]}"; do
    service=$(echo $service_port | cut -d: -f1)
    port=$(echo $service_port | cut -d: -f2)

    echo -n "  $service ($port): "

    if curl -s http://localhost:$port/metrics > /dev/null 2>&1 || \
       curl -s http://localhost:$port/api/health > /dev/null 2>&1 || \
       curl -s http://localhost:$port/ready > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${YELLOW}⚠️  Starting...${NC}"
        all_healthy=false
    fi
done

echo ""
echo "=========================================="

if $all_healthy; then
    echo -e "${GREEN}✅ Observability stack is fully operational!${NC}"
else
    echo -e "${YELLOW}⚠️  Some services are still starting. Please wait 30s and check again.${NC}"
fi

echo ""
echo "📊 Access Points:"
echo "  Prometheus:   http://localhost:9090"
echo "  Grafana:      http://localhost:3000 (admin/admin123)"
echo "  AlertManager: http://localhost:9093"
echo "  Loki:         http://localhost:3100"
echo ""
echo "📝 Logs:"
echo "  docker-compose -f docker-compose.monitoring.yml logs -f"
echo ""
echo "🔍 Next steps:"
echo "  1. Open Grafana: http://localhost:3000"
echo "  2. Import dashboards from config/grafana/dashboards/"
echo "  3. Start core modules and watch metrics appear"
echo ""
echo "Configuration files:"
echo "  Prometheus:   config/prometheus/prometheus.yml"
echo "  Alert rules:  config/prometheus/rules/"
echo "  Grafana:      config/grafana/"
echo "  Service discovery: config/prometheus/sd_configs/"
