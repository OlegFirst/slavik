# AI Event Manager - Infrastructure Service

**FastAPI сервис для практического управления событиями**

---

## 🎯 Назначение

AI Event Manager - это **инфраструктурный слой**, который:
- Предоставляет REST API для работы с Event Intelligence
- Применяет рекомендации AI на практике
- Собирает feedback для обучения
- Мониторит состояние событийной архитектуры

---

## 🏗️ Архитектура

```
infrastructure/ai_event_manager/  (Практика - API)
         │
         ├─ main.py           (FastAPI service)
         ├─ requirements.txt
         └─ README.md

         ↓ использует ↓

intelligent-core/event_intelligence/  (Мозг - AI)
         │
         ├─ analyzer.py       (Анализ)
         ├─ learner.py        (Обучение)
         ├─ predictor.py      (Предсказания)
         └─ knowledge_base.py

         ↓ использует ↓

tools/event_intelligence/  (Утилиты - Сканирование)
         │
         ├─ event_intelligence_system.py
         ├─ auto_fixer.py
         └─ continuous_monitor.py
```

---

## 🚀 Quick Start

### 1. Установка

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/ai_event_manager

pip install -r requirements.txt
```

### 2. Запуск

```bash
python3 main.py

# API доступен на http://localhost:8055
# Docs: http://localhost:8055/docs
```

### 3. Проверка

```bash
curl http://localhost:8055/health
```

---

## 📡 API Endpoints

### Health & Status

```bash
# Health check
GET /health

# Dashboard summary
GET /dashboard/summary
```

### Analysis

```bash
# Analyze single event
POST /analyze/event
{
  "event_name": "bia.completed",
  "publishers": ["bia-service"],
  "subscribers": ["predictive-service"]
}
```

### Recommendations

```bash
# Get AI recommendations
GET /recommendations?scope=all
# scope: all, critical, workflow, high-priority
```

### Learning

```bash
# Record feedback
POST /feedback
{
  "suggestion_id": "2025-10-07T...",
  "decision": "approved",
  "outcome": "success"
}

# Learning stats
GET /learning/stats

# Full learning report
GET /learning/report
```

### Predictions

```bash
# Future predictions
GET /predictions/future
```

---

## 💡 Use Cases

### Use Case 1: Утреннее совещание

```bash
# Получить топ рекомендации
curl http://localhost:8055/recommendations?scope=high-priority

{
  "recommendations": [
    {
      "event_name": "bia.completed",
      "importance": 0.85,
      "learned_confidence": 0.92,
      "recommendations": ["Add publisher..."],
      "ai_insights": "Core system event..."
    }
  ]
}
```

### Use Case 2: После внедрения события

```bash
# Записать feedback
curl -X POST http://localhost:8055/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "suggestion_id": "2025-10-07T10:30:00.000Z",
    "decision": "approved",
    "outcome": "success"
  }'

# AI обучится и улучшит будущие рекомендации
```

### Use Case 3: Мониторинг

```bash
# Dashboard summary
curl http://localhost:8055/dashboard/summary

{
  "summary": {
    "learning": {
      "total_examples": 150,
      "accuracy": 0.85,
      "patterns_learned": 12
    },
    "recommendations": {
      "high_priority": 8
    }
  },
  "health": "healthy"
}
```

---

## 🆕 Infrastructure State Monitoring (NEW!)

**Дата**: 2025-10-10
**Статус**: ✅ Production Ready

### Overview

Unified infrastructure monitoring system that collects state from multiple sources and publishes to EventBus for platform-wide coordination.

**Replaces**: `/infrastructure/central-brain/` (archived as deprecated)

### Data Sources

The Infrastructure State Monitor collects from:
- **Project Manager** - ports, databases, metrics coverage
- **MIO Manager** - CPU, memory, disk usage
- **Service Discovery** - health checks
- **Prometheus** - service metrics

### EventBus Events

**Published** (for coordination):
- `platform.infrastructure.state_updated` - Every 60s with complete state
- `platform.infrastructure.emergency` - Critical issues (DB down, resource exhausted)
- `platform.infrastructure.strategy_recommended` - Scaling strategy recommendations
- `platform.infrastructure.resource_deficit` - Low resource warnings

**Subscribed** (for awareness):
- `platform.service.registered` - New service added
- `platform.service.unregistered` - Service removed
- `platform.resources.snapshot` - From mio-manager

### API Endpoints

```bash
# Get current infrastructure state
GET /infrastructure/state

