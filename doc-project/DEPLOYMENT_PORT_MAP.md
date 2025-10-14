# 🗺️ DEPLOYMENT PORT MAP & STARTUP GUIDE

**Project:** NASH 4.0 Universal AI Partnership Platform
**Date:** 2025-10-11 (Updated after Phase 2.1 & Monitoring Cleanup)
**Purpose:** Поэтапный запуск без конфликтов портов
**Architecture:** Event-Driven Choreography with MIO EYES Observatory

---

## 🎯 СТРАТЕГИЯ ЗАПУСКА

**ВАЖНО:** Запускаем НЕ ВСЕ сразу, а **ПОЭТАПНО** по слоям!

### Порядок запуска (снизу вверх):

```
1. Infrastructure (База) → Порты 5432, 6379, 5672, 8080
2. Platform Services → Порты 8001-8012, 8070
3. Intelligent Core → Порты 8020-8030
4. AI-Office Infrastructure → Порты 8050, 8055, 8060, 8061, 8090
5. Interface → Порты 3000-3003, 8000
```

---

## 📊 COMPLETE PORT MAP

### 🗄️ Layer 1: Infrastructure (ЗАПУСКАЕМ ПЕРВЫМИ)

| Service | Port | Status | Priority | Command |
|---------|------|--------|----------|---------|
| **PostgreSQL** | 5432 | 🔴 Required | 1 | `docker run -d -p 5432:5432 postgres:15` |
| **Redis** | 6379 | 🔴 Required | 1 | `docker run -d -p 6379:6379 redis:7` |
| **RabbitMQ** | 5672 | 🔴 Required | 1 | `docker run -d -p 5672:5672 rabbitmq:3-management` |
| **RabbitMQ UI** | 15672 | 🟡 Optional | 2 | (включается автоматически) |
| **API Gateway** | 8080 | 🔴 Required | 1 | `cd infrastructure/gateway && uvicorn main:app --port 8080` |
| **Qdrant Vector DB** | 6333 | 🟡 Optional | 3 | `docker run -d -p 6333:6333 qdrant/qdrant` |
| **Prometheus** | 9090 | 🔴 Required (Phase 2.1) | 2 | `docker run -d -p 9090:9090 prom/prometheus` |
| **Grafana** | 3001 | 🟡 Optional | 3 | `docker run -d -p 3001:3000 grafana/grafana` |
| **Service Catalog** | N/A | 🔴 Required (Phase 2.1) | 1 | Loaded by Service Discovery v2.0 |

**Startup Script:**
```bash
# infrastructure/start-infrastructure.sh
docker-compose -f infrastructure/docker-compose.yml up -d
```

---

### 🏢 Layer 2: Platform Services (ЗАПУСКАЕМ ВТОРЫМИ)

| Service | Port | Status | Dependencies | Command |
|---------|------|--------|--------------|---------|
| **BIA Service** | 8001 | 🔴 Required | PostgreSQL, Redis | `uvicorn main:app --port 8001` |
| **Risk Service** | 8002 | 🔴 Required | PostgreSQL, Redis | `uvicorn main:app --port 8002` |
| **Compliance Service** | 8003 | 🔴 Required | PostgreSQL, Redis | `uvicorn main:app --port 8003` |
| **Governance Service** | 8004 | 🔴 Required | PostgreSQL, Redis | `uvicorn main:app --port 8004` |
| **Documents Service** | 8005 | 🔴 Required | PostgreSQL, Redis | `uvicorn main:app --port 8005` |
| **Validation Service** | 8006 | 🔴 Required | PostgreSQL, Redis | `uvicorn main:app --port 8006` |
| **Response Service** | 8007 | 🟡 Optional | PostgreSQL, Redis | `uvicorn main:app --port 8007` |
| **Community Service** | 8008 | 🟡 Optional | PostgreSQL, Redis | `uvicorn main:app --port 8008` |
| **Learning Service** | 8009 | 🟡 Optional | PostgreSQL, Redis | `uvicorn main:app --port 8009` |
| **Planning Service** | 8010 | 🟡 Optional | PostgreSQL, Redis | `uvicorn main:app --port 8010` |
| **Plans Service** | 8011 | 🟡 Optional | PostgreSQL, Redis | `uvicorn main:app --port 8011` |
| **BCM Coordination** | 8070 | 🟡 Optional | All BCM Services | `uvicorn main:app --port 8070` |

