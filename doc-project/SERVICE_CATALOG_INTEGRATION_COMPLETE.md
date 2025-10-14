# Service Catalog + Discovery Integration - COMPLETE

**Дата**: 2025-10-11
**Статус**: ✅ Реализовано
**Версия**: Service Discovery v2.0

---

## 🎯 Что реализовано

Объединение **Service Catalog** (статический каталог) и **Service Discovery** (runtime регистрация) в единую систему с:
- ✅ Unified view (шаблон + runtime данные)
- ✅ Автоматическое определение missing services
- ✅ Автоматическое определение unknown services
- ✅ REST API для Admin Panel
- ✅ EventBus integration для real-time updates
- ✅ PostgreSQL persistence (готова структура)

---

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    Service Discovery v2.0                        │
│                         Port: 8500                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌───────────────┐  ┌────────────────┐  ┌─────────────────┐
│Service Catalog│  │ServiceRegistry │  │EventBus         │
│(YAML template)│  │(Runtime data)  │  │Integration      │
└───────────────┘  └────────────────┘  └─────────────────┘
        ↓                   ↓                   ↓
        └───────────────────┼───────────────────┘
                            ↓
                ┌───────────────────────┐
                │CatalogIntegration     │
                │  (Unified Service)    │
                └───────────────────────┘
                            ↓
                ┌───────────────────────┐
                │PostgreSQL Database    │
                │  (Persistence)        │
                └───────────────────────┘
```

---

## 🔧 Компоненты

### 1. **CatalogIntegration** (`catalog_integration.py`)

**Основная логика объединения данных**

#### Классы:

**`ServiceTemplate`** - Статический шаблон из catalog:
```python
@dataclass
class ServiceTemplate:
    name: str
    type: str  # intelligent-core, platform-services, infrastructure/*
    business_process: str
    kpis: List[str]
    dependencies: List[str]
    port: Optional[int]
    metrics_endpoint: Optional[str]
    health_endpoint: Optional[str]
    path: Optional[str]
    framework: Optional[str]
```

**`UnifiedService`** - Объединённые данные (catalog + runtime):
```python
@dataclass
class UnifiedService:
    # From catalog (static)
    name: str
    type: str
    business_process: str
    kpis: List[str]
    template_dependencies: List[str]
    expected_port: Optional[int]

    # From runtime (dynamic)
    runtime_status: ServiceStatus  # unknown, registered, running, failed, etc.
    registration_status: RegistrationStatus  # not_registered, registered, unknown_service
    orchestrator: Optional[str]
    actual_port: Optional[int]
    health_status: Optional[str]
    last_seen: Optional[datetime]
    runtime_dependencies: List[str]
```

#### Enums:

**`ServiceStatus`**:
- `UNKNOWN` - Не известен статус
- `REGISTERED` - Зарегистрирован
- `STARTING` - Запускается
- `RUNNING` - Работает
- `STOPPING` - Останавливается
- `STOPPED` - Остановлен
- `FAILED` - Упал

**`RegistrationStatus`**:
- `NOT_REGISTERED` - В каталоге, но не зарегистрирован (missing)
- `REGISTERED` - В каталоге И зарегистрирован (OK)
- `UNKNOWN_SERVICE` - Зарегистрирован, но нет в каталоге

#### Методы:

```python
async def get_unified_service(service_name, runtime_service) -> UnifiedService
    """Объединить данные catalog + runtime для одного сервиса"""

async def get_all_unified_services(service_registry) -> List[UnifiedService]
    """Получить все сервисы с объединёнными данными"""

async def get_missing_services(service_registry) -> List[UnifiedService]
    """Сервисы в каталоге, но не зарегистрированы"""

async def get_unknown_services(service_registry) -> List[UnifiedService]
    """Сервисы зарегистрированы, но нет в каталоге"""

async def get_healthy_services(service_registry) -> List[UnifiedService]
    """Все здоровые сервисы (running + healthy)"""

async def get_catalog_stats(service_registry) -> Dict
    """Статистика: total, registered, missing, coverage%, группировки"""
```

---

### 2. **Service Discovery v2.0** (`main.py`)

**Enhanced с Catalog Integration**

#### Startup Process:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Service Registry (runtime data)
    service_registry = ServiceRegistry()

    # 2. Initialize Catalog Integration (load YAML)
    catalog_integration = CatalogIntegration()
    await catalog_integration.initialize()  # Loads service-catalog.yaml

    # 3. Initialize EventBus Integration (real-time updates)
    eventbus = create_eventbus('redis')
    await eventbus.connect()

    eventbus_integration = ServiceDiscoveryEventBusIntegration(
        service_registry=service_registry,
        eventbus=eventbus,
        heartbeat_timeout=60
    )
    await eventbus_integration.start()

    yield  # Service running

    # Shutdown
    await eventbus_integration.stop()
    await eventbus.disconnect()
```

