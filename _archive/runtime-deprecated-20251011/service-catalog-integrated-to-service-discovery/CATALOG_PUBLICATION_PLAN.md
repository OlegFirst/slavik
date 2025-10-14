# Service Catalog - План публикации

**Version**: 1.0.0
**Date**: October 11, 2025
**Status**: 🚧 Реализация

---

## 🎯 ЦЕЛЬ

Опубликовать Service Catalog в 4 местах для разных аудиторий:

1. **Admin Control Center** → Для разработчиков/DevOps (интерактивно)
2. **Grafana Dashboard** → Для мониторинга (real-time)
3. **Prometheus Metrics** → Для алертинга
4. **GitHub Pages** → Для документации (публично)

---

## 📋 1. ADMIN CONTROL CENTER (Главная панель)

### Текущий статус
- ✅ React admin panel готов (port 3001)
- ✅ TypeScript + Vite + Tailwind
- ✅ API service layer готов
- ❌ Service Catalog компонент НЕ создан

### Что нужно сделать

#### 1.1 Создать Service Catalog Page

```typescript
// /interface/админ/admin-control-center/src/pages/ServiceCatalogPage.tsx

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { serviceCatalogAPI } from '@/services/catalog';

interface Service {
  name: string;
  type: string;
  business_process: string;
  port: number | null;
  status: string;
  kpis: string[];
  runtime_status?: 'running' | 'stopped';
  health_status?: 'healthy' | 'unhealthy' | 'degraded';
}

export const ServiceCatalogPage = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [filteredServices, setFilteredServices] = useState<Service[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadCatalog();
    loadStats();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadCatalog();
      loadStats();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadCatalog = async () => {
    try {
      const data = await serviceCatalogAPI.getAllServices();
      setServices(data.services);
      setFilteredServices(data.services);
    } catch (error) {
      console.error('Failed to load catalog:', error);
    }
  };

  const loadStats = async () => {
    try {
      const data = await serviceCatalogAPI.getStats();
      setStats(data.totals);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  // Filter logic
  useEffect(() => {
    let filtered = services;

    if (searchTerm) {
      filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.business_process.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter(s => s.type.includes(typeFilter));
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(s => s.status === statusFilter);
    }

    setFilteredServices(filtered);
  }, [searchTerm, typeFilter, statusFilter, services]);

  const getStatusBadge = (status: string) => {
    const variants = {
      active: 'bg-green-500',
      configured: 'bg-blue-500',
      deprecated: 'bg-orange-500',
      archived: 'bg-gray-500'
    };
    return <Badge className={variants[status] || 'bg-gray-500'}>{status}</Badge>;
  };

  const getHealthBadge = (health?: string) => {
    if (!health) return <Badge variant="outline">Unknown</Badge>;

    const variants = {
      healthy: 'bg-green-500',
      degraded: 'bg-yellow-500',
      unhealthy: 'bg-red-500'
    };
    return <Badge className={variants[health] || 'bg-gray-500'}>{health}</Badge>;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header with Stats */}
      <div>
        <h1 className="text-3xl font-bold">Service Catalog</h1>
        <p className="text-gray-500">Platform services registry and monitoring</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                Total Services
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total_services}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                Registered
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {stats.registered_services}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                Missing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">
                {stats.missing_services}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                Coverage
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {stats.coverage_percent}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              placeholder="Search services..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />

            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <option value="all">All Types</option>
              <option value="infrastructure">Infrastructure</option>
              <option value="intelligent-core">Intelligent Core</option>
              <option value="platform-services">Platform Services</option>
              <option value="interface">Interface</option>
            </Select>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="configured">Configured</option>
              <option value="deprecated">Deprecated</option>
              <option value="archived">Archived</option>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Services Table */}
      <Card>
        <CardHeader>
          <CardTitle>Services ({filteredServices.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Business Process</TableHead>
                <TableHead>Port</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Health</TableHead>
                <TableHead>KPIs</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredServices.map((service) => (
                <TableRow key={service.name}>
                  <TableCell className="font-medium">{service.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{service.type}</Badge>
                  </TableCell>
                  <TableCell>{service.business_process}</TableCell>
                  <TableCell>{service.port || '-'}</TableCell>
                  <TableCell>{getStatusBadge(service.status)}</TableCell>
                  <TableCell>{getHealthBadge(service.health_status)}</TableCell>
                  <TableCell>{service.kpis?.length || 0} KPIs</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};
```

