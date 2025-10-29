# 🚀 Gateway Deployment Guide

## Архитектура "всё в одном"

```
https://bcm.local/               → Frontend (Vue)
https://bcm.local/api/events/... → EventBus (8001)   (SSE/WS)
https://bcm.local/api/ai/...     → Orchestrator (8002)
https://bcm.local/odoo/...       → Odoo (8069, в iframe)
```

**Один домен / один порт / корректный CORS / рабочие SSE/WS**

## 🎯 Быстрый запуск

```bash
# 1. Остановить старые контейнеры
docker compose -f docker-compose.mvp.yml down

# 2. Запустить новый стек через gateway
docker compose -f docker-compose.stack.yml up -d --build

# 3. Проверить статус (ждать ~60 сек до healthy)
docker compose -f docker-compose.stack.yml ps

# 4. Открыть приложение
open http://localhost:8080
```

## ✅ Проверка работы

### Frontend через Gateway
- **Главная**: http://localhost:8080/
- **Overview**: http://localhost:8080/overview  
- **Events**: http://localhost:8080/events
- **Orchestrator**: http://localhost:8080/orchestrator
- **Documents**: http://localhost:8080/documents
- **Admin (Odoo)**: http://localhost:8080/admin

### API через Gateway
```bash
# EventBus health
curl http://localhost:8080/api/events/health

# Orchestrator health  
curl http://localhost:8080/api/ai/health

# Publish event
curl -X POST http://localhost:8080/api/events/publish \
  -H "Content-Type: application/json" \
  -d '{"event_type":"bcm.smoke","tenant_id":"demo","data":{},"event_id":"gw-1"}'

# SSE stream
curl -N "http://localhost:8080/api/events/stream?tenant_id=demo" | head

# Orchestrator pending decisions
curl "http://localhost:8080/api/ai/decisions/pending?tenant_id=demo"

# Odoo iframe
curl -s http://localhost:8080/odoo/ | head
```

## 🌐 Vercel Deployment

### 1. Подготовка Frontend

```bash
cd frontend/web_portal

# Проверить наличие vercel.json (уже создан)
cat vercel.json

# Проверить .env.example
cat .env.example
```

### 2. Deploy на Vercel

1. **Import Project**: https://vercel.com/new
2. **Framework**: Other/Vite  
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist`

### 3. Environment Variables в Vercel

Для **временного тестирования** (через ngrok):
```bash
# Запустить ngrok туннели для backend сервисов
ngrok http 8080  # Gateway
```

Затем в Vercel Environment Variables:
```
VITE_EVENTBUS_URL=https://<ngrok-url>/api/events
VITE_ORCHESTRATOR_URL=https://<ngrok-url>/api  
VITE_ODOO_URL=https://<ngrok-url>/odoo
VITE_DOCPROC_URL=https://<ngrok-url>/api/docproc
```

Для **production** с отдельными доменами:
```
VITE_EVENTBUS_URL=https://api.yourdomain.com/events
VITE_ORCHESTRATOR_URL=https://api.yourdomain.com
VITE_ODOO_URL=https://odoo.yourdomain.com  
VITE_DOCPROC_URL=https://api.yourdomain.com/docproc
```

## 🔧 CORS Configuration

Для Vercel домена обновить в `.env`:
```bash
ALLOWED_ORIGIN=https://<your-app>.vercel.app
GATEWAY_ORIGIN=https://<your-app>.vercel.app
```

## 📁 Структура проекта

```
├── .env                          # Gateway configuration
├── gateway/
│   └── nginx.conf               # Единый routing для всех API
├── docker-compose.stack.yml     # Полный стек с gateway
├── frontend/web_portal/
│   ├── vercel.json             # SPA routing для Vercel
│   ├── .env.example            # Frontend env template
│   └── src/services/api.js     # Обновлены для relative URLs
└── GATEWAY_DEPLOYMENT.md       # Эта инструкция
```

## 🐛 Troubleshooting

### White Screen / JS Errors
```bash
# Проверить статус контейнеров
docker compose -f docker-compose.stack.yml ps

# Проверить логи gateway
docker logs bcm_gateway -f

# Проверить логи frontend  
docker logs bcm_frontend_stack -f

# Проверить API доступность
curl http://localhost:8080/api/events/health
curl http://localhost:8080/health
```

### SSE/Events не работают
```bash
# Проверить SSE напрямую
curl -N "http://localhost:8080/api/events/stream?tenant_id=demo"

# Должно выводить heartbeat каждые 1-2 сек
```

### Odoo iframe блокируется
- В production добавить CSP headers для iframe
- Проверить X-Frame-Options в Odoo

### CORS ошибки
- Убедиться что ALLOWED_ORIGIN соответствует frontend домену
- Проверить preflight OPTIONS запросы

## 🔥 Преимущества Gateway подхода

✅ **Один порт** для всего (8080)  
✅ **Единый CORS** policy  
✅ **Рабочие SSE/WebSocket** (buffering off)  
✅ **Простая настройка** Vercel (относительные URL)  
✅ **Production ready** архитектура  
✅ **Легкое масштабирование** (добавление сервисов)  

## 📈 Следующие шаги

1. **Deploy на Vercel**: Frontend готов к деплою
2. **Production backend**: Развернуть gateway + сервисы на сервере  
3. **Custom domain**: Настроить bcm.yourdomain.com
4. **SSL/HTTPS**: Добавить сертификаты
5. **Monitoring**: Добавить health checks и метрики