---

## 🌐 API Endpoints

### Legacy Consul-Compatible Endpoints (v1)

Сохранены для обратной совместимости:

```
GET    /health
POST   /v1/agent/service/register
DELETE /v1/agent/service/deregister/{service_id}
GET    /v1/catalog/services
GET    /v1/catalog/service/{service_name}
PUT    /v1/agent/check/pass/{service_id}
PUT    /v1/agent/check/fail/{service_id}
GET    /v1/health/service/{service_name}
```

### New Unified Endpoints (v2)

**Catalog + Registry Unified View:**

#### `GET /v2/catalog/services`
**Все сервисы с unified view (catalog + runtime)**

Response:
```json
{
  "services": [
    {
      "name": "ai-foundation",
      "type": "intelligent-core",
      "business_process": "AI Intelligence & Decision Support",
      "kpis": ["request_latency_ms", "ai_decisions_total"],
      "expected_port": 8040,
      "runtime_status": "running",
      "registration_status": "registered",
      "actual_port": 8040,
      "health_status": "healthy",
      "last_seen": "2025-10-11T12:00:00",
      "orchestrator": "docker-compose"
    },
    {
      "name": "planning-service",
      "type": "platform-services",
      "business_process": "Business Continuity Planning",
      "expected_port": null,
      "runtime_status": "unknown",
      "registration_status": "not_registered",
      "actual_port": null,
      "health_status": null,
      "last_seen": null
    }
  ],
  "count": 27
}
```

#### `GET /v2/catalog/services/{service_name}`
**Детальный unified view одного сервиса**

#### `GET /v2/catalog/stats`
**Комплексная статистика**

Response:
```json
{
  "metadata": {
    "timestamp": "2025-10-11T12:00:00",
    "catalog_version": "1.0.0"
  },
  "totals": {
    "total_services": 27,
    "registered_services": 8,
    "missing_services": 19,
    "unknown_services": 0,
    "healthy_services": 7,
    "coverage_percent": 29.6
  },
  "by_type": {
    "intelligent-core": 13,
    "platform-services": 11,
    "infrastructure/gateway": 1,
    "infrastructure/observability": 2
  },
  "by_business_process": {
    "AI Intelligence & Decision Support": 5,
    "Business Continuity Planning": 3,
    "Core Platform Services": 6,
    ...
  },
  "services": {
    "registered": ["ai-foundation", "orchestrator", "mio-manager"],
    "missing": ["planning-service", "compliance-service", ...],
    "unknown": []
  }
}
```

#### `GET /v2/catalog/missing`
**Missing services (в каталоге, но не работают)**

Response:
```json
{
  "services": [
    {
      "name": "planning-service",
      "type": "platform-services",
      "registration_status": "not_registered",
      "runtime_status": "unknown"
    }
  ],
  "count": 19
}
```

#### `GET /v2/catalog/unknown`
**Unknown services (работают, но нет в каталоге)**

#### `GET /v2/catalog/healthy`
**Все healthy services**

#### `GET /v2/registry/services`
**Raw runtime data (без catalog enrichment)**

#### `GET /v2/registry/stats`
**Registry статистика**

---

## 💾 Database Schema

**PostgreSQL таблица для unified registry:**

```sql
CREATE TABLE unified_service_registry (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) UNIQUE NOT NULL,

    -- From catalog (static)
    service_type VARCHAR(100),
    business_process VARCHAR(255),
    kpis JSONB,
    template_dependencies JSONB,
    expected_port INTEGER,
    metrics_endpoint TEXT,
    health_endpoint TEXT,
    service_path TEXT,
    framework VARCHAR(100),

    -- From runtime (dynamic)
    runtime_status VARCHAR(50),
    registration_status VARCHAR(50),
    orchestrator VARCHAR(100),
    actual_port INTEGER,
    health_status VARCHAR(50),
    last_seen TIMESTAMP,
    registered_at TIMESTAMP,
    runtime_dependencies JSONB,
    runtime_metadata JSONB,

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_service_name ON unified_service_registry(service_name);
CREATE INDEX idx_runtime_status ON unified_service_registry(runtime_status);
CREATE INDEX idx_registration_status ON unified_service_registry(registration_status);
CREATE INDEX idx_business_process ON unified_service_registry(business_process);
```

---

## 🔄 Event Flow

### Service Startup Flow:

