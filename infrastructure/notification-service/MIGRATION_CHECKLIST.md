# 📋 notification_service - Migration Checklist

**Source:** `/Users/MD/ISO-22301—копия/services/SERVICES/BCM_1/notification_service/`
**Target:** `/Users/MD/AI-Platform-ISO/infrastructure/notification-service/`

---

## 🔍 АНАЛИЗ (STEP 1 - COMPLETE)

### Текущее состояние:
- **Lines:** 256
- **Port:** 8000 (КОНФЛИКТ с gateway!)
- **Dependencies:** FastAPI, Redis, RabbitMQ, SMTP
- **Endpoints:** 4 notification types (email, sms, push, webhook)

### Внешние зависимости:
- ✅ Redis (localhost:6379) → **НУЖЕН Upstash**
- ✅ RabbitMQ (localhost:5672) → **ОПЦИОНАЛЬНО** (можем использовать EventBus)
- ❌ SMTP (не настроен) → **НУЖНЫ credentials**
- ❌ Auth (нет) → **НУЖНА Supabase Auth**

---

## 🛠️ ТРЕБУЕМЫЕ ИЗМЕНЕНИЯ

### 1. Port Configuration
- [ ] Line 256: `port=8000` → `port=8035`

### 2. Redis Connection
- [ ] Line 78: `redis://localhost:6379/2` → `os.getenv("UPSTASH_REDIS_URL")`
- [ ] Добавить fallback для local development

### 3. RabbitMQ (Optional)
- [ ] Line 82-83: Сделать опциональным
- [ ] Можно заменить на EventBus integration

### 4. Environment Variables
- [ ] Создать `.env.example` с:
  - PORT=8035
  - UPSTASH_REDIS_URL=
  - SMTP_HOST=
  - SMTP_PORT=
  - SMTP_USER=
  - SMTP_PASSWORD=
  - EVENTBUS_URL=http://localhost:8001
  - RABBITMQ_URL= (optional)

### 5. Auth Middleware
- [ ] Добавить JWT validation
- [ ] Supabase Auth integration
- [ ] Dependency для protected endpoints

### 6. SMTP Implementation
- [ ] Раскомментировать TODO в send_email()
- [ ] Реализовать реальную отправку
- [ ] Добавить SMTP config из env

### 7. Logging
- [ ] Интеграция с Loki (structured logging)
- [ ] Добавить correlation IDs
- [ ] Log levels из env

### 8. Error Handling
- [ ] Улучшить error responses
- [ ] Добавить retry logic
- [ ] Dead letter queue для failed notifications

### 9. Metrics
- [ ] Prometheus metrics endpoint
- [ ] Counter для sent notifications
- [ ] Histogram для response times

### 10. Health Check
- [ ] Проверка SMTP connection
- [ ] Проверка EventBus availability
- [ ] Readiness vs Liveness

---

## 📝 STEP 2: ADAPTATION PLAN

### Phase 1: Basic Adaptation (15 min)
1. Copy to BCM_1_MIGRATED/notification_service/
2. Change port 8000 → 8035
3. Update Redis URL to use env var
4. Make RabbitMQ optional
5. Create .env.example

### Phase 2: Production Features (30 min)
6. Add Auth middleware
7. Implement real SMTP
8. Add EventBus integration
9. Add Prometheus metrics
10. Improve error handling

### Phase 3: Testing (15 min)
11. Test locally with .env
12. Test Redis connection (Upstash)
13. Test email sending
14. Test health endpoint

---

## 🚀 STEP 3: PRODUCTION TRANSFER

### Checklist:
- [ ] Copy adapted version to infrastructure/notification-service/
- [ ] Add to Tool Registry (coordination-center)
- [ ] Update docker-compose
- [ ] Add to Prometheus scrape targets
- [ ] Create README.md
- [ ] Test integration with other services

---

## 📊 ESTIMATED TIME

- Step 1 (Analysis): ✅ 5 min DONE
- Step 2 (Adaptation): ⏱️ 45-60 min
- Step 3 (Transfer): ⏱️ 10 min

**Total: ~60 min**

---

**ГОТОВ К STEP 2!** 🎯
