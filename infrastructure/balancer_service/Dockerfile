FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy intelligent-core (balancers live here)
COPY ../../intelligent-core /app/intelligent-core

# Copy infrastructure (EventBus lives here)
COPY ../eventbus /app/infrastructure/eventbus
COPY ../AI-office-infrastructure/mio-manager/integrations/resource_tracker_client.py /app/infrastructure/resource_tracker_client.py

# Copy service code
COPY . /app/balancer-service

WORKDIR /app/balancer-service

# Expose Prometheus metrics port
EXPOSE 9091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9091')"

CMD ["python", "main.py"]
