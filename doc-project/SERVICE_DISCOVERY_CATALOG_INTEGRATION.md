# Service Discovery ↔️ Service Catalog Integration Plan

**Created**: 2025-10-11
**Goal**: Объединить динамический Service Discovery с статическим Service Catalog
**For**: Единая система учёта для платформы И админ-панели

---

## 🎯 Концепция

### Текущая ситуация

**Два источника правды:**

1. **Service Catalog** (`observability/service-catalog/`)
   - 📋 **Статический** - ручное обновление
   - 📊 **Полный** - все 27 сервисов (даже не запущенные)
   - 📈 **Метаданные** - KPIs, business processes, dependencies
   - 🎨 **Шаблон** - определяет "что должно быть"

2. **Service Registry** (`runtime/service-discovery/`)
   - 🔴 **Динамический** - автоматическое обновление
   - 🟢 **Актуальный** - только запущенные сервисы
   - ⚡ **Real-time** - текущий статус (healthy/unhealthy)
   - 👀 **Обнаружение** - находит незарегистрированные

### Проблема

- ❌ Service Catalog **не знает** какие сервисы запущены
- ❌ Service Registry **не знает** про KPIs и бизнес-процессы
- ❌ Admin Panel **не знает** где брать данные

### Решение

**Service Discovery = Master Source** (единая точка истины)

```
Service Catalog (шаблон)
    ↓
Service Discovery (мастер)  ←  EventBus (real-time)
    ↑                       ↑
Resource Tracker           Сервисы (регистрация)
(активное обнаружение)
    ↓
Admin Panel (UI)
```

---

## 📊 Архитектура интеграции

### Компоненты

```
┌─────────────────────────────────────────────────────────┐
│             Service Discovery (Port 8500)                │
│                  ЕДИНАЯ ТОЧКА ИСТИНЫ                     │
└─────────────────────────────────────────────────────────┘
           ↑                    ↑                   ↑
           │                    │                   │
    ┌──────┴─────┐      ┌──────┴───────┐    ┌──────┴────────┐
    │  Service   │      │   EventBus   │    │   Resource    │
    │  Catalog   │      │ Integration  │    │   Tracker     │
    │  (YAML)    │      │  (Real-time) │    │   (Scanner)   │
    └────────────┘      └──────────────┘    └───────────────┘
         📋                   🔴                    👀
      Template             Running              Discovery
           │                    │                   │
           └────────────────────┴───────────────────┘
                              ↓
                    ┌─────────────────┐
                    │ Unified Catalog │
                    │   (Enhanced)    │
                    └─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  Admin Panel    │
                    │    REST API     │
                    └─────────────────┘
```

---

## 🔧 Техническое решение

### 1. Расширить ServiceRegistry

**Файл**: `infrastructure/runtime/service-discovery/service_registry.py`

**Добавить**:

