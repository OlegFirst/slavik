# Analytics Specialist AI - Dockerfile
# ==================================

FROM python:3.11-slim

LABEL maintainer="AI Platform ISO"
LABEL service="analytics-specialist"
LABEL version="1.0.0"
LABEL description="Platform Intelligence Expert - AI Colleague #6"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 analytics && \
    chown -R analytics:analytics /app

USER analytics

# Environment variables (can be overridden)
ENV PORT=8051
ENV HOST=0.0.0.0
ENV COMPETENCY_LEVEL=junior
ENV DEBUG=false

# Expose port
EXPOSE 8051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8051/health')" || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8051"]
