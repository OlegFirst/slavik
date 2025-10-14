FROM python:3.11-alpine

# Security: Create non-root user
RUN addgroup -g 1001 -S apiuser && \
    adduser -S -D -H -u 1001 -s /sbin/nologin -G apiuser apiuser

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY module_validator_api.py .

# Create necessary directories
RUN mkdir -p /app/logs && \
    chown -R apiuser:apiuser /app

# Switch to non-root user
USER apiuser

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/api/modules/list').raise_for_status()" || exit 1

# Start application
CMD ["python", "module_validator_api.py"]