```python
from pathlib import Path
import yaml
import json

class EnhancedServiceRegistry(ServiceRegistry):
    """
    Service Registry с интеграцией Service Catalog

    Функции:
    1. Загрузка шаблона из service-catalog.yaml
    2. Объединение template + runtime данных
    3. Определение незарегистрированных сервисов
    4. Экспорт unified catalog для Admin Panel
    """

    def __init__(self, catalog_path: Optional[Path] = None):
        super().__init__()

        # Путь к Service Catalog
        self.catalog_path = catalog_path or Path(__file__).parent.parent.parent / \
                           "observability/service-catalog/service-catalog.yaml"

        # Загрузить шаблон
        self.catalog_template = self._load_catalog_template()

        # Unified catalog (template + runtime)
        self.unified_catalog = {}

    def _load_catalog_template(self) -> Dict[str, Any]:
        """Загрузить service-catalog.yaml как шаблон"""
        if not self.catalog_path.exists():
            logger.warning(f"Service Catalog not found: {self.catalog_path}")
            return {"services": []}

        with open(self.catalog_path) as f:
            return yaml.safe_load(f)

    async def register(self, service_name: str, **kwargs) -> Service:
        """Регистрация сервиса с обновлением unified catalog"""

        # 1. Стандартная регистрация
        service = await super().register(service_name, **kwargs)

        # 2. Обогатить данными из catalog
        await self._enrich_from_catalog(service)

        # 3. Обновить unified catalog
        await self._update_unified_catalog()

        # 4. Notify об обновлении
        await self._notify_catalog_updated(service_name)

        return service

    async def _enrich_from_catalog(self, service: Service):
        """Обогатить сервис метаданными из catalog"""

        # Найти в template
        for catalog_service in self.catalog_template.get("services", []):
            if catalog_service["name"] == service.name:
                # Добавить metadata из catalog
                service.metadata.update({
                    "catalog_type": catalog_service.get("type"),
                    "business_process": catalog_service.get("business_process"),
                    "kpis": catalog_service.get("kpis", []),
                    "dependencies_expected": catalog_service.get("dependencies", []),
                    "metrics_endpoint": catalog_service.get("metrics_endpoint"),
                    "health_endpoint": catalog_service.get("health_endpoint"),
                    "path": catalog_service.get("path")
                })
                break

    async def _update_unified_catalog(self):
        """Обновить unified catalog (template + runtime)"""

        unified = {
            "metadata": {
                "updated_at": datetime.utcnow().isoformat(),
                "total_services": len(self.catalog_template.get("services", [])),
                "registered_services": len(self.services),
                "running_services": len([s for s in self.services.values()
                                         if s.status == "active"]),
                "platform_name": "AI-Platform-ISO",
                "version": "2.0.0"
            },
            "services": []
        }

        # Объединить template + runtime
        for catalog_service in self.catalog_template.get("services", []):
            service_name = catalog_service["name"]

            # Базовые данные из template
            unified_service = {
                **catalog_service,
                "runtime_status": "not_registered",
                "health": None,
                "last_seen": None,
                "registered_at": None
            }

            # Если сервис зарегистрирован - добавить runtime данные
            if service_name in self.services:
                runtime = self.services[service_name]
                unified_service.update({
                    "runtime_status": runtime.status,
                    "health": runtime.health_status,
                    "last_seen": runtime.last_seen.isoformat(),
                    "registered_at": runtime.registered_at.isoformat(),
                    "orchestrator": runtime.orchestrator,
                    "actual_port": runtime.port,
                    "url": runtime.url
                })

            unified["services"].append(unified_service)

        # Найти незарегистрированные в catalog (новые сервисы)
        catalog_names = {s["name"] for s in self.catalog_template.get("services", [])}
        for service_name, runtime in self.services.items():
            if service_name not in catalog_names:
                # Новый сервис, не в catalog
                unified["services"].append({
                    "name": service_name,
                    "type": "unknown",
                    "port": runtime.port,
                    "status": "discovered",
                    "runtime_status": runtime.status,
                    "health": runtime.health_status,
                    "orchestrator": runtime.orchestrator,
                    "registered_at": runtime.registered_at.isoformat(),
                    "last_seen": runtime.last_seen.isoformat(),
                    "metadata": runtime.metadata,
                    "_note": "Discovered service not in catalog template"
                })

        self.unified_catalog = unified

    async def _notify_catalog_updated(self, service_name: str):
        """Notify через EventBus об обновлении catalog"""
        if self.eventbus:
            await self.eventbus.publish(
                "catalog.updated",
                {
                    "service_name": service_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_services": len(self.unified_catalog["services"])
                }
            )

    def get_unified_catalog(self) -> Dict[str, Any]:
        """Получить unified catalog для Admin Panel"""
        return self.unified_catalog

    def get_unregistered_services(self) -> List[str]:
        """Список сервисов из catalog, которые не зарегистрированы"""
        catalog_names = {s["name"] for s in self.catalog_template.get("services", [])}
        registered_names = set(self.services.keys())
        return list(catalog_names - registered_names)

    def get_discovered_services(self) -> List[str]:
        """Список новых сервисов, не в catalog template"""
        catalog_names = {s["name"] for s in self.catalog_template.get("services", [])}
        registered_names = set(self.services.keys())
        return list(registered_names - catalog_names)

    async def export_catalog(self, format: str = "json") -> str:
        """Экспорт unified catalog в JSON/YAML"""
        if format == "json":
            return json.dumps(self.unified_catalog, indent=2, default=str)
        elif format == "yaml":
            return yaml.dump(self.unified_catalog, default_flow_style=False)
        else:
            raise ValueError(f"Unknown format: {format}")
```

