# ============================================================================
# API Gateway Container - Production
# ============================================================================
# Entry point for all API requests
# Port: 8000
# ============================================================================

FROM python:3.11-slim AS base

LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="API Gateway - Entry Point"

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
COPY api-gateway-simple/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Application Code
# ============================================================================
COPY api-gateway-simple/ .

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if API Gateway is responding

if ! curl -sf "http://localhost:8000/health" > /dev/null 2>&1; then
    echo "❌ API Gateway health check failed"
    exit 1
fi

# Check if gateway can reach auth service
if ! curl -sf "http://localhost:8000/api/status" > /dev/null 2>&1; then
    echo "⚠️  Gateway up but may have routing issues"
fi

echo "✅ API Gateway healthy"
exit 0
EOF

RUN chmod +x /app/healthcheck.sh

# ============================================================================
# Non-root User
# ============================================================================
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# ============================================================================
# Port
# ============================================================================
EXPOSE 8000

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["python3", "main.py"]
