# Dockerfile for Consolidated Cognitive Orchestration System
# Multi-stage build for production-ready hybrid Python + JavaScript architecture

# ===== STAGE 1: Node.js base for JavaScript orchestrators =====
FROM node:18-alpine AS nodejs-base

WORKDIR /app/orchestrators

# Copy JavaScript orchestrators
COPY ../ORCHESTRATORS/ ./
COPY ../SYSTEM_COMPONENTS/ ../SYSTEM_COMPONENTS/
COPY ../BRIDGE_LAYER/ ../BRIDGE_LAYER/
COPY ../PROGRAM_COMPONENTS_NEW/ ../PROGRAM_COMPONENTS_NEW/
COPY ../CLIENT_INFRASTRUCTURE/ ../CLIENT_INFRASTRUCTURE/

# Install Node.js dependencies if package.json exists
RUN if [ -f package.json ]; then npm install --production; fi

# ===== STAGE 2: Python base with FastAPI =====
FROM python:3.11-slim AS python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash cognitiveuser
USER cognitiveuser
WORKDIR /home/cognitiveuser/app

# Copy requirements and install Python dependencies
COPY --chown=cognitiveuser:cognitiveuser requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Add user's pip bin to PATH
ENV PATH="/home/cognitiveuser/.local/bin:$PATH"

# ===== STAGE 3: Final production image =====
FROM python-base AS production

# Copy JavaScript orchestrators from nodejs-base
COPY --from=nodejs-base --chown=cognitiveuser:cognitiveuser /app/orchestrators/ ./orchestrators/

# Copy Python application code
COPY --chown=cognitiveuser:cognitiveuser main.py .
COPY --chown=cognitiveuser:cognitiveuser models.py .
COPY --chown=cognitiveuser:cognitiveuser orchestrators.py .
COPY --chown=cognitiveuser:cognitiveuser integrations.py .

# Create necessary directories
RUN mkdir -p logs temp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/health || exit 1

# Expose port
EXPOSE 8000

# Set default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# ===== STAGE 4: Development image =====
FROM production AS development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Switch back to application user
USER cognitiveuser

# Install development Python packages
RUN pip install --user \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy \
    ipython

# Override command for development (with reload)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]