# Get available resources
GET /infrastructure/resources

# Get scaling strategy recommendation
GET /infrastructure/strategy

# Check if service can be deployed
POST /infrastructure/deployment-check
{
  "service_name": "new-service",
  "requires_db": true,
  "requires_metrics": true
}

# Get state history (trending)
GET /infrastructure/history?limit=10
```

### Example: Infrastructure State

```json
{
  "status": "success",
  "state": {
    "timestamp": "2025-10-10T12:00:00",
    "ports_available": 50,
    "ports_used": 30,
    "prometheus_available": true,
    "grafana_available": true,
    "postgres_available": true,
    "redis_available": true,
    "services_with_metrics": 18,
    "services_with_db": 20,
    "total_services": 24,
    "healthy_services": 22,
    "unhealthy_services": 2,
    "cpu_usage": 0.45,
    "memory_usage": 0.62,
    "monitoring_coverage": 0.75,
    "database_coverage": 0.83,
    "health_check_coverage": 0.92
  }
}
```

### Integration with balancer-service

The **balancer-service** now subscribes to infrastructure events:
- Makes **infrastructure-aware balancing decisions**
- Adjusts strategy based on resource capacity
- Enters **emergency mode** when critical resources unavailable
- Aligns with strategic recommendations

### Benefits

✅ **Unified monitoring** - All infrastructure data in one place
✅ **EventBus coordination** - All services receive state updates
✅ **Infrastructure-aware balancing** - Smarter resource allocation
✅ **Strategic decisions** - Rule-based scaling recommendations
✅ **API access** - Easy integration with any service
✅ **Historical trending** - Analyze patterns over time

---

## 🔗 Интеграции

### С Event Intelligence (tools)

```python
from tools.event_intelligence.event_intelligence_system import EventIntelligenceSystem

# Загружаем данные
eis = EventIntelligenceSystem('/Users/MD/AI-Platform-ISO')
eis.load_catalog()
```

### С AI Foundation (intelligent-core)

```python
from intelligent_core.event_intelligence import EventAnalyzer, EventLearner

# Используем AI компоненты
analyzer = EventAnalyzer()
learner = EventLearner()
```

---

## 📊 Мониторинг

### Prometheus Metrics

```bash
# Prometheus metrics доступны на /metrics
curl http://localhost:8055/metrics
```

Доступные метрики:
- `ai_event_manager_requests_total` - Общее количество запросов (по endpoint и method)
- `ai_event_manager_request_duration_seconds` - Длительность запросов (по endpoint)
- `ai_event_manager_recommendations_total` - Количество рекомендаций (по scope)
- `ai_event_manager_learning_accuracy` - Точность обучения
- `ai_event_manager_feedback_total` - Количество feedback (по decision)

### Logging

```python
# Логи доступны в stdout
tail -f /var/log/ai_event_manager.log
```

---

## 🎓 Best Practices

1. **Регулярно собирайте feedback**
   - После каждого внедрения события записывайте result
   - AI будет учиться и улучшать рекомендации

2. **Мониторьте accuracy**
   - Проверяйте `/learning/stats`
   - Если accuracy < 0.6, нужно больше feedback

3. **Используйте scope**
   - `high-priority` для спринт-планирования
   - `critical` для hotfixes
   - `workflow` для оптимизации

---

## 🔮 Roadmap

- [x] MVP API
- [x] AI Integration
- [x] Learning System
- [ ] Auto-execution (с подтверждением)
- [ ] Webhook notifications
- [ ] Grafana dashboard
- [ ] Slack integration

---

**🏗️ Инфраструктурный слой готов!**

Теперь AI может не только анализировать, но и практически управлять событиями через API.
