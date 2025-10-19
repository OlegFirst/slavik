# Multi-stage Dockerfile for BCM Orchestration Service
# Optimized for production with security hardening

# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (better layer caching)
COPY requirements.txt .

# Install Python dependencies in a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.11-slim

# Metadata
LABEL maintainer="SEH Foundation <noreply@seh-foundation.org>"
LABEL description="BCM Unified Orchestration Service with Platform Integration"
LABEL version="2.0.0"
LABEL iso-compliance="ISO 22301:2019"

# Create non-root user
RUN groupadd -r orchestration && useradd -r -g orchestration -u 1000 orchestration

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=orchestration:orchestration . /app

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R orchestration:orchestration /app/logs /app/data

# Security hardening
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* && \
    chmod -R 755 /app && \
    find /app -type f -name "*.py" -exec chmod 644 {} \;

# Switch to non-root user
USER orchestration

# Expose ports
EXPOSE 8002 9090

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health').read()" || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8002 \
    HOST=0.0.0.0 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "4"]
