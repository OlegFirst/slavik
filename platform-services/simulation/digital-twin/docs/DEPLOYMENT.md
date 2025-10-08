# 🚀 Digital Twin Service - Deployment Guide

**Дата:** 2025-10-01
**Статус:** ✅ Production Ready

---

## 📋 Что включено

### Системные сервисы:
- ✅ **PostgreSQL 16** - Основная БД
- ✅ **Redis 7** - Кеширование
- ✅ **Digital Twin API** - FastAPI приложение

### Встроенные движки (в API):
- ✅ **Queue Theory Engine** - BIA анализ (M/M/c, Erlang C)
- ✅ **Advanced AI Generator** - AI генерация сценариев
- ✅ **Monte Carlo Engine** - Вероятностная симуляция
- ✅ **8 других движков** - Полный набор

---

## 🎯 Варианты деплоя

### Вариант 1: Docker Compose (рекомендуется для dev/test)

#### Шаг 1: Подготовка окружения
```bash
# Клонируем/переходим в папку
cd /Users/MD/ISO-22301/sandbox/services-v2/digital-twin

# Копируем .env.example в .env
cp .env.example .env

# Редактируем .env (при необходимости)
nano .env
```

#### Шаг 2: Запуск всех сервисов
```bash
# Запускаем все (PostgreSQL + Redis + API)
docker-compose up -d

# Проверяем статус
docker-compose ps

# Смотрим логи
docker-compose logs -f api
```

#### Шаг 3: Применяем миграции БД
```bash
# Заходим в контейнер API
docker-compose exec api bash

# Запускаем миграции
python -m alembic upgrade head

# Выходим
exit
```

#### Шаг 4: Проверка
```bash
# Открываем в браузере:
http://localhost:8000/docs

# Или curl:
curl http://localhost:8000/api/v1/health
```

**Готово!** API работает на `http://localhost:8000`

---

### Вариант 2: Только БД в Docker (dev режим)

Если хочешь запускать API локально (для разработки):

#### Шаг 1: Запускаем только БД
```bash
# Запускаем только PostgreSQL + Redis
docker-compose up -d postgres redis

# Проверяем
docker-compose ps
```

#### Шаг 2: Локальная установка зависимостей
```bash
# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate     # для Windows

# Устанавливаем зависимости
pip install -r requirements.txt
```

#### Шаг 3: Применяем миграции
```bash
# Убедитесь что в .env указано:
# POSTGRES_HOST=localhost

python -m alembic upgrade head
```

#### Шаг 4: Запускаем API локально
```bash
# Development режим (auto-reload)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Production режим
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

**API доступен на:** `http://localhost:8000`

---

### Вариант 3: Production Deployment (Kubernetes)

Для production рекомендуем Kubernetes. Пример манифестов:

#### PostgreSQL (StatefulSet)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  ports:
  - port: 5432
  selector:
    app: postgres
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        env:
        - name: POSTGRES_DB
          value: digital_twin
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 20Gi
```

#### Digital Twin API (Deployment)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-twin-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: digital-twin-api
  template:
    metadata:
      labels:
        app: digital-twin-api
    spec:
      containers:
      - name: api
        image: your-registry/digital-twin-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_HOST
          value: postgres
        - name: REDIS_HOST
          value: redis
        envFrom:
        - secretRef:
            name: digital-twin-secrets
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: digital-twin-api
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: digital-twin-api
```

---

## 🔧 Конфигурация

### Переменные окружения (.env)

#### Обязательные:
```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=digital_twin
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### Опциональные:
```bash
# API
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO

# Odoo (если используете)
ODOO_URL=http://odoo-server:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin-password

# AI (если используете OpenAI вместо Gemma)
OPENAI_API_KEY=sk-...

# Salesforce (если используете)
SALESFORCE_USERNAME=user@company.com
SALESFORCE_PASSWORD=password
SALESFORCE_SECURITY_TOKEN=token
```

---

## 📊 Мониторинг

### Health Check Endpoints:

```bash
# Основной health check
GET /api/v1/health

# Ответ:
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-01T12:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### Метрики (Prometheus готовность):

```bash
# TODO: Добавить /metrics endpoint
# GET /metrics
```

---

## 🔐 Безопасность

### 1. JWT Secret
```bash
# Генерируем секретный ключ
openssl rand -hex 32

# Добавляем в .env
JWT_SECRET_KEY=generated-secret-key
```