**Startup Script:**
```bash
# platform-services/start-platform-services.sh
cd platform-services
for service in bia-service risk-service compliance-service governance-service documents-service validation-service; do
    cd $service
    uvicorn main:app --port $(cat .port) &
    cd ..
done
```

---

### 🧠 Layer 3: Intelligent Core (ЗАПУСКАЕМ ТРЕТЬИМИ)

| Module | Port | Status | Dependencies | Command |
|--------|------|--------|--------------|---------|
| **AI Foundation** | 8020 | 🔴 Required | Redis, Qdrant | `python main.py --port 8020` |
| **Workflow Intelligence** | 8021 | 🔴 Required | AI Foundation | `python main.py --port 8021` |
| **Orchestration** | 8022 | 🔴 Required | All Platform Services | `python main.py --port 8022` |
| **Expertise Center** | 8023 | 🟡 Optional | AI Foundation | `python main.py --port 8023` |
| **Collective** | 8024 | 🟡 Optional | Workflow Intelligence | `python main.py --port 8024` |
| **Community Intelligence** | 8025 | 🟡 Optional | Community Service | `python main.py --port 8025` |
| **Predictive** | 8026 | 🟡 Optional | All Services | `python main.py --port 8026` |
| **Workflow Engine** | 8027 | 🟡 Optional | Workflow Intelligence | `python main.py --port 8027` |
| **Event Intelligence** | 8028 | 🟡 Optional | RabbitMQ | `python main.py --port 8028` |
| **AI Workflow Optimizer** | 8029 | 🟡 Optional | Workflow Intelligence | `python main.py --port 8029` |

**Startup Script:**
```bash
# intelligent-core/start-intelligent-core.sh
cd intelligent-core
python ai-foundation/main.py --port 8020 &
python workflow_intelligence/main.py --port 8021 &
python orchestration/main.py --port 8022 &
```

---

### 🤖 Layer 4: AI-Office Infrastructure (РЕКОМЕНДУЕТСЯ для Phase 2.1)

| Component | Port | Status | Dependencies | Command |
|-----------|------|--------|--------------|---------|
| **Service Discovery v2.0** | 8500 | 🔴 Required | Service Catalog, EventBus | `uvicorn main:app --port 8500` |
| **MIO Manager (EYES)** | 8046 | 🔴 Required | Service Discovery, Prometheus, EventBus | `uvicorn main:app --port 8046` |
| **DB Intelligence** | 8050 | 🟢 Optional | PostgreSQL | `python main.py --port 8050` |
| **AI Event Manager** | 8055 | 🟢 Optional | EventBus | `python main:app --port 8055` |
| **DevOps Agent** | 8060 | 🟢 Optional | MIO Manager, EventBus | `uvicorn main:app --port 8060` |
| **Analytics Specialist** | 8051 | 🟢 Optional | MIO Manager | `uvicorn main:app --port 8051` |

**Startup Script (Phase 2.1):**
```bash
# infrastructure/AI-office-infrastructure/start-ai-office.sh

# ВАЖНО: Запускать ПОСЛЕ Infrastructure Layer 1 (Redis, Prometheus)

# 1. Service Discovery v2.0 (required for MIO)
cd infrastructure/runtime/service-discovery
uvicorn main:app --port 8500 &
sleep 3

# 2. MIO Manager EYES (observes Service Discovery events)
cd ../../AI-office-infrastructure/mio-manager
uvicorn main:app --port 8046 &
sleep 3

# 3. Optional AI Office components
cd ../db-intelligence
python main.py --port 8050 &

cd ../ai-event-manager
python main:app --port 8055 &

cd ../devops-agent
uvicorn main:app --port 8060 &

cd ../analytics-specialist
uvicorn main:app --port 8051 &
```

---

### 🖥️ Layer 5: Interface (ЗАПУСКАЕМ ПОСЛЕДНИМИ)

| Application | Port | Status | Dependencies | Command |
|-------------|------|--------|--------------|---------|
| **Web App** | 3000 | 🔴 Required | Gateway (8080) | `npm start` |
| **Admin Panel** | 3002 | 🟡 Optional | All Services | `npm start` |
| **Admin Control Center** | 3003 | 🟡 Optional | All Services | `npm start` |
| **FastAPI Dashboard** | 8000 | 🟡 Optional | All Services | `uvicorn main:app --port 8000` |

**Startup Script:**
```bash
# interface/start-interface.sh
cd interface/web-app
npm start &
```

---

## 🆕 PHASE 2.1: EVENT-DRIVEN ARCHITECTURE (Oct 11, 2025)

### Новая архитектура: MIO EYES Observatory

