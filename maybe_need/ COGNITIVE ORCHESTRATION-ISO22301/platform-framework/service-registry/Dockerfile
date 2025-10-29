FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx \
    websockets

# Copy application
COPY service_registry.py .

# Expose port
EXPOSE 8002

# Run service
CMD ["uvicorn", "service_registry:app", "--host", "0.0.0.0", "--port", "8002"]