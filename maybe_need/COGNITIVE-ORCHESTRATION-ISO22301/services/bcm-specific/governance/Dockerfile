FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including gcc for psutil
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory and non-root user
RUN mkdir -p /app/data && \
    useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8009

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8009/health').raise_for_status()"

# Run the application
CMD ["python", "governance_service.py"]