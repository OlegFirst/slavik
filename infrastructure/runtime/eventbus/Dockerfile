# ============================================================================
# EventBus Container - Production
# ============================================================================
# Central event-driven messaging service
# Port: 8001
# ============================================================================

FROM python:3.11-slim AS base

LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="EventBus - Central Event Messaging"

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
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Application Code
# ============================================================================
COPY . .

# ============================================================================
# Create data directory
# ============================================================================
RUN mkdir -p /data && chmod 755 /data

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if EventBus is responding

if ! curl -sf "http://localhost:8001/health" > /dev/null 2>&1; then
    echo "❌ EventBus health check failed"
    exit 1
fi

echo "✅ EventBus healthy"
exit 0
EOF

RUN chmod +x /app/healthcheck.sh

# ============================================================================
# Non-root User
# ============================================================================
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /data

USER appuser

# ============================================================================
# Port
# ============================================================================
EXPOSE 8001

# ============================================================================
# Volumes
# ============================================================================
VOLUME ["/data", "/var/log"]

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["python3", "main.py"]
