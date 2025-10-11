# Message Queue Service - Async message broker
# Port: 8061
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV MESSAGE_QUEUE_PORT=8061
ENV MESSAGE_QUEUE_HOST=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8061/health || exit 1

# Expose port
EXPOSE 8061

# Run the service
CMD ["python", "main.py"]
