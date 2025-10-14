# REAL_SYSTEM_ARCHITECTURE.md - Update v2.0.0

**Дата**: 2025-10-12
**Статус**: ✅ Complete

---

## 🎯 ЧТО ОБНОВЛЕНО

Добавлены **4 missing компонента** из каталогов:
1. ✅ **API Gateway** (Port 8000)
2. ✅ **Service Discovery** (Port 8500, Consul)
3. ✅ **Prometheus** (Port 9090)
4. ✅ **Grafana** (Port 3000)

---

## 📝 ИЗМЕНЕНИЯ ПО ФАЗАМ

### PHASE 0 (NEW!) - API Gateway Entry Point

**Добавлено**:
- 7 шагов обработки запроса в API Gateway
- JWT validation (Auth Service)
- Rate limiting (Redis, token bucket)
- Service Discovery lookup (Consul)
- Load balancing (round-robin)
- Circuit breaker check
- Request routing
- Audit logging

**Номера шагов**: 0-2 (новые)

---

### PHASE 4 (РАСШИРЕН) - Service Discovery Integration

**Добавлено**:
- Step 12: AI Orchestration → Service Discovery
- 3 query запроса к Consul:
  1. db-intelligence → 10.0.1.15:8051
  2. devops-agent → 10.0.1.18:8097
  3. scenario-intelligence → 10.0.1.25:8090
- Response с ServiceMeta (version, health, last_check)

---

### PHASE 10 (РАСШИРЕН) - Prometheus + Grafana Observability

**Добавлено**:

**Step 30: Prometheus** (Port 9090)
- Scraping /metrics from 30+ services every 15s
- Time-series storage (15 days retention)
- Alerting rules engine
- Alert: "DB Overload" (FIRING → RESOLVED)
- Sends to Alertmanager

**Step 31: Grafana** (Port 3000)
- Queries Prometheus data
- 4 panels:
  1. Service Health (30/30 healthy)
  2. DB Query Latency (график 5000ms → 800ms)
  3. EventBus Throughput (35 events)
  4. Resource Usage (connections, memory, CPU)
- 18 Pre-configured Dashboards
- Real-time updates
- Slack notifications

---

## 📊 ОБНОВЛЕННАЯ СТАТИСТИКА

### v1.0.0 (было):
- **Фазы**: 10 (Phase 1-10)
- **Шаги**: 28
- **События**: 28 EventBus
- **Компоненты**: 22

### v2.0.0 (стало):
- **Фазы**: 11 (Phase 0-10)
- **Шаги**: 32
- **События**: 35+ EventBus (28 scenario + 7 monitoring)
- **Компоненты**: 26

### Layer 0 (Infrastructure):
**v1.0.0**: 5 компонентов
- PostgreSQL, Redis, EventBus, MiO Manager, Digital Twin

**v2.0.0**: 9 компонентов ✅
- **API Gateway** (NEW!)
- **Service Discovery** (NEW!)
- PostgreSQL
- Redis
- EventBus
- **Prometheus** (NEW!)
- **Grafana** (NEW!)
- MiO Manager
- Balancer Service (упомянут)
- Digital Twin

---

## 🔥 КЛЮЧЕВЫЕ ВЫВОДЫ

### 1. API Gateway - Единая точка входа

**Было**: Запросы шли напрямую к сервисам
**Стало**: Все через API Gateway с:
- JWT authentication (<100ms)
- Rate limiting (10,000 req/min)
- Load balancing
- Circuit breaker
- Audit logging

### 2. Service Discovery - Динамическое обнаружение

**Было**: Hardcoded адреса сервисов
**Стало**: Consul registry с:
- Service registration
- Health checks (10s)
- Dynamic lookup (<50ms)
- Version tracking

### 3. Prometheus + Grafana - Observability

**Было**: Только MiO Manager
**Стало**: Полная observability stack:
- Prometheus scraping (15s)
- 30+ services monitored
- Grafana dashboards (18)
- Real-time alerts

---

## 📋 НОВЫЕ КОМПОНЕНТЫ В СЦЕНАРИИ

### API Gateway Integration:
```
External Request
   ↓
API Gateway (7 steps)
   ↓ JWT validation
   ↓ Rate limiting
   ↓ Service Discovery lookup
   ↓ Load balancing
   ↓ Circuit breaker check
   ↓ Route request
   ↓ Audit log
   ↓
Target Service (BIA Service)
```

### Service Discovery Integration:
```
AI Orchestration
   ↓
Service Discovery (Consul)
   ↓ Query: "Where is db-intelligence?"
   ↓ Response: {address: "10.0.1.15", port: 8051}
   ↓
Call Agent at address
```

### Observability Integration:
```
All Services expose /metrics
   ↓
Prometheus scrapes every 15s
   ↓ Stores time-series data
   ↓ Alerting rules engine
   ↓
Grafana queries Prometheus
   ↓ 18 dashboards
   ↓ Real-time visualization
   ↓ Slack alerts
```

---

## ✅ ПРОВЕРКА СООТВЕТСТВИЯ С КАТАЛОГАМИ

### SERVICE_CATALOG_DETAILED.yaml:
- ✅ API Gateway (Port 8000) - описан в каталоге
- ✅ Service Discovery (Port 8500) - описан в каталоге
- ✅ Prometheus (Port 9090) - описан в каталоге
- ✅ Grafana (Port 3000) - описан в каталоге

### SUBSYSTEMS_CATALOG.yaml:
- ✅ Gateway Layer (subsystem #3)
- ✅ Runtime Services (subsystem #2, включая Service Discovery)
- ✅ Observability (subsystem #4, включая Prometheus + Grafana)

### SYSTEMS_CATALOG.yaml:
- ✅ API & Communication System (functional system #7)
- ✅ Startup & Orchestration System (functional system #1)
- ✅ Monitoring & Observability System (functional system #4)

**Вердикт**: ✅ **ПОЛНОЕ СООТВЕТСТВИЕ** с каталогами!

---

## 🚀 ИСПОЛЬЗОВАНИЕ

Для моделирования новых сценариев:

1. **ВСЕГДА начинай с PHASE 0** (API Gateway)
2. **Используй Service Discovery** для lookup адресов сервисов
3. **Добавляй Prometheus + Grafana** в PHASE 10 для observability
4. **Проверяй каталоги** перед моделированием:
   - `/catalogs/services/SERVICE_CATALOG_DETAILED.yaml`
   - `/catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml`
   - `/catalogs/systems/SYSTEMS_CATALOG.yaml`

---

## 📁 ФАЙЛЫ

**Главный документ**:
- `/intelligent-core/scenario-intelligence/REAL_SYSTEM_ARCHITECTURE.md` (v2.0.0)

**Анализ каталогов**:
- `/catalogs/CATALOG_VS_REALITY_ANALYSIS.md`

**Этот summary**:
- `/intelligent-core/scenario-intelligence/UPDATE_V2_SUMMARY.md`

---

**Версия**: v2.0.0
**Дата**: 2025-10-12
**Автор**: Claude + User collaboration
**Статус**: ✅ Ready to use for scenario modeling
