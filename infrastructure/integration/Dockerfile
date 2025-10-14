# ============================================================================
# Integrations Container - Production
# ============================================================================
# Contains: GitHub Integration, MCP Server, Partisia Contracts
# Ports: 8087, 8088, 8089
# ============================================================================

FROM python:3.11-slim AS base

LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="External Integrations - GitHub, MCP, Partisia"

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
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Dependencies
# ============================================================================
COPY github-integration/requirements.txt ./github-requirements.txt
COPY mcp-server/requirements.txt ./mcp-requirements.txt
COPY partisia-contracts/requirements.txt ./partisia-requirements.txt

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

[program:github-integration]
command=python3 github-integration/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/github-integration.err.log
stdout_logfile=/var/log/supervisor/github-integration.out.log
environment=PORT=8087,SERVICE_NAME=github-integration

[program:mcp-server]
command=python3 mcp-server/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/mcp-server.err.log
stdout_logfile=/var/log/supervisor/mcp-server.out.log
environment=PORT=8088,SERVICE_NAME=mcp-server

[program:partisia-contracts]
command=python3 partisia-contracts/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/partisia-contracts.err.log
stdout_logfile=/var/log/supervisor/partisia-contracts.out.log
environment=PORT=8089,SERVICE_NAME=partisia-contracts
EOF

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if integration services are responding

# Check GitHub Integration
if ! curl -sf "http://localhost:8087/health" > /dev/null 2>&1; then
    echo "❌ GitHub Integration health check failed"
    exit 1
fi

# Check MCP Server
if ! curl -sf "http://localhost:8088/health" > /dev/null 2>&1; then
    echo "❌ MCP Server health check failed"
    exit 1
fi

# Check Partisia Contracts
if ! curl -sf "http://localhost:8089/health" > /dev/null 2>&1; then
    echo "❌ Partisia Contracts health check failed"
    exit 1
fi

echo "✅ All integration services healthy"
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
EXPOSE 8087 8088 8089

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
