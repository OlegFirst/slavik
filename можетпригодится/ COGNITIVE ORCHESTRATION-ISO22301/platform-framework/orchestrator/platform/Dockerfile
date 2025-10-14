FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    docker.io \
    docker-compose \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    REDIS_HOST=redis \
    POSTGRES_HOST=postgres \
    POSTGRES_USER=odoo \
    POSTGRES_PASSWORD=postgres123 \
    POSTGRES_DB=bcm_platform

# Run the orchestrator
CMD ["python", "main.py"]