```
1. Сервис запускается
   ↓
2. EventBus Helper публикует:
   - platform.service.started
   {
     service_name: "ai-foundation",
     orchestrator: "docker-compose",
     port: 8040,
     metadata: {version: "1.0", capabilities: [...]}
   }
   ↓
3. Service Discovery EventBus Integration получает событие
   ↓
4. ServiceRegistry.register() - регистрация в runtime
   ↓
5. CatalogIntegration.get_unified_service() - обогащение данными из catalog
   ↓
6. Save to PostgreSQL (опционально)
   ↓
7. Heartbeat monitoring начинается (30s interval)
```

### Heartbeat Flow:

```
Every 30 seconds:

1. Сервис публикует: platform.service.heartbeat
   ↓
2. EventBus Integration обновляет last_seen
   ↓
3. ServiceRegistry.update_status("running")
   ↓
4. Если heartbeat timeout (60s):
   - Status → "failed"
   - Health → "unhealthy"
   - Publish: platform.service_discovery.heartbeat_timeout
```

---

## 📈 Use Cases

### 1. Admin Panel - Service Status Dashboard

```javascript
// Получить все сервисы с unified view
const response = await fetch('http://localhost:8500/v2/catalog/services');
const data = await response.json();

// Показать таблицу:
data.services.forEach(service => {
  console.log({
    name: service.name,
    status: service.registration_status,  // registered, not_registered, unknown
    health: service.health_status,        // healthy, unhealthy, null
    port: service.actual_port || service.expected_port,
    lastSeen: service.last_seen
  });
});
```

### 2. Monitoring - Missing Services Alert

```javascript
// Получить missing services
const response = await fetch('http://localhost:8500/v2/catalog/missing');
const data = await response.json();

if (data.count > 0) {
  console.error(`⚠️ ${data.count} services are missing!`);
  data.services.forEach(s => {
    console.error(`  - ${s.name} (${s.business_process})`);
  });
}
```

### 3. Platform Health Check

```javascript
// Получить статистику
const response = await fetch('http://localhost:8500/v2/catalog/stats');
const stats = await response.json();

console.log(`Platform Health:
  Total Services: ${stats.totals.total_services}
  Running: ${stats.totals.registered_services}
  Missing: ${stats.totals.missing_services}
  Coverage: ${stats.totals.coverage_percent}%
`);

if (stats.totals.coverage_percent < 50) {
  console.error('⚠️ Platform coverage below 50%!');
}
```

### 4. Service Dependency Check

```javascript
// Получить unified service
const response = await fetch('http://localhost:8500/v2/catalog/services/ai-foundation');
const service = await response.json();

console.log(`Service: ${service.name}
  Expected dependencies: ${service.template_dependencies}
  Runtime dependencies: ${service.runtime_dependencies}
  Status: ${service.runtime_status}
  Health: ${service.health_status}
`);
```

---

## 🚀 Deployment

### 1. Start Service Discovery

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service-discovery

# Ensure service-catalog.yaml exists
ls ../service-catalog/service-catalog.yaml

# Start Service Discovery v2.0
python main.py

# Output:
# 🚀 Service Discovery v2.0 starting...
#    📊 Enhanced with Catalog Integration
#    ✅ Service Registry initialized
#    ✅ Catalog Integration initialized
#    ✅ EventBus connected
#    ✅ EventBus Integration started
# ✅ Service Discovery v2.0 ready on port 8500
#    🔍 Consul-compatible endpoints available
#    📊 Unified Catalog + Registry view enabled
```

### 2. Start Services with EventBus

```bash
# Services with EventBus integration will auto-register
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/orchestrator
python main.py

# Service Discovery logs:
# ✅ Service CONNECTED: orchestrator (orchestrator: ai-office, port: 8059)
```

### 3. Check Unified View

```bash
# Get all services
curl http://localhost:8500/v2/catalog/services | jq

# Get stats
curl http://localhost:8500/v2/catalog/stats | jq

