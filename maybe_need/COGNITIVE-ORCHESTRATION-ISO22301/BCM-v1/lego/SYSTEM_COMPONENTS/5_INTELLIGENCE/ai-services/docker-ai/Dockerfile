# Docker AI Proof-of-Concept for BCM Services
FROM python:3.11-slim

# Set Docker AI environment
LABEL ai.docker.service="bcm-ai-unified"
LABEL ai.docker.type="agentic"

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install core dependencies first (Docker AI optimized)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy unified AI service
COPY unified_ai_service.py .

# Docker AI health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8090/health || exit 1

EXPOSE 8090

# Docker AI optimized startup - FIXED PORT
CMD ["python", "-m", "uvicorn", "unified_ai_service:app", "--host", "0.0.0.0", "--port", "8090"]