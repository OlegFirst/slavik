# Infrastructure Services Catalog
**Generated:** 2025-10-10 02:45:00 UTC
**Total Services:** 24
**Running:** 5/24 (21%)
**Ready to Launch:** 9/24 (38%)
**Missing Files:** 10/24 (42%)

---

## 📊 Summary by Category

| Category | Total | Running | Ready | Missing Files |
|----------|-------|---------|-------|---------------|
| **AI Office Infrastructure** | 8 | 0 | 4 | 4 |
| **Gateway** | 3 | 0 | 3 | 0 |
| **Observability** | 6 | 3 | 3 | 0 |
| **Runtime** | 3 | 1 | 1 | 2 |
| **Security** | 4 | 1 | 2 | 2 |
| **Integration** | 3 | 0 | 1 | 2 |
| **Balancer** | 1 | 0 | 0 | 1 |
| **TOTAL** | **24** | **5** | **9** | **10** |

---

## 1. AI Office Infrastructure (8 сервисов)

### ✅ ai-event-manager
- **Port:** 8055
- **Status:** 🟡 Ready to Launch
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:** Нет
- **Команда запуска:**
  ```bash
  cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager
  python3 main.py
  ```

### ✅ analytics-specialist
- **Port:** Not configured (needs port assignment)
- **Status:** 🟡 Ready to Launch
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:**
  - ⚠️ Порт не указан в main.py
  - Нужно добавить `uvicorn.run(app, host="0.0.0.0", port=XXXX)`
- **Рекомендуемый порт:** 8056

### ✅ db-intelligence
- **Port:** 8050 (DB_INTELLIGENCE_PORT)
- **Status:** 🔴 Port Conflict
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:**
  - ❌ **КОНФЛИКТ ПОРТА 8050** с monitoring-backend
  - monitoring-backend уже запущен на 8050
- **Решение:**
  ```bash
  export DB_INTELLIGENCE_PORT=8051
  cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/db-intelligence
  python3 main.py
  ```

### ✅ mio-manager
- **Port:** 8046
- **Status:** 🟡 Ready to Launch
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:** Нет
- **Команда запуска:**
  ```bash
  cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/mio-manager
  python3 main.py
  ```

### ❌ agent-router
- **Port:** Unknown
- **Status:** 🔴 Missing main.py
- **Files:** ❌ main.py, ✅ requirements.txt
- **Проблемы:**
  - ❌ **main.py не существует**
  - Сервис не реализован или перемещен
- **Решение:** Проверить архитектуру, возможно сервис deprecated

### ❌ devops-agent
- **Port:** Unknown
- **Status:** 🔴 Missing Files
- **Files:** ❌ main.py, ❌ requirements.txt
- **Проблемы:**
  - ❌ **Нет main.py и requirements.txt**
  - Сервис не реализован
- **Решение:** Реализовать сервис или удалить директорию

### ❌ orchestrator
- **Port:** Unknown
- **Status:** 🔴 Missing main.py
- **Files:** ❌ main.py, ✅ requirements.txt
- **Проблемы:**
  - ❌ **main.py не существует**
  - requirements.txt есть, но код отсутствует
- **Решение:** Реализовать main.py или deprecate

### ❌ project-agent
- **Port:** Unknown
- **Status:** 🔴 Missing main.py
- **Files:** ❌ main.py, ✅ requirements.txt
- **Проблемы:**
  - ❌ **main.py не существует**
- **Решение:** Реализовать или удалить

---

## 2. Gateway (3 сервиса)

### ✅ gateway/api-gateway
- **Port:** 8080 (из settings)
- **Status:** 🟡 Ready to Launch
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:** Нет
- **Особенности:**
  - Использует Pydantic Settings для конфигурации
  - Поддерживает JWT auth, rate limiting, circuit breaker
  - Маршрутизация на все микросервисы
- **Команда запуска:**
  ```bash
  cd /Users/MD/AI-Platform-ISO/infrastructure/gateway/api-gateway
  python3 main.py
  ```

### ✅ security/api-gateway
- **Port:** Unknown (нужно проверить settings)
- **Status:** 🟡 Ready to Launch (возможный дубликат)
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:**
  - ⚠️ **Возможный дубликат** gateway/api-gateway
  - Два api-gateway в разных директориях
- **Решение:**
  - Проверить различия между двумя gateway
  - Выбрать один как основной
  - Второй переименовать или deprecate

### 🗑️ gateway/_deprecated_unified_database_gateway
- **Port:** Unknown
- **Status:** 🔴 Deprecated
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:**
  - ⚠️ **Deprecated** (указано в названии директории)
- **Решение:** Переместить в _archive

---

## 3. Observability (6 сервисов)