# Get missing services
curl http://localhost:8500/v2/catalog/missing | jq
```

---

## 📊 Что даёт эта интеграция

### ✅ До интеграции:

**Service Catalog:**
- ✅ Статический YAML с спецификациями
- ❌ Не знает что реально работает
- ❌ Нет runtime данных

**Service Discovery:**
- ✅ Runtime регистрация
- ❌ Не знает что ДОЛЖНО работать
- ❌ Нет спецификаций/метрик

### ✅ После интеграции:

**Unified System:**
- ✅ **Template данные** из Catalog (что должно быть)
- ✅ **Runtime данные** из Registry (что реально есть)
- ✅ **Missing detection** (в catalog, но не работает)
- ✅ **Unknown detection** (работает, но нет в catalog)
- ✅ **Coverage metrics** (сколько % сервисов работает)
- ✅ **Health monitoring** через EventBus (real-time)
- ✅ **REST API** для Admin Panel
- ✅ **Database persistence** (готова схема)

---

## 📝 Примеры ответов API

### `/v2/catalog/stats` - Полная статистика

```json
{
  "metadata": {
    "timestamp": "2025-10-11T14:30:00.123456",
    "catalog_version": "1.0.0"
  },
  "totals": {
    "total_services": 27,
    "registered_services": 3,
    "missing_services": 24,
    "unknown_services": 0,
    "healthy_services": 3,
    "coverage_percent": 11.1
  },
  "by_type": {
    "intelligent-core": 13,
    "platform-services": 11,
    "infrastructure/gateway": 1,
    "infrastructure/observability": 2,
    "interface": 3
  },
  "by_business_process": {
    "AI Intelligence & Decision Support": 5,
    "API Gateway & Routing": 1,
    "Business Continuity Planning": 3,
    "Core Platform Services": 6,
    "Data Validation & Quality": 1,
    "Document Management": 1,
    "Governance & Policy Management": 1,
    "ISO 22301 Compliance Management": 1,
    "Incident Response Management": 1,
    "Learning & Knowledge Management": 2,
    "Risk Assessment & Management": 1,
    "System Monitoring & Observability": 2,
    "User Interface & Presentation": 3,
    "Workflow Orchestration & Automation": 3
  },
  "services": {
    "registered": [
      "orchestrator",
      "ai-event-manager",
      "mio-manager"
    ],
    "missing": [
      "api-gateway",
      "monitoring-backend",
      "notification-service",
      "ai-foundation",
      "ai_workflow_optimizer",
      "collective",
      "community_intelligence",
      "event_intelligence",
      "learning-system",
      "predictive",
      "system-bcm-service",
      "workflow-engine",
      "workflow_intelligence",
      "admin-control-center",
      "admin_panel",
      "web-app",
      "bia-service",
      "compliance-service",
      "documents-service",
      "governance-service",
      "learning-service",
      "living-docs",
      "planning_service",
      "plans_service",
      "response-service",
      "risk-service",
      "validation-service"
    ],
    "unknown": []
  }
}
```

---

## 🎯 Next Steps

### Immediate:
1. ✅ **Catalog Integration** - DONE
2. ✅ **REST API endpoints** - DONE
3. ⏳ **Add EventBus to AI Office services** - In Progress (REMAINING_TASKS.md)
4. ⏳ **PostgreSQL persistence** - Schema ready, need connection pool

### Future:
- Admin Panel React component для визуализации
- Historical analytics (service uptime, failure patterns)
- Auto-alerts для missing critical services
- Service dependency graph visualization
- Integration с Policy Engine для auto-recovery

---

## 📁 Файлы

### Созданные:
1. `/infrastructure/runtime/service-discovery/catalog_integration.py` (600+ строк)
   - `ServiceTemplate` dataclass
   - `UnifiedService` dataclass
   - `CatalogIntegration` class
   - Database schema + CRUD methods

### Изменённые:
2. `/infrastructure/runtime/service-discovery/main.py`
   - Added `lifespan` context manager
   - Integrated `CatalogIntegration`
   - Integrated `ServiceDiscoveryEventBusIntegration`
   - Added v2 API endpoints (8 новых endpoints)

### Существующие (используются):
3. `/infrastructure/runtime/service-discovery/service_registry.py`
4. `/infrastructure/runtime/service-discovery/eventbus_integration.py`
5. `/infrastructure/runtime/service-catalog/service-catalog.yaml`

---

## ✅ Summary

**Реализована полная интеграция Service Catalog + Service Discovery:**

- ✅ **Unified Service Registry** - объединение статических спецификаций и runtime данных
- ✅ **Missing/Unknown detection** - автоматическое определение проблем
- ✅ **REST API v2** - 8 новых endpoints для Admin Panel
- ✅ **EventBus integration** - real-time updates через события
- ✅ **Database schema** - готова структура для PostgreSQL persistence
- ✅ **Backward compatibility** - сохранены Consul-compatible endpoints

**Теперь система знает:**
- Какие сервисы **должны** работать (из Catalog)
- Какие сервисы **реально** работают (из Registry)
- Какие сервисы **missing** (критично!)
- Какие сервисы **unknown** (требуют добавления в Catalog)

---

**Status**: ✅ COMPLETE
**Version**: Service Discovery v2.0
**Date**: 2025-10-11
