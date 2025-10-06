# 🚀 AI-Platform BCM - Алгоритм Настройки

**Version:** 1.0
**Date:** 2025-10-06
**Для:** Production Deployment

---

## 📋 Краткое содержание

Этот документ описывает **правильный и эффективный алгоритм** настройки всего проекта AI-Platform BCM от нуля до production.

**Ключевые принципы:**
1. **Bottom-Up подход** - начинаем с foundation (database, redis), поднимаемся вверх
2. **Layer-by-Layer** - каждый слой зависит только от нижних слоев
3. **Validate as you go** - проверяем каждый шаг перед переходом к следующему
4. **Automate where possible** - используем скрипты для повторяющихся задач

---

## 🎯 Архитектура (Dependency Order)

```
Layer 5: Human Interface          ← Deploy LAST
         (Web App, API Gateway)
              ↓ depends on
Layer 4: Platform Services        ← Deploy 4th
         (12 BCM Microservices)
              ↓ depends on
Layer 3: Intelligent Core         ← Deploy 3rd
         (AI + Workflow + Domain)
              ↓ depends on
Layer 2: Shared Libraries         ← Setup 2nd
         (Auth, DB, Cache, etc.)
              ↓ depends on
Layer 1: Infrastructure           ← Deploy FIRST ⭐
         (Database, EventBus, etc.)
```

**Правило:** Никогда не запускаем слой N, пока не проверили работу слоя N-1!

---

## 🚀 Алгоритм (Step-by-Step)

### STEP 0: Prerequisites (2-3 часа) ✅

**Цель:** Убедиться что система готова

```bash
# 1. Проверить системные требования
docker --version          # >= 24.0
python3 --version         # >= 3.11
psql --version            # >= 14
free -h                   # Min 8GB RAM

# 2. Клонировать проект
git clone <repo-url>
cd AI-Platform-ISO

# 3. Создать .env
cp .env.example .env
nano .env  # Заполнить все критичные переменные

# 4. Проверить структуру
ls -la infrastructure/
ls -la shared/
ls -la platform-services/
ls -la intelligent-core/
```

**Критерии успеха:**
- ✅ Docker, Python, PostgreSQL установлены
- ✅ Проект склонирован
- ✅ .env создан и заполнен
- ✅ Структура проверена

