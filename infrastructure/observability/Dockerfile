# ============================================================================
# Observability Container - Production
# ============================================================================
# Contains: Prometheus, Monitoring Backend, Service Catalog
# Ports: 9090, 8050, 8052
# ============================================================================

FROM python:3.11-slim AS base

LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="Observability - Prometheus & Monitoring"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# ============================================================================
# System Dependencies
# ============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Install Prometheus
# ============================================================================
ARG PROMETHEUS_VERSION=2.47.0
RUN wget -q https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz && \
    tar xzf prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz && \
    mv prometheus-${PROMETHEUS_VERSION}.linux-amd64 /prometheus && \
    rm prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz

# ============================================================================
# Python Dependencies
# ============================================================================
COPY monitoring-backend/requirements.txt ./monitoring-requirements.txt
COPY service-catalog/requirements.txt ./catalog-requirements.txt

RUN cat *-requirements.txt | sort -u > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Install supervisor
RUN pip install supervisor

# ============================================================================
# Application Code
# ============================================================================
COPY . .

# ============================================================================
# Prometheus Configuration
# ============================================================================
RUN mkdir -p /prometheus-data /etc/prometheus

COPY <<EOF /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'bcm-platform'
    environment: 'production'

scrape_configs:
  # Platform Services
  - job_name: 'platform-services'
    static_configs:
      - targets: ['platform-services:8012', 'platform-services:8026']
    metrics_path: '/metrics'

  # Intelligent Core
  - job_name: 'intelligent-core'
    static_configs:
      - targets: ['intelligent-core:8002', 'intelligent-core:8028']
    metrics_path: '/metrics'

  # Infrastructure
  - job_name: 'infrastructure'
    static_configs:
      - targets: ['eventbus:8001', 'gateway:8000']
    metrics_path: '/metrics'

  # AI Office
  - job_name: 'ai-office'
    static_configs:
      - targets: ['ai-office:8057', 'ai-office:8056']
    metrics_path: '/metrics'

  # Monitoring itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files: []
EOF

# ============================================================================
# Supervisor Configuration
# ============================================================================
RUN mkdir -p /var/log/supervisor /var/run/supervisor

COPY <<EOF /etc/supervisord.conf
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisor/supervisord.pid

[program:prometheus]
command=/prometheus/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus-data --web.listen-address=:9090
directory=/prometheus
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/prometheus.err.log
stdout_logfile=/var/log/supervisor/prometheus.out.log

[program:monitoring-backend]
command=python3 monitoring-backend/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/monitoring-backend.err.log
stdout_logfile=/var/log/supervisor/monitoring-backend.out.log
environment=PORT=8050,SERVICE_NAME=monitoring-backend

[program:service-catalog]
command=python3 service-catalog/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/service-catalog.err.log
stdout_logfile=/var/log/supervisor/service-catalog.out.log
environment=PORT=8052,SERVICE_NAME=service-catalog
EOF

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if all monitoring services are responding

# Check Prometheus
if ! curl -sf "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
    echo "❌ Prometheus health check failed"
    exit 1
fi

# Check Monitoring Backend
if ! curl -sf "http://localhost:8050/health" > /dev/null 2>&1; then
    echo "❌ Monitoring Backend health check failed"
    exit 1
fi

# Check Service Catalog
if ! curl -sf "http://localhost:8052/health" > /dev/null 2>&1; then
    echo "❌ Service Catalog health check failed"
    exit 1
fi

echo "✅ All monitoring services healthy"
exit 0
EOF

RUN chmod +x /app/healthcheck.sh

# ============================================================================
# Non-root User
# ============================================================================
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /prometheus-data /var/log/supervisor /var/run/supervisor && \
    chown -R appuser:appuser /prometheus /etc/prometheus

USER appuser

# ============================================================================
# Ports
# ============================================================================
EXPOSE 9090 8050 8052

# ============================================================================
# Volumes
# ============================================================================
VOLUME ["/prometheus-data", "/var/log"]

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
