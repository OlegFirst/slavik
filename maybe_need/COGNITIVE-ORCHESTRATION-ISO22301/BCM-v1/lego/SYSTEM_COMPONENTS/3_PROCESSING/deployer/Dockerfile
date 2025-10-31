FROM python:3.11-slim
WORKDIR /app

# Установка Docker CLI для управления контейнерами
RUN apt-get update && apt-get install -y \
    docker.io \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8002

CMD ["python", "main.py"]