---

### 2. Добавить API endpoints

**Файл**: `infrastructure/runtime/service-discovery/main.py`

**Добавить**:

```python
from service_registry import EnhancedServiceRegistry

# Replace ServiceRegistry with Enhanced
registry = EnhancedServiceRegistry()

@app.get("/v1/catalog")
async def get_unified_catalog():
    """
    Получить unified catalog (template + runtime)

    Для Admin Panel - полная информация о всех сервисах.
    """
    return registry.get_unified_catalog()

@app.get("/v1/catalog/services")
async def list_all_services():
    """Список всех сервисов (из template)"""
    return {
        "services": registry.unified_catalog.get("services", []),
        "total": len(registry.unified_catalog.get("services", []))
    }

@app.get("/v1/catalog/services/{service_name}")
async def get_service_details(service_name: str):
    """Детальная информация о сервисе"""
    for service in registry.unified_catalog.get("services", []):
        if service["name"] == service_name:
            return service
    raise HTTPException(status_code=404, detail="Service not found")

@app.get("/v1/catalog/unregistered")
async def get_unregistered_services():
    """
    Сервисы из catalog, которые должны быть, но не зарегистрированы

    КРИТИЧНО для мониторинга!
    """
    unregistered = registry.get_unregistered_services()
    return {
        "unregistered": unregistered,
        "count": len(unregistered),
        "severity": "critical" if len(unregistered) > 5 else "warning"
    }

@app.get("/v1/catalog/discovered")
async def get_discovered_services():
    """
    Новые сервисы, найденные Resource Tracker, но не в catalog

    Полезно для обновления catalog template.
    """
    discovered = registry.get_discovered_services()
    return {
        "discovered": discovered,
        "count": len(discovered),
        "action": "Update service-catalog.yaml"
    }

@app.get("/v1/catalog/by-status")
async def get_services_by_status():
    """Сервисы по статусам"""
    services = registry.unified_catalog.get("services", [])

    by_status = {
        "running": [],
        "registered": [],
        "not_registered": [],
        "unhealthy": []
    }

    for service in services:
        runtime_status = service.get("runtime_status")
        health = service.get("health")

        if runtime_status == "active" and health == "healthy":
            by_status["running"].append(service["name"])
        elif runtime_status == "active":
            by_status["unhealthy"].append(service["name"])
        elif runtime_status == "registered":
            by_status["registered"].append(service["name"])
        else:
            by_status["not_registered"].append(service["name"])

    return by_status

@app.get("/v1/catalog/by-process")
async def get_services_by_business_process():
    """Сервисы по бизнес-процессам"""
    services = registry.unified_catalog.get("services", [])

    by_process = {}
    for service in services:
        process = service.get("business_process", "Unknown")
        if process not in by_process:
            by_process[process] = []
        by_process[process].append({
            "name": service["name"],
            "status": service.get("runtime_status", "not_registered")
        })

    return by_process

@app.get("/v1/catalog/export")
async def export_catalog(format: str = "json"):
    """
    Экспорт unified catalog

    Для сохранения snapshot или интеграции с внешними системами.
    """
    content = await registry.export_catalog(format=format)

    if format == "json":
        return Response(content=content, media_type="application/json")
    elif format == "yaml":
        return Response(content=content, media_type="text/yaml")

@app.post("/v1/catalog/sync")
async def sync_catalog_from_template():
    """
    Принудительная синхронизация с template

    Полезно после обновления service-catalog.yaml вручную.
    """
    registry.catalog_template = registry._load_catalog_template()
    await registry._update_unified_catalog()

    return {
        "status": "synced",
        "timestamp": datetime.utcnow().isoformat(),
        "total_services": len(registry.unified_catalog["services"])
    }
```

---

### 3. Admin Panel Integration

**Файл**: `interface/admin_panel/src/services/service-catalog.ts`

**Создать**:

```typescript
// Service Catalog API Client for Admin Panel

const SERVICE_DISCOVERY_URL = "http://localhost:8500";

export interface ServiceCatalogEntry {
  name: string;
  type: string;
  port: number | null;
  status: string;
  runtime_status: string;
  health: string | null;
  business_process: string;
  kpis: string[];
  dependencies: string[];
  last_seen: string | null;
  registered_at: string | null;
  metrics_endpoint: string | null;
  health_endpoint: string | null;
  path: string;
}

export interface UnifiedCatalog {
  metadata: {
    updated_at: string;
    total_services: number;
    registered_services: number;
    running_services: number;
    platform_name: string;
    version: string;
  };
  services: ServiceCatalogEntry[];
}

/**
 * Get unified service catalog
 */
export async function getServiceCatalog(): Promise<UnifiedCatalog> {
  const response = await fetch(`${SERVICE_DISCOVERY_URL}/v1/catalog`);
  if (!response.ok) {
    throw new Error("Failed to fetch service catalog");
  }
  return response.json();
}

/**
 * Get services by status
 */
export async function getServicesByStatus() {
  const response = await fetch(`${SERVICE_DISCOVERY_URL}/v1/catalog/by-status`);
  return response.json();
}

/**
 * Get unregistered services (critical!)
 */
export async function getUnregisteredServices() {
  const response = await fetch(`${SERVICE_DISCOVERY_URL}/v1/catalog/unregistered`);
  return response.json();
}

/**
 * Get discovered services (new, not in template)
 */
export async function getDiscoveredServices() {
  const response = await fetch(`${SERVICE_DISCOVERY_URL}/v1/catalog/discovered`);
  return response.json();
}

/**
 * Get services grouped by business process
 */
export async function getServicesByBusinessProcess() {
  const response = await fetch(`${SERVICE_DISCOVERY_URL}/v1/catalog/by-process`);
  return response.json();
}

/**
 * Trigger catalog sync with template
 */
export async function syncCatalog() {
  const response = await fetch(`${SERVICE_DISCOVERY_URL}/v1/catalog/sync`, {
    method: "POST"
  });
  return response.json();
}

/**
 * Export catalog
 */
export async function exportCatalog(format: "json" | "yaml" = "json") {
  const response = await fetch(
    `${SERVICE_DISCOVERY_URL}/v1/catalog/export?format=${format}`
  );
  return response.text();
}
```

---

### 4. Admin Panel Component

**Файл**: `interface/admin_panel/src/pages/ServiceCatalog.tsx`

**Создать**:

