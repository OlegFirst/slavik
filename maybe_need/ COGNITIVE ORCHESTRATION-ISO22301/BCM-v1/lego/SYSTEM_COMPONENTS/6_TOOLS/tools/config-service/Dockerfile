FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pyyaml \
    aioredis \
    httpx \
    cryptography

# Copy application
COPY config_service.py .

# Create config directory
RUN mkdir -p /tmp/bcm_configs

# Expose port
EXPOSE 8888

# Run service
CMD ["uvicorn", "config_service:app", "--host", "0.0.0.0", "--port", "8888"]