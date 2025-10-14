# ============================================================================
# Runtime Services Container - Production
# ============================================================================
# Contains: Realtime WebSocket, Message Queue, Service Discovery
# Ports: 8082, 8085, 8086
# ============================================================================

FROM python:3.11-slim AS base

LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="Runtime Services - WebSocket, Queue, Discovery"

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
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Python Dependencies
# ============================================================================
COPY realtime-websocket/requirements.txt ./websocket-requirements.txt
COPY message-queue/requirements.txt ./queue-requirements.txt
COPY service-discovery/requirements.txt ./discovery-requirements.txt

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

[program:realtime-websocket]
command=python3 realtime-websocket/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/realtime-websocket.err.log
stdout_logfile=/var/log/supervisor/realtime-websocket.out.log
environment=PORT=8082,SERVICE_NAME=realtime-websocket

[program:message-queue]
command=python3 message-queue/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/message-queue.err.log
stdout_logfile=/var/log/supervisor/message-queue.out.log
environment=PORT=8085,SERVICE_NAME=message-queue

[program:service-discovery]
command=python3 service-discovery/main.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/service-discovery.err.log
stdout_logfile=/var/log/supervisor/service-discovery.out.log
environment=PORT=8086,SERVICE_NAME=service-discovery
EOF

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if runtime services are responding

# Check Realtime WebSocket
if ! curl -sf "http://localhost:8082/health" > /dev/null 2>&1; then
    echo "❌ Realtime WebSocket health check failed"
    exit 1
fi

# Check Message Queue
if ! curl -sf "http://localhost:8085/health" > /dev/null 2>&1; then
    echo "❌ Message Queue health check failed"
    exit 1
fi

# Check Service Discovery
if ! curl -sf "http://localhost:8086/health" > /dev/null 2>&1; then
    echo "❌ Service Discovery health check failed"
    exit 1
fi

echo "✅ All runtime services healthy"
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
EXPOSE 8082 8085 8086

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
