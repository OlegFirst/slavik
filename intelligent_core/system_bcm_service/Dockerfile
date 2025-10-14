FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY main.py .

# Copy BCM modules from learning-knowledge
COPY ../ai-foundation/learning-knowledge/system_bcm /app/system_bcm
COPY ../ai-foundation/learning-knowledge/learning /app/learning
COPY ../ai-foundation/learning-knowledge/scenarios /app/scenarios

# Create log directory
RUN mkdir -p /var/log

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8050/health')"

# Run service
CMD ["python", "main.py"]
