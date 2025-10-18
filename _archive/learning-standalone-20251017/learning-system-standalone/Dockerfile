FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared libraries
COPY ../shared /app/shared

# Copy application
COPY . .

# Expose port
EXPOSE 8033

# Run application
CMD ["python", "main.py"]
