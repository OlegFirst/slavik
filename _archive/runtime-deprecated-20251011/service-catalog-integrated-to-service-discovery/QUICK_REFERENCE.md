# Service Catalog - Быстрая справка

## 📋 Обязательные поля для каждого сервиса

```yaml
name: "service-name"              # ✅ REQUIRED - уникальное имя
type: "infrastructure/..."        # ✅ REQUIRED - тип из списка ниже
business_process: "Process Name"  # ✅ REQUIRED - процесс из списка ниже
port: 8046                        # ✅ REQUIRED для HTTP (null для UI/CLI)
status: "active"                  # ✅ REQUIRED - статус
path: "path/to/service"          # ✅ REQUIRED - путь к коду
kpis: [...]                      # ✅ REQUIRED - минимум 4 базовых
dependencies: [...]              # ✅ REQUIRED - список зависимостей
metrics_endpoint: "http://..."   # ✅ REQUIRED для HTTP
health_endpoint: "http://..."    # ✅ REQUIRED для HTTP
framework: "React"               # 📝 OPTIONAL - для UI сервисов
```

## 🏷️ Типы сервисов (type)

### Infrastructure
```
infrastructure/gateway                    # API Gateway
infrastructure/observability              # Monitoring, Logging
infrastructure/AI-office-infrastructure   # MIO, Orchestrator, Analytics
infrastructure/runtime                    # Service Discovery, Message Queue
infrastructure/security                   # Auth, Secrets
infrastructure/integration                # GitHub, MCP, External APIs
```

### Intelligent Core
```
intelligent-core                          # AI Foundation, Brain, Predictive
```

### Platform Services
```
platform-services                         # BIA, Compliance, Risk, etc.
```

### Interface
```
interface                                 # Admin panels, Web apps
```

## 📊 Бизнес-процессы (business_process)

### Infrastructure
- `API Gateway & Routing`
- `System Monitoring & Observability`
- `Service Discovery & Registry`
- `Message Queue & Event Bus`
- `Security & Authentication`
- `Integration & Connectivity`

### AI & Intelligence
- `AI Intelligence & Decision Support`
- `Workflow Orchestration & Automation`
- `Learning & Knowledge Management`
- `Predictive Analytics & Forecasting`
- `Event Intelligence & Analysis`

### Business Services
- `Business Continuity Planning`
- `ISO 22301 Compliance Management`
- `Risk Assessment & Management`
- `Incident Response Management`
- `Document Management`
- `Governance & Policy Management`
- `Data Validation & Quality`

### UI
- `User Interface & Presentation`
- `Administration & Control`

### Generic
- `Core Platform Services`  *(используйте только если ничего не подходит)*

## 📈 KPIs - Обязательные для HTTP сервисов

```yaml
kpis:
  - request_latency_ms          # ✅ REQUIRED
  - requests_per_second         # ✅ REQUIRED
  - error_rate_percent          # ✅ REQUIRED
  - availability_percent        # ✅ REQUIRED
```

## 📈 KPIs - Дополнительные (по типу сервиса)

### AI Services
```yaml
  - ai_decisions_total
  - ml_prediction_accuracy
  - knowledge_graph_size
```

### Workflow Services
```yaml
  - workflows_executed
  - workflow_success_rate
  - avg_workflow_duration_sec
```

### Monitoring Services (MIO)
```yaml
  - coverage_percentage
  - alert_response_time
  - services_monitored
  - observations_published
```

### Compliance Services
```yaml
  - compliance_score_percent
  - audit_items_tracked
  - violations_detected
```

### UI Services
```yaml
  - page_load_time_ms
  - time_to_interactive_ms
  - bundle_size_kb
  - user_sessions_active
```

## 🔗 Endpoints - Формат

```yaml
metrics_endpoint: "http://localhost:8046/metrics"  # Prometheus
health_endpoint: "http://localhost:8046/health"    # Health check
```

Для UI/CLI сервисов:
```yaml
metrics_endpoint: null
health_endpoint: null
```

## 🎯 Ports - Диапазоны

| Range | Назначение |
|-------|-----------|
| 8000-8099 | API Gateway & Core |
| 8100-8199 | Infrastructure |
| 8200-8299 | Platform Services |
| 8300-8399 | Intelligent Core |
| 8400-8499 | AI Office |
| 8500-8599 | Runtime Services |

## 📦 Dependencies - Примеры

### Python Backend
```yaml
dependencies:
  - fastapi
  - uvicorn[standard]
  - pydantic
  - pydantic-settings
  - sqlalchemy
  - asyncpg
  - redis
  - httpx
  - prometheus-client
```

### React Frontend
```yaml
dependencies:
  - react
  - react-dom
  - typescript
  - "@mui/material"
  - "@radix-ui/react-dialog"
  - vite
```

## ⚠️ Status Values

| Status | Когда использовать |
|--------|--------------------|
| `active` | Сервис работает в продакшн |
| `configured` | Сконфигурирован, готов к запуску |
| `deprecated` | Устарел, планируется замена |
| `archived` | Заархивирован |
| `planned` | Запланирован, но не реализован |

## ✅ Checklist для нового сервиса

1. ⬜ Выбрать уникальное имя (kebab-case/snake_case)
2. ⬜ Определить тип (infrastructure/intelligent-core/platform-services/interface)
3. ⬜ Выбрать бизнес-процесс
4. ⬜ Назначить порт (если HTTP)
5. ⬜ Указать путь к коду
6. ⬜ Добавить 4+ KPIs
7. ⬜ Перечислить dependencies
8. ⬜ Указать metrics_endpoint (если HTTP)
9. ⬜ Указать health_endpoint (если HTTP)
10. ⬜ Установить status = "active"
11. ⬜ Добавить framework (если UI)

## 🚀 Быстрый старт - Шаблон нового сервиса

### HTTP Backend Service
```yaml
- name: my-new-service
  type: infrastructure/observability
  business_process: "System Monitoring & Observability"
  port: 8150
  status: active
  path: infrastructure/observability/my-new-service

  kpis:
    - request_latency_ms
    - requests_per_second
    - error_rate_percent
    - availability_percent

  dependencies:
    - fastapi
    - uvicorn[standard]
    - pydantic
    - httpx

  metrics_endpoint: http://localhost:8150/metrics
  health_endpoint: http://localhost:8150/health
```

### React UI Service
```yaml
- name: my-new-ui
  type: interface
  business_process: "User Interface & Presentation"
  port: null
  status: active
  path: interface/my-new-ui
  framework: "React + Vite"

  kpis:
    - page_load_time_ms
    - time_to_interactive_ms
    - bundle_size_kb
    - user_sessions_active

  dependencies:
    - react
    - react-dom
    - vite

  metrics_endpoint: null
  health_endpoint: null
```

## 📚 Дополнительная информация

Полная спецификация: `CATALOG_SCHEMA.md`

---

**Version**: 2.0
**Last Updated**: October 11, 2025
