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
