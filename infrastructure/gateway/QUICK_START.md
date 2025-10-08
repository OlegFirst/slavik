# API Gateway - Quick Start Guide

**Дата:** 2025-10-07
**Статус:** ✅ ГОТОВ К ЗАПУСКУ

---

## ⚡ Быстрый старт (1 команда)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/gateway/api-gateway
./start_gateway.sh
```

**Всё!** Gateway запустится автоматически на порту 8000.

---

## 📋 Что было настроено

### 1. JWT_SECRET сгенерирован ✅
```
Cj8QUzVaQzC5rfn9lEUQA_jP3-y4ecoMrBDzptlokv2B0Fny3zhph3bzeyJXA4c482JlrmTBN5n5O-QEXD0ZAg
```
Сохранён в `.env` файле.

### 2. .env файл создан ✅
Все конфигурации готовы:
- ✅ JWT_SECRET (безопасный 512-bit ключ)
- ✅ Redis URL (Redis Cloud)
- ✅ PostgreSQL URL (Supabase)
- ✅ AI Manager интеграция (порт 8046)
- ✅ Rate limiting настроен (100 req/min, VIP: 500 req/min)
- ✅ Circuit breaker включён
- ✅ Audit logging включён

### 3. Startup script создан ✅
`start_gateway.sh` автоматически:
- Загружает .env
- Проверяет зависимости
- Тестирует Redis и PostgreSQL
- Освобождает порт 8000 если занят
- Запускает Gateway

---

## 🚀 Запуск Gateway

### Вариант 1: Автоматический (рекомендуется)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/gateway/api-gateway
./start_gateway.sh
```

### Вариант 2: Ручной

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/gateway/api-gateway

# Установить зависимости (если не установлены)
pip3 install -r requirements.txt

# Загрузить .env и запустить
source .env
python3 main.py
```

### Вариант 3: Background (как daemon)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/gateway/api-gateway

# Запустить в фоне
nohup ./start_gateway.sh > gateway.log 2>&1 &

# Проверить PID
echo $! > gateway.pid

# Остановить
kill $(cat gateway.pid)
```

---

## ✅ Проверка работы

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-07T...",
  "components": {
    "redis": "healthy",
    "database": "healthy",
    "backends": {...}
  }
}
```

### 2. Swagger UI
Откройте в браузере:
```
http://localhost:8000/docs
```

Вы увидите все endpoints включая:
- `/health` - Health check
- `/metrics` - Prometheus metrics
- `/api/v1/gateway/ai/analyze` - AI анализ Gateway
- `/api/v1/gateway/ai/optimize` - AI оптимизации
- `/api/v1/gateway/services` - Список сервисов

### 3. Metrics
```bash
curl http://localhost:8000/metrics
```

**Ожидаемый ответ:**
```
# HELP gateway_requests_total Total requests
# TYPE gateway_requests_total counter
gateway_requests_total 0.0

# HELP gateway_request_duration_seconds Request duration
# TYPE gateway_request_duration_seconds histogram
...
```

### 4. AI Analysis (требует authentication)
```bash
# Сначала получить токен (пока Gateway без auth service):
# curl -X POST http://localhost:8001/auth/login ...

# Затем запросить анализ
curl -X POST http://localhost:8000/api/v1/gateway/ai/analyze?time_range=5m \
  -H "Content-Type: application/json"
```

---

## 🔧 Конфигурация (.env)

### Основные настройки:

| Параметр | Значение | Описание |
|----------|----------|----------|
| `JWT_SECRET` | `Cj8QUzVa...` | Секретный ключ для JWT |
| `PORT` | `8000` | Порт Gateway |
| `ENVIRONMENT` | `production` | Режим работы |

### Redis:
```bash
REDIS_URL=redis://redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com:10023
```

### PostgreSQL (Supabase):
```bash
DATABASE_URL=postgresql://postgres.tpdkhddtbhpoqzzgxfni:K@x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres?sslmode=require
```

### AI Manager:
```bash
AI_MANAGER_ENABLED=true
AI_MANAGER_URL=http://localhost:8046/api/gateway
```

---

## 📊 Monitoring

### Prometheus Metrics

Gateway экспортирует метрики на `/metrics`:

```promql
# Request rate
rate(gateway_requests_total[5m])

# Latency (95th percentile)
histogram_quantile(0.95, gateway_request_duration_seconds)

# Error rate
rate(gateway_errors_total[5m])

# Rate limit hits
gateway_rate_limit_exceeded_total

