# BCM Community Forum Service
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8006

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libmagic1 \
    libmagic-dev \
    file \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Create non-root user
RUN groupadd -r forumuser && useradd -r -g forumuser forumuser

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs temp && \
    chown -R forumuser:forumuser /app

# Switch to non-root user
USER forumuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["python", "-m", "uvicorn", "forum_service:app", "--host", "0.0.0.0", "--port", "8006"]