#### 1.2 Создать API Service

```typescript
// /interface/админ/admin-control-center/src/services/catalog.ts

import axios from 'axios';

const CATALOG_API_BASE = '/api/catalog';

export const serviceCatalogAPI = {
  /**
   * Get all services from catalog + runtime status
   */
  getAllServices: async () => {
    const response = await axios.get(`${CATALOG_API_BASE}/v2/catalog/services`);
    return response.data;
  },

  /**
   * Get missing services (in catalog but not running)
   */
  getMissingServices: async () => {
    const response = await axios.get(`${CATALOG_API_BASE}/v2/catalog/missing`);
    return response.data;
  },

  /**
   * Get unknown services (running but not in catalog)
   */
  getUnknownServices: async () => {
    const response = await axios.get(`${CATALOG_API_BASE}/v2/catalog/unknown`);
    return response.data;
  },

  /**
   * Get catalog statistics
   */
  getStats: async () => {
    const response = await axios.get(`${CATALOG_API_BASE}/v2/catalog/stats`);
    return response.data;
  },

  /**
   * Get specific service details
   */
  getService: async (name: string) => {
    const response = await axios.get(`${CATALOG_API_BASE}/v2/services/${name}`);
    return response.data;
  }
};
```

#### 1.3 Добавить маршрут

```typescript
// /interface/админ/admin-control-center/src/App.tsx

import { ServiceCatalogPage } from '@/pages/ServiceCatalogPage';

// В router
<Route path="/catalog" element={<ServiceCatalogPage />} />
```

#### 1.4 Добавить в навигацию

```typescript
// /interface/админ/admin-control-center/src/components/Navigation.tsx

import { Book } from 'lucide-react';

<NavLink to="/catalog">
  <Book className="w-5 h-5" />
  <span>Service Catalog</span>
</NavLink>
```

#### 1.5 Настроить Vite Proxy

```typescript
// /interface/админ/admin-control-center/vite.config.ts

export default defineConfig({
  server: {
    port: 3001,
    proxy: {
      '/api/catalog': {
        target: 'http://localhost:8500',  // Service Discovery v2.0
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/catalog/, '')
      }
    }
  }
});
```

---

## 📊 2. GRAFANA DASHBOARD

### Что нужно сделать

#### 2.1 Создать Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "Service Catalog - Platform Overview",
    "tags": ["service-catalog", "platform"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Service Catalog Statistics",
        "type": "stat",
        "targets": [
          {
            "expr": "service_catalog_total_services",
            "legendFormat": "Total Services"
          },
          {
            "expr": "service_catalog_registered_services",
            "legendFormat": "Registered"
          },
          {
            "expr": "service_catalog_missing_services",
            "legendFormat": "Missing"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Services by Type",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (type) (service_catalog_services_by_type)"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 3,
        "title": "Services by Status",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (status) (service_catalog_services_by_status)"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 4,
        "title": "Service Health Status",
        "type": "table",
        "targets": [
          {
            "expr": "service_health_status",
            "format": "table"
          }
        ],
        "gridPos": {"h": 12, "w": 24, "x": 0, "y": 16}
      }
    ]
  }
}
```

Сохранить в:
```
/infrastructure/observability/grafana/dashboards/service-catalog-overview.json
```

#### 2.2 Service Discovery должен экспортировать метрики

```python
# /infrastructure/runtime/service-discovery/metrics_exporter.py

from prometheus_client import Gauge, Counter, Histogram, Info

