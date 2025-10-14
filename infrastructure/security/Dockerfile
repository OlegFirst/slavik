# ============================================================================
# Security Container - Production
# ============================================================================
# Contains: Auth Service, Secrets Manager
# Ports: 8081, 8084
# ============================================================================

FROM python:3.11-slim AS base

LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="Security Services - Auth & Secrets"

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
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Dependencies
# ============================================================================
COPY auth/requirements.txt ./auth-requirements.txt
COPY secrets-manager/requirements.txt ./secrets-requirements.txt

RUN cat *-requirements.txt | sort -u > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Install supervisor
RUN pip install supervisor

# ============================================================================
# Application Code
# ============================================================================
COPY . .

# ============================================================================
# Create secrets directory
# ============================================================================
RUN mkdir -p /secrets && chmod 700 /secrets

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

[program:auth-service]
command=python3 auth/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/auth-service.err.log
stdout_logfile=/var/log/supervisor/auth-service.out.log
environment=PORT=8081,SERVICE_NAME=auth-service

[program:secrets-manager]
command=python3 secrets-manager/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/secrets-manager.err.log
stdout_logfile=/var/log/supervisor/secrets-manager.out.log
environment=PORT=8084,SERVICE_NAME=secrets-manager,SECRETS_PATH=/secrets
EOF

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if security services are responding

# Check Auth Service
if ! curl -sf "http://localhost:8081/health" > /dev/null 2>&1; then
    echo "❌ Auth Service health check failed"
    exit 1
fi

# Check Secrets Manager
if ! curl -sf "http://localhost:8084/health" > /dev/null 2>&1; then
    echo "❌ Secrets Manager health check failed"
    exit 1
fi

echo "✅ All security services healthy"
exit 0
EOF

RUN chmod +x /app/healthcheck.sh

# ============================================================================
# Non-root User
# ============================================================================
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /secrets /var/log/supervisor /var/run/supervisor

USER appuser

# ============================================================================
# Ports
# ============================================================================
EXPOSE 8081 8084

# ============================================================================
# Volumes
# ============================================================================
VOLUME ["/secrets", "/var/log"]

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