### 2. PostgreSQL пароль
```bash
# Используйте сильный пароль
POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

### 3. HTTPS (Production)
Используйте nginx или traefik для SSL:

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📈 Масштабирование

### Горизонтальное (несколько инстансов API):

```bash
# Docker Compose
docker-compose up -d --scale api=3

# Kubernetes
kubectl scale deployment digital-twin-api --replicas=5
```

### Вертикальное (больше ресурсов):

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## 🔄 Обновление (Zero Downtime)

### Docker Compose:
```bash
# 1. Собираем новый образ
docker-compose build api

# 2. Запускаем новый контейнер (старый продолжает работать)
docker-compose up -d --no-deps --build api

# 3. Миграции (если нужны)
docker-compose exec api python -m alembic upgrade head
```

### Kubernetes (Rolling Update):
```bash
# Обновляем образ
kubectl set image deployment/digital-twin-api api=your-registry/digital-twin-api:v2

# Следим за rollout
kubectl rollout status deployment/digital-twin-api

# Откат если нужно
kubectl rollout undo deployment/digital-twin-api
```

---

## 🐛 Troubleshooting

### Проблема: "Connection refused" к PostgreSQL

**Решение:**
```bash
# Проверяем что PostgreSQL запущен
docker-compose ps postgres

# Проверяем логи
docker-compose logs postgres

# Проверяем подключение
docker-compose exec postgres psql -U postgres -d digital_twin -c "SELECT 1"
```

### Проблема: "redis.exceptions.ConnectionError"

**Решение:**
```bash
# Проверяем Redis
docker-compose ps redis
docker-compose logs redis

# Тестируем
docker-compose exec redis redis-cli ping
# Должен ответить: PONG
```

### Проблема: "ImportError" или "ModuleNotFoundError"

**Решение:**
```bash
# Пересобираем образ
docker-compose build --no-cache api

# Или локально:
pip install -r requirements.txt
```

### Проблема: Миграции не применяются

**Решение:**
```bash
# Проверяем текущую версию
docker-compose exec api python -m alembic current

# Смотрим историю
docker-compose exec api python -m alembic history

# Применяем
docker-compose exec api python -m alembic upgrade head

# Откатываем (если нужно)
docker-compose exec api python -m alembic downgrade -1
```

---

## 📝 Полезные команды

### Docker Compose:
```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Остановка + удаление volumes (ВНИМАНИЕ: удалятся данные!)
docker-compose down -v

# Перезапуск одного сервиса
docker-compose restart api

# Логи
docker-compose logs -f api

# Заход в контейнер
docker-compose exec api bash

# Проверка ресурсов
docker stats
```

### Миграции БД:
```bash
# Создать новую миграцию
alembic revision -m "description"

# Применить все миграции
alembic upgrade head

# Откатить одну миграцию
alembic downgrade -1

# Показать текущую версию
alembic current

# История миграций
alembic history
```

### PostgreSQL:
```bash
# Вход в psql
docker-compose exec postgres psql -U postgres -d digital_twin

# Список таблиц
\dt

# Описание таблицы
\d table_name

# Выход
\q
```

---

## ✅ Чек-лист перед Production

### Конфигурация:
- [ ] `.env` файл с production настройками
- [ ] Сильные пароли для БД
- [ ] JWT_SECRET_KEY сгенерирован
- [ ] CORS настроен правильно
- [ ] LOG_LEVEL=WARNING или ERROR

### Безопасность:
- [ ] HTTPS включен
- [ ] Firewall настроен
- [ ] PostgreSQL не открыт наружу
- [ ] Redis не открыт наружу
- [ ] Secrets хранятся в секьюрити-менеджере (не в .env)

### Производительность:
- [ ] Connection pool настроен
- [ ] Redis кеш работает
- [ ] Индексы БД созданы (миграции)
- [ ] Ресурсы (CPU/RAM) выделены

### Мониторинг:
- [ ] Health checks работают
- [ ] Логи собираются
- [ ] Алерты настроены
- [ ] Backup БД настроен

### Тестирование:
- [ ] Все тесты проходят
- [ ] Load testing выполнен
- [ ] Failover протестирован

---

## 🎊 Готово!

**Digital Twin Service готов к деплою!**

**Стандартный деплой:**
```bash
docker-compose up -d
docker-compose exec api python -m alembic upgrade head
```

**Проверка:**
```bash
curl http://localhost:8000/api/v1/health
```

**Swagger UI:**
```
http://localhost:8000/docs
```

---

**Удачного деплоя!** 🚀
