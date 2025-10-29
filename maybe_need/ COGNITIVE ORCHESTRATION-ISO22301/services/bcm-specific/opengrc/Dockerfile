FROM python:3.11-slim

WORKDIR /app

# Install basic dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    psycopg2-binary \
    redis

# Create a simple API server for OpenGRC OSCAL integration
RUN cat > main.py << 'EOF'
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "OpenGRC OSCAL Integration"}

@app.get("/")
def root():
    return {"message": "OpenGRC OSCAL Integration Service", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

EXPOSE 8000

CMD ["python", "main.py"]