```typescript
import React, { useEffect, useState } from "react";
import {
  getServiceCatalog,
  getServicesByStatus,
  getUnregisteredServices,
  getDiscoveredServices,
  type UnifiedCatalog,
  type ServiceCatalogEntry
} from "../services/service-catalog";

export default function ServiceCatalogPage() {
  const [catalog, setCatalog] = useState<UnifiedCatalog | null>(null);
  const [statusGroups, setStatusGroups] = useState<any>(null);
  const [unregistered, setUnregistered] = useState<string[]>([]);
  const [discovered, setDiscovered] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCatalog();
    const interval = setInterval(loadCatalog, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  async function loadCatalog() {
    try {
      const [catalogData, statusData, unregData, discData] = await Promise.all([
        getServiceCatalog(),
        getServicesByStatus(),
        getUnregisteredServices(),
        getDiscoveredServices()
      ]);

      setCatalog(catalogData);
      setStatusGroups(statusData);
      setUnregistered(unregData.unregistered);
      setDiscovered(discData.discovered);
      setLoading(false);
    } catch (error) {
      console.error("Failed to load service catalog:", error);
    }
  }

  if (loading) return <div>Loading service catalog...</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Service Catalog</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <SummaryCard
          title="Total Services"
          value={catalog?.metadata.total_services}
          color="blue"
        />
        <SummaryCard
          title="Running"
          value={catalog?.metadata.running_services}
          color="green"
        />
        <SummaryCard
          title="Unregistered"
          value={unregistered.length}
          color="red"
          critical={unregistered.length > 5}
        />
        <SummaryCard
          title="Discovered"
          value={discovered.length}
          color="yellow"
        />
      </div>

      {/* Unregistered Services Alert */}
      {unregistered.length > 0 && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Warning:</strong> {unregistered.length} expected services not registered:
          <ul className="list-disc ml-6 mt-2">
            {unregistered.map(name => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Discovered Services Info */}
      {discovered.length > 0 && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
          <strong>Info:</strong> {discovered.length} new services discovered:
          <ul className="list-disc ml-6 mt-2">
            {discovered.map(name => (
              <li key={name}>{name}</li>
            ))}
          </ul>
          <p className="mt-2">Consider updating service-catalog.yaml</p>
        </div>
      )}

      {/* Services Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Service
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Port
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Health
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Business Process
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {catalog?.services.map(service => (
              <ServiceRow key={service.name} service={service} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ServiceRow({ service }: { service: ServiceCatalogEntry }) {
  const statusColor = {
    active: "green",
    registered: "yellow",
    not_registered: "gray",
    discovered: "blue"
  }[service.runtime_status] || "gray";

  const healthColor = {
    healthy: "green",
    unhealthy: "red",
    null: "gray"
  }[service.health || "null"];

  return (
    <tr>
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
        {service.name}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {service.type}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {service.port || service.actual_port || "-"}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-${statusColor}-100 text-${statusColor}-800`}>
          {service.runtime_status}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        {service.health ? (
          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-${healthColor}-100 text-${healthColor}-800`}>
            {service.health}
          </span>
        ) : (
          <span className="text-gray-400">-</span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {service.business_process}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
        {service.health_endpoint && (
          <a
            href={service.health_endpoint}
            target="_blank"
            className="text-indigo-600 hover:text-indigo-900 mr-3"
          >
            Health
          </a>
        )}
        {service.metrics_endpoint && (
          <a
            href={service.metrics_endpoint}
            target="_blank"
            className="text-indigo-600 hover:text-indigo-900"
          >
            Metrics
          </a>
        )}
      </td>
    </tr>
  );
}

function SummaryCard({ title, value, color, critical = false }) {
  const bgColor = critical ? "bg-red-500" : `bg-${color}-500`;

  return (
    <div className={`${bgColor} text-white p-4 rounded-lg shadow`}>
      <div className="text-sm opacity-80">{title}</div>
      <div className="text-3xl font-bold">{value}</div>
    </div>
  );
}
```

---

## 🚀 Реализация по этапам

### Phase 1: Enhanced Registry (1-2 часа)
1. ✅ Создать `EnhancedServiceRegistry`
2. ✅ Добавить загрузку `service-catalog.yaml`
3. ✅ Реализовать `unified_catalog` merge
4. ✅ Тесты

### Phase 2: API Endpoints (30 минут)
1. ✅ `/v1/catalog` - unified catalog
2. ✅ `/v1/catalog/unregistered` - критично!
3. ✅ `/v1/catalog/discovered` - новые сервисы
4. ✅ `/v1/catalog/by-status` - группировка
5. ✅ `/v1/catalog/by-process` - бизнес-процессы

### Phase 3: Admin Panel (2 часа)
1. ✅ API client (`service-catalog.ts`)
2. ✅ Service Catalog Page
3. ✅ Real-time updates (10s refresh)
4. ✅ Alerts для unregistered

### Phase 4: Testing (1 час)
1. ✅ Запустить Service Discovery
2. ✅ Зарегистрировать 3-5 сервисов
3. ✅ Проверить unified catalog
4. ✅ Открыть Admin Panel
5. ✅ Проверить real-time updates

---

## 📊 Результат

### Для системы:
- ✅ **Единая точка истины** - Service Discovery
- ✅ **Автоматическое обновление** - через EventBus
- ✅ **Обнаружение проблем** - unregistered services
- ✅ **Обогащённые данные** - template + runtime

### Для администратора:
- ✅ **Визуализация** - Admin Panel
- ✅ **Real-time мониторинг** - статусы обновляются
- ✅ **Алерты** - критичные незарегистрированные сервисы
- ✅ **Группировка** - по процессам, статусам
- ✅ **Ссылки** - прямо на health/metrics endpoints

---

## 🎯 Immediate Next Steps

### 1. Запустить Service Discovery с Enhanced Registry
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service-discovery
python main.py  # Port 8500
```

### 2. Проверить unified catalog
```bash
curl http://localhost:8500/v1/catalog | jq
```

### 3. Открыть Admin Panel
```bash
cd /Users/MD/AI-Platform-ISO/interface/admin_panel
npm run dev
# Navigate to /service-catalog
```

### 4. Запустить несколько сервисов и увидеть real-time updates

---

**Status**: 📝 Plan Ready
**Implementation**: Ready to start
**Dependencies**: Service Discovery должен быть запущен