**Документация:** [infrastructure/DEPLOYMENT_ROADMAP.md#phase-0-prerequisites](infrastructure/DEPLOYMENT_ROADMAP.md#phase-0-prerequisites)

---

### STEP 1: Foundation Layer (3-4 часа) ✅

**Цель:** Запустить базовые сервисы (Database, Redis, Qdrant)

```bash
# 1. Start PostgreSQL + Redis
docker-compose up -d postgres redis

# 2. Verify connections
psql $DATABASE_URL -c "SELECT 1;"
redis-cli -u $REDIS_URL ping

# 3. Apply database migrations
cd infrastructure/database
python apply_migrations_simple.py

# 4. Verify tables created
psql $DATABASE_URL -c "\dt"

# 5. Initialize Qdrant Vector DB
cd infrastructure/vector-db
pip install -r requirements.txt
python test_connection.py
python qdrant/init_collections.py

# 6. Test Redis managers
cd infrastructure/database
python test_redis_managers.py
```

**Критерии успеха:**
- ✅ PostgreSQL running + migrations applied
- ✅ Redis running + cache works
- ✅ Qdrant Cloud connected + collections created
- ✅ All tables exist in database

**Troubleshooting:** [infrastructure/TECHNICAL_GUIDE.md#troubleshooting](infrastructure/TECHNICAL_GUIDE.md#troubleshooting)

---

### STEP 2: Infrastructure Services (6-8 часов) ✅

**Цель:** Запустить критичные infrastructure сервисы

```bash
# 1. Start EventBus
cd infrastructure/eventbus
export EVENTBUS_TRANSPORT=redis
python -m eventbus.main
# Verify: pub/sub test

# 2. Start API Gateway
cd infrastructure/security/api-gateway
uvicorn main:app --port 3001
# Verify: curl http://localhost:3001/health

# 3. Start Monitoring
cd infrastructure/monitoring
docker-compose up -d
# Verify: open http://localhost:9090

# 4. Start Service Discovery
cd infrastructure/service-discovery
python main.py
# Verify: curl http://localhost:8500/v1/catalog/services

# 5. Start Notification Service (optional)
cd infrastructure/notification-service
uvicorn main:app --port 8010
# Verify: send test email

# 6. Start WebSocket Service (optional)
cd infrastructure/realtime-websocket
uvicorn main:app --port 8001
# Verify: WebSocket connection test
```

**Критерии успеха:**
- ✅ EventBus running (Redis transport)
- ✅ API Gateway running + auth works
- ✅ Prometheus + Grafana running
- ✅ Service Discovery running
- ✅ Notification service working (optional)
- ✅ WebSocket service working (optional)

**Документация:** [infrastructure/DEPLOYMENT_ROADMAP.md#phase-2-infrastructure-services](infrastructure/DEPLOYMENT_ROADMAP.md#phase-2-infrastructure-services)

---

### STEP 3: Shared Libraries (2-3 часа) ✅

**Цель:** Установить и протестировать shared libraries

```bash
# 1. Install shared library
cd shared/
pip install -r requirements.txt

# Or install as editable package
pip install -e .

# 2. Test database module
python -c "
from shared.database import get_db
import asyncio

async def test():
    db = await get_db()
    result = await db.fetch_one('SELECT 1')
    print('✅ Database OK')

asyncio.run(test())
"

# 3. Test auth module
python -c "
from shared.auth import create_jwt_token, verify_jwt_token

token = create_jwt_token({'sub': 'user-123'})
payload = verify_jwt_token(token)
print('✅ Auth OK')
"

# 4. Test cache module
python -c "
from shared.cache import get_cache
import asyncio

async def test():
    cache = await get_cache()
    await cache.set('test', 'value')
    value = await cache.get('test')
    print('✅ Cache OK')

asyncio.run(test())
"

# 5. Test EventBus client
python -c "
from shared.eventbus import EventBusClient
import asyncio

async def test():
    eb = EventBusClient()
    await eb.connect()
    print('✅ EventBus client OK')

asyncio.run(test())
"

# 6. Test integrations
python -c "
from shared.integrations.rag_connector import RAGConnector
print('✅ RAG Connector OK')
"
```

**Критерии успеха:**
- ✅ Shared library installed
- ✅ Database module works
- ✅ Auth module works
- ✅ Cache module works
- ✅ EventBus client works
- ✅ Integrations import successfully

**Документация:** [infrastructure/DEPLOYMENT_ROADMAP.md#phase-3-shared-libraries](infrastructure/DEPLOYMENT_ROADMAP.md#phase-3-shared-libraries)

---

### STEP 4: Platform Services (8-10 часов) ✅

**Цель:** Запустить все 11 бизнес-сервисов

**Автоматический способ (рекомендуется):**
```bash
# Start all services with one command
./infrastructure/scripts/start_platform_services.sh

# Wait for startup (30-60 seconds)
sleep 60

# Check health of all services
./infrastructure/scripts/health_check_all.sh
```

**Ручной способ (для debugging):**
```bash
# Start each service manually in separate terminals

# Terminal 1: BIA Service
cd platform-services/bia-service
uvicorn main:app --port 8001

# Terminal 2: Risk Service
cd platform-services/risk-service
uvicorn main:app --port 8002

# Terminal 3: Compliance Service
cd platform-services/compliance-service
uvicorn main:app --port 8003

# ... continue for all 11 services
```

**Verify each service:**
```bash
# Check all health endpoints
for port in {8001..8011}; do
  curl http://localhost:$port/health
done
```

**Критерии успеха:**
- ✅ Все 11 platform services запущены
- ✅ Все health checks green
- ✅ Service Discovery видит все сервисы
- ✅ API endpoints отвечают
- ✅ Database connections работают
- ✅ EventBus integration работает

**Документация:** [infrastructure/DEPLOYMENT_ROADMAP.md#phase-4-platform-services](infrastructure/DEPLOYMENT_ROADMAP.md#phase-4-platform-services)

---

### STEP 5: Intelligent Core (6-8 часов) ✅

**Цель:** Запустить AI intelligence layer

```bash
# 1. Workflow Intelligence
cd intelligent-core/workflow_intelligence
pip install -r requirements.txt
uvicorn main:app --port 9001
# Verify: curl http://localhost:9001/health

# 2. AI Experts
cd intelligent-core/ai_experts
pip install -r requirements.txt
uvicorn main:app --port 9002
# Verify: test expert query

# 3. Coordination Center
cd intelligent-core/coordination-center
pip install -r requirements.txt
uvicorn main:app --port 8004
# Verify: test coordination

# 4. Learning System
cd intelligent-core/learning-system
pip install -r requirements.txt
uvicorn main:app --port 9003
# Verify: test learning event

# 5. Predictive Services
cd intelligent-core/predictive
pip install -r requirements.txt
uvicorn main:app --port 9004
# Verify: test prediction
```

**Критерии успеха:**
- ✅ Workflow Engine running
- ✅ AI Experts responding
- ✅ Coordination Center working
- ✅ Learning System capturing events
- ✅ Predictions working
- ✅ Integration with Qdrant working
- ✅ Integration with platform services working

**Документация:** [infrastructure/DEPLOYMENT_ROADMAP.md#phase-5-intelligent-core](infrastructure/DEPLOYMENT_ROADMAP.md#phase-5-intelligent-core)

---

### STEP 6: Human Interface (4-6 часов) ✅

**Цель:** Запустить user-facing interfaces

```bash
# 1. API Gateway (GraphQL/REST)
cd human-interface/api-gateway
npm install
cp .env.example .env
# Edit .env with backend URLs
npm run dev
# Verify: open http://localhost:3000/api/docs

# 2. Web Application
cd human-interface/web-app
npm install
cp .env.local.example .env.local
# Edit with API URLs
npm run dev
# Verify: open http://localhost:3001

# 3. Test end-to-end flow
# - Open web app
# - Login
# - Navigate to BIA module
# - Create a critical function
# - Verify data saved in database
```

**Критерии успеха:**
- ✅ API Gateway running
- ✅ Web App running
- ✅ Login works
- ✅ API calls successful
- ✅ Data persistence works
- ✅ Real-time updates via WebSocket work

**Документация:** [infrastructure/DEPLOYMENT_ROADMAP.md#phase-6-human-interface](infrastructure/DEPLOYMENT_ROADMAP.md#phase-6-human-interface)

---

### STEP 7: Production Hardening (8-12 часов) ✅

**Цель:** Production-ready configuration

```bash
# 1. Secrets Management
cd infrastructure/secrets-manager
docker-compose up -d vault
vault operator init
# Migrate secrets from .env to Vault

# 2. SSL/TLS
certbot certonly --standalone -d your-domain.com
# Configure nginx with SSL

# 3. Database Backups
cd infrastructure/database
# Setup automated backups (cron job)
crontab -e

# 4. Monitoring & Alerting
cd infrastructure/monitoring
# Configure Grafana dashboards
# Setup Prometheus alerts
# Configure alert notifications

# 5. Load Balancing
cd infrastructure/intelligent-gateway
# Setup HAProxy/nginx for load balancing
# Configure upstream servers

# 6. Final Production Checklist
# - All secrets in Vault
# - SSL/TLS enabled
# - CORS configured
# - Rate limiting enabled
# - Automated backups running
# - Monitoring alerts configured
# - Performance optimization done
```

**Критерии успеха:**
- ✅ Vault running + secrets migrated
- ✅ SSL certificates configured
- ✅ HTTPS working
- ✅ Automated backups running
- ✅ Monitoring dashboards configured
- ✅ Alerts configured and tested
- ✅ Load balancing configured
- ✅ Production checklist completed

**Документация:** [infrastructure/DEPLOYMENT_ROADMAP.md#phase-7-production-hardening](infrastructure/DEPLOYMENT_ROADMAP.md#phase-7-production-hardening)

---

## ⏱️ Timeline Summary

| Step | Description | Time | Cumulative |
|------|-------------|------|------------|
| **STEP 0** | Prerequisites | 2-3h | 2-3h |
| **STEP 1** | Foundation Layer | 3-4h | 5-7h |
| **STEP 2** | Infrastructure Services | 6-8h | 11-15h |
| **STEP 3** | Shared Libraries | 2-3h | 13-18h |
| **STEP 4** | Platform Services | 8-10h | 21-28h |
| **STEP 5** | Intelligent Core | 6-8h | 27-36h |
| **STEP 6** | Human Interface | 4-6h | 31-42h |
| **STEP 7** | Production Hardening | 8-12h | 39-54h |
| **TOTAL** | | **40-54h** | **~1-2 weeks** |

**Recommendation:** Plan for 2 недели (10 рабочих дней) для комфортной настройки с тестированием.

---

## 🎯 Daily Breakdown (Рекомендуемый график)

### Week 1: Foundation + Infrastructure + Platform

**Day 1 (8h):**
- ✅ STEP 0: Prerequisites (2h)
- ✅ STEP 1: Foundation Layer (4h)
- ✅ STEP 2: Infrastructure Services - Part 1 (EventBus, API Gateway) (2h)

**Day 2 (8h):**
- ✅ STEP 2: Infrastructure Services - Part 2 (Monitoring, Service Discovery, Notifications) (6h)
- ✅ STEP 3: Shared Libraries (2h)

**Day 3 (8h):**
- ✅ STEP 4: Platform Services - Part 1 (BIA, Risk, Compliance, Documents) (8h)

**Day 4 (8h):**
- ✅ STEP 4: Platform Services - Part 2 (Response, Validation, Governance) (4h)
- ✅ STEP 4: Platform Services - Part 3 (Planning, Plans, Learning, Community) (4h)

**Day 5 (8h):**
- ✅ STEP 4: Integration Testing Platform Services (4h)
- ✅ STEP 5: Intelligent Core - Part 1 (Workflow, AI Experts) (4h)

### Week 2: AI Layer + UI + Production

**Day 6 (8h):**
- ✅ STEP 5: Intelligent Core - Part 2 (Coordination, Learning, Predictive) (6h)
- ✅ STEP 6: Human Interface - Part 1 (API Gateway) (2h)

**Day 7 (8h):**
- ✅ STEP 6: Human Interface - Part 2 (Web App) (4h)
- ✅ End-to-End Testing (4h)

**Day 8 (8h):**
- ✅ STEP 7: Production Hardening - Part 1 (Secrets, SSL) (8h)

**Day 9 (8h):**
- ✅ STEP 7: Production Hardening - Part 2 (Backups, Monitoring) (8h)

**Day 10 (8h):**
- ✅ STEP 7: Production Hardening - Part 3 (Load Balancing, Final Checklist) (4h)
- ✅ Final Testing & Documentation (4h)

---

## 📊 Validation Strategy

**После каждого шага проверяем:**

### 1. Health Checks
```bash
./infrastructure/scripts/health_check_all.sh
```

### 2. Integration Tests
```bash
pytest tests/integration/ -v
```

### 3. Manual Verification
- Check logs (no errors)
- Test API endpoints
- Verify database records
- Check monitoring dashboards

---

## 🚀 Quick Start Commands

### Development (все в одной команде)
```bash
# Start everything
./scripts/start_all.sh

# Health check
./infrastructure/scripts/health_check_all.sh

# View logs
docker-compose logs -f
```

### Stop everything
```bash
./scripts/stop_all.sh
```

---

## 🔧 Helper Scripts

**Созданы автоматические скрипты:**

1. **[health_check_all.sh](infrastructure/scripts/health_check_all.sh)**
   - Проверяет health всех сервисов
   - Показывает summary (healthy/unhealthy)

2. **[start_platform_services.sh](infrastructure/scripts/start_platform_services.sh)**
   - Запускает все 11 platform services
   - Логи в `platform-services/logs/`

3. **[stop_platform_services.sh](infrastructure/scripts/stop_platform_services.sh)**
   - Останавливает все platform services
   - Cleanup processes

**Usage:**
```bash
# Make executable
chmod +x infrastructure/scripts/*.sh

# Use
./infrastructure/scripts/health_check_all.sh
./infrastructure/scripts/start_platform_services.sh
./infrastructure/scripts/stop_platform_services.sh
```

---

## 📚 Документация

**Главные документы:**

1. **[DEPLOYMENT_ROADMAP.md](infrastructure/DEPLOYMENT_ROADMAP.md)** - Детальный roadmap
2. **[TECHNICAL_GUIDE.md](infrastructure/TECHNICAL_GUIDE.md)** - Техническое руководство
3. **[OVERVIEW.md](infrastructure/OVERVIEW.md)** - Архитектура
4. **[QUICK_REFERENCE.md](infrastructure/QUICK_REFERENCE.md)** - Быстрая справка
5. **[INDEX.md](infrastructure/INDEX.md)** - Полный индекс документации

**Service-specific:**
- [eventbus/QUICKSTART.md](infrastructure/eventbus/QUICKSTART.md)
- [vector-db/QUICKSTART.md](infrastructure/vector-db/QUICKSTART.md)
- [notification-service/QUICK_START.md](infrastructure/notification-service/QUICK_START.md)

---

## ⚠️ Common Pitfalls (Частые ошибки)

### 1. Запуск сервисов в неправильном порядке
**Ошибка:** Запускать platform services до infrastructure
**Решение:** Следуй строгому порядку: Infrastructure → Shared → Platform → Intelligent Core

### 2. Забыть проверить .env
**Ошибка:** Пустые или неправильные environment variables
**Решение:** Проверь `.env` перед каждым шагом

### 3. Не проверять health после каждого шага
**Ошибка:** Двигаться дальше с broken services
**Решение:** Всегда запускай `health_check_all.sh` после каждого шага

### 4. Не читать логи при ошибках
**Ошибка:** Пытаться гадать что не работает
**Решение:** `docker-compose logs <service>` или `tail -f logs/<service>.log`

### 5. Забыть про dependencies
**Ошибка:** Не установить `pip install -r requirements.txt`
**Решение:** Всегда устанавливай dependencies перед запуском сервиса

---

## 🆘 Troubleshooting

**Проблема:** Сервис не запускается
```bash
# 1. Check logs
docker-compose logs <service>

# 2. Check environment variables
env | grep DATABASE_URL

# 3. Check dependencies
pip list | grep <package>

# 4. Check port conflicts
lsof -i :<port>
```

**Проблема:** Database connection failed
```bash
# Check connection
psql $DATABASE_URL -c "SELECT 1;"

# Check Supabase status
curl https://status.supabase.com/
```

**Проблема:** Redis connection failed
```bash
# Check Redis
redis-cli -u $REDIS_URL ping

# Check container
docker-compose ps redis
```

**Полный troubleshooting:** [TECHNICAL_GUIDE.md#troubleshooting](infrastructure/TECHNICAL_GUIDE.md#troubleshooting)

---

## ✅ Success Criteria (Критерии успеха)

**Deployment успешен если:**

1. ✅ Все health checks green
2. ✅ End-to-end flow работает (UI → API → Database)
3. ✅ EventBus доставляет события
4. ✅ Мониторинг собирает метрики
5. ✅ Alerts configured и тестированы
6. ✅ Backups running
7. ✅ SSL/HTTPS working
8. ✅ Load testing passed (optional)
9. ✅ Security scan passed (optional)
10. ✅ Documentation updated

---

## 🎉 Next Steps After Deployment

1. **Populate Knowledge Base**
   - Load ISO standards в Qdrant
   - Import BCI guidelines
   - Add industry best practices

2. **Configure Workflows**
   - Setup BIA workflow templates
   - Configure risk assessment workflows
   - Create compliance check workflows

3. **Onboard Users**
   - Create admin accounts
   - Setup organizations
   - Configure permissions

4. **Training**
   - Train AI models on your data
   - Fine-tune predictive models
   - Calibrate recommendation engine

5. **Monitoring**
   - Setup custom Grafana dashboards
   - Configure business metrics
   - Setup alerting rules

---

## 📞 Support

**Questions?**
- Check [TECHNICAL_GUIDE.md](infrastructure/TECHNICAL_GUIDE.md)
- Review service-specific README
- Check [архив/](infrastructure/архив/) for context

**Found a bug?**
- Check logs first
- Review troubleshooting guide
- Document the issue

---

**Last Updated:** 2025-10-06
**Version:** 1.0
**Status:** Production Ready ✅