# Circuit breaker state
gateway_circuit_breaker_state{service="bia-service"}
```

### Grafana Dashboard

После запуска Grafana (порт 3000):
1. Открыть http://localhost:3000
2. Login: `admin` / `admin123`
3. Добавить Prometheus datasource: http://prometheus:9090
4. Импортировать dashboard для Gateway

---

## 🛠️ Troubleshooting

### Проблема: Port 8000 already in use

**Решение:**
```bash
# Найти процесс
lsof -i :8000

# Убить процесс
kill -9 <PID>

# Или автоматически
lsof -ti:8000 | xargs kill -9
```

### Проблема: Redis connection failed

**Проверить:**
```bash
redis-cli -h redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com -p 10023 ping
```

**Альтернатива:** Использовать локальный Redis
```bash
# Установить Redis
brew install redis  # macOS

# Запустить
redis-server

# Обновить .env
REDIS_URL=redis://localhost:6379
```

### Проблема: PostgreSQL connection failed

**Проверить credentials в .env:**
```bash
# Тестовое подключение
python3 -c "
import asyncpg
import asyncio
import os

async def test():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    print('✅ Connected to PostgreSQL')
    await conn.close()

asyncio.run(test())
"
```

### Проблема: Dependencies missing

**Установить:**
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/gateway/api-gateway
pip3 install -r requirements.txt
```

---

## 🔐 Security Notes

### JWT_SECRET
- ✅ **512-bit криптографически случайный ключ**
- ✅ Сохранён в `.env` (не в git)
- ⚠️ **НЕ ПУБЛИКУЙТЕ** этот ключ
- ⚠️ Для production - используйте отдельный ключ

### Rate Limiting
- Standard users: **100 requests/min**
- VIP users: **500 requests/min**
- Burst: **+20 requests**

### CORS
По умолчанию разрешено:
- `http://localhost:3000`
- `http://localhost:8080`

Для добавления origins:
```bash
# В .env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://yourdomain.com
```

---

## 🚀 Next Steps

### После запуска Gateway:

1. **Запустить MIO Manager** (порт 8046)
   ```bash
   cd /Users/MD/AI-Platform-ISO/infrastructure/observability/mio-manager
   python3 main.py
   ```

2. **Запустить Backend Services**
   - BIA Service (8012)
   - Risk Service (8013)
   - Compliance Service (8014)
   - И другие...

3. **Запустить Observability Stack**
   ```bash
   cd /Users/MD/AI-Platform-ISO/infrastructure/observability
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

4. **Проверить интеграцию**
   ```bash
   # Gateway health
   curl http://localhost:8000/health

   # MIO Manager health
   curl http://localhost:8046/health

   # Prometheus targets
   curl http://localhost:9090/api/v1/targets
   ```

---

## 📚 Документация

- **Полный аудит:** [GATEWAY_SERVICES_AUDIT.md](GATEWAY_SERVICES_AUDIT.md)
- **AI Integration:** [GATEWAY_AI_INTEGRATION_COMPLETE.md](GATEWAY_AI_INTEGRATION_COMPLETE.md)
- **Service Spec:** [SERVICE_SPEC.md](SERVICE_SPEC.md)

---

## 💡 Tips

### Автозапуск при старте системы (macOS)

Создать Launch Agent:
```bash
# Создать plist файл
cat > ~/Library/LaunchAgents/com.bcm.gateway.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.bcm.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/MD/AI-Platform-ISO/infrastructure/gateway/api-gateway/start_gateway.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Загрузить
launchctl load ~/Library/LaunchAgents/com.bcm.gateway.plist
```

### Логирование

```bash
# Запустить с логами в файл
./start_gateway.sh 2>&1 | tee gateway.log

# Следить за логами
tail -f gateway.log

# Ротация логов (добавить в cron)
find . -name "gateway.log" -size +100M -delete
```

---

## ✅ Checklist

- [x] JWT_SECRET сгенерирован
- [x] .env файл создан
- [x] Redis credentials настроены
- [x] PostgreSQL credentials настроены
- [x] AI Manager integration включена
- [x] Startup script готов
- [x] Port 8000 свободен
- [ ] Gateway запущен (`./start_gateway.sh`)
- [ ] Health check успешен (`curl http://localhost:8000/health`)
- [ ] Swagger UI доступен (`http://localhost:8000/docs`)

---

**Создано:** 2025-10-07
**Готово к запуску:** ✅ ДА
**Время до старта:** 1 команда!
