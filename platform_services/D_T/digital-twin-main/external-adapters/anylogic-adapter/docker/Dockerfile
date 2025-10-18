FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ../api_server/ ./api_server/
COPY ../anylogic-model/python_scripts/ ./python_scripts/

# Expose port
EXPOSE 7004

# Run the application
CMD ["python", "-m", "uvicorn", "api_server.app:app", "--host", "0.0.0.0", "--port", "7004"]