# Catalog metrics
catalog_total_services = Gauge(
    'service_catalog_total_services',
    'Total number of services in catalog'
)

catalog_registered_services = Gauge(
    'service_catalog_registered_services',
    'Number of registered (running) services'
)

catalog_missing_services = Gauge(
    'service_catalog_missing_services',
    'Number of missing services (in catalog but not running)'
)

catalog_unknown_services = Gauge(
    'service_catalog_unknown_services',
    'Number of unknown services (running but not in catalog)'
)

catalog_coverage_percent = Gauge(
    'service_catalog_coverage_percent',
    'Percentage of catalog services that are running'
)

# Services by type
catalog_services_by_type = Gauge(
    'service_catalog_services_by_type',
    'Number of services by type',
    ['type']
)

# Services by status
catalog_services_by_status = Gauge(
    'service_catalog_services_by_status',
    'Number of services by status',
    ['status']
)

# Service health
service_health_status = Gauge(
    'service_health_status',
    'Health status of each service',
    ['service_name', 'status']  # status: healthy|degraded|unhealthy
)

# Catalog info (metadata)
catalog_info = Info(
    'service_catalog',
    'Service catalog metadata'
)

# Export function
async def export_catalog_metrics(catalog_integration, service_registry):
    """Export catalog metrics to Prometheus"""

    stats = await catalog_integration.get_stats()

    # Update metrics
    catalog_total_services.set(stats['totals']['total_services'])
    catalog_registered_services.set(stats['totals']['registered_services'])
    catalog_missing_services.set(stats['totals']['missing_services'])
    catalog_unknown_services.set(stats['totals']['unknown_services'])
    catalog_coverage_percent.set(stats['totals']['coverage_percent'])

    # By type
    for type_name, count in stats['by_type'].items():
        catalog_services_by_type.labels(type=type_name).set(count)

    # By status
    for status, count in stats['by_status'].items():
        catalog_services_by_status.labels(status=status).set(count)

    # Service health
    services = await catalog_integration.get_unified_services()
    for service in services:
        health = service.get('health_status', 'unknown')
        service_health_status.labels(
            service_name=service['name'],
            status=health
        ).set(1 if health == 'healthy' else 0)

    # Catalog metadata
    catalog_info.info({
        'version': stats['metadata']['version'],
        'last_updated': stats['metadata']['generated_at']
    })
```

Интегрировать в Service Discovery:
```python
# /infrastructure/runtime/service-discovery/main.py

from metrics_exporter import export_catalog_metrics
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Schedule metrics export every 30 seconds
scheduler = AsyncIOScheduler()
scheduler.add_job(
    export_catalog_metrics,
    'interval',
    seconds=30,
    args=[catalog_integration, service_registry]
)
scheduler.start()
```

---

## 🔥 3. PROMETHEUS METRICS & ALERTS

### 3.1 Добавить scrape config

```yaml
# /infrastructure/observability/prometheus/prometheus.yml

scrape_configs:
  - job_name: 'service-discovery'
    static_configs:
      - targets: ['localhost:8500']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### 3.2 Создать алерты для каталога