**Ключевые изменения:**
1. **Service Discovery v2.0** - Unified Catalog + Registry + Event Broadcasting
2. **MIO Manager EYES** - Observatory pattern (observes, doesn't command)
3. **Event-Driven Choreography** - Services react autonomously to observations
4. **Service Catalog v2.0** - 27 services with 13-section schema

### Порядок запуска Phase 2.1:

```bash
# 1. Infrastructure (Base)
docker-compose -f infrastructure/observability/docker-compose.monitoring.yml up -d
# → Redis (6379), Prometheus (9090), Grafana (3001)

# 2. Service Discovery v2.0 (loads Service Catalog)
cd infrastructure/runtime/service-discovery
uvicorn main:app --port 8500

# 3. MIO Manager EYES (subscribes to Service Discovery events)
cd ../../AI-office-infrastructure/mio-manager
uvicorn main:app --port 8046

# 4. AI Event Manager (receives observations)
cd ../ai-event-manager
python main:app --port 8055

# 5. DevOps Agent (executes auto-fixes based on observations)
cd ../devops-agent
uvicorn main:app --port 8060
```

### Event Flow (Phase 2.1):

```
1. Service registers → Service Discovery publishes event
                    ↓
2. MIO EYES observes → Checks if monitored by Prometheus
                    ↓
3. If NOT monitored → Publishes observation event
                    ↓
4. DevOps Agent receives → Adds service to Prometheus config
                    ↓
5. Verification → MIO confirms service now monitored
```

### Observation Cycles:

- **Metrics Coverage** (every 5 min): Service Discovery vs Prometheus comparison
- **Metrics Health** (every 1 min): Endpoint accessibility, scrape freshness
- **Service Events** (real-time): Service registration/deregistration

### Integration Points:

```
Service Discovery v2.0 (8500)
    ↓ (publishes events)
EventBus (Redis Streams)
    ↓ (subscribes)
MIO Manager EYES (8046)
    ↓ (publishes observations)
EventBus
    ↓ (subscribers)
AI Event Manager (8055) + DevOps Agent (8060)
```

---

## 🚀 ПОЭТАПНЫЙ ЗАПУСК (RECOMMENDED)

### ФАЗА 1: Базовая инфраструктура (5 минут)

```bash
# Терминал 1: PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=bcm_platform \
  -p 5432:5432 \
  postgres:15

# Терминал 2: Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7

# Терминал 3: RabbitMQ
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management

# Проверка
echo "Waiting for services..."
sleep 10
docker ps | grep -E "postgres|redis|rabbitmq"
```

**Проверка:** Все 3 контейнера запущены ✅

---

### ФАЗА 2: Основные BCM сервисы (10 минут)

```bash
# Запускаем 6 основных сервисов
cd /Users/MD/AI-Platform-ISO/platform-services

# BIA Service (Port 8001)
cd bia-service
uvicorn main:app --host 0.0.0.0 --port 8001 &
cd ..

# Risk Service (Port 8002)
cd risk-service
uvicorn main:app --host 0.0.0.0 --port 8002 &
cd ..

# Compliance Service (Port 8003)
cd compliance-service
uvicorn main:app --host 0.0.0.0 --port 8003 &
cd ..

# Governance Service (Port 8004)
cd governance-service
uvicorn main:app --host 0.0.0.0 --port 8004 &
cd ..

# Documents Service (Port 8005)
cd documents-service
uvicorn main:app --host 0.0.0.0 --port 8005 &
cd ..

# Validation Service (Port 8006)
cd validation-service
uvicorn main:app --host 0.0.0.0 --port 8006 &
cd ..

# Проверка
sleep 5
lsof -i :8001-8006 | grep LISTEN
```

**Проверка:** 6 сервисов слушают порты 8001-8006 ✅

---

### ФАЗА 3: API Gateway (5 минут)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/gateway
uvicorn main:app --host 0.0.0.0 --port 8080 &

# Проверка
sleep 3
curl http://localhost:8080/health
```

**Проверка:** Gateway отвечает на /health ✅

---

### ФАЗА 4: Intelligent Core (опционально, 10 минут)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core

# AI Foundation (Port 8020)
cd ai-foundation
python main.py --port 8020 &
cd ..

# Workflow Intelligence (Port 8021)
cd workflow_intelligence
python main.py --port 8021 &
cd ..

# Orchestration (Port 8022)
cd orchestration
python main.py --port 8022 &
cd ..
```

**Проверка:** Intelligent Core модули запущены ✅

---

### ФАЗА 5: Frontend (5 минут)

```bash
cd /Users/MD/AI-Platform-ISO/interface/web-app
npm install  # если еще не установлено
npm start
```

**Проверка:** Браузер открывается на http://localhost:3000 ✅

---

## 🔍 ПРОВЕРКА ЗАПУЩЕННЫХ СЕРВИСОВ

### Быстрая проверка портов

```bash
# Проверить все занятые порты
lsof -i :5432,6379,5672,8001,8002,8003,8004,8005,8006,8080,3000

# Или через netstat
netstat -an | grep LISTEN | grep -E "5432|6379|5672|8001|8002|8003|8004|8005|8006|8080|3000"
```

### Health Check всех сервисов

```bash
#!/bin/bash
# check-all-health.sh

echo "🔍 Checking all services health..."

# Infrastructure
curl -s http://localhost:8080/health && echo "✅ Gateway"

# Platform Services
curl -s http://localhost:8001/health && echo "✅ BIA Service"
curl -s http://localhost:8002/health && echo "✅ Risk Service"
curl -s http://localhost:8003/health && echo "✅ Compliance Service"
curl -s http://localhost:8004/health && echo "✅ Governance Service"
curl -s http://localhost:8005/health && echo "✅ Documents Service"
curl -s http://localhost:8006/health && echo "✅ Validation Service"

# Frontend
curl -s http://localhost:3000 && echo "✅ Web App"
```

---

## 🛑 ОСТАНОВКА СЕРВИСОВ

### Полная остановка

```bash
#!/bin/bash
# stop-all-services.sh

echo "🛑 Stopping all services..."

# Kill all uvicorn processes
pkill -f "uvicorn main:app"

# Kill all Python services
pkill -f "python main.py"

# Stop Docker containers
docker stop postgres redis rabbitmq
docker rm postgres redis rabbitmq

# Stop frontend
pkill -f "npm start"

echo "✅ All services stopped"
```

### Остановка по слоям

```bash
# Остановить только Platform Services
pkill -f "uvicorn main:app --port 800"

# Остановить только Intelligent Core
pkill -f "python main.py --port 802"

# Остановить только Infrastructure
docker stop postgres redis rabbitmq
```

---

## 🔧 КОНФЛИКТЫ ПОРТОВ - РЕШЕНИЯ

### Если порт занят

```bash
# Найти процесс на порту 8001
lsof -i :8001

# Убить процесс
kill -9 <PID>

# Или освободить порт
sudo lsof -ti:8001 | xargs kill -9
```

### Альтернативные порты

Если основные порты заняты, используй альтернативные:

| Service | Default | Alternative |
|---------|---------|-------------|
| PostgreSQL | 5432 | 5433, 5434 |
| Redis | 6379 | 6380, 6381 |
| RabbitMQ | 5672 | 5673, 5674 |
| Gateway | 8080 | 8081, 8082 |
| BIA Service | 8001 | 8101, 8201 |

**Как изменить порт:**
```bash
# В .env файле сервиса
PORT=8101

# Или при запуске
uvicorn main:app --port 8101
```

---

## 📋 МИНИМАЛЬНАЯ КОНФИГУРАЦИЯ (Для тестов)

Если нужно запустить только минимум для тестирования:

```bash
# 1. PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  postgres:15

# 2. Redis
docker run -d -p 6379:6379 redis:7

# 3. BIA Service
cd platform-services/bia-service
uvicorn main:app --port 8001

# 4. Gateway
cd infrastructure/gateway
uvicorn main:app --port 8080

# 5. Web App
cd interface/web-app
npm start
```

**Это даст тебе:** База данных + Один сервис + Gateway + Frontend

---

## 🎯 РЕКОМЕНДУЕМАЯ КОНФИГУРАЦИЯ

### Для разработки

```
✅ PostgreSQL (5432)
✅ Redis (6379)
✅ RabbitMQ (5672)
✅ Gateway (8080)
✅ BIA Service (8001)
✅ Risk Service (8002)
✅ Compliance Service (8003)
✅ Web App (3000)
```

### Для production

```
✅ Все Infrastructure
✅ Все 11 Platform Services
✅ Gateway
✅ AI Foundation
✅ Workflow Intelligence
✅ Orchestration
✅ All Frontend Apps
```

---

## 🚨 TROUBLESHOOTING

### Проблема: Сервис не запускается

```bash
# Проверь логи
tail -f logs/service.log

# Проверь переменные окружения
cat .env

# Проверь зависимости
pip list | grep fastapi
```

### Проблема: База недоступна

```bash
# Проверь PostgreSQL
docker logs postgres

# Попробуй подключиться
psql -h localhost -U postgres -d bcm_platform
```

### Проблема: Порт занят

```bash
# Найди и убей процесс
lsof -ti:8001 | xargs kill -9

# Или используй другой порт
uvicorn main:app --port 8101
```

---

## 📊 МОНИТОРИНГ

### Dashboard URLs

После запуска доступны:

- **RabbitMQ UI:** http://localhost:15672 (guest/guest)
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001 (admin/admin)
- **API Gateway:** http://localhost:8080
- **Web App:** http://localhost:3000

---

## 🎓 ПРИМЕРЫ ЗАПУСКА

### Пример 1: Быстрый старт (5 минут)

```bash
# Терминал 1
docker-compose -f infrastructure/docker-compose.yml up

# Терминал 2
cd platform-services/bia-service && uvicorn main:app --port 8001

# Терминал 3
cd infrastructure/gateway && uvicorn main:app --port 8080

# Терминал 4
cd interface/web-app && npm start
```

### Пример 2: Полный запуск (20 минут)

```bash
# Используй мастер-скрипт
./deployment/start-all-services.sh
```

---

## 📝 CHECKLIST ЗАПУСКА

```
☐ Установлены Docker, Python 3.11+, Node.js 18+
☐ Клонирован репозиторий
☐ Установлены зависимости (pip install, npm install)
☐ Созданы .env файлы
☐ Запущена Infrastructure (PostgreSQL, Redis, RabbitMQ)
☐ Запущены Platform Services
☐ Запущен Gateway
☐ Запущен Frontend
☐ Проверены health checks
☐ Открыт браузер на localhost:3000
```

---

## 🚀 ГОТОВО!

После выполнения всех шагов у тебя будет:

✅ Работающая база данных  
✅ Все необходимые сервисы  
✅ API Gateway  
✅ Frontend приложение  
✅ Мониторинг (опционально)  

**ПОЕХАЛИ!** 🔥

---

## 📝 PHASE 2.1 CHECKLIST (NEW - Oct 11, 2025)

```
☐ Infrastructure базовая запущена (PostgreSQL, Redis, Prometheus)
☐ Service Catalog v2.0 проверен (27 services, /runtime/service-catalog/service-catalog.yaml)
☐ Service Discovery v2.0 запущен на порту 8500
☐ MIO Manager EYES запущен на порту 8046
☐ EventBus (Redis Streams) работает
☐ Prometheus доступен на порту 9090
☐ MIO EYES подписан на события Service Discovery
☐ Observability stack merged (/infrastructure/observability/)
☐ Alert rules загружены (orchestrator-alerts.yml)
☐ Grafana dashboards доступны
☐ Observation cycles работают (Coverage: 5 min, Health: 1 min)
```

### Проверка Phase 2.1:

```bash
# 1. Service Discovery v2.0
curl http://localhost:8500/v2/catalog/services | jq

# 2. MIO Manager EYES
curl http://localhost:8046/health

# 3. Prometheus targets
curl http://localhost:9090/api/v1/targets

# 4. Service Catalog
cat /Users/MD/AI-Platform-ISO/infrastructure/runtime/service-catalog/service-catalog.yaml | grep "version:"
# Expected: version: 2.0.0
```

---

## 📚 ДОКУМЕНТАЦИЯ

### Phase 2.1 Документация:

- **MIO Manager:** `/infrastructure/AI-office-infrastructure/mio-manager/START_HERE.md`
- **Quick Reference:** `/infrastructure/AI-office-infrastructure/mio-manager/QUICK_MONITORING_OVERVIEW.md`
- **Service Catalog Schema:** `/infrastructure/runtime/service-catalog/CATALOG_SCHEMA.md`
- **Service Catalog Quick Ref:** `/infrastructure/runtime/service-catalog/QUICK_REFERENCE.md`
- **Component Catalog:** `/infrastructure/FULL_COMPONENT_CATALOG.md` (updated Oct 11)
- **Cleanup Report:** `/infrastructure/AI-office-infrastructure/mio-manager/CLEANUP_COMPLETE.md`

---

**Version:** 2.1.0 (Phase 2.1 Complete)
**Date:** 2025-10-11 (Updated after Phase 2.1 & Monitoring Cleanup)
**Status:** Production Ready - Event-Driven Architecture
**Architecture:** MIO EYES Observatory + Event-Driven Choreography
