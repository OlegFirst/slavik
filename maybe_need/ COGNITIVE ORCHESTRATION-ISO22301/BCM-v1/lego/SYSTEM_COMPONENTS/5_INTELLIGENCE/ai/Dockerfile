FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn httpx pydantic redis

# Copy PDCA Assistant
COPY pdca_assistant.py .

EXPOSE 8010

CMD ["python", "pdca_assistant.py"]