```yaml
# /infrastructure/observability/prometheus/alerts/service-catalog-alerts.yml

groups:
  - name: service_catalog
    interval: 1m
    rules:
      # Missing services alert
      - alert: ServiceCatalogMissingServices
        expr: service_catalog_missing_services > 5
        for: 5m
        labels:
          severity: warning
          component: service-catalog
        annotations:
          summary: "Multiple services missing from runtime"
          description: "{{ $value }} services are in catalog but not running"

      # Unknown services alert
      - alert: ServiceCatalogUnknownServices
        expr: service_catalog_unknown_services > 3
        for: 10m
        labels:
          severity: info
          component: service-catalog
        annotations:
          summary: "Unknown services detected"
          description: "{{ $value }} services are running but not in catalog"

      # Low coverage alert
      - alert: ServiceCatalogLowCoverage
        expr: service_catalog_coverage_percent < 70
        for: 15m
        labels:
          severity: warning
          component: service-catalog
        annotations:
          summary: "Service catalog coverage is low"
          description: "Only {{ $value }}% of catalog services are running"

      # Service health degraded
      - alert: ServiceHealthDegraded
        expr: service_health_status{status="degraded"} == 1
        for: 5m
        labels:
          severity: warning
          component: "{{ $labels.service_name }}"
        annotations:
          summary: "Service health degraded: {{ $labels.service_name }}"
          description: "Service {{ $labels.service_name }} is in degraded state"

      # Service unhealthy
      - alert: ServiceUnhealthy
        expr: service_health_status{status="unhealthy"} == 1
        for: 2m
        labels:
          severity: critical
          component: "{{ $labels.service_name }}"
        annotations:
          summary: "Service unhealthy: {{ $labels.service_name }}"
          description: "Service {{ $labels.service_name }} is unhealthy"
```

Добавить в prometheus.yml:
```yaml
rule_files:
  - 'alerts/orchestrator-alerts.yml'
  - 'alerts/service-catalog-alerts.yml'  # ← NEW
```

---

## 🌐 4. GITHUB PAGES (Публичная документация)

### Что нужно сделать

#### 4.1 Создать статический JSON для GitHub Pages

```python
# /infrastructure/tools/doc-generators/github_pages_exporter.py

import json
import yaml
from pathlib import Path
from datetime import datetime

async def export_catalog_for_github_pages():
    """Export service catalog to GitHub Pages friendly format"""

    # Load catalog
    catalog_path = Path("/Users/MD/AI-Platform-ISO/infrastructure/runtime/service-catalog/service-catalog.yaml")
    with open(catalog_path, 'r') as f:
        catalog = yaml.safe_load(f)

    # Transform to JSON
    github_pages_data = {
        'metadata': {
            'platform_name': catalog['metadata']['platform_name'],
            'version': catalog['metadata']['version'],
            'total_services': catalog['metadata']['total_services'],
            'generated_at': datetime.now().isoformat(),
            'last_updated': catalog['metadata']['generated_at']
        },
        'services': []
    }

    for service in catalog['services']:
        github_pages_data['services'].append({
            'name': service['name'],
            'display_name': service.get('display_name', service['name']),
            'type': service['type'],
            'business_process': service['business_process'],
            'description': service.get('description', ''),
            'port': service.get('port'),
            'status': service['status'],
            'kpis': service.get('kpis', []),
            'documentation': service.get('documentation', {}),
            'endpoints': {
                'health': service.get('health_endpoint'),
                'metrics': service.get('metrics_endpoint'),
                'api_docs': service.get('api_docs_endpoint')
            }
        })

    # Save to docs website
    output_path = Path("/Users/MD/AI-Platform-ISO/docs-website/public/data/service-catalog.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(github_pages_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Exported catalog to: {output_path}")
    print(f"   Services: {len(github_pages_data['services'])}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(export_catalog_for_github_pages())
```

#### 4.2 Создать React компонент для GitHub Pages

```tsx
// /docs-website/src/components/ServiceCatalog.tsx

import React, { useEffect, useState } from 'react';

interface Service {
  name: string;
  display_name: string;
  type: string;
  business_process: string;
  description: string;
  port: number | null;
  status: string;
  kpis: string[];
}

export const ServiceCatalog = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetch('/data/service-catalog.json')
      .then(res => res.json())
      .then(data => setServices(data.services));
  }, []);

  const filteredServices = services.filter(s =>
    s.name.toLowerCase().includes(filter.toLowerCase()) ||
    s.business_process.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="service-catalog">
      <h1>Service Catalog</h1>

      <input
        type="text"
        placeholder="Search services..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="search-input"
      />

      <table className="catalog-table">
        <thead>
          <tr>
            <th>Service</th>
            <th>Type</th>
            <th>Business Process</th>
            <th>Port</th>
            <th>Status</th>
            <th>KPIs</th>
          </tr>
        </thead>
        <tbody>
          {filteredServices.map(service => (
            <tr key={service.name}>
              <td>{service.display_name}</td>
              <td><span className="badge">{service.type}</span></td>
              <td>{service.business_process}</td>
              <td>{service.port || '-'}</td>
              <td>
                <span className={`status-badge ${service.status}`}>
                  {service.status}
                </span>
              </td>
              <td>{service.kpis.length} KPIs</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

#### 4.3 GitHub Actions для автопубликации

```yaml
# .github/workflows/publish-catalog.yml

