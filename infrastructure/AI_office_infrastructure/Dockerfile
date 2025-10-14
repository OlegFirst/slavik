# ============================================================================
# AI Office Infrastructure Container - Production
# ============================================================================
# Contains: MIO Manager, Agent Router, Project Agent, DevOps Agent,
#           Analytics Specialist, AI Event Manager
# Ports: 8055-8060
# ============================================================================

FROM python:3.11-slim AS base

LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="AI Office Infrastructure - Internal AI Agents"

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
    git \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Dependencies
# ============================================================================
# Copy all requirements files
COPY ai-event-manager/requirements.txt ./ai-event-manager-requirements.txt
COPY analytics-specialist/requirements.txt ./analytics-specialist-requirements.txt
COPY agent-router/requirements.txt ./agent-router-requirements.txt
COPY project-agent/requirements.txt ./project-agent-requirements.txt
COPY devops-agent/requirements.txt ./devops-agent-requirements.txt
COPY mio-manager/requirements.txt ./mio-manager-requirements.txt

# Merge and install all dependencies
RUN cat *-requirements.txt | sort -u > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Install supervisor
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

[program:ai-event-manager]
command=python3 ai-event-manager/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/ai-event-manager.err.log
stdout_logfile=/var/log/supervisor/ai-event-manager.out.log
environment=PORT=8055,SERVICE_NAME=ai-event-manager

[program:analytics-specialist]
command=python3 analytics-specialist/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/analytics-specialist.err.log
stdout_logfile=/var/log/supervisor/analytics-specialist.out.log
environment=PORT=8056,SERVICE_NAME=analytics-specialist

[program:mio-manager]
command=python3 mio-manager/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/mio-manager.err.log
stdout_logfile=/var/log/supervisor/mio-manager.out.log
environment=PORT=8057,SERVICE_NAME=mio-manager

[program:devops-agent]
command=python3 devops-agent/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/devops-agent.err.log
stdout_logfile=/var/log/supervisor/devops-agent.out.log
environment=PORT=8058,SERVICE_NAME=devops-agent

[program:agent-router]
command=python3 agent-router/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/agent-router.err.log
stdout_logfile=/var/log/supervisor/agent-router.out.log
environment=PORT=8059,SERVICE_NAME=agent-router

[program:project-agent]
command=python3 project-agent/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/project-agent.err.log
stdout_logfile=/var/log/supervisor/project-agent.out.log
environment=PORT=8060,SERVICE_NAME=project-agent
EOF

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if all AI Office services are responding

SERVICES=(
    "8055:/health:ai-event-manager"
    "8056:/health:analytics-specialist"
    "8057:/health:mio-manager"
    "8058:/health:devops-agent"
    "8059:/health:agent-router"
    "8060:/health:project-agent"
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
    echo "⚠️  $FAILED AI Office services unhealthy"
    exit 1
fi

echo "✅ All AI Office services healthy"
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
EXPOSE 8055 8056 8057 8058 8059 8060

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
