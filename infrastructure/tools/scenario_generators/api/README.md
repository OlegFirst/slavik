# Scenario Orchestrator

**AI Office Service** для управления генерацией сценариев тестирования.

## 🎯 Роль в AI Office

Scenario Orchestrator координирует процесс генерации тестовых сценариев через:
- REST API для триггеров генерации
- Интеграция с EventBus для событий
- Мониторинг через MIO Manager
- Прогресс-трекинг генерации

## 🏗️ Архитектура

```
/scenario-orchestrator/
├── main.py                     ← FastAPI application
├── requirements.txt            ← Python dependencies
├── api/
│   ├── __init__.py
│   ├── generation_routes.py   ← Generation endpoints
│   └── monitoring_routes.py   ← Health & metrics
├── models/
│   ├── __init__.py
│   └── requests.py            ← Pydantic models
└── README.md
```

## 🔌 Integration Points

### EventBus Events
**Publishes:**
- `scenario.generation.started`
- `scenario.generation.level_completed`
- `scenario.generation.completed`
- `scenario.generation.failed`

**Subscribes:**
- `system.startup.completed` → Trigger initial generation
- `catalog.updated` → Trigger regeneration

### MIO Manager
- Registers as AI Office agent
- Reports generation progress
- Receives coordination commands

## 📡 API Endpoints

### Generation Control
```http
POST /api/v1/generate/start
POST /api/v1/generate/stop
GET  /api/v1/generate/progress
GET  /api/v1/generate/status
```

### Level-Specific Generation
```http
POST /api/v1/generate/l1/platform
POST /api/v1/generate/l1/applications
POST /api/v1/generate/l2
POST /api/v1/generate/l3
POST /api/v1/generate/l4
```

### Monitoring
```http
GET /health
GET /metrics
GET /api/v1/statistics
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
PORT=8060 python main.py

# Trigger generation
curl -X POST http://localhost:8060/api/v1/generate/start \
  -H "Content-Type: application/json" \
  -d '{"levels": ["l1_platform"]}'
```

## 📊 Service Info

- **Port:** 8060
- **Subsystem:** AI Office
- **Criticality:** Medium
- **Dependencies:**
  - scenario-intelligence module
  - EventBus
  - MIO Manager

## 🔧 Configuration

Environment variables:
```bash
PORT=8060
SCENARIO_INTELLIGENCE_PATH=/path/to/intelligent-core/scenario-intelligence
EVENTBUS_URL=redis://localhost:6379
MIO_MANAGER_URL=http://localhost:8025
```

## 📈 Metrics

Exposes Prometheus metrics:
- `scenario_generation_requests_total`
- `scenario_generation_duration_seconds`
- `scenarios_generated_total`
- `generation_errors_total`

## 🎭 Use Cases

1. **Automated Generation on Startup**
   - System starts → Generate all scenarios

2. **On-Demand Generation**
   - User triggers via UI → Generate specific level

3. **Catalog Update Response**
   - Service catalog updated → Regenerate affected scenarios

4. **Scheduled Regeneration**
   - Daily job → Refresh all scenarios

## 🔗 Related Services

- **scenario-intelligence**: Core generation logic
- **mio-manager**: Coordination and scheduling
- **ai-orchestrator**: Intelligent workflow management
- **simulation-service**: Scenario execution
