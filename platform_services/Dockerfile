# ============================================================================
# Platform Services Container
# ============================================================================
# Contains: BIA, Risk, Compliance, Governance, Planning, Plans, Response,
#           Learning, Documents services
# Ports: 8011-8027
# ============================================================================

FROM python:3.11-slim AS base

# Metadata
LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="BCM Platform Services - All business logic services"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ============================================================================
# System Dependencies
# ============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Dependencies
# ============================================================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install supervisor for multi-service management
RUN pip install supervisor

# ============================================================================
# Application Code
# ============================================================================
COPY . .

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

[program:bia-service]
command=python3 bia-service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/bia-service.err.log
stdout_logfile=/var/log/supervisor/bia-service.out.log
environment=PORT=8012,SERVICE_NAME=bia-service

[program:risk-service]
command=python3 risk-service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/risk-service.err.log
stdout_logfile=/var/log/supervisor/risk-service.out.log
environment=PORT=8026,SERVICE_NAME=risk-service

[program:compliance-service]
command=python3 compliance-service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/compliance-service.err.log
stdout_logfile=/var/log/supervisor/compliance-service.out.log
environment=PORT=8014,SERVICE_NAME=compliance-service

[program:governance-service]
command=python3 governance-service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/governance-service.err.log
stdout_logfile=/var/log/supervisor/governance-service.out.log
environment=PORT=8025,SERVICE_NAME=governance-service

[program:planning-service]
command=python3 planning_service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/planning-service.err.log
stdout_logfile=/var/log/supervisor/planning-service.out.log
environment=PORT=8011,SERVICE_NAME=planning-service

[program:plans-service]
command=python3 plans_service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/plans-service.err.log
stdout_logfile=/var/log/supervisor/plans-service.out.log
environment=PORT=8023,SERVICE_NAME=plans-service

[program:response-service]
command=python3 response-service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/response-service.err.log
stdout_logfile=/var/log/supervisor/response-service.out.log
environment=PORT=8027,SERVICE_NAME=response-service

[program:learning-service]
command=python3 learning-service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/learning-service.err.log
stdout_logfile=/var/log/supervisor/learning-service.out.log
environment=PORT=8021,SERVICE_NAME=learning-service

[program:documents-service]
command=python3 documents-service/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/documents-service.err.log
stdout_logfile=/var/log/supervisor/documents-service.out.log
environment=PORT=8022,SERVICE_NAME=documents-service
EOF

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if all services are responding

SERVICES=(
    "8012:/health:bia-service"
    "8026:/health:risk-service"
    "8014:/health:compliance-service"
    "8025:/health:governance-service"
    "8011:/health:planning-service"
    "8023:/health:plans-service"
    "8027:/health:response-service"
    "8021:/health:learning-service"
    "8022:/health:documents-service"
)

FAILED=0

for service in "${SERVICES[@]}"; do
    IFS=':' read -r port path name <<< "$service"
    if ! curl -sf "http://localhost:${port}${path}" > /dev/null 2>&1; then
        echo "❌ $name (port $port) health check failed"
        FAILED=$((FAILED + 1))
    fi
done

if [ $FAILED -gt 0 ]; then
    echo "⚠️  $FAILED services unhealthy"
    exit 1
fi

echo "✅ All services healthy"
exit 0
EOF

RUN chmod +x /app/healthcheck.sh

# ============================================================================
# Non-root User
# ============================================================================
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /var/log/supervisor /var/run/supervisor

USER appuser

# ============================================================================
# Ports
# ============================================================================
EXPOSE 8011 8012 8013 8014 8015 8016 8017 8018 8019 8020 8021 8022 8023 8024 8025 8026 8027

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