### ✅ prometheus (9090) 🟢 RUNNING
- **Port:** 9090
- **Status:** 🟢 RUNNING
- **Health:** http://localhost:9090/-/healthy
- **Targets:** 9 configured, 5 healthy
- **Проблемы:** Нет
- **Команда:**
  ```bash
  prometheus --config.file=/Users/MD/AI-Platform-ISO/infrastructure/monitoring/prometheus/prometheus.yml --web.enable-lifecycle
  ```

### ✅ monitoring-backend (8050) 🟢 RUNNING
- **Port:** 8050
- **Status:** 🟢 RUNNING
- **Health:** http://localhost:8050/health
- **Dependencies:** Prometheus (connected)
- **Проблемы:**
  - ⚠️ **КОНФЛИКТ ПОРТА** с db-intelligence (также хочет 8050)
- **Dashboard:** Real-time metrics (MOCK data removed ✅)

### ✅ notification-service (8083) 🟢 RUNNING
- **Port:** 8083
- **Status:** 🟢 RUNNING
- **Health:** http://localhost:8083/
- **Dependencies:** Redis (connected), Supabase (not configured)
- **Warnings:**
  - ⚠️ Supabase not configured - notifications cached in Redis only
  - ⚠️ RabbitMQ not configured - direct delivery only
  - ℹ️ Using deprecated @app.on_event (migrate to lifespan)

### 🟡 node-exporter
- **Port:** 9100
- **Status:** 🟡 Ready to Launch
- **Binary:** Requires binary installation
- **Проблемы:**
  - ⚠️ Не установлен (используются process metrics вместо node metrics)
- **Установка:**
  ```bash
  brew install node_exporter
  node_exporter
  ```

### 🟡 alertmanager
- **Port:** 9093
- **Status:** 🟡 Ready to Launch
- **Binary:** Requires binary installation
- **Проблемы:**
  - ⚠️ Не установлен (alerts не отправляются)
- **Установка:**
  ```bash
  brew install alertmanager
  alertmanager --config.file=/Users/MD/AI-Platform-ISO/infrastructure/monitoring/alertmanager/config.yml
  ```

### 🟡 grafana
- **Port:** 3000
- **Status:** 🟡 Ready to Launch
- **Binary:** Requires binary installation
- **Проблемы:**
  - ⚠️ Не установлен (нет визуализации метрик)
- **Установка:**
  ```bash
  brew install grafana
  brew services start grafana
  ```

---

## 4. Runtime (3 сервиса)

### ✅ realtime-websocket (8082) 🟢 RUNNING
- **Port:** 8082
- **Status:** 🟢 RUNNING
- **Health:** http://localhost:8082/health
- **Dependencies:** Redis (connected), PostgreSQL (database not exist)
- **Warnings:**
  - ❌ Database "bcm_realtime" does not exist
  - Service runs in Redis-only mode
- **Решение:**
  ```sql
  -- Create database in PostgreSQL
  CREATE DATABASE bcm_realtime;
  ```

### ❌ message-queue
- **Port:** Unknown
- **Status:** 🔴 Missing main.py
- **Files:** ❌ main.py, ✅ requirements.txt
- **Проблемы:**
  - ❌ **main.py не существует**
- **Решение:** Реализовать или использовать внешний RabbitMQ

### ❌ service-discovery
- **Port:** 8500 (стандартный Consul)
- **Status:** 🔴 Missing Files
- **Files:** ❌ main.py, ❌ requirements.txt
- **Проблемы:**
  - ❌ **Нет файлов реализации**
- **Решение:**
  - Вариант 1: Использовать внешний Consul
  - Вариант 2: Реализовать простой service registry на FastAPI

---

## 5. Security (4 сервиса)

### ✅ auth (8081) 🟢 RUNNING
- **Port:** 8081
- **Status:** 🟢 RUNNING
- **Health:** http://localhost:8081/health
- **Dependencies:** Supabase
- **Features:** JWT auth, user registration/login, token validation
- **Проблемы:**
  - ⚠️ requirements.txt отсутствует (зависимости не документированы)

### ✅ security/api-gateway
- **Port:** Unknown
- **Status:** 🟡 Ready to Launch (дубликат?)
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:** См. раздел Gateway выше

### ❌ secrets-management
- **Port:** Unknown
- **Status:** 🔴 Missing Files
- **Files:** ❌ main.py, ❌ requirements.txt
- **Проблемы:**
  - ❌ **Нет main.py и requirements.txt**
- **Решение:**
  - Вариант 1: Использовать HashiCorp Vault
  - Вариант 2: Реализовать на FastAPI с интеграцией в Supabase

### ❌ secrets-manager
- **Port:** Unknown
- **Status:** 🔴 Missing main.py
- **Files:** ❌ main.py, ✅ requirements.txt
- **Проблемы:**
  - ❌ **main.py не существует**
  - ⚠️ Возможно дубликат secrets-management
- **Решение:** Объединить с secrets-management или удалить

---

## 6. Integration (3 сервиса)

### ✅ github-integration
- **Port:** Unknown
- **Status:** 🟡 Ready to Launch
- **Files:** ✅ main.py, ✅ requirements.txt
- **Проблемы:**
  - ⚠️ Порт не указан в main.py
- **Рекомендуемый порт:** 8085
- **Команда запуска:**
  ```bash
  cd /Users/MD/AI-Platform-ISO/infrastructure/integration/github-integration
  PORT=8085 python3 main.py
  ```

### ❌ mcp-server
- **Port:** Unknown
- **Status:** 🔴 Missing main.py
- **Files:** ❌ main.py, ✅ requirements.txt
- **Проблемы:**
  - ❌ **main.py не существует**
- **Решение:** Реализовать MCP server или deprecate

### ❌ partisia-contracts
- **Port:** Unknown
- **Status:** 🔴 Missing Files
- **Files:** ❌ main.py, ❌ requirements.txt
- **Проблемы:**
  - ❌ **Нет файлов реализации**
- **Решение:** Реализовать интеграцию с Partisia или удалить

---

## 7. Balancer (1 сервис)

### ❌ balancer-service
- **Port:** Unknown
- **Status:** 🔴 Needs Investigation
- **Files:** ✅ main.py (предполагается)
- **Проблемы:**
  - ⚠️ Не проверен (нужно исследовать код)
- **Решение:** Проверить main.py и определить статус

---

## 🔥 Критические Проблемы

### 1. Конфликт порта 8050
- **Сервисы:** monitoring-backend (запущен) vs db-intelligence (не запущен)
- **Impact:** db-intelligence не может запуститься
- **Решение:**
  ```bash
  export DB_INTELLIGENCE_PORT=8051
  ```

### 2. Дубликаты api-gateway
- **Locations:**
  - `/infrastructure/gateway/api-gateway`
  - `/infrastructure/security/api-gateway`
- **Impact:** Неясно какой использовать, возможна путаница
- **Решение:** Определить основной, второй переименовать или удалить

### 3. Missing main.py (10 сервисов)
- **Сервисы:** agent-router, devops-agent, orchestrator, project-agent, message-queue, service-discovery, secrets-management, secrets-manager, mcp-server, partisia-contracts
- **Impact:** 42% Infrastructure сервисов не могут запуститься
- **Решение:** Реализовать или переместить в _archive

### 4. Missing Database
- **Service:** realtime-websocket
- **Database:** bcm_realtime
- **Impact:** Service runs without persistent storage
- **Решение:**
  ```sql
  CREATE DATABASE bcm_realtime;
  ```

### 5. Missing External Dependencies
- **node-exporter:** Нет системных метрик (CPU, Memory, Disk)
- **alertmanager:** Нет управления алертами
- **grafana:** Нет визуализации метрик
- **Решение:** Установить через brew

---

## 📋 Приоритет Запуска

### Priority 1: Core Infrastructure (критично)
1. ✅ **prometheus** (9090) - запущен
2. ✅ **monitoring-backend** (8050) - запущен
3. ✅ **auth-service** (8081) - запущен
4. 🟡 **gateway/api-gateway** (8080) - готов к запуску

### Priority 2: Real-time & Notifications
5. ✅ **realtime-websocket** (8082) - запущен (с warnings)
6. ✅ **notification-service** (8083) - запущен (с warnings)

### Priority 3: AI Office Infrastructure
7. 🟡 **ai-event-manager** (8055) - готов к запуску
8. 🟡 **mio-manager** (8046) - готов к запуску
9. 🟡 **db-intelligence** (8051) - готов (после смены порта)
10. 🟡 **analytics-specialist** (8056) - готов (после добавления порта)

### Priority 4: External Tools
11. 🟡 **node-exporter** (9100) - установить
12. 🟡 **alertmanager** (9093) - установить
13. 🟡 **grafana** (3000) - установить

### Priority 5: Integration
14. 🟡 **github-integration** (8085) - готов к запуску

---

## 🎯 Рекомендации

### Immediate Actions (сейчас)
1. **Запустить gateway/api-gateway** - центральный роутинг для всех сервисов
2. **Установить node-exporter** - получить системные метрики в Prometheus
3. **Создать базу bcm_realtime** - включить persistent storage для websocket

### Short-term (на этой неделе)
4. **Разрешить конфликт db-intelligence порта** - переназначить на 8051
5. **Определить статус дубликатов api-gateway** - выбрать основной
6. **Запустить AI Office services** - ai-event-manager, mio-manager
7. **Установить Grafana** - визуализация метрик