name: Publish Service Catalog to GitHub Pages

on:
  push:
    paths:
      - 'infrastructure/runtime/service-catalog/service-catalog.yaml'
      - '**/SERVICE_INFO.yaml'
  workflow_dispatch:

jobs:
  publish-catalog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pyyaml

      - name: Export catalog to GitHub Pages format
        run: python3 infrastructure/tools/doc-generators/github_pages_exporter.py

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Build docs website
        run: |
          cd docs-website
          npm install
          npm run build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs-website/dist
```

---

## 📋 ЧЕКЛИСТ РЕАЛИЗАЦИИ

### Phase 1: Admin Control Center (1-2 дня)
- [ ] Создать ServiceCatalogPage.tsx
- [ ] Создать catalog.ts API service
- [ ] Добавить маршрут в App.tsx
- [ ] Добавить в навигацию
- [ ] Настроить Vite proxy
- [ ] Протестировать интеграцию

### Phase 2: Prometheus + Grafana (1 день)
- [ ] Создать metrics_exporter.py в Service Discovery
- [ ] Добавить scrape config для Service Discovery
- [ ] Создать service-catalog-alerts.yml
- [ ] Создать Grafana dashboard JSON
- [ ] Импортировать dashboard в Grafana
- [ ] Протестировать алерты

### Phase 3: GitHub Pages (1 день)
- [ ] Создать github_pages_exporter.py
- [ ] Создать ServiceCatalog.tsx для docs-website
- [ ] Настроить GitHub Actions
- [ ] Протестировать автопубликацию
- [ ] Добавить в docs navigation

### Phase 4: Интеграция (1 день)
- [ ] Связать все 4 источника
- [ ] Настроить auto-refresh
- [ ] Документировать workflow
- [ ] Провести end-to-end тест

---

## 🚀 ИТОГОВАЯ АРХИТЕКТУРА ПУБЛИКАЦИИ

```
SERVICE_INFO.yaml (в каждом сервисе)
    ↓
service_catalog_generator.py (сканирует проект)
    ↓
service-catalog.yaml (централизованный каталог)
    ↓
    ├── Service Discovery v2.0 (loads catalog)
    │       ↓
    │       ├── REST API (/v2/catalog/*)
    │       │       ↓
    │       │       └── Admin Control Center (React UI)
    │       │
    │       └── Prometheus Metrics (/metrics)
    │               ↓
    │               ├── Grafana Dashboard
    │               └── AlertManager (alerts)
    │
    └── github_pages_exporter.py
            ↓
            └── GitHub Pages (public docs)
```

---

## 📊 РЕЗУЛЬТАТ

После реализации у нас будет:

✅ **Admin Control Center** (localhost:3001/catalog)
- Интерактивная таблица с фильтрами
- Real-time статус сервисов
- Health monitoring
- KPIs и метрики

✅ **Grafana Dashboard** (localhost:3000)
- Service Catalog Overview
- Pie charts по типам и статусам
- Health status table
- Coverage metrics

✅ **Prometheus Alerts**
- Missing services
- Unknown services
- Low coverage
- Service health

✅ **GitHub Pages** (публично)
- Статическая документация
- JSON API для внешних систем
- Автообновление через GitHub Actions

---

**Status**: 🚧 Готово к реализации
**Priority**: HIGH
**Effort**: 4-5 дней
**Date**: October 11, 2025
