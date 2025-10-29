FROM python:3.9-slim

WORKDIR /app

# Install dependencies if requirements.txt exists
RUN pip install --no-cache-dir fastapi uvicorn pydantic redis

COPY . .

EXPOSE 8093

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8093"]