### Medium-term (следующая неделя)
8. **Audit missing main.py services** - реализовать или архивировать
9. **Implement service-discovery** - или использовать Consul
10. **Configure Supabase for notifications** - persistent storage
11. **Setup RabbitMQ** - async notification delivery

### Long-term (месяц)
12. **Migrate to lifespan handlers** - убрать deprecated @app.on_event
13. **Implement secrets-management** - или интегрировать Vault
14. **Complete Integration services** - mcp-server, partisia-contracts
15. **Load testing** - проверить performance всех сервисов

---

## 📊 Port Allocation Map

| Port | Service | Status | Category |
|------|---------|--------|----------|
| 3000 | grafana | Not installed | Observability |
| 8046 | mio-manager | Ready | AI Office |
| 8050 | monitoring-backend | 🟢 Running | Observability |
| 8051 | db-intelligence | Ready (reassigned) | AI Office |
| 8055 | ai-event-manager | Ready | AI Office |
| 8056 | analytics-specialist | Ready (needs config) | AI Office |
| 8080 | api-gateway | Ready | Gateway |
| 8081 | auth-service | 🟢 Running | Security |
| 8082 | realtime-websocket | 🟢 Running | Runtime |
| 8083 | notification-service | 🟢 Running | Observability |
| 8085 | github-integration | Ready | Integration |
| 9090 | prometheus | 🟢 Running | Observability |
| 9093 | alertmanager | Not installed | Observability |
| 9100 | node-exporter | Not installed | Observability |

**Legend:**
- 🟢 Running - сервис запущен и работает
- Ready - готов к запуску (есть все файлы)
- Not installed - требует внешней установки
- Missing - отсутствуют файлы реализации

---

## 🚀 Quick Launch Commands

### Launch Core Infrastructure
```bash
# Kill existing processes
killall -9 prometheus python3 2>/dev/null; sleep 3

# 1. Prometheus
prometheus --config.file=/Users/MD/AI-Platform-ISO/infrastructure/monitoring/prometheus/prometheus.yml --web.enable-lifecycle > /tmp/prometheus.log 2>&1 &

# 2. monitoring-backend
cd /Users/MD/AI-Platform-ISO/infrastructure/observability/monitoring-backend
python3 main.py > /tmp/monitoring_backend.log 2>&1 &

# 3. auth-service
cd /Users/MD/AI-Platform-ISO/infrastructure/security/auth
PORT=8081 python3 main.py > /tmp/auth.log 2>&1 &

# 4. realtime-websocket
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/realtime-websocket
export PORT=8082 && python3 main.py > /tmp/realtime_ws.log 2>&1 &

# 5. notification-service
cd /Users/MD/AI-Platform-ISO/infrastructure/observability/notification-service
PORT=8083 python3 main.py > /tmp/notification.log 2>&1 &

# 6. api-gateway
cd /Users/MD/AI-Platform-ISO/infrastructure/gateway/api-gateway
python3 main.py > /tmp/gateway.log 2>&1 &
```

### Launch AI Office Infrastructure
```bash
# 7. ai-event-manager
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager
python3 main.py > /tmp/ai_event_manager.log 2>&1 &

# 8. mio-manager
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/mio-manager
python3 main.py > /tmp/mio_manager.log 2>&1 &

# 9. db-intelligence (reassigned port)
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/db-intelligence
export DB_INTELLIGENCE_PORT=8051 && python3 main.py > /tmp/db_intelligence.log 2>&1 &
```

### Verify All Services
```bash
sleep 5
echo "=== Infrastructure Health Check ==="
curl -s http://localhost:9090/-/healthy && echo "✅ Prometheus"
curl -s http://localhost:8050/health | grep -q healthy && echo "✅ monitoring-backend"
curl -s http://localhost:8081/health | grep -q healthy && echo "✅ auth-service"
curl -s http://localhost:8082/health | grep -q healthy && echo "✅ realtime-websocket"
curl -s http://localhost:8083/ | grep -q BCM && echo "✅ notification-service"
curl -s http://localhost:8080/health | grep -q healthy && echo "✅ api-gateway"
curl -s http://localhost:8055/health | grep -q healthy && echo "✅ ai-event-manager"
curl -s http://localhost:8046/health | grep -q healthy && echo "✅ mio-manager"
curl -s http://localhost:8051/health | grep -q healthy && echo "✅ db-intelligence"
```

---

**Last Updated:** 2025-10-10 02:45:00 UTC
**Updated By:** Claude (Infrastructure Audit)
**Next Review:** After launching remaining services and resolving conflicts
