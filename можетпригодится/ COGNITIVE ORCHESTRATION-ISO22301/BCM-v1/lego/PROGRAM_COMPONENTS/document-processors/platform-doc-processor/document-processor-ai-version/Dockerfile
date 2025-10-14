# BCM Document Processor Dockerfile
FROM python:3.11-slim

LABEL maintainer="BCM Platform Team"
LABEL description="AI-powered document processor for BCM Platform"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Document processing dependencies
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libreoffice \
    antiword \
    unrtf \
    # Image processing
    libgl1-mesa-glx \
    libglib2.0-0 \
    # General utilities
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy language model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY document_processor.py .
COPY models/ ./models/
COPY templates/ ./templates/

# Create directories
RUN mkdir -p /app/{uploads,processed,models,logs}

# Non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 docprocessor
RUN chown -R docprocessor:docprocessor /app
USER docprocessor

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

# Expose port
EXPOSE 8002

# Environment variables
ENV PYTHONPATH=/app
ENV UPLOAD_DIR=/app/uploads
ENV PROCESSED_DIR=/app/processed
ENV MODEL_DIR=/app/models

# Run the document processor
CMD ["python", "document_processor.py"]
