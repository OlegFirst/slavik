# Multi-stage build for Decision Center API
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# Final stage
# ============================================
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r decision && useradd -r -g decision decision

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/decision/.local

# Copy application code
COPY . /app/

# Copy infrastructure modules (needed by Decision Center)
COPY ../policy_engine /app/infrastructure/policy_engine/
COPY ../decision_center/integrations /app/infrastructure/decision_center/integrations/
COPY ../eventbus /app/infrastructure/eventbus/

# Set Python path
ENV PYTHONPATH=/app
ENV PATH=/home/decision/.local/bin:$PATH

# Change ownership
RUN chown -R decision:decision /app

# Switch to non-root user